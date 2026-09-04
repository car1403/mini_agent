"""PostgreSQL 여행 데이터를 제공하는 Streamable HTTP MCP Server."""

from datetime import date
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
import psycopg


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8020"))

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL이 필요합니다.")

mcp = FastMCP(
    "optional-multimodal-travel-tools",
    instructions="PostgreSQL에서 날씨, 숙소, 관광지 정보를 조회합니다.",
    host=MCP_HOST,
    port=MCP_PORT,
    stateless_http=True,
    json_response=True,
)


def load_items(tool_name: str, city: str) -> list[dict]:
    with psycopg.connect(DATABASE_URL) as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT payload
            FROM optional_multimodal_travel_tool_data
            WHERE tool_name = %s AND city = %s
            ORDER BY updated_at DESC
            """,
            (tool_name, city),
        )
        return [row[0] for row in cursor.fetchall()]


@mcp.tool(annotations=ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
))
def get_weather(city: str, target_date: date) -> dict:
    """도시와 날짜에 맞는 날씨 정보를 PostgreSQL에서 조회합니다."""
    items = load_items("get_weather", city)
    if not items:
        return {"success": False, "city": city, "error": "WEATHER_NOT_FOUND"}
    return {
        "success": True,
        "city": city,
        "date": target_date.isoformat(),
        **items[0],
        "source": "postgres",
    }


@mcp.tool(annotations=ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
))
def search_hotels(city: str, check_in: date, check_out: date, guests: int) -> dict:
    """도시, 숙박 기간과 인원에 맞는 숙소를 PostgreSQL에서 조회합니다."""
    if check_out <= check_in:
        raise ValueError("체크아웃은 체크인 이후여야 합니다.")
    if guests < 1 or guests > 10:
        raise ValueError("guests는 1 이상 10 이하여야 합니다.")
    items = [
        item
        for item in load_items("search_hotels", city)
        if item.get("capacity", 0) >= guests
    ]
    return {
        "success": True,
        "items": items,
        "query": {
            "city": city,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "guests": guests,
        },
        "source": "postgres",
    }


@mcp.tool(annotations=ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
))
def search_attractions(city: str, category: str = "all") -> dict:
    """도시와 분류에 맞는 관광지를 PostgreSQL에서 조회합니다."""
    if category not in {"nature", "culture", "food", "all"}:
        raise ValueError("category는 nature, culture, food, all 중 하나여야 합니다.")
    items = load_items("search_attractions", city)
    if category != "all":
        items = [item for item in items if item.get("category") == category]
    return {
        "success": True,
        "items": items,
        "category": category,
        "source": "postgres",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
