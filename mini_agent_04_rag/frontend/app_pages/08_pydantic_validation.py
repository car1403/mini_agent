import json

import streamlit as st

from clients.agent_client import validate_travel_plan
from core.api_client import BackendAPIError


st.title("✅ Pydantic 검증")
sample = {"destination": "부산", "summary": "대중교통 여행", "recommended_days": 3, "activities": ["해운대"], "cautions": []}
raw = st.text_area("검증할 JSON", json.dumps(sample, ensure_ascii=False, indent=2), height=220)
if st.button("Schema 검증"):
    try:
        result = validate_travel_plan(json.loads(raw))
        if result["valid"]:
            st.success("검증 성공")
            st.json(result["data"])
        else:
            st.error("검증 실패")
            st.dataframe(result["errors"], use_container_width=True)
    except json.JSONDecodeError as error:
        st.error(f"JSON 문법 오류: {error}")
    except BackendAPIError as error:
        st.error(str(error))
