def recent_messages(messages: list[dict], limit: int) -> list[dict]:
    """TODO: 마지막 limit개의 메시지만 반환하세요."""
    raise NotImplementedError


if __name__ == "__main__":
    sample = [{"role": "user", "content": str(index)} for index in range(5)]
    print(recent_messages(sample, 2))
