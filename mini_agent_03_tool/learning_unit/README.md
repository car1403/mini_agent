# 03 Tool Use

Tool Use는 LLM이 필요한 함수와 arguments를 제안하고, Backend가 검증한 뒤 허용된
함수만 실행해 그 결과로 최종 답변을 만드는 과정입니다. Tool Call은 실행 명령이
아니라 제안이며 실행 권한은 항상 Backend에 있습니다.

```text
사용자 질문 → LLM Tool Call → 누락 정보 확인 → Backend 검증
→ Allowlist Tool 실행 → Tool Result → LLM 최종 답변
```

## Tool과 Agent는 무엇이 다른가?

Tool은 특정 작업을 수행하는 **기능**이고, Agent는 사용자 목표를 달성하기 위해
상태를 확인하면서 다음 행동을 선택하는 **실행 구조**입니다.

```text
Tool  = 날씨 조회, 호텔 검색, 문서 검색처럼 한 가지 일을 수행하는 함수
Agent = 사용자 요청을 해석하고 Tool 사용·재질문·종료를 반복해서 결정하는 실행 주체
```

| 구분 | Tool | Agent |
| --- | --- | --- |
| 질문 | 무엇을 실행할 수 있는가? | 목표를 위해 다음에 무엇을 해야 하는가? |
| 형태 | Python 함수, API, Database 조회 | LLM + 상태 + Tool + 실행 Loop + 종료 조건 |
| 입력 | 검증된 arguments | 사용자 메시지와 현재 실행 상태 |
| 출력 | 조회하거나 계산한 데이터 | 사용자 목표에 맞춘 최종 답변 또는 다음 행동 |
| 판단 | 보통 하지 않음 | Tool 선택, 재질문, 재시도, 종료를 판단 |
| 실행 횟수 | 호출 한 번에 한 번 실행 | 필요하면 여러 Tool을 여러 번 호출 |
| 권한 | Backend가 명시적으로 허용 | Agent도 Backend가 허용한 Tool만 사용 가능 |

Tool 하나를 호출했다고 해서 반드시 Agent인 것은 아닙니다. Backend가 정해진
순서대로 함수를 호출하면 일반 Workflow입니다. 반면 LLM이 현재 상태를 보고 다음
Tool, 재질문 또는 종료를 선택하고 그 과정이 반복되면 Agent에 가까워집니다.

```text
고정 Workflow
사용자 입력 → 항상 날씨 조회 → 항상 안내문 생성 → 종료

Agent
사용자 입력 → 정보 충분한가?
             ├─ 아니오: 사용자에게 도시 재질문
             └─ 예: 어떤 Tool이 필요한가?
                    ├─ 날씨 조회
                    ├─ 호텔 검색
                    └─ Tool 불필요: 바로 답변
                         ↓
                    결과가 충분한가?
                    ├─ 아니오: 다른 Tool 또는 재질문
                    └─ 예: 최종 답변 후 종료
```

## 사용자 메시지부터 최종 답변까지

다음 요청을 예로 살펴봅니다.

```text
부산의 현재 날씨를 확인해서 여행 준비물을 알려 주세요.
```

### 1. 첫 번째 LLM 호출

Backend는 System Prompt와 사용자 메시지를 `messages`로, 사용 가능한 Tool의
Schema를 `tools`로 전달합니다.

```python
messages = [
    {
        "role": "system",
        "content": "현재 정보가 필요하면 허용된 조회 Tool을 사용하세요.",
    },
    {
        "role": "user",
        "content": "부산의 현재 날씨를 확인해서 여행 준비물을 알려 주세요.",
    },
]

weather_tool_schema = {
    "name": "get_current_weather",
    "description": "도시의 현재 날씨를 조회합니다.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "조회할 도시"},
        },
        "required": ["city"],
        "additionalProperties": False,
    },
}
```

사용자 메시지는 Tool을 선택하고 arguments를 만드는 근거입니다. LLM은 현재
날씨가 필요하다는 사실과 `부산`이라는 값을 읽고 다음 Tool Call을 제안합니다.

```json
{
  "name": "get_current_weather",
  "arguments": {
    "city": "부산"
  }
}
```

### 2. Backend 검증과 Tool 실행

Tool Call은 LLM의 제안일 뿐 아직 실행된 것이 아닙니다. Backend는 Tool 이름이
Allowlist에 있는지 확인하고 arguments를 Pydantic으로 검증한 뒤 함수를 실행합니다.

```python
class WeatherArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: str = Field(min_length=1)


tool_functions = {
    "get_current_weather": get_current_weather,
}

if tool_call["name"] not in tool_functions:
    raise ValueError("허용되지 않은 Tool입니다.")

arguments = WeatherArguments.model_validate(tool_call["arguments"])
tool_result = tool_functions[tool_call["name"]](**arguments.model_dump())
```

Tool Result는 자연어 답변이 아니라 Backend가 조회한 근거 데이터일 수 있습니다.

```json
{
  "city": "부산",
  "condition": "비",
  "temperature": 18,
  "precipitation_probability": 80,
  "source": "weather-api"
}
```

### 3. 두 번째 LLM 호출과 최종 답변

Backend는 원래 사용자 메시지, LLM의 Tool Call, Tool Result를 같은 대화에 넣어
LLM을 다시 호출합니다. 원래 메시지를 유지해야 LLM이 단순히 날씨만 설명하지 않고
사용자의 최종 목적이었던 여행 준비물까지 안내할 수 있습니다.

```text
System: 현재 정보가 필요하면 허용된 조회 Tool을 사용하세요.
User: 부산의 현재 날씨를 확인해서 여행 준비물을 알려 주세요.
Assistant: get_current_weather(city="부산") 호출 제안
Tool: 부산, 비, 18도, 강수 확률 80%
Assistant: 현재 부산은 비가 오고 18도입니다. 우산과 얇은 겉옷을 준비하세요.
```

각 단계의 담당은 다음과 같습니다.

| 단계 | 담당 | 만들어지는 값 |
| --- | --- | --- |
| 사용자 요청 | 사용자 | User Message |
| Tool 설명 | 개발자 | Tool Schema |
| Tool 선택과 인자 제안 | LLM | Tool Call |
| Tool 이름·인자 검증 | Backend | 검증된 arguments |
| 함수·API 실행 | Backend와 외부 시스템 | Tool Result |
| Result 기반 답변 생성 | LLM | 최종 자연어 답변 |
| 응답 정책·Schema 검증 | Backend | 사용자에게 보낼 안전한 응답 |

## Tool만 필요한 경우와 Agent가 필요한 경우

정해진 함수 한 번이면 끝나는 작업에는 Agent Loop가 필요하지 않습니다.

```python
# Tool만 사용하는 결정적 Workflow
arguments = WeatherArguments(city=user_city)
result = get_current_weather(**arguments.model_dump())
return format_weather(result)
```

다음처럼 실행 중에 판단이 반복되는 경우에는 Agent 구조가 유용합니다.

- 사용자 요청만으로 필요한 Tool을 미리 결정하기 어려운 경우
- 첫 번째 Tool Result를 보고 두 번째 Tool을 선택해야 하는 경우
- 필수 정보가 없으면 추측하지 않고 사용자에게 재질문해야 하는 경우
- 검색 결과가 부족하면 다른 검색어로 다시 시도해야 하는 경우
- 충분한 근거가 모였는지 판단한 뒤 종료해야 하는 경우

Agent를 사용하더라도 실행 권한까지 LLM에 넘기면 안 됩니다. 최대 반복 횟수,
허용 Tool, arguments Schema, timeout, 사용자별 권한, 승인 필요 행동은 Backend가
결정해야 합니다.

## Structured Output과 Tool Calling 비교

두 기능 모두 Schema를 사용할 수 있지만 목적이 다릅니다.

| 구분 | Structured Output | Tool Calling |
| --- | --- | --- |
| 목적 | LLM 최종 결과의 데이터 구조를 고정 | 외부 함수 실행을 요청 |
| LLM 출력 | Schema에 맞는 최종 데이터 | Tool 이름과 arguments |
| 외부 실행 | 반드시 필요하지 않음 | Backend Tool 실행 필요 |
| 실행 후 재호출 | 보통 한 번의 생성과 검증 | Tool Result를 넣어 LLM을 다시 호출할 수 있음 |

```text
Structured Output
User Message → LLM이 Schema에 맞는 결과 생성 → Pydantic 검증 → 사용

Tool Calling
User Message → LLM Tool Call → Backend 실행 → Tool Result
→ LLM 최종 답변 → Backend 검증 → 사용
```

## 학습 목표

- Tool Schema·Tool Call·Tool Result를 구분합니다.
- 사용자 메시지와 Tool Choice가 실제 LLM 선택에 미치는 영향을 비교합니다.
- Provider 원본 Tool Call과 정규화된 arguments를 관찰합니다.
- 누락값을 추측하지 않고 사용자에게 추가 질문합니다.
- Allowlist와 Pydantic 검증 후에만 Tool을 실행합니다.
- Tool Result만 사용해 최종 답변을 만들고 전체 Trace를 확인합니다.

## 예제 순서

| 순서 | 파일 | Backend | 핵심 내용 |
|---:|---|---|---|
| 00 | `00_tool_use_concepts.py` | 불필요 | 함수·Schema·Call·Result |
| 01 | `01_tool_schema_validation.py` | 불필요 | arguments 계약 검증 |
| 02 | `02_mock_tool_selection.py` | 불필요 | 선택과 실행 분리 |
| 03 | `03_mock_tool_loop.py` | 불필요 | System·User·Tool Call·Result·최종 답변 전체 흐름 |
| 04 | `04_current_vs_forecast_selection.py` | 필요 | 현재 날씨·미래 예보 Tool 선택 비교 |
| 05 | `05_real_tool_call_inspection.py` | 필요 | 원본 Call·arguments·auto/none |
| 06 | `06_missing_arguments_and_clarification.py` | 필요 | 누락 정보 재질문 |
| 07 | `07_safe_tool_execution.py` | 불필요 | Allowlist·검증·결정적 답변 조립 |
| 08 | `08_real_tool_loop.py` | 필요 | 실제 전체 Loop Trace |

## 실전 Lab

기본 예제 이후에는 API 키 없이 실행할 수 있는 여섯 가지 업무 시나리오로 안전한 Tool 설계를 연습합니다. 자세한 실습 내용과 확장 과제는 [`10_labs/README.md`](10_labs/README.md)를 참고합니다.

| Lab | 파일 | 핵심 개념 |
|---:|---|---|
| 01 | `01_parking_gate_tool.py` | 조회 Tool과 상태 변경 Tool 분리, 서버 승인 |
| 02 | `02_air_conditioner_workflow.py` | Agent가 필요 없는 규칙 기반 Workflow |
| 03 | `03_parcel_locker_authorization.py` | 인증, 만료, 중복 실행 방지 |
| 04 | `04_cafe_argument_extraction.py` | arguments 추출, 누락값 재질문 |
| 05 | `05_library_multi_tool_rules.py` | 여러 Tool Result와 백엔드 업무 규칙 |
| 06 | `06_inventory_reservation_concurrency.py` | 실행 직전 재검증, 동시성, 낙관적 잠금 |

## 실행

로컬 예제부터 실행합니다.

```powershell
cd C:\aidevs\05_llm-agent-orchestration\03_tool-use
python .\00_tool_use_concepts.py
python .\01_tool_schema_validation.py
python .\02_mock_tool_selection.py
python .\03_mock_tool_loop.py
python .\07_safe_tool_execution.py
```

실전 Lab도 같은 위치에서 실행합니다.

```powershell
python .\10_labs\01_parking_gate_tool.py
python .\10_labs\02_air_conditioner_workflow.py
python .\10_labs\03_parcel_locker_authorization.py
python .\10_labs\04_cafe_argument_extraction.py
python .\10_labs\05_library_multi_tool_rules.py
python .\10_labs\06_inventory_reservation_concurrency.py
```

실제 호출 예제는 Mini Agent Backend를 먼저 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_03_tool\backend
uvicorn app.main:app --reload --port 8000
```

새 PowerShell에서 Provider를 선택합니다.

```powershell
cd C:\aidevs\05_llm-agent-orchestration\03_tool-use
$env:TOOL_EXAMPLE_PROVIDER="gemini"  # mock, gemini, openai, ollama
python .\04_current_vs_forecast_selection.py
python .\05_real_tool_call_inspection.py
python .\06_missing_arguments_and_clarification.py
python .\08_real_tool_loop.py
```

`mock`은 호출 흐름과 안전 검증용입니다. 현재 날씨와 미래 예보처럼 경계가 가까운
Tool의 선택 결과는 실제 Provider로 비교합니다. 날씨 Tool은 `WEATHER_MODE`에 따라
Mock 또는 Open-Meteo를 사용하며 예약·결제·삭제는 실행하지 않습니다.
