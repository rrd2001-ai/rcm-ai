
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AgentPersona(StrictModel):
    role: str = Field(min_length=3)
    objective: str = Field(min_length=10)


class AgentModelConfig(StrictModel):
    provider: Literal["ollama"] = "ollama"
    name: str = Field(min_length=1)
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)


class AgentTools(StrictModel):
    allowed: list[str] = Field(min_length=1)


class AgentGuardrails(StrictModel):
    can_modify_hmis: bool = False
    can_modify_original_bill: bool = False
    can_submit_claims: bool = False
    can_contact_tpa: bool = False
    can_approve_financial_adjustments: bool = False
    requires_human_approval: bool = True


class AgentOutput(StrictModel):
    schema_name: str = Field(alias="schema", min_length=1)


class AgentDefinition(StrictModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=3)
    version: str = "1.0"
    persona: AgentPersona
    model: AgentModelConfig
    tools: AgentTools
    guardrails: AgentGuardrails
    output: AgentOutput


class AgentConfig(StrictModel):
    agent: AgentDefinition

