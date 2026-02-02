"""Configuration via environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Running Coach Memory MCP configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Required
    openrouter_api_key: str

    # Configurable
    database_path: str = "~/.local/share/running-coach/memory.db"

    # Fixed (not exposed in .env)
    embedding_model: str = "openai/text-embedding-3-large"
    embedding_dimensions: int = 3072
    log_path: str = "~/Library/Logs/running-coach-memory.log"

    @property
    def db_path(self) -> Path:
        """Get expanded database path."""
        return Path(self.database_path).expanduser()

    @property
    def log_file_path(self) -> Path:
        """Get expanded log file path."""
        return Path(self.log_path).expanduser()


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
