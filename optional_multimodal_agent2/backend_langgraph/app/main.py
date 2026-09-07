from fastapi import FastAPI
import uvicorn

from app.routers.api import router


app = FastAPI(
    title="Optional Multimodal LangGraph Agent",
    description="실제 LLM과 PostgreSQL을 사용하는 LangGraph 여행 Agent API",
    version="1.0.0",
)
app.include_router(router)