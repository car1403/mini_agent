from fastapi import FastAPI

from app.routers.agent_router import agent_router
from app.routers.media_router import media_router


app = FastAPI(title="Mini Agent 02 · Prompt와 Structured Output")
app.include_router(agent_router)
app.include_router(media_router)
