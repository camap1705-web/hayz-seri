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
        model='gemini-2.5-flash',
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
    c.execute('''CREATE TABLE IF NOT EXISTS exam_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    subject TEXT,
                    exam_data TEXT,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# Quản lý trạng thái phiên đăng nhập mặc định
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = True
if "username" not in st.session_state:
    st.session_state["username"] = "t.bun"

# Khung giao diện chính với các tab chức năng đầy đủ
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
                
                # Lưu vào lịch sử database
                conn = sqlite3.connect("users_data.db")
                c = conn.cursor()
                c.execute("INSERT INTO exam_history (username, subject, exam_data, timestamp) VALUES (?, ?, ?, ?)",
                          (st.session_state["username"], mon, json.dumps(parsed_exam, ensure_ascii=False), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()

                st.success("✅ Đã tạo đề thi thành công! Kéo xuống dưới hoặc chuyển tab để làm bài.")
            except Exception as e:
                st.error(f"Lỗi khi tạo đề: {e}")

    # Hiển thị đề thi hiện tại nếu đã được tạo
    if "current_exam" in st.session_state and st.session_state["current_exam"]:
        st.markdown("---")
        st.subheader("📄 Đề Thi Hiện Tại")
        st.json(st.session_state["current_exam"])

with tab2:
    st.header("📚 Chắt Lọc Tài Liệu Học Tập")
    st.info("Khu vực tra cứu, tổng hợp lý thuyết và tài liệu ôn tập thông minh cho dự án KHKT.")
    
    # Khu vực tìm kiếm tài liệu
    keyword_tai_lieu = st.text_input("Tìm kiếm lý thuyết hoặc công thức trọng tâm:")
    if keyword_tai_lieu:
        with st.spinner("Đang chắt lọc tài liệu..."):
            prompt_tl = f"Tổng hợp kiến thức trọng tâm ngắn gọn về: {keyword_tai_lieu}"
            ket_qua_tl = goi_ai_sieu_toc(prompt_tl)
            st.markdown(ket_qua_tl)

with tab4:
    st.header("📂 Lịch Sử Đề Thi & Chia Sẻ Mạng Xã Hội")
    st.info("Danh sách các đề thi bạn đã từng tạo và lưu trữ trên hệ thống:")
    
    try:
        conn = sqlite3.connect("users_data.db")
        c = conn.cursor()
        c.execute("SELECT subject, exam_data, timestamp FROM exam_history WHERE username = ? ORDER BY id DESC", (st.session_state["username"],))
        history_rows = c.fetchall()
        conn.close()
        
        if history_rows:
            for idx, (sub, edata, ts) in enumerate(history_rows):
                with st.expander(f"📌 Đề môn {sub} - Tạo lúc: {ts}"):
                    st.text(f"Môn học: {sub} | Thời gian: {ts}")
                    if st.button(f"Tải lại đề này #{idx}", key=f"load_hist_{idx}"):
                        st.session_state["current_exam"] = json.loads(edata)
                        st.success("Đã tải lại đề thi vào tab Thi Thử!")
        else:
            st.write("Chưa có lịch sử đề thi nào được lưu.")
    except Exception as e:
        st.write("Đang khởi tạo cơ sở dữ liệu lịch sử...")
