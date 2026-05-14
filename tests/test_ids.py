"""ID 生成のテスト."""

import pytest

from benkyo.ids import (
    CONCEPT_PREFIX,
    PROBLEM_PREFIX,
    PROJECT_PREFIX,
    next_id,
    parse_id,
)


def test_next_id_sequential(conn):
    assert next_id(conn, CONCEPT_PREFIX) == "c1"
    assert next_id(conn, CONCEPT_PREFIX) == "c2"
    assert next_id(conn, CONCEPT_PREFIX) == "c3"


def test_next_id_independent_prefixes(conn):
    assert next_id(conn, CONCEPT_PREFIX) == "c1"
    assert next_id(conn, PROBLEM_PREFIX) == "p1"
    assert next_id(conn, CONCEPT_PREFIX) == "c2"
    assert next_id(conn, PROJECT_PREFIX) == "prj1"


def test_parse_id_valid():
    assert parse_id("c5") == ("c", 5)
    assert parse_id("p10") == ("p", 10)
    assert parse_id("prj3") == ("prj", 3)


def test_parse_id_invalid():
    with pytest.raises(ValueError):
        parse_id("xyz")
    with pytest.raises(ValueError):
        parse_id("c")
    with pytest.raises(ValueError):
        parse_id("c1a")
