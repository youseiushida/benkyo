"""DB file path resolution.

Priority: CLI flag > BENKYO_DB env var > XDG / OS default.
"""

import os
from pathlib import Path

from platformdirs import user_data_path

DB_FILENAME = "db.sqlite"
APP_NAME = "benkyo"
ENV_VAR = "BENKYO_DB"


def resolve_db_path(cli_path: str | None = None) -> Path:
    """Resolve the DB file path."""
    if cli_path:
        return Path(cli_path).expanduser().resolve()

    env_path = os.environ.get(ENV_VAR)
    if env_path:
        return Path(env_path).expanduser().resolve()

    return user_data_path(APP_NAME) / DB_FILENAME


def resolve_db_path_source(cli_path: str | None = None) -> tuple[Path, str]:
    """Return the DB path together with its source ('cli' | 'env' | 'default')."""
    if cli_path:
        return Path(cli_path).expanduser().resolve(), "cli"

    env_path = os.environ.get(ENV_VAR)
    if env_path:
        return Path(env_path).expanduser().resolve(), "env"

    return user_data_path(APP_NAME) / DB_FILENAME, "default"


def ensure_parent_dir(path: Path) -> None:
    """Create the parent directory of the DB file if it does not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
