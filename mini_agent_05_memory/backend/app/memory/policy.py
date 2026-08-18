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


def validate_memory_key(key: str) -> None:
    if key in SENSITIVE_MEMORY_KEYS:
        raise ValueError("민감정보는 Memory에 저장할 수 없습니다.")
    if key not in ALLOWED_MEMORY_KEYS:
        raise ValueError("허용되지 않은 Memory 항목입니다.")
