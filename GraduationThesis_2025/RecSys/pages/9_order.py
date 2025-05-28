import streamlit as st
import pymysql
import random
import os
from datetime import datetime
from typing import List, Dict
from NBCF_ItemItem import ItemItemRecommender, recommend_items_for_user, get_connection, load_interaction_data

placeholder_path = 'C:/Users/ASUS/Desktop/T/ĐAN_KLTN/getImages/placeholder.jpg'

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

def fetch_address(customer_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT address FROM customer WHERE customer_id = %s", (customer_id,))
            result = cursor.fetchone()
            return result["address"] if result else ""
    finally:
        conn.close()

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

def fetch_payment_methods():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT payment_id, description FROM payment")
            return cursor.fetchall()
    finally:
        conn.close()

def place_order(customer_id, cart_items, payment_method, address):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT MAX(CAST(SUBSTRING(order_id, 2) AS UNSIGNED)) AS max_id FROM orders")
            result = cursor.fetchone()
            max_order_id = result["max_id"]
            new_order_id = f"O{(max_order_id + 1):04d}" if max_order_id is not None else "O0001"

            cursor.execute(""" 
                INSERT INTO orders (order_id, customer_id, order_status, order_date, address, total_price, payment)
                VALUES (%s, %s, 'PENDING', NOW(), %s, 0, %s)
            """, (new_order_id, customer_id, address, payment_method))
            
            total = 0
            for item in cart_items:
                if "product_id" not in item:
                    print("Lỗi: item không có product_id:", item)
                    continue 

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

def get_random_products(n=5):
    n = int(n)
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = f'''
                SELECT p.product_id, p.name, p.price, p.image_url, p.sold, p.rating, GROUP_CONCAT(c.description SEPARATOR ', ') AS category_description
                FROM product p
                LEFT JOIN producthascategories pc ON p.product_id = pc.product_id
                LEFT JOIN category c ON pc.category_id = c.category_id
                GROUP BY p.product_id
                ORDER BY RAND()
                LIMIT {n}
            '''
            cursor.execute(query)
            return cursor.fetchall()
    finally:
        conn.close()

def get_similar_products(product_id: str, top_k: int = 5) -> List[Dict]:
    df = load_interaction_data()
    if df.empty:
        return []

    model = ItemItemRecommender(df[['customer_id', 'product_id', 'rating']])
    model.prepare_matrices()
    similar_ids = model.get_similar_items(product_id, top_k)

    results = []
    for pid in similar_ids:
        row = df[df['product_id'] == pid].iloc[0].to_dict()
        price = row.get('price', 0)
        discount = row.get('discount', 0)
        final_price = price * (1 - discount / 100) if discount else price
        results.append({
            "product_id": pid,
            "name": row.get('name', ''),
            "image_url": row.get('image_url', ''),
            "price": price,
            "discounted_price": final_price,
            "discount": discount,
            "sold": row.get('sold', 0),
            "quantity": row.get('quantity', 0),
            "rating": row.get('avg_rating', 0),
            "category": {
                "id": row.get('category_id'),
                "description": row.get('category_description', '')
            }
        })
    return results

if st.button("🏠Về trang chủ"):
    st.switch_page("pages/5_home.py")

if "logged_in_user" not in st.session_state:
    st.warning("Vui lòng đăng nhập để đặt hàng.")
    st.stop()

customer_id = st.session_state["customer_id"]
st.markdown("---")
st.title("🧾 Xác nhận đơn hàng")

cart_items = fetch_cart(customer_id)

if not cart_items:
    st.info("Danh sách các đơn hàng của bạn đang trống.")
    st.stop()

total = 0
for item in cart_items:
    st.write(f"- **{item['name']}** x {item['quantity']} = {item['price'] * item['quantity']:,.0f} VND")
    total += item['price'] * item['quantity']

st.markdown("---")
st.subheader(f"**Tổng cộng: {total:,.0f} VND**")

default_address = fetch_address(customer_id)
use_new_address = st.checkbox("Tôi muốn thay đổi địa chỉ giao hàng")
if use_new_address:
    delivery_address = st.text_input("Nhập địa chỉ giao hàng", value=default_address)
else:
    delivery_address = default_address

st.markdown("### 💳 Chọn phương thức thanh toán")
payments = fetch_payment_methods()
payment_options = {p['description']: p['payment_id'] for p in payments}
selected_description = st.selectbox("Phương thức thanh toán", list(payment_options.keys()))
selected_payment_id = payment_options[selected_description]

if st.button("✅ Xác nhận đặt hàng"):
    order_id = place_order(customer_id, cart_items, selected_payment_id, delivery_address)
    st.success(f"🎉 Đơn hàng #{order_id} đã được đặt thành công với phương thức thanh toán **{selected_description}**!")

st.markdown("---")
st.subheader("🛒 Có thể bạn sẽ thích")
num_cols = 5

product_ids = [item['product_id'] for item in cart_items]
suggested = []
for pid in product_ids[:2]:
    suggested.extend(get_similar_products(pid, 3))
unique_suggested = {p['product_id']: p for p in suggested}
suggested = list(unique_suggested.values())[:5]
print(suggested)
cols = st.columns(num_cols)
for idx, p in enumerate(suggested):
    image_path = p.get('image_url') or placeholder_path
    if not os.path.exists(image_path):
        image_path = placeholder_path

    with cols[idx]:
        st.image(image_path, width=150)
        st.markdown(f"**{p.get('name', 'Không rõ tên')}**")
        st.markdown(f"💰 {p.get('discounted_price', p.get('price', 0)):,.0f} VND")
        st.markdown(f"🔥 Đã bán: {p.get('sold', 'N/A')}")
        st.markdown(f"⭐ {p.get('rating', 'N/A')} sao")
        category = p.get('category', {})
        st.markdown(f"📦 Danh mục: {category.get('description', 'Không rõ')}")
        if st.button("🔎 Chi tiết", key=f"detail_{p['product_id']}"):
            st.session_state['selected_product_id'] = p['product_id']
            st.switch_page("pages/10_productdetail.py")


suggested = get_random_products(5)
print(suggested)
cols = st.columns(num_cols)
for idx, p in enumerate(suggested):
    image_path = p.get('image_url') or placeholder_path
    if not os.path.exists(image_path):
        image_path = placeholder_path

    with cols[idx]:
        st.image(image_path, width=150)
        st.markdown(f"**{p.get('name', 'Không rõ tên')}**")
        st.markdown(f"💰 {p.get('discounted_price', p.get('price', 0)):,.0f} VND")
        st.markdown(f"🔥 Đã bán: {p.get('sold', 'N/A')}")
        st.markdown(f"⭐ {p.get('rating', 'N/A')} sao")
        st.markdown(f"📦 Danh mục: {p.get('category_description', {'Không rõ'})}")
        if st.button("🔎 Chi tiết", key=f"detail_{p['product_id']}"):
            st.session_state['selected_product_id'] = p['product_id']
            st.switch_page("pages/10_productdetail.py")