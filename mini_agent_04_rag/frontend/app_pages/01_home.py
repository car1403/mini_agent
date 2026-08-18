import streamlit as st


st.title("🏠 Mini Agent 04 · RAG")
st.write("01~04단계 기능을 유지하면서 문서 검색과 근거 기반 답변을 추가합니다.")

st.subheader("이번 단계에서 추가하는 흐름")
st.code("질문 → 검색 → Context → LLM 답변 → 출처", language="text")

st.info("처음에는 keyword + mock으로 실행하세요. 이 경로는 API Key와 Docker가 필요하지 않습니다.")

st.subheader("Docker는 언제 사용하나요?")
st.write(
    "마지막 pgvector 실습에서만 Ollama가 Embedding을 만들고 PostgreSQL이 Vector를 저장·검색합니다. "
    "앞 단계에서 배운 흐름은 그대로이고 검색 구현만 교체됩니다."
)
