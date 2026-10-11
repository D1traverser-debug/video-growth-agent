import copy
import json
from pathlib import Path

import pytest

from video_growth_agent import ArtifactRecord, ProjectStore, StudioRuntime
from video_growth_agent.execution_attestation import ExecutionAttestation, ExecutionTrustRegistry, canonical_digest
from video_growth_agent.models import QACheck, QAReport
from video_growth_agent.resources import data_path
from video_growth_agent.studio_agents import AgenticStudio
from video_growth_agent.system_audit import _artifact_reachability_failures
from video_growth_agent.techniques import TechniqueLibrary


TEST_TRUST = {
    "policy": {
        "attestation_required_stages": ["VISUAL_PREVIEW"],
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


def _studio(tmp_path: Path) -> tuple[StudioRuntime, AgenticStudio]:
    runtime = StudioRuntime(store=ProjectStore(tmp_path / "projects"))
    return runtime, AgenticStudio(runtime=runtime)


def _review_runtime(tmp_path: Path) -> StudioRuntime:
    return StudioRuntime(
        store=ProjectStore(tmp_path / "projects"),
        execution_trust=ExecutionTrustRegistry(config=TEST_TRUST),
    )


def _completed_creative_review(runtime: StudioRuntime, project_id: str) -> tuple[AgenticStudio, dict, dict]:
    runtime.create_project(project_id)
    state = runtime.state(project_id)
    state.stage = "VISUAL_PREVIEW"
    for name, digest in (
        ("storyboard", "story-digest"),
        ("style_bible", "style-digest"),
        ("hero_frames", "hero-digest"),
        ("benchmark_pack", "bench-digest"),
    ):
        state.artifacts[name] = ArtifactRecord(name, f"file://{name}", "LOOKDEV", digest=digest)
    runtime.store.save(state)
    studio = AgenticStudio(runtime=runtime)
    studio.dispatch_stage(project_id)
    studio.complete_work(
        project_id,
        "preview_build",
        outputs={
            "visual_preview": {"uri": "file://preview.mp4", "kind": "media", "digest": "preview-digest"},
            "visual_contact_sheet": {"uri": "file://contact.jpg", "kind": "image", "digest": "contact-digest"},
        },
    )
    studio.dispatch_stage(project_id)
    contract = runtime.review_execution_contract(project_id, "creative_preview")
    studio.submit_review(
        project_id,
        "creative_preview",
        "PASS",
        notes="inspected",
        evidence=("file://preview.mp4", "file://contact.jpg"),
        findings=("current media inspected",),
        target_digest="preview-digest",
    )
    order_path = runtime.store.project_dir(project_id) / "work_orders" / "VISUAL_PREVIEW" / "creative_preview.json"
    order = json.loads(order_path.read_text(encoding="utf-8"))
    return studio, contract, order


def _attestation(order: dict, packet_digest: str, suffix: str) -> ExecutionAttestation:
    input_digests = order["result"].get("input_digests", {})
    return ExecutionAttestation(
        executor_id="test-executor",
        provider="test-provider",
        model="test-model",
        execution_id=f"exec-{suffix}",
        provider_run_id=f"run-{suffix}",
        context_id=f"ctx-{suffix}",
        trace_id=f"trace-{suffix}",
        work_order_id=order["work_order_id"],
        stage="VISUAL_PREVIEW",
        agent_id=order["agent_id"],
        packet_digest=packet_digest,
        result_digest=canonical_digest(order["result"]),
        observed_input_digests=tuple(d for d in input_digests.values() if d),
        isolated_context=True,
        sibling_verdicts_visible=False,
        proof_ref=f"proof://{suffix}",
    )


def _append_historical_attestation(runtime: StudioRuntime, project_id: str, suffix: str) -> None:
    old = ExecutionAttestation(
        executor_id="test-executor",
        provider="test-provider",
        model="test-model",
        execution_id=f"exec-{suffix}",
        provider_run_id=f"run-{suffix}",
        context_id=f"ctx-{suffix}",
        trace_id=f"trace-{suffix}",
        work_order_id="historical-work-order",
        stage="VISUAL_PREVIEW",
        agent_id="creative_director",
        packet_digest="historical-packet",
        result_digest="historical-result",
        observed_input_digests=("historical-input",),
        proof_ref=f"proof://historical-{suffix}",
    )
    runtime.store.append_receipt(
        project_id,
        "AGENT_EXECUTION_ATTESTED",
        {
            "stage": "VISUAL_PREVIEW",
            "task_id": "creative_preview",
            "work_order_id": "historical-work-order",
            "wave": 2,
            "attestation_digest": old.digest,
            "attestation": old.to_dict(),
        },
    )


def test_upstream_change_retires_downstream_artifact_and_completed_work_order(tmp_path):
    runtime, studio = _studio(tmp_path)
    runtime.create_project("replay")
    first = studio.dispatch_stage("replay")[0]
    studio.complete_work(
        "replay",
        "intake",
        outputs={"brief": {"uri": "file://brief-v1", "digest": "brief-v1"}},
    )
    assert studio.advance("replay") == "POSITIONING"
    studio.dispatch_stage("replay")
    studio.complete_work(
        "replay",
        "positioning_build",
        outputs={"positioning": {"uri": "file://positioning-v1", "digest": "positioning-v1"}},
    )
    assert "positioning" in runtime.state("replay").artifacts

    runtime.record_artifact(
        "replay",
        "brief",
        "file://brief-v2",
        "INTAKE",
        digest="brief-v2",
    )
    state = runtime.state("replay")
    assert state.stage == "INTAKE"
    assert state.artifacts["brief"].digest == "brief-v2"
    assert "positioning" not in state.artifacts

    rerun = studio.dispatch_stage("replay")[0]
    assert rerun.status == "READY"
    assert rerun.work_order_id != first.work_order_id
    events = (tmp_path / "projects" / "replay" / "events.jsonl").read_text(encoding="utf-8")
    assert "WORK_ORDER_COMPLETED" in events
    assert "WORK_ORDER_RETIRED" in events


def test_ffmpeg_measure_cannot_be_completed_as_fabricated_artifact(tmp_path):
    runtime, studio = _studio(tmp_path)
    runtime.create_project("qa")
    state = runtime.state("qa")
    state.stage = "TECH_QA"
    state.artifacts["final_candidate"] = ArtifactRecord(
        "final_candidate",
        "file://candidate.mp4",
        "SOUND",
        kind="media",
        digest="candidate-sha",
    )
    runtime.store.save(state)

    orders = studio.dispatch_stage("qa")
    measure = next(order for order in orders if order.task_id == "media_qa")
    assert measure.status == "READY"
    with pytest.raises(ValueError, match="complete_media_qa"):
        studio.complete_work(
            "qa",
            "media_qa",
            outputs={"technical_qa": {"uri": "file://fake.json", "kind": "qa_report"}},
        )

    report = QAReport(
        media_uri="file://candidate.mp4",
        checks=tuple(
            QACheck(check_id, "PASS", "measured")
            for check_id in ("video_stream", "stream_duration_match", "true_peak", "black_frames")
        ),
        metadata={"checker": "ffmpeg-ffprobe-v0.2", "sha256": "candidate-sha"},
    )
    completed = studio.complete_media_qa("qa", "media_qa", report)
    assert completed.status == "COMPLETED"
    qa_artifact = runtime.state("qa").artifacts["technical_qa"]
    assert qa_artifact.digest
    assert qa_artifact.metadata["work_order_id"] == completed.work_order_id
    assert runtime.machine_guard_report(runtime.state("qa"))["pass"] is True

    orders = studio.dispatch_stage("qa")
    review = next(order for order in orders if order.task_id == "technical_review")
    assert review.status == "READY"


def test_artifact_reachability_catches_hidden_qa_side_effect():
    workflow = json.loads(data_path("workflow.json").read_text(encoding="utf-8"))
    plan = json.loads(data_path("execution-plan.json").read_text(encoding="utf-8"))
    broken = copy.deepcopy(plan)
    broken["stages"]["TECH_QA"]["tasks"][0]["outputs"] = []
    failures = _artifact_reachability_failures(workflow, broken)
    assert "artifact_input_unreachable:TECH_QA/technical_review:technical_qa" in failures
    assert "workflow_required_artifact_unreachable:TECH_QA:technical_qa" in failures


def test_candidate_techniques_are_explicit_opt_in_only():
    library = TechniqueLibrary()
    assert library.find({"keyframe"}) == []
    candidate_ids = {item.technique_id for item in library.find({"keyframe"}, validated_only=False)}
    assert "T-009" in candidate_ids


def test_historical_attestation_does_not_authorize_new_run_but_identity_cannot_be_reused(tmp_path):
    runtime = _review_runtime(tmp_path)
    _, contract, order = _completed_creative_review(runtime, "history-block")
    _append_historical_attestation(runtime, "history-block", "old")
    with pytest.raises(ValueError, match="execution_id=exec-old"):
        runtime.record_execution_attestation(
            "history-block",
            "creative_preview",
            _attestation(order, contract["packet_digest"], "old"),
        )

    runtime2 = StudioRuntime(
        store=ProjectStore(tmp_path / "projects-2"),
        execution_trust=ExecutionTrustRegistry(config=TEST_TRUST),
    )
    _, contract2, order2 = _completed_creative_review(runtime2, "history-new")
    _append_historical_attestation(runtime2, "history-new", "old")
    receipt = runtime2.record_execution_attestation(
        "history-new",
        "creative_preview",
        _attestation(order2, contract2["packet_digest"], "fresh"),
    )
    assert receipt
