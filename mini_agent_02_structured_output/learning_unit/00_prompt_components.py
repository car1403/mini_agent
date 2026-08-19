"""서로 다른 업무의 Prompt를 네 구성 요소로 나누어 조립합니다."""

from typing import TypedDict


class PromptExample(TypedDict):
    role: str
    instruction: str
    context: str
    constraint: str


EXAMPLES: dict[str, PromptExample] = {
    "여행 요청 분석": {
        "role": "당신은 초보자를 돕는 여행 요청 분석가입니다.",
        "instruction": "사용자의 여행 요청에서 필요한 정보를 추출하세요.",
        "context": "사용자는 국내 여행을 계획하고 있습니다.",
        "constraint": "추측하지 말고, 모르는 값은 missing_fields에 넣으세요.",
    },
    "고객 문의 분류": {
        "role": "당신은 온라인 쇼핑몰 고객 지원 분류 담당자입니다.",
        "instruction": "문의를 유형과 긴급도로 분류하고 핵심 내용을 요약하세요.",
        "context": "분류 결과는 담당 팀을 자동 배정하는 데 사용됩니다.",
        "constraint": "고객의 감정만으로 긴급도를 높이지 말고 근거를 한 문장으로 쓰세요.",
    },
    "회의 내용 요약": {
        "role": "당신은 프로젝트 회의 기록 정리자입니다.",
        "instruction": "결정 사항과 담당자별 할 일을 구분해 정리하세요.",
        "context": "회의에는 개발자, 디자이너, 운영 담당자가 참여했습니다.",
        "constraint": "회의에서 확정되지 않은 내용은 결정 사항에 포함하지 마세요.",
    },
}


def build_prompt(role: str, instruction: str, context: str, constraint: str) -> str:
    return (
        f"[Role]\n{role}\n\n[Instruction]\n{instruction}\n\n"
        f"[Context]\n{context}\n\n[Constraint]\n{constraint}"
    )


if __name__ == "__main__":
    for name, components in EXAMPLES.items():
        print(f"\n===== {name} =====")
        print(build_prompt(**components))
