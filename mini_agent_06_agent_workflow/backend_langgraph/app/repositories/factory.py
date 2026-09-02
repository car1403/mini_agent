from app.core.config import settings
from app.repositories.postgres_store import PostgresStore
from app.repositories.store import InMemoryStore


def create_store():
    if settings.storage_mode == "memory":
        return InMemoryStore()
    if settings.storage_mode == "postgres":
        return PostgresStore(settings.database_url)
    raise ValueError("STORAGE_MODE은 memory 또는 postgres여야 합니다.")
