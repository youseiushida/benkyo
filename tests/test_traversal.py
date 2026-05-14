"""トラバーサル (window, breakdown, frontier, ancestors) のテスト."""

import pytest

from benkyo import repository as repo
from benkyo import traversal


@pytest.fixture
def simple_project(conn):
    """単純なチェーン: p1 -> c1 -> c2 -> c3."""
    p1 = repo.create_problem(conn, "問題", "解")
    c1 = repo.create_concept(conn, "概念1")
    c2 = repo.create_concept(conn, "概念2")
    c3 = repo.create_concept(conn, "概念3")
    repo.create_edge(conn, p1["id"], c1["id"], "prereq")
    repo.create_edge(conn, c1["id"], c2["id"], "prereq")
    repo.create_edge(conn, c2["id"], c3["id"], "prereq")
    proj = repo.create_project(conn, "テスト", [p1["id"]])
    return {
        "conn": conn,
        "project_id": proj["id"],
        "p1": p1["id"],
        "c1": c1["id"],
        "c2": c2["id"],
        "c3": c3["id"],
    }


class TestWindow:
    def test_all_whitebox_full_chain(self, simple_project):
        sp = simple_project
        w = traversal.window(sp["conn"], sp["project_id"])
        node_ids = {n["id"] for n in w["nodes"]}
        assert node_ids == {sp["p1"], sp["c1"], sp["c2"], sp["c3"]}
        assert w["edge_count"] == 3

    def test_blackbox_terminates(self, simple_project):
        sp = simple_project
        # mark c2 as blackbox → traversal stops, c3 is excluded
        repo.set_treatment(
            sp["conn"], sp["project_id"], sp["c2"], "blackbox", "ref"
        )
        w = traversal.window(sp["conn"], sp["project_id"])
        node_ids = {n["id"] for n in w["nodes"]}
        assert sp["c3"] not in node_ids
        assert sp["c2"] in node_ids  # c2 は含まれる (終端として)

    def test_blackbox_concept_has_reference(self, simple_project):
        sp = simple_project
        repo.set_treatment(
            sp["conn"], sp["project_id"], sp["c2"], "blackbox", "公式表"
        )
        w = traversal.window(sp["conn"], sp["project_id"])
        c2_node = next(n for n in w["nodes"] if n["id"] == sp["c2"])
        assert c2_node["treatment"] == "blackbox"
        assert c2_node["reference_content"] == "公式表"

    def test_empty_goals(self, conn):
        proj = repo.create_project(conn, "空")
        w = traversal.window(conn, proj["id"])
        assert w["node_count"] == 0
        assert w["edge_count"] == 0

    def test_related_edges_included(self, conn):
        p1 = repo.create_problem(conn, "P", "A")
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        repo.create_edge(conn, p1["id"], c1["id"], "prereq")
        repo.create_edge(conn, p1["id"], c2["id"], "prereq")
        repo.create_edge(conn, c1["id"], c2["id"], "related")
        proj = repo.create_project(conn, "P", [p1["id"]])
        w = traversal.window(conn, proj["id"])
        types = {e["type"] for e in w["edges"]}
        assert "related" in types


class TestBreakdown:
    def test_direct_dependencies(self, simple_project):
        sp = simple_project
        items = traversal.breakdown(sp["conn"], sp["project_id"], sp["p1"])
        assert len(items) == 1
        assert items[0]["id"] == sp["c1"]

    def test_breakdown_at_blackbox(self, simple_project):
        sp = simple_project
        repo.set_treatment(
            sp["conn"], sp["project_id"], sp["c2"], "blackbox", "ref"
        )
        items = traversal.breakdown(sp["conn"], sp["project_id"], sp["c1"])
        assert len(items) == 1
        # c2 が表示され, treatment は blackbox
        assert items[0]["treatment"] == "blackbox"
        assert items[0]["reference_content"] == "ref"


class TestFrontier:
    def test_empty_when_all_whitebox(self, simple_project):
        sp = simple_project
        items = traversal.frontier(sp["conn"], sp["project_id"])
        assert items == []

    def test_lists_blackbox_in_window(self, simple_project):
        sp = simple_project
        repo.set_treatment(
            sp["conn"], sp["project_id"], sp["c2"], "blackbox", "ref"
        )
        items = traversal.frontier(sp["conn"], sp["project_id"])
        ids = {i["id"] for i in items}
        assert ids == {sp["c2"]}


class TestAncestors:
    def test_direct_ancestor(self, simple_project):
        sp = simple_project
        items = traversal.ancestors(sp["conn"], sp["project_id"], sp["c1"])
        ids = {i["id"] for i in items}
        assert ids == {sp["p1"]}

    def test_node_outside_window(self, simple_project):
        sp = simple_project
        # 別 problem を作るが project の goal にしない
        p_other = repo.create_problem(sp["conn"], "別問題", "解")
        items = traversal.ancestors(sp["conn"], sp["project_id"], p_other["id"])
        assert items == []
