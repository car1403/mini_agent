import streamlit as st

from core.config import API_URLS


def init_state() -> None:
    st.session_state.setdefault("selected_backend", "Python Agent")
    st.session_state.setdefault("agent_run", None)
    st.session_state.setdefault("agent_run_backend", None)
    st.session_state.setdefault("evaluation_baseline", None)
    st.session_state.setdefault("provider_results", [])


def selected_backend() -> tuple[str, str]:
    init_state()
    name = st.session_state.selected_backend
    return name, API_URLS[name]


def save_agent_run(run: dict | None) -> None:
    name, _ = selected_backend()
    st.session_state.agent_run = run
    st.session_state.agent_run_backend = name if run else None


def current_agent_run() -> dict | None:
    name, _ = selected_backend()
    if st.session_state.get("agent_run_backend") != name:
        return None
    return st.session_state.get("agent_run")
