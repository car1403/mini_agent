from typing import Any

import httpx

from core.config import PYTHON_AGENT_API_URL


class ApiClientError(RuntimeError):
    pass


def upload_image(
    path: str,
    filename: str,
    content: bytes,
    content_type: str,
    question: str,
    base_url: str,
) -> Any:
    try:
        response = httpx.post(
            f"{base_url.rstrip('/')}{path}",
            files={"image": (filename, content, content_type)},
            data={"question": question},
            timeout=60,
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
        raise ApiClientError(f"Backend 연결에 실패했습니다: {error}") from error


def upload_multimodal_agent_run(
    filename: str,
    content: bytes,
    content_type: str,
    user_id: str,
    message: str,
    provider: str,
    base_url: str,
) -> Any:
    try:
        response = httpx.post(
            f"{base_url.rstrip('/')}/api/media/agent-runs",
            files={"image": (filename, content, content_type)},
            data={
                "user_id": user_id,
                "message": message,
                "provider": provider,
            },
            timeout=90,
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
        raise ApiClientError(f"Backend 연결에 실패했습니다: {error}") from error


def request_audio(path: str, payload: dict, base_url: str) -> bytes:
    try:
        response = httpx.post(
            f"{base_url.rstrip('/')}{path}",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.content
    except httpx.HTTPStatusError as error:
        try:
            message = error.response.json().get("detail", str(error))
        except ValueError:
            message = str(error)
        raise ApiClientError(message) from error
    except httpx.RequestError as error:
        raise ApiClientError(f"Backend 연결에 실패했습니다: {error}") from error


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
