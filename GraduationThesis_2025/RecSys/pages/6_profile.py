import streamlit as st
import pymysql

# --- Hàm kết nối CSDL ---
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

# --- Hàm lấy thông tin khách hàng ---
def get_customer_profile(customer_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM customer WHERE customer_id = %s", (customer_id,))
            return cursor.fetchone()
    finally:
        conn.close()

# --- Giao diện hồ sơ khách hàng ---
st.title("👤 Hồ sơ khách hàng")

if "customer_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập để xem hồ sơ.")
    st.stop()

# --- Lấy dữ liệu từ CSDL ---
customer = get_customer_profile(st.session_state.customer_id)

if customer:
    st.subheader("Thông tin cá nhân")
    
    st.text_input("Mã khách hàng", customer["customer_id"], disabled=True)
    st.text_input("Họ", customer["last_name"], disabled=True)
    st.text_input("Tên", customer["first_name"], disabled=True)
    st.text_input("Email", customer["email"], disabled=True)
    st.text_input("Số điện thoại", customer["phone_number"], disabled=True)
    st.text_area("Địa chỉ", customer["address"], disabled=True)
else:
    st.error("Không tìm thấy thông tin khách hàng.")
