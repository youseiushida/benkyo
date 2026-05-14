"""Graph visualization format conversion (DOT, Mermaid)."""

from typing import Any


def _truncate(text: str, max_len: int = 60) -> str:
    """Shorten text for use as a node label."""
    text = text.replace("\n", " ").strip()
    if len(text) > max_len:
        return text[: max_len - 1] + "…"
    return text


def _concept_label(node: dict[str, Any]) -> str:
    """Short display label for a concept node (name → fallback to truncated content)."""
    name = (node.get("name") or "").strip()
    return name if name else _truncate(node["content"])


# ---------------------------------------------------------------------------
# DOT (Graphviz)
# ---------------------------------------------------------------------------


def _dot_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def to_dot(window_data: dict[str, Any], graph_name: str = "benkyo") -> str:
    """Convert window data to Graphviz DOT format."""
    lines = [f'digraph "{graph_name}" {{']
    lines.append("    rankdir=TB;")
    lines.append('    node [fontname="sans-serif"];')
    lines.append('    edge [fontname="sans-serif"];')

    for node in window_data["nodes"]:
        node_id = node["id"]
        if node["type"] == "problem":
            label = _dot_escape(_truncate(node["statement"], 40))
            lines.append(
                f'    "{node_id}" [label="{label}", '
                f'shape=box, style="rounded,filled", fillcolor="#f0f4ff"];'
            )
        elif node["type"] == "concept":
            label = _dot_escape(_concept_label(node))
            if node["treatment"] == "blackbox":
                lines.append(
                    f'    "{node_id}" [label="{label}", '
                    f'shape=box, style=filled, fillcolor="#fde68a", '
                    f'color="#d97706", penwidth=2];'
                )
            else:
                lines.append(
                    f'    "{node_id}" [label="{label}", '
                    f'shape=box, style=filled, fillcolor="#dbeafe", color="#3b82f6"];'
                )

    for edge in window_data["edges"]:
        from_id, to_id, etype = edge["from"], edge["to"], edge["type"]
        if etype == "prereq":
            lines.append(f'    "{from_id}" -> "{to_id}";')
        elif etype == "related":
            lines.append(
                f'    "{from_id}" -> "{to_id}" '
                '[dir=none, style=dashed, color="grey", label="related"];'
            )

    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mermaid
# ---------------------------------------------------------------------------


def _mermaid_escape(text: str) -> str:
    """Escape dangerous chars inside Mermaid labels using HTML entities."""
    return (
        text.replace("\\", "\\\\")
        .replace('"', "&quot;")
        .replace("#", "&#35;")
    )


def to_mermaid(window_data: dict[str, Any]) -> str:
    """Convert window data to Mermaid graph format.

    Shape conventions:
        - problem node: ([...])  stadium
        - whitebox concept: [...]   rectangle
        - blackbox concept: [(...)] cylinder (suggests "stored reference")

    Edge conventions:
        - prereq:  -->
        - related: -.-  (undirected dashed — symmetric "easy to confuse" relationship)

    Treatment styling:
        - blackbox nodes get classDef fill to distinguish at a glance
    """
    lines = ["graph TD"]
    blackbox_ids: list[str] = []

    problem_ids: list[str] = []
    whitebox_ids: list[str] = []

    for node in window_data["nodes"]:
        node_id = node["id"]
        if node["type"] == "problem":
            label = _mermaid_escape(_truncate(node["statement"], 40))
            lines.append(f'    {node_id}(["{label}"])')
            problem_ids.append(node_id)
        elif node["type"] == "concept":
            label = _mermaid_escape(_concept_label(node))
            lines.append(f'    {node_id}["{label}"]')
            if node["treatment"] == "blackbox":
                blackbox_ids.append(node_id)
            else:
                whitebox_ids.append(node_id)

    for edge in window_data["edges"]:
        from_id, to_id, etype = edge["from"], edge["to"], edge["type"]
        if etype == "prereq":
            lines.append(f"    {from_id} --> {to_id}")
        elif etype == "related":
            lines.append(f"    {from_id} -.- {to_id}")

    if window_data["nodes"]:
        lines.append(
            "    classDef problem  fill:#f0f4ff,stroke:#6b7280,stroke-width:1px"
        )
        lines.append(
            "    classDef whitebox fill:#dbeafe,stroke:#3b82f6,stroke-width:1px"
        )
        lines.append(
            "    classDef blackbox fill:#fde68a,stroke:#d97706,stroke-width:2px"
        )
        if problem_ids:
            lines.append(f"    class {','.join(problem_ids)} problem")
        if whitebox_ids:
            lines.append(f"    class {','.join(whitebox_ids)} whitebox")
        if blackbox_ids:
            lines.append(f"    class {','.join(blackbox_ids)} blackbox")

    return "\n".join(lines)
