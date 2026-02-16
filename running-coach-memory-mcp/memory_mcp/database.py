"""Turso (libSQL) database with native vector search."""

from pathlib import Path
from typing import Any

import libsql

from memory_mcp.config import Settings


def get_schema_sql() -> str:
    """Load schema SQL from file."""
    schema_path = Path(__file__).parent.parent / "schema.sql"
    return schema_path.read_text()


def _execute_schema(conn: Any, schema_sql: str) -> None:
    """Execute schema SQL statements individually.

    libsql does not support executescript(), so we split on semicolons
    and execute each statement separately.
    """
    for statement in schema_sql.split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(statement)


def init_database(settings: Settings) -> Any:
    """Initialize database with schema."""
    url = settings.turso_database_url

    # Create parent directory for local file databases
    if not url.startswith(("libsql://", "http")):
        db_path = Path(url).expanduser()
        db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection(settings)
    _execute_schema(conn, get_schema_sql())
    conn.commit()
    return conn


def get_connection(settings: Settings) -> Any:
    """Get database connection."""
    url = settings.turso_database_url

    # Expand user path for local file databases
    if not url.startswith(("libsql://", "http")):
        url = str(Path(url).expanduser())

    if settings.turso_auth_token:
        return libsql.connect(url, auth_token=settings.turso_auth_token)
    return libsql.connect(url)


def query_one(conn: Any, sql: str, params: tuple = ()) -> dict | None:
    """Execute query and return single row as dict."""
    cursor = conn.execute(sql, params)
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [d[0] for d in cursor.description]
    return dict(zip(columns, row))


def query_all(conn: Any, sql: str, params: tuple = ()) -> list[dict]:
    """Execute query and return all rows as dicts."""
    cursor = conn.execute(sql, params)
    rows = cursor.fetchall()
    if not rows:
        return []
    columns = [d[0] for d in cursor.description]
    return [dict(zip(columns, row)) for row in rows]
