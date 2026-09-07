import asyncio
from mcp_server.rag.embeddings import embed, vector_literal, MODEL
from mcp_server.database.knowledge_queries import search

async def retrieve(kind: str, target_id: str, question: str):
    if not question.strip() or len(question)>2000:
        raise ValueError("검색 질문은 1~2000자입니다.")
    vector = (await embed([question]))[0]
    items = await asyncio.to_thread(search,vector_literal(vector),kind,target_id,MODEL)
    return {"items":items,"source":"rag", "note":"검색 결과의 관련성을 확인하고 근거가 없으면 답변을 추측하지 마세요."}
