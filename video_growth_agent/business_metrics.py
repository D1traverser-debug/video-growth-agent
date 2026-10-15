from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


class MetricError(ValueError):
    pass


@dataclass(frozen=True)
class PlatformPerformanceReceipt:
    platform: str
    variant_id: str
    raw_metrics: Mapping[str, float]
    metric_semantics: Mapping[str, str]
    evidence_refs: tuple[str, ...]
    observed_at: str

    def __post_init__(self) -> None:
        if not self.platform.strip() or not self.variant_id.strip() or not self.observed_at.strip():
            raise MetricError("platform, variant_id and observed_at are required")
        if not self.evidence_refs:
            raise MetricError("platform performance requires evidence_refs")
        if set(self.raw_metrics) - set(self.metric_semantics):
            raise MetricError("every raw metric requires declared semantics")
        if any(float(value) < 0 for value in self.raw_metrics.values()):
            raise MetricError("raw metrics cannot be negative")


@dataclass(frozen=True)
class ProductionEconomics:
    published_minutes: float
    cash_cost_usd: float
    creator_minutes: float
    generated_video_seconds: float
    premium_video_seconds: float
    generation_attempts: int
    rejected_generation_attempts: int
    accepted_generated_assets: int
    reused_asset_uses: int = 0

    def __post_init__(self) -> None:
        if self.published_minutes <= 0:
            raise MetricError("published_minutes must be positive")
        numeric = (
            self.cash_cost_usd,
            self.creator_minutes,
            self.generated_video_seconds,
            self.premium_video_seconds,
        )
        if any(value < 0 for value in numeric):
            raise MetricError("production economics cannot be negative")
        integer_values = (
            self.generation_attempts,
            self.rejected_generation_attempts,
            self.accepted_generated_assets,
            self.reused_asset_uses,
        )
        if any(value < 0 for value in integer_values):
            raise MetricError("production counts cannot be negative")
        if self.rejected_generation_attempts > self.generation_attempts:
            raise MetricError("rejected attempts cannot exceed total attempts")
        if self.premium_video_seconds > self.generated_video_seconds:
            raise MetricError("premium seconds cannot exceed generated video seconds")

    @property
    def cost_per_published_minute(self) -> float:
        return self.cash_cost_usd / self.published_minutes

    @property
    def creator_minutes_per_published_minute(self) -> float:
        return self.creator_minutes / self.published_minutes

    @property
    def retry_rejection_rate(self) -> float | None:
        if not self.generation_attempts:
            return None
        return self.rejected_generation_attempts / self.generation_attempts

    @property
    def premium_video_seconds_per_published_minute(self) -> float:
        return self.premium_video_seconds / self.published_minutes


@dataclass(frozen=True)
class CommercialOutcome:
    revenue_usd: float = 0.0
    direct_cost_usd: float = 0.0
    rights_revenue_usd: float = 0.0
    repeat_buy_signal: str = "UNKNOWN"
    brand_outcome_metrics: Mapping[str, float] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.revenue_usd < 0 or self.direct_cost_usd < 0 or self.rights_revenue_usd < 0:
            raise MetricError("commercial values cannot be negative")
        if (self.revenue_usd or self.rights_revenue_usd or self.brand_outcome_metrics) and not self.evidence_refs:
            raise MetricError("observed commercial outcomes require evidence_refs")

    @property
    def gross_margin_usd(self) -> float:
        return self.revenue_usd + self.rights_revenue_usd - self.direct_cost_usd


@dataclass(frozen=True)
class EpisodeOutcomeReceipt:
    episode_id: str
    platform_receipts: tuple[PlatformPerformanceReceipt, ...]
    production: ProductionEconomics
    commercial: CommercialOutcome
    qualitative_evidence_refs: tuple[str, ...] = ()
    learning_candidate_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.episode_id.strip():
            raise MetricError("episode_id is required")

    def derived_metrics(self) -> dict[str, float | None]:
        return {
            "cost_per_published_minute": self.production.cost_per_published_minute,
            "creator_minutes_per_published_minute": self.production.creator_minutes_per_published_minute,
            "retry_rejection_rate": self.production.retry_rejection_rate,
            "premium_video_seconds_per_published_minute": self.production.premium_video_seconds_per_published_minute,
            "commercial_gross_margin_usd": self.commercial.gross_margin_usd,
        }

    def objective_vector(self) -> dict[str, object]:
        """Expose separate outcome classes; intentionally do not collapse to one score."""
        return {
            "platform": [
                {
                    "platform": receipt.platform,
                    "variant_id": receipt.variant_id,
                    "metrics": dict(receipt.raw_metrics),
                    "semantics": dict(receipt.metric_semantics),
                }
                for receipt in self.platform_receipts
            ],
            "production": self.derived_metrics(),
            "commercial": {
                "revenue_usd": self.commercial.revenue_usd,
                "rights_revenue_usd": self.commercial.rights_revenue_usd,
                "gross_margin_usd": self.commercial.gross_margin_usd,
                "repeat_buy_signal": self.commercial.repeat_buy_signal,
                "brand_outcome_metrics": dict(self.commercial.brand_outcome_metrics),
            },
            "qualitative_evidence_refs": self.qualitative_evidence_refs,
            "learning_candidate_refs": self.learning_candidate_refs,
        }
