"""Test fixtures for Running Coach Memory MCP."""

import os
import tempfile
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from memory_mcp.config import Settings
from memory_mcp.database import init_database


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Create a temporary database path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def mock_settings(temp_db_path: str) -> Settings:
    """Create settings with temp database."""
    return Settings(
        openrouter_api_key="test-key",
        turso_database_url=temp_db_path,
        turso_auth_token="",
        embedding_model="openai/text-embedding-3-large",
        embedding_dimensions=3072,
    )


@pytest.fixture
def mock_embedding():
    """Mock embedding function to avoid API calls."""
    # Create a fake embedding of correct dimension
    fake_embedding = [0.1] * 3072

    with patch("memory_mcp.tools.memory.get_embedding_client") as mock_client:
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=fake_embedding)]
        mock_openai.embeddings.create.return_value = mock_response
        mock_client.return_value = mock_openai
        yield mock_client


@pytest.fixture
def db_connection(mock_settings: Settings):
    """Create database connection with initialized schema."""
    conn = init_database(mock_settings)
    yield conn
    conn.close()
