import streamlit as st


st.title("5-3. 사용자별 대화 분리")
st.caption("같은 Memory 저장소에서도 user_id별로 데이터를 분리합니다.")

memories = {
    "user-a": ["창가 좌석 선호", "채식 식사"],
    "user-b": ["조용한 객실 선호"],
}
user_id = st.selectbox("사용자", list(memories))
st.json({"user_id": user_id, "memories": memories[user_id]})
st.warning("클라이언트가 보낸 user_id만 신뢰하지 말고 실제 서비스에서는 로그인 정보로 확인합니다.")
