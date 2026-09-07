import httpx
from mcp_server.core.config import env

OLLAMA_BASE_URL = env("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL = env("OLLAMA_EMBEDDING_MODEL", "embeddinggemma")
DIMENSIONS = int(env("EMBEDDING_DIMENSIONS", "768"))

async def embed(texts: list[str]) -> list[list[float]]:
    if DIMENSIONS != 768:
        raise ValueError("현재 SQL은 embeddinggemma의 768차원으로 구성되어 있습니다.")
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={"model": MODEL, "input": texts},
        )
        response.raise_for_status()
    vectors = response.json().get("embeddings", [])
    if len(vectors) != len(texts):
        raise ValueError("Ollama가 입력 개수와 다른 임베딩 결과를 반환했습니다.")
    if any(len(v)!=DIMENSIONS for v in vectors):
        raise ValueError("임베딩 차원이 일치하지 않습니다.")
    return vectors

def vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(v) for v in vector) + "]"
