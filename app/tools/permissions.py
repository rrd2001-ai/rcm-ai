from app.tools.registry import (
    ToolNotFoundError,
    ToolPermissionError,
    ToolRegistry,
)


def validate_agent_tools(agent_config, registry: ToolRegistry) -> None:
    """Ensure every tool in an agent's allowlist is registered."""

    agent = agent_config.agent

    for tool_name in agent.tools.allowed:
        try:
            registry.get(tool_name)
        except ToolNotFoundError as exc:
            raise ToolPermissionError(
                f"Agent '{agent.id}' references an unregistered "
                f"tool: '{tool_name}'"
            ) from exc
