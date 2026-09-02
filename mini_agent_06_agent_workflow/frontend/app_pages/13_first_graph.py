import streamlit as st

from clients.learning_client import get_graph_components
from core.api_client import ApiClientError


st.title("6-4. 첫 번째 Graph")
st.caption("Node와 Edge로 만든 Graph 구조를 Mermaid 텍스트로 확인합니다.")

try:
    components = get_graph_components()
    st.code(components["flow"], language="text")
    st.code(components["mermaid"], language="text")
except ApiClientError as error:
    st.error(str(error))

st.info("코드의 add_node, add_edge, add_conditional_edges가 어떤 선을 만드는지 찾아보세요.")
