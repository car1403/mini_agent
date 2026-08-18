from fastapi import FastAPI

from app.routers.agent_router import agent_router
from app.routers.rag_router import rag_router


app = FastAPI(title="Mini Agent 04 · RAG")
app.include_router(agent_router)
app.include_router(rag_router)
