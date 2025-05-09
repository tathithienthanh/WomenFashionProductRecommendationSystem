import streamlit as st
import pandas as pd
import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce"
    )

def has_permission(permission_id: str) -> bool:
    admin_id = st.session_state.get("admin_id")
    if not admin_id:
        return False
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 1 FROM AdminHasPermissions
                WHERE permission_id = %s AND admin_id = %s
                LIMIT 1
            """
            cursor.execute(query, (permission_id, admin_id))
            return cursor.fetchone() is not None
    finally:
        conn.close()

def log_admin_activity(admin_id, activity):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO ActivityLog (admin_id, activity) VALUES (%s, %s)"
            cursor.execute(sql, (admin_id, activity))
        conn.commit()
    finally:
        conn.close()

def get_orders():
    conn = get_connection()
    try:
        query = '''
        SELECT o.order_id, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
                   o.order_date, o.shipped_date, os.description AS status, 
                   o.total_price, p.description AS payment, o.address
            FROM Orders o
            JOIN Customer c ON o.customer_id = c.customer_id
            JOIN OrderStatus os ON o.order_status = os.status_id
            JOIN Payment p ON o.payment = p.payment_id
            ORDER BY o.order_date DESC
        '''
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def get_order_detail(order_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT od.product_id, pr.name AS product_name, od.quantity, od.unit_price, od.discount
                FROM OrderDetail od
                JOIN Product pr ON od.product_id = pr.product_id
                WHERE od.order_id = %s
            """, (order_id,))
            result = cursor.fetchall()
            columns = ['product_id', 'product_name', 'quantity', 'unit_price', 'discount']
            return pd.DataFrame(result, columns=columns)
    finally:
        conn.close()

def get_order_statuses():
    conn = get_connection()
    try:
        query = "SELECT status_id, description FROM OrderStatus"
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def update_order_status(order_id, new_status):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE Orders SET order_status = %s WHERE order_id = %s", (new_status, order_id))
        conn.commit()

st.title("📦 Quản lý đơn hàng")

if "admin_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập với vai trò admin để truy cập trang này.")
    st.stop()

if not has_permission("MANAGE_ORDERS"):
    st.warning("Bạn không có quyền truy cập chức năng này.")
    st.stop()

tab1, tab2 = st.tabs(["📋 Danh sách đơn hàng", "🔍 Chi tiết & cập nhật trạng thái"])

with tab1:
    st.subheader("📋 Danh sách đơn hàng")
    orders_df = get_orders()
    if orders_df.empty:
        st.info("Không có đơn hàng nào.")
    else:
        unique_statuses = orders_df["status"].unique().tolist()
        selected_status = st.selectbox("🔎 Lọc theo trạng thái", ["Tất cả"] + unique_statuses)

        if selected_status != "Tất cả":
            filtered_orders_df = orders_df[orders_df["status"] == selected_status]
        else:
            filtered_orders_df = orders_df
        st.dataframe(filtered_orders_df, use_container_width=True)

with tab2:
    st.subheader("🔍 Xem chi tiết & cập nhật trạng thái")
    orders_df = get_orders()
    order_ids = orders_df["order_id"].tolist()

    if order_ids:
        selected_order_id = st.selectbox("Chọn mã đơn hàng", order_ids)
        detail_df = get_order_detail(selected_order_id)
        st.write("🧾 **Chi tiết sản phẩm:**")
        st.dataframe(detail_df, use_container_width=True)

        current_status = orders_df[orders_df["order_id"] == selected_order_id]["status"].values[0]
        st.write(f"**Trạng thái hiện tại:** `{current_status}`")

        if current_status in ['Đã hủy đơn', 'Đã gaio hàng']:
            st.warning(f"Bạn không thể thay đổi trạng thái của đơn hàng này vì trạng thái hiện tại là '{current_status}'.")
        else:
            statuses = get_order_statuses()
            status_options = statuses.set_index('description')['status_id'].to_dict()
            status_labels = list(status_options.keys())
            selected_status_label = st.selectbox("Chọn trạng thái mới", status_labels)

            if st.button("✅ Cập nhật trạng thái"):
                update_order_status(selected_order_id, status_options[selected_status_label])
                log_admin_activity(st.session_state.admin_id, f"Cập nhật trạng thái đơn hàng {selected_order_id} → {selected_status_label}")
                st.success("Đã cập nhật trạng thái đơn hàng.")
    else:
        st.info("Không có đơn hàng để chọn.")