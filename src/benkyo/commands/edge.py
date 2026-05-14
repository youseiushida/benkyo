"""edge subcommand."""

import click

from benkyo import repository as repo
from benkyo._db import get_conn
from benkyo._output import handle_errors, output_ok

EDGE_TYPES = ["prereq", "related"]


@click.group(name="edge")
def edge_group():
    """Manage edges (prereq / related)."""


@edge_group.command(name="add")
@click.option("--from", "from_id", required=True, help="Source node id")
@click.option("--to", "to_id", required=True, help="Target node id")
@click.option(
    "--type",
    "edge_type",
    required=True,
    type=click.Choice(EDGE_TYPES),
    help="Edge type",
)
@click.pass_context
@handle_errors
def add(ctx, from_id, to_id, edge_type):
    """Add an edge between two nodes."""
    output_ok(repo.create_edge(get_conn(ctx), from_id, to_id, edge_type))


@edge_group.command(name="delete")
@click.option("--from", "from_id", required=True)
@click.option("--to", "to_id", required=True)
@click.option("--type", "edge_type", required=True, type=click.Choice(EDGE_TYPES))
@click.pass_context
@handle_errors
def delete(ctx, from_id, to_id, edge_type):
    """Delete an edge."""
    output_ok(repo.delete_edge(get_conn(ctx), from_id, to_id, edge_type))


@edge_group.command(name="list")
@click.option("--from", "from_id", default=None)
@click.option("--to", "to_id", default=None)
@click.option("--type", "edge_type", default=None, type=click.Choice(EDGE_TYPES))
@click.pass_context
@handle_errors
def list_cmd(ctx, from_id, to_id, edge_type):
    """List edges, optionally filtered by from / to / type."""
    items = repo.list_edges(get_conn(ctx), from_id, to_id, edge_type)
    output_ok(items, count=len(items))
