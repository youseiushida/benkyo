"""treatment subcommand (per (project, concept) blackbox/whitebox annotation)."""

import click

from benkyo import repository as repo
from benkyo._db import get_conn
from benkyo._input import resolve_text
from benkyo._output import handle_errors, output_ok

TREATMENTS = ["blackbox", "whitebox"]
SET_BY = ["system", "learner", "material"]


@click.group(name="treatment")
def treatment_group():
    """Manage per-project concept treatment (blackbox / whitebox).

    blackbox = use the concept as a tool (formula / lookup, no derivation needed).
    whitebox = understand the why (derivation / proof / internals).
    """


@treatment_group.command(name="set")
@click.option("--project", "project_id", required=True)
@click.option("--concept", "concept_id", required=True)
@click.option(
    "--treatment",
    "treatment_val",
    required=True,
    type=click.Choice(TREATMENTS),
)
@click.option("--reference", default=None, help="Reference content when blackbox")
@click.option("--reference-file", default=None, type=click.Path())
@click.option("--set-by", default="learner", type=click.Choice(SET_BY))
@click.pass_context
@handle_errors
def set_cmd(ctx, project_id, concept_id, treatment_val, reference, reference_file, set_by):
    """Set or update treatment for a (project, concept) pair."""
    ref = resolve_text(reference, reference_file)
    output_ok(
        repo.set_treatment(
            get_conn(ctx), project_id, concept_id, treatment_val, ref, set_by
        )
    )


@treatment_group.command(name="get")
@click.option("--project", "project_id", required=True)
@click.option("--concept", "concept_id", required=True)
@click.pass_context
@handle_errors
def get(ctx, project_id, concept_id):
    """Get the treatment (defaults to whitebox if unset)."""
    output_ok(repo.get_treatment(get_conn(ctx), project_id, concept_id))


@treatment_group.command(name="unset")
@click.option("--project", "project_id", required=True)
@click.option("--concept", "concept_id", required=True)
@click.pass_context
@handle_errors
def unset(ctx, project_id, concept_id):
    """Remove explicit setting (reverts to default whitebox)."""
    output_ok(repo.unset_treatment(get_conn(ctx), project_id, concept_id))


@treatment_group.command(name="list")
@click.option("--project", "project_id", required=True)
@click.option("--treatment", "treatment_val", default=None, type=click.Choice(TREATMENTS))
@click.pass_context
@handle_errors
def list_cmd(ctx, project_id, treatment_val):
    """List explicit treatments for a project."""
    items = repo.list_treatments(get_conn(ctx), project_id, treatment_val)
    output_ok(items, count=len(items))
