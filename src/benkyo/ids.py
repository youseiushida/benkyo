"""Sequential id generation (c1, p1, prj1, ...)."""

import sqlite3

CONCEPT_PREFIX = "c"
PROBLEM_PREFIX = "p"
PROJECT_PREFIX = "prj"


def next_id(conn: sqlite3.Connection, prefix: str) -> str:
    """Return the next sequential id for the given prefix.

    Examples:
        next_id(conn, "c") -> "c1", "c2", ...
        next_id(conn, "p") -> "p1", "p2", ...
        next_id(conn, "prj") -> "prj1", "prj2", ...
    """
    row = conn.execute(
        "SELECT last_value FROM id_counters WHERE prefix = ?", (prefix,)
    ).fetchone()

    if row is None:
        next_value = 1
        conn.execute(
            "INSERT INTO id_counters (prefix, last_value) VALUES (?, ?)",
            (prefix, next_value),
        )
    else:
        next_value = row["last_value"] + 1
        conn.execute(
            "UPDATE id_counters SET last_value = ? WHERE prefix = ?",
            (next_value, prefix),
        )

    return f"{prefix}{next_value}"


def parse_id(value: str) -> tuple[str, int]:
    """Split an id into its prefix and numeric part. Raises ValueError on malformed input."""
    for prefix in (PROJECT_PREFIX, CONCEPT_PREFIX, PROBLEM_PREFIX):
        if value.startswith(prefix):
            rest = value[len(prefix):]
            if rest.isdigit():
                return prefix, int(rest)
    raise ValueError(f"invalid id format: {value!r}")
