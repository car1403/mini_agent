r"""05. Redis TTL로 자동 만료되는 단기 Agent 상태를 저장합니다.

학습 목표:
- Redis Key에 사용자와 Session을 함께 넣어 상태를 격리합니다.
- TTL이 단기 상태의 남은 수명을 뜻한다는 점을 확인합니다.

실행: python .\05_redis_session.py
외부 서비스: Redis 필요
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from redis import Redis
from redis.exceptions import RedisError


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
REDIS_TTL_SECONDS = int(os.getenv("REDIS_TTL_SECONDS", "1800"))


def session_key(user_id: str, session_id: str) -> str:
    """같은 Session ID라도 사용자가 다르면 별도 Key를 만듭니다."""
    return f"mini-agent:session:{user_id}:{session_id}"


def main() -> None:
    client = Redis.from_url(REDIS_URL, decode_responses=True)
    user_id = "student-01"
    session_id = "travel-demo"
    key = session_key(user_id, session_id)
    state = {"current_step": "collect_information", "destination": "부산"}

    client.setex(key, REDIS_TTL_SECONDS, json.dumps(state, ensure_ascii=False))
    saved = client.get(key)

    print("[05] Redis 단기 Session\n")
    print("Redis Key:", key)
    print("저장한 상태:", json.loads(saved) if saved else None)
    print("남은 TTL(초):", client.ttl(key))
    print("\n핵심: 사용자별 단기 상태는 TTL이 지나면 Redis에서 자동으로 사라집니다.")


if __name__ == "__main__":
    try:
        main()
    except RedisError as error:
        print("\n[실행 실패] Redis에 연결하거나 상태를 저장하지 못했습니다.")
        print("원인:", error)
        print("REDIS_URL과 Redis Container를 확인하세요.")
        print("환경 점검: python .\00_check_environment.py")
