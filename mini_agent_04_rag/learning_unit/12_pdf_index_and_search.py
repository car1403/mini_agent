"""텍스트형 PDF를 페이지별 Chunk로 나누어 pgvector에 색인하고 검색합니다."""

import argparse
import hashlib
import re
from pathlib import Path

from pypdf import PdfReader

from _pgvector_store import delete_collection, similarity_search, upsert_text


COLLECTION = "rag_pdf_lesson"


def split_text(text: str, *, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    """문단 경계를 우선 사용하고 긴 문단은 글자 수 기준 overlap으로 나눕니다."""
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap은 0 이상 chunk_size 미만이어야 합니다.")
    normalized = re.sub(r"[ \t]+", " ", text).strip()
    if not normalized:
        return []
    chunks = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = max(normalized.rfind("\n", start, end), normalized.rfind(". ", start, end))
            if boundary > start + chunk_size // 2:
                end = boundary + 1
        chunks.append(normalized[start:end].strip())
        if end == len(normalized):
            break
        start = end - overlap
    return [chunk for chunk in chunks if chunk]


def index_pdf(pdf_path: Path, *, reset_collection: bool = True) -> int:
    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
    if reset_collection:
        delete_collection(COLLECTION)

    file_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    reader = PdfReader(pdf_path)
    total = 0
    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        for page_chunk_index, content in enumerate(split_text(page_text)):
            upsert_text(
                collection=COLLECTION,
                title=pdf_path.stem,
                content=content,
                source=pdf_path.name,
                chunk_index=total,
                metadata={
                    "input_type": "pdf",
                    "page_number": page_number,
                    "page_chunk_index": page_chunk_index,
                    "file_sha256": file_hash,
                },
            )
            total += 1
    if total == 0:
        raise ValueError("텍스트를 추출하지 못했습니다. 스캔 PDF는 OCR 처리가 필요합니다.")
    return total


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PDF를 pgvector에 색인하고 의미 검색합니다.")
    parser.add_argument("pdf", type=Path, help="색인할 텍스트형 PDF 경로")
    parser.add_argument("--query", default="환불 규정은 어떻게 되나요?")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--score-threshold", type=float)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    count = index_pdf(args.pdf)
    print(f"색인 완료: {args.pdf.name}, {count} chunks")
    for item in similarity_search(
        args.query,
        collection=COLLECTION,
        top_k=args.top_k,
        score_threshold=args.score_threshold,
    ):
        page = item["metadata"].get("page_number", "?")
        print(f"{item['score']:.3f} | {item['source']} p.{page} | {item['content']}")
