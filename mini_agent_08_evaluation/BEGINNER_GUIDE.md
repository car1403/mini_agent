# 08 초보자 가이드 · Evaluation과 Tracing

좋은 문장인지 평가하기 전에 Agent 행동이 맞았는지 확인합니다.

```text
8-1 왜 평가하는가
→ 8-2 시나리오 하나 작성
→ 8-3 여러 시나리오 반복 실행
→ 8-4 Trace에서 첫 실패 찾기
→ 8-5 수정 후 회귀 확인
→ 8-6 Provider 비교 (선택)
```

## 첫 시나리오의 네 부분

```python
{
    "name": "날씨 조회",
    "message": "부산 날씨를 알려줘",
    "expected_tool": "get_weather",
    "expected_status": "completed",
}
```

- 입력: Agent에게 전달할 요청
- 기대 Tool: 선택해야 하는 Tool 또는 `None`
- 기대 상태: `completed`, `needs_input`, `blocked`
- 실제 결과: Agent를 실행해 얻은 Tool과 상태

## 권장 순서

처음에는 Tool과 상태만 정확히 비교합니다. 그다음 인자·RAG 근거·Memory 격리·승인 안전성을 한 항목씩 추가합니다. 점수 하나보다 어떤 검사가 왜 실패했는지가 더 중요합니다.

LLM Judge와 복잡한 가중치는 이번 과정에서 필수가 아닙니다. Provider 비교도 환경 설정과 비용을 확인한 뒤 선택적으로 진행합니다.
