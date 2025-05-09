import streamlit as st
import pymysql
import random
import string

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

def get_customer_by_email(email):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM customer WHERE email = %s", (email,))
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

def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

if "customer_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập để sử dụng chức năng này.")
    st.stop()

if "step" not in st.session_state:
    st.session_state.step = 1
if "confirm_code" not in st.session_state:
    st.session_state.confirm_code = None
if "customer_id" not in st.session_state:
    st.session_state.customer_id = None

st.title("🔐 Quên mật khẩu")

if st.session_state.step == 1:
    with st.form("email_form"):
        email = st.text_input("📧 Nhập email đã đăng ký:")
        submit_email = st.form_submit_button("Gửi mã xác nhận")

        if submit_email:
            user = get_customer_by_email(email)
            if user:
                st.session_state.confirm_code = generate_code()
                st.session_state.customer_id = user["customer_id"]
                st.session_state.step = 2
                st.success("✅ Mã xác nhận đã được gửi tới email (giả lập).")
                st.rerun()
            else:
                st.error("❌ Email không tồn tại.")

elif st.session_state.step == 2:
    st.success("✅ Mã xác nhận đã gửi tới email (giả lập).")
    st.info(f"🔑 Mã xác nhận của bạn là: **{st.session_state.confirm_code}**")

    with st.form("code_form"):
        input_code = st.text_input("Nhập mã xác nhận:")
        submit_code = st.form_submit_button("Xác nhận")

        if submit_code:
            if input_code == st.session_state.confirm_code:
                st.session_state.step = 3
                st.rerun()
            else:
                st.error("❌ Mã xác nhận không đúng.")

    if st.button("📩 Gửi lại mã"):
        st.session_state.confirm_code = generate_code()
        st.success("✅ Mã mới đã được tạo.")
        st.rerun()

elif st.session_state.step == 3:
    with st.form("new_pass_form"):
        new_pass = st.text_input("🔐 Nhập mật khẩu mới:", type="password")
        confirm_pass = st.text_input("🔐 Xác nhận mật khẩu:", type="password")
        submit_pass = st.form_submit_button("Đổi mật khẩu")

        if submit_pass:
            if not new_pass or not confirm_pass:
                st.error("❌ Vui lòng nhập đầy đủ thông tin.")
            elif new_pass != confirm_pass:
                st.error("❌ Mật khẩu không khớp.")
            else:
                try:
                    update_customer_password(st.session_state.customer_id, new_pass)
                    st.success("🎉 Đổi mật khẩu thành công!")
                    st.session_state.step = 4
                except pymysql.err.OperationalError as e:
                    st.error(f"❌ Lỗi: {e.args[1]}")

elif st.session_state.step == 4:
    st.success("✅ Bạn đã đổi mật khẩu thành công. Vui lòng đăng nhập lại.")
    if st.button("🔙 Quay lại trang đăng nhập"):
        st.session_state.clear()
        st.switch_page("2_login.py")