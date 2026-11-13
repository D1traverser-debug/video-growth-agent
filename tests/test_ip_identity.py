from __future__ import annotations

from video_growth_agent.continuity import ContinuityRule
from video_growth_agent.ip_identity import (
    IPIdentityIntegrationError,
    admit_ipos_bound_candidate_generation,
    bind_ipos_identity_to_shot,
    build_ipos_continuity_link,
    build_ipos_continuity_rules,
    build_ipos_continuity_snapshot,
    import_ipos_bundle,
    inspect_ipos_bundle,
)
from video_growth_agent.media_graph import (
    AssetRef,
    AssetVersion,
    ContextRecord,
    MediaGraph,
)
from video_growth_agent.production_os import (
    ShotContract,
    admit_candidate_generation,
)


def _bundle(
    *,
    canon_version: str = "v1",
    asset_version: str = "v1",
    approval_status: str = "OWNER_APPROVED",
    readiness_status: str = "READY_FOR_VIDEO",
    g2: str = "PASS",
) -> dict:
    return {
        "schema_version": "1.0",
        "issuer": "IP_STUDIO_OS",
        "bundle_id": f"creator-character-{canon_version}",
        "project_id": "personal-ip-creation",
        "issued_at": "2026-11-13T12:00:00+08:00",
        "canon": {
            "canon_id": "creator-character",
            "version": canon_version,
            "carrier": "ORIGINAL_CHARACTER",
            "identity_thesis": "A distinctive, owner-approved character identity.",
            "identity_invariants": ["preserve the approved silhouette", "preserve face construction"],
            "allowed_variations": ["expression may change within the approved range"],
            "forbidden_drift": ["do not replace the identity with a generic portrait"],
        },
        "approval": {
            "status": approval_status,
            "approval_ref": "owner-approval://canon-v1",
            "approved_at": "2026-11-13T11:55:00+08:00",
        },
        "readiness": {
            "status": readiness_status,
            "gates": {"G2": g2, "G7": "PASS", "G8": "PASS"},
        },
        "usage": {
            "video_allowed": True,
            "usage_constraints": ["organic creator video"],
        },
        "assets": [
            {
                "asset_id": "hero-reference",
                "version_id": asset_version,
                "kind": "IMAGE",
                "role": "PRIMARY_VISUAL_REFERENCE",
                "uri": f"asset://ipos/hero-reference/{asset_version}.png",
                "digest": "sha256:" + (asset_version[-1].lower() * 64),
                "state": "PROMOTED",
                "approved_for_video": True,
                "rights_ref": "rights://owner/character",
                "consent_ref": None,
                "requires_consent": False,
                "provenance_refs": ["ipos-source://design-ledger/R39"],
            },
            {
                "asset_id": "turnaround",
                "version_id": asset_version,
                "kind": "IMAGE_SET",
                "role": "TURNAROUND_SHEET",
                "uri": f"asset://ipos/turnaround/{asset_version}",
                "digest": "sha256:" + (asset_version[-1].lower() * 64),
                "state": "PROMOTED",
                "approved_for_video": True,
                "rights_ref": "rights://owner/character",
                "consent_ref": None,
                "requires_consent": False,
                "provenance_refs": ["ipos-source://design-ledger/R39"],
            },
        ],
        "continuity": {
            "dimensions": {
                "silhouette": "approved silhouette v1",
                "face_geometry": "approved face geometry v1",
                "palette": "approved restrained palette v1",
            },
            "rules": [
                {
                    "dimension": "silhouette",
                    "severity": "HARD",
                    "mode": "PRESERVE",
                    "reason": "Silhouette is an identity anchor.",
                },
                {
                    "dimension": "face_geometry",
                    "severity": "HARD",
                    "mode": "PRESERVE",
                    "reason": "Do not drift facial construction.",
                },
                {
                    "dimension": "palette",
                    "severity": "SOFT",
                    "mode": "EXPECT",
                    "expected_value": "approved restrained palette v1",
                    "reason": "Allow lighting variation without changing canon.",
                },
            ],
        },
        "source_provenance_refs": ["ipos-source://owner-brief/R39"],
        "bundle_uri": f"ipos://exports/creator-character/{canon_version}.json",
    }


def _graph() -> MediaGraph:
    graph = MediaGraph()
    graph.add_context(ContextRecord("program", "PROGRAM"))
    graph.add_context(ContextRecord("episode", "EPISODE", "program"))
    graph.add_context(ContextRecord("sequence", "SEQUENCE", "episode"))
    graph.add_context(ContextRecord("shot", "SHOT", "sequence"))
    return graph


def _shot(**overrides) -> ShotContract:
    values = {
        "shot_id": "SHOT-001",
        "sequence_id": "SEQ-001",
        "narrative_job": "Introduce the recurring creator character.",
        "duration_seconds": 4.0,
        "truth_mode": "SYNTHETIC",
        "risk": "HERO",
        "allowed_modes": frozenset({"I2V", "T2V"}),
        "required_capabilities": frozenset({"I2V"}),
        "quality_targets": {"identity": 4.0, "motion": 3.5},
        "budget_usd": 5.0,
    }
    values.update(overrides)
    return ShotContract(**values)


def _admission_kwargs() -> dict:
    return {
        "lane": "PRODUCTION",
        "provider_id": "provider/model",
        "route_evidence_refs": ["route://approved"],
        "rights_evidence_refs": ["rights://approved"],
        "capability_evidence_refs": ["capability://available"],
        "budget_evidence_refs": ["budget://within-limit"],
        "provider_available": True,
        "commercial_use_admitted": True,
        "within_budget": True,
        "required_reference_rights_satisfied": True,
    }


def test_unapproved_or_unpassed_ipos_canon_is_not_video_ready():
    candidate = _bundle(approval_status="NOT_APPROVED")
    readiness = inspect_ipos_bundle(candidate)
    assert readiness.ready is False
    assert "IPOS_CANON_NOT_OWNER_APPROVED" in readiness.reasons

    failed_gate = _bundle(g2="OPEN")
    readiness = inspect_ipos_bundle(failed_gate)
    assert readiness.ready is False
    assert "IPOS_GATE_NOT_PASSED:G2" in readiness.reasons

    graph = _graph()
    try:
        import_ipos_bundle(candidate, graph, program_context_id="program")
    except IPIdentityIntegrationError as exc:
        assert "not admissible" in str(exc)
    else:
        raise AssertionError("unapproved IPOS canon must not be imported")


def test_approved_bundle_imports_exact_assets_and_is_idempotent():
    graph = _graph()
    bundle = _bundle()
    receipt = import_ipos_bundle(bundle, graph, program_context_id="program")

    assert receipt.bundle_ref == "ipos://creator-character-v1@v1"
    assert receipt.canon_ref == "ipos://creator-character@v1"
    assert len(receipt.asset_refs) == 2
    assert all(graph.asset_state(ref) == "PROMOTED" for ref in receipt.asset_refs)
    assert graph.asset_state(receipt.bundle_asset_ref) == "PROMOTED"
    assert all(graph.assets[ref].metadata["external_authority"] == "IP_STUDIO_OS" for ref in receipt.asset_refs)
    assert len(receipt.reference_bindings) == 2

    repeated = import_ipos_bundle(bundle, graph, program_context_id="program")
    assert repeated.imported_asset_refs == ()
    assert repeated.asset_refs == receipt.asset_refs
    assert repeated.bundle_digest == receipt.bundle_digest


def test_new_ipos_canon_version_invalidates_only_downstream_assets_of_old_version():
    graph = _graph()
    first = import_ipos_bundle(_bundle(), graph, program_context_id="program")
    old_primary = next(ref for ref in first.asset_refs if ref.asset_id.endswith(":hero-reference"))
    derived = AssetRef("shot-keyframe", "v1")
    graph.add_asset(
        AssetVersion(
            ref=derived,
            context_id="shot",
            kind="IMAGE",
            uri="asset://shot/keyframe-v1",
            digest="sha256:" + "f" * 64,
            derived_from=(old_primary,),
        )
    )

    second = import_ipos_bundle(
        _bundle(canon_version="v2", asset_version="v2"),
        graph,
        program_context_id="program",
    )
    assert old_primary in graph.assets
    assert graph.asset_state(old_primary) == "STALE"
    assert derived in second.invalidated_refs
    assert graph.asset_state(derived) == "STALE"
    assert any(ref.version_id == "v2" for ref in second.asset_refs)


def test_shot_binding_and_generation_admission_require_ipos_owner_evidence():
    bundle = _bundle()
    graph = _graph()
    receipt = import_ipos_bundle(bundle, graph, program_context_id="program")
    shot = bind_ipos_identity_to_shot(_shot(), bundle, receipt, required=True)

    assert shot.ip_identity_required is True
    assert shot.ip_identity_bundle_ref == receipt.bundle_ref
    assert shot.ip_identity_approval_ref == "owner-approval://canon-v1"
    assert len([ref for ref in shot.references if ref.role.startswith("IPOS_")]) == 2
    assert "preserve the approved silhouette" in shot.must_have
    assert "do not replace the identity with a generic portrait" in shot.must_not_have

    bypass = admit_candidate_generation(
        shot,
        **_admission_kwargs(),
    )
    assert bypass.admitted is False
    assert "IPOS_IDENTITY_NOT_OWNER_APPROVED" in bypass.reasons
    assert "IPOS_BUNDLE_EVIDENCE_MISSING" in bypass.reasons
    assert "IPOS_OWNER_APPROVAL_EVIDENCE_MISSING" in bypass.reasons

    admitted = admit_ipos_bound_candidate_generation(
        shot,
        bundle,
        receipt,
        **_admission_kwargs(),
    )
    assert admitted.admitted is True
    assert admitted.ip_identity_evidence_refs == (
        receipt.bundle_ref,
        "owner-approval://canon-v1",
    )


def test_ipos_continuity_contract_maps_to_video_dimension_rules():
    bundle = _bundle()
    rules = build_ipos_continuity_rules(bundle)
    assert len(rules) == 3
    assert isinstance(rules[0], ContinuityRule)
    assert rules[0].dimension == "silhouette"
    assert rules[0].severity == "HARD"

    snapshot = build_ipos_continuity_snapshot("SHOT-001", bundle)
    assert snapshot.dimensions["character_canon"] == "ipos://creator-character@v1"
    assert snapshot.canon_refs == (
        "ipos://creator-character-v1@v1",
        "ipos://creator-character@v1",
    )

    link = build_ipos_continuity_link("SHOT-001", "SHOT-002", bundle)
    assert link.from_shot_id == "SHOT-001"
    assert link.to_shot_id == "SHOT-002"
    assert link.rules == rules


def test_identity_independent_shots_remain_unblocked():
    admission = admit_candidate_generation(
        _shot(ip_identity_required=False),
        **_admission_kwargs(),
    )
    assert admission.admitted is True
    assert admission.ip_identity_evidence_refs == ()

def test_rebinding_shot_replaces_old_ipos_references_and_identity_rules():
    graph = _graph()
    first_bundle = _bundle()
    first_receipt = import_ipos_bundle(first_bundle, graph, program_context_id="program")
    first_shot = bind_ipos_identity_to_shot(_shot(), first_bundle, first_receipt, required=True)

    second_bundle = _bundle(canon_version="v2", asset_version="v2")
    second_bundle["approval"]["approval_ref"] = "owner-approval://canon-v2"
    second_bundle["canon"]["identity_invariants"] = ["new canon invariant"]
    second_bundle["canon"]["forbidden_drift"] = ["new forbidden drift"]
    second_receipt = import_ipos_bundle(second_bundle, graph, program_context_id="program")
    rebound = bind_ipos_identity_to_shot(
        first_shot,
        second_bundle,
        second_receipt,
        required=True,
    )

    assert all(reference.version_id == "v2" for reference in rebound.references if reference.role.startswith("IPOS_"))
    assert "preserve the approved silhouette" not in rebound.must_have
    assert "new canon invariant" in rebound.must_have
    assert "do not replace the identity with a generic portrait" not in rebound.must_not_have
    assert "new forbidden drift" in rebound.must_not_have
    assert rebound.ip_identity_bundle_ref == second_receipt.bundle_ref
    assert rebound.ip_identity_approval_ref == "owner-approval://canon-v2"

def test_identity_generation_admission_rejects_incomplete_reference_binding():
    bundle = _bundle()
    graph = _graph()
    receipt = import_ipos_bundle(bundle, graph, program_context_id="program")
    shot = bind_ipos_identity_to_shot(_shot(), bundle, receipt, required=True)
    one_reference_missing = shot.__class__(
        **{
            **shot.__dict__,
            "references": shot.references[:-1],
        }
    )

    try:
        admit_ipos_bound_candidate_generation(
            one_reference_missing,
            bundle,
            receipt,
            **_admission_kwargs(),
        )
    except IPIdentityIntegrationError as exc:
        assert "every exact imported IPOS reference version" in str(exc)
    else:
        raise AssertionError("all imported IPOS reference versions must be bound")
