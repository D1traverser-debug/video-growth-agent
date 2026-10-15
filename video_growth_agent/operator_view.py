from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping


class OperatorViewError(ValueError):
    pass


ACTION_STATES = {"READY", "BLOCKED", "WAITING", "OPTIONAL", "DONE"}


@dataclass(frozen=True)
class OperatorAction:
    action_id: str
    label: str
    state: str
    governing_outcome: str
    authority_refs: tuple[str, ...]
    dependency_refs: tuple[str, ...] = ()
    blocker_reasons: tuple[str, ...] = ()
    recovery_refs: tuple[str, ...] = ()
    progress_evidence_expected: tuple[str, ...] = ()
    destructive_or_paid: bool = False

    def __post_init__(self) -> None:
        if not all(str(value).strip() for value in (self.action_id, self.label, self.governing_outcome)):
            raise OperatorViewError("operator action identity/label/outcome are required")
        if self.state not in ACTION_STATES:
            raise OperatorViewError(f"unsupported operator action state: {self.state}")
        if not self.authority_refs:
            raise OperatorViewError("operator action requires authority_refs")
        if self.state == "BLOCKED" and not self.blocker_reasons:
            raise OperatorViewError("blocked operator action requires blocker_reasons")
        if self.state == "READY" and not self.progress_evidence_expected:
            raise OperatorViewError("ready operator action requires expected progress evidence")


@dataclass(frozen=True)
class OperatorSnapshot:
    context_id: str
    governing_outcome: str
    current_focus: str
    authority_refs: tuple[str, ...]
    actions: tuple[OperatorAction, ...]
    pending_decision_refs: tuple[str, ...] = ()
    stale_asset_refs: tuple[str, ...] = ()
    stale_evidence_refs: tuple[str, ...] = ()
    capability_blockers: tuple[str, ...] = ()
    budget_risks: tuple[str, ...] = ()
    resume_refs: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all(str(value).strip() for value in (self.context_id, self.governing_outcome, self.current_focus)):
            raise OperatorViewError("operator snapshot context/outcome/focus are required")
        if not self.authority_refs:
            raise OperatorViewError("operator snapshot requires authority_refs")
        ids = [action.action_id for action in self.actions]
        if len(ids) != len(set(ids)):
            raise OperatorViewError("operator action IDs must be unique")

    @property
    def ready_actions(self) -> tuple[OperatorAction, ...]:
        return tuple(action for action in self.actions if action.state == "READY")

    @property
    def blocked_actions(self) -> tuple[OperatorAction, ...]:
        return tuple(action for action in self.actions if action.state == "BLOCKED")

    def next_action_ids(self) -> tuple[str, ...]:
        """Return all currently admissible actions; do not invent one global next action."""
        return tuple(action.action_id for action in self.ready_actions)

    def recovery_surface(self) -> dict[str, tuple[str, ...]]:
        return {
            "resume_refs": self.resume_refs,
            "capability_blockers": self.capability_blockers,
            "stale_asset_refs": self.stale_asset_refs,
            "stale_evidence_refs": self.stale_evidence_refs,
        }


def derive_operator_snapshot(
    *,
    context_id: str,
    governing_outcome: str,
    current_focus: str,
    authority_refs: Iterable[str],
    actions: Iterable[OperatorAction],
    pending_decision_refs: Iterable[str] = (),
    stale_asset_refs: Iterable[str] = (),
    stale_evidence_refs: Iterable[str] = (),
    capability_blockers: Iterable[str] = (),
    budget_risks: Iterable[str] = (),
    resume_refs: Iterable[str] = (),
    metadata: Mapping[str, str] | None = None,
) -> OperatorSnapshot:
    """Build a non-authoritative projection from current owner state.

    This projection exists to make the current Agent's operating surface legible. It
    never becomes a second controller and cannot promote assets or decisions.
    """

    return OperatorSnapshot(
        context_id=context_id,
        governing_outcome=governing_outcome,
        current_focus=current_focus,
        authority_refs=tuple(str(ref).strip() for ref in authority_refs if str(ref).strip()),
        actions=tuple(actions),
        pending_decision_refs=tuple(pending_decision_refs),
        stale_asset_refs=tuple(stale_asset_refs),
        stale_evidence_refs=tuple(stale_evidence_refs),
        capability_blockers=tuple(capability_blockers),
        budget_risks=tuple(budget_risks),
        resume_refs=tuple(resume_refs),
        metadata=dict(metadata or {}),
    )
