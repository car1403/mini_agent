"""TTL 상태와 장기 Memory의 보존·내보내기·삭제 정책을 비교하는 독립 Lab."""

from dataclasses import dataclass


@dataclass
class Record:
    user_id: str
    kind: str
    value: str
    expires_at: int | None


def active(records: list[Record], *, user_id: str, now: int) -> list[Record]:
    return [
        record for record in records
        if record.user_id == user_id
        and (record.expires_at is None or record.expires_at > now)
    ]


def export_user(records: list[Record], user_id: str, now: int) -> list[dict]:
    return [record.__dict__.copy() for record in active(records, user_id=user_id, now=now)]


def delete_user(records: list[Record], user_id: str) -> int:
    before = len(records)
    records[:] = [record for record in records if record.user_id != user_id]
    return before - len(records)


if __name__ == "__main__":
    data = [
        Record("user-a", "session", "부산 여행 2단계", 120),
        Record("user-a", "preference", "대중교통", None),
        Record("user-b", "preference", "도보", None),
    ]
    print("만료 전:", export_user(data, "user-a", now=100))
    print("만료 후:", export_user(data, "user-a", now=130))
    print("삭제 수:", delete_user(data, "user-a"))
    print("남은 사용자:", [record.user_id for record in data])
