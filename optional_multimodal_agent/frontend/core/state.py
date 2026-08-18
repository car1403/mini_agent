import streamlit as st

from core.config import API_URLS, PROVIDERS


def init_state() -> None:
    st.session_state.setdefault("selected_backend", "Python Agent")
    st.session_state.setdefault("selected_provider_label", "GPT")
    st.session_state.setdefault("agent_run", None)
    st.session_state.setdefault("agent_run_backend", None)
    st.session_state.setdefault("agent_run_provider", None)


def selected_backend() -> tuple[str, str]:
    init_state()
    name = st.session_state.selected_backend
    return name, API_URLS[name]


def selected_provider() -> tuple[str, str]:
    init_state()
    label = st.session_state.selected_provider_label
    return label, PROVIDERS[label]


def save_agent_run(run: dict | None) -> None:
    name, _ = selected_backend()
    _, provider = selected_provider()
    st.session_state.agent_run = run
    st.session_state.agent_run_backend = name if run else None
    st.session_state.agent_run_provider = provider if run else None


def current_agent_run() -> dict | None:
    name, _ = selected_backend()
    _, provider = selected_provider()
    if st.session_state.get("agent_run_backend") != name:
        return None
    if st.session_state.get("agent_run_provider") != provider:
        return None
    return st.session_state.get("agent_run")
