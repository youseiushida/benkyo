"""edge CLI のテスト."""

import json

from tests.test_cli.conftest import parse_ok


def test_add_list_delete(invoke):
    invoke("concept", "add", "--content", "A")
    invoke("concept", "add", "--content", "B")
    invoke("edge", "add", "--from", "c1", "--to", "c2", "--type", "prereq")

    result = invoke("edge", "list", "--from", "c1")
    assert json.loads(result.output)["count"] == 1

    invoke("edge", "delete", "--from", "c1", "--to", "c2", "--type", "prereq")
    result = invoke("edge", "list")
    assert json.loads(result.output)["count"] == 0


def test_self_loop_rejected(invoke):
    invoke("concept", "add", "--content", "A")
    result = invoke(
        "edge", "add", "--from", "c1", "--to", "c1", "--type", "prereq",
        expect_ok=False,
    )
    assert result.exit_code == 1  # invalid_arg


def test_duplicate_rejected(invoke):
    invoke("concept", "add", "--content", "A")
    invoke("concept", "add", "--content", "B")
    invoke("edge", "add", "--from", "c1", "--to", "c2", "--type", "prereq")
    result = invoke(
        "edge", "add", "--from", "c1", "--to", "c2", "--type", "prereq",
        expect_ok=False,
    )
    assert result.exit_code == 3  # conflict
