import streamlit as st
from docx import Document
from PIL import Image, ImageDraw, ImageFont
import tempfile

# --------------------------
def docx_to_images(docx_file):
    doc = Document(docx_file)
    images = []
    
    img_width, img_height = 1200, 1600
    margin = 50
    line_height = 40
    font_size = 24
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    img = Image.new("RGB", (img_width, img_height), color="white")
    draw = ImageDraw.Draw(img)
    y = margin
    
    for para in doc.paragraphs:
        text = para.text
        if not text.strip():
            y += line_height
            continue
        
        if para.runs:
            for run in para.runs:
                run_text = run.text
                display_text = run_text
                if run.bold:
                    display_text = f"**{run_text}**"
                if run.italic:
                    display_text = f"*{display_text}*"
                draw.text((margin, y), display_text, fill="black", font=font)
                y += line_height
        else:
            draw.text((margin, y), text, fill="black", font=font)
            y += line_height
        
        if y > img_height - margin:
            images.append(img)
            img = Image.new("RGB", (img_width, img_height), color="white")
            draw = ImageDraw.Draw(img)
            y = margin
    
    images.append(img)
    return images
# --------------------------

# --------------------------
# Streamlit GUI
st.set_page_config(page_title="DOCX → 이미지 변환기", page_icon="🖼️", layout="centered")

# 스타일
st.markdown("""
<style>
.title { font-size:2.4rem; font-weight:700; text-align:center; margin-bottom:0.3rem; }
.subtitle { text-align:center; font-size:1.1rem; color:#666; margin-bottom:2rem; }
.page-card { padding:1rem; border-radius:16px; background:#f9f9f9; margin-bottom:1.5rem; border:1px solid #e3e3e3; box-shadow: 0px 3px 10px rgba(0,0,0,0.05);}
.download-btn { margin-top:0.5rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📄 DOCX → 이미지 변환기</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">업로드한 Word 문서를 이미지로 변환하여 페이지별로 확인하고 다운로드할 수 있습니다.</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Word(.docx) 파일 선택", type=["docx"])

if uploaded_file:
    if st.button("🖼 변환 시작"):
        with st.spinner("⏳ 변환 중..."):
            images = docx_to_images(uploaded_file)
        st.success(f"✅ 변환 완료! 총 {len(images)} 페이지")

        # 페이지별 카드 UI
        for i, img in enumerate(images):
            st.markdown('<div class="page-card">', unsafe_allow_html=True)
            st.image(img, caption=f"페이지 {i+1}", use_column_width=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                img.save(tmp_img.name, "PNG")
                with open(tmp_img.name, "rb") as f:
                    st.download_button(f"⬇️ 페이지 {i+1} 다운로드", f, file_name=f"page_{i+1}.png", key=i, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
