# Mini Agent 03 · MCP

`mini_agent_03_tool`의 여행 Tool을 MCP Server로 분리한 작은 실전 프로젝트입니다.
FastAPI Backend는 Tool 함수를 직접 import하지 않고 MCP Client를 통해 Tool을 발견하고
호출합니다.

```text
Streamlit :8501
  → FastAPI Backend :8000
    → Travel MCP Server :8010/mcp (Streamable HTTP)
    → Policy MCP Server (stdio 자식 프로세스)
    → OpenAI Responses API가 한 번에 Tool 하나를 선택
      → Tool 결과를 돌려주고 필요한 만큼 반복
```

Travel Server는 Backend와 독립된 프로세스와 포트에서 실행합니다. Policy Server는
Backend가 stdio 자식 프로세스로 실행합니다. 하나의 Agent가 두 Transport를 함께
사용하면서 Server prefix와 라우팅, 순차 Tool 의존성을 학습합니다.

## stdio 학습 예제에서 달라지는 점

Tool 구현과 MCP의 `tools/list`·`tools/call` 의미는 바뀌지 않습니다. 달라지는 것은
Server의 실행 주체와 메시지를 전달하는 Transport입니다.

| 구분 | Policy MCP | Travel MCP |
| --- | --- | --- |
| Transport | stdio | Streamable HTTP |
| Server 실행 | Backend가 자식 프로세스로 자동 실행 | 첫 번째 터미널에서 독립 실행 |
| 주소 | Python 파일과 실행 명령 | `http://127.0.0.1:8010/mcp` |
| 포트 | 없음 | 8010 |
| Server 수명 | Client Session과 함께 종료 | Backend와 무관하게 계속 실행 |
| 제공 Tool | 호텔 정책 조회 | 날씨·호텔 검색 |

```text
stdio
Backend → 자식 MCP Server

Streamable HTTP
Backend :8000 → 네트워크 → MCP Server :8010
```

Frontend는 MCP Server를 직접 호출하지 않습니다. 사용자의 요청은 항상 Agent
Backend를 거치며, GPT가 Tool을 제안하고 Backend가 권한 확인·MCP 호출·결과 전달을
담당합니다. GPT는 MCP Tool을 직접 실행하지 않습니다.

## 제공 기능

- `GET /health`: Backend 상태
- `GET /api/mcp/status`: 별도 MCP Server 연결 상태
- `GET /api/mcp/tools`: MCP Server가 공개한 Tool 발견
- `GET /api/mcp/resources`: MCP Resource 발견
- `POST /api/mcp/run`: 질문 → Tool 선택 → MCP 호출 → 답변 Trace
- `GET /api/mcp/baggage-policy`: MCP Resource 읽기

## 실습 및 실행 순서

세 프로세스의 실행 순서를 지킵니다. 앞 단계가 정상인지 확인한 뒤 다음 단계로
이동하면 어느 연결에서 문제가 발생했는지 쉽게 구분할 수 있습니다.

```text
0. 구조 확인
→ 1. 가상환경 준비
→ 2. OpenAI 환경변수 설정
→ 3. MCP Server 실행 (:8010)
→ 4. Backend 실행 (:8000)
→ 5. Backend에서 MCP 연결 확인
→ 6. GPT·Tool·Resource API 확인
→ 7. Frontend 실행 (:8501)
→ 8. 화면에서 전체 Trace 확인
```

### 0단계 · 호출 구조 확인

코드를 실행하기 전에 다음 네 파일의 역할을 확인합니다.

| 파일 | 역할 |
| --- | --- |
| `mcp_server/travel_server.py` | 날씨·호텔 Tool과 Resource를 공개하는 HTTP Server |
| `mcp_server/policy_stdio_server.py` | 호텔 ID로 정책을 조회하는 stdio Server |
| `backend/app/mcp_client.py` | 두 Transport의 Session을 생성·관리하는 Client |
| `backend/app/agent.py` | Tool prefix·라우팅과 순차 Agent Loop 관리 |

### 1단계 · 가상환경과 패키지 준비

최초 한 번만 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_03_mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

이미 `.venv`를 만들었다면 다음 수업부터는 활성화만 합니다.

```powershell
cd C:\mini_agent_st\mini_agent_03_mcp
.\.venv\Scripts\Activate.ps1
```

### 2단계 · OpenAI 환경변수 설정

`.env.example`을 `.env`로 복사하고 발급받은 API Key를 입력합니다.

```powershell
Copy-Item .env.example .env
```

```env
OPENAI_API_KEY=발급받은_API_KEY
OPENAI_MODEL=gpt-4.1-mini
```

API Key는 Git에 Commit하거나 화면과 로그에 출력하지 않습니다.

### 3단계 · MCP Server 실행

첫 번째 터미널을 열고 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_03_mcp
.\.venv\Scripts\Activate.ps1
python .\mcp_server\travel_server.py
```

이 터미널은 종료하지 않습니다. MCP endpoint는
`http://127.0.0.1:8010/mcp`입니다. 콘솔에 `127.0.0.1:8010`에서 서버가 실행됐다는
안내가 표시되면 다음 단계로 이동합니다.

### 4단계 · FastAPI Backend 실행

두 번째 터미널을 열고 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_03_mcp
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --port 8000
```

Backend 자체 상태를 확인합니다.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

예상 결과의 핵심 값은 다음과 같습니다.

```text
status      : ok
mcp_servers : travel=streamable-http, policy=stdio
```

### 5단계 · Backend와 MCP Server 연결 확인

세 번째 PowerShell 터미널에서 실행합니다.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/mcp/status
```

정상이라면 `status=connected`, `tool_count=3`이 표시됩니다. 여기서 503이 발생하면
Frontend를 실행하기 전에 첫 번째 터미널의 MCP Server와 `TRAVEL_MCP_URL`을 먼저
확인합니다.

### 6단계 · GPT, Tool과 Resource API 확인

MCP Server가 공개한 Tool을 확인합니다.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/mcp/tools |
    ConvertTo-Json -Depth 10
```

`travel__get_current_weather`, `travel__search_hotels`,
`policy__get_hotel_policy`와 각 arguments Schema가 표시돼야 합니다.

Agent 전체 흐름을 호출합니다.

```powershell
$body = @{
    question = "부산 날씨와 15만원 이하 호텔을 찾고 호텔 정책도 알려 주세요."
} | ConvertTo-Json
Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/api/mcp/run `
    -Method Post `
    -ContentType "application/json" `
    -Body $body |
    ConvertTo-Json -Depth 10
```

응답에서 다음 순서를 확인합니다.

```text
available_tools
→ travel__get_current_weather
→ travel__search_hotels
→ 검색 결과에서 hotel_id 획득
→ policy__get_hotel_policy(hotel_id)
→ Function Call이 없는 응답에서 Loop 종료
→ 일반적으로 llm_calls = Tool 실행 수 + 1
→ answer
```

Resource도 확인합니다.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/mcp/baggage-policy |
    ConvertTo-Json -Depth 10
```

### 7단계 · Streamlit Frontend 실행

네 번째 터미널을 열고 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_03_mcp
.\.venv\Scripts\Activate.ps1
streamlit run frontend\app.py --server.port 8501
```

브라우저에서 `http://127.0.0.1:8501`을 엽니다. FastAPI Swagger는
`http://127.0.0.1:8000/docs`입니다.

### 8단계 · 화면 실습

다음 순서로 버튼을 실행합니다.

1. 상단의 MCP 연결 상태가 `connected`인지 확인합니다.
2. `MCP Tool 발견`을 눌러 Tool 이름과 Schema를 확인합니다.
3. 기본 질문으로 MCP Agent를 실행합니다.
4. 한 Round에 Tool이 하나씩 실행되는지 확인합니다.
5. 호텔 검색 결과의 `hotel_id`가 Policy Tool arguments로 전달되는지 확인합니다.
6. 질문을 `서울에서 15만원 이하 호텔을 찾아 주세요.`로 바꿔 Tool 선택을 비교합니다.
7. `수하물 정책 읽기`로 Tool이 아닌 Resource 조회를 확인합니다.

### 종료 순서

각 실행 터미널에서 `Ctrl+C`를 누릅니다.

```text
Frontend 종료
→ Backend 종료
→ MCP Server 종료
```

MCP Server만 먼저 종료한 뒤 `/api/mcp/status`를 다시 호출하면 Backend가 503을
반환하는 연결 실패 실습도 할 수 있습니다.

## 비교 포인트

| `mini_agent_03_tool` | `mini_agent_03_mcp` |
| --- | --- |
| Backend가 Tool 함수를 직접 import | Backend는 MCP Client만 사용 |
| Tool 목록이 Agent 코드에 고정 | `tools/list`로 서버에서 발견 |
| Python 함수 직접 호출 | `tools/call` 프로토콜 호출 |
| 앱 내부 Context | URI 기반 MCP Resource |

## 환경변수

```env
BACKEND_API_URL=http://127.0.0.1:8000
TRAVEL_MCP_URL=http://127.0.0.1:8010/mcp
MCP_HOST=127.0.0.1
MCP_PORT=8010
OPENAI_API_KEY=발급받은_API_KEY
OPENAI_MODEL=gpt-4.1-mini
```

Frontend는 Backend만 호출하고 MCP Server URL과 실행 권한은 Backend가 관리합니다.

Backend는 두 MCP Server에서 발견한 Tool Schema에 Server prefix를 붙여 OpenAI
Responses API에 전달합니다. `parallel_tool_calls=False`이므로 GPT는 한 Round에 Tool
하나를 제안합니다. Backend가 Tool 결과를 돌려주면 GPT가 다음 Tool을 선택하며,
Function Call 없이 답변할 때까지 Agent Loop를 반복합니다.
