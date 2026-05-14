"""record_session_end: atomic session end + delayed JOL events."""

import pytest

from benkyo import repository as repo
from benkyo.errors import InvalidArgError, NotFoundError


@pytest.fixture
def project_with_goal(conn):
    repo.create_problem(conn, "Q", "A")
    prj = repo.create_project(conn, "test", ["p1"])
    return prj["id"]


class TestRecordSessionEnd:
    def test_minimal_session(self, conn, project_with_goal):
        result = repo.record_session_end(conn, project_with_goal, {})
        assert result["session_end"]["kind"] == "session_end"
        assert result["delayed_jols"] == []
        # one event in the log
        events = repo.list_events(conn)
        assert len(events) == 1
        assert events[0]["kind"] == "session_end"

    def test_full_summary(self, conn, project_with_goal):
        summary = {
            "completed_problems": ["p1"],
            "treatment_changes": [
                {"concept_id": "c1", "from": "blackbox", "to": "whitebox"}
            ],
            "pending": ["c4 mid-breakdown"],
            "delayed_jols": [
                {"concept_id": "c1", "claim": "high"},
                {"concept_id": "c2", "claim": "mid", "note": "怪しい"},
            ],
            "notes": "学習者は明日試験",
        }
        result = repo.record_session_end(conn, project_with_goal, summary)
        # session_end carries non-jol payload
        se = result["session_end"]
        assert se["payload"]["completed_problems"] == ["p1"]
        assert se["payload"]["treatment_changes"][0]["concept_id"] == "c1"
        assert se["payload"]["pending"] == ["c4 mid-breakdown"]
        assert se["notes"] == "学習者は明日試験"
        assert "delayed_jols" not in se["payload"]

        # jol events are separate
        assert len(result["delayed_jols"]) == 2
        kinds = [e["kind"] for e in result["delayed_jols"]]
        assert kinds == ["delayed_jol_recorded", "delayed_jol_recorded"]
        # jol note migrates to event.notes column
        jol_with_note = next(
            e for e in result["delayed_jols"] if e["payload"]["concept_id"] == "c2"
        )
        assert jol_with_note["notes"] == "怪しい"

    def test_three_events_total(self, conn, project_with_goal):
        repo.record_session_end(
            conn,
            project_with_goal,
            {
                "delayed_jols": [
                    {"concept_id": "c1", "claim": "high"},
                    {"concept_id": "c2", "claim": "mid"},
                ]
            },
        )
        all_events = repo.list_events(conn)
        assert len(all_events) == 3
        # all attributed to the project
        assert all(e["project_id"] == project_with_goal for e in all_events)

    def test_filter_jol_events(self, conn, project_with_goal):
        repo.record_session_end(
            conn,
            project_with_goal,
            {"delayed_jols": [{"concept_id": "c1", "claim": "high"}]},
        )
        jols = repo.list_events(conn, kind="delayed_jol_recorded")
        assert len(jols) == 1
        assert jols[0]["payload"] == {"concept_id": "c1", "claim": "high"}

    def test_invalid_project_id_rejected(self, conn):
        with pytest.raises(InvalidArgError):
            repo.record_session_end(conn, "c1", {})
        with pytest.raises(InvalidArgError):
            repo.record_session_end(conn, "", {})

    def test_project_must_exist(self, conn):
        with pytest.raises(NotFoundError):
            repo.record_session_end(conn, "prj999", {})

    def test_non_dict_summary_rejected(self, conn, project_with_goal):
        with pytest.raises(InvalidArgError):
            repo.record_session_end(conn, project_with_goal, "notdict")  # type: ignore

    def test_non_list_delayed_jols_rejected(self, conn, project_with_goal):
        with pytest.raises(InvalidArgError):
            repo.record_session_end(
                conn,
                project_with_goal,
                {"delayed_jols": "string instead of list"},
            )

    def test_non_dict_jol_entry_rejected(self, conn, project_with_goal):
        with pytest.raises(InvalidArgError):
            repo.record_session_end(
                conn,
                project_with_goal,
                {"delayed_jols": ["not a dict"]},
            )

    def test_rollback_on_jol_failure(self, conn, project_with_goal):
        # one valid jol, one invalid → all-or-nothing
        with pytest.raises(InvalidArgError):
            repo.record_session_end(
                conn,
                project_with_goal,
                {
                    "delayed_jols": [
                        {"concept_id": "c1", "claim": "high"},
                        "broken",
                    ]
                },
            )
        # nothing persisted
        assert repo.list_events(conn) == []
