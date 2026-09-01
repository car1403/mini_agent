"""03. 사용자별 장기 Memory를 저장·조회·수정·삭제합니다.

학습 목표:
- upsert가 같은 key를 새 값으로 갱신하는 동작을 이해합니다.
- 모든 조회와 삭제를 user_id 범위로 제한해야 하는 이유를 확인합니다.

실행: python .\03_user_memory_crud.py
외부 서비스: 필요 없음
"""

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
        """사용자와 key가 같으면 수정하고, 없으면 새로 저장합니다."""
        identity = (user_id, key)
        current = self._items.get(identity)
        memory = Memory(current.id if current else str(uuid4()), user_id, key, value)
        self._items[identity] = memory
        return memory

    def list_for_user(self, user_id: str) -> list[dict]:
        """요청한 사용자의 Memory만 반환합니다."""
        return [asdict(item) for item in self._items.values() if item.user_id == user_id]

    def delete(self, user_id: str, memory_id: str) -> bool:
        """Memory ID와 사용자 ID가 모두 일치할 때만 삭제합니다."""
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
    print("[03] 사용자별 장기 Memory CRUD\n")
    memory = store.upsert("user-a", "transportation", "대중교통")
    updated = store.upsert("user-a", "transportation", "도보와 대중교통")
    store.upsert("user-b", "transportation", "렌터카")
    print("같은 Memory ID로 수정됨:", memory.id == updated.id)
    print("user-a 조회:", store.list_for_user("user-a"))
    print("user-b 조회:", store.list_for_user("user-b"))
    print("다른 사용자의 삭제 차단(False):", store.delete("user-b", memory.id))
    print("본인 삭제 성공(True):", store.delete("user-a", memory.id))
    print("삭제 후 user-a:", store.list_for_user("user-a"))
    print("\n핵심: Memory 작업에는 항상 인증된 사용자 범위가 필요합니다.")
