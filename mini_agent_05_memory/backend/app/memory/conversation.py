from app.schemas import ConversationMessage, ConversationWindowResult


def make_window(
    messages: list[ConversationMessage],
    max_recent_messages: int,
) -> ConversationWindowResult:
    older = messages[:-max_recent_messages]
    recent = messages[-max_recent_messages:]
    summary = "이전 대화 없음"
    if older:
        summary = " / ".join(message.content for message in older)
    return ConversationWindowResult(
        total_count=len(messages),
        older_summary=summary,
        recent_messages=recent,
    )
