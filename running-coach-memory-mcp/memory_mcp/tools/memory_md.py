"""Memory MD tool for persistent MEMORY.md content in Turso."""

from typing import Any

from memory_mcp.database import query_one


def get_memory_md(conn: Any) -> str:
    """Get the MEMORY.md content."""
    row = query_one(conn, "SELECT content FROM memory_md WHERE id = 1")
    if row is None:
        return ""
    return row["content"]


def update_memory_md(conn: Any, content: str) -> str:
    """Update the MEMORY.md content."""
    conn.execute(
        "UPDATE memory_md SET content = ? WHERE id = 1",
        (content,),
    )
    conn.commit()
    return content
