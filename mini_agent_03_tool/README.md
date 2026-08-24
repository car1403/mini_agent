# Mini Agent 03 · Tool Use

01~03에서 만든 화면과 API를 유지하면서 Tool 선택, 안전 실행, 최종 답변 생성을 추가한 누적형 완성본입니다.
Stage 03은 Adapter를 배우기 전 단계이므로 OpenAI SDK를 직접 호출합니다.

```text
Streamlit app_pages
  → clients/agent_client.py
  → FastAPI routers/stage_01·02·03_router.py
  → agents/travel_agent.py가 여행 역할·지침·Tool 정의
  → agents/runtime.py
      ① LLM이 Tool과 arguments 선택
      ② Python Backend가 Tool 검증·실행
      ③ LLM이 Tool Result로 최종 답변 생성
```

## 새로 배우는 내용

- Python 함수·Tool Schema·Tool Call·Tool Result
- 현재 날씨와 미래 예보 Tool의 선택 결과 비교
- `auto`·`none`·`required` Tool Choice
- OpenAI가 반환한 Tool Call
- 누락값을 추측하지 않는 추가 질문
- Pydantic arguments 검증
- Tool 선택과 실행 분리
- Allowlist 기반 안전 실행
- 공통 Tool 오류 코드
- Tool Result를 사용한 최종 답변
- OpenAI Tool Calling 직접 실행

## 추가 메뉴

1. `Tool 선택`: 설명·Choice를 바꾸며 LLM의 원본 Tool Call과 정규화 결과를 확인합니다.
2. `Tool 실행`: arguments를 수정하고 Backend 검증 결과를 확인합니다.
3. `Agent Cycle`: 선택 → 재질문 또는 한 번 실행 → Tool Result → 최종 답변을 Trace로 확인합니다.

## Backend Router와 Swagger

기존 API URL은 유지하면서 Router를 과정 단계별로 분리했습니다.

- `stage_01_router.py`: LLM 기초·Provider·분류·Media
- `stage_02_router.py`: Prompt·Pydantic·Structured Output
- `stage_03_router.py`: Tool 선택·실행·단일 Agent Cycle

`http://127.0.0.1:8000/docs`에서도 같은 세 Tag로 구분되어 표시됩니다.

Schema도 Router 단계와 동일하게 분리합니다.

- `schemas/common.py`: Provider 이름과 공통 Message
- `schemas/stage_01.py`: LLM·분류·Media 계약
- `schemas/stage_02.py`: Prompt·Pydantic·Structured Output 계약
- `schemas/stage_03.py`: Tool arguments·선택·실행·Agent Cycle 계약

Schema 모델은 정의 위치를 분명히 알 수 있도록 각 Stage 모듈에서 직접 import합니다.

공통 환경 설정은 `core/config.py`에 두고 `.env`, 모델명, 외부 API URL과 제한값을
한곳에서 제공합니다. 이미지 분석과 음성 생성은 다음 경계로 분리합니다.

```text
stage_01_router
  → services/image_analysis_service.py 또는 speech_service.py
  → providers/openai_media.py
  → OpenAI Vision 또는 Speech API
```

Service는 입력 검증과 유스케이스를, Media Provider는 OpenAI SDK 요청·응답 변환을 담당합니다.

## Stage 03의 LLM 호출

Stage 03의 도메인 정의는 `backend/app/agents/travel_agent.py`, 공통 실행 흐름은
`backend/app/agents/runtime.py`에서 확인합니다. 이 단계에서는 Provider Adapter나
Registry를 거치지 않고 OpenAI SDK를 직접 호출합니다.

```text
Travel Agent = 무엇을 해결할지 정의
Agent Runtime = 어떻게 판단하고 실행할지 정의
```

```text
select_tool()
  → client.responses.create(..., tools=...)
  → LLM이 Tool 이름과 arguments 반환

execute_tool_safely()
  → Python Backend가 허용된 Tool 실행

_make_final_answer()
  → client.responses.create(...)
  → LLM이 Tool Result를 자연어 답변으로 변환
```

Stage 03은 실제 OpenAI Tool Calling에 집중합니다. Mock Tool 판단과 멀티 Provider
Adapter는 포함하지 않으며, 멀티 Provider Adapter는 Mini Agent 04에서 도입합니다.

실행되는 Tool은 날씨·숙소·관광지 조회용 Mock 함수뿐입니다. 실제 예약, 결제, 환불, 삭제는 실행하지 않습니다.

## ToolSpec의 역할

`tools/registry.py`의 `ToolSpec`은 LLM에게 보여줄 Tool 설명과 Backend가 실행할 함수를
연결하는 단일 등록 단위입니다. 이름·설명·Pydantic 입력 모델·실행 함수를 한곳에 등록하고,
같은 입력 모델에서 LLM용 JSON Schema와 실행 직전 검증을 모두 생성합니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_03_tool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

cd backend
uvicorn app.main:app --reload --port 8000
```

새 터미널에서 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_03_tool
.\.venv\Scripts\Activate.ps1
streamlit run .\frontend\app.py
```

Stage 03 Tool Calling에는 `OPENAI_API_KEY`가 필요합니다. Stage 01·02의 일반 생성과 구조화 출력은 기존 Provider 선택 기능을 유지합니다.

현재 과정은 Tool 하나를 선택하고 최대 한 번 실행하는 Cycle까지 다룹니다. 여러 Tool을
반복 호출하는 Agent Loop는 이후 과정에서 최대 반복 횟수와 종료 조건을 함께 추가합니다.

## 실제 날씨 Tool

날씨 Tool은 현재 상태와 미래 예보를 구분합니다.

- `get_current_weather`: 현재 기온·체감 온도·강수량·바람
- `get_weather_forecast`: 지정한 미래 날짜의 최고·최저 기온과 강수 확률

기본 `WEATHER_MODE=mock`은 인터넷 없이 결정적으로 실행됩니다. `.env`에서 다음과
같이 바꾸면 Tool 실행 단계가 Open-Meteo Geocoding API와 Forecast API를 호출합니다.

```env
WEATHER_MODE=open_meteo
```

Open-Meteo의 현재 상태는 관측소 실측값이 아니라 최신 기상 모델 기반 값입니다.
외부 API 오류가 발생하면 실제 값처럼 Mock으로 조용히 대체하지 않고 Tool 오류를
반환합니다.

## Tool Use 통합 Labs

Frontend의 `3-7. 통합 Labs`에서는 일곱 가지 Tool Use 사례를 하나의 API로 실행합니다.

```text
POST /api/labs/run
→ lab_id=auto이면 Ollama Structured Output으로 Lab 분류
→ Backend Allowlist에서 Handler 선택
→ Agent-assisted Workflow 또는 Agent-controlled Loop 실행
→ In-memory Mock Repository와 Trace 반환
```

- Agent-assisted Workflow: 주차장, 에어컨, 택배함, 재고
- Agent-controlled Loop: 카페 주문, 도서 대출, 여행 준비
- 상태 변경은 사용자의 `confirmed=true` 확인 후에만 실행합니다.
- 도메인 Agent가 자연어 arguments를 추출한 뒤 Pydantic과 Backend 정책으로 다시 검증합니다.
- 확인 전 검증된 작업은 만료되는 `pending_action`으로 저장하며 확인 시 Ollama를 다시 호출하지 않습니다.
- 명시적인 `lab_id`는 재현 가능한 실습을 위해 Ollama 분류를 건너뜁니다.
- Repository 데이터는 교육용 Mock이며 Backend를 재시작하면 초기화됩니다.

## 통합 Lab 설계 문서

1. [Tool Use Lab 아키텍처](./docs/01_lab-architecture.md)
2. [Agent와 Workflow 구분](./docs/02_agent-vs-workflow.md)
3. [Routing Agent와 Handler Allowlist](./docs/03_routing-and-allowlist.md)
4. [Pending Action과 사용자 확인](./docs/04_pending-action-and-confirmation.md)
5. [일곱 가지 Tool Use 시나리오](./docs/05_lab-scenarios.md)
