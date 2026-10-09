from pathlib import Path

import pytest

from video_growth_agent import ArtifactRecord, GateBlocked, ProjectStore, StudioRuntime
from video_growth_agent.studio_agents import AgenticStudio


VISUAL_ROLES = [
    "creative_director",
    "art_director",
    "motion_director",
    "director",
    "retention_editor",
]


def _scores(role: str) -> dict[str, float]:
    dims = {
        "creative_director": [
            "benchmark_parity",
            "distinctiveness",
            "advertiser_showcase",
            "overall_craft",
            "sample_final_fidelity",
            "picture_sound_cohesion",
        ],
        "art_director": [
            "composition_hierarchy",
            "material_light_depth",
            "typography",
            "visual_consistency",
        ],
        "motion_director": [
            "motion_craft",
            "easing_stagger",
            "camera_depth",
            "motion_explains",
            "physicality_or_spatial_coherence",
        ],
        "director": [
            "narrative_visual_arc",
            "shot_scale_contrast",
            "reveal_payoff",
            "emotion_rhythm",
            "sample_represents_final_language",
        ],
        "retention_editor": [
            "first_2s_stop",
            "visual_reset_frequency",
            "silent_comprehension",
            "dead_zone_risk",
        ],
    }[role]
    return {dim: 4.5 for dim in dims}


def _runtime(tmp_path: Path) -> StudioRuntime:
    return StudioRuntime(store=ProjectStore(tmp_path / "projects"))


def _force_visual_artifacts(rt: StudioRuntime, project_id: str) -> None:
    state = rt.state(project_id)
    state.stage = "VISUAL_PREVIEW"
    state.artifacts.update(
        {
            "visual_preview": ArtifactRecord(
                "visual_preview",
                "file://preview.mp4",
                "VISUAL_PREVIEW",
                kind="media",
                digest="preview-digest",
            ),
            "visual_contact_sheet": ArtifactRecord(
                "visual_contact_sheet",
                "file://contact.jpg",
                "VISUAL_PREVIEW",
                kind="image",
                digest="contact-digest",
            ),
        }
    )
    rt.store.save(state)


def _sign_all_visual_roles(rt: StudioRuntime, project_id: str) -> None:
    for role in VISUAL_ROLES:
        rt.sign(
            project_id,
            role,
            "PASS",
            notes="current rendered artifact meets the bar",
            evidence=("file://preview.mp4", "file://contact.jpg"),
            findings=("actual pixels inspected",),
            scorecard=_scores(role),
            benchmark_refs=("ref://film", "ref://motion", "ref://explanation"),
            target_digest="preview-digest",
            blind_review=True,
        )


def test_direct_runtime_advance_cannot_bypass_missing_work_orders(tmp_path):
    rt = _runtime(tmp_path)
    rt.create_project("manual")
    _force_visual_artifacts(rt, "manual")
    _sign_all_visual_roles(rt, "manual")

    # Legacy role + quality checks alone look green; process proof is intentionally
    # enforced at advancement so hand-authored aggregate QA cannot authorize production.
    assert rt.gate_report("manual")["pass"] is True
    with pytest.raises(GateBlocked, match="process_work_order_missing:preview_build"):
        rt.advance("manual")


def test_formal_agentic_visual_preview_leaves_proof_and_can_advance(tmp_path):
    rt = _runtime(tmp_path)
    rt.create_project("formal")
    state = rt.state("formal")
    state.stage = "VISUAL_PREVIEW"
    for name, digest in (
        ("storyboard", "story-digest"),
        ("style_bible", "style-digest"),
        ("hero_frames", "hero-digest"),
        ("benchmark_pack", "bench-digest"),
    ):
        state.artifacts[name] = ArtifactRecord(
            name,
            f"file://{name}",
            "LOOKDEV",
            digest=digest,
        )
    rt.store.save(state)

    studio = AgenticStudio(runtime=rt)
    orders = studio.dispatch_stage("formal")
    assert next(o for o in orders if o.task_id == "preview_build").status == "READY"
    studio.complete_work(
        "formal",
        "preview_build",
        outputs={
            "visual_preview": {
                "uri": "file://preview.mp4",
                "kind": "media",
                "digest": "preview-digest",
            },
            "visual_contact_sheet": {
                "uri": "file://contact.jpg",
                "kind": "image",
                "digest": "contact-digest",
            },
        },
    )

    studio.dispatch_stage("formal")
    task_by_role = {
        task["approval_role"]: task["id"]
        for task in studio.planner.stage("VISUAL_PREVIEW")["tasks"]
        if task.get("approval_role")
    }
    for role in VISUAL_ROLES:
        studio.submit_review(
            "formal",
            task_by_role[role],
            "PASS",
            notes="current rendered artifact meets the bar",
            evidence=("file://preview.mp4", "file://contact.jpg"),
            findings=("actual rendered media inspected",),
            scorecard=_scores(role),
            benchmark_refs=("ref://film", "ref://motion", "ref://explanation"),
            target_digest="preview-digest",
        )

    process = rt.process_guard_report(rt.state("formal"))
    assert process["pass"] is True, process
    events = (tmp_path / "projects" / "formal" / "events.jsonl").read_text(encoding="utf-8")
    assert events.count("WORK_ORDER_REVIEW_COMPLETED") == 5
    assert studio.advance("formal") == "ASSET_BUILD"


def test_process_proof_is_bound_to_exact_review_inputs(tmp_path):
    rt = _runtime(tmp_path)
    rt.create_project("tamper")
    state = rt.state("tamper")
    state.stage = "VISUAL_PREVIEW"
    for name, digest in (
        ("storyboard", "story-digest"),
        ("style_bible", "style-digest"),
        ("hero_frames", "hero-digest"),
        ("benchmark_pack", "bench-digest"),
    ):
        state.artifacts[name] = ArtifactRecord(name, f"file://{name}", "LOOKDEV", digest=digest)
    rt.store.save(state)
    studio = AgenticStudio(runtime=rt)
    studio.dispatch_stage("tamper")
    studio.complete_work(
        "tamper",
        "preview_build",
        outputs={
            "visual_preview": {"uri": "file://preview.mp4", "kind": "media", "digest": "preview-digest"},
            "visual_contact_sheet": {"uri": "file://contact.jpg", "kind": "image", "digest": "contact-digest"},
        },
    )
    studio.dispatch_stage("tamper")
    task_by_role = {
        task["approval_role"]: task["id"]
        for task in studio.planner.stage("VISUAL_PREVIEW")["tasks"]
        if task.get("approval_role")
    }
    for role in VISUAL_ROLES:
        studio.submit_review(
            "tamper",
            task_by_role[role],
            "PASS",
            notes="current rendered artifact meets the bar",
            evidence=("file://preview.mp4", "file://contact.jpg"),
            findings=("actual rendered media inspected",),
            scorecard=_scores(role),
            benchmark_refs=("ref://film", "ref://motion", "ref://explanation"),
            target_digest="preview-digest",
        )

    state = rt.state("tamper")
    old = state.artifacts["benchmark_pack"]
    state.artifacts["benchmark_pack"] = ArtifactRecord(
        old.name,
        old.uri,
        old.stage,
        kind=old.kind,
        digest="changed-after-review",
        metadata=old.metadata,
    )
    rt.store.save(state)
    process = rt.process_guard_report(rt.state("tamper"))
    assert process["pass"] is False
    assert any("process_review_input_digest_mismatch" in failure for failure in process["failures"])
