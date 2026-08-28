"""PDF 유사도 검색 결과를 Context로 사용해 Ollama 답변을 생성합니다."""

import os

import httpx

from _pgvector_store import OLLAMA_BASE_URL, similarity_search


COLLECTION = "rag_pdf_lesson"
CHAT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
QUESTION = "당일 취소 규정은 어떻게 되나요?"
TOP_K = 3


def answer_pdf_question(question: str) -> dict:
    results = similarity_search(
        question,
        collection=COLLECTION,
        top_k=TOP_K,
    )
    if not results:
        return {
            "answer": "PDF에서 질문과 관련된 근거를 찾지 못했습니다.",
            "sources": [],
            "results": [],
        }

    context = "\n".join(
        f"[{item['source']} p.{item['metadata'].get('page_number', '?')}] "
        f"{item['content']}"
        for item in results
    )
    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": CHAT_MODEL,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "제공된 PDF Context만 사용해 한국어로 답하세요. "
                        "근거가 부족하면 모른다고 답하고 출처 페이지를 표시하세요."
                    ),
                },
                {
                    "role": "user",
                    "content": f"질문: {question}\n\nPDF Context:\n{context}",
                },
            ],
        },
        timeout=120,
    )
    response.raise_for_status()
    answer = response.json()["message"]["content"]
    sources = sorted({
        f"{item['source']} p.{item['metadata'].get('page_number', '?')}"
        for item in results
    })
    return {"answer": answer, "sources": sources, "results": results}


if __name__ == "__main__":
    result = answer_pdf_question(QUESTION)
    print(f"질문: {QUESTION}\n")
    print(f"답변: {result['answer']}")
    print(f"출처: {', '.join(result['sources']) or '없음'}")
