import streamlit as st

from core.api_client import BackendAPIError, request_audio


st.title("1-6. 음성 생성")
st.caption("여행 안내문을 MP3 합성 음성으로 변환합니다.")

analysis = st.session_state.get("image_analysis", {})
default_text = analysis.get("summary", "부산 여행 안내를 시작합니다.")
text = st.text_area("음성으로 변환할 안내문", default_text, max_chars=2000)
voice = st.selectbox("음성", ["coral", "marin", "cedar", "alloy", "nova"])
instructions = st.text_input("말하기 방식", "한국어로 또렷하고 따뜻한 여행 가이드처럼 말하세요.")

if st.button("음성 생성", type="primary", disabled=not text.strip()):
    try:
        with st.spinner("합성 음성을 생성하고 있습니다."):
            audio = request_audio(text, voice, instructions)
        st.warning("아래 음성은 AI가 생성한 합성 음성입니다.")
        st.audio(audio, format="audio/mpeg")
    except BackendAPIError as error:
        st.error(str(error))

st.info("이 과정에서는 임의 인물의 음성을 복제하지 않습니다.")
