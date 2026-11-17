from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from video_growth_agent.media_graph import (
    AssetRef,
    AssetVersion,
    ContextRecord,
    DecisionRecord,
    EvidenceRecord,
    MediaGraph,
)
from video_growth_agent.timeline import TimelineClip, TimelineSpec
from video_studio.adapters import (
    DomainAdapterError,
    assess_shot_continuity,
    editorial_plan_from_dict,
    outcome_metrics,
    route_shot,
    run_claimed_domain_adapter,
    timeline_spec_from_dict,
)
from video_studio.cli import build_parser
from video_studio.engine import StudioEngine


def _editorial_payload():
    return {
        "intent": {
            "episode_id": "E001",
            "series_id": "systems-explained",
            "audience_contract": "Explain one system without faking certainty.",
            "editorial_question": "Why does inference move toward the edge?",
            "primary_platform": "BILIBILI",
            "target_duration_seconds": 120,
            "evidence_refs": ["research://edge-inference"],
            "desired_outcomes": ["qualified_watch_time"],
            "success_metric_semantics": {"qualified_watch_time": "minutes from target viewers"},
        },
        "claims": [
            {"claim_id": "C1", "statement": "This is an analytical framing.", "claim_class": "ANALYSIS", "risk": "MEDIUM"},
        ],
        "beats": [
            {"beat_id": "B1", "episode_id": "E001", "narrative_job": "Open the mechanism", "audience_function": "Create curiosity", "target_duration_seconds": 20, "claim_ids": ["C1"]},
        ],
        "shots": [
            {"shot_id": "S1", "beat_id": "B1", "visual_job": "Show the inference path", "target_duration_seconds": 2, "truth_mode": "SYNTHETIC", "risk": "LOW", "source_claim_ids": ["C1"], "allowed_production_modes": ["PROGRAMMATIC_GRAPHICS"]},
        ],
        "plan_version": "v1",
    }


def _brief():
    return {
        "goal": "Create and independently validate one short visual candidate.",
        "audience": "Technology viewers.",
        "deliverables": ["candidate.mp4", "render-receipt.json"],
        "success_criteria": ["The exact candidate and receipt are registered with immutable lineage."],
    }


def test_editorial_plan_adapter_validates_claim_beat_shot_traceability():
    plan = editorial_plan_from_dict(_editorial_payload())
    assert plan.plan_ref == "editorial-plan://E001@v1"
    assert len(plan.claims) == len(plan.beats) == len(plan.shots) == 1
    broken = _editorial_payload()
    broken["shots"][0]["beat_id"] = "missing-beat"
    with pytest.raises(ValueError, match="missing beat"):
        editorial_plan_from_dict(broken)
    malformed = _editorial_payload()
    malformed["intent"]["evidence_refs"] = "research://not-an-array"
    with pytest.raises(DomainAdapterError, match="array of non-empty strings"):
        editorial_plan_from_dict(malformed)


def test_timeline_adapter_reconstructs_refs_and_requires_promoted_graph_assets():
    graph = MediaGraph()
    graph.add_context(ContextRecord("program", "PROGRAM"))
    graph.add_context(ContextRecord("episode", "EPISODE", "program"))
    ref = AssetRef("take-01", "v1")
    graph.add_asset(AssetVersion(ref, "episode", "VIDEO", "asset://take-01", "sha256:take"))
    graph.add_evidence(EvidenceRecord("ev-01", "ASSET_VERSION", ref.key(), "REVIEW", ("review://take-01",), "2026-11-16T00:00:00Z"))
    graph.add_decision(DecisionRecord("dec-01", "PROMOTION", "director", (ref.key(),), ("criteria://shot",), ("ev-01",), "PROMOTE", "2026-11-16T00:01:00Z"))
    graph.promote_asset(ref, decision_id="dec-01")
    payload = {
        "timeline_id": "master", "version_id": "v1", "context_id": "episode",
        "clips": [{
            "clip_id": "clip-01", "asset_ref": {"asset_id": "take-01", "version_id": "v1"},
            "track_id": "V1", "timeline_start_seconds": 0, "source_start_seconds": 0,
            "duration_seconds": 5,
        }],
    }
    timeline = timeline_spec_from_dict(payload)
    timeline.validate_against_graph(graph)
    assert timeline.duration_seconds == 5
    graph.asset_state_overrides[ref] = "CANDIDATE"
    with pytest.raises(ValueError, match="not promoted"):
        timeline.validate_against_graph(graph)


def test_shot_router_adapter_uses_operation_capability_quality_and_evidence_gates():
    decision = route_shot({
        "request": {
            "shot_id": "S1", "required_capabilities": ["i2v", "image_reference"],
            "duration_seconds": 4, "minimum_quality": 4.0, "lane": "production", "risk": "hero",
        },
        "engines": [
            {"engine_id": "cheap", "capabilities": ["i2v", "image_reference"], "measured_quality": 4.1,
             "available": True, "output_cost_usd_per_second": 0.05,
             "quality_evidence_refs": ["benchmark://cheap"], "pricing_evidence_refs": ["pricing://cheap"]},
            {"engine_id": "premium", "capabilities": ["i2v", "image_reference"], "measured_quality": 4.8,
             "available": True, "premium": True, "output_cost_usd_per_second": 0.50,
             "quality_evidence_refs": ["benchmark://premium"], "pricing_evidence_refs": ["pricing://premium"]},
        ],
    })
    assert decision["selected_engine_id"] == "premium"
    assert all(item["eligible"] for item in decision["assessments"])


def test_business_metrics_adapter_preserves_objective_vector_without_global_score():
    result = outcome_metrics({
        "episode_id": "E001",
        "platform_receipts": [{
            "platform": "BILIBILI", "variant_id": "master-v1",
            "raw_metrics": {"play": 1000, "follow_conversion": 0.03},
            "metric_semantics": {"play": "platform play count", "follow_conversion": "play-to-follow"},
            "evidence_refs": ["platform://receipt"], "observed_at": "2026-11-16T00:00:00Z",
        }],
        "production": {
            "published_minutes": 2, "cash_cost_usd": 10, "creator_minutes": 60,
            "generated_video_seconds": 20, "premium_video_seconds": 5,
            "generation_attempts": 4, "rejected_generation_attempts": 1,
            "accepted_generated_assets": 3, "reused_asset_uses": 2,
        },
        "commercial": {
            "revenue_usd": 100, "direct_cost_usd": 20, "rights_revenue_usd": 5,
            "repeat_buy_signal": "UNKNOWN", "evidence_refs": ["commercial://receipt"],
        },
    })
    assert result["derived_metrics"]["cost_per_published_minute"] == 5
    assert result["derived_metrics"]["commercial_gross_margin_usd"] == 85
    assert "score" not in result["objective_vector"]


def test_shot_route_adapter_uses_fresh_evidence_bound_model_registry(tmp_path):
    from datetime import datetime, timezone

    engine = StudioEngine(tmp_path)
    engine.create_project("routing", "Evidence-bound shot routing", _brief())
    observed_at = datetime.now(timezone.utc).isoformat()
    routing_request = {
        "request": {
            "shot_id": "S001", "lane": "PRODUCTION", "risk": "HERO",
            "duration_seconds": 5, "required_capabilities": ["I2V", "IMAGE_REFERENCES"],
            "minimum_quality": {"identity": 3.5, "motion": 3.0},
            "quality_priorities": ["identity", "motion"],
            "quality_rubric_id": "video-quality-v1", "calibration_scope": "episode-pilot-v1",
            "operation_mode": "I2V", "require_operation_profile": True,
            "required_resolution": "1080p", "reference_images": 1,
            "require_commercial_use": True, "require_provenance": True,
            "max_cost_usd": 5.0, "evidence_max_age_days": 30,
        },
        "engines": [{
            "engine_id": "provider-a", "observed_at": observed_at,
            "capabilities": ["I2V", "IMAGE_REFERENCES"], "quality_scores": {},
            "quality_observations": {
                "identity": {"value": 4.7, "rubric_id": "video-quality-v1", "calibration_scope": "episode-pilot-v1", "uncertainty": 0.1, "evidence_class": "OWNER_BENCHMARK", "evidence_refs": ["provider-capability-benchmark"]},
                "motion": {"value": 4.5, "rubric_id": "video-quality-v1", "calibration_scope": "episode-pilot-v1", "uncertainty": 0.1, "evidence_class": "OWNER_BENCHMARK", "evidence_refs": ["provider-capability-benchmark"]},
            },
            "available": True, "commercial_use_allowed": True, "provenance_supported": True,
            "max_duration_seconds": 10, "max_reference_images": 3,
            "resolutions": ["1080p"], "fixed_cost_usd": 0.1,
            "output_cost_usd_per_second": 0.2, "input_cost_usd_per_second": 0.0,
            "quality_evidence_refs": ["provider-capability-benchmark"],
            "pricing_evidence_refs": ["production-economics-baseline"],
            "terms_evidence_refs": ["provider-capability-benchmark"],
            "availability_evidence_refs": ["provider-capability-benchmark"],
            "operation_profiles": [{
                "profile_id": "i2v-1080p-5s", "mode": "I2V",
                "capabilities": ["I2V", "IMAGE_REFERENCES"],
                "allowed_durations_seconds": [5], "resolutions": ["1080p"],
                "max_reference_images": 3,
            }],
        }],
    }
    request_path = tmp_path / "routing-request.json"
    request_path.write_text(json.dumps(routing_request), encoding="utf-8")
    engine.import_asset(
        "routing", "routing-request", request_path, kind="document",
        media_type="application/json", rights_status="NOT_APPLICABLE",
    )
    engine.add_tasks("routing", [{
        "task_id": "route-shot", "title": "Route shot with current evidence-bound provider observations",
        "kind": "domain_adapter", "executor": "tool", "depends_on": [],
        "inputs": ["routing-request"], "outputs": ["shot-route-decision"],
        "requirements": {"domain_adapter": {
            "name": "shot_route", "routing_request_input": "routing-request",
            "output_name": "shot-route-decision",
        }},
        "acceptance": {"route": "The selected operation profile must meet the shot's current quality, terms, provenance and cost gates."},
    }])
    packet = engine.claim_next("routing", "router")
    result = run_claimed_domain_adapter(
        engine, "routing", "route-shot", "router", packet["claim"]["claim_token"],
    )
    output = result["completion"]["artifacts"]["shot-route-decision"]
    payload = json.loads(Path(output["path"]).read_text(encoding="utf-8"))
    assert payload["selected_engine_id"] == "provider-a"
    assert payload["assessments"][0]["operation_profile_id"] == "i2v-1080p-5s"
    assert payload["assessments"][0]["quality_lower_bounds"]["identity"] == 4.6
    assert engine.audit("routing")["pass"] is True


def test_cli_exposes_domain_adapter_execution_inside_standalone_runtime():
    args = build_parser().parse_args([
        "run-adapter", "demo", "render", "--worker", "renderer", "--token", "lease-token",
    ])
    assert args.command == "run-adapter"
    assert args.project_id == "demo"


def test_programmatic_graphic_adapter_executes_and_registers_candidate_with_lineage(tmp_path):
    font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe") or not font.is_file():
        pytest.skip("FFmpeg/ffprobe/DejaVuSans are required for local graphic rendering")

    engine = StudioEngine(tmp_path)
    engine.create_project("demo", "Adapter integration", _brief())

    plan_path = tmp_path / "editorial-plan.json"
    plan_path.write_text(json.dumps(_editorial_payload()), encoding="utf-8")
    shot_path = tmp_path / "shot-contract.json"
    shot_path.write_text(json.dumps({
        "shot_id": "S1", "sequence_id": "sequence-01", "narrative_job": "Show the inference path",
        "duration_seconds": 2, "truth_mode": "SYNTHETIC", "risk": "LOW",
        "allowed_modes": ["PROGRAMMATIC_GRAPHICS"], "required_capabilities": ["ffmpeg.drawtext"],
        "quality_targets": {"readability": 4}, "disclosure_required": True,
        "editorial_plan_ref": "editorial-plan://E001@v1", "beat_id": "B1", "source_claim_ids": ["C1"],
    }), encoding="utf-8")
    spec_path = tmp_path / "graphic-spec.json"
    spec_path.write_text(json.dumps({
        "spec_id": "spec-01", "kind": "TITLE_CARD", "title": "Inference moves closer",
        "subtitle": "A synthetic explanatory visual", "duration_seconds": 2,
        "width": 640, "height": 640, "fps": 24,
    }), encoding="utf-8")
    rights_path = tmp_path / "rights-clearance.txt"
    rights_path.write_text("The local font is licensed for this use.", encoding="utf-8")

    engine.import_asset("demo", "editorial-plan", plan_path, kind="document", media_type="application/json", rights_status="NOT_APPLICABLE")
    engine.import_asset("demo", "shot-contract", shot_path, kind="document", media_type="application/json", rights_status="NOT_APPLICABLE")
    engine.import_asset("demo", "graphic-spec", spec_path, kind="document", media_type="application/json", rights_status="NOT_APPLICABLE")
    engine.import_asset("demo", "font-asset", font, kind="font", media_type="font/ttf", rights_status="LICENSED", metadata={"rights_evidence_refs": ["rights-clearance"]})
    engine.import_asset("demo", "rights-clearance", rights_path, kind="document", media_type="text/plain", rights_status="OWNED")

    engine.add_tasks("demo", [{
        "task_id": "render", "title": "Render one programmatic graphic candidate",
        "kind": "domain_adapter", "executor": "tool", "depends_on": [],
        "inputs": ["editorial-plan", "shot-contract", "graphic-spec", "font-asset", "rights-clearance"],
        "outputs": ["graphic-candidate", "graphic-render-receipt"],
        "requirements": {"domain_adapter": {
            "name": "programmatic_graphic_render",
            "editorial_plan_input": "editorial-plan",
            "shot_contract_input": "shot-contract",
            "graphic_spec_input": "graphic-spec",
            "font_input": "font-asset",
            "rights_evidence_input": "rights-clearance",
            "video_output": "graphic-candidate",
            "receipt_output": "graphic-render-receipt",
        }},
        "acceptance": {"candidate": "The rendered output is a candidate only; it is not promoted or released."},
        "priority": 100,
    }])
    packet = engine.claim_next("demo", "renderer")
    assert packet["task"]["task_id"] == "render"
    result = run_claimed_domain_adapter(
        engine, "demo", "render", "renderer", packet["claim"]["claim_token"],
    )
    assert result["status"] == "COMPLETED"
    artifacts = result["completion"]["artifacts"]
    video = artifacts["graphic-candidate"]
    receipt = artifacts["graphic-render-receipt"]
    assert Path(video["path"]).is_file()
    assert video["metadata"]["candidate_only"] is True
    assert video["metadata"]["promotion_authorized"] is False
    assert video["metadata"]["rights_evidence_refs"] == ["rights-clearance"]
    receipt_payload = json.loads(Path(receipt["path"]).read_text(encoding="utf-8"))
    assert receipt_payload["candidate_only"] is True
    assert receipt_payload["release_authorized"] is False
    with engine._connect("demo") as connection:
        lineage = connection.execute(
            "SELECT COUNT(*) FROM artifact_inputs WHERE project_id='demo' AND output_artifact_id=?",
            (video["artifact_id"],),
        ).fetchone()[0]
    assert lineage == 5
    assert engine.audit("demo")["pass"] is True


def test_continuity_adapter_distinguishes_hard_identity_from_allowed_location_change():
    report = assess_shot_continuity({
        "before": {"shot_id": "S1", "dimensions": {"face": "approved-face", "wardrobe": "blue", "location": "office"}},
        "after": {"shot_id": "S2", "dimensions": {"face": "generic-face", "wardrobe": "blue", "location": "street"}},
        "link": {
            "from_shot_id": "S1", "to_shot_id": "S2",
            "rules": [
                {"dimension": "face", "severity": "HARD", "mode": "PRESERVE", "reason": "Identity must remain stable."},
                {"dimension": "wardrobe", "severity": "HARD", "mode": "PRESERVE"},
                {"dimension": "location", "severity": "SOFT", "mode": "ALLOW_CHANGE"},
            ],
        },
        "evidence_refs": ["frame://S1", "frame://S2"],
    })
    assert report["hard_pass"] is False
    violations = report["assessment"]["violations"]
    assert len(violations) == 1
    assert violations[0]["dimension"] == "face"
    assert violations[0]["severity"] == "HARD"


def test_extended_media_qa_adapter_records_loudness_and_silence_analysis(tmp_path):
    import subprocess

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg/ffprobe are required for extended media QA")
    engine = StudioEngine(tmp_path)
    engine.create_project("audio", "Extended QA", _brief())
    media = tmp_path / "audio-video.mp4"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-v", "error",
        "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=1:r=25",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=1",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "-y", str(media),
    ], check=True, capture_output=True)
    engine.import_asset("audio", "final-candidate", media, kind="video", media_type="video/mp4", rights_status="OWNED")
    engine.add_tasks("audio", [{
        "task_id": "extended-qa", "title": "Run supplementary loudness and silence QA",
        "kind": "domain_adapter", "executor": "tool", "depends_on": [],
        "inputs": ["final-candidate"], "outputs": ["extended-audio-qa"],
        "requirements": {"domain_adapter": {
            "name": "extended_media_qa", "media_input": "final-candidate", "output_name": "extended-audio-qa",
        }},
        "acceptance": {"qa": "Record integrated loudness, true peak, long silence and black-frame diagnostics."},
    }])
    packet = engine.claim_next("audio", "audio-qa")
    result = run_claimed_domain_adapter(engine, "audio", "extended-qa", "audio-qa", packet["claim"]["claim_token"])
    report = json.loads(Path(result["completion"]["artifacts"]["extended-audio-qa"]["path"]).read_text(encoding="utf-8"))
    check_ids = {item["check_id"] for item in report["checks"]}
    assert {"integrated_loudness", "true_peak", "long_silence", "black_frames"}.issubset(check_ids)
    assert report["metadata"]["checker"] == "ffmpeg-ffprobe-v0.2"


def test_business_object_validate_adapter_emits_typed_commercial_fit_artifact(tmp_path):
    engine = StudioEngine(tmp_path)
    engine.create_project("commercial", "Commercial adapter", _brief())
    fit_path = tmp_path / "commercial-fit.json"
    fit_path.write_text(json.dumps({
        "fit_id": "fit-001", "context_id": "series-001",
        "advertiser_categories": ["cloud"],
        "integration_surfaces": ["verified product workflow"],
        "product_truth_requirements": ["claims require primary evidence"],
        "prohibited_integration_forms": ["guaranteed outcome"],
        "measurement_plan_refs": ["measurement://fit-001"],
        "evidence_refs": ["research://advertiser-map"],
        "editorial_independence_required": True,
    }), encoding="utf-8")
    engine.import_asset("commercial", "commercial-fit-draft", fit_path, kind="document", media_type="application/json", rights_status="NOT_APPLICABLE")
    engine.add_tasks("commercial", [{
        "task_id": "validate-fit", "title": "Validate typed CommercialFit",
        "kind": "domain_adapter", "executor": "tool", "depends_on": [],
        "inputs": ["commercial-fit-draft"], "outputs": ["topic-commercial-fit"],
        "requirements": {"domain_adapter": {
            "name": "business_object_validate", "object_type": "CommercialFit",
            "input_name": "commercial-fit-draft", "output_name": "topic-commercial-fit",
        }},
        "acceptance": {"contract": "The typed commercial fit must pass domain validation."},
    }])
    packet = engine.claim_next("commercial", "commercial-validator")
    result = run_claimed_domain_adapter(engine, "commercial", "validate-fit", "commercial-validator", packet["claim"]["claim_token"])
    output = result["completion"]["artifacts"]["topic-commercial-fit"]
    payload = json.loads(Path(output["path"]).read_text(encoding="utf-8"))
    assert payload["object_type"] == "CommercialFit"
    assert payload["object"]["fit_id"] == "fit-001"
    assert payload["object"]["editorial_independence_required"] is True
    assert engine.audit("commercial")["pass"] is True


def test_episode_intent_validate_adapter_checks_real_source_bindings_and_cross_project_transfer(tmp_path):
    engine = StudioEngine(tmp_path)
    engine.create_project("program", "Program handoff adapter", _brief())
    source_names = [
        "portfolio-allocation-decision", "pilot-topic-slate-decision",
        "production-strategy", "commercial-production-constraints", "growth-baseline",
    ]
    source_artifacts = {}
    for name in source_names:
        source_path = tmp_path / f"{name}.json"
        source_path.write_text(json.dumps({"source": name}), encoding="utf-8")
        source_artifacts[name] = engine.import_asset(
            "program", name, source_path, kind="evidence",
            media_type="application/json", rights_status="NOT_APPLICABLE",
        )
    bindings = [
        {"name": name, "artifact_id": source_artifacts[name]["artifact_id"],
         "version": source_artifacts[name]["version"], "sha256": source_artifacts[name]["sha256"]}
        for name in source_names
    ]
    handoff = {
        "schema_version": "1.0", "handoff_type": "VIDEO_PROGRAM_TO_EPISODE",
        "program_id": "program", "source_project_id": "program",
        "episode_id": "E001", "series_id": "S001",
        "source_artifact_bindings": bindings,
        "episode_intent": {
            "episode_id": "E001", "series_id": "S001",
            "audience_contract": "Explain one system to technology-curious viewers.",
            "editorial_question": "What is the central mechanism?",
            "primary_platform": "BILIBILI", "target_duration_seconds": 180,
            "evidence_refs": ["artifact://growth-baseline"],
            "desired_outcomes": ["qualified_watch_time"],
            "success_metric_semantics": {"qualified_watch_time": "minutes from target viewers"},
            "commercial_context_refs": [], "constraints": ["Do not invent IPOS identity canon."],
        },
        "identity_usage": {"mode": "NON_CHARACTER", "reason": "No approved IPOS identity bundle is available."},
    }
    handoff_path = tmp_path / "episode-handoff.json"
    handoff_path.write_text(json.dumps(handoff), encoding="utf-8")
    engine.import_asset(
        "program", "episode-production-handoff", handoff_path,
        kind="document", media_type="application/json", rights_status="NOT_APPLICABLE",
    )
    engine.add_tasks("program", [{
        "task_id": "validate-handoff", "title": "Validate Program-to-Episode handoff",
        "kind": "domain_adapter", "executor": "tool", "depends_on": [],
        "inputs": ["episode-production-handoff", *source_names], "outputs": ["validated-episode-intent"],
        "requirements": {"domain_adapter": {
            "name": "episode_intent_validate", "handoff_input": "episode-production-handoff",
            "source_artifact_inputs": source_names,
            "program_id": "program", "output_name": "validated-episode-intent",
        }},
        "acceptance": {"contract": "Every handoff source binding must match the exact current Program artifact ID, version and digest."},
    }])
    packet = engine.claim_next("program", "handoff-validator")
    result = run_claimed_domain_adapter(
        engine, "program", "validate-handoff", "handoff-validator", packet["claim"]["claim_token"],
    )
    output = result["completion"]["artifacts"]["validated-episode-intent"]
    validated = json.loads(Path(output["path"]).read_text(encoding="utf-8"))
    assert validated["episode_id"] == "E001"
    assert validated["identity_usage"]["mode"] == "NON_CHARACTER"
    assert validated["source_validation"]["status"] == "PASS"
    assert validated["source_validation"]["source_artifact_bindings"] == sorted(bindings, key=lambda item: item["name"])
    assert validated["handoff_type"] == "VIDEO_PROGRAM_TO_EPISODE"
    assert engine.audit("program")["pass"] is True

    engine.create_project("episode", "Receiving Episode", _brief())
    engine.add_tasks("episode", [{
        "task_id": "validate-program-handoff", "title": "Validate transferred Program handoff",
        "kind": "domain_adapter", "executor": "tool", "depends_on": [],
        "inputs": ["validated-episode-intent"], "outputs": ["episode-intent"],
        "requirements": {"domain_adapter": {
            "name": "episode_intent_validate", "handoff_input": "validated-episode-intent",
            "program_id": "program", "require_validated_transfer": True,
            "source_artifact_name": "validated-episode-intent", "output_name": "episode-intent",
        }},
        "acceptance": {"contract": "Only the exact validated Program artifact may start Episode work."},
    }])
    assert engine.list_tasks("episode")[0]["status"] == "WAITING_INPUT"
    transferred = engine.transfer_artifact(
        "program", "validated-episode-intent", "episode", "validated-episode-intent",
        expected_artifact_id=output["artifact_id"], expected_version=output["version"],
        expected_sha256=output["sha256"],
    )
    assert transferred["target"]["metadata"]["cross_project_transfer"] == transferred["transfer"]
    assert engine.list_tasks("episode")[0]["status"] == "READY"
    episode_packet = engine.claim_next("episode", "episode-validator")
    episode_result = run_claimed_domain_adapter(
        engine, "episode", "validate-program-handoff", "episode-validator",
        episode_packet["claim"]["claim_token"],
    )
    episode_output = episode_result["completion"]["artifacts"]["episode-intent"]
    episode_payload = json.loads(Path(episode_output["path"]).read_text(encoding="utf-8"))
    assert episode_payload["source_validation"]["status"] == "PASS"
    assert episode_payload["cross_project_transfer"]["source_artifact_id"] == output["artifact_id"]
    assert episode_payload["identity_usage"]["mode"] == "NON_CHARACTER"
    assert engine.audit("episode")["pass"] is True


def _ipos_bundle():
    return {
        "schema_version": "1.0", "issuer": "IP_STUDIO_OS",
        "bundle_id": "creator-character-v1", "project_id": "ipos-project",
        "issued_at": "2026-11-13T12:00:00+08:00",
        "canon": {
            "canon_id": "creator-character", "version": "v1", "carrier": "ORIGINAL_CHARACTER",
            "identity_thesis": "An owner-approved recurring character.",
            "identity_invariants": ["preserve silhouette", "preserve face geometry"],
            "allowed_variations": ["expression may change"], "forbidden_drift": ["do not replace the identity"],
        },
        "approval": {"status": "OWNER_APPROVED", "approval_ref": "owner-approval://canon-v1", "approved_at": "2026-11-13T11:55:00+08:00"},
        "readiness": {"status": "READY_FOR_VIDEO", "gates": {"G2": "PASS", "G7": "PASS", "G8": "PASS"}},
        "usage": {"video_allowed": True, "usage_constraints": ["organic creator video"]},
        "assets": [{
            "asset_id": "hero-reference", "version_id": "v1", "kind": "IMAGE",
            "role": "PRIMARY_VISUAL_REFERENCE", "uri": "asset://ipos/hero-reference/v1.png",
            "digest": "sha256:" + "a" * 64, "state": "PROMOTED", "approved_for_video": True,
            "rights_ref": "rights://owner/character", "consent_ref": None, "requires_consent": False,
            "provenance_refs": ["ipos-source://design-ledger/R39"],
        }],
        "continuity": {
            "dimensions": {"silhouette": "approved silhouette v1"},
            "rules": [{"dimension": "silhouette", "severity": "HARD", "mode": "PRESERVE", "reason": "Identity anchor."}],
        },
        "source_provenance_refs": ["ipos-source://owner-brief/R39"],
        "bundle_uri": "ipos://exports/creator-character/v1.json",
    }


def test_ipos_bundle_import_adapter_preserves_external_canon_and_graph_lineage(tmp_path):
    engine = StudioEngine(tmp_path)
    engine.create_project("ipos", "IPOS adapter", _brief())
    bundle_path = tmp_path / "ipos-bundle.json"
    bundle_path.write_text(json.dumps(_ipos_bundle()), encoding="utf-8")
    shot_path = tmp_path / "shot-contract.json"
    shot_path.write_text(json.dumps({
        "shot_id": "SHOT-001", "sequence_id": "SEQ-001",
        "narrative_job": "Introduce the approved recurring character.",
        "duration_seconds": 4, "truth_mode": "SYNTHETIC", "risk": "HERO",
        "allowed_modes": ["I2V", "T2V"], "required_capabilities": ["I2V"],
        "quality_targets": {"identity": 4.0, "motion": 3.5}, "budget_usd": 5.0,
    }), encoding="utf-8")
    engine.import_asset("ipos", "ipos-bundle", bundle_path, kind="document", media_type="application/json", rights_status="NOT_APPLICABLE")
    engine.import_asset("ipos", "shot-contract", shot_path, kind="document", media_type="application/json", rights_status="NOT_APPLICABLE")
    engine.add_tasks("ipos", [
        {
            "task_id": "bootstrap-graph", "title": "Initialize the Video-owned MediaGraph root",
            "kind": "domain_adapter", "executor": "tool", "depends_on": [],
            "inputs": [], "outputs": ["media-graph"],
            "requirements": {"domain_adapter": {
                "name": "media_graph_initialize", "output_name": "media-graph",
                "contexts": [{"context_id": "program", "kind": "PROGRAM"}],
            }},
            "acceptance": {"graph": "Create the Video-owned Program context without importing or mutating IPOS canon."},
        },
        {
            "task_id": "import-ipos", "title": "Import the owner-approved IPOS bundle",
            "kind": "domain_adapter", "executor": "tool", "depends_on": ["bootstrap-graph"],
            "inputs": ["ipos-bundle", "media-graph"],
            "outputs": ["media-graph-imported", "ipos-import-receipt"],
            "requirements": {"domain_adapter": {
                "name": "ipos_bundle_import", "bundle_input": "ipos-bundle",
                "media_graph_input": "media-graph", "program_context_id": "program",
                "media_graph_output": "media-graph-imported", "receipt_output": "ipos-import-receipt",
            }},
            "acceptance": {"import": "Only owner-approved READY_FOR_VIDEO bundles are imported with exact asset digests."},
        },
    ])
    bootstrap = engine.claim_next("ipos", "ipos-adapter")
    assert bootstrap["task"]["task_id"] == "bootstrap-graph"
    run_claimed_domain_adapter(engine, "ipos", "bootstrap-graph", "ipos-adapter", bootstrap["claim"]["claim_token"])
    packet = engine.claim_next("ipos", "ipos-adapter")
    assert packet["task"]["task_id"] == "import-ipos"
    result = run_claimed_domain_adapter(engine, "ipos", "import-ipos", "ipos-adapter", packet["claim"]["claim_token"])
    graph_artifact = result["completion"]["artifacts"]["media-graph-imported"]
    receipt_artifact = result["completion"]["artifacts"]["ipos-import-receipt"]
    graph_result = json.loads(Path(graph_artifact["path"]).read_text(encoding="utf-8"))
    receipt = json.loads(Path(receipt_artifact["path"]).read_text(encoding="utf-8"))
    assert receipt["canon_ref"].endswith("@v1")
    assert len(receipt["imported_asset_refs"]) == 2
    assert any(item["kind"] == "IPOS_IDENTITY_BUNDLE" for item in graph_result["assets"])

    engine.add_tasks("ipos", [{
        "task_id": "inspect-ipos-import", "title": "Verify exact imported IPOS bundle provenance",
        "kind": "domain_adapter", "executor": "tool", "depends_on": ["import-ipos"],
        "inputs": ["ipos-bundle", "ipos-import-receipt", "media-graph-imported"],
        "outputs": ["ipos-bundle-readiness"],
        "requirements": {"domain_adapter": {
            "name": "ipos_bundle_inspect", "bundle_input": "ipos-bundle",
            "import_receipt_input": "ipos-import-receipt", "media_graph_input": "media-graph-imported",
            "output_name": "ipos-bundle-readiness",
        }},
        "acceptance": {"provenance": "The inspected bundle, receipt and promoted MediaGraph digests must match exactly."},
    }])
    inspect_packet = engine.claim_next("ipos", "ipos-inspector")
    assert inspect_packet["task"]["task_id"] == "inspect-ipos-import"
    inspect_result = run_claimed_domain_adapter(
        engine, "ipos", "inspect-ipos-import", "ipos-inspector", inspect_packet["claim"]["claim_token"],
    )
    readiness_path = inspect_result["completion"]["artifacts"]["ipos-bundle-readiness"]["path"]
    readiness_payload = json.loads(Path(readiness_path).read_text(encoding="utf-8"))
    assert readiness_payload["readiness"]["ready"] is True
    assert readiness_payload["import_validation"]["imported_asset_count"] == 2
    assert readiness_payload["import_validation"]["reference_binding_count"] >= 1

    engine.add_tasks("ipos", [{
        "task_id": "bind-ipos-shot", "title": "Bind the exact imported IPOS canon to a shot contract",
        "kind": "domain_adapter", "executor": "tool", "depends_on": ["import-ipos"],
        "inputs": ["ipos-bundle", "ipos-import-receipt", "media-graph-imported", "shot-contract"],
        "outputs": ["shot-contract-ipos-bound", "ipos-continuity-rules"],
        "requirements": {"domain_adapter": {
            "name": "ipos_shot_bind", "bundle_input": "ipos-bundle",
            "import_receipt_input": "ipos-import-receipt", "media_graph_input": "media-graph-imported",
            "shot_contract_input": "shot-contract", "shot_contract_output": "shot-contract-ipos-bound",
            "continuity_rules_output": "ipos-continuity-rules",
        }},
        "acceptance": {"binding": "Bind exact imported asset versions and external identity invariants without mutating IPOS canon."},
    }])
    bind_packet = engine.claim_next("ipos", "ipos-shot-binder")
    assert bind_packet["task"]["task_id"] == "bind-ipos-shot"
    bound_result = run_claimed_domain_adapter(
        engine, "ipos", "bind-ipos-shot", "ipos-shot-binder", bind_packet["claim"]["claim_token"],
    )
    bound_path = bound_result["completion"]["artifacts"]["shot-contract-ipos-bound"]["path"]
    bound = json.loads(Path(bound_path).read_text(encoding="utf-8"))["shot_contract"]
    assert bound["ip_identity_required"] is True
    assert bound["ip_identity_bundle_ref"].endswith("@v1")
    assert any(item["role"].startswith("IPOS_") for item in bound["references"])
    rules_path = bound_result["completion"]["artifacts"]["ipos-continuity-rules"]["path"]
    rules = json.loads(Path(rules_path).read_text(encoding="utf-8"))["continuity_rules"]
    assert any(item["severity"] == "HARD" for item in rules)
    assert engine.audit("ipos")["pass"] is True
