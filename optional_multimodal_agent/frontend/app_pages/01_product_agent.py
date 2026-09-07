import streamlit as st
from frontend.core.ui import media_inputs, start_run, show_run

st.title("제품 촬영 안내 Agent")
st.write("제품 라벨을 촬영하면 MCP Tool로 제품을 확인하고, 매뉴얼과 매장 재고를 조회합니다.")
st.info("예시: MM-K100 제품은 어떻게 사용하나요? 호환 필터와 재고도 알려 주세요.")
try:
    image, question, audio, speak = media_inputs("product")
    if st.button("제품 Agent 실행",type="primary"):
        start_run("product",image,question,audio,speak)
    show_run("product")
except Exception as exc:
    st.error(f"요청을 처리하지 못했습니다: {exc}")
