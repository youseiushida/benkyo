"""export / import commands."""

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click

from benkyo import repository as repo
from benkyo._db import get_conn
from benkyo._output import handle_errors, output_ok
from benkyo.db import transaction
from benkyo.errors import ConflictError, InvalidArgError, NotFoundError
from benkyo.ids import CONCEPT_PREFIX, PROBLEM_PREFIX, PROJECT_PREFIX

GRAPH_FORMAT = "benkyo/graph/v1"
PROJECT_FORMAT = "benkyo/project/v1"


# =======================================================================
# Common helpers
# =======================================================================


def _emit(text: str, output: str | None) -> None:
    if output:
        Path(output).write_text(text, encoding="utf-8")
        output_ok({"written_to": output, "size_bytes": len(text.encode("utf-8"))})
    else:
        click.echo(text)


def _load_payload(path: str, expected_format: str) -> dict[str, Any]:
    if path == "-":
        text = sys.stdin.read()
    else:
        text = Path(path).read_text(encoding="utf-8")
    payload = json.loads(text)
    fmt = payload.get("format")
    if fmt != expected_format:
        raise InvalidArgError(
            f"unexpected format: {fmt!r} (expected {expected_format!r})"
        )
    return payload


def _refresh_id_counters(conn: sqlite3.Connection) -> None:
    """After import, bump id_counters to the maximum existing id."""
    for table, prefix in [
        ("concept_nodes", CONCEPT_PREFIX),
        ("problem_nodes", PROBLEM_PREFIX),
        ("projects", PROJECT_PREFIX),
    ]:
        rows = conn.execute(f"SELECT id FROM {table}").fetchall()
        max_val = 0
        for r in rows:
            rest = r["id"][len(prefix):]
            if rest.isdigit():
                max_val = max(max_val, int(rest))
        conn.execute(
            """
            INSERT INTO id_counters (prefix, last_value) VALUES (?, ?)
            ON CONFLICT(prefix) DO UPDATE SET last_value = MAX(last_value, excluded.last_value)
            """,
            (prefix, max_val),
        )


# =======================================================================
# Export
# =======================================================================


@click.group(name="export")
def export_group():
    """Export data to JSON."""


@export_group.command(name="graph")
@click.option("--output", "-o", default=None, type=click.Path(), help="Output file (stdout if omitted)")
@click.pass_context
@handle_errors
def export_graph(ctx, output):
    """Export the entire global graph."""
    conn = get_conn(ctx)
    payload = {
        "format": GRAPH_FORMAT,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "concept_nodes": [
            dict(r) for r in conn.execute("SELECT * FROM concept_nodes ORDER BY id").fetchall()
        ],
        "problem_nodes": [
            dict(r) for r in conn.execute("SELECT * FROM problem_nodes ORDER BY id").fetchall()
        ],
        "edges": [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM edges ORDER BY from_id, to_id, edge_type"
            ).fetchall()
        ],
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    _emit(text, output)


@export_group.command(name="project")
@click.argument("project_id")
@click.option("--output", "-o", default=None, type=click.Path())
@click.pass_context
@handle_errors
def export_project(ctx, project_id, output):
    """Export a project (references global graph ids; graph not included)."""
    conn = get_conn(ctx)
    project = repo.get_project(conn, project_id)
    treatments = [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM project_concepts WHERE project_id = ? ORDER BY concept_id",
            (project_id,),
        ).fetchall()
    ]
    payload = {
        "format": PROJECT_FORMAT,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "project": project,
        "treatments": treatments,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    _emit(text, output)


# =======================================================================
# Import
# =======================================================================


@click.group(name="import")
def import_group():
    """Import data from JSON."""


def _import_concept(conn, node, on_conflict, stats):
    existing = conn.execute(
        "SELECT 1 FROM concept_nodes WHERE id = ?", (node["id"],)
    ).fetchone()
    if existing:
        if on_conflict == "skip":
            stats["skipped"] += 1
            return
        if on_conflict == "error":
            raise ConflictError(f"concept exists: {node['id']}")
        conn.execute(
            "UPDATE concept_nodes SET content = ? WHERE id = ?",
            (node["content"], node["id"]),
        )
        stats["overwritten"] += 1
    else:
        conn.execute(
            "INSERT INTO concept_nodes (id, content, created_at) VALUES (?, ?, ?)",
            (node["id"], node["content"], node.get("created_at")),
        )
        stats["inserted"] += 1


def _import_problem(conn, node, on_conflict, stats):
    existing = conn.execute(
        "SELECT 1 FROM problem_nodes WHERE id = ?", (node["id"],)
    ).fetchone()
    if existing:
        if on_conflict == "skip":
            stats["skipped"] += 1
            return
        if on_conflict == "error":
            raise ConflictError(f"problem exists: {node['id']}")
        conn.execute(
            "UPDATE problem_nodes SET statement = ?, answer = ? WHERE id = ?",
            (node["statement"], node["answer"], node["id"]),
        )
        stats["overwritten"] += 1
    else:
        conn.execute(
            "INSERT INTO problem_nodes (id, statement, answer, created_at) VALUES (?, ?, ?, ?)",
            (node["id"], node["statement"], node["answer"], node.get("created_at")),
        )
        stats["inserted"] += 1


def _import_edge(conn, edge, on_conflict, stats):
    existing = conn.execute(
        "SELECT 1 FROM edges WHERE from_id = ? AND to_id = ? AND edge_type = ?",
        (edge["from_id"], edge["to_id"], edge["edge_type"]),
    ).fetchone()
    if existing:
        if on_conflict == "skip":
            stats["skipped"] += 1
            return
        if on_conflict == "error":
            raise ConflictError(
                f"edge exists: {edge['from_id']} -> {edge['to_id']} ({edge['edge_type']})"
            )
        stats["skipped"] += 1
        return
    try:
        conn.execute(
            "INSERT INTO edges (from_id, to_id, edge_type, created_at) VALUES (?, ?, ?, ?)",
            (
                edge["from_id"],
                edge["to_id"],
                edge["edge_type"],
                edge.get("created_at"),
            ),
        )
    except sqlite3.IntegrityError as e:
        raise InvalidArgError(f"invalid edge: {edge}") from e
    stats["inserted"] += 1


@import_group.command(name="graph")
@click.argument("path")
@click.option(
    "--on-conflict",
    type=click.Choice(["skip", "overwrite", "error"]),
    default="error",
    help="What to do when an id already exists locally",
)
@click.pass_context
@handle_errors
def import_graph(ctx, path, on_conflict):
    """Import a global graph from a JSON file (or '-' for stdin)."""
    conn = get_conn(ctx)
    payload = _load_payload(path, GRAPH_FORMAT)
    stats = {
        "concept_nodes": {"inserted": 0, "skipped": 0, "overwritten": 0},
        "problem_nodes": {"inserted": 0, "skipped": 0, "overwritten": 0},
        "edges": {"inserted": 0, "skipped": 0},
    }
    with transaction(conn):
        for node in payload.get("concept_nodes", []):
            _import_concept(conn, node, on_conflict, stats["concept_nodes"])
        for node in payload.get("problem_nodes", []):
            _import_problem(conn, node, on_conflict, stats["problem_nodes"])
        for edge in payload.get("edges", []):
            _import_edge(conn, edge, on_conflict, stats["edges"])
        _refresh_id_counters(conn)
    output_ok(stats)


def _insert_project(conn, project, treatments):
    for gid in project.get("goals", []):
        if conn.execute("SELECT 1 FROM problem_nodes WHERE id = ?", (gid,)).fetchone() is None:
            raise NotFoundError(f"goal problem not found: {gid}")
    for t in treatments:
        if conn.execute(
            "SELECT 1 FROM concept_nodes WHERE id = ?", (t["concept_id"],)
        ).fetchone() is None:
            raise NotFoundError(f"treatment concept not found: {t['concept_id']}")

    conn.execute(
        "INSERT INTO projects (id, metadata, created_at) VALUES (?, ?, ?)",
        (project["id"], project.get("metadata", ""), project.get("created_at")),
    )
    for gid in project.get("goals", []):
        conn.execute(
            "INSERT INTO project_goals (project_id, problem_id) VALUES (?, ?)",
            (project["id"], gid),
        )
    for t in treatments:
        conn.execute(
            """
            INSERT INTO project_concepts
                (project_id, concept_id, treatment, reference_content, set_by, set_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                project["id"],
                t["concept_id"],
                t["treatment"],
                t.get("reference_content"),
                t.get("set_by", "learner"),
                t.get("set_at"),
            ),
        )


@import_group.command(name="project")
@click.argument("path")
@click.option(
    "--on-conflict",
    type=click.Choice(["skip", "overwrite", "error"]),
    default="error",
)
@click.pass_context
@handle_errors
def import_project(ctx, path, on_conflict):
    """Import a project from a JSON file (or '-' for stdin)."""
    conn = get_conn(ctx)
    payload = _load_payload(path, PROJECT_FORMAT)
    project = payload["project"]
    treatments = payload.get("treatments", [])
    pid = project["id"]

    existing = conn.execute("SELECT 1 FROM projects WHERE id = ?", (pid,)).fetchone()
    if existing:
        if on_conflict == "skip":
            output_ok({"skipped": True, "project_id": pid})
            return
        if on_conflict == "error":
            raise ConflictError(f"project exists: {pid}")
        with transaction(conn):
            conn.execute("DELETE FROM projects WHERE id = ?", (pid,))
            _insert_project(conn, project, treatments)
            _refresh_id_counters(conn)
        output_ok({"overwritten": True, "project_id": pid})
        return

    with transaction(conn):
        _insert_project(conn, project, treatments)
        _refresh_id_counters(conn)
    output_ok({"inserted": True, "project_id": pid})


def register(cli_group):
    cli_group.add_command(export_group)
    cli_group.add_command(import_group)
