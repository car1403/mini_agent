# Mini Agent 04 · RAG

Mini Agent 03의 메뉴와 구조를 그대로 유지하면서 문서 검색과 근거 기반 답변을 추가한 누적형 완성본입니다.

## Backend 공통 구조

`core`, `providers`, `routers`, `schemas`, `services`, `agents`, `tools`는 Mini Agent 03과 같은 책임을 유지합니다. 04에서는 `rag/`만 과정 전용 계층으로 추가됩니다. Router와 Schema는 Stage 01~03 및 `rag`로 분리되고, Tool은 `registry.py`와 `executor.py`의 단일 등록·실행 경로를 사용합니다.

```text
Streamlit app_pages
  → clients/agent_client.py
  → FastAPI routers
  → rag/service.py
  → keyword 또는 Ollama + pgvector
  → Redis TTL 답변 Cache
```

## 새로 추가된 메뉴

1. RAG 흐름
2. 문서와 Chunk
3. 문서 검색
4. 근거 기반 답변
5. Ollama + pgvector + Redis
6. 직접 입력 문장과 PDF 색인
7. Metadata Filter와 Hybrid Search
8. RAG Agent 검색 Tool
9. RAG Labs 01~02 통합 실습
10. RAG Labs 03~05 상품·ACL·PDF 실습
11. RAG Labs 06~07 검색 평가·Multi-Tool Agent

`keyword + mock`은 Docker와 API Key 없이 실행됩니다. 실제 구성에서는 pgvector가 Chunk와 Embedding을 영구 저장하고 Redis가 동일 조건의 답변을 TTL 동안 Cache합니다.

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
docker exec mini-agent-ollama ollama pull llama3.2
.\check_rag_prerequisites.ps1
```

사전점검은 Docker CLI, Ollama·PostgreSQL/pgvector·Redis 연결과 필수 Ollama 모델을
한 번에 확인합니다. 모든 항목이 `PASS`인 상태에서 실제 인프라 Lab을 진행합니다.

전체 Lab의 실제 인프라 E2E Test는 다음 명령으로 실행합니다. Test 데이터는 `e2e-` Source와
교육용 Lab Source만 사용하며 전체 Collection이나 기존 사용자 문서를 초기화하지 않습니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag
.\run_rag_e2e.ps1
```

Cache MISS→HIT, Source 교체, 상품 조건, ACL, PDF 재색인, 검색 평가, Multi-Tool
재질문과 Redis 상태 유지를 순서대로 검증합니다.

Streamlit의 `pgvector 실습` 메뉴에서 연결 상태를 확인하고 `교육용 문서 색인`을 누릅니다.

`근거 기반 답변`에서 Redis Cache를 켜고 같은 질문을 두 번 실행하면 MISS→HIT와 남은 TTL, 전체 Trace를 확인할 수 있습니다. 문서를 재색인하면 Mini Agent RAG 전용 Cache가 무효화됩니다.

`텍스트·PDF 색인`에서는 직접 작성한 정책과 텍스트형 PDF를 등록합니다. PDF 검색 결과는
페이지 번호를 Metadata로 유지하며 스캔 PDF는 별도 OCR이 필요합니다. `Metadata·Hybrid`
메뉴는 활성 문서 Filter, 요청별 유사도 임계값, 키워드와 pgvector 순위를 결합한 RRF를
비교합니다. `RAG Agent Tool`은 DB나 임의 SQL 대신 제한된 `search_knowledge_base`
계약만 사용합니다.

`RAG Labs 01~02`에서는 고객지원 질문의 실제 Tool 선택·pgvector 결과와 Redis
MISS→HIT를 한 화면에서 비교합니다. 정책 갱신 실습은 동일 Source의 version 1·2를
교체하고 `/api/rag/indexed` 관찰 API로 실제 저장 Chunk와 문서 Version을 확인합니다.

`RAG Labs 03~05`에서는 상품 Catalog의 Metadata·최대 가격·Hybrid Search, 인증 역할별
사내 규정 ACL, PDF 페이지 출처와 재색인을 다룹니다. ACL 역할은 Agent arguments나 JSON
Body가 아니라 교육용 `X-Demo-Role` Header에서 가져옵니다. 실제 서비스에서는 이 Header를
클라이언트가 직접 정하게 하지 않고 인증 Middleware가 확인한 사용자 세션으로 대체합니다.

`RAG Labs 06~07`에서는 정답 문서 ID가 포함된 평가 Dataset으로 Keyword·pgvector·Hybrid의
Hit@K와 MRR을 계산합니다. Multi-Tool Agent는 Redis TTL 상태에 이전 Cycle의 주제와 단계
수를 저장하고, 재질문 후 호텔·항공·관광 전용 Tool을 Backend Allowlist로 실행합니다.
`MAX_STEPS=4`를 넘으면 추가 검색을 중단하며 화면에서 전체 상태·Tool·종료 Trace를 확인합니다.

문서를 교체할 때는 모든 Chunk Embedding을 먼저 완료합니다. 그다음 PostgreSQL의 한
Transaction 안에서 이전 Source 정리와 새 Chunk Upsert를 수행하고, Commit이 성공한
후에만 `mini-agent:rag-answer:` Redis Namespace를 무효화합니다. Embedding이나 DB 저장이
실패하면 기존 문서와 기존 Cache를 유지합니다.

> 기존 PostgreSQL Volume에는 새 `documents` 테이블이 자동 생성되지 않을 수 있습니다. 이 경우 [공용 인프라 안내](../infra/README.md)의 기존 Volume 주의를 확인합니다.

## 안전 범위

- 기존 여행 Tool은 조회용 Mock이며, RAG Agent에는 읽기 전용 지식검색 Tool만 제공합니다.
- Agent에 DB 연결 정보나 임의 SQL 실행 권한을 제공하지 않습니다.
- RAG 색인 초기화는 `mini_agent_travel` collection만 대상으로 합니다.
- 전체 DB나 다른 단계의 문서는 삭제하지 않습니다.
- 근거 문서가 없으면 Mock RAG는 답변하지 않습니다.

## 학생용과 완성본

- `starter`: 핵심 함수를 학생이 작성합니다.
- `learning_unit`: 개념 예제 01~15와 Redis·pgvector 기반 독립 Lab 01~07을 순서대로 실행합니다.
- `backend`, `frontend`: 시간이 부족할 때 바로 시연하는 완성본입니다.
- `solution`: 정답 코드 위치와 해설 순서를 안내합니다.
