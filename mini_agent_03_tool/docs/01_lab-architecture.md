# Tool Use Lab 아키텍처

## 목적

이 문서는 일곱 가지 Tool Use Lab이 하나의 FastAPI Backend와 Streamlit Frontend에서
어떻게 연결되는지 설명합니다. 작은 Python 예제의 개념을 실제 애플리케이션 계층으로
확장하되 Agent가 보안 정책이나 상태 변경 권한을 소유하지 않도록 구성합니다.

## 전체 흐름

```text
Streamlit Frontend
→ POST /api/labs/run
→ Lab Router
→ Lab Routing Agent 또는 명시적 Lab 선택
→ Lab Routing Service의 Handler Allowlist
→ Agent-assisted Workflow 또는 Agent-controlled Loop
→ Tool
→ In-memory Mock Repository
→ 공통 결과와 Trace
```

## 계층별 책임

| 계층 | 책임 | 하지 않는 일 |
|---|---|---|
| Frontend | 입력, 확인, Trace 표시 | 정책 판단과 Tool 실행 |
| Router | HTTP 요청·응답과 오류 변환 | Lab 판단과 업무 규칙 |
| Routing Agent | 자연어 요청의 Lab 제안 | Handler 직접 실행 |
| Routing Service | confidence 검사와 Handler 선택 | 동적 import와 임의 함수 실행 |
| Domain Agent | arguments 추출 또는 다음 행동 선택 | 승인·인증·재고 성공 결정 |
| Workflow Service | 고정 순서, 정책, 확인 절차 | LLM 출력 무조건 신뢰 |
| Tool | 하나의 조회 또는 상태 변경 | 전체 실행 순서 결정 |
| Repository | 교육용 Mock 상태 보관 | 실제 DB·Redis·장치 운영 |

## 주요 디렉터리

```text
backend/app/
├─ routers/lab_router.py
├─ schemas/lab.py
├─ agents/
├─ services/
├─ tools/lab_tools.py
└─ repositories/lab_repository.py

frontend/
├─ app.py
├─ clients/agent_client.py
└─ app_pages/18_tool_use_labs.py
```

## 공통 API

```http
POST /api/labs/run
POST /api/labs/reset
```

`lab_id=auto`이면 Ollama가 Lab을 분류합니다. 명시적인 Lab ID는 반복 가능한 실습을
위해 분류 Agent를 거치지 않지만, Workflow 내부의 도메인 Agent는 자연어 arguments를
계속 추출합니다.

