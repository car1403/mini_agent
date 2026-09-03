import asyncio

import pytest

from app.agents.runtime import resume_after_decision
from app.approval.policies import action_risk
from app.approval.store import PROCESSED_CALLS, RUNS


TARGET = {
    "agent_id": "order",
    "tool": "place_order",
    "arguments": {"product_id": "P-KEYBOARD", "quantity": 2},
}


def pending_state(run_id: str = "run-test") -> dict:
    return {
        "run_id": run_id,
        "agent_id": "order",
        "agent_name": "Order Assistant Agent",
        "goal": "안전한 주문",
        "actor_id": "user-01",
        "question": "키보드 2개 주문",
        "model": "test",
        "status": "waiting_approval",
        "termination_reason": "approval_required",
        "llm_calls": 1,
        "tool_calls": 0,
        "trace": [],
        "answer": None,
        "pending_approval": {"approval_target": TARGET},
        "pending_call": {"call_id": "call-1", "tool": "place_order", "arguments": TARGET["arguments"]},
        "response_id": "response-1",
    }


@pytest.fixture(autouse=True)
def clear_store():
    RUNS.clear()
    PROCESSED_CALLS.clear()
    yield
    RUNS.clear()
    PROCESSED_CALLS.clear()


def test_tool_risk_is_deterministic() -> None:
    assert action_risk("search_product") == "read"
    assert action_risk("place_order") == "change"
    assert action_risk("make_payment") == "forbidden"


def test_different_actor_is_blocked() -> None:
    RUNS["run-test"] = pending_state()
    with pytest.raises(ValueError, match="실행 소유자"):
        asyncio.run(resume_after_decision("run-test", "user-02", "approve", TARGET))


def test_tampered_snapshot_is_blocked() -> None:
    RUNS["run-test"] = pending_state()
    changed = {**TARGET, "arguments": {"product_id": "P-KEYBOARD", "quantity": 99}}
    with pytest.raises(ValueError, match="승인 대상"):
        asyncio.run(resume_after_decision("run-test", "user-01", "approve", changed))


def test_duplicate_execution_is_blocked_before_tool_call() -> None:
    RUNS["run-test"] = pending_state()
    PROCESSED_CALLS.add("run-test:call-1")
    with pytest.raises(ValueError, match="이미 실행된"):
        asyncio.run(resume_after_decision("run-test", "user-01", "approve", TARGET))
