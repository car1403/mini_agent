from copy import deepcopy
from uuid import uuid4


class InMemoryStore:
    def __init__(self) -> None:
        self.memories: dict[str, dict[str, dict]] = {}
        self.runs: dict[str, dict] = {}

    def add_memory(self, user_id: str, key: str, value: str) -> dict:
        memory_id = str(uuid4())
        item = {"id": memory_id, "user_id": user_id, "key": key, "value": value}
        self.memories.setdefault(user_id, {})[memory_id] = item
        return deepcopy(item)

    def list_memories(self, user_id: str) -> list[dict]:
        return deepcopy(list(self.memories.get(user_id, {}).values()))

    def delete_memory(self, user_id: str, memory_id: str) -> bool:
        if memory_id not in self.memories.get(user_id, {}):
            return False
        del self.memories[user_id][memory_id]
        return True

    def create_run(self, data: dict) -> dict:
        run_id = str(uuid4())
        item = {"run_id": run_id, **data}
        self.runs[run_id] = item
        return deepcopy(item)

    def get_run(self, run_id: str) -> dict | None:
        item = self.runs.get(run_id)
        return deepcopy(item) if item else None

    def update_run(self, run_id: str, updates: dict) -> dict | None:
        if run_id not in self.runs:
            return None
        self.runs[run_id].update(updates)
        return deepcopy(self.runs[run_id])


from app.core.config import settings


if settings.storage_mode == "postgres":
    from app.repositories.postgres_store import PostgresStore

    store = PostgresStore(settings.database_url)
else:
    store = InMemoryStore()
