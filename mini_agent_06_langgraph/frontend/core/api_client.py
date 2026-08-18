from typing import Any

import httpx

from core.config import PYTHON_AGENT_API_URL


class ApiClientError(RuntimeError):
    pass


def request(
    method: str,
    path: str,
    payload: dict | None = None,
    base_url: str | None = None,
) -> Any:
    selected_base_url = (base_url or PYTHON_AGENT_API_URL).rstrip("/")
    try:
        response = httpx.request(
            method,
            f"{selected_base_url}{path}",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()
        return body.get("data", body)
    except httpx.HTTPStatusError as error:
        try:
            message = error.response.json().get("detail", str(error))
        except ValueError:
            message = str(error)
        raise ApiClientError(message) from error
    except httpx.RequestError as error:
        raise ApiClientError(f"Backend에 연결할 수 없습니다: {error}") from error
