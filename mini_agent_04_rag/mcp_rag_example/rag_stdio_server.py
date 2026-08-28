"""pgvector 검색 기능 하나를 제공하는 stdio MCP Server입니다."""

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.simple_service import search_documents  # noqa: E402


mcp = FastMCP(
    "mini-agent-rag",
    instructions="여행 정책 문서를 pgvector에서 의미 검색합니다.",
)


@mcp.tool()
def search_knowledge_base(question: str, top_k: int = 3) -> dict:
    """여행·호텔 정책 질문과 관련된 문서를 의미 검색합니다."""
    safe_top_k = max(1, min(top_k, 5))
    results = search_documents(
        question=question,
        mode="pgvector",
        top_k=safe_top_k,
    )
    return {
        "question": question,
        "results": [item.model_dump(mode="json") for item in results],
    }


if __name__ == "__main__":
    # stdio의 stdout은 MCP 메시지 전용이므로 print를 사용하지 않습니다.
    mcp.run(transport="stdio")
