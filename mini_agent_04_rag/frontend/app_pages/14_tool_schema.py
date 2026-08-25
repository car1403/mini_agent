import streamlit as st


st.title("3-1. Tool Schema")
st.caption("Tool 이름, 설명, 입력값을 계약서처럼 정의합니다.")

tool_schema = {
    "name": "search_weather",
    "description": "도시의 날씨를 조회합니다.",
    "parameters": {
        "city": {"type": "string", "required": True},
        "days": {"type": "integer", "minimum": 1, "maximum": 7},
    },
}
st.json(tool_schema)
st.info("LLM은 Tool을 제안하지만, 실제 입력 검증과 실행 권한은 Python 코드가 담당합니다.")
