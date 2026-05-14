"""SQLite connection and schema management."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from benkyo.paths import ensure_parent_dir

SCHEMA = """
CREATE TABLE IF NOT EXISTS concept_nodes (
    id TEXT PRIMARY KEY,
    name TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS problem_nodes (
    id TEXT PRIMARY KEY,
    name TEXT,
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
    treatment TEXT NOT NULL CHECK (treatment IN ('blackbox', 'whitebox')),
    reference_content TEXT,
    set_by TEXT NOT NULL DEFAULT 'learner'
        CHECK (set_by IN ('system', 'learner', 'material')),
    set_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, concept_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concept_nodes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    project_id TEXT,
    kind TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    notes TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_edges_from ON edges(from_id);
CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_project_concepts_concept ON project_concepts(concept_id);
CREATE INDEX IF NOT EXISTS idx_project_goals_problem ON project_goals(problem_id);
CREATE INDEX IF NOT EXISTS idx_events_project_kind ON events(project_id, kind);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);

CREATE TABLE IF NOT EXISTS id_counters (
    prefix TEXT PRIMARY KEY,
    last_value INTEGER NOT NULL DEFAULT 0
);
"""


def _extract_name(content: str) -> str:
    """Extract short display name from content using 'Name: definition' convention."""
    colon_pos = content.find(":")
    if colon_pos > 0:
        candidate = content[:colon_pos].strip()
        if candidate:
            return candidate
    return content[:30].strip()


def _migrate_v02_to_v03(conn: sqlite3.Connection) -> None:
    """v0.2 → v0.3: rename treatment values procedural→blackbox, conceptual→whitebox.

    Auto-detects an old `project_concepts` table by inspecting sqlite_master for
    the old CHECK constraint, and rebuilds it with the new values + new CHECK.
    Idempotent: a v0.3+ DB is left untouched.
    """
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='project_concepts'"
    ).fetchone()
    if row is None:
        return  # fresh DB; SCHEMA will create the new table directly
    sql = row[0] or ""
    if "'procedural'" not in sql and "'conceptual'" not in sql:
        return  # already on the new naming

    conn.execute("BEGIN")
    try:
        conn.execute(
            """
            CREATE TABLE project_concepts_v03 (
                project_id TEXT NOT NULL,
                concept_id TEXT NOT NULL,
                treatment TEXT NOT NULL CHECK (treatment IN ('blackbox', 'whitebox')),
                reference_content TEXT,
                set_by TEXT NOT NULL DEFAULT 'learner'
                    CHECK (set_by IN ('system', 'learner', 'material')),
                set_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (project_id, concept_id),
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id) REFERENCES concept_nodes(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            INSERT INTO project_concepts_v03
                (project_id, concept_id, treatment, reference_content, set_by, set_at)
            SELECT
                project_id,
                concept_id,
                CASE treatment
                    WHEN 'procedural' THEN 'blackbox'
                    WHEN 'conceptual' THEN 'whitebox'
                    ELSE treatment
                END,
                reference_content, set_by, set_at
            FROM project_concepts
            """
        )
        conn.execute("DROP TABLE project_concepts")
        conn.execute("ALTER TABLE project_concepts_v03 RENAME TO project_concepts")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_project_concepts_concept "
            "ON project_concepts(concept_id)"
        )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def _migrate_v03_to_v04(conn: sqlite3.Connection) -> None:
    """v0.3 → v0.4: add name column to concept_nodes.

    Populates name from content using the 'Name: definition' convention.
    Idempotent: checks PRAGMA table_info before acting.
    """
    columns = [
        row[1]
        for row in conn.execute("PRAGMA table_info(concept_nodes)").fetchall()
    ]
    if not columns or "name" in columns:
        return

    conn.execute("BEGIN")
    try:
        conn.execute("ALTER TABLE concept_nodes ADD COLUMN name TEXT")
        rows = conn.execute("SELECT id, content FROM concept_nodes").fetchall()
        for row in rows:
            name = _extract_name(row["content"])
            conn.execute(
                "UPDATE concept_nodes SET name = ? WHERE id = ?", (name, row["id"])
            )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def _migrate_add_problem_name(conn: sqlite3.Connection) -> None:
    """Add name column to problem_nodes (v0.4.2+). No auto-backfill — name is set explicitly."""
    columns = [
        row[1]
        for row in conn.execute("PRAGMA table_info(problem_nodes)").fetchall()
    ]
    if not columns or "name" in columns:
        return

    conn.execute("BEGIN")
    try:
        conn.execute("ALTER TABLE problem_nodes ADD COLUMN name TEXT")
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def connect(db_path: Path) -> sqlite3.Connection:
    """Open a DB connection. Enables FK enforcement and initializes the schema.

    Auto-runs migrations transparently. All migrations are idempotent.
    """
    ensure_parent_dir(db_path)
    conn = sqlite3.connect(db_path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    _migrate_v02_to_v03(conn)
    _migrate_v03_to_v04(conn)
    _migrate_add_problem_name(conn)
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
