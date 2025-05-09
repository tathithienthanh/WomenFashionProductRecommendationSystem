import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud

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

def report_top_selling_products():
    conn = get_connection()
    try:
        query = """
        SELECT product_id AS 'Mã SP', product_name AS 'Tên sản phẩm', total_sold AS 'Đã bán', discounted_price AS 'Giá'
        FROM TopSellingProducts
        ORDER BY total_sold DESC
        LIMIT 10;
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def report_most_reviewed_products():
    conn = get_connection()
    try:
        query = """
        SELECT product_id, product_name, total_reviews, avg_rating
        FROM ProductReviewsSummary
        ORDER BY avg_rating DESC
        LIMIT 10;
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def get_reviews_for_top_products(product_ids):
    conn = get_connection()
    try:
        format_ids = ",".join(f"'{pid}'" for pid in product_ids)
        query = f"""
        SELECT content
        FROM Review
        WHERE product_id IN ({format_ids});
        """
        df_reviews = pd.read_sql(query, conn)
        return df_reviews['content'].dropna().tolist()
    finally:
        conn.close()

def report_top_customers():
    conn = get_connection()
    try:
        query = """
        SELECT C.customer_id AS 'Mã KH', C.first_name AS 'Tên', C.last_name AS 'Họ',
               COUNT(O.order_id) AS 'Số đơn hàng', SUM(O.total_price) AS 'Tổng chi tiêu'
        FROM Orders O
        JOIN Customer C ON O.customer_id = C.customer_id
        GROUP BY O.customer_id
        ORDER BY SUM(O.total_price) DESC
        LIMIT 10;
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def report_revenue():
    try:
        conn = get_connection()
        query = """
            SELECT DATE(order_date) AS 'Ngày', SUM(total_price) AS 'Doanh thu'
            FROM Orders
            GROUP BY DATE(order_date)
            ORDER BY DATE(order_date) ASC;
        """
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

def report_product_statistics():
    try:
        conn = get_connection()
        query = """
            SELECT c.description AS 'Loại sản phẩm',
                   COUNT(p.product_id) AS 'Số lượng sản phẩm',
                   ROUND(AVG(p.price * (1 - IFNULL(p.discount, 0))), 2) AS 'Giá trung bình'
            FROM Product p
            JOIN ProductHasCategories pc ON p.product_id = pc.product_id
            JOIN Category c ON pc.category_id = c.category_id
            GROUP BY c.description
            ORDER BY 'Số lượng sản phẩm';
        """
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

st.title("📊 Trang Báo Cáo Thống Kê")

if "admin_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập với vai trò admin để truy cập trang này.")
    st.stop()

if not has_permission("VIEW_REPORT"):
    st.warning("Bạn không có quyền truy cập chức năng này.")
    st.stop()

st.success("Xin chào admin!")

report_type = st.selectbox("📌 Chọn loại báo cáo muốn xem:", [
    "Top 10 sản phẩm bán chạy nhất",
    "Top 10 sản phẩm được đánh giá nhiều nhất",
    "Top 10 khách hàng mua nhiều nhất",
    "Báo cáo doanh thu",
    "Báo cáo thống kê sản phẩm"
])

if st.button("📥 Xem báo cáo"):
    with st.spinner("Đang truy xuất dữ liệu..."):
        if report_type == "Top 10 sản phẩm bán chạy nhất":
            df = report_top_selling_products()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo sản phẩm bán chạy")
        elif report_type == "Top 10 sản phẩm được đánh giá nhiều nhất":
            df = report_most_reviewed_products()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo sản phẩm đánh giá nhiều")
        elif report_type == "Top 10 khách hàng mua nhiều nhất":
            df = report_top_customers()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo khách hàng mua nhiều")
        elif report_type == "Báo cáo doanh thu":
            df = report_revenue()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo doanh thu")
        elif report_type == "Báo cáo thống kê sản phẩm":
            df = report_product_statistics()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo thống kê sản phẩm")

        st.dataframe(df, use_container_width=True)
        st.session_state.current_report_df = df

        st.subheader("📈 Biểu đồ minh họa")
        if report_type == "Top 10 sản phẩm bán chạy nhất":
            df_chart = df.melt(id_vars='Mã SP', value_vars=['Đã bán', 'Giá'], var_name='Chỉ số', value_name='Giá trị')

            fig = px.bar(df_chart, x='Mã SP', y='Giá trị', color='Chỉ số', barmode='group', title='Top 10 sản phẩm bán chạy: So sánh Đã bán và Giá')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        elif report_type == "Top 10 sản phẩm được đánh giá nhiều nhất":
            fig = px.bar(df, x='avg_rating', y='product_id', orientation='h',
                         title="Top 10 sản phẩm được đánh giá cao", text='avg_rating')
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

            product_ids = df['product_id'].tolist()
            reviews = get_reviews_for_top_products(product_ids)
            all_text = " ".join(reviews)

            if all_text.strip():
                st.subheader("📈 Biểu đồ Wordcloud các đánh giá của sản phẩm")
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.info("Không tìm thấy nội dung đánh giá để tạo WordCloud.")

        elif report_type == "Top 10 khách hàng mua nhiều nhất":
            fig = px.bar(df, x='Tổng chi tiêu', y='Mã KH', orientation='h',
                         title="Top 10 khách hàng mua nhiều nhất", text='Tổng chi tiêu')
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

        elif report_type == "Báo cáo doanh thu":
            fig = px.line(df, x='Ngày', y='Doanh thu', title="📅 Doanh thu theo ngày")
            st.plotly_chart(fig, use_container_width=True)

        elif report_type == "Báo cáo thống kê sản phẩm":
            fig = px.pie(df, names='Loại sản phẩm', values='Số lượng sản phẩm', title="📦 Tỷ lệ số lượng sản phẩm theo danh mục", hole=0.5)
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
            fig2 = px.bar(df, x='Loại sản phẩm', y='Giá trung bình', title="💰 Giá trung bình theo danh mục", text='Giá trung bình')
            st.plotly_chart(fig2, use_container_width=True)

# Nút xuất CSV
if 'current_report_df' in st.session_state:
    csv = st.session_state.current_report_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Xuất CSV",
        data=csv,
        file_name=f"{report_type}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
        help="Tải báo cáo dưới dạng file CSV"
    )
