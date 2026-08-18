"""Quick validation script for /api/generate endpoint.

Usage (run from repository root):
    python -m backend.tests.quick_generate

It reads the existing .env in `mini_agent_01_llm` and posts to the running backend.
"""
import os
import sys
from dotenv import load_dotenv
import httpx

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ENV_PATH = os.path.abspath(os.path.join(ROOT, '..', '.env'))
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

BASE_URL = os.getenv('PYTHON_AGENT_API_URL', os.getenv('BACKEND_API_URL', 'http://127.0.0.1:8000'))

PROVIDERS = ("gemini", "openai", "ollama")

PAYLOAD_TEMPLATE = {
    "message": "부산 2박 여행을 준비할 때 먼저 확인할 것은 무엇인가요?",
}


def call_generate(provider: str):
    payload = {**PAYLOAD_TEMPLATE, "provider": provider}
    try:
        resp = httpx.post(f"{BASE_URL}/api/generate", json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json().get('data') or resp.json()
        model = data.get('model')
        latency = data.get('latency_ms')
        content = data.get('content')
        print(f"[{provider}] model={model} latency_ms={latency}")
        if content:
            print(content[:800])
    except Exception as e:
        print(f"[{provider}] 호출 실패: {e}")


if __name__ == '__main__':
    print('Base URL:', BASE_URL)
    for p in PROVIDERS:
        call_generate(p)
