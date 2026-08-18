"""Redis TTL로 자동 만료되는 단기 Agent 상태를 저장합니다."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from redis import Redis


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
REDIS_TTL_SECONDS = int(os.getenv("REDIS_TTL_SECONDS", "1800"))


def session_key(session_id: str) -> str:
    return f"mini-agent:session:{session_id}"


client = Redis.from_url(REDIS_URL, decode_responses=True)
state = {"current_step": "collect_information", "destination": "부산"}
client.setex(session_key("travel-demo"), REDIS_TTL_SECONDS, json.dumps(state, ensure_ascii=False))

saved = client.get(session_key("travel-demo"))
print("저장한 상태:", json.loads(saved) if saved else None)
print("남은 TTL(초):", client.ttl(session_key("travel-demo")))
print("TTL이 지나면 Redis가 이 상태를 자동 삭제합니다.")
