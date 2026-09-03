import json
from datetime import datetime, timezone
from typing import Any

from redis import Redis

from app.core.config import REDIS_URL, RUN_PROGRESS_TTL_SECONDS

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

def publish(run_id: str, stage: str, message: str, progress: int, status: str) -> None:
    state_key, event_key = f"agent:run:{run_id}:state", f"agent:run:{run_id}:events"
    now = datetime.now(timezone.utc).isoformat()
    redis_client.hset(state_key, mapping={"status": status, "stage": stage, "message": message, "progress": progress, "updated_at": now})
    redis_client.xadd(event_key, {"stage": stage, "message": message, "progress": progress, "status": status, "created_at": now}, maxlen=200)
    redis_client.expire(state_key, RUN_PROGRESS_TTL_SECONDS)
    redis_client.expire(event_key, RUN_PROGRESS_TTL_SECONDS)

def read_progress(run_id: str) -> dict[str, Any]:
    state = redis_client.hgetall(f"agent:run:{run_id}:state")
    events = redis_client.xrange(f"agent:run:{run_id}:events")
    return {"run_id": run_id, "state": state, "events": [{"id": event_id, **data} for event_id, data in events]}
