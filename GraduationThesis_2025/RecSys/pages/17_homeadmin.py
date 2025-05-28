import streamlit as st
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


if "admin_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập với vai trò admin để truy cập trang này.")
    if st.button("🔑 Đăng nhập"):
        st.switch_page("pages/11_loginadmin.py")
    st.stop()

menu_options = [
    {"label": "🏠 Trang chủ", "permission": None, "page": "pages/17_homeadmin.py"},
    {"label": "📊 Xem báo cáo", "permission": "VIEW_REPORT", "page": "pages/12_report.py"},
    {"label": "📦 Quản lý sản phẩm", "permission": "MANAGE_PRODUCTS", "page": "pages/14_productmanagement.py"},
    {"label": "👥 Quản lý người dùng", "permission": "MANAGE_USERS", "page": "pages/13_usermanagement.py"},
    {"label": "📦 Quản lý đơn hàng", "permission": "MANAGE_ORDERS", "page": "pages/15_ordermanagement.py"},
    {"label": "📜 Nhật ký hoạt động", "permission": "VIEW_LOGS", "page": "pages/16_viewlogs.py"},
    {"label": "🚪 Đăng xuất", "permission": None, "page": "pages/11_loginadmin.py"}
]

option_labels = []
option_map = {}

for item in menu_options:
    label = item["label"]
    permission_id = item["permission"]
    page = item["page"]
    
    if permission_id is None or has_permission(permission_id):
        option_labels.append(label)
        option_map[label] = page
    else:
        disabled_label = f"{label} 🚫 (không có quyền)"
        option_labels.append(disabled_label)
        option_map[disabled_label] = None

selected_option = st.selectbox("🔽 Menu chức năng", option_labels)
selected_page = option_map[selected_option]

if selected_page is None:
    st.error("🚫 Bạn không có quyền truy cập chức năng này.")
    st.stop()
else:
    if selected_option == "🚪 Đăng xuất":
        st.session_state.clear()
        st.switch_page("pages/11_loginadmin.py")
    st.switch_page(selected_page)