"""SQLite connection and schema management."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from benkyo.paths import ensure_parent_dir

SCHEMA = """
CREATE TABLE IF NOT EXISTS concept_nodes (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS problem_nodes (
    id TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS edges (
    from_id TEXT NOT NULL,
    to_id TEXT NOT NULL,
    edge_type TEXT NOT NULL CHECK (edge_type IN ('prereq', 'related')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (from_id, to_id, edge_type)
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    metadata TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_goals (
    project_id TEXT NOT NULL,
    problem_id TEXT NOT NULL,
    PRIMARY KEY (project_id, problem_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES problem_nodes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS project_concepts (
    project_id TEXT NOT NULL,
    concept_id TEXT NOT NULL,
    treatment TEXT NOT NULL CHECK (treatment IN ('procedural', 'conceptual')),
    reference_content TEXT,
    set_by TEXT NOT NULL DEFAULT 'learner'
        CHECK (set_by IN ('system', 'learner', 'material')),
    set_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, concept_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concept_nodes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_edges_from ON edges(from_id);
CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_project_concepts_concept ON project_concepts(concept_id);
CREATE INDEX IF NOT EXISTS idx_project_goals_problem ON project_goals(problem_id);

CREATE TABLE IF NOT EXISTS id_counters (
    prefix TEXT PRIMARY KEY,
    last_value INTEGER NOT NULL DEFAULT 0
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    """Open a DB connection. Enables FK enforcement and initializes the schema."""
    ensure_parent_dir(db_path)
    conn = sqlite3.connect(db_path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.executescript(SCHEMA)
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[None]:
    """Multi-statement atomic block. Works with autocommit mode."""
    conn.execute("BEGIN")
    try:
        yield
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
