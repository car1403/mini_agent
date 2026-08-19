"""TODO 1: Prompt 구성 요소와 출력 형식을 하나의 문자열로 조립하세요."""


def build_prompt(
    role: str,
    instruction: str,
    context: str,
    constraint: str,
    output_format: str = "",
) -> str:
    # TODO: 네 제목을 조립하고 output_format이 있으면 [Output Format]도 추가하세요.
    raise NotImplementedError


if __name__ == "__main__":
    print(build_prompt(
        "여행 도우미",
        "정보를 추출한다",
        "국내 여행",
        "추측하지 않는다",
        "추출 정보와 누락 정보 목록",
    ))
