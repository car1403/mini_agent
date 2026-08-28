# stdio MCP RAG Agent

기존 RAG 검색을 stdio MCP Tool로 감싸고 Ollama Agent가 Tool을 선택하는 예제입니다.
Redis Cache는 사용하지 않습니다.

```text
사용자 질문
  → Ollama가 MCP Tool 선택
  → stdio MCP Server의 search_knowledge_base 실행
  → Ollama Embedding → pgvector 검색
  → Tool Result를 받은 Ollama가 최종 답변
```

먼저 Backend 또는 Frontend에서 `POST /api/rag/index`를 한 번 실행하여 교육 문서를
pgvector에 저장합니다. 그 다음 프로젝트 가상환경에서 Agent를 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag
.\.venv\Scripts\Activate.ps1
python .\mcp_rag_example\rag_agent.py
```

`rag_agent.py`가 `rag_stdio_server.py`를 자식 프로세스로 자동 실행하므로 MCP Server를
별도 터미널에서 실행할 필요는 없습니다.
