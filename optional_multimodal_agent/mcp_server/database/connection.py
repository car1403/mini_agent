import psycopg
from psycopg.rows import dict_row
from mcp_server.core.config import DATABASE_URL

def connect():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=5)

def query(sql: str, params: tuple = ()) -> list[dict]:
    with connect() as conn:
        conn.execute("SET TRANSACTION READ ONLY")
        conn.execute("SET LOCAL statement_timeout = '10s'")
        return conn.execute(sql, params).fetchall()
