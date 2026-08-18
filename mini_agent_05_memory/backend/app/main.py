from fastapi import FastAPI

from app.routers.agent_router import agent_router
from app.routers.rag_router import rag_router
from app.routers.memory_router import memory_router


app = FastAPI(title="Mini Agent 05 · Memory")
app.include_router(agent_router)
app.include_router(rag_router)
app.include_router(memory_router)
