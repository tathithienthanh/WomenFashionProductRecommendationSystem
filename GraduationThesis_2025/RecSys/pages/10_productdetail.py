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

def get_all_products():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT product_id, name FROM Product")
        return cursor.fetchall()

def get_product_detail(product_id):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM Product WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

        cursor.execute("""
            SELECT c.description 
            FROM ProductHasCategories pc 
            JOIN Category c ON pc.category_id = c.category_id 
            WHERE pc.product_id = %s
        """, (product_id,))
        categories = [row["description"] for row in cursor.fetchall()]
    conn.close()
    return product, categories

def add_to_cart(customer_id, product_id, quantity=1):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT quantity FROM Cart 
            WHERE customer_id = %s AND product_id = %s
        """, (customer_id, product_id))
        existing = cursor.fetchone()

        if existing:
            new_quantity = existing["quantity"] + quantity
            cursor.execute("""
                UPDATE Cart SET quantity = %s 
                WHERE customer_id = %s AND product_id = %s
            """, (new_quantity, customer_id, product_id))
        else:
            cursor.execute("""
                INSERT INTO Cart (customer_id, product_id, quantity) 
                VALUES (%s, %s, %s)
            """, (customer_id, product_id, quantity))
    conn.commit()
    conn.close()

def get_product_reviews(product_id):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT rating, content, created_at
            FROM review
            WHERE product_id = %s
            ORDER BY created_at DESC
        """, (product_id,))
        reviews = cursor.fetchall()
    conn.close()
    return reviews

st.title("📦 Chi tiết sản phẩm")

product_list = get_all_products()
product_options = {f"{p['name']} ({p['product_id']})": p['product_id'] for p in product_list}

selected = st.selectbox("Chọn sản phẩm", options=list(product_options.keys()))

if selected:
    product_id = product_options[selected]
    product, categories = get_product_detail(product_id)

    st.image(product["image_url"], width=250)
    st.markdown(f"### 🛍️ {product['name']}")
    st.markdown(f"**Mô tả:** {product['description']}")
    st.markdown(f"**Giá:** 💸 {product['price']:,} đ")
    if product["discount"]:
        st.markdown(f"**Giảm giá:** {product['discount']}%")
    st.markdown(f"**Số lượng còn:** {product['quantity']}")
    st.markdown(f"**Đã bán:** {product['sold']}")
    st.markdown(f"**Đánh giá:** ⭐ {product['rating']}/5")

    if categories:
        st.markdown("**Danh mục:** " + ", ".join(categories))
    else:
        st.markdown("**Danh mục:** (Không có)")

    if st.button("🛒 Thêm vào giỏ hàng"):
        if "customer_id" not in st.session_state or st.session_state["customer_id"] is None:
            st.warning("🔒 Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng.")
        else:
            add_to_cart(st.session_state["customer_id"], product_id)
            st.success("✅ Đã thêm vào giỏ hàng!")

    st.markdown("---")
    st.subheader("📝 Đánh giá từ người mua")

    reviews = get_product_reviews(product_id)

    if reviews:
        for r in reviews:
            stars = "⭐" * r["rating"] + "☆" * (5 - r["rating"])
            st.markdown(f"- {stars} &nbsp;&nbsp;`{r['created_at'].strftime('%Y-%m-%d %H:%M')}`  \n{r['content']}")
    else:
        st.info("Chưa có đánh giá nào cho sản phẩm này.")
