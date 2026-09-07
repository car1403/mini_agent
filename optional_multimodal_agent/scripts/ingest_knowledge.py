"""실행: python -m scripts.ingest_knowledge (로컬 Ollama embeddinggemma 사용)"""
import asyncio
import sys
from pathlib import Path

# `python scripts/ingest_knowledge.py` 실행도 지원합니다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import psycopg
from shared.config import ROOT, DATABASE_URL
from mcp_server.rag.embeddings import embed, vector_literal, MODEL, DIMENSIONS

RAG_DIRECTORY = ROOT / "data" / "rag"

def chunks(text):
    result = []
    for section in text.split("\n## "):
        title = section.splitlines()[0].lstrip("# ")
        for offset in range(0,len(section),1000):
            result.append((title,section[offset:offset+1000]))
    return result

def discover_documents():
    """폴더와 파일 이름만으로 RAG 문서의 연결 대상을 결정합니다."""
    documents = []

    for path in sorted((RAG_DIRECTORY / "products").glob("*.md")):
        documents.append((path, "product", path.stem))

    for path in sorted((RAG_DIRECTORY / "facilities").glob("*.md")):
        if path.stem.startswith("PG-"):
            target_type = "program"
        elif path.stem.startswith("F"):
            target_type = "facility"
        else:
            raise ValueError(f"시설 문서 파일 이름을 확인하세요: {path.name}")
        documents.append((path, target_type, path.stem))

    return documents

async def ingest():
    documents = discover_documents()
    if not documents:
        raise ValueError("data/rag 폴더에 적재할 Markdown 문서가 없습니다.")

    for path, target_type, target_id in documents:
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ")
        source_path = path.relative_to(RAG_DIRECTORY).as_posix()
        parts = chunks(text)
        vectors = await embed([content for _,content in parts])
        # 문서 하나의 교체를 한 트랜잭션으로 확정합니다.
        with psycopg.connect(DATABASE_URL) as conn:
            conn.execute("""INSERT INTO multimodal_knowledge_documents
              (document_id,title,source_path,embedding_model,embedding_dimensions)
              VALUES (%s,%s,%s,%s,%s)
              ON CONFLICT(document_id) DO UPDATE SET title=EXCLUDED.title,
              source_path=EXCLUDED.source_path,
              embedding_model=EXCLUDED.embedding_model,embedding_dimensions=EXCLUDED.embedding_dimensions""",
              (target_id,title,source_path,MODEL,DIMENSIONS))
            conn.execute("DELETE FROM multimodal_knowledge_chunks WHERE document_id=%s",(target_id,))
            for index,((section,content),vector) in enumerate(zip(parts,vectors,strict=True)):
                conn.execute("INSERT INTO multimodal_knowledge_chunks VALUES (%s,%s,%s,%s,%s::vector)",
                             (target_id,index,section,content,vector_literal(vector)))
            for table in ("multimodal_product_documents","multimodal_facility_documents","multimodal_program_documents"):
                from psycopg import sql
                conn.execute(sql.SQL("DELETE FROM {} WHERE document_id=%s").format(sql.Identifier(table)),(target_id,))
            statement = {"product":"INSERT INTO multimodal_product_documents VALUES (%s,%s)",
                         "facility":"INSERT INTO multimodal_facility_documents VALUES (%s,%s)",
                         "program":"INSERT INTO multimodal_program_documents VALUES (%s,%s)"}[target_type]
            conn.execute(statement,(target_id,target_id))
        print("Indexed:",source_path,len(parts),"chunks")

if __name__ == "__main__":
    asyncio.run(ingest())
