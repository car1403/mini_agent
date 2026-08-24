"""7개 Lab에서 재사용하는 조회·상태 변경 Mock Tool입니다.

Tool은 전달받은 하나의 동작만 수행합니다. 어떤 Tool을 언제 호출할지는 Agent 또는
Workflow가 결정하고, 승인·인증·동시성 같은 업무 정책은 Service가 소유합니다.
실제 장치나 외부 서비스 대신 In-memory Mock Repository에만 접근합니다.
"""
from datetime import date, datetime, timezone
from dataclasses import dataclass
from typing import Any
from collections.abc import Callable

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.repositories.lab_repository import lab_repository

WEATHER = {"서울": ("맑음", 27), "부산": ("비", 23), "제주": ("바람", 25)}
ATTRACTIONS = {"서울": ["경복궁", "서울숲"], "부산": ["해운대", "감천문화마을"], "제주": ["성산일출봉", "비자림"]}

def parking_entry(plate_number: str) -> dict[str, Any]:
    """Workflow가 승인과 사용자 확인을 끝낸 뒤 호출하는 게이트 상태 변경 Tool입니다."""
    vehicle = lab_repository.vehicles.get(plate_number)
    if vehicle is None: return {"opened": False, "reason": "등록되지 않은 차량입니다."}
    if not vehicle["active"]: return {"opened": False, "reason": "출입 권한이 비활성 상태입니다."}
    lab_repository.gate_open = True
    return {"opened": True, "plate_number": plate_number}

def lookup_vehicle(plate_number: str) -> dict[str, Any]:
    """차량 사실만 반환하는 읽기 Tool이며 출입 허용 여부를 결정하지 않습니다."""
    vehicle = lab_repository.vehicles.get(plate_number)
    return {"plate_number": plate_number, "registered": vehicle is not None, "active": bool(vehicle and vehicle["active"])}

def control_air_conditioner(temperature_c: float) -> dict[str, Any]:
    """Workflow가 선택한 히스테리시스 결과를 Mock 장치 상태에 반영합니다."""
    if not -40 <= temperature_c <= 80: return {"success": False, "reason": "센서 값이 허용 범위를 벗어났습니다."}
    power, action = lab_repository.air_conditioner["power"], "keep"
    if temperature_c >= 27 and power == "off": power, action = "on", "turn_on"
    elif temperature_c <= 23 and power == "on": power, action = "off", "turn_off"
    lab_repository.air_conditioner["power"] = power
    return {"success": True, "temperature_c": temperature_c, "power": power, "action": action}

def open_locker(locker_id: str, code: str) -> dict[str, Any]:
    """확인된 일회성 action에서만 호출되는 택배함 상태 변경 Tool입니다."""
    locker = lab_repository.lockers.get(locker_id)
    if locker is None: return {"opened": False, "reason": "택배함을 찾을 수 없습니다."}
    if locker["used"]: return {"opened": False, "reason": "이미 사용한 인증 코드입니다."}
    if datetime.now(timezone.utc) > locker["expires_at"]: return {"opened": False, "reason": "인증 코드가 만료되었습니다."}
    if locker["code"] != code: return {"opened": False, "reason": "인증 코드가 올바르지 않습니다."}
    locker["used"] = True
    return {"opened": True, "locker_id": locker_id}

def inspect_locker(locker_id: str, code: str) -> dict[str, Any]:
    """문을 열지 않고 코드·만료·재사용 상태를 검사하는 읽기 전용 단계입니다."""
    locker = lab_repository.lockers.get(locker_id)
    if locker is None: return {"valid": False, "reason": "택배함을 찾을 수 없습니다."}
    if locker["used"]: return {"valid": False, "reason": "이미 사용한 인증 코드입니다."}
    if datetime.now(timezone.utc) > locker["expires_at"]: return {"valid": False, "reason": "인증 코드가 만료되었습니다."}
    if locker["code"] != code: return {"valid": False, "reason": "인증 코드가 올바르지 않습니다."}
    return {"valid": True, "locker_id": locker_id}

def get_inventory(sku: str) -> dict[str, Any]:
    """예약 전 현재 수량과 Version을 반환하는 읽기 Tool입니다."""
    item = lab_repository.inventory.get(sku)
    return {"sku": sku, **item} if item else {"sku": sku, "not_found": True}

def reserve_inventory(sku: str, quantity: int, expected_version: int) -> dict[str, Any]:
    """실행 직전 Version과 수량을 재검사하는 조건부 상태 변경 Tool입니다."""
    item = lab_repository.inventory.get(sku)
    if item is None: return {"reserved": False, "code": "NOT_FOUND"}
    if item["version"] != expected_version: return {"reserved": False, "code": "VERSION_CONFLICT", "current": item.copy()}
    if item["available"] < quantity: return {"reserved": False, "code": "INSUFFICIENT_STOCK", "current": item.copy()}
    item["available"] -= quantity; item["version"] += 1
    return {"reserved": True, "sku": sku, "quantity": quantity, **item}

def get_member(member_id: str) -> dict[str, Any]:
    return {"member_id": member_id, "member": lab_repository.members.get(member_id)}

def get_book(book_id: str) -> dict[str, Any]:
    return {"book_id": book_id, "book": lab_repository.books.get(book_id)}

def get_current_loans(member_id: str) -> dict[str, Any]:
    return {"member_id": member_id, "loans": lab_repository.loans.get(member_id, []).copy()}

def library_facts(member_id: str, book_id: str) -> dict[str, Any]:
    """기존 호출자를 위한 일괄 조회 함수입니다."""
    return {
        "member": get_member(member_id)["member"],
        "book": get_book(book_id)["book"],
        "loans": get_current_loans(member_id)["loans"],
    }

def evaluate_loan(facts: dict[str, Any]) -> dict[str, Any]:
    """상태를 변경하지 않고 현재 근거로 대출 정책만 평가합니다."""
    member, book, loans = facts["member"], facts["book"], facts["loans"]
    if member is None or book is None: return {"allowed": False, "reason": "회원 또는 도서를 찾을 수 없습니다."}
    if not member["active"] or member["overdue"]: return {"allowed": False, "reason": "회원 상태로 인해 대출할 수 없습니다."}
    if not book["available"] or len(loans) >= 3: return {"allowed": False, "reason": "도서 상태 또는 대출 권수를 확인해 주세요."}
    return {"allowed": True, "reason": "대출 가능한 상태입니다."}

def apply_loan(member_id: str, book_id: str) -> dict[str, Any]:
    """확인 시점의 최신 상태를 다시 읽고 정책을 통과한 경우에만 변경합니다."""
    facts = library_facts(member_id, book_id)
    decision = evaluate_loan(facts)
    if not decision["allowed"]: return decision
    book = lab_repository.books[book_id]
    lab_repository.loans.setdefault(member_id, []).append(book_id); book["available"] = False
    return {"allowed": True, "reason": "대출이 완료되었습니다."}

def get_travel_weather(city: str, travel_date: str) -> dict[str, Any]:
    target = date.fromisoformat(travel_date)
    result = travel_data(city, target)
    return {"found": result["found"], "city": city, "travel_date": travel_date, "weather": result.get("weather")}

def search_travel_attractions(city: str) -> dict[str, Any]:
    return {"found": city in ATTRACTIONS, "city": city, "attractions": ATTRACTIONS.get(city, [])}

def create_mock_order(menu: str, size: str, quantity: int) -> dict[str, Any]:
    return {"accepted": True, "menu": menu, "size": size, "quantity": quantity}

def travel_data(city: str, travel_date: date) -> dict[str, Any]:
    """여행 Agent가 선택한 읽기 작업을 고정 Mock 데이터로 수행합니다."""
    weather = WEATHER.get(city)
    if weather is None: return {"found": False, "city": city}
    condition, temperature = weather if travel_date == date.today() else (("비" if travel_date.day % 2 == 0 else "맑음"), 22)
    preparation = ["편한 신발"]
    if condition == "비": preparation.append("우산")
    if temperature <= 23: preparation.append("얇은 겉옷")
    return {"found": True, "city": city, "travel_date": travel_date.isoformat(), "weather": {"condition": condition, "temperature_c": temperature}, "attractions": ATTRACTIONS[city], "preparation": preparation}


class _StrictArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

class MemberArgs(_StrictArgs):
    member_id: str = Field(min_length=1, max_length=50)

class BookArgs(_StrictArgs):
    book_id: str = Field(min_length=1, max_length=50)

class LoanArgs(MemberArgs, BookArgs):
    pass

class TravelWeatherArgs(_StrictArgs):
    city: str = Field(min_length=1, max_length=50)
    travel_date: date

class TravelAttractionArgs(_StrictArgs):
    city: str = Field(min_length=1, max_length=50)

class MockOrderArgs(_StrictArgs):
    menu: str = Field(min_length=1, max_length=50)
    size: str = Field(min_length=1, max_length=20)
    quantity: int = Field(ge=1, le=20)

LabToolFunction = Callable[[BaseModel], dict[str, Any]]

@dataclass(frozen=True)
class LabToolSpec:
    input_model: type[BaseModel]
    function: LabToolFunction

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return self.function(self.input_model.model_validate(arguments))

LAB_TOOL_REGISTRY: dict[str, LabToolSpec] = {
    "get_member": LabToolSpec(MemberArgs, lambda args: get_member(args.member_id)),
    "get_book": LabToolSpec(BookArgs, lambda args: get_book(args.book_id)),
    "get_current_loans": LabToolSpec(MemberArgs, lambda args: get_current_loans(args.member_id)),
    "apply_library_loan": LabToolSpec(LoanArgs, lambda args: apply_loan(args.member_id, args.book_id)),
    "get_current_weather": LabToolSpec(TravelWeatherArgs, lambda args: get_travel_weather(args.city, args.travel_date.isoformat())),
    "get_weather_forecast": LabToolSpec(TravelWeatherArgs, lambda args: get_travel_weather(args.city, args.travel_date.isoformat())),
    "search_attractions": LabToolSpec(TravelAttractionArgs, lambda args: search_travel_attractions(args.city)),
    "create_mock_order": LabToolSpec(MockOrderArgs, lambda args: create_mock_order(args.menu, args.size, args.quantity)),
}

def execute_lab_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """통합 Lab Tool을 Allowlist와 Pydantic 검증 뒤 실행합니다."""
    spec = LAB_TOOL_REGISTRY.get(name)
    if spec is None:
        return {"success": False, "tool_name": name, "error": {"code": "TOOL_NOT_ALLOWED"}}
    try:
        return {"success": True, "tool_name": name, "data": spec.execute(arguments)}
    except ValidationError as error:
        return {"success": False, "tool_name": name, "error": {"code": "TOOL_VALIDATION_ERROR", "details": error.errors()}}
    except Exception as error:
        return {"success": False, "tool_name": name, "error": {"code": "TOOL_EXECUTION_ERROR", "message": str(error)}}
