# 05 과정과 Mini Agent 연결표

| 05 학습 폴더 | Mini Agent 적용 위치 | 실행 결과 |
| --- | --- | --- |
| `01_llm-to-agent` | `mini_agent_01_llm` | 개념 비교·여행 분류·세 Provider 응답 |
| `02_prompt-and-structured-output` | `mini_agent_02_structured_output` | Prompt 조립·Pydantic 검증·Provider별 TravelPlan |
| `01_llm-to-agent` 확장 | `mini_agent_01_llm/learning_unit` | GPT 이미지 분석·Pydantic·TTS |
| `03_tool-use` | `mini_agent_03_tool/learning_unit` | Schema·선택·안전 실행·Agent Loop |
| `04_rag` | `mini_agent_04_rag/learning_unit` | Chunk·검색·근거 제한·Ollama Embedding·pgvector |
| `05_memory` | `mini_agent_05_memory/learning_unit` | 대화 Window·사용자 격리·개인화·Redis·PostgreSQL |
| `06_langgraph-workflow` 준비 | `mini_agent_06_langgraph/python_workflow_steps` | 일반 Python 조건 분기와 실행 순서 |
| `06_langgraph-workflow` | `mini_agent_06_langgraph/learning_unit` | 초보자 Graph·분기·Reducer·반복·Checkpoint |
| `07_human-approval-and-safety` | `mini_agent_07_human_approval/learning_unit` | 승인 중단·재개 |
| `08_agent-evaluation-and-tracing` | `mini_agent_08_evaluation/learning_unit` | 평가와 Trace |
| `09_integrated-agent-lab` | `mini_agent_08_evaluation` 전체 | 두 Backend·Frontend 통합 실행과 최종 확장 |

## 선택 심화

| 자료 | 적용 위치 | 실행 결과 |
|---|---|---|
| Multimodal Agent | `optional_multimodal_agent` | 이미지 분석→Agent→승인→TTS 전체 연결 |

LangChain은 필수 단계에서 제외했습니다. 필요한 경우
`C:\aidevs\05_llm-agent-orchestration\00_references\10_optional-langchain-core`를
선택 자료로만 사용합니다.

## 수업 진행

```text
learning_unit 개념 예제
→ 여행 예제
→ starter 또는 steps 실습
→ Mock 테스트
→ 실제 Docker/Provider 선택 연결
→ Backend API 확인
→ Streamlit 화면 연결
→ 과제 도메인으로 변형
```

- 01~05는 `starter`에서 작성하고 `solution`과 비교합니다.
- 06은 Python Workflow·LangGraph `steps`와 `starter/solution`을 함께 사용합니다.
- 07~08은 작은 `steps`를 학생 실습으로 사용하고 누적 완성 Backend·Frontend에서
  전체 동작을 확인합니다.
