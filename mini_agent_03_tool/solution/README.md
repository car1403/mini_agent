# Solution · 완성 동작 확인

| 학습 항목 | 완성 코드 |
| --- | --- |
| 입력 Schema | `backend/app/schemas.py` |
| 명확한/모호한 Tool 설명 | `backend/app/tools/definitions.py` |
| Allowlist와 Mock 함수 | `backend/app/tools/travel_tools.py` |
| Provider Tool Calling·Choice | `backend/app/providers.py` |
| 추가 질문과 Agent Loop Trace | `backend/app/routers/agent_router.py` |
| Frontend API | `frontend/clients/agent_client.py` |
| 설명·Choice·원본 Call 화면 | `frontend/app_pages/11_tool_select.py` |
| 검증·실행 화면 | `frontend/app_pages/12_tool_run.py` |
| 최종 답변 화면 | `frontend/app_pages/13_tool_loop.py` |

시간이 부족하면 00~02 단위 예제 후 완성 화면에서 설명·Choice 비교와 Mock Agent Loop를 시연합니다. 이어 누락값 재질문, 날짜 오류, `delete_database` 차단을 확인합니다.
