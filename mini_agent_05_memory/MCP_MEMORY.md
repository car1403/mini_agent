# PostgreSQL Memory HTTP MCP

Mini Agent 03 MCP와 같은 구조로 독립 MCP Server, Backend MCP Client, Streamlit 화면을
연결합니다. 이 예제는 기존 PostgreSQL Memory Service를
재사용합니다.

```text
Streamlit 5-8
→ FastAPI /api/mcp/*
→ Streamable HTTP :8012/mcp
→ app.memory.service
→ PostgreSQL user_memories
```

## 실행 순서

### 1. PostgreSQL과 Schema

`C:\mini_agent_st\infra` 또는 과정의 `00_local-runtime` 중 하나만 실행합니다.

### 2. Memory MCP Server

```powershell
cd C:\mini_agent_st\mini_agent_05_memory
.\.venv\Scripts\Activate.ps1
$env:MCP_DEMO_USER_ID="student-01"
python .\mcp_server\memory_server.py
```

Endpoint는 `http://127.0.0.1:8012/mcp`입니다.

### 3. Backend

```powershell
cd C:\mini_agent_st\mini_agent_05_memory\backend
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

연결 확인:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/mcp/status
Invoke-RestMethod http://127.0.0.1:8000/api/mcp/tools
```

### 4. Frontend

기존 Streamlit을 실행하고 `5-8. PostgreSQL HTTP MCP` 화면을 엽니다.

## 환경 변수

```dotenv
MEMORY_MCP_URL=http://127.0.0.1:8012/mcp
MEMORY_MCP_HOST=127.0.0.1
MEMORY_MCP_PORT=8012
MCP_DEMO_USER_ID=student-01
```

## 사용자 범위

MCP Tool은 `user_id`를 받지 않습니다. Server가 `MCP_DEMO_USER_ID`를 인증된 사용자라고
가정하고 PostgreSQL의 모든 조회·수정·삭제 조건에 사용합니다. 운영 환경에서는 이
환경 변수 대신 OAuth/JWT/Bearer Token 검증 결과의 사용자 ID를 사용해야 합니다.
