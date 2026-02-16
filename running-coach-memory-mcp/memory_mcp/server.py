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
from memory_mcp.tools import memory_md as memory_md_tools
from memory_mcp.tools import plan as plan_tools
from memory_mcp.tools import status as status_tools

# Initialize settings, logging, and database
settings = get_settings()
setup_logging(settings)
init_database(settings)

# Create FastMCP server
mcp = FastMCP(
    "RunningCoachMemory",
    instructions=(
        "Persistent memory and training plan management for an AI running coach. "
        "Two data domains: Plans (scheduled workouts with status lifecycle: pending → completed/skipped/cancelled) "
        "and Memory (semantic long-term storage of coaching insights, athlete observations, and decisions). "
        "Start every session with get_athlete_status(). Use search_memories() before asking the athlete "
        "something you might already know."
    ),
)


# =============================================================================
# Status Tool
# =============================================================================


@mcp.tool()
def get_athlete_status() -> AthleteStatus:
    """Get a snapshot of the athlete's current training situation.

    Use at the START of every coaching session to load context.
    Returns: last 5 past plans, next 5 upcoming plans, and 20 most recent memories.
    This single call replaces multiple queries when you need a quick overview.
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
    """Store a coaching insight, observation, or decision for long-term recall.

    Memories are facts worth remembering across sessions: athlete tendencies,
    injury history, training decisions, or relevant life events.
    An embedding is generated automatically to enable semantic search later.

    Args:
        author: "user" = something the athlete said, "agent" = your observation or decision, "system" = automated log
        content: The insight to remember — be specific and include date context when relevant
    """
    conn = get_connection(settings)
    try:
        return memory_tools.add_memory(conn, settings, author, content)
    finally:
        conn.close()


@mcp.tool()
def get_memory(memory_id: int) -> Memory | None:
    """Retrieve a single memory by its ID.

    Use when you already have a memory ID (e.g., from search results or list)
    and need the full record.

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
    """List memories in reverse chronological order (newest first).

    Use for browsing recent activity or auditing memories by author.
    For finding memories by topic, prefer search_memories() which uses semantic similarity.

    Args:
        author: Filter by author — "user", "agent", or "system". Omit for all.
        limit: Maximum number of memories to return (default 50)
    """
    conn = get_connection(settings)
    try:
        return memory_tools.list_memories(conn, author, limit)
    finally:
        conn.close()


@mcp.tool()
def search_memories(query: str, limit: int = 10) -> list[MemorySearchResult]:
    """Find memories by meaning using semantic vector search.

    This is the PRIMARY way to retrieve memories — use natural language queries
    (e.g., "knee injury history", "preferred long run day"). Results are ranked
    by similarity (lower distance = better match). Always search before asking
    the athlete something you might already know.

    Args:
        query: Natural language description of what you're looking for
        limit: Maximum number of results to return (default 10)
    """
    conn = get_connection(settings)
    try:
        return memory_tools.search_memories(conn, settings, query, limit)
    finally:
        conn.close()


@mcp.tool()
def delete_memory(memory_id: int) -> bool:
    """Permanently delete a memory and its embedding.

    This is irreversible — the memory and its vector embedding are both removed.
    Use only for incorrect or outdated information that should not appear in future searches.

    Args:
        memory_id: The ID of the memory to delete
    """
    conn = get_connection(settings)
    try:
        return memory_tools.delete_memory(conn, memory_id)
    finally:
        conn.close()


# =============================================================================
# Memory MD Tools
# =============================================================================


@mcp.tool()
def get_memory_md() -> str:
    """Get the full MEMORY.md content from the database.

    MEMORY.md is the athlete's persistent profile document — a structured
    markdown file containing biographical data, training philosophy, goals,
    injury history, and other long-term reference information.
    """
    conn = get_connection(settings)
    try:
        return memory_md_tools.get_memory_md(conn)
    finally:
        conn.close()


@mcp.tool()
def update_memory_md(content: str) -> str:
    """Replace the full MEMORY.md content in the database.

    Use when the athlete's profile needs updating — new goals, revised PRs,
    injury updates, or any structural change to the document.
    Always get_memory_md() first, modify the content, then update.

    Args:
        content: The complete new MEMORY.md content (replaces existing)
    """
    conn = get_connection(settings)
    try:
        return memory_md_tools.update_memory_md(conn, content)
    finally:
        conn.close()


# =============================================================================
# Plan Tools
# =============================================================================


@mcp.tool()
def add_plan(planned_at: str, description: str, notes: str | None = None) -> Plan:
    """Schedule a training session. Created with status "pending".

    Each plan represents one workout on a specific date. Use when building
    weekly plans, mesocycles, or scheduling individual sessions.

    Args:
        planned_at: Target date in YYYY-MM-DD format
        description: WHAT to do — the workout itself (e.g., "10km easy @ 5:30/km" or "6x1000m @ 4:15 r:2min")
        notes: WHY this workout — training rationale, phase context, or adaptation goal (optional)
    """
    conn = get_connection(settings)
    try:
        return plan_tools.add_plan(conn, planned_at, description, notes)
    finally:
        conn.close()


@mcp.tool()
def get_plan(plan_id: int) -> Plan | None:
    """Retrieve a single plan by its ID.

    Use when you have a plan ID and need the full record (e.g., to review
    before updating status or to check details).

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
    """Query plans with optional date range and status filters. Ordered by date ascending.

    Use for reviewing training blocks, checking compliance (e.g., all "skipped" plans
    in the last month), or finding plans for a specific date range.

    Args:
        start_date: Include plans from this date onwards (YYYY-MM-DD)
        end_date: Include plans up to this date (YYYY-MM-DD)
        status: Filter by status — "pending", "completed", "skipped", or "cancelled"
        limit: Maximum number of plans to return (default 50)
    """
    conn = get_connection(settings)
    try:
        return plan_tools.list_plans(conn, start_date, end_date, status, limit)
    finally:
        conn.close()


@mcp.tool()
def get_today_plan() -> list[Plan]:
    """Get all plans scheduled for today, regardless of status.

    Use when the athlete asks "what's my workout today?" or when giving
    post-workout feedback to find the planned session for comparison.
    """
    conn = get_connection(settings)
    try:
        return plan_tools.get_today_plan(conn)
    finally:
        conn.close()


@mcp.tool()
def get_upcoming_plans(days: int = 7) -> list[Plan]:
    """Get plans from today through the next N days.

    Use to preview the upcoming training load, check what's scheduled
    for the week, or review the short-term plan with the athlete.

    Args:
        days: Number of days to look ahead from today (default 7)
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
    """Update a plan's fields. Key tool for closing the training feedback loop.

    Status lifecycle: pending → completed | skipped | cancelled.
    After a workout, mark "completed" and link the Garmin activity_id.
    Mark "skipped" if the athlete didn't do it (record why in notes).
    Mark "cancelled" if the session is removed from the plan entirely.
    Only pass the fields you want to change — others remain unchanged.

    Args:
        plan_id: The ID of the plan to update
        planned_at: Reschedule to a new date (YYYY-MM-DD)
        description: Updated workout description
        notes: Updated rationale or post-workout observations
        status: New status — "pending", "completed", "skipped", or "cancelled"
        activity_id: Garmin activity ID to link (set when marking completed)
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
    """Permanently delete a plan record.

    This hard-deletes the plan from the database. To keep a record that a session
    was intentionally removed, prefer update_plan(status="cancelled") instead.
    Use delete only for plans created by mistake.

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
    """Run the MCP server.

    Transport is controlled by MCP_TRANSPORT env var:
      - "stdio" (default): for local use via Claude Desktop
      - "streamable-http": for remote use via HTTP (e.g., from a VPS)

    When using streamable-http, also configure MCP_HOST and MCP_PORT.
    """
    mcp.run(
        transport=settings.mcp_transport,
        host=settings.mcp_host,
        port=settings.mcp_port,
    )


if __name__ == "__main__":
    main()
