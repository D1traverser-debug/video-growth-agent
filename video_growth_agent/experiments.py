from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


class ExperimentError(ValueError):
    pass


EXPERIMENT_STATES = {"PLANNED", "RUNNING", "STOPPED", "CONCLUDED"}
OUTCOMES = {"WINNER", "NO_CLEAR_WINNER", "INCONCLUSIVE", "STOPPED_GUARDRAIL"}


@dataclass(frozen=True)
class ExperimentVariant:
    variant_id: str
    artifact_or_plan_ref: str
    changed_variables: Mapping[str, str]
    fixed_variables: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.variant_id.strip() or not self.artifact_or_plan_ref.strip():
            raise ExperimentError("variant identity and artifact_or_plan_ref are required")
        if not self.changed_variables:
            raise ExperimentError("variant requires declared changed_variables")
        if set(self.changed_variables).intersection(self.fixed_variables):
            raise ExperimentError("a variable cannot be both changed and fixed")


@dataclass(frozen=True)
class ExperimentPlan:
    experiment_id: str
    context_id: str
    hypothesis: str
    variants: tuple[ExperimentVariant, ...]
    primary_metric: str
    metric_semantics: Mapping[str, str]
    guardrail_metrics: tuple[str, ...]
    attribution_mode: str
    minimum_observation_rule: str
    stop_rules: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    state: str = "PLANNED"

    def __post_init__(self) -> None:
        if not all(str(value).strip() for value in (self.experiment_id, self.context_id, self.hypothesis, self.primary_metric, self.attribution_mode, self.minimum_observation_rule)):
            raise ExperimentError("experiment identity/context/hypothesis/metric/attribution/observation rule are required")
        if len(self.variants) < 2:
            raise ExperimentError("experiment requires at least two variants")
        ids = [variant.variant_id for variant in self.variants]
        if len(ids) != len(set(ids)):
            raise ExperimentError("variant IDs must be unique")
        if self.primary_metric not in self.metric_semantics:
            raise ExperimentError("primary metric requires declared semantics")
        missing_guardrails = set(self.guardrail_metrics).difference(self.metric_semantics)
        if missing_guardrails:
            raise ExperimentError("guardrail metrics require declared semantics: " + ",".join(sorted(missing_guardrails)))
        if not self.stop_rules:
            raise ExperimentError("experiment requires stop_rules")
        if not self.evidence_refs:
            raise ExperimentError("experiment requires evidence_refs")
        if self.state not in EXPERIMENT_STATES:
            raise ExperimentError(f"unsupported experiment state: {self.state}")

        changed_sets = [frozenset(variant.changed_variables) for variant in self.variants]
        changed_union = set().union(*changed_sets)
        if self.attribution_mode == "SINGLE_VARIABLE_CAUSAL" and len(changed_union) != 1:
            raise ExperimentError("single-variable causal attribution requires exactly one changed variable")


@dataclass(frozen=True)
class VariantObservation:
    variant_id: str
    metrics: Mapping[str, float]
    sample_or_exposure: float
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.variant_id.strip():
            raise ExperimentError("variant observation requires variant_id")
        if self.sample_or_exposure < 0:
            raise ExperimentError("sample_or_exposure cannot be negative")
        if not self.evidence_refs:
            raise ExperimentError("variant observation requires evidence_refs")
        if any(float(value) < 0 for value in self.metrics.values()):
            raise ExperimentError("experiment metrics cannot be negative")


@dataclass(frozen=True)
class ExperimentConclusion:
    experiment_id: str
    outcome: str
    winning_variant_id: str | None
    observations: tuple[VariantObservation, ...]
    evidence_refs: tuple[str, ...]
    inference: str
    followup: str = ""

    def __post_init__(self) -> None:
        if not self.experiment_id.strip() or not self.inference.strip():
            raise ExperimentError("experiment conclusion identity and inference are required")
        if self.outcome not in OUTCOMES:
            raise ExperimentError(f"unsupported experiment outcome: {self.outcome}")
        if self.outcome == "WINNER" and not str(self.winning_variant_id or "").strip():
            raise ExperimentError("WINNER outcome requires winning_variant_id")
        if self.outcome != "WINNER" and self.winning_variant_id is not None:
            raise ExperimentError("non-winner outcome cannot invent a winning variant")
        if not self.observations or not self.evidence_refs:
            raise ExperimentError("experiment conclusion requires observations and evidence")


def conclude_experiment(
    plan: ExperimentPlan,
    *,
    observations: tuple[VariantObservation, ...],
    outcome: str,
    winning_variant_id: str | None,
    evidence_refs: tuple[str, ...],
    inference: str,
    followup: str = "",
) -> ExperimentConclusion:
    expected = {variant.variant_id for variant in plan.variants}
    observed = {item.variant_id for item in observations}
    if expected != observed:
        missing = expected - observed
        extra = observed - expected
        raise ExperimentError(
            "experiment observations do not match variants"
            + (f" missing={','.join(sorted(missing))}" if missing else "")
            + (f" extra={','.join(sorted(extra))}" if extra else "")
        )
    if outcome == "WINNER" and winning_variant_id not in expected:
        raise ExperimentError("winner must be one of the planned variants")
    return ExperimentConclusion(
        experiment_id=plan.experiment_id,
        outcome=outcome,
        winning_variant_id=winning_variant_id,
        observations=observations,
        evidence_refs=evidence_refs,
        inference=inference,
        followup=followup,
    )
