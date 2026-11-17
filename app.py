# ==============================================================================
# HỆ THỐNG KHKT: SIÊU TỐC ĐỘ & ĐƯỜNG TRUYỀN NGROK CỐ ĐỊNH CHUẨN DOMAIN
# (BẢO MẬT API KEY & CẬP NHẬT TÙY BIẾN AVATAR/TÊN HIỂN THỊ CHO HỌC VIÊN)
# ==============================================================================

import os
import shutil
import socket
import sqlite3
import subprocess
import time
import requests
import json
AUTHTOKEN_MOI = "..."

GEMINI_API_KEY_MOI = "AQ.Ab8RN6KdFjAWDJaydUEY0-kdfbS2uc6s203ADG7UowKF98CBqg"
AUTHTOKEN_MOI = "3LKGlsOWuXBl2L6LvUzw2FPoVUv_5reay1sZf6CZHrbmw6XaT"
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY_MOI

# Avatar mặc định bằng SVG Base64
DEFAULT_AVATAR = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='50' fill='%231E88E5'/><circle cx='50' cy='37' r='17' fill='%23FFFFFF'/><path d='M18,78 C18,60 32,54 50,54 C68,54 82,60 82,78 C82,85 75,90 50,90 C25,90 18,85 18,78 Z' fill='%23FFFFFF'/></svg>"

# Khởi tạo DB cấu trúc hoàn chỉnh trước khi chạy ứng dụng
def setup_initial_db():
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        face_id TEXT UNIQUE,
        display_name TEXT,
        avatar TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        subject TEXT,
        topic TEXT,
        mode TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1 TEXT,
        user2 TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user1, user2)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS shared_exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        subject TEXT,
        topic TEXT,
        mode TEXT,
        content TEXT,
        is_notified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    try:
        c.execute("INSERT OR IGNORE INTO users (username, password, face_id, display_name, avatar) VALUES ('t.bun', '1', '0001', 'Trưởng nhóm t.bun', '" + DEFAULT_AVATAR + "')")
        c.execute("INSERT OR IGNORE INTO users (username, password, face_id, display_name, avatar) VALUES ('No2', '1', '0002', 'Đồng sáng lập No2', '" + DEFAULT_AVATAR + "')")
    except Exception:
        pass
    conn.commit()
    conn.close()

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
app_source_code = """import os
import time
import json
import sqlite3
import random
import base64
import streamlit as st
from google import genai

st.set_page_config(
    page_title="AI Education KHKT - Học Cùng AI",
    page_icon="☕",
    layout="wide"
)

# Avatar mặc định bằng SVG Base64
DEFAULT_AVATAR = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='50' fill='%231E88E5'/><circle cx='50' cy='37' r='17' fill='%23FFFFFF'/><path d='M18,78 C18,60 32,54 50,54 C68,54 82,60 82,78 C82,85 75,90 50,90 C25,90 18,85 18,78 Z' fill='%23FFFFFF'/></svg>"

def init_db():
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        face_id TEXT UNIQUE,
        display_name TEXT,
        avatar TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        subject TEXT,
        topic TEXT,
        mode TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1 TEXT,
        user2 TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user1, user2)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS shared_exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        subject TEXT,
        topic TEXT,
        mode TEXT,
        content TEXT,
        is_notified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    try:
        c.execute("INSERT OR IGNORE INTO users (username, password, face_id, display_name, avatar) VALUES ('t.bun', '1', '0001', 'Trưởng nhóm t.bun', '" + DEFAULT_AVATAR + "')")
        c.execute("INSERT OR IGNORE INTO users (username, password, face_id, display_name, avatar) VALUES ('No2', '1', '0002', 'Đồng sáng lập No2', '" + DEFAULT_AVATAR + "')")
    except Exception:
        pass
    conn.commit()
    conn.close()

init_db()

def verify_user(username, password, face_id):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ? AND face_id = ?", (username, password, face_id))
    res = c.fetchone()
    conn.close()
    return res is not None

def add_user(username, password, face_id):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, face_id, display_name, avatar) VALUES (?, ?, ?, ?, ?)",
                  (username, password, face_id, username, DEFAULT_AVATAR))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_user_profile(username, new_display_name, avatar_base64=None):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    if avatar_base64:
        c.execute("UPDATE users SET display_name = ?, avatar = ? WHERE username = ?", (new_display_name, avatar_base64, username))
    else:
        c.execute("UPDATE users SET display_name = ? WHERE username = ?", (new_display_name, username))
    conn.commit()
    conn.close()

def get_user_profile(username):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("SELECT display_name, avatar, face_id FROM users WHERE username = ?", (username,))
    res = c.fetchone()
    conn.close()
    if res:
        return {
            "display_name": res[0] if res[0] else username,
            "avatar": res[1] if res[1] else DEFAULT_AVATAR,
            "face_id": res[2]
        }
    return {"display_name": username, "avatar": DEFAULT_AVATAR, "face_id": ""}

def get_user_face_id(username):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("SELECT face_id FROM users WHERE username = ?", (username,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else ""

def find_user_by_face_id(face_id):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE face_id = ?", (face_id,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else None

def make_friend(user1, user2):
    if user1 == user2: return False
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    u1, u2 = sorted([user1, user2])
    try:
        c.execute("INSERT INTO friends (user1, user2) VALUES (?, ?)", (u1, u2))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_friends_list(username):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("SELECT user1, user2 FROM friends WHERE user1 = ? OR user2 = ?", (username, username))
    rows = c.fetchall()
    conn.close()
    friends = []
    for r in rows:
        friend = r[1] if r[0] == username else r[0]
        friends.append(friend)
    return friends

def send_chat_message(sender, receiver, msg):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO chats (sender, receiver, message) VALUES (?, ?, ?)", (sender, receiver, msg))
    conn.commit()
    conn.close()

def get_chat_history(user1, user2):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute('''SELECT sender, message, created_at FROM chats
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY id ASC''', (user1, user2, user2, user1))
    res = c.fetchall()
    conn.close()
    return res

def save_exam(username, subject, topic, mode, content):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO exams (username, subject, topic, mode, content) VALUES (?, ?, ?, ?, ?)",
              (username, subject, topic, mode, content))
    conn.commit()
    conn.close()

def share_exam_with_friend(sender, receiver, subject, topic, mode, content):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO shared_exams (sender, receiver, subject, topic, mode, content, is_notified) VALUES (?, ?, ?, ?, ?, ?, 0)",
              (sender, receiver, subject, topic, mode, content))
    conn.commit()
    conn.close()

def get_shared_exams(receiver):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("SELECT sender, subject, topic, mode, content, created_at FROM shared_exams WHERE receiver = ? ORDER BY id DESC", (receiver,))
    res = c.fetchall()
    conn.close()
    return res

def check_unnotified_shares(receiver):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("SELECT id, sender, subject, topic FROM shared_exams WHERE receiver = ? AND is_notified = 0", (receiver,))
    res = c.fetchall()
    if res:
        c.execute("UPDATE shared_exams SET is_notified = 1 WHERE receiver = ?", (receiver,))
        conn.commit()
    conn.close()
    return res

def get_exams(username):
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute("SELECT subject, topic, mode, content, created_at FROM exams WHERE username = ? ORDER BY id DESC", (username,))
    res = c.fetchall()
    conn.close()
    return res

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.face_id = ""

# Giao diện Đăng nhập / Đăng ký
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>☕ ĐĂNG NHẬP HỆ THỐNG AI EDUCATION</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #757575; font-weight: normal; margin-bottom: 30px;'>☕ HỌC CÙNG AI - KIẾN TẠO TƯƠNG LAI</h4>", unsafe_allow_html=True)

    tab_log, tab_reg = st.tabs(["Đăng Nhập", "Đăng Ký"])
    with tab_log:
        u = st.text_input("Tên đăng nhập:", key="u_log")
        p = st.text_input("Mật khẩu:", type="password", key="p_log")
        f_id = st.text_input("Face ID cá nhân (Nhập 4 số tự chọn của bạn, ví dụ: 1234):", key="f_log")
        if st.button("Đăng Nhập ☕", use_container_width=True):
            if verify_user(u, p, f_id):
                st.session_state.authenticated = True
                st.session_state.username = u
                st.session_state.face_id = f_id
                st.success("Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("Sai tài khoản, mật khẩu hoặc Face ID!")
    with tab_reg:
        ru = st.text_input("Tài khoản mới:", key="ru_reg")
        rp = st.text_input("Mật khẩu mới:", type="password", key="rp_reg")
        rf = st.text_input("Tạo Face ID tự chọn của bạn (Mã gồm đúng 4 chữ số từ 0001 đến 9999):", key="rf_reg", max_chars=4)
        if st.button("Tạo Tài Khoản ✨", use_container_width=True):
            if ru and rp and rf:
                if not rf.isdigit() or len(rf) != 4:
                    st.error("Lỗi định dạng: Face ID của bạn bắt buộc phải chứa đúng 4 chữ số!")
                elif rf in ["0000"]:
                    st.error("Lỗi bảo mật: Không được phép tạo tài khoản có mã Face ID 0000!")
                else:
                    if add_user(ru, rp, rf):
                        st.success("Tạo tài khoản thành công! Hãy chuyển sang Đăng nhập với Face ID mới của bạn.")
                    else:
                        st.error("Tên tài khoản hoặc Face ID đã tồn tại trên hệ thống!")
            else:
                st.error("Vui lòng không để trống bất kỳ trường nào!")
else:
    prof = get_user_profile(st.session_state.username)

    # Quét thông báo đề thi mới được chia sẻ
    unnotified = check_unnotified_shares(st.session_state.username)
    for _, sender, s_subject, s_topic in unnotified:
        st.toast(f"✉️ {sender} vừa chia sẻ cho bạn đề thi môn {s_subject} về chủ đề {s_topic}! Hãy mở Tab LỊCH SỬ để xem.")

    # Thiết kế Sidebar Profile siêu tối giản mới
    profile_html = f'''<div style='display: flex; align-items: center; gap: 12px; margin-bottom: 15px;'>
        <img src="{prof['avatar']}" style='width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #1E88E5;' />
        <div>
            <h4 style='margin: 0; color: #1E88E5; font-size: 16px;'>{prof['display_name']}</h4>
            <code style='background-color: #f1f1f1; padding: 1px 4px; border-radius: 4px; font-size: 11px;'>ID: {prof['face_id']}</code>
        </div>
    </div>'''
    st.sidebar.markdown(profile_html, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # Phần chỉnh sửa hồ sơ
    with st.sidebar.expander("⚙️ Chỉnh sửa hồ sơ cá nhân"):
        new_name = st.text_input("Thay đổi tên hiển thị:", value=prof["display_name"])
        uploaded_avatar = st.file_uploader("Tải ảnh đại diện mới (.png, .jpg, .jpeg):", type=["png", "jpg", "jpeg"])
        if st.button("Lưu thay đổi 💾", use_container_width=True):
            avatar_b64 = None
            if uploaded_avatar is not None:
                raw_bytes = uploaded_avatar.read()
                encoded = base64.b64encode(raw_bytes).decode("utf-8")
                mime = uploaded_avatar.type
                avatar_b64 = f"data:{mime};base64,{encoded}"
            update_user_profile(st.session_state.username, new_name, avatar_b64)
            st.success("Đã lưu hồ sơ cá nhân mới!")
            st.rerun()

    # Phân quyền API Key bảo mật
    is_vip = st.session_state.username in ["t.bun", "No2"] and st.session_state.face_id in ["0001", "0002"]
    system_fallback_key = os.environ.get("GEMINI_API_KEY", "")

    if is_vip:
        api_key_input = st.sidebar.text_input("🔑 Gemini API Key (VIP được sửa):", value=system_fallback_key, type="password")
    else:
        api_key_input = system_fallback_key

    if st.sidebar.button("Đăng Xuất 🚪", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.face_id = ""
        st.rerun()

    # ==========================================
    # TÍNH NĂNG KẾT BẠN & TRÒ CHUYỆN Ở SIDEBAR
    # ==========================================
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 MẠNG XÃ HỘI HỌC TẬP")

    with st.sidebar.expander("🔍 Tìm bạn bè bằng Face ID"):
        friend_fid = st.text_input("Nhập Face ID của bạn học:")
        if st.button("Tìm kiếm & Kết bạn"):
            target_user = find_user_by_face_id(friend_fid)
            if target_user:
                if make_friend(st.session_state.username, target_user):
                    st.success(f"Đã kết bạn thành công với {target_user}!")
                    st.rerun()
                else:
                    st.info(f"Hai bạn đã là bạn bè hoặc đây là Face ID của chính bạn!")
            else:
                st.error("Không tìm thấy người dùng nào với mã Face ID này!")

    friend_list = get_friends_list(st.session_state.username)
    if friend_list:
        st.sidebar.markdown("**Bạn bè đã kết nối:**")
        for fr in friend_list:
            fr_prof = get_user_profile(fr)
            if st.sidebar.button(f"💬 {fr_prof['display_name']} (ID: {fr_prof['face_id']})", key=f"chat_{fr}", use_container_width=True):
                st.session_state["chat_active_with"] = fr
    else:
        st.sidebar.caption("Bạn chưa kết nối với ai. Hãy dùng mục tìm kiếm Face ID trên để kết bạn nhé!")

    if "chat_active_with" in st.session_state:
        target_chat = st.session_state["chat_active_with"]
        target_prof = get_user_profile(target_chat)
        st.sidebar.markdown(f"**Trò chuyện với {target_prof['display_name']}:**")
        chat_history = get_chat_history(st.session_state.username, target_chat)

        chat_container = ""
        for sender, message, _ in chat_history[-10:]:
            align = "Tôi" if sender == st.session_state.username else target_prof['display_name']
            chat_container += f"**{align}**: {message}\\n\\n"

        st.sidebar.markdown(chat_container if chat_container else "*Hãy gửi tin nhắn đầu tiên...*")

        new_msg = st.sidebar.text_input("Nhập nội dung tin nhắn:", key="send_new_msg_val")
        if st.sidebar.button("Gửi", key="btn_send_chat", use_container_width=True):
            if new_msg:
                send_chat_message(st.session_state.username, target_chat, new_msg)
                st.rerun()

    def goi_ai_sieu_toc(prompt, system_prompt=None):
        key = api_key_input
        if not key:
            raise Exception("Hệ thống chưa tìm thấy Gemini API Key khả dụng. Vui lòng liên hệ quản trị viên!")
        client = genai.Client(api_key=key)
        full_input = prompt
        if system_prompt:
            full_input = f"[QUY TẮC BẮT BUỘC]: {system_prompt}\\n\\n{prompt}"

        cac_models = ["gemini-3.8-flash"]
        last_exception = None

        for m_name in cac_models:
            for retry in range(2):
                try:
                    res = client.models.generate_content(
                        model=m_name,
                        contents=full_input,
                        config={"temperature": 0.95}
                    )
                    if hasattr(res, "text") and res.text:
                        return res.text
                except Exception as e:
                    last_exception = e
                    time.sleep((retry + 1) * 2)
                    continue
        raise last_exception

    tab1, tab2, tab4 = st.tabs(["📝 THI THỬ TRỰC TUYẾN", "📚 CHẮT LỌC TÀI LIỆU", "📂 LỊCH SỬ ĐỀ THI & CHIA SẺ"])

    with tab1:
        st.header("📝 Biên Soạn Đề Chuẩn & Làm Bài Trực Tuyến")
        c1, c2 = st.columns(2)
        with c1:
            mon = st.selectbox("Môn học:", ["Toán Học", "Vật Lý", "Hóa Học", "Sinh Học", "Tiếng Anh", "Tin Học"])
            bai = st.text_input("Chủ đề cụ thể:", value="Khảo sát hàm số")
        with c2:
            che_do = st.selectbox("Chọn cấu trúc phần thi:", [
                "Phần 1: Trắc nghiệm khách quan (18 câu - chọn 1 đáp án đúng trong 4 lựa chọn)",
                "Phần 2: Câu hỏi Đúng/Sai (12 câu - mỗi câu có các khẳng định đúng/sai)",
                "Phần 3: Câu hỏi Trả lời ngắn (8 câu - gồm toán cơ bản và thực tế ứng dụng)",
                "Phần 4: Nguyên đề tổng hợp (Phần 1: 18 câu, Phần 2: 4 câu, Phần 3: 6 câu)"
            ])
            thang_diem = st.selectbox("Mục tiêu Thang điểm đạt:", ["7đ", "8đ", "9đ", "10đ"])

        system_inst = '''Bạn là chuyên gia biên soạn đề thi chuẩn học thuật cực kỳ trực quan. Hãy trả về kết quả dưới định dạng JSON duy nhất. Không thêm bất kỳ văn bản giải thích nào ngoài chuỗi JSON.
Format JSON cấu trúc như sau:
{
  "questions": [
     {
       "id": 1,
       "type": "choice",
       "text": "Câu hỏi...",
       "options": ["A. Phương án 1", "B. Phương án 2", "C. Phương án 3", "D. Phương án 4"],
       "correct_answer": "A",
       "image_desc": "Mô tả hình vẽ hoặc đồ thị cụ thể để minh họa cho bài toán"
     },
     {
       "id": 2,
       "type": "true_false",
       "text": "Khẳng định cần đánh giá...",
       "options": ["Đúng", "Sai"],
       "correct_answer": "Đúng"
     },
     {
       "id": 3,
       "type": "short_answer",
       "text": "Câu hỏi thực tế hoặc tính toán...",
       "correct_answer": "Số hoặc chữ ngắn gọn"
     }
  ]
}

[QUY TẮC BẮT BUỘC ĐỂ KHÔNG BAO GIỜ TRÙNG ĐỀ THI]:
1. Thay đổi toàn diện: Bạn phải thay đổi hoàn toàn nội dung, các trị số toán học so với các phiên bản trước.
2. Thiết kế thông minh với các số liệu ngẫu nhiên khác nhau rõ rệt.
3. Đối với loại câu hỏi "choice", trường "correct_answer" BẮT BUỘC chỉ được chứa đúng duy nhất 1 ký tự chữ cái viết hoa đại diện là "A" hoặc "B" hoặc "C" hoặc "D".
4. Tránh lỗi font và ký tự lạ: Tuyệt đối không sử dụng các ký tự toán học LaTeX phức tạp. Các biểu thức toán học phải được viết dưới dạng ký tự đơn giản, rõ chữ.'''

        if st.button("🚀 TẠO ĐỀ THI NGAY", use_container_width=True):
            with st.spinner("AI đang soạn đề thi mới lạ, vui lòng chờ trong giây lát..."):
                try:
                    seed_rand = random.randint(1000000, 9999999)
                    prompt_gen = f"Tạo một đề thi hoàn toàn độc nhất vô nhị môn {mon}, chủ đề: '{bai}' (Hạt giống: {seed_rand}). Cấu trúc: {che_do}. Mục tiêu điểm: {thang_diem}. Chỉ trả về duy nhất chuỗi JSON chuẩn định dạng theo chỉ dẫn, không giải thích."
                    output_raw = goi_ai_sieu_toc(prompt_gen, system_prompt=system_inst)

                    clean_json = output_raw.strip()
                    if "```json" in clean_json:
                        clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                    elif "```" in clean_json:
                        clean_json = clean_json.split("```")[1].split("```")[0].strip()

                    parsed_exam = json.loads(clean_json)
                    st.session_state["current_exam"] = parsed_exam
                    st.session_state["answers_submitted"] = False
                    st.session_state["user_answers"] = {}
                    st.success("✅ Đã tạo đề thi thành công! Nhấn vào các câu hỏi bên dưới để làm bài thi trực tiếp.")

                    save_exam(st.session_state.username, mon, bai, che_do, clean_json)
                except Exception as e:
                    st.error(f"Trạng thái tạo đề: {e}")

        if "current_exam" in st.session_state:
            st.divider()
            st.subheader("📝 Đề thi đang làm trực tuyến")
            exam_data = st.session_state["current_exam"]
            questions = exam_data.get("questions", [])

            for i, q in enumerate(questions):
                st.markdown(f"**Câu {i+1}:** {q.get('text')}")
                if q.get("image_desc"):
                    st.info(f"🎨 [Mô tả hình vẽ]: {q.get('image_desc')}")

                q_id = str(q.get("id", i))
                if q.get("type") == "choice":
                    opts = q.get("options", [])
                    st.session_state["user_answers"][q_id] = st.radio(
                        "Chọn đáp án:", opts, key=f"q_{q_id}", label_visibility="collapsed"
                    )
                elif q.get("type") == "true_false":
                    st.session_state["user_answers"][q_id] = st.radio(
                        "Chọn Đúng/Sai:", ["Đúng", "Sai"], key=f"q_{q_id}", label_visibility="collapsed"
                    )
                elif q.get("type") == "short_answer":
                    st.session_state["user_answers"][q_id] = st.text_input(
                        "Nhập đáp án ngắn:", key=f"q_{q_id}", label_visibility="collapsed"
                    )
                st.divider()

            if not st.session_state["answers_submitted"]:
                if st.button("📝 NỘP BÀI & CHẤM ĐIỂM", use_container_width=True):
                    st.session_state["answers_submitted"] = True
                    st.rerun()
            else:
                st.header("📊 KẾT QUẢ BÀI THI CỦA BẠN")
                correct_count = 0
                total_q = len(questions)

                for i, q in enumerate(questions):
                    q_id = str(q.get("id", i))
                    u_ans = st.session_state["user_answers"].get(q_id, "")
                    c_ans = q.get("correct_answer", "")

                    is_correct = False
                    if q.get("type") == "choice":
                        u_char = u_ans[0] if u_ans else ""
                        is_correct = (u_char.upper() == c_ans.upper() or c_ans.upper() in u_ans.upper())
                    else:
                        is_correct = (str(u_ans).strip().lower() == str(c_ans).strip().lower())

                    if is_correct:
                        correct_count += 1
                        st.write(f"✅ **Câu {i+1}**: Đúng! (Bạn chọn: {u_ans})")
                    else:
                        st.write(f"❌ **Câu {i+1}**: Chưa chính xác. Bạn chọn: `{u_ans}` | Đáp án đúng: `{c_ans}`")

                score = round((correct_count / total_q) * 10.0, 2) if total_q > 0 else 0.0
                target_val = float(thang_diem.replace("đ", ""))

                st.metric("Điểm số đạt được", f" {score} / 10.0đ")
                if score >= target_val:
                    st.balloons()
                    st.success(f"🎉 Tuyệt vời! Bạn đạt {score}đ, vượt mức mục tiêu là {thang_diem}.")
                else:
                    st.warning(f"⚠️ Bạn đạt {score}đ, cố gắng ôn tập thêm để đạt mục tiêu nhé!")

    with tab2:
        st.header("📚 Chắt Lọc Tài Liệu Siêu Tốc")
        files = st.file_uploader("Tải file tài liệu (.txt, .md):", accept_multiple_files=True, type=["txt", "md"])
        if st.button("🔍 TRÍCH XUẤT KIẾN THỨC CỐT LÕI", use_container_width=True):
            if not files:
                st.warning("Vui lòng tải tập tin lên!")
            else:
                with st.spinner("AI đang đọc và tổng hợp..."):
                    try:
                        nd = "".join([f"\\n--- {f.name} ---\\n" + f.read().decode("utf-8", errors="ignore") for f in files])
                        prompt = f"Trích xuất nhanh các công thức, định nghĩa và mẹo giải quan trọng từ tài liệu sau:\\n\\n{nd[:10000]}"
                        res = goi_ai_sieu_toc(prompt)
                        st.success("✅ Trích xuất hoàn thành!")
                        st.markdown(res)
                    except Exception as e:
                        st.error(f"Lỗi xử lý tài liệu: {e}")

    with tab4:
        st.header("📂 Kho Đề Thi Học Tập")
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("📝 Đề Thi Đã Lưu Cá Nhân")
            danh_sach = get_exams(st.session_state.username)
            if not danh_sach:
                st.info("Chưa có đề thi cá nhân nào được lưu.")
            else:
                for s, t, m, c, time_created in danh_sach:
                    with st.expander(f"📝 [{s}] {t} ({time_created})"):
                        if st.button("Tải lại đề thi này để làm bài 🔄", key=f"reload_{time_created}"):
                            try:
                                st.session_state["current_exam"] = json.loads(c)
                                st.session_state["answers_submitted"] = False
                                st.session_state["user_answers"] = {}
                                st.success("Đã nạp lại đề thi! Hãy chuyển qua tab 1 để bắt đầu.")
                            except Exception:
                                st.markdown(c)
                        if friend_list:
                            friend_to_share = st.selectbox("Chọn bạn học để chia sẻ:", friend_list, key=f"share_select_{time_created}")
                            if st.button("Chia sẻ đề thi ✈️", key=f"share_btn_{time_created}"):
                                share_exam_with_friend(st.session_state.username, friend_to_share, s, t, m, c)
                                st.success(f"Đã gửi đề thi thành công tới {friend_to_share}!")
                        else:
                            st.caption("Kết bạn ở mục Bạn bè để mở khóa tính năng chia sẻ đề thi nhé!")
        with col_b:
            st.subheader("📬 Đề Thi Nhận Được Từ Bạn Bè")
            de_chia_se = get_shared_exams(st.session_state.username)
            if not de_chia_se:
                st.info("Kho lưu trữ trống.")
            else:
                for sender, s, t, m, c, time_created in de_chia_se:
                    with st.expander(f"📬 Từ {sender}: [{s}] {t}"):
                        st.caption(f"Nhận lúc: {time_created}")
                        if st.button("Nạp đề thi làm bài ⚡", key=f"load_shared_{time_created}_{sender}"):
                            try:
                                st.session_state["current_exam"] = json.loads(c)
                                st.session_state["answers_submitted"] = False
                                st.session_state["user_answers"] = {}
                                st.success("Đã nạp đề thi từ bạn bè! Hãy chuyển sang Tab 1 để làm bài ngay.")
                            except Exception:
                                st.markdown(c)
"""

# Ghi file app.py
with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_source_code)
print("✅ Ghi file app.py thành công!")

# KHỞI CHẠY STREAMLIT & NGROK
ngrok.kill()
try:
    ngrok.set_auth_token(AUTHTOKEN_MOI)
except Exception as auth_err:
    print("ℹ️ Authtoken đã được lưu cấu hình trước đó, bỏ qua bước đăng ký mới.")

print("⚙️ Đang khởi chạy ứng dụng Streamlit...")
process = subprocess.Popen(["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Tăng thời gian chờ đợi lên 10 giây để đảm bảo Streamlit khởi động hoàn tất trước khi mở cổng
time.sleep(10)

try:
    public_url = ngrok.connect(8501)
    print("\n======================================================================")
    print("⚡ ĐÃ THIẾT LẬP LINK TRANG WEB THÀNH CÔNG!")
    print(f"🔗 Link truy cập của bạn ở đây: {public_url.public_url}")
    print("======================================================================")
except Exception as e:
    print(f"❌ Lỗi khi thiết lập ngrok: {e}")
