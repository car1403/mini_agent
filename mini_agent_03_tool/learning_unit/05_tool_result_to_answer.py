"""Tool Result를 사용자가 읽을 수 있는 최종 답변으로 변환합니다."""

from datetime import date


def select_tool(message: str) -> dict:
    if "날씨" in message:
        return {"tool_name": "get_weather", "arguments": {"city": "부산", "target_date": date.today().isoformat()}}
    return {"tool_name": None, "arguments": {}}


def run_tool(tool_call: dict) -> dict:
    if tool_call["tool_name"] != "get_weather":
        return {"success": False, "error": {"code": "TOOL_NOT_ALLOWED"}}
    return {"success": True, "data": {"city": tool_call["arguments"]["city"], "condition": "맑음", "temperature_c": 26}}


def make_final_answer(question: str, tool_result: dict) -> str:
    if not tool_result["success"]:
        return "요청을 처리하지 못했습니다. 입력을 확인해 주세요."
    data = tool_result["data"]
    return f"{data['city']}의 교육용 날씨는 {data['condition']}, 기온은 {data['temperature_c']}도입니다."


def agent_loop(question: str) -> dict:
    tool_call = select_tool(question)
    if tool_call["tool_name"] is None:
        return {"question": question, "tool_call": tool_call, "tool_result": None, "final_answer": "이 질문에는 Tool이 필요하지 않습니다."}
    tool_result = run_tool(tool_call)
    return {"question": question, "tool_call": tool_call, "tool_result": tool_result, "final_answer": make_final_answer(question, tool_result)}


if __name__ == "__main__":
    result = agent_loop("부산 날씨를 알려줘")
    for step, value in result.items():
        print(step, "→", value)
