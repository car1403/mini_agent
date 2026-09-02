import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Mini Agent 06 · Single Agent Service", page_icon="🤖", layout="wide")
st.title("Mini Agent 06 · Single Agent Service")
st.caption("여러 Agent를 제공하지만 Agent끼리 연결하지 않습니다. 사용자가 실행할 Single Agent를 직접 선택합니다.")

try:
    agents_response = requests.get(f"{API_BASE_URL}/api/agents", timeout=5)
    agents_response.raise_for_status()
    agents = agents_response.json()
except requests.RequestException as error:
    st.error(f"Backend 연결 실패: {error}")
    st.stop()

try:
    mcp_response = requests.get(f"{API_BASE_URL}/api/agents/mcp-status", timeout=5)
    mcp_response.raise_for_status()
    mcp = mcp_response.json()
except requests.RequestException:
    st.warning("MCP Tool Server에 연결할 수 없습니다. 8010 포트의 Server를 먼저 실행하세요.")
else:
    st.success(f"MCP 연결: {mcp['status']} · Tool {mcp['tool_count']}개")

labels = {agent["agent_id"]: f"{agent['name']} · {agent['goal']}" for agent in agents}
agent_id = st.selectbox("실행할 Single Agent", options=list(labels), format_func=labels.get)
selected = next(agent for agent in agents if agent["agent_id"] == agent_id)

with st.expander("선택한 Agent의 경계", expanded=True):
    st.markdown(f"**Goal**  \n{selected['goal']}")
    st.markdown(f"**설명**  \n{selected['description']}")
    st.markdown("**허용된 Tool**")
    st.code("\n".join(selected["allowed_tools"]), language="text")

question_key = f"question_{agent_id}"
if question_key not in st.session_state:
    st.session_state[question_key] = selected["example_question"]
question = st.text_area("질문", key=question_key, height=100)

if st.button("선택한 Single Agent 실행", type="primary", use_container_width=True):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/agents/run",
            json={"agent_id": agent_id, "question": question},
            timeout=90,
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as error:
        st.error(f"Agent 실행 실패: {error}")
    else:
        if result["status"] == "completed":
            st.success(result.get("answer") or "답변이 없습니다.")
        else:
            st.error(f"실행 종료: {result['termination_reason']}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Agent", result["agent_name"])
        col2.metric("종료 이유", result["termination_reason"])
        col3.metric("LLM 호출", result["llm_calls"])
        col4.metric("MCP Tool 호출", result["tool_calls"])
        st.subheader("Single Agent Trace")
        for index, item in enumerate(result["trace"], start=1):
            with st.expander(f"{index}. {item.get('owner', 'system')} · {item.get('stage', 'unknown')}", expanded=True):
                st.json(item)

st.divider()
st.info("현재 Agent 간 메시지, 자동 위임, Coordinator와 공유 State는 없습니다. 다음 Multi-Agent 과정에서 이 경계를 연결합니다.")
