"""problem CLI のテスト."""

import json

from tests.test_cli.conftest import parse_ok


def test_add_and_get(invoke):
    result = invoke(
        "problem", "add", "--statement", "1+1は?", "--answer", "2"
    )
    data = parse_ok(result)
    assert data["id"] == "p1"

    result = invoke("problem", "get", "p1")
    assert parse_ok(result)["statement"] == "1+1は?"


def test_update_partial(invoke):
    invoke("problem", "add", "--statement", "Q", "--answer", "A")
    result = invoke("problem", "update", "p1", "--statement", "Q2")
    data = parse_ok(result)
    assert data["statement"] == "Q2"
    assert data["answer"] == "A"


def test_delete(invoke):
    invoke("problem", "add", "--statement", "Q", "--answer", "A")
    result = invoke("problem", "delete", "p1")
    assert parse_ok(result)["deleted_id"] == "p1"
