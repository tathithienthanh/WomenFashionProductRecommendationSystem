import streamlit as st
import pymysql
import pandas as pd

# --- Hàm kết nối CSDL ---
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

# --- Lấy tất cả trạng thái đơn hàng ---
def get_all_order_status():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT status_id, description FROM orderstatus")
            return cursor.fetchall()
    finally:
        conn.close()

# --- Lấy lịch sử đơn hàng (có lọc) ---
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

# --- Giao diện chính ---
st.title("📜 Lịch sử mua hàng")

if "customer_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập để xem lịch sử đơn hàng.")
    st.stop()

# --- Lọc theo trạng thái đơn hàng ---
statuses = get_all_order_status()
status_options = ["Tất cả"] + [s["description"] for s in statuses]
selected_status = st.selectbox("📌 Lọc theo trạng thái đơn hàng:", status_options)

orders = get_order_history(st.session_state.customer_id, selected_status)

# --- Hiển thị kết quả ---
if orders:
    df = pd.DataFrame(orders)
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.strftime("%d/%m/%Y %H:%M")
    df["shipped_date"] = df["shipped_date"].apply(
    lambda x: pd.to_datetime(x).strftime("%d/%m/%Y %H:%M") if pd.notnull(x) else "Chưa giao"
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
else:
    st.info("📭 Không có đơn hàng nào.")
