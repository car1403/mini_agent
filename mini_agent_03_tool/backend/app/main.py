from fastapi import FastAPI

from app.routers.stage_01_router import stage_01_router
from app.routers.stage_02_router import stage_02_router
from app.routers.stage_03_router import stage_03_router
from app.routers.lab_router import lab_router


TAGS_METADATA = [
    {
        "name": "01 · LLM 기초",
        "description": "Provider, 일반 생성, 요청 분류와 Multimodal 기본 기능입니다.",
    },
    {
        "name": "02 · Prompt와 구조화 출력",
        "description": "Prompt 구성, Pydantic 검증과 Structured Output 기능입니다.",
    },
    {
        "name": "03 · Tool과 Agent",
        "description": "Tool 선택, Allowlist 실행과 단일 Agent Cycle 기능입니다.",
    },
    {
        "name": "03 · Tool Use Labs",
        "description": "Ollama가 7개 Lab을 분류하고 안전한 Agent 또는 Workflow로 연결합니다.",
    },
]


app = FastAPI(title="Mini Agent 03 · Tool Use", openapi_tags=TAGS_METADATA)
app.include_router(stage_01_router)
app.include_router(stage_02_router)
app.include_router(stage_03_router)
# 7개 실전 Lab은 HTTP 진입점을 하나로 유지하고 내부 Routing Service에서
# Agent-controlled Loop와 Agent-assisted Workflow로 안전하게 분기합니다.
app.include_router(lab_router)
