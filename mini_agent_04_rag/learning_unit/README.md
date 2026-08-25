# 04 RAG

## 한 문장으로 이해하기

RAG는 LLM에게 바로 질문하지 않고, 먼저 관련 문서를 찾은 다음 그 근거와 함께 질문하는 과정입니다.

```text
질문 → 검색(Retrieval) → Context 구성 → LLM 답변(Generation) → 출처 표시
```

## 학습 목표

- LLM의 내부 지식과 수업에서 제공한 외부 문서를 구분합니다.
- 문서를 Chunk로 나누고 Metadata를 붙입니다.
- 키워드 검색과 의미 검색의 차이를 설명합니다.
- 검색 결과로 Context를 만들고 출처를 표시합니다.
- 근거가 없을 때 답변을 제한합니다.
- Ollama Embedding과 PostgreSQL/pgvector의 역할을 구분합니다.
- Redis Cache의 TTL, hit/miss, 재색인 무효화를 확인합니다.
- Retrieval부터 LLM 답변까지 전체 Trace를 관찰합니다.
- 직접 입력한 문장과 PDF를 pgvector에 색인하고 의미 검색합니다.
- Agent가 검색 전용 Tool을 선택·실행하고 근거 답변을 만드는 과정을 확인합니다.

## 예제 순서

| 순서 | 예제 | 외부 환경 | 확인할 내용 |
| --- | --- | --- | --- |
| 01 | `01_concept_example.py` | 필요 없음 | LLM 단독 답변과 RAG 비교 |
| 02 | `02_chunking_and_metadata.py` | 필요 없음 | Chunk와 Metadata |
| 03 | `03_keyword_retrieval.py` | 필요 없음 | 점수와 `top_k` |
| 04 | `04_vector_similarity.py` | 필요 없음 | 코사인 유사도와 의미 검색 |
| 05 | `05_grounded_answer.py` | 필요 없음 | Context·출처·답변 제한 |
| 06 | `06_pgvector_ollama_example.py` | Docker 필요 | 실제 Embedding 저장과 검색 |
| 07 | `07_keyword_vs_pgvector.py` | Backend·Docker 필요 | 키워드와 의미 검색 비교 |
| 08 | `08_real_rag_answer.py` | Backend·Docker 필요 | 실제 LLM 근거 답변과 출처 |
| 09 | `09_redis_rag_cache.py` | Backend·Docker 필요 | Redis MISS·HIT·TTL |
| 10 | `10_full_rag_pipeline.py` | Backend·Docker 필요 | 전체 RAG Trace |
| 11 | `11_text_insert_and_search.py` | Docker 필요 | 문장 입력·저장·유사도 검색 |
| 12 | `12_pdf_index_and_search.py` | Docker·PDF 필요 | PDF 추출·Chunk·페이지 출처 |
| 13 | `13_agent_pgvector_tool.py` | Docker 필요 | Agent의 pgvector Tool 호출 |
| 14 | `14_metadata_and_threshold.py` | Docker 필요 | JSONB Filter·유사도 임계값 |
| 15 | `15_hybrid_search.py` | Docker 필요 | 키워드·벡터 검색과 RRF 결합 |

처음 다섯 예제는 API Key와 Docker 없이 실행합니다. RAG의 흐름을 먼저 이해한 후 마지막 예제에서 같은 과정을 실제 인프라로 교체합니다.

## 기본과 실제 인프라 비교

| 학습용 Python | 실제 구성 |
| --- | --- |
| 문자열 목록 | PostgreSQL `documents` 테이블 |
| 간단한 키워드/숫자 벡터 | Ollama `embeddinggemma` |
| Python 정렬 | pgvector 코사인 거리 검색 |
| Mock 답변 | 검색 Context를 전달받은 LLM |
| 매번 다시 계산 | Redis TTL 답변 Cache |

채팅 모델인 `llama3.2`와 Embedding 모델인 `embeddinggemma`는 역할이 다릅니다. 문서를 저장할 때와 질문을 검색할 때는 반드시 같은 Embedding 모델을 사용해야 합니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_04_rag\learning_unit
python .\01_concept_example.py
python .\02_chunking_and_metadata.py
python .\03_keyword_retrieval.py
python .\04_vector_similarity.py
python .\05_grounded_answer.py
```

06 예제는 `C:\mini_agent_st\infra`의 공용 Docker 환경과 Embedding 모델을 사용합니다.

```powershell
cd C:\mini_agent_st\infra
docker compose up -d
docker exec mini-agent-ollama ollama pull embeddinggemma

cd C:\mini_agent_st\mini_agent_04_rag\learning_unit
python .\06_pgvector_ollama_example.py
```

07~10은 `mini_agent_04_rag` Backend를 실행한 뒤 호출합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag\backend
uvicorn app.main:app --reload --port 8000

cd C:\mini_agent_st\mini_agent_04_rag\learning_unit
$env:RAG_EXAMPLE_PROVIDER="ollama"  # mock, gemini, openai, ollama
python .\07_keyword_vs_pgvector.py
python .\08_real_rag_answer.py
python .\09_redis_rag_cache.py
python .\10_full_rag_pipeline.py
```

11~15는 Mini Backend 없이 Ollama와 PostgreSQL에 직접 연결합니다. 먼저 06과 같은
방법으로 공용 인프라와 DB Schema를 준비합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag\learning_unit
python .\11_text_insert_and_search.py
python .\12_pdf_index_and_search.py C:\data\travel-policy.pdf --query "당일 취소 규정은?" --top-k 3
python .\13_agent_pgvector_tool.py
python .\14_metadata_and_threshold.py
python .\15_hybrid_search.py

# 실제 Ollama Agent Tool Calling을 확인할 때
$env:RAG_AGENT_PROVIDER="ollama"
python .\13_agent_pgvector_tool.py
```

12는 텍스트가 포함된 PDF를 대상으로 합니다. 검색 결과에는 파일명과 페이지 번호가
표시됩니다. 이미지로 스캔된 PDF는 텍스트 추출 전에 별도 OCR 처리가 필요합니다.

11~15가 공유하는 `_pgvector_store.py`는 다음 계약을 한곳에서 관리합니다.

- 문서와 질문에 동일한 `embeddinggemma` 모델 사용
- `collection/source/chunk_index` 기반 결정적 ID와 Upsert
- `top_k`, 선택적 `score_threshold`, JSONB Metadata Filter 적용
- Parameterized SQL을 이용한 코사인 유사도 검색
- Agent에는 DB나 SQL 대신 `search_knowledge_base` 검색 Tool만 제공

pgvector는 Chunk와 Embedding을 영구 저장하고 Redis는 계산된 RAG 답변을 짧게
보관합니다. Redis 장애는 검색과 답변 생성을 막지 않으며 재색인하면 전용 Cache를
무효화합니다.

## 독립 실행 통합 Lab 01~07

기본 예제 01~15에서 익힌 검색 기법을 실제 업무 시나리오로 연결합니다. 모든 Lab은
Agent가 제한된 검색 Tool을 선택하고, Tool Executor가 검증·실행한 결과만으로 답변하는
Mini Agent 03의 계약을 유지합니다. pgvector는 원문 Chunk 검색에, Redis는 답변 Cache나
Agent의 짧은 대화 상태 저장에 사용합니다.

| Lab | 시나리오 | 핵심 학습 |
| --- | --- | --- |
| 01 | 고객지원 정책 Agent | Tool Call, pgvector 검색, Redis Cache |
| 02 | 정책 문서 갱신 | 재색인, 오래된 Chunk 제거, Cache 무효화 |
| 03 | 쇼핑몰 상품 검색 | Metadata Filter, 가격·카테고리 조건, Hybrid Search |
| 04 | 사내 규정 문서 | 사용자 권한별 문서 검색, ACL Filter |
| 05 | PDF 여행 가이드 | PDF Chunking, 페이지 출처, 중복 색인 방지 |
| 06 | 검색 품질 평가 | Hit@K, MRR, Keyword·Vector·Hybrid 비교 |
| 07 | Multi-Tool RAG Agent | 재질문, 여러 지식 저장소 선택, 종료 조건 |

공용 Docker 인프라와 `embeddinggemma`를 준비한 뒤 각 파일을 독립 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag\learning_unit
python .\10_labs\01_customer_support_agent.py
python .\10_labs\02_policy_document_update.py
python .\10_labs\03_product_hybrid_search.py
python .\10_labs\04_acl_document_search.py
python .\10_labs\05_pdf_travel_guide.py
python .\10_labs\06_retrieval_evaluation.py
python .\10_labs\07_multi_tool_rag_agent.py
```

상세 준비 사항과 Lab별 관찰 지점은
[`10_labs/README.md`](./10_labs/README.md), 과제는
[`20_assignments/README.md`](./20_assignments/README.md)에서 확인합니다.

## 독립 실행 통합 Lab 01~07

기본 예제 01~15에서 익힌 검색 기법을 실제 업무 시나리오로 연결합니다. 모든 Lab은
Agent가 제한된 검색 Tool을 선택하고, Tool Executor가 검증·실행한 결과만으로 답변하는
Mini Agent 03의 계약을 유지합니다. pgvector는 원문 Chunk 검색에, Redis는 답변 Cache나
Agent의 짧은 대화 상태 저장에 사용합니다.

| Lab | 시나리오 | 핵심 학습 |
| --- | --- | --- |
| 01 | 고객지원 정책 Agent | Tool Call, pgvector 검색, Redis Cache |
| 02 | 정책 문서 갱신 | 재색인, 오래된 Chunk 제거, Cache 무효화 |
| 03 | 쇼핑몰 상품 검색 | Metadata Filter, 가격·카테고리 조건, Hybrid Search |
| 04 | 사내 규정 문서 | 사용자 권한별 문서 검색, ACL Filter |
| 05 | PDF 여행 가이드 | PDF Chunking, 페이지 출처, 중복 색인 방지 |
| 06 | 검색 품질 평가 | Hit@K, MRR, Keyword·Vector·Hybrid 비교 |
| 07 | Multi-Tool RAG Agent | 재질문, 여러 지식 저장소 선택, 종료 조건 |

공용 Docker 인프라와 `embeddinggemma`를 준비한 뒤 각 파일을 독립 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag\learning_unit
python .\10_labs\01_customer_support_agent.py
python .\10_labs\02_policy_document_update.py
python .\10_labs\03_product_hybrid_search.py
python .\10_labs\04_acl_document_search.py
python .\10_labs\05_pdf_travel_guide.py
python .\10_labs\06_retrieval_evaluation.py
python .\10_labs\07_multi_tool_rag_agent.py
```

상세 준비 사항과 Lab별 관찰 지점은
[`10_labs/README.md`](./10_labs/README.md), 과제는
[`assignments/README.md`](./assignments/README.md)에서 확인합니다.

> 기존 PostgreSQL Volume에서는 수정된 `infra/postgres/init.sql`이 자동 재실행되지
> 않습니다. 데이터 보존이 필요하면 Volume을 삭제하지 말고 필요한 Schema만 적용합니다.

## 수업 진행 권장 순서

1. 01~03에서 RAG 흐름과 검색을 이해합니다.
2. 04에서 벡터는 의미를 나타내는 숫자 배열이라는 정도만 확인합니다.
3. 05에서 검색 결과가 없을 때 모른다고 답하도록 만듭니다.
4. 06~07에서 Ollama와 pgvector 색인·검색을 확인합니다.
5. 08에서 검색 Context를 실제 LLM에 전달합니다.
6. 09~10에서 Redis Cache와 전체 Trace를 확인합니다.
7. 11에서 직접 입력한 문장의 저장과 유사도 검색을 확인합니다.
8. 12에서 PDF의 페이지별 Chunk와 출처를 확인합니다.
9. 13에서 Agent의 Tool 선택·실행·최종 답변 Loop를 확인합니다.
10. 14에서 문서 범위 Filter와 임계값에 따른 결과 변화를 확인합니다.
11. 15에서 키워드·벡터 검색 결과를 RRF로 결합합니다.
12. Lab 01~02에서 Tool 기반 정책 답변과 안전한 문서 교체를 통합합니다.
13. Lab 03~05에서 Metadata·ACL·PDF 출처를 업무 조건에 적용합니다.
14. Lab 06에서 검색 전략을 수치로 평가하고 Lab 07에서 Multi-Tool Agent의 재질문과 종료 조건을 확인합니다.
12. Lab 01~02에서 Tool 기반 정책 답변과 안전한 문서 교체를 통합합니다.
13. Lab 03~05에서 Metadata·ACL·PDF 출처를 업무 조건에 적용합니다.
14. Lab 06에서 검색 전략을 수치로 평가하고 Lab 07에서 Multi-Tool Agent의 재질문과 종료 조건을 확인합니다.

## 14~15 검색 품질 확장

14는 벡터가 비슷하더라도 만료된 정책이나 다른 업무 영역의 문서를 제외하는 방법을
다룹니다. `metadata @> filter` 조건으로 `category`, `status`, `language`를 제한하고,
`score_threshold`보다 낮은 결과는 Context에 포함하지 않습니다. 임계값은 모델과
데이터에 따라 점수 분포가 달라지므로 고정된 정답이 아니라 평가 결과로 조정합니다.

15는 정확한 객실 코드 같은 고유명사에 강한 키워드 검색과 표현이 달라도 의미를 찾는
pgvector 검색을 함께 사용합니다. 두 검색 점수는 단위가 다르므로 직접 더하지 않고,
각 결과의 순위를 Reciprocal Rank Fusion(RRF)으로 결합합니다. 이 예제의 키워드 검색은
원리를 보기 위한 Python 구현이며, 대규모 서비스에서는 PostgreSQL Full Text Search나
별도 검색 엔진으로 후보를 가져오는 구조로 교체할 수 있습니다.

## 공식 참고 자료

- [Ollama Embedding](https://docs.ollama.com/capabilities/embeddings)
- [Ollama `/api/embed`](https://docs.ollama.com/api/embed)
- [pgvector Python · Psycopg 3](https://github.com/pgvector/pgvector-python#psycopg-3)
