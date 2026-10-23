from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from .editorial_planning import EditorialPlan
from .media_graph import AssetRef, AssetVersion, MediaGraph


class PlanGraphBridgeError(ValueError):
    pass


def editorial_plan_digest(plan: EditorialPlan) -> str:
    payload = json.dumps(asdict(plan), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=list).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def editorial_plan_asset_ref(plan: EditorialPlan) -> AssetRef:
    return AssetRef(asset_id=f"editorial-plan:{plan.intent.episode_id}", version_id=plan.plan_version)


def register_editorial_plan_asset(
    graph: MediaGraph,
    *,
    plan: EditorialPlan,
    context_id: str,
    uri: str,
    rights_refs: tuple[str, ...] = (),
    provenance_refs: tuple[str, ...] = (),
) -> AssetRef:
    """Register one immutable editorial-plan version in the existing MediaGraph.

    Production assets/tasks can bind this AssetRef as an input/derived_from edge. A
    later plan version does not mutate the old version; invalidating the old plan can
    mechanically stale its downstream production assets.
    """
    if context_id not in graph.contexts:
        raise PlanGraphBridgeError(f"plan context missing: {context_id}")
    if not uri.strip():
        raise PlanGraphBridgeError("durable plan uri is required")
    ref = editorial_plan_asset_ref(plan)
    graph.add_asset(
        AssetVersion(
            ref=ref,
            context_id=context_id,
            kind="EDITORIAL_PLAN",
            uri=uri,
            digest=editorial_plan_digest(plan),
            rights_refs=rights_refs,
            provenance_refs=provenance_refs,
            metadata={
                "episode_id": plan.intent.episode_id,
                "series_id": plan.intent.series_id,
                "plan_ref": plan.plan_ref,
            },
        )
    )
    return ref

def register_directed_take_observation(
    graph: MediaGraph,
    *,
    plan: dict,
    media: str,
    context_id: str,
    director_plan_id: str,
    plan_version: str,
    take_id: str,
    take_version: str,
    rights_refs: tuple[str, ...] = (),
) -> tuple[AssetRef, dict]:
    """Register one real local take and its unscored technical review.

    Uses existing MediaGraph identities/evidence. Never asserts vendor origin,
    independent viewing, frame-by-frame story semantics, or promotion.
    A new plan version stales only downstream media attached to the old version.
    """
    from datetime import datetime, timezone
    from .media_qa import prepare_directed_media_review
    from .media_graph import EvidenceRecord, MediaGraphError
    from .prompt_director import validate_plan

    validate_plan(plan)
    if context_id not in graph.contexts:
        raise PlanGraphBridgeError("existing sequence/shot context is required")
    if graph.contexts[context_id].kind not in {"SEQUENCE", "SHOT"}:
        raise PlanGraphBridgeError("directed take needs a sequence or shot context")
    plan_ref = AssetRef(director_plan_id, plan_version)
    take_ref = AssetRef(take_id, take_version)
    if plan_ref == take_ref:
        raise PlanGraphBridgeError("director plan and take must have distinct identities")
    if take_ref in graph.assets:
        raise PlanGraphBridgeError("take version already registered; use a new take version")
    digest = hashlib.sha256(json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    existing = graph.assets.get(plan_ref)
    if existing is not None and (
        existing.kind != "DIRECTOR_PLAN" or existing.digest != "sha256:" + digest
        or existing.context_id != context_id
    ):
        raise PlanGraphBridgeError("director plan identity does not match stored immutable plan")
    if existing is not None and graph.asset_state(plan_ref) not in {"CANDIDATE", "PROMOTED"}:
        raise PlanGraphBridgeError("stale/rejected director plan cannot produce a current take")
    # Media bytes and mechanical checks must be observed before the graph is
    # mutated. The review packet is a *prepared* review, not a watched film.
    packet = prepare_directed_media_review(plan, media)
    if packet["source_plan_sha256"] != digest:
        raise PlanGraphBridgeError("director plan digest drift during media inspection")
    raw_sha = packet["media_asset_ref"]["sha256"]
    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if existing is None:
        graph.add_asset(AssetVersion(
            ref=plan_ref, context_id=context_id, kind="DIRECTOR_PLAN",
            uri="source-plan-sha256:" + digest, digest="sha256:" + digest,
            metadata={
                "source_reference": plan["source"]["reference"],
                "source_scope_claim": plan["source"]["completeness"],
                "narrative_semantics_verified": False,
            },
        ))
    graph.add_asset(AssetVersion(
        ref=take_ref, context_id=context_id, kind="VIDEO_TAKE",
        uri=packet["media_asset_ref"]["uri"], digest="sha256:" + raw_sha,
        derived_from=(plan_ref,), rights_refs=rights_refs,
        metadata={
            "review_state": "NOT_STARTED",
            "technical_hard_pass": packet["technical_media_qa"]["hard_pass"],
            "timeline_alignment": packet["timeline_alignment"],
            "provider_execution_verified": False,
            "independent_viewing_verified": False,
            "release_authorized": False,
        },
    ))
    evidence_id = "media-inspection:" + take_ref.key()
    graph.add_evidence(EvidenceRecord(
        evidence_id=evidence_id, subject_type="ASSET", subject_id=take_ref.key(),
        action="TECHNICAL_MEDIA_INSPECTION_AND_REVIEW_PACKET_PREPARED",
        refs=(take_ref.key(), "sha256:" + raw_sha, plan_ref.key()),
        observed_at=observed_at,
        metadata={"review_packet": packet, "quality_outcome": "NOT_REVIEWED"},
    ))
    return take_ref, packet
