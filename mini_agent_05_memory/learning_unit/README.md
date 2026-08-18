# 05 Memory

## 한 문장으로 이해하기

Memory는 모든 대화를 무조건 저장하는 기능이 아니라, 다음 요청에 필요하고 사용자가 확인·수정·삭제할 수 있는 상태와 선호를 관리하는 기능입니다.

## 네 가지를 먼저 구분하기

| 종류 | 예 | 보관 기간 | 대표 저장소 |
| --- | --- | --- | --- |
| 대화 기록 | 최근 질문과 답변 | 현재 대화 또는 정책 기간 | 메모리·PostgreSQL |
| 단기 상태 | 현재 Agent 단계 | TTL까지 | Redis |
| 장기 Memory | 교통·음식·숙소 선호 | 삭제 요청까지 | PostgreSQL |
| RAG 문서 | 환불·수하물 정책 | 문서 갱신까지 | PostgreSQL/pgvector |

Memory는 사용자와 대화의 상태이고, RAG는 외부 지식 문서를 검색합니다.

## 학습 목표

- 대화 기록·단기 상태·장기 Memory·RAG를 구분합니다.
- 전체 대화 대신 최근 메시지와 요약을 사용합니다.
- 사용자별 Memory를 격리합니다.
- 필요한 Memory만 선택해 개인화 답변에 사용합니다.
- 민감정보와 허용되지 않은 항목을 저장하지 않습니다.
- Redis TTL과 PostgreSQL 영구 저장을 비교합니다.
- 사용자가 Memory를 확인·수정·삭제할 수 있게 합니다.

## 예제 순서

| 순서 | 예제 | 외부 환경 | 확인할 내용 |
| --- | --- | --- | --- |
| 01 | `01_memory_types.py` | 필요 없음 | 네 가지 데이터 종류 비교 |
| 02 | `02_conversation_window.py` | 필요 없음 | 최근 메시지와 요약 |
| 03 | `03_user_memory_crud.py` | 필요 없음 | 사용자 격리와 CRUD |
| 04 | `04_relevant_and_safe_memory.py` | 필요 없음 | 관련 Memory·민감정보·개인화 |
| 05 | `05_redis_session.py` | Redis 필요 | TTL 단기 상태 |
| 06 | `06_postgres_long_term_memory.py` | PostgreSQL 필요 | 영구 Memory CRUD |

처음 네 예제는 Docker 없이 실행합니다. Redis와 PostgreSQL은 개념과 안전 규칙을 이해한 후 연결합니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_05_memory\learning_unit
python .\01_memory_types.py
python .\02_conversation_window.py
python .\03_user_memory_crud.py
python .\04_relevant_and_safe_memory.py
```

05와 06은 공용 Docker 환경을 먼저 실행합니다.

```powershell
cd C:\mini_agent_st\infra
Copy-Item .env.example .env
docker compose up -d

cd C:\mini_agent_st\mini_agent_05_memory\learning_unit
python .\05_redis_session.py
python .\06_postgres_long_term_memory.py
```

> 기존 PostgreSQL Volume에는 새 Memory 테이블이 자동 생성되지 않을 수 있습니다. [공용 인프라 안내](../../../mini_agent_st/infra/README.md)의 스키마 적용 방법을 확인합니다.

## 저장하지 않는 정보

- 비밀번호
- 카드번호와 인증번호
- 여권번호와 주민등록번호
- API Key와 Access Token
- 사용자가 저장에 동의하지 않은 민감정보

수업 예제는 저장 가능한 key를 Allowlist로 제한합니다.

## 운영 환경의 사용자 식별

예제의 `user_id`는 사용자 격리 원리를 보여주기 위한 수업용 값입니다. 실제 서비스에서는 요청 Body나 화면에서 받은 `user_id`를 그대로 신뢰하면 안 됩니다. Backend가 로그인 토큰이나 인증 Session에서 확인한 사용자 ID를 조회·수정·삭제 조건에 사용해야 합니다.
