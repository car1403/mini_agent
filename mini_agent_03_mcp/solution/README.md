# Solution

완성 코드는 프로젝트 루트의 `backend`, `frontend`, `mcp_server`에 있습니다. 핵심은
Backend가 여행 Tool 함수를 import하지 않고 MCP Client API만 사용한다는 점입니다.
MCP Server는 Backend와 별도로 `8010/mcp`에서 실행됩니다.
