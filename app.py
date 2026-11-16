import sqlite3

def init_db():
    conn = sqlite3.connect("users_data.db")
    # các câu lệnh bên dưới...
def init_db():
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

init_db()

     

setup_initial_db()

# Tự động cập nhật cấu trúc database cũ (thêm cột display_name, avatar nếu chưa có)
try:
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    if "display_name" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN display_name TEXT")
    if "avatar" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN avatar TEXT")
    conn.commit()
    conn.close()
    print("♻️ Đã cập nhật cấu trúc Database (Thêm Avatar & Tên hiển thị thành công)")
except Exception as e:
    print(f"⚠️ Lưu ý kiểm tra DB: {e}")

# ==========================================
# 1. TẠO FILE app.py HOÀN CHỈNH KHÔNG LỖI CÚ PHÁP
# ==========================================
