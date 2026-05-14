"""problem subcommand."""

import click

from benkyo import repository as repo
from benkyo._db import get_conn
from benkyo._input import resolve_text
from benkyo._output import handle_errors, output_ok


@click.group(name="problem")
def problem_group():
    """Manage problem nodes."""


@problem_group.command(name="add")
@click.option("--statement", default=None)
@click.option("--statement-file", default=None, type=click.Path())
@click.option("--answer", default=None)
@click.option("--answer-file", default=None, type=click.Path())
@click.pass_context
@handle_errors
def add(ctx, statement, statement_file, answer, answer_file):
    """Add a new problem node."""
    stmt = resolve_text(statement, statement_file)
    ans = resolve_text(answer, answer_file)
    if stmt is None or ans is None:
        raise click.UsageError("--statement(-file) and --answer(-file) are required")
    output_ok(repo.create_problem(get_conn(ctx), stmt, ans))


@problem_group.command(name="get")
@click.argument("problem_id")
@click.pass_context
@handle_errors
def get(ctx, problem_id):
    """Get a problem node by id."""
    output_ok(repo.get_problem(get_conn(ctx), problem_id))


@problem_group.command(name="update")
@click.argument("problem_id")
@click.option("--statement", default=None)
@click.option("--statement-file", default=None, type=click.Path())
@click.option("--answer", default=None)
@click.option("--answer-file", default=None, type=click.Path())
@click.pass_context
@handle_errors
def update(ctx, problem_id, statement, statement_file, answer, answer_file):
    """Update statement and/or answer of a problem node."""
    stmt = resolve_text(statement, statement_file)
    ans = resolve_text(answer, answer_file)
    output_ok(repo.update_problem(get_conn(ctx), problem_id, stmt, ans))


@problem_group.command(name="delete")
@click.argument("problem_id")
@click.pass_context
@handle_errors
def delete(ctx, problem_id):
    """Delete a problem node (related rows cascade)."""
    output_ok(repo.delete_problem(get_conn(ctx), problem_id))


@problem_group.command(name="list")
@click.option("--query", default=None)
@click.pass_context
@handle_errors
def list_cmd(ctx, query):
    """List problem nodes."""
    items = repo.list_problems(get_conn(ctx), query)
    output_ok(items, count=len(items))


@problem_group.command(name="merge")
@click.argument("source_id")
@click.option("--into", "canonical_id", required=True, help="Canonical problem id to merge into")
@click.pass_context
@handle_errors
def merge(ctx, source_id, canonical_id):
    """Merge source problem into canonical. Edges and project goals redirect."""
    output_ok(repo.merge_problem(get_conn(ctx), source_id, canonical_id))
