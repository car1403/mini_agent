# 08 Agent Evaluation and Tracing

Agent가 **실행되는 것**과 **올바르게 행동하는 것**은 다릅니다. 작은 테스트 시나리오로 행동을 확인하고, 실패하면 Trace에서 원인을 찾습니다.

## 학습 목표

- 입력과 기대 행동을 한 쌍으로 기록합니다.
- 기대 Tool·상태와 실제 결과를 규칙으로 비교합니다.
- 정상뿐 아니라 정보 부족·정책 위반 시나리오도 평가합니다.
- Trace에서 처음 실패한 Node와 원인을 찾습니다.
- 코드 수정 뒤 이전 기능이 깨지지 않았는지 회귀 테스트합니다.
- 선택 실습으로 GPT·Gemini·Ollama의 결과와 지연 시간을 비교합니다.

## 학습 순서

| 메뉴 | 파일 | 핵심 내용 |
|---|---|---|
| 8-1 | `01_why_evaluate.py` | 실행 성공과 올바른 행동의 차이 |
| 8-2 | `02_one_scenario.py` | 첫 평가 시나리오 |
| 8-3 | `03_multiple_scenarios.py` | 여러 시나리오와 통과율 |
| 8-4 | `04_trace_failure.py` | Trace에서 실패 위치 찾기 |
| 8-5 | `05_regression.py` | 수정 전후 회귀 확인 |
| 8-6 | `06_provider_comparison_optional.py` | Provider 비교 선택 확장 |

## 실행

```powershell
python .\01_why_evaluate.py
python .\02_one_scenario.py
python .\03_multiple_scenarios.py
python .\04_trace_failure.py
python .\05_regression.py
```

8-1~8-5는 외부 API 없이 실행됩니다. 8-6은 Backend를 먼저 실행하고 Provider 환경 변수를 설정한 경우에만 진행합니다.

```powershell
python .\06_provider_comparison_optional.py
```

## 처음 평가할 항목

| 항목 | 질문 |
|---|---|
| Tool | 필요한 Tool만 선택했는가? |
| Status | 완료·정보 부족·차단 상태가 맞는가? |
| Arguments | 날짜·지역·인원이 정확한가? |
| Grounding | 필요한 답변에 근거가 있는가? |
| Safety | 승인 없는 변경을 차단했는가? |
| Termination | 정해진 횟수 안에 종료했는가? |

처음에는 Tool과 Status 두 항목만 평가하고, 앞 과정의 RAG·Memory·Safety 시나리오를 한 가지씩 추가합니다.

## Trace는 로그와 무엇이 다른가

단순 오류 문장만 남기는 대신 다음 정보를 실행 단계별로 기록합니다.

```text
trace_id · node · tool · status · duration_ms · iteration · error
```

Trace의 목적은 점수를 예쁘게 만드는 것이 아니라 **어디서 처음 잘못되었는지 찾는 것**입니다.

## 이번 단계의 범위

- 규칙 기반 평가는 필수입니다.
- LLM Judge, 외부 평가 플랫폼, 복잡한 가중치는 다루지 않습니다.
- Provider 비교는 선택 실습이며 실제 호출 비용과 시간이 발생할 수 있습니다.
- API Key, 전체 Prompt, 개인정보는 평가 보고서에 저장하지 않습니다.
