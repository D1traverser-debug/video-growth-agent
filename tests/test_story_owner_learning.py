"""Verify narrative depth is wired into the EXISTING responsible specialists.

These tests prove prompt/role ownership, not that any film was loved or viewed.
"""
from video_growth_agent.roles import RoleRegistry
from video_growth_agent.studio_agents import AgentRegistry, ExecutionPlanner


def test_writer_is_the_actual_script_producer_and_story_editor_is_not_author():
    planner = ExecutionPlanner()
    script = planner.stage("SCRIPT")
    tasks = {t["id"]: t for t in script["tasks"]}
    assert tasks["script_build"]["agent"] == "writer"
    assert tasks["script_build"]["type"] == "produce"
    assert tasks["story_edit"]["agent"] == "story_editor"
    assert tasks["story_edit"]["type"] == "review"
    assert tasks["story_edit"]["blind"] is True
    assert tasks["story_edit"]["wave"] > tasks["script_build"]["wave"]


def test_existing_story_owners_receive_primary_source_and_counterfactual_method():
    registry = AgentRegistry()
    writer = registry.get("writer")
    editor = registry.get("story_editor")
    director = registry.get("director")
    assert writer.kind == "worker" and editor.kind == "reviewer"
    assert "raw brief" in writer.mandate.lower()
    assert "alternate" in writer.mandate.lower()
    assert "causal" in writer.mandate.lower()
    assert "first-party" in editor.mandate.lower()
    assert "counterfactual" in editor.mandate.lower()
    assert "animatic" in editor.prompt.lower()
    assert "storyreel" in director.prompt.lower()
    assert "storyteller/editor" in director.prompt.lower()
    assert registry.get("production_methodologist").kind == "worker"
    assert "original script" in registry.get("production_methodologist").mandate.lower()


def test_role_prompt_contains_scene_specific_rejection_not_a_model_self_score():
    roles = RoleRegistry()
    writer = roles.get("writer")
    editor = roles.get("story_editor")
    assert "source_refs" in writer.prompt
    assert "specific scene-level" in editor.prompt
    assert "STORY_REVISION_REQUIRED" in editor.prompt
    assert "blind no-context" in editor.prompt
    assert "Correct-but-boring" in editor.prompt


def test_short_story_still_uses_existing_pipeline_without_six_chunk_stage():
    planner = ExecutionPlanner()
    assert not planner.validate()
    stages = planner.config["stages"]
    assert "SCRIPT" in stages and "SCRIPT_AUDIT" in stages
    assert "STORYBOARD" in stages
    assert not any("story" in stage.lower() and "controller" in stage.lower()
                   for stage in stages)
    reviewers = {t.get("agent") for t in stages["SCRIPT_AUDIT"]["tasks"]}
    assert {"retention_editor", "director", "fact_checker"} <= reviewers
