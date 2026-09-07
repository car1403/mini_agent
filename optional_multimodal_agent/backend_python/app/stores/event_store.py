import json
from backend_python.app.stores.run_store import event_key, get_run, TERMINAL

async def event_stream(redis, run_id, after="0-0"):
    """첫 연결은 전체 재생, 재연결은 마지막 ID 이후부터 읽습니다."""
    cursor = after
    while True:
        batches = await redis.xread({event_key(run_id):cursor},count=100,block=1500)
        if batches:
            for _, entries in batches:
                for event_id, values in entries:
                    cursor = event_id
                    yield f"id: {event_id}\nevent: progress\ndata: {values['data']}\n\n"
            continue
        run = await get_run(redis,run_id)
        if run is None or run["status"] in TERMINAL:
            yield "event: end\ndata: {}\n\n"
            return
        yield ": heartbeat\n\n"
