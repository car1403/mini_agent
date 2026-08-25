import json

import streamlit as st

from clients.agent_client import search_rag
from core.api_client import BackendAPIError


st.title("8️⃣ Metadata·Hybrid 검색")
st.caption("키워드와 의미 검색을 RRF로 결합하고 Metadata와 유사도 임계값으로 범위를 제한합니다.")

query = st.text_input("질문", "A-1703에 강아지와 묵으면 비용이 더 드나요?")
mode = st.radio("검색 방식", ["keyword", "pgvector", "hybrid"], index=2, horizontal=True)
top_k = st.slider("top_k", 1, 10, 3)
use_threshold = st.checkbox("유사도 임계값 사용")
threshold = st.slider("score_threshold", -1.0, 1.0, 0.35, 0.05, disabled=not use_threshold)
raw_filter = st.text_area("Metadata Filter(JSON)", '{"status": "active"}')

if st.button("고급 검색", type="primary"):
    try:
        metadata_filter = json.loads(raw_filter) if raw_filter.strip() else {}
        result = search_rag(query, mode, top_k, threshold if use_threshold else None, metadata_filter)
        if not result["results"]:
            st.warning("조건을 만족하는 결과가 없습니다.")
        for index, item in enumerate(result["results"], start=1):
            st.subheader(f"{index}위 · score {item['score']:.4f}")
            st.write(item["content"])
            st.caption(f"출처: {item['source']} · metadata: {item['metadata']}")
            if item.get("matched_by"):
                st.caption(f"결합: {item['matched_by']} · keyword {item.get('keyword_rank')} · vector {item.get('vector_rank')}")
    except json.JSONDecodeError:
        st.error("Metadata Filter는 올바른 JSON 객체여야 합니다.")
    except BackendAPIError as error:
        st.error(str(error))
