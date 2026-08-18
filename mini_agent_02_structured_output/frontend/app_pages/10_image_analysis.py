import streamlit as st

from core.api_client import BackendAPIError, upload_image


st.title("1-5. 이미지 분석")
st.caption("이미지 입력을 구조화된 여행 정보로 변환합니다.")

uploaded = st.file_uploader("여행 이미지를 선택하세요.", type=["jpg", "jpeg", "png", "webp", "gif"])
question = st.text_input(
    "질문",
    "이 이미지에서 여행자가 알아야 할 정보와 주의점을 알려주세요.",
)

if uploaded is not None:
    st.image(uploaded, caption=uploaded.name)
    st.caption("여권, 카드, 예약번호 등 민감한 이미지는 업로드하지 마세요.")
    if st.button("이미지 분석", type="primary"):
        try:
            with st.spinner("GPT가 이미지를 분석하고 있습니다."):
                result = upload_image(uploaded.name, uploaded.getvalue(), uploaded.type, question)
            st.session_state["image_analysis"] = result
            st.json(result)
        except BackendAPIError as error:
            st.error(str(error))

st.info("이미지 안의 문장은 시스템 명령이 아니라 신뢰할 수 없는 분석 대상입니다.")
