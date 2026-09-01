# Mini Agent 05 · Memory

대화 Window, Redis 단기 상태, PostgreSQL 장기 사용자 Memory와 Hybrid 복원을
한 단계에서 학습하는 Memory 전용 미니 프로젝트입니다. 이전 01~04 화면은 반복하지 않습니다.

## 무엇을 배우나요?

```text
질문
→ 사용자별 Memory 조회
→ 질문과 관련된 Memory만 선택
→ 안전 정책 확인
→ Prompt에 추가
→ 개인화 답변
→ 사용한 Memory와 Trace 표시
```

Memory는 사용자의 선호와 현재 작업 상태를 다루고, RAG는 외부 지식 문서를
검색합니다. 화면의 `user_id`는 사용자 격리를 체험하기 위한 수업용 값입니다.

## 초보자 권장 학습 경로

### 1단계 · Python으로 핵심 이해

1. `learning_unit/01_memory_types.py`
2. `learning_unit/02_conversation_window.py`
3. `learning_unit/03_user_memory_crud.py`
4. `learning_unit/04_relevant_and_safe_memory.py`
5. PostgreSQL·Redis와 실제 LLM Provider 준비
6. Backend와 Streamlit 실행
7. Memory 저장·조회·수정·삭제
8. 저장 전·후·삭제 후 개인화 답변 비교

여기까지 진행해도 Memory의 핵심 원리는 학습할 수 있습니다.

### 2단계 · Redis와 PostgreSQL 기능 확인

1. 공용 `infra` 실행
2. `Redis·PostgreSQL` 화면에서 연결 상태 확인
3. Redis Session 저장과 TTL 확인
4. Backend 재시작 후 장기 Memory 유지 확인
5. `Hybrid Memory 복원`에서 저장소별 Trace 확인
6. `learning_unit/07~13`으로 TTL·충돌·대화·개인화·삭제 실습
7. `learning_unit/10_labs/01~03`으로 동의·보존·인증 범위 정책 확인

## 화면과 학습 예제 연결

| 화면 | 먼저 볼 독립 예제 | 핵심 내용 |
| --- | --- | --- |
| Memory 종류 | `01_memory_types.py` | 대화·상태·장기 Memory·RAG 구분 |
| 대화 Window | `02_conversation_window.py` | 오래된 요약과 최근 메시지 |
| 사용자별 대화 분리 | `03_user_memory_crud.py` | 사용자 범위와 격리 |
| Memory CRUD | `03`, `04` | 저장 정책과 사용자별 CRUD |
| 개인화 답변 | `04`, `12` | 관련 Memory만 LLM에 전달 |
| Redis·PostgreSQL | `05~10` | TTL, upsert와 대화 기록 |
| Hybrid 복원·Trace | `11` | 두 저장소의 결과와 실패 분리 |

## 실행 1 · Redis와 PostgreSQL 준비

```powershell
cd C:\mini_agent_st\infra
Copy-Item .env.example .env
docker compose up -d
```

기존 PostgreSQL Volume을 사용한다면 [공용 인프라 안내](../infra/README.md)에 따라
수정된 `init.sql`을 적용합니다.

## 실행 2 · 실제 PostgreSQL Memory와 LLM

```powershell
cd C:\mini_agent_st\mini_agent_05_memory
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

cd backend
uvicorn app.main:app --reload --port 8000
```

새 Terminal에서 Frontend를 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_05_memory
.\.venv\Scripts\Activate.ps1
streamlit run .\frontend\app.py
```

독립 Python 예제 01~04는 Docker 없이 실행할 수 있습니다. Backend와 화면의 장기
Memory는 PostgreSQL만 사용하며 개인화 답변은 OpenAI·Gemini·Ollama 중 설정한 실제
Provider를 호출합니다. Backend API는 `http://127.0.0.1:8000/docs`에서도 확인할 수 있습니다.

## Memory 전용 화면

```text
Memory 종류 → 대화 Window → 사용자 범위 → CRUD
→ 관련 Memory와 개인화 → Redis·PostgreSQL → Hybrid 복원 → HTTP MCP
```

## 프로젝트 구조

```text
mini_agent_05_memory/
├─ learning_unit/  독립 실행형 Memory 예제와 정책 Lab
├─ backend/        FastAPI, Memory Service와 저장소 Adapter
└─ frontend/       Streamlit 학습 화면
```

- `learning_unit`: 개념을 작은 Python 예제로 먼저 확인합니다.
- `backend`: Memory API, Redis, PostgreSQL과 개인화 LLM을 연결합니다.
- `frontend`: 저장 전후 상태와 Trace를 화면에서 비교합니다.

독립 예제의 원본은 `C:\aidevs\05_llm-agent-orchestration\05_memory`입니다.
`learning_unit`은 원본을 직접 수정하지 않고 `05_memory\sync_learning_unit.ps1`로 동기화합니다.

## Memory 안전 원칙

- 허용한 key만 저장합니다.
- 비밀번호·카드번호·여권번호·API Key는 key와 value 양쪽에서 차단합니다.
- 조회·수정·삭제에 항상 인증된 사용자 범위를 포함합니다.
- 외부 사용자·Session ID는 안전한 Token으로 바꿔 Redis Key에 사용합니다.
- 질문과 관련된 Memory만 LLM에 전달합니다.
- 사용자가 자신의 Memory를 확인하고 삭제할 수 있게 합니다.

민감정보 정규식은 교육용 최소 방어선입니다. 운영 환경에서는 동의, 분류, 암호화,
접근 통제와 보존 정책을 함께 적용해야 합니다.

> 운영 환경에서는 요청 Body나 화면에서 받은 `user_id`를 소유권 근거로 신뢰하지
> 않습니다. Backend가 인증 토큰이나 로그인 Session에서 확인한 사용자 ID를 사용해야
> 합니다.

## PostgreSQL HTTP MCP

독립 MCP Server와 Backend·Streamlit 연결 방법은 [MCP_MEMORY.md](./MCP_MEMORY.md)를 참고합니다.
