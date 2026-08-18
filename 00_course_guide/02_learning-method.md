# 단계별 학습 방법

각 단계에는 다음 자료가 있습니다.

| 자료 | 사용 방법 |
| --- | --- |
| `BEGINNER_GUIDE.md` | 오늘 배울 내용과 파일 순서 |
| `learning_unit` | 작은 개념·실제 예제 |
| `starter` | 학생이 TODO를 작성하는 위치 |
| 기존 Backend·Frontend | 해당 단계의 실행 가능한 Solution |
| `solution/README.md` | Starter와 완성본 비교 방법 |

## 이전 수업 코드 재사용 원칙

`mini_agent_st`의 화면과 Backend 골격은 `C:\mini_frontend_sam`에서 배운 표현을
유지합니다. 학생이 새로 배워야 하는 것은 Agent 기능이며, 이미 배운 연결 코드를
다른 방식으로 다시 배우게 하지 않습니다.

```text
Streamlit app.py
→ app_pages
→ clients/agent_client.py
→ core/api_client.py
→ FastAPI main.py
→ routers/agent_router.py
→ services + schemas
```

- 화면은 `st.Page`, `st.navigation`, `st.page_link`를 그대로 사용합니다.
- API 호출은 화면에 직접 쓰지 않고 `clients` 함수로 이름을 붙입니다.
- 오류는 이전 수업과 같은 `BackendAPIError`와 `try/except`로 표시합니다.
- Backend `main.py`는 Router 등록만 담당합니다.
- 로그인, Database, Upload는 해당 기능을 배우는 단계 전에는 복사하지 않습니다.
- 새 Helper나 추상화는 같은 코드가 반복되어 실제로 필요할 때만 추가합니다.

## 완료 기준

- 코드를 복사하지 않고 데이터 흐름을 말로 설명할 수 있습니다.
- Mock 실행과 실제 실행을 구분할 수 있습니다.
- 실패 메시지에서 확인할 설정을 찾을 수 있습니다.
- 해당 단계의 작은 테스트를 통과시킬 수 있습니다.
