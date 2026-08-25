import streamlit as st

from clients.agent_client import compare_tools, get_tools, select_tool
from core.api_client import BackendAPIError


st.title("🧭 Tool 선택")
st.caption("LLM은 Tool Call을 제안할 뿐, 이 화면에서는 아직 함수를 실행하지 않습니다.")

try:
    registry = get_tools()
    with st.expander("허용된 조회 Tool과 입력 Schema"):
        st.json(registry)
except BackendAPIError as error:
    st.error(str(error))

provider = st.selectbox("선택 Provider", ["mock", "gemini", "openai", "ollama"])
message = st.selectbox("요청", ["부산 날씨를 알려줘.", "부산 숙소를 찾아줘.", "제주 관광지를 추천해 줘.", "여행 준비를 도와줘."])

if st.button("Tool Call 제안 받기"):
    try:
        decision = select_tool(provider, message)
        st.session_state["tool_decision"] = decision
        st.json(decision)
        st.info("아직 Tool 함수는 실행되지 않았습니다. 다음 메뉴에서 arguments를 확인하고 실행합니다.")
    except BackendAPIError as error:
        st.error(str(error))

st.divider()
providers = st.multiselect("선택 결과 비교", ["mock", "gemini", "openai", "ollama"], default=["mock"])
if st.button("Provider별 Tool 선택 비교", disabled=not providers):
    try:
        st.json(compare_tools(providers, message))
    except BackendAPIError as error:
        st.error(str(error))
