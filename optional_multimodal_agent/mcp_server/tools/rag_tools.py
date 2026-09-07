from mcp_server.rag.search import retrieve

async def search_product_manuals(product_id: str, question: str) -> dict:
    """확인된 제품의 매뉴얼에서 사용법·주의사항을 검색합니다. 문서 출처와 섹션을 반환합니다."""
    return await retrieve("product",product_id,question)

async def search_facility_guides(program_id: str, question: str) -> dict:
    """확인된 프로그램 및 시설의 참가 조건·준비물·이용 규정 문서를 검색합니다."""
    return await retrieve("program",program_id,question)
