"""세 독립 Single Agent의 Tool을 제공하는 Streamable HTTP MCP Server입니다."""

import os
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8010"))

mcp = FastMCP(
    "mini-agent-06-business-tools",
    instructions="여행, 고객 지원과 주문 도우미 Agent가 사용하는 교육용 Tool Server입니다.",
    host=MCP_HOST,
    port=MCP_PORT,
    stateless_http=True,
    json_response=True,
)

WEATHER = {"서울": {"condition": "맑음", "temperature_c": 24}, "제주": {"condition": "비", "temperature_c": 21}}
INDOOR = {"서울": ["국립중앙박물관", "서울시립미술관"], "제주": ["제주현대미술관", "아쿠아플라넷"]}
OUTDOOR = {"서울": ["서울숲", "북한산"], "제주": ["비자림", "성산일출봉"]}
ORDERS = {
    "ORDER-1001": {"status": "배송 중", "delivered": False, "purchased_days_ago": 3},
    "ORDER-1002": {"status": "배송 완료", "delivered": True, "purchased_days_ago": 10},
}
PRODUCTS = {
    "P-KEYBOARD": {"name": "무선 키보드", "price": 45_000, "stock": 7},
    "P-MOUSE": {"name": "무선 마우스", "price": 28_000, "stock": 0},
}


@mcp.tool()
def get_weather(city: str) -> dict:
    """한국 도시의 현재 날씨를 조회합니다."""
    city = city.strip()
    data = WEATHER.get(city)
    return {"success": data is not None, "city": city, **(data or {"error": "CITY_NOT_FOUND"})}


@mcp.tool()
def search_indoor_places(city: str) -> dict:
    """비 오는 날에 적합한 실내 장소를 검색합니다."""
    city = city.strip()
    if not city:
        return {"success": False, "city": city, "error": "INVALID_CITY"}
    return {"success": True, "city": city, "category": "indoor", "items": INDOOR.get(city, [])}


@mcp.tool()
def search_outdoor_places(city: str) -> dict:
    """맑은 날에 적합한 야외 장소를 검색합니다."""
    city = city.strip()
    if not city:
        return {"success": False, "city": city, "error": "INVALID_CITY"}
    return {"success": True, "city": city, "category": "outdoor", "items": OUTDOOR.get(city, [])}


@mcp.tool()
def get_order_status(order_id: str) -> dict:
    """주문 번호로 현재 주문 상태와 구매 경과일을 조회합니다."""
    order_id = order_id.strip().upper()
    data = ORDERS.get(order_id)
    return {"success": data is not None, "order_id": order_id, **(data or {"error": "ORDER_NOT_FOUND"})}


@mcp.tool()
def search_return_policy() -> dict:
    """현재 반품 정책을 조회합니다."""
    return {
        "success": True,
        "return_window_days": 14,
        "conditions": ["상품 훼손 없음", "구성품 보유"],
        "source": "learning-return-policy",
    }


@mcp.tool()
def search_product(query: str) -> dict:
    """상품명으로 상품 ID와 가격을 검색합니다."""
    normalized = query.strip().lower()
    if not normalized:
        return {"success": False, "query": query, "error": "INVALID_QUERY", "items": []}
    items = [
        {"product_id": product_id, "name": data["name"], "price": data["price"]}
        for product_id, data in PRODUCTS.items()
        if normalized in data["name"].lower()
    ]
    return {"success": True, "query": query, "items": items}


@mcp.tool()
def check_inventory(product_id: str) -> dict:
    """상품 ID로 현재 주문 가능한 재고를 확인합니다."""
    product_id = product_id.strip().upper()
    data = PRODUCTS.get(product_id)
    if data is None:
        return {"success": False, "product_id": product_id, "error": "PRODUCT_NOT_FOUND"}
    return {"success": True, "product_id": product_id, "stock": data["stock"]}


@mcp.tool()
def calculate_order_total(product_id: str, quantity: int) -> dict:
    """상품 ID와 수량으로 예상 주문 금액을 계산합니다. 주문을 생성하지 않습니다."""
    product_id = product_id.strip().upper()
    if quantity < 1:
        raise ValueError("quantity는 1 이상이어야 합니다.")
    data = PRODUCTS.get(product_id)
    if data is None:
        return {"success": False, "product_id": product_id, "error": "PRODUCT_NOT_FOUND"}
    if data["stock"] < quantity:
        return {"success": False, "product_id": product_id, "error": "INSUFFICIENT_STOCK", "stock": data["stock"]}
    return {
        "success": True,
        "product_id": product_id,
        "quantity": quantity,
        "unit_price": data["price"],
        "total": data["price"] * quantity,
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
