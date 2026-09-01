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

## 전체 흐름

```text
질문
→ 인증된 사용자 확인
→ 사용자 Memory 조회
→ 질문과 관련된 Memory 선택
→ 안전 정책 적용
→ Prompt에 필요한 Memory만 추가
→ 답변 생성
→ 사용한 Memory와 Trace 표시
```

처음부터 데이터베이스나 LLM을 연결하지 않습니다. Python 예제로 핵심 원리를 먼저
확인한 후 Redis, PostgreSQL, 실제 LLM 순서로 진행합니다.

## 처음 한 번 준비하기

과정 루트에서 가상 환경, 패키지와 공통 `.env`를 준비합니다.

```powershell
cd C:\aidevs\05_llm-agent-orchestration
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python .\05_memory\00_check_environment.py
```

이미 `.env`가 있으면 덮어쓰지 않습니다. 다음 항목이 Memory 예제의 공통 설정입니다.

| 환경 변수 | 기본값 | 사용하는 예제 |
| --- | --- | --- |
| `REDIS_URL` | `redis://127.0.0.1:6379/0` | 05, 07, 08, 11, 13 |
| `REDIS_TTL_SECONDS` | `1800` | Redis Session |
| `DATABASE_URL` | PostgreSQL `127.0.0.1:5433` | 06, 09~13 |
| `BACKEND_API_URL` | `http://127.0.0.1:8000` | 07~13 |
| `MEMORY_EXAMPLE_PROVIDER` | `openai` | 12 |
| `REQUEST_TIMEOUT_SECONDS` | `30` | 07~13 API 요청 |
| `MEMORY_MCP_URL` | `http://127.0.0.1:8012/mcp` | PostgreSQL HTTP MCP Client |
| `MCP_DEMO_USER_ID` | `student-01` | 교육용 MCP 사용자 범위 |

## 학습 목표

- 대화 기록·단기 상태·장기 Memory·RAG를 구분합니다.
- 전체 대화 대신 최근 메시지와 요약을 사용합니다.
- 사용자별 Memory를 격리합니다.
- 필요한 Memory만 선택해 개인화 답변에 사용합니다.
- 민감정보와 허용되지 않은 항목을 저장하지 않습니다.
- Redis TTL과 PostgreSQL 영구 저장을 비교합니다.
- 사용자가 Memory를 확인·수정·삭제할 수 있게 합니다.
- Redis 원자 갱신과 PostgreSQL 대화 복원을 확인합니다.
- 실제 LLM이 사용한 Memory와 전체 Trace를 관찰합니다.

## 학습 순서

### 1단계 · Python만 사용

| 예제 | 배우는 내용 | 실행 후 확인할 것 |
| --- | --- | --- |
| `01_memory_types.py` | 대화·단기 상태·장기 Memory·RAG 구분 | 목적과 보관 기간이 서로 다름 |
| `02_conversation_window.py` | 오래된 대화 요약과 최근 Window | 전체 대화를 Prompt에 넣지 않음 |
| `03_user_memory_crud.py` | 사용자별 저장·조회·수정·삭제 | 다른 사용자의 Memory를 삭제할 수 없음 |
| `04_relevant_and_safe_memory.py` | 관련 Memory 선택과 저장 정책 | 음식 질문에 음식 관련 Memory만 사용 |

```powershell
cd C:\aidevs\05_llm-agent-orchestration\05_memory
python .\01_memory_types.py
python .\02_conversation_window.py
python .\03_user_memory_crud.py
python .\04_relevant_and_safe_memory.py
```

각 파일은 독립적으로 실행할 수 있습니다. 네 예제가 정상적으로 실행되면 Memory의
핵심 개념 학습은 완료한 것입니다.

### 2단계 · Redis와 PostgreSQL

| 순서 | 예제 | 외부 환경 | 확인할 내용 |
| --- | --- | --- | --- |
| 05 | `05_redis_session.py` | Redis 필요 | TTL 단기 상태 |
| 06 | `06_postgres_long_term_memory.py` | PostgreSQL 필요 | 영구 Memory CRUD |
| 07 | `07_redis_ttl_and_isolation.py` | Backend·Redis 필요 | TTL 연장과 사용자 격리 |
| 08 | `08_redis_atomic_update.py` | Backend·Redis 필요 | WATCH/MULTI와 version 충돌 |
| 09 | `09_postgres_upsert_and_isolation.py` | Backend·PostgreSQL 필요 | upsert와 사용자 범위 |
| 10 | `10_postgres_conversation_history.py` | Backend·PostgreSQL 필요 | 대화 저장과 최근 Window |
| 11 | `11_hybrid_session_restore.py` | Backend·Redis·PostgreSQL 필요 | 두 저장소 복원과 Trace |

05와 06은 저장소를 직접 사용합니다. 07~11은 Mini Agent 05 Backend API를 통해
TTL, 충돌, 사용자 격리와 복원 과정을 확인합니다.

### 3단계 · 실제 LLM과 사용자 통제

| 순서 | 예제 | 외부 환경 | 확인할 내용 |
| --- | --- | --- | --- |
| 12 | `12_real_llm_personalization.py` | Backend·LLM 필요 | 실제 개인화와 Trace |
| 13 | `13_memory_export_and_delete.py` | Backend·Redis·PostgreSQL 필요 | 내보내기와 전체 삭제 |

실제 LLM에는 전체 Memory가 아니라 질문과 관련된 안전한 Memory만 전달합니다.
마지막에는 사용자가 자신의 데이터를 확인하고 삭제할 수 있는지도 검증합니다.

### 선택 과정 · Streamable HTTP MCP

`30_mcp`는 Memory 기능을 Agent가 호출할 수 있는 Tool로 제공합니다.

```text
Codex 또는 MCP Client
→ http://127.0.0.1:8012/mcp
→ 사용자 범위 Memory Tool
→ PostgreSQL user_memories
```

[30_mcp/README.md](./30_mcp/README.md)의 PostgreSQL Server와 Client를 실행합니다. 이 예제도 실제 PostgreSQL만 사용합니다.
Tool 인자에서 `user_id`를 제거하고 서버가 확인한 사용자 범위를 쓰는 이유도 함께
확인합니다.

## 2~3단계 실행 환경

05와 06은 `00_local-runtime`에서 만든 Redis와 PostgreSQL Container를 먼저
실행합니다. `C:\mini_agent_st\infra`의 Docker Compose 환경과 동시에 실행하면 같은
Port가 충돌하므로 둘 중 하나만 사용합니다.

```powershell
cd C:\aidevs\05_llm-agent-orchestration
.\00_local-runtime\scripts\start-local-services.ps1
python .\00_local-runtime\database\apply_schema.py
python .\05_memory\05_redis_session.py
python .\05_memory\06_postgres_long_term_memory.py
```

07~13은 Mini Agent 05 Backend를 먼저 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_05_memory\backend
uvicorn app.main:app --reload --port 8000

cd C:\aidevs\05_llm-agent-orchestration\05_memory
$env:MEMORY_EXAMPLE_PROVIDER="openai"  # openai, gemini, ollama
python .\07_redis_ttl_and_isolation.py
python .\08_redis_atomic_update.py
python .\09_postgres_upsert_and_isolation.py
python .\10_postgres_conversation_history.py
python .\11_hybrid_session_restore.py
python .\12_real_llm_personalization.py
python .\13_memory_export_and_delete.py
```

> 기존 PostgreSQL Volume을 사용해도 `apply_schema.py`는 필요한 테이블을 다시
> 확인하고, 없는 테이블만 생성합니다. 일반 종료에서는 Volume을 삭제하지 않습니다.

## 초보자가 자주 헷갈리는 점

- 대화 기록은 장기 선호와 다릅니다. 최근 대화는 Window로 제한할 수 있습니다.
- Redis는 영구 보관소가 아닙니다. TTL이 지나면 단기 상태가 사라집니다.
- PostgreSQL에 저장했다고 모두 Prompt에 넣지 않습니다. 질문과 관련된 항목만 고릅니다.
- 화면에서 받은 `user_id`는 운영 환경의 인증 정보가 아닙니다.
- RAG 문서는 여러 사용자가 참고하는 외부 지식이고, Memory는 사용자 또는 대화 상태입니다.

## 실패했을 때 확인할 순서

먼저 다음 진단을 다시 실행합니다.

```powershell
python .\05_memory\00_check_environment.py
```

| 증상 | 주된 원인 | 해결 방법 |
| --- | --- | --- |
| `ModuleNotFoundError` | 가상 환경 미활성화 또는 패키지 미설치 | `.venv` 활성화 후 `pip install -r requirements.txt` |
| Redis 연결 거부 | Redis Container가 중지됨 | `00_local-runtime` 서비스 실행 후 6379 Port 확인 |
| PostgreSQL 연결 거부 | PostgreSQL Container가 중지됨 | 서비스 실행 후 5433 Port 확인 |
| `user_memories` 테이블 없음 | Schema를 적용하지 않음 | `python .\00_local-runtime\database\apply_schema.py` |
| Backend 연결 실패 | Uvicorn이 실행되지 않았거나 주소가 다름 | Backend 실행 후 `BACKEND_API_URL` 확인 |
| HTTP 409 | 오래된 Session version으로 갱신 | 최신 Session을 다시 조회하고 재시도 |
| HTTP 422 | 허용되지 않은 key 또는 잘못된 요청 | Allowlist와 요청 값을 확인 |
| HTTP 503 | Backend 내부 저장소 또는 LLM 연결 실패 | Backend Terminal의 원인 메시지 확인 |
| LLM 시간 초과 | 모델 로딩 또는 응답 지연 | Provider 상태와 `REQUEST_TIMEOUT_SECONDS` 확인 |

`00_local-runtime`과 `C:\mini_agent_st\infra`는 같은 Port를 사용할 수 있으므로 두
환경을 동시에 실행하지 않습니다.

## 저장하지 않는 정보

- 비밀번호
- 카드번호와 인증번호
- 여권번호와 주민등록번호
- API Key와 Access Token
- 사용자가 저장에 동의하지 않은 민감정보

수업 예제는 저장 가능한 key를 Allowlist로 제한합니다.

## 운영 환경의 사용자 식별

예제의 `user_id`는 사용자 격리 원리를 보여주기 위한 수업용 값입니다. 실제 서비스에서는 요청 Body나 화면에서 받은 `user_id`를 그대로 신뢰하면 안 됩니다. Backend가 로그인 토큰이나 인증 Session에서 확인한 사용자 ID를 조회·수정·삭제 조건에 사용해야 합니다.

## Mini Agent learning_unit 동기화

독립 예제의 원본은 이 디렉터리입니다. `C:\mini_agent_st\mini_agent_05_memory\learning_unit`
복사본을 직접 수정하지 않고 다음 스크립트로 동기화합니다.

```powershell
# 차이만 확인
.\05_memory\sync_learning_unit.ps1 -Check

# 원본에서 Mini Agent 복사본으로 반영
.\05_memory\sync_learning_unit.ps1
```

MCP 예제는 Mini Agent Backend와 별도로 실행하므로 `learning_unit` 동기화 대상에서
제외합니다.
