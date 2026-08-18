from uuid import uuid4

from app.memory.policy import validate_memory_key
from app.schemas import MemoryItem


class MockMemoryStore:
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], MemoryItem] = {}

    def upsert(self, user_id: str, key: str, value: str) -> MemoryItem:
        validate_memory_key(key)
        identity = (user_id, key)
        current = self._items.get(identity)
        item = MemoryItem(
            id=current.id if current else str(uuid4()),
            user_id=user_id,
            key=key,
            value=value,
        )
        self._items[identity] = item
        return item

    def list(self, user_id: str) -> list[MemoryItem]:
        return [item for item in self._items.values() if item.user_id == user_id]

    def delete(self, user_id: str, memory_id: str) -> bool:
        identity = next(
            (
                identity
                for identity, item in self._items.items()
                if item.user_id == user_id and item.id == memory_id
            ),
            None,
        )
        if identity is None:
            return False
        del self._items[identity]
        return True

    def clear(self) -> None:
        self._items.clear()


mock_memory_store = MockMemoryStore()
