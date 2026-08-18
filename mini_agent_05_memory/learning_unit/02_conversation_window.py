"""전체 대화 대신 최근 메시지와 간단한 요약만 Prompt에 넣습니다."""

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
        return [asdict(message) for message in self.messages[-self.max_recent_messages :]]

    def older_summary(self) -> str:
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

    print("전체 메시지 수:", len(window.messages))
    print("오래된 대화 요약:", window.older_summary())
    print("최근 메시지:", window.recent())
