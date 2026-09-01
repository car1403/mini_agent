import re


ALLOWED_MEMORY_KEYS = {
    "transportation",
    "food_restriction",
    "hotel_preference",
}

SENSITIVE_MEMORY_KEYS = {
    "password",
    "card_number",
    "passport_number",
    "resident_registration_number",
    "api_key",
    "access_token",
}

SENSITIVE_VALUE_PATTERNS = (
    re.compile(r"(?i)(password|passwd|api[_ -]?key|access[_ -]?token|비밀번호|인증번호)\s*[:=]?\s*\S+"),
    re.compile(r"(?<!\d)(?:\d[ -]?){15,16}(?!\d)"),
    re.compile(r"(?<!\d)\d{6}\s?-\s?\d{7}(?!\d)"),
    re.compile(r"(?i)(?:passport|여권번호)\s*[:=]?\s*[A-Z0-9-]{6,20}"),
)


def validate_memory_key(key: str) -> None:
    if key in SENSITIVE_MEMORY_KEYS:
        raise ValueError("민감정보는 Memory에 저장할 수 없습니다.")
    if key not in ALLOWED_MEMORY_KEYS:
        raise ValueError("허용되지 않은 Memory 항목입니다.")


def validate_memory_value(value: str) -> None:
    """명백한 인증정보와 식별번호를 차단하는 교육용 최소 방어선입니다."""
    if any(pattern.search(value) for pattern in SENSITIVE_VALUE_PATTERNS):
        raise ValueError("Memory 값에 저장할 수 없는 민감정보가 포함되어 있습니다.")


def validate_memory(key: str, value: str) -> None:
    validate_memory_key(key)
    validate_memory_value(value)
