# Solution 확인

Starter를 작성하고 테스트한 뒤 다음 파일과 비교합니다.

| Starter | 완성 구현 |
| --- | --- |
| `01_concept_compare.py` | `backend/app/services/concept_service.py` |
| `02_travel_classifier.py` | `backend/app/services/travel_classifier.py` |
| `provider_call.py` | `backend/app/providers.py` |
| `04_image_contract.py` | `backend/app/services/media_service.py` |

처음부터 완성 파일을 복사하지 말고 다음 차이를 기록합니다.

- 고정 규칙과 의미 기반 판단의 차이
- confidence가 낮을 때의 다음 행동
- API Key를 Backend에서만 읽는 이유
- 하나의 Provider 실패가 비교 전체를 중단하지 않는 이유
- 이미지 형식과 파일 시그니처를 함께 확인하는 이유
- AI 합성 음성을 화면에서 고지하는 이유

화면 완성본은 `07_image_analysis.py`와 `08_tts.py`에서 확인합니다.
