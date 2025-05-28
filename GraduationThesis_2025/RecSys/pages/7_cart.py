import streamlit as st
import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

def fetch_cart(customer_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT Cart.product_id, Product.name, Product.price, Cart.quantity
                FROM Cart
                JOIN Product ON Cart.product_id = Product.product_id
                WHERE Cart.customer_id = %s
            """, (customer_id,))
            return cursor.fetchall()
    finally:
        conn.close()

def remove_from_cart(customer_id, product_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM Cart
                WHERE customer_id = %s AND product_id = %s
            """, (customer_id, product_id))
            conn.commit()
    finally:
        conn.close()

if "logged_in_user" not in st.session_state:
    st.warning("Vui lòng đăng nhập để xem giỏ hàng.")
    st.stop()
else:
    customer_id = st.session_state["customer_id"]

st.title("🛒 Giỏ hàng của bạn")

cart_items = fetch_cart(customer_id)

if not cart_items:
    st.info("Giỏ hàng của bạn đang trống.")
else:
    total = 0
    for item in cart_items:
        col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
        with col1:
            st.write(f"**{item['name']}**")
        with col2:
            st.write(f"Số lượng: {item['quantity']}")
        with col3:
            subtotal = item['price'] * item['quantity']
            st.write(f"Giá: {subtotal:,.0f} đ")
            total += subtotal
        with col4:
            if st.button("❌ Xóa", key=f"remove_{item['product_id']}"):
                remove_from_cart(customer_id, item['product_id'])
                st.rerun()

    st.markdown("---")
    st.subheader(f"**Tổng tiền: {total:,.0f} đ**")

    if st.button("🧾 Tiến hành đặt hàng"):
        st.switch_page('pages/9_order.py')
    
    st.markdown("---")
    if st.button("🏠Về trang chủ"):
        st.switch_page('pages/5_home.py')