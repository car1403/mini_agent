from app.agents.registry import AGENTS, get_agent
from app.agents.runtime import run_single_agent
from app.schemas.agent import AgentRequest, AgentResponse, AgentSummary


def list_agents() -> list[AgentSummary]:
    return [
        AgentSummary(
            agent_id=profile.agent_id,
            name=profile.name,
            goal=profile.goal,
            description=profile.description,
            example_question=profile.example_question,
            allowed_tools=sorted(profile.allowed_tools),
        )
        for profile in AGENTS.values()
    ]


async def execute_single_agent(request: AgentRequest) -> AgentResponse:
    profile = get_agent(request.agent_id)
    result = await run_single_agent(profile, request.question.strip())
    return AgentResponse.model_validate(result)
