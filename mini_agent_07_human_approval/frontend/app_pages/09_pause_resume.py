import streamlit as st


st.title("7-3. 중단·저장·재개")
st.caption("실행을 멈추고 현재 상태를 저장한 뒤 같은 실행을 이어갑니다.")

if "approval_demo" not in st.session_state:
    st.session_state.approval_demo = {"status": "started", "current_node": "prepare"}

left, right = st.columns(2)
if left.button("중단하고 저장"):
    st.session_state.approval_demo = {
        "status": "waiting_approval",
        "current_node": "approval",
        "thread_id": "demo-thread-001",
    }
if right.button("승인 값으로 재개"):
    state = st.session_state.approval_demo
    if state.get("status") != "waiting_approval":
        st.error("승인 대기 중인 실행만 재개할 수 있습니다.")
    else:
        st.session_state.approval_demo = {
            **state,
            "status": "completed",
            "current_node": "end",
            "decision": "approve",
        }

st.json(st.session_state.approval_demo)
