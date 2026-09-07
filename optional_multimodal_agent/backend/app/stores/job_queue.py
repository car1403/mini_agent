from redis.exceptions import ResponseError
from backend.app.stores.run_store import QUEUE
from backend.app.core.config import RUN_TIMEOUT

GROUP = "agents"

async def initialize(redis):
    try:
        await redis.xgroup_create(QUEUE,GROUP,id="0-0",mkstream=True)
    except ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise

async def next_job(redis, consumer):
    # 처리 제한시간이 지난 미확인 작업을 회수합니다.
    reclaimed = await redis.xautoclaim(QUEUE,GROUP,consumer,
                                     min_idle_time=(RUN_TIMEOUT+60)*1000,start_id="0-0",count=1)
    if reclaimed[1]:
        return (*reclaimed[1][0], True)
    batches = await redis.xreadgroup(GROUP,consumer,{QUEUE:">"},count=1,block=3000)
    if batches:
        return (*batches[0][1][0], False)
    return None

async def acknowledge(redis, event_id):
    async with redis.pipeline(transaction=True) as pipe:
        pipe.xack(QUEUE,GROUP,event_id)
        pipe.xdel(QUEUE,event_id)
        await pipe.execute()
