from fastapi import FastAPI

from app.simple_router import router


app = FastAPI(title="Mini Agent 04 · Simple RAG")
app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "stage": "mini_agent_04_rag"}
