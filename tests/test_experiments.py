import pytest

from video_growth_agent.experiments import (
    ExperimentError,
    ExperimentPlan,
    ExperimentVariant,
    VariantObservation,
    conclude_experiment,
)


def _variant(variant_id: str, **changed):
    return ExperimentVariant(variant_id, f"artifact://{variant_id}", changed_variables=changed)


def test_single_variable_attribution_rejects_multi_variable_change():
    with pytest.raises(ExperimentError, match="exactly one changed variable"):
        ExperimentPlan(
            experiment_id="EXP1",
            context_id="episode-1",
            hypothesis="New packaging improves watch quality",
            variants=(_variant("A", title="old", thumbnail="old"), _variant("B", title="new", thumbnail="new")),
            primary_metric="watch_time",
            metric_semantics={"watch_time": "total watch time from experiment traffic"},
            guardrail_metrics=(),
            attribution_mode="SINGLE_VARIABLE_CAUSAL",
            minimum_observation_rule="platform-declared experiment completion",
            stop_rules=("platform experiment concludes",),
            evidence_refs=("platform://ab-method",),
        )


def test_inconclusive_result_does_not_invent_a_winner():
    plan = ExperimentPlan(
        experiment_id="EXP1",
        context_id="episode-1",
        hypothesis="Thumbnail B improves watch time",
        variants=(_variant("A", thumbnail="old"), _variant("B", thumbnail="new")),
        primary_metric="watch_time",
        metric_semantics={"watch_time": "total watch time from experiment traffic"},
        guardrail_metrics=(),
        attribution_mode="SINGLE_VARIABLE_CAUSAL",
        minimum_observation_rule="platform-declared experiment completion",
        stop_rules=("platform experiment concludes",),
        evidence_refs=("platform://ab-method",),
    )
    observations = (
        VariantObservation("A", {"watch_time": 100.0}, 1000, ("receipt://a",)),
        VariantObservation("B", {"watch_time": 101.0}, 1000, ("receipt://b",)),
    )
    conclusion = conclude_experiment(
        plan,
        observations=observations,
        outcome="NO_CLEAR_WINNER",
        winning_variant_id=None,
        evidence_refs=("platform://conclusion",),
        inference="The platform did not establish a clear winner.",
    )
    assert conclusion.winning_variant_id is None


def test_conclusion_must_cover_every_planned_variant():
    plan = ExperimentPlan(
        experiment_id="EXP1",
        context_id="episode-1",
        hypothesis="Hook B improves retention",
        variants=(_variant("A", hook="old"), _variant("B", hook="new")),
        primary_metric="retention",
        metric_semantics={"retention": "first-30-second retention"},
        guardrail_metrics=(),
        attribution_mode="SINGLE_VARIABLE_CAUSAL",
        minimum_observation_rule="fixed exposure threshold",
        stop_rules=("threshold met",),
        evidence_refs=("experiment://plan",),
    )
    with pytest.raises(ExperimentError, match="observations do not match"):
        conclude_experiment(
            plan,
            observations=(VariantObservation("A", {"retention": 0.5}, 100, ("receipt://a",)),),
            outcome="INCONCLUSIVE",
            winning_variant_id=None,
            evidence_refs=("receipt://experiment",),
            inference="Missing B observation.",
        )
