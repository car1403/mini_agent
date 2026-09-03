from app.agents.order_agent import ORDER_AGENT
from app.agents.runtime import resume_after_decision, start_single_agent
from app.approval.store import get_run, list_audit
from app.schemas.agent import AgentRequest, AgentResponse, ApprovalDecision


async def start(request: AgentRequest) -> AgentResponse:
    return AgentResponse.model_validate(
        await start_single_agent(ORDER_AGENT, request.question.strip(), request.actor_id.strip())
    )


async def decide(run_id: str, request: ApprovalDecision) -> AgentResponse:
    return AgentResponse.model_validate(
        await resume_after_decision(
            run_id,
            request.actor_id.strip(),
            request.decision,
            request.approval_target,
            request.note,
        )
    )


def find_run(run_id: str):
    return get_run(run_id)


def audit_for_run(run_id: str):
    return list_audit(run_id)
