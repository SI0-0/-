import streamlit as st
from PIL import Image
import numpy as np
import cv2
from font_classify import FontClassifier  # GitHub 패키지
import torch

st.set_page_config(
    page_title="AI 폰트 찾기",
    page_icon="🔍",
    layout="centered"
)

# ===============================
#   Custom UI 스타일
# ===============================
st.markdown("""
<style>
.title {
    font-size: 2.3rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.7rem;
}
.subtitle {
    text-align: center;
    font-size: 1.05rem;
    color: #666;
    margin-bottom: 2rem;
}
.font-card {
    padding: 1rem;
    border-radius: 14px;
    background: #fafafa;
    margin-bottom: 0.7rem;
    border: 1px solid #e3e3e3;
}
.font-name {
    font-size: 1.1rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ===============================
#   Header
# ===============================
st.markdown('<div class="title">🔍 AI 폰트 찾기</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">업로드한 이미지에서 글자 영역을 추출하고,<br>AI가 비슷한 폰트를 자동으로 추천합니다.</div>', unsafe_allow_html=True)


# ===============================
#   Font Classifier 로드
# ===============================
@st.cache_resource
def load_model():
    # pretrained=True → GitHub 모델 자동 다운로드
    return FontClassifier(pretrained=True)

model = load_model()


# ===============================
#   이미지 업로드
# ===============================
uploaded_file = st.file_uploader("📤 텍스트가 포함된 이미지를 업로드하세요",
                                 type=["png", "jpg", "jpeg", "bmp"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="업로드된 이미지", use_column_width=True)

    img_np = np.array(image)

    # ===============================
    #   텍스트 영역 자동 추출(OpenCV)
    # ===============================
    def extract_text_region(img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (22, 6))
        dilated = cv2.dilate(thresh, kernel, iterations=2)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        biggest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(biggest)
        return img[y:y+h, x:x+w]

    text_region = extract_text_region(img_np)

    if text_region is None:
        st.warning("⚠️ 텍스트 영역을 자동으로 추출할 수 없습니다. 더 선명한 이미지로 시도해 주세요.")
    else:
        st.image(text_region, caption="감지된 텍스트 영역", use_column_width=True)


    # ===============================
    #   버튼 → 폰트 분석 실행
    # ===============================
    if st.button("🔎 비슷한 폰트 찾기"):
        with st.spinner("AI가 이미지를 분석하고 있습니다…"):

            # PIL 형태로 변환
            text_region_pil = Image.fromarray(text_region)

            # font-classify 모델 호출
            results = model.predict_topk(text_region_pil, k=8)
            # 결과 형식 예: [("Roboto", 0.82), ("Noto Sans", 0.74), ...]

        st.success("🎉 비슷한 폰트를 찾았습니다!")

        # ===============================
        #   결과 출력
        # ===============================
        for font, score in results:
            st.markdown(f"""
                <div class="font-card">
                    <div class="font-name">{font}</div>
                    <div style="color:#888;">유사도: {score*100:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
