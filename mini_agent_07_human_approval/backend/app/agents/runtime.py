import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.agents.models import AgentProfile
from app.agents.registry import get_agent
from app.approval.policies import action_risk
from app.approval.store import PROCESSED_CALLS, add_audit, get_run, save_run
from app.core.config import MAX_AGENT_STEPS, OPENAI_MODEL
from app.mcp.client import call_tool, discover_tools
from app.providers.openai import create_client, first_response, next_response
from app.progress.store import publish


def public_result(state: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "run_id", "agent_id", "agent_name", "goal", "actor_id", "question", "model",
        "status", "termination_reason", "llm_calls", "tool_calls", "trace", "answer",
        "pending_approval",
    )
    return {key: state.get(key) for key in keys}


async def _advance(profile: AgentProfile, state: dict[str, Any], response: Any) -> dict[str, Any]:
    """읽기는 실행하고 변경 Tool 직전에 승인 대기 상태로 중단합니다."""
    client = create_client()
    tools = await discover_tools(profile.allowed_tools)
    for step in range(state.get("next_step", 1), MAX_AGENT_STEPS + 1):
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            state.update(status="completed", termination_reason="model_finished", answer=response.output_text)
            publish(state["run_id"], "completed", "Agent 실행이 완료됐습니다.", 100, "completed")
            state["trace"].append(
                {"step": step, "owner": "ai_agent", "stage": "model_final_answer", "text": response.output_text}
            )
            state["pending_approval"] = None
            save_run(state)
            return public_result(state)

        call = calls[0]
        publish(state["run_id"], "model_selected_tool", f"Model이 {call.name} Tool을 선택했습니다.", min(20 + step * 10, 75), "running")
        try:
            arguments = json.loads(call.arguments)
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments는 JSON Object여야 합니다.")
            if call.name not in profile.allowed_tools:
                raise ValueError(f"이 Agent에 허용되지 않은 Tool입니다: {call.name}")
        except (AttributeError, json.JSONDecodeError, TypeError, ValueError) as error:
            state.update(status="blocked", termination_reason="invalid_tool_call")
            state["trace"].append(
                {"step": step, "owner": "policy", "stage": "invalid_tool_call", "error": str(error)}
            )
            save_run(state)
            return public_result(state)

        risk = action_risk(call.name)
        state["trace"].append(
            {"step": step, "owner": "ai_agent", "stage": "model_selected_tool", "tool": call.name, "risk": risk}
        )
        if risk == "forbidden":
            state.update(status="blocked", termination_reason="forbidden_tool")
            state["trace"].append(
                {"step": step, "owner": "policy", "stage": "forbidden_tool_blocked", "tool": call.name}
            )
            save_run(state)
            return public_result(state)

        if risk == "change":
            target = {
                "agent_id": profile.agent_id,
                "tool": call.name,
                "arguments": arguments,
            }
            state.update(
                status="waiting_approval",
                termination_reason="approval_required",
                response_id=response.id,
                next_step=step + 1,
                pending_call={"call_id": call.call_id, "tool": call.name, "arguments": arguments},
                pending_approval={
                    "risk": "change",
                    "question": f"{call.name} 변경 작업을 실행할까요?",
                    "approval_target": target,
                    "allowed_decisions": ["approve", "reject"],
                },
            )
            state["trace"].append(
                {"step": step, "owner": "policy", "stage": "paused_for_approval", "approval_target": target}
            )
            save_run(state)
            publish(state["run_id"], "waiting_approval", "사용자 승인을 기다리고 있습니다.", 80, "waiting_approval")
            return public_result(state)

        try:
            result, trace = await call_tool(call.name, arguments, profile.allowed_tools)
            publish(state["run_id"], "tool_completed", f"{call.name} Tool 실행을 완료했습니다.", min(30 + step * 10, 70), "running")
            state["tool_calls"] += 1
            state["trace"].append({"step": step, "owner": "mcp", "stage": "read_tool_executed", **trace})
            output = {
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result, ensure_ascii=False),
            }
            response = await next_response(client, response.id, [output], profile.instructions, tools)
            state["llm_calls"] += 1
        except Exception as error:
            state.update(status="failed", termination_reason="tool_or_model_error")
            state["trace"].append(
                {"step": step, "owner": "runtime", "stage": "tool_or_model_error", "error": str(error)}
            )
            save_run(state)
            return public_result(state)

    state.update(status="stopped", termination_reason="max_steps_exceeded")
    state["trace"].append({"owner": "runtime", "stage": "max_steps_exceeded"})
    save_run(state)
    return public_result(state)


async def start_single_agent(profile: AgentProfile, question: str, actor_id: str) -> dict[str, Any]:
    state: dict[str, Any] = {
        "run_id": f"run-{uuid4().hex[:12]}",
        "agent_id": profile.agent_id,
        "agent_name": profile.name,
        "goal": profile.goal,
        "actor_id": actor_id,
        "question": question,
        "model": OPENAI_MODEL,
        "status": "running",
        "termination_reason": None,
        "llm_calls": 0,
        "tool_calls": 0,
        "trace": [{"owner": "runtime", "stage": "run_started", "actor_id": actor_id}],
        "answer": None,
        "pending_approval": None,
        "next_step": 1,
    }
    publish(state["run_id"], "queued", "Agent 실행 요청을 접수했습니다.", 5, "queued")
    try:
        tools = await discover_tools(profile.allowed_tools)
        names = {tool["name"] for tool in tools}
        missing = profile.allowed_tools - names
        if missing:
            raise RuntimeError(f"MCP Server에 필요한 Tool이 없습니다: {sorted(missing)}")
        state["trace"].append({"owner": "mcp", "stage": "tools_discovered", "tools": sorted(names)})
        publish(state["run_id"], "tools_discovered", "MCP Tool을 확인했습니다.", 15, "running")
        response = await first_response(create_client(), question, profile.instructions, tools)
        state["llm_calls"] = 1
        return await _advance(profile, state, response)
    except Exception as error:
        state.update(status="failed", termination_reason="startup_error")
        state["trace"].append({"owner": "runtime", "stage": "startup_error", "error": str(error)})
        save_run(state)
        return public_result(state)


async def resume_after_decision(
    run_id: str,
    actor_id: str,
    decision: str,
    approval_target: dict[str, Any],
    note: str = "",
) -> dict[str, Any]:
    state = get_run(run_id)
    if state is None:
        raise ValueError("실행을 찾을 수 없습니다.")
    if state["status"] != "waiting_approval":
        raise ValueError("승인 대기 상태의 실행만 재개할 수 있습니다.")
    if actor_id != state["actor_id"]:
        raise ValueError("실행 소유자만 승인하거나 거절할 수 있습니다.")
    if decision not in {"approve", "reject"}:
        raise ValueError("decision은 approve 또는 reject여야 합니다.")
    expected = state["pending_approval"]["approval_target"]
    if approval_target != expected:
        raise ValueError("승인 대상이 대기 중인 Tool과 arguments와 다릅니다.")

    event = {
        "run_id": run_id,
        "actor_id": actor_id,
        "decision": decision,
        "approval_target": expected,
        "note": note,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if decision == "reject":
        state.update(status="rejected", termination_reason="user_rejected", pending_approval=None)
        state["trace"].append({"owner": "human", "stage": "change_rejected", **event})
        add_audit(event)
        save_run(state)
        publish(run_id, "rejected", "사용자가 변경 요청을 거절했습니다.", 100, "rejected")
        return public_result(state)

    pending = state["pending_call"]
    call_key = f"{run_id}:{pending['call_id']}"
    if call_key in PROCESSED_CALLS:
        raise ValueError("이미 실행된 승인 요청입니다.")
    profile = get_agent(state["agent_id"])
    if pending["tool"] not in profile.allowed_tools or action_risk(pending["tool"]) != "change":
        raise ValueError("현재 Agent 정책에서 허용된 변경 Tool이 아닙니다.")

    result, trace = await call_tool(pending["tool"], pending["arguments"], profile.allowed_tools)
    publish(run_id, "approved_change_executed", "승인된 변경 Tool을 실행했습니다.", 90, "running")
    PROCESSED_CALLS.add(call_key)
    state["tool_calls"] += 1
    event["result"] = result
    add_audit(event)
    state["trace"].extend(
        [
            {"owner": "human", "stage": "change_approved", "actor_id": actor_id, "approval_target": expected},
            {"owner": "mcp", "stage": "approved_change_executed", **trace},
        ]
    )
    state["pending_approval"] = None
    state["status"] = "change_executed"
    state["termination_reason"] = "approved_change_executed"
    save_run(state)
    output = {
        "type": "function_call_output",
        "call_id": pending["call_id"],
        "output": json.dumps(result, ensure_ascii=False),
    }
    tools = await discover_tools(profile.allowed_tools)
    try:
        response = await next_response(create_client(), state["response_id"], [output], profile.instructions, tools)
        state["llm_calls"] += 1
        return await _advance(profile, state, response)
    except Exception as error:
        state["status"] = "completed"
        state["termination_reason"] = "change_executed_model_error"
        state["answer"] = "승인된 변경 작업은 실행됐지만 최종 안내 생성에 실패했습니다."
        state["trace"].append(
            {"owner": "runtime", "stage": "final_model_error_after_change", "error": str(error)}
        )
        save_run(state)
        return public_result(state)
