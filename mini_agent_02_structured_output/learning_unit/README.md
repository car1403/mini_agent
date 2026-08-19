# 02 Prompt and Structured Output · 학습 단위

이 폴더는 강의 단원의 작은 Python 예제를 미니 프로젝트 안에서 다시 실행하기 위한
수업용 축약본입니다. 원본은 `C:\aidevs\05_llm-agent-orchestration\02_prompt-and-structured-output`입니다.

## 순서

1. `00_prompt_components.py`: 세 가지 업무의 Prompt 네 부분
2. `01_prompt_template_and_variables.py`: Template과 변수 재사용
3. `02_zero_shot_few_shot.py`: Zero-shot·Few-shot 실제 호출 비교
4. `03_delimiters_and_prompt_injection.py`: 지시와 사용자 데이터 경계
5. `04_system_and_user_messages.py`: 메시지 역할 분리
6. `05_prompt_before_after.py`: 개선 전후 실제 응답 비교
7. `06_prompt_to_structured_output.py`: 자유 응답과 Schema 연결
8. `07_pydantic_validation.py`: dict와 Pydantic 검증
9. `08_travel_structured_output.py`: TravelPlan JSON 검증
10. `09_support_ticket_structured_output.py`: SupportTicket JSON 검증

```text
JSON/dict → Pydantic Validation → LLM Structured Output
```

`02`~`06`과 `10_labs\01_structured_provider_comparison.py`는 Mini Agent 02
Backend를 먼저 실행해야 합니다. Prompt 차이는 실제 Provider로 관찰합니다.

```powershell
$env:PROMPT_EXAMPLE_PROVIDER="gemini"  # mock, gemini, openai, ollama
```

`mock`은 System Prompt를 해석하지 않으므로 호출 흐름 확인에만 사용합니다.
