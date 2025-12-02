import streamlit as st
import requests
from docx2pdf import convert
from pdf2image import convert_from_path
import os

# 페이지 설정
st.set_page_config(page_title="GitHub DOCX → 이미지", page_icon="🖼️", layout="centered")

# 스타일 커스터마이징
st.markdown("""
<style>
.title { font-size:2.4rem; font-weight:700; text-align:center; margin-bottom:0.3rem; }
.subtitle { text-align:center; font-size:1.1rem; color:#666; margin-bottom:2rem; }
.page-card { padding:1rem; border-radius:16px; background:#f9f9f9; margin-bottom:1rem; border:1px solid #e3e3e3; box-shadow: 0px 3px 8px rgba(0,0,0,0.05);}
.download-btn { background-color: #4CAF50; color:white; border-radius:8px; padding:0.4rem 0.8rem; font-weight:600;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📄 GitHub Word(.docx) → 이미지</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">모든 페이지를 PNG로 변환하여 슬라이드처럼 확인하고 다운로드하세요.</div>', unsafe_allow_html=True)

# --------------------------
docx_url = st.text_input("🔗 GitHub .docx 파일 URL")
# --------------------------

def download_docx(url, filename):
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(filename, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        st.error(f"❌ 다운로드 실패: {e}")
        return False

def docx_to_png_list(docx_file):
    pdf_file = "temp.pdf"
    convert(docx_file, pdf_file)
    pages = convert_from_path(pdf_file)
    os.remove(pdf_file)
    return pages

if st.button("🖼 변환 시작"):
    if not docx_url:
        st.warning("URL을 입력해주세요!")
    else:
        local_docx = "temp.docx"
        if download_docx(docx_url, local_docx):
            with st.spinner("⏳ 변환 중..."):
                images = docx_to_png_list(local_docx)
            st.success(f"✅ 변환 완료! 총 {len(images)} 페이지")
            os.remove(local_docx)

            # 페이지별 카드형 UI
            for i, img in enumerate(images):
                st.markdown('<div class="page-card">', unsafe_allow_html=True)
                st.image(img, caption=f"페이지 {i+1}", use_column_width=True)
                png_name = f"page_{i+1}.png"
                img.save(png_name, "PNG")
                with open(png_name, "rb") as f:
                    st.download_button(f"⬇️ 페이지 {i+1} 다운로드", f, file_name=png_name, key=i)
                st.markdown('</div>', unsafe_allow_html=True)
                os.remove(png_name)
