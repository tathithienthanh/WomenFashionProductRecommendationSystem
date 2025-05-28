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
    admin_id = st.session_state["admin_id"]
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

def list_users():
    conn = get_connection()
    try:
        df = pd.read_sql(
            "SELECT customer_id, first_name, last_name, email, phone_number, address FROM Customer", conn)
        return df
    finally:
        conn.close()

def add_user(first_name, last_name, email, password, phone_number=None, address=None):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM Customer")
            result = cursor.fetchone()
            next_id = result[0] + 1
            customer_id = f"C{next_id:03}"
            
            cursor.execute( 
                """
                INSERT INTO Customer (customer_id, last_name, first_name, email, password, phone_number, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (customer_id, last_name, first_name, email, password, phone_number, address)
            )
        conn.commit()
    finally:
        conn.close()

def update_user(customer_id, first_name, last_name, phone=None, address=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
            UPDATE Customer
            SET first_name = %s, last_name = %s, phone_number = %s, address = %s
            WHERE customer_id = %s
            """
            cursor.execute(query, (first_name, last_name, phone, address, customer_id))
        conn.commit()
    finally:
        conn.close()

def delete_user(customer_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Customer WHERE customer_id = %s", (customer_id,))
        conn.commit()
    finally:
        conn.close()

st.title("👥 Quản lý người dùng")

if "admin_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập với vai trò admin để truy cập trang này.")
    st.stop()

if not has_permission("MANAGE_USERS"):
    st.warning("Bạn không có quyền truy cập chức năng này.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📋 Danh sách", "➕ Thêm", "✏️ Cập nhật / ❌ Xoá"])

with tab1:
    st.subheader("📋 Danh sách người dùng")
    df = list_users()
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("➕ Thêm người dùng")
    with st.form("add_user_form"):
        fname = st.text_input("Họ")
        lname = st.text_input("Tên")
        email = st.text_input("Email")
        phone = st.text_input("Số điện thoại")
        address = st.text_input("Địa chỉ")
        submitted = st.form_submit_button("Thêm")
        if submitted:
            if fname and lname and email:
                add_user(fname, lname, email, 'Abcxyz@123', phone, address)
                st.success("Đã thêm người dùng thành công!")
                log_admin_activity(st.session_state.admin_id, 'Thêm người dùng thành công')
            else:
                st.error("Vui lòng nhập đầy đủ thông tin.")
                log_admin_activity(st.session_state.admin_id, 'Thêm người dùng không thành công')

with tab3:
    st.subheader("✏️ Cập nhật / ❌ Xoá")
    df = list_users()
    if not df.empty:
        selected_user = st.selectbox("Chọn người dùng", df["customer_id"].tolist())
        user_data = df[df["customer_id"] == selected_user].iloc[0]

        with st.form("update_user_form"):
            fname = st.text_input("Họ", value=user_data["first_name"])
            lname = st.text_input("Tên", value=user_data["last_name"])
            phone = st.text_input("SĐT", value=user_data["phone_number"])
            address = st.text_input("Địa chỉ", value=user_data["address"])
            col1, col2 = st.columns(2)
            if col1.form_submit_button("Cập nhật"):
                update_user(selected_user, fname, lname, phone, address)
                st.success("Cập nhật thành công!")
                log_admin_activity(st.session_state.admin_id, 'Cập nhật thông tin người dùng thành công')
            if col2.form_submit_button("❌ Xoá người dùng"):
                delete_user(selected_user)
                st.warning("Đã xoá người dùng.")
                log_admin_activity(st.session_state.admin_id, 'Xóa thông tin người dùng thành công')
    else:
        st.info("Không có người dùng nào trong hệ thống.")

st.markdown("---")
if st.button("🏠Về trang chủ"):
    st.switch_page("pages/17_homeadmin.py")