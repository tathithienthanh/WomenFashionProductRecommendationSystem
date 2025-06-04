import streamlit as st
import random
import pymysql

if "step" not in st.session_state:
    st.session_state.step = 1
if "confirm_code" not in st.session_state:
    st.session_state.confirm_code = None
if "form_data" not in st.session_state:
    st.session_state.form_data = {}
if "resend_requested" not in st.session_state:
    st.session_state.resend_requested = False

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

def email_exists(email):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Customer WHERE email = %s", (email,))
            return cursor.fetchone() is not None
    finally:
        conn.close()

def insert_user(last_name, first_name, email, password, phone_number, address):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM Customer")
            result = cursor.fetchone()
            next_id = result["total"] + 1
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
    return customer_id

def reset_code():
    st.session_state.confirm_code = str(random.randint(100000, 999999))
    st.session_state.resend_requested = False

if st.session_state.step == 1:
    st.title("📝 Đăng ký tài khoản")

    with st.form("register_form"):
        last_name = st.text_input("👤 Họ")
        first_name = st.text_input("👤 Tên")
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Mật khẩu", type="password")
        phone = st.text_input("📱 Số điện thoại")
        address = st.text_input("🏠 Địa chỉ")
        submit = st.form_submit_button("Đăng ký")

        if submit:
            if not all([last_name, first_name, email, password, phone, address]):
                st.error("Vui lòng nhập đầy đủ thông tin.")
            elif len(password) < 6:
                st.error("Mật khẩu phải có ít nhất 6 ký tự.")
            elif not "@" in email:
                st.error("Email không hợp lệ.")
            elif not phone.isdigit() or len(phone) < 9:
                st.error("Số điện thoại không hợp lệ.")
            elif email_exists(email):
                st.error("Email đã được sử dụng.")
            else:
                st.session_state.form_data = {
                    "last_name": last_name,
                    "first_name": first_name,
                    "email": email,
                    "password": password,
                    "phone_number": phone,
                    "address": address
                }
                reset_code()
                st.session_state.step = 2
                st.rerun()
        
    if st.button("❓Đã có tài khoản?"):
        st.switch_page('pages/2_login.py')
        
    if st.button("🏠Về trang chủ"):
        st.switch_page('ecommerce_app.py')

elif st.session_state.step == 2:
    st.success("✅ Mã xác nhận đã gửi tới email (giả lập).")
    st.info(f"🔑 Mã xác nhận của bạn là: **{st.session_state.confirm_code}**")

    with st.form("verify_form"):
        input_code = st.text_input("Nhập mã xác nhận:")
        verify = st.form_submit_button("Xác nhận")

        if verify:
            if input_code == st.session_state.confirm_code:
                data = st.session_state.form_data
                user_id = insert_user(data["last_name"], data["first_name"], data["email"], data["password"], data["phone_number"], data["address"])
                st.session_state.user_id = user_id
                st.session_state.step = 3
                st.rerun()
            else:
                st.error("Mã xác nhận không đúng.")

    if st.button("📩 Gửi lại mã"):
        reset_code()
        st.session_state.resend_requested = True
        st.rerun()

elif st.session_state.step == 3:
    st.balloons()
    st.success(f"🎉 Đăng ký thành công tài khoản **{st.session_state.user_id}**!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Đăng ký tài khoản khác", key="register_another"):
            st.session_state.step = 1
            st.session_state.form_data = {}
            st.rerun()
    with col2:
        if st.button("🏠 Trang chủ", key="go_home"):
            st.switch_page("pages/5_home.py")