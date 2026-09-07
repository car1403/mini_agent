import asyncio
import json
from types import SimpleNamespace
from contextlib import asynccontextmanager
import fakeredis.aioredis
from backend.app.stores import run_store as store
from backend.app.stores import job_queue
from backend.workers import agent_worker as worker
from backend.app.agents import runner
from backend.app.schemas import AgentAnswer

REQUEST = {"agent":"product","image_id":"image","question":"사용법과 재고","audio_id":None,"speak":True}

def test_atomic_claim_and_completion(monkeypatch):
    async def fake_execute(redis,run):
        return {"status":"completed","answer":"ok"}
    monkeypatch.setattr(worker,"execute",fake_execute)
    async def check():
        async with fakeredis.aioredis.FakeRedis(decode_responses=True) as redis:
            await job_queue.initialize(redis)
            run = await store.create_run(redis,REQUEST)
            item = await job_queue.next_job(redis,"test")
            await worker.process(redis,item)
            assert (await store.get_run(redis,run["run_id"]))["status"]=="completed"
            assert await redis.xlen(store.QUEUE)==0
            assert (await redis.xpending(store.QUEUE,job_queue.GROUP))["pending"]==0
            assert await store.change(redis,run["run_id"],expected={"queued"},status="running") is None
            events = await redis.xrange(store.event_key(run["run_id"]))
            assert [json.loads(e[1]["data"])["status"] for e in events]==["queued","running","completed"]
    asyncio.run(check())

def test_worker_failure_and_recovery(monkeypatch):
    async def broken(redis,run):
        raise RuntimeError("secret upstream error")
    monkeypatch.setattr(worker,"execute",broken)
    async def check():
        async with fakeredis.aioredis.FakeRedis(decode_responses=True) as redis:
            await job_queue.initialize(redis)
            for interrupted in (False,True):
                run = await store.create_run(redis,REQUEST)
                item = await job_queue.next_job(redis,"test")
                if interrupted:
                    await store.change(redis,run["run_id"],status="running")
                    item = (*item[:2],True)
                await worker.process(redis,item)
                saved = await store.get_run(redis,run["run_id"])
                assert saved["status"]=="failed"
                assert "secret" not in saved["error"]
    asyncio.run(check())

def test_runner_continues_when_code_is_read_and_preserves_text_on_tts_error(monkeypatch):
    called = []
    @asynccontextmanager
    async def session():
        yield object()
    async def discover(session,allowed):
        return [{"function":{"name":name}} for name in allowed]
    async def call(session,name,args,allowed):
        called.append(name)
        if name=="synthesize_speech":
            raise RuntimeError("tts down")
        if name=="analyze_scene":
            # 사진에 세부 정보가 없다는 이유로 잘못 true가 와도 코드를 읽었으면 계속합니다.
            return {"needs_new_photo":True,"candidate_codes":["MM-K100"]}
        return {"items":[{"product_id":"MM-K100"}]}
    class Message:
        def __init__(self,name=None):
            self.content = None if name else "확인"
            self.tool_calls = [SimpleNamespace(id=name,function=SimpleNamespace(name=name,arguments='{"term":"MM-K100"}'))] if name else None
        def model_dump(self,**kwargs):
            return {"role":"assistant","content":"확인"}
    messages = iter([Message("find_products"),Message("search_product_manuals"),Message()])
    async def next_step(*args):
        return next(messages)
    async def answer(*args):
        return AgentAnswer(status="completed",answer="확인한 답변",speech_text="음성 안내")
    for name,value in [("tools_session",session),("discover",discover),("call",call),("next_step",next_step),("final_answer",answer)]:
        monkeypatch.setattr(runner,name,value)
    async def check():
        async with fakeredis.aioredis.FakeRedis(decode_responses=True) as redis:
            run = await store.create_run(redis,REQUEST)
            await store.change(redis,run["run_id"],status="running")
            result = await runner.execute(redis,run)
            assert result["answer"]=="확인한 답변"
            assert result["audio_error"]
            assert called==["analyze_scene","find_products","search_product_manuals","synthesize_speech"]
    asyncio.run(check())
