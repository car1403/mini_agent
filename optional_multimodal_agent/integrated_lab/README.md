# 12 Integrated Agent Lab

## 주제

**AI 여행 일정 및 예약 요청 도우미**

현재 프로젝트의 `backend_python`, `backend_langgraph`, `frontend`를 연결한 뒤
두 구현의 차이를 비교하고 기능을 확장합니다.

## 현재 제공 기능

- 여행 요청 구조화
- 날씨·숙소·관광지 Mock Tool
- 여행 정책 검색
- 사용자별 Memory
- 정보 부족 분기
- 일정과 예산 검증
- Mock 예약 요청 승인·거절
- 실행 Trace
- FastAPI Backend
- Streamlit Frontend

## Lab 진행 순서

1. Backend와 Frontend를 실행합니다.
2. 정상 여행 요청을 실행합니다.
3. 목적지나 예산이 없는 요청으로 `needs_input`을 확인합니다.
4. Memory를 저장하고 Agent 결과에 포함되는지 확인합니다.
5. 정책 검색 결과와 출처를 확인합니다.
6. Mock 예약 요청을 승인·거절합니다.
7. 평가 시나리오를 실행합니다.

## 필수 확장

- Tool 하나 추가
- 정책 문서 하나 추가
- Memory 항목 하나 추가
- 실패 경로 하나 추가
- 평가 시나리오 두 개 추가

## 제외 범위

- 실제 예약과 결제
- Docker Compose
- AWS 배포
- Multi-Agent

## 완료 기준

```text
Streamlit 입력
→ FastAPI 요청 검증
→ Agent 업무 흐름
→ Tool/RAG/Memory
→ 검증과 승인
→ 실행 상태 저장
→ Streamlit 결과와 Trace
```

이 흐름을 코드와 화면으로 설명할 수 있어야 합니다.
