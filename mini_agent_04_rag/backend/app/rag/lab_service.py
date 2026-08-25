"""실제 pgvector·Redis를 사용하는 RAG Lab 03~07 업무 Service입니다."""

from typing import Any

from app.rag import redis_cache
from app.rag.service import index_chunks, search
from app.services.generation_service import generate
from app.schemas import (
    AclSearchRequest, AclSearchResult, ProductSearchRequest,
    ProductSearchResult, RagChunk, RagIndexResult, RagSearchItem,
    RetrievalEvaluationCase, RetrievalEvaluationReport,
    RetrievalEvaluationRequest, RetrievalEvaluationResult,
    MultiToolRagRequest, MultiToolRagResult,
)
from app.tools.executor import execute_tool_safely


PRODUCT_SOURCE = "lab-product-catalog.json"
POLICY_SOURCE = "lab-internal-policy.md"
EVALUATION_SOURCE = "lab-retrieval-evaluation.md"
MULTI_TOOL_SOURCE = "lab-multi-tool-knowledge.md"
MAX_MULTI_TOOL_STEPS = 4


def seed_products() -> RagIndexResult:
    products = [
        ("RUN-100", "초경량 러닝화로 장거리 달리기에 적합합니다.", "shoes", 89000),
        ("TRAIL-20", "접지력이 높은 방수 트레일 러닝화입니다.", "shoes", 129000),
        ("WALK-7", "쿠션이 부드러운 일상용 워킹화입니다.", "shoes", 69000),
        ("BAG-15", "15리터 러닝 백팩으로 물통 수납이 가능합니다.", "bag", 59000),
    ]
    chunks = [
        RagChunk(
            chunk_id=f"{PRODUCT_SOURCE}:{index}",
            text=f"상품 코드 {sku}. {description} 가격 {price:,}원.",
            source=PRODUCT_SOURCE,
            title=sku,
            chunk_index=index,
            metadata={
                "dataset": "product", "sku": sku, "category": category,
                "price": price, "status": "active",
            },
        )
        for index, (sku, description, category, price) in enumerate(products)
    ]
    return index_chunks(chunks, source=PRODUCT_SOURCE, replace_source=True)


def search_products(payload: ProductSearchRequest) -> ProductSearchResult:
    metadata_filter = {"dataset": "product", "status": "active"}
    if payload.category:
        metadata_filter["category"] = payload.category
    candidates = search(payload.query, "hybrid", 30, None, metadata_filter)
    filtered = [
        item for item in candidates
        if payload.max_price is None or item.metadata.get("price", 0) <= payload.max_price
    ]
    return ProductSearchResult(
        query=payload.query,
        category=payload.category,
        max_price=payload.max_price,
        results=filtered[:payload.top_k],
        candidate_count=len(candidates),
    )


def seed_internal_policies() -> RagIndexResult:
    policies = [
        ("휴가 규정", "연차 휴가는 사내 시스템에서 신청합니다.", ["employee", "manager", "hr"]),
        ("관리자 평가", "관리자는 분기마다 팀원 성과 면담을 진행합니다.", ["manager", "hr"]),
        ("급여 운영", "급여 정정 요청은 HR 담당자가 승인합니다.", ["hr"]),
    ]
    chunks = [
        RagChunk(
            chunk_id=f"{POLICY_SOURCE}:{index}",
            text=content,
            source=POLICY_SOURCE,
            title=title,
            chunk_index=index,
            metadata={
                "dataset": "internal_policy", "allowed_roles": roles,
                "status": "active",
            },
        )
        for index, (title, content, roles) in enumerate(policies)
    ]
    return index_chunks(chunks, source=POLICY_SOURCE, replace_source=True)


def search_internal_policies(
    payload: AclSearchRequest,
    *,
    authenticated_role: str,
) -> AclSearchResult:
    if authenticated_role not in {"employee", "manager", "hr"}:
        raise ValueError(f"허용되지 않은 사용자 역할입니다: {authenticated_role}")
    results = search(
        payload.query,
        "hybrid",
        payload.top_k,
        None,
        {
            "dataset": "internal_policy", "status": "active",
            "allowed_roles": [authenticated_role],
        },
    )
    return AclSearchResult(
        role=authenticated_role,
        results=results,
        termination_reason="authorized_evidence" if results else "no_authorized_evidence",
    )


EVALUATION_SET = [
    ("숙소를 예약 당일 취소하면 돈을 돌려받나요?", "refund"),
    ("비행기에 맡길 수 있는 가방 무게는?", "baggage"),
    ("바다 박물관이 쉬는 요일은?", "museum"),
    ("강아지와 숙박할 때 추가 비용이 있나요?", "pet"),
]


def seed_evaluation_documents() -> RagIndexResult:
    documents = [
        ("refund", "체크인 당일 취소에는 숙박 요금 전액이 부과됩니다."),
        ("baggage", "교육용 국내선의 위탁 수하물은 15kg까지 허용합니다."),
        ("museum", "바다 박물관은 매주 화요일에 휴관합니다."),
        ("pet", "반려동물 동반 객실은 1박당 3만 원이 추가됩니다."),
    ]
    chunks = [
        RagChunk(
            chunk_id=f"{EVALUATION_SOURCE}:{index}", text=content,
            source=EVALUATION_SOURCE, title=document_id, chunk_index=index,
            metadata={"dataset": "retrieval_evaluation", "evaluation_id": document_id},
        )
        for index, (document_id, content) in enumerate(documents)
    ]
    return index_chunks(chunks, source=EVALUATION_SOURCE, replace_source=True)


def evaluate_retrieval(payload: RetrievalEvaluationRequest) -> RetrievalEvaluationResult:
    reports = []
    metadata_filter = {"dataset": "retrieval_evaluation"}
    for mode in ("keyword", "pgvector", "hybrid"):
        cases = []
        reciprocal_ranks = []
        hits = 0
        for question, expected_id in EVALUATION_SET:
            results = search(question, mode, payload.top_k, None, metadata_filter)
            ranked_ids = [str(item.metadata["evaluation_id"]) for item in results]
            rank = ranked_ids.index(expected_id) + 1 if expected_id in ranked_ids else None
            hits += int(rank is not None)
            reciprocal_ranks.append(1 / rank if rank else 0.0)
            cases.append(RetrievalEvaluationCase(
                question=question, expected_id=expected_id,
                ranked_ids=ranked_ids, rank=rank,
            ))
        reports.append(RetrievalEvaluationReport(
            mode=mode,
            top_k=payload.top_k,
            hit_at_k=hits / len(EVALUATION_SET),
            mrr=sum(reciprocal_ranks) / len(reciprocal_ranks),
            cases=cases,
        ))
    return RetrievalEvaluationResult(reports=reports)


def seed_multi_tool_documents() -> RagIndexResult:
    documents = [
        ("hotel", "체크인 3일 전까지 취소하면 전액 환불합니다."),
        ("hotel", "체크인 당일 취소에는 숙박 요금 전액이 부과됩니다."),
        ("flight", "교육용 국내선의 위탁 수하물은 15kg까지 허용합니다."),
        ("flight", "국내선 탑승 수속은 출발 40분 전에 마감합니다."),
        ("attraction", "바다 박물관은 매주 화요일에 휴관합니다."),
        ("attraction", "전망대 운영 시간은 오전 9시부터 오후 8시까지입니다."),
    ]
    chunks = [
        RagChunk(
            chunk_id=f"{MULTI_TOOL_SOURCE}:{index}", text=content,
            source=MULTI_TOOL_SOURCE, title=f"{topic} 지식 저장소", chunk_index=index,
            metadata={"dataset": "multi_tool", "topic": topic, "status": "active"},
        )
        for index, (topic, content) in enumerate(documents)
    ]
    return index_chunks(chunks, source=MULTI_TOOL_SOURCE, replace_source=True)


def _detect_topics(message: str) -> set[str]:
    keywords = {
        "hotel": ("호텔", "숙소", "체크인", "환불", "취소"),
        "flight": ("항공", "비행기", "수하물", "탑승"),
        "attraction": ("관광", "박물관", "전망대", "명소"),
    }
    return {topic for topic, words in keywords.items() if any(word in message for word in words)}


def run_multi_tool_agent(payload: MultiToolRagRequest) -> MultiToolRagResult:
    state = redis_cache.get_agent_state(payload.session_id) or {
        "topics": [], "step_count": 0, "trace": [],
    }
    if state["step_count"] >= MAX_MULTI_TOOL_STEPS:
        return MultiToolRagResult(
            status="stopped", final_answer="최대 실행 횟수를 초과했습니다.",
            topics=state["topics"], step_count=state["step_count"],
            max_steps=MAX_MULTI_TOOL_STEPS, termination_reason="max_steps_exceeded",
            trace=state["trace"],
        )

    state["step_count"] += 1
    topics = set(state["topics"]) | _detect_topics(payload.message)
    state["topics"] = sorted(topics)
    state["trace"].append({"stage": "agent_state", "data": {
        "step_count": state["step_count"], "topics": state["topics"],
    }})
    if not topics:
        question = "호텔, 항공, 관광 중 어떤 정보가 필요한가요?"
        state["trace"].append({"stage": "clarification", "data": {"question": question}})
        redis_cache.set_agent_state(payload.session_id, state)
        return MultiToolRagResult(
            status="needs_clarification", final_answer=question,
            topics=[], step_count=state["step_count"], max_steps=MAX_MULTI_TOOL_STEPS,
            termination_reason="clarification_required", trace=state["trace"],
        )

    tool_names = {
        "hotel": "search_hotel_knowledge",
        "flight": "search_flight_knowledge",
        "attraction": "search_attraction_knowledge",
    }
    calls: list[dict[str, Any]] = []
    tool_results: dict[str, list[RagSearchItem]] = {}
    for topic in sorted(topics):
        if state["step_count"] >= MAX_MULTI_TOOL_STEPS:
            redis_cache.set_agent_state(payload.session_id, state)
            return MultiToolRagResult(
                status="stopped", final_answer="최대 실행 횟수를 초과했습니다.",
                topics=state["topics"], tool_calls=calls, tool_results=tool_results,
                step_count=state["step_count"], max_steps=MAX_MULTI_TOOL_STEPS,
                termination_reason="max_steps_exceeded", trace=state["trace"],
            )
        state["step_count"] += 1
        call = {"name": tool_names[topic], "arguments": {"query": payload.message, "top_k": 2}}
        calls.append(call)
        state["trace"].append({"stage": "tool_call", "data": call})
        execution = execute_tool_safely(call["name"], call["arguments"])
        state["trace"].append({"stage": "tool_execution", "data": execution.model_dump(mode="json")})
        if not execution.success:
            redis_cache.set_agent_state(payload.session_id, state)
            return MultiToolRagResult(
                status="stopped", final_answer="검색 Tool 실행에 실패했습니다.",
                topics=state["topics"], tool_calls=calls, tool_results=tool_results,
                step_count=state["step_count"], max_steps=MAX_MULTI_TOOL_STEPS,
                termination_reason="tool_error", trace=state["trace"],
            )
        tool_results[topic] = [
            RagSearchItem.model_validate(item) for item in execution.data["results"]
        ]

    evidence = [item for items in tool_results.values() for item in items]
    if not evidence:
        answer = "선택한 지식 저장소에서 근거를 찾지 못했습니다."
        reason = "no_evidence"
    elif payload.provider == "mock":
        answer = " ".join(f"{item.content} (출처: {item.source})" for item in evidence)
        reason = "grounded_answer"
    else:
        context = "\n".join(f"[{item.source}] {item.content}" for item in evidence)
        answer = str(generate(
            payload.provider,
            "Tool Result만 사용해 한국어로 답하고 출처를 표시하세요.",
            f"질문: {payload.message}\n\nTool Result:\n{context}",
        ).content)
        reason = "grounded_answer"
    state["trace"].append({"stage": "finish", "data": {"reason": reason}})
    redis_cache.set_agent_state(payload.session_id, state)
    return MultiToolRagResult(
        status="completed", final_answer=answer, topics=state["topics"],
        tool_calls=calls, tool_results=tool_results,
        step_count=state["step_count"], max_steps=MAX_MULTI_TOOL_STEPS,
        termination_reason=reason, trace=state["trace"],
    )
