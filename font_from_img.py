import streamlit as st
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import cv2
import os
from skimage.feature import hog
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="폰트 찾기", layout="centered", page_icon="🔍")

# ==================== CSS ====================
st.markdown("""
<style>
    .title {
        font-size: 2.3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .font-card {
        padding: 1rem;
        border-radius: 12px;
        background: #f7f7f9;
        margin-bottom: 0.7rem;
        border: 1px solid #e1e1e6;
    }
    .font-name {
        font-size: 1.05rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 헤더 ====================
st.markdown('<div class="title">🔍 이미지 → 비슷한 폰트 찾기</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">이미지를 업로드하면 비슷한 폰트를 찾아드립니다.</div>', unsafe_allow_html=True)

# ==================== 폰트 폴더 설정 ====================
FONT_DIR = "fonts"

if not os.path.exists(FONT_DIR):
    os.makedirs(FONT_DIR)
    st.warning("⚠️ fonts/ 폴더가 없어 새로 생성했습니다. 여기에 .ttf 또는 .otf 파일을 넣어주세요!")

# ==================== 이미지 업로드 ====================
uploaded_file = st.file_uploader("이미지를 업로드하세요.", type=["png","jpg","jpeg","bmp"])

# ==================== HOG 특징 추출 함수 ====================
def extract_hog(gray):
    return hog(gray, pixels_per_cell=(16,16), cells_per_block=(2,2), feature_vector=True)

# ==================== 텍스트 박스 추출 ====================
def extract_text_area(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5))
    dilated = cv2.dilate(th, kernel, 2)

    cnts, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    x, y, w, h = cv2.boundingRect(max(cnts, key=cv2.contourArea))
    return img[y:y+h, x:x+w]

# ==================== 폰트 렌더링 ====================
def render_font_sample(text, font_path, size=80):
    img = Image.new("L", (500, 120), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, size)
    draw.text((10, 10), text, fill=0, font=font)
    return np.array(img)

# ==================== 메인 기능 ====================
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="업로드된 이미지", use_column_width=True)

    img_np = np.array(image)
    text_region = extract_text_area(img_np)

    if text_region is None:
        st.error("❗ 텍스트 영역을 찾지 못했습니다.")
        st.stop()

    st.image(text_region, caption="감지된 텍스트 영역", use_column_width=True)

    user_text = st.text_input("비교에 사용할 문자 입력 (예: ABC / 가나 / 테스트)", "테스트")

    if st.button("🔎 비슷한 폰트 찾기"):
        with st.spinner("폰트를 분석하는 중입니다..."):
            gray = cv2.cvtColor(text_region, cv2.COLOR_RGB2GRAY)
            gray = cv2.resize(gray, (300, 100))
            target_hog = extract_hog(gray).reshape(1, -1)

            results = []
            for font_file in os.listdir(FONT_DIR):
                if font_file.endswith((".ttf", ".otf")):
                    font_path = os.path.join(FONT_DIR, font_file)
                    sample = render_font_sample(user_text, font_path)
                    sample = cv2.resize(sample, (300, 100))
                    font_hog = extract_hog(sample).reshape(1, -1)

                    sim = cosine_similarity(target_hog, font_hog)[0][0]
                    results.append((font_file, sim))

            results.sort(key=lambda x: x[1], reverse=True)

        st.success("🎉 분석 완료! 비슷한 폰트 Top 결과입니다:")

        for fname, score in results[:10]:
            st.markdown(f"""
                <div class="font-card">
                    <div class="font-name">{fname}</div>
                    <div style="font-size:0.9rem;color:#888;">유사도: {score*100:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
