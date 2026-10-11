import copy
import json
from pathlib import Path

import pytest

from video_growth_agent import ArtifactRecord, ProjectStore, StudioRuntime
from video_growth_agent.models import QACheck, QAReport
from video_growth_agent.resources import data_path
from video_growth_agent.studio_agents import AgenticStudio
from video_growth_agent.system_audit import _artifact_reachability_failures
from video_growth_agent.techniques import TechniqueLibrary


def _studio(tmp_path: Path) -> tuple[StudioRuntime, AgenticStudio]:
    runtime = StudioRuntime(store=ProjectStore(tmp_path / "projects"))
    return runtime, AgenticStudio(runtime=runtime)


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
