"""DB スキーマと接続のテスト."""


def test_all_tables_exist(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    tables = {r[0] for r in rows}
    expected = {
        "concept_nodes",
        "problem_nodes",
        "edges",
        "projects",
        "project_goals",
        "project_concepts",
        "id_counters",
    }
    assert expected.issubset(tables)


def test_foreign_keys_enabled(conn):
    row = conn.execute("PRAGMA foreign_keys").fetchone()
    assert row[0] == 1


def test_indexes_exist(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index'"
    ).fetchall()
    indexes = {r[0] for r in rows}
    expected = {
        "idx_edges_from",
        "idx_edges_to",
        "idx_edges_type",
        "idx_project_concepts_concept",
        "idx_project_goals_problem",
    }
    assert expected.issubset(indexes)
