"""사용자별 장기 Memory를 저장·조회·수정·삭제합니다."""

from dataclasses import asdict, dataclass
from uuid import uuid4


@dataclass
class Memory:
    id: str
    user_id: str
    key: str
    value: str


class MemoryStore:
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], Memory] = {}

    def upsert(self, user_id: str, key: str, value: str) -> Memory:
        identity = (user_id, key)
        current = self._items.get(identity)
        memory = Memory(current.id if current else str(uuid4()), user_id, key, value)
        self._items[identity] = memory
        return memory

    def list_for_user(self, user_id: str) -> list[dict]:
        return [asdict(item) for item in self._items.values() if item.user_id == user_id]

    def delete(self, user_id: str, memory_id: str) -> bool:
        identity = next(
            (key for key, item in self._items.items() if item.id == memory_id and item.user_id == user_id),
            None,
        )
        if identity is None:
            return False
        del self._items[identity]
        return True


if __name__ == "__main__":
    store = MemoryStore()
    memory = store.upsert("user-a", "transportation", "대중교통")
    store.upsert("user-a", "transportation", "도보와 대중교통")
    store.upsert("user-b", "transportation", "렌터카")
    print("user-a:", store.list_for_user("user-a"))
    print("다른 사용자의 삭제 차단:", store.delete("user-b", memory.id))
    print("본인 삭제:", store.delete("user-a", memory.id))
