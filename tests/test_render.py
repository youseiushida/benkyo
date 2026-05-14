"""render モジュール (DOT, Mermaid 変換) のテスト."""

from benkyo import render


def _sample_window():
    return {
        "nodes": [
            {
                "id": "p1",
                "type": "problem",
                "statement": "RLC直列回路の電流を求めよ",
                "answer": "i(t) = ...",
            },
            {
                "id": "c1",
                "type": "concept",
                "name": "RLC回路",
                "content": "RLC回路の微分方程式: ...",
                "treatment": "whitebox",
            },
            {
                "id": "c2",
                "type": "concept",
                "name": "ラプラス変換",
                "content": "ラプラス変換: 時間関数 f(t) を ...",
                "treatment": "blackbox",
                "reference_content": "変換表",
            },
        ],
        "edges": [
            {"from": "p1", "to": "c1", "type": "prereq"},
            {"from": "c1", "to": "c2", "type": "prereq"},
            {"from": "c1", "to": "c2", "type": "related"},
        ],
        "node_count": 3,
        "edge_count": 3,
    }


def _sample_window_no_name():
    """Nodes without name field — render should fall back to truncated content."""
    return {
        "nodes": [
            {
                "id": "c1",
                "type": "concept",
                "content": "RLC回路の微分方程式",
                "treatment": "whitebox",
            },
        ],
        "edges": [],
        "node_count": 1,
        "edge_count": 0,
    }


# ---- DOT ----


class TestDot:
    def test_basic_structure(self):
        dot = render.to_dot(_sample_window())
        assert dot.startswith("digraph")
        assert dot.rstrip().endswith("}")

    def test_includes_all_nodes(self):
        dot = render.to_dot(_sample_window())
        for nid in ("p1", "c1", "c2"):
            assert f'"{nid}"' in dot

    def test_blackbox_has_marker(self):
        dot = render.to_dot(_sample_window())
        assert "[blackbox]" in dot

    def test_concept_label_uses_name(self):
        dot = render.to_dot(_sample_window())
        assert "RLC回路" in dot
        assert "ラプラス変換" in dot

    def test_concept_label_fallback_to_content(self):
        dot = render.to_dot(_sample_window_no_name())
        assert "RLC回路の微分方程式" in dot

    def test_problem_label_is_statement(self):
        dot = render.to_dot(_sample_window())
        assert "RLC直列回路の電流を求めよ" in dot

    def test_dependency_edges(self):
        dot = render.to_dot(_sample_window())
        assert '"p1" -> "c1"' in dot

    def test_relation_edges_undirected(self):
        dot = render.to_dot(_sample_window())
        assert "dir=none" in dot
        assert "dashed" in dot

    def test_special_chars_escaped(self):
        window = {
            "nodes": [
                {
                    "id": "c1",
                    "type": "concept",
                    "content": 'quote "in content"',
                    "treatment": "whitebox",
                }
            ],
            "edges": [],
            "node_count": 1,
            "edge_count": 0,
        }
        dot = render.to_dot(window)
        assert '\\"' in dot

    def test_empty_window(self):
        dot = render.to_dot({"nodes": [], "edges": [], "node_count": 0, "edge_count": 0})
        assert "digraph" in dot
        assert "}" in dot


# ---- Mermaid ----


class TestMermaid:
    def test_basic_structure(self):
        mm = render.to_mermaid(_sample_window())
        assert mm.startswith("graph TD")

    def test_problem_uses_stadium_shape(self):
        mm = render.to_mermaid(_sample_window())
        assert "p1([" in mm

    def test_whitebox_uses_rectangle(self):
        mm = render.to_mermaid(_sample_window())
        assert "c1[" in mm and "c1[(" not in mm

    def test_blackbox_uses_cylinder(self):
        mm = render.to_mermaid(_sample_window())
        assert "c2[(" in mm

    def test_concept_label_uses_name(self):
        mm = render.to_mermaid(_sample_window())
        assert "RLC回路" in mm
        assert "ラプラス変換" in mm

    def test_concept_label_fallback_to_content(self):
        mm = render.to_mermaid(_sample_window_no_name())
        assert "RLC回路の微分方程式" in mm

    def test_dependency_edges(self):
        mm = render.to_mermaid(_sample_window())
        assert "p1 --> c1" in mm

    def test_relation_edges_undirected_dashed(self):
        mm = render.to_mermaid(_sample_window())
        assert "c1 -.- c2" in mm
        assert "c1 -.-> c2" not in mm

    def test_blackbox_classdef_present(self):
        mm = render.to_mermaid(_sample_window())
        assert "classDef blackbox" in mm
        assert "class c2 blackbox" in mm

    def test_no_class_assignment_when_no_blackbox(self):
        window = {
            "nodes": [
                {"id": "c1", "type": "concept", "content": "A", "treatment": "whitebox"}
            ],
            "edges": [],
            "node_count": 1,
            "edge_count": 0,
        }
        mm = render.to_mermaid(window)
        assert "classDef blackbox" in mm
        assert "class c1 blackbox" not in mm

    def test_empty_window(self):
        mm = render.to_mermaid({"nodes": [], "edges": [], "node_count": 0, "edge_count": 0})
        assert mm == "graph TD"

    def test_quote_escaped(self):
        window = {
            "nodes": [
                {
                    "id": "c1",
                    "type": "concept",
                    "content": 'has "quotes"',
                    "treatment": "whitebox",
                }
            ],
            "edges": [],
            "node_count": 1,
            "edge_count": 0,
        }
        mm = render.to_mermaid(window)
        assert "&quot;" in mm
