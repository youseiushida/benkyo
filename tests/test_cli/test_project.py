"""project CLI のテスト."""

import json

from tests.test_cli.conftest import parse_ok


def test_create_with_goals(invoke):
    invoke("problem", "add", "--statement", "Q1", "--answer", "A1")
    invoke("problem", "add", "--statement", "Q2", "--answer", "A2")
    result = invoke(
        "project", "create",
        "--metadata", "テスト課題",
        "--goals", "p1,p2",
    )
    data = parse_ok(result)
    assert data["id"] == "prj1"
    assert set(data["goals"]) == {"p1", "p2"}


def test_update_goals(invoke):
    invoke("problem", "add", "--statement", "Q1", "--answer", "A1")
    invoke("problem", "add", "--statement", "Q2", "--answer", "A2")
    invoke("project", "create", "--metadata", "X", "--goals", "p1")
    result = invoke("project", "update", "prj1", "--goals", "p2")
    assert parse_ok(result)["goals"] == ["p2"]


def test_delete_cascades(invoke):
    invoke("problem", "add", "--statement", "Q", "--answer", "A")
    invoke("project", "create", "--metadata", "X", "--goals", "p1")
    result = invoke("project", "delete", "prj1")
    assert parse_ok(result)["cascade"]["project_goals"] == 1
