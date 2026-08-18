from retrieval import search


def answer(question: str) -> dict:
    """TODO: 검색 결과가 없으면 grounded=False, 있으면 답변과 출처를 반환하세요."""
    raise NotImplementedError


if __name__ == "__main__":
    print(answer("수하물은 몇 kg인가요?"))
    print(answer("여권을 잃어버렸어요."))
