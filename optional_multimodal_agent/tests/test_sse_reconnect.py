import asyncio
import fakeredis.aioredis
from backend_python.app.stores.run_store import create_run, change, event_key
from backend_python.app.stores.event_store import event_stream
from frontend.core.sse_client import parse_events

def test_replay_only_after_last_id():
    async def check():
        async with fakeredis.aioredis.FakeRedis(decode_responses=True) as redis:
            run = await create_run(redis,{"agent":"product"})
            first = (await redis.xrange(event_key(run["run_id"])))[0][0]
            await change(redis,run["run_id"],status="completed",step="completed",message="완료")
            frames = [frame async for frame in event_stream(redis,run["run_id"],first)]
            parsed = list(parse_events("".join(frames).splitlines()))
            assert [p["event"] for p in parsed]==["progress","end"]
            assert parsed[0]["data"]["status"]=="completed"
            assert parsed[0]["id"]!=first
    asyncio.run(check())

def test_parser_ignores_heartbeat_and_supports_multiline():
    parsed = list(parse_events([': heartbeat','','id: 1-0','event: progress','data: {','data: "message": "안녕"}','']))
    assert parsed==[{"id":"1-0","event":"progress","data":{"message":"안녕"}}]
