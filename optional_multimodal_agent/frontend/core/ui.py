import time
import streamlit as st
from frontend.core import api_client as api
from frontend.core.sse_client import listen
from frontend.core.state import current, select_run

def media_inputs(key):
    mode = st.radio("사진 입력 방법",["파일 업로드","카메라 촬영"],horizontal=True,key=f"mode_{key}")
    if mode == "카메라 촬영":
        image = st.camera_input("대상이나 코드를 촬영하세요",key=f"camera_{key}")
    else:
        image = st.file_uploader("사진 선택",type=["jpg","jpeg","png","webp"],key=f"image_{key}")
    if image:
        st.image(image,width=360)
    question = st.text_area("질문",key=f"question_{key}",max_chars=2000)
    audio = st.audio_input("질문을 음성으로 녹음해도 됩니다 (최대 120초)",key=f"audio_{key}")
    speak = st.checkbox("답변을 음성으로도 받기",value=True,key=f"speak_{key}")
    return image, question, audio, speak

def start_run(agent, image, question, audio, speak):
    if image is None:
        st.warning("먼저 사진을 촬영하거나 업로드하세요.")
        return
    with st.spinner("사진과 질문을 전송합니다."):
        image_id = api.upload(image,"image")
        audio_id = api.upload(audio,"audio") if audio else None
        run = api.request("POST","/api/runs",json={"agent":agent,"image_id":image_id,
                          "question":question,"audio_id":audio_id,"speak":speak})
        select_run(agent,run["run_id"])

def show_progress(state):
    placeholder = st.empty()
    started = time.monotonic()
    last_status = "queued"
    # 실행이 끝날 때까지 이벤트를 받아 같은 표시 영역을 갱신합니다.
    # 사용자 rerun으로 수신이 끊겨도 서버 Worker는 계속 실행합니다.
    for attempt in range(3):
        try:
            for event in listen(state["run_id"],state["last_id"]):
                elapsed = int(time.monotonic()-started)
                if event.get("event")=="heartbeat":
                    placeholder.info(f"{last_status} · 연결 대기 {elapsed}초")
                    if elapsed>60 and last_status=="queued":
                        st.warning("작업이 대기 중입니다. Agent Worker가 실행 중인지 확인하세요.")
                        return
                    if elapsed>720:
                        st.warning("연결 대기가 길어졌습니다. 서비스 상태를 확인하고 다시 연결하세요.")
                        return
                    continue
                if event.get("event")=="end":
                    return
                last_status = event["data"].get("status",last_status)
                event_id = event.get("id")
                if event_id and event_id != state["last_id"]:
                    state["last_id"] = event_id
                    state["events"].append(event["data"])
                placeholder.info(event["data"].get("message","진행 중"))
                if event["data"].get("status") in {"completed","needs_input","failed"}:
                    return
            return
        except Exception:
            if attempt==2:
                st.warning("진행 연결이 끊겼습니다. 아래 버튼으로 다시 연결할 수 있습니다.")
                return
            time.sleep(1)

def show_run(agent):
    state = current(agent)
    saved_id = st.query_params.get(agent)
    if not state["run_id"] and saved_id:
        state = select_run(agent,saved_id)
    if not state["run_id"]:
        return
    run_id = state["run_id"]
    run = api.request("GET",f"/api/runs/{run_id}")
    if run["request"]["agent"] != agent:
        st.error("다른 Agent의 실행 ID입니다.")
        return
    st.subheader("진행 상황")
    st.caption(f"실행 ID: {run_id}")
    if run["status"] in {"queued","running"} or not state["events"]:
        show_progress(state)
        run = api.request("GET",f"/api/runs/{run_id}")
    st.write("현재 상태:",run["status"])
    if state["events"]:
        st.dataframe(state["events"],hide_index=True,use_container_width=True)
    if run["status"] in {"queued","running"}:
        st.button("진행 상황 이어 보기",key=f"reconnect_{agent}")
        st.caption("화면을 새로고침해도 서버 작업은 계속됩니다.")
    if run.get("error"):
        st.error(run["error"])
    result = run.get("result") or {}
    if result:
        st.subheader("Agent 답변")
        st.write(result.get("answer",""))
        with st.expander("이미지 분석·RAG 출처·DB 조회 결과"):
            st.json(result.get("analysis",{}))
            for item in result.get("evidence",[]):
                st.write(item["tool"])
                st.json(item["result"])
        if result.get("audio_id"):
            content = api.get_audio(result["audio_id"])
            st.caption("AI가 생성한 합성 음성입니다.")
            st.audio(content,format="audio/mpeg")
            st.download_button("음성 다운로드",content,file_name="answer.mp3",mime="audio/mpeg",key=f"download_{agent}")
        if result.get("audio_error"):
            st.warning(result["audio_error"])
            if st.button("음성만 다시 생성",key=f"tts_{agent}"):
                api.request("POST",f"/api/runs/{run_id}/speech")
                st.rerun()
    if run["status"] in {"completed","needs_input","failed"}:
        with st.expander("추가 질문·재촬영·다시 실행",expanded=run["status"]=="needs_input"):
            question = st.text_input("추가 설명 또는 다시 실행할 질문",key=f"follow_{agent}")
            source = st.radio("새 사진 입력",["기존 사진 사용","파일 업로드","카메라 촬영"],key=f"follow_mode_{agent}")
            image = None
            if source=="파일 업로드":
                image = st.file_uploader("새 사진",type=["jpg","jpeg","png","webp"],key=f"follow_image_{agent}")
            elif source=="카메라 촬영":
                image = st.camera_input("다시 촬영",key=f"follow_camera_{agent}")
            if st.button("추가 입력 전송",key=f"follow_button_{agent}"):
                if question.strip() and (source=="기존 사진 사용" or image):
                    image_id = api.upload(image,"image") if image else None
                    new = api.request("POST",f"/api/runs/{run_id}/input",json={"question":question,"image_id":image_id})
                    select_run(agent,new["run_id"])
                    st.rerun()
                else:
                    st.warning("질문과 선택한 새 사진을 입력하세요.")
