import streamlit as st
from pdf2image import convert_from_path
import subprocess
import tempfile
import os

# --------------------------
def docx_to_pdf(docx_path, pdf_path):
    out_dir = os.path.dirname(pdf_path)
    subprocess.run([
        'libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', out_dir, docx_path
    ], check=True)
    input_pdf_name = os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
    os.rename(os.path.join(out_dir, input_pdf_name), pdf_path)

def docx_to_png_list(docx_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
        tmp_docx.write(docx_file.getbuffer())
        tmp_docx_path = tmp_docx.name

    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    docx_to_pdf(tmp_docx_path, pdf_file)
    images = convert_from_path(pdf_file)
    os.remove(tmp_docx_path)
    os.remove(pdf_file)
    return images
# --------------------------

# Streamlit GUI
st.set_page_config(page_title="DOCX → 이미지 변환기", page_icon="🖼️", layout="centered")
st.markdown("""
<style>
.title { font-size:2.4rem; font-weight:700; text-align:center; margin-bottom:0.3rem; }
.subtitle { text-align:center; font-size:1.1rem; color:#666; margin-bottom:2rem; }
.page-card { padding:1rem; border-radius:16px; background:#f9f9f9; margin-bottom:1.5rem; border:1px solid #e3e3e3; box-shadow: 0px 3px 10px rgba(0,0,0,0.05);}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📄 DOCX → 이미지 변환기</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">업로드한 Word 문서를 페이지별 PNG로 변환하여 확인 및 다운로드합니다.</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Word(.docx) 파일 선택", type=["docx"])

if uploaded_file:
    if st.button("🖼 변환 시작"):
        with st.spinner("⏳ 변환 중..."):
            images = docx_to_png_list(uploaded_file)
        st.success(f"✅ 변환 완료! 총 {len(images)} 페이지")
        
        # 페이지별 카드 UI
        import tempfile
        for i, img in enumerate(images):
            st.markdown('<div class="page-card">', unsafe_allow_html=True)
            st.image(img, caption=f"페이지 {i+1}", use_column_width=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                img.save(tmp_img.name, "PNG")
                with open(tmp_img.name, "rb") as f:
                    st.download_button(f"⬇️ 페이지 {i+1} 다운로드", f, file_name=f"page_{i+1}.png", key=i, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
