
import pytest

from app.runtime.agent_loader import (
    AgentConfigError,
    AgentConfigLoader,
)


def test_load_all_eight_agents():
    agents = AgentConfigLoader().load_all()

    assert len(agents) == 8


def test_all_agent_ids_are_unique():
    agents = AgentConfigLoader().load_all()

    ids = [agent.agent.id for agent in agents.values()]

    assert len(ids) == len(set(ids))


def test_all_agents_use_ollama():
    agents = AgentConfigLoader().load_all()

    for agent in agents.values():
        assert agent.agent.model.provider == "ollama"


def test_all_agents_require_human_approval():
    agents = AgentConfigLoader().load_all()

    for agent in agents.values():
        assert agent.agent.guardrails.requires_human_approval is True


def test_no_agent_can_contact_tpa_automatically():
    agents = AgentConfigLoader().load_all()

    for agent in agents.values():
        assert agent.agent.guardrails.can_contact_tpa is False


def test_no_agent_can_modify_hmis_or_original_bill():
    agents = AgentConfigLoader().load_all()

    for agent in agents.values():
        assert agent.agent.guardrails.can_modify_hmis is False
        assert agent.agent.guardrails.can_modify_original_bill is False


def test_missing_agent_configuration_is_rejected(tmp_path):
    loader = AgentConfigLoader(config_dir=tmp_path)

    with pytest.raises(AgentConfigError):
        loader.load_agent("unknown_agent")


def test_invalid_agent_id_is_rejected():
    loader = AgentConfigLoader()

    with pytest.raises(AgentConfigError):
        loader.load_agent("../invalid")

