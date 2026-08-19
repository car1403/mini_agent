import json

import streamlit as st

from clients.agent_client import validate_structured_output
from core.api_client import BackendAPIError


st.title("✅ Pydantic 검증")
st.caption("JSON 파싱 성공과 Schema 검증 성공은 다릅니다.")
schema_labels = {"여행 계획": "travel_plan", "고객 문의": "support_ticket"}
selected_schema_label = st.selectbox("Schema", list(schema_labels))
schema_type = schema_labels[selected_schema_label]
samples = {
    "travel_plan": {
        "정상": {"destination": "부산", "summary": "대중교통 중심 여행", "recommended_days": 3, "activities": ["해운대", "시장 방문"], "cautions": ["운영 시간 확인"]},
        "잘못된 범위": {"destination": "부산", "summary": "여행", "recommended_days": 0, "activities": [], "cautions": []},
        "추가 필드": {"destination": "부산", "summary": "여행", "recommended_days": 2, "activities": ["산책"], "cautions": [], "password": "보내면 안 되는 값"},
    },
    "support_ticket": {
        "정상": {"category": "billing", "priority": "medium", "summary": "중복 결제 확인 요청", "requires_human": True, "missing_information": ["주문 번호"]},
        "잘못된 허용값": {"category": "refund", "priority": "urgent", "summary": "환불 요청", "requires_human": True, "missing_information": []},
        "잘못된 Boolean": {"category": "technical", "priority": "medium", "summary": "오류 문의", "requires_human": "yes", "missing_information": []},
        "추가 필드": {"category": "account", "priority": "low", "summary": "계정 문의", "requires_human": False, "missing_information": [], "password": "보내면 안 되는 값"},
    },
}
selected = st.selectbox("예제", list(samples[schema_type]))
raw = st.text_area("검증할 JSON", json.dumps(samples[schema_type][selected], ensure_ascii=False, indent=2), height=240, key=f"payload-{schema_type}-{selected}")

if st.button("Schema 검증"):
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        st.error(f"JSON 문법 오류: {error}")
    else:
        try:
            result = validate_structured_output(schema_type, payload)
            if result["valid"]:
                st.success(f"{selected_schema_label} Schema 검증 성공")
                st.json(result["data"])
            else:
                st.error(f"{selected_schema_label} Schema 검증 실패")
                st.dataframe(result["errors"], use_container_width=True)
        except BackendAPIError as error:
            st.error(str(error))
