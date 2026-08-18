# 01 초보자 가이드 · LLM 판단에서 서비스 연결까지

## 오늘의 목표

수업의 작은 Python 판단 함수를 메뉴에 하나씩 추가하고, 마지막에 질문이
Streamlit→FastAPI→LLM으로 이동하는 과정을 이해합니다.

## 오늘 볼 파일

1. `starter/01_concept_compare.py`
2. `starter/02_travel_classifier.py`
3. `starter/provider_call.py`
4. `backend/app/schemas.py`
5. `frontend/clients/agent_client.py`
6. `frontend/app_pages/07_image_analysis.py`
7. `frontend/app_pages/08_tts.py`

화면 연결은 이전 `mini_frontend_sam` 수업과 같습니다.

```text
app_pages → clients/agent_client.py → core/api_client.py
Backend main.py → routers/agent_router.py → services/schemas
```

새로운 `lambda` Wrapper나 별도 UI Helper를 배우지 않습니다.

## 순서

```text
고정 Workflow와 의미 기반 Mock Router 비교
→ 여행 요청 분류
→ confidence와 추가 질문
→ Mock으로 Backend·Frontend 연결
→ 이전 과정의 Gemini
→ OpenAI GPT
→ Docker Ollama/Llama
→ 동일 Prompt 비교
→ 이미지 분석
→ 음성 생성
```

## 아직 하지 않는 것

API 요청·응답 검증에는 Pydantic을 사용하지만, LLM 응답을 Pydantic Schema로
강제하는 Structured Output은 아직 사용하지 않습니다. LangChain, Tool, RAG,
Memory, Agent Workflow도 이후 단계에서 추가합니다.

이미지 분석과 음성 생성은 01 단원에 포함합니다. 이미지 결과가 Pydantic으로
검증되는 자세한 원리는 02 Structured Output에서 다시 설명합니다.

## 완료 체크

- [ ] Provider와 Model의 차이를 설명할 수 있다.
- [ ] 고정 Workflow와 의미 기반 Router의 차이를 설명할 수 있다.
- [ ] confidence가 낮을 때 추가 질문을 반환할 수 있다.
- [ ] API Key가 필요한 Provider를 구분할 수 있다.
- [ ] Backend 오류를 화면에서 확인할 수 있다.
- [ ] 동일한 Prompt의 Gemini·GPT·Llama 결과를 비교할 수 있다.
- [ ] 이미지가 Base64 Data URL로 전달되는 이유를 설명할 수 있다.
- [ ] AI 합성 음성임을 사용자에게 알려야 하는 이유를 설명할 수 있다.
