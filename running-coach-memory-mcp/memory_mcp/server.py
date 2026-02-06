"""Running Coach Memory MCP Server - Entry point for FastMCP."""

from typing import Literal

from mcp.server.fastmcp import FastMCP

from memory_mcp.config import get_settings
from memory_mcp.database import get_connection, init_database
from memory_mcp.logging import setup_logging
from memory_mcp.models import (
    AthleteStatus,
    Memory,
    MemorySearchResult,
    Plan,
    PlanUpdate,
)
from memory_mcp.tools import memory as memory_tools
from memory_mcp.tools import plan as plan_tools
from memory_mcp.tools import status as status_tools

# Initialize settings, logging, and database
settings = get_settings()
setup_logging(settings)
init_database(settings)

# Create FastMCP server
mcp = FastMCP(
    "RunningCoachMemory",
    instructions="Memory and Training Plan MCP for an AI running coach agent. Provides persistent storage for training plans and semantic memory.",
)


# =============================================================================
# Status Tool
# =============================================================================


@mcp.tool()
def get_athlete_status() -> AthleteStatus:
    """Get aggregated athlete status.

    Returns a snapshot with past plans, upcoming plans,
    and recent memories. Use this to understand the athlete's
    current situation at a glance.
    """
    conn = get_connection(settings)
    try:
        return status_tools.get_athlete_status(conn)
    finally:
        conn.close()


# =============================================================================
# Memory Tools
# =============================================================================


@mcp.tool()
def add_memory(
    author: Literal["user", "agent", "system"],
    content: str,
) -> Memory:
    """Add a memory with automatic embedding generation.

    Args:
        author: Who created the memory (user, agent, or system)
        content: The memory content to store
    """
    conn = get_connection(settings)
    try:
        return memory_tools.add_memory(conn, settings, author, content)
    finally:
        conn.close()


@mcp.tool()
def get_memory(memory_id: int) -> Memory | None:
    """Get a memory by ID.

    Args:
        memory_id: The ID of the memory to retrieve
    """
    conn = get_connection(settings)
    try:
        return memory_tools.get_memory(conn, memory_id)
    finally:
        conn.close()


@mcp.tool()
def list_memories(
    author: Literal["user", "agent", "system"] | None = None,
    limit: int = 50,
) -> list[Memory]:
    """List memories with optional author filter.

    Args:
        author: Filter by author (user, agent, or system)
        limit: Maximum number of memories to return
    """
    conn = get_connection(settings)
    try:
        return memory_tools.list_memories(conn, author, limit)
    finally:
        conn.close()


@mcp.tool()
def search_memories(query: str, limit: int = 10) -> list[MemorySearchResult]:
    """Search memories by semantic similarity.

    Uses vector embeddings to find memories similar to the query.

    Args:
        query: The search query
        limit: Maximum number of results to return
    """
    conn = get_connection(settings)
    try:
        return memory_tools.search_memories(conn, settings, query, limit)
    finally:
        conn.close()


@mcp.tool()
def delete_memory(memory_id: int) -> bool:
    """Delete a memory and its embedding.

    Args:
        memory_id: The ID of the memory to delete
    """
    conn = get_connection(settings)
    try:
        return memory_tools.delete_memory(conn, memory_id)
    finally:
        conn.close()


# =============================================================================
# Plan Tools
# =============================================================================


@mcp.tool()
def add_plan(planned_at: str, description: str, notes: str | None = None) -> Plan:
    """Add a training plan entry.

    Args:
        planned_at: Date in YYYY-MM-DD format
        description: The workout (clear, concise and direct)
        notes: The why (explanation, context or justification)
    """
    conn = get_connection(settings)
    try:
        return plan_tools.add_plan(conn, planned_at, description, notes)
    finally:
        conn.close()


@mcp.tool()
def get_plan(plan_id: int) -> Plan | None:
    """Get a plan by ID.

    Args:
        plan_id: The ID of the plan to retrieve
    """
    conn = get_connection(settings)
    try:
        return plan_tools.get_plan(conn, plan_id)
    finally:
        conn.close()


@mcp.tool()
def list_plans(
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[Plan]:
    """List plans with optional filters.

    Args:
        start_date: Filter plans from this date (YYYY-MM-DD)
        end_date: Filter plans until this date (YYYY-MM-DD)
        status: Filter by status (pending, completed, skipped, cancelled)
        limit: Maximum number of plans to return
    """
    conn = get_connection(settings)
    try:
        return plan_tools.list_plans(conn, start_date, end_date, status, limit)
    finally:
        conn.close()


@mcp.tool()
def get_today_plan() -> list[Plan]:
    """Get plans scheduled for today."""
    conn = get_connection(settings)
    try:
        return plan_tools.get_today_plan(conn)
    finally:
        conn.close()


@mcp.tool()
def get_upcoming_plans(days: int = 7) -> list[Plan]:
    """Get plans for the next N days.

    Args:
        days: Number of days to look ahead
    """
    conn = get_connection(settings)
    try:
        return plan_tools.get_upcoming_plans(conn, days)
    finally:
        conn.close()


@mcp.tool()
def update_plan(
    plan_id: int,
    planned_at: str | None = None,
    description: str | None = None,
    notes: str | None = None,
    status: Literal["pending", "completed", "skipped", "cancelled"] | None = None,
    activity_id: str | None = None,
) -> Plan | None:
    """Update a plan.

    Args:
        plan_id: The ID of the plan to update
        planned_at: New date (YYYY-MM-DD)
        description: New workout description
        notes: New notes (explanation/context)
        status: New status
        activity_id: External activity ID (e.g., Garmin Activity ID)
    """
    conn = get_connection(settings)
    try:
        update = PlanUpdate(
            planned_at=planned_at,
            description=description,
            notes=notes,
            status=status,
            activity_id=activity_id,
        )
        return plan_tools.update_plan(conn, plan_id, update)
    finally:
        conn.close()


@mcp.tool()
def delete_plan(plan_id: int) -> bool:
    """Delete a plan.

    Args:
        plan_id: The ID of the plan to delete
    """
    conn = get_connection(settings)
    try:
        return plan_tools.delete_plan(conn, plan_id)
    finally:
        conn.close()


# =============================================================================
# Main Entry Point
# =============================================================================


def main():
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
