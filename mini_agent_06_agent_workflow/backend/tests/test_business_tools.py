"""MCP Tool의 입력 검증 계약을 확인하는 회귀 테스트입니다."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mcp_server.business_tools_server import (  # noqa: E402
    search_indoor_places,
    search_outdoor_places,
    search_product,
)


def test_blank_city_is_rejected() -> None:
    for search_places in (search_indoor_places, search_outdoor_places):
        result = search_places("   ")

        assert result["success"] is False
        assert result["error"] == "INVALID_CITY"


def test_blank_product_query_is_rejected() -> None:
    result = search_product("   ")

    assert result["success"] is False
    assert result["error"] == "INVALID_QUERY"
    assert result["items"] == []
