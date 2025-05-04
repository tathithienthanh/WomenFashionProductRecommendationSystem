# import streamlit as st
# import pymysql
# import os
# import pandas as pd
# from NBCF_ItemItem import recommend_items_for_user

# # --- Cấu hình ---
# PLACEHOLDER_PATH = r"C:\Users\ASUS\Desktop\T\ĐAN_KLTN\getImages\placeholder.jpg"
# PRODUCTS_PER_PAGE = 10
# INITIAL_PRODUCTS = 10

# # --- Kiểm tra đăng nhập ---
# if "customer_id" not in st.session_state or st.session_state["customer_id"] is None:
#     st.warning("🔒 Vui lòng đăng nhập để truy cập trang này.")
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("🔑 Đăng nhập"):
#             st.switch_page("pages/2_login.py")
#     with col2:
#         if st.button("📝 Đăng ký"):
#             st.switch_page("pages/1_signin.py")
#     st.stop()

# # --- Khởi tạo biến session ---
# if "visible_count" not in st.session_state:
#     st.session_state.visible_count = INITIAL_PRODUCTS

# # --- Kết nối CSDL ---
# @st.cache_resource
# def get_db_connection():
#     return pymysql.connect(
#         host="localhost",
#         user="root",
#         password="Abcxyz@123",
#         database="eCommerce",
#         cursorclass=pymysql.cursors.DictCursor
#     )

# # --- Lấy toàn bộ sản phẩm ---
# @st.cache_data(ttl=3600)
# def get_all_products():
#     try:
#         with get_db_connection() as conn:
#             with conn.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT DISTINCT 
#                         p.product_id,
#                         p.name AS product_name,
#                         p.price,
#                         p.discount,
#                         p.price * (1 - IFNULL(p.discount, 0)/100) AS discounted_price,
#                         p.sold AS total_sold,
#                         p.rating AS avg_rating,
#                         p.image_url,
#                         c.description AS category_description
#                     FROM Product p
#                     LEFT JOIN ProductHasCategories phc ON p.product_id = phc.product_id
#                     LEFT JOIN Category c ON phc.category_id = c.category_id
#                 """)
#                 products = cursor.fetchall()
#                 for p in products:
#                     p['avg_rating'] = p.get('avg_rating') or 0
#                     p['discount'] = p.get('discount') or 0
#                     p['discounted_price'] = p.get('discounted_price') or p['price']
#                     p['category_description'] = p.get('category_description') or None
#                     p['image_url'] = p.get('image_url') or PLACEHOLDER_PATH
#                 return products
#     except Exception as e:
#         st.error(f"Lỗi khi tải sản phẩm: {e}")
#         return []

# # --- Hiển thị sản phẩm ---
# def display_product_card(product, col):
#     with col:
#         image_path = product.get("image_url", "")
#         if not image_path or not os.path.exists(image_path):
#             image_path = PLACEHOLDER_PATH
#         st.image(image_path, width=150, use_column_width=True)
#         st.markdown(f"**{product.get('product_name', 'Sản phẩm')}**")
#         st.markdown(f"💰 {product.get('discounted_price', 0):,} VND")
#         st.markdown(f"🔥 Đã bán: {product.get('total_sold', 0):,}")
#         st.markdown(f"⭐ {product.get('avg_rating', 0):.1f}/5")
#         st.markdown(f"📦 {product.get('category_description', 'Chưa rõ')}")

# # --- Giao diện chính ---
# st.title("🛍️ Trang chủ khách hàng")

# # --- Lấy tất cả sản phẩm ---
# all_products = get_all_products()
# df_products = pd.DataFrame(all_products)

# # --- Loại bỏ trùng lặp theo product_id ---
# df_products = df_products.drop_duplicates(subset='product_id', keep='first')

# # --- Bộ lọc ---
# search_query = st.text_input("🔍 Tìm kiếm sản phẩm", placeholder="Nhập tên sản phẩm")

# # categories = df_products['category_description'].dropna().unique()
# # selected_categories = st.multiselect("🔖 Lọc theo loại sản phẩm", categories, default=categories)

# if not df_products.empty:
#     min_rating_value = df_products['avg_rating'].min()
#     max_rating_value = df_products['avg_rating'].max()

#     min_rating, max_rating = st.slider(
#         "🌟 Lọc theo đánh giá sao",
#         min_value=float(min_rating_value),
#         max_value=float(max_rating_value),
#         value=(float(min_rating_value), float(max_rating_value)),
#         step=0.1
#     )

# if not df_products.empty:
#     min_price, max_price = st.slider(
#         "💰 Khoảng giá",
#         int(df_products['discounted_price'].min()),
#         int(df_products['discounted_price'].max()),
#         (int(df_products['discounted_price'].min()), int(df_products['discounted_price'].max()))
#     )

# # --- Áp dụng bộ lọc ---
# if not df_products.empty:
#     if search_query:
#         df_products = df_products[df_products['product_name'].str.contains(search_query, case=False, na=False)]

#     # if selected_categories:
#     #     df_products = df_products[df_products['category_description'].isin(selected_categories)]

#     df_products = df_products[
#         (df_products['avg_rating'] >= min_rating) & (df_products['avg_rating'] <= max_rating)
#     ]
#     df_products = df_products[
#         (df_products['discounted_price'] >= min_price) & (df_products['discounted_price'] <= max_price)
#     ]

# # --- Gợi ý sản phẩm ---
# st.subheader("🎯 Gợi ý cho bạn")
# recommendations = recommend_items_for_user(st.session_state["customer_id"], top_n=6)
# recommendations = recommendations or df_products.head(6)

# if recommendations:
#     cols = st.columns(3)
#     for i, product in enumerate(recommendations):
#         display_product_card(product, cols[i % 3])
# else:
#     st.info("Chưa có sản phẩm gợi ý phù hợp.")

# # --- Danh sách sản phẩm ---
# st.subheader("🔥 Tất cả sản phẩm")
# st.write(f"Đang hiển thị {len(df_products)} sản phẩm phù hợp")

# if not df_products.empty:
#     cols = st.columns(3)
#     for i, product in enumerate(df_products.head(st.session_state.visible_count)):
#         display_product_card(product, cols[i % 3])

#     col1, col2, _ = st.columns([1, 1, 2])
#     with col1:
#         if st.session_state.visible_count < len(df_products):
#             if st.button("🔽 Xem thêm"):
#                 st.session_state.visible_count += PRODUCTS_PER_PAGE
#                 st.rerun()
#     with col2:
#         if st.session_state.visible_count > INITIAL_PRODUCTS:
#             if st.button("🔼 Thu gọn"):
#                 st.session_state.visible_count = INITIAL_PRODUCTS
#                 st.rerun()
# else:
#     st.warning("Không tìm thấy sản phẩm nào phù hợp.")

# # --- Đăng xuất ---
# if st.button("🚪 Đăng xuất"):
#     st.session_state.clear()
#     st.success("Đăng xuất thành công.")
#     st.switch_page("ecommerce_app.py")

# # --- CSS Tùy chỉnh ---
# st.markdown("""
# <style>
#     [data-testid="stHorizontalBlock"] { gap: 1rem; }
#     .stImage { border-radius: 10px; transition: transform 0.2s; }
#     .stImage:hover { transform: scale(1.03); }
#     div[data-testid="column"] { padding: 10px; }
#     .stButton button { width: 100%; }
# </style>
# """, unsafe_allow_html=True)




import streamlit as st
import subprocess
import pandas as pd
import pymysql
import os
from NBCF_ItemItem import recommend_items_for_user

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
    df_products = pd.read_sql(query, conn)

except pymysql.Error as e:
    st.error(f"Lỗi MySQL: {e}")
except Exception as e:
    st.error(f"Lỗi khác: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()

# Xử lý trùng lặp sản phẩm
df_products = df_products.drop_duplicates(subset='product_id')

# --- Gợi ý sản phẩm ---
recommendations = recommend_items_for_user(st.session_state["customer_id"], top_n=20)
recommendations = recommendations or df_products.head(20)
print(recommendations.columns)

# Khởi tạo số lượng sản phẩm hiển thị mặc định
if 'visible_count' not in st.session_state:
    st.session_state.visible_count = 10

# Bộ lọc tìm kiếm
search_query = st.text_input("🔍 Tìm kiếm sản phẩm", "")

# Bộ lọc danh mục
categories = df_products['category_description'].unique()
selected_categories = st.multiselect("🔖 Lọc theo loại sản phẩm", categories, default=categories)

# Bộ lọc số sao
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

# Bộ lọc giá
min_price, max_price = st.slider(
    "💰 Lọc theo giá",
    min_value=int(df_products['discounted_price'].min()),
    max_value=int(df_products['discounted_price'].max()),
    value=(int(df_products['discounted_price'].min()), int(df_products['discounted_price'].max()))
)

# Áp dụng bộ lọc
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

    if num_show < len(recommendations):
        if st.button("🔽 Click for more"):
            st.session_state.visible_count += 10
            st.rerun()
else:
    st.info("Chưa có sản phẩm gợi ý phù hợp.")

# Hiển thị dữ liệu sản phẩm
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

    if num_show < len(df_products):
        if st.button("🔽 Click for more"):
            st.session_state.visible_count += 10
            st.rerun()

else:
    st.warning("Không có dữ liệu sản phẩm để hiển thị.")

# --- Đăng xuất ---
if st.button("🚪 Đăng xuất"):
    st.session_state.clear()
    st.success("Đăng xuất thành công.")
    st.switch_page("ecommerce_app.py")