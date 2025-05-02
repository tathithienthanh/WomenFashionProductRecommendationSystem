import streamlit as st
import pymysql
import sys
import os

from NBCF_ItemItem import recommend_items_for_user  # Đảm bảo file này nằm cùng thư mục hoặc được import đúng

# --- Khởi tạo session key nếu chưa có ---
if "customer_id" not in st.session_state:
    st.session_state["customer_id"] = None

# --- Nếu chưa đăng nhập, hiển thị cảnh báo và nút chuyển trang ---
if st.session_state["customer_id"] is None:
    st.warning("🔒 Vui lòng đăng nhập để xem nội dung.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Đăng nhập"):
            st.switch_page("pages/login_app.py")
    with col2:
        if st.button("📝 Đăng ký"):
            st.switch_page("pages/signin_app.py")
    st.stop()

# --- Hàm kết nối CSDL ---
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

# --- Tiêu đề chính ---
st.title("🏠 Trang chủ cá nhân")

# --- Gợi ý sản phẩm cá nhân hóa ---
st.subheader("🎯 Gợi ý cho bạn")

customer_id = st.session_state["customer_id"]
recommendations = recommend_items_for_user(customer_id, top_n=6)

# Nếu không có gợi ý từ collaborative filtering →  bảng TopSellingProducts
if not recommendations:
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM TopSellingProducts ORDER BY sold DESC LIMIT 6")
            recommendations = cursor.fetchall()
    finally:
        conn.close()

# Hiển thị danh sách sản phẩm
cols = st.columns(3)
for i, product in enumerate(recommendations):
    with cols[i % 3]:
        st.image(product.get("image_url", ""), width=150)
        st.markdown(f"**{product.get('name', 'Sản phẩm')}**")
        st.markdown(f"💸 {product.get('price', 0)} đ")
        if product.get("rating"):
            st.markdown(f"⭐ {product['rating']}/5")

# --- Hiển thị thêm sản phẩm nổi bật ---
st.subheader("🔥 Sản phẩm nổi bật")

def get_top_products(limit=6):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM Product ORDER BY sold DESC LIMIT %s", (limit,)
            )
            return cursor.fetchall()
    finally:
        conn.close()

top_products = get_top_products()

cols = st.columns(3)
for i, product in enumerate(top_products):
    with cols[i % 3]:
        st.image(product["image_url"], width=150)
        st.markdown(f"**{product['name']}**")
        st.markdown(f"💸 {product['price']} đ")
        if product.get("rating"):
            st.markdown(f"⭐ {product['rating']}/5")

# --- Nút đăng xuất ---
if st.button("🚪 Đăng xuất"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Bạn đã đăng xuất.")
    st.switch_page("ecommerce_app.py")
