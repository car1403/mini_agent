# 04 RAG 실습

## 실습 1. Chunk 크기 비교

`02_chunking_and_metadata.py`의 `sentences_per_chunk`를 1, 2, 4로 바꾸고 Chunk 개수와 내용을 비교합니다.

## 실습 2. 검색 결과 설명하기

`03_keyword_retrieval.py`에서 `top_k`를 1과 3으로 실행하고, 검색 결과가 늘어날 때 Context에 불필요한 내용이 섞일 수 있는 이유를 적습니다.

## 실습 3. 근거 없음 처리

등록되지 않은 여권 분실 질문을 입력하고 다음을 확인합니다.

- `grounded`가 `False`인가?
- `sources`가 비어 있는가?
- 문서에 없는 내용을 추측하지 않는가?

## 실습 4. 실제 pgvector 검색

Docker 환경을 실행한 후 `06_pgvector_ollama_example.py`의 질문을 세 가지로 바꿉니다.

- 호텔 예약을 취소하고 싶어요.
- 비행기에 가방을 몇 kg까지 실을 수 있나요?
- 박물관이 쉬는 날은 언제인가요?

각 질문에서 1위 문서와 점수를 기록합니다.
