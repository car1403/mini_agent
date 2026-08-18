import streamlit as st

from core.api_client import request_audio, upload_multimodal_agent_run
from core.state import (
    current_agent_run,
    save_agent_run,
    selected_backend,
    selected_provider,
)
from core.ui import backend_request, run_api


backend_name, api_url = selected_backend()
provider_label, provider = selected_provider()

st.title("Multimodal Agent")
st.caption(f"현재 선택: {backend_name} · {provider_label}")
st.info(
    "이미지는 GPT가 분석하고, 구조화된 분석 결과만 선택한 Python/LangGraph "
    "Agent에 전달합니다. 이미지 원본은 Agent State에 저장하지 않습니다."
)

user_id = st.text_input("사용자 ID", "demo-user")
message = st.text_area(
    "여행 요청",
    "8월 부산 2박 여행을 성인 2명이 가고 싶어요. 예산은 50만 원입니다.",
)
uploaded = st.file_uploader(
    "여행지, 교통표, 음식 또는 숙소 이미지",
    type=["jpg", "jpeg", "png", "webp", "gif"],
)

if uploaded:
    st.image(uploaded, caption=uploaded.name)
    st.caption("여권, 카드, 예약번호 등 민감한 이미지는 업로드하지 마세요.")
    if st.button("이미지로 Agent 실행", type="primary"):
        save_agent_run(
            run_api(
                lambda: upload_multimodal_agent_run(
                    uploaded.name,
                    uploaded.getvalue(),
                    uploaded.type,
                    user_id,
                    message,
                    provider,
                    api_url,
                )
            )
        )

run = current_agent_run()
if run:
    st.subheader("Agent 실행 결과")
    st.info(
        f"상태: {run['status']} · 현재 단계: {run['current_node']}"
    )
    analysis = run.get("image_analysis") or (run.get("result") or {}).get(
        "image_analysis"
    )
    if analysis:
        st.write("이미지 분석", analysis["summary"])
        with st.expander("TravelImageAnalysis"):
            st.json(analysis)
    if run.get("result"):
        st.write("여행 계획")
        st.json(run["result"])
    if run.get("trace"):
        st.write("실행 Trace")
        st.dataframe(run["trace"], use_container_width=True)

    if run.get("requires_approval"):
        st.warning("교육용 Mock 예약 요청이며 실제 예약은 발생하지 않습니다.")
        approve, reject = st.columns(2)
        if approve.button("승인"):
            save_agent_run(
                run_api(
                    lambda: backend_request(
                        "POST",
                        f"/api/agent/runs/{run['run_id']}/approve",
                        {"actor": user_id, "note": "Multimodal Agent 승인"},
                    )
                )
            )
            st.rerun()
        if reject.button("거절"):
            save_agent_run(
                run_api(
                    lambda: backend_request(
                        "POST",
                        f"/api/agent/runs/{run['run_id']}/reject",
                        {"actor": user_id, "note": "Multimodal Agent 거절"},
                    )
                )
            )
            st.rerun()

    st.divider()
    tts_text = st.text_area(
        "음성으로 들을 최종 안내",
        run.get("message") or "여행 계획이 준비되었습니다.",
        max_chars=2000,
    )
    voice = st.selectbox("음성", ["coral", "marin", "cedar", "alloy", "nova"])
    if st.button("최종 안내 TTS"):
        audio = run_api(
            lambda: request_audio(
                "/api/media/tts",
                {
                    "text": tts_text,
                    "voice": voice,
                    "instructions": "한국어로 친절하고 또렷하게 말하세요.",
                },
                api_url,
            )
        )
        if audio:
            st.warning("아래 음성은 AI가 생성한 합성 음성입니다.")
            st.audio(audio, format="audio/mpeg")
