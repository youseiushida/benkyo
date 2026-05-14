"""concept CLI のテスト."""

import json

from tests.test_cli.conftest import parse_ok


def test_add_and_get(invoke):
    result = invoke("concept", "add", "--content", "ラプラス変換")
    data = parse_ok(result)
    assert data["id"] == "c1"
    assert data["content"] == "ラプラス変換"

    result = invoke("concept", "get", "c1")
    data = parse_ok(result)
    assert data["content"] == "ラプラス変換"


def test_list_and_query(invoke):
    invoke("concept", "add", "--content", "ラプラス変換")
    invoke("concept", "add", "--content", "フーリエ変換")
    invoke("concept", "add", "--content", "微分方程式")

    result = invoke("concept", "list")
    data = json.loads(result.output)
    assert data["count"] == 3

    result = invoke("concept", "list", "--query", "変換")
    data = json.loads(result.output)
    assert data["count"] == 2


def test_update(invoke):
    invoke("concept", "add", "--content", "旧")
    result = invoke("concept", "update", "c1", "--content", "新")
    assert parse_ok(result)["content"] == "新"


def test_delete(invoke):
    invoke("concept", "add", "--content", "X")
    result = invoke("concept", "delete", "c1")
    assert parse_ok(result)["deleted_id"] == "c1"


def test_get_not_found_exit_code(invoke):
    result = invoke("concept", "get", "c999", expect_ok=False)
    assert result.exit_code == 2  # not_found


def test_find_exact(invoke):
    invoke("concept", "add", "--content", "X")
    invoke("concept", "add", "--content", "X 拡張")
    result = invoke("concept", "find", "--content", "X")
    assert json.loads(result.output)["count"] == 1
