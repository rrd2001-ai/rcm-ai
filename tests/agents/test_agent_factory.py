
from app.runtime.agent_factory import AgentFactory


def test_factory_creates_insurance_agent():
    factory = AgentFactory()

    agent = factory.create_agent("insurance_verification")

    assert agent.config.agent.id == "insurance_verification"
    assert agent.config.agent.model.name == "qwen3:4b"
    assert agent.model is not None
    assert "Insurance" in agent.system_prompt


def test_factory_creates_different_agent_personas():
    factory = AgentFactory()

    insurance = factory.create_agent("insurance_verification")
    claims = factory.create_agent("claim_preparation")

    assert insurance.config.agent.id != claims.config.agent.id
    assert insurance.system_prompt != claims.system_prompt


def test_factory_preserves_agent_guardrails():
    factory = AgentFactory()

    agent = factory.create_agent("claims_followup")

    guardrails = agent.config.agent.guardrails

    assert guardrails.can_contact_tpa is False
    assert guardrails.requires_human_approval is True

