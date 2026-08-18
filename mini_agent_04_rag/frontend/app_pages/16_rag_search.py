import streamlit as st

from clients.agent_client import search_rag
from core.api_client import BackendAPIError


st.title("3️⃣ 문서 검색")
st.caption("먼저 Docker가 필요 없는 키워드 검색으로 점수와 top_k를 관찰합니다.")

questions = {
    "키워드 일치 · 호텔": "호텔 당일 취소 환불",
    "키워드 일치 · 수하물": "위탁 수하물 15kg",
    "키워드 일치 · 관광지": "바다 박물관 화요일 휴관",
    "표현이 다른 질문": "비행기에 짐을 몇 kg까지 실을 수 있나요?",
    "근거 없는 질문": "여권을 잃어버리면 어떻게 하나요?",
}
question_type = st.selectbox("질문 유형", list(questions))
query = questions[question_type]
st.code(query, language="text")
mode = st.radio("검색 방식", ["keyword", "pgvector"], horizontal=True)
top_k = st.slider("top_k", 1, 5, 3)

if mode == "pgvector":
    st.warning("pgvector 검색 전에는 마지막 메뉴에서 문서 색인을 먼저 실행하세요.")

if st.button("관련 문서 찾기", type="primary"):
    try:
        result = search_rag(query, mode, top_k)
        if not result["results"]:
            st.warning("관련 문서를 찾지 못했습니다.")
        for index, item in enumerate(result["results"], start=1):
            st.subheader(f"{index}위 · score {item['score']:.3f}")
            st.write(item["content"])
            st.caption(f"출처: {item['source']} · chunk {item['chunk_index']}")
    except BackendAPIError as error:
        st.error(str(error))
