"""CLI テスト用 fixtures."""

import json

import pytest
from click.testing import CliRunner

from benkyo.cli import cli


@pytest.fixture
def runner(tmp_path, monkeypatch):
    """CLI runner with a temp DB via BENKYO_DB env var."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("BENKYO_DB", str(db_path))
    return CliRunner()


@pytest.fixture
def invoke(runner):
    """benkyo を呼ぶヘルパー."""

    def _invoke(*args, expect_ok=True):
        result = runner.invoke(cli, list(args), catch_exceptions=False)
        if expect_ok:
            assert result.exit_code == 0, (
                f"command failed: {args}\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr if hasattr(result, 'stderr') else '(merged)'}"
            )
        return result

    return _invoke


def parse_ok(result):
    """Parse JSON output, assert ok=True, return result."""
    data = json.loads(result.output)
    assert data["ok"] is True, f"expected ok=True, got: {data}"
    return data["result"]


def parse_err(result):
    """Parse JSON output for error case."""
    # CliRunner merges stderr with stdout by default; for our error JSON,
    # the json is in stdout or stderr depending on configuration.
    text = result.output or (result.stderr if hasattr(result, "stderr") else "")
    data = json.loads(text)
    assert data["ok"] is False
    return data
