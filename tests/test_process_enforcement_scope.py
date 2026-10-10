import pytest

from video_growth_agent import ArtifactRecord, GateBlocked, ProjectStore, StudioRuntime


def test_direct_runtime_advance_cannot_bypass_intake_work_order(tmp_path):
    rt = StudioRuntime(store=ProjectStore(tmp_path / "projects"))
    rt.create_project("intake-bypass")

    state = rt.state("intake-bypass")
    state.artifacts["brief"] = ArtifactRecord(
        "brief",
        "file://brief.md",
        "INTAKE",
        kind="document",
        digest="brief-digest",
    )
    rt.store.save(state)

    # Producer-only INTAKE has no approval role. Even with the required artifact present,
    # direct runtime advance must fail without the declared producer work order/provenance.
    report = rt.gate_report("intake-bypass")
    assert report["pass"] is False
    assert "process_work_order_missing:intake" in report["process_failures"]

    with pytest.raises(GateBlocked, match="process_work_order_missing:intake"):
        rt.advance("intake-bypass")


def test_process_enforcement_scope_is_derived_from_execution_plan(tmp_path):
    rt = StudioRuntime(store=ProjectStore(tmp_path / "projects"))
    planned = {
        stage
        for stage, spec in rt.execution_plan["stages"].items()
        if isinstance(spec, dict) and spec.get("tasks")
    }
    assert "INTAKE" in planned
    assert "LEARN" in planned
    assert "VISUAL_PREVIEW" in planned
    assert "COMPLETE" not in planned
    assert rt.PROCESS_ENFORCEMENT_POLICY == "ALL_EXECUTION_PLAN_TASK_STAGES"
