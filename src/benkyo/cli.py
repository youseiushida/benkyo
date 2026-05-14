"""benkyo CLI entry point."""

import sys

import click

from benkyo import __version__


def _force_utf8_io() -> None:
    """Force UTF-8 on stdout/stderr.

    Required on Windows where the default code page (cp932 etc.) cannot encode
    characters that appear in content (Japanese, math symbols like ², ω, etc.).
    Without this, click.echo raises UnicodeEncodeError when output contains
    such characters.
    """
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except Exception:
            # Best-effort: if reconfigure fails (e.g., stream is redirected to
            # a non-text target), leave it alone.
            pass
from benkyo.commands.concept import concept_group
from benkyo.commands.edge import edge_group
from benkyo.commands.events import events_group
from benkyo.commands.info import info_cmd
from benkyo.commands.io_cmds import register as register_io
from benkyo.commands.problem import problem_group
from benkyo.commands.project import project_group
from benkyo.commands.render import render_cmd
from benkyo.commands.schema import register as register_schema
from benkyo.commands.session import session_group
from benkyo.commands.traversal_cmds import register as register_traversal
from benkyo.commands.treatment import treatment_group


@click.group()
@click.option(
    "--db",
    "db_path_override",
    type=str,
    default=None,
    help="Override DB file path (takes precedence over BENKYO_DB and OS default)",
)
@click.version_option(version=__version__, prog_name="benkyo")
@click.pass_context
def cli(ctx: click.Context, db_path_override: str | None) -> None:
    """benkyo: problem-driven learning support CLI.

    Manages a global concept-dependency graph and per-project annotations
    of blackbox (use-as-tool) vs whitebox (understand-internals) treatment
    for each concept.
    """
    ctx.ensure_object(dict)
    ctx.obj["db_path_override"] = db_path_override


cli.add_command(concept_group)
cli.add_command(problem_group)
cli.add_command(edge_group)
cli.add_command(project_group)
cli.add_command(treatment_group)
cli.add_command(events_group)
cli.add_command(session_group)
register_traversal(cli)
register_io(cli)
cli.add_command(render_cmd)
cli.add_command(info_cmd)
register_schema(cli)


def main() -> None:
    _force_utf8_io()
    cli()


if __name__ == "__main__":
    main()
