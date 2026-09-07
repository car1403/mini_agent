from mcp_server.tools import product_tools as tools
import pytest

def test_inventory_zero_preserved(monkeypatch):
    monkeypatch.setattr(tools.db,"availability",lambda product_id:[{"product_id":product_id,"quantity":0}])
    result = tools.get_product_availability("AC-A30")
    assert result["items"][0]["quantity"]==0
    assert result["queried_at"]

def test_blank_search_rejected():
    with pytest.raises(ValueError):
        tools.find_products(" ")
