import pytest

from video_growth_agent.operator_view import (
    OperatorAction,
    OperatorViewError,
    derive_operator_snapshot,
)


def test_ready_action_requires_observable_progress_evidence():
    with pytest.raises(OperatorViewError, match="expected progress evidence"):
        OperatorAction(
            action_id="A1",
            label="Plan episode",
            state="READY",
            governing_outcome="Produce a strong episode",
            authority_refs=("program://state",),
        )


def test_blocked_action_requires_actual_blocker():
    with pytest.raises(OperatorViewError, match="blocker_reasons"):
        OperatorAction(
            action_id="A1",
            label="Generate hero shot",
            state="BLOCKED",
            governing_outcome="Create promotable hero shot",
            authority_refs=("shot://contract",),
        )


def test_snapshot_exposes_all_ready_actions_instead_of_inventing_one_global_next_step():
    a1 = OperatorAction(
        "growth", "Research topic slate", "READY", "Find qualified audience demand",
        ("program://state",), progress_evidence_expected=("topic://evidence",),
    )
    a2 = OperatorAction(
        "ip", "Continue H1", "READY", "Build distinctive reusable IP",
        ("program://state",), progress_evidence_expected=("asset://candidate",),
    )
    blocked = OperatorAction(
        "release", "Release episode", "BLOCKED", "Publish verified media",
        ("release://policy",), blocker_reasons=("no final artifact",), recovery_refs=("episode://plan",),
    )
    snapshot = derive_operator_snapshot(
        context_id="program",
        governing_outcome="Build a durable AI-native media business",
        current_focus="IP H1 while growth research can proceed in parallel",
        authority_refs=("PROGRAM_STATE.json", "SUBTASK_GRAPH.json"),
        actions=(a1, a2, blocked),
        resume_refs=("RESUME_ENTRY.md",),
    )
    assert snapshot.next_action_ids() == ("growth", "ip")
    assert snapshot.blocked_actions == (blocked,)
    assert snapshot.recovery_surface()["resume_refs"] == ("RESUME_ENTRY.md",)
