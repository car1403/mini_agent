"""작업을 읽기, 초안, 변경, 금지 위험도로 분류합니다."""

from dataclasses import dataclass
from typing import Literal


Risk = Literal["read", "draft", "change", "forbidden"]


@dataclass(frozen=True)
class ActionPolicy:
    name: str
    risk: Risk
    description: str


POLICIES = {
    "search_policy": ActionPolicy("search_policy", "read", "정책 문서를 조회합니다."),
    "create_draft": ActionPolicy("create_draft", "draft", "전송하지 않는 초안을 만듭니다."),
    "send_message": ActionPolicy("send_message", "change", "외부 사용자에게 메시지를 전송합니다."),
    "make_payment": ActionPolicy("make_payment", "forbidden", "교육 과정에서 결제를 금지합니다."),
}


def classify_action(action_name: str) -> dict:
    policy = POLICIES.get(action_name)
    if policy is None:
        return {"action": action_name, "risk": "unknown", "next": "block"}
    next_step = {
        "read": "allow",
        "draft": "allow",
        "change": "request_approval",
        "forbidden": "block",
    }[policy.risk]
    return {"action": policy.name, "risk": policy.risk, "next": next_step}


if __name__ == "__main__":
    for name in ("search_policy", "create_draft", "send_message", "make_payment", "unknown_tool"):
        print(classify_action(name))
