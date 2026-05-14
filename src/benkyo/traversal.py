"""Graph traversal: window, breakdown, frontier, ancestors."""

import sqlite3
from typing import Any

from benkyo import repository as repo
from benkyo.errors import NotFoundError
from benkyo.ids import CONCEPT_PREFIX, PROBLEM_PREFIX, parse_id


def _node_payload(
    conn: sqlite3.Connection,
    project_id: str,
    node_id: str,
    treatment_cache: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return the full payload for a node (concepts include their treatment)."""
    try:
        prefix, _ = parse_id(node_id)
    except ValueError as e:
        raise NotFoundError(f"invalid node id: {node_id}") from e

    if prefix == CONCEPT_PREFIX:
        cdata = repo.get_concept(conn, node_id)
        if treatment_cache is not None and node_id in treatment_cache:
            t = treatment_cache[node_id]
        else:
            t = repo.get_treatment(conn, project_id, node_id)
            if treatment_cache is not None:
                treatment_cache[node_id] = t
        return {
            "id": node_id,
            "type": "concept",
            "name": cdata.get("name"),
            "content": cdata["content"],
            "treatment": t["treatment"],
            "reference_content": t.get("reference_content"),
        }
    if prefix == PROBLEM_PREFIX:
        pdata = repo.get_problem(conn, node_id)
        return {
            "id": node_id,
            "type": "problem",
            "name": pdata.get("name"),
            "statement": pdata["statement"],
            "answer": pdata["answer"],
        }
    raise NotFoundError(f"id is not a node: {node_id}")


def window(conn: sqlite3.Connection, project_id: str) -> dict[str, Any]:
    """Return the project's entire window.

    Traversal starts from the project's goals and follows prereq edges.
    Blackbox-treated concepts act as terminals (included in the result but
    their outgoing edges are not followed).
    """
    project = repo.get_project(conn, project_id)
    goal_ids = project["goals"]

    visited: set[str] = set(goal_ids)
    queue: list[str] = list(goal_ids)
    treatment_cache: dict[str, dict[str, Any]] = {}

    while queue:
        current = queue.pop(0)

        # blackbox concepts are terminals
        if current.startswith(CONCEPT_PREFIX):
            if current not in treatment_cache:
                treatment_cache[current] = repo.get_treatment(
                    conn, project_id, current
                )
            if treatment_cache[current]["treatment"] == "blackbox":
                continue

        # follow outgoing prereq edges
        rows = conn.execute(
            "SELECT to_id FROM edges WHERE from_id = ? AND edge_type = 'prereq'",
            (current,),
        ).fetchall()
        for row in rows:
            to_id = row["to_id"]
            if to_id not in visited:
                visited.add(to_id)
                queue.append(to_id)

    # collect full node payloads
    nodes = [
        _node_payload(conn, project_id, nid, treatment_cache)
        for nid in sorted(visited)
    ]

    # collect all edges (prereq + related) between in-window nodes
    node_list = sorted(visited)
    edges: list[dict[str, Any]] = []
    if node_list:
        placeholders = ",".join("?" * len(node_list))
        edge_rows = conn.execute(
            f"""SELECT from_id, to_id, edge_type FROM edges
                WHERE from_id IN ({placeholders})
                AND to_id IN ({placeholders})
                ORDER BY from_id, to_id, edge_type""",
            (*node_list, *node_list),
        ).fetchall()
        edges = [
            {"from": r["from_id"], "to": r["to_id"], "type": r["edge_type"]}
            for r in edge_rows
        ]

    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


def project_scope(conn: sqlite3.Connection, project_id: str) -> dict[str, Any]:
    """BFS from (goals ∪ explicit project_concepts) without the blackbox-terminal rule.

    Seeds: project_goals + all concepts with an explicit treatment row.
    This gives every node the project has intentionally registered, plus
    their full prereq chains (blackbox does not terminate traversal).
    Unlike --scope graph, nodes belonging only to other projects are excluded.
    """
    project = repo.get_project(conn, project_id)

    explicit_concept_ids = {
        r["concept_id"]
        for r in conn.execute(
            "SELECT concept_id FROM project_concepts WHERE project_id = ?",
            (project_id,),
        ).fetchall()
    }
    seeds = set(project["goals"]) | explicit_concept_ids

    visited: set[str] = set(seeds)
    queue: list[str] = list(seeds)

    while queue:
        current = queue.pop(0)
        rows = conn.execute(
            "SELECT to_id FROM edges WHERE from_id = ? AND edge_type = 'prereq'",
            (current,),
        ).fetchall()
        for row in rows:
            to_id = row["to_id"]
            if to_id not in visited:
                visited.add(to_id)
                queue.append(to_id)

    treatment_cache: dict[str, dict[str, Any]] = {}
    nodes = [
        _node_payload(conn, project_id, nid, treatment_cache)
        for nid in sorted(visited)
    ]

    edges: list[dict[str, Any]] = []
    if visited:
        node_list = sorted(visited)
        placeholders = ",".join("?" * len(node_list))
        edge_rows = conn.execute(
            f"""SELECT from_id, to_id, edge_type FROM edges
                WHERE from_id IN ({placeholders})
                AND to_id IN ({placeholders})
                ORDER BY from_id, to_id, edge_type""",
            (*node_list, *node_list),
        ).fetchall()
        edges = [
            {"from": r["from_id"], "to": r["to_id"], "type": r["edge_type"]}
            for r in edge_rows
        ]

    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


def graph_scope(conn: sqlite3.Connection, project_id: str) -> dict[str, Any]:
    """Return the entire global graph with treatments from project_id."""
    repo.get_project(conn, project_id)  # validates project

    concept_ids = [
        r["id"]
        for r in conn.execute("SELECT id FROM concept_nodes ORDER BY id").fetchall()
    ]
    problem_ids = [
        r["id"]
        for r in conn.execute("SELECT id FROM problem_nodes ORDER BY id").fetchall()
    ]

    treatment_cache: dict[str, dict[str, Any]] = {}
    nodes = [
        _node_payload(conn, project_id, nid, treatment_cache)
        for nid in sorted(concept_ids + problem_ids)
    ]

    edge_rows = conn.execute(
        "SELECT from_id, to_id, edge_type FROM edges ORDER BY from_id, to_id, edge_type"
    ).fetchall()
    edges = [
        {"from": r["from_id"], "to": r["to_id"], "type": r["edge_type"]}
        for r in edge_rows
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


def breakdown(
    conn: sqlite3.Connection, project_id: str, node_id: str
) -> list[dict[str, Any]]:
    """List the direct prereq dependencies of the given node, with each
    target's treatment in the project."""
    repo.get_project(conn, project_id)  # validates project
    _node_payload(conn, project_id, node_id)  # validates node

    rows = conn.execute(
        """SELECT to_id FROM edges
           WHERE from_id = ? AND edge_type = 'prereq'
           ORDER BY to_id""",
        (node_id,),
    ).fetchall()

    return [_node_payload(conn, project_id, r["to_id"]) for r in rows]


def frontier(conn: sqlite3.Connection, project_id: str) -> list[dict[str, Any]]:
    """List blackbox-treated concepts within the window (= promotion candidates)."""
    w = window(conn, project_id)
    return [
        node
        for node in w["nodes"]
        if node["type"] == "concept" and node["treatment"] == "blackbox"
    ]


def ancestors(
    conn: sqlite3.Connection, project_id: str, node_id: str
) -> list[dict[str, Any]]:
    """List in-window nodes that depend on the given node."""
    w = window(conn, project_id)
    window_node_ids = {n["id"] for n in w["nodes"]}

    if node_id not in window_node_ids:
        # node is outside the window: no in-window ancestors
        return []

    rows = conn.execute(
        """SELECT from_id FROM edges
           WHERE to_id = ? AND edge_type = 'prereq'
           ORDER BY from_id""",
        (node_id,),
    ).fetchall()

    ancestor_ids = [r["from_id"] for r in rows if r["from_id"] in window_node_ids]
    id_to_node = {n["id"]: n for n in w["nodes"]}
    return [id_to_node[aid] for aid in ancestor_ids]
