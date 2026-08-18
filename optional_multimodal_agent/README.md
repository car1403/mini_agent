# Optional Multimodal Agent

정규 01~09 과정과 분리된 선택 심화 완성본입니다. Mini01에서 배운 이미지 분석과 TTS를 Python Agent와 LangGraph Agent의 전체 흐름에 연결합니다.

```text
이미지 업로드
→ GPT 이미지 분석
→ TravelImageAnalysis
→ Python 또는 LangGraph Agent
→ Tool·RAG·Memory
→ Human Approval
→ 최종 안내
→ 선택적 TTS
```

## 핵심 규칙

- 이미지 bytes와 Base64는 Agent State에 저장하지 않습니다.
- 구조화된 `TravelImageAnalysis`만 Agent에 전달합니다.
- Python Agent는 분석 결과를 여행 계획 입력과 결과에 포함합니다.
- LangGraph는 `use_image_analysis` Node에서 분석 결과를 State에 병합합니다.
- TTS 실패는 Agent 실행 성공과 승인 기록을 취소하지 않습니다.
- 실제 예약과 결제는 수행하지 않습니다.

## API

| API | 역할 |
|---|---|
| `POST /api/media/image-analysis` | 이미지 분석만 실행 |
| `POST /api/media/agent-runs` | 이미지 분석 후 Agent 실행 |
| `POST /api/media/tts` | 최종 텍스트를 MP3로 변환 |

## 실행

```powershell
cd C:\mini_agent_st\optional_multimodal_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

```powershell
# 터미널 1
cd C:\mini_agent_st\optional_multimodal_agent\backend_python
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# 터미널 2
cd C:\mini_agent_st\optional_multimodal_agent\backend_langgraph
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001

# 터미널 3
cd C:\mini_agent_st\optional_multimodal_agent
.\.venv\Scripts\python.exe -m streamlit run .\frontend\app.py
```

프런트엔드의 `이미지와 음성` 메뉴에서 전체 흐름을 실행합니다. 실제 이미지 분석과 TTS에는 `OPENAI_API_KEY`가 필요합니다.
