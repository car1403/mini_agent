import streamlit as st

def current(agent):
    return st.session_state.setdefault(f"run_{agent}",{"run_id":None,"last_id":"0-0","events":[]})

def select_run(agent, run_id):
    state = {"run_id":run_id,"last_id":"0-0","events":[]}
    st.session_state[f"run_{agent}"] = state
    # 새로고침으로 session_state가 없어져도 실행 ID를 복원합니다.
    st.query_params[agent] = run_id
    return state
