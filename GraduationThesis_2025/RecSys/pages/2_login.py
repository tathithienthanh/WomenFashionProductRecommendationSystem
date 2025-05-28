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

def validate_login(customer_id, password):
    hashed = hash_password(password)
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM Customer WHERE customer_id = %s AND password = %s",
                (customer_id, hashed)
            )
            return cursor.fetchone()
    finally:
        conn.close()

st.title("🔐 Đăng nhập hệ thống")

with st.form("login_form"):
    customer_id = st.text_input("🆔 Mã khách hàng (VD: C001)")
    password = st.text_input("🔒 Mật khẩu", type="password")
    submit = st.form_submit_button("Đăng nhập")

    if submit:
        if not customer_id or not password:
            st.error("Vui lòng nhập đầy đủ thông tin.")
        else:
            user = validate_login(customer_id, password)
            if user:
                st.session_state["customer_id"] = customer_id
                st.session_state["logged_in_user"] = user
                st.success("🎉 Đăng nhập thành công!")
                st.switch_page("pages/5_home.py")
            else:
                st.error("❌ Sai ID hoặc mật khẩu. Vui lòng thử lại.")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("❓ Quên mật khẩu?"):
        st.switch_page("pages/3_forgetpassword.py")
with col2:
    if st.button("❓ Chưa có tài khoản?"):
        st.switch_page("pages/1_signin.py")

if st.button("🏠Về trang chủ"):
        st.switch_page('ecommerce_app.py')