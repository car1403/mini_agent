# 04 RAG 과제

## 필수 과제

새로운 여행 정책 문서 두 개를 추가하고 다음 결과를 제출합니다.

1. 문서를 Chunk로 나눈 결과
2. 질문별 상위 2개 검색 결과와 점수
3. 최종 답변과 출처
4. 근거가 없는 질문에 대한 제한 답변
5. 같은 질문의 Redis Cache MISS·HIT와 TTL
6. 재색인 후 Cache 무효화 결과
7. 직접 입력한 문장과 의미가 유사한 질문의 pgvector 검색 결과
8. PDF 한 개의 Chunk·페이지 Metadata와 질문별 상위 검색 결과
9. Agent의 검색 Tool Call·Tool Result·출처가 포함된 최종 답변
10. 활성 문서만 선택하는 Metadata Filter와 임계값 적용 전후 결과
11. 키워드·pgvector·Hybrid 검색 순위 비교와 RRF 결과

## 선택 과제

키워드 검색과 pgvector 검색이 서로 다른 문서를 1위로 선택하는 질문을 찾아 그 이유를 설명합니다.

## 독립 Lab 제출 항목

1. 고객지원 Agent의 Tool Call·Tool Result와 Redis MISS→HIT Trace
2. 정책 version 2 색인 후 오래된 Chunk 제거와 Cache 무효화 결과
3. 상품 카테고리·최대 가격 적용 전후와 Hybrid 검색 순위
4. 직원·관리자·HR 역할별 ACL 검색 결과와 역할별 Cache Key 구분
5. PDF 페이지 Metadata, 재색인 전후 Chunk 수, 질문별 출처
6. Keyword·Vector·Hybrid의 Hit@K·MRR와 실패 사례 분석
7. Multi-Tool Agent의 재질문, 선택 Tool, 최대 단계, 종료 사유

## 완료 기준

- 답변에 사용한 출처가 표시됩니다.
- 검색 결과가 없을 때 내용을 지어내지 않습니다.
- 문서 저장과 질문 검색에 같은 Embedding 모델을 사용합니다.
- 재색인해도 같은 Chunk가 중복 저장되지 않습니다.
- Cache Key가 collection·질문·검색 조건·Provider를 구분합니다.
- PDF 검색 결과에 원본 파일명과 페이지 번호가 표시됩니다.
- Agent는 임의 SQL이 아니라 허용된 검색 Tool만 호출합니다.
- Agent 답변은 Tool Result에 없는 내용을 정책처럼 지어내지 않습니다.
- 만료 문서는 Metadata Filter 적용 후 검색 결과에서 제외됩니다.
- Hybrid Search는 서로 다른 점수의 단순 합이 아니라 순위 결합을 사용합니다.
- API Key나 DB 비밀번호를 코드에 직접 작성하지 않습니다.
