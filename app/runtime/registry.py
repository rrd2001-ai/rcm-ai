
from app.schemas.agent_config import AgentConfig


class AgentRegistry:
    """Stores loaded agent configurations."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentConfig] = {}

    def register(self, config: AgentConfig) -> None:
        agent_id = config.agent.id

        if agent_id in self._agents:
            raise ValueError(f"Agent already registered: {agent_id}")

        self._agents[agent_id] = config

    def get(self, agent_id: str) -> AgentConfig:
        config = self._agents.get(agent_id)

        if config is None:
            raise ValueError(f"Agent not registered: {agent_id}")

        return config

    def list_agents(self) -> list[str]:
        return sorted(self._agents.keys())

