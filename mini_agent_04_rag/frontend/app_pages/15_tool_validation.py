import streamlit as st


st.title("3-3. Tool 입력 검증")
st.caption("Tool을 실행하기 전에 필수값과 허용 범위를 확인합니다.")

city = st.text_input("도시")
days = st.number_input("조회 일수", min_value=0, max_value=10, value=3)
if st.button("입력 검증", type="primary"):
    errors = []
    if not city.strip():
        errors.append("city는 필수입니다.")
    if not 1 <= days <= 7:
        errors.append("days는 1~7이어야 합니다.")
    if errors:
        st.error("\n".join(errors))
    else:
        st.success("검증을 통과했습니다. Tool을 실행할 수 있습니다.")
        st.json({"city": city, "days": days})
