"""concept subcommand."""

import click

from benkyo import repository as repo
from benkyo._db import get_conn
from benkyo._input import resolve_text
from benkyo._output import handle_errors, output_ok


@click.group(name="concept")
def concept_group():
    """Manage concept nodes."""


@concept_group.command(name="add")
@click.option(
    "--name",
    default=None,
    help="Short display name for graph labels (auto-extracted from content if omitted)",
)
@click.option("--content", default=None, help="Concept content. Pass '-' to read from stdin")
@click.option("--content-file", default=None, type=click.Path(), help="Read content from file")
@click.pass_context
@handle_errors
def add(ctx, name, content, content_file):
    """Add a new concept node."""
    text = resolve_text(content, content_file)
    if text is None:
        raise click.UsageError("--content or --content-file is required")
    output_ok(repo.create_concept(get_conn(ctx), text, name=name))


@concept_group.command(name="get")
@click.argument("concept_id")
@click.pass_context
@handle_errors
def get(ctx, concept_id):
    """Get a concept node by id."""
    output_ok(repo.get_concept(get_conn(ctx), concept_id))


@concept_group.command(name="update")
@click.argument("concept_id")
@click.option("--name", default=None, help="Short display name for graph labels")
@click.option("--content", default=None)
@click.option("--content-file", default=None, type=click.Path())
@click.pass_context
@handle_errors
def update(ctx, concept_id, name, content, content_file):
    """Update the content and/or name of a concept node."""
    text = resolve_text(content, content_file)
    if text is None and name is None:
        raise click.UsageError("--content, --content-file, or --name is required")
    output_ok(repo.update_concept(get_conn(ctx), concept_id, content=text, name=name))


@concept_group.command(name="delete")
@click.argument("concept_id")
@click.pass_context
@handle_errors
def delete(ctx, concept_id):
    """Delete a concept node (related rows cascade)."""
    output_ok(repo.delete_concept(get_conn(ctx), concept_id))


@concept_group.command(name="list")
@click.option("--query", default=None, help="Substring filter on content")
@click.pass_context
@handle_errors
def list_cmd(ctx, query):
    """List concept nodes."""
    items = repo.list_concepts(get_conn(ctx), query)
    output_ok(items, count=len(items))


@concept_group.command(name="find")
@click.option("--content", required=True, help="Exact content to match")
@click.pass_context
@handle_errors
def find(ctx, content):
    """Find a concept by exact content match (identity check)."""
    items = repo.find_concept_by_content(get_conn(ctx), content)
    output_ok(items, count=len(items))


@concept_group.command(name="merge")
@click.argument("source_id")
@click.option("--into", "canonical_id", required=True, help="Canonical concept id to merge into")
@click.option(
    "--on-conflict",
    type=click.Choice(["error", "keep_canonical", "keep_source"]),
    default="error",
    help="Behavior when both source and canonical have a treatment for the same project",
)
@click.pass_context
@handle_errors
def merge(ctx, source_id, canonical_id, on_conflict):
    """Merge source concept into canonical. Edges and treatments redirect."""
    output_ok(repo.merge_concept(get_conn(ctx), source_id, canonical_id, on_conflict))


@concept_group.command(name="fork")
@click.argument("source_id")
@click.option("--content", default=None, help="New content (defaults to source's content)")
@click.option("--content-file", default=None, type=click.Path())
@click.pass_context
@handle_errors
def fork(ctx, source_id, content, content_file):
    """Create a new concept that copies source's edges (but not treatments)."""
    text = resolve_text(content, content_file)
    output_ok(repo.fork_concept(get_conn(ctx), source_id, text))
