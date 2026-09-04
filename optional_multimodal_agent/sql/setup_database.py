"""DATABASE_URL의 PostgreSQL에 Optional Multimodal Agent Schema를 적용합니다."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


load_dotenv()


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL이 필요합니다.")

    schema_path = Path(__file__).with_name("init.sql")
    sql = schema_path.read_text(encoding="utf-8")

    with psycopg.connect(database_url, autocommit=True) as connection:
        connection.execute(sql)

    print("Schema applied:", schema_path)


if __name__ == "__main__":
    main()
