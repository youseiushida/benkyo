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
                "content": "RLC回路の微分方程式",
                "treatment": "conceptual",
            },
            {
                "id": "c2",
                "type": "concept",
                "content": "ラプラス変換",
                "treatment": "procedural",
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

    def test_procedural_has_marker(self):
        dot = render.to_dot(_sample_window())
        assert "[procedural]" in dot

    def test_problem_label_is_statement(self):
        dot = render.to_dot(_sample_window())
        assert "RLC直列回路の電流を求めよ" in dot

    def test_dependency_edges(self):
        dot = render.to_dot(_sample_window())
        assert '"p1" -> "c1"' in dot

    def test_relation_edges_dashed(self):
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
                    "treatment": "conceptual",
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

    def test_conceptual_uses_rectangle(self):
        mm = render.to_mermaid(_sample_window())
        assert "c1[" in mm and "c1[(" not in mm

    def test_procedural_uses_cylinder(self):
        mm = render.to_mermaid(_sample_window())
        assert "c2[(" in mm

    def test_dependency_edges(self):
        mm = render.to_mermaid(_sample_window())
        assert "p1 --> c1" in mm

    def test_relation_edges_dotted(self):
        mm = render.to_mermaid(_sample_window())
        assert "-.->" in mm

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
                    "treatment": "conceptual",
                }
            ],
            "edges": [],
            "node_count": 1,
            "edge_count": 0,
        }
        mm = render.to_mermaid(window)
        assert "&quot;" in mm
