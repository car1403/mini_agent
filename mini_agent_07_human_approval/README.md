# Mini Agent 07 · Safe Order Agent

`mini_agent_06_agent_workflow`에서 배운 Single Agent 구조에 **변경 Tool 실행 전 사용자 승인과 Backend 안전 정책**을 적용하는 단일 사례 프로젝트입니다.

06에서는 Travel·Support·Order Agent의 경계를 비교했습니다. 07에서는 Agent 선택을 반복하지 않고 승인 필요성이 가장 명확한 Order Agent 하나에 집중합니다.

```text
상품 검색 → 재고 확인 → 금액 계산 → 주문 생성 제안
                                      ↓
                                사용자 승인
                                      ↓
                              place_order 한 번 실행
```

## Tool 위험도

| Tool | 위험도 | 실행 방식 |
| --- | --- | --- |
| `search_product` | read | 자동 실행 |
| `check_inventory` | read | 자동 실행 |
| `calculate_order_total` | read | 자동 실행 |
| `place_order` | change | 사용자 승인 후 실행 |

OpenAI Model은 Tool을 제안할 뿐 실행 권한을 갖지 않습니다.

```text
Model Tool Call
  ↓
Backend Policy
  ├─ read      → HTTP MCP Tool 자동 실행
  ├─ change    → waiting_approval
  └─ forbidden → blocked
```

## 실행 흐름

```text
사용자: 무선 키보드 2개를 주문해 줘.
  ↓
OpenAI Safe Order Agent
  ↓
search_product 자동 실행
  ↓
check_inventory 자동 실행
  ↓
calculate_order_total 자동 실행
  ↓
place_order 제안
  ↓
Backend가 실행하지 않고 승인 Snapshot 저장
  ↓
사용자 승인 또는 거절
  ↓
actor·상태·Snapshot·Allowlist·risk·중복 실행 재검사
  ↓ approve
place_order 한 번 실행
  ↓
최종 답변과 Audit Log
```

## 승인 Snapshot

```json
{
  "agent_id": "order",
  "tool": "place_order",
  "arguments": {
    "product_id": "P-KEYBOARD",
    "quantity": 2
  }
}
```

승인 API가 받은 Snapshot과 Backend에 저장된 Snapshot이 다르면 실행하지 않습니다. 승인자는 최초 실행의 `actor_id`와 같아야 하며 동일한 Tool Call은 두 번 실행하지 않습니다.

> 화면의 `actor_id` 입력은 학습용입니다. 운영 환경에서는 로그인 Session이나 검증된 Token에서 사용자 ID를 가져와야 합니다.

## 프로젝트 구조

```text
backend/app/
├─ agents/
│  ├─ order_agent.py         # Goal·Instructions·Tool 권한
│  ├─ runtime.py             # OpenAI Loop, pause와 resume
│  └─ registry.py
├─ approval/
│  ├─ policies.py            # read·change·forbidden
│  └─ store.py               # 학습용 State·멱등성·Audit
├─ mcp/client.py             # 실제 HTTP MCP tools/list·tools/call
├─ routers/agent_router.py
├─ schemas/agent.py
└─ main.py

mcp_server/order_tools_server.py
frontend/app.py
10_optional_langgraph/approval_interrupt.py
```

`approval/store.py`는 개념 학습을 위한 Process Memory 저장소입니다. 운영 환경에서는 사용자 격리와 원자적인 상태 전이를 보장하는 Database로 교체해야 합니다.

## API

| Method | Endpoint | 역할 |
| --- | --- | --- |
| GET | `/api/agents/mcp-status` | Order MCP Server와 Tool 확인 |
| POST | `/api/agents/runs` | Order Agent 실행 또는 승인 대기까지 진행 |
| GET | `/api/agents/runs/{run_id}` | 저장된 실행 State 조회 |
| POST | `/api/agents/runs/{run_id}/decision` | 승인·거절 후 재개 |
| GET | `/api/agents/runs/{run_id}/audit` | 승인과 주문 실행 Audit 조회 |

## 실행 준비

```powershell
cd C:\mini_agent_st\mini_agent_07_human_approval
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`의 `OPENAI_API_KEY`를 설정합니다.

## 실행

터미널 1 · HTTP MCP Server:

```powershell
python .\mcp_server\order_tools_server.py
```

터미널 2 · FastAPI Backend:

```powershell
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

터미널 3 · 단일 화면 Frontend:

```powershell
streamlit run frontend\app.py --server.port 8501
```

## 선택 LangGraph 비교

메인은 일반 Python State Store와 승인 API로 중단·재개합니다. 선택 예제는 같은 주문 Snapshot을 LangGraph `interrupt()`와 `Command(resume=...)`로 비교합니다.

```powershell
python .\10_optional_langgraph\approval_interrupt.py
```

LangGraph는 인증·인가·승인 대상·Tool 정책과 멱등성을 대신 보장하지 않습니다.

## 안전 정책 테스트

실제 OpenAI와 MCP Server 없이 위험도, 다른 사용자 승인, 변조 Snapshot과 중복 실행 차단을 검사합니다.

```powershell
cd C:\mini_agent_st\mini_agent_07_human_approval
pytest backend\tests\test_approval_safety.py -q
```

## 다른 Agent로 확장

같은 패턴은 다음과 같이 확장할 수 있지만 이번 프로젝트에는 구현하지 않습니다.

```text
Travel Agent  → save_itinerary 승인
Support Agent → create_return_request 승인
Order Agent   → place_order 승인 ← 현재 구현
```

다음 Multi-Agent 과정에서 여러 Agent를 연결하더라도 각 Worker의 변경 Tool은 동일한 Backend Policy와 승인 경계를 통과해야 합니다.

## 포함하지 않는 범위

- Agent 선택과 여러 Agent 구현
- 실제 결제와 외부 주문 API
- 운영용 인증 Provider와 Database
- 여러 승인자의 공동 승인
- Multi-Agent Coordinator와 Handoff
- 운영용 LangGraph Checkpointer
