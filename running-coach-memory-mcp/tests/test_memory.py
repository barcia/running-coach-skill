"""Tests for memory tools."""

from memory_mcp.tools.memory import (
    add_memory,
    delete_memory,
    get_memory,
    list_memories,
    search_memories,
)


def test_add_memory(db_connection, mock_settings, mock_embedding):
    """Test adding a memory."""
    memory = add_memory(
        db_connection,
        mock_settings,
        author="user",
        content="El atleta prefiere entrenar por las mañanas",
    )

    assert memory.id == 1
    assert memory.author == "user"
    assert "mañanas" in memory.content


def test_get_memory(db_connection, mock_settings, mock_embedding):
    """Test getting a memory by ID."""
    created = add_memory(
        db_connection,
        mock_settings,
        author="agent",
        content="Test memory",
    )
    memory = get_memory(db_connection, created.id)

    assert memory is not None
    assert memory.content == "Test memory"


def test_list_memories_by_author(db_connection, mock_settings, mock_embedding):
    """Test listing memories filtered by author."""
    add_memory(db_connection, mock_settings, author="user", content="User memory")
    add_memory(db_connection, mock_settings, author="agent", content="Agent memory")
    add_memory(db_connection, mock_settings, author="system", content="System memory")

    user_memories = list_memories(db_connection, author="user")
    assert len(user_memories) == 1
    assert user_memories[0].author == "user"


def test_search_memories(db_connection, mock_settings, mock_embedding):
    """Test semantic search of memories."""
    add_memory(
        db_connection,
        mock_settings,
        author="user",
        content="Le gusta correr temprano por la mañana",
    )
    add_memory(
        db_connection,
        mock_settings,
        author="agent",
        content="Prefiere series de velocidad los martes",
    )

    # Search should return results (mocked embeddings will return same distance)
    results = search_memories(db_connection, mock_settings, query="horario de entrenamiento", limit=5)

    assert len(results) >= 1
    assert hasattr(results[0], "distance")


def test_delete_memory(db_connection, mock_settings, mock_embedding):
    """Test deleting a memory."""
    created = add_memory(
        db_connection,
        mock_settings,
        author="user",
        content="To be deleted",
    )

    result = delete_memory(db_connection, created.id)
    assert result is True

    memory = get_memory(db_connection, created.id)
    assert memory is None
