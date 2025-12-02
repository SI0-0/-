import streamlit as st
from PIL import Image
import torch
import cv2
import numpy as np
import os

st.set_page_config(
    page_title="AI 폰트 찾기",
    layout="centered",
    page_icon="🔍"
)

# ===============================
#  Custom Korean UI Styling
# ===============================
st.markdown("""
<style>
    .title {
        font-size: 2.3rem;
        font-weight: 700;
        text-align: center;
        color: #222;
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
#  Header
# ===============================
st.markdown('<div class="title">🔍 AI 폰트 찾기</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">이미지를 업로드하면 AI가 비슷한 폰트를 순서대로 찾아드립니다.</div>',
    unsafe_allow_html=True
)


# ===============================
#  모델 로드
# ===============================
MODEL_PATH = "models/font_similarity_vgg.pth"

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        st.error("❌ 모델 파일을 찾을 수 없습니다.\nmodels 폴더에 font_similarity_vgg.pth 를 넣어주세요.")
        return None

    model = torch.load(MODEL_PATH, map_location="cpu")
    model.eval()
    return model

model = load_model()


# ===============================
#  이미지 업로드
# ===============================
uploaded_file = st.file_uploader("📤 텍스트가 포함된 이미지를 업로드하세요", 
                                 type=["png", "jpg", "jpeg", "bmp"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="업로드된 이미지", use_column_width=True)

    img_np = np.array(image)

    # ===============================
    #  텍스트 영역 추출
    # ===============================
    def extract_text_region(img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5))
        dilated = cv2.dilate(thresh, kernel, iterations=2)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        biggest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(biggest)
        return img[y:y+h, x:x+w]

    text_region = extract_text_region(img_np)

    if text_region is None:
        st.warning("⚠️ 텍스트 영역을 자동으로 찾아낼 수 없습니다.\n더 선명한 이미지를 시도해 주세요.")
    else:
        st.image(text_region, caption="감지된 텍스트 영역", use_column_width=True)


    # ===============================
    #  폰트 찾기 버튼
    # ===============================
    if st.button("🔎 비슷한 폰트 찾기"):
        if model is None:
            st.stop()

        with st.spinner("AI가 이미지 속 폰트를 분석하는 중입니다…"):

            resized = cv2.resize(text_region, (224, 224))
            img_tensor = torch.tensor(resized).permute(2, 0, 1).float().unsqueeze(0) / 255.

            with torch.no_grad():
                output = model(img_tensor)
                probs = torch.softmax(output, dim=1)[0]

            # Top 8 폰트 후보
            topk = 8
            top_probs, indices = torch.topk(probs, topk)

            font_list = []
            for score, idx in zip(top_probs.tolist(), indices.tolist()):
                font_name = f"Font_{idx}"  # (※ 실제 font-classify는 label→font map 필요)
                font_list.append((font_name, score))

        st.success("🎉 AI가 비슷한 폰트를 찾았습니다!")

        # ===============================
        #  출력
        # ===============================
        for font, score in font_list:
            st.markdown(f"""
                <div class="font-card">
                    <div class="font-name">{font}</div>
                    <div style="font-size:0.9rem; color:#888;">
                        유사도: {score*100:.1f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)
