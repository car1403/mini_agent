def load_context(state: dict) -> dict:
    return {
        **state,
        "memories": [{"key": "transport", "value": "대중교통"}],
        "documents": [{"title": "숙소 환불 규정"}],
    }


print(load_context({"destination": "부산"}))
