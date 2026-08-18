"""TODO 3: Allowlist를 확인한 뒤에만 Tool을 실행하세요."""


def get_weather(arguments: dict) -> dict:
    return {"city": arguments["city"], "condition": "맑음", "source": "mock"}


TOOLS = {"get_weather": get_weather}


def run_tool(name: str, arguments: dict) -> dict:
    # TODO: name이 TOOLS에 없으면 차단하고, 있으면 함수를 실행하세요.
    raise NotImplementedError
