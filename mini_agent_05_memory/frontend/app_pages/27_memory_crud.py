import streamlit as st

from clients.agent_client import delete_memory, list_memories, save_memory
from core.api_client import BackendAPIError


st.title("5-4. 사용자 Memory CRUD")
st.caption("모든 요청에 user_id를 넣어 사용자별 Memory를 격리합니다.")
st.warning("이 화면의 user_id 선택은 수업용입니다. 실제 서비스는 인증 토큰에서 사용자 ID를 확인해야 합니다.")

storage = "postgres"
st.caption("장기 Memory 저장소: PostgreSQL")
user_id = st.selectbox("사용자", ["student-01", "student-02"])
key = st.selectbox("Memory key", ["transportation", "food_restriction", "hotel_preference", "password"])
value = st.text_input("값", "대중교통")

st.warning("PostgreSQL과 Memory 스키마가 준비되어야 합니다.")

if st.button("저장 또는 수정", type="primary"):
    try:
        st.success("저장했습니다.")
        st.json(save_memory(user_id, key, value, storage))
    except BackendAPIError as error:
        st.error(str(error))

st.divider()
memory_state_key = f"memory_items-{storage}-{user_id}"
if st.button("내 Memory 조회"):
    try:
        st.session_state[memory_state_key] = list_memories(user_id, storage)["items"]
    except BackendAPIError as error:
        st.error(str(error))

for item in st.session_state.get(memory_state_key, []):
    left, right = st.columns([4, 1])
    with left:
        st.write(f"**{item['key']}** = {item['value']}")
        st.caption(item["id"])
    with right:
        if st.button("삭제", key=f"delete-{storage}-{user_id}-{item['id']}"):
            try:
                result = delete_memory(user_id, item["id"], storage)
                st.write("삭제됨" if result["deleted"] else "삭제 권한 없음 또는 이미 삭제됨")
            except BackendAPIError as error:
                st.error(str(error))
