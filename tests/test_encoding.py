"""Regression test: CLI output works with non-ASCII (Japanese, math symbols)
even when the OS default encoding (cp932 on Windows) cannot represent them.
"""

import json
import subprocess
import sys


def test_japanese_content_in_concept_list(tmp_path):
    """Adding and listing a concept with Japanese + math chars must not raise UnicodeEncodeError."""
    db_path = tmp_path / "enc.db"
    env = {"BENKYO_DB": str(db_path)}

    content = "ラプラス変換: F(s) = ∫₀^∞ f(t) e^(-st) dt, ω² の計算など"

    # add
    result = subprocess.run(
        [sys.executable, "-m", "benkyo", "concept", "add", "--content", content],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**__import__("os").environ, **env},
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["result"]["content"] == content

    # list
    result = subprocess.run(
        [sys.executable, "-m", "benkyo", "concept", "list"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**__import__("os").environ, **env},
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["count"] == 1


def test_render_with_japanese_content(tmp_path):
    """`benkyo render` outputs Japanese in Mermaid format without encoding errors."""
    import os

    db_path = tmp_path / "enc2.db"
    env = {**os.environ, "BENKYO_DB": str(db_path)}

    # set up a minimal project
    def run(args):
        r = subprocess.run(
            [sys.executable, "-m", "benkyo", *args],
            capture_output=True, text=True, encoding="utf-8", env=env,
        )
        assert r.returncode == 0, f"failed {args}: {r.stderr}"
        return json.loads(r.stdout) if r.stdout.strip().startswith("{") else r.stdout

    run(["problem", "add", "--statement", "問題: y²+1=0 を解け", "--answer", "y=±i"])
    run(["concept", "add", "--content", "虚数: i² = -1"])
    run(["edge", "add", "--from", "p1", "--to", "c1", "--type", "prereq"])
    run(["project", "create", "--metadata", "テスト", "--goals", "p1"])

    # render — this used to fail with cp932
    out = run(["render", "--project", "prj1", "--format", "mermaid"])
    assert "虚数" in out or "ω" in out or "問題" in out
