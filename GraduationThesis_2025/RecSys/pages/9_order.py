import streamlit as st
import pymysql
import random
from datetime import datetime

# --- Kết nối CSDL ---
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

# --- Lấy giỏ hàng ---
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

# --- Lấy phương thức thanh toán ---
def fetch_payment_methods():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT payment_id, description FROM payment")
            return cursor.fetchall()
    finally:
        conn.close()

# --- Đặt hàng ---
def place_order(customer_id, cart_items, payment_method):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Lấy ID đơn hàng lớn nhất hiện tại
            cursor.execute("SELECT MAX(CAST(SUBSTRING(order_id, 2) AS UNSIGNED)) AS max_id FROM orders")
            result = cursor.fetchone()
            max_order_id = result["max_id"]
            new_order_id = f"O{(max_order_id + 1):04d}" if max_order_id is not None else "O0001"

            # Tạo đơn hàng mới
            cursor.execute(""" 
                INSERT INTO orders (order_id, customer_id, order_status, order_date, address, total_price, payment)
                VALUES (%s, %s, 'SHIPPED', NOW(), '', 0, %s)
            """, (new_order_id, customer_id, payment_method))
            
            total = 0
            for item in cart_items:
                total += item["price"] * item["quantity"]
                cursor.execute("""
                    INSERT INTO orderdetail (order_id, product_id, quantity, unit_price, discount)
                    VALUES (%s, %s, %s, %s, 0)
                """, (new_order_id, item["product_id"], item["quantity"], item["price"]))

            cursor.execute("UPDATE orders SET total_price = %s WHERE order_id = %s", (total, new_order_id))
            cursor.execute("DELETE FROM Cart WHERE customer_id = %s", (customer_id,))
            conn.commit()
            return new_order_id
    finally:
        conn.close()

# --- Lấy sản phẩm trong đơn hàng ---
def get_order_products(order_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT od.product_id, p.name
                FROM orderdetail od
                JOIN product p ON od.product_id = p.product_id
                WHERE od.order_id = %s
            """, (order_id,))
            return cursor.fetchall()
    finally:
        conn.close()

# --- Thêm đánh giá ---
def submit_review(customer_id, product_id, rating, content):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO review (customer_id, product_id, rating, content, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (customer_id, product_id, rating, content, datetime.now()))
            conn.commit()
    finally:
        conn.close()

# --- Gợi ý ngẫu nhiên sản phẩm ---
def get_random_products(limit=5):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT product_id, name, price FROM Product")
            products = cursor.fetchall()
            return random.sample(products, min(limit, len(products)))
    finally:
        conn.close()

# --- Kiểm tra đăng nhập ---
if "logged_in_user" not in st.session_state:
    st.warning("Vui lòng đăng nhập để đặt hàng.")
    st.stop()

customer_id = st.session_state["customer_id"]
st.title("🧾 Xác nhận đơn hàng")

# --- Hiển thị giỏ hàng ---
cart_items = fetch_cart(customer_id)

if not cart_items:
    st.info("Giỏ hàng của bạn đang trống.")
    st.stop()

# Hiển thị sản phẩm trong giỏ hàng
total = 0
for item in cart_items:
    st.write(f"- **{item['name']}** x {item['quantity']} = {item['price'] * item['quantity']:,.0f} đ")
    total += item['price'] * item['quantity']

st.markdown("---")
st.subheader(f"**Tổng cộng: {total:,.0f} đ**")

# --- Chọn phương thức thanh toán ---
st.markdown("### 💳 Chọn phương thức thanh toán")
payments = fetch_payment_methods()
payment_options = {p['description']: p['payment_id'] for p in payments}
selected_description = st.selectbox("Phương thức thanh toán", list(payment_options.keys()))
selected_payment_id = payment_options[selected_description]

if st.button("✅ Xác nhận đặt hàng"):
    order_id = place_order(customer_id, cart_items, selected_payment_id)
    st.success(f"🎉 Đơn hàng #{order_id} đã được đặt thành công với phương thức thanh toán **{selected_description}**!")

    st.markdown("---")
    st.subheader("🛍 Có thể bạn sẽ thích")

    suggested = get_random_products(5)
    for sp in suggested:
        st.markdown(f"- **{sp['name']}** - {sp['price']:,.0f} đ")

    st.markdown("---")
    st.subheader("✍️ Viết đánh giá sản phẩm")

    products = get_order_products(order_id)
    for product in products:
        st.markdown(f"**🧾 {product['name']}**")

        with st.form(f"review_form_{product['product_id']}"):
            rating = st.slider("Đánh giá (1-5 ⭐)", 1, 5, 5)
            content = st.text_area("Nội dung đánh giá")
            submit = st.form_submit_button("Gửi đánh giá")

            if submit:
                submit_review(customer_id, product['product_id'], rating, content)
                st.success("🎉 Đánh giá của bạn đã được gửi!")
