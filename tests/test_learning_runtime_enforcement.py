import pytest

from video_growth_agent import ArtifactRecord, GateBlocked, ProjectStore, StudioRuntime


def test_direct_runtime_advance_cannot_bypass_learn_work_orders(tmp_path):
    rt = StudioRuntime(store=ProjectStore(tmp_path / "projects"))
    rt.create_project("learn-bypass")

    state = rt.state("learn-bypass")
    state.stage = "LEARN"
    state.artifacts["learning_receipt"] = ArtifactRecord(
        "learning_receipt",
        "file://learning-receipt.json",
        "LEARN",
        kind="document",
        digest="learning-digest",
    )
    rt.store.save(state)

    # Simulate the exact bypass the runtime must reject: required artifact and role
    # approvals are present, but the Methodologist/Evolution/Red-Team/Showrunner
    # work-order pipeline never executed.
    rt.sign("learn-bypass", "red_team", "PASS", notes="manual sign-off must not count as execution")
    rt.sign("learn-bypass", "showrunner", "PASS", notes="manual sign-off must not count as execution")

    report = rt.gate_report("learn-bypass")
    assert report["pass"] is False
    assert "process_work_order_missing:learning_methodology" in report["process_failures"]
    assert "process_work_order_missing:learning_evolution_candidate" in report["process_failures"]

    with pytest.raises(GateBlocked, match="process_work_order_missing:learning_methodology"):
        rt.advance("learn-bypass")
