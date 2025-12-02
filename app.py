import streamlit as st
import zipfile
from xml.etree import ElementTree as ET

# --------------------------
# 예시 글꼴 → 다운로드 링크 매핑
FONT_LINKS = {
    "Roboto": "https://fonts.google.com/specimen/Roboto",
    "Open Sans": "https://fonts.google.com/specimen/Open+Sans",
    "Arial": "https://www.wfonts.com/font/arial",
    "Times New Roman": "https://www.wfonts.com/font/times-new-roman",
    "Calibri": "https://www.wfonts.com/font/calibri",
    "Verdana": "https://www.wfonts.com/font/verdana",
    # 필요한 글꼴 추가 가능
}

def extract_fonts_from_pptx(pptx_file):
    fonts = set()
    with zipfile.ZipFile(pptx_file) as pptx_zip:
        for file in pptx_zip.namelist():
            if file.startswith("ppt/slides/slide") and file.endswith(".xml"):
                xml_data = pptx_zip.read(file)
                try:
                    root = ET.fromstring(xml_data)
                except ET.ParseError:
                    continue
                for elem in root.iter():
                    font = elem.attrib.get("{http://schemas.openxmlformats.org/drawingml/2006/main}typeface")
                    if font:
                        fonts.add(font)
    return fonts
# --------------------------

# --------------------------
# Streamlit GUI
st.set_page_config(page_title="PPT 글꼴 확인기", page_icon="🎨", layout="centered")

st.markdown("""
<style>
.title { font-size:2.4rem; font-weight:700; text-align:center; margin-bottom:0.3rem; }
.subtitle { text-align:center; font-size:1.1rem; color:#666; margin-bottom:2rem; }
.card { padding:1rem; border-radius:16px; background:#f9f9f9; margin-bottom:1rem; border:1px solid #e3e3e3; box-shadow:0px 3px 10px rgba(0,0,0,0.05);}
.card a { text-decoration:none; color:#1f77b4; font-weight:600;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎨 PPT 글꼴 확인기</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">업로드한 PPTX 파일에서 사용된 글꼴을 추출하고 다운로드 링크를 제공합니다.</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 PPTX 파일 선택", type=["pptx"])

if uploaded_file:
    st.info("⚡ 분석 중...")
    fonts = extract_fonts_from_pptx(uploaded_file)

    if fonts:
        st.success(f"✅ 발견된 글꼴 {len(fonts)}개")

        # 카드형으로 글꼴 + 링크 출력
        for font in sorted(fonts):
            link = FONT_LINKS.get(font)
            if link:
                st.markdown(f'<div class="card">{font} → <a href="{link}" target="_blank">다운로드 / 사이트 방문</a></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="card">{font} → 링크 없음</div>', unsafe_allow_html=True)
    else:
        st.warning("❌ 글꼴을 찾지 못했습니다. PPTX에 텍스트가 없거나 XML 구조가 표준과 다를 수 있습니다.")
