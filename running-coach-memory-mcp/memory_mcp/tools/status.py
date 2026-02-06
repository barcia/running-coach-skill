"""Status tool for aggregated athlete situation report."""

import sqlite3

from memory_mcp.models import AthleteStatus, Memory, Plan


def get_athlete_status(conn: sqlite3.Connection) -> AthleteStatus:
    """Get aggregated athlete status.

    Returns:
    - past_plans: Last 5 plans with planned_at before today (any status)
    - upcoming_plans: Next 5 plans with planned_at today or later (any status)
    - recent_memories: Last 20 memories
    """
    # Last 5 plans before today (any status)
    past_rows = conn.execute(
        """
        SELECT id, created_at, planned_at, description, notes, status, activity_id
        FROM plan
        WHERE planned_at < date('now')
        ORDER BY planned_at DESC
        LIMIT 5
        """,
    ).fetchall()

    past_plans = [
        Plan(
            id=row["id"],
            created_at=row["created_at"],
            planned_at=row["planned_at"],
            description=row["description"],
            notes=row["notes"],
            status=row["status"],
            activity_id=row["activity_id"],
        )
        for row in past_rows
    ]

    # Next 5 plans from today onwards (any status)
    upcoming_rows = conn.execute(
        """
        SELECT id, created_at, planned_at, description, notes, status, activity_id
        FROM plan
        WHERE planned_at >= date('now')
        ORDER BY planned_at ASC
        LIMIT 5
        """,
    ).fetchall()

    upcoming_plans = [
        Plan(
            id=row["id"],
            created_at=row["created_at"],
            planned_at=row["planned_at"],
            description=row["description"],
            notes=row["notes"],
            status=row["status"],
            activity_id=row["activity_id"],
        )
        for row in upcoming_rows
    ]

    # Last 20 memories
    memory_rows = conn.execute(
        """
        SELECT id, created_at, author, content
        FROM memory
        ORDER BY id DESC
        LIMIT 20
        """,
    ).fetchall()

    recent_memories = [
        Memory(
            id=row["id"],
            created_at=row["created_at"],
            author=row["author"],
            content=row["content"],
        )
        for row in memory_rows
    ]

    return AthleteStatus(
        past_plans=past_plans,
        upcoming_plans=upcoming_plans,
        recent_memories=recent_memories,
    )
