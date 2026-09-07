from datetime import date, datetime, timezone
from mcp_server.database import facility_queries as db

def find_programs(term: str) -> dict:
    """안내문의 프로그램 코드, 프로그램명 또는 시설명으로 현재 DB의 프로그램을 확인합니다."""
    if not term.strip() or len(term)>100:
        raise ValueError("검색어는 1~100자입니다.")
    return {"items": db.programs(term), "source": "programs"}

def get_program_sessions(program_id: str, date_from: date, date_to: date) -> dict:
    """기간의 프로그램 회차·잔여 정원·취소 상태를 조회합니다. 날짜는 YYYY-MM-DD, 최대 90일입니다."""
    if not 0 <= (date_to-date_from).days <= 90:
        raise ValueError("조회 기간은 0~90일입니다.")
    return {"items": db.sessions(program_id,date_from,date_to), "queried_at": datetime.now(timezone.utc).isoformat(), "source": "program_sessions"}
