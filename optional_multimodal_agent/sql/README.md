# Database SQL

`init.sql`은 Optional Multimodal Agent 과정에서 새로 추가한 다음 구조만
생성합니다.

- `optional_multimodal_agent_runs`: 이미지 분석 결과를 포함한 Agent 실행·승인 이력
- `optional_multimodal_travel_tool_data`: 실제 PostgreSQL Tool 조회 데이터

초기화할 때 위 두 과정 전용 테이블은 삭제 후 다시 생성됩니다. 기존 실행 이력과
Tool 데이터는 초기화되지만, 다른 과정의 공용 테이블과 데이터는 변경하지 않습니다.

공용 `documents`와 `user_memories` 테이블은 이전 RAG·Memory 과정 및
`infra/postgres/init.sql`의 소유이므로 이 파일에서 중복 생성하지 않습니다.
LangGraph Checkpoint 테이블도 Backend 시작 시 자동 생성됩니다.

## 권장 실행 방법

프로젝트 폴더(`optional_multimodal_agent`)에서 Python 초기화 프로그램을
실행합니다. `.env`의 `DATABASE_URL`을 사용하므로 Docker PostgreSQL 컨테이너가
호스트의 5433 포트에서 실행 중이면 됩니다.

```powershell
python .\sql\setup_database.py
```

PostgreSQL 콘솔에서 직접 확인하려면 다음 명령을 사용합니다.

```powershell
docker exec -it aidevs-pgvector psql -U agent_user -d agent_db
```

먼저 공용 `infra/postgres/init.sql`이 적용된 데이터베이스에서 실행해야 합니다.
여러 번 실행해도 초기 Tool 데이터는 중복되지 않습니다.
