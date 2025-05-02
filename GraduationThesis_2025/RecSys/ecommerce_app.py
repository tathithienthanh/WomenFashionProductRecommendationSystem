import streamlit as st
import subprocess
import pandas as pd
import pymysql
import os

# Giao diện cho Sign In và Log In
st.markdown("""
    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-bottom: 20px;">
        <form action="?signin=true" method="get">
            <button style="padding: 6px 12px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;">Sign In</button>
        </form>
        <form action="?login=true" method="get">
            <button style="padding: 6px 12px; background-color: #2196F3; color: white; border: none; border-radius: 5px;">Log In</button>
        </form>
    </div>
""", unsafe_allow_html=True)

# Đọc query parameters mới
query_params = st.query_params
if "signin" in query_params:
    st.switch_page("pages/signin_app.py")
elif "login" in query_params:
    st.switch_page("pages/login_app.py")

# Kết nối tới MySQL và lấy dữ liệu sản phẩm
try:
    image_dir = 'C:/Users/ASUS/Desktop/T/ĐAN_KLTN/getImages'
    placeholder_path = os.path.join(image_dir, 'placeholder.jpg')

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce"
    )

    query = """
    SELECT t.product_id, 
        t.product_name, 
        t.discounted_price, 
        t.total_sold, 
        t.avg_rating, 
        p.image_url,
        c.category_id,
        c.description AS category_description
    FROM TopSellingProducts t
    JOIN Product p ON t.product_id = p.product_id
    JOIN ProductHasCategories phc ON p.product_id = phc.product_id
    JOIN Category c ON phc.category_id = c.category_id
    """
    df_top = pd.read_sql(query, conn)

except pymysql.Error as e:
    st.error(f"Lỗi MySQL: {e}")
except Exception as e:
    st.error(f"Lỗi khác: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()

# Xử lý trùng lặp sản phẩm
df_top = df_top.drop_duplicates(subset='product_id')

# Khởi tạo số lượng sản phẩm hiển thị mặc định
if 'visible_count' not in st.session_state:
    st.session_state.visible_count = 10

# Bộ lọc tìm kiếm
search_query = st.text_input("🔍 Tìm kiếm sản phẩm", "")

# Bộ lọc danh mục
categories = df_top['category_description'].unique()
selected_categories = st.multiselect("🔖 Lọc theo danh mục", categories, default=categories)

# Bộ lọc số sao
if not df_top.empty:
    min_rating_value = df_top['avg_rating'].min()
    max_rating_value = df_top['avg_rating'].max()

    min_rating, max_rating = st.slider(
        "🌟 Lọc theo đánh giá sao",
        min_value=float(min_rating_value),
        max_value=float(max_rating_value),
        value=(float(min_rating_value), float(max_rating_value)),
        step=0.1
    )

# Bộ lọc giá
min_price, max_price = st.slider(
    "💰 Lọc theo giá",
    min_value=int(df_top['discounted_price'].min()),
    max_value=int(df_top['discounted_price'].max()),
    value=(int(df_top['discounted_price'].min()), int(df_top['discounted_price'].max()))
)

# Áp dụng bộ lọc
if not df_top.empty:
    if search_query:
        df_top = df_top[df_top['product_name'].str.contains(search_query, case=False, na=False)]

    if selected_categories:
        df_top = df_top[df_top['category_description'].isin(selected_categories)]

    df_top = df_top[(df_top['avg_rating'] >= min_rating) & (df_top['avg_rating'] <= max_rating)]
    df_top = df_top[(df_top['discounted_price'] >= min_price) & (df_top['discounted_price'] <= max_price)]

# Hiển thị dữ liệu sản phẩm
if not df_top.empty:
    st.title("🛒 Sản Phẩm Hot!!!")

    num_cols = 5
    num_show = st.session_state.visible_count

    for i in range(0, min(num_show, len(df_top)), num_cols):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            idx = i + j
            if idx < len(df_top):
                product = df_top.iloc[idx]
                image_path = product['image_url']
                if not os.path.exists(image_path):
                    image_path = placeholder_path

                with cols[j]:
                    st.image(image_path, width=150)
                    st.markdown(f"**{product['product_name']}**")
                    st.markdown(f"💰 {product['discounted_price']:,} VND")
                    st.markdown(f"🔥 Đã bán: {product['total_sold']}")
                    st.markdown(f"⭐ {product['avg_rating']} sao")
                    st.markdown(f"📦 Danh mục: {product['category_description']}")

    if num_show < len(df_top):
        if st.button("🔽 Click for more"):
            st.session_state.visible_count += 10
            st.rerun()

else:
    st.warning("Không có dữ liệu sản phẩm để hiển thị.")
