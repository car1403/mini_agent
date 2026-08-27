import os

import httpx
import streamlit as st


BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")


def get(path: str) -> dict:
    response = httpx.get(f"{BASE_URL}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def post(path: str, payload: dict) -> dict:
    response = httpx.post(f"{BASE_URL}{path}", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


st.set_page_config(page_title="Mini Agent 03 MCP", page_icon="🔌", layout="wide")
st.title("Mini Agent 03 · MCP")
st.caption(
    "FastAPI가 Streamable HTTP와 stdio MCP Server의 Tool을 발견하고 "
    "순차 Agent Loop로 호출합니다."
)

try:
    status = get("/api/mcp/status")
    st.success(f"MCP 연결: {status['status']} · Tool {status['tool_count']}개")
    for server in status["servers"]:
        st.write(
            f"- `{server['name']}` · {server['transport']} · "
            f"{server['endpoint']}"
        )
except httpx.HTTPError:
    st.warning(
        "MCP Server에 연결할 수 없습니다. Travel 서버가 8010 포트에서 "
        "실행 중인지 확인하세요."
    )

if st.button("MCP Tool 발견"):
    try:
        st.json(get("/api/mcp/tools"))
    except httpx.HTTPError as error:
        st.error(f"Backend 호출 실패: {error}")

question = st.text_input(
    "질문",
    "부산 날씨와 15만원 이하 호텔을 찾고, 검색된 호텔의 정책도 알려 주세요.",
)
if st.button("MCP Agent 실행", type="primary"):
    try:
        result = post("/api/mcp/run", {"question": question})
        st.success(result["answer"])
        left, right = st.columns(2)
        left.metric("GPT 호출 횟수", result["llm_calls"])
        right.metric("실행된 Tool 수", len(result["trace"]))
        st.subheader("GPT가 선택하고 MCP가 실행한 Tool")
        for index, item in enumerate(result["trace"], start=1):
            title = (
                f"Round {item['round']} · {item['server']} · "
                f"{item['tool']}"
            )
            with st.expander(title, expanded=True):
                st.caption(f"Public Tool: {item['public_tool']}")
                st.write("Arguments")
                st.json(item["arguments"])
                st.write("Tool Result")
                st.code(item["result"])
                if item["is_error"]:
                    st.error("MCP Tool 실행 오류")
        with st.expander("전체 응답 JSON"):
            st.json(result)
    except httpx.HTTPError as error:
        st.error(f"Backend 호출 실패: {error}")

with st.expander("MCP Resource 확인"):
    if st.button("수하물 정책 읽기"):
        try:
            st.json(get("/api/mcp/baggage-policy"))
        except httpx.HTTPError as error:
            st.error(f"Backend 호출 실패: {error}")
