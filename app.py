import streamlit as st
import sqlite3
import random
import json
import base64
from datetime import datetime

# Thiết lập cấu hình trang
st.set_page_config(
    page_title="Giáo dục AI KHKT - Học Cùng AI",
    page_icon="🤖",
    layout="wide"
)

# Hàm gọi AI siêu tốc với bộ lọc chống lỗi font ASCII
def goi_ai_sieu_toc(prompt, system_prompt=None):
    if isinstance(prompt, str):
        prompt = prompt.encode("utf-8", errors="ignore").decode("utf-8")
    if system_prompt and isinstance(system_prompt, str):
        system_prompt = system_prompt.encode("utf-8", errors="ignore").decode("utf-8")
        
    key = st.session_state.get("api_key_input", "")
    
    from google import genai
    client = genai.Client(api_key=key if key else None)
    
    config = {}
    if system_prompt:
        config["system_instruction"] = system_prompt
        
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
        config=config if config else None
    )
    return response.text

# Khởi tạo cơ sở dữ liệu SQLite
def init_db():
    conn = sqlite3.connect("users_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    display_name TEXT,
                    avatar TEXT,
                    face_id TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS friends (
                    user1 TEXT,
                    user2 TEXT,
                    UNIQUE(user1, user2)
                )''')
    conn.commit()
    conn.close()

init_db()

# Quản lý trạng thái phiên đăng nhập mặc định
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = True
if "username" not in st.session_state:
    st.session_state["username"] = "t.bun"

# Giao diện chính hiển thị các tab chức năng
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
        thang_diem = st.selectbox("Mức tiêu Thang điểm đạt:", ["7đ", "8đ", "9đ", "10đ"])

    if st.button("🚀 TẠO ĐỀ THI NGAY", use_container_width=True):
        with st.spinner("AI đang soạn đề thi mới lạ, vui lòng chờ trong giây lát..."):
            try:
                seed_rand = random.randint(1000000, 9999999)
                prompt_gen = f"Tạo một đề thi hoàn đoàn độc nhất vô nhị môn {mon}, chủ đề: '{bai}' (Hạt giống: {seed_rand}). Trả về định dạng JSON thuần túy."
                system_inst = "Bạn là chuyên gia ra đề thi chuẩn giáo dục. Chỉ trả về JSON."
                
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
                st.success("✅ Đã tạo đề thi thành công! Nhắn vào các câu hỏi bên dưới để làm bài thi trực tiếp.")
            except Exception as e:
                st.error(f"Trạng thái tạo đề: {e}")

with tab2:
    st.header("📚 Chắt Lọc Tài Liệu Học Tập")
    st.info("Khu vực tra cứu và tổng hợp lý thuyết thông minh.")

with tab4:
    st.header("📂 Lịch Sử Đề Thi & Chia Sẻ Mạng Xã Hội")
    st.info("Xem lại các đề thi đã lưu và chia sẻ kết quả với bạn bè.")
