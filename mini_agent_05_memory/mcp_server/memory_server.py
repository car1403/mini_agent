"""PostgreSQL Memory를 제공하는 독립 Streamable HTTP MCP Server입니다."""

import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from app.memory.relevance import relevant_memories  # noqa: E402
from app.memory.service import (  # noqa: E402
    delete_memory as delete_from_store,
    list_memories as list_from_store,
    upsert_memory,
)


MCP_HOST = os.getenv("MEMORY_MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MEMORY_MCP_PORT", "8012"))
AUTHENTICATED_USER_ID = os.getenv("MCP_DEMO_USER_ID", "student-01")
STORAGE = "postgres"

mcp = FastMCP(
    "mini-agent-memory-postgres",
    instructions=(
        "PostgreSQL에 저장된 인증 사용자의 Memory만 관리합니다. Tool 인자로 user_id를 "
        "받지 않습니다. 민감정보를 저장하지 말고 답변에는 find_relevant_memories가 "
        "반환한 관련 Memory만 사용하세요."
    ),
    host=MCP_HOST,
    port=MCP_PORT,
    stateless_http=True,
    json_response=True,
)


def serialize(items) -> list[dict]:
    return [item.model_dump() for item in items]


@mcp.tool()
def list_memories() -> dict:
    """인증된 사용자의 PostgreSQL 장기 Memory를 조회합니다."""
    return {
        "user_scope": AUTHENTICATED_USER_ID,
        "storage": STORAGE,
        "items": serialize(list_from_store(STORAGE, AUTHENTICATED_USER_ID)),
    }


@mcp.tool()
def save_memory(key: str, value: str) -> dict:
    """인증된 사용자의 허용된 선호를 PostgreSQL에 저장하거나 수정합니다."""
    item = upsert_memory(STORAGE, AUTHENTICATED_USER_ID, key, value)
    return {
        "user_scope": AUTHENTICATED_USER_ID,
        "storage": STORAGE,
        "item": item.model_dump(),
    }


@mcp.tool()
def delete_memory(memory_id: str) -> dict:
    """인증된 사용자의 PostgreSQL Memory ID가 일치할 때만 삭제합니다."""
    return {
        "user_scope": AUTHENTICATED_USER_ID,
        "storage": STORAGE,
        "deleted": delete_from_store(STORAGE, AUTHENTICATED_USER_ID, memory_id),
    }


@mcp.tool()
def find_relevant_memories(question: str) -> dict:
    """질문과 관련 있는 인증 사용자의 PostgreSQL Memory만 선택합니다."""
    items = list_from_store(STORAGE, AUTHENTICATED_USER_ID)
    selected = relevant_memories(items, question)
    return {
        "user_scope": AUTHENTICATED_USER_ID,
        "storage": STORAGE,
        "question": question,
        "items": serialize(selected),
    }


@mcp.tool()
def export_memories() -> dict:
    """인증된 사용자의 PostgreSQL Memory를 내보냅니다."""
    return {
        "user_scope": AUTHENTICATED_USER_ID,
        "storage": STORAGE,
        "memories": serialize(list_from_store(STORAGE, AUTHENTICATED_USER_ID)),
    }


if __name__ == "__main__":
    print(f"PostgreSQL Memory MCP: http://{MCP_HOST}:{MCP_PORT}/mcp")
    print("교육용 인증 사용자:", AUTHENTICATED_USER_ID)
    mcp.run(transport="streamable-http")
