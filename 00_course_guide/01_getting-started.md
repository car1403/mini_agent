# 과정 시작 가이드

## 선수 학습

- Python 변수, 함수, 조건문
- `dict`, `list`
- 가상환경과 `pip`
- HTTP 요청과 JSON을 들어본 경험

FastAPI, Streamlit, Docker, LangChain, LangGraph를 미리 알 필요는 없습니다.

## 수업 규칙

1. 한 번에 한 기능만 실행합니다.
2. 처음에는 Mock으로 데이터 흐름을 확인합니다.
3. 그다음 실제 Provider 또는 Docker 시스템에 연결합니다.
4. 오류가 발생하면 Mock으로 숨기지 않고 원인을 확인합니다.
5. API Key는 `.env`에만 작성합니다.

## 공통 설치

각 단계 폴더에서 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## 도움이 필요할 때 확인할 순서

```text
가상환경 활성화
→ requirements 설치
→ .env 위치
→ Backend /health
→ Provider 상태
→ Docker 컨테이너
→ Frontend 주소
```
