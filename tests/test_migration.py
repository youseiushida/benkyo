"""v0.2 → v0.3 migration: treatment value rename auto-runs on connect()."""

import sqlite3

from benkyo.db import connect


def _make_v02_db(path):
    """Create a DB pinned to the v0.2 schema (old CHECK constraint)."""
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(
        """
        CREATE TABLE concept_nodes (id TEXT PRIMARY KEY, content TEXT NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE problem_nodes (id TEXT PRIMARY KEY, statement TEXT NOT NULL, answer TEXT NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE edges (from_id TEXT, to_id TEXT, edge_type TEXT NOT NULL CHECK (edge_type IN ('prereq', 'related')), created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (from_id, to_id, edge_type));
        CREATE TABLE projects (id TEXT PRIMARY KEY, metadata TEXT NOT NULL DEFAULT '', created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE project_goals (project_id TEXT, problem_id TEXT, PRIMARY KEY (project_id, problem_id), FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE, FOREIGN KEY (problem_id) REFERENCES problem_nodes(id) ON DELETE CASCADE);
        CREATE TABLE project_concepts (
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
        CREATE TABLE id_counters (prefix TEXT PRIMARY KEY, last_value INTEGER NOT NULL DEFAULT 0);
        """
    )
    return conn


class TestMigration:
    def test_v02_db_with_old_values_migrates(self, tmp_path):
        path = tmp_path / "v02.db"
        c = _make_v02_db(path)
        c.execute("INSERT INTO concept_nodes (id, content) VALUES ('c1', 'A')")
        c.execute("INSERT INTO concept_nodes (id, content) VALUES ('c2', 'B')")
        c.execute("INSERT INTO problem_nodes (id, statement, answer) VALUES ('p1', 'Q', 'A')")
        c.execute("INSERT INTO projects (id, metadata) VALUES ('prj1', 'm')")
        c.execute(
            "INSERT INTO project_concepts (project_id, concept_id, treatment) "
            "VALUES ('prj1', 'c1', 'procedural')"
        )
        c.execute(
            "INSERT INTO project_concepts (project_id, concept_id, treatment) "
            "VALUES ('prj1', 'c2', 'conceptual')"
        )
        c.close()

        # Re-open with v0.3 connect() → triggers migration
        conn = connect(path)
        try:
            rows = conn.execute(
                "SELECT concept_id, treatment FROM project_concepts ORDER BY concept_id"
            ).fetchall()
            treatments = {r["concept_id"]: r["treatment"] for r in rows}
            assert treatments == {"c1": "blackbox", "c2": "whitebox"}

            # New CHECK constraint is in place
            schema = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='project_concepts'"
            ).fetchone()[0]
            assert "'blackbox'" in schema and "'whitebox'" in schema
            assert "'procedural'" not in schema and "'conceptual'" not in schema
        finally:
            conn.close()

    def test_fresh_db_no_migration_noise(self, tmp_path):
        path = tmp_path / "fresh.db"
        conn = connect(path)
        try:
            # Brand-new DB should accept new values normally
            conn.execute("INSERT INTO concept_nodes (id, content) VALUES ('c1', 'X')")
            conn.execute("INSERT INTO projects (id, metadata) VALUES ('prj1', 'm')")
            conn.execute(
                "INSERT INTO project_concepts (project_id, concept_id, treatment) "
                "VALUES ('prj1', 'c1', 'whitebox')"
            )
        finally:
            conn.close()

    def test_idempotent_reconnect(self, tmp_path):
        path = tmp_path / "idem.db"
        c = _make_v02_db(path)
        c.execute("INSERT INTO concept_nodes (id, content) VALUES ('c1', 'A')")
        c.execute("INSERT INTO projects (id, metadata) VALUES ('prj1', 'm')")
        c.execute(
            "INSERT INTO project_concepts (project_id, concept_id, treatment) "
            "VALUES ('prj1', 'c1', 'procedural')"
        )
        c.close()

        # 1st open: migrates
        conn = connect(path)
        conn.close()
        # 2nd open: no-op
        conn = connect(path)
        try:
            t = conn.execute(
                "SELECT treatment FROM project_concepts WHERE concept_id = 'c1'"
            ).fetchone()["treatment"]
            assert t == "blackbox"
        finally:
            conn.close()
