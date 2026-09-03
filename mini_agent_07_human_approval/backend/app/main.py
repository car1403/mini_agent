from fastapi import FastAPI

from app.routers.agent_router import router


app = FastAPI(
    title="Mini Agent 07 · Human Approval and Safety",
    description="Order Agent의 주문 Tool을 중단하고 사용자 승인 후 안전하게 실행합니다.",
    version="1.0.0",
)
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Mini Agent 06 API", "docs": "/docs"}
