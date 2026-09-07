"""backend_python/app 디렉터리에서 실행: python worker.py"""
import asyncio
import logging
import sys
from pathlib import Path
from uuid import uuid4

# 직접 실행하면 이 파일의 디렉터리가 sys.path[0]이 됩니다.
# 이 상태에서는 app/mcp가 외부 MCP SDK인 mcp보다 먼저 검색되므로 제거합니다.
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parents[1]
sys.path = [path for path in sys.path if Path(path or ".").resolve() != APP_DIR]
sys.path.insert(0, str(PROJECT_ROOT))

from backend_python.app.agents.runner import execute
from backend_python.app.stores.run_store import redis_client, get_run, change
from backend_python.app.stores.job_queue import initialize, next_job, acknowledge
from shared.config import RUN_TIMEOUT

async def process(redis, item):
    event_id, fields, recovered = item
    run_id = fields["run_id"]
    run = await get_run(redis,run_id)
    if run and recovered and run["status"]=="running":
        await change(redis,run_id,expected={"running"},status="failed",step="interrupted",
                     error="Worker가 중단되었습니다. 다시 실행해 주세요.",message="중단된 작업을 감지했습니다.")
    else:
        run = await change(redis,run_id,expected={"queued"},status="running",step="started",message="Agent 실행을 시작합니다.")
        if run:
            try:
                async with asyncio.timeout(RUN_TIMEOUT):
                    result = await execute(redis,run)
                await change(redis,run_id,expected={"running"},status=result["status"],step=result["status"],
                             result=result,message="추가 입력이 필요합니다." if result["status"]=="needs_input" else "실행이 완료되었습니다.")
            except Exception:
                logging.exception("Agent run failed: %s",run_id)
                await change(redis,run_id,expected={"running"},status="failed",step="failed",
                             error="실행에 실패했습니다. 서비스 설정과 Worker 로그를 확인한 뒤 다시 실행하세요.",message="실행 실패")
    await acknowledge(redis,event_id)

async def main():
    logging.basicConfig(level=logging.INFO)
    async with redis_client() as redis:
        await initialize(redis)
        consumer = uuid4().hex
        while True:
            try:
                item = await next_job(redis,consumer)
                if item:
                    await process(redis,item)
            except Exception:
                logging.exception("Redis queue error; reconnecting")
                await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
