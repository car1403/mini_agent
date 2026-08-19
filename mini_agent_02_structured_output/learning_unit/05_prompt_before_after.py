"""모호한 Prompt와 개선된 Prompt를 비교합니다."""

import httpx
from _llm_backend import generate_text, print_connection_help, print_result


MEETING = "민수는 금요일까지 API를 완성한다. 지연은 다음 주 시안을 공유한다. 배포일은 아직 정하지 않았다."
BEFORE = "회의 내용을 정리해 주세요."
AFTER = """[Role] 회의 기록 담당자
[Instruction] 결정 사항과 담당자별 할 일을 분리하세요.
[Context] 배포 준비 회의입니다.
[Constraint] 미확정 내용은 결정 사항에서 제외하세요.
[Output Format] 두 개의 Markdown 목록"""


if __name__ == "__main__":
    try:
        print_result("Before", generate_text(BEFORE, MEETING))
        print_result("After", generate_text(AFTER, MEETING))
    except httpx.HTTPError as error:
        print_connection_help(error)
