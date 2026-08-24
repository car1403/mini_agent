"""교육용 In-memory Mock Repository입니다.

Agent와 Workflow가 같은 상태를 관찰하도록 한곳에서 차량, 장치, 인증 코드, 도서,
재고와 Session을 보관합니다. 실제 DB 트랜잭션·Redis TTL·장치 연결을 구현한 것이
아니며 Backend 재시작 또는 reset API 호출 시 모두 초기화됩니다.

Agent는 Repository를 직접 수정하지 않습니다. 조회·상태 변경 Tool과 Service를
통해서만 접근하게 하여 실제 저장소로 교체할 때도 업무 경계를 유지합니다.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Any

class LabRepository:
    def __init__(self) -> None: self.reset()
    def reset(self) -> None:
        now = datetime.now(timezone.utc)
        self.vehicles = {"12가3456": {"active": True}, "34나7890": {"active": False}}
        self.gate_open = False
        self.lockers = {"L101": {"code": "1234", "expires_at": now + timedelta(hours=1), "used": False}, "L102": {"code": "9999", "expires_at": now - timedelta(minutes=1), "used": False}}
        self.air_conditioner = {"power": "off"}
        self.members = {"M100": {"active": True, "overdue": False}, "M200": {"active": True, "overdue": True}}
        self.books = {"B101": {"title": "파이썬 첫걸음", "available": True}, "B102": {"title": "에이전트 설계", "available": False}}
        self.loans = {"M100": ["B201", "B202"], "M200": ["B203"]}
        self.inventory = {"SKU-001": {"available": 5, "version": 1}}
        self.sessions: dict[str, dict[str, Any]] = {}
        self.pending_actions: dict[str, dict[str, Any]] = {}
    def session(self, session_id: str, lab_id: str) -> dict[str, Any]:
        return self.sessions.setdefault(f"{lab_id}:{session_id}", {})
    def snapshot(self, lab_id: str) -> dict[str, Any]:
        values = {"parking": {"gate_open": self.gate_open, "vehicles": self.vehicles}, "air_conditioner": self.air_conditioner, "parcel_locker": self.lockers, "library": {"books": self.books, "loans": self.loans}, "inventory": self.inventory}
        return deepcopy(values.get(lab_id, {}))

    def create_pending_action(self, lab_id: str, tool_name: str, arguments: dict[str, Any], ttl_seconds: int = 120) -> dict[str, Any]:
        """정책 검사를 통과한 상태 변경 인자를 사용자 확인 전까지 짧게 보관합니다."""
        action_id = str(uuid4())
        action = {"action_id": action_id, "lab_id": lab_id, "tool_name": tool_name, "arguments": deepcopy(arguments), "expires_at": datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)}
        self.pending_actions[action_id] = action
        return deepcopy(action)

    def consume_pending_action(self, action_id: str, expected_lab_id: str) -> dict[str, Any] | None:
        """유효한 action을 한 번만 반환하여 확인 요청의 중복 실행을 막습니다."""
        action = self.pending_actions.pop(action_id, None)
        if action is None or action["lab_id"] != expected_lab_id:
            return None
        if datetime.now(timezone.utc) > action["expires_at"]:
            return None
        return action

    def get_pending_action(self, action_id: str) -> dict[str, Any] | None:
        """확인 요청을 원래 Lab으로 라우팅하기 위한 읽기 전용 조회입니다."""
        action = self.pending_actions.get(action_id)
        if action is None or datetime.now(timezone.utc) > action["expires_at"]:
            return None
        return deepcopy(action)

lab_repository = LabRepository()

