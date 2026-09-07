# 멀티모달 Agent 실습

사진·텍스트·음성을 입력받아 MCP Tool, RAG, 업무 DB를 사용하는 두 가지 Python AI Agent 예제입니다. Frontend는 Streamlit, Backend는 FastAPI이며 LangGraph는 사용하지 않습니다.

| Agent     | 입력                           | 사용하는 정보                          | 출력                     |
| --------- | ------------------------------ | -------------------------------------- | ------------------------ |
| 제품 안내 | 제품 사진과 텍스트·음성 질문   | 제품 설명서, 호환 액세서리, 가격, 재고 | 사용법·출처·재고·음성    |
| 시설 안내 | 안내문 사진과 텍스트·음성 질문 | 참가 안내, 시설 규정, 일정, 잔여 정원  | 참가 조건·일정·출처·음성 |

제품·시설·재고·안내문은 모두 가상 실습 자료입니다. 실제 예약이나 결제는 수행하지 않습니다.

## 1. 준비

Python 3.11 이상과 OpenAI API 키가 필요합니다. PostgreSQL은 이 프로젝트 전용 컨테이너를 만들고, Redis와 Ollama는 기존 실습 환경의 서비스를 사용합니다.

```powershell
cd C:\mini_agent\optional_multimodal_agent
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`의 `OPENAI_API_KEY`를 입력합니다. 기본 연결 정보는 다음과 같습니다.

```dotenv
DATABASE_URL=postgresql://agent_user:agent_password@127.0.0.1:5433/multimodal_agent_db
REDIS_URL=redis://127.0.0.1:6379/0
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_EMBEDDING_MODEL=embeddinggemma
EMBEDDING_DIMENSIONS=768
```

OpenAI는 Agent 판단, 이미지 분석, STT와 TTS에 사용합니다. RAG 임베딩은 Ollama의 `embeddinggemma`를 사용합니다.

## 2. PostgreSQL 만들기

PowerShell에서 다음 명령을 한 번 실행합니다. 컨테이너, 데이터베이스, 데이터 볼륨 모두 이 프로젝트 전용 이름을 사용합니다.

```powershell
docker run -d `
  --name multimodal-agent-pgvector `
  -p 5433:5432 `
  -e POSTGRES_DB=multimodal_agent_db `
  -e POSTGRES_USER=agent_user `
  -e POSTGRES_PASSWORD=agent_password `
  -v multimodal-agent-pgvector-data:/var/lib/postgresql/data `
  pgvector/pgvector:pg16
```

컨테이너가 생성되었는지 확인합니다.

```powershell
docker ps
```

PC를 재시작한 뒤 컨테이너가 중지되어 있으면 다음 명령으로 다시 시작합니다.

```powershell
docker start multimodal-agent-pgvector
```

기존 PostgreSQL이 이미 `5433` 포트를 사용 중이면 먼저 해당 컨테이너를 중지하거나, 새 컨테이너와 `DATABASE_URL`에 다른 포트를 함께 지정해야 합니다.

## 3. 데이터 준비

```powershell
# pgvector 확장과 프로젝트 테이블 생성
.\.venv\Scripts\python.exe -m scripts.setup_database

# 제품·재고·시설·프로그램 가상 데이터 입력
.\.venv\Scripts\python.exe -m scripts.seed_database

# Markdown 문서를 embeddinggemma로 변환하여 RAG DB에 저장
.\.venv\Scripts\python.exe -m scripts.ingest_knowledge
```

일정 Seed는 실행일 이후 첫 토요일부터 4주를 만듭니다. 기준일을 지정할 수도 있습니다.

```powershell
.\.venv\Scripts\python.exe -m scripts.seed_database --base-date 2026-09-07
```

Seed를 다시 실행해도 기존 재고와 회차는 덮어쓰지 않습니다.

## 4. 실행

네 개의 터미널을 열어 각각 실행합니다. 아래 명령은 이제 각 하위 폴더에서 바로 실행할 수 있도록 조정되어 있습니다.

```powershell
# 터미널 1: MCP Tool Server (변경 없음)
cd C:\mini_agent\optional_multimodal_agent\mcp_server
..\.venv\Scripts\python.exe main.py
```

```powershell
# 터미널 2: FastAPI Backend (권장: backend_python 폴더에서 uvicorn으로 실행)
cd C:\mini_agent\optional_multimodal_agent\backend_python
uvicorn app.main:app --reload

# 또는 프로젝트 루트에서(대체):
..\.venv\Scripts\python.exe -m backend_python.app.main
```

```powershell
# 터미널 3: Redis 작업을 처리하는 Agent Worker (권장: 별도 프로세스)
# 프로젝트 루트에서 모듈로 실행:
..\.venv\Scripts\python.exe -m backend_python.app.worker

# 또는 backend_python/app 폴더에서 직접 실행:
cd C:\mini_agent\optional_multimodal_agent\backend_python\app
..\..\.venv\Scripts\python.exe worker.py
```

```powershell
# 터미널 4: Streamlit Frontend (권장: frontend 폴더에서 실행)
cd C:\mini_agent\optional_multimodal_agent\frontend
streamlit run app.py

# 또는 프로젝트 루트에서(대체):
..\.venv\Scripts\python.exe -m streamlit run frontend/app.py
```

브라우저에서 `http://localhost:8501`을 엽니다. 카메라 권한을 허용하거나 샘플 이미지를 업로드합니다. 음성 질문은 최대 120초 WAV, 이미지는 JPEG·PNG·WEBP를 지원합니다.

서비스 상태 확인:

```powershell
.\.venv\Scripts\python.exe -m scripts.check_services
```

## 5. 전체 흐름

```text
Streamlit에서 사진·질문 입력
        ↓
FastAPI가 파일 저장 및 작업 등록
        ↓
Redis 작업 큐 → Python Worker가 Agent 실행
        ↓
MCP Tool Server
├─ 이미지 분석·STT·TTS
├─ 업무 데이터 조회 → PostgreSQL
└─ RAG 검색 → Ollama embeddinggemma + pgvector
        ↓
Worker가 Redis에 진행 상태 저장
        ↓
FastAPI SSE → Streamlit 화면 갱신
```

실행 상태는 `queued → running → completed / needs_input / failed` 순서로 바뀝니다. 진행 이벤트에는 Tool 시작·완료·실패만 기록합니다. TTS가 실패해도 텍스트 답변은 유지됩니다.

## 6. 디렉터리와 코드 읽는 순서

```text
optional_multimodal_agent/
├─ frontend/          Streamlit 화면
├─ backend_python/    FastAPI, Agent, Worker, Redis·SSE
├─ mcp_server/        이미지·음성·RAG·DB Tool
├─ shared/            공통 설정과 미디어 처리
├─ sql/               테이블 생성과 가상 데이터
├─ data/rag/          RAG Markdown 문서
├─ data/samples/      촬영·업로드용 이미지
├─ scripts/           DB 준비, RAG 적재, 서비스 확인
└─ tests/             자동 테스트
```

1. `frontend/app_pages/01_product_agent.py`: 사진과 질문 입력
2. `backend_python/app/routers/runs.py`: 작업 등록과 SSE API
3. `backend_python/app/worker.py`: Redis 작업 처리
4. `backend_python/app/agents/product_agent.py`: Agent 지침과 허용 Tool
5. `backend_python/app/agents/runner.py`: Tool 호출과 답변 생성
6. `mcp_server/tools/product_tools.py`: MCP Tool
7. `mcp_server/database/product_queries.py`: DB 조회
8. `backend_python/app/stores/`: Redis 상태·이벤트·작업 큐

## 7. Frontend와 Backend

Streamlit은 `st.camera_input`, `st.audio_input`, `st.audio`를 사용합니다. Python 코드가 Backend SSE를 수신하므로 별도 HTML이나 JavaScript는 없습니다. 새로고침하면 실행 ID와 마지막 이벤트 ID를 이용해 진행 상태를 복원합니다.

FastAPI 문서: `http://127.0.0.1:8000/docs`

| API                          | 기능                        |
| ---------------------------- | --------------------------- |
| `POST /api/media/image`      | 이미지 업로드               |
| `POST /api/media/audio`      | WAV 음성 업로드             |
| `GET /api/media/{id}`        | 이미지·생성 음성 조회       |
| `POST /api/runs`             | Agent 작업 등록             |
| `GET /api/runs/{id}`         | 실행 상태와 결과 조회       |
| `GET /api/runs/{id}/events`  | 진행 상황 SSE 수신          |
| `POST /api/runs/{id}/input`  | 추가 질문 또는 새 사진 전달 |
| `POST /api/runs/{id}/speech` | 최종 답변 음성 재생성       |

Worker가 실행되지 않으면 작업은 `queued` 상태로 기다립니다.

## 8. MCP Tool

MCP Server 주소는 `http://127.0.0.1:8020/mcp`입니다.

| Tool                         | 역할                               |
| ---------------------------- | ---------------------------------- |
| `analyze_scene`              | 제품 사진과 라벨 분석              |
| `read_document`              | 안내문 사진과 코드 분석            |
| `transcribe_audio`           | 녹음을 질문 텍스트로 변환          |
| `synthesize_speech`          | 최종 답변을 MP3로 생성             |
| `find_products`              | 제품 후보 조회                     |
| `get_compatible_accessories` | 호환 액세서리 조회                 |
| `get_product_availability`   | 가격과 매장별 재고 조회            |
| `find_programs`              | 프로그램과 시설 확인               |
| `get_program_sessions`       | 회차와 잔여 정원 조회              |
| `search_product_manuals`     | 제품 설명서 RAG 검색               |
| `search_facility_guides`     | 프로그램 안내와 시설 규정 RAG 검색 |

Agent는 임의 SQL이나 로컬 파일 경로를 Tool에 전달하지 않습니다. DB Tool은 정해진 인자만 받고 읽기 전용 SQL을 실행합니다.

## 9. PostgreSQL

| 영역     | 테이블                                                                                          | 내용                    |
| -------- | ----------------------------------------------------------------------------------------------- | ----------------------- |
| 제품     | `multimodal_products`, `multimodal_product_compatibility`                                       | 제품과 호환 관계        |
| 재고     | `multimodal_stores`, `multimodal_inventory`                                                     | 매장과 재고             |
| 시설     | `multimodal_facilities`, `multimodal_programs`                                                  | 시설과 프로그램         |
| 일정     | `multimodal_program_sessions`                                                                   | 회차와 잔여 정원        |
| RAG      | `multimodal_knowledge_documents`, `multimodal_knowledge_chunks`                                 | 문서와 768차원 벡터     |
| RAG 연결 | `multimodal_product_documents`, `multimodal_facility_documents`, `multimodal_program_documents` | 업무 데이터와 문서 연결 |

`sql/01_extensions.sql`부터 `sql/04_knowledge_tables.sql`까지 번호 순서로 실행합니다. 별도 일반 인덱스와 벡터 인덱스는 사용하지 않습니다.

## 10. RAG 문서 추가

별도 manifest 파일은 없습니다. 적재 스크립트가 Markdown 파일을 자동으로 찾습니다.

```text
data/rag/
├─ products/       제품 설명서
└─ facilities/     프로그램 안내와 시설 규정
```

| 파일                    | 연결 대상          |
| ----------------------- | ------------------ |
| `products/MM-K100.md`   | 제품 `MM-K100`     |
| `facilities/PG-YOGA.md` | 프로그램 `PG-YOGA` |
| `facilities/F01.md`     | 시설 `F01`         |

파일 이름은 DB의 대상 ID와 같아야 합니다. Markdown 첫 줄의 `# 제목`은 Agent가 보여주는 출처 제목입니다. 문서를 추가하거나 수정한 뒤 다시 적재합니다.

```powershell
.\.venv\Scripts\python.exe -m scripts.ingest_knowledge
```

## 11. 실습 시나리오

| 샘플 이미지                    | 질문                    | 확인할 동작                         |
| ------------------------------ | ----------------------- | ----------------------------------- |
| `product_labels/MM-K100.png`   | 사용법·호환 필터·재고   | 제품 확인, 매뉴얼 출처, AC-K10 재고 |
| `product_labels/MM-A300.png`   | 필터 주의사항·재고      | 물세척 금지와 AC-A30 품절           |
| `product_labels/unclear.png`   | 사용법                  | 모델을 추측하지 않고 추가 입력 요청 |
| `facility_notices/PG-YOGA.png` | 초보 참가·향후 4주 자리 | 준비물, 첫 회차 마감, DB 정보 확인  |
| `facility_notices/PG-DRAW.png` | 일정·준비물             | 두 번째 회차 취소 확인              |
| `product_labels/MM-K100.png`   | 해외 전압 호환          | 근거가 없음을 알리고 추측하지 않음  |

`data/samples/scenarios.json`은 위 내용을 구조화한 수동 실습 자료이며 Agent가 실행 중 읽지는 않습니다.

## 12. 테스트

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

테스트는 미디어 검증, Redis 상태 전환, SSE 재연결, Agent Tool 호출, API 입력과 Streamlit 화면을 확인합니다. 테스트 대역을 사용하므로 OpenAI API 비용은 발생하지 않습니다.

## 실행 범위

- Redis 상태와 이벤트는 기본 24시간 보관하며 키에 `mm:` 접두사를 사용합니다.
- 이미지와 음성은 UUID 파일명으로 `storage`에 저장하고 Redis에는 파일 ID만 보관합니다.
- 추가 입력은 이전 답변을 포함한 새 실행이며 장기 대화 메모리는 아닙니다.
- 스마트폰 등 다른 장치에서 카메라를 사용하려면 HTTPS 환경이 필요합니다.
- 인증 없는 로컬 학습용이므로 외부 공개 서비스로 사용하지 않습니다.
