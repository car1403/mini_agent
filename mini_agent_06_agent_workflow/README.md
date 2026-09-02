# Mini Agent 06 · Independent Single Agent Service

`06_agent-workflow`에서 배운 Goal, Tool, State, Agent Loop와 종료 조건을 여러 개의 **독립적인 Single Agent**에 적용하는 미니 프로젝트입니다.

```text
사용자
├─ Travel Agent 직접 선택
├─ Customer Support Agent 직접 선택
└─ Order Assistant Agent 직접 선택
```

Agent가 여러 개 존재하지만 Agent 간 메시지, Coordinator, Handoff와 공유 State가 없으므로 Multi-Agent Orchestration이 아닙니다.

## 이 프로젝트의 목적

```text
03 Tool·MCP
→ Tool을 안전하게 발견하고 실행

06 Agent Workflow
→ 하나의 Agent가 Result를 보고 재판단

Mini Project 06
→ Goal과 Tool 권한이 다른 Single Agent들을 독립적으로 서비스

다음 Multi-Agent 과정
→ Coordinator가 Agent 선택·위임·결과 전달을 관리
```

## 세 Single Agent

| Agent | Goal | 허용된 MCP Tool |
| --- | --- | --- |
| Travel Agent | 날씨에 맞는 장소 추천 | `get_weather`, 실내·야외 장소 검색 |
| Customer Support Agent | 주문 상태와 반품 정책 안내 | `get_order_status`, `search_return_policy` |
| Order Assistant Agent | 상품·재고·예상 금액 안내 | 상품 검색, 재고 확인, 금액 계산 |

각 Agent는 자신의 Tool만 OpenAI에 전달합니다. Travel Agent가 주문 Tool을 호출하거나 Order Agent가 고객 지원 Tool을 호출할 수 없습니다.

## 공통 Python Agent Runtime

세 Agent는 [공통 Runtime](backend/app/agents/runtime.py)을 사용하지만 서로의 실행에는 참여하지 않습니다.

```text
선택한 Agent Profile
├─ Goal
├─ Instructions
├─ Allowed Tools
└─ Max Steps
        ↓
공통 순수 Python Agent Loop
Model → MCP Tool → Result → Model → 완료 또는 중단
```

## AI Agent, Workflow, Runtime과 MCP

| 영역 | 책임 |
| --- | --- |
| AI Agent | Goal과 Result를 보고 다음 Tool 또는 최종 답변 선택 |
| Agent Runtime | Loop, Tool Result 전달, 최대 단계와 종료 이유 관리 |
| Backend Workflow | Agent 선택, Tool Allowlist와 arguments 검증 |
| HTTP MCP Server | Backend 밖에서 Tool Schema와 실제 실행 제공 |

AI Agent가 순서를 계획할 수 있고 Python Runtime 없이 직접 동작하는 것처럼 보일 수 있지만, 실제 Tool 실행과 반복을 연결하는 애플리케이션 코드는 항상 필요합니다. 반드시 강제할 권한과 입력 검증은 Model이 아니라 Backend가 책임집니다.

## 현재와 다음 과정의 차이

현재:

```text
사용자가 Agent 선택
→ 선택된 Agent 하나만 독립 실행
→ 실행 종료
```

다음 Multi-Agent Orchestration:

```text
사용자 요청
→ Coordinator가 Agent 선택
→ Agent에 Goal과 Context 위임
→ Handoff 또는 결과 집계
→ 전체 시스템 종료
```

| 현재 프로젝트 | 다음 과정 |
| --- | --- |
| 사용자가 Agent 선택 | Coordinator가 Agent 선택 |
| 독립 State | 공유 State와 비공개 State |
| Agent 간 호출 없음 | Handoff와 결과 전달 |
| Agent별 종료 | 전체 Orchestration 종료 |
| Agent별 Trace | 전체 시스템 Trace |

## 프로젝트 구조

```text
backend/app/
├─ agents/
│  ├─ runtime.py              # 공통 순수 Python Agent Loop
│  ├─ travel_agent.py
│  ├─ support_agent.py
│  ├─ order_agent.py
│  └─ registry.py
├─ mcp/client.py              # 실제 tools/list와 tools/call
├─ providers/openai.py
├─ services/agent_service.py
├─ routers/agent_router.py
└─ main.py

mcp_server/business_tools_server.py
frontend/app.py
```

## 실행 준비

```powershell
cd C:\mini_agent_st\mini_agent_06_agent_workflow
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`의 `OPENAI_API_KEY`를 실제 값으로 설정합니다. Backend, MCP Server와 Frontend는
모두 프로젝트 루트의 같은 `.env`를 읽으므로 필요하면 Model, 포트와 API 주소도 이
파일에서 변경할 수 있습니다.

## 실행 순서

터미널 1 · HTTP MCP Server:

```powershell
python .\mcp_server\business_tools_server.py
```

터미널 2 · FastAPI Backend:

```powershell
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

터미널 3 · 단일 화면 Frontend:

```powershell
streamlit run frontend\app.py --server.port 8501
```

브라우저에서 `http://127.0.0.1:8501`을 열고 Agent를 선택합니다.

## 테스트

외부 OpenAI API나 MCP Server를 실행하지 않고 Runtime의 종료 조건과 API 입력 검증을
확인합니다.

```powershell
pytest -q
```

## 포함하지 않는 범위

- Agent가 다른 Agent를 호출하는 기능
- Coordinator, Router Agent와 Handoff
- Agent 간 공유 State와 결과 집계
- Human Approval과 Checkpoint
- RAG, 장기 Memory, Database와 인증

이 기능들은 다음 Multi-Agent Orchestration 또는 이후 운영 과정에서 다룹니다.
