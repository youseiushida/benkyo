"""Graph visualization format conversion (DOT, Mermaid)."""

from typing import Any


def _truncate(text: str, max_len: int = 60) -> str:
    """Shorten text for use as a node label."""
    text = text.replace("\n", " ").strip()
    if len(text) > max_len:
        return text[: max_len - 1] + "…"
    return text


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
            label = _truncate(node["statement"])
            lines.append(
                f'    "{node_id}" [label="{_dot_escape(label)}", '
                f'shape=box, style=rounded];'
            )
        elif node["type"] == "concept":
            content = _truncate(node["content"])
            if node["treatment"] == "blackbox":
                lines.append(
                    f'    "{node_id}" [label="{_dot_escape(content)}\\n[blackbox]", '
                    f'shape=cylinder, style=filled, fillcolor="lightgrey"];'
                )
            else:
                lines.append(
                    f'    "{node_id}" [label="{_dot_escape(content)}", shape=box];'
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
        - related: -.->
    """
    lines = ["graph TD"]

    for node in window_data["nodes"]:
        node_id = node["id"]
        if node["type"] == "problem":
            label = _truncate(node["statement"])
            lines.append(f'    {node_id}(["{_mermaid_escape(label)}"])')
        elif node["type"] == "concept":
            content = _truncate(node["content"])
            if node["treatment"] == "blackbox":
                lines.append(
                    f'    {node_id}[("{_mermaid_escape(content)} [blackbox]")]'
                )
            else:
                lines.append(f'    {node_id}["{_mermaid_escape(content)}"]')

    for edge in window_data["edges"]:
        from_id, to_id, etype = edge["from"], edge["to"], edge["type"]
        if etype == "prereq":
            lines.append(f"    {from_id} --> {to_id}")
        elif etype == "related":
            lines.append(f"    {from_id} -.-> {to_id}")

    return "\n".join(lines)
