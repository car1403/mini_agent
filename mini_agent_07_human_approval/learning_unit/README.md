# 07 Human Approval and Safety

Agent가 제안한 작업을 곧바로 실행하지 않고, **정책 검사 → 승인 대기 → 안전한 실행** 순서로 처리합니다.

## 학습 목표

- 조회와 변경 작업의 위험도를 구분합니다.
- 허용된 Tool과 요청 소유자를 코드로 검사합니다.
- 일반 Python으로 중단·저장·재개를 먼저 이해합니다.
- LangGraph의 `interrupt()`와 `Command(resume=...)`를 사용합니다.
- 승인·거절·잘못된 결정·중복 실행을 구분합니다.
- 승인 뒤에도 실제 결제 대신 교육용 Mock 작업만 실행합니다.

## 전체 흐름

```text
사용자 요청 / LLM의 Tool 제안
→ Tool allowlist 검사
→ 요청 소유자 검사
→ 작업 위험도 분류
→ 변경 작업이면 승인 대기
→ 승인한 경우에만 Mock 실행
→ 처리 기록 저장
```

LLM은 작업을 **제안**할 뿐입니다. 실행 허용 여부는 Prompt가 아니라 애플리케이션 코드가 결정합니다.

## 예제 순서

| 순서 | 파일 | 핵심 내용 |
|---|---|---|
| 7-1 | `01_action_risk.py` | 조회·초안·변경·금지 작업 분류 |
| 7-2 | `02_allowlist_and_ownership.py` | Tool allowlist와 소유자 검사 |
| 7-3 | `03_pause_save_resume.py` | 일반 Python 중단·저장·재개 |
| 7-4 | `04_langgraph_interrupt.py` | LangGraph interrupt와 동일한 thread 재개 |
| 7-5 | `05_approve_and_reject.py` | 승인·거절·잘못된 결정 검증 |
| 7-6 | `06_safe_execution.py` | 승인 뒤 Mock 실행과 중복 실행 방지 |

## 실행

```powershell
python .\01_action_risk.py
python .\02_allowlist_and_ownership.py
python .\03_pause_save_resume.py
python .\04_langgraph_interrupt.py
python .\05_approve_and_reject.py
python .\06_safe_execution.py
```

`04_langgraph_interrupt.py`만 `langgraph` 패키지가 필요합니다. 나머지는 Python 표준 라이브러리만 사용합니다.

## 꼭 기억할 규칙

### 1. 재개 정보는 구조화합니다

```python
{"decision": "approve", "actor": "user-01", "note": "내용 확인"}
```

자유로운 문장 하나보다 결정·승인자·메모를 분리한 데이터가 검사와 기록에 안전합니다.

### 2. 같은 실행은 같은 thread로 재개합니다

LangGraph 중단·재개에는 checkpointer와 같은 `thread_id`가 필요합니다. 다른 ID로 재개하면 기존 실행 상태를 찾을 수 없습니다.

### 3. Side Effect는 interrupt 뒤에 둡니다

중단된 Node는 재개할 때 처음부터 다시 실행될 수 있습니다. 예약·결제·메시지 전송 같은 변경 작업은 `interrupt()` 앞에 두지 않습니다.

### 4. 승인도 인증은 아닙니다

예제의 `actor` 문자열 검사는 개념 학습용입니다. 운영 환경에서는 로그인 세션이나 검증된 토큰에서 사용자 ID를 가져와야 합니다.

## 이번 단계에서 다루지 않는 것

- 실제 예약과 결제
- 승인 내용 수정(`edit`)과 여러 명의 동시 승인
- 영구 저장형 checkpointer
- LangChain Human-in-the-loop middleware

먼저 직접 만든 작은 승인 흐름을 이해한 뒤, 필요할 때 위 기능으로 확장합니다.
