import streamlit as st
import pymysql
import pandas as pd

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

def get_all_order_status():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT status_id, description FROM orderstatus")
            return cursor.fetchall()
    finally:
        conn.close()

def get_order_history(customer_id, selected_status):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    o.order_id,
                    o.order_date,
                    o.shipped_date,
                    o.total_price,
                    os.description AS order_status,
                    p.description AS payment_method,
                    o.address,
                    o.note
                FROM orders o
                LEFT JOIN orderstatus os ON o.order_status = os.status_id
                LEFT JOIN payment p ON o.payment = p.payment_id
                WHERE o.customer_id = %s
            """
            params = [customer_id]

            if selected_status and selected_status != "Tất cả":
                query += " AND os.description = %s"
                params.append(selected_status)

            query += " ORDER BY o.order_date DESC"
            cursor.execute(query, params)
            return cursor.fetchall()
    finally:
        conn.close()

def get_order_details(order_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.product_id, p.name AS product_name, od.quantity, od.unit_price, od.discount, (od.quantity * od.unit_price * (1 - od.discount)) AS total
                FROM orderdetail od
                JOIN product p ON od.product_id = p.product_id
                WHERE od.order_id = %s
            """, (order_id,))
            return cursor.fetchall()
    finally:
        conn.close()

st.title("📜 Lịch sử mua hàng")

if "customer_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập để xem lịch sử đơn hàng.")
    st.stop()

statuses = get_all_order_status()
status_options = ["Tất cả"] + [s["description"] for s in statuses]
selected_status = st.selectbox("📌 Lọc theo trạng thái đơn hàng:", status_options)

orders = get_order_history(st.session_state.customer_id, selected_status)

if orders:
    df = pd.DataFrame(orders)
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.strftime("%d/%m/%Y %H:%M")
    df["shipped_date"] = df["shipped_date"].apply(
    lambda x: pd.to_datetime(x).strftime("%d/%m/%Y %H:%M") if pd.notnull(x) else ""
    )
    df.rename(columns={
        "order_id": "Mã đơn",
        "order_date": "Ngày đặt",
        "shipped_date": "Ngày giao",
        "total_price": "Tổng tiền",
        "order_status": "Trạng thái",
        "payment_method": "Thanh toán",
        "address": "Địa chỉ nhận hàng",
        "note": "Ghi chú"
    }, inplace=True)

    st.dataframe(df, use_container_width=True)
    for order in orders:
        with st.expander(f"📦 Xem chi tiết đơn hàng {order['order_id']}"):
            details = get_order_details(order['order_id'])
            if details:
                df_detail = pd.DataFrame(details)
                df_detail.rename(columns={
                    "product_name": "Sản phẩm",
                    "quantity": "Số lượng",
                    "unit_price": "Đơn giá",
                    "discount": "Giảm giá (%)",
                    "total": "Thành tiền"
                }, inplace=True)

                df_detail["Đơn giá"] = df_detail["Đơn giá"].apply(lambda x: f"{x:,.0f}₫")
                df_detail["Thành tiền"] = df_detail["Thành tiền"].apply(lambda x: f"{x:,.0f}₫")
                df_detail["Giảm giá (%)"] = df_detail["Giảm giá (%)"] * 100

                st.dataframe(df_detail, use_container_width=True)

                if order["order_status"] == "Đã gaio hàng":
                    st.markdown("### ✍️ Đánh giá sản phẩm:")
                    for item in details:
                        product_name = item["product_name"]
                        product_id = item.get("product_id")
                        
                        st.write(f"#### 🛍️ {product_name}")
                        
                        conn = get_connection()
                        with conn.cursor() as cursor:
                            cursor.execute("""
                                SELECT * FROM review
                                WHERE customer_id = %s AND product_id = %s
                            """, (st.session_state.customer_id, product_id))
                            review = cursor.fetchone()
                        
                        if review:
                            st.success(f"✅ Bạn đã đánh giá: {review['rating']}⭐ - \"{review['content']}\"")
                        else:
                            rating = st.slider(f"Đánh giá (1-5 sao) cho {product_name}", 1, 5, key=f"rating_{order['order_id']}_{product_id}")
                            content = st.text_area("Nội dung đánh giá", key=f"content_{order['order_id']}_{product_id}")
                            if st.button(f"Gửi đánh giá cho {product_name}", key=f"submit_{order['order_id']}_{product_id}"):
                                conn = get_connection()
                                with conn.cursor() as cursor:
                                    cursor.execute("""
                                        INSERT INTO review (customer_id, product_id, rating, content, created_at)
                                        VALUES (%s, %s, %s, %s, NOW())
                                    """, (st.session_state.customer_id, product_id, rating, content))
                                    conn.commit()
                                conn.close()
                                st.success("🎉 Đánh giá đã được gửi!")
else:
    st.info("📭 Không có đơn hàng nào.")

if st.button("🏠Về trang chủ"):
    st.switch_page('pages/5_home.py')