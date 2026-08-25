from app.schemas import RagChunk


def split_document(
    text: str,
    *,
    source: str,
    title: str,
    sentences_per_chunk: int = 2,
) -> list[RagChunk]:
    sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
    chunks = []
    for start in range(0, len(sentences), sentences_per_chunk):
        index = len(chunks)
        chunk_text = ". ".join(sentences[start : start + sentences_per_chunk]) + "."
        chunks.append(
            RagChunk(
                chunk_id=f"{source}:{index}",
                text=chunk_text,
                source=source,
                title=title,
                chunk_index=index,
            )
        )
    return chunks
