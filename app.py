import streamlit as st
import sqlite3

def setup_initial_db():
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, face_id TEXT, display_name TEXT, avatar TEXT)''')
    try:
        c.execute("INSERT OR IGNORE INTO users (username, password, face_id, display_name, avatar) VALUES ('t.bun', '1', '0001', 'Trưởng nhóm t.bun', '')")
        c.execute("INSERT OR IGNORE INTO users (username, password, face_id, display_name, avatar) VALUES ('No2', '1', '0002', 'Đồng sáng lập No2', '')")
    except Exception:
        pass
    conn.commit()
    conn.close()

# Gọi hàm khởi tạo
setup_initial_db()

st.title("AI Education KHKT")
st.write("Hệ thống đang hoạt động ổn định!")
