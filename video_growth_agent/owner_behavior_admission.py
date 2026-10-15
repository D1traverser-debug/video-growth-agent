from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

RECOVERY_OUTCOMES = {"RESOLVED", "PROVISIONAL", "UNRESOLVED"}
CLOSURE_TERMINALS = {"REPAIR_EXECUTED", "BLOCKED_WITH_REASON", "NO_CHANGE_WITH_EVIDENCE"}


class BehaviorAdmissionError(RuntimeError):
    pass


def _clean(values: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(value.strip() for value in (values or ()) if isinstance(value, str) and value.strip())


def _present(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


class ProblemLayer(str, Enum):
    LOCAL_IMPLEMENTATION = "LOCAL_IMPLEMENTATION"
    DOMAIN_WORKFLOW = "DOMAIN_WORKFLOW"
    DOMAIN_ARCHITECTURE = "DOMAIN_ARCHITECTURE"
    COMMON_CAPABILITY = "COMMON_CAPABILITY"
    CONTROL_PLANE = "CONTROL_PLANE"
    HOST = "HOST"
    REQUIREMENT_OR_GOAL = "REQUIREMENT_OR_GOAL"


class HypothesisDisposition(str, Enum):
    PLAUSIBLE = "PLAUSIBLE"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class RootScopeHypothesis:
    hypothesis_id: str
    layer: ProblemLayer
    statement: str
    disposition: HypothesisDisposition
    supporting_evidence_refs: tuple[str, ...]
    falsification_or_rejection_refs: tuple[str, ...]


@dataclass(frozen=True)
class RootScopeReceipt:
    selected_hypothesis_id: str
    selected_layer: ProblemLayer
    compared_layers: tuple[ProblemLayer, ...]
    rejected_hypothesis_ids: tuple[str, ...]
    architecture_reassessment_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]


def build_root_scope_receipt(
    *,
    hypotheses: Iterable[RootScopeHypothesis],
    selected_hypothesis_id: str,
    systemic_signal: bool = False,
    architecture_reassessment_refs: Iterable[str] | None = None,
    direct_user_or_external_claim_promoted_without_test: bool = False,
) -> RootScopeReceipt:
    """Build Video-owner evidence that the repair layer was tested, not assumed."""
    items = tuple(hypotheses)
    architecture_refs = _clean(architecture_reassessment_refs)
    if direct_user_or_external_claim_promoted_without_test:
        raise BehaviorAdmissionError(
            "root-scope admission denied: user/external framing was promoted without falsification"
        )
    if not items:
        raise BehaviorAdmissionError("root-scope admission requires hypotheses")
    ids = [item.hypothesis_id.strip() for item in items]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise BehaviorAdmissionError("root-scope hypothesis ids must be non-empty and unique")
    for item in items:
        if not item.statement.strip() or not item.supporting_evidence_refs or not item.falsification_or_rejection_refs:
            raise BehaviorAdmissionError(
                "every root-scope hypothesis requires statement, supporting evidence and falsification/rejection evidence"
            )
    selected = [item for item in items if item.hypothesis_id == selected_hypothesis_id]
    if len(selected) != 1 or selected[0].disposition is not HypothesisDisposition.SELECTED:
        raise BehaviorAdmissionError("selected_hypothesis_id must identify the one SELECTED hypothesis")
    if sum(item.disposition is HypothesisDisposition.SELECTED for item in items) != 1:
        raise BehaviorAdmissionError("exactly one root-scope hypothesis may be SELECTED")

    layers = tuple(sorted({item.layer for item in items}, key=lambda item: item.value))
    rejected = tuple(sorted(item.hypothesis_id for item in items if item.disposition is HypothesisDisposition.REJECTED))
    if systemic_signal:
        if len(items) < 2 or len(layers) < 2:
            raise BehaviorAdmissionError("systemic Video problem requires hypotheses across at least two layers")
        if not rejected:
            raise BehaviorAdmissionError("systemic Video problem requires an evidence-rejected alternative")
        upstream = {
            ProblemLayer.DOMAIN_ARCHITECTURE,
            ProblemLayer.COMMON_CAPABILITY,
            ProblemLayer.CONTROL_PLANE,
            ProblemLayer.HOST,
            ProblemLayer.REQUIREMENT_OR_GOAL,
        }
        if not any(item.layer in upstream for item in items):
            raise BehaviorAdmissionError("systemic Video problem must test an architecture/upstream hypothesis")
        if not architecture_refs:
            raise BehaviorAdmissionError("systemic Video problem requires architecture reassessment evidence")

    chosen = selected[0]
    evidence_refs = tuple(sorted({
        *chosen.supporting_evidence_refs,
        *chosen.falsification_or_rejection_refs,
        *architecture_refs,
    }))
    return RootScopeReceipt(
        selected_hypothesis_id=chosen.hypothesis_id,
        selected_layer=chosen.layer,
        compared_layers=layers,
        rejected_hypothesis_ids=rejected,
        architecture_reassessment_refs=architecture_refs,
        evidence_refs=evidence_refs,
    )


@dataclass(frozen=True)
class VideoRecoveryReceipt:
    project_refs: tuple[str, ...]
    asset_refs: tuple[str, ...]
    work_order_or_decision_refs: tuple[str, ...]
    context_refs: tuple[str, ...]
    external_evidence_refs: tuple[str, ...]
    outcome: str
    unknowns: tuple[str, ...]
    confidence: str
    safe_to_continue: bool

    @property
    def attempted(self) -> bool:
        return bool(
            self.project_refs
            or self.asset_refs
            or self.work_order_or_decision_refs
            or self.context_refs
            or self.external_evidence_refs
        )


def record_recovery_attempt(
    *,
    outcome: str,
    safe_to_continue: bool,
    project_refs: Iterable[str] | None = None,
    asset_refs: Iterable[str] | None = None,
    work_order_or_decision_refs: Iterable[str] | None = None,
    context_refs: Iterable[str] | None = None,
    external_evidence_refs: Iterable[str] | None = None,
    unknowns: Iterable[str] | None = None,
    confidence: str = "UNSPECIFIED",
) -> VideoRecoveryReceipt:
    if outcome not in RECOVERY_OUTCOMES:
        raise BehaviorAdmissionError(f"invalid recovery outcome: {outcome}")
    receipt = VideoRecoveryReceipt(
        project_refs=_clean(project_refs),
        asset_refs=_clean(asset_refs),
        work_order_or_decision_refs=_clean(work_order_or_decision_refs),
        context_refs=_clean(context_refs),
        external_evidence_refs=_clean(external_evidence_refs),
        outcome=outcome,
        unknowns=_clean(unknowns),
        confidence=confidence.strip() if isinstance(confidence, str) else "UNSPECIFIED",
        safe_to_continue=bool(safe_to_continue),
    )
    if not receipt.attempted:
        raise BehaviorAdmissionError("recovery receipt has no inspected Video evidence source")
    if outcome == "UNRESOLVED" and not receipt.unknowns:
        raise BehaviorAdmissionError("UNRESOLVED recovery requires concrete unknowns")
    if outcome in {"RESOLVED", "PROVISIONAL"} and not safe_to_continue:
        raise BehaviorAdmissionError(f"{outcome} cannot be unsafe to continue")
    return receipt


def require_user_escalation_admission(
    receipt: VideoRecoveryReceipt | None,
    *,
    explicit_user_confirmation: bool = False,
    requires_user_fact_authorization_or_preference: bool = False,
) -> str:
    if explicit_user_confirmation:
        return "ADMITTED_EXPLICIT_USER_CONFIRMATION"
    if receipt is None or not receipt.attempted:
        raise BehaviorAdmissionError("user escalation denied: no Video recovery receipt")
    if receipt.outcome in {"RESOLVED", "PROVISIONAL"} and receipt.safe_to_continue:
        raise BehaviorAdmissionError("user escalation denied: safe owner path remains available")
    if requires_user_fact_authorization_or_preference and receipt.outcome == "UNRESOLVED":
        return "ADMITTED_REQUIRED_USER_FACT_AUTHORIZATION_OR_PREFERENCE"
    if receipt.outcome == "UNRESOLVED" and receipt.unknowns and not receipt.safe_to_continue:
        return "ADMITTED_UNRESOLVED_AFTER_RECOVERY"
    raise BehaviorAdmissionError("user escalation denied: blocker conditions are not satisfied")


def _require_cognition_and_evolution(
    *,
    root_scope_receipt: RootScopeReceipt | None,
    evolution_disposition: str | None,
    problem_record_required: bool,
    problem_record_ref: str | None,
) -> None:
    if root_scope_receipt is None:
        raise BehaviorAdmissionError("problem action denied: root-scope cognition receipt is missing")
    if not _present(evolution_disposition):
        raise BehaviorAdmissionError("problem action denied: evolution/learning disposition is missing")
    if problem_record_required and not _present(problem_record_ref):
        raise BehaviorAdmissionError("material/evolution-relevant Video problem requires durable problem evidence")


def finalize_problem_closure(
    *,
    problem_detected: bool,
    repair_path_available: bool,
    authority_permits_repair: bool,
    explicit_user_choice_required: bool,
    repair_attempted: bool,
    repair_succeeded: bool,
    blocker_reason: str | None = None,
    no_change_evidence: Iterable[str] | None = None,
    root_scope_receipt: RootScopeReceipt | None = None,
    evolution_disposition: str | None = None,
    problem_record_required: bool = False,
    problem_record_ref: str | None = None,
) -> str:
    if not problem_detected:
        return "CLEAN_NO_PROBLEM"

    blocker = blocker_reason.strip() if isinstance(blocker_reason, str) else ""
    evidence = _clean(no_change_evidence)

    if blocker and (explicit_user_choice_required or not authority_permits_repair or not repair_path_available):
        if problem_record_required and not _present(problem_record_ref):
            raise BehaviorAdmissionError("material blocked Video problem requires durable problem evidence")
        return "BLOCKED_WITH_REASON"

    if repair_path_available and authority_permits_repair and not explicit_user_choice_required:
        _require_cognition_and_evolution(
            root_scope_receipt=root_scope_receipt,
            evolution_disposition=evolution_disposition,
            problem_record_required=problem_record_required,
            problem_record_ref=problem_record_ref,
        )
        if not repair_attempted:
            raise BehaviorAdmissionError(
                "problem closure denied: cognitively-admitted authorized Video repair exists but was not attempted"
            )
        if repair_succeeded:
            return "REPAIR_EXECUTED"
        if blocker:
            return "BLOCKED_WITH_REASON"
        raise BehaviorAdmissionError(
            "problem closure denied: failed repair requires concrete blocker or further repair"
        )

    if evidence:
        _require_cognition_and_evolution(
            root_scope_receipt=root_scope_receipt,
            evolution_disposition=evolution_disposition,
            problem_record_required=problem_record_required,
            problem_record_ref=problem_record_ref,
        )
        return "NO_CHANGE_WITH_EVIDENCE"
    raise BehaviorAdmissionError("problem closure denied: no valid cognitively-admitted terminal evidence")
