"""Data access layer: CRUD operations for every entity."""

import sqlite3
from typing import Any

from benkyo.errors import ConflictError, InvalidArgError, NotFoundError
from benkyo.ids import (
    CONCEPT_PREFIX,
    PROBLEM_PREFIX,
    PROJECT_PREFIX,
    next_id,
    parse_id,
)

VALID_EDGE_TYPES = ("prereq", "related")
VALID_TREATMENTS = ("procedural", "conceptual")
VALID_SET_BY = ("system", "learner", "material")


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]


# =======================================================================
# Node existence helpers
# =======================================================================


def _node_table(node_id: str) -> str:
    """Return the table name corresponding to the prefix of node_id."""
    try:
        prefix, _ = parse_id(node_id)
    except ValueError as e:
        raise InvalidArgError(f"invalid id: {node_id!r}") from e

    if prefix == CONCEPT_PREFIX:
        return "concept_nodes"
    if prefix == PROBLEM_PREFIX:
        return "problem_nodes"
    raise InvalidArgError(f"id is not a node (concept/problem): {node_id!r}")


def _node_exists(conn: sqlite3.Connection, node_id: str) -> bool:
    """True if id exists as a concept or problem node."""
    try:
        table = _node_table(node_id)
    except InvalidArgError:
        return False
    return (
        conn.execute(f"SELECT 1 FROM {table} WHERE id = ?", (node_id,)).fetchone()
        is not None
    )


# =======================================================================
# Concept nodes
# =======================================================================


def create_concept(conn: sqlite3.Connection, content: str) -> dict[str, Any]:
    content = (content or "").strip()
    if not content:
        raise InvalidArgError("content must not be empty")
    new_id = next_id(conn, CONCEPT_PREFIX)
    conn.execute(
        "INSERT INTO concept_nodes (id, content) VALUES (?, ?)",
        (new_id, content),
    )
    return get_concept(conn, new_id)


def get_concept(conn: sqlite3.Connection, concept_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM concept_nodes WHERE id = ?", (concept_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"concept not found: {concept_id}")
    return dict(row)


def update_concept(
    conn: sqlite3.Connection, concept_id: str, content: str
) -> dict[str, Any]:
    content = (content or "").strip()
    if not content:
        raise InvalidArgError("content must not be empty")
    cur = conn.execute(
        "UPDATE concept_nodes SET content = ? WHERE id = ?", (content, concept_id)
    )
    if cur.rowcount == 0:
        raise NotFoundError(f"concept not found: {concept_id}")
    return get_concept(conn, concept_id)


def delete_concept(conn: sqlite3.Connection, concept_id: str) -> dict[str, Any]:
    """Delete a concept. project_concepts and edges (touching this id) cascade."""
    if not _node_exists(conn, concept_id) or not concept_id.startswith(CONCEPT_PREFIX):
        raise NotFoundError(f"concept not found: {concept_id}")
    # count cascade rows before deletion
    pc_count = conn.execute(
        "SELECT COUNT(*) FROM project_concepts WHERE concept_id = ?", (concept_id,)
    ).fetchone()[0]
    edge_count = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE from_id = ? OR to_id = ?",
        (concept_id, concept_id),
    ).fetchone()[0]
    # delete
    conn.execute("DELETE FROM edges WHERE from_id = ? OR to_id = ?", (concept_id, concept_id))
    conn.execute("DELETE FROM concept_nodes WHERE id = ?", (concept_id,))
    return {
        "deleted_id": concept_id,
        "cascade": {"project_concepts": pc_count, "edges": edge_count},
    }


def list_concepts(
    conn: sqlite3.Connection, query: str | None = None
) -> list[dict[str, Any]]:
    if query:
        rows = conn.execute(
            "SELECT * FROM concept_nodes WHERE content LIKE ? ORDER BY id",
            (f"%{query}%",),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM concept_nodes ORDER BY id").fetchall()
    return _rows_to_dicts(rows)


def find_concept_by_content(
    conn: sqlite3.Connection, content: str
) -> list[dict[str, Any]]:
    """Find concepts by exact content match (identity check)."""
    rows = conn.execute(
        "SELECT * FROM concept_nodes WHERE content = ? ORDER BY id", (content,)
    ).fetchall()
    return _rows_to_dicts(rows)


# =======================================================================
# Problem nodes
# =======================================================================


def create_problem(
    conn: sqlite3.Connection, statement: str, answer: str
) -> dict[str, Any]:
    statement = (statement or "").strip()
    answer = (answer or "").strip()
    if not statement:
        raise InvalidArgError("statement must not be empty")
    if not answer:
        raise InvalidArgError("answer must not be empty")
    new_id = next_id(conn, PROBLEM_PREFIX)
    conn.execute(
        "INSERT INTO problem_nodes (id, statement, answer) VALUES (?, ?, ?)",
        (new_id, statement, answer),
    )
    return get_problem(conn, new_id)


def get_problem(conn: sqlite3.Connection, problem_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM problem_nodes WHERE id = ?", (problem_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"problem not found: {problem_id}")
    return dict(row)


def update_problem(
    conn: sqlite3.Connection,
    problem_id: str,
    statement: str | None = None,
    answer: str | None = None,
) -> dict[str, Any]:
    if statement is None and answer is None:
        raise InvalidArgError("nothing to update")

    if not _node_exists(conn, problem_id) or not problem_id.startswith(PROBLEM_PREFIX):
        raise NotFoundError(f"problem not found: {problem_id}")

    if statement is not None:
        statement = statement.strip()
        if not statement:
            raise InvalidArgError("statement must not be empty")
        conn.execute(
            "UPDATE problem_nodes SET statement = ? WHERE id = ?",
            (statement, problem_id),
        )
    if answer is not None:
        answer = answer.strip()
        if not answer:
            raise InvalidArgError("answer must not be empty")
        conn.execute(
            "UPDATE problem_nodes SET answer = ? WHERE id = ?",
            (answer, problem_id),
        )
    return get_problem(conn, problem_id)


def delete_problem(conn: sqlite3.Connection, problem_id: str) -> dict[str, Any]:
    if not _node_exists(conn, problem_id) or not problem_id.startswith(PROBLEM_PREFIX):
        raise NotFoundError(f"problem not found: {problem_id}")
    pg_count = conn.execute(
        "SELECT COUNT(*) FROM project_goals WHERE problem_id = ?", (problem_id,)
    ).fetchone()[0]
    edge_count = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE from_id = ? OR to_id = ?",
        (problem_id, problem_id),
    ).fetchone()[0]
    conn.execute("DELETE FROM edges WHERE from_id = ? OR to_id = ?", (problem_id, problem_id))
    conn.execute("DELETE FROM problem_nodes WHERE id = ?", (problem_id,))
    return {
        "deleted_id": problem_id,
        "cascade": {"project_goals": pg_count, "edges": edge_count},
    }


def list_problems(
    conn: sqlite3.Connection, query: str | None = None
) -> list[dict[str, Any]]:
    if query:
        rows = conn.execute(
            "SELECT * FROM problem_nodes WHERE statement LIKE ? OR answer LIKE ? ORDER BY id",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM problem_nodes ORDER BY id").fetchall()
    return _rows_to_dicts(rows)


# =======================================================================
# Edges
# =======================================================================


def create_edge(
    conn: sqlite3.Connection, from_id: str, to_id: str, edge_type: str
) -> dict[str, Any]:
    if edge_type not in VALID_EDGE_TYPES:
        raise InvalidArgError(
            f"invalid edge_type: {edge_type!r} (must be one of {VALID_EDGE_TYPES})"
        )
    if from_id == to_id:
        raise InvalidArgError(f"self-loop not allowed: {from_id}")
    if not _node_exists(conn, from_id):
        raise NotFoundError(f"from node not found: {from_id}")
    if not _node_exists(conn, to_id):
        raise NotFoundError(f"to node not found: {to_id}")

    try:
        conn.execute(
            "INSERT INTO edges (from_id, to_id, edge_type) VALUES (?, ?, ?)",
            (from_id, to_id, edge_type),
        )
    except sqlite3.IntegrityError as e:
        raise ConflictError(
            f"edge already exists: {from_id} -> {to_id} ({edge_type})"
        ) from e

    row = conn.execute(
        "SELECT * FROM edges WHERE from_id = ? AND to_id = ? AND edge_type = ?",
        (from_id, to_id, edge_type),
    ).fetchone()
    return dict(row)


def delete_edge(
    conn: sqlite3.Connection, from_id: str, to_id: str, edge_type: str
) -> dict[str, Any]:
    if edge_type not in VALID_EDGE_TYPES:
        raise InvalidArgError(f"invalid edge_type: {edge_type!r}")
    cur = conn.execute(
        "DELETE FROM edges WHERE from_id = ? AND to_id = ? AND edge_type = ?",
        (from_id, to_id, edge_type),
    )
    if cur.rowcount == 0:
        raise NotFoundError(
            f"edge not found: {from_id} -> {to_id} ({edge_type})"
        )
    return {"deleted": {"from_id": from_id, "to_id": to_id, "edge_type": edge_type}}


def list_edges(
    conn: sqlite3.Connection,
    from_id: str | None = None,
    to_id: str | None = None,
    edge_type: str | None = None,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM edges WHERE 1=1"
    params: list[Any] = []
    if from_id is not None:
        sql += " AND from_id = ?"
        params.append(from_id)
    if to_id is not None:
        sql += " AND to_id = ?"
        params.append(to_id)
    if edge_type is not None:
        if edge_type not in VALID_EDGE_TYPES:
            raise InvalidArgError(f"invalid edge_type: {edge_type!r}")
        sql += " AND edge_type = ?"
        params.append(edge_type)
    sql += " ORDER BY from_id, to_id, edge_type"
    rows = conn.execute(sql, params).fetchall()
    return _rows_to_dicts(rows)


# =======================================================================
# Projects
# =======================================================================


def create_project(
    conn: sqlite3.Connection,
    metadata: str = "",
    goal_problem_ids: list[str] | None = None,
) -> dict[str, Any]:
    goals = goal_problem_ids or []
    # validate that all goals exist as problem ids
    for pid in goals:
        if not pid.startswith(PROBLEM_PREFIX):
            raise InvalidArgError(f"goal must be a problem id: {pid!r}")
        if not _node_exists(conn, pid):
            raise NotFoundError(f"problem not found: {pid}")

    new_id = next_id(conn, PROJECT_PREFIX)
    conn.execute(
        "INSERT INTO projects (id, metadata) VALUES (?, ?)",
        (new_id, metadata or ""),
    )
    for pid in goals:
        conn.execute(
            "INSERT INTO project_goals (project_id, problem_id) VALUES (?, ?)",
            (new_id, pid),
        )
    return get_project(conn, new_id)


def get_project(conn: sqlite3.Connection, project_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"project not found: {project_id}")
    goals = [
        r["problem_id"]
        for r in conn.execute(
            "SELECT problem_id FROM project_goals WHERE project_id = ? ORDER BY problem_id",
            (project_id,),
        ).fetchall()
    ]
    return {**dict(row), "goals": goals}


def update_project(
    conn: sqlite3.Connection,
    project_id: str,
    metadata: str | None = None,
    goal_problem_ids: list[str] | None = None,
) -> dict[str, Any]:
    if metadata is None and goal_problem_ids is None:
        raise InvalidArgError("nothing to update")
    # existence check
    if conn.execute(
        "SELECT 1 FROM projects WHERE id = ?", (project_id,)
    ).fetchone() is None:
        raise NotFoundError(f"project not found: {project_id}")

    if metadata is not None:
        conn.execute(
            "UPDATE projects SET metadata = ? WHERE id = ?", (metadata, project_id)
        )

    if goal_problem_ids is not None:
        # validate that all goals exist
        for pid in goal_problem_ids:
            if not pid.startswith(PROBLEM_PREFIX):
                raise InvalidArgError(f"goal must be a problem id: {pid!r}")
            if not _node_exists(conn, pid):
                raise NotFoundError(f"problem not found: {pid}")
        # clear existing goals and re-insert
        conn.execute("DELETE FROM project_goals WHERE project_id = ?", (project_id,))
        for pid in goal_problem_ids:
            conn.execute(
                "INSERT INTO project_goals (project_id, problem_id) VALUES (?, ?)",
                (project_id, pid),
            )

    return get_project(conn, project_id)


def delete_project(conn: sqlite3.Connection, project_id: str) -> dict[str, Any]:
    if conn.execute(
        "SELECT 1 FROM projects WHERE id = ?", (project_id,)
    ).fetchone() is None:
        raise NotFoundError(f"project not found: {project_id}")
    pc_count = conn.execute(
        "SELECT COUNT(*) FROM project_concepts WHERE project_id = ?", (project_id,)
    ).fetchone()[0]
    pg_count = conn.execute(
        "SELECT COUNT(*) FROM project_goals WHERE project_id = ?", (project_id,)
    ).fetchone()[0]
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    return {
        "deleted_id": project_id,
        "cascade": {"project_concepts": pc_count, "project_goals": pg_count},
    }


def list_projects(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT * FROM projects ORDER BY id").fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["goals"] = [
            r["problem_id"]
            for r in conn.execute(
                "SELECT problem_id FROM project_goals WHERE project_id = ? ORDER BY problem_id",
                (d["id"],),
            ).fetchall()
        ]
        result.append(d)
    return result


# =======================================================================
# Project-concept treatments
# =======================================================================


def set_treatment(
    conn: sqlite3.Connection,
    project_id: str,
    concept_id: str,
    treatment: str,
    reference_content: str | None = None,
    set_by: str = "learner",
) -> dict[str, Any]:
    if treatment not in VALID_TREATMENTS:
        raise InvalidArgError(f"invalid treatment: {treatment!r}")
    if set_by not in VALID_SET_BY:
        raise InvalidArgError(f"invalid set_by: {set_by!r}")

    if conn.execute(
        "SELECT 1 FROM projects WHERE id = ?", (project_id,)
    ).fetchone() is None:
        raise NotFoundError(f"project not found: {project_id}")
    if conn.execute(
        "SELECT 1 FROM concept_nodes WHERE id = ?", (concept_id,)
    ).fetchone() is None:
        raise NotFoundError(f"concept not found: {concept_id}")

    # null out reference_content for conceptual treatment to avoid confusion
    ref = reference_content if treatment == "procedural" else None

    conn.execute(
        """
        INSERT INTO project_concepts (project_id, concept_id, treatment, reference_content, set_by, set_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(project_id, concept_id) DO UPDATE SET
            treatment = excluded.treatment,
            reference_content = excluded.reference_content,
            set_by = excluded.set_by,
            set_at = excluded.set_at
        """,
        (project_id, concept_id, treatment, ref, set_by),
    )
    return get_treatment(conn, project_id, concept_id)


def get_treatment(
    conn: sqlite3.Connection, project_id: str, concept_id: str
) -> dict[str, Any]:
    """Get treatment. If unset, return 'conceptual' with default=True."""
    if conn.execute(
        "SELECT 1 FROM projects WHERE id = ?", (project_id,)
    ).fetchone() is None:
        raise NotFoundError(f"project not found: {project_id}")
    if conn.execute(
        "SELECT 1 FROM concept_nodes WHERE id = ?", (concept_id,)
    ).fetchone() is None:
        raise NotFoundError(f"concept not found: {concept_id}")

    row = conn.execute(
        "SELECT * FROM project_concepts WHERE project_id = ? AND concept_id = ?",
        (project_id, concept_id),
    ).fetchone()
    if row is None:
        return {
            "project_id": project_id,
            "concept_id": concept_id,
            "treatment": "conceptual",
            "reference_content": None,
            "set_by": None,
            "set_at": None,
            "default": True,
        }
    return {**dict(row), "default": False}


def unset_treatment(
    conn: sqlite3.Connection, project_id: str, concept_id: str
) -> dict[str, Any]:
    cur = conn.execute(
        "DELETE FROM project_concepts WHERE project_id = ? AND concept_id = ?",
        (project_id, concept_id),
    )
    if cur.rowcount == 0:
        # already at default state; not an error (idempotent)
        return {"removed": False, "already_default": True}
    return {"removed": True}


def list_treatments(
    conn: sqlite3.Connection, project_id: str, treatment: str | None = None
) -> list[dict[str, Any]]:
    if conn.execute(
        "SELECT 1 FROM projects WHERE id = ?", (project_id,)
    ).fetchone() is None:
        raise NotFoundError(f"project not found: {project_id}")
    sql = "SELECT * FROM project_concepts WHERE project_id = ?"
    params: list[Any] = [project_id]
    if treatment is not None:
        if treatment not in VALID_TREATMENTS:
            raise InvalidArgError(f"invalid treatment: {treatment!r}")
        sql += " AND treatment = ?"
        params.append(treatment)
    sql += " ORDER BY concept_id"
    rows = conn.execute(sql, params).fetchall()
    return _rows_to_dicts(rows)


# =======================================================================
# Merge / fork
# =======================================================================


VALID_MERGE_CONFLICTS = ("error", "keep_canonical", "keep_source")


def _redirect_edges(
    conn: sqlite3.Connection, source_id: str, canonical_id: str
) -> tuple[int, int]:
    """Redirect all edges referencing source_id to canonical_id.

    Returns (redirected, skipped). Skipped covers self-loops and duplicates
    that would arise after redirection.
    """
    redirected = 0
    skipped = 0

    # 1. Edges where source is from
    rows = conn.execute(
        "SELECT to_id, edge_type FROM edges WHERE from_id = ?", (source_id,)
    ).fetchall()
    for row in rows:
        to_id = row["to_id"]
        etype = row["edge_type"]
        conn.execute(
            "DELETE FROM edges WHERE from_id = ? AND to_id = ? AND edge_type = ?",
            (source_id, to_id, etype),
        )
        if canonical_id == to_id:
            skipped += 1
            continue
        exists = conn.execute(
            "SELECT 1 FROM edges WHERE from_id = ? AND to_id = ? AND edge_type = ?",
            (canonical_id, to_id, etype),
        ).fetchone()
        if exists:
            skipped += 1
            continue
        conn.execute(
            "INSERT INTO edges (from_id, to_id, edge_type) VALUES (?, ?, ?)",
            (canonical_id, to_id, etype),
        )
        redirected += 1

    # 2. Edges where source is to
    rows = conn.execute(
        "SELECT from_id, edge_type FROM edges WHERE to_id = ?", (source_id,)
    ).fetchall()
    for row in rows:
        from_id = row["from_id"]
        etype = row["edge_type"]
        conn.execute(
            "DELETE FROM edges WHERE from_id = ? AND to_id = ? AND edge_type = ?",
            (from_id, source_id, etype),
        )
        if from_id == canonical_id:
            skipped += 1
            continue
        exists = conn.execute(
            "SELECT 1 FROM edges WHERE from_id = ? AND to_id = ? AND edge_type = ?",
            (from_id, canonical_id, etype),
        ).fetchone()
        if exists:
            skipped += 1
            continue
        conn.execute(
            "INSERT INTO edges (from_id, to_id, edge_type) VALUES (?, ?, ?)",
            (from_id, canonical_id, etype),
        )
        redirected += 1

    return redirected, skipped


def merge_concept(
    conn: sqlite3.Connection,
    source_id: str,
    canonical_id: str,
    on_conflict: str = "error",
) -> dict[str, Any]:
    """Merge source concept into canonical. Edges and project_concepts redirect.

    on_conflict controls behavior when both source and canonical have
    project_concepts rows for the same project:
        - "error": raise ConflictError
        - "keep_canonical": discard source's row, keep canonical's
        - "keep_source": discard canonical's row, redirect source's to canonical
    """
    if on_conflict not in VALID_MERGE_CONFLICTS:
        raise InvalidArgError(
            f"invalid on_conflict: {on_conflict!r} (must be one of {VALID_MERGE_CONFLICTS})"
        )
    if source_id == canonical_id:
        raise InvalidArgError(f"source and canonical are the same: {source_id}")
    if not source_id.startswith(CONCEPT_PREFIX):
        raise InvalidArgError(f"source must be a concept id: {source_id!r}")
    if not canonical_id.startswith(CONCEPT_PREFIX):
        raise InvalidArgError(f"canonical must be a concept id: {canonical_id!r}")
    for cid in (source_id, canonical_id):
        if conn.execute(
            "SELECT 1 FROM concept_nodes WHERE id = ?", (cid,)
        ).fetchone() is None:
            raise NotFoundError(f"concept not found: {cid}")

    edges_redirected, edges_skipped = _redirect_edges(conn, source_id, canonical_id)

    treatments_redirected = 0
    treatments_skipped = 0

    rows = conn.execute(
        "SELECT * FROM project_concepts WHERE concept_id = ?", (source_id,)
    ).fetchall()
    for row in rows:
        project_id = row["project_id"]
        existing = conn.execute(
            "SELECT 1 FROM project_concepts WHERE project_id = ? AND concept_id = ?",
            (project_id, canonical_id),
        ).fetchone()
        if existing is None:
            conn.execute(
                "UPDATE project_concepts SET concept_id = ? "
                "WHERE project_id = ? AND concept_id = ?",
                (canonical_id, project_id, source_id),
            )
            treatments_redirected += 1
        else:
            if on_conflict == "error":
                raise ConflictError(
                    f"both source ({source_id}) and canonical ({canonical_id}) "
                    f"have treatment in project {project_id}; pass --on-conflict"
                )
            if on_conflict == "keep_canonical":
                conn.execute(
                    "DELETE FROM project_concepts "
                    "WHERE project_id = ? AND concept_id = ?",
                    (project_id, source_id),
                )
                treatments_skipped += 1
            else:  # keep_source
                conn.execute(
                    "DELETE FROM project_concepts "
                    "WHERE project_id = ? AND concept_id = ?",
                    (project_id, canonical_id),
                )
                conn.execute(
                    "UPDATE project_concepts SET concept_id = ? "
                    "WHERE project_id = ? AND concept_id = ?",
                    (canonical_id, project_id, source_id),
                )
                treatments_redirected += 1

    conn.execute("DELETE FROM concept_nodes WHERE id = ?", (source_id,))

    return {
        "merged_source": source_id,
        "into_canonical": canonical_id,
        "edges_redirected": edges_redirected,
        "edges_skipped": edges_skipped,
        "treatments_redirected": treatments_redirected,
        "treatments_skipped": treatments_skipped,
    }


def merge_problem(
    conn: sqlite3.Connection,
    source_id: str,
    canonical_id: str,
) -> dict[str, Any]:
    """Merge source problem into canonical. Edges and project_goals redirect.

    Problems don't have project_concepts entries (those are for concepts), so
    there's no treatment conflict possible. Project goals (problem references)
    are simply deduplicated.
    """
    if source_id == canonical_id:
        raise InvalidArgError(f"source and canonical are the same: {source_id}")
    if not source_id.startswith(PROBLEM_PREFIX):
        raise InvalidArgError(f"source must be a problem id: {source_id!r}")
    if not canonical_id.startswith(PROBLEM_PREFIX):
        raise InvalidArgError(f"canonical must be a problem id: {canonical_id!r}")
    for pid in (source_id, canonical_id):
        if conn.execute(
            "SELECT 1 FROM problem_nodes WHERE id = ?", (pid,)
        ).fetchone() is None:
            raise NotFoundError(f"problem not found: {pid}")

    edges_redirected, edges_skipped = _redirect_edges(conn, source_id, canonical_id)

    goals_redirected = 0
    goals_skipped = 0

    rows = conn.execute(
        "SELECT project_id FROM project_goals WHERE problem_id = ?", (source_id,)
    ).fetchall()
    for row in rows:
        project_id = row["project_id"]
        existing = conn.execute(
            "SELECT 1 FROM project_goals WHERE project_id = ? AND problem_id = ?",
            (project_id, canonical_id),
        ).fetchone()
        if existing is None:
            conn.execute(
                "UPDATE project_goals SET problem_id = ? "
                "WHERE project_id = ? AND problem_id = ?",
                (canonical_id, project_id, source_id),
            )
            goals_redirected += 1
        else:
            conn.execute(
                "DELETE FROM project_goals "
                "WHERE project_id = ? AND problem_id = ?",
                (project_id, source_id),
            )
            goals_skipped += 1

    conn.execute("DELETE FROM problem_nodes WHERE id = ?", (source_id,))

    return {
        "merged_source": source_id,
        "into_canonical": canonical_id,
        "edges_redirected": edges_redirected,
        "edges_skipped": edges_skipped,
        "goals_redirected": goals_redirected,
        "goals_skipped": goals_skipped,
    }


def fork_concept(
    conn: sqlite3.Connection,
    source_id: str,
    content: str | None = None,
) -> dict[str, Any]:
    """Create a new concept whose edges mirror those of source.

    Treatments are NOT copied — the new concept starts with default (conceptual)
    in every project. This is intentional: treatments are project-specific
    judgments that should be re-considered after a split.

    If content is None, copies the source's content verbatim.
    """
    if not source_id.startswith(CONCEPT_PREFIX):
        raise InvalidArgError(f"source must be a concept id: {source_id!r}")
    src = conn.execute(
        "SELECT * FROM concept_nodes WHERE id = ?", (source_id,)
    ).fetchone()
    if src is None:
        raise NotFoundError(f"concept not found: {source_id}")

    new_content = content.strip() if content else src["content"]
    if not new_content:
        raise InvalidArgError("content must not be empty")

    new_id = next_id(conn, CONCEPT_PREFIX)
    conn.execute(
        "INSERT INTO concept_nodes (id, content) VALUES (?, ?)",
        (new_id, new_content),
    )

    edges_copied = 0
    # Copy out-edges
    rows = conn.execute(
        "SELECT to_id, edge_type FROM edges WHERE from_id = ?", (source_id,)
    ).fetchall()
    for row in rows:
        if row["to_id"] == new_id:
            continue
        try:
            conn.execute(
                "INSERT INTO edges (from_id, to_id, edge_type) VALUES (?, ?, ?)",
                (new_id, row["to_id"], row["edge_type"]),
            )
            edges_copied += 1
        except sqlite3.IntegrityError:
            pass

    # Copy in-edges
    rows = conn.execute(
        "SELECT from_id, edge_type FROM edges WHERE to_id = ?", (source_id,)
    ).fetchall()
    for row in rows:
        if row["from_id"] == new_id:
            continue
        try:
            conn.execute(
                "INSERT INTO edges (from_id, to_id, edge_type) VALUES (?, ?, ?)",
                (row["from_id"], new_id, row["edge_type"]),
            )
            edges_copied += 1
        except sqlite3.IntegrityError:
            pass

    return {
        "forked_from": source_id,
        "new_id": new_id,
        "edges_copied": edges_copied,
    }
