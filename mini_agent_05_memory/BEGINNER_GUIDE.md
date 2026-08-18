# Mini Agent 05 초보자 진행 순서

## Docker 없이

1. `learning_unit/01_memory_types.py`
2. `learning_unit/02_conversation_window.py`
3. `learning_unit/03_user_memory_crud.py`
4. `learning_unit/04_relevant_and_safe_memory.py`
5. Backend와 Streamlit 실행
6. Mock Memory 저장·조회·수정·삭제
7. 저장 전·후·삭제 후 개인화 답변 비교

여기까지 진행해도 Memory 핵심 수업은 완료할 수 있습니다.

## Docker 연결

1. 공용 `infra` 실행
2. `Redis·PostgreSQL` 메뉴에서 상태 확인
3. Redis Session 저장과 TTL 조회
4. Memory CRUD 저장소를 `postgres`로 변경
5. Backend 재시작 후 Memory가 유지되는지 확인

## 꼭 구분할 것

| 데이터 | 저장 위치 | 특징 |
| --- | --- | --- |
| 최근 대화 | Prompt Window | 개수 제한 |
| Agent 단기 상태 | Redis | TTL 자동 만료 |
| 사용자 장기 선호 | PostgreSQL | CRUD와 사용자 격리 |
| RAG 지식 문서 | pgvector | 검색 가능한 외부 지식 |
