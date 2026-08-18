import streamlit as st


st.title("6-1. 일반 Python Workflow")
st.caption("LangGraph를 사용하기 전에 함수와 if문으로 실행 순서를 확인합니다.")

message = st.selectbox("여행 요청", ["부산 여행을 준비해줘", "여행을 준비해줘"])


def run_python_workflow(user_message: str) -> dict:
    trace = ["extract"]
    destination = "부산" if "부산" in user_message else None
    if destination is None:
        return {
            "status": "needs_input",
            "answer": "어느 도시로 여행할까요?",
            "trace": [*trace, "ask_user"],
        }
    return {
        "status": "completed",
        "answer": f"{destination} Mock 일정을 만들었습니다.",
        "trace": [*trace, "create_plan"],
    }


if st.button("일반 Python 실행", type="primary"):
    result = run_python_workflow(message)
    st.json(result)
    st.code(" → ".join(result["trace"]), language="text")

st.info("다음 화면부터 같은 실행 흐름을 State, Node, Edge로 옮깁니다.")
