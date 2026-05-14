"""DB パス解決のテスト."""

from benkyo.paths import resolve_db_path, resolve_db_path_source


def test_cli_flag_takes_precedence(monkeypatch, tmp_path):
    monkeypatch.setenv("BENKYO_DB", str(tmp_path / "env.db"))
    result = resolve_db_path(str(tmp_path / "cli.db"))
    assert result.name == "cli.db"


def test_env_var_used_when_no_cli(monkeypatch, tmp_path):
    env_path = tmp_path / "env.db"
    monkeypatch.setenv("BENKYO_DB", str(env_path))
    result = resolve_db_path()
    assert result == env_path.resolve()


def test_default_when_no_env_no_cli(monkeypatch):
    monkeypatch.delenv("BENKYO_DB", raising=False)
    result = resolve_db_path()
    assert result.name == "db.sqlite"
    assert "benkyo" in str(result).lower()


def test_source_default(monkeypatch):
    monkeypatch.delenv("BENKYO_DB", raising=False)
    _, source = resolve_db_path_source(None)
    assert source == "default"


def test_source_env(monkeypatch, tmp_path):
    monkeypatch.setenv("BENKYO_DB", str(tmp_path / "env.db"))
    _, source = resolve_db_path_source(None)
    assert source == "env"


def test_source_cli(monkeypatch, tmp_path):
    monkeypatch.setenv("BENKYO_DB", str(tmp_path / "env.db"))
    _, source = resolve_db_path_source(str(tmp_path / "cli.db"))
    assert source == "cli"
