"""TODO 1: 네 Prompt 구성 요소를 하나의 문자열로 조립하세요."""


def build_prompt(role: str, instruction: str, context: str, constraint: str) -> str:
    # TODO: [Role], [Instruction], [Context], [Constraint] 제목을 포함해 반환하세요.
    raise NotImplementedError


if __name__ == "__main__":
    print(build_prompt("여행 도우미", "정보를 추출한다", "국내 여행", "추측하지 않는다"))
