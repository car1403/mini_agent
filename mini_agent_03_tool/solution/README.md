# Solution · 완성 동작 확인

| 학습 항목 | 완성 코드 |
| --- | --- |
| 입력 Schema | `backend/app/schemas.py` |
| Tool 설명 | `backend/app/tools/definitions.py` |
| Allowlist와 Mock 함수 | `backend/app/tools/travel_tools.py` |
| Provider Tool Calling | `backend/app/providers.py` |
| 안전 실행과 Agent Loop | `backend/app/routers/agent_router.py` |
| Frontend API | `frontend/clients/agent_client.py` |
| Tool 선택 화면 | `frontend/app_pages/11_tool_select.py` |
| 검증·실행 화면 | `frontend/app_pages/12_tool_run.py` |
| 최종 답변 화면 | `frontend/app_pages/13_tool_loop.py` |

시간이 부족하면 01~05 단위 예제를 실행한 후 완성 화면에서 Mock Agent Loop를 시연합니다. 그다음 날짜 오류와 `delete_database` 차단을 보여주면 핵심 흐름을 모두 설명할 수 있습니다.
