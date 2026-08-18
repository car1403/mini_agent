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

## 예제 순서

| 순서 | 예제 | 외부 환경 | 확인할 내용 |
| --- | --- | --- | --- |
| 01 | `01_concept_example.py` | 필요 없음 | LLM 단독 답변과 RAG 비교 |
| 02 | `02_chunking_and_metadata.py` | 필요 없음 | Chunk와 Metadata |
| 03 | `03_keyword_retrieval.py` | 필요 없음 | 점수와 `top_k` |
| 04 | `04_vector_similarity.py` | 필요 없음 | 코사인 유사도와 의미 검색 |
| 05 | `05_grounded_answer.py` | 필요 없음 | Context·출처·답변 제한 |
| 06 | `06_pgvector_ollama_example.py` | Docker 필요 | 실제 Embedding 저장과 검색 |

처음 다섯 예제는 API Key와 Docker 없이 실행합니다. RAG의 흐름을 먼저 이해한 후 마지막 예제에서 같은 과정을 실제 인프라로 교체합니다.

## 기본과 실제 인프라 비교

| 학습용 Python | 실제 구성 |
| --- | --- |
| 문자열 목록 | PostgreSQL `documents` 테이블 |
| 간단한 키워드/숫자 벡터 | Ollama `embeddinggemma` |
| Python 정렬 | pgvector 코사인 거리 검색 |
| Mock 답변 | 검색 Context를 전달받은 LLM |

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

06 예제는 먼저 공용 Docker 환경을 실행하고 Embedding 모델을 준비합니다.

```powershell
cd C:\mini_agent_st\infra
Copy-Item .env.example .env
docker compose up -d
docker exec mini-agent-ollama ollama pull embeddinggemma

cd C:\mini_agent_st\mini_agent_04_rag\learning_unit
python .\06_pgvector_ollama_example.py
```

> 기존 PostgreSQL Volume이 이미 만들어진 경우 수정된 `init.sql`은 자동 재실행되지 않습니다. 데이터 보존이 필요하면 Volume을 삭제하지 말고 `documents` 생성 SQL만 직접 실행합니다.

## 수업 진행 권장 순서

1. 01~03에서 RAG 흐름과 검색을 이해합니다.
2. 04에서 벡터는 의미를 나타내는 숫자 배열이라는 정도만 확인합니다.
3. 05에서 검색 결과가 없을 때 모른다고 답하도록 만듭니다.
4. 06에서 Docker의 Ollama와 pgvector로 구현을 교체합니다.
5. `mini_agent_04_rag` 화면에서 Chunk·검색·답변·출처를 확인합니다.

## 공식 참고 자료

- [Ollama Embedding](https://docs.ollama.com/capabilities/embeddings)
- [Ollama `/api/embed`](https://docs.ollama.com/api/embed)
- [pgvector Python · Psycopg 3](https://github.com/pgvector/pgvector-python#psycopg-3)
