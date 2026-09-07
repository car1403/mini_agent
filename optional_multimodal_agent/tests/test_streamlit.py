from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_both_pages_render():
    app = AppTest.from_file(str(Path("frontend/app.py").resolve()),default_timeout=10).run()
    assert not app.exception
    assert app.title[0].value=="제품 촬영 안내 Agent"
    app.switch_page("app_pages/02_facility_agent.py").run()
    assert not app.exception
    assert app.title[0].value=="안내문 촬영 시설 도우미 Agent"
