# Running Coach Memory MCP

Memory and Training Plan MCP for an AI running coach agent.

> **Note**: This MCP does NOT store raw health metrics or biometric data. That data lives in external MCPs (e.g., Garmin). This system acts as the "brain" that manages training plans and long-term semantic memory.

## What It Stores

| Component | Purpose |
|-----------|---------|
| **Plans** | Training calendar with past and future workouts. Links to external activity/workout IDs. |
| **Memories** | Semantic memory with vector embeddings for intelligent retrieval across sessions. |

## Installation

```bash
# With uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Configuration

Create a `.env` file based on `.env.example`:

```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-xxxx

# Optional
DATABASE_PATH=~/.local/share/running-coach/memory.db
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | - | OpenRouter API key for embeddings |
| `DATABASE_PATH` | No | `~/.local/share/running-coach/memory.db` | SQLite database path |

The embedding model (`openai/text-embedding-3-large`, 3072 dimensions) is fixed in the code.

## Usage

### Run the Server

```bash
# With uv
uv run python -m memory_mcp.server

# Or directly
python -m memory_mcp.server
```

### Configure in Cursor/Claude

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "Running Coach Memory": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/running-coach-memory-mcp", "python", "-m", "memory_mcp.server"],
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-xxxx"
      }
    }
  }
}
```

### Verify with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run python -m memory_mcp.server
```

## Available Tools

### Status

| Tool | Parameters | Description |
|------|------------|-------------|
| `get_athlete_status` | - | Get a snapshot: last 5 past plans, next 5 upcoming plans, and last 20 memories. |

### Memory (Semantic Search)

| Tool | Parameters | Description |
|------|------------|-------------|
| `add_memory` | `author`, `content` | Add a memory with automatic embedding generation. |
| `search_memories` | `query`, `limit` | Semantic search. Find memories similar to the query using vectors. |
| `list_memories` | `author?`, `limit?` | List memories chronologically with optional author filter. |
| `get_memory` | `memory_id` | Get a specific memory by ID. |
| `delete_memory` | `memory_id` | Delete a memory and its embedding. |

### Plan (Training Schedule)

| Tool | Parameters | Description |
|------|------------|-------------|
| `add_plan` | `planned_at`, `description`, `notes?` | Schedule a workout. `description` is the what, `notes` is the why. |
| `get_plan` | `plan_id` | Get plan details by ID. |
| `list_plans` | `start_date?`, `end_date?`, `status?`, `limit?` | List plans with optional filters. |
| `get_today_plan` | - | Get today's scheduled workouts. |
| `get_upcoming_plans` | `days?` | Get workouts for the next N days (default: 7). |
| `update_plan` | `plan_id`, `planned_at?`, `description?`, `notes?`, `status?`, `activity_id?`, `workout_id?` | Update any plan field or link external IDs. |
| `delete_plan` | `plan_id` | Delete a plan entry. |

## Tech Stack

- **Python 3.12+**
- **FastMCP** - MCP server framework
- **sqlite-vec** - Vector search extension for SQLite
- **Pydantic** - Data validation
- **OpenAI client** - Embeddings via OpenRouter

## License

MIT
