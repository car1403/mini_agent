# API 계약 가이드

## 구현 순서

```text
요청 JSON
→ 응답 JSON
→ Pydantic Schema
→ Mock Endpoint
→ Streamlit 연결
→ 실제 Agent 연결
```

## 공통 응답

```json
{
  "success": true,
  "data": {},
  "error": null,
  "trace_id": "trace-001"
}
```

## 오류 응답

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "출발 날짜를 확인해 주세요.",
    "details": []
  },
  "trace_id": "trace-001"
}
```

Frontend는 오류 객체를 사용자가 이해할 수 있는 문장으로 표시합니다.
