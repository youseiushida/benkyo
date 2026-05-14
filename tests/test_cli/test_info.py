"""info CLI のテスト."""

import json

from tests.test_cli.conftest import parse_ok


def test_info_empty_db(invoke):
    result = invoke("info")
    data = parse_ok(result)
    assert data["counts"]["concept_nodes"] == 0
    assert data["counts"]["problem_nodes"] == 0
    assert data["db_path_source"] == "env"


def test_info_with_data(invoke):
    invoke("concept", "add", "--content", "A")
    invoke("problem", "add", "--statement", "Q", "--answer", "A")
    result = invoke("info")
    data = parse_ok(result)
    assert data["counts"]["concept_nodes"] == 1
    assert data["counts"]["problem_nodes"] == 1
