import json

import streamlit as st

from clients.agent_client import validate_travel_plan
from core.api_client import BackendAPIError


st.title("✅ Pydantic 검증")
st.caption("JSON 파싱 성공과 Schema 검증 성공은 다릅니다.")
samples = {
    "정상": {"destination": "부산", "summary": "대중교통 중심 여행", "recommended_days": 3, "activities": ["해운대", "시장 방문"], "cautions": ["운영 시간 확인"]},
    "잘못된 범위": {"destination": "부산", "summary": "여행", "recommended_days": 0, "activities": [], "cautions": []},
    "추가 필드": {"destination": "부산", "summary": "여행", "recommended_days": 2, "activities": ["산책"], "cautions": [], "password": "보내면 안 되는 값"},
}
selected = st.selectbox("예제", list(samples))
raw = st.text_area("검증할 JSON", json.dumps(samples[selected], ensure_ascii=False, indent=2), height=240)

if st.button("Schema 검증"):
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        st.error(f"JSON 문법 오류: {error}")
    else:
        try:
            result = validate_travel_plan(payload)
            if result["valid"]:
                st.success("TravelPlan 검증 성공")
                st.json(result["data"])
            else:
                st.error("TravelPlan 검증 실패")
                st.dataframe(result["errors"], use_container_width=True)
        except BackendAPIError as error:
            st.error(str(error))
