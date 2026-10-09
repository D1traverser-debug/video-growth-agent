import pytest
from video_growth_agent import Approval, GateBlocked, ProjectState, StudioOrchestrator


def test_missing_signoff_blocks():
    o = StudioOrchestrator()
    s = ProjectState("x")
    with pytest.raises(GateBlocked):
        o.advance(s)


def test_fail_veto_blocks():
    o = StudioOrchestrator()
    s = ProjectState("x")
    o.sign(s, Approval("showrunner", "FAIL", "not worth publishing"))
    with pytest.raises(GateBlocked):
        o.advance(s)


def test_pass_advances():
    o = StudioOrchestrator()
    s = ProjectState("x")
    o.sign(s, Approval("showrunner", "PASS"))
    assert o.advance(s) == "POSITIONING"


def test_multi_role_stage_requires_everyone():
    o = StudioOrchestrator()
    s = ProjectState("x", stage="POSITIONING")
    o.sign(s, Approval("growth_strategist", "PASS"))
    o.sign(s, Approval("commercial_director", "PASS"))
    with pytest.raises(GateBlocked):
        o.advance(s)
    o.sign(s, Approval("showrunner", "PASS"))
    assert o.advance(s) == "RESEARCH"


def test_invalidation_removes_downstream_approvals():
    o = StudioOrchestrator()
    s = ProjectState("x", stage="ROUGH_CUT")
    s.approvals["SCRIPT"] = {"writer": Approval("writer", "PASS")}
    s.approvals["ROUGH_CUT"] = {"editor": Approval("editor", "PASS")}
    o.invalidate_from(s, "SCRIPT")
    assert s.stage == "SCRIPT"
    assert s.approvals == {}
