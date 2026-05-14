"""CLI input helpers (text from argument / file / stdin)."""

import sys
from pathlib import Path


def resolve_text(value: str | None, file: str | None) -> str | None:
    """Resolve text input from either `value` (or '-' for stdin) or a file path.

    Returns None if neither is provided.
    """
    if value is not None and value != "-":
        return value
    if value == "-":
        return sys.stdin.read()
    if file is not None:
        if file == "-":
            return sys.stdin.read()
        return Path(file).read_text(encoding="utf-8")
    return None


def parse_id_list(value: str | None) -> list[str]:
    """Split a comma-separated id list."""
    if not value:
        return []
    return [s.strip() for s in value.split(",") if s.strip()]
