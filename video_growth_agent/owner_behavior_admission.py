from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

RECOVERY_OUTCOMES = {"RESOLVED", "PROVISIONAL", "UNRESOLVED"}
CLOSURE_TERMINALS = {"REPAIR_EXECUTED", "BLOCKED_WITH_REASON", "NO_CHANGE_WITH_EVIDENCE"}


class BehaviorAdmissionError(RuntimeError):
    pass


class ProblemLayer(str, Enum):
    ASSET_OR_TOOL = "ASSET_OR_TOOL"
    WORK_ORDER_OR_EDITORIAL_WORKFLOW = "WORK_ORDER_OR_EDITORIAL_WORKFLOW"
    MEDIA_BUSINESS_ARCHITECTURE = "MEDIA_BUSINESS_ARCHITECTURE"
    COMMON_CAPABILITY = "COMMON_CAPABILITY"
    PARENT_CONTROL_PLANE = "PARENT_CONTROL_PLANE"
    HOST = "HOST"
    REQUIREMENT_OR_GOAL = "REQUIREMENT_OR_GOAL"


class HypothesisDisposition(str, Enum):
    PLAUSIBLE = "PLAUSIBLE"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"


class EvolutionDisposition(str, Enum):
    LOCAL_LEARNING_ONLY = "LOCAL_LEARNING_ONLY"
    NO_DURABLE_EVOLUTION_WITH_EVIDENCE = "NO_DURABLE_EVOLUTION_WITH_EVIDENCE"
    DOMAIN_EVOLUTION_CANDIDATE = "DOMAIN_EVOLUTION_CANDIDATE"
    DOMAIN_EVOLUTION_UPDATED = "DOMAIN_EVOLUTION_UPDATED"
    PARENT_OR_COMMON_UPCALL = "PARENT_OR_COMMON_UPCALL"


@dataclass(frozen=True)
class RootScopeHypothesis:
    hypothesis_id: str
    layer: ProblemLayer
    statement: str
    disposition: HypothesisDisposition
    supporting_evidence_refs: tuple[str, ...]
    falsification_or_rejection_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip() or not self.statement.strip():
            raise ValueError("root-scope hypothesis requires identity and statement")
        if not self.supporting_evidence_refs or not self.falsification_or_rejection_refs:
            raise ValueError("root-scope hypothesis requires support and falsification/rejection evidence")


@dataclass(frozen=True)
class RootScopeReceipt:
    selected_hypothesis_id: str
    selected_layer: ProblemLayer
    compared_layers: tuple[ProblemLayer, ...]
    hypothesis_count: int
    architecture_reassessment_performed: bool
    current_agent_dogfood_bound: bool
    durable_problem_record_required: bool
    evidence_refs: tuple[str, ...]


_UPSTREAM_LAYERS = {
    ProblemLayer.MEDIA_BUSINESS_ARCHITECTURE,
    ProblemLayer.COMMON_CAPABILITY,
    ProblemLayer.PARENT_CONTROL_PLANE,
    ProblemLayer.HOST,
    ProblemLayer.REQUIREMENT_OR_GOAL,
}


def _clean(values: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(value.strip() for value in (values or ()) if isinstance(value, str) and value.strip())


def require_root_scope_admission(
    *,
    hypotheses: tuple[RootScopeHypothesis, ...],
    selected_hypothesis_id: str,
    material_problem: bool = False,
    repeated_failure: bool = False,
    cross_subsystem: bool = False,
    architecture_gap: bool = False,
    complexity_growth: bool = False,
    scope_expansion: bool = False,
    architecture_reassessment_refs: Iterable[str] | None = None,
    current_agent_dogfood_refs: Iterable[str] | None = None,
    direct_user_or_external_claim_promoted_without_test: bool = False,
) -> RootScopeReceipt:
    """Admit Video problem action only after an evidence-tested causal layer exists.

    Material/systemic Video problems bind current media-business/agent-operability
    evidence so the architecture is evaluated as used, not only as described.
    """

    if direct_user_or_external_claim_promoted_without_test:
        raise BehaviorAdmissionError(
            "root-scope admission denied: user/external framing was promoted without falsification"
        )
    if not hypotheses:
        raise BehaviorAdmissionError("root-scope admission requires hypotheses")
    if len({h.hypothesis_id for h in hypotheses}) != len(hypotheses):
        raise BehaviorAdmissionError("root-scope hypothesis identifiers must be unique")

    selected = [h for h in hypotheses if h.hypothesis_id == selected_hypothesis_id]
    if len(selected) != 1 or selected[0].disposition is not HypothesisDisposition.SELECTED:
        raise BehaviorAdmissionError("exactly one SELECTED hypothesis must match selected_hypothesis_id")
    if sum(h.disposition is HypothesisDisposition.SELECTED for h in hypotheses) != 1:
        raise BehaviorAdmissionError("exactly one root-scope hypothesis may be SELECTED")

    systemic = any((material_problem, repeated_failure, cross_subsystem, architecture_gap, complexity_growth, scope_expansion))
    architecture_refs = _clean(architecture_reassessment_refs)
    dogfood_refs = _clean(current_agent_dogfood_refs)
    compared_layers = tuple(sorted({h.layer for h in hypotheses}, key=lambda layer: layer.value))
    if systemic:
        if len(hypotheses) < 2 or len(compared_layers) < 2:
            raise BehaviorAdmissionError("systemic/material problem requires competing hypotheses across at least two layers")
        if not any(h.disposition is HypothesisDisposition.REJECTED for h in hypotheses):
            raise BehaviorAdmissionError("systemic/material problem requires an evidence-rejected alternative")
        if not any(h.layer in _UPSTREAM_LAYERS for h in hypotheses):
            raise BehaviorAdmissionError("systemic/material problem must test an architecture/upstream hypothesis")
        if not architecture_refs:
            raise BehaviorAdmissionError("systemic/material problem requires architecture/upstream reassessment evidence")
        if not dogfood_refs:
            raise BehaviorAdmissionError("systemic/material Video problem requires current-agent operability/dogfood evidence")

    chosen = selected[0]
    refs = tuple(sorted({*chosen.supporting_evidence_refs, *chosen.falsification_or_rejection_refs, *architecture_refs, *dogfood_refs}))
    return RootScopeReceipt(
        selected_hypothesis_id=chosen.hypothesis_id,
        selected_layer=chosen.layer,
        compared_layers=compared_layers,
        hypothesis_count=len(hypotheses),
        architecture_reassessment_performed=bool(architecture_refs),
        current_agent_dogfood_bound=bool(dogfood_refs),
        durable_problem_record_required=systemic,
        evidence_refs=refs,
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
        return bool(self.project_refs or self.asset_refs or self.work_order_or_decision_refs or self.context_refs or self.external_evidence_refs)


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
    evolution_disposition: EvolutionDisposition | None = None,
    durable_problem_ref: str | None = None,
) -> str:
    if not problem_detected:
        return "CLEAN_NO_PROBLEM"

    blocker = blocker_reason.strip() if isinstance(blocker_reason, str) else ""
    evidence = _clean(no_change_evidence)

    if explicit_user_choice_required and blocker:
        return "BLOCKED_WITH_REASON"

    if root_scope_receipt is None:
        raise BehaviorAdmissionError("problem closure denied: root-scope admission is missing")
    if not isinstance(evolution_disposition, EvolutionDisposition):
        raise BehaviorAdmissionError("problem closure denied: typed evolution disposition is missing")
    durable_required = bool(
        root_scope_receipt.durable_problem_record_required
        or evolution_disposition in {
            EvolutionDisposition.DOMAIN_EVOLUTION_CANDIDATE,
            EvolutionDisposition.DOMAIN_EVOLUTION_UPDATED,
            EvolutionDisposition.PARENT_OR_COMMON_UPCALL,
        }
    )
    if durable_required and not (isinstance(durable_problem_ref, str) and durable_problem_ref.strip()):
        raise BehaviorAdmissionError("problem closure denied: material/evolution-relevant problem requires durable causal evidence")

    if repair_path_available and authority_permits_repair:
        if not repair_attempted:
            raise BehaviorAdmissionError("problem closure denied: admitted authorized Video repair exists but was not attempted")
        if repair_succeeded:
            return "REPAIR_EXECUTED"
        if blocker:
            return "BLOCKED_WITH_REASON"
        raise BehaviorAdmissionError("problem closure denied: failed repair requires concrete blocker or further repair")

    if blocker and (not authority_permits_repair or not repair_path_available):
        return "BLOCKED_WITH_REASON"
    if evidence:
        return "NO_CHANGE_WITH_EVIDENCE"
    raise BehaviorAdmissionError("problem closure denied: no valid terminal evidence")
