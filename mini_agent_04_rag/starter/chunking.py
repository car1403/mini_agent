def split_document(text: str, sentences_per_chunk: int = 2) -> list[str]:
    """TODO: 마침표로 문장을 나누고 지정한 개수씩 묶어 반환하세요."""
    raise NotImplementedError


if __name__ == "__main__":
    document = "첫 문장입니다. 두 번째 문장입니다. 세 번째 문장입니다."
    print(split_document(document))
