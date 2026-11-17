import streamlit as st
import sqlite3
import random
import json

# Cấu hình trang
st.set_page_config(
    page_title="Học Cùng AI - KHKT",
    page_icon="🤖",
    layout="wide"
)

# Hàm gọi AI siêu tốc kèm chống lỗi font tiếng Việt
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

# Giao diện chính đơn giản để tạo đề thi
st.header("📝 Trình Tạo Đề Thi Nhanh Cùng AI")

col1, col2 = st.columns(2)
with col1:
    mon = st.selectbox("Chọn môn học:", ["Toán Học", "Vật Lý", "Hóa Học", "Sinh Học", "Tiếng Anh", "Tin Học"])
    bai = st.text_input("Nhập chủ đề cụ thể:", value="Khảo sát hàm số")
with col2:
    che_do = st.selectbox("Cấu trúc đề:", [
        "Trắc nghiệm khách quan (18 câu)",
        "Câu hỏi Đúng/Sai (12 câu)",
        "Câu hỏi Trả lời ngắn (8 câu)"
    ])
    thang_diem = st.selectbox("Thang điểm:", ["7đ", "8đ", "9đ", "10đ"])

if st.button("🚀 TẠO ĐỀ THI NGAY", use_container_width=True):
    with st.spinner("Đang kết nối AI để biên soạn đề thi..."):
        try:
            seed_rand = random.randint(100000, 999999)
            prompt_gen = f"Tạo một đề thi môn {mon}, chủ đề: '{bai}', yêu cầu dạng {che_do} (Mã đề: {seed_rand}). Trả về định dạng JSON thuần túy gồm danh sách câu hỏi, đáp án và lời giải."
            system_inst = "Bạn là chuyên gia ra đề thi giáo dục. Chỉ trả về JSON thuần túy, không kèm văn bản ngoài."
            
            output_raw = goi_ai_sieu_toc(prompt_gen, system_prompt=system_inst)
            clean_json = output_raw.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()

            parsed_exam = json.loads(clean_json)
            st.success("✅ Tạo đề thi thành công tuyệt đối!")
            st.json(parsed_exam)
        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi gọi AI: {e}")
