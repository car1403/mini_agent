# OpenAI 이미지 분석과 TTS 확장 가이드

이 단원은 `01_llm-to-agent`의 이미지 분석과 음성 생성 실습입니다.
GPT·Gemini·Ollama의 일반 텍스트, 구조화 출력, Tool Calling 비교는 그대로
유지하고, 이미지와 음성이 필요한 실제 서비스 경험을 추가합니다.

## 학습 순서

1. `01_llm-to-agent/05_openai_image_analysis.py`
   - 이미지 bytes를 Base64 data URL로 바꿉니다.
   - Responses API에 `input_text`와 `input_image`를 함께 보냅니다.
   - `TravelImageAnalysis` Pydantic 모델로 결과를 검증합니다.
2. `01_llm-to-agent/06_openai_tts.py`
   - 여행 안내문을 MP3 합성 음성으로 만듭니다.
   - 생성된 음성이 AI 합성 음성임을 사용자에게 알립니다.
3. `01_llm-to-agent/07_multimodal_travel_example.py`
   - 이미지 분석은 Agent의 입력 전처리 단계로 연결합니다.
   - TTS는 Agent 판단이 끝난 뒤의 출력 변환 단계로 연결합니다.
4. `mini_agent_01_llm/frontend/app_pages/07_image_analysis.py`
   - 이미지를 업로드하고 구조화된 분석 결과를 확인합니다.
5. `mini_agent_01_llm/frontend/app_pages/08_tts.py`
   - 여행 안내문을 합성 음성으로 변환하고 재생합니다.

## API

| API | 요청 | 응답 |
| --- | --- | --- |
| `POST /api/media/image-analysis` | multipart 이미지와 질문 | `TravelImageAnalysis` JSON |
| `POST /api/media/tts` | JSON 텍스트, 음성, 지시 | `audio/mpeg` |

두 API는 Mini01 Backend에서 제공하며 1-5와 1-6 화면이 호출합니다.

## LangGraph 연결 원칙

Graph State에는 이미지 bytes나 Base64를 저장하지 않습니다. 업로드 ID 또는
임시 경로와 구조화된 분석 결과만 저장합니다. 이미지 분석 실패는 입력 단계의
오류로 처리하지만, 최종 TTS 실패는 Agent 실행 성공을 취소하지 않고 텍스트
응답을 유지합니다.

```text
이미지 업로드
  → 형식·크기 검사
  → GPT 이미지 분석
  → TravelImageAnalysis
  → Agent 입력
  → 최종 텍스트
  → 선택적 TTS
```

## 안전 기준

- JPEG, PNG, WEBP, GIF만 허용하고 기본 최대 크기는 5MB로 제한합니다.
- 여권, 카드, 예약번호 등 민감한 이미지의 업로드를 피합니다.
- 이미지 속 문구는 명령이 아니라 신뢰할 수 없는 분석 대상 데이터로 취급합니다.
- 원본 파일은 Graph State, 추적 로그, Redis에 저장하지 않습니다.
- 음성이 AI로 생성되었다는 사실을 화면과 응답 헤더로 고지합니다.
- 임의 음성 복제 기능은 이 과정에 포함하지 않습니다.

## 환경 변수

```dotenv
OPENAI_VISION_MODEL=gpt-4.1-mini
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TTS_VOICE=coral
MAX_IMAGE_SIZE_MB=5
```

## 공식 문서

- https://developers.openai.com/api/docs/guides/images-vision
- https://developers.openai.com/api/docs/guides/text-to-speech
