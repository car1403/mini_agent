"""텍스트형 PDF를 Chunk로 나누어 pgvector에 저장합니다."""

import hashlib
import re
from pathlib import Path

from pypdf import PdfReader

from _pgvector_store import delete_collection, upsert_text


COLLECTION = "rag_pdf_lesson"
PDF_PATH = Path(__file__).resolve().parent / "travel-policy.pdf"
CHUNK_SIZE = 500
OVERLAP = 80


def split_text(text: str) -> list[str]:
    """PDF 페이지의 텍스트를 overlap이 있는 작은 Chunk로 나눕니다."""
    normalized = re.sub(r"[ \t]+", " ", text).strip()
    if not normalized:
        return []

    step = CHUNK_SIZE - OVERLAP
    return [
        normalized[start:start + CHUNK_SIZE]
        for start in range(0, len(normalized), step)
    ]


def index_pdf(pdf_path: Path) -> int:
    """기존 PDF 실습 Collection을 비우고 PDF Chunk를 저장합니다."""
    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")

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
            print(
                f"저장: chunk={total}, page={page_number}, "
                f"characters={len(content)}"
            )
            total += 1

    if total == 0:
        raise ValueError(
            "텍스트를 추출하지 못했습니다. 스캔 PDF는 OCR 처리가 필요합니다."
        )
    return total


if __name__ == "__main__":
    count = index_pdf(PDF_PATH)
    print(f"\n색인 완료: {PDF_PATH.name}, {count} chunks")
    print(f"Collection: {COLLECTION}")
