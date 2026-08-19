import streamlit as st

from clients.agent_client import generate_response, preview_prompt
from core.api_client import BackendAPIError


st.title("🧩 Prompt 구성과 실험")
st.caption("Prompt를 조립한 뒤 같은 입력으로 개선 전후의 실제 응답을 비교합니다.")
examples = {
    "여행 요청 분석": (
        "당신은 초보자를 돕는 여행 요청 분석가입니다.",
        "사용자의 여행 요청에서 필요한 정보를 추출하세요.",
        "사용자는 국내 여행을 계획하고 있습니다.",
        "추측하지 말고 모르는 값은 누락 정보로 표시하세요.",
        "추출한 정보와 누락 정보 목록",
    ),
    "고객 문의 분류": (
        "당신은 온라인 쇼핑몰 고객 지원 분류 담당자입니다.",
        "문의를 유형과 긴급도로 분류하고 핵심 내용을 요약하세요.",
        "분류 결과는 담당 팀을 자동 배정하는 데 사용됩니다.",
        "긴급도 판단 근거를 한 문장으로 작성하세요.",
        "유형, 긴급도, 한 문장 요약",
    ),
    "회의 내용 요약": (
        "당신은 프로젝트 회의 기록 정리자입니다.",
        "결정 사항과 담당자별 할 일을 구분해 정리하세요.",
        "개발자, 디자이너, 운영 담당자가 참여한 회의입니다.",
        "확정되지 않은 내용은 결정 사항에 포함하지 마세요.",
        "결정 사항과 담당자별 할 일 목록",
    ),
}

builder_tab, experiment_tab = st.tabs(["Prompt 조립", "Before / After 실험"])

with builder_tab:
    selected = st.selectbox("Prompt 예제", list(examples))
    defaults = examples[selected]
    role = st.text_input("Role", defaults[0], key=f"role-{selected}")
    instruction = st.text_area("Instruction", defaults[1], key=f"instruction-{selected}")
    context = st.text_area("Context", defaults[2], key=f"context-{selected}")
    constraint = st.text_area("Constraint", defaults[3], key=f"constraint-{selected}")
    output_format = st.text_area("Output Format", defaults[4], key=f"format-{selected}")

    if st.button("Prompt 조립"):
        try:
            result = preview_prompt(
                role, instruction, context, constraint, output_format
            )
            st.code(result["prompt"], language="text")
        except BackendAPIError as error:
            st.error(str(error))

with experiment_tab:
    scenarios = {
        "회의 요약 Before / After": {
            "message": "민수는 금요일까지 API를 완성한다. 배포일은 다음 회의에서 정한다.",
            "before": "회의 내용을 정리해 주세요.",
            "after": """[Role] 프로젝트 회의 기록 담당자
[Instruction] 결정 사항과 담당자별 할 일을 분리하세요.
[Context] 배포 준비 회의입니다.
[Constraint] 확정되지 않은 내용은 결정 사항에서 제외하세요.
[Output Format] 결정 사항과 할 일을 Markdown 목록으로 작성하세요.""",
        },
        "고객 문의 Zero-shot / Few-shot": {
            "message": "배송 조회 화면에서 오류가 발생해 주문 상태를 볼 수 없습니다.",
            "before": "문의를 billing, technical, account, other 중 하나로 분류하세요.",
            "after": """문의를 billing, technical, account, other 중 하나로 분류하세요.
예시: 결제 중복 → billing, 비밀번호 분실 → account, 서버 오류 → technical
분류값과 한 문장 근거만 답하세요.""",
        },
    }
    scenario_name = st.selectbox("비교 실험", list(scenarios))
    scenario = scenarios[scenario_name]
    provider = st.selectbox("Provider", ["mock", "gemini", "openai", "ollama"])
    st.text_area("동일하게 사용할 입력", scenario["message"], disabled=True)
    before_prompt = st.text_area("Before Prompt", scenario["before"])
    after_prompt = st.text_area("After Prompt", scenario["after"])
    if provider == "mock":
        st.info("Mock은 호출 흐름만 확인합니다. Prompt 품질 차이는 실제 Provider로 비교하세요.")
    else:
        st.warning("버튼을 누르면 선택한 Provider를 두 번 호출합니다.")

    if st.button("두 Prompt 비교"):
        try:
            before = generate_response(provider, before_prompt, scenario["message"])
            after = generate_response(provider, after_prompt, scenario["message"])
            before_column, after_column = st.columns(2)
            with before_column:
                st.subheader("Before")
                st.write(before["content"])
                st.caption(f"{before['model']} · {before['latency_ms']} ms")
            with after_column:
                st.subheader("After")
                st.write(after["content"])
                st.caption(f"{after['model']} · {after['latency_ms']} ms")
        except BackendAPIError as error:
            st.error(str(error))
