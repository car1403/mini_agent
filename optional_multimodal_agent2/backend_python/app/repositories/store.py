from app.core.config import settings
from app.repositories.postgres_store import PostgresStore


if settings.storage_mode != "postgres":
    raise RuntimeError("실행 저장소는 PostgreSQL만 지원합니다. STORAGE_MODE=postgres로 설정하세요.")

store = PostgresStore(settings.database_url)
