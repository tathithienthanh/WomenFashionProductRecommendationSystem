import streamlit as st
import pymysql
import re
import random
from email.mime.text import MIMEText

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

def get_customer_profile(customer_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM customer WHERE customer_id = %s", (customer_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def update_customer_info(customer_id, first_name, last_name, email, phone_number, address):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE customer SET
                first_name = %s,
                last_name = %s,
                email = %s,
                phone_number = %s,
                address = %s
            WHERE customer_id = %s
            """
            cursor.execute(sql, (first_name, last_name, email, phone_number, address, customer_id))
        conn.commit()
    finally:
        conn.close()

def send_verification_email(email, code):
    # Giả lập gửi email bằng in mã xác nhận (có thể tích hợp SMTP thật)
    st.session_state.email_verification_code = code
    st.info(f"Mã xác nhận đã được gửi tới {email} (demo: mã là {code})")

st.title("👤 Hồ sơ khách hàng")

if "customer_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập để xem hồ sơ.")
    st.stop()

customer = get_customer_profile(st.session_state.customer_id)

if customer:
    st.subheader("Thông tin cá nhân")

    edit_mode = st.checkbox("✏️ Cập nhật hồ sơ")

    if not edit_mode:
        st.text_input("Mã khách hàng", customer["customer_id"], disabled=True)
        st.text_input("Họ", customer["last_name"], disabled=True)
        st.text_input("Tên", customer["first_name"], disabled=True)
        st.text_input("Email", customer["email"], disabled=True)
        st.text_input("Số điện thoại", customer["phone_number"], disabled=True)
        st.text_area("Địa chỉ", customer["address"], disabled=True)

    else:
        new_last_name = st.text_input("Họ", customer["last_name"])
        new_first_name = st.text_input("Tên", customer["first_name"])
        new_email = st.text_input("Email", customer["email"])
        new_phone = st.text_input("Số điện thoại", customer["phone_number"])
        new_address = st.text_area("Địa chỉ", customer["address"])

        if st.button("📨 Gửi mã xác nhận"):
            if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
                st.error("❌ Email không hợp lệ.")
            else:
                verification_code = str(random.randint(100000, 999999))
                send_verification_email(new_email, verification_code)
                st.session_state.awaiting_verification = {
                    "last_name": new_last_name,
                    "first_name": new_first_name,
                    "email": new_email,
                    "phone_number": new_phone,
                    "address": new_address
                }

        if "awaiting_verification" in st.session_state:
            st.success("📩 Vui lòng nhập mã xác nhận đã được gửi đến email của bạn.")
            input_code = st.text_input("Nhập mã xác nhận")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Xác nhận"):
                    if input_code == st.session_state.get("email_verification_code", ""):
                        data = st.session_state.awaiting_verification
                        update_customer_info(
                            st.session_state.customer_id,
                            data["first_name"],
                            data["last_name"],
                            data["email"],
                            data["phone_number"],
                            data["address"]
                        )
                        st.success("✅ Cập nhật hồ sơ thành công.")
                        del st.session_state.awaiting_verification
                        del st.session_state.email_verification_code
                        st.rerun()
                    else:
                        st.error("❌ Mã xác nhận không đúng. Vui lòng thử lại.")
            with col2:
                if st.button("🔁 Gửi lại mã"):
                    new_code = str(random.randint(100000, 999999))
                    send_verification_email(new_email, new_code)
    if st.button("🏠Về trang chủ"):
        st.switch_page('pages/5_home.py')
else:
    st.error("Không tìm thấy thông tin khách hàng.")