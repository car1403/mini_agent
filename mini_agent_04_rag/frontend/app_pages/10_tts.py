import streamlit as st

from clients.agent_client import create_tts
from core.api_client import BackendAPIError


st.title("1-6. 음성 생성")
st.caption("여행 안내문을 MP3 합성 음성으로 변환합니다.")

analysis = st.session_state.get("image_analysis", {})
text = st.text_area("음성 안내문", analysis.get("summary", "즐겁고 안전한 여행 되세요."))
voice = st.selectbox("음성", ["coral", "marin", "cedar", "alloy", "nova"])
if st.button("음성 생성", type="primary", disabled=not text.strip()):
    try:
        st.warning("아래 음성은 AI가 생성한 합성 음성입니다.")
        st.audio(create_tts(text, voice, "한국어로 또렷하게 말하세요."), format="audio/mpeg")
    except BackendAPIError as error:
        st.error(str(error))

st.info("이 과정에서는 임의 인물의 음성을 복제하지 않습니다.")
