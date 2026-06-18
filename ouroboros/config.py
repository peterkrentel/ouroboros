from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="OUROBOROS_", extra="ignore")

    project_name: str = "Ouroboros"
    domain: str = "platform engineering"
    llm_provider: str = "ollama"
    llm_model: str = "qwen3:8b"
    llm_timeout_seconds: float = 20.0
    ollama_url: str = "http://localhost:11434"
    gemini_model: str = "gemini-2.0-flash-lite"
    gemini_api_key: str = Field(default="", repr=False)
    guard_jwt_secret: str = Field(default="dev-secret", repr=False)
    required_tool_scope: str = "tools:invoke"
    promotion_quorum: int = 2


settings = Settings()
