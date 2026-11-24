
from pathlib import Path
import re

import yaml
from pydantic import ValidationError

from app.schemas.agent_config import AgentConfig


class AgentConfigError(Exception):
    """Raised when an agent configuration cannot be loaded or validated."""


class AgentConfigLoader:

    def __init__(self, config_dir: Path | None = None):
        self.config_dir = config_dir or (
            Path(__file__).resolve().parents[1]
            / "agents"
            / "configs"
        )

    def load_agent(self, agent_id: str) -> AgentConfig:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", agent_id):
            raise AgentConfigError(
                f"Invalid agent ID: {agent_id}"
            )

        config_path = self.config_dir / f"{agent_id}.yaml"

        if not config_path.is_file():
            raise AgentConfigError(
                f"Configuration not found: {config_path}"
            )

        try:
            with config_path.open("r", encoding="utf-8") as file:
                raw_config = yaml.safe_load(file)

            if not isinstance(raw_config, dict):
                raise AgentConfigError(
                    f"Configuration must contain a YAML mapping: {config_path}"
                )

            config = AgentConfig.model_validate(raw_config)

            if config.agent.id != agent_id:
                raise AgentConfigError(
                    f"Agent ID mismatch in {config_path}"
                )

            return config

        except yaml.YAMLError as exc:
            raise AgentConfigError(
                f"Invalid YAML in {config_path}: {exc}"
            ) from exc

        except ValidationError as exc:
            raise AgentConfigError(
                f"Invalid agent configuration in {config_path}:\n{exc}"
            ) from exc

    def load_all(self) -> dict[str, AgentConfig]:
        if not self.config_dir.is_dir():
            raise AgentConfigError(
                f"Agent config directory not found: {self.config_dir}"
            )

        configs = {}

        for config_path in sorted(self.config_dir.glob("*.yaml")):
            agent_id = config_path.stem
            config = self.load_agent(agent_id)

            if config.agent.id in configs:
                raise AgentConfigError(
                    f"Duplicate agent ID: {config.agent.id}"
                )

            configs[config.agent.id] = config

        return configs

