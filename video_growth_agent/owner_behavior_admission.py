from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

RECOVERY_OUTCOMES = {"RESOLVED", "PROVISIONAL", "UNRESOLVED"}
CLOSURE_TERMINALS = {"REPAIR_EXECUTED", "BLOCKED_WITH_REASON", "NO_CHANGE_WITH_EVIDENCE"}


class BehaviorAdmissionError(RuntimeError):
    pass


def _clean(values: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(value.strip() for value in (values or ()) if isinstance(value, str) and value.strip())


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
) -> str:
    if not problem_detected:
        return "CLEAN_NO_PROBLEM"

    blocker = blocker_reason.strip() if isinstance(blocker_reason, str) else ""
    evidence = _clean(no_change_evidence)

    if repair_path_available and authority_permits_repair and not explicit_user_choice_required:
        if not repair_attempted:
            raise BehaviorAdmissionError(
                "problem closure denied: authorized Video repair exists but was not attempted"
            )
        if repair_succeeded:
            return "REPAIR_EXECUTED"
        if blocker:
            return "BLOCKED_WITH_REASON"
        raise BehaviorAdmissionError(
            "problem closure denied: failed repair requires concrete blocker or further repair"
        )

    if blocker and (explicit_user_choice_required or not authority_permits_repair or not repair_path_available):
        return "BLOCKED_WITH_REASON"
    if evidence:
        return "NO_CHANGE_WITH_EVIDENCE"
    raise BehaviorAdmissionError("problem closure denied: no valid terminal evidence")
