from app.agents.models import AgentProfile
from app.agents.order_agent import ORDER_AGENT
from app.agents.support_agent import SUPPORT_AGENT
from app.agents.travel_agent import TRAVEL_AGENT


AGENTS: dict[str, AgentProfile] = {
    profile.agent_id: profile
    for profile in (TRAVEL_AGENT, SUPPORT_AGENT, ORDER_AGENT)
}


def get_agent(agent_id: str) -> AgentProfile:
    try:
        return AGENTS[agent_id]
    except KeyError as error:
        raise ValueError(f"지원하지 않는 Agent입니다: {agent_id}") from error
