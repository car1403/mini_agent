import httpx

from app.core.config import settings


def embed(text: str) -> list[float]:
    response = httpx.post(
        f"{settings.ollama_base_url}/api/embed",
        json={"model": settings.ollama_embedding_model, "input": text},
        timeout=settings.request_timeout_seconds,
    )
    response.raise_for_status()
    return response.json()["embeddings"][0]
