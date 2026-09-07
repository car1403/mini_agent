import streamlit as st

from core.ui import backend_request, run_api, show_json


st.title("📚 RAG와 Memory")

st.subheader("정책 문서 검색")
question = st.text_input("정책 질문", "숙소를 당일 취소하면 환불되나요?")
if st.button("정책 검색"):
    data = run_api(
        lambda: backend_request(
            "POST", "/api/knowledge/search", {"query": question, "limit": 3}
        )
    )
    if data:
        st.dataframe(data["documents"], use_container_width=True)
        show_json(data)

st.divider()
st.subheader("사용자별 장기 Memory")
user_id = st.text_input("사용자 ID", "demo-user")
key = st.selectbox(
    "기억 항목",
    ["transportation", "food_restriction", "hotel_preference"],
)
value = st.text_input("값", "대중교통")

save, load = st.columns(2)
if save.button("Memory 저장"):
    data = run_api(
        lambda: backend_request(
            "POST",
            f"/api/users/{user_id}/memories",
            {"key": key, "value": value},
        )
    )
    if data:
        st.success("저장했습니다.")

if load.button("Memory 조회"):
    data = run_api(
        lambda: backend_request("GET", f"/api/users/{user_id}/memories")
    )
    if data is not None:
        st.dataframe(data, use_container_width=True)
