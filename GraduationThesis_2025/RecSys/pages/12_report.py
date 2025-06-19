import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px # type: ignore
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

def report_slowest_selling_products():
    conn = get_connection()
    try:
        query = """
        SELECT product_id AS 'Mã SP', product_name AS 'Tên sản phẩm', total_sold AS 'Đã bán', discounted_price AS 'Giá'
        FROM TopSellingProducts
        ORDER BY total_sold ASC
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

def report_low_rating_reviews():
    conn = get_connection()
    try:
        query = """
        SELECT r.product_id AS 'Mã SP', p.name AS 'Tên sản phẩm',
            r.rating AS 'Số sao', r.content AS 'Nội dung đánh giá', created_at AS 'Thời gian'
        FROM Review r
        JOIN Product p ON r.product_id = p.product_id
        WHERE r.rating < 4
        ORDER BY r.rating ASC;
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def report_cancelled_rate():
    conn = get_connection()
    try:
        query = """
        SELECT o.order_id AS 'Mã đơn hàng', o.order_date AS 'Ngày đặt hàng', c.customer_id AS 'Mã khách hàng',
                o.order_status AS 'Trạng thái đơn', o.total_price AS 'Tổng tiền'
        FROM Orders o
        JOIN OrderDetail od ON o.order_id = od.order_id
        JOIN Customer c ON o.customer_id = c.customer_id
        WHERE o.order_status IN ('Cancelled', 'Đã hủy đơn')
        GROUP BY o.order_id
        ORDER BY o.order_date DESC;
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

def get_order_details(order_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.product_id, p.name AS product_name, od.quantity, od.unit_price, od.discount, (od.quantity * od.unit_price * (1 - od.discount)) AS total
                FROM orderdetail od
                JOIN product p ON od.product_id = p.product_id
                WHERE od.order_id = %s
            """, (order_id,))
            return cursor.fetchall()
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

def report_loyal_customers():
    conn = get_connection()
    try:
        query = """
        SELECT c.customer_id AS 'Mã KH', c.first_name AS 'Tên', c.last_name AS 'Họ',
               COUNT(o.order_id) AS 'Số đơn hàng', SUM(o.total_price) AS 'Tổng chi tiêu'
        FROM Orders o
        JOIN Customer c ON o.customer_id = c.customer_id
        GROUP BY o.customer_id
        HAVING COUNT(o.order_id) > 5
        ORDER BY COUNT(o.order_id) DESC;
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
    "Top 10 sản phẩm bán chậm nhất",
    "Top 10 sản phẩm được đánh giá nhiều nhất",
    "Top 10 khách hàng mua nhiều nhất",
    "Báo cáo doanh thu",
    "Báo cáo thống kê sản phẩm",
    "Các đánh giá sản phẩm dưới 4 sao",
    "Các đơn hàng bị hủy",
    "Báo cáo khách hàng trung thành (mua > 5 lần)"
])

if st.button("📥 Xem báo cáo"):
    with st.spinner("Đang truy xuất dữ liệu..."):
        if report_type == "Top 10 sản phẩm bán chạy nhất":
            df = report_top_selling_products()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo sản phẩm bán chạy")
        elif report_type == "Top 10 sản phẩm bán chậm nhất":
            df = report_slowest_selling_products()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo sản phẩm bán chậm")
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
        elif report_type == "Các đánh giá sản phẩm dưới 4 sao":
            df = report_low_rating_reviews()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo các đánh giá dưới 4 sao")
        elif report_type == "Các đơn hàng bị hủy":
            df = report_cancelled_rate()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo các đơn hàng bị hủy")
        elif report_type == "Báo cáo khách hàng trung thành (mua > 5 lần)":
            df = report_loyal_customers()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo khách hàng trung thành")

        st.dataframe(df, use_container_width=True)
        st.session_state.current_report_df = df

        st.subheader("📈 Biểu đồ minh họa")
        if report_type == "Top 10 sản phẩm bán chạy nhất":
            df_chart = df.melt(id_vars='Mã SP', value_vars=['Đã bán', 'Giá'], var_name='Chỉ số', value_name='Giá trị')

            fig = px.bar(df_chart, x='Mã SP', y='Giá trị', color='Chỉ số', color_discrete_sequence=px.colors.qualitative.Set2, barmode='group', title='Top 10 sản phẩm bán chạy: So sánh Đã bán và Giá')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        elif report_type == "Top 10 sản phẩm bán chậm nhất":
            df_chart = df.melt(id_vars='Mã SP', value_vars=['Đã bán', 'Giá'], var_name='Chỉ số', value_name='Giá trị')

            fig = px.bar(df_chart, x='Mã SP', y='Giá trị', color='Chỉ số', color_discrete_sequence=px.colors.qualitative.Set2, barmode='group', title='Top 10 sản phẩm bán chậm: So sánh Đã bán và Giá')
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
        
        elif report_type == "Các đơn hàng bị hủy":
            if df.empty:
                st.warning("Không có đơn hàng bị huỷ để hiển thị.")
            else:
                st.subheader("📦 Chi tiết đơn hàng bị huỷ")
                all_details = []
                for _, order in df.iterrows():
                    with st.expander(f"🔎 Đơn hàng {order['Mã đơn hàng']} - Ngày đặt: {order['Ngày đặt hàng']}"):
                        details = get_order_details(order['Mã đơn hàng'])
                        if details:
                            for item in details:
                                item_with_order = list(item) + [order['Mã đơn hàng']]
                                all_details.append(item_with_order)

                            df_detail = pd.DataFrame(details)
                            df_detail.columns=[" Mã SP", "Sản phẩm", "Số lượng", "Đơn giá", "Giảm giá (%)", "Thành tiền"]

                            df_detail["Giảm giá (%)"] = df_detail["Giảm giá (%)"] * 100
                            df_detail["Đơn giá"] = df_detail["Đơn giá"].apply(lambda x: f"{x:,.0f}₫")
                            df_detail["Thành tiền"] = df_detail["Thành tiền"].apply(lambda x: f"{x:,.0f}₫")

                            st.dataframe(df_detail, use_container_width=True)

            df['Ngày đặt hàng'] = pd.to_datetime(df['Ngày đặt hàng'])
            df['Năm'] = df['Ngày đặt hàng'].dt.year
            df['Quý'] = df['Ngày đặt hàng'].dt.to_period('Q').astype(str)
            df_by_quarter = df.groupby('Quý').size().reset_index(name='Số đơn bị huỷ')
            fig_quarter = px.bar(df_by_quarter, x='Quý', y='Số đơn bị huỷ',
                                title="📊 Số đơn hàng bị huỷ theo Quý",
                                labels={'Số đơn bị huỷ': 'Số đơn'})
            fig_quarter.update_layout(xaxis_title="Quý", yaxis_title="Số đơn huỷ")
            st.plotly_chart(fig_quarter, use_container_width=True)

            df_by_year = df.groupby('Năm').size().reset_index(name='Số đơn bị huỷ')
            fig_year = px.line(df_by_year, x='Năm', y='Số đơn bị huỷ',
                            title="📈 Số đơn hàng bị huỷ theo Năm",
                            markers=True)
            fig_year.update_layout(xaxis_title="Năm", yaxis_title="Số đơn huỷ")
            st.plotly_chart(fig_year, use_container_width=True)

            df_cancel_by_customer = df['Mã khách hàng'].value_counts().reset_index()
            df_cancel_by_customer.columns = ['Mã khách hàng', 'Số đơn bị huỷ']
            fig3 = px.pie(df_cancel_by_customer, names='Mã khách hàng', values='Số đơn bị huỷ', title='🥧Các khách hàng từng hủy đơn')
            st.plotly_chart(fig3, use_container_width=True)

            if all_details:
                df_all_details = pd.DataFrame(all_details, columns=["Mã SP", "Sản phẩm", "Số lượng", "Đơn giá", "Giảm giá (%)", "Thành tiền", "Mã đơn hàng"])
                df_all_details["Đơn giá"] = pd.to_numeric(df_all_details["Đơn giá"], errors='coerce')

                fig_price_dist = px.histogram(
                    df_all_details,
                    x="Đơn giá",
                    nbins=30,
                    title="💰 Phân phối đơn giá của các sản phẩm bị huỷ đơn",
                    labels={"Đơn giá": "Đơn giá (VND)"},
                    color_discrete_sequence=['#EF553B']
                )
                fig_price_dist.update_layout(xaxis_title="Đơn giá (VND)", yaxis_title="Số lượng sản phẩm")
                st.plotly_chart(fig_price_dist, use_container_width=True)

                fig_discount_dist = px.histogram(
                    df_all_details,
                    x="Giảm giá (%)",
                    nbins=20,
                    title="🔻 Phân phối % giảm giá của các sản phẩm bị huỷ đơn",
                    labels={"Giảm giá (%)": "Giảm giá (%)"},
                    color_discrete_sequence=['#00CC96']
                )
                fig_discount_dist.update_layout(xaxis_title="Giảm giá (%)", yaxis_title="Số lượng sản phẩm")
                st.plotly_chart(fig_discount_dist, use_container_width=True)

        elif report_type == "Báo cáo khách hàng trung thành (mua > 5 lần)":
            fig = px.bar(df, x='Mã KH', y='Tổng chi tiêu', color='Số đơn hàng',
                        title="Top 10 khách hàng mua nhiều nhất", text='Tổng chi tiêu', color_continuous_scale='Viridis')
            fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            

if 'current_report_df' in st.session_state:
    csv = st.session_state.current_report_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Xuất CSV",
        data=csv,
        file_name=f"{report_type}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
        help="Tải báo cáo dưới dạng file CSV"
    )

st.markdown("---")
if st.button("🏠Về trang chủ"):
    st.switch_page("pages/17_homeadmin.py")