import json
from pathlib import Path

import pytest

from video_growth_agent import ArtifactRecord, GateBlocked, ProjectStore, StudioRuntime
from video_growth_agent.execution_attestation import ExecutionAttestation, ExecutionTrustRegistry, canonical_digest
from video_growth_agent.studio_agents import AgenticStudio


VISUAL_ROLES = [
    "creative_director",
    "art_director",
    "motion_director",
    "director",
    "retention_editor",
]

TEST_EXECUTION_CONFIG = {
    "version": "test",
    "policy": {
        "attestation_required_stages": ["LOOKDEV", "VISUAL_PREVIEW", "ROUGH_CUT", "RELEASE"],
        "blind_reviews_only": True,
        "require_isolated_context": True,
        "forbid_sibling_verdict_visibility": True,
        "require_unique_execution_id_within_wave": True,
        "require_unique_provider_run_id_within_wave": True,
        "require_unique_context_id_within_wave": True,
        "require_unique_trace_id_within_wave": True,
        "require_all_input_digests_observed": True,
        "require_proof_ref": True,
    },
    "trusted_executors": {
        "test-executor": {"provider": "test-provider", "models": ["test-model"]}
    },
}


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


def _runtime(tmp_path: Path, *, trusted: bool = True) -> StudioRuntime:
    trust = ExecutionTrustRegistry(config=TEST_EXECUTION_CONFIG) if trusted else None
    return StudioRuntime(store=ProjectStore(tmp_path / "projects"), execution_trust=trust)


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


def _attest_completed_review(
    rt: StudioRuntime,
    project_id: str,
    task_id: str,
    packet_digest: str,
    *,
    identity_suffix: str | None = None,
    context_id: str | None = None,
) -> None:
    state = rt.state(project_id)
    order_path = rt.store.project_dir(project_id) / "work_orders" / state.stage / f"{task_id}.json"
    order = json.loads(order_path.read_text(encoding="utf-8"))
    suffix = identity_suffix or task_id
    input_digests = order["result"].get("input_digests", {})
    attestation = ExecutionAttestation(
        executor_id="test-executor",
        provider="test-provider",
        model="test-model",
        execution_id=f"exec-{suffix}",
        provider_run_id=f"run-{suffix}",
        context_id=context_id or f"ctx-{suffix}",
        trace_id=f"trace-{suffix}",
        work_order_id=order["work_order_id"],
        stage=state.stage,
        agent_id=order["agent_id"],
        packet_digest=packet_digest,
        result_digest=canonical_digest(order["result"]),
        observed_input_digests=tuple(d for d in input_digests.values() if d),
        isolated_context=True,
        sibling_verdicts_visible=False,
        group_id=f"group-{project_id}-{state.stage}",
        proof_ref=f"test-trace://{suffix}",
    )
    rt.record_execution_attestation(project_id, task_id, attestation)


def _formal_visual_review(rt: StudioRuntime, project_id: str, *, attest: bool = True) -> AgenticStudio:
    rt.create_project(project_id)
    state = rt.state(project_id)
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
        task_id = task_by_role[role]
        contract = rt.review_execution_contract(project_id, task_id)
        studio.submit_review(
            project_id,
            task_id,
            "PASS",
            notes="current rendered artifact meets the bar",
            evidence=("file://preview.mp4", "file://contact.jpg"),
            findings=("actual rendered media inspected",),
            scorecard=_scores(role),
            benchmark_refs=("ref://film", "ref://motion", "ref://explanation"),
            target_digest="preview-digest",
        )
        if attest:
            _attest_completed_review(rt, project_id, task_id, contract["packet_digest"])
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


def test_formal_agentic_visual_preview_requires_execution_attestations(tmp_path):
    rt = _runtime(tmp_path)
    _formal_visual_review(rt, "formal-no-attestation", attest=False)

    process = rt.process_guard_report(rt.state("formal-no-attestation"))
    assert process["pass"] is False
    assert any("process_execution_attestation_missing_or_ambiguous" in item for item in process["failures"])
    assert rt.gate_report("formal-no-attestation")["pass"] is False


def test_formal_agentic_visual_preview_with_unique_attestations_can_advance(tmp_path):
    rt = _runtime(tmp_path)
    studio = _formal_visual_review(rt, "formal")

    process = rt.process_guard_report(rt.state("formal"))
    assert process["pass"] is True, process
    report = rt.gate_report("formal")
    assert report["pass"] is True, report
    events = (tmp_path / "projects" / "formal" / "events.jsonl").read_text(encoding="utf-8")
    assert events.count("WORK_ORDER_REVIEW_COMPLETED") == 5
    assert events.count("AGENT_EXECUTION_ATTESTED") == 5
    assert studio.advance("formal") == "ASSET_BUILD"


def test_production_default_trust_registry_rejects_unregistered_executor(tmp_path):
    rt = _runtime(tmp_path, trusted=False)
    _formal_visual_review(rt, "untrusted", attest=False)
    task_id = "creative_preview"
    contract = rt.review_execution_contract("untrusted", task_id)
    state = rt.state("untrusted")
    order_path = rt.store.project_dir("untrusted") / "work_orders" / state.stage / f"{task_id}.json"
    order = json.loads(order_path.read_text(encoding="utf-8"))
    input_digests = order["result"].get("input_digests", {})
    attestation = ExecutionAttestation(
        executor_id="test-executor",
        provider="test-provider",
        model="test-model",
        execution_id="exec-untrusted",
        provider_run_id="run-untrusted",
        context_id="ctx-untrusted",
        trace_id="trace-untrusted",
        work_order_id=order["work_order_id"],
        stage=state.stage,
        agent_id=order["agent_id"],
        packet_digest=contract["packet_digest"],
        result_digest=canonical_digest(order["result"]),
        observed_input_digests=tuple(d for d in input_digests.values() if d),
        proof_ref="test-trace://untrusted",
    )
    with pytest.raises(ValueError, match="execution_executor_untrusted"):
        rt.record_execution_attestation("untrusted", task_id, attestation)


def test_same_context_cannot_masquerade_as_two_blind_reviewers(tmp_path):
    rt = _runtime(tmp_path)
    rt.create_project("duplicate")
    state = rt.state("duplicate")
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
    studio.dispatch_stage("duplicate")
    studio.complete_work(
        "duplicate",
        "preview_build",
        outputs={
            "visual_preview": {"uri": "file://preview.mp4", "kind": "media", "digest": "preview-digest"},
            "visual_contact_sheet": {"uri": "file://contact.jpg", "kind": "image", "digest": "contact-digest"},
        },
    )
    studio.dispatch_stage("duplicate")

    first = "creative_preview"
    first_contract = rt.review_execution_contract("duplicate", first)
    studio.submit_review(
        "duplicate",
        first,
        "PASS",
        notes="pass",
        evidence=("file://preview.mp4", "file://contact.jpg"),
        findings=("inspected",),
        scorecard=_scores("creative_director"),
        benchmark_refs=("ref://film", "ref://motion", "ref://explanation"),
        target_digest="preview-digest",
    )
    _attest_completed_review(rt, "duplicate", first, first_contract["packet_digest"], context_id="shared-context")

    second = "art_preview"
    second_contract = rt.review_execution_contract("duplicate", second)
    studio.submit_review(
        "duplicate",
        second,
        "PASS",
        notes="pass",
        evidence=("file://preview.mp4", "file://contact.jpg"),
        findings=("inspected",),
        scorecard=_scores("art_director"),
        benchmark_refs=("ref://film", "ref://motion", "ref://explanation"),
        target_digest="preview-digest",
    )
    with pytest.raises(ValueError, match="context_id=shared-context"):
        _attest_completed_review(rt, "duplicate", second, second_contract["packet_digest"], context_id="shared-context")


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
    assert any("process_execution_packet_digest_mismatch" in failure for failure in process["failures"])


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


def test_deleted_execution_attestation_invalidates_gate(tmp_path):
    rt = _runtime(tmp_path)
    _formal_visual_review(rt, "attestation-proof")

    receipts_dir = tmp_path / "projects" / "attestation-proof" / "receipts"
    attestation_receipts = []
    for path in receipts_dir.glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("event") == "AGENT_EXECUTION_ATTESTED":
            attestation_receipts.append(path)
    assert len(attestation_receipts) == 5
    attestation_receipts[0].unlink()

    process = rt.process_guard_report(rt.state("attestation-proof"))
    assert process["pass"] is False
    assert any("process_execution_attestation_missing_or_ambiguous" in failure for failure in process["failures"])
