from fastapi import FastAPI

from app.routers.agent_router import agent_router


app = FastAPI(title="Mini Agent 03 · Tool Use")
app.include_router(agent_router)
