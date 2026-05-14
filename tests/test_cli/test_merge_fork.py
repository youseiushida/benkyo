"""CLI tests for merge / fork."""

import json

from tests.test_cli.conftest import parse_ok


def test_concept_merge_cli(invoke):
    invoke("concept", "add", "--content", "A")
    invoke("concept", "add", "--content", "B")
    invoke("concept", "add", "--content", "C")
    invoke("edge", "add", "--from", "c2", "--to", "c3", "--type", "prereq")

    result = invoke("concept", "merge", "c2", "--into", "c1")
    data = parse_ok(result)
    assert data["merged_source"] == "c2"
    assert data["into_canonical"] == "c1"
    assert data["edges_redirected"] == 1


def test_concept_merge_conflict_error_exit_code(invoke):
    invoke("concept", "add", "--content", "A")
    invoke("concept", "add", "--content", "B")
    invoke("project", "create", "--metadata", "P")
    invoke(
        "treatment", "set", "--project", "prj1",
        "--concept", "c1", "--treatment", "whitebox",
    )
    invoke(
        "treatment", "set", "--project", "prj1",
        "--concept", "c2", "--treatment", "blackbox",
    )

    # default --on-conflict=error → conflict (exit code 3)
    result = invoke(
        "concept", "merge", "c2", "--into", "c1", expect_ok=False
    )
    assert result.exit_code == 3


def test_concept_merge_keep_canonical(invoke):
    invoke("concept", "add", "--content", "A")
    invoke("concept", "add", "--content", "B")
    invoke("project", "create", "--metadata", "P")
    invoke(
        "treatment", "set", "--project", "prj1",
        "--concept", "c1", "--treatment", "whitebox",
    )
    invoke(
        "treatment", "set", "--project", "prj1",
        "--concept", "c2", "--treatment", "blackbox",
        "--reference", "ref",
    )

    result = invoke(
        "concept", "merge", "c2", "--into", "c1",
        "--on-conflict", "keep_canonical",
    )
    data = parse_ok(result)
    assert data["treatments_skipped"] == 1

    # c1 still whitebox
    result = invoke("treatment", "get", "--project", "prj1", "--concept", "c1")
    t = parse_ok(result)
    assert t["treatment"] == "whitebox"


def test_problem_merge_cli(invoke):
    invoke("problem", "add", "--statement", "Q1", "--answer", "A1")
    invoke("problem", "add", "--statement", "Q2", "--answer", "A2")
    invoke("project", "create", "--metadata", "P", "--goals", "p1,p2")

    result = invoke("problem", "merge", "p2", "--into", "p1")
    data = parse_ok(result)
    assert data["merged_source"] == "p2"
    assert data["goals_skipped"] == 1  # both were goals, p2 dedup'd

    proj = parse_ok(invoke("project", "get", "prj1"))
    assert proj["goals"] == ["p1"]


def test_concept_fork_cli(invoke):
    invoke("concept", "add", "--content", "Laplace transform")
    invoke("concept", "add", "--content", "Definite integral")
    invoke("edge", "add", "--from", "c1", "--to", "c2", "--type", "prereq")

    result = invoke("concept", "fork", "c1")
    data = parse_ok(result)
    assert data["forked_from"] == "c1"
    assert data["new_id"] == "c3"
    assert data["edges_copied"] == 1

    # new concept has same content
    new = parse_ok(invoke("concept", "get", "c3"))
    assert new["content"] == "Laplace transform"


def test_concept_fork_with_new_content(invoke):
    invoke("concept", "add", "--content", "Original")
    result = invoke(
        "concept", "fork", "c1", "--content", "Modified copy"
    )
    data = parse_ok(result)
    assert data["new_id"] == "c2"

    new = parse_ok(invoke("concept", "get", "c2"))
    assert new["content"] == "Modified copy"
