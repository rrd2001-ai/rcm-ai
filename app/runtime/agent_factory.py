
from dataclasses import dataclass

from langchain_ollama import ChatOllama

from app.core.config import settings
from app.schemas.agent_config import AgentConfig
from app.runtime.agent_loader import AgentConfigLoader


@dataclass
class AgentRuntime:
    """Runtime representation of a configured RCM agent."""

    config: AgentConfig
    model: ChatOllama
    system_prompt: str


class AgentFactory:
    """Creates configured agents using a shared runtime."""

    def __init__(
        self,
        loader: AgentConfigLoader | None = None,
    ) -> None:
        self.loader = loader or AgentConfigLoader()

    def create_agent(self, agent_id: str) -> AgentRuntime:
        config = self.loader.load_agent(agent_id)
        agent = config.agent

        model = ChatOllama(
            model=agent.model.name,
            base_url=settings.ollama_base_url,
            temperature=agent.model.temperature,
        )

        system_prompt = self._build_system_prompt(config)

        return AgentRuntime(
            config=config,
            model=model,
            system_prompt=system_prompt,
        )

    @staticmethod
    def _build_system_prompt(config: AgentConfig) -> str:
        agent = config.agent
        guardrails = agent.guardrails

        return f"""
You are {agent.name}, a specialized hospital RCM AI agent.

ROLE:
{agent.persona.role}

OBJECTIVE:
{agent.persona.objective}

OPERATING RULES:
- Work only within your assigned responsibilities.
- Use only tools explicitly permitted by your configuration.
- Treat HMIS patient, encounter and bill records as read-only.
- Do not perform actions outside your authorized permissions.
- Do not invent missing patient, policy, claim or financial information.
- Clearly identify uncertainty and missing evidence.
- Require human approval for decisions requiring authorization.

PERMISSIONS:
- Modify HMIS: {guardrails.can_modify_hmis}
- Modify original bill: {guardrails.can_modify_original_bill}
- Submit claims: {guardrails.can_submit_claims}
- Contact TPA: {guardrails.can_contact_tpa}
- Approve financial adjustments:
  {guardrails.can_approve_financial_adjustments}
- Requires human approval:
  {guardrails.requires_human_approval}

Return findings in a structured and evidence-based manner.
""".strip()

