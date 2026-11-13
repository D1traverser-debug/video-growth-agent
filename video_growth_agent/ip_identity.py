from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Mapping

from .continuity import ContinuityLink, ContinuityRule, ContinuitySnapshot
from .media_graph import (
    AssetRef,
    AssetVersion,
    DecisionRecord,
    EvidenceRecord,
    MediaGraph,
    MediaGraphError,
)
from .production_os import (
    GenerationAdmission,
    ReferenceBinding,
    ShotContract,
    admit_candidate_generation,
)


IPOS_BUNDLE_SCHEMA_VERSION = "1.0"
IPOS_ISSUER = "IP_STUDIO_OS"
VIDEO_READY_STATUS = "READY_FOR_VIDEO"
REQUIRED_VIDEO_GATES = ("G2", "G7", "G8")
PRIMARY_VISUAL_ROLES = {
    "PRIMARY_VISUAL_REFERENCE",
    "TURNAROUND_SHEET",
    "CHARACTER_MODEL",
}


class IPIdentityIntegrationError(ValueError):
    """Raised when an IPOS identity export cannot safely enter video production."""


def _required_text(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise IPIdentityIntegrationError(f"{field_name} is required")
    return text


def _text_tuple(value: Any, field_name: str, *, required: bool = False) -> tuple[str, ...]:
    if value is None:
        values: tuple[str, ...] = ()
    elif isinstance(value, (list, tuple)):
        values = tuple(str(item).strip() for item in value if str(item).strip())
    else:
        raise IPIdentityIntegrationError(f"{field_name} must be an array of strings")
    if required and not values:
        raise IPIdentityIntegrationError(f"{field_name} must not be empty")
    return values


def _canonical_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _validate_timestamp(value: str, field_name: str) -> str:
    text = _required_text(value, field_name)
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise IPIdentityIntegrationError(f"{field_name} must be an ISO-8601 timestamp") from exc
    return text


@dataclass(frozen=True)
class IPIdentityAsset:
    asset_id: str
    version_id: str
    kind: str
    role: str
    uri: str
    digest: str
    state: str
    approved_for_video: bool
    rights_ref: str
    provenance_refs: tuple[str, ...]
    consent_ref: str | None = None
    requires_consent: bool = False

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "IPIdentityAsset":
        if not isinstance(raw, Mapping):
            raise IPIdentityIntegrationError("each IPOS asset must be an object")
        consent_ref = str(raw.get("consent_ref") or "").strip() or None
        item = cls(
            asset_id=_required_text(raw.get("asset_id"), "asset.asset_id"),
            version_id=_required_text(raw.get("version_id"), "asset.version_id"),
            kind=_required_text(raw.get("kind"), "asset.kind"),
            role=_required_text(raw.get("role"), "asset.role").upper(),
            uri=_required_text(raw.get("uri"), "asset.uri"),
            digest=_required_text(raw.get("digest"), "asset.digest"),
            state=_required_text(raw.get("state"), "asset.state").upper(),
            approved_for_video=raw.get("approved_for_video") is True,
            rights_ref=_required_text(raw.get("rights_ref"), "asset.rights_ref"),
            provenance_refs=_text_tuple(
                raw.get("provenance_refs"),
                "asset.provenance_refs",
                required=True,
            ),
            consent_ref=consent_ref,
            requires_consent=raw.get("requires_consent") is True,
        )
        if item.requires_consent and not item.consent_ref:
            raise IPIdentityIntegrationError(
                f"asset {item.asset_id} requires consent_ref"
            )
        return item

    @property
    def video_eligible(self) -> bool:
        return (
            self.state == "PROMOTED"
            and self.approved_for_video
            and re.fullmatch(r"sha256:[0-9a-fA-F]{64}", self.digest) is not None
            and bool(self.rights_ref)
            and bool(self.provenance_refs)
            and (not self.requires_consent or bool(self.consent_ref))
        )


@dataclass(frozen=True)
class IPIdentityReadiness:
    ready: bool
    bundle_ref: str
    canon_ref: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class IPIdentityImportReceipt:
    bundle_ref: str
    canon_ref: str
    bundle_digest: str
    bundle_asset_ref: AssetRef
    asset_refs: tuple[AssetRef, ...]
    reference_bindings: tuple[ReferenceBinding, ...]
    imported_asset_refs: tuple[AssetRef, ...]
    invalidated_refs: tuple[AssetRef, ...]


@dataclass(frozen=True)
class IPIdentityBundle:
    bundle_id: str
    project_id: str
    issued_at: str
    canon_id: str
    canon_version: str
    carrier: str
    identity_thesis: str
    identity_invariants: tuple[str, ...]
    allowed_variations: tuple[str, ...]
    forbidden_drift: tuple[str, ...]
    approval_status: str
    approval_ref: str
    approved_at: str
    readiness_status: str
    gates: Mapping[str, str]
    video_allowed: bool
    usage_constraints: tuple[str, ...]
    assets: tuple[IPIdentityAsset, ...]
    continuity_dimensions: Mapping[str, str]
    continuity_rules: tuple[Mapping[str, Any], ...]
    source_provenance_refs: tuple[str, ...]
    bundle_uri: str
    raw_payload: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "IPIdentityBundle":
        if not isinstance(payload, Mapping):
            raise IPIdentityIntegrationError("IPOS bundle must be a JSON object")
        if str(payload.get("schema_version") or "") != IPOS_BUNDLE_SCHEMA_VERSION:
            raise IPIdentityIntegrationError(
                "unsupported IPOS bundle schema_version: "
                + str(payload.get("schema_version"))
            )
        if str(payload.get("issuer") or "") != IPOS_ISSUER:
            raise IPIdentityIntegrationError("bundle issuer must be IP_STUDIO_OS")

        canon = payload.get("canon")
        approval = payload.get("approval")
        readiness = payload.get("readiness")
        usage = payload.get("usage")
        continuity = payload.get("continuity")
        if not all(isinstance(item, Mapping) for item in (canon, approval, readiness, usage, continuity)):
            raise IPIdentityIntegrationError(
                "canon, approval, readiness, usage and continuity objects are required"
            )

        raw_assets = payload.get("assets")
        if not isinstance(raw_assets, list):
            raise IPIdentityIntegrationError("assets must be an array")
        assets = tuple(IPIdentityAsset.from_mapping(item) for item in raw_assets)
        identities = [(item.asset_id, item.version_id) for item in assets]
        if len(identities) != len(set(identities)):
            raise IPIdentityIntegrationError("duplicate IPOS asset_id/version_id pair")

        dimensions_raw = continuity.get("dimensions")
        if not isinstance(dimensions_raw, Mapping):
            raise IPIdentityIntegrationError("continuity.dimensions must be an object")
        dimensions = {
            _required_text(key, "continuity dimension name"): _required_text(
                value, f"continuity.dimensions.{key}"
            )
            for key, value in dimensions_raw.items()
        }
        rules_raw = continuity.get("rules", [])
        if not isinstance(rules_raw, list):
            raise IPIdentityIntegrationError("continuity.rules must be an array")
        rules: list[Mapping[str, Any]] = []
        rule_dimensions: set[str] = set()
        for raw_rule in rules_raw:
            if not isinstance(raw_rule, Mapping):
                raise IPIdentityIntegrationError("each continuity rule must be an object")
            dimension = _required_text(raw_rule.get("dimension"), "continuity rule dimension")
            if dimension not in dimensions:
                raise IPIdentityIntegrationError(
                    f"continuity rule references undeclared dimension: {dimension}"
                )
            if dimension in rule_dimensions:
                raise IPIdentityIntegrationError(
                    f"duplicate continuity rule dimension: {dimension}"
                )
            rule_dimensions.add(dimension)
            severity = _required_text(raw_rule.get("severity"), "continuity rule severity").upper()
            mode = _required_text(raw_rule.get("mode"), "continuity rule mode").upper()
            if severity not in {"HARD", "SOFT"} or mode not in {"PRESERVE", "EXPECT", "ALLOW_CHANGE"}:
                raise IPIdentityIntegrationError(
                    f"unsupported continuity rule: {dimension}/{severity}/{mode}"
                )
            expected = str(raw_rule.get("expected_value") or "").strip() or None
            if mode == "EXPECT" and not expected:
                raise IPIdentityIntegrationError(
                    f"EXPECT continuity rule requires expected_value: {dimension}"
                )
            rules.append({
                "dimension": dimension,
                "severity": severity,
                "mode": mode,
                "expected_value": expected,
                "reason": str(raw_rule.get("reason") or "").strip(),
            })

        gates_raw = readiness.get("gates")
        if not isinstance(gates_raw, Mapping):
            raise IPIdentityIntegrationError("readiness.gates must be an object")
        gates = {str(key).upper(): str(value).upper() for key, value in gates_raw.items()}

        return cls(
            bundle_id=_required_text(payload.get("bundle_id"), "bundle_id"),
            project_id=_required_text(payload.get("project_id"), "project_id"),
            issued_at=_validate_timestamp(payload.get("issued_at"), "issued_at"),
            canon_id=_required_text(canon.get("canon_id"), "canon.canon_id"),
            canon_version=_required_text(canon.get("version"), "canon.version"),
            carrier=_required_text(canon.get("carrier"), "canon.carrier"),
            identity_thesis=_required_text(canon.get("identity_thesis"), "canon.identity_thesis"),
            identity_invariants=_text_tuple(
                canon.get("identity_invariants"),
                "canon.identity_invariants",
                required=True,
            ),
            allowed_variations=_text_tuple(
                canon.get("allowed_variations"),
                "canon.allowed_variations",
            ),
            forbidden_drift=_text_tuple(
                canon.get("forbidden_drift"),
                "canon.forbidden_drift",
                required=True,
            ),
            approval_status=str(approval.get("status") or "NOT_APPROVED").upper(),
            approval_ref=str(approval.get("approval_ref") or "").strip(),
            approved_at=str(approval.get("approved_at") or "").strip(),
            readiness_status=str(readiness.get("status") or "NOT_READY").upper(),
            gates=gates,
            video_allowed=usage.get("video_allowed") is True,
            usage_constraints=_text_tuple(
                usage.get("usage_constraints"),
                "usage.usage_constraints",
            ),
            assets=assets,
            continuity_dimensions=dimensions,
            continuity_rules=tuple(rules),
            source_provenance_refs=_text_tuple(
                payload.get("source_provenance_refs"),
                "source_provenance_refs",
            ),
            bundle_uri=str(payload.get("bundle_uri") or "").strip()
            or f"ipos://{payload.get('bundle_id')}@{canon.get('version')}",
            raw_payload=dict(payload),
        )

    @property
    def bundle_ref(self) -> str:
        return f"ipos://{self.bundle_id}@{self.canon_version}"

    @property
    def canon_ref(self) -> str:
        return f"ipos://{self.canon_id}@{self.canon_version}"

    @property
    def approval_reference(self) -> str:
        return self.approval_ref

    @property
    def digest(self) -> str:
        return _canonical_digest(self.raw_payload)

    def readiness(self) -> IPIdentityReadiness:
        reasons: list[str] = []
        if self.approval_status != "OWNER_APPROVED":
            reasons.append("IPOS_CANON_NOT_OWNER_APPROVED")
        if self.approval_status == "OWNER_APPROVED" and not self.approved_at:
            reasons.append("IPOS_OWNER_APPROVAL_TIMESTAMP_MISSING")
        if not self.approval_ref:
            reasons.append("IPOS_OWNER_APPROVAL_REFERENCE_MISSING")
        if self.readiness_status != VIDEO_READY_STATUS:
            reasons.append("IPOS_BUNDLE_NOT_MARKED_READY_FOR_VIDEO")
        for gate in REQUIRED_VIDEO_GATES:
            if self.gates.get(gate) != "PASS":
                reasons.append(f"IPOS_GATE_NOT_PASSED:{gate}")
        if not self.video_allowed:
            reasons.append("IPOS_VIDEO_USAGE_NOT_ALLOWED")
        if not self.source_provenance_refs:
            reasons.append("IPOS_SOURCE_PROVENANCE_MISSING")
        eligible_assets = [asset for asset in self.assets if asset.video_eligible]
        if not any(asset.role in PRIMARY_VISUAL_ROLES for asset in eligible_assets):
            reasons.append("IPOS_PRIMARY_VISUAL_REFERENCE_MISSING")
        for asset in self.assets:
            if asset.approved_for_video and not asset.video_eligible:
                reasons.append(f"IPOS_ASSET_NOT_VIDEO_ELIGIBLE:{asset.asset_id}@{asset.version_id}")
        if not self.continuity_dimensions:
            reasons.append("IPOS_CONTINUITY_DIMENSIONS_MISSING")
        if not self.continuity_rules:
            reasons.append("IPOS_CONTINUITY_RULES_MISSING")
        elif set(self.continuity_dimensions) - {
            str(rule["dimension"]) for rule in self.continuity_rules
        }:
            reasons.append("IPOS_CONTINUITY_RULES_INCOMPLETE")
        return IPIdentityReadiness(
            ready=not reasons,
            bundle_ref=self.bundle_ref,
            canon_ref=self.canon_ref,
            reasons=tuple(dict.fromkeys(reasons)),
        )

    def require_video_ready(self) -> None:
        readiness = self.readiness()
        if not readiness.ready:
            raise IPIdentityIntegrationError(
                "IPOS identity is not admissible for identity-dependent video production: "
                + ", ".join(readiness.reasons)
            )


def inspect_ipos_bundle(payload: Mapping[str, Any] | IPIdentityBundle) -> IPIdentityReadiness:
    bundle = payload if isinstance(payload, IPIdentityBundle) else IPIdentityBundle.from_mapping(payload)
    return bundle.readiness()


def _promote_external_asset(
    graph: MediaGraph,
    *,
    ref: AssetRef,
    context_id: str,
    kind: str,
    uri: str,
    digest: str,
    rights_refs: tuple[str, ...],
    consent_refs: tuple[str, ...],
    provenance_refs: tuple[str, ...],
    metadata: Mapping[str, Any],
    observed_at: str,
    evidence_refs: tuple[str, ...],
) -> tuple[bool, tuple[AssetRef, ...]]:
    existing = graph.assets.get(ref)
    if existing is not None:
        if existing.digest != digest:
            raise IPIdentityIntegrationError(
                f"immutable IPOS version digest conflict: {ref.key()}"
            )
        state = graph.asset_state(ref)
        if state == "PROMOTED":
            return False, ()
        if state in {"REJECTED", "RETIRED", "STALE"}:
            raise IPIdentityIntegrationError(
                f"existing IPOS asset cannot be silently resurrected: {ref.key()} ({state})"
            )
    else:
        graph.add_asset(
            AssetVersion(
                ref=ref,
                context_id=context_id,
                kind=kind,
                uri=uri,
                digest=digest,
                state="CANDIDATE",
                rights_refs=rights_refs,
                consent_refs=consent_refs,
                provenance_refs=provenance_refs,
                metadata=dict(metadata),
            )
        )

    previous_version = graph.promoted_versions.get(ref.asset_id)
    evidence_id = f"ipos-import-evidence:{ref.asset_id}:{ref.version_id}"
    if evidence_id not in graph.evidence:
        graph.add_evidence(
            EvidenceRecord(
                evidence_id=evidence_id,
                subject_type="IPOS_ASSET",
                subject_id=ref.key(),
                action="IMPORT_OWNER_APPROVED_IPOS_ASSET",
                refs=evidence_refs,
                observed_at=observed_at,
                metadata=dict(metadata),
            )
        )
    decision_id = f"ipos-import-decision:{ref.asset_id}:{ref.version_id}"
    if decision_id not in graph.decisions:
        graph.add_decision(
            DecisionRecord(
                decision_id=decision_id,
                decision_type="EXTERNAL_CANON_IMPORT",
                owner=IPOS_ISSUER,
                subject_refs=(ref.key(),),
                criteria_refs=("ipos:video-readiness-contract:1.0",),
                evidence_ids=(evidence_id,),
                result="PROMOTE",
                decided_at=observed_at,
                notes="Preserve IPOS as the external canon authority; video imports the exact approved version.",
            )
        )
    graph.promote_asset(ref, decision_id=decision_id)
    invalidated: tuple[AssetRef, ...] = ()
    if previous_version and previous_version != ref.version_id:
        invalidated = graph.invalidate_downstream(
            AssetRef(asset_id=ref.asset_id, version_id=previous_version)
        )
    return True, invalidated


def import_ipos_bundle(
    payload: Mapping[str, Any] | IPIdentityBundle,
    graph: MediaGraph,
    *,
    program_context_id: str,
) -> IPIdentityImportReceipt:
    """Import an approved IPOS bundle as immutable, externally authoritative MediaGraph assets.

    This adapter is local and deterministic. It makes no CAOS, IPOS-server, model-provider,
    image-generation or network call. The caller supplies the exported JSON artifact.
    """

    bundle = payload if isinstance(payload, IPIdentityBundle) else IPIdentityBundle.from_mapping(payload)
    bundle.require_video_ready()
    if program_context_id not in graph.contexts:
        raise IPIdentityIntegrationError(
            f"video Program context does not exist: {program_context_id}"
        )

    bundle_asset_ref = AssetRef(
        asset_id=f"ipos:{bundle.canon_id}:bundle",
        version_id=bundle.bundle_id,
    )
    imported: list[AssetRef] = []
    invalidated: list[AssetRef] = []
    bundle_evidence_refs = tuple(dict.fromkeys(
        (bundle.bundle_ref, bundle.approval_ref, bundle.canon_ref)
        + bundle.source_provenance_refs
    ))
    did_import, stale = _promote_external_asset(
        graph,
        ref=bundle_asset_ref,
        context_id=program_context_id,
        kind="IPOS_IDENTITY_BUNDLE",
        uri=bundle.bundle_uri,
        digest=bundle.digest,
        rights_refs=tuple(dict.fromkeys(asset.rights_ref for asset in bundle.assets if asset.video_eligible)),
        consent_refs=tuple(dict.fromkeys(asset.consent_ref for asset in bundle.assets if asset.video_eligible and asset.consent_ref)),
        provenance_refs=bundle.source_provenance_refs,
        metadata={
            "external_authority": IPOS_ISSUER,
            "bundle_ref": bundle.bundle_ref,
            "canon_ref": bundle.canon_ref,
            "approval_ref": bundle.approval_ref,
            "approval_status": bundle.approval_status,
            "readiness_status": bundle.readiness_status,
            "bundle_digest": bundle.digest,
        },
        observed_at=bundle.issued_at,
        evidence_refs=bundle_evidence_refs,
    )
    if did_import:
        imported.append(bundle_asset_ref)
    invalidated.extend(stale)

    asset_refs: list[AssetRef] = []
    bindings: list[ReferenceBinding] = []
    for asset in bundle.assets:
        if not asset.video_eligible:
            continue
        ref = AssetRef(
            asset_id=f"ipos:{bundle.canon_id}:{asset.asset_id}",
            version_id=asset.version_id,
        )
        asset_refs.append(ref)
        did_import, stale = _promote_external_asset(
            graph,
            ref=ref,
            context_id=program_context_id,
            kind=f"IPOS_{asset.kind.upper()}",
            uri=asset.uri,
            digest=asset.digest,
            rights_refs=(asset.rights_ref,),
            consent_refs=(asset.consent_ref,) if asset.consent_ref else (),
            provenance_refs=asset.provenance_refs,
            metadata={
                "external_authority": IPOS_ISSUER,
                "bundle_ref": bundle.bundle_ref,
                "canon_ref": bundle.canon_ref,
                "approval_ref": bundle.approval_ref,
                "role": asset.role,
                "source_asset_id": asset.asset_id,
                "source_version_id": asset.version_id,
            },
            observed_at=bundle.issued_at,
            evidence_refs=tuple(dict.fromkeys(
                (bundle.bundle_ref, bundle.approval_ref, asset.uri, asset.digest, asset.rights_ref)
                + asset.provenance_refs
                + ((asset.consent_ref,) if asset.consent_ref else ())
            )),
        )
        if did_import:
            imported.append(ref)
        invalidated.extend(stale)
        bindings.append(
            ReferenceBinding(
                asset_id=ref.asset_id,
                version_id=ref.version_id,
                digest=asset.digest,
                role=f"IPOS_{asset.role}",
                rights_ref=asset.rights_ref,
                consent_ref=asset.consent_ref,
            )
        )

    return IPIdentityImportReceipt(
        bundle_ref=bundle.bundle_ref,
        canon_ref=bundle.canon_ref,
        bundle_digest=bundle.digest,
        bundle_asset_ref=bundle_asset_ref,
        asset_refs=tuple(asset_refs),
        reference_bindings=tuple(bindings),
        imported_asset_refs=tuple(dict.fromkeys(imported)),
        invalidated_refs=tuple(dict.fromkeys(invalidated)),
    )


def build_ipos_continuity_rules(
    payload: Mapping[str, Any] | IPIdentityBundle,
) -> tuple[ContinuityRule, ...]:
    bundle = payload if isinstance(payload, IPIdentityBundle) else IPIdentityBundle.from_mapping(payload)
    bundle.require_video_ready()
    return tuple(
        ContinuityRule(
            dimension=str(rule["dimension"]),
            severity=str(rule["severity"]),
            mode=str(rule["mode"]),
            expected_value=rule.get("expected_value"),
            reason=str(rule.get("reason") or ""),
        )
        for rule in bundle.continuity_rules
    )


def build_ipos_continuity_snapshot(
    shot_id: str,
    payload: Mapping[str, Any] | IPIdentityBundle,
) -> ContinuitySnapshot:
    bundle = payload if isinstance(payload, IPIdentityBundle) else IPIdentityBundle.from_mapping(payload)
    bundle.require_video_ready()
    dimensions = {
        "character_canon": bundle.canon_ref,
        **dict(bundle.continuity_dimensions),
    }
    evidence = tuple(dict.fromkeys(
        (bundle.bundle_ref, bundle.approval_ref) + bundle.source_provenance_refs
    ))
    return ContinuitySnapshot(
        shot_id=shot_id,
        dimensions=dimensions,
        canon_refs=(bundle.bundle_ref, bundle.canon_ref),
        evidence_refs=evidence,
    )


def build_ipos_continuity_link(
    from_shot_id: str,
    to_shot_id: str,
    payload: Mapping[str, Any] | IPIdentityBundle,
) -> ContinuityLink:
    bundle = payload if isinstance(payload, IPIdentityBundle) else IPIdentityBundle.from_mapping(payload)
    return ContinuityLink(
        from_shot_id=from_shot_id,
        to_shot_id=to_shot_id,
        rules=build_ipos_continuity_rules(bundle),
        rationale_refs=(bundle.bundle_ref, bundle.approval_ref),
    )


def bind_ipos_identity_to_shot(
    shot: ShotContract,
    payload: Mapping[str, Any] | IPIdentityBundle,
    receipt: IPIdentityImportReceipt,
    *,
    required: bool = True,
) -> ShotContract:
    bundle = payload if isinstance(payload, IPIdentityBundle) else IPIdentityBundle.from_mapping(payload)
    bundle.require_video_ready()
    if receipt.bundle_ref != bundle.bundle_ref or receipt.canon_ref != bundle.canon_ref:
        raise IPIdentityIntegrationError("IPOS import receipt does not match the supplied bundle")
    expected_bindings = tuple(
        ReferenceBinding(
            asset_id=f"ipos:{bundle.canon_id}:{asset.asset_id}",
            version_id=asset.version_id,
            digest=asset.digest,
            role=f"IPOS_{asset.role}",
            rights_ref=asset.rights_ref,
            consent_ref=asset.consent_ref,
        )
        for asset in bundle.assets
        if asset.video_eligible
    )
    imported = {(item.asset_id, item.version_id, item.digest) for item in receipt.reference_bindings}
    if any((item.asset_id, item.version_id, item.digest) not in imported for item in expected_bindings):
        raise IPIdentityIntegrationError("IPOS reference assets were not imported into MediaGraph")

    base_references = tuple(
        item for item in shot.references if not item.role.startswith("IPOS_")
    )
    references_by_identity = {
        (item.asset_id, item.version_id, item.role): item
        for item in base_references + expected_bindings
    }
    references = tuple(references_by_identity.values())
    prior_identity_invariants = set(shot.ip_identity_invariants)
    prior_forbidden_drift = set(shot.ip_identity_forbidden_drift)
    base_must_have = tuple(item for item in shot.must_have if item not in prior_identity_invariants)
    base_must_not_have = tuple(item for item in shot.must_not_have if item not in prior_forbidden_drift)
    must_have = tuple(dict.fromkeys(base_must_have + bundle.identity_invariants))
    must_not_have = tuple(dict.fromkeys(base_must_not_have + bundle.forbidden_drift))
    continuity_ref = "ipos-continuity://" + bundle.canon_id + "@" + bundle.canon_version
    if shot.continuity_ref:
        continuity_ref = shot.continuity_ref + "|" + continuity_ref

    return replace(
        shot,
        references=references,
        must_have=must_have,
        must_not_have=must_not_have,
        continuity_ref=continuity_ref,
        ip_identity_required=required,
        ip_identity_bundle_ref=bundle.bundle_ref,
        ip_identity_approval_ref=bundle.approval_ref,
        ip_identity_invariants=bundle.identity_invariants,
        ip_identity_forbidden_drift=bundle.forbidden_drift,
    )


def admit_ipos_bound_candidate_generation(
    shot: ShotContract,
    payload: Mapping[str, Any] | IPIdentityBundle,
    receipt: IPIdentityImportReceipt,
    **admission_kwargs: Any,
) -> GenerationAdmission:
    """Fail-closed candidate admission for a shot bound to an imported IPOS canon."""

    bundle = payload if isinstance(payload, IPIdentityBundle) else IPIdentityBundle.from_mapping(payload)
    bundle.require_video_ready()
    if receipt.bundle_ref != bundle.bundle_ref or receipt.canon_ref != bundle.canon_ref:
        raise IPIdentityIntegrationError("IPOS import receipt does not match the supplied bundle")
    if not shot.ip_identity_required:
        raise IPIdentityIntegrationError("shot is not marked as requiring IPOS identity")
    if shot.ip_identity_bundle_ref != bundle.bundle_ref:
        raise IPIdentityIntegrationError("shot is bound to a different IPOS bundle")
    if shot.ip_identity_approval_ref != bundle.approval_ref:
        raise IPIdentityIntegrationError("shot is bound to a different IPOS approval")
    expected_bindings = {
        (item.asset_id, item.version_id, item.digest, item.role)
        for item in receipt.reference_bindings
    }
    actual_bindings = {
        (item.asset_id, item.version_id, item.digest, item.role)
        for item in shot.references
        if item.role.startswith("IPOS_")
    }
    if not expected_bindings or not expected_bindings.issubset(actual_bindings):
        raise IPIdentityIntegrationError(
            "shot does not bind every exact imported IPOS reference version"
        )

    return admit_candidate_generation(
        shot,
        ip_identity_approved=True,
        ip_identity_evidence_refs=(bundle.bundle_ref, bundle.approval_ref),
        **admission_kwargs,
    )
