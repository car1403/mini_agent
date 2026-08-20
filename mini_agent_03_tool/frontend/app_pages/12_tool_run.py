import json
from datetime import date, timedelta

import streamlit as st

from clients.agent_client import run_tool
from core.api_client import BackendAPIError


st.title("🛡️ Tool 검증과 실행")
st.caption("Backend가 Allowlist와 Pydantic Schema를 통과한 조회 함수만 실행합니다.")

decision = st.session_state.get("tool_decision", {})
allowed = ["get_current_weather", "get_weather_forecast", "search_hotels", "search_attractions"]
default_tool = decision.get("tool_name") if decision.get("tool_name") in allowed else "get_current_weather"
tool_name = st.selectbox("Tool 이름", allowed + ["delete_database (차단 실습)"], index=allowed.index(default_tool))
tool_name = "delete_database" if tool_name.startswith("delete_database") else tool_name

today = date.today()
sample_arguments = {
    "get_current_weather": {"city": "부산"},
    "get_weather_forecast": {"city": "부산", "target_date": (today + timedelta(days=1)).isoformat()},
    "search_hotels": {
        "city": "부산",
        "check_in": today.isoformat(),
        "check_out": (today + timedelta(days=2)).isoformat(),
        "guests": 2,
    },
    "search_attractions": {"city": "제주", "category": "all"},
    "delete_database": {},
}
arguments = decision.get("arguments") if decision.get("tool_name") == tool_name else sample_arguments[tool_name]
raw = st.text_area("arguments JSON", json.dumps(arguments, ensure_ascii=False, indent=2), height=180)

st.warning("실행 버튼을 누르기 전에는 어떤 함수도 실행되지 않습니다.")
if st.button("Backend에서 Tool 실행", type="primary"):
    try:
        result = run_tool(tool_name, json.loads(raw))
        if result["success"]:
            st.success("Tool 실행 성공")
            st.json(result["data"])
        else:
            st.error("Tool 실행 차단 또는 검증 실패")
            st.json(result["error"])
    except json.JSONDecodeError as error:
        st.error(f"JSON 문법 오류: {error}")
    except BackendAPIError as error:
        st.error(str(error))
