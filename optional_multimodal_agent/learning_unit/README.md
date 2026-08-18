# 08 Agent Evaluation and Tracing

## 학습 목표

- 최종 문장뿐 아니라 Agent의 행동을 평가합니다.
- 기대 Tool과 실제 Tool, 인자, 근거, 반복 횟수를 비교합니다.
- Mock으로 반복 가능한 시나리오 테스트를 만듭니다.

## 평가 항목

| 항목 | 질문 |
| --- | --- |
| Intent | 요청을 올바르게 분류했는가? |
| Tool | 필요한 Tool만 호출했는가? |
| Arguments | 날짜·지역·인원이 정확한가? |
| Grounding | 근거 문서를 사용했는가? |
| Safety | 승인 없는 변경을 차단했는가? |
| Termination | 정해진 횟수 안에 종료했는가? |

## 실행

```powershell
python .\01_concept_example.py
python .\02_travel_evaluation.py
```
