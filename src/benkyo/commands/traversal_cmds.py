"""Traversal commands: window, breakdown, frontier, ancestors."""

import click

from benkyo import traversal
from benkyo._db import get_conn
from benkyo._output import handle_errors, output_ok


@click.command(name="window")
@click.option("--project", "project_id", required=True)
@click.pass_context
@handle_errors
def window_cmd(ctx, project_id):
    """Return the project's window (nodes + edges).

    Traversal starts from the project's goal problems and follows prereq edges.
    Procedural-treated concepts are terminals (included in the window but not
    traversed further).
    """
    output_ok(traversal.window(get_conn(ctx), project_id))


@click.command(name="breakdown")
@click.option("--project", "project_id", required=True)
@click.option("--node", "node_id", required=True)
@click.pass_context
@handle_errors
def breakdown_cmd(ctx, project_id, node_id):
    """List the direct prereq dependencies of the given node."""
    items = traversal.breakdown(get_conn(ctx), project_id, node_id)
    output_ok(items, count=len(items))


@click.command(name="frontier")
@click.option("--project", "project_id", required=True)
@click.pass_context
@handle_errors
def frontier_cmd(ctx, project_id):
    """List procedural concepts within the window (promotion candidates)."""
    items = traversal.frontier(get_conn(ctx), project_id)
    output_ok(items, count=len(items))


@click.command(name="ancestors")
@click.option("--project", "project_id", required=True)
@click.option("--node", "node_id", required=True)
@click.pass_context
@handle_errors
def ancestors_cmd(ctx, project_id, node_id):
    """List nodes within the window that depend on the given node."""
    items = traversal.ancestors(get_conn(ctx), project_id, node_id)
    output_ok(items, count=len(items))


def register(cli_group):
    cli_group.add_command(window_cmd)
    cli_group.add_command(breakdown_cmd)
    cli_group.add_command(frontier_cmd)
    cli_group.add_command(ancestors_cmd)
