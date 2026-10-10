import pytest
from video_growth_agent import Approval, ArtifactRecord, GateBlocked, ProjectState, StudioOrchestrator


def artifact(name: str, stage: str) -> ArtifactRecord:
    return ArtifactRecord(name=name, uri=f"memory://{name}", stage=stage)


def test_producer_only_stage_requires_artifact_not_self_signoff():
    o = StudioOrchestrator(); s = ProjectState("x")
    with pytest.raises(GateBlocked): o.advance(s)
    s.artifacts["brief"] = artifact("brief", "INTAKE")
    assert o.advance(s) == "POSITIONING"


def test_missing_artifact_blocks_even_with_independent_reviews():
    o = StudioOrchestrator(); s = ProjectState("x", stage="POSITIONING")
    o.sign(s, Approval("growth_strategist", "PASS")); o.sign(s, Approval("commercial_director", "PASS"))
    report = o.gate_report(s)
    assert report["missing_artifacts"] == ["positioning"]
    with pytest.raises(GateBlocked): o.advance(s)


def test_review_fail_veto_blocks():
    o = StudioOrchestrator(); s = ProjectState("x", stage="POSITIONING")
    s.artifacts["positioning"] = artifact("positioning", "POSITIONING")
    o.sign(s, Approval("growth_strategist", "FAIL", "not worth publishing"))
    o.sign(s, Approval("commercial_director", "PASS"))
    with pytest.raises(GateBlocked): o.advance(s)


def test_independent_reviews_pass_advances():
    o = StudioOrchestrator(); s = ProjectState("x", stage="POSITIONING")
    s.artifacts["positioning"] = artifact("positioning", "POSITIONING")
    o.sign(s, Approval("growth_strategist", "PASS")); o.sign(s, Approval("commercial_director", "PASS"))
    assert o.advance(s) == "RESEARCH"


def test_multi_role_stage_requires_every_reviewer():
    o = StudioOrchestrator(); s = ProjectState("x", stage="POSITIONING")
    s.artifacts["positioning"] = artifact("positioning", "POSITIONING")
    o.sign(s, Approval("growth_strategist", "PASS"))
    with pytest.raises(GateBlocked): o.advance(s)
    o.sign(s, Approval("commercial_director", "PASS")); assert o.advance(s) == "RESEARCH"


def test_irrelevant_role_cannot_sign_current_stage():
    o = StudioOrchestrator(); s = ProjectState("x")
    with pytest.raises(ValueError): o.sign(s, Approval("writer", "PASS"))


def test_producer_role_cannot_self_approve_producer_only_stage():
    o = StudioOrchestrator(); s = ProjectState("x")
    with pytest.raises(ValueError): o.sign(s, Approval("showrunner", "PASS"))


def test_red_team_pass_requires_three_findings():
    o = StudioOrchestrator(); s = ProjectState("x", stage="RED_TEAM")
    with pytest.raises(ValueError): o.sign(s, Approval("red_team", "PASS", findings=("one", "two")))
    o.sign(s, Approval("red_team", "PASS", findings=("one", "two", "three")))


def test_invalidation_removes_downstream_approvals():
    o = StudioOrchestrator(); s = ProjectState("x", stage="ROUGH_CUT"); s.approvals["SCRIPT"] = {"story_editor": Approval("story_editor", "PASS")}; s.approvals["ROUGH_CUT"] = {"editor": Approval("editor", "PASS")}; o.invalidate_from(s, "SCRIPT")
    assert s.stage == "SCRIPT"; assert s.approvals == {}


def test_every_required_role_has_prompt():
    from video_growth_agent import RoleRegistry
    registry = RoleRegistry(); assert registry.validate_workflow() == []


def test_role_registry_loads_only_requested_prompt():
    from video_growth_agent import RoleRegistry
    registry = RoleRegistry(); role = registry.get("art_director"); assert role.role == "art_director"; assert "PPT/SaaS-dashboard" in role.prompt; assert "looks-like-ppt" in role.veto


def test_creative_director_prompt_and_lookdev_stage_exist():
    from video_growth_agent import RoleRegistry
    registry = RoleRegistry(); prompt = registry.get("creative_director").prompt; assert "absolute craft bar" in prompt
    o = StudioOrchestrator(); assert "LOOKDEV" in o.index; assert "creative_director" in o.required_roles("VISUAL_PREVIEW")
