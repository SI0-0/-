import streamlit as st
from docx2pdf import convert
from pdf2image import convert_from_path
import os

# 페이지 설정
st.set_page_config(page_title="DOCX → 이미지 변환기", page_icon="🖼️", layout="centered")

# 스타일
st.markdown("""
<style>
.title { font-size:2.4rem; font-weight:700; text-align:center; margin-bottom:0.3rem; }
.subtitle { text-align:center; font-size:1.1rem; color:#666; margin-bottom:2rem; }
.page-card { padding:1rem; border-radius:16px; background:#f9f9f9; margin-bottom:1rem; border:1px solid #e3e3e3; box-shadow: 0px 3px 8px rgba(0,0,0,0.05);}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📄 DOCX → 이미지 변환기</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">업로드한 Word 문서를 모든 페이지 PNG로 변환하여 확인 및 다운로드할 수 있습니다.</div>', unsafe_allow_html=True)

# --------------------------
uploaded_file = st.file_uploader("📤 Word(.docx) 파일을 선택하세요", type=["docx"])
# --------------------------

def docx_to_png_list(docx_file_path):
    # Word -> PDF
    pdf_file = "temp.pdf"
    convert(docx_file_path, pdf_file)
    # PDF -> 이미지
    pages = convert_from_path(pdf_file)
    os.remove(pdf_file)
    return pages

if uploaded_file:
    # 임시 저장
    temp_docx = "temp_uploaded.docx"
    with open(temp_docx, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🖼 변환 시작"):
        with st.spinner("⏳ 변환 중..."):
            images = docx_to_png_list(temp_docx)
        st.success(f"✅ 변환 완료! 총 {len(images)} 페이지")
        os.remove(temp_docx)

        # 페이지별 카드 UI
        for i, img in enumerate(images):
            st.markdown('<div class="page-card">', unsafe_allow_html=True)
            st.image(img, caption=f"페이지 {i+1}", use_column_width=True)
            png_name = f"page_{i+1}.png"
            img.save(png_name, "PNG")
            with open(png_name, "rb") as f:
                st.download_button(f"⬇️ 페이지 {i+1} 다운로드", f, file_name=png_name, key=i)
            st.markdown('</div>', unsafe_allow_html=True)
            os.remove(png_name)
