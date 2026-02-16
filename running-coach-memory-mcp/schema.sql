-- Running Coach Memory MCP - Database Schema
-- Memory and Training Plan management (Turso/libSQL)

-- plan: Bridge to external execution (links to external activity IDs)
CREATE TABLE IF NOT EXISTS plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    planned_at TEXT NOT NULL,       -- Date YYYY-MM-DD
    description TEXT NOT NULL,      -- The workout: clear, concise and direct
    notes TEXT,                     -- The why: explanation, context or justification
    status TEXT DEFAULT 'pending',  -- pending, completed, skipped, cancelled
    activity_id TEXT                -- External ID (e.g., Garmin Activity ID)
);

-- memory: Central memory with native libSQL vector search
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    author TEXT NOT NULL CHECK (author IN ('user', 'agent', 'system')),
    content TEXT NOT NULL,
    embedding F32_BLOB(3072)        -- Native libSQL vector column for semantic search
);

-- memory_md: Single-row table for MEMORY.md content
CREATE TABLE IF NOT EXISTS memory_md (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    content TEXT NOT NULL DEFAULT ''
);

-- Ensure memory_md always has its single row
INSERT OR IGNORE INTO memory_md (id, content) VALUES (1, '');

-- Indexes
CREATE INDEX IF NOT EXISTS idx_plan_planned_at ON plan(planned_at);
CREATE INDEX IF NOT EXISTS idx_plan_status ON plan(status);
CREATE INDEX IF NOT EXISTS idx_memory_author ON memory(author);
