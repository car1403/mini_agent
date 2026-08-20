"""택배함 인증 코드의 만료와 중복 실행을 안전하게 처리합니다."""

from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OpenLockerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    locker_id: str = Field(min_length=1)
    access_code: str = Field(pattern=r"^\d{6}$")


AUTHORIZATIONS: dict[str, dict[str, Any]] = {}
LOCKERS = {"A-01": {"is_open": False}, "B-02": {"is_open": False}}


def issue_access_code(locker_id: str, now: datetime, valid_minutes: int = 5) -> str:
    if locker_id not in LOCKERS:
        raise ValueError("존재하지 않는 택배함입니다.")
    if valid_minutes <= 0:
        raise ValueError("인증 코드 유효 시간은 1분 이상이어야 합니다.")
    code = "123456" if locker_id == "A-01" else "654321"
    AUTHORIZATIONS[code] = {
        "locker_id": locker_id,
        "expires_at": now + timedelta(minutes=valid_minutes),
        "used": False,
    }
    return code


def open_locker(arguments: dict[str, Any], now: datetime) -> dict[str, Any]:
    args = OpenLockerInput.model_validate(arguments)
    if args.locker_id not in LOCKERS:
        return {"opened": False, "code": "LOCKER_NOT_FOUND"}
    authorization = AUTHORIZATIONS.get(args.access_code)
    if authorization is None or authorization["locker_id"] != args.locker_id:
        return {"opened": False, "code": "INVALID_AUTHORIZATION"}
    if authorization["used"]:
        return {"opened": False, "code": "ALREADY_USED"}
    if now >= authorization["expires_at"]:
        return {"opened": False, "code": "EXPIRED"}

    # 실제 서비스에서는 사용 처리와 문 열기 명령을 하나의 원자적 작업으로 보호합니다.
    authorization["used"] = True
    LOCKERS[args.locker_id]["is_open"] = True
    return {"opened": True, "locker_id": args.locker_id}


if __name__ == "__main__":
    start = datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc)

    normal_code = issue_access_code("A-01", start)
    print("정상 실행:", open_locker({"locker_id": "A-01", "access_code": normal_code}, start))
    print("중복 실행:", open_locker({"locker_id": "A-01", "access_code": normal_code}, start))

    expired_code = issue_access_code("B-02", start)
    print("만료 실행:", open_locker({"locker_id": "B-02", "access_code": expired_code}, start + timedelta(minutes=6)))
    print("잘못된 인증:", open_locker({"locker_id": "A-01", "access_code": "999999"}, start))
    print("없는 택배함:", open_locker({"locker_id": "Z-99", "access_code": "999999"}, start))
