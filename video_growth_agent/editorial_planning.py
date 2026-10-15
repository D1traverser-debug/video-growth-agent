from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

from .production_os import ReferenceBinding, ShotContract


class EditorialPlanningError(ValueError):
    pass


CLAIM_CLASSES = {"FACT", "ANALYSIS", "HYPOTHESIS", "OPINION", "PRODUCT_TRUTH"}
CLAIM_RISKS = {"LOW", "MEDIUM", "HIGH", "BRAND_TRUTH"}
TRUTH_MODES = {"SYNTHETIC", "EDITORIAL_REAL", "PRODUCT_TRUTH", "MIXED_DISCLOSED"}
SHOT_RISKS = {"LOW", "MEDIUM", "HIGH", "HERO", "BRAND_TRUTH"}


def _clean(values: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(str(value).strip() for value in (values or ()) if str(value).strip())


@dataclass(frozen=True)
class EpisodeIntent:
    episode_id: str
    series_id: str
    audience_contract: str
    editorial_question: str
    primary_platform: str
    target_duration_seconds: float
    evidence_refs: tuple[str, ...]
    desired_outcomes: tuple[str, ...]
    success_metric_semantics: Mapping[str, str]
    ip_role: str = "OPTIONAL"
    commercial_context_refs: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("episode_id", "series_id", "audience_contract", "editorial_question", "primary_platform"):
            if not str(getattr(self, name)).strip():
                raise EditorialPlanningError(f"episode intent missing {name}")
        if self.target_duration_seconds <= 0:
            raise EditorialPlanningError("target_duration_seconds must be positive")
        if not self.evidence_refs:
            raise EditorialPlanningError("episode intent requires evidence_refs")
        if not self.desired_outcomes:
            raise EditorialPlanningError("episode intent requires desired_outcomes")
        if not self.success_metric_semantics:
            raise EditorialPlanningError("episode intent requires declared success metric semantics")


@dataclass(frozen=True)
class ClaimSpec:
    claim_id: str
    statement: str
    claim_class: str
    risk: str
    evidence_refs: tuple[str, ...] = ()
    uncertainty: str = ""
    sponsor_related: bool = False

    def __post_init__(self) -> None:
        if not self.claim_id.strip() or not self.statement.strip():
            raise EditorialPlanningError("claim identity and statement are required")
        if self.claim_class not in CLAIM_CLASSES:
            raise EditorialPlanningError(f"unsupported claim_class: {self.claim_class}")
        if self.risk not in CLAIM_RISKS:
            raise EditorialPlanningError(f"unsupported claim risk: {self.risk}")
        if self.claim_class in {"FACT", "PRODUCT_TRUTH"} and not self.evidence_refs:
            raise EditorialPlanningError(f"{self.claim_class} claim requires evidence_refs")
        if self.claim_class == "PRODUCT_TRUTH" and self.risk != "BRAND_TRUTH":
            raise EditorialPlanningError("PRODUCT_TRUTH claims must use BRAND_TRUTH risk")


@dataclass(frozen=True)
class BeatSpec:
    beat_id: str
    episode_id: str
    narrative_job: str
    audience_function: str
    target_duration_seconds: float
    claim_ids: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    tension_or_emotion_job: str = ""
    transition_job: str = ""

    def __post_init__(self) -> None:
        if not all(str(value).strip() for value in (self.beat_id, self.episode_id, self.narrative_job, self.audience_function)):
            raise EditorialPlanningError("beat identity/episode/narrative/audience fields are required")
        if self.target_duration_seconds <= 0:
            raise EditorialPlanningError("beat duration must be positive")
        if self.beat_id in self.depends_on:
            raise EditorialPlanningError("beat cannot depend on itself")


@dataclass(frozen=True)
class ShotIntent:
    shot_id: str
    beat_id: str
    visual_job: str
    target_duration_seconds: float
    truth_mode: str
    risk: str
    source_claim_ids: tuple[str, ...]
    allowed_production_modes: frozenset[str]
    continuity_dimensions: tuple[str, ...] = ()
    reference_intents: tuple[str, ...] = ()
    value_vector: Mapping[str, float] = field(default_factory=dict)
    must_show: tuple[str, ...] = ()
    must_avoid: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.shot_id.strip() or not self.beat_id.strip() or not self.visual_job.strip():
            raise EditorialPlanningError("shot identity/beat/visual_job are required")
        if self.target_duration_seconds <= 0:
            raise EditorialPlanningError("shot duration must be positive")
        if self.truth_mode not in TRUTH_MODES:
            raise EditorialPlanningError(f"unsupported truth_mode: {self.truth_mode}")
        if self.risk not in SHOT_RISKS:
            raise EditorialPlanningError(f"unsupported shot risk: {self.risk}")
        if not self.allowed_production_modes:
            raise EditorialPlanningError("shot requires at least one allowed production mode")
        for name, value in self.value_vector.items():
            if not 0 <= float(value) <= 5:
                raise EditorialPlanningError(f"shot value dimension out of range: {name}={value}")


@dataclass(frozen=True)
class EditorialPlan:
    intent: EpisodeIntent
    claims: tuple[ClaimSpec, ...]
    beats: tuple[BeatSpec, ...]
    shots: tuple[ShotIntent, ...]
    plan_version: str
    derived_from_version: str | None = None
    revision_reason: str = ""

    def __post_init__(self) -> None:
        if not self.plan_version.strip():
            raise EditorialPlanningError("plan_version is required")
        if self.derived_from_version == self.plan_version:
            raise EditorialPlanningError("plan version cannot derive from itself")
        if self.derived_from_version and not self.revision_reason.strip():
            raise EditorialPlanningError("derived editorial plan requires revision_reason")
        self.validate()

    @property
    def plan_ref(self) -> str:
        return f"editorial-plan://{self.intent.episode_id}@{self.plan_version}"

    def validate(self) -> None:
        claims = {item.claim_id: item for item in self.claims}
        beats = {item.beat_id: item for item in self.beats}
        shots = {item.shot_id: item for item in self.shots}
        if len(claims) != len(self.claims) or len(beats) != len(self.beats) or len(shots) != len(self.shots):
            raise EditorialPlanningError("claim/beat/shot IDs must be unique")
        if not beats:
            raise EditorialPlanningError("editorial plan requires at least one beat")
        if not shots:
            raise EditorialPlanningError("editorial plan requires at least one shot")

        for beat in self.beats:
            if beat.episode_id != self.intent.episode_id:
                raise EditorialPlanningError(f"beat episode mismatch: {beat.beat_id}")
            missing_claims = set(beat.claim_ids).difference(claims)
            if missing_claims:
                raise EditorialPlanningError(f"beat references missing claims: {beat.beat_id}:{','.join(sorted(missing_claims))}")
            missing_deps = set(beat.depends_on).difference(beats)
            if missing_deps:
                raise EditorialPlanningError(f"beat dependencies missing: {beat.beat_id}:{','.join(sorted(missing_deps))}")

        self._assert_beat_dag(beats)

        shots_by_beat: dict[str, int] = {beat_id: 0 for beat_id in beats}
        for shot in self.shots:
            if shot.beat_id not in beats:
                raise EditorialPlanningError(f"shot references missing beat: {shot.shot_id}:{shot.beat_id}")
            shots_by_beat[shot.beat_id] += 1
            missing_claims = set(shot.source_claim_ids).difference(claims)
            if missing_claims:
                raise EditorialPlanningError(f"shot references missing claims: {shot.shot_id}:{','.join(sorted(missing_claims))}")
            if shot.truth_mode == "PRODUCT_TRUTH":
                if not any(claims[claim_id].claim_class == "PRODUCT_TRUTH" for claim_id in shot.source_claim_ids):
                    raise EditorialPlanningError("PRODUCT_TRUTH shot must bind at least one PRODUCT_TRUTH claim")
        uncovered = [beat_id for beat_id, count in shots_by_beat.items() if count == 0]
        if uncovered:
            raise EditorialPlanningError("beats without shots: " + ",".join(sorted(uncovered)))

    @staticmethod
    def _assert_beat_dag(beats: Mapping[str, BeatSpec]) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(beat_id: str) -> None:
            if beat_id in visited:
                return
            if beat_id in visiting:
                raise EditorialPlanningError(f"beat dependency cycle detected at {beat_id}")
            visiting.add(beat_id)
            for dep in beats[beat_id].depends_on:
                visit(dep)
            visiting.remove(beat_id)
            visited.add(beat_id)

        for beat_id in beats:
            visit(beat_id)

    def derive(
        self,
        *,
        plan_version: str,
        revision_reason: str,
        intent: EpisodeIntent | None = None,
        claims: tuple[ClaimSpec, ...] | None = None,
        beats: tuple[BeatSpec, ...] | None = None,
        shots: tuple[ShotIntent, ...] | None = None,
    ) -> "EditorialPlan":
        return EditorialPlan(
            intent=intent or self.intent,
            claims=claims if claims is not None else self.claims,
            beats=beats if beats is not None else self.beats,
            shots=shots if shots is not None else self.shots,
            plan_version=plan_version,
            derived_from_version=self.plan_version,
            revision_reason=revision_reason,
        )

    def impact_of_revision(self, newer: "EditorialPlan") -> Mapping[str, tuple[str, ...]]:
        if newer.intent.episode_id != self.intent.episode_id:
            raise EditorialPlanningError("cannot compare plans from different episodes")
        old_claims = {item.claim_id: item for item in self.claims}
        new_claims = {item.claim_id: item for item in newer.claims}
        old_beats = {item.beat_id: item for item in self.beats}
        new_beats = {item.beat_id: item for item in newer.beats}
        old_shots = {item.shot_id: item for item in self.shots}
        new_shots = {item.shot_id: item for item in newer.shots}
        changed_beats = sorted(
            beat_id for beat_id in set(old_beats) | set(new_beats)
            if old_beats.get(beat_id) != new_beats.get(beat_id)
        )
        changed_shots = sorted(
            shot_id for shot_id in set(old_shots) | set(new_shots)
            if old_shots.get(shot_id) != new_shots.get(shot_id)
        )
        changed_claims = sorted(
            claim_id for claim_id in set(old_claims) | set(new_claims)
            if old_claims.get(claim_id) != new_claims.get(claim_id)
        )
        return {
            "changed_claim_ids": tuple(changed_claims),
            "changed_beat_ids": tuple(changed_beats),
            "changed_shot_ids": tuple(changed_shots),
        }

    def shot(self, shot_id: str) -> ShotIntent:
        for shot in self.shots:
            if shot.shot_id == shot_id:
                return shot
        raise EditorialPlanningError(f"shot not found in editorial plan: {shot_id}")


def materialize_shot_contract(
    plan: EditorialPlan,
    *,
    shot_id: str,
    sequence_id: str,
    required_capabilities: frozenset[str],
    quality_targets: Mapping[str, float],
    references: tuple[ReferenceBinding, ...] = (),
    continuity_ref: str = "",
    graceful_degradation: tuple[str, ...] = (),
    stop_conditions: tuple[str, ...] = (),
    budget_usd: float | None = None,
    disclosure_required: bool = False,
) -> ShotContract:
    """Cross the explicit boundary from editorial intent into production execution."""
    shot = plan.shot(shot_id)
    if shot.truth_mode == "PRODUCT_TRUTH" and not references:
        raise EditorialPlanningError("PRODUCT_TRUTH shot cannot materialize without verified references")
    return ShotContract(
        shot_id=shot.shot_id,
        sequence_id=sequence_id,
        narrative_job=shot.visual_job,
        duration_seconds=shot.target_duration_seconds,
        truth_mode=shot.truth_mode,
        risk=shot.risk,
        allowed_modes=shot.allowed_production_modes,
        required_capabilities=required_capabilities,
        quality_targets=quality_targets,
        references=references,
        must_have=shot.must_show,
        must_not_have=shot.must_avoid,
        graceful_degradation=graceful_degradation,
        stop_conditions=stop_conditions,
        budget_usd=budget_usd,
        disclosure_required=disclosure_required,
        editorial_plan_ref=plan.plan_ref,
        beat_id=shot.beat_id,
        source_claim_ids=shot.source_claim_ids,
        continuity_ref=continuity_ref,
        value_vector=shot.value_vector,
    )
