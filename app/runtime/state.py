
from typing import Any, TypedDict


class AgentExecutionState(TypedDict, total=False):
    """State shared across an agent execution."""

    execution_id: str
    agent_id: str
    input: str

    messages: list[dict[str, Any]]

    output: dict[str, Any] | str | None
    status: str

    error: str | None

    tool_calls: list[dict[str, Any]]

    requires_human_approval: bool
    human_approved: bool

