# 인증된 사용자 범위 Memory API

기존 `/api/memory/*` API는 화면에서 `user_id`를 바꿔 사용자 격리 원리를 관찰하는
수업용 API입니다. `/api/memory/me/*`는 요청 Body나 URL에서 `user_id`를 받지 않고
Backend Dependency가 확인한 사용자 범위를 사용합니다.

이 과정은 로그인 구현 과정이 아니므로 `X-Demo-User-ID` Header를 사용합니다.

```powershell
$headers = @{ "X-Demo-User-ID" = "user-a" }
$body = @{
    key = "hotel_preference"
    value = "조용한 호텔"
    storage = "postgres"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri http://127.0.0.1:8000/api/memory/me/items `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $body
```

주요 Endpoint:

| Method | Endpoint | 역할 |
| --- | --- | --- |
| POST | `/api/memory/me/items` | 내 Memory 저장·수정 |
| GET | `/api/memory/me/items` | 내 Memory 조회 |
| DELETE | `/api/memory/me/items/{memory_id}` | 내 Memory 삭제 |
| POST | `/api/memory/me/personalize` | 내 Memory로 개인화 |
| GET | `/api/memory/me/export` | 내 Memory 내보내기 |
| DELETE | `/api/memory/me` | 내 Memory 전체 삭제 |

클라이언트가 Body에 `user_id`를 추가하면 HTTP 422로 거부합니다. PostgreSQL 조회와
삭제 SQL에도 Dependency에서 얻은 `user_id`가 조건으로 전달됩니다.

운영 환경에서는 `X-Demo-User-ID`를 사용하지 않습니다. JWT, OAuth 또는 로그인
Session을 검증하는 Dependency로 교체하고, 검증 결과의 사용자 ID만 사용합니다.
