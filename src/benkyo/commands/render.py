"""render command: visualize a project graph as DOT or Mermaid text."""

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
    "--scope",
    type=click.Choice(["window", "project", "graph"]),
    default="window",
    help=(
        "window: BFS from goals via prereq edges (default); "
        "project: all nodes registered in the project; "
        "graph: entire global concept/problem graph"
    ),
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
def render_cmd(ctx, project_id, fmt, scope, output):
    """Render a project graph as DOT or Mermaid text.

    \b
    Scope options:
      window   BFS from project goals via prereq edges (default)
      project  All nodes registered in the project (project_concepts + goals)
      graph    Entire global concept/problem graph

    \b
    Examples:
      benkyo render --project prj1
      benkyo render --project prj1 --scope project --format mermaid
      benkyo render --project prj1 --scope graph --format dot | dot -Tpng > graph.png
      benkyo render --project prj1 --format dot --output graph.dot
    """
    conn = get_conn(ctx)
    if scope == "window":
        data = traversal.window(conn, project_id)
    elif scope == "project":
        data = traversal.project_scope(conn, project_id)
    else:  # graph
        data = traversal.graph_scope(conn, project_id)

    if fmt == "dot":
        text = render.to_dot(data, graph_name=f"benkyo_{project_id}_{scope}")
    else:
        text = render.to_mermaid(data)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        output_ok(
            {
                "written_to": output,
                "format": fmt,
                "scope": scope,
                "size_bytes": len(text.encode("utf-8")),
                "node_count": data["node_count"],
                "edge_count": data["edge_count"],
            }
        )
    else:
        click.echo(text)
