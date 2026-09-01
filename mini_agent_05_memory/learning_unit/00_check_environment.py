"""05 Memory 예제를 실행하기 전에 패키지·설정·서비스 상태를 확인합니다.

이 파일은 외부 Python 패키지 없이 실행할 수 있습니다.
실행: python .\00_check_environment.py
"""

import importlib.util
import os
from pathlib import Path
import socket
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
REQUIRED_PACKAGES = {
    "dotenv": "python-dotenv",
    "httpx": "httpx",
    "psycopg": "psycopg[binary]",
    "redis": "redis",
}


def load_simple_env(path: Path) -> dict[str, str]:
    """진단에 필요한 단순 KEY=VALUE 항목만 읽습니다."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def endpoint(url: str, default_port: int) -> tuple[str, int]:
    parsed = urlparse(url)
    return parsed.hostname or "127.0.0.1", parsed.port or default_port


def port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def show(label: str, success: bool, detail: str) -> None:
    print(f"{'OK' if success else 'FAIL':<4} {label:<20} {detail}")


def main() -> None:
    env = {**load_simple_env(ENV_FILE), **os.environ}
    redis_url = env.get("REDIS_URL", "redis://127.0.0.1:6379/0")
    database_url = env.get(
        "DATABASE_URL",
        "postgresql://agent_user:agent_password@127.0.0.1:5433/agent_db",
    )
    backend_url = env.get("BACKEND_API_URL", "http://127.0.0.1:8000")

    print("[00] Memory 실행 환경 점검\n")
    show("과정 루트 .env", ENV_FILE.exists(), str(ENV_FILE))

    print("\nPython 패키지")
    for module, package in REQUIRED_PACKAGES.items():
        installed = importlib.util.find_spec(module) is not None
        show(module, installed, "설치됨" if installed else f"pip install {package}")

    print("\n서비스 Port")
    for name, url, default_port, examples in (
        ("Redis", redis_url, 6379, "05, 07, 08, 11, 13"),
        ("PostgreSQL", database_url, 5432, "06, 09~13"),
        ("Mini Agent Backend", backend_url, 8000, "07~13"),
    ):
        host, port = endpoint(url, default_port)
        show(name, port_open(host, port), f"{host}:{port} · 예제 {examples}")

    print("\n다음 행동")
    print("- 패키지 FAIL: 과정 루트에서 pip install -r requirements.txt")
    print("- .env FAIL: Copy-Item .env.example .env")
    print("- Redis/PostgreSQL FAIL: 00_local-runtime 서비스를 실행")
    print("- Backend FAIL: Mini Agent 05 Backend를 실행")


if __name__ == "__main__":
    main()
