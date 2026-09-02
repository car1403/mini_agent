from fastapi import FastAPI

from app.routers.agent_router import router


app = FastAPI(
    title="Mini Agent 06 · Independent Single Agent Service",
    description="서로 연결되지 않은 여러 Single Agent를 공통 Python Agent Runtime으로 실행합니다.",
    version="1.0.0",
)
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Mini Agent 06 API", "docs": "/docs"}
