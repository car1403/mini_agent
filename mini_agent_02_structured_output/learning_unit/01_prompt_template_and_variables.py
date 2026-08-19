"""Prompt 고정 구조와 업무별 변수를 분리합니다."""

from string import Template


TEMPLATE = Template("""[Role]\n$role\n\n[Instruction]\n$instruction\n\n[Context]\n$context\n\n[Constraint]\n$constraint\n\n[Output Format]\n$output_format""")
TASKS = {
    "고객 문의": {"role": "고객 지원 분류 담당자", "instruction": "유형과 긴급도를 분류하세요.", "context": "담당 팀 배정에 사용됩니다.", "constraint": "추측하지 마세요.", "output_format": "유형, 긴급도, 요약"},
    "회의 요약": {"role": "회의 기록 담당자", "instruction": "결정 사항과 할 일을 구분하세요.", "context": "프로젝트 회의입니다.", "constraint": "미확정 내용을 결정으로 쓰지 마세요.", "output_format": "두 개의 목록"},
}


if __name__ == "__main__":
    for name, values in TASKS.items():
        print(f"\n===== {name} =====\n{TEMPLATE.substitute(values)}")
