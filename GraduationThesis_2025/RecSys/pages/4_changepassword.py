import streamlit as st
import pymysql
import hashlib

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_id(customer_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM customer WHERE customer_id = %s", (customer_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def update_customer_password(customer_id, new_password):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE customer SET password = %s WHERE customer_id = %s", (new_password, customer_id))
        conn.commit()
    finally:
        conn.close()

st.title("🔑 Đổi mật khẩu")

if "customer_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập để sử dụng chức năng này.")
    st.stop()


if "step_change" not in st.session_state:
    st.session_state.step_change = 1

if st.session_state.step_change == 1:
    with st.form("current_pass_form"):
        current_pass = st.text_input("🔒 Nhập mật khẩu hiện tại", type="password")
        check = st.form_submit_button("Tiếp tục")

        if check:
            user = get_user_by_id(st.session_state.customer_id)
            if user and user["password"] == hash_password(current_pass):
                st.session_state.step_change = 2
                st.rerun()
            else:
                st.error("❌ Mật khẩu hiện tại không đúng.")
    
    if st.button("🏠Về trang chủ"):
        st.switch_page('pages/5_home.py')

elif st.session_state.step_change == 2:
    with st.form("new_pass_form"):
        new_pass = st.text_input("🔐 Nhập mật khẩu mới", type="password")
        confirm_pass = st.text_input("🔐 Xác nhận mật khẩu mới", type="password")
        submit = st.form_submit_button("Cập nhật mật khẩu")

        if submit:
            if not new_pass or not confirm_pass:
                st.error("Vui lòng nhập đầy đủ thông tin.")
            elif new_pass != confirm_pass:
                st.error("❌ Mật khẩu xác nhận không khớp.")
            else:
                try:
                    update_customer_password(st.session_state.customer_id, new_pass)
                    st.success("✅ Cập nhật mật khẩu thành công.")
                    st.info("🔁 Vui lòng đăng nhập lại.")
                    st.session_state.clear()
                    st.switch_page("pages/2_login.py")
                except pymysql.err.OperationalError as e:
                    st.error(f"❌ Lỗi: {e.args[1]}")
