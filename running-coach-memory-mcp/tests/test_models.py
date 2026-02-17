"""Tests for Pydantic model datetime serialization (RFC 3339 compliance)."""

import json
import re
from datetime import datetime, timezone

import pytest

from memory_mcp.models import AthleteStatus, Memory, Plan

RFC3339_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$")


def is_rfc3339(value: str) -> bool:
    return RFC3339_PATTERN.match(value) is not None


class TestPlanDatetimeSerialization:
    """Plan.created_at must always serialize as RFC 3339 (with timezone)."""

    def test_naive_datetime_string(self):
        plan = Plan(
            id=1,
            created_at="2026-02-06T19:19:07",
            planned_at="2026-02-17",
            description="Rodaje 8km",
            status="pending",
        )
        data = json.loads(plan.model_dump_json())
        assert is_rfc3339(data["created_at"]), f"Not RFC 3339: {data['created_at']}"

    def test_utc_datetime_string(self):
        plan = Plan(
            id=2,
            created_at="2026-01-30T01:26:29Z",
            planned_at="2026-02-17",
            description="Series 4x1000m",
            status="completed",
        )
        data = json.loads(plan.model_dump_json())
        assert is_rfc3339(data["created_at"]), f"Not RFC 3339: {data['created_at']}"

    def test_offset_datetime_string(self):
        plan = Plan(
            id=3,
            created_at="2026-02-06T20:19:07+01:00",
            planned_at="2026-02-17",
            description="Fartlek",
            status="pending",
        )
        data = json.loads(plan.model_dump_json())
        assert is_rfc3339(data["created_at"]), f"Not RFC 3339: {data['created_at']}"

    def test_naive_datetime_object(self):
        plan = Plan(
            id=4,
            created_at=datetime(2026, 2, 6, 19, 19, 7),
            planned_at="2026-02-17",
            description="Rodaje",
            status="pending",
        )
        assert plan.created_at.tzinfo is not None

    def test_aware_datetime_object_preserved(self):
        plan = Plan(
            id=5,
            created_at=datetime(2026, 1, 30, 1, 26, 29, tzinfo=timezone.utc),
            planned_at="2026-02-17",
            description="Rodaje",
            status="pending",
        )
        assert plan.created_at.tzinfo is not None


class TestMemoryDatetimeSerialization:
    """Memory.created_at must always serialize as RFC 3339 (with timezone)."""

    def test_naive_datetime_string(self):
        memory = Memory(
            id=1,
            created_at="2026-02-06T19:19:07",
            author="agent",
            content="Test insight",
        )
        data = json.loads(memory.model_dump_json())
        assert is_rfc3339(data["created_at"]), f"Not RFC 3339: {data['created_at']}"

    def test_utc_datetime_string(self):
        memory = Memory(
            id=2,
            created_at="2026-01-30T01:05:31Z",
            author="user",
            content="Prefiero correr por la mañana",
        )
        data = json.loads(memory.model_dump_json())
        assert is_rfc3339(data["created_at"]), f"Not RFC 3339: {data['created_at']}"


class TestAthleteStatusSerialization:
    """AthleteStatus with mixed naive/aware datetimes must serialize as valid RFC 3339."""

    def test_mixed_datetimes(self):
        status = AthleteStatus(
            past_plans=[
                Plan(id=1, created_at="2026-01-30T01:26:29Z", planned_at="2026-02-15", description="P1", status="completed"),
                Plan(id=2, created_at="2026-02-06T19:19:07", planned_at="2026-02-16", description="P2", status="pending"),
            ],
            upcoming_plans=[
                Plan(id=3, created_at="2026-02-06T19:19:11", planned_at="2026-02-18", description="P3", status="pending"),
            ],
            recent_memories=[
                Memory(id=1, created_at="2026-02-06T19:19:07", author="agent", content="M1"),
                Memory(id=2, created_at="2026-01-30T01:05:31Z", author="user", content="M2"),
            ],
        )

        data = json.loads(status.model_dump_json())

        for plan in data["past_plans"] + data["upcoming_plans"]:
            assert is_rfc3339(plan["created_at"]), f"Plan not RFC 3339: {plan['created_at']}"

        for mem in data["recent_memories"]:
            assert is_rfc3339(mem["created_at"]), f"Memory not RFC 3339: {mem['created_at']}"


class TestDatabaseRoundtrip:
    """Datetimes from SQLite (both with and without Z) must roundtrip correctly."""

    def test_plan_from_sqlite_naive(self, db_connection):
        db_connection.execute(
            "INSERT INTO plan (created_at, planned_at, description) VALUES (?, ?, ?)",
            ("2026-02-06T19:19:07", "2026-02-17", "Test workout"),
        )
        db_connection.commit()

        row = db_connection.execute("SELECT * FROM plan WHERE id = 1").fetchone()
        plan = Plan(
            id=row["id"],
            created_at=row["created_at"],
            planned_at=row["planned_at"],
            description=row["description"],
            status=row["status"],
            notes=row["notes"],
            activity_id=row["activity_id"],
        )

        data = json.loads(plan.model_dump_json())
        assert is_rfc3339(data["created_at"])

    def test_plan_from_sqlite_default(self, db_connection):
        """Plans created via DEFAULT (strftime with Z) should also work."""
        db_connection.execute(
            "INSERT INTO plan (planned_at, description) VALUES (?, ?)",
            ("2026-02-17", "Default timestamp workout"),
        )
        db_connection.commit()

        row = db_connection.execute("SELECT * FROM plan WHERE id = 1").fetchone()
        plan = Plan(
            id=row["id"],
            created_at=row["created_at"],
            planned_at=row["planned_at"],
            description=row["description"],
            status=row["status"],
            notes=row["notes"],
            activity_id=row["activity_id"],
        )

        data = json.loads(plan.model_dump_json())
        assert is_rfc3339(data["created_at"])

    def test_memory_from_sqlite_naive(self, db_connection):
        db_connection.execute(
            "INSERT INTO memory (created_at, author, content) VALUES (?, ?, ?)",
            ("2026-02-06T19:19:07", "agent", "Naive timestamp memory"),
        )
        db_connection.commit()

        row = db_connection.execute("SELECT * FROM memory WHERE id = 1").fetchone()
        memory = Memory(
            id=row["id"],
            created_at=row["created_at"],
            author=row["author"],
            content=row["content"],
        )

        data = json.loads(memory.model_dump_json())
        assert is_rfc3339(data["created_at"])
