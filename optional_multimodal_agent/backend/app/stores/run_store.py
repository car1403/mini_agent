"""상태와 이벤트를 같은 Redis 트랜잭션에서 저장합니다."""
import json
from datetime import datetime, timezone
from uuid import uuid4
from redis.asyncio import Redis
from redis.exceptions import WatchError
from backend.app.core.config import REDIS_URL, TTL

QUEUE = "mm:jobs"
TERMINAL = {"completed","needs_input","failed"}

def redis_client():
    return Redis.from_url(REDIS_URL,decode_responses=True)

def key(run_id):
    return f"mm:run:{run_id}"

def event_key(run_id):
    return f"mm:events:{run_id}"

async def get_run(redis, run_id):
    value = await redis.get(key(run_id))
    return json.loads(value) if value else None

def write(pipe, run, message, tool_name=None, enqueue=False):
    run["updated_at"] = datetime.now(timezone.utc).isoformat()
    event = {"run_id":run["run_id"],"status":run["status"],"step":run["step"],
             "message":message,"tool_name":tool_name,"timestamp":run["updated_at"]}
    pipe.set(key(run["run_id"]),json.dumps(run,ensure_ascii=False),ex=TTL)
    pipe.xadd(event_key(run["run_id"]),{"data":json.dumps(event,ensure_ascii=False)})
    pipe.expire(event_key(run["run_id"]),TTL)
    if enqueue:
        pipe.xadd(QUEUE,{"run_id":run["run_id"]})

async def create_run(redis, request, parent_id=None):
    run = {"run_id":uuid4().hex,"request":request,"parent_id":parent_id,
           "status":"queued","step":"queued","result":None,"error":None}
    async with redis.pipeline(transaction=True) as pipe:
        write(pipe,run,"작업이 등록되었습니다.",enqueue=True)
        await pipe.execute()
    return run

async def change(redis, run_id, *, expected=None, message="", tool_name=None, **updates):
    while True:
        async with redis.pipeline(transaction=True) as pipe:
            try:
                await pipe.watch(key(run_id))
                raw = await pipe.get(key(run_id))
                if not raw:
                    return None
                run = json.loads(raw)
                if expected is not None and run["status"] not in expected:
                    return None
                run.update(updates)
                pipe.multi()
                write(pipe,run,message,tool_name)
                await pipe.execute()
                return run
            except WatchError:
                continue
