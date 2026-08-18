# 02 Prompt and Structured Output · 학습 단위

이 폴더는 강의 단원의 작은 Python 예제를 미니 프로젝트 안에서 다시 실행하기 위한
복사본입니다. 원본은 `C:\aidevs\05_llm-agent-orchestration\02_prompt-and-structured-output`입니다.

## 순서

1. `00_prompt_components.py`: Prompt 네 부분
2. `01_concept_example.py`: dict와 Pydantic 검증
3. `02_travel_example.py`: 정상·누락·잘못된 여행 JSON
4. `03_real_provider_comparison.py`: 완성 Backend의 구조화 결과 비교

```text
JSON/dict → Pydantic Validation → LLM Structured Output
```

`03`은 Mini Agent 02 Backend를 먼저 실행해야 합니다. 기본 Mock은 API Key 없이
성공하며, 설정되지 않은 실제 Provider 오류도 비교 결과에 남습니다.
