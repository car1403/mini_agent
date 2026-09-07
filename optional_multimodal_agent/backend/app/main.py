from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
import sys
from pathlib import Path

# Ensure the project root (optional_multimodal_agent) is on sys.path so
# absolute imports resolve when running from `backend`.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# Use package-relative imports so `uvicorn app.main:app` works when
# the current working directory is `backend` (module name `app`).
from .stores.run_store import redis_client
from .routers import media, runs

@asynccontextmanager
async def lifespan(app):
    app.state.redis = redis_client()
    yield
    await app.state.redis.aclose()

app = FastAPI(title="멀티모달 Agent 실습",lifespan=lifespan)
app.include_router(media.router)
app.include_router(runs.router)

@app.exception_handler(RedisError)
async def redis_error(request, exc):
    return JSONResponse(status_code=503,content={"detail":"Redis에 연결할 수 없습니다. 서비스를 확인하세요."})

@app.get("/health")
async def health():
    await app.state.redis.ping()
    return {"status":"ok","redis":"connected"}

if __name__ == "__main__":
    import uvicorn
    # Run the ASGI app object directly. This is robust whether the
    # package is addressed as `backend.app` or `app`.
    uvicorn.run(app, host="127.0.0.1", port=8000)
