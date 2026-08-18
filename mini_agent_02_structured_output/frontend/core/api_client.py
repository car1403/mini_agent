"""모든 Agent 메뉴에서 공통으로 사용하는 HTTP 요청 기능."""

import os
from typing import Any

import httpx


BACKEND_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = 70.0


class BackendAPIError(Exception):
    """Backend 연결 또는 API 응답 처리 중 발생한 오류입니다."""


def request(method: str, path: str, json: dict[str, Any] | None = None) -> Any:
    try:
        response = httpx.request(method, f"{BACKEND_URL}{path}", json=json, timeout=REQUEST_TIMEOUT)
    except httpx.TimeoutException as error:
        raise BackendAPIError("백엔드 응답 시간이 초과되었습니다.") from error
    except httpx.RequestError as error:
        raise BackendAPIError("백엔드 서버에 연결할 수 없습니다. 서버 실행 상태를 확인해 주세요.") from error
    if response.is_error:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text or "알 수 없는 오류"
        raise BackendAPIError(f"요청에 실패했습니다 ({response.status_code}): {detail}")
    try:
        return response.json()
    except ValueError as error:
        raise BackendAPIError("백엔드가 올바른 JSON을 반환하지 않았습니다.") from error


def upload_image(filename: str, content: bytes, content_type: str, question: str) -> Any:
    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/media/image-analysis",
            files={"image": (filename, content, content_type)},
            data={"question": question},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as error:
        try:
            detail = error.response.json().get("detail", str(error))
        except ValueError:
            detail = str(error)
        raise BackendAPIError(detail) from error
    except httpx.RequestError as error:
        raise BackendAPIError("백엔드 서버에 연결할 수 없습니다.") from error


def request_audio(text: str, voice: str, instructions: str) -> bytes:
    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/media/tts",
            json={"text": text, "voice": voice, "instructions": instructions},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.content
    except httpx.HTTPStatusError as error:
        try:
            detail = error.response.json().get("detail", str(error))
        except ValueError:
            detail = str(error)
        raise BackendAPIError(detail) from error
    except httpx.RequestError as error:
        raise BackendAPIError("백엔드 서버에 연결할 수 없습니다.") from error
