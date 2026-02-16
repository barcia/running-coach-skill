"""Memory tools with semantic search."""

import json
from typing import Any, Literal

from memory_mcp.config import Settings
from memory_mcp.database import query_all, query_one
from memory_mcp.embeddings import create_embedding, get_embedding_client
from memory_mcp.models import Memory, MemorySearchResult


def add_memory(
    conn: Any,
    settings: Settings,
    author: Literal["user", "agent", "system"],
    content: str,
) -> Memory:
    """Add a memory with automatic embedding generation."""
    # Generate embedding
    client = get_embedding_client(settings)
    embedding = create_embedding(client, content, settings.embedding_model)
    embedding_json = json.dumps(embedding)

    # Insert memory with embedding in one statement
    cursor = conn.execute(
        "INSERT INTO memory (author, content, embedding) VALUES (?, ?, vector32(?))",
        (author, content, embedding_json),
    )
    memory_id = cursor.lastrowid
    conn.commit()

    # Return created memory
    row = query_one(
        conn,
        "SELECT id, created_at, author, content FROM memory WHERE id = ?",
        (memory_id,),
    )

    return Memory(
        id=row["id"],
        created_at=row["created_at"],
        author=row["author"],
        content=row["content"],
    )


def get_memory(conn: Any, memory_id: int) -> Memory | None:
    """Get a memory by ID."""
    row = query_one(
        conn,
        "SELECT id, created_at, author, content FROM memory WHERE id = ?",
        (memory_id,),
    )

    if row is None:
        return None

    return Memory(
        id=row["id"],
        created_at=row["created_at"],
        author=row["author"],
        content=row["content"],
    )


def list_memories(
    conn: Any,
    author: Literal["user", "agent", "system"] | None = None,
    limit: int = 50,
) -> list[Memory]:
    """List memories with optional author filter."""
    if author:
        rows = query_all(
            conn,
            "SELECT id, created_at, author, content FROM memory WHERE author = ? ORDER BY created_at DESC LIMIT ?",
            (author, limit),
        )
    else:
        rows = query_all(
            conn,
            "SELECT id, created_at, author, content FROM memory ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )

    return [
        Memory(
            id=row["id"],
            created_at=row["created_at"],
            author=row["author"],
            content=row["content"],
        )
        for row in rows
    ]


def search_memories(
    conn: Any,
    settings: Settings,
    query: str,
    limit: int = 10,
) -> list[MemorySearchResult]:
    """Search memories by semantic similarity using native libSQL vector search."""
    # Generate query embedding
    client = get_embedding_client(settings)
    query_embedding = create_embedding(client, query, settings.embedding_model)
    query_json = json.dumps(query_embedding)

    # Native vector search with cosine distance
    rows = query_all(
        conn,
        """
        SELECT
            id,
            created_at,
            author,
            content,
            vector_distance_cos(embedding, vector32(?)) AS distance
        FROM memory
        WHERE embedding IS NOT NULL
        ORDER BY distance
        LIMIT ?
        """,
        (query_json, limit),
    )

    return [
        MemorySearchResult(
            id=row["id"],
            created_at=row["created_at"],
            author=row["author"],
            content=row["content"],
            distance=row["distance"],
        )
        for row in rows
    ]


def delete_memory(conn: Any, memory_id: int) -> bool:
    """Delete a memory and its embedding."""
    cursor = conn.execute("DELETE FROM memory WHERE id = ?", (memory_id,))
    conn.commit()
    return cursor.rowcount > 0
