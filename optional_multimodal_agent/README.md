# Optional Multimodal Agent

정규 01~09 과정과 분리된 선택 심화 완성본입니다. 이미지 분석과 TTS를 Python Agent와 LangGraph Agent의 전체 흐름에 연결하며, 실제 LLM과 PostgreSQL만 사용합니다.

```text
이미지 업로드
→ GPT 이미지 분석
→ TravelImageAnalysis
→ Python 또는 LangGraph Agent
→ MCP Tool Server·RAG·Memory
→ Human Approval
→ 최종 안내
→ 선택적 TTS
```

## 핵심 규칙

- 이미지 bytes와 Base64는 Agent State에 저장하지 않습니다.
- 구조화된 `TravelImageAnalysis`만 Agent에 전달합니다.
- Python Agent는 분석 결과를 여행 계획 입력과 결과에 포함합니다.
- LangGraph는 `use_image_analysis` Node에서 분석 결과를 State에 병합합니다.
- TTS 실패는 Agent 실행 성공과 승인 기록을 취소하지 않습니다.
- Agent 실행 이력, Memory, RAG 문서와 LangGraph Checkpoint를 PostgreSQL에 저장합니다.
- 실제 예약과 결제는 수행하지 않습니다. 승인은 예약 요청 초안을 기록하는 단계입니다.

## API

| API | 역할 |
|---|---|
| `POST /api/media/image-analysis` | 이미지 분석만 실행 |
| `POST /api/media/agent-runs` | 이미지 분석 후 Agent 실행 |
| `POST /api/media/tts` | 최종 텍스트를 MP3로 변환 |
| `GET /api/tools/status` | MCP Tool Server 연결과 Tool 목록 확인 |
| `POST /api/tools/run` | MCP Tool Server를 통해 Tool 실행 |

## 실행

Python 3.11 이상을 사용합니다.

```powershell
cd C:\mini_agent\optional_multimodal_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`에 사용할 Provider의 인증정보와 `DATABASE_URL`을 입력하고, `docker ps`에서
`aidevs-pgvector` PostgreSQL 컨테이너가 실행 중인지 확인합니다. `APP_MODE=real`,
`STORAGE_MODE=postgres` 외의 값과 `mock` Provider는 허용되지 않습니다.
기존 PostgreSQL Volume을 사용하는 경우에는 이 프로젝트의 `sql/init.sql`을 기존
데이터베이스에 직접 적용해야 `optional_multimodal_agent_runs`와
`optional_multimodal_travel_tool_data`를 사용할 수
있습니다. LangGraph Checkpoint 테이블은 Backend 시작 시 자동 준비됩니다.

```powershell
python .\sql\setup_database.py
```

환경별 필수 값은 다음과 같습니다.

| 기능 | 필수 설정 |
|---|---|
| PostgreSQL | `DATABASE_URL` |
| OpenAI LLM | `OPENAI_API_KEY`, `OPENAI_MODEL` |
| 이미지 분석·TTS | `OPENAI_API_KEY`, `OPENAI_VISION_MODEL`, `OPENAI_TTS_MODEL` |
| Gemini LLM | `GEMINI_API_KEY`, `GEMINI_MODEL` |
| Ollama LLM | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` |
| MCP Tool Server | `TOOLS_MCP_URL`, `MCP_HOST`, `MCP_PORT` |

```powershell
# 터미널 1
cd C:\mini_agent\optional_multimodal_agent
.\.venv\Scripts\python.exe .\mcp_server\travel_tools_server.py

# 터미널 2
cd C:\mini_agent\optional_multimodal_agent\backend_python
..\.venv\Scripts\python.exe -m app.main

# 터미널 3
cd C:\mini_agent\optional_multimodal_agent\backend_langgraph
..\.venv\Scripts\python.exe -m app.main

# 터미널 4
cd C:\mini_agent\optional_multimodal_agent
.\.venv\Scripts\python.exe -m streamlit run .\frontend\app.py
```

프런트엔드의 `이미지와 음성` 메뉴에서 전체 흐름을 실행합니다. 실제 이미지 분석과 TTS에는 `OPENAI_API_KEY`가 필요합니다.
