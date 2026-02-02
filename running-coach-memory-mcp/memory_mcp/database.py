"""SQLite database with sqlite-vec for vector search."""

import sqlite3
from pathlib import Path

import sqlite_vec

from memory_mcp.config import Settings


def get_schema_sql() -> str:
    """Load schema SQL from file."""
    schema_path = Path(__file__).parent.parent / "schema.sql"
    return schema_path.read_text()


def init_database(settings: Settings) -> sqlite3.Connection:
    """Initialize database with schema and sqlite-vec extension."""
    db_path = settings.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Load sqlite-vec extension
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    # Apply schema
    conn.executescript(get_schema_sql())

    # Create vector table for memory embeddings
    # Check if table exists first
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='memory_vec'"
    )
    if cursor.fetchone() is None:
        conn.execute(
            f"CREATE VIRTUAL TABLE memory_vec USING vec0(embedding float[{settings.embedding_dimensions}])"
        )

    conn.commit()
    return conn


def get_connection(settings: Settings) -> sqlite3.Connection:
    """Get database connection."""
    conn = sqlite3.connect(str(settings.db_path))
    conn.row_factory = sqlite3.Row

    # Load sqlite-vec extension
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    return conn
