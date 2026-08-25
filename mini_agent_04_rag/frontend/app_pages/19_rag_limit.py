import streamlit as st


st.title("4-4. 검색 결과 제한")
st.caption("관련도가 낮은 문서까지 답변에 넣지 않도록 개수와 점수를 제한합니다.")

documents = [
    {"title": "부산 교통", "score": 0.92},
    {"title": "부산 숙소", "score": 0.81},
    {"title": "제주 맛집", "score": 0.43},
    {"title": "서울 전시", "score": 0.21},
]
top_k = st.slider("가져올 문서 수", 1, 4, 2)
minimum_score = st.slider("최소 관련도", 0.0, 1.0, 0.7, 0.05)
selected = [doc for doc in documents if doc["score"] >= minimum_score][:top_k]
st.dataframe(selected, use_container_width=True)
st.info("검색 결과가 없으면 근거 없이 답하지 말고 정보가 부족하다고 알려야 합니다.")
