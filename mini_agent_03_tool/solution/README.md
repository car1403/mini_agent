# Solution · 완성 동작 확인

| 학습 항목 | 완성 코드 |
| --- | --- |
| 입력·응답 Schema | `backend/app/schemas/common.py`, `stage_01.py`, `stage_02.py`, `stage_03.py` |
| Tool 설명·Schema·함수 단일 등록 | `backend/app/tools/registry.py`의 `ToolSpec` |
| Allowlist와 실행기 | `backend/app/tools/registry.py`, `executor.py` |
| 날씨·여행 Tool | `backend/app/tools/weather`, `tools/travel` |
| Agent 선택·Loop | `backend/app/agents` |
| Provider Tool Calling·Choice | `backend/app/providers/openai.py`, `gemini.py`, `ollama.py` |
| Provider 공통 계약·조회 | `backend/app/providers/base.py`, `models.py`, `registry.py` |
| 일반·구조화 생성 Service | `backend/app/services/generation_service.py`, `structured_service.py` |
| 공통 환경 설정 | `backend/app/core/config.py` |
| Media Service·Provider | `backend/app/services/image_analysis_service.py`, `speech_service.py`, `providers/openai_media.py` |
| 추가 질문과 Agent Cycle Trace | `backend/app/agents/tool_loop.py`, `routers/stage_03_router.py` |
| Frontend API | `frontend/clients/agent_client.py` |
| Tool Schema 화면 | `frontend/app_pages/12_tool_schema.py` |
| 설명·Choice·원본 Call 화면 | `frontend/app_pages/13_tool_select.py` |
| 검증·실행 화면 | `frontend/app_pages/14_tool_validation.py`, `15_tool_run.py` |
| 최종 답변 화면 | `frontend/app_pages/17_agent_cycle.py` |

시간이 부족하면 00~02 단위 예제 후 완성 화면에서 설명·Choice 비교와 Mock Agent Cycle을 시연합니다. 이어 누락값 재질문, 날짜 오류, `delete_database` 차단을 확인합니다.
