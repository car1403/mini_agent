class MemoryStore:
    def __init__(self) -> None:
        self.items = {}

    def save(self, user_id: str, key: str, value: str) -> None:
        """TODO: (user_id, key)를 기준으로 저장 또는 수정하세요."""
        raise NotImplementedError

    def list_for_user(self, user_id: str) -> list[dict]:
        """TODO: 해당 사용자의 Memory만 반환하세요."""
        raise NotImplementedError
