"""project subcommand."""

import click

from benkyo import repository as repo
from benkyo._db import get_conn
from benkyo._input import parse_id_list, resolve_text
from benkyo._output import handle_errors, output_ok


@click.group(name="project")
def project_group():
    """Manage projects."""


@project_group.command(name="create")
@click.option("--metadata", default=None)
@click.option("--metadata-file", default=None, type=click.Path())
@click.option("--goals", default=None, help="Comma-separated list of goal problem ids")
@click.pass_context
@handle_errors
def create(ctx, metadata, metadata_file, goals):
    """Create a new project."""
    meta = resolve_text(metadata, metadata_file) or ""
    goal_ids = parse_id_list(goals)
    output_ok(repo.create_project(get_conn(ctx), meta, goal_ids))


@project_group.command(name="get")
@click.argument("project_id")
@click.pass_context
@handle_errors
def get(ctx, project_id):
    """Get a project by id."""
    output_ok(repo.get_project(get_conn(ctx), project_id))


@project_group.command(name="update")
@click.argument("project_id")
@click.option("--metadata", default=None)
@click.option("--metadata-file", default=None, type=click.Path())
@click.option(
    "--goals",
    default=None,
    help="Comma-separated goal problem ids (empty string clears all goals)",
)
@click.pass_context
@handle_errors
def update(ctx, project_id, metadata, metadata_file, goals):
    """Update a project."""
    meta = resolve_text(metadata, metadata_file)
    goal_ids = parse_id_list(goals) if goals is not None else None
    output_ok(repo.update_project(get_conn(ctx), project_id, meta, goal_ids))


@project_group.command(name="delete")
@click.argument("project_id")
@click.pass_context
@handle_errors
def delete(ctx, project_id):
    """Delete a project (related rows cascade)."""
    output_ok(repo.delete_project(get_conn(ctx), project_id))


@project_group.command(name="list")
@click.pass_context
@handle_errors
def list_cmd(ctx):
    """List all projects."""
    items = repo.list_projects(get_conn(ctx))
    output_ok(items, count=len(items))
