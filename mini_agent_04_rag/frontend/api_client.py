"""Streamlit 화면에서 RAG Backend를 호출하는 간단한 함수입니다."""

import os

import httpx


BACKEND_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")


def request(method: str, path: str, **kwargs) -> dict:
    try:
        response = httpx.request(
            method,
            f"{BACKEND_URL}{path}",
            timeout=120,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as error:
        raise RuntimeError(f"Backend 요청 실패: {error}") from error


def make_chunks(text: str, sentences_per_chunk: int) -> dict:
    return request("POST", "/api/rag/chunks", json={
        "text": text,
        "sentences_per_chunk": sentences_per_chunk,
    })


def index_documents() -> dict:
    return request("POST", "/api/rag/index")


def search_documents(
    question: str,
    mode: str,
    top_k: int,
    score_threshold: float | None = None,
    metadata_filter: dict | None = None,
) -> dict:
    return request("POST", "/api/rag/search", json={
        "question": question,
        "mode": mode,
        "top_k": top_k,
        "score_threshold": score_threshold,
        "metadata_filter": metadata_filter or {},
    })


def answer_question(
    question: str,
    mode: str,
    top_k: int,
    use_ollama: bool,
    use_cache: bool,
) -> dict:
    return request("POST", "/api/rag/answer", json={
        "question": question,
        "mode": mode,
        "top_k": top_k,
        "use_ollama": use_ollama,
        "use_cache": use_cache,
    })


def upload_pdf(filename: str, content: bytes) -> dict:
    return request(
        "POST",
        "/api/rag/pdf",
        files={"pdf": (filename, content, "application/pdf")},
    )


def get_status() -> dict:
    return request("GET", "/api/rag/status")
