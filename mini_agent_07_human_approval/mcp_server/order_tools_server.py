"""Safe Order Agent의 Tool을 제공하는 Streamable HTTP MCP Server입니다."""

import os

from mcp.server.fastmcp import FastMCP


MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8010"))

mcp = FastMCP(
    "mini-agent-07-order-tools",
    instructions="상품 조회와 승인된 주문 생성을 제공하는 교육용 Tool Server입니다.",
    host=MCP_HOST,
    port=MCP_PORT,
    stateless_http=True,
    json_response=True,
)

PRODUCTS = {
    "P-KEYBOARD": {"name": "무선 키보드", "price": 45_000, "stock": 7},
    "P-MOUSE": {"name": "무선 마우스", "price": 28_000, "stock": 0},
}
PLACED_ORDERS: list[dict] = []


@mcp.tool()
def search_product(query: str) -> dict:
    """상품명으로 상품 ID와 가격을 검색하는 읽기 Tool입니다."""
    normalized = query.strip().lower()
    items = [
        {"product_id": product_id, "name": data["name"], "price": data["price"]}
        for product_id, data in PRODUCTS.items()
        if normalized in data["name"].lower()
    ]
    return {"success": True, "query": query, "items": items}


@mcp.tool()
def check_inventory(product_id: str) -> dict:
    """상품 ID로 현재 주문 가능한 재고를 확인하는 읽기 Tool입니다."""
    product_id = product_id.strip().upper()
    data = PRODUCTS.get(product_id)
    if data is None:
        return {"success": False, "product_id": product_id, "error": "PRODUCT_NOT_FOUND"}
    return {"success": True, "product_id": product_id, "stock": data["stock"]}


@mcp.tool()
def calculate_order_total(product_id: str, quantity: int) -> dict:
    """상품과 수량으로 예상 금액을 계산하는 읽기 Tool입니다."""
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


@mcp.tool()
def place_order(product_id: str, quantity: int) -> dict:
    """승인된 주문을 생성하고 재고를 차감하는 변경 Tool입니다."""
    product_id = product_id.strip().upper()
    if quantity < 1:
        raise ValueError("quantity는 1 이상이어야 합니다.")
    data = PRODUCTS.get(product_id)
    if data is None:
        return {"success": False, "product_id": product_id, "error": "PRODUCT_NOT_FOUND"}
    if data["stock"] < quantity:
        return {"success": False, "product_id": product_id, "error": "INSUFFICIENT_STOCK", "stock": data["stock"]}
    data["stock"] -= quantity
    item = {
        "order_id": f"NEW-{len(PLACED_ORDERS) + 1:04d}",
        "product_id": product_id,
        "quantity": quantity,
        "total": data["price"] * quantity,
        "remaining_stock": data["stock"],
    }
    PLACED_ORDERS.append(item)
    return {"success": True, **item}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
