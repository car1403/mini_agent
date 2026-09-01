from fastapi import FastAPI

from app.routers.stage_01_router import stage_01_router
from app.routers.stage_02_router import stage_02_router
from app.routers.stage_03_router import stage_03_router
from app.routers.rag_router import rag_router
from app.routers.memory_router import memory_router
from app.routers.authenticated_memory_router import authenticated_memory_router
from app.routers.mcp_router import mcp_router


TAGS_METADATA = [
    {"name": "01 · LLM 기초", "description": "Provider, 일반 생성, 분류와 Media 기능입니다."},
    {"name": "02 · Prompt와 구조화 출력", "description": "Prompt, Pydantic와 Structured Output 기능입니다."},
    {"name": "03 · Tool과 Agent", "description": "Tool 선택, 안전 실행과 단일 Agent Cycle입니다."},
    {"name": "04 · RAG", "description": "Chunking, Indexing, 검색과 RAG 답변 기능입니다."},
    {"name": "05 · Memory", "description": "대화·세션·장기 Memory 저장과 복원 기능입니다."},
]

app = FastAPI(title="Mini Agent 05 · Memory", openapi_tags=TAGS_METADATA)
app.include_router(stage_01_router)
app.include_router(stage_02_router)
app.include_router(stage_03_router)
app.include_router(rag_router)
app.include_router(memory_router)
app.include_router(authenticated_memory_router)
app.include_router(mcp_router)
