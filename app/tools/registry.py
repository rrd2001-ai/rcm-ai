
from dataclasses import dataclass
from inspect import isawaitable
from typing import Any, Callable
import re

from pydantic import BaseModel, ValidationError

from app.tools.capabilities import ToolCapability


class ToolRegistryError(Exception):
    """Base exception for tool registry errors."""


class ToolNotFoundError(ToolRegistryError):
    """Raised when a requested tool is not registered."""


class ToolPermissionError(ToolRegistryError):
    """Raised when an agent is not allowed to use a tool."""


class ToolInputError(ToolRegistryError):
    """Raised when tool arguments fail schema validation."""


EXTERNAL_GUARDRAILS = {
    "can_contact_tpa",
    "can_submit_claims",
    "can_modify_hmis",
    "can_modify_original_bill",
}

FINANCIAL_GUARDRAIL = "can_approve_financial_adjustments"


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    handler: Callable[..., Any]
    description: str = ""
    args_schema: type[BaseModel] | None = None
    capability: ToolCapability = ToolCapability.READ
    required_guardrail: str | None = None


class ToolRegistry:
    """Central registry for tools shared across RCM agents."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        handler: Callable[..., Any],
        description: str = "",
        args_schema: type[BaseModel] | None = None,
        capability: ToolCapability = ToolCapability.READ,
        required_guardrail: str | None = None,
    ) -> None:

        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValueError(f"Invalid tool name: {name}")

        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")

        if not callable(handler):
            raise ValueError(f"Handler must be callable: {name}")

        if not isinstance(capability, ToolCapability):
            raise ValueError(f"Invalid capability for tool: {name}")

        if capability == ToolCapability.EXTERNAL_ACTION:
            if required_guardrail not in EXTERNAL_GUARDRAILS:
                raise ValueError(
                    f"External tool '{name}' must declare "
                    "a valid required_guardrail"
                )

        if capability == ToolCapability.FINANCIAL_ACTION:
            if required_guardrail != FINANCIAL_GUARDRAIL:
                raise ValueError(
                    f"Financial tool '{name}' must require "
                    f"'{FINANCIAL_GUARDRAIL}'"
                )

        self._tools[name] = ToolDefinition(
            name=name,
            handler=handler,
            description=description,
            args_schema=args_schema,
            capability=capability,
            required_guardrail=required_guardrail,
        )

    def get(self, name: str) -> ToolDefinition:
        tool = self._tools.get(name)

        if tool is None:
            raise ToolNotFoundError(
                f"Tool not registered: {name}"
            )

        return tool

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    async def execute(
        self,
        agent_config,
        tool_name: str,
        *,
        human_approved: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Authorize, validate and execute a registered tool."""

        agent = agent_config.agent

        # 1. Enforce the agent's tool allowlist.
        if tool_name not in agent.tools.allowed:
            raise ToolPermissionError(
                f"Agent '{agent.id}' is not allowed "
                f"to use '{tool_name}'"
            )

        # 2. Verify that the tool is registered.
        tool = self.get(tool_name)

        # 3. Enforce capability-specific guardrails.
        if tool.capability in {
            ToolCapability.EXTERNAL_ACTION,
            ToolCapability.FINANCIAL_ACTION,
        }:
            guardrail = tool.required_guardrail

            if not guardrail:
                raise ToolPermissionError(
                    f"Tool '{tool_name}' has no required guardrail"
                )

            if not getattr(agent.guardrails, guardrail, False):
                raise ToolPermissionError(
                    f"Agent '{agent.id}' lacks permission "
                    f"'{guardrail}' for tool '{tool_name}'"
                )

            if not human_approved:
                raise ToolPermissionError(
                    f"Tool '{tool_name}' requires explicit "
                    "human approval"
                )

        # 4. Validate arguments.
        if tool.args_schema is not None:
            try:
                validated_input = tool.args_schema.model_validate(
                    kwargs
                )
            except ValidationError as exc:
                raise ToolInputError(
                    f"Invalid input for tool '{tool_name}': {exc}"
                ) from exc

            kwargs = validated_input.model_dump()

        # 5. Execute the handler.
        result = tool.handler(**kwargs)

        if isawaitable(result):
            result = await result

        return result

