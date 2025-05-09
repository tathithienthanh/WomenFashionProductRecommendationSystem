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
    admin_id = st.session_state.get("admin_id")
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

def get_activity_logs():
    conn = get_connection()
    try:
        query = """
            SELECT * FROM adminactivitydetail
            ORDER BY activity_time
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()

st.title("📜 Nhật ký hoạt động quản trị viên")

if "admin_id" not in st.session_state:
    st.warning("⚠️ Vui lòng đăng nhập với vai trò admin để truy cập trang này.")
    st.stop()

if not has_permission("VIEW_LOGS"):
    st.warning("Bạn không có quyền truy cập chức năng này.")
    st.stop()

logs_df = get_activity_logs()
if logs_df.empty:
    st.info("Không có hoạt động nào được ghi nhận.")
else:
    st.dataframe(logs_df, use_container_width=True)
    log_admin_activity(st.session_state.admin_id, 'Xem nhật ký hoạt động của các quản trị viên')