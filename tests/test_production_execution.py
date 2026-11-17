from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import shutil
import subprocess
import time
import zipfile

import pytest
from PIL import Image

from video_studio.engine import StudioEngine
from video_studio.production.worker_pool import run_ready_tool_tasks
from video_studio.engine import GateError


def _brief():
    return {
        "goal": "Assemble and package a short audiovisual production master from declared shot and audio assets.",
        "audience": "Video production operators.",
        "deliverables": [
            "final-video", "audio-master", "captions", "cover", "reproducible-project-source-bundle",
            "publish-copy", "rights-manifest", "technical-qa", "delivery-package",
        ],
    }


def _simple_task(task_id: str, inputs=()):
    return {
        "task_id": task_id, "title": task_id, "kind": "production",
        "executor": "agent", "depends_on": [], "inputs": list(inputs),
        "outputs": [f"{task_id}-artifact"],
        "acceptance": {"observable": "A concrete output artifact is registered."},
    }


def _ffmpeg(path: Path, *args: str) -> None:
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", *args, "-y", str(path)],
        check=True, capture_output=True, text=True,
    )


def _source_assets(root: Path):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg and FFprobe are required for production execution tests")
    shot1 = root / "shot-01.mp4"
    shot2 = root / "shot-02.mp4"
    audio = root / "audio-mix.wav"
    _ffmpeg(shot1, "-f", "lavfi", "-i", "color=c=blue:s=320x568:d=2:r=10", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an")
    _ffmpeg(shot2, "-f", "lavfi", "-i", "color=c=red:s=320x568:d=2:r=10", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an")
    _ffmpeg(audio, "-f", "lavfi", "-i", "sine=frequency=440:duration=4", "-c:a", "pcm_s24le", "-ar", "48000", "-ac", "2")
    captions = root / "captions.srt"
    captions.write_text(
        "1\n00:00:00,000 --> 00:00:02,000\nFirst shot\n\n"
        "2\n00:00:02,000 --> 00:00:04,000\nSecond shot\n",
        encoding="utf-8",
    )
    cover = root / "cover.png"
    Image.new("RGB", (320, 568), "navy").save(cover)
    publish = root / "publish-copy.md"
    publish.write_text("# A short production demo\n\nA deterministic local render test.\n", encoding="utf-8")
    rights = root / "rights-manifest.json"
    rights.write_text(json.dumps({"sources": ["owner-created test assets"], "cleared": True}), encoding="utf-8")
    timeline = root / "production-timeline.json"
    timeline.write_text(json.dumps({
        "schema_version": "1.0",
        "project_id": "delivery-demo",
        "archetype": "CINEMATIC_EXPLAINER",
        "width": 320,
        "height": 568,
        "fps": 10,
        "duration_seconds": 4,
        "clips": [
            {"input_name": "shot-01", "source_start_seconds": 0, "duration_seconds": 2, "fit": "cover"},
            {"input_name": "shot-02", "source_start_seconds": 0, "duration_seconds": 2, "fit": "cover"},
        ],
        "audio_tracks": [
            {"input_name": "audio-mix", "start_seconds": 0, "duration_seconds": 4, "gain_db": -6, "role": "MIX"},
        ],
        "audio_required": True,
        "captions_input": "captions",
        "burn_captions": False,
        "video_output": "final-video",
        "audio_output": "audio-master",
        "receipt_output": "render-receipt",
    }, indent=2), encoding="utf-8")
    return {
        "shot-01": (shot1, "video", "video/mp4", "OWNED"),
        "shot-02": (shot2, "video", "video/mp4", "OWNED"),
        "audio-mix": (audio, "audio", "audio/wav", "OWNED"),
        "captions": (captions, "subtitle", "application/x-subrip", "OWNED"),
        "cover": (cover, "image", "image/png", "OWNED"),
        "publish-copy": (publish, "document", "text/markdown", "OWNED"),
        "rights-manifest": (rights, "evidence", "application/json", "NOT_APPLICABLE"),
        "timeline-spec": (timeline, "document", "application/json", "NOT_APPLICABLE"),
    }


def test_end_to_end_production_render_qa_and_delivery_package(tmp_path):
    engine = StudioEngine(tmp_path / "workspace")
    engine.create_project("delivery-demo", "Production delivery demo", _brief())
    assets = _source_assets(tmp_path)
    for name, (path, kind, media_type, rights) in assets.items():
        engine.import_asset("delivery-demo", name, path, kind=kind, media_type=media_type, rights_status=rights)

    package_map = {
        "final-video": "deliverables/final-video.mp4",
        "audio-master": "deliverables/audio-master.wav",
        "captions": "deliverables/captions.srt",
        "cover": "deliverables/cover.png",
        "publish-copy": "publish/publish-copy.md",
        "rights-manifest": "rights/rights-manifest.json",
        "timeline-spec": "project/production-timeline.json",
        "shot-01": "project/assets/shot-01.mp4",
        "shot-02": "project/assets/shot-02.mp4",
        "audio-mix": "project/assets/audio-mix.wav",
        "render-receipt": "evidence/render-receipt.json",
        "technical-qa": "evidence/technical-qa.json",
    }
    required = list(package_map)
    engine.add_tasks("delivery-demo", [
        {
            "task_id": "render-master",
            "title": "Assemble the exact audiovisual master and separate audio master",
            "kind": "production_render",
            "executor": "tool",
            "depends_on": [],
            "inputs": ["timeline-spec", "shot-01", "shot-02", "audio-mix", "captions"],
            "outputs": ["final-video", "audio-master", "render-receipt"],
            "requirements": {"production": {"operation": "ffmpeg_assemble", "render_spec_input": "timeline-spec"}},
            "acceptance": {"render": "Produce a non-empty MP4, 24-bit WAV master and digest-bound render receipt."},
        },
        {
            "task_id": "technical-qa",
            "title": "Measure the exact rendered master",
            "kind": "technical_measurement",
            "executor": "tool",
            "depends_on": ["render-master"],
            "inputs": ["final-video"],
            "outputs": ["technical-qa"],
            "requirements": {
                "tools": ["ffprobe"],
                "resolution": "320x568",
                "frame_rate": 10,
                "duration_min_seconds": 3.9,
                "duration_max_seconds": 4.1,
                "audio_required": True,
            },
            "acceptance": {"qa": "The exact final candidate has the requested streams, dimensions, frame rate and duration."},
        },
        {
            "task_id": "package-delivery",
            "title": "Package all requested outputs and editable source dependencies",
            "kind": "delivery_package",
            "executor": "tool",
            "depends_on": ["technical-qa"],
            "inputs": required,
            "outputs": ["delivery-package", "delivery-manifest"],
            "requirements": {"production": {
                "operation": "delivery_package",
                "required_artifacts": required,
                "package_map": package_map,
                "package_output": "delivery-package",
                "manifest_output": "delivery-manifest",
                "expected_types": {
                    "final-video": {"kind": "video", "media_type": "video/mp4"},
                    "audio-master": {"kind": "audio", "media_type": "audio/wav"},
                    "captions": {"kind": "subtitle", "media_type": "application/x-subrip"},
                    "cover": {"kind": "image", "media_type": "image/png"},
                    "publish-copy": {"kind": "document", "media_type": "text/markdown"},
                    "rights-manifest": {"kind": "evidence", "media_type": "application/json"},
                    "timeline-spec": {"kind": "document", "media_type": "application/json"},
                    "shot-01": {"kind": "video", "media_type": "video/mp4"},
                    "shot-02": {"kind": "video", "media_type": "video/mp4"},
                    "audio-mix": {"kind": "audio", "media_type": "audio/wav"},
                    "render-receipt": {"kind": "evidence", "media_type": "application/json"},
                    "technical-qa": {"kind": "qa_report", "media_type": "application/json"}
                }
            }},
            "acceptance": {"delivery": "Every required deliverable and source dependency is present with exact artifact identity and digest."},
        },
    ])

    result = run_ready_tool_tasks(engine, "delivery-demo", worker_prefix="test-renderer", max_workers=2)
    assert result["scheduler_status"] == "TASK_GRAPH_COMPLETE_NOT_RELEASED", result
    assert [item["task_id"] for item in result["completed"]] == ["render-master", "technical-qa", "package-delivery"]
    assert result["failed"] == []
    assert result["ready_tool_tasks_without_registered_executor"] == []

    tasks = {item["task_id"]: item for item in engine.list_tasks("delivery-demo")}
    assert {key: value["status"] for key, value in tasks.items()} == {
        "render-master": "COMPLETED",
        "technical-qa": "COMPLETED",
        "package-delivery": "COMPLETED",
    }

    assert engine.audit("delivery-demo")["pass"] is True
    artifact_path = next(
        path for path in (engine._project_dir("delivery-demo") / "artifacts" / "production" / "package-delivery").rglob("delivery-package.zip")
    )
    assert artifact_path.is_file()
    with zipfile.ZipFile(artifact_path) as archive:
        names = set(archive.namelist())
    assert set(package_map.values()).issubset(names)
    assert "delivery-manifest.json" in names
    assert engine.audit("delivery-demo")["pass"] is True


def test_local_tool_pool_claims_independent_render_tasks_in_the_same_round(tmp_path):
    engine = StudioEngine(tmp_path / "parallel-workspace")
    engine.create_project("parallel-demo", "Parallel render demo", _brief())
    assets = _source_assets(tmp_path)
    for name, (path, kind, media_type, rights) in assets.items():
        engine.import_asset("parallel-demo", name, path, kind=kind, media_type=media_type, rights_status=rights)

    tasks = []
    for index in (1, 2):
        spec_name = f"timeline-{index}"
        spec = json.loads((tmp_path / "production-timeline.json").read_text(encoding="utf-8"))
        spec["project_id"] = "parallel-demo"
        spec["video_output"] = f"final-video-{index}"
        spec["audio_output"] = f"audio-master-{index}"
        spec["receipt_output"] = f"render-receipt-{index}"
        spec_path = tmp_path / f"{spec_name}.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        engine.import_asset("parallel-demo", spec_name, spec_path, kind="document", media_type="application/json", rights_status="NOT_APPLICABLE")
        tasks.append({
            "task_id": f"render-{index}",
            "title": f"Render independent candidate {index}",
            "kind": "production_render",
            "executor": "tool",
            "depends_on": [],
            "inputs": [spec_name, "shot-01", "shot-02", "audio-mix", "captions"],
            "outputs": [f"final-video-{index}", f"audio-master-{index}", f"render-receipt-{index}"],
            "requirements": {"production": {"operation": "ffmpeg_assemble", "render_spec_input": spec_name}},
            "acceptance": {"render": "Produce a digest-bound audiovisual candidate."},
        })
    engine.add_tasks("parallel-demo", tasks)
    result = run_ready_tool_tasks(engine, "parallel-demo", worker_prefix="parallel-renderer", max_workers=2)
    assert result["scheduler_status"] == "TASK_GRAPH_COMPLETE_NOT_RELEASED", result
    assert {item["task_id"] for item in result["claimed"]} == {"render-1", "render-2"}
    assert {item["task_id"] for item in result["completed"]} == {"render-1", "render-2"}
    assert len({item["worker_id"] for item in result["claimed"]}) == 2
    assert all(task["status"] == "COMPLETED" for task in engine.list_tasks("parallel-demo"))



def test_trusted_python_frame_renderer_produces_a_real_motion_shot(tmp_path):
    from video_studio.production.contracts import FrameRenderSpec, ProductionContractError

    engine = StudioEngine(tmp_path / "motion-workspace")
    engine.create_project("motion-demo", "Trusted motion renderer demo", _brief())
    renderer = tmp_path / "renderer.py"
    renderer.write_text(
        "from PIL import Image, ImageDraw\n"
        "def render_frame(t, width, height, assets, params):\n"
        "    image = Image.new('RGB', (width, height), tuple(params['background']))\n"
        "    draw = ImageDraw.Draw(image)\n"
        "    x = int((0.1 + 0.8 * t / params['duration']) * width)\n"
        "    y = height // 2\n"
        "    radius = max(3, min(width, height) // 12)\n"
        "    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=tuple(params['accent']))\n"
        "    draw.text((8, 8), params['title'], fill=(255, 255, 255))\n"
        "    return image\n",
        encoding="utf-8",
    )
    frame_spec = tmp_path / "frame-render-spec.json"
    frame_spec.write_text(json.dumps({
        "schema_version": "1.0",
        "project_id": "motion-demo",
        "renderer_input": "renderer-script",
        "entrypoint": "render_frame",
        "width": 160,
        "height": 284,
        "fps": 5,
        "duration_seconds": 2,
        "asset_inputs": [],
        "params": {"duration": 2, "title": "Motion test", "background": [7, 17, 35], "accent": [0, 220, 255]},
        "trusted_code_execution": True,
        "video_output": "shot-candidate",
        "receipt_output": "shot-render-receipt",
    }, indent=2), encoding="utf-8")
    engine.import_asset("motion-demo", "renderer-script", renderer, kind="source_code", media_type="text/x-python", rights_status="OWNED")
    engine.import_asset("motion-demo", "frame-render-spec", frame_spec, kind="document", media_type="application/json", rights_status="NOT_APPLICABLE")
    engine.add_tasks("motion-demo", [{
        "task_id": "render-motion-shot",
        "title": "Render a project-owned animated scene with explicit code execution approval",
        "kind": "production_render",
        "executor": "tool",
        "depends_on": [],
        "inputs": ["renderer-script", "frame-render-spec"],
        "outputs": ["shot-candidate", "shot-render-receipt"],
        "requirements": {"production": {
            "operation": "python_frame_render",
            "render_spec_input": "frame-render-spec",
            "trusted_code_execution": True,
        }},
        "acceptance": {"render": "Produce exactly 10 frames and a digest-bound candidate receipt."},
    }])

    result = run_ready_tool_tasks(engine, "motion-demo", worker_prefix="motion-renderer", max_workers=1)
    assert result["scheduler_status"] == "TASK_GRAPH_COMPLETE_NOT_RELEASED", result
    assert result["failed"] == []
    task = engine.list_tasks("motion-demo")[0]
    assert task["status"] == "COMPLETED"
    output_dir = engine._project_dir("motion-demo") / "artifacts" / "production" / "render-motion-shot" / "attempt-1"
    shot = output_dir / "shot-candidate.mp4"
    receipt = json.loads((output_dir / "shot-render-receipt.json").read_text(encoding="utf-8"))
    assert shot.is_file() and shot.stat().st_size > 0
    assert receipt["renderer"] == "python-frame-renderer-v1"
    assert receipt["trusted_project_code_execution"] is True
    assert receipt["candidate_only"] is True
    assert receipt["frame_count"] == 10
    assert engine.audit("motion-demo")["pass"] is True

    invalid = json.loads(frame_spec.read_text(encoding="utf-8"))
    invalid["trusted_code_execution"] = False
    invalid_spec = FrameRenderSpec.from_dict(invalid)
    with pytest.raises(ProductionContractError, match="trusted_code_execution=true"):
        invalid_spec.validate_inputs({"renderer-script"})



def test_executor_registry_reports_unknown_tool_tasks_without_claiming_them(tmp_path):
    from video_studio.production.registry import PRODUCTION_EXECUTORS

    assert set(PRODUCTION_EXECUTORS.operations()) == {
        "python_frame_render", "ffmpeg_assemble", "delivery_package", "ffprobe_media_qa",
    }
    engine = StudioEngine(tmp_path / "unknown-tool-workspace")
    engine.create_project("unknown-tool", "Unregistered tool demo", _brief())
    engine.add_tasks("unknown-tool", [{
        "task_id": "unknown-local-tool",
        "title": "A tool task with no registered executor",
        "kind": "unknown_tool_operation",
        "executor": "tool",
        "depends_on": [],
        "inputs": [],
        "outputs": ["unproduced-output"],
        "requirements": {"tool_name": "not-installed"},
        "acceptance": {"execution": "Must not be silently claimed or marked complete."},
    }])
    result = run_ready_tool_tasks(engine, "unknown-tool", max_workers=2)
    assert result["scheduler_status"] == "BLOCKED_UNREGISTERED_TOOL_EXECUTOR"
    assert result["claimed"] == []
    assert result["completed"] == []
    assert result["ready_tool_tasks_without_registered_executor"][0]["task_id"] == "unknown-local-tool"
    assert engine.list_tasks("unknown-tool")[0]["status"] == "READY"


def test_local_tool_completion_does_not_claim_project_complete_while_agent_work_is_ready(tmp_path):
    engine = StudioEngine(tmp_path / "mixed-workspace")
    engine.create_project("mixed", "Mixed executor graph", _brief())
    assets = _source_assets(tmp_path)
    source_path = assets["shot-01"][0]
    engine.import_asset("mixed", "shot-01", source_path, kind="video", media_type="video/mp4", rights_status="OWNED")
    engine.add_tasks("mixed", [
        {
            "task_id": "agent-research", "title": "Research and author the source package",
            "kind": "editorial_research", "executor": "agent", "depends_on": [],
            "inputs": [], "outputs": ["research-package"],
            "acceptance": {"research": "Every claim has a source and counterevidence."},
        },
        {
            "task_id": "technical-measurement", "title": "Measure the imported shot",
            "kind": "technical_measurement", "executor": "tool", "depends_on": [],
            "inputs": ["shot-01"], "outputs": ["technical-qa"],
            "requirements": {"tools": ["ffmpeg", "ffprobe"], "audio_required": False},
            "acceptance": {"qa": "Produce a digest-bound technical report."},
        },
    ])
    result = run_ready_tool_tasks(engine, "mixed", max_workers=1)
    assert result["scheduler_status"] == "AWAITING_AGENT_WORK"
    assert result["project_status"] == "IN_PROGRESS"
    assert result["ready_by_executor"]["agent"] == ["agent-research"]
    assert result["task_counts"]["COMPLETED"] == 1
    assert engine.resume("mixed")["next_action"].startswith("Dispatch the READY agent work packets")


def test_worker_pool_heartbeats_long_running_tool_claim(tmp_path, monkeypatch):
    import video_studio.production.worker_pool as worker_pool

    engine = StudioEngine(tmp_path / "heartbeat-workspace")
    engine.create_project("heartbeat", "Lease heartbeat demo", _brief())
    engine.add_tasks("heartbeat", [{
        "task_id": "slow-measurement", "title": "Simulate a long-running local measurement",
        "kind": "technical_measurement", "executor": "tool", "depends_on": [],
        "inputs": [], "outputs": ["measurement-receipt"],
        "requirements": {"tools": ["ffprobe"]},
        "acceptance": {"measurement": "Complete under a renewed worker lease."},
    }])
    original_heartbeat = engine.heartbeat
    heartbeat_calls = []

    def counted_heartbeat(*args, **kwargs):
        heartbeat_calls.append(args[1])
        return original_heartbeat(*args, **kwargs)

    monkeypatch.setattr(engine, "heartbeat", counted_heartbeat)

    def slow_complete(active_engine, project_id, task_id, worker_id, claim_token):
        time.sleep(0.14)
        output = active_engine._project_dir(project_id) / "artifacts" / "measurement.json"
        output.write_text(json.dumps({"measurement": "complete"}), encoding="utf-8")
        return active_engine.complete_task(project_id, task_id, worker_id, claim_token, {
            "measurement-receipt": {
                "path": str(output), "kind": "qa_report", "media_type": "application/json",
                "rights_status": "NOT_APPLICABLE",
            }
        })

    monkeypatch.setattr(worker_pool, "run_claimed_tool_task", slow_complete)
    result = run_ready_tool_tasks(
        engine, "heartbeat", max_workers=1, lease_seconds=30,
        heartbeat_interval_seconds=0.02,
    )
    assert heartbeat_calls
    assert result["scheduler_status"] == "TASK_GRAPH_COMPLETE_NOT_RELEASED"
    assert engine.list_tasks("heartbeat")[0]["status"] == "COMPLETED"


def test_completion_binds_exact_input_artifact_digest_and_rejects_mutated_claim_input(tmp_path):
    engine = StudioEngine(tmp_path / "lineage-workspace")
    engine.create_project("lineage", "Input lineage demo", _brief())
    source = tmp_path / "source.txt"
    source.write_text("approved source bytes", encoding="utf-8")
    imported = engine.import_asset(
        "lineage", "source-evidence", source, kind="evidence",
        media_type="text/plain", rights_status="NOT_APPLICABLE",
    )
    engine.add_tasks("lineage", [_simple_task("consume-source", inputs=["source-evidence"])])
    packet = engine.claim_next("lineage", "lineage-worker")
    output = engine._project_dir("lineage") / "artifacts" / "output.txt"
    output.write_text("derived result", encoding="utf-8")
    imported_path = Path(imported["path"])
    imported_path.write_text("tampered source bytes", encoding="utf-8")
    with pytest.raises(GateError, match="claimed input artifact bytes changed"):
        engine.complete_task("lineage", "consume-source", "lineage-worker", packet["claim"]["claim_token"], {
            "consume-source-artifact": {
                "path": str(output), "kind": "document", "media_type": "text/plain", "rights_status": "OWNED",
            }
        })
    assert engine.list_tasks("lineage")[0]["status"] == "RUNNING"
    assert engine.audit("lineage")["pass"] is False


def test_completed_task_persists_exact_input_lineage_for_resume_and_release(tmp_path):
    engine = StudioEngine(tmp_path / "lineage-complete-workspace")
    engine.create_project("lineage-complete", "Completed lineage", _brief())
    source = tmp_path / "source.txt"
    source.write_text("source bytes", encoding="utf-8")
    imported = engine.import_asset(
        "lineage-complete", "source-evidence", source, kind="evidence",
        media_type="text/plain", rights_status="NOT_APPLICABLE",
    )
    engine.add_tasks("lineage-complete", [_simple_task("consume-source", inputs=["source-evidence"])])
    packet = engine.claim_next("lineage-complete", "lineage-worker")
    output = engine._project_dir("lineage-complete") / "artifacts" / "output.txt"
    output.write_text("derived result", encoding="utf-8")
    engine.complete_task("lineage-complete", "consume-source", "lineage-worker", packet["claim"]["claim_token"], {
        "consume-source-artifact": {
            "path": str(output), "kind": "document", "media_type": "text/plain", "rights_status": "OWNED",
        }
    })
    task_record = engine.list_tasks("lineage-complete")[0]
    bindings = task_record["result"]["input_bindings"]
    assert len(bindings) == 1
    assert bindings[0]["artifact_id"] == imported["artifact_id"]
    assert bindings[0]["sha256"] == imported["sha256"]
    assert engine.resume("lineage-complete")["project_status"] == "TASK_GRAPH_COMPLETE"
    assert engine.audit("lineage-complete")["pass"] is True



def _rights_clearance_fixture(
    tmp_path: Path,
    *,
    producer_executor: str = "human",
    producer_id: str = "reviewer-01",
    reviewer_id: str = "reviewer-01",
    asset_rights_status: str = "OWNED",
    clearance_digest_override: str | None = None,
    clearance_artifact_override: str | None = None,
    clearance_rights_override: str | None = None,
    evidence_refs: list[str] | None = None,
):
    from video_studio.production.contracts import RenderSpec

    source_names = ("shot-01", "audio-mix")
    inputs = {}
    clearance_assets = []
    for name in source_names:
        source_path = tmp_path / f"{name}.bin"
        source_path.write_bytes(f"verified bytes for {name}".encode("utf-8"))
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        artifact_id = f"artifact-{name}"
        rights_status = asset_rights_status
        inputs[name] = {
            "artifact_id": artifact_id,
            "version": 1,
            "path": str(source_path),
            "sha256": digest,
            "kind": "video" if name == "shot-01" else "audio",
            "media_type": "video/mp4" if name == "shot-01" else "audio/wav",
            "rights_status": rights_status,
            "metadata": {"rights_evidence_refs": ["rights-evidence"]},
        }
        clearance_assets.append({
            "input_name": name,
            "artifact_id": clearance_artifact_override if name == "shot-01" and clearance_artifact_override else artifact_id,
            "sha256": clearance_digest_override if name == "shot-01" and clearance_digest_override else digest,
            "rights_status": clearance_rights_override if name == "shot-01" and clearance_rights_override else rights_status,
            "evidence_refs": evidence_refs if evidence_refs is not None else ["rights-evidence"],
        })

    clearance_path = tmp_path / "rights-clearance.json"
    clearance_path.write_text(json.dumps({
        "schema_version": "1.0",
        "status": "PASS",
        "reviewer_id": reviewer_id,
        "assets": clearance_assets,
    }), encoding="utf-8")
    inputs["rights-clearance"] = {
        "artifact_id": "clearance-artifact",
        "version": 1,
        "path": str(clearance_path),
        "sha256": hashlib.sha256(clearance_path.read_bytes()).hexdigest(),
        "kind": "evidence",
        "media_type": "application/json",
        "rights_status": "NOT_APPLICABLE",
        "producer_id": producer_id,
        "produced_by_task": "rights-review",
        "metadata": {},
    }
    task = {
        "task_id": "rights-review",
        "executor": producer_executor,
        "status": "COMPLETED",
        "result": {"outputs": {"rights-clearance": "clearance-artifact"}},
    }
    context = SimpleNamespace(
        inputs=inputs,
        project_id="rights-demo",
        engine=SimpleNamespace(list_tasks=lambda project_id: [task]),
    )
    spec = RenderSpec.from_dict({
        "schema_version": "1.0",
        "project_id": "rights-demo",
        "archetype": "CINEMATIC_EXPLAINER",
        "width": 320,
        "height": 568,
        "fps": 30,
        "duration_seconds": 2,
        "clips": [{"input_name": "shot-01", "source_start_seconds": 0, "duration_seconds": 2, "fit": "cover"}],
        "audio_tracks": [{"input_name": "audio-mix", "start_seconds": 0, "duration_seconds": 2, "gain_db": 0, "role": "MIX"}],
        "audio_required": True,
    })
    return context, spec


def test_render_rights_clearance_requires_exact_assets_and_completed_human_review(tmp_path):
    from video_studio.production.handlers import _validate_render_rights_clearance

    context, spec = _rights_clearance_fixture(tmp_path)
    assert _validate_render_rights_clearance(context, spec, "rights-clearance") == "AUTHORIZED"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"producer_executor": "agent"}, "completed human rights review task"),
        ({"reviewer_id": "different-reviewer"}, "reviewer_id must match"),
        ({"producer_id": "different-producer"}, "reviewer_id must match"),
        ({"clearance_digest_override": "0" * 64}, "exact source artifact"),
        ({"clearance_artifact_override": "different-artifact"}, "exact source artifact"),
        ({"clearance_rights_override": "UNKNOWN"}, "exact source artifact"),
        ({"asset_rights_status": "UNKNOWN"}, "source asset rights are not cleared"),
        ({"evidence_refs": ["unregistered-evidence"]}, "matching rights evidence refs"),
    ],
)
def test_render_rights_clearance_rejects_unproven_or_mismatched_clearance(tmp_path, overrides, message):
    from video_studio.production.contracts import ProductionContractError
    from video_studio.production.handlers import _validate_render_rights_clearance

    context, spec = _rights_clearance_fixture(tmp_path, **overrides)
    with pytest.raises(ProductionContractError, match=message):
        _validate_render_rights_clearance(context, spec, "rights-clearance")
