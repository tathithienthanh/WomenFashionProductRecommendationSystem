import streamlit as st
import subprocess
import pandas as pd
import pymysql
import os

col1, col2 = st.columns([1, 1], gap="small")
with col1:
    if st.button("Sign In", key="signin_btn", type="primary"):
        st.switch_page("pages/1_signin.py")
with col2:
    if st.button("Log In", key="login_btn", type="primary"):
        st.switch_page("pages/2_login.py")

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

def get_top_products() -> pd.DataFrame:
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
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        if conn and conn.open:
            conn.close()


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

df_top = df_top.drop_duplicates(subset='product_id')

if 'visible_count' not in st.session_state:
    st.session_state.visible_count = 10

st.markdown("---")
search_query = st.text_input("🔍 Tìm kiếm sản phẩm", "")

categories = df_top['category_description'].unique()
selected_categories = st.multiselect("🔖 Lọc theo loại sản phẩm", categories, default=categories)

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

min_price, max_price = st.slider(
    "💰 Lọc theo giá",
    min_value=int(df_top['discounted_price'].min()),
    max_value=int(df_top['discounted_price'].max()),
    value=(int(df_top['discounted_price'].min()), int(df_top['discounted_price'].max()))
)

if not df_top.empty:
    if search_query:
        df_top = df_top[df_top['product_name'].str.contains(search_query, case=False, na=False)]

    if selected_categories:
        df_top = df_top[df_top['category_description'].isin(selected_categories)]

    df_top = df_top[(df_top['avg_rating'] >= min_rating) & (df_top['avg_rating'] <= max_rating)]
    df_top = df_top[(df_top['discounted_price'] >= min_price) & (df_top['discounted_price'] <= max_price)]

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
                    if st.button("🔎 Chi tiết", key=f"detail_{product['product_id']}"):
                        st.session_state.selected_product_id = product['product_id']
                        st.switch_page("pages/10_productdetail.py")

    if num_show < len(df_top):
        if st.button("🔽 Click for more"):
            st.session_state.visible_count += 10
            st.rerun()

else:
    st.warning("Không có dữ liệu sản phẩm để hiển thị.")
