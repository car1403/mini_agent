"""멀티모달 Agent 전용 데이터베이스에 프로젝트 테이블을 생성합니다."""
import sys
from pathlib import Path

# `python scripts/setup_database.py` 실행도 지원합니다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import psycopg
from scripts.core.config import ROOT, DATABASE_URL

def setup():
    with psycopg.connect(DATABASE_URL) as conn:
        for path in sorted((ROOT/"sql").glob("*.sql")):
            conn.execute(path.read_text(encoding="utf-8"))
            print("Applied:",path.name)

if __name__ == "__main__":
    setup()
