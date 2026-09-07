# Travel Tools MCP Server

날씨, 숙소, 관광지 Tool을 Backend 프로세스와 분리해 제공하는 Streamable HTTP
MCP Server입니다. Tool 데이터는 PostgreSQL의
`optional_multimodal_travel_tool_data`에서 조회합니다.

```powershell
cd C:\mini_agent\optional_multimodal_agent
.\.venv\Scripts\python.exe .\mcp_server\travel_tools_server.py
```

기본 주소는 `http://127.0.0.1:8020/mcp`입니다.
