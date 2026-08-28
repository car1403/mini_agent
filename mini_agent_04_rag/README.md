# Mini Agent 04 · Simple RAG

문서를 Chunk로 나누고, 관련 문서를 검색한 뒤, 그 근거로 답변하는 과정을 배우는
초보자용 RAG 프로젝트입니다. 이전 LLM·Prompt·Tool 과정과 별도 Labs는 포함하지
않습니다.

```text
문서 → Chunk → Embedding → pgvector 검색 → Context → Ollama 답변
                                      └→ 동일 질문은 Redis Cache
```

## 화면 순서

1. Chunk와 키워드 검색
2. pgvector 의미 검색
3. 근거 기반 답변
4. PDF RAG
5. Cache와 검색 조건

`keyword` 검색과 Mock 답변은 Docker 없이 실행할 수 있습니다. `pgvector`, Ollama,
PDF 색인, Redis Cache는 공용 Docker 환경이 필요합니다.

## 설치

```powershell
cd C:\mini_agent_st\mini_agent_04_rag
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Backend 실행

```powershell
cd C:\mini_agent_st\mini_agent_04_rag\backend
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

API 문서: `http://127.0.0.1:8000/docs`

## Frontend 실행

새 터미널에서 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag
.\.venv\Scripts\Activate.ps1
streamlit run .\frontend\app.py
```

화면: `http://127.0.0.1:8501`

## 실제 RAG 환경

```powershell
cd C:\mini_agent_st\infra
docker compose up -d
docker exec mini-agent-ollama ollama pull embeddinggemma
docker exec mini-agent-ollama ollama pull llama3.2
```

Frontend의 `pgvector 의미 검색`에서 `교육 문서 저장`을 먼저 실행한 뒤 의미 검색과
Ollama 답변을 확인합니다.

## 독립 Python 예제

`learning_unit`에는 `C:\aidevs\05_llm-agent-orchestration\04_rag`의 01~15 예제만
유지합니다. `10_labs`와 `20_assignments`는 이 프로젝트 범위에서 제외했습니다.

PDF 단계는 다음처럼 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag\learning_unit
python .\12_01_pdf_chunk.py
python .\12_02_pdf_rag.py
python .\12_03_pdf_rag_ollama.py
python .\12_04_pdf_rag_cache.py
```

## stdio MCP RAG Agent

기본 RAG를 이해한 다음에는 같은 pgvector 검색을 MCP Tool로 제공할 수 있습니다.
Redis Cache 없이 `Agent → stdio MCP Server → pgvector → Agent 답변` 흐름만 확인합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag
.\.venv\Scripts\Activate.ps1
python .\mcp_rag_example\rag_agent.py
```

자세한 설명은 [`mcp_rag_example/README.md`](mcp_rag_example/README.md)를 확인합니다.

## 테스트

```powershell
cd C:\mini_agent_st\mini_agent_04_rag\backend
python -m pytest tests -q
```
