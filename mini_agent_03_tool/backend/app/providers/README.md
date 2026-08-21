# Providers

Provider는 OpenAI, Gemini, Ollama, Mock처럼 서로 다른 LLM API를 애플리케이션의 공통
호출·결과 계약으로 변환하는 Adapter 계층입니다.

## 담당하는 일

1. 공통 Prompt와 Message를 모델별 요청 형식으로 변환합니다.
2. 선택된 모델 API를 한 번 호출합니다.
3. 모델별 응답을 공통 텍스트 또는 구조화 결과로 정규화합니다.
4. Provider, 모델과 지연 시간 같은 통신 정보를 반환합니다.

## 담당하지 않는 일

- 어떤 Tool을 Agent에 제공할지 결정하지 않습니다.
- Tool arguments를 업무 규칙에 따라 추측하거나 보완하지 않습니다.
- Tool Allowlist 검증과 실제 함수를 실행하지 않습니다.
- 반복, 승인, 재시도와 종료 같은 Agent 정책을 결정하지 않습니다.

## 다른 계층과의 관계

```text
Router → Service → Provider Adapter → LLM API

Router → Travel Agent → Agent Runtime → OpenAI Tool Calling
                                      → Tool Executor → 실제 Tool
```

- 일반 생성과 Structured Output은 Service가 Provider를 호출합니다.
- Stage 03 Tool Calling은 Provider Adapter를 거치지 않고 Agent Runtime이 OpenAI를 직접 호출합니다.

## 현재 구조

하나의 거대한 Gateway 대신 Provider별 Adapter와 공통 계약·레지스트리를 분리했습니다.

```text
providers/
├── __init__.py
├── base.py
├── models.py
├── registry.py
├── mock.py
├── openai.py
├── openai_media.py
├── gemini.py
└── ollama.py
```

이 Provider Adapter들은 Stage 01·02의 일반 생성과 구조화 출력 호환성을 위해 유지합니다.
Stage 03의 Tool Calling은 Adapter를 거치지 않습니다. `agents/travel_agent.py`가 여행
도메인을 정의하고 `agents/runtime.py`가 OpenAI SDK를 직접 호출합니다. 멀티 Provider
Tool Adapter는 Mini Agent 04에서 도입합니다.
