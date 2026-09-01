"""02. 전체 대화 대신 최근 메시지와 간단한 요약만 Prompt에 넣습니다.

학습 목표:
- 대화가 길어질 때 모든 메시지를 Prompt에 넣지 않는 이유를 이해합니다.
- 오래된 대화의 요약과 최근 메시지 Window를 구분합니다.

실행: python .\02_conversation_window.py
외부 서비스: 필요 없음
"""

from dataclasses import asdict, dataclass


@dataclass
class Message:
    role: str
    content: str


class ConversationWindow:
    def __init__(self, max_recent_messages: int = 4) -> None:
        self.max_recent_messages = max_recent_messages
        self.messages: list[Message] = []

    def add(self, role: str, content: str) -> None:
        self.messages.append(Message(role, content))

    def recent(self) -> list[dict]:
        """가장 최근 메시지를 설정한 개수만큼 반환합니다."""
        return [asdict(message) for message in self.messages[-self.max_recent_messages :]]

    def older_summary(self) -> str:
        """최근 Window에서 밀려난 메시지를 수업용 문자열로 요약합니다."""
        older = self.messages[: -self.max_recent_messages]
        if not older:
            return "이전 대화 없음"
        return " / ".join(message.content for message in older)


if __name__ == "__main__":
    window = ConversationWindow(max_recent_messages=3)
    window.add("user", "부산으로 여행 갈 거예요.")
    window.add("assistant", "며칠 일정인가요?")
    window.add("user", "2박 3일이에요.")
    window.add("assistant", "교통수단 선호가 있나요?")
    window.add("user", "대중교통을 이용하고 싶어요.")

    print("[02] 대화 Window\n")
    print("전체 메시지 수:", len(window.messages))
    print("Prompt에 유지할 최근 메시지 수:", window.max_recent_messages)
    print("\n오래된 대화 요약:", window.older_summary())
    print("\n최근 메시지:")
    for message in window.recent():
        print(f"- {message['role']}: {message['content']}")
    print("\n핵심: Prompt에는 오래된 대화의 요약과 최근 메시지만 전달할 수 있습니다.")
