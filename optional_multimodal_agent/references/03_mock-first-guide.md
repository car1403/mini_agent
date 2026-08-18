# Mock First 가이드

## 목적

API Key, 네트워크, 외부 서비스 상태와 무관하게 핵심 흐름을 학습하고 테스트합니다.

## 세 단계

```text
고정 Mock 결과
→ 실제 LLM + Mock Tool
→ 실제 LLM + 선택적 실제 조회 API
```

## Mock이 필요한 대상

- LLM 응답
- 날씨·숙소·관광지 Tool
- 예약 요청
- Vector Search
- 사용자 Memory 저장소

## 규칙

- Mock 결과에도 실제 응답과 같은 Schema를 사용합니다.
- 성공 결과뿐 아니라 timeout, 빈 결과, 잘못된 Schema를 제공합니다.
- 테스트에서는 현재 날짜나 네트워크에 의존하지 않습니다.
