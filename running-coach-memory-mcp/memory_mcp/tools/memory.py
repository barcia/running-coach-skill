"""Memory tools with semantic search."""

import sqlite3
from typing import Literal

from memory_mcp.config import Settings
from memory_mcp.embeddings import create_embedding, get_embedding_client, serialize_embedding
from memory_mcp.models import Memory, MemorySearchResult


def add_memory(
    conn: sqlite3.Connection,
    settings: Settings,
    author: Literal["user", "agent", "system"],
    content: str,
) -> Memory:
    """Add a memory with automatic embedding generation."""
    # Insert memory
    cursor = conn.execute(
        "INSERT INTO memory (author, content) VALUES (?, ?)",
        (author, content),
    )
    memory_id = cursor.lastrowid

    # Generate and store embedding
    client = get_embedding_client(settings)
    embedding = create_embedding(client, content, settings.embedding_model)
    embedding_bytes = serialize_embedding(embedding)

    conn.execute(
        "INSERT INTO memory_vec (rowid, embedding) VALUES (?, ?)",
        (memory_id, embedding_bytes),
    )

    conn.commit()

    # Return created memory
    row = conn.execute(
        "SELECT id, created_at, author, content FROM memory WHERE id = ?",
        (memory_id,),
    ).fetchone()

    return Memory(
        id=row["id"],
        created_at=row["created_at"],
        author=row["author"],
        content=row["content"],
    )


def get_memory(conn: sqlite3.Connection, memory_id: int) -> Memory | None:
    """Get a memory by ID."""
    row = conn.execute(
        "SELECT id, created_at, author, content FROM memory WHERE id = ?",
        (memory_id,),
    ).fetchone()

    if row is None:
        return None

    return Memory(
        id=row["id"],
        created_at=row["created_at"],
        author=row["author"],
        content=row["content"],
    )


def list_memories(
    conn: sqlite3.Connection,
    author: Literal["user", "agent", "system"] | None = None,
    limit: int = 50,
) -> list[Memory]:
    """List memories with optional author filter."""
    if author:
        rows = conn.execute(
            "SELECT id, created_at, author, content FROM memory WHERE author = ? ORDER BY created_at DESC LIMIT ?",
            (author, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, created_at, author, content FROM memory ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()

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
    conn: sqlite3.Connection,
    settings: Settings,
    query: str,
    limit: int = 10,
) -> list[MemorySearchResult]:
    """Search memories by semantic similarity."""
    # Generate query embedding
    client = get_embedding_client(settings)
    query_embedding = create_embedding(client, query, settings.embedding_model)
    query_bytes = serialize_embedding(query_embedding)

    # Vector search with sqlite-vec KNN syntax
    rows = conn.execute(
        """
        SELECT
            m.id,
            m.created_at,
            m.author,
            m.content,
            v.distance
        FROM memory_vec v
        JOIN memory m ON m.id = v.rowid
        WHERE v.embedding MATCH ? AND k = ?
        ORDER BY v.distance
        """,
        (query_bytes, limit),
    ).fetchall()

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


def delete_memory(conn: sqlite3.Connection, memory_id: int) -> bool:
    """Delete a memory and its embedding.

    Uses explicit transaction to ensure both memory and embedding
    are deleted atomically.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION")
        # Delete from memory table first (primary record)
        cursor.execute("DELETE FROM memory WHERE id = ?", (memory_id,))
        deleted = cursor.rowcount > 0
        # Delete from vector table (secondary record)
        cursor.execute("DELETE FROM memory_vec WHERE rowid = ?", (memory_id,))
        cursor.execute("COMMIT")
        return deleted
    except Exception:
        cursor.execute("ROLLBACK")
        raise
