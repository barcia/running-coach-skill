-- Running Coach Memory MCP - Database Schema
-- Memory and Training Plan management

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

-- memory: Central memory with vector search
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    author TEXT NOT NULL CHECK (author IN ('user', 'agent', 'system')),
    content TEXT NOT NULL
);

-- memory_vec: Virtual table for vector search (sqlite-vec)
-- Created programmatically in database.py because it requires the extension loaded.
-- Structure: CREATE VIRTUAL TABLE memory_vec USING vec0(embedding float[dimensions])
-- The rowid of memory_vec corresponds to the id in memory.

-- Índices
CREATE INDEX IF NOT EXISTS idx_plan_planned_at ON plan(planned_at);
CREATE INDEX IF NOT EXISTS idx_plan_status ON plan(status);
CREATE INDEX IF NOT EXISTS idx_memory_author ON memory(author);
