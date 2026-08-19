from fastapi import FastAPI

from app.routers.agent_router import agent_router
from app.routers.media_router import media_router


app = FastAPI(
    title="Mini Agent 02 · Prompt와 Structured Output",
    openapi_tags=[
        {
            "name": "01. LLM to Agent",
            "description": "Mini Agent 01에서 이어받은 기본 LLM 및 멀티모달 API",
        },
        {
            "name": "02. Prompt & Structured Output",
            "description": "Mini Agent 02에서 추가된 프롬프트 및 구조화 출력 API",
        },
    ],
)
app.include_router(agent_router)
app.include_router(media_router)
