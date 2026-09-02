from fastapi import FastAPI

from app.routers.api import router


app = FastAPI(
    title="05 LLM Agent Orchestration",
    description="여행 Agent 교육용 Mock First API",
    version="1.0.0",
)
app.include_router(router)
