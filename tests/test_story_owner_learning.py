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


def test_story_reviews_fail_closed_without_registered_independent_executor():
    """A blind role in a plan is not proof a different review execution occurred."""
    from video_growth_agent.execution_attestation import ExecutionTrustRegistry
    registry = ExecutionTrustRegistry()
    assert not registry.config["trusted_executors"]
    for stage in ("SCRIPT", "SCRIPT_AUDIT", "STORYBOARD"):
        assert registry.requires_attestation(stage, blind=True, task_type="review")
    assert not registry.requires_attestation("SCRIPT", blind=True, task_type="produce")


def test_existing_writer_editor_director_prompts_prescribe_four_questions_and_actual_evidence():
    roles = RoleRegistry()
    writer = roles.get("writer").prompt
    story_editor = roles.get("story_editor").prompt
    director = roles.get("director").prompt
    assert "pre-rewrite four-answer study" in writer
    assert "least-processed materials" in writer
    assert "truly different competing treatment" in writer
    assert "INDEPENDENT_REVIEW" in story_editor
    assert "EXTERNAL_REVIEW_MISSING" in story_editor
    assert "VIEWABLE timed story reel" in director
    assert "STORY_REEL_MISSING" in director


def test_reviewer_prompt_no_longer_misrepresents_self_role_as_real_independence():
    roles = RoleRegistry()
    assert "SINGLE_AUTHOR_SELF_CRITIQUE" in roles.sections["Blind review protocol"]
    assert "context separation" in roles.sections["Blind review protocol"]


def test_fake_script_editor_pass_cannot_advance_without_real_execution_attestation(tmp_path):
    """A completed work order/role signature is not evidence of an independent model run."""
    from video_growth_agent import ArtifactRecord, ProjectStore, StudioRuntime
    from video_growth_agent.studio_agents import AgenticStudio
    runtime = StudioRuntime(store=ProjectStore(tmp_path / "projects"))
    runtime.create_project("narrative")
    state = runtime.state("narrative")
    state.stage = "SCRIPT"
    for name in ("research_package", "positioning"):
        state.artifacts[name] = ArtifactRecord(
            name=name, uri=f"file://{name}", stage="SCRIPT", digest=f"digest-{name}"
        )
    runtime.store.save(state)
    studio = AgenticStudio(runtime=runtime)
    studio.dispatch_stage("narrative")
    studio.complete_work(
        "narrative", "script_build",
        outputs={"script": {"uri": "file://draft", "digest": "draft-v6"}}
    )
    studio.dispatch_stage("narrative")
    studio.submit_review(
        "narrative", "story_edit", "PASS",
        notes="single-author pretend story-editor PASS", target_digest="draft-v6",
    )
    failures = runtime.process_guard_report(runtime.state("narrative"))["failures"]
    assert "process_execution_attestation_missing_or_ambiguous:story_edit" in failures
