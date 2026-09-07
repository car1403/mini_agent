"""실행: python -m streamlit run frontend/app.py"""
import sys
from pathlib import Path
import streamlit as st

# Streamlit이 페이지 파일을 실행해도 프로젝트 공통 모듈을 찾도록 합니다.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

st.set_page_config(page_title="멀티모달 Agent 실습",page_icon="📷",layout="wide")
st.sidebar.title("멀티모달 Agent")
st.sidebar.caption("촬영 → MCP Tool → RAG·DB → 음성 답변")
st.sidebar.info("모든 제품·시설·재고는 가상 실습 데이터입니다.")
pages = [st.Page("app_pages/01_product_agent.py",title="제품 촬영 안내",icon="📷"),
         st.Page("app_pages/02_facility_agent.py",title="안내문 촬영 안내",icon="📄")]
st.navigation(pages).run()
