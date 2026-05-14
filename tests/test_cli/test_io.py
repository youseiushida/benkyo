"""export / import CLI のテスト."""

import json

from tests.test_cli.conftest import parse_ok


def test_export_import_graph_roundtrip(invoke, tmp_path):
    # データを作る
    invoke("concept", "add", "--content", "A")
    invoke("concept", "add", "--content", "B")
    invoke("edge", "add", "--from", "c1", "--to", "c2", "--type", "prereq")

    # export
    out = tmp_path / "graph.json"
    invoke("export", "graph", "--output", str(out))
    assert out.exists()

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["format"] == "benkyo/graph/v1"
    assert len(payload["concept_nodes"]) == 2
    assert len(payload["edges"]) == 1


def test_import_graph_into_fresh_db(invoke, tmp_path, monkeypatch):
    # 最初の DB にデータを作る
    invoke("concept", "add", "--content", "A")
    invoke("concept", "add", "--content", "B")

    out = tmp_path / "graph.json"
    invoke("export", "graph", "--output", str(out))

    # 別の DB に切り替え
    fresh_db = tmp_path / "fresh.db"
    monkeypatch.setenv("BENKYO_DB", str(fresh_db))

    # import
    result = invoke("import", "graph", str(out))
    data = parse_ok(result)
    assert data["concept_nodes"]["inserted"] == 2


def test_import_graph_on_conflict_skip(invoke, tmp_path):
    invoke("concept", "add", "--content", "A")
    out = tmp_path / "g.json"
    invoke("export", "graph", "--output", str(out))

    # 同じ DB に同じ ID で import → skip
    result = invoke("import", "graph", str(out), "--on-conflict", "skip")
    data = parse_ok(result)
    assert data["concept_nodes"]["skipped"] == 1


def test_export_import_project_roundtrip(invoke, tmp_path):
    invoke("problem", "add", "--statement", "Q", "--answer", "A")
    invoke("concept", "add", "--content", "C")
    invoke("project", "create", "--metadata", "P", "--goals", "p1")
    invoke(
        "treatment", "set",
        "--project", "prj1", "--concept", "c1",
        "--treatment", "blackbox",
        "--reference", "公式",
    )

    out = tmp_path / "proj.json"
    invoke("export", "project", "prj1", "--output", str(out))

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["format"] == "benkyo/project/v1"
    assert payload["project"]["id"] == "prj1"
    assert len(payload["treatments"]) == 1
