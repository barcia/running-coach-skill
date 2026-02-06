"""Pydantic models for Running Coach Memory MCP."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def validate_date_format(value: str) -> str:
    """Validate date is in YYYY-MM-DD format and is a valid date."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format and be a valid date")
    return value


# Memory Models
class MemoryBase(BaseModel):
    """Base memory model."""

    author: Literal["user", "agent", "system"]
    content: str


class MemoryCreate(MemoryBase):
    """Model for creating a memory."""

    pass


class Memory(MemoryBase):
    """Memory with database fields."""

    id: int
    created_at: datetime


class MemorySearchResult(Memory):
    """Memory with similarity score."""

    distance: float


# Plan Models
class PlanBase(BaseModel):
    """Base plan model."""

    planned_at: str = Field(description="Date YYYY-MM-DD")
    description: str = Field(description="The workout: clear, concise and direct")
    notes: str | None = Field(default=None, description="The why: explanation, context or justification")

    @field_validator("planned_at")
    @classmethod
    def validate_planned_at(cls, v: str) -> str:
        return validate_date_format(v)


class PlanCreate(PlanBase):
    """Model for creating a plan."""

    pass


class PlanUpdate(BaseModel):
    """Model for updating a plan."""

    planned_at: str | None = None
    description: str | None = None
    notes: str | None = None
    status: Literal["pending", "completed", "skipped", "cancelled"] | None = None
    activity_id: str | None = None

    @field_validator("planned_at")
    @classmethod
    def validate_planned_at(cls, v: str | None) -> str | None:
        if v is not None:
            return validate_date_format(v)
        return v


class Plan(PlanBase):
    """Plan with database fields."""

    id: int
    created_at: datetime
    status: str
    activity_id: str | None = None


# Status Models
class AthleteStatus(BaseModel):
    """Aggregated athlete status."""

    past_plans: list[Plan] = Field(default_factory=list)
    upcoming_plans: list[Plan] = Field(default_factory=list)
    recent_memories: list[Memory] = Field(default_factory=list)
