"""Tests for status tools."""

from datetime import date, timedelta

from memory_mcp.models import PlanUpdate
from memory_mcp.tools.memory import add_memory
from memory_mcp.tools.plan import add_plan, update_plan
from memory_mcp.tools.status import get_athlete_status


def test_get_athlete_status_empty(db_connection):
    """Test status with empty database."""
    status = get_athlete_status(db_connection)

    assert status.past_plans == []
    assert status.upcoming_plans == []
    assert status.recent_memories == []


def test_get_athlete_status_with_past_plans(db_connection):
    """Test status with past plans (any status)."""
    today = date.today()

    # Add some past plans with different statuses
    for i in range(3):
        add_plan(
            db_connection,
            (today - timedelta(days=i + 1)).isoformat(),
            f"Workout {i + 1}",
        )

    status = get_athlete_status(db_connection)

    assert len(status.past_plans) == 3
    # Should be ordered by planned_at DESC (most recent first)
    assert status.past_plans[0].description == "Workout 1"


def test_get_athlete_status_with_upcoming_plans(db_connection):
    """Test status with upcoming plans (any status)."""
    today = date.today()

    # Add some future plans
    for i in range(3):
        add_plan(
            db_connection,
            (today + timedelta(days=i + 1)).isoformat(),
            f"Future workout {i + 1}",
        )

    status = get_athlete_status(db_connection)

    assert len(status.upcoming_plans) == 3
    # Should be ordered by planned_at ASC (soonest first)
    assert status.upcoming_plans[0].description == "Future workout 1"


def test_get_athlete_status_includes_all_statuses(db_connection):
    """Test that status includes plans regardless of their status."""
    today = date.today()

    # Add past plans with different statuses
    plan1 = add_plan(db_connection, (today - timedelta(days=1)).isoformat(), "Completed")
    update_plan(db_connection, plan1.id, PlanUpdate(status="completed"))

    plan2 = add_plan(db_connection, (today - timedelta(days=2)).isoformat(), "Skipped")
    update_plan(db_connection, plan2.id, PlanUpdate(status="skipped"))

    plan3 = add_plan(db_connection, (today - timedelta(days=3)).isoformat(), "Pending")
    # Leave as pending (not updated)

    status = get_athlete_status(db_connection)

    # All 3 should be included regardless of status
    assert len(status.past_plans) == 3
    statuses = {p.status for p in status.past_plans}
    assert statuses == {"completed", "skipped", "pending"}


def test_get_athlete_status_with_memories(db_connection, mock_embedding, mock_settings):
    """Test status with memories."""
    # Add some memories
    for i in range(5):
        add_memory(db_connection, mock_settings, "user", f"Memory {i + 1}")

    status = get_athlete_status(db_connection)

    assert len(status.recent_memories) == 5
    # Should be ordered by id DESC (most recent first)
    assert status.recent_memories[0].content == "Memory 5"


def test_get_athlete_status_limits(db_connection, mock_embedding, mock_settings):
    """Test that status respects limits."""
    today = date.today()

    # Add more than the limits for past plans
    for i in range(10):
        add_plan(
            db_connection,
            (today - timedelta(days=i + 1)).isoformat(),
            f"Past {i + 1}",
        )

    # Add more than the limits for upcoming plans
    for i in range(10):
        add_plan(
            db_connection,
            (today + timedelta(days=i + 1)).isoformat(),
            f"Future {i + 1}",
        )

    # Add more than the limits for memories
    for i in range(30):
        add_memory(db_connection, mock_settings, "user", f"Memory {i + 1}")

    status = get_athlete_status(db_connection)

    # Should respect limits: 5 past, 5 upcoming, 20 memories
    assert len(status.past_plans) == 5
    assert len(status.upcoming_plans) == 5
    assert len(status.recent_memories) == 20
