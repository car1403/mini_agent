# Mini Agent 03 · Tool Use

01~03에서 만든 화면과 API를 유지하면서 Tool 선택, 안전 실행, 최종 답변 생성을 추가한 누적형 완성본입니다.

```text
Streamlit app_pages
  → clients/agent_client.py
  → FastAPI routers/agent_router.py
  → providers.py에서 Tool 선택
  → 필수 arguments 누락 시 사용자에게 추가 질문
  → tools/travel_tools.py에서 검증·실행
  → Tool Result로 최종 답변
```

## 새로 배우는 내용

- Python 함수·Tool Schema·Tool Call·Tool Result
- 현재 날씨와 미래 예보 Tool의 선택 결과 비교
- `auto`·`none`·`required` Tool Choice
- Provider 원본 Tool Call과 정규화 결과
- 누락값을 추측하지 않는 추가 질문
- Pydantic arguments 검증
- Tool 선택과 실행 분리
- Allowlist 기반 안전 실행
- 공통 Tool 오류 코드
- Tool Result를 사용한 최종 답변
- Mock·Gemini·GPT·Ollama/Llama 비교

## 추가 메뉴

1. `Tool 선택`: 설명·Choice를 바꾸며 LLM의 원본 Tool Call과 정규화 결과를 확인합니다.
2. `Tool 실행`: arguments를 수정하고 Backend 검증 결과를 확인합니다.
3. `Agent Loop`: 선택 → 재질문 또는 실행 → Tool Result → 최종 답변을 Trace로 확인합니다.

실행되는 Tool은 날씨·숙소·관광지 조회용 Mock 함수뿐입니다. 실제 예약, 결제, 환불, 삭제는 실행하지 않습니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_03_tool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

cd backend
uvicorn app.main:app --reload --port 8000
```

새 터미널에서 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_03_tool
.\.venv\Scripts\Activate.ps1
streamlit run .\frontend\app.py
```

기본 Provider는 Mock입니다. 먼저 Mock으로 전체 Agent Loop를 확인한 다음 준비된 Provider만 선택적으로 비교합니다.

## 실제 날씨 Tool

날씨 Tool은 현재 상태와 미래 예보를 구분합니다.

- `get_current_weather`: 현재 기온·체감 온도·강수량·바람
- `get_weather_forecast`: 지정한 미래 날짜의 최고·최저 기온과 강수 확률

기본 `WEATHER_MODE=mock`은 인터넷 없이 결정적으로 실행됩니다. `.env`에서 다음과
같이 바꾸면 Tool 실행 단계가 Open-Meteo Geocoding API와 Forecast API를 호출합니다.

```env
WEATHER_MODE=open_meteo
```

Open-Meteo의 현재 상태는 관측소 실측값이 아니라 최신 기상 모델 기반 값입니다.
외부 API 오류가 발생하면 실제 값처럼 Mock으로 조용히 대체하지 않고 Tool 오류를
반환합니다.
