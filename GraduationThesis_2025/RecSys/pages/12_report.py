import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime

# --- Hàm kết nối CSDL ---
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce"
    )

# --- Ghi nhật ký hoạt động ---
def log_admin_activity(admin_id, activity):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO ActivityLog (admin_id, activity) VALUES (%s, %s)"
            cursor.execute(sql, (admin_id, activity))
        conn.commit()
    finally:
        conn.close()

# --- Truy vấn các loại báo cáo ---
def report_top_selling_products():
    conn = get_connection()
    try:
        query = """
        SELECT product_name AS 'Tên sản phẩm', total_sold AS 'Đã bán', discounted_price AS 'Giá'
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
        SELECT * FROM ProductReviewsSummary
        ORDER BY avg_rating	DESC
        LIMIT 10;
        """
        return pd.read_sql(query, conn)
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

# --- Giao diện trang báo cáo ---
st.title("📊 Trang Báo Cáo Thống Kê")

# Kiểm tra đăng nhập admin
if "admin_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập với vai trò admin để truy cập trang này.")
    st.stop()

st.success("Xin chào admin!")

# Bước 2: Hiển thị lựa chọn loại báo cáo
report_type = st.selectbox("📌 Chọn loại báo cáo muốn xem:", [
    "Top 10 sản phẩm bán chạy nhất",
    "Top 10 sản phẩm được đánh giá nhiều nhất",
    "Top 10 khách hàng mua nhiều nhất"
])

# Bước 3 + 4: Hiển thị kết quả truy xuất
if st.button("📥 Xem báo cáo"):
    with st.spinner("Đang truy xuất dữ liệu..."):
        if report_type == "Top 10 sản phẩm bán chạy nhất":
            df = report_top_selling_products()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo sản phẩm bán chạy")
        elif report_type == "Top 10 sản phẩm được đánh giá nhiều nhất":
            df = report_most_reviewed_products()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo sản phẩm đánh giá nhiều")
        else:
            df = report_top_customers()
            log_admin_activity(st.session_state.admin_id, "Xem báo cáo khách hàng mua nhiều")
        
        st.dataframe(df, use_container_width=True)
        
        st.session_state.current_report_df = df

# Hiển thị nút xuất CSV bên ngoài điều kiện trên
if 'current_report_df' in st.session_state:
    csv = st.session_state.current_report_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Xuất CSV",
        data=csv,
        file_name=f"{report_type}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
        help="Tải báo cáo dưới dạng file CSV"
    )