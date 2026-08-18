import streamlit as st


st.set_page_config(page_title="Mini Agent 04", page_icon="📚", layout="wide")

home = st.Page("app_pages/01_home.py", title="HOME", default=True)
environment = st.Page("app_pages/02_environment.py", title="환경 상태")
concept = st.Page("app_pages/03_concept_compare.py", title="LLM·Workflow·Agent")
travel = st.Page("app_pages/04_travel_classifier.py", title="여행 요청 분류")
llm = st.Page("app_pages/05_llm.py", title="LLM 호출")
providers = st.Page("app_pages/06_provider_compare.py", title="Provider 비교")
prompt = st.Page("app_pages/07_prompt_builder.py", title="Prompt 구성")
validation = st.Page("app_pages/08_pydantic_validation.py", title="Pydantic 검증")
structured = st.Page("app_pages/09_structured_output.py", title="Structured Output")
image_analysis = st.Page("app_pages/10_image_analysis.py", title="이미지 분석")
tts = st.Page("app_pages/10_tts.py", title="음성 생성")
tool_select = st.Page("app_pages/11_tool_select.py", title="Tool 선택")
tool_run = st.Page("app_pages/12_tool_run.py", title="Tool 실행")
tool_loop = st.Page("app_pages/13_tool_loop.py", title="Agent Loop")
rag_concept = st.Page("app_pages/14_rag_concept.py", title="RAG 흐름")
rag_chunks = st.Page("app_pages/15_rag_chunks.py", title="문서와 Chunk")
rag_search = st.Page("app_pages/16_rag_search.py", title="문서 검색")
rag_answer = st.Page("app_pages/17_rag_answer.py", title="근거 기반 답변")
rag_pgvector = st.Page("app_pages/18_rag_pgvector.py", title="pgvector 실습")
tool_schema = st.Page("app_pages/14_tool_schema.py", title="Tool Schema")
tool_validation = st.Page("app_pages/15_tool_validation.py", title="Tool 입력 검증")
tool_errors = st.Page("app_pages/16_tool_errors.py", title="Tool 오류 처리")
rag_limit = st.Page("app_pages/19_rag_limit.py", title="검색 결과 제한")

pages = [
    home, concept, travel, environment, llm, providers, prompt, validation,
    structured, image_analysis, tts, tool_schema, tool_select, tool_validation,
    tool_run, tool_errors, tool_loop, rag_concept, rag_chunks, rag_search,
    rag_limit, rag_answer, rag_pgvector,
]
navigation = st.navigation(pages, position="hidden")

with st.sidebar:
    st.title("📚 Mini Agent 04")
    st.caption("05 과정 · 04_rag")
    st.page_link(home, label="🏠 HOME")

    st.divider()
    with st.expander("01. LLM에서 Agent로", expanded=False):
        st.page_link(concept, label="1-1. LLM·Workflow·Agent")
        st.page_link(travel, label="1-2. 여행 요청 분류")
        st.page_link(llm, label="1-3. LLM 호출")
        st.page_link(providers, label="1-4. Provider 비교")
        st.page_link(image_analysis, label="1-5. 이미지 분석")
        st.page_link(tts, label="1-6. 음성 생성")

    st.divider()
    with st.expander("02. Prompt와 구조화 출력", expanded=False):
        st.page_link(prompt, label="2-1. Prompt 구성")
        st.page_link(validation, label="2-2. Pydantic 검증")
        st.page_link(structured, label="2-3. Structured Output")

    st.divider()
    with st.expander("03. Tool Use", expanded=False):
        st.page_link(tool_schema, label="3-1. Tool Schema")
        st.page_link(tool_select, label="3-2. Tool 선택")
        st.page_link(tool_validation, label="3-3. Tool 입력 검증")
        st.page_link(tool_run, label="3-4. Tool 안전 실행")
        st.page_link(tool_errors, label="3-5. Tool 오류 처리")
        st.page_link(tool_loop, label="3-6. Agent Loop")

    st.divider()
    with st.expander("04. RAG", expanded=True):
        st.page_link(rag_concept, label="4-1. RAG 흐름")
        st.page_link(rag_chunks, label="4-2. 문서와 Chunk")
        st.page_link(rag_search, label="4-3. 문서 검색")
        st.page_link(rag_limit, label="4-4. 검색 결과 제한")
        st.page_link(rag_answer, label="4-5. 근거 기반 답변")
        st.page_link(rag_pgvector, label="4-6. pgvector 실습")

    st.divider()
    st.caption("실행 환경")
    st.page_link(environment, label="🩺 환경 상태")

navigation.run()
