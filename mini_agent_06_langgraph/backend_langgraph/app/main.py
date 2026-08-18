from fastapi import FastAPI

from app.routers.api import router
from app.routers.learning import learning_router


app = FastAPI(
    title="05 LLM Agent Orchestration",
    description="여행 Agent 교육용 Mock First API",
    version="1.0.0",
)
app.include_router(router)
app.include_router(learning_router)
