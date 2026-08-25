# 04 RAG 실습

## 독립 Lab 구성

모든 Lab은 실제 pgvector를 사용합니다. Redis가 필요한 Lab은 실제 TTL Cache와
Namespace 무효화를 사용하며, Agent에게 DB·SQL·Redis 명령을 직접 제공하지 않습니다.

| Lab | 시나리오 | 핵심 학습 |
|---:|---|---|
| 01 | 고객지원 정책 Agent | Tool Call, pgvector 검색, Redis Cache |
| 02 | 정책 문서 갱신 | 재색인, 오래된 Chunk 제거, Cache 무효화 |
| 03 | 쇼핑몰 상품 검색 | Metadata Filter, 가격·카테고리 조건, Hybrid Search |
| 04 | 사내 규정 문서 | 사용자 권한별 문서 검색, ACL Filter |
| 05 | PDF 여행 가이드 | PDF Chunking, 페이지 출처, 중복 색인 방지 |
| 06 | 검색 품질 평가 | Hit@K, MRR, Keyword·Vector·Hybrid 비교 |
| 07 | Multi-Tool RAG Agent | 재질문, 여러 지식 저장소 선택, 종료 조건 |

## 독립 Lab 1. 고객지원 RAG Agent

`01_customer_support_rag_agent.py`는 `03_tool-use`의 Agent와 Tool 실행 원칙을 실제
pgvector·Redis RAG에 연결합니다.

```text
질문 → Agent의 검색 Tool Call 제안 → Backend Allowlist·Pydantic 검증
→ pgvector 검색 → Tool Result → Ollama 근거 답변 → Redis TTL Cache
```

```powershell
cd C:\aidevs\05_llm-agent-orchestration\04_rag
python .\10_labs\01_customer_support_rag_agent.py

# 실제 Ollama Tool Calling으로 Agent의 선택을 확인할 때
$env:RAG_LAB_AGENT_PROVIDER="ollama"
python .\10_labs\01_customer_support_rag_agent.py
```

첫 실행은 pgvector 검색과 답변 생성을 수행하는 Cache MISS이고, 같은 질문의 두 번째
실행은 Redis Cache HIT입니다. Redis를 중지하면 Cache 저장은 실패하지만 pgvector
검색과 답변 생성은 계속됩니다.

확인할 항목:

1. Agent의 Tool Call과 Backend가 실행한 Tool Result를 구분합니다.
2. 허용되지 않은 Tool과 잘못된 `query`, `top_k`가 실행 전에 차단되는지 확인합니다.
3. 답변의 출처가 `파일명#Chunk 번호`로 표시되는지 확인합니다.
4. 첫 호출의 `cache_hit=False`와 두 번째 호출의 `cache_hit=True`를 확인합니다.
5. Redis 장애가 장기 문서 저장소인 pgvector 검색을 막지 않는지 확인합니다.

## 독립 Lab 2. 정책 문서 갱신과 Cache 무효화

`02_document_update_and_cache_invalidation.py`는 정책 문서의 새 버전을 pgvector에
Upsert하고, 새 문서에서 사라진 이전 Chunk를 제거한 뒤 관련 Redis Cache만
무효화하는 결정적 Workflow입니다.

```text
version 1 색인·Cache 무효화 → 검색 MISS·HIT → version 2 Upsert
→ 오래된 Chunk 제거·전용 Redis Namespace 무효화 → 새 검색 MISS
```

```powershell
cd C:\aidevs\05_llm-agent-orchestration\04_rag
python .\10_labs\02_document_update_and_cache_invalidation.py
```

문서 갱신 순서와 Cache 무효화는 정해진 업무 규칙이므로 Agent가 판단하지 않습니다.
Backend Workflow가 처리하며, 사용자 질문에 답할 때만 Agent가 검색 Tool을 선택합니다.

확인할 항목:

1. version 1의 두 Chunk가 pgvector에 저장되는지 확인합니다.
2. 동일 질문의 Redis Cache MISS→HIT를 확인합니다.
3. 한 Chunk로 줄어든 version 2를 색인한 뒤 이전 두 번째 Chunk가 제거되는지 확인합니다.
4. 각 문서 변경 후 `FLUSHDB`가 아니라 이 Lab의 Cache Namespace만 SCAN·삭제하는지 확인합니다.
5. version 2 색인 직후 같은 질문이 새 정책을 검색하고 다시 MISS가 되는지 확인합니다.

## 독립 Lab 3. 쇼핑몰 상품 Hybrid Search

```powershell
python .\10_labs\03_product_hybrid_search.py
```

실제 상품을 pgvector에 저장하고 카테고리는 JSONB Metadata Filter로, 최대 가격은
검증된 Backend 조건으로 제한합니다. 키워드와 벡터 순위는 RRF로 결합하고 검색 조건
전체를 Redis Cache Key에 포함합니다.

확인할 항목:

1. `category=shoes`, `max_price=100000` 밖의 상품이 제외되는지 확인합니다.
2. 상품 코드에 강한 키워드 검색과 설명에 강한 벡터 검색을 비교합니다.
3. 단위가 다른 점수를 더하지 않고 RRF 순위를 사용하는지 확인합니다.

## 독립 Lab 4. 사내 규정 ACL 검색

```powershell
python .\10_labs\04_internal_policy_acl_search.py
```

사용자 역할은 Agent arguments가 아니라 인증된 Backend 세션에서 가져옵니다. pgvector
검색 SQL에 JSONB ACL Filter를 적용하고, Redis Cache Key에도 역할을 포함합니다.

확인할 항목:

1. 일반 직원이 HR 전용 문서를 검색할 수 없는지 확인합니다.
2. Agent가 Tool arguments로 자신의 역할을 변경할 수 없는지 확인합니다.
3. 서로 다른 역할이 동일한 Cache Entry를 공유하지 않는지 확인합니다.

## 독립 Lab 5. PDF 여행 가이드

```powershell
python .\10_labs\05_pdf_travel_guide.py C:\data\travel-guide.pdf --query "박물관 휴관일은?"
```

텍스트형 PDF를 페이지별 Chunk로 나누어 pgvector에 저장합니다. 파일명·페이지 번호·파일
Hash를 Metadata로 보존하며, 같은 PDF를 다시 색인해도 결정적 Chunk ID로 갱신합니다.

확인할 항목:

1. 검색 결과에 원본 파일명과 페이지 번호가 표시되는지 확인합니다.
2. 동일 파일 재색인 시 Chunk가 중복 증가하지 않는지 확인합니다.
3. 문서가 짧아졌을 때 오래된 Chunk가 제거되는지 확인합니다.
4. 스캔 PDF에 OCR이 필요한 이유를 설명합니다.

## 독립 Lab 6. 검색 품질 평가

```powershell
python .\10_labs\06_retrieval_quality_evaluation.py
```

질문과 정답 문서 ID로 구성된 작은 평가 Dataset을 사용합니다. 실제 Keyword·pgvector·
Hybrid 검색 결과에서 Hit@3와 MRR을 계산하여 유사도 점수 자체가 아니라 정답 순위를
비교합니다.

확인할 항목:

1. 정답이 Top-K에 포함되는 비율과 정답의 평균 역순위를 구분합니다.
2. 검색 방식별 실패 질문과 정답 순위를 비교합니다.
3. `top_k`를 변경하고 Hit@K와 MRR의 변화를 관찰합니다.

## 독립 Lab 7. Multi-Tool RAG Agent

```powershell
python .\10_labs\07_multi_tool_rag_agent.py
```

첫 Cycle의 모호한 요청에는 답을 추측하지 않고 호텔·항공·관광 중 필요한 영역을
재질문합니다. 다음 사용자 입력에서 상태를 병합한 뒤 서로 분리된 pgvector Collection의
검색 Tool을 호출하고 근거 답변을 Redis에 캐싱합니다.

확인할 항목:

1. 모호한 첫 요청이 `clarification_required`로 종료되는지 확인합니다.
2. 두 번째 Cycle에서 호텔과 항공 Tool만 호출되는지 확인합니다.
3. Tool별 Allowlist와 Pydantic arguments 검증을 확인합니다.
4. `MAX_STEPS`, 전체 Trace, `termination_reason`을 확인합니다.
5. Agent가 Collection 이름이나 SQL을 직접 선택하지 않는지 확인합니다.

## 실행 준비

이 폴더의 독립 Lab 1~7은 모두 Mini Backend 없이 실행하지만, 공통 모듈
`_pgvector_store.py`를 통해 PostgreSQL·pgvector와 Ollama에 직접 연결합니다. Cache를
다루는 Lab은 Redis도 사용합니다. 따라서 Docker가 필요 없다는 뜻이 아니라 별도의
FastAPI Backend가 필요 없다는 뜻입니다.

먼저 과정 의존성을 설치하고 공용 인프라와 DB Schema를 준비합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag
python -m pip install -r .\requirements.txt

cd C:\mini_agent_st\infra
Copy-Item .env.example .env
docker compose up -d
docker exec mini-agent-ollama ollama pull embeddinggemma
docker exec mini-agent-ollama ollama pull llama3.2
.\check_rag_prerequisites.ps1
```

연결 주소가 기본값과 다르면 실행 전에 환경 변수를 설정합니다.

```powershell
$env:DATABASE_URL="postgresql://agent_user:agent_password@127.0.0.1:5433/agent_db"
$env:REDIS_URL="redis://127.0.0.1:6379/0"
$env:OLLAMA_BASE_URL="http://127.0.0.1:11434"
```

공용 인프라의 상세 설치·점검 방법은
[`infra/README.md`](../../../infra/README.md), 기본 예제 01~15의 단계별 실습은 상위
[`learning_unit/README.md`](../README.md)를 참고합니다. 이 문서는 위에서 설명한 독립
Lab 1~7만 다룹니다.

## 실행 결과 확인

- Lab 1: 첫 검색은 `cache_hit=false`, 같은 질문의 두 번째 검색은 `true`입니다.
- Lab 2: version 2 색인 후 Chunk가 하나만 남고 다음 검색은 다시 MISS입니다.
- Lab 3: 검색 결과는 `shoes`, 100,000원 이하 조건을 만족합니다.
- Lab 4: `employee`와 `manager`에게 HR 전용 문서가 노출되지 않습니다.
- Lab 5: 결과에 PDF 파일명과 페이지 번호가 표시됩니다.
- Lab 6: Keyword·Vector·Hybrid별 Hit@3와 MRR 및 질문별 순위가 출력됩니다.
- Lab 7: 첫 요청은 재질문으로 끝나고, 두 번째 요청은 호텔·항공 Tool만 호출합니다.

> Lab 7의 Tool 선택은 재현 가능한 학습을 위한 키워드 기반 결정적 Router입니다. 실제
> LLM Tool Calling 예제는 상위 `13_agent_pgvector_tool.py`와 Lab 1의 선택적 Ollama
> 모드를 사용합니다.
