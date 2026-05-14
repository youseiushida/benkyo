"""リポジトリ層 (CRUD) のテスト."""

import pytest

from benkyo import repository as repo
from benkyo.errors import ConflictError, InvalidArgError, NotFoundError


# =======================================================================
# Concept
# =======================================================================


class TestConcept:
    def test_create_and_get(self, conn):
        c = repo.create_concept(conn, "ラプラス変換")
        assert c["id"] == "c1"
        assert c["content"] == "ラプラス変換"

        got = repo.get_concept(conn, "c1")
        assert got["content"] == "ラプラス変換"

    def test_create_empty_rejected(self, conn):
        with pytest.raises(InvalidArgError):
            repo.create_concept(conn, "")
        with pytest.raises(InvalidArgError):
            repo.create_concept(conn, "   ")

    def test_get_not_found(self, conn):
        with pytest.raises(NotFoundError):
            repo.get_concept(conn, "c999")

    def test_update(self, conn):
        c = repo.create_concept(conn, "古い内容")
        updated = repo.update_concept(conn, c["id"], "新しい内容")
        assert updated["content"] == "新しい内容"

    def test_update_not_found(self, conn):
        with pytest.raises(NotFoundError):
            repo.update_concept(conn, "c999", "X")

    def test_delete(self, conn):
        c = repo.create_concept(conn, "削除対象")
        result = repo.delete_concept(conn, c["id"])
        assert result["deleted_id"] == c["id"]
        with pytest.raises(NotFoundError):
            repo.get_concept(conn, c["id"])

    def test_delete_cascade_edges(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        repo.create_edge(conn, c1["id"], c2["id"], "prereq")
        result = repo.delete_concept(conn, c1["id"])
        assert result["cascade"]["edges"] == 1

    def test_list(self, conn):
        repo.create_concept(conn, "A")
        repo.create_concept(conn, "B")
        items = repo.list_concepts(conn)
        assert len(items) == 2

    def test_list_query(self, conn):
        repo.create_concept(conn, "ラプラス変換")
        repo.create_concept(conn, "フーリエ変換")
        repo.create_concept(conn, "微分方程式")
        items = repo.list_concepts(conn, "変換")
        assert len(items) == 2

    def test_find_exact(self, conn):
        repo.create_concept(conn, "ラプラス変換")
        repo.create_concept(conn, "ラプラス変換 (拡張)")
        found = repo.find_concept_by_content(conn, "ラプラス変換")
        assert len(found) == 1


# =======================================================================
# Problem
# =======================================================================


class TestProblem:
    def test_create_and_get(self, conn):
        p = repo.create_problem(conn, "問題文", "解答")
        assert p["id"] == "p1"
        assert p["statement"] == "問題文"
        assert p["answer"] == "解答"

    def test_create_empty_rejected(self, conn):
        with pytest.raises(InvalidArgError):
            repo.create_problem(conn, "", "ans")
        with pytest.raises(InvalidArgError):
            repo.create_problem(conn, "stmt", "")

    def test_update_partial(self, conn):
        p = repo.create_problem(conn, "S1", "A1")
        updated = repo.update_problem(conn, p["id"], statement="S2")
        assert updated["statement"] == "S2"
        assert updated["answer"] == "A1"

    def test_update_both(self, conn):
        p = repo.create_problem(conn, "S1", "A1")
        updated = repo.update_problem(conn, p["id"], statement="S2", answer="A2")
        assert updated["statement"] == "S2"
        assert updated["answer"] == "A2"

    def test_update_nothing(self, conn):
        p = repo.create_problem(conn, "S1", "A1")
        with pytest.raises(InvalidArgError):
            repo.update_problem(conn, p["id"])

    def test_delete(self, conn):
        p = repo.create_problem(conn, "S", "A")
        result = repo.delete_problem(conn, p["id"])
        assert result["deleted_id"] == p["id"]


# =======================================================================
# Edge
# =======================================================================


class TestEdge:
    def test_create(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        e = repo.create_edge(conn, c1["id"], c2["id"], "prereq")
        assert e["from_id"] == c1["id"]
        assert e["edge_type"] == "prereq"

    def test_self_loop_rejected(self, conn):
        c1 = repo.create_concept(conn, "A")
        with pytest.raises(InvalidArgError):
            repo.create_edge(conn, c1["id"], c1["id"], "prereq")

    def test_invalid_type_rejected(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        with pytest.raises(InvalidArgError):
            repo.create_edge(conn, c1["id"], c2["id"], "invalid")

    def test_missing_node_rejected(self, conn):
        c1 = repo.create_concept(conn, "A")
        with pytest.raises(NotFoundError):
            repo.create_edge(conn, c1["id"], "c999", "prereq")

    def test_duplicate_rejected(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        repo.create_edge(conn, c1["id"], c2["id"], "prereq")
        with pytest.raises(ConflictError):
            repo.create_edge(conn, c1["id"], c2["id"], "prereq")

    def test_both_types_allowed(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        repo.create_edge(conn, c1["id"], c2["id"], "prereq")
        # 同じ from/to で別 type は OK
        repo.create_edge(conn, c1["id"], c2["id"], "related")
        edges = repo.list_edges(conn, c1["id"], c2["id"])
        assert len(edges) == 2

    def test_delete(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        repo.create_edge(conn, c1["id"], c2["id"], "prereq")
        repo.delete_edge(conn, c1["id"], c2["id"], "prereq")
        assert repo.list_edges(conn) == []

    def test_list_filter(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        c3 = repo.create_concept(conn, "C")
        repo.create_edge(conn, c1["id"], c2["id"], "prereq")
        repo.create_edge(conn, c1["id"], c3["id"], "related")
        assert len(repo.list_edges(conn, from_id=c1["id"])) == 2
        assert len(repo.list_edges(conn, edge_type="prereq")) == 1


# =======================================================================
# Project
# =======================================================================


class TestProject:
    def test_create_simple(self, conn):
        proj = repo.create_project(conn, metadata="テスト課題")
        assert proj["id"] == "prj1"
        assert proj["metadata"] == "テスト課題"
        assert proj["goals"] == []

    def test_create_with_goals(self, conn):
        p1 = repo.create_problem(conn, "S1", "A1")
        p2 = repo.create_problem(conn, "S2", "A2")
        proj = repo.create_project(conn, "課題", [p1["id"], p2["id"]])
        assert set(proj["goals"]) == {p1["id"], p2["id"]}

    def test_create_invalid_goal(self, conn):
        with pytest.raises(NotFoundError):
            repo.create_project(conn, "課題", ["p999"])

    def test_update_goals(self, conn):
        p1 = repo.create_problem(conn, "S1", "A1")
        p2 = repo.create_problem(conn, "S2", "A2")
        proj = repo.create_project(conn, "課題", [p1["id"]])
        updated = repo.update_project(conn, proj["id"], goal_problem_ids=[p2["id"]])
        assert updated["goals"] == [p2["id"]]

    def test_delete_cascades(self, conn):
        p1 = repo.create_problem(conn, "S", "A")
        c1 = repo.create_concept(conn, "X")
        proj = repo.create_project(conn, "課題", [p1["id"]])
        repo.set_treatment(conn, proj["id"], c1["id"], "procedural")
        result = repo.delete_project(conn, proj["id"])
        assert result["cascade"]["project_goals"] == 1
        assert result["cascade"]["project_concepts"] == 1


# =======================================================================
# Treatment
# =======================================================================


class TestTreatment:
    def test_default_is_conceptual(self, conn):
        c = repo.create_concept(conn, "X")
        proj = repo.create_project(conn, "P")
        t = repo.get_treatment(conn, proj["id"], c["id"])
        assert t["treatment"] == "conceptual"
        assert t["default"] is True

    def test_set_procedural_with_reference(self, conn):
        c = repo.create_concept(conn, "X")
        proj = repo.create_project(conn, "P")
        t = repo.set_treatment(
            conn, proj["id"], c["id"], "procedural", "参照内容"
        )
        assert t["treatment"] == "procedural"
        assert t["reference_content"] == "参照内容"
        assert t["default"] is False

    def test_set_conceptual_ignores_reference(self, conn):
        c = repo.create_concept(conn, "X")
        proj = repo.create_project(conn, "P")
        t = repo.set_treatment(
            conn, proj["id"], c["id"], "conceptual", "参照"
        )
        assert t["reference_content"] is None

    def test_set_overwrites(self, conn):
        c = repo.create_concept(conn, "X")
        proj = repo.create_project(conn, "P")
        repo.set_treatment(conn, proj["id"], c["id"], "procedural", "old")
        t = repo.set_treatment(conn, proj["id"], c["id"], "procedural", "new")
        assert t["reference_content"] == "new"

    def test_unset(self, conn):
        c = repo.create_concept(conn, "X")
        proj = repo.create_project(conn, "P")
        repo.set_treatment(conn, proj["id"], c["id"], "procedural")
        result = repo.unset_treatment(conn, proj["id"], c["id"])
        assert result["removed"] is True
        t = repo.get_treatment(conn, proj["id"], c["id"])
        assert t["default"] is True

    def test_unset_already_default(self, conn):
        c = repo.create_concept(conn, "X")
        proj = repo.create_project(conn, "P")
        result = repo.unset_treatment(conn, proj["id"], c["id"])
        assert result["removed"] is False
        assert result["already_default"] is True

    def test_list_treatments(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        proj = repo.create_project(conn, "P")
        repo.set_treatment(conn, proj["id"], c1["id"], "procedural")
        repo.set_treatment(conn, proj["id"], c2["id"], "conceptual")
        all_t = repo.list_treatments(conn, proj["id"])
        assert len(all_t) == 2
        proc_only = repo.list_treatments(conn, proj["id"], "procedural")
        assert len(proc_only) == 1
