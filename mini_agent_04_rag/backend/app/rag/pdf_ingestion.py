"""텍스트형 PDF를 페이지 출처를 보존한 Chunk로 변환합니다."""

from hashlib import sha256
from io import BytesIO
import re

from pypdf import PdfReader

from app.schemas import RagChunk


def _split_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
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


def pdf_to_chunks(content: bytes, *, source: str, title: str) -> list[RagChunk]:
    digest = sha256(content).hexdigest()
    reader = PdfReader(BytesIO(content))
    chunks = []
    for page_number, page in enumerate(reader.pages, start=1):
        for page_chunk_index, text in enumerate(_split_text(page.extract_text() or "")):
            index = len(chunks)
            chunks.append(RagChunk(
                chunk_id=f"{source}:{index}",
                text=text,
                source=source,
                title=title,
                chunk_index=index,
                metadata={
                    "input_type": "pdf",
                    "source_id": source,
                    "page_number": page_number,
                    "page_chunk_index": page_chunk_index,
                    "file_sha256": digest,
                },
            ))
    if not chunks:
        raise ValueError("PDF에서 텍스트를 추출하지 못했습니다. 스캔 PDF는 OCR이 필요합니다.")
    return chunks
