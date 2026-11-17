from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from ..media import run_claimed_media_qa
from .context import ProductionTaskContext
from .contracts import FrameRenderSpec, ProductionContractError, RenderSpec
from .delivery import create_delivery_package
from .ffmpeg_assembler import FfmpegAssembler
from .python_frame_renderer import PythonFrameRenderer


def _output_payload(
    path: Path, *, kind: str, media_type: str,
    metadata: Mapping[str, Any] | None = None,
    rights_status: str = "NOT_APPLICABLE",
) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size <= 0:
        raise ProductionContractError(f"production executor output is missing or empty: {path.name}")
    if rights_status not in {"OWNED", "AUTHORIZED", "LICENSED", "PUBLIC_DOMAIN", "NOT_APPLICABLE"}:
        raise ProductionContractError(f"unsupported production output rights status: {rights_status}")
    return {
        "path": str(path), "kind": kind, "media_type": media_type,
        "rights_status": rights_status, "metadata": dict(metadata or {}),
    }


def _validate_render_rights_clearance(
    context: ProductionTaskContext, spec: RenderSpec, clearance_input: str,
) -> str:
    clearance = context.inputs.get(clearance_input)
    if not clearance:
        raise ProductionContractError(f"rights clearance is not a declared task input: {clearance_input}")
    try:
        payload = json.loads(Path(str(clearance["path"])).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductionContractError(f"cannot read structured rights clearance: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != "1.0" or payload.get("status") != "PASS":
        raise ProductionContractError("rights clearance must be schema_version 1.0 with status PASS")
    reviewer_id = payload.get("reviewer_id")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ProductionContractError("rights clearance must identify the human reviewer")
    if reviewer_id != clearance.get("producer_id"):
        raise ProductionContractError("rights clearance reviewer_id must match the clearance artifact producer_id")
    clearance_task_id = clearance.get("produced_by_task")
    clearance_artifact_id = clearance.get("artifact_id")
    if not isinstance(clearance_task_id, str) or not clearance_task_id.strip():
        raise ProductionContractError("rights clearance must be produced by a completed human rights review task")
    if not isinstance(clearance_artifact_id, str) or not clearance_artifact_id.strip():
        raise ProductionContractError("rights clearance artifact identity is missing")
    task_rows = context.engine.list_tasks(context.project_id)
    clearance_task = next(
        (item for item in task_rows if item.get("task_id") == clearance_task_id),
        None,
    )
    task_outputs = (
        clearance_task.get("result", {}).get("outputs", {})
        if isinstance(clearance_task, Mapping) and isinstance(clearance_task.get("result"), Mapping)
        else {}
    )
    if (
        not isinstance(clearance_task, Mapping)
        or clearance_task.get("executor") != "human"
        or clearance_task.get("status") != "COMPLETED"
        or clearance_artifact_id not in (task_outputs.values() if isinstance(task_outputs, Mapping) else [])
    ):
        raise ProductionContractError("rights clearance must be produced by a completed human rights review task")
    used_names = list(dict.fromkeys(
        [clip.input_name for clip in spec.clips] + [track.input_name for track in spec.audio_tracks]
    ))
    records = payload.get("assets")
    if not isinstance(records, list):
        raise ProductionContractError("rights clearance assets must be an array")
    by_name: dict[str, Mapping[str, Any]] = {}
    for record in records:
        if not isinstance(record, Mapping):
            raise ProductionContractError("rights clearance contains a malformed asset record")
        name = record.get("input_name")
        if not isinstance(name, str) or name in by_name:
            raise ProductionContractError("rights clearance asset input_name must be unique")
        by_name[name] = record
    if set(by_name) != set(used_names):
        raise ProductionContractError(
            f"rights clearance must cover exactly the rendered source assets: expected {sorted(used_names)}, got {sorted(by_name)}"
        )
    allowed = {"OWNED", "AUTHORIZED", "LICENSED", "PUBLIC_DOMAIN"}
    for name in used_names:
        source = context.inputs.get(name)
        record = by_name[name]
        if not source:
            raise ProductionContractError(f"rendered source asset is not a declared task input: {name}")
        if (
            record.get("artifact_id") != source.get("artifact_id")
            or record.get("sha256") != source.get("sha256")
            or record.get("rights_status") != source.get("rights_status")
        ):
            raise ProductionContractError(f"rights clearance does not bind the exact source artifact: {name}")
        if source.get("rights_status") not in allowed:
            raise ProductionContractError(f"source asset rights are not cleared: {name}")
        evidence_refs = record.get("evidence_refs")
        metadata = source.get("metadata", {})
        source_refs = metadata.get("rights_evidence_refs", []) if isinstance(metadata, Mapping) else []
        if (
            not isinstance(evidence_refs, list) or not evidence_refs
            or not all(isinstance(item, str) and item.strip() for item in evidence_refs)
            or not isinstance(source_refs, list) or not source_refs
            or not set(evidence_refs).issubset(set(source_refs))
        ):
            raise ProductionContractError(f"source asset lacks matching rights evidence refs: {name}")
    return "AUTHORIZED"


def execute_python_frame_render(context: ProductionTaskContext) -> dict[str, Any]:
    if context.config.get("trusted_code_execution") is not True:
        raise ProductionContractError("task config must explicitly authorize trusted_code_execution=true")
    spec_name = str(context.config.get("render_spec_input", "")).strip()
    spec_artifact = context.inputs.get(spec_name)
    if not spec_artifact:
        raise ProductionContractError(f"frame render spec is not a declared task input: {spec_name}")
    spec = FrameRenderSpec.from_dict(json.loads(Path(str(spec_artifact["path"])).read_text(encoding="utf-8")))
    result = PythonFrameRenderer().render(
        spec, input_artifacts=context.inputs, output_dir=context.output_dir,
        expected_outputs=context.outputs, project_root=context.engine._project_dir(context.project_id),
    )
    outputs = {
        spec.video_output: _output_payload(
            Path(result["video_path"]), kind="video", media_type="video/mp4",
            metadata={"production_executor": "python_frame_render", "candidate_only": True, "render_receipt_ref": spec.receipt_output},
        ),
        spec.receipt_output: _output_payload(
            Path(result["receipt_path"]), kind="evidence", media_type="application/json",
            metadata={"production_executor": "python_frame_render", "frame_count": spec.frame_count, "media_sha256": result["receipt"]["output"]["sha256"]},
        ),
    }
    completion = context.engine.complete_task(
        context.project_id, context.task_id, context.worker_id, context.claim_token, outputs,
        {"production_executor": "python_frame_render", "candidate_only": True, "render_receipt": result["receipt"]},
    )
    return {"operation": "python_frame_render", "completion": completion}


def execute_ffmpeg_assemble(context: ProductionTaskContext) -> dict[str, Any]:
    spec_name = str(context.config.get("render_spec_input", "")).strip()
    spec_artifact = context.inputs.get(spec_name)
    if not spec_artifact:
        raise ProductionContractError(f"render spec is not a declared task input: {spec_name}")
    spec = RenderSpec.from_dict(json.loads(Path(str(spec_artifact["path"])).read_text(encoding="utf-8")))
    clearance_input = str(context.config.get("rights_clearance_input", "")).strip()
    output_rights_status = (
        _validate_render_rights_clearance(context, spec, clearance_input)
        if clearance_input else "NOT_APPLICABLE"
    )
    result = FfmpegAssembler().render(
        spec, input_artifacts=context.inputs, output_dir=context.output_dir, expected_outputs=context.outputs,
    )
    outputs = {
        spec.video_output: _output_payload(
            Path(result["video_path"]), kind="video", media_type="video/mp4",
            rights_status=output_rights_status,
            metadata={"production_executor": "ffmpeg_assemble", "candidate_only": True, "render_receipt_ref": spec.receipt_output},
        ),
        spec.audio_output: _output_payload(
            Path(result["audio_path"]), kind="audio", media_type="audio/wav",
            rights_status=output_rights_status,
            metadata={"production_executor": "ffmpeg_assemble", "master_mix": True, "sample_rate": 48000, "bit_depth": 24},
        ),
        spec.receipt_output: _output_payload(
            Path(result["receipt_path"]), kind="evidence", media_type="application/json",
            metadata={"production_executor": "ffmpeg_assemble", "media_sha256": result["receipt"]["output"]["sha256"]},
        ),
    }
    completion = context.engine.complete_task(
        context.project_id, context.task_id, context.worker_id, context.claim_token, outputs,
        {"production_executor": "ffmpeg_assemble", "candidate_only": True, "render_receipt": result["receipt"]},
    )
    return {"operation": "ffmpeg_assemble", "completion": completion}


def execute_delivery_package(context: ProductionTaskContext) -> dict[str, Any]:
    package_map = context.config.get("package_map")
    if not isinstance(package_map, Mapping):
        raise ProductionContractError("package_map must be an object")
    expected_types = context.config.get("expected_types", {})
    if not isinstance(expected_types, Mapping):
        raise ProductionContractError("expected_types must be an object")
    required = context.config.get("required_artifacts", [])
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        raise ProductionContractError("required_artifacts must be an array of artifact names")
    missing = sorted(set(required) - set(context.inputs))
    if missing:
        raise ProductionContractError(f"delivery package is missing required input artifacts: {missing}")
    if not set(required).issubset(set(package_map)):
        raise ProductionContractError("package_map must include every required_artifact")
    package_output = str(context.config.get("package_output", "delivery-package"))
    manifest_output = str(context.config.get("manifest_output", "delivery-manifest"))
    if context.outputs != {package_output, manifest_output}:
        raise ProductionContractError("delivery task outputs must exactly match package_output and manifest_output")
    result = create_delivery_package(
        input_artifacts=context.inputs,
        package_map={str(k): str(v) for k, v in package_map.items()},
        package_path=context.output_dir / f"{package_output}.zip",
        manifest_path=context.output_dir / f"{manifest_output}.json",
        project_id=context.project_id,
        expected_types=expected_types,
    )
    outputs = {
        package_output: _output_payload(
            Path(result["package_path"]), kind="archive", media_type="application/zip",
            metadata={"production_executor": "delivery_package", "artifact_count": result["manifest"]["artifact_count"], "package_sha256": result["manifest"]["package_sha256"]},
        ),
        manifest_output: _output_payload(
            Path(result["manifest_path"]), kind="evidence", media_type="application/json",
            metadata={"production_executor": "delivery_package", "package_sha256": result["manifest"]["package_sha256"]},
        ),
    }
    completion = context.engine.complete_task(
        context.project_id, context.task_id, context.worker_id, context.claim_token, outputs,
        {"production_executor": "delivery_package", "package_manifest": result["manifest"]},
    )
    return {"operation": "delivery_package", "completion": completion}


def execute_ffprobe_media_qa(context: ProductionTaskContext) -> dict[str, Any]:
    return run_claimed_media_qa(
        context.engine, context.project_id, context.task_id, context.worker_id, context.claim_token,
    )
