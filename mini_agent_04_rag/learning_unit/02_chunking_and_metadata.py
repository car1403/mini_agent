"""긴 문서를 작은 Chunk로 나누고 출처 정보를 붙입니다."""

from dataclasses import asdict, dataclass


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source: str
    title: str
    chunk_index: int


def split_document(text: str, *, source: str, title: str, sentences_per_chunk: int = 2) -> list[Chunk]:
    sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
    chunks = []
    for start in range(0, len(sentences), sentences_per_chunk):
        index = len(chunks)
        chunk_text = ". ".join(sentences[start : start + sentences_per_chunk]) + "."
        chunks.append(Chunk(f"{source}:{index}", chunk_text, source, title, index))
    return chunks


if __name__ == "__main__":
    policy = (
        "체크인 3일 전까지 취소하면 전액 환불합니다. "
        "체크인 2일 전에는 숙박 요금의 50%를 환불합니다. "
        "체크인 당일에는 환불하지 않습니다. "
        "예약 변경은 고객센터에서 처리합니다."
    )
    for chunk in split_document(policy, source="hotel-refund.md", title="호텔 환불 정책"):
        print(asdict(chunk))
