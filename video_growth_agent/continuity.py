from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


class ContinuityError(ValueError):
    pass


SEVERITIES = {"HARD", "SOFT"}


@dataclass(frozen=True)
class ContinuitySnapshot:
    shot_id: str
    dimensions: Mapping[str, str]
    canon_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.shot_id.strip():
            raise ContinuityError("shot_id is required")
        if not self.dimensions:
            raise ContinuityError("continuity snapshot requires dimensions")
        for key, value in self.dimensions.items():
            if not str(key).strip() or not str(value).strip():
                raise ContinuityError("continuity dimensions require non-empty keys and values")


@dataclass(frozen=True)
class ContinuityRule:
    dimension: str
    severity: str
    mode: str
    expected_value: str | None = None
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.dimension.strip():
            raise ContinuityError("continuity rule dimension is required")
        if self.severity not in SEVERITIES:
            raise ContinuityError(f"unsupported continuity severity: {self.severity}")
        if self.mode not in {"PRESERVE", "EXPECT", "ALLOW_CHANGE"}:
            raise ContinuityError(f"unsupported continuity rule mode: {self.mode}")
        if self.mode == "EXPECT" and not str(self.expected_value or "").strip():
            raise ContinuityError("EXPECT continuity rule requires expected_value")


@dataclass(frozen=True)
class ContinuityLink:
    from_shot_id: str
    to_shot_id: str
    rules: tuple[ContinuityRule, ...]
    rationale_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.from_shot_id.strip() or not self.to_shot_id.strip():
            raise ContinuityError("continuity link shot identities are required")
        if self.from_shot_id == self.to_shot_id:
            raise ContinuityError("continuity link requires distinct shots")
        if not self.rules:
            raise ContinuityError("continuity link requires at least one rule")
        dimensions = [rule.dimension for rule in self.rules]
        if len(dimensions) != len(set(dimensions)):
            raise ContinuityError("continuity link cannot define a dimension twice")


@dataclass(frozen=True)
class ContinuityViolation:
    dimension: str
    severity: str
    expected: str
    observed: str | None
    reason: str


@dataclass(frozen=True)
class ContinuityAssessment:
    from_shot_id: str
    to_shot_id: str
    violations: tuple[ContinuityViolation, ...]
    evidence_refs: tuple[str, ...] = ()

    @property
    def hard_pass(self) -> bool:
        return not any(item.severity == "HARD" for item in self.violations)


def assess_continuity(
    before: ContinuitySnapshot,
    after: ContinuitySnapshot,
    link: ContinuityLink,
    *,
    evidence_refs: tuple[str, ...] = (),
) -> ContinuityAssessment:
    if before.shot_id != link.from_shot_id or after.shot_id != link.to_shot_id:
        raise ContinuityError("snapshot/link shot identity mismatch")

    violations: list[ContinuityViolation] = []
    for rule in link.rules:
        before_value = before.dimensions.get(rule.dimension)
        after_value = after.dimensions.get(rule.dimension)
        if rule.mode == "ALLOW_CHANGE":
            continue
        if rule.mode == "PRESERVE":
            expected = before_value
            if expected is None:
                violations.append(
                    ContinuityViolation(
                        dimension=rule.dimension,
                        severity=rule.severity,
                        expected="SOURCE_VALUE_REQUIRED",
                        observed=after_value,
                        reason=rule.reason or "source shot omitted a required continuity dimension",
                    )
                )
                continue
        else:
            expected = rule.expected_value
        if after_value != expected:
            violations.append(
                ContinuityViolation(
                    dimension=rule.dimension,
                    severity=rule.severity,
                    expected=str(expected),
                    observed=after_value,
                    reason=rule.reason,
                )
            )

    return ContinuityAssessment(
        from_shot_id=before.shot_id,
        to_shot_id=after.shot_id,
        violations=tuple(violations),
        evidence_refs=tuple(evidence_refs),
    )


@dataclass(frozen=True)
class ContinuityLedger:
    snapshots: tuple[ContinuitySnapshot, ...] = ()
    links: tuple[ContinuityLink, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        snapshot_ids = {item.shot_id for item in self.snapshots}
        if len(snapshot_ids) != len(self.snapshots):
            raise ContinuityError("continuity ledger shot snapshots must be unique")
        for link in self.links:
            if link.from_shot_id not in snapshot_ids or link.to_shot_id not in snapshot_ids:
                raise ContinuityError("continuity link references missing shot snapshot")

    def assess_all(self) -> tuple[ContinuityAssessment, ...]:
        self.validate()
        by_id = {item.shot_id: item for item in self.snapshots}
        return tuple(assess_continuity(by_id[link.from_shot_id], by_id[link.to_shot_id], link) for link in self.links)
