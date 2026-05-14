"""Migration tests: v0.2 → v0.3 (treatment rename) and v0.3 → v0.4 (name column)."""

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

    def test_v02_gets_name_column_too(self, tmp_path):
        """v0.2 DBs also get the name column via chained migrations."""
        path = tmp_path / "v02_name.db"
        c = _make_v02_db(path)
        c.execute("INSERT INTO concept_nodes (id, content) VALUES ('c1', '凸関数: f は凸')")
        c.close()

        conn = connect(path)
        try:
            row = conn.execute(
                "SELECT name FROM concept_nodes WHERE id = 'c1'"
            ).fetchone()
            assert row["name"] == "凸関数"
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


def _make_v03_db(path):
    """Create a DB pinned to the v0.3 schema (no name column in concept_nodes)."""
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE concept_nodes (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE problem_nodes (
            id TEXT PRIMARY KEY,
            statement TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE edges (
            from_id TEXT NOT NULL, to_id TEXT NOT NULL,
            edge_type TEXT NOT NULL CHECK (edge_type IN ('prereq', 'related')),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (from_id, to_id, edge_type)
        );
        CREATE TABLE projects (id TEXT PRIMARY KEY, metadata TEXT NOT NULL DEFAULT '', created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE project_goals (project_id TEXT NOT NULL, problem_id TEXT NOT NULL, PRIMARY KEY (project_id, problem_id));
        CREATE TABLE project_concepts (
            project_id TEXT NOT NULL, concept_id TEXT NOT NULL,
            treatment TEXT NOT NULL CHECK (treatment IN ('blackbox', 'whitebox')),
            reference_content TEXT, set_by TEXT NOT NULL DEFAULT 'learner'
                CHECK (set_by IN ('system', 'learner', 'material')),
            set_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (project_id, concept_id)
        );
        CREATE TABLE events (
            id TEXT PRIMARY KEY, ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            project_id TEXT, kind TEXT NOT NULL,
            payload_json TEXT NOT NULL DEFAULT '{}', notes TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE id_counters (prefix TEXT PRIMARY KEY, last_value INTEGER NOT NULL DEFAULT 0);
        """
    )
    return conn


class TestMigrationV03ToV04:
    def test_name_column_added_and_populated(self, tmp_path):
        """v0.3 DBs get a name column on connect(); populated from content."""
        path = tmp_path / "v03.db"
        c = _make_v03_db(path)
        c.execute(
            "INSERT INTO concept_nodes (id, content) VALUES ('c1', '凸関数: f: C→ℝ は凸')"
        )
        c.execute(
            "INSERT INTO concept_nodes (id, content) VALUES ('c2', 'no colon content here')"
        )
        c.close()

        conn = connect(path)
        try:
            rows = conn.execute(
                "SELECT id, name FROM concept_nodes ORDER BY id"
            ).fetchall()
            names = {r["id"]: r["name"] for r in rows}
            assert names["c1"] == "凸関数"
            assert names["c2"] == "no colon content here"
        finally:
            conn.close()

    def test_idempotent_on_v04_db(self, tmp_path):
        """Re-opening a v0.4 DB does not crash or alter data."""
        path = tmp_path / "v04.db"
        conn = connect(path)
        conn.execute(
            "INSERT INTO concept_nodes (id, name, content) VALUES ('c1', 'A', 'A: content')"
        )
        conn.close()

        conn = connect(path)
        try:
            row = conn.execute(
                "SELECT name FROM concept_nodes WHERE id = 'c1'"
            ).fetchone()
            assert row["name"] == "A"
        finally:
            conn.close()

    def test_fresh_db_has_name_column(self, tmp_path):
        """Fresh v0.4 DBs have the name column from SCHEMA."""
        path = tmp_path / "fresh_v04.db"
        conn = connect(path)
        try:
            columns = [
                row[1]
                for row in conn.execute("PRAGMA table_info(concept_nodes)").fetchall()
            ]
            assert "name" in columns
        finally:
            conn.close()
