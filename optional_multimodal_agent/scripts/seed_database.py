"""실행: python -m scripts.seed_database --base-date 2026-09-07"""
import argparse
import sys
from datetime import date
from pathlib import Path

# `python scripts/seed_database.py` 실행도 지원합니다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import psycopg
from shared.config import ROOT, DATABASE_URL

def seed(base_date):
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("SELECT set_config('app.seed_date',%s,true)",(base_date.isoformat(),))
        for path in sorted((ROOT/"sql"/"seeds").glob("*.sql")):
            conn.execute(path.read_text(encoding="utf-8"))
            print("Seeded:",path.name)
    print("기존 회차·재고는 보존됩니다. 날짜를 바꿔도 기존 회차가 덮어써지지 않습니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-date",type=date.fromisoformat,default=date.today())
    seed(parser.parse_args().base_date)
