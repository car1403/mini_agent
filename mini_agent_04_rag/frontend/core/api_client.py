"""모든 Agent 메뉴에서 공통으로 사용하는 HTTP 요청 기능."""

import os
from typing import Any

import httpx


BACKEND_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))


class BackendAPIError(Exception):
    """Backend 연결 또는 API 응답 처리 중 발생한 오류입니다."""


def _check(response: httpx.Response) -> httpx.Response:
    if response.is_error:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text or "알 수 없는 오류"
        raise BackendAPIError(f"요청에 실패했습니다 ({response.status_code}): {detail}")
    return response


def request(
    method: str,
    path: str,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    try:
        response = _check(httpx.request(
            method, f"{BACKEND_URL}{path}", json=json, params=params, headers=headers,
            timeout=REQUEST_TIMEOUT,
        ))
        return response.json()
    except httpx.TimeoutException as error:
        raise BackendAPIError("백엔드 응답 시간이 초과되었습니다.") from error
    except httpx.RequestError as error:
        raise BackendAPIError("백엔드 서버에 연결할 수 없습니다. 서버 실행 상태를 확인해 주세요.") from error
    except ValueError as error:
        raise BackendAPIError("백엔드가 올바른 JSON을 반환하지 않았습니다.") from error


def upload(path: str, files: dict[str, Any], data: dict[str, Any]) -> Any:
    try:
        return _check(httpx.post(f"{BACKEND_URL}{path}", files=files, data=data, timeout=REQUEST_TIMEOUT)).json()
    except httpx.TimeoutException as error:
        raise BackendAPIError("파일 업로드 응답 시간이 초과되었습니다.") from error
    except httpx.RequestError as error:
        raise BackendAPIError("파일 업로드 중 Backend에 연결할 수 없습니다.") from error
    except ValueError as error:
        raise BackendAPIError("파일 업로드 응답이 올바른 JSON이 아닙니다.") from error


def request_bytes(path: str, json: dict[str, Any]) -> bytes:
    try:
        return _check(httpx.post(f"{BACKEND_URL}{path}", json=json, timeout=REQUEST_TIMEOUT)).content
    except httpx.RequestError as error:
        raise BackendAPIError("음성 생성 중 Backend에 연결할 수 없습니다.") from error
