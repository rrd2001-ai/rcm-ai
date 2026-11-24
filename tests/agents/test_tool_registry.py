from app.tools.registry import ToolInputError
from app.tools.schemas.patient import PatientRecordLookupInput
import pytest

from app.runtime.agent_loader import AgentConfigLoader
from app.tools.registry import (
    ToolRegistry,
    ToolPermissionError,
    ToolNotFoundError,
)
from app.tools.permissions import validate_agent_tools


def test_register_and_list_tools():
    registry = ToolRegistry()

    registry.register(
        "patient_record_lookup",
        lambda patient_id: {"patient_id": patient_id},
    )

    assert "patient_record_lookup" in registry.list_tools()


def test_duplicate_tool_registration_is_rejected():
    registry = ToolRegistry()
    handler = lambda: "ok"

    registry.register("test_tool", handler)

    with pytest.raises(ValueError):
        registry.register("test_tool", handler)


def test_unregistered_tool_is_rejected():
    registry = ToolRegistry()

    with pytest.raises(ToolNotFoundError):
        registry.get("unknown_tool")


def test_invalid_tool_name_is_rejected():
    registry = ToolRegistry()

    with pytest.raises(ValueError):
        registry.register("../invalid", lambda: None)


@pytest.mark.asyncio
async def test_allowed_agent_can_execute_tool():
    agents = AgentConfigLoader().load_all()
    agent = agents["insurance_verification"]

    registry = ToolRegistry()
    registry.register(
        "patient_record_lookup",
        lambda patient_id: {"patient_id": patient_id},
    )

    result = await registry.execute(
        agent,
        "patient_record_lookup",
        patient_id="TEST-001",
    )

    assert result == {"patient_id": "TEST-001"}


@pytest.mark.asyncio
async def test_agent_cannot_execute_disallowed_tool():
    agents = AgentConfigLoader().load_all()
    agent = agents["insurance_verification"]

    registry = ToolRegistry()
    registry.register("claim_analytics_lookup", lambda: {})

    with pytest.raises(ToolPermissionError):
        await registry.execute(
            agent,
            "claim_analytics_lookup",
        )


def test_agent_configuration_references_registered_tools():
    agents = AgentConfigLoader().load_all()
    registry = ToolRegistry()

    # Collect unique tool names across all agents.
    all_tool_names = {
        tool_name
        for agent in agents.values()
        for tool_name in agent.agent.tools.allowed
    }

    # Register each shared tool exactly once.
    for tool_name in all_tool_names:
        registry.register(tool_name, lambda: {})

    # Verify every agent's allowed tools exist.
    registered_tools = set(registry.list_tools())

    for agent in agents.values():
        for tool_name in agent.agent.tools.allowed:
            assert tool_name in registered_tools


def test_patient_lookup_accepts_valid_input():
    result = PatientRecordLookupInput(
        patient_id="PAT-001"
    )

    assert result.patient_id == "PAT-001"


def test_patient_lookup_rejects_empty_patient_id():
    with pytest.raises(Exception):
        PatientRecordLookupInput(patient_id="")


@pytest.mark.asyncio
async def test_tool_registry_validates_input():
    agents = AgentConfigLoader().load_all()
    agent = agents["insurance_verification"]

    registry = ToolRegistry()

    registry.register(
        "patient_record_lookup",
        lambda patient_id: {"patient_id": patient_id},
        description="Read-only HMIS patient lookup",
        args_schema=PatientRecordLookupInput,
    )

    result = await registry.execute(
        agent,
        "patient_record_lookup",
        patient_id="PAT-001",
    )

    assert result == {"patient_id": "PAT-001"}


@pytest.mark.asyncio
async def test_tool_registry_rejects_invalid_input():
    agents = AgentConfigLoader().load_all()
    agent = agents["insurance_verification"]

    registry = ToolRegistry()

    registry.register(
        "patient_record_lookup",
        lambda patient_id: {"patient_id": patient_id},
        args_schema=PatientRecordLookupInput,
    )

    with pytest.raises(ToolInputError):
        await registry.execute(
            agent,
            "patient_record_lookup",
            patient_id="",
        )


@pytest.mark.asyncio
async def test_disallowed_agent_cannot_execute_typed_tool():
    agents = AgentConfigLoader().load_all()
    agent = agents["authorization"]

    registry = ToolRegistry()

    registry.register(
        "patient_record_lookup",
        lambda patient_id: {"patient_id": patient_id},
        args_schema=PatientRecordLookupInput,
    )

    with pytest.raises(ToolPermissionError):
        await registry.execute(
            agent,
            "patient_record_lookup",
            patient_id="PAT-001",
        )

