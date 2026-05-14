"""info command: summary of the current DB."""

import click

from benkyo._db import get_conn
from benkyo._output import handle_errors, output_ok
from benkyo.paths import resolve_db_path_source


@click.command(name="info")
@click.pass_context
@handle_errors
def info_cmd(ctx):
    """Show DB path, source of that path, and row counts per table."""
    db_path_override = ctx.obj.get("db_path_override") if ctx.obj else None
    path, source = resolve_db_path_source(db_path_override)

    conn = get_conn(ctx)
    counts = {
        "concept_nodes": conn.execute("SELECT COUNT(*) FROM concept_nodes").fetchone()[0],
        "problem_nodes": conn.execute("SELECT COUNT(*) FROM problem_nodes").fetchone()[0],
        "edges": conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0],
        "projects": conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
        "project_concepts": conn.execute("SELECT COUNT(*) FROM project_concepts").fetchone()[0],
        "project_goals": conn.execute("SELECT COUNT(*) FROM project_goals").fetchone()[0],
    }

    output_ok(
        {
            "db_path": str(path),
            "db_path_source": source,
            "db_exists": path.exists(),
            "db_size_bytes": path.stat().st_size if path.exists() else 0,
            "counts": counts,
        }
    )
