from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from .resources import data_path


def canonical_digest(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ExecutionAttestation:
    """Auditable identity for one isolated reviewer execution.

    The attestation is not a claim that arbitrary strings are cryptographically trusted.
    It is accepted only when its executor_id is registered in the runtime trust registry.
    Production ships with no trusted executors, so quality-critical blind review fails
    closed until a real provider adapter is connected and registered.
    """

    executor_id: str
    provider: str
    model: str
    execution_id: str
    provider_run_id: str
    context_id: str
    trace_id: str
    packet_digest: str
    result_digest: str
    observed_input_digests: tuple[str, ...]
    isolated_context: bool = True
    sibling_verdicts_visible: bool = False
    group_id: str | None = None
    proof_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["observed_input_digests"] = list(self.observed_input_digests)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ExecutionAttestation":
        data = dict(payload)
        data["observed_input_digests"] = tuple(data.get("observed_input_digests", ()))
        return cls(**data)

    @property
    def digest(self) -> str:
        return canonical_digest(self.to_dict())


class ExecutionTrustRegistry:
    """Fail-closed registry for execution providers allowed to authorize blind review."""

    def __init__(self, config_path: Path | None = None, config: dict[str, Any] | None = None):
        if config is not None:
            self.config = config
            self.path = None
        else:
            self.path = config_path or data_path("executors.json")
            self.config = json.loads(self.path.read_text(encoding="utf-8"))

    @property
    def policy(self) -> dict[str, Any]:
        return self.config.get("policy", {})

    def requires_attestation(self, stage: str, *, blind: bool, task_type: str) -> bool:
        if task_type not in {"review", "meta_review"}:
            return False
        if self.policy.get("blind_reviews_only", True) and not blind:
            return False
        return stage in set(self.policy.get("attestation_required_stages", []))

    def trusted_executor(self, executor_id: str) -> dict[str, Any] | None:
        raw = self.config.get("trusted_executors", {}).get(executor_id)
        return raw if isinstance(raw, dict) else None

    def validate(
        self,
        attestation: ExecutionAttestation,
        *,
        stage: str,
        work_order_id: str,
        packet_digest: str,
        result_digest: str,
        input_digests: dict[str, str | None],
    ) -> list[str]:
        failures: list[str] = []
        executor = self.trusted_executor(attestation.executor_id)
        if executor is None:
            failures.append(f"execution_executor_untrusted:{attestation.executor_id}")
            return failures

        expected_provider = executor.get("provider")
        if expected_provider and attestation.provider != expected_provider:
            failures.append(
                f"execution_provider_mismatch:{attestation.executor_id}:{attestation.provider}!={expected_provider}"
            )
        allowed_models = executor.get("models")
        if isinstance(allowed_models, list) and allowed_models and attestation.model not in allowed_models:
            failures.append(f"execution_model_untrusted:{attestation.executor_id}:{attestation.model}")

        required_strings = {
            "execution_id": attestation.execution_id,
            "provider_run_id": attestation.provider_run_id,
            "context_id": attestation.context_id,
            "trace_id": attestation.trace_id,
            "model": attestation.model,
        }
        for field, value in required_strings.items():
            if not str(value).strip():
                failures.append(f"execution_field_missing:{field}")

        if attestation.packet_digest != packet_digest:
            failures.append("execution_packet_digest_mismatch")
        if attestation.result_digest != result_digest:
            failures.append("execution_result_digest_mismatch")
        if self.policy.get("require_isolated_context", True) and not attestation.isolated_context:
            failures.append("execution_context_not_isolated")
        if self.policy.get("forbid_sibling_verdict_visibility", True) and attestation.sibling_verdicts_visible:
            failures.append("execution_sibling_verdicts_visible")

        required_digests = {digest for digest in input_digests.values() if digest}
        observed = set(attestation.observed_input_digests)
        if self.policy.get("require_all_input_digests_observed", True) and not required_digests.issubset(observed):
            missing = sorted(required_digests - observed)
            failures.append("execution_inputs_not_observed:" + ",".join(missing))

        return failures

    @classmethod
    def test_registry(cls) -> "ExecutionTrustRegistry":
        """Explicit test-only trust boundary; never loaded by production defaults."""
        return cls(
            config={
                "version": "test",
                "policy": {
                    "attestation_required_stages": ["LOOKDEV", "VISUAL_PREVIEW", "ROUGH_CUT", "RELEASE"],
                    "blind_reviews_only": True,
                    "require_isolated_context": True,
                    "forbid_sibling_verdict_visibility": True,
                    "require_unique_execution_id_within_wave": True,
                    "require_unique_provider_run_id_within_wave": True,
                    "require_unique_context_id_within_wave": True,
                    "require_unique_trace_id_within_wave": True,
                    "require_all_input_digests_observed": True,
                },
                "trusted_executors": {
                    "test-executor": {"provider": "test-provider", "models": ["test-model"]}
                },
            }
        )
