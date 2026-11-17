from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Mapping

from video_growth_agent.continuity import (
    ContinuityLink,
    ContinuityRule,
    ContinuitySnapshot,
    assess_continuity,
)
from video_growth_agent.business_metrics import (
    CommercialOutcome,
    EpisodeOutcomeReceipt,
    PlatformPerformanceReceipt,
    ProductionEconomics,
)
from video_growth_agent.business_objects import BusinessHypothesisDecision, CommercialFit, CommercialOfferCandidate, ContentPortfolioItem, DistinctiveAssetObservation, RightsPackage
from video_growth_agent.editorial_planning import (
    BeatSpec,
    ClaimSpec,
    EditorialPlan,
    EpisodeIntent,
    ShotIntent,
    materialize_shot_contract,
)
from video_growth_agent.model_registry import (
    EvidenceBoundModelRouter,
    ModelObservation,
    OperationProfile,
    QualityObservation,
    ShotRoutingRequest,
)
from video_growth_agent.ip_identity import (
    IPIdentityImportReceipt,
    bind_ipos_identity_to_shot,
    build_ipos_continuity_link,
    build_ipos_continuity_rules,
    build_ipos_continuity_snapshot,
    import_ipos_bundle,
    inspect_ipos_bundle,
)
from video_growth_agent.production_os import ReferenceBinding
from video_growth_agent.media_graph import ContextRecord, MediaGraph
from video_growth_agent.media_qa import MediaQAChecker
from video_growth_agent.programmatic_graphics import (
    graphic_spec_from_dict,
    register_graph_candidate,
    render_programmatic_graphic,
    shot_contract_from_dict,
)
from video_growth_agent.timeline import (
    TimelineClip,
    TimelineMarker,
    TimelineSpec,
    assert_platform_variant_lineage,
)
from video_growth_agent.media_graph import AssetRef

from .engine import ContractError, StudioEngine, StudioError


class DomainAdapterError(StudioError):
    """A deterministic Video-domain capability adapter rejected its input."""


SUPPORTED_DOMAIN_ADAPTERS = frozenset({"editorial_plan_validate","shot_contract_materialize","shot_contract_validate","ipos_bundle_inspect","ipos_bundle_import","ipos_shot_bind","ipos_continuity_snapshot","ipos_continuity_link","timeline_validate","shot_route","extended_media_qa","continuity_assess","business_outcome_metrics","programmatic_graphic_render","media_graph_initialize","business_object_validate","episode_intent_validate"})


def supports_domain_adapter(name: str) -> bool:
    return name in SUPPORTED_DOMAIN_ADAPTERS


def business_object_from_dict(object_type: str, payload: Mapping[str, Any]) -> Any:
    classes = {
        "ContentPortfolioItem": (ContentPortfolioItem, ("topic_evidence_refs","commercial_adjacency_categories","distinctive_asset_opportunities")),
        "DistinctiveAssetObservation": (DistinctiveAssetObservation, ("evidence_refs","qualitative_refs")),
        "CommercialFit": (CommercialFit, ("advertiser_categories","integration_surfaces","product_truth_requirements","prohibited_integration_forms","measurement_plan_refs","evidence_refs")),
        "RightsPackage": (RightsPackage, ("territories","exclusivity_categories","usage_constraints","evidence_refs")),
        "CommercialOfferCandidate": (CommercialOfferCandidate, ("deliverables","pricing_evidence_refs")),
        "BusinessHypothesisDecision": (BusinessHypothesisDecision, ("subject_ids","evidence_refs","counterexample_refs","followup_measurement_refs")),
    }
    selected=classes.get(object_type)
    if selected is None: raise DomainAdapterError(f"unsupported shared business object type: {object_type}")
    cls, tuple_fields=selected; data=dict(_mapping(payload,object_type))
    for field_name in tuple_fields:
        raw=data.get(field_name,())
        if not isinstance(raw,(list,tuple)): raise DomainAdapterError(f"{object_type}.{field_name} must be an array")
        data[field_name]=tuple(raw)
    try: return cls(**data)
    except (TypeError,ValueError) as exc: raise DomainAdapterError(f"invalid {object_type}: {exc}") from exc


def program_episode_handoff_to_intent(payload: Mapping[str, Any], *, expected_program_id: str | None = None) -> dict[str, Any]:
    data=_mapping(payload,"Program -> Episode handoff")
    if data.get("schema_version")!="1.0" or data.get("handoff_type")!="VIDEO_PROGRAM_TO_EPISODE": raise DomainAdapterError("Program -> Episode handoff must use schema_version 1.0 and VIDEO_PROGRAM_TO_EPISODE")
    program_id=str(data.get("program_id") or "").strip()
    if not program_id or (expected_program_id and program_id!=expected_program_id): raise DomainAdapterError("Program -> Episode handoff has the wrong or missing program_id")
    if str(data.get("source_project_id") or "").strip()!=program_id: raise DomainAdapterError("handoff source_project_id must match program_id")
    bindings=data.get("source_artifact_bindings")
    if not isinstance(bindings,list) or not bindings: raise DomainAdapterError("handoff requires source_artifact_bindings")
    by_name={}
    for raw in bindings:
        item=_mapping(raw,"source_artifact_binding"); name=str(item.get("name") or "").strip(); aid=str(item.get("artifact_id") or "").strip(); digest=str(item.get("sha256") or "").strip().lower(); version=item.get("version")
        if not name or not aid or not isinstance(version,int) or version<1: raise DomainAdapterError("each source artifact binding requires name, artifact_id and positive version")
        if not re.fullmatch(r"[0-9a-f]{64}",digest): raise DomainAdapterError(f"source artifact binding has an invalid SHA-256 digest: {name}")
        if name in by_name: raise DomainAdapterError(f"duplicate source artifact binding: {name}")
        by_name[name]=item
    required={"portfolio-allocation-decision","pilot-topic-slate-decision","production-strategy","commercial-production-constraints","growth-baseline"}
    missing=sorted(required-set(by_name))
    if missing: raise DomainAdapterError(f"handoff is missing required source artifact bindings: {missing}")
    raw_intent=dict(_mapping(data.get("episode_intent"),"episode_intent"))
    for field_name in ("evidence_refs","desired_outcomes","commercial_context_refs","constraints"):
        value=raw_intent.get(field_name,())
        if not isinstance(value,(list,tuple)): raise DomainAdapterError(f"episode_intent.{field_name} must be an array")
        raw_intent[field_name]=tuple(value)
    try: intent=EpisodeIntent(**raw_intent)
    except (TypeError,ValueError) as exc: raise DomainAdapterError(f"invalid EpisodeIntent in Program handoff: {exc}") from exc
    if str(data.get("episode_id") or "").strip()!=intent.episode_id or str(data.get("series_id") or "").strip()!=intent.series_id: raise DomainAdapterError("handoff episode_id/series_id must match EpisodeIntent")
    identity=_mapping(data.get("identity_usage",{}),"identity_usage"); mode=identity.get("mode")
    if mode=="NON_CHARACTER":
        if not str(identity.get("reason") or "").strip(): raise DomainAdapterError("NON_CHARACTER handoff must explain why identity usage is excluded")
        if any(identity.get(k) for k in ("bundle_ref","canon_ref","approval_ref")): raise DomainAdapterError("NON_CHARACTER handoff cannot claim IPOS identity approvals")
    elif mode=="IPOS_APPROVED":
        missing_identity=[k for k in ("bundle_ref","canon_ref","approval_ref","rights_evidence_refs") if not identity.get(k)]
        if missing_identity: raise DomainAdapterError(f"IPOS_APPROVED handoff is missing identity evidence: {missing_identity}")
    else: raise DomainAdapterError("identity_usage.mode must be NON_CHARACTER or IPOS_APPROVED")
    return {"schema_version":"1.0","handoff_type":"VIDEO_PROGRAM_TO_EPISODE","program_id":program_id,"source_project_id":program_id,"episode_id":intent.episode_id,"series_id":intent.series_id,"episode_intent":_jsonable(intent),"identity_usage":dict(identity),"source_artifact_bindings":[dict(by_name[n]) for n in sorted(by_name)],"portfolio_decision_ref":dict(by_name["portfolio-allocation-decision"]),"topic_decision_ref":dict(by_name["pilot-topic-slate-decision"]),"production_strategy_ref":dict(by_name["production-strategy"]),"commercial_constraints_ref":dict(by_name["commercial-production-constraints"])}


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(_jsonable(item) for item in value)
    if isinstance(value, Path):
        return str(value)
    return value


def _mapping(payload: Any, label: str) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise DomainAdapterError(f"{label} must be a JSON object")
    return dict(payload)


def _string_tuple(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or not all(isinstance(item, str) and item.strip() for item in value):
        raise DomainAdapterError(f"{label} must be an array of non-empty strings")
    return tuple(value)


def editorial_plan_from_dict(payload: Mapping[str, Any]) -> EditorialPlan:
    data = _mapping(payload, "EditorialPlan")
    intent_data = _mapping(data.get("intent"), "EditorialPlan.intent")
    for field in ("evidence_refs", "desired_outcomes", "constraints", "commercial_context_refs"):
        if field in intent_data:
            intent_data[field] = _string_tuple(intent_data[field], f"EditorialPlan.intent.{field}")
    intent = EpisodeIntent(**intent_data)

    claims = []
    for raw in data.get("claims", []):
        item = _mapping(raw, "EditorialPlan.claim")
        item["evidence_refs"] = _string_tuple(item.get("evidence_refs", []), "EditorialPlan.claim.evidence_refs") if item.get("evidence_refs", []) else ()
        claims.append(ClaimSpec(**item))

    beats = []
    for raw in data.get("beats", []):
        item = _mapping(raw, "EditorialPlan.beat")
        for field in ("claim_ids", "depends_on"):
            item[field] = _string_tuple(item.get(field, []), f"EditorialPlan.beat.{field}") if item.get(field, []) else ()
        beats.append(BeatSpec(**item))

    shots = []
    for raw in data.get("shots", []):
        item = _mapping(raw, "EditorialPlan.shot")
        for field in ("source_claim_ids", "continuity_dimensions", "reference_intents", "must_show", "must_avoid"):
            item[field] = _string_tuple(item.get(field, []), f"EditorialPlan.shot.{field}") if item.get(field, []) else ()
        item["allowed_production_modes"] = frozenset(_string_tuple(item.get("allowed_production_modes", []), "EditorialPlan.shot.allowed_production_modes"))
        item["value_vector"] = dict(item.get("value_vector", {}))
        shots.append(ShotIntent(**item))

    return EditorialPlan(
        intent=intent,
        claims=tuple(claims),
        beats=tuple(beats),
        shots=tuple(shots),
        plan_version=str(data["plan_version"]),
        derived_from_version=data.get("derived_from_version"),
        revision_reason=str(data.get("revision_reason", "")),
    )


def validate_shot_against_editorial_plan(plan: EditorialPlan, shot: Any) -> None:
    planned = plan.shot(shot.shot_id)
    if shot.editorial_plan_ref != plan.plan_ref:
        raise DomainAdapterError("ShotContract editorial_plan_ref does not match the exact supplied EditorialPlan")
    if shot.beat_id != planned.beat_id:
        raise DomainAdapterError("ShotContract beat_id does not match the supplied EditorialPlan")
    if tuple(shot.source_claim_ids) != tuple(planned.source_claim_ids):
        raise DomainAdapterError("ShotContract source_claim_ids do not match the supplied EditorialPlan")
    if abs(float(shot.duration_seconds) - float(planned.target_duration_seconds)) > 0.01:
        raise DomainAdapterError("ShotContract duration does not match the supplied EditorialPlan")
    if shot.truth_mode != planned.truth_mode or shot.risk != planned.risk:
        raise DomainAdapterError("ShotContract truth_mode/risk do not match the supplied EditorialPlan")
    permitted_modes = set(planned.allowed_production_modes)
    contract_modes = set(shot.allowed_modes)
    if not contract_modes or not contract_modes.issubset(permitted_modes):
        raise DomainAdapterError(
            "ShotContract allowed_modes exceed the exact EditorialPlan permissions: "
            f"contract={sorted(contract_modes)}, plan={sorted(permitted_modes)}"
        )


def timeline_spec_from_dict(payload: Mapping[str, Any]) -> TimelineSpec:
    data = _mapping(payload, "TimelineSpec")
    clips = []
    for raw in data.get("clips", []):
        item = _mapping(raw, "TimelineClip")
        ref = item.get("asset_ref")
        if isinstance(ref, str):
            item["asset_ref"] = AssetRef.from_key(ref)
        else:
            item["asset_ref"] = AssetRef(**_mapping(ref, "TimelineClip.asset_ref"))
        item["transform"] = dict(item.get("transform", {}))
        clips.append(TimelineClip(**item))
    markers = tuple(TimelineMarker(**_mapping(raw, "TimelineMarker")) for raw in data.get("markers", []))
    return TimelineSpec(
        timeline_id=str(data["timeline_id"]),
        version_id=str(data["version_id"]),
        context_id=str(data["context_id"]),
        clips=tuple(clips),
        markers=markers,
        derived_from_version=data.get("derived_from_version"),
        edit_reason=str(data.get("edit_reason", "")),
        metadata=dict(data.get("metadata", {})),
    )


def route_shot(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _mapping(payload, "shot routing request")
    request_data = _mapping(data.get("request"), "request")
    request_data["required_capabilities"] = frozenset(request_data.get("required_capabilities", ()))
    request = ShotRequest(**request_data)
    engines = []
    for raw in data.get("engines", []):
        item = _mapping(raw, "engine profile")
        item["capabilities"] = frozenset(item.get("capabilities", ()))
        item["quality_evidence_refs"] = tuple(item.get("quality_evidence_refs", ()))
        item["pricing_evidence_refs"] = tuple(item.get("pricing_evidence_refs", ()))
        engines.append(EngineProfile(**item))
    if not engines:
        raise DomainAdapterError("shot routing requires at least one measured engine profile")
    decision = CostAwareShotRouter().route(request, engines)
    return _jsonable(decision)


def assess_shot_continuity(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _mapping(payload, "continuity assessment")
    before_data = _mapping(data.get("before"), "before snapshot")
    after_data = _mapping(data.get("after"), "after snapshot")
    link_data = _mapping(data.get("link"), "continuity link")
    before = ContinuitySnapshot(
        shot_id=str(before_data["shot_id"]),
        dimensions=dict(before_data["dimensions"]),
        canon_refs=tuple(before_data.get("canon_refs", ())),
        evidence_refs=tuple(before_data.get("evidence_refs", ())),
    )
    after = ContinuitySnapshot(
        shot_id=str(after_data["shot_id"]),
        dimensions=dict(after_data["dimensions"]),
        canon_refs=tuple(after_data.get("canon_refs", ())),
        evidence_refs=tuple(after_data.get("evidence_refs", ())),
    )
    rules = tuple(
        ContinuityRule(**{**dict(item), "reason": str(dict(item).get("reason", ""))})
        for item in link_data.get("rules", [])
    )
    link = ContinuityLink(
        from_shot_id=str(link_data["from_shot_id"]),
        to_shot_id=str(link_data["to_shot_id"]),
        rules=rules,
        rationale_refs=tuple(link_data.get("rationale_refs", ())),
    )
    assessment = assess_continuity(
        before, after, link, evidence_refs=tuple(data.get("evidence_refs", ())),
    )
    return {
        "hard_pass": assessment.hard_pass,
        "assessment": _jsonable(assessment),
    }


def outcome_metrics(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _mapping(payload, "EpisodeOutcomeReceipt")
    platforms = []
    for raw in data.get("platform_receipts", []):
        item = _mapping(raw, "PlatformPerformanceReceipt")
        item["evidence_refs"] = tuple(item.get("evidence_refs", ()))
        platforms.append(PlatformPerformanceReceipt(**item))
    production = ProductionEconomics(**_mapping(data.get("production"), "production"))
    commercial_data = _mapping(data.get("commercial", {}), "commercial")
    commercial_data["evidence_refs"] = tuple(commercial_data.get("evidence_refs", ()))
    commercial = CommercialOutcome(**commercial_data)
    receipt = EpisodeOutcomeReceipt(
        episode_id=str(data["episode_id"]),
        platform_receipts=tuple(platforms),
        production=production,
        commercial=commercial,
        qualitative_evidence_refs=tuple(data.get("qualitative_evidence_refs", ())),
        learning_candidate_refs=tuple(data.get("learning_candidate_refs", ())),
    )
    return {
        "episode_id": receipt.episode_id,
        "derived_metrics": receipt.derived_metrics(),
        "objective_vector": _jsonable(receipt.objective_vector()),
    }




def _model_routing_request(payload: Mapping[str, Any]) -> tuple[ShotRoutingRequest, tuple[ModelObservation, ...]]:
    data = _mapping(payload, "evidence-bound model routing request")
    request_data = dict(_mapping(data.get("request"), "routing request"))
    request_data["required_capabilities"] = frozenset(request_data.get("required_capabilities", []))
    request_data["quality_priorities"] = tuple(request_data.get("quality_priorities", []))
    request_data["quality_weights"] = dict(request_data.get("quality_weights", {}))
    request = ShotRoutingRequest(**request_data)

    raw_engines = data.get("engines")
    if not isinstance(raw_engines, list) or not raw_engines:
        raise DomainAdapterError("shot routing requires a non-empty engines array")
    engines = []
    for raw_engine in raw_engines:
        engine_data = dict(_mapping(raw_engine, "model observation"))
        engine_data["capabilities"] = frozenset(engine_data.get("capabilities", []))
        engine_data["resolutions"] = frozenset(engine_data.get("resolutions", []))
        for field_name in (
            "quality_evidence_refs", "pricing_evidence_refs", "terms_evidence_refs",
            "availability_evidence_refs",
        ):
            engine_data[field_name] = tuple(engine_data.get(field_name, []))
        profiles = []
        for raw_profile in engine_data.get("operation_profiles", []):
            profile_data = dict(_mapping(raw_profile, "operation profile"))
            profile_data["capabilities"] = frozenset(profile_data.get("capabilities", []))
            profile_data["allowed_durations_seconds"] = frozenset(profile_data.get("allowed_durations_seconds", []))
            profile_data["resolutions"] = frozenset(profile_data.get("resolutions", []))
            profile_data["allowed_source_origins"] = frozenset(profile_data.get("allowed_source_origins", []))
            profile_data["conditions"] = tuple(profile_data.get("conditions", []))
            profiles.append(OperationProfile(**profile_data))
        engine_data["operation_profiles"] = tuple(profiles)
        observations = {}
        for dimension, raw_observation in _mapping(
            engine_data.get("quality_observations", {}), "quality_observations"
        ).items():
            observation_data = dict(_mapping(raw_observation, f"quality observation {dimension}"))
            observation_data["evidence_refs"] = tuple(observation_data.get("evidence_refs", []))
            observations[str(dimension)] = QualityObservation(**observation_data)
        engine_data["quality_observations"] = observations
        engines.append(ModelObservation(**engine_data))
    return request, tuple(engines)


def ipos_import_receipt_from_dict(payload: Mapping[str, Any]) -> IPIdentityImportReceipt:
    data = _mapping(payload, "IPOS import receipt")
    return IPIdentityImportReceipt(
        bundle_ref=str(data["bundle_ref"]),
        canon_ref=str(data["canon_ref"]),
        bundle_digest=str(data["bundle_digest"]),
        bundle_asset_ref=AssetRef(**_mapping(data["bundle_asset_ref"], "bundle_asset_ref")),
        asset_refs=tuple(AssetRef(**_mapping(item, "asset_ref")) for item in data.get("asset_refs", [])),
        reference_bindings=tuple(ReferenceBinding(**_mapping(item, "reference_binding")) for item in data.get("reference_bindings", [])),
        imported_asset_refs=tuple(AssetRef(**_mapping(item, "imported_asset_ref")) for item in data.get("imported_asset_refs", [])),
        invalidated_refs=tuple(AssetRef(**_mapping(item, "invalidated_ref")) for item in data.get("invalidated_refs", [])),
    )


def _input_json(packet: Mapping[str, Any], name: str) -> dict[str, Any]:
    artifact = packet["input_artifacts"].get(name)
    if artifact is None:
        raise DomainAdapterError(f"required declared JSON input is unavailable: {name}")
    path = Path(artifact["path"])
    try:
        return _mapping(json.loads(path.read_text(encoding="utf-8")), f"input {name}")
    except (OSError, json.JSONDecodeError) as exc:
        raise DomainAdapterError(f"cannot read JSON input {name}: {exc}") from exc


def _input_path(packet: Mapping[str, Any], name: str) -> Path:
    artifact = packet["input_artifacts"].get(name)
    if artifact is None:
        raise DomainAdapterError(f"required declared input is unavailable: {name}")
    path = Path(artifact["path"])
    if not path.is_file():
        raise DomainAdapterError(f"declared input file is missing: {name}")
    return path


def _safe_filename(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    if not safe:
        raise DomainAdapterError("output name cannot be converted to a safe filename")
    return safe[:100]


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise DomainAdapterError(f"adapter output already exists; refusing overwrite: {path.name}")
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(_jsonable(payload), ensure_ascii=False, indent=2) + "\n")


def run_claimed_domain_adapter(
    engine: StudioEngine,
    project_id: str,
    task_id: str,
    worker_id: str,
    claim_token: str,
) -> dict[str, Any]:
    """Run one declared local domain adapter inside a current Studio task lease.

    Inputs must be declared task artifacts. Outputs are written into the project
    workspace and registered by the same immutable artifact/lineage transaction
    as any other task completion. This function never promotes a candidate or
    publishes media.
    """
    packet = engine.claimed_packet(project_id, task_id, worker_id, claim_token)
    task = packet["task"]
    requirements = _mapping(task.get("requirements", {}), "task.requirements")
    config = _mapping(requirements.get("domain_adapter"), "task.requirements.domain_adapter")
    name = str(config.get("name", "")).strip()
    if not name:
        raise DomainAdapterError("domain_adapter.name is required")
    outputs = list(task.get("outputs", []))
    if not outputs:
        raise DomainAdapterError("domain adapter task must declare at least one output")
    output_dir = engine._project_dir(project_id) / "artifacts" / "domain-adapters" / _safe_filename(task_id)
    attempt = int(task.get("attempt", 1))
    result: dict[str, Any]

    try:
        if name == "business_object_validate":
            object_type=str(config.get("object_type","")).strip(); input_name=str(config.get("input_name","")).strip()
            obj=business_object_from_dict(object_type,_input_json(packet,input_name)); output_name=str(config.get("output_name",outputs[0]))
            path=output_dir/f"{_safe_filename(output_name)}-attempt-{attempt}.json"; _write_json(path,{"schema_version":"1.0","adapter":name,"object_type":object_type,"object":_jsonable(obj)})
            identity_field={"ContentPortfolioItem":"item_id","DistinctiveAssetObservation":"asset_id","CommercialFit":"fit_id","RightsPackage":"package_id","CommercialOfferCandidate":"offer_id","BusinessHypothesisDecision":"decision_id"}[object_type]
            artifact_outputs={output_name:{"path":str(path),"kind":"business_object","media_type":"application/json","rights_status":"NOT_APPLICABLE","metadata":{"adapter":name,"object_type":object_type,"object_id":getattr(obj,identity_field)}}}
            result={"adapter":name,"object_type":object_type,"object_id":getattr(obj,identity_field)}
        elif name == "episode_intent_validate":
            handoff_input = str(config.get("handoff_input", "")).strip()
            expected_program_id = str(config.get("program_id") or "").strip() or None
            raw_handoff = _input_json(packet, handoff_input)
            if config.get("require_validated_transfer") is True:
                imported = packet["input_artifacts"].get(handoff_input)
                if imported is None:
                    raise DomainAdapterError(f"validated Program handoff input is unavailable: {handoff_input}")
                transfer = _mapping(imported.get("metadata", {}).get("cross_project_transfer"), "cross_project_transfer")
                target_project_id = engine.project(project_id)["project_id"]
                if transfer.get("schema_version") != "1.0" or transfer.get("transfer_mode") != "IMMUTABLE_COPY":
                    raise DomainAdapterError("Episode handoff must arrive through a schema 1.0 immutable cross-project transfer")
                if transfer.get("source_project_id") != expected_program_id:
                    raise DomainAdapterError("transferred Episode handoff has the wrong source Program")
                if transfer.get("target_project_id") != target_project_id or transfer.get("target_artifact_name") != handoff_input:
                    raise DomainAdapterError("transferred Episode handoff target identity does not match this Episode project/input")
                if transfer.get("source_artifact_name") != str(config.get("source_artifact_name", "validated-episode-intent")):
                    raise DomainAdapterError("transferred Episode handoff is not the validated Program artifact")
                if transfer.get("source_sha256") != imported.get("sha256"):
                    raise DomainAdapterError("transferred Episode handoff digest does not match its source transfer receipt")
                if not str(transfer.get("source_artifact_id") or "").strip() or not isinstance(transfer.get("source_artifact_version"), int):
                    raise DomainAdapterError("transferred Episode handoff is missing exact source artifact identity")
                source_validation = _mapping(raw_handoff.get("source_validation"), "source_validation")
                if source_validation.get("schema_version") != "1.0" or source_validation.get("status") != "PASS":
                    raise DomainAdapterError("Episode handoff lacks a passing source Program validation receipt")
                if source_validation.get("validator") != "video_studio.adapters.episode_intent_validate":
                    raise DomainAdapterError("Episode handoff source validation was not produced by the registered Program validator")
                if source_validation.get("source_project_id") != expected_program_id:
                    raise DomainAdapterError("Episode handoff source validation belongs to a different Program")
                if source_validation.get("source_artifact_bindings") != raw_handoff.get("source_artifact_bindings"):
                    raise DomainAdapterError("Episode handoff source validation does not match the embedded artifact bindings")
                handoff = program_episode_handoff_to_intent(raw_handoff, expected_program_id=expected_program_id)
                handoff["source_validation"] = source_validation
                handoff["cross_project_transfer"] = transfer
            else:
                handoff = program_episode_handoff_to_intent(raw_handoff, expected_program_id=expected_program_id)
                source_names = config.get("source_artifact_inputs")
                if not isinstance(source_names, list) or not source_names or len(source_names) != len(set(source_names)):
                    raise DomainAdapterError("Program handoff validation requires unique source_artifact_inputs")
                bindings = {item["name"]: item for item in handoff["source_artifact_bindings"]}
                if set(source_names) != set(bindings):
                    raise DomainAdapterError("source_artifact_inputs must exactly match the handoff's source_artifact_bindings")
                verified = []
                for source_name in sorted(source_names):
                    actual = packet["input_artifacts"].get(source_name)
                    binding = bindings[source_name]
                    if actual is None:
                        raise DomainAdapterError(f"Program source artifact is not bound as a declared input: {source_name}")
                    if (
                        binding["artifact_id"] != actual.get("artifact_id")
                        or binding["version"] != actual.get("version")
                        or binding["sha256"].lower() != str(actual.get("sha256", "")).lower()
                    ):
                        raise DomainAdapterError(f"Program handoff source binding does not match the exact current artifact: {source_name}")
                    verified.append({
                        "name": source_name, "artifact_id": actual["artifact_id"],
                        "version": actual["version"], "sha256": actual["sha256"],
                    })
                handoff["source_validation"] = {
                    "schema_version": "1.0", "status": "PASS",
                    "validator": "video_studio.adapters.episode_intent_validate",
                    "source_project_id": handoff["program_id"],
                    "source_artifact_bindings": verified,
                }
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            _write_json(path, handoff)
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "episode_intent", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {
                        "adapter": name, "program_id": handoff["program_id"],
                        "episode_id": handoff["episode_id"], "series_id": handoff["series_id"],
                        "identity_usage_mode": handoff["identity_usage"]["mode"],
                        "source_validation_status": handoff["source_validation"]["status"],
                        "cross_project_transfer_verified": bool(handoff.get("cross_project_transfer")),
                    },
                }
            }
            result = {
                "adapter": name, "program_id": handoff["program_id"],
                "episode_id": handoff["episode_id"], "series_id": handoff["series_id"],
                "identity_usage_mode": handoff["identity_usage"]["mode"],
                "source_validation_status": handoff["source_validation"]["status"],
                "cross_project_transfer_verified": bool(handoff.get("cross_project_transfer")),
            }
        elif name == "editorial_plan_validate":
            input_name = str(config["editorial_plan_input"])
            plan = editorial_plan_from_dict(_input_json(packet, input_name))
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            summary = {
                "adapter": name,
                "valid": True,
                "plan_ref": plan.plan_ref,
                "episode_id": plan.intent.episode_id,
                "claim_count": len(plan.claims),
                "beat_count": len(plan.beats),
                "shot_count": len(plan.shots),
                "editorial_plan": _jsonable(plan),
            }
            _write_json(path, summary)
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "valid": True, "plan_ref": plan.plan_ref},
                }
            }
            result = {"adapter": name, "valid": True, "plan_ref": plan.plan_ref}

        elif name == "shot_contract_materialize":
            plan_name = str(config["editorial_plan_input"])
            plan = editorial_plan_from_dict(_input_json(packet, plan_name))
            references = config.get("references", [])
            references_input = str(config.get("references_input", "")).strip()
            if references_input:
                reference_payload = _input_json(packet, references_input)
                references = reference_payload.get("references", [])
            if not isinstance(references, list) or not all(isinstance(item, dict) for item in references):
                raise DomainAdapterError("shot materialization references must be an array of objects")
            shot = materialize_shot_contract(
                plan,
                shot_id=str(config["shot_id"]),
                sequence_id=str(config["sequence_id"]),
                required_capabilities=frozenset(config.get("required_capabilities", [])),
                quality_targets=dict(config.get("quality_targets", {})),
                references=tuple(ReferenceBinding(**item) for item in references),
                continuity_ref=str(config.get("continuity_ref", "")),
                graceful_degradation=tuple(config.get("graceful_degradation", [])),
                stop_conditions=tuple(config.get("stop_conditions", [])),
                budget_usd=config.get("budget_usd"),
                disclosure_required=bool(config.get("disclosure_required", False)),
            )
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            payload = {"adapter": name, "valid": True, "shot_contract": _jsonable(shot)}
            _write_json(path, payload)
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "valid": True, "shot_id": shot.shot_id, "editorial_plan_ref": shot.editorial_plan_ref},
                }
            }
            result = {"adapter": name, "valid": True, "shot_id": shot.shot_id, "editorial_plan_ref": shot.editorial_plan_ref}

        elif name == "shot_contract_validate":
            input_name = str(config["shot_contract_input"])
            shot = shot_contract_from_dict(_input_json(packet, input_name))
            editorial_plan_name = str(config.get("editorial_plan_input", "")).strip()
            if editorial_plan_name:
                plan = editorial_plan_from_dict(_input_json(packet, editorial_plan_name))
                validate_shot_against_editorial_plan(plan, shot)
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            payload = {"adapter": name, "valid": True, "shot_contract": _jsonable(shot)}
            _write_json(path, payload)
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "valid": True, "shot_id": shot.shot_id},
                }
            }
            result = {"adapter": name, "valid": True, "shot_id": shot.shot_id}

        elif name == "ipos_bundle_inspect":
            input_name = str(config["bundle_input"])
            readiness = inspect_ipos_bundle(_input_json(packet, input_name))
            if not readiness.ready:
                raise DomainAdapterError("IPOS bundle is not video-ready: " + "; ".join(readiness.reasons))
            import_validation = None
            receipt_input = str(config.get("import_receipt_input", "")).strip()
            graph_input = str(config.get("media_graph_input", "")).strip()
            if bool(receipt_input) != bool(graph_input):
                raise DomainAdapterError("IPOS import verification requires both import_receipt_input and media_graph_input")
            if receipt_input and graph_input:
                receipt = ipos_import_receipt_from_dict(_input_json(packet, receipt_input))
                graph = MediaGraph.from_dict(_input_json(packet, graph_input))
                if receipt.bundle_ref != readiness.bundle_ref or receipt.canon_ref != readiness.canon_ref:
                    raise DomainAdapterError("IPOS import receipt does not match the inspected bundle/canon")
                bundle_asset = graph.assets.get(receipt.bundle_asset_ref)
                if bundle_asset is None or graph.asset_state(receipt.bundle_asset_ref) != "PROMOTED":
                    raise DomainAdapterError("IPOS bundle asset is missing or not promoted in MediaGraph")
                if bundle_asset.digest != receipt.bundle_digest:
                    raise DomainAdapterError("IPOS bundle asset digest does not match the import receipt")
                verified_refs = 0
                for ref in receipt.imported_asset_refs:
                    asset = graph.assets.get(ref)
                    if asset is None or graph.asset_state(ref) != "PROMOTED":
                        raise DomainAdapterError(f"IPOS imported asset is missing or not promoted: {ref.key()}")
                    verified_refs += 1
                for binding in receipt.reference_bindings:
                    ref = AssetRef(binding.asset_id, binding.version_id)
                    asset = graph.assets.get(ref)
                    if asset is None or graph.asset_state(ref) != "PROMOTED" or asset.digest != binding.digest:
                        raise DomainAdapterError(f"IPOS reference binding does not match the exact promoted digest: {ref.key()}")
                import_validation = {
                    "bundle_asset_ref": receipt.bundle_asset_ref.key(),
                    "bundle_digest": receipt.bundle_digest,
                    "imported_asset_count": verified_refs,
                    "reference_binding_count": len(receipt.reference_bindings),
                    "media_graph_context_id": bundle_asset.context_id,
                }
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            payload = {"adapter": name, "readiness": _jsonable(readiness), "import_validation": import_validation}
            _write_json(path, payload)
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {
                        "adapter": name, "ipos_ready": True, "bundle_ref": readiness.bundle_ref,
                        "import_verified": import_validation is not None,
                        "imported_asset_count": import_validation["imported_asset_count"] if import_validation else 0,
                    },
                }
            }
            result = {
                "adapter": name, "ipos_ready": True, "bundle_ref": readiness.bundle_ref,
                "import_verified": import_validation is not None,
                "imported_asset_count": import_validation["imported_asset_count"] if import_validation else 0,
            }

        elif name == "media_graph_initialize":
            contexts = config.get("contexts", [])
            if not isinstance(contexts, list) or not contexts:
                raise DomainAdapterError("media_graph_initialize requires a non-empty contexts array")
            graph = MediaGraph()
            for raw_context in contexts:
                context_data = _mapping(raw_context, "MediaGraph context")
                graph.add_context(ContextRecord(**context_data))
            output_name = str(config.get("output_name", outputs[0]))
            if outputs != [output_name]:
                raise DomainAdapterError("media_graph_initialize must declare exactly its output_name")
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            _write_json(path, graph.to_dict())
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "domain_state", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "context_count": len(graph.contexts), "asset_count": 0},
                }
            }
            result = {"adapter": name, "context_count": len(graph.contexts), "asset_count": 0}

        elif name == "ipos_bundle_import":
            bundle_name = str(config["bundle_input"])
            graph_name = str(config["media_graph_input"])
            graph = MediaGraph.from_dict(_input_json(packet, graph_name))
            receipt = import_ipos_bundle(
                _input_json(packet, bundle_name),
                graph,
                program_context_id=str(config["program_context_id"]),
            )
            graph_output = str(config["media_graph_output"])
            receipt_output = str(config["receipt_output"])
            if set(outputs) != {graph_output, receipt_output}:
                raise DomainAdapterError("ipos_bundle_import must declare exactly media_graph_output and receipt_output")
            graph_path = output_dir / f"{_safe_filename(graph_output)}-attempt-{attempt}.json"
            receipt_path = output_dir / f"{_safe_filename(receipt_output)}-attempt-{attempt}.json"
            _write_json(graph_path, graph.to_dict())
            _write_json(receipt_path, receipt)
            artifact_outputs = {
                graph_output: {
                    "path": str(graph_path), "kind": "domain_state", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE", "metadata": {"adapter": name, "canon_ref": receipt.canon_ref},
                },
                receipt_output: {
                    "path": str(receipt_path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE", "metadata": {"adapter": name, "bundle_digest": receipt.bundle_digest},
                },
            }
            result = {"adapter": name, "bundle_ref": receipt.bundle_ref, "imported_asset_count": len(receipt.imported_asset_refs)}

        elif name == "ipos_shot_bind":
            bundle = _input_json(packet, str(config["bundle_input"]))
            receipt = ipos_import_receipt_from_dict(_input_json(packet, str(config["import_receipt_input"])))
            graph = MediaGraph.from_dict(_input_json(packet, str(config["media_graph_input"])))
            for binding in receipt.reference_bindings:
                ref = AssetRef(binding.asset_id, binding.version_id)
                asset = graph.assets.get(ref)
                if asset is None or graph.asset_state(ref) != "PROMOTED" or asset.digest != binding.digest:
                    raise DomainAdapterError(f"IPOS reference is not present as the exact promoted MediaGraph version: {ref.key()}")
            shot = shot_contract_from_dict(_input_json(packet, str(config["shot_contract_input"])))
            bound = bind_ipos_identity_to_shot(
                shot, bundle, receipt, required=bool(config.get("required", True)),
            )
            rules = build_ipos_continuity_rules(bundle)
            shot_output = str(config["shot_contract_output"])
            rules_output = str(config["continuity_rules_output"])
            if set(outputs) != {shot_output, rules_output}:
                raise DomainAdapterError("ipos_shot_bind must declare exactly shot_contract_output and continuity_rules_output")
            shot_path = output_dir / f"{_safe_filename(shot_output)}-attempt-{attempt}.json"
            rules_path = output_dir / f"{_safe_filename(rules_output)}-attempt-{attempt}.json"
            _write_json(shot_path, {"adapter": name, "shot_contract": _jsonable(bound)})
            _write_json(rules_path, {"adapter": name, "continuity_rules": _jsonable(rules)})
            artifact_outputs = {
                shot_output: {
                    "path": str(shot_path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "shot_id": bound.shot_id, "ip_identity_required": bound.ip_identity_required, "ip_identity_bundle_ref": bound.ip_identity_bundle_ref},
                },
                rules_output: {
                    "path": str(rules_path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "canon_ref": receipt.canon_ref, "rule_count": len(rules)},
                },
            }
            result = {"adapter": name, "shot_id": bound.shot_id, "ip_identity_required": bound.ip_identity_required, "canon_ref": receipt.canon_ref, "reference_count": len(bound.references)}

        elif name == "ipos_continuity_snapshot":
            bundle = _input_json(packet, str(config["bundle_input"]))
            shot_id = str(config["shot_id"])
            snapshot = build_ipos_continuity_snapshot(shot_id, bundle)
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            _write_json(path, {"adapter": name, "snapshot": _jsonable(snapshot)})
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "shot_id": shot_id, "canon_refs": list(snapshot.canon_refs)},
                }
            }
            result = {"adapter": name, "shot_id": shot_id, "dimension_count": len(snapshot.dimensions)}

        elif name == "ipos_continuity_link":
            bundle = _input_json(packet, str(config["bundle_input"]))
            link = build_ipos_continuity_link(
                str(config["from_shot_id"]), str(config["to_shot_id"]), bundle,
            )
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            _write_json(path, {"adapter": name, "link": _jsonable(link)})
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "from_shot_id": link.from_shot_id, "to_shot_id": link.to_shot_id, "rule_count": len(link.rules)},
                }
            }
            result = {"adapter": name, "from_shot_id": link.from_shot_id, "to_shot_id": link.to_shot_id, "rule_count": len(link.rules)}

        elif name == "timeline_validate":
            timeline = timeline_spec_from_dict(_input_json(packet, str(config["timeline_input"])))
            graph = MediaGraph.from_dict(_input_json(packet, str(config["media_graph_input"])))
            timeline.validate_against_graph(
                graph, require_promoted_assets=bool(config.get("require_promoted_assets", True)),
            )
            platform = str(config.get("platform", "")).strip()
            master_input = str(config.get("master_timeline_input", "")).strip()
            if platform or master_input:
                if not platform or not master_input:
                    raise DomainAdapterError("platform and master_timeline_input must be supplied together")
                master = timeline_spec_from_dict(_input_json(packet, master_input))
                assert_platform_variant_lineage(master=master, variant=timeline, platform=platform)
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            receipt = {
                "adapter": name, "valid": True, "timeline_id": timeline.timeline_id,
                "version_id": timeline.version_id, "duration_seconds": timeline.duration_seconds,
                "clip_count": len(timeline.clips), "asset_refs": [ref.key() for ref in timeline.asset_refs()],
                "platform": platform or None, "derived_from_version": timeline.derived_from_version,
            }
            _write_json(path, receipt)
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE", "metadata": {"adapter": name, "valid": True, "timeline_id": timeline.timeline_id},
                }
            }
            result = receipt

        elif name == "shot_route":
            request, engines = _model_routing_request(
                _input_json(packet, str(config["routing_request_input"]))
            )
            now_value = str(config.get("now", "")).strip()
            now = datetime.fromisoformat(now_value.replace("Z", "+00:00")) if now_value else None
            decision = EvidenceBoundModelRouter().route(request, engines, now=now)
            route = _jsonable(decision)
            route["blocked"] = decision.blocked
            if decision.blocked and config.get("block_if_no_engine", True):
                raise DomainAdapterError(
                    "shot routing blocked: no current model observation satisfies operation profile, "
                    "commercial terms, provenance, calibrated quality, evidence freshness and budget policy: "
                    + str(decision.blocked_reason)
                )
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            _write_json(path, {"adapter": name, **route})
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "decision", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {
                        "adapter": name, "selected_engine_id": decision.selected_engine_id,
                        "blocked": decision.blocked, "blocked_reason": decision.blocked_reason,
                        "pareto_front": list(decision.pareto_front),
                    },
                }
            }
            result = {
                "adapter": name, "selected_engine_id": decision.selected_engine_id,
                "blocked": decision.blocked, "blocked_reason": decision.blocked_reason,
                "pareto_front": list(decision.pareto_front),
            }

        elif name == "extended_media_qa":
            media_name = str(config["media_input"])
            media_path = _input_path(packet, media_name)
            report = MediaQAChecker().inspect(media_path).to_dict()
            if report.get("hard_pass") is not True and config.get("block_on_hard_fail", True):
                raise DomainAdapterError("supplementary media QA hard-failed: " + json.dumps(report.get("checks", []), ensure_ascii=False))
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            payload = {"adapter": name, **report}
            _write_json(path, payload)
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "qa_report", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {
                        "adapter": name, "checker": report.get("metadata", {}).get("checker"),
                        "media_sha256": report.get("metadata", {}).get("sha256"),
                        "hard_pass": report.get("hard_pass"),
                    },
                }
            }
            result = {"adapter": name, "hard_pass": report.get("hard_pass"), "check_count": len(report.get("checks", []))}

        elif name == "continuity_assess":
            continuity = assess_shot_continuity(_input_json(packet, str(config["continuity_input"])))
            if not continuity["hard_pass"] and config.get("block_on_hard_fail", True):
                violations = continuity["assessment"]["violations"]
                raise DomainAdapterError("hard continuity violation(s): " + json.dumps(violations, ensure_ascii=False))
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            _write_json(path, {"adapter": name, **continuity})
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "hard_pass": continuity["hard_pass"]},
                }
            }
            result = {"adapter": name, "hard_pass": continuity["hard_pass"]}

        elif name == "business_outcome_metrics":
            metrics = outcome_metrics(_input_json(packet, str(config["outcome_receipt_input"])))
            output_name = str(config.get("output_name", outputs[0]))
            path = output_dir / f"{_safe_filename(output_name)}-attempt-{attempt}.json"
            _write_json(path, {"adapter": name, **metrics})
            artifact_outputs = {
                output_name: {
                    "path": str(path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "episode_id": metrics["episode_id"]},
                }
            }
            result = {"adapter": name, "episode_id": metrics["episode_id"], "derived_metrics": metrics["derived_metrics"]}

        elif name == "programmatic_graphic_render":
            spec_name = str(config["graphic_spec_input"])
            shot_name = str(config["shot_contract_input"])
            font_name = str(config["font_input"])
            rights_name = str(config["rights_evidence_input"])
            spec = graphic_spec_from_dict(_input_json(packet, spec_name))
            shot = shot_contract_from_dict(_input_json(packet, shot_name))
            editorial_plan_name = str(config["editorial_plan_input"])
            editorial_plan = editorial_plan_from_dict(_input_json(packet, editorial_plan_name))
            validate_shot_against_editorial_plan(editorial_plan, shot)
            font_path = _input_path(packet, font_name)
            font_artifact = packet["input_artifacts"].get(font_name)
            rights_artifact = packet["input_artifacts"].get(rights_name)
            if font_artifact is None or font_artifact.get("rights_status") not in {"OWNED", "AUTHORIZED", "LICENSED", "PUBLIC_DOMAIN"}:
                raise DomainAdapterError(f"font input must have an allowed, evidenced rights status: {font_name}")
            if rights_artifact is None or rights_artifact.get("kind") not in {"document", "evidence", "rights_record"}:
                raise DomainAdapterError(f"rights evidence input must be a declared document/evidence artifact: {rights_name}")
            if rights_artifact.get("rights_status") not in {"OWNED", "AUTHORIZED", "LICENSED", "PUBLIC_DOMAIN"}:
                raise DomainAdapterError(f"rights evidence artifact itself is not rights-cleared: {rights_name}")
            input_names = set(packet["input_artifacts"])
            font_rights_refs = font_artifact.get("metadata", {}).get("rights_evidence_refs", [])
            if not isinstance(font_rights_refs, list) or rights_name not in font_rights_refs:
                raise DomainAdapterError(f"font metadata.rights_evidence_refs must include the exact rights evidence artifact: {rights_name}")
            for binding in shot.references:
                rights_binding = packet["input_artifacts"].get(binding.rights_ref)
                if (
                    rights_binding is None
                    or rights_binding.get("kind") not in {"document", "evidence", "rights_record"}
                    or rights_binding.get("rights_status") not in {"OWNED", "AUTHORIZED", "LICENSED", "PUBLIC_DOMAIN"}
                ):
                    raise DomainAdapterError(f"ShotContract rights_ref must resolve to a rights-cleared evidence artifact: {binding.rights_ref}")
                if binding.consent_ref:
                    consent_binding = packet["input_artifacts"].get(binding.consent_ref)
                    if (
                        consent_binding is None
                        or consent_binding.get("kind") not in {"document", "evidence", "rights_record"}
                        or consent_binding.get("rights_status") not in {"OWNED", "AUTHORIZED", "LICENSED", "PUBLIC_DOMAIN"}
                    ):
                        raise DomainAdapterError(f"ShotContract consent_ref must resolve to a rights-cleared consent evidence artifact: {binding.consent_ref}")
            video_output = str(config["video_output"])
            receipt_output = str(config["receipt_output"])
            graph_input = str(config.get("media_graph_input", "")).strip()
            graph_output = str(config.get("media_graph_output", "")).strip()
            expected = {video_output, receipt_output}
            if graph_input or graph_output:
                if not graph_input or not graph_output:
                    raise DomainAdapterError("media_graph_input and media_graph_output must be supplied together")
                expected.add(graph_output)
            if shot.references and not graph_input:
                raise DomainAdapterError("referenced shots require media_graph_input for exact promoted-asset validation")
            if set(outputs) != expected:
                raise DomainAdapterError(f"programmatic_graphic_render outputs must be {sorted(expected)}")
            media_path = output_dir / f"{_safe_filename(video_output)}-attempt-{attempt}.mp4"
            receipt = render_programmatic_graphic(shot, spec, output_path=media_path, font_path=font_path)
            receipt_path = output_dir / f"{_safe_filename(receipt_output)}-attempt-{attempt}.json"
            _write_json(receipt_path, receipt)
            artifact_outputs = {
                video_output: {
                    "path": str(media_path), "kind": "video", "media_type": "video/mp4",
                    "rights_status": "OWNED",
                    "metadata": {
                        "adapter": name, "candidate_only": True, "promotion_authorized": False,
                        "release_authorized": False, "media_sha256": receipt["media_sha256"],
                        "shot_contract_digest": receipt["shot_contract_digest"],
                        "graphic_spec_digest": receipt["graphic_spec_digest"],
                        "rights_evidence_refs": [rights_name],
                    },
                },
                receipt_output: {
                    "path": str(receipt_path), "kind": "evidence", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "candidate_only": True, "media_sha256": receipt["media_sha256"]},
                },
            }
            graph_candidate_ref = None
            if graph_input:
                graph = MediaGraph.from_dict(_input_json(packet, graph_input))
                graph_candidate_ref = register_graph_candidate(graph, shot, spec, receipt)
                graph_path = output_dir / f"{_safe_filename(graph_output)}-attempt-{attempt}.json"
                _write_json(graph_path, graph.to_dict())
                artifact_outputs[graph_output] = {
                    "path": str(graph_path), "kind": "domain_state", "media_type": "application/json",
                    "rights_status": "NOT_APPLICABLE",
                    "metadata": {"adapter": name, "candidate_ref": graph_candidate_ref, "candidate_only": True},
                }
            result = {
                "adapter": name, "candidate_only": True, "media_sha256": receipt["media_sha256"],
                "duration_seconds": receipt["duration_seconds"], "width": receipt["width"],
                "height": receipt["height"], "fps": receipt["fps"], "graph_candidate_ref": graph_candidate_ref,
            }

        else:
            raise DomainAdapterError(f"unsupported domain adapter: {name}")

        if set(artifact_outputs) != set(outputs):
            raise DomainAdapterError(f"adapter {name} produced {sorted(artifact_outputs)} but task declares {sorted(outputs)}")
        completed = engine.complete_task(project_id, task_id, worker_id, claim_token, artifact_outputs, result=result)
        return {"status": "COMPLETED", "adapter": name, "result": result, "completion": completed}

    except Exception as exc:
        try:
            engine.fail_task(
                project_id, task_id, worker_id, claim_token,
                {"category": "domain_adapter_failed", "adapter": name, "exception": type(exc).__name__, "message": str(exc)},
                retryable=False,
            )
        except Exception:
            pass
        if isinstance(exc, StudioError):
            raise
        raise DomainAdapterError(f"domain adapter {name} failed: {exc}") from exc
