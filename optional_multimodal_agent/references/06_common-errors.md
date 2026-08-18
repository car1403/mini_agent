# 공통 오류

## 확인 순서

```text
현재 폴더
→ 가상환경
→ Python 실행 경로
→ requirements 설치
→ .env 위치
→ APP_MODE
→ Backend URL
→ 요청·응답 Schema
→ trace_id
```

## Agent가 종료되지 않을 때

- `iteration`이 증가하는지 확인합니다.
- `max_iterations`를 검사하는 분기가 있는지 확인합니다.
- 모든 조건 경로가 종료 또는 사용자 입력 대기로 연결되는지 확인합니다.

## Tool이 잘못 호출될 때

- Tool 이름과 설명이 겹치지 않는지 확인합니다.
- 입력 Schema의 필수 필드를 확인합니다.
- Tool 선택 결과와 실행 코드를 분리해 출력합니다.

## 실제 LLM 연결이 실패할 때

먼저 `APP_MODE=mock`으로 전체 흐름을 확인합니다. 그 후 API Key, 모델명, 네트워크, 사용량 제한을 확인합니다.
