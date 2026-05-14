"""traversal CLI のテスト."""

import json

from tests.test_cli.conftest import parse_ok


def _setup(invoke):
    invoke("problem", "add", "--statement", "Q", "--answer", "A")
    invoke("concept", "add", "--content", "C1")
    invoke("concept", "add", "--content", "C2")
    invoke("edge", "add", "--from", "p1", "--to", "c1", "--type", "prereq")
    invoke("edge", "add", "--from", "c1", "--to", "c2", "--type", "prereq")
    invoke("project", "create", "--metadata", "P", "--goals", "p1")


def test_window(invoke):
    _setup(invoke)
    result = invoke("window", "--project", "prj1")
    data = parse_ok(result)
    assert data["node_count"] == 3
    assert data["edge_count"] == 2


def test_window_blackbox_terminates(invoke):
    _setup(invoke)
    invoke(
        "treatment", "set",
        "--project", "prj1", "--concept", "c1",
        "--treatment", "blackbox",
    )
    result = invoke("window", "--project", "prj1")
    data = parse_ok(result)
    ids = {n["id"] for n in data["nodes"]}
    assert "c2" not in ids


def test_breakdown(invoke):
    _setup(invoke)
    result = invoke("breakdown", "--project", "prj1", "--node", "p1")
    data = json.loads(result.output)
    assert data["count"] == 1
    assert data["result"][0]["id"] == "c1"


def test_frontier(invoke):
    _setup(invoke)
    invoke(
        "treatment", "set",
        "--project", "prj1", "--concept", "c1",
        "--treatment", "blackbox",
    )
    result = invoke("frontier", "--project", "prj1")
    data = json.loads(result.output)
    ids = {n["id"] for n in data["result"]}
    assert ids == {"c1"}


def test_ancestors(invoke):
    _setup(invoke)
    result = invoke("ancestors", "--project", "prj1", "--node", "c1")
    data = json.loads(result.output)
    ids = {n["id"] for n in data["result"]}
    assert ids == {"p1"}
