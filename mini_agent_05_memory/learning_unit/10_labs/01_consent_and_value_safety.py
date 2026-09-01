"""명시적 동의와 Memory key/value 안전 검증을 연습하는 독립 Lab."""

import re
from dataclasses import dataclass


ALLOWED_KEYS = {"transportation", "food_restriction", "hotel_preference"}
SENSITIVE_PATTERNS = (
    re.compile(r"(?i)(password|api[_ -]?key|비밀번호)\s*[:=]?\s*\S+"),
    re.compile(r"(?<!\d)(?:\d[ -]?){15,16}(?!\d)"),
)


@dataclass(frozen=True)
class SaveDecision:
    allowed: bool
    reason: str


def decide_save(*, key: str, value: str, consent: bool) -> SaveDecision:
    if not consent:
        return SaveDecision(False, "consent_required")
    if key not in ALLOWED_KEYS:
        return SaveDecision(False, "key_not_allowed")
    if any(pattern.search(value) for pattern in SENSITIVE_PATTERNS):
        return SaveDecision(False, "sensitive_value")
    return SaveDecision(True, "approved")


if __name__ == "__main__":
    cases = [
        {"key": "transportation", "value": "대중교통", "consent": True},
        {"key": "hotel_preference", "value": "조용한 객실", "consent": False},
        {"key": "hotel_preference", "value": "카드 1234-5678-9012-3456", "consent": True},
    ]
    for case in cases:
        print(case, "→", decide_save(**case))
