import streamlit as st
import requests
from docx2pdf import convert
from pdf2image import convert_from_path
import os

st.set_page_config(page_title="GitHub DOCX → 이미지", page_icon="🖼️", layout="centered")
st.title("📄 GitHub Word(.docx) → 이미지 변환기")
st.write("GitHub의 Word 문서를 바로 PNG 이미지로 변환합니다.")

# --------------------------
# 사용자 입력
docx_url = st.text_input("🔗 GitHub .docx 파일 URL")
image_name = st.text_input("🖼 저장할 이미지 이름", "output.png")
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

def docx_to_png(docx_file, output_file):
    # Word -> PDF
    pdf_file = "temp.pdf"
    convert(docx_file, pdf_file)
    # PDF -> 이미지
    pages = convert_from_path(pdf_file)
    if pages:
        # 첫 페이지만 저장
        pages[0].save(output_file, "PNG")
        os.remove(pdf_file)
        return True
    return False

if st.button("🖼 변환 시작"):
    if not docx_url:
        st.warning("URL을 입력해주세요!")
    else:
        local_docx = "temp.docx"
        if download_docx(docx_url, local_docx):
            success = docx_to_png(local_docx, image_name)
            if success:
                st.success(f"✅ 변환 완료: {image_name}")
                st.image(image_name, caption="변환된 이미지", use_column_width=True)
                with open(image_name, "rb") as f:
                    st.download_button("⬇️ 이미지 다운로드", f, file_name=image_name)
            else:
                st.error("❌ 변환 실패")
            os.remove(local_docx)
