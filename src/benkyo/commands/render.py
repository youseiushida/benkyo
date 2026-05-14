"""render command: visualize a project's window as DOT or Mermaid text."""

from pathlib import Path

import click

from benkyo import render, traversal
from benkyo._db import get_conn
from benkyo._output import handle_errors, output_ok


@click.command(name="render")
@click.option("--project", "project_id", required=True)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["dot", "mermaid"]),
    default="mermaid",
    help="Output format (default: mermaid)",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(),
    help="Output file (raw text written to stdout if omitted)",
)
@click.pass_context
@handle_errors
def render_cmd(ctx, project_id, fmt, output):
    """Render a project's window as DOT or Mermaid text.

    \b
    Examples:
      benkyo render --project prj1 --format mermaid
      benkyo render --project prj1 --format dot | dot -Tpng > graph.png
      benkyo render --project prj1 --format dot --output graph.dot
    """
    conn = get_conn(ctx)
    window_data = traversal.window(conn, project_id)

    if fmt == "dot":
        text = render.to_dot(window_data, graph_name=f"benkyo_{project_id}")
    else:  # mermaid
        text = render.to_mermaid(window_data)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        output_ok(
            {
                "written_to": output,
                "format": fmt,
                "size_bytes": len(text.encode("utf-8")),
                "node_count": window_data["node_count"],
                "edge_count": window_data["edge_count"],
            }
        )
    else:
        click.echo(text)
