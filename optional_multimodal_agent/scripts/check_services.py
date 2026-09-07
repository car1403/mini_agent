import asyncio
import sys
from pathlib import Path

# 파일로 직접 실행해도 프로젝트의 backend, scripts 패키지를 찾게 합니다.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx
import psycopg
from scripts.core.config import DATABASE_URL, env
from backend.app.stores.run_store import redis_client
from backend.app.mcp.client import tools_session

async def main():
    failed = False
    for name in ("postgres","redis","mcp","backend"):
        try:
            if name=="postgres":
                with psycopg.connect(DATABASE_URL,connect_timeout=3) as conn:
                    counts = conn.execute("SELECT (SELECT count(*) FROM multimodal_products),(SELECT count(*) FROM multimodal_program_sessions),(SELECT count(*) FROM multimodal_knowledge_chunks)").fetchone()
                    if not all(counts):
                        raise RuntimeError("SQL seed 또는 RAG 적재가 필요합니다.")
                    print("postgres counts:",counts)
            elif name=="redis":
                async with redis_client() as redis:
                    await redis.ping()
            elif name=="mcp":
                async with tools_session() as session:
                    print("tools:",[t.name for t in (await session.list_tools()).tools])
            else:
                async with httpx.AsyncClient(timeout=5) as client:
                    (await client.get(env("BACKEND_URL","http://127.0.0.1:8000")+"/health")).raise_for_status()
            print(name,"OK")
        except Exception as exc:
            failed = True
            print(name,"FAIL",type(exc).__name__)
    if failed:
        raise SystemExit(1)

if __name__ == "__main__":
    asyncio.run(main())
