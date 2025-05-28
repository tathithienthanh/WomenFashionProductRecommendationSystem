import streamlit as st
import pandas as pd
import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce"
    )

def has_permission(permission_id: str) -> bool:
    admin_id = st.session_state["admin_id"]
    if not admin_id:
        return False
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 1 FROM AdminHasPermissions
                WHERE permission_id = %s AND admin_id = %s
                LIMIT 1
            """
            cursor.execute(query, (permission_id, admin_id))
            return cursor.fetchone() is not None
    finally:
        conn.close()

def log_admin_activity(admin_id, activity):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO ActivityLog (admin_id, activity) VALUES (%s, %s)"
            cursor.execute(sql, (admin_id, activity))
        conn.commit()
    finally:
        conn.close()

def list_products():
    conn = get_connection()
    try:
        query = "SELECT * FROM Product"
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def list_categories():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM Category", conn)
    finally:
        conn.close()

def add_product(name, description, price, quantity, image_url, discount, sold, rating, categories):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Product")
            count = cursor.fetchone()[0]
            product_id = f"P{count+1:03}"

            cursor.execute("""
                INSERT INTO Product (product_id, name, description, price, quantity, image_url, discount, sold, rating)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (product_id, name, description, price, quantity, image_url, discount, sold, rating))

            for category_id in categories:
                cursor.execute("INSERT INTO ProductHasCategories (category_id, product_id) VALUES (%s, %s)",
                               (category_id, product_id))
        conn.commit()
    finally:
        conn.close()

def update_product(product_id, name, description, price, quantity, image_url, discount, sold, rating):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Product SET name=%s, description=%s, price=%s, quantity=%s, image_url=%s, discount=%s, sold=%s, rating=%s
                WHERE product_id = %s
            """, (name, description, price, quantity, image_url, discount, sold, rating, product_id))
        conn.commit()
    finally:
        conn.close()

def delete_product(product_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Product WHERE product_id = %s", (product_id,))
        conn.commit()
    finally:
        conn.close()
st.title("📦 Quản lý sản phẩm")

if "admin_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập với vai trò admin để truy cập trang này.")
    st.stop()

if not has_permission("MANAGE_PRODUCTS"):
    st.warning("Bạn không có quyền truy cập chức năng này.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📋 Danh sách", "➕ Thêm", "✏️ Cập nhật / ❌ Xoá"])

with tab1:
    st.subheader("📋 Danh sách sản phẩm")
    df = list_products()
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("➕ Thêm sản phẩm")
    with st.form("add_product_form"):
        name = st.text_input("Tên sản phẩm")
        description = st.text_area("Mô tả")
        price = st.number_input("Giá", min_value=0.0, step=1000.0)
        quantity = st.number_input("Số lượng", min_value=0)
        image_url = st.text_input("Link hình ảnh")
        discount = st.number_input("Giảm giá (%)", min_value=0.0, max_value=100.0, step=0.5)
        categories_df = list_categories()
        selected_categories = st.multiselect("Danh mục", categories_df["category_id"].tolist())

        submitted = st.form_submit_button("Thêm")
        if submitted and name and price:
            add_product(name, description, price, quantity, image_url, discount, 0, 0, selected_categories)
            st.success("✅ Đã thêm sản phẩm thành công.")
            log_admin_activity(st.session_state.admin_id, f"Thêm sản phẩm: {name}")
        elif submitted:
            st.error("Vui lòng nhập đầy đủ thông tin cần thiết.")

with tab3:
    st.subheader("✏️ Cập nhật / ❌ Xoá sản phẩm")
    products_df = list_products()
    if not products_df.empty:
        selected_product_id = st.selectbox("Chọn sản phẩm", products_df["product_id"].tolist())
        prod = products_df[products_df["product_id"] == selected_product_id].iloc[0]

        with st.form("update_product_form"):
            name = st.text_input("Tên", value=prod["name"])
            description = st.text_area("Mô tả", value=prod["description"])
            price = st.number_input("Giá", value=prod["price"], step=1000.0)
            quantity = st.number_input("Số lượng", value=prod["quantity"])
            image_url = st.text_input("Hình ảnh", value=prod["image_url"])
            discount = st.number_input("Giảm giá", value=prod["discount"] or 0.0, step=0.5)
            sold = st.number_input("Đã bán", value=prod["sold"], disabled=True)
            rating = st.slider("Đánh giá", value=prod["rating"] or 0.0, min_value=0.0, max_value=5.0, step=0.1, disabled=True)

            col1, col2 = st.columns(2)
            if col1.form_submit_button("Cập nhật"):
                update_product(selected_product_id, name, description, price, quantity, image_url, discount, sold, rating)
                st.success("✅ Cập nhật sản phẩm thành công.")
                log_admin_activity(st.session_state.admin_id, f"Cập nhật sản phẩm: {selected_product_id}")
            if col2.form_submit_button("❌ Xoá"):
                delete_product(selected_product_id)
                st.warning("❌ Đã xoá sản phẩm.")
                log_admin_activity(st.session_state.admin_id, f"Xoá sản phẩm: {selected_product_id}")
    else:
        st.info("Không có sản phẩm nào.")

st.markdown("---")
if st.button("🏠Về trang chủ"):
    st.switch_page("pages/17_homeadmin.py")