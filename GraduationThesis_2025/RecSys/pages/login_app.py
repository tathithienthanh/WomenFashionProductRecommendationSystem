import streamlit as st
import pymysql
import hashlib

# --- Hàm kết nối cơ sở dữ liệu ---
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

# --- Hàm băm mật khẩu ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Hàm kiểm tra thông tin đăng nhập ---
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

# --- Giao diện đăng nhập ---
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
                st.session_state["logged_in_user"] = user  # nếu bạn cần thêm thông tin sau này
                st.success("🎉 Đăng nhập thành công!")
                st.switch_page("home_app.py")
            else:
                st.error("❌ Sai ID hoặc mật khẩu. Vui lòng thử lại.")
