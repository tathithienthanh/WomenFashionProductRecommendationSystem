# pages/5_home.py
import streamlit as st
import pymysql
import os
import pandas as pd
from NBCF_ItemItem import recommend_items_for_user

# --- Cấu hình ---
PLACEHOLDER_PATH = r"C:\Users\ASUS\Desktop\T\ĐAN_KLTN\getImages\placeholder.jpg"
PRODUCTS_PER_PAGE = 10
INITIAL_PRODUCTS = 10

# --- Kiểm tra đăng nhập ---
if "customer_id" not in st.session_state or st.session_state["customer_id"] is None:
    st.warning("🔒 Vui lòng đăng nhập để truy cập trang này.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Đăng nhập"):
            st.switch_page("pages/2_login.py")
    with col2:
        if st.button("📝 Đăng ký"):
            st.switch_page("pages/1_signin.py")
    st.stop()

# --- Khởi tạo session ---
if "visible_count" not in st.session_state:
    st.session_state.visible_count = INITIAL_PRODUCTS

# --- Kết nối CSDL ---
@st.cache_resource
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

# --- Hàm hiển thị sản phẩm ---
def display_product_card(product, col):
    with col:
        image_path = product.get("image_url", "")
        if not image_path or not os.path.exists(image_path):
            image_path = PLACEHOLDER_PATH
        st.image(image_path, width=150, use_column_width=True)

        st.markdown(f"**{product.get('product_name', 'Sản phẩm')}**")
        st.markdown(f"💰 {product.get('discounted_price', 0):,} VND")
        st.markdown(f"🔥 Đã bán: {product.get('total_sold', 0):,}")
        st.markdown(f"⭐ {product.get('rating', 0):.1f}/5")
        st.markdown(f"📦 {product.get('category_description', 'Chưa rõ')}")

# --- Lấy dữ liệu sản phẩm ---
@st.cache_data(ttl=3600)
def get_all_products():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT 
                        p.product_id,
                        p.name AS product_name,
                        p.price,
                        p.discount,
                        p.price * (1 - IFNULL(p.discount, 0)/100) AS discounted_price,
                        p.sold AS total_sold,
                        p.rating,
                        p.image_url,
                        c.description AS category_description
                    FROM Product p
                    LEFT JOIN ProductHasCategories phc ON p.product_id = phc.product_id
                    LEFT JOIN Category c ON phc.category_id = c.category_id
                """)
                products = cursor.fetchall()

                for p in products:
                    p['rating'] = p['rating'] or 0
                    p['discount'] = p['discount'] or 0
                    p['discounted_price'] = p['discounted_price'] or p['price']
                return products
    except Exception as e:
        st.error(f"Lỗi khi tải sản phẩm: {str(e)}")
        return []

# --- Giao diện chính ---
st.title("🛍️ Trang chủ khách hàng")

# --- Bộ lọc sản phẩm ---
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

all_products = get_all_products()
df_products = pd.DataFrame(all_products)

with filter_col1:
    search_query = st.text_input("🔍 Tìm kiếm", placeholder="Nhập tên sản phẩm")

with filter_col2:
    categories = df_products['category_description'].dropna().unique()
    selected_categories = st.multiselect(
        "🔖 Danh mục",
        options=categories,
        default=categories[:3] if len(categories) > 3 else categories
    )

with filter_col3:
    if not df_products.empty:
        min_price, max_price = st.slider(
            "💰 Khoảng giá",
            min_value=int(df_products['discounted_price'].min()),
            max_value=int(df_products['discounted_price'].max()),
            value=(int(df_products['discounted_price'].min()), 
                   int(df_products['discounted_price'].max()))
        )

with filter_col4:
    if not df_products.empty:
        min_rating = st.slider(
            "🌟 Đánh giá từ",
            min_value=0.0,
            max_value=5.0,
            value=3.0,
            step=0.5
        )

# --- Áp dụng bộ lọc ---
filtered_products = all_products.copy()

if search_query:
    filtered_products = [p for p in filtered_products if search_query.lower() in p['product_name'].lower()]
if selected_categories:
    filtered_products = [p for p in filtered_products if p['category_description'] in selected_categories]
filtered_products = [p for p in filtered_products if min_price <= p['discounted_price'] <= max_price]
filtered_products = [p for p in filtered_products if p['rating'] >= min_rating]

unique_products = {p['product_id']: p for p in filtered_products}
filtered_products = list(unique_products.values())

# --- Gợi ý sản phẩm ---
st.subheader("🎯 Gợi ý cho bạn")
recommendations = recommend_items_for_user(st.session_state["customer_id"], top_n=6)
recommendations = recommendations or filtered_products[:6]

if recommendations:
    cols = st.columns(3)
    for i, product in enumerate(recommendations):
        display_product_card(product, cols[i % 3])
else:
    st.info("Chưa có sản phẩm gợi ý phù hợp.")

# --- Danh sách sản phẩm ---
st.subheader("🔥 Tất cả sản phẩm")
st.write(f"Đang hiển thị {len(filtered_products)} sản phẩm phù hợp")

if filtered_products:
    cols = st.columns(3)
    for i, product in enumerate(filtered_products[:st.session_state.visible_count]):
        display_product_card(product, cols[i % 3])

    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        if st.session_state.visible_count < len(filtered_products):
            if st.button("🔽 Click for more"):
                st.session_state.visible_count += PRODUCTS_PER_PAGE
                st.rerun()
    with col2:
        if st.session_state.visible_count > INITIAL_PRODUCTS:
            if st.button("🔼 Show less"):
                st.session_state.visible_count = INITIAL_PRODUCTS
                st.rerun()
else:
    st.warning("Không tìm thấy sản phẩm nào phù hợp.")

# --- Đăng xuất ---
if st.button("🚪 Đăng xuất"):
    st.session_state.clear()
    st.success("Đăng xuất thành công.")
    st.switch_page("ecommerce_app.py")

# --- CSS tùy chỉnh ---
st.markdown("""
<style>
    [data-testid="stHorizontalBlock"] { gap: 1rem; }
    .stImage { border-radius: 10px; transition: transform 0.2s; }
    .stImage:hover { transform: scale(1.03); }
    div[data-testid="column"] { padding: 10px; }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)
