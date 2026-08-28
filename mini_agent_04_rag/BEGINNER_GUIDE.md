# Mini Agent 04 초보자 진행 순서

## 1. Docker 없이 시작

1. `learning_unit/01~05`를 실행합니다.
2. Backend와 Streamlit을 실행합니다.
3. `Chunk와 키워드 검색`에서 문장 수를 바꿉니다.
4. 같은 화면에서 `키워드 검색`을 실행합니다.
5. `근거 기반 답변`에서 Ollama 선택을 끕니다.
6. 여권 분실 질문이 제한되는지 확인합니다.

## 2. Docker 연결

1. 공용 `infra`에서 `docker compose up -d`를 실행합니다.
2. Ollama에 `embeddinggemma`를 내려받습니다.
3. HOME에서 연결 상태를 확인합니다.
4. 교육용 문서를 색인합니다.
5. 검색 방식을 `pgvector`로 바꿉니다.
6. 같은 질문을 두 번 실행해 Redis Cache MISS→HIT를 확인합니다.
7. `Cache와 검색 조건`에서 동일 질문을 두 번 보내 MISS→HIT를 확인합니다.

## 꼭 구분할 것

| 구성 요소 | 역할 |
| --- | --- |
| `llama3.2` | Context를 읽고 답변 생성 |
| `embeddinggemma` | 문장을 검색용 Vector로 변환 |
| PostgreSQL | 문서와 Metadata 저장 |
| pgvector | 비슷한 Vector 검색 |
| Redis | 검색·답변 결과의 TTL Cache |
| Streamlit | 결과와 출처 확인 |

문서 색인과 질문 검색에는 같은 Embedding 모델을 사용해야 합니다.
