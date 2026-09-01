# 05 Memory 과제

교육 상담 Agent의 사용자 Memory를 구현합니다.

저장 후보:

- 학습 목표
- 선호 수업 시간
- 현재 Python 수준

필수 기능:

1. 사용자별 저장·조회·수정·삭제
2. 최근 대화 Window
3. 질문에 관련된 Memory만 선택
4. 민감정보와 허용되지 않은 key 차단
5. 선택한 Memory를 사용한 개인화 답변
6. 사용한 Memory를 사용자에게 표시

완료 기준:

- 사용자 A가 B의 Memory에 접근할 수 없습니다.
- 저장 전·수정 후·삭제 후 답변 차이를 설명할 수 있습니다.
- 사용자가 자신의 Memory 목록을 확인할 수 있습니다.
- Redis 단기 상태와 PostgreSQL 장기 Memory를 구분합니다.
- 비밀번호나 인증정보를 저장하지 않습니다.
- Redis Key가 사용자와 Session을 함께 구분합니다.
- 오래된 version이 최신 Session을 덮어쓰지 않습니다.
- PostgreSQL 조회·삭제가 항상 user_id 범위를 강제합니다.
- 실제 답변에 사용된 Memory와 Trace를 표시합니다.
- 사용자가 자신의 Memory를 내보내고 전체 삭제할 수 있습니다.
