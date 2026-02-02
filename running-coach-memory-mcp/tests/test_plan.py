"""Tests for plan tools."""

from datetime import date

from memory_mcp.models import PlanUpdate
from memory_mcp.tools.plan import (
    add_plan,
    delete_plan,
    get_plan,
    get_today_plan,
    get_upcoming_plans,
    list_plans,
    update_plan,
)


def test_add_plan(db_connection):
    """Test adding a plan."""
    plan = add_plan(db_connection, "2025-01-30", "Rodaje 45' Z2")

    assert plan.id == 1
    assert plan.planned_at == "2025-01-30"
    assert plan.description == "Rodaje 45' Z2"
    assert plan.status == "pending"


def test_get_plan(db_connection):
    """Test getting a plan by ID."""
    created = add_plan(db_connection, "2025-01-30", "Rodaje 45' Z2")
    plan = get_plan(db_connection, created.id)

    assert plan is not None
    assert plan.id == created.id
    assert plan.description == "Rodaje 45' Z2"


def test_get_plan_not_found(db_connection):
    """Test getting a non-existent plan."""
    plan = get_plan(db_connection, 999)
    assert plan is None


def test_list_plans(db_connection):
    """Test listing plans."""
    add_plan(db_connection, "2025-01-30", "Plan 1")
    add_plan(db_connection, "2025-01-31", "Plan 2")
    add_plan(db_connection, "2025-02-01", "Plan 3")

    plans = list_plans(db_connection)
    assert len(plans) == 3

    # Test date filter
    plans = list_plans(db_connection, start_date="2025-01-31")
    assert len(plans) == 2


def test_update_plan(db_connection):
    """Test updating a plan."""
    created = add_plan(db_connection, "2025-01-30", "Rodaje 45' Z2")

    updated = update_plan(
        db_connection,
        created.id,
        PlanUpdate(status="completed", activity_id="12345"),
    )

    assert updated is not None
    assert updated.status == "completed"
    assert updated.activity_id == "12345"


def test_delete_plan(db_connection):
    """Test deleting a plan."""
    created = add_plan(db_connection, "2025-01-30", "Rodaje 45' Z2")

    result = delete_plan(db_connection, created.id)
    assert result is True

    plan = get_plan(db_connection, created.id)
    assert plan is None


def test_get_today_plan(db_connection):
    """Test getting today's plans."""
    today = date.today().isoformat()
    add_plan(db_connection, today, "Today's workout")
    add_plan(db_connection, "2030-01-01", "Future workout")

    plans = get_today_plan(db_connection)
    assert len(plans) == 1
    assert plans[0].description == "Today's workout"


def test_get_upcoming_plans(db_connection):
    """Test getting upcoming plans."""
    today = date.today().isoformat()
    add_plan(db_connection, today, "Today's workout")
    add_plan(db_connection, "2020-01-01", "Past workout")

    plans = get_upcoming_plans(db_connection, days=7)
    assert len(plans) == 1
    assert plans[0].description == "Today's workout"
