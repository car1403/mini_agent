"""Role, Instruction, Context, Constraint를 나누어 Prompt를 조립합니다."""


def build_prompt(role: str, instruction: str, context: str, constraint: str) -> str:
    return (
        f"[Role]\n{role}\n\n[Instruction]\n{instruction}\n\n"
        f"[Context]\n{context}\n\n[Constraint]\n{constraint}"
    )


if __name__ == "__main__":
    print(build_prompt(
        "당신은 초보자를 돕는 여행 요청 분석가입니다.",
        "사용자의 여행 요청에서 필요한 정보를 추출하세요.",
        "사용자는 국내 여행을 계획하고 있습니다.",
        "추측하지 말고, 모르는 값은 missing_fields에 넣으세요.",
    ))
