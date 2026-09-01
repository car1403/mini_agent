import streamlit as st

from core.api_client import BackendAPIError, request


st.title("5-8. PostgreSQL HTTP MCP")
st.caption(
    "FastAPI가 8012번 Streamable HTTP MCP Server를 통해 PostgreSQL Memory를 관리합니다."
)

try:
    status = request("GET", "/api/mcp/status")
    st.success(
        f"MCP 연결: {status['status']} · {status['transport']} · "
        f"{status['storage']} · Tool {status['tool_count']}개"
    )
    st.code(status["endpoint"])
except BackendAPIError as error:
    st.warning(str(error))
    st.info("PostgreSQL과 `python .\\mcp_server\\memory_server.py` 실행 상태를 확인하세요.")

if st.button("MCP Tool 발견"):
    try:
        st.json(request("GET", "/api/mcp/tools"))
    except BackendAPIError as error:
        st.error(str(error))

st.divider()
st.subheader("PostgreSQL Memory 저장")
key = st.selectbox("Memory key", ["transportation", "food_restriction", "hotel_preference"])
value = st.text_input("Memory value", "대중교통")
if st.button("MCP로 저장", type="primary"):
    try:
        st.json(request("POST", "/api/mcp/memories", json={"key": key, "value": value}))
    except BackendAPIError as error:
        st.error(str(error))

left, right = st.columns(2)
with left:
    if st.button("MCP로 전체 조회"):
        try:
            st.json(request("GET", "/api/mcp/memories"))
        except BackendAPIError as error:
            st.error(str(error))
with right:
    if st.button("MCP로 내보내기"):
        try:
            st.json(request("GET", "/api/mcp/export"))
        except BackendAPIError as error:
            st.error(str(error))

st.divider()
question = st.text_input("관련 Memory를 찾을 질문", "부산에서 식당을 추천해줘")
if st.button("관련 Memory 선택"):
    try:
        st.json(request("POST", "/api/mcp/relevant", json={"question": question}))
    except BackendAPIError as error:
        st.error(str(error))

with st.expander("Memory ID로 삭제"):
    memory_id = st.text_input("삭제할 Memory ID")
    if st.button("MCP로 삭제"):
        if not memory_id.strip():
            st.warning("Memory ID를 입력하세요.")
        else:
            try:
                st.json(request("DELETE", f"/api/mcp/memories/{memory_id.strip()}"))
            except BackendAPIError as error:
                st.error(str(error))

st.info(
    "Tool에는 user_id 입력란이 없습니다. MCP Server가 MCP_DEMO_USER_ID를 인증 사용자 "
    "범위로 사용합니다."
)
