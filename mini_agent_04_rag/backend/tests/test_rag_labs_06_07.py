from app.rag import lab_service
from app.schemas import (
    MultiToolRagRequest, RagSearchItem, RetrievalEvaluationRequest, ToolRunResult,
)


def evaluation_item(document_id: str, rank: int = 0) -> RagSearchItem:
    return RagSearchItem(
        title=document_id,
        content=f"{document_id} 근거",
        source="lab-retrieval-evaluation.md",
        chunk_index=rank,
        score=1.0 - rank * 0.1,
        metadata={"dataset": "retrieval_evaluation", "evaluation_id": document_id},
    )


def test_retrieval_evaluation_calculates_hit_at_k_and_mrr(monkeypatch) -> None:
    expected_by_question = {
        question: expected for question, expected in lab_service.EVALUATION_SET
    }

    def search(query, mode, top_k, threshold, metadata_filter):
        expected = expected_by_question[query]
        if mode == "keyword" and expected == "pet":
            return []
        if mode == "pgvector" and expected == "refund":
            return [evaluation_item("baggage"), evaluation_item(expected, 1)]
        return [evaluation_item(expected)]

    monkeypatch.setattr(lab_service, "search", search)
    result = lab_service.evaluate_retrieval(RetrievalEvaluationRequest(top_k=3))
    reports = {report.mode: report for report in result.reports}

    assert reports["keyword"].hit_at_k == 0.75
    assert reports["keyword"].mrr == 0.75
    assert reports["pgvector"].hit_at_k == 1.0
    assert reports["pgvector"].mrr == 0.875
    assert reports["hybrid"].hit_at_k == 1.0
    assert reports["hybrid"].mrr == 1.0


def test_multi_tool_agent_clarifies_then_executes_two_allowed_tools(monkeypatch) -> None:
    states: dict[str, dict] = {}
    monkeypatch.setattr(
        lab_service.redis_cache,
        "get_agent_state",
        lambda session_id: states.get(session_id),
    )
    monkeypatch.setattr(
        lab_service.redis_cache,
        "set_agent_state",
        lambda session_id, state: states.__setitem__(session_id, state.copy()) or 1800,
    )

    executed: list[str] = []

    def execute(name: str, arguments: dict) -> ToolRunResult:
        executed.append(name)
        topic = "hotel" if "hotel" in name else "flight"
        return ToolRunResult(
            success=True,
            tool_name=name,
            data={"results": [RagSearchItem(
                title=topic,
                content=f"{topic} 근거",
                source="lab-multi-tool-knowledge.md",
                score=0.9,
                metadata={"dataset": "multi_tool", "topic": topic},
            ).model_dump()]},
        )

    monkeypatch.setattr(lab_service, "execute_tool_safely", execute)

    first = lab_service.run_multi_tool_agent(MultiToolRagRequest(
        session_id="session-1", message="여행 규정을 알려 주세요.", provider="mock",
    ))
    assert first.status == "needs_clarification"
    assert first.termination_reason == "clarification_required"
    assert first.step_count == 1

    second = lab_service.run_multi_tool_agent(MultiToolRagRequest(
        session_id="session-1",
        message="호텔 당일 취소와 항공 수하물 규정이 궁금합니다.",
        provider="mock",
    ))
    assert second.status == "completed"
    assert second.termination_reason == "grounded_answer"
    assert second.step_count == 4
    assert set(second.topics) == {"hotel", "flight"}
    assert executed == ["search_flight_knowledge", "search_hotel_knowledge"]
    assert all(call["name"] != "search_knowledge_base" for call in second.tool_calls)


def test_multi_tool_agent_stops_after_max_steps(monkeypatch) -> None:
    monkeypatch.setattr(
        lab_service.redis_cache,
        "get_agent_state",
        lambda session_id: {
            "topics": ["hotel"],
            "step_count": lab_service.MAX_MULTI_TOOL_STEPS,
            "trace": [],
        },
    )
    result = lab_service.run_multi_tool_agent(MultiToolRagRequest(
        session_id="done", message="호텔 정책", provider="mock",
    ))
    assert result.status == "stopped"
    assert result.termination_reason == "max_steps_exceeded"
