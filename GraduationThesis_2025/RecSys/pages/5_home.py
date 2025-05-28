import streamlit as st
import subprocess
import pandas as pd
import pymysql
import os
from NBCF_ItemItem import recommend_items_for_user

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

option = st.selectbox(
    "🔽Menu chức năng",
    (
        "🏠 Home",
        "🛒 My cart",
        "📦 My orders",
        "👤 Profile",
        "🔒 Change password",
        "🚪 Log out"
    )
)

if option != "🏠 Home":
    if option == "🛒 My cart":
        st.switch_page("pages/7_cart.py")
    elif option == "📦 My orders":
        st.switch_page("pages/8_history.py")
    elif option == "👤 Profile":
        st.switch_page("pages/6_profile.py")
    elif option == "🔒 Change password":
        st.switch_page("pages/4_changepassword.py")
    elif option == "🚪 Log out":
        st.session_state.clear()
        st.switch_page("ecommerce_app.py")

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
        SELECT t.product_id, t.product_name, t.discounted_price, t.total_sold, t.avg_rating, p.image_url, 
            c.category_id, c.description AS category_description
        FROM TopSellingProducts t
        JOIN Product p ON t.product_id = p.product_id
        JOIN ProductHasCategories phc ON p.product_id = phc.product_id
        JOIN Category c ON phc.category_id = c.category_id
    """
    df_products = pd.read_sql(query, conn)

except pymysql.Error as e:
    st.error(f"Lỗi MySQL: {e}")
except Exception as e:
    st.error(f"Lỗi khác: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()

df_products = df_products.drop_duplicates(subset='product_id')

recommendations = recommend_items_for_user(st.session_state["customer_id"], top_n=20)
recommendations = recommendations or df_products.head(20)
print(recommendations.columns)

if 'visible_count' not in st.session_state:
    st.session_state.visible_count = 10

st.markdown("---")
search_query = st.text_input("🔍 Tìm kiếm sản phẩm", "")

categories = df_products['category_description'].unique()
selected_categories = st.multiselect("🔖 Lọc theo loại sản phẩm", categories, default=categories)

if not df_products.empty:
    min_rating_value = df_products['avg_rating'].min()
    max_rating_value = df_products['avg_rating'].max()

    min_rating, max_rating = st.slider(
        "🌟 Lọc theo đánh giá sao",
        min_value=float(min_rating_value),
        max_value=float(max_rating_value),
        value=(float(min_rating_value), float(max_rating_value)),
        step=0.1
    )

min_price, max_price = st.slider(
    "💰 Lọc theo giá",
    min_value=int(df_products['discounted_price'].min()),
    max_value=int(df_products['discounted_price'].max()),
    value=(int(df_products['discounted_price'].min()), int(df_products['discounted_price'].max()))
)

if not df_products.empty:
    if search_query:
        df_products = df_products[df_products['product_name'].str.contains(search_query, case=False, na=False)]
        recommendations = recommendations[recommendations['product_name'].str.contains(search_query, case=False, na=False)]

    if selected_categories:
        df_products = df_products[df_products['category_description'].isin(selected_categories)]
        recommendations = recommendations[recommendations['category_description'].isin(selected_categories)]

    df_products = df_products[(df_products['avg_rating'] >= min_rating) & (df_products['avg_rating'] <= max_rating)]
    df_products = df_products[(df_products['discounted_price'] >= min_price) & (df_products['discounted_price'] <= max_price)]
    recommendations = recommendations[(recommendations['avg_rating'] >= min_rating) & (recommendations['avg_rating'] <= max_rating)]
    recommendations = recommendations[(recommendations['discounted_price'] >= min_price) & (recommendations['discounted_price'] <= max_price)]

if len(recommendations) > 0:
    st.title("🎯 Gợi ý cho bạn")

    num_cols = 5
    num_show = st.session_state.visible_count

    for i in range(0, min(num_show, len(recommendations)), num_cols):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            idx = i + j
            if idx < len(recommendations):
                recommendation = recommendations.iloc[idx]
                image_path = recommendation['image_url']
                if not os.path.exists(image_path):
                    image_path = placeholder_path

                with cols[j]:
                    st.image(image_path, width=150)
                    st.markdown(f"**{recommendation['product_name']}**")
                    st.markdown(f"💰 {recommendation['discounted_price']:,} VND")
                    st.markdown(f"🔥 Đã bán: {recommendation['total_sold']}")
                    st.markdown(f"⭐ {recommendation['avg_rating']} sao")
                    st.markdown(f"📦 Danh mục: {recommendation['category_description']}")
                    if st.button("🔎 Chi tiết", key=f"rcm_detail_{recommendation['product_id']}"):
                        st.session_state.selected_product_id = recommendation['product_id']
                        st.switch_page("pages/10_productdetail.py")

    if num_show < len(recommendations):
        if st.button("🔽 Click for more", key=f'rcm_more_btn'):
            st.session_state.visible_count += 10
            st.rerun()
else:
    st.info("Chưa có sản phẩm gợi ý phù hợp.")

if not df_products.empty:
    st.title("🛒 Sản Phẩm Hot!!!")

    num_cols = 5
    num_show = st.session_state.visible_count

    for i in range(0, min(num_show, len(df_products)), num_cols):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            idx = i + j
            if idx < len(df_products):
                product = df_products.iloc[idx]
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
                    if st.button("🔎 Chi tiết", key=f"product_detail_{product['product_id']}"):
                        st.session_state.selected_product_id = product['product_id']
                        st.switch_page("pages/10_productdetail.py")

    if num_show < len(df_products):
        if st.button("🔽 Click for more", key=f'top_more_btn'):
            st.session_state.visible_count += 10
            st.rerun()

else:
    st.warning("Không có dữ liệu sản phẩm để hiển thị.")

if st.button("🚪 Đăng xuất"):
    st.session_state.clear()
    st.success("Đăng xuất thành công.")
    st.switch_page("ecommerce_app.py")