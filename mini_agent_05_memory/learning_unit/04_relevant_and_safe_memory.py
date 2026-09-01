"""04. 민감정보를 거부하고 질문에 관련된 Memory만 답변에 사용합니다.

학습 목표:
- Allowlist에 포함된 Memory key만 저장합니다.
- 질문과 관련된 Memory만 골라 Prompt에 전달합니다.
- 비밀번호나 여권번호 같은 민감정보의 저장을 차단합니다.

실행: python .\04_relevant_and_safe_memory.py
외부 서비스: 필요 없음
"""

SENSITIVE_KEYS = {"card_number", "password", "passport_number"}
ALLOWED_KEYS = {"transportation", "food_restriction", "hotel_preference"}


class TravelMemory:
    def __init__(self) -> None:
        self._users: dict[str, dict[str, str]] = {}

    def save(self, user_id: str, key: str, value: str) -> None:
        """수업에서 허용한 key만 사용자별로 저장합니다."""
        if key in SENSITIVE_KEYS or key not in ALLOWED_KEYS:
            raise ValueError("저장하도록 허용되지 않은 Memory 항목입니다.")
        self._users.setdefault(user_id, {})[key] = value

    def relevant(self, user_id: str, question: str) -> dict[str, str]:
        """질문의 주제와 관련된 Memory만 선택합니다."""
        keys = []
        if any(word in question for word in ("이동", "교통", "경로")):
            keys.append("transportation")
        if any(word in question for word in ("음식", "식당", "먹")):
            keys.append("food_restriction")
        if any(word in question for word in ("호텔", "숙소")):
            keys.append("hotel_preference")
        user_memory = self._users.get(user_id, {})
        return {key: user_memory[key] for key in keys if key in user_memory}


def personalized_answer(question: str, memories: dict[str, str]) -> str:
    if not memories:
        return "이 질문에 사용할 사용자 Memory가 없습니다."
    facts = ", ".join(f"{key}={value}" for key, value in memories.items())
    return f"사용자 선호({facts})를 반영해 답변합니다: {question}"


if __name__ == "__main__":
    memory = TravelMemory()
    print("[04] 관련 있고 안전한 Memory\n")
    memory.save("student-01", "transportation", "대중교통")
    memory.save("student-01", "food_restriction", "해산물 알레르기")
    memory.save("student-01", "hotel_preference", "조용한 호텔")

    question = "부산에서 식당을 추천해줘"
    selected = memory.relevant("student-01", question)
    print("질문:", question)
    print("선택한 Memory:", selected)
    print("최종 답변:", personalized_answer(question, selected))

    try:
        memory.save("student-01", "passport_number", "M12345678")
    except ValueError as error:
        print("민감정보 차단:", error)

    print("\n핵심: 저장 가능한 정보인지 확인하고, 답변에 필요한 Memory만 사용합니다.")
