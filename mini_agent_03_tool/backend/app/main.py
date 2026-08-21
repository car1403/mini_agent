from fastapi import FastAPI

from app.routers.agent_router import agent_router


app = FastAPI(
    title="Mini Agent 03 · Tool Use",
    openapi_tags=[
        {
            "name": "01. LLM to Agent",
            "description": "Mini Agent 01의 기본 LLM, 판단, 멀티모달 API",
        },
        {
            "name": "02. Prompt & Structured Output",
            "description": "Mini Agent 02의 프롬프트 및 구조화 출력 API",
        },
        {
            "name": "03. Tool Use",
            "description": "Mini Agent 03에서 추가된 Tool 선택, 실행, 완결 API",
        },
    ],
)
app.include_router(agent_router)
