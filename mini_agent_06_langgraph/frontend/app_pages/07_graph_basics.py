import streamlit as st

from clients.learning_client import get_graph_components
from core.api_client import ApiClientError


st.title("6-2. State · Node · Edge")
st.caption("새로운 용어를 한 번에 하나씩 확인합니다.")

try:
    components = get_graph_components()
    st.code(components["flow"], language="text")
    for key in ("state", "node", "edge"):
        st.subheader(key)
        st.write(components[key])
except ApiClientError as error:
    st.error(str(error))

st.info("Node는 State 전체가 아니라 변경할 값만 반환합니다.")
