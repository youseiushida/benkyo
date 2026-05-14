"""treatment CLI のテスト."""

import json

from tests.test_cli.conftest import parse_ok


def setup_basic(invoke):
    invoke("concept", "add", "--content", "X")
    invoke("project", "create", "--metadata", "P")


def test_default_is_conceptual(invoke):
    setup_basic(invoke)
    result = invoke("treatment", "get", "--project", "prj1", "--concept", "c1")
    data = parse_ok(result)
    assert data["treatment"] == "conceptual"
    assert data["default"] is True


def test_set_procedural_with_reference(invoke):
    setup_basic(invoke)
    result = invoke(
        "treatment", "set",
        "--project", "prj1", "--concept", "c1",
        "--treatment", "procedural",
        "--reference", "公式表",
    )
    data = parse_ok(result)
    assert data["treatment"] == "procedural"
    assert data["reference_content"] == "公式表"


def test_unset_returns_to_default(invoke):
    setup_basic(invoke)
    invoke(
        "treatment", "set",
        "--project", "prj1", "--concept", "c1",
        "--treatment", "procedural",
    )
    invoke("treatment", "unset", "--project", "prj1", "--concept", "c1")
    result = invoke("treatment", "get", "--project", "prj1", "--concept", "c1")
    assert parse_ok(result)["default"] is True
