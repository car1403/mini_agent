# Solution · 완성 동작 확인

완성 코드는 별도 복사본이 아니라 이 프로젝트의 `backend`와 `frontend`입니다.

```text
starter     학생이 TODO 작성
backend     완성된 API와 Pydantic 검증
frontend    완성된 Streamlit 메뉴
solution    해설과 빠른 진행 경로
```

시간이 충분하면 Starter를 작성한 뒤 완성 화면과 비교합니다. 시간이 부족하면
Backend와 Frontend를 실행하여 다음 메뉴를 순서대로 설명합니다.

1. Prompt 구성과 Before/After 실제 응답 비교
2. TravelPlan·SupportTicket 검증의 정상·범위 오류·추가 필드
3. Mock Structured Output
4. Gemini·GPT·Ollama/Llama의 동일 Schema 비교

정답의 핵심 위치:

- Prompt 조립: `backend/app/services/prompt_service.py`
- TravelPlan·SupportTicket: `backend/app/schemas.py`
- Provider 구조화 호출: `backend/app/providers.py`
- 범용 Structured Output API: `POST /api/structured/generate`
- API Endpoint 구현: `backend/app/routers/agent_router.py`
- Backend 시작점: `backend/app/main.py`
- Frontend API 함수: `frontend/clients/agent_client.py`
- 화면: `frontend/app_pages/07_prompt_builder.py`부터 `09_structured_output.py`
