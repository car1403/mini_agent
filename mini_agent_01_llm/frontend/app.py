import streamlit as st


st.set_page_config(page_title="Mini Agent 01", page_icon="🤖", layout="wide")

home_page = st.Page("app_pages/01_home.py", title="HOME", default=True)
environment_page = st.Page("app_pages/02_environment.py", title="환경 상태")
concept_page = st.Page("app_pages/03_concept_compare.py", title="LLM·Workflow·Agent")
travel_page = st.Page("app_pages/04_travel_classifier.py", title="여행 요청 분류")
llm_page = st.Page("app_pages/05_llm.py", title="LLM 호출")
compare_page = st.Page("app_pages/06_provider_compare.py", title="Provider 비교")
image_page = st.Page("app_pages/07_image_analysis.py", title="이미지 분석")
tts_page = st.Page("app_pages/08_tts.py", title="음성 생성")

navigation = st.navigation(
    [home_page, concept_page, travel_page, environment_page, llm_page, compare_page, image_page, tts_page],
    position="hidden",
)

with st.sidebar:
    st.title("🤖 Mini Agent 01")
    st.caption("05 과정 · 01_llm-to-agent")
    st.page_link(home_page, label="🏠 HOME")

    st.divider()
    with st.expander("01. LLM에서 Agent로", expanded=True):
        st.page_link(concept_page, label="1-1. LLM·Workflow·Agent")
        st.page_link(travel_page, label="1-2. 여행 요청 분류")
        st.page_link(llm_page, label="1-3. LLM 호출")
        st.page_link(compare_page, label="1-4. Provider 비교")
        st.page_link(image_page, label="1-5. 이미지 분석")
        st.page_link(tts_page, label="1-6. 음성 생성")

    st.divider()
    st.caption("실행 환경")
    st.page_link(environment_page, label="🩺 환경 상태")

navigation.run()
