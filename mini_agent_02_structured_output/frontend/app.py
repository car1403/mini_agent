import streamlit as st


st.set_page_config(page_title="Mini Agent 02", page_icon="🧱", layout="wide")

home_page = st.Page("app_pages/01_home.py", title="HOME", default=True)
environment_page = st.Page("app_pages/02_environment.py", title="환경 상태")
concept_page = st.Page("app_pages/03_concept_compare.py", title="LLM·Workflow·Agent")
travel_page = st.Page("app_pages/04_travel_classifier.py", title="여행 요청 분류")
llm_page = st.Page("app_pages/05_llm.py", title="LLM 호출")
provider_page = st.Page("app_pages/06_provider_compare.py", title="Provider 비교")
prompt_page = st.Page("app_pages/07_prompt_builder.py", title="Prompt 구성")
validation_page = st.Page("app_pages/08_pydantic_validation.py", title="Pydantic 검증")
structured_page = st.Page("app_pages/09_structured_output.py", title="Structured Output")
image_page = st.Page("app_pages/10_image_analysis.py", title="이미지 분석")
tts_page = st.Page("app_pages/11_tts.py", title="음성 생성")

navigation = st.navigation(
    [home_page, concept_page, travel_page, environment_page, llm_page, provider_page,
     prompt_page, validation_page, structured_page, image_page, tts_page],
    position="hidden",
)

with st.sidebar:
    st.title("🧱 Mini Agent 02")
    st.caption("05 과정 · 02_prompt-and-structured-output")
    st.page_link(home_page, label="🏠 HOME")

    st.divider()
    with st.expander("01. LLM에서 Agent로", expanded=False):
        st.page_link(concept_page, label="1-1. LLM·Workflow·Agent")
        st.page_link(travel_page, label="1-2. 여행 요청 분류")
        st.page_link(llm_page, label="1-3. LLM 호출")
        st.page_link(provider_page, label="1-4. Provider 비교")
        st.page_link(image_page, label="1-5. 이미지 분석")
        st.page_link(tts_page, label="1-6. 음성 생성")

    st.divider()
    with st.expander("02. Prompt와 구조화 출력", expanded=True):
        st.page_link(prompt_page, label="2-1. Prompt 구성")
        st.page_link(validation_page, label="2-2. Pydantic 검증")
        st.page_link(structured_page, label="2-3. Structured Output")

    st.divider()
    st.caption("실행 환경")
    st.page_link(environment_page, label="🩺 환경 상태")

navigation.run()
