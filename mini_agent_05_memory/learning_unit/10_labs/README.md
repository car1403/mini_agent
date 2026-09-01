# 05 Memory 실습

## 독립 Lab 구성

다음 세 Lab은 Docker와 Backend 없이 실행하며, Memory를 저장하기 전에 적용할 정책을
작은 결정적 코드로 확인합니다.

| Lab | 파일 | 핵심 학습 |
|---:|---|---|
| 01 | `01_consent_and_value_safety.py` | 명시적 동의, key Allowlist, 민감한 value 차단 |
| 02 | `02_retention_and_user_control.py` | TTL과 장기 보존, 내보내기, 사용자 전체 삭제 |
| 03 | `03_authenticated_scope_and_safe_keys.py` | 인증 사용자 범위, Redis-safe 결정적 Key |

```powershell
cd C:\aidevs\05_llm-agent-orchestration\05_memory
python .\10_labs\01_consent_and_value_safety.py
python .\10_labs\02_retention_and_user_control.py
python .\10_labs\03_authenticated_scope_and_safe_keys.py
```

각 Lab에서 확인할 항목은 다음과 같습니다.

1. 허용된 key라도 동의가 없거나 value에 민감정보가 있으면 저장하지 않습니다.
2. Redis 단기 상태는 만료되지만 PostgreSQL 장기 선호는 삭제 요청까지 유지됩니다.
3. 내보내기와 삭제는 인증된 사용자 범위에만 적용됩니다.
4. 외부 ID를 Redis Key에 그대로 넣지 않아 `*`, `?`, `:`에 의한 충돌을 막습니다.

## 실행 위치

아래 기본 실습 1~5는 Backend 없이 진행합니다. 기본 예제 `05_redis_session.py`와
`06_postgres_long_term_memory.py`를 실행할 때는 공용 Redis와 PostgreSQL을 준비합니다.

```powershell
cd C:\mini_agent_st\infra
docker compose up -d redis postgres
```

기본 예제 07~13과 완성 화면, Backend 재시작 후 영속성을 확인할 때는 Mini Agent 05
Backend를 별도 터미널에서 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_05_memory\backend
uvicorn app.main:app --reload --port 8000
```

## 실습 1. 데이터 종류 분류

다음 정보를 대화 기록·단기 상태·장기 Memory·RAG 문서로 분류합니다.

- 현재 Agent 단계
- 호텔 환불 정책
- 사용자의 해산물 알레르기
- 직전 질문과 답변
- 다음 달에도 유지할 교통 선호

## 실습 2. Conversation Window

`max_recent_messages`를 2, 4, 6으로 바꾸고 Prompt에 들어가는 메시지 수와 요약을 비교합니다.

## 실습 3. 사용자 격리

사용자 A와 B에게 서로 다른 교통 선호를 저장합니다. A가 B의 Memory를 조회·수정·삭제할 수 없는지 확인합니다.

## 실습 4. 관련 Memory 선택

- 식당 질문에는 `food_restriction`만 사용
- 이동 경로 질문에는 `transportation`만 사용
- 호텔 질문에는 `hotel_preference`만 사용
- 관련 없는 Memory는 Prompt에서 제외

## 실습 5. 민감정보 차단

비밀번호·카드번호·여권번호·API Key 저장을 시도하고 모두 거부되는지 확인합니다.

## 실습 6. Redis TTL

TTL을 30초로 줄여 상태 저장 직후와 만료 후를 비교합니다. `TTL=-2`는 key가 없다는 의미입니다.

## 실습 7. PostgreSQL 영속성

Memory를 저장하고 Backend를 재시작한 뒤에도 남는지 확인합니다. 삭제 후 다시 조회해 사라졌는지도 확인합니다.

## 실습 8. 개인화 답변 변화

Memory 저장 전·저장 후·수정 후·삭제 후에 같은 질문을 보내 최종 답변이 어떻게 달라지는지 기록합니다.

## 실습 9. Redis 사용자 격리와 충돌

`07_redis_ttl_and_isolation.py`와 `08_redis_atomic_update.py`로 같은 session_id의 사용자
격리, TTL 연장, 오래된 version의 HTTP 409 차단을 확인합니다.

## 실습 10. PostgreSQL 대화와 Hybrid 복원

`10_postgres_conversation_history.py`와 `11_hybrid_session_restore.py`로 최근 대화,
장기 Memory, Redis 단기 상태가 사용자별로 복원되는지 확인합니다.

## 실습 11. 실제 개인화와 사용자 제어

`12_real_llm_personalization.py`에서 사용 Memory·Trace를 검증하고
`13_memory_export_and_delete.py`로 내보내기와 전체 삭제를 확인합니다.
