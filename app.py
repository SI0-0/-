import streamlit as st
from PIL import Image
import numpy as np
from font_classifier import LocalFontClassifier
from utils import extract_text_region

st.set_page_config(page_title="AI 폰트 찾기", page_icon="🔍", layout="centered")

st.markdown("""
<style>
.title { font-size:2.4rem; font-weight:700; text-align:center; margin-bottom:0.3rem; }
.subtitle { text-align:center; font-size:1.1rem; color:#666; margin-bottom:2rem; }
.font-card { padding:1rem; border-radius:14px; background:#fafafa; margin-bottom:0.7rem; border:1px solid #e3e3e3; }
.font-name { font-size:1.15rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🔍 AI 폰트 찾기</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">이미지에서 텍스트를 추출하여 AI가 가장 비슷한 폰트를 추천합니다.</div>', unsafe_allow_html=True)

@st.cache_resource
def load_model():
    return LocalFontClassifier(model_path="model/font_classifier.pth",
                               label_path="model/label_map.json")

model = load_model()

uploaded_file = st.file_uploader("📤 텍스트가 포함된 이미지를 업로드하세요.", type=["png","jpg","jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="업로드된 이미지", use_column_width=True)
    img_np = np.array(image)
    text_region = extract_text_region(img_np)
    if text_region is None:
        st.warning("⚠ 텍스트 영역을 찾지 못했습니다. 더 명확한 이미지를 사용하세요.")
    else:
        st.image(text_region, caption="감지된 텍스트 영역", use_column_width=True)
        if st.button("🔎 비슷한 폰트 분석하기"):
            with st.spinner("AI가 이미지를 분석 중입니다..."):
                result = model.predict(text_region, top_k=8)
            st.success("🎉 분석 완료! 후보 폰트:")
            for font, score in result:
                st.markdown(f"""
                    <div class="font-card">
                        <div class="font-name">{font}</div>
                        <div style="color:#888;">유사도: {score*100:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
