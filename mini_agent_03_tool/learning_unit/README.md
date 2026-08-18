# 03 Tool Use

## 한 문장으로 이해하기

Tool Use는 LLM이 필요한 함수를 제안하고, Backend가 그 제안을 검증한 후 허용된 함수만 실행하는 과정입니다.

```text
사용자 질문
→ LLM의 Tool Call 제안
→ Backend Allowlist 확인
→ Pydantic arguments 검증
→ Tool 실행
→ Tool Result
→ 사용자용 최종 답변
```

LLM의 Tool Call은 실행 명령이 아니라 제안입니다. 실행 권한은 항상 Backend가 가집니다.

## 학습 목표

- Python 함수, Tool Schema, Tool Call, Tool Result를 구분합니다.
- Tool 선택과 실제 실행을 분리합니다.
- Tool 입력을 Pydantic으로 검증합니다.
- Allowlist에 등록된 조회 Tool만 실행합니다.
- Tool Result를 최종 답변으로 변환합니다.
- Mock·Gemini·GPT·Ollama/Llama의 Tool 선택을 비교합니다.

## 예제 순서

| 순서 | 예제 | 외부 환경 | 확인할 내용 |
| --- | --- | --- | --- |
| 01 | `01_concept_example.py` | 필요 없음 | 함수·Schema·Call·Result |
| 02 | `02_tool_schema_validation.py` | 필요 없음 | 누락·날짜·추가 인자 검증 |
| 03 | `03_mock_tool_selection.py` | 필요 없음 | 선택과 실행의 분리 |
| 04 | `04_safe_tool_execution.py` | 필요 없음 | Allowlist와 오류 코드 |
| 05 | `05_tool_result_to_answer.py` | 필요 없음 | 전체 Agent Loop |
| 06 | `06_multi_provider_tool_calling.py` | Backend 필요 | Provider 비교와 실제 API |

처음 다섯 예제는 API Key와 Docker 없이 실행합니다. 마지막 예제만 실행 중인 `mini_agent_03_tool` Backend를 사용합니다.

## 네 가지 용어

```text
Python 함수  실제로 실행되는 코드
Tool Schema  LLM과 Backend가 공유하는 입력 계약
Tool Call    LLM이 제안한 Tool 이름과 arguments
Tool Result  Backend가 검증 후 실행한 결과
```

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_03_tool\learning_unit
python .\01_concept_example.py
python .\02_tool_schema_validation.py
python .\03_mock_tool_selection.py
python .\04_safe_tool_execution.py
python .\05_tool_result_to_answer.py
```

06은 Mini Agent Backend를 먼저 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_03_tool\backend
uvicorn app.main:app --reload --port 8000

cd C:\mini_agent_st\mini_agent_03_tool\learning_unit
python .\06_multi_provider_tool_calling.py
```

기본 확인 순서는 `Mock → Gemini → GPT → Ollama/Llama`입니다. Cloud Provider와 Docker Ollama는 선택 환경이 준비된 경우에만 비교합니다. Provider 하나가 실패해도 비교 결과의 다른 항목은 유지됩니다.

## 안전 범위

수업에서는 날씨·숙소·관광지 조회용 Mock Tool만 실행합니다. 예약, 결제, 환불, 삭제처럼 상태를 바꾸는 Tool은 이후 Human Approval 단계에서 다룹니다.
