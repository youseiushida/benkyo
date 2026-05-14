"""Tests for concept merge / problem merge / concept fork."""

import pytest

from benkyo import repository as repo
from benkyo.errors import ConflictError, InvalidArgError, NotFoundError


# ---------------------------------------------------------------------------
# merge_concept
# ---------------------------------------------------------------------------


class TestMergeConcept:
    def test_basic_merge(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        c3 = repo.create_concept(conn, "C")
        # c1 -> c3, c2 -> c3 (different edges to same target)
        repo.create_edge(conn, c1["id"], c3["id"], "prereq")
        repo.create_edge(conn, c2["id"], c3["id"], "prereq")

        # merge c2 into c1
        result = repo.merge_concept(conn, c2["id"], c1["id"])
        assert result["merged_source"] == c2["id"]
        # c2 -> c3 redirect would dup c1 -> c3, so skipped
        assert result["edges_skipped"] == 1
        assert result["edges_redirected"] == 0

        # c2 is gone
        with pytest.raises(NotFoundError):
            repo.get_concept(conn, c2["id"])

    def test_merge_redirects_unique_edge(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        c3 = repo.create_concept(conn, "C")
        repo.create_edge(conn, c2["id"], c3["id"], "prereq")  # c2 -> c3 only

        result = repo.merge_concept(conn, c2["id"], c1["id"])
        assert result["edges_redirected"] == 1
        # c1 -> c3 should now exist
        edges = repo.list_edges(conn, from_id=c1["id"])
        assert len(edges) == 1
        assert edges[0]["to_id"] == c3["id"]

    def test_merge_avoids_self_loop(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        # c2 -> c1 (would become c1 -> c1 self-loop if redirected)
        repo.create_edge(conn, c2["id"], c1["id"], "prereq")

        result = repo.merge_concept(conn, c2["id"], c1["id"])
        assert result["edges_skipped"] == 1
        # no self-loop edge created
        edges = repo.list_edges(conn, from_id=c1["id"])
        assert all(e["to_id"] != c1["id"] for e in edges)

    def test_merge_treatment_no_conflict(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        proj = repo.create_project(conn, "P")
        # only c2 has treatment in project
        repo.set_treatment(conn, proj["id"], c2["id"], "blackbox", "ref")

        result = repo.merge_concept(conn, c2["id"], c1["id"])
        assert result["treatments_redirected"] == 1
        # now c1 has the treatment
        t = repo.get_treatment(conn, proj["id"], c1["id"])
        assert t["treatment"] == "blackbox"

    def test_merge_treatment_conflict_error(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        proj = repo.create_project(conn, "P")
        repo.set_treatment(conn, proj["id"], c1["id"], "whitebox")
        repo.set_treatment(conn, proj["id"], c2["id"], "blackbox", "ref")
        with pytest.raises(ConflictError):
            repo.merge_concept(conn, c2["id"], c1["id"], on_conflict="error")

    def test_merge_treatment_keep_canonical(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        proj = repo.create_project(conn, "P")
        repo.set_treatment(conn, proj["id"], c1["id"], "whitebox")
        repo.set_treatment(conn, proj["id"], c2["id"], "blackbox", "ref")
        result = repo.merge_concept(
            conn, c2["id"], c1["id"], on_conflict="keep_canonical"
        )
        assert result["treatments_skipped"] == 1
        t = repo.get_treatment(conn, proj["id"], c1["id"])
        assert t["treatment"] == "whitebox"  # kept

    def test_merge_treatment_keep_source(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        proj = repo.create_project(conn, "P")
        repo.set_treatment(conn, proj["id"], c1["id"], "whitebox")
        repo.set_treatment(conn, proj["id"], c2["id"], "blackbox", "ref-source")
        result = repo.merge_concept(
            conn, c2["id"], c1["id"], on_conflict="keep_source"
        )
        assert result["treatments_redirected"] == 1
        t = repo.get_treatment(conn, proj["id"], c1["id"])
        assert t["treatment"] == "blackbox"
        assert t["reference_content"] == "ref-source"

    def test_merge_self_rejected(self, conn):
        c1 = repo.create_concept(conn, "A")
        with pytest.raises(InvalidArgError):
            repo.merge_concept(conn, c1["id"], c1["id"])

    def test_merge_not_found(self, conn):
        c1 = repo.create_concept(conn, "A")
        with pytest.raises(NotFoundError):
            repo.merge_concept(conn, "c999", c1["id"])


# ---------------------------------------------------------------------------
# merge_problem
# ---------------------------------------------------------------------------


class TestMergeProblem:
    def test_basic_problem_merge(self, conn):
        p1 = repo.create_problem(conn, "Q1", "A1")
        p2 = repo.create_problem(conn, "Q2", "A2")
        proj = repo.create_project(conn, "P", [p2["id"]])
        # merge p2 into p1
        result = repo.merge_problem(conn, p2["id"], p1["id"])
        assert result["goals_redirected"] == 1
        proj_after = repo.get_project(conn, proj["id"])
        assert p1["id"] in proj_after["goals"]
        assert p2["id"] not in proj_after["goals"]

    def test_merge_dedups_goal(self, conn):
        p1 = repo.create_problem(conn, "Q1", "A1")
        p2 = repo.create_problem(conn, "Q2", "A2")
        proj = repo.create_project(conn, "P", [p1["id"], p2["id"]])  # both goals
        result = repo.merge_problem(conn, p2["id"], p1["id"])
        assert result["goals_skipped"] == 1
        proj_after = repo.get_project(conn, proj["id"])
        assert proj_after["goals"] == [p1["id"]]


# ---------------------------------------------------------------------------
# fork_concept
# ---------------------------------------------------------------------------


class TestForkConcept:
    def test_basic_fork(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        repo.create_edge(conn, c1["id"], c2["id"], "prereq")

        result = repo.fork_concept(conn, c1["id"])
        new_id = result["new_id"]
        assert new_id != c1["id"]
        assert result["edges_copied"] == 1

        # new concept has same content
        new = repo.get_concept(conn, new_id)
        assert new["content"] == "A"

        # both original and new have edge to c2
        edges_from_new = repo.list_edges(conn, from_id=new_id)
        assert len(edges_from_new) == 1
        assert edges_from_new[0]["to_id"] == c2["id"]

        edges_from_orig = repo.list_edges(conn, from_id=c1["id"])
        assert len(edges_from_orig) == 1  # original unchanged

    def test_fork_with_new_content(self, conn):
        c1 = repo.create_concept(conn, "Original")
        result = repo.fork_concept(conn, c1["id"], "Modified")
        new = repo.get_concept(conn, result["new_id"])
        assert new["content"] == "Modified"

    def test_fork_copies_both_directions(self, conn):
        c1 = repo.create_concept(conn, "A")
        c2 = repo.create_concept(conn, "B")
        c3 = repo.create_concept(conn, "C")
        repo.create_edge(conn, c1["id"], c2["id"], "prereq")  # c1 -> c2
        repo.create_edge(conn, c3["id"], c1["id"], "prereq")  # c3 -> c1

        result = repo.fork_concept(conn, c1["id"])
        # 2 edges copied (in + out)
        assert result["edges_copied"] == 2

    def test_fork_no_treatment_copy(self, conn):
        c1 = repo.create_concept(conn, "A")
        proj = repo.create_project(conn, "P")
        repo.set_treatment(conn, proj["id"], c1["id"], "blackbox", "ref")

        result = repo.fork_concept(conn, c1["id"])
        # new concept has default treatment, no explicit setting
        t = repo.get_treatment(conn, proj["id"], result["new_id"])
        assert t["default"] is True
        assert t["treatment"] == "whitebox"

    def test_fork_not_found(self, conn):
        with pytest.raises(NotFoundError):
            repo.fork_concept(conn, "c999")
