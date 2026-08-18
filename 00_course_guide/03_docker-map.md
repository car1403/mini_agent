# Docker 사용 단계

Docker는 모든 단계의 시작 조건이 아닙니다. 먼저 Mock·Memory 저장소로 개념을
확인하고, 실제 Local LLM이나 저장소를 비교할 때만 필요한 서비스를 실행합니다.

| 단계 | 기본 실습 | Docker 선택 확장 |
| --- | --- | --- |
| 01 LLM | Mock·GPT·Gemini | Ollama/Llama 비교 |
| 02 Structured Output | Mock·Cloud Provider | Ollama/Llama 비교 |
| 03 Tool Use | Mock Tool | Ollama/Llama Tool Calling 비교 |
| 04 RAG | Python Chunk·검색 | Ollama Embedding + PostgreSQL/pgvector |
| 05 Memory | Memory 저장소 | Redis 단기 상태 + PostgreSQL 장기 Memory |
| 06 LangGraph | Memory Checkpointer | 필요할 때 기존 Local 서비스 연결 |
| 07 Human Approval | Mock 실행·Memory 상태 | 필요할 때 PostgreSQL·Redis 연결 |
| 08 Evaluation | Mock 시나리오·Trace | Provider·저장소별 결과 비교 |

## Mini Agent 공용 환경을 사용할 때

```powershell
cd C:\mini_agent_st\infra
Copy-Item .env.example .env
docker compose up -d
docker compose ps
```

Mini Agent Compose는 `mini-agent-*` Container를 만듭니다. 강의
`00_local-runtime`의 개별 `aidevs-*` Container와 같은 Host Port를 사용하므로
두 환경을 동시에 실행하지 않습니다.

```powershell
# 개별 강의 환경을 사용 중이었다면 먼저 중지
cd C:\aidevs\05_llm-agent-orchestration
.\00_local-runtime\scripts\stop-local-services.ps1

# 그다음 Mini Agent Compose 시작
cd C:\mini_agent_st\infra
docker compose up -d
```

일반 종료는 `docker compose stop`을 사용합니다. `docker compose down -v`는
학습 데이터와 다운로드한 모델을 삭제할 수 있으므로 수업의 일반 종료 명령으로
사용하지 않습니다.
