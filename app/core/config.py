
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "Hospital RCM Agentic AI"
    app_version: str = "0.1.0"

    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "qwen3:4b"

    agent_config_dir: str = "app/agents/configs"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

