import json
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


def _formal_visual_review(rt: StudioRuntime, project_id: str) -> AgenticStudio:
    rt.create_project(project_id)
    state = rt.state(project_id)
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
    orders = studio.dispatch_stage(project_id)
    assert next(o for o in orders if o.task_id == "preview_build").status == "READY"
    studio.complete_work(
        project_id,
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

    studio.dispatch_stage(project_id)
    task_by_role = {
        task["approval_role"]: task["id"]
        for task in studio.planner.stage("VISUAL_PREVIEW")["tasks"]
        if task.get("approval_role")
    }
    for role in VISUAL_ROLES:
        studio.submit_review(
            project_id,
            task_by_role[role],
            "PASS",
            notes="current rendered artifact meets the bar",
            evidence=("file://preview.mp4", "file://contact.jpg"),
            findings=("actual rendered media inspected",),
            scorecard=_scores(role),
            benchmark_refs=("ref://film", "ref://motion", "ref://explanation"),
            target_digest="preview-digest",
        )
    return studio


def test_direct_runtime_advance_cannot_bypass_missing_work_orders(tmp_path):
    rt = _runtime(tmp_path)
    rt.create_project("manual")
    _force_visual_artifacts(rt, "manual")
    _sign_all_visual_roles(rt, "manual")

    report = rt.gate_report("manual")
    assert report["pass"] is False
    assert "process_work_order_missing:preview_build" in report["process_failures"]
    with pytest.raises(GateBlocked, match="process_work_order_missing:preview_build"):
        rt.advance("manual")


def test_formal_agentic_visual_preview_leaves_proof_and_can_advance(tmp_path):
    rt = _runtime(tmp_path)
    studio = _formal_visual_review(rt, "formal")

    process = rt.process_guard_report(rt.state("formal"))
    assert process["pass"] is True, process
    report = rt.gate_report("formal")
    assert report["pass"] is True, report
    events = (tmp_path / "projects" / "formal" / "events.jsonl").read_text(encoding="utf-8")
    assert events.count("WORK_ORDER_REVIEW_COMPLETED") == 5
    assert studio.advance("formal") == "ASSET_BUILD"


def test_process_proof_is_bound_to_exact_review_inputs(tmp_path):
    rt = _runtime(tmp_path)
    _formal_visual_review(rt, "tamper")

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


def test_completed_review_work_order_without_immutable_receipt_is_invalid(tmp_path):
    rt = _runtime(tmp_path)
    _formal_visual_review(rt, "receipt-proof")

    receipts_dir = tmp_path / "projects" / "receipt-proof" / "receipts"
    review_receipts = []
    for path in receipts_dir.glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("event") == "WORK_ORDER_REVIEW_COMPLETED":
            review_receipts.append(path)
    assert len(review_receipts) == 5

    review_receipts[0].unlink()
    process = rt.process_guard_report(rt.state("receipt-proof"))
    assert process["pass"] is False
    assert any("process_review_receipt_missing_or_mismatch" in failure for failure in process["failures"])
    assert rt.gate_report("receipt-proof")["pass"] is False
