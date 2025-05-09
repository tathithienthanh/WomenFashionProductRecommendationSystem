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

def validate_admin_login(admin_id, password):
    hashed = hash_password(password)
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM Admin WHERE admin_id = %s AND password = %s",
                (admin_id, hashed)
            )
            return cursor.fetchone()
    finally:
        conn.close()

st.title("🛠️ Đăng nhập quản trị viên")

with st.form("admin_login_form"):
    admin_id = st.text_input("🆔 Mã Admin (VD: A001)")
    password = st.text_input("🔒 Mật khẩu", type="password")
    submit = st.form_submit_button("Đăng nhập")

    if submit:
        if not admin_id or not password:
            st.error("Vui lòng nhập đầy đủ thông tin.")
        else:
            admin = validate_admin_login(admin_id, password)
            if admin:
                st.session_state["admin_id"] = admin_id
                st.session_state["logged_in_admin"] = admin
                st.success("🎉 Đăng nhập thành công!")
                st.switch_page("pages/12_report.py")
            else:
                st.error("❌ Sai ID hoặc mật khẩu. Vui lòng thử lại.")