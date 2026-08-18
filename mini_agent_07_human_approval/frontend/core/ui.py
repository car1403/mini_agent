from collections.abc import Callable
from typing import Any

import streamlit as st

from core.api_client import ApiClientError, request
from core.config import API_URLS
from core.state import init_state, selected_backend


def run_api(call: Callable[[], Any]) -> Any | None:
    try:
        with st.spinner("처리 중입니다..."):
            return call()
    except ApiClientError as error:
        st.error(str(error))
        return None


def show_json(data: Any) -> None:
    with st.expander("원본 JSON"):
        st.json(data)


def render_backend_selector() -> tuple[str, str]:
    init_state()
    name = st.radio(
        "Backend 선택",
        ["Python Agent", "LangGraph Agent"],
        key="selected_backend",
    )
    url = API_URLS[name]
    st.caption(f"연결 주소: {url}")
    return name, url


def backend_request(method: str, path: str, payload: dict | None = None) -> Any:
    _, url = selected_backend()
    return request(method, path, payload, base_url=url)
