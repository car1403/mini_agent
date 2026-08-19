# Mini Agent 02 · Prompt와 Structured Output

`mini_agent_01_llm`의 메뉴와 API를 유지하면서 `02_prompt-and-structured-output`의
단위 예제를 실제 FastAPI·Streamlit 기능으로 추가한 누적 미니 프로젝트입니다.

```text
Prompt 네 부분
→ 일반 LLM 응답
→ Pydantic Schema 검증
→ LLM Structured Output
→ Provider별 동일 계약 비교
```

## 이번 단계에서 추가

- Role, Instruction, Context, Constraint Prompt 조립
- 정상 JSON, 잘못된 범위, 계약에 없는 필드 검증
- 생성형 `TravelPlan`과 분류형 `SupportTicket` Pydantic Schema
- Prompt 구성 화면의 여행·고객 지원·회의 예제
- Template, Zero/Few-shot, 구분자, 메시지 역할, Before/After 실제 호출 예제
- Prompt 구성 화면의 Output Format과 Before/After 실제 응답 비교
- Schema별 JSON 검증과 입력 예제
- Schema를 선택하는 Mock·Gemini·GPT·Ollama/Llama Structured Output
- Provider별 성공, 지연 시간, 실패 비교

기본 Provider는 `mock`입니다. API Key나 Ollama 없이도 모든 개념과 완성 화면을
확인한 다음 실제 Provider를 선택적으로 연결할 수 있습니다.

## Structured Output API

- `POST /api/structured/validate`: 선택한 Schema로 일반 JSON을 검증합니다.
- `POST /api/structured/generate`: 선택한 Schema로 한 Provider의 결과를 생성합니다.
- `POST /api/structured/compare`: 여러 Provider의 동일 Schema 결과를 비교합니다.

요청의 `schema_type`은 `travel_plan` 또는 `support_ticket`입니다. 이전 실습과의
호환성을 위해 `/api/structured/travel-plan`도 유지하지만, 새 코드에서는 범용
`/api/structured/generate`를 사용합니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_02_structured_output
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

터미널 1:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

터미널 2:

```powershell
cd C:\mini_agent_st\mini_agent_02_structured_output
streamlit run .\frontend\app.py
```

## 수업 운영

- Build Track: `learning_unit → starter → backend → frontend` 순서로 구현합니다.
- Demo Track: 시간이 부족하면 `solution`을 읽고 완성된 Backend·Frontend를 실행합니다.

실제 Provider 비교 순서는 `Mock → Gemini → GPT → Ollama/Llama`를 권장합니다.
Cloud 호출은 비용과 사용량을 확인하고, Ollama는 Docker Container와 모델이 준비된
경우에 실행합니다. 한 Provider가 실패해도 비교 결과에 오류가 남습니다.

## 아직 구현하지 않음

LangChain, Tool, RAG, Memory, Agent Workflow, LangGraph, 로그인은 이후 단계에서
하나씩 누적합니다.
