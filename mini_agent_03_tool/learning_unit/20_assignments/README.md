# 03 Tool Use 과제

## 필수 과제

`search_restaurants(city, category, people)` 조회 Tool을 추가합니다.

제출 내용:

1. Pydantic 입력 Schema
2. 정상·필수값 누락·범위 오류 예제
3. Tool 선택 규칙
4. 필수값이 부족할 때의 `missing_arguments`와 추가 질문
5. Allowlist 등록과 안전 실행
6. Tool Result를 이용한 최종 답변
7. Streamlit 실행 화면

## 선택 과제

Gemini·GPT·Ollama/Llama 중 사용 가능한 두 Provider의 실제 Tool Call을 비교하고,
사용자 메시지와 Provider에 따라 Tool 이름과 arguments가 달라진 이유를 설명합니다.

## 완료 기준

- Tool 선택만으로 함수가 실행되지 않습니다.
- 누락값을 임의의 도시·날짜·인원으로 채우지 않습니다.
- Backend가 Tool 이름과 arguments를 검증합니다.
- 정의되지 않은 인자를 거부합니다.
- 미등록 Tool 실행을 차단합니다.
- 최종 답변이 Tool Result의 값을 사용합니다.
- API Key를 코드에 직접 작성하지 않습니다.
