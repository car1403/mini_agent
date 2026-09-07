from fastapi import FastAPI
import uvicorn

from app.routers.api import router


app = FastAPI(
    title="Optional Multimodal Python Agent",
    description="실제 LLM과 PostgreSQL을 사용하는 여행 Agent API",
    version="1.0.0",
)
app.include_router(router)

