from datetime import timedelta

import streamlit as st

from core.ui import backend_request, run_api, show_json
from core.state import selected_provider


st.title("🧰 Tool 선택과 실행")
provider_label, provider = selected_provider()
st.caption(f"Tool 선택 Provider: {provider_label}")
message = st.text_input("요청", "부산 호텔을 찾아줘")
if st.button("Tool 선택"):
    data = run_api(
        lambda: backend_request(
            "POST",
            "/api/tools/select",
            {"provider": provider, "message": message},
        )
    )
    if data:
        show_json(data)

st.divider()
st.subheader("Mock 숙소 검색 Tool")
city = st.text_input("도시", "부산")
col1, col2, col3 = st.columns(3)
check_in = col1.date_input("체크인")
check_out = col2.date_input("체크아웃", value=check_in + timedelta(days=2))
guests = col3.number_input("인원", 1, 10, 2)

if st.button("숙소 Tool 실행"):
    data = run_api(
        lambda: backend_request(
            "POST",
            "/api/tools/run",
            {
                "tool_name": "search_hotels",
                "arguments": {
                    "city": city,
                    "check_in": check_in.isoformat(),
                    "check_out": check_out.isoformat(),
                    "guests": guests,
                },
            },
        )
    )
    if data:
        st.dataframe(data["items"], use_container_width=True)
