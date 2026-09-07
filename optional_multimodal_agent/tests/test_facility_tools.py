from datetime import date
import pytest
from mcp_server.tools import facility_tools as tools

def test_date_range_validation():
    with pytest.raises(ValueError):
        tools.get_program_sessions("PG-YOGA",date(2026,10,1),date(2026,9,1))
    with pytest.raises(ValueError):
        tools.get_program_sessions("PG-YOGA",date(2026,1,1),date(2026,9,1))

def test_cancelled_status_preserved(monkeypatch):
    monkeypatch.setattr(tools.db,"sessions",lambda *args:[{"status":"cancelled","remaining":8}])
    result = tools.get_program_sessions("PG-DRAW",date(2026,9,1),date(2026,9,30))
    assert result["items"][0]["status"]=="cancelled"
