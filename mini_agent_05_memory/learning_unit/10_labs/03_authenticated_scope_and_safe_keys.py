"""인증 사용자 범위와 Redis-safe 결정적 Key를 확인하는 독립 Lab."""

from hashlib import sha256


def token(value: str) -> str:
    if not value or len(value) > 100:
        raise ValueError("ID는 1~100자여야 합니다.")
    return sha256(value.encode("utf-8")).hexdigest()


def session_key(authenticated_user_id: str, session_id: str) -> str:
    return f"memory:session:{token(authenticated_user_id)}:{token(session_id)}"


def scoped_items(items: list[dict], authenticated_user_id: str) -> list[dict]:
    return [item for item in items if item["user_id"] == authenticated_user_id]


if __name__ == "__main__":
    documents = [
        {"user_id": "user-a", "value": "대중교통"},
        {"user_id": "user-b", "value": "도보"},
    ]
    claimed_user_id = "user-b"
    authenticated_user_id = "user-a"
    print("클라이언트 주장:", claimed_user_id)
    print("Backend 조회 결과:", scoped_items(documents, authenticated_user_id))
    print("안전한 Redis Key:", session_key("user-*", "trip:*"))
