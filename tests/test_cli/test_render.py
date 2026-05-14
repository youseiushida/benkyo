"""render CLI のテスト."""

import json
from pathlib import Path

from tests.test_cli.conftest import parse_ok


def _setup_project(invoke):
    invoke("problem", "add", "--statement", "Q", "--answer", "A")
    invoke("concept", "add", "--content", "C1")
    invoke("concept", "add", "--content", "C2")
    invoke("edge", "add", "--from", "p1", "--to", "c1", "--type", "prereq")
    invoke("edge", "add", "--from", "c1", "--to", "c2", "--type", "prereq")
    invoke("project", "create", "--metadata", "P", "--goals", "p1")


def test_render_mermaid_default(invoke):
    _setup_project(invoke)
    result = invoke("render", "--project", "prj1")
    assert "graph TD" in result.output
    assert "p1(" in result.output


def test_render_dot(invoke):
    _setup_project(invoke)
    result = invoke("render", "--project", "prj1", "--format", "dot")
    assert "digraph" in result.output
    assert '"p1" -> "c1"' in result.output


def test_render_to_file(invoke, tmp_path):
    _setup_project(invoke)
    out = tmp_path / "graph.mmd"
    result = invoke(
        "render",
        "--project",
        "prj1",
        "--format",
        "mermaid",
        "--output",
        str(out),
    )
    data = parse_ok(result)
    assert data["written_to"] == str(out)
    assert data["format"] == "mermaid"
    assert out.exists()
    assert "graph TD" in out.read_text(encoding="utf-8")


def test_render_blackbox_marker(invoke):
    _setup_project(invoke)
    invoke(
        "treatment",
        "set",
        "--project",
        "prj1",
        "--concept",
        "c2",
        "--treatment",
        "blackbox",
        "--reference",
        "公式",
    )
    result = invoke("render", "--project", "prj1", "--format", "mermaid")
    assert "class c2 blackbox" in result.output
    assert "fde68a" in result.output


def test_render_pipeable_to_dot(invoke):
    """stdout への出力が生テキスト (JSON エンベロープなし) であることを確認."""
    _setup_project(invoke)
    result = invoke("render", "--project", "prj1", "--format", "dot")
    # 先頭が "digraph" であり, JSON ではない
    assert result.output.lstrip().startswith("digraph")
