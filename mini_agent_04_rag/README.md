# Mini Agent 04 · RAG

Mini Agent 03의 메뉴와 구조를 그대로 유지하면서 문서 검색과 근거 기반 답변을 추가한 누적형 완성본입니다.

```text
Streamlit app_pages
  → clients/agent_client.py
  → FastAPI routers
  → rag/service.py
  → keyword 또는 Ollama + pgvector
```

## 새로 추가된 메뉴

1. RAG 흐름
2. 문서와 Chunk
3. 문서 검색
4. 근거 기반 답변
5. Ollama + pgvector

`keyword + mock`은 Docker와 API Key 없이 실행됩니다. 여기서 RAG의 전체 흐름을 확인한 다음 `pgvector + Ollama`로 검색 구현을 교체합니다.

## 실행 1: Mock RAG

```powershell
cd C:\mini_agent_st\mini_agent_04_rag
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

cd backend
uvicorn app.main:app --reload --port 8000
```

새 터미널에서 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag
.\.venv\Scripts\Activate.ps1
streamlit run .\frontend\app.py
```

## 실행 2: 실제 pgvector RAG

```powershell
cd C:\mini_agent_st\infra
Copy-Item .env.example .env
docker compose up -d
docker exec mini-agent-ollama ollama pull embeddinggemma
```

Streamlit의 `pgvector 실습` 메뉴에서 연결 상태를 확인하고 `교육용 문서 색인`을 누릅니다.

> 기존 PostgreSQL Volume에는 새 `documents` 테이블이 자동 생성되지 않을 수 있습니다. 이 경우 [공용 인프라 안내](../infra/README.md)의 기존 Volume 주의를 확인합니다.

## 안전 범위

- 제공 Tool은 이전 단계와 동일한 조회용 Mock Tool입니다.
- RAG 색인 초기화는 `mini_agent_travel` collection만 대상으로 합니다.
- 전체 DB나 다른 단계의 문서는 삭제하지 않습니다.
- 근거 문서가 없으면 Mock RAG는 답변하지 않습니다.

## 학생용과 완성본

- `starter`: 핵심 함수를 학생이 작성합니다.
- `learning_unit`: 작은 단위 예제를 순서대로 실행합니다.
- `backend`, `frontend`: 시간이 부족할 때 바로 시연하는 완성본입니다.
- `solution`: 정답 코드 위치와 해설 순서를 안내합니다.
