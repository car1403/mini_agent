"""Lab 03 — 택배함 인증 코드의 만료와 중복 실행을 안전하게 처리합니다.

학습 분류:
- 현재 성격: 인증·멱등성 Workflow
- Agent 여부: 아니오
- 권장 방향: 백엔드 보안 정책으로 유지
- 판단 근거: 인증, 만료, 일회성 사용과 상태 변경은 확률적인 LLM 판단이 아니라
  Backend가 결정적으로 검증해야 합니다. Agent는 누락 정보 재질문까지만 맡을 수 있습니다.

Backend 디렉터리 기준 역할:
- `schemas/`: OpenLockerInput이 택배함 ID와 인증 코드 입력 계약을 정의합니다.
- `tools/`: open_locker가 검증된 요청으로 택배함을 여는 실행 Tool입니다.
- `services/`: issue_access_code와 인증 상태가 발급·만료·일회성 사용 정책을 담당합니다.
- `agents/`: 실행 순서가 고정되어 있어 별도 Agent를 사용하지 않습니다.
- `routers/`: 이 파일에서는 `__main__` 실행부가 요청과 결과 확인을 대신합니다.
- `providers/`: LLM 호출 없이 서버 권한 검증을 학습하므로 사용하지 않습니다.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# [schemas/] 택배함 열기 Tool의 ID와 6자리 인증 코드 입력 계약입니다.
class OpenLockerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    locker_id: str = Field(min_length=1)
    access_code: str = Field(pattern=r"^\d{6}$")


# [학습용 저장소] 실제 Backend에서는 인증 저장소와 택배함 DB로 분리할 상태입니다.
AUTHORIZATIONS: dict[str, dict[str, Any]] = {}
LOCKERS = {"A-01": {"is_open": False}, "B-02": {"is_open": False}}


# [services/] 인증 코드를 발급하고 만료 시각과 일회성 사용 상태를 저장합니다.
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


# [tools/] 입력·권한·만료·중복 사용을 검사한 뒤 택배함 상태를 변경합니다.
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


# [routers/ 대체] 정상·중복·만료·잘못된 인증 요청을 직접 실행해 응답을 비교합니다.
if __name__ == "__main__":
    start = datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc)

    normal_code = issue_access_code("A-01", start)
    print("정상 실행:", open_locker({"locker_id": "A-01", "access_code": normal_code}, start))
    print("중복 실행:", open_locker({"locker_id": "A-01", "access_code": normal_code}, start))

    expired_code = issue_access_code("B-02", start)
    print("만료 실행:", open_locker({"locker_id": "B-02", "access_code": expired_code}, start + timedelta(minutes=6)))
    print("잘못된 인증:", open_locker({"locker_id": "A-01", "access_code": "999999"}, start))
    print("없는 택배함:", open_locker({"locker_id": "Z-99", "access_code": "999999"}, start))
