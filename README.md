# Mini Agent ST · 초보자 단계별 실습

`C:\mini_agent_st`는 완성 코드를 읽는 과정이 아니라, 작은 기능을 하나씩
실행하고 연결하는 초보자용 프로젝트입니다.

화면과 Backend 구조는 이전 과정의 `C:\mini_frontend_sam`을 기준으로 합니다.
학생들은 익숙한 `app_pages → clients → core/api_client`와
`main → routers → services/schemas` 흐름에서 Agent 기능만 새로 배웁니다.

```text
05_llm-agent-orchestration
→ 개념과 단위 예제

mini_agent_st
→ 작은 예제와 Starter에서 직접 작성
→ 작은 테스트 실행
→ Solution 또는 완성 Backend와 비교

mini_agent_sam
→ 추가 강사용 참고 자료
```

## 과정 구분

| 구간 | 단계 | 난이도 |
| --- | --- | --- |
| 기본 | 01~05 | 초급 |
| Agent 핵심 | 06~08 | 초급 후반~중급 |
| 선택 심화 | 별도 통합 프로젝트 | 중급 |

## 전체 과정

| 단계 | 이번 단계에서 추가하는 한 가지 핵심 |
| --- | --- |
| `mini_agent_01_llm` | 판단 함수→API→세 Provider 비교·이미지 분석·음성 생성 |
| `mini_agent_02_structured_output` | Pydantic 구조화 결과 |
| `mini_agent_03_tool` | Schema·선택·안전 실행·Tool Result 최종 답변 |
| `mini_agent_04_rag` | Chunk·키워드 검색·근거 답변·Ollama/pgvector |
| `mini_agent_05_memory` | 대화 Window·사용자 CRUD·개인화·Redis·PostgreSQL |
| `mini_agent_06_langgraph` | 일반 Python→State·Node·Edge·분기·반복·Checkpoint |
| `mini_agent_07_human_approval` | 중단·저장·재개 |
| `mini_agent_08_evaluation` | 시나리오 평가와 Trace·누적 완성 Backend와 Frontend |
| `optional_multimodal_agent` | 선택 심화: 이미지→Agent→승인→TTS |

`09_integrated-agent-lab`은 새 프로젝트를 복사하지 않고
`mini_agent_08_evaluation`의 `backend_python`, `backend_langgraph`, `frontend`를
함께 실행하여 전체 흐름을 확인합니다.

`optional_multimodal_agent`는 정규 번호에 포함하지 않습니다. 01~08을 마친 뒤
전체 멀티모달 연결을 시연할 때만 사용합니다.

## 단계별 폴더 사용법

| 구간 | 학생 실습 | 시간이 부족할 때 |
| --- | --- | --- |
| 01~05 | `learning_unit → starter → test → solution` | 제공된 Backend·Frontend로 동작 확인 |
| 06 | Python 기초 예제와 `steps → starter → solution` | 두 완성 Backend·Frontend 비교 |
| 07~08 | `learning_unit → steps` | 완성 Backend·Frontend로 승인·평가 시연 |

07~08은 누적 코드가 커지는 시점이므로 같은 코드를 다시 복사한 `starter`와
`solution`을 두지 않습니다. 학생은 작은 `steps`를 수정하고, 전체 연결은 완성
Backend와 Frontend에서 확인합니다.

## 매 단원의 학습 순서

```text
BEGINNER_GUIDE.md 읽기
→ learning_unit 또는 steps의 작은 예제 실행
→ Mock 결과 확인
→ 제공된 경우 starter TODO 작성
→ 작은 테스트 실행
→ 제공된 경우 solution과 비교
→ 실제 Provider·Docker 선택 연결
→ 완성 Backend·Frontend 확인
→ 완료 체크
```

한 수업에서 새로 읽을 파일은 최대 5개로 제한합니다. 기존 파일 전체를 먼저
읽지 마세요.

`mini_agent_01_llm`은 메뉴를 한 번에 완성하지 않습니다. `01_llm-to-agent`의
단위 예제를 학습할 때마다 다음 메뉴를 하나씩 추가합니다.

```text
LLM·Workflow·Agent
→ 여행 요청 분류
→ 정보 부족과 추가 질문
→ Mock 연결
→ Gemini
→ GPT
→ Ollama/Llama
→ Provider 비교
→ 이미지 분석
→ 음성 생성
```

`mini_agent_02_structured_output`은 위 메뉴를 그대로 유지하고 다음 메뉴를
추가합니다.

```text
Prompt 구성
→ Pydantic 정상·오류 검증
→ Mock Structured Output
→ Gemini·GPT·Ollama/Llama의 동일 Schema 비교
```

## 시작

1. [과정 시작 가이드](00_course_guide/01_getting-started.md)를 읽습니다.
2. `mini_agent_01_llm/BEGINNER_GUIDE.md`부터 시작합니다.
3. Docker는 해당 단계에서 요구할 때만 실행합니다.

로그인과 실제 예약·결제는 포함하지 않습니다.
