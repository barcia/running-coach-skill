"""Configuration via environment variables."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Running Coach Memory MCP configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Required
    openrouter_api_key: str

    # Turso database
    turso_database_url: str  # libsql://your-db.turso.io or local file path
    turso_auth_token: str = ""  # Required for remote Turso, empty for local

    # Transport configuration
    mcp_transport: Literal["stdio", "streamable-http"] = "stdio"
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8000

    # Fixed (not exposed in .env)
    embedding_model: str = "openai/text-embedding-3-large"
    embedding_dimensions: int = 3072
    log_path: str = "~/Library/Logs/running-coach-memory.log"

    @property
    def log_file_path(self) -> Path:
        """Get expanded log file path."""
        return Path(self.log_path).expanduser()


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
