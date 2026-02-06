"""Plan tools for training schedule management."""

import sqlite3
from datetime import date, timedelta

from memory_mcp.models import Plan, PlanUpdate


def add_plan(
    conn: sqlite3.Connection,
    planned_at: str,
    description: str,
    notes: str | None = None,
) -> Plan:
    """Add a training plan entry."""
    cursor = conn.execute(
        "INSERT INTO plan (planned_at, description, notes) VALUES (?, ?, ?)",
        (planned_at, description, notes),
    )
    conn.commit()

    row = conn.execute(
        "SELECT id, created_at, planned_at, description, notes, status, activity_id FROM plan WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()

    return Plan(
        id=row["id"],
        created_at=row["created_at"],
        planned_at=row["planned_at"],
        description=row["description"],
        notes=row["notes"],
        status=row["status"],
        activity_id=row["activity_id"],
    )


def get_plan(conn: sqlite3.Connection, plan_id: int) -> Plan | None:
    """Get a plan by ID."""
    row = conn.execute(
        "SELECT id, created_at, planned_at, description, notes, status, activity_id FROM plan WHERE id = ?",
        (plan_id,),
    ).fetchone()

    if row is None:
        return None

    return Plan(
        id=row["id"],
        created_at=row["created_at"],
        planned_at=row["planned_at"],
        description=row["description"],
        notes=row["notes"],
        status=row["status"],
        activity_id=row["activity_id"],
    )


def list_plans(
    conn: sqlite3.Connection,
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[Plan]:
    """List plans with optional filters."""
    query = "SELECT id, created_at, planned_at, description, notes, status, activity_id FROM plan WHERE 1=1"
    params: list = []

    if start_date:
        query += " AND planned_at >= ?"
        params.append(start_date)

    if end_date:
        query += " AND planned_at <= ?"
        params.append(end_date)

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY planned_at ASC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()

    return [
        Plan(
            id=row["id"],
            created_at=row["created_at"],
            planned_at=row["planned_at"],
            description=row["description"],
            notes=row["notes"],
            status=row["status"],
            activity_id=row["activity_id"],
        )
        for row in rows
    ]


def get_today_plan(conn: sqlite3.Connection) -> list[Plan]:
    """Get plans for today."""
    today = date.today().isoformat()
    return list_plans(conn, start_date=today, end_date=today)


def get_upcoming_plans(conn: sqlite3.Connection, days: int = 7) -> list[Plan]:
    """Get plans for the next N days."""
    today = date.today()
    end = today + timedelta(days=days)
    return list_plans(conn, start_date=today.isoformat(), end_date=end.isoformat())


def update_plan(conn: sqlite3.Connection, plan_id: int, update: PlanUpdate) -> Plan | None:
    """Update a plan."""
    updates: list[str] = []
    params: list = []

    if update.planned_at is not None:
        updates.append("planned_at = ?")
        params.append(update.planned_at)

    if update.description is not None:
        updates.append("description = ?")
        params.append(update.description)

    if update.notes is not None:
        updates.append("notes = ?")
        params.append(update.notes)

    if update.status is not None:
        updates.append("status = ?")
        params.append(update.status)

    if update.activity_id is not None:
        updates.append("activity_id = ?")
        params.append(update.activity_id)

    if not updates:
        return get_plan(conn, plan_id)

    params.append(plan_id)
    query = f"UPDATE plan SET {', '.join(updates)} WHERE id = ?"

    conn.execute(query, params)
    conn.commit()

    return get_plan(conn, plan_id)


def delete_plan(conn: sqlite3.Connection, plan_id: int) -> bool:
    """Delete a plan."""
    cursor = conn.execute("DELETE FROM plan WHERE id = ?", (plan_id,))
    conn.commit()
    return cursor.rowcount > 0
