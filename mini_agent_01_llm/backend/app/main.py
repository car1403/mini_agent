from fastapi import FastAPI

from app.routers.agent_router import agent_router
from app.routers.media_router import media_router


app = FastAPI(title="Mini Agent 01 · LLM 판단에서 서비스 연결까지")
app.include_router(agent_router)
app.include_router(media_router)
