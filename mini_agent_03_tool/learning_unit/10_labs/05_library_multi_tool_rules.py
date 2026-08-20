"""여러 조회 Tool Result를 모은 뒤 서버의 도서 대출 규칙을 적용합니다."""

from typing import Any


MEMBERS = {
    "M100": {"name": "김민준", "active": True, "overdue": False},
    "M200": {"name": "이서연", "active": True, "overdue": True},
}
BOOKS = {
    "B101": {"title": "파이썬 첫걸음", "available": True},
    "B102": {"title": "에이전트 설계", "available": False},
}
LOANS = {"M100": ["B201", "B202"], "M200": ["B203"]}
MAX_LOANS = 3


def get_member(member_id: str) -> dict[str, Any]:
    return {"member_id": member_id, "member": MEMBERS.get(member_id)}


def get_book(book_id: str) -> dict[str, Any]:
    return {"book_id": book_id, "book": BOOKS.get(book_id)}


def get_current_loans(member_id: str) -> dict[str, Any]:
    loans = LOANS.get(member_id, [])
    return {"member_id": member_id, "book_ids": loans.copy(), "count": len(loans)}


def evaluate_loan(member_result: dict, book_result: dict, loans_result: dict) -> dict[str, Any]:
    """LLM 답변이 아니라 백엔드 업무 규칙이 대출 가능 여부를 결정합니다."""
    member = member_result["member"]
    book = book_result["book"]
    if member is None:
        return {"allowed": False, "reason": "회원 정보를 찾을 수 없습니다."}
    if not member["active"]:
        return {"allowed": False, "reason": "비활성 회원입니다."}
    if member["overdue"]:
        return {"allowed": False, "reason": "연체 도서가 있습니다."}
    if book is None:
        return {"allowed": False, "reason": "도서 정보를 찾을 수 없습니다."}
    if not book["available"]:
        return {"allowed": False, "reason": "이미 대출 중인 도서입니다."}
    if loans_result["count"] >= MAX_LOANS:
        return {"allowed": False, "reason": "최대 대출 권수를 초과합니다."}
    return {"allowed": True, "reason": "대출할 수 있습니다."}


def request_loan(member_id: str, book_id: str) -> dict[str, Any]:
    tool_results = {
        "member": get_member(member_id),
        "book": get_book(book_id),
        "loans": get_current_loans(member_id),
    }
    decision = evaluate_loan(tool_results["member"], tool_results["book"], tool_results["loans"])
    if decision["allowed"]:
        LOANS.setdefault(member_id, []).append(book_id)
        BOOKS[book_id]["available"] = False
    return {"tool_results": tool_results, "decision": decision}


if __name__ == "__main__":
    for member_id, book_id in (("M100", "B101"), ("M200", "B101"), ("M100", "B102")):
        print(f"\n요청: {member_id} / {book_id}")
        print(request_loan(member_id, book_id))
