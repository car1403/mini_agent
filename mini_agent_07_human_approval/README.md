# Mini Agent 07 · Human Approval과 Safety

`01`~`06`에서 만든 여행 Agent에 **사람의 승인과 실행 안전장치**를 추가합니다. 기존 화면·백엔드 구조는 유지하고, 위험도 확인부터 안전 실행까지 메뉴 7-1~7-6에서 한 단계씩 확인합니다.

## 학습 순서

| 메뉴 | 주제 | 확인할 내용 |
|---|---|---|
| 7-1 | 작업 위험도 | 조회·초안·변경·금지 구분 |
| 7-2 | Allowlist와 소유자 | 허용 Tool 및 본인 요청 검사 |
| 7-3 | 중단·저장·재개 | 승인 대기 상태의 필요성 |
| 7-4 | LangGraph interrupt | checkpointer와 같은 thread 재개 |
| 7-5 | 승인과 거절 | 구조화된 결정과 잘못된 요청 차단 |
| 7-6 | 안전 실행 | 승인 후 Mock 실행 및 중복 방지 |

## 폴더 역할

- `learning_unit`: 강의용 설명·예제·실습·과제
- `steps`: 수업 중 순서대로 실행할 작은 예제
- `backend_langgraph`: 완성 동작 확인용 FastAPI + LangGraph 백엔드
- `frontend`: 이전 Mini Agent와 같은 Streamlit 화면 구조

## 안전 범위

- LLM은 Tool을 제안하고, 애플리케이션 코드가 실행 권한을 결정합니다.
- 실제 예약·결제·메시지 전송은 수행하지 않습니다.
- 승인된 요청도 교육용 Mock 결과만 기록합니다.
- 예제의 `actor` 문자열 대신 운영 환경에서는 인증된 사용자 ID를 사용해야 합니다.

처음에는 `steps`를 직접 실행하고, 시간이 부족하면 `backend_langgraph`와 `frontend` 완성본으로 전체 흐름을 시연할 수 있습니다.
