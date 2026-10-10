from __future__ import annotations

from typing import Any, Mapping

from .execution_attestation import canonical_digest


REQUIRED_FIELDS = (
    "narrative_job",
    "before_state",
    "crossing_state",
    "after_state",
    "must_have",
    "must_not_have",
    "benchmark_refs",
    "engine_route",
    "quality_floor",
    "stop_conditions",
    "exact_prompt",
)

CHALLENGE_ROLES = ("art_creative", "red_team")
CHALLENGE_PROOF_FIELDS = (
    "work_order_id",
    "review_receipt_ref",
    "attestation_ref",
    "executor_id",
    "execution_id",
    "provider_run_id",
    "context_id",
    "trace_id",
    "packet_digest",
    "result_digest",
    "brief_digest",
    "proof_ref",
)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def generation_brief_contract(brief: Mapping[str, Any]) -> dict[str, Any]:
    """Return the authoring contract that review evidence must bind to.

    Review verdicts and proof refs are deliberately excluded. They are evidence about the
    brief, not part of the brief being reviewed.
    """

    fields = REQUIRED_FIELDS + ("prompt_blocklist", "literal_forbidden_prompt_terms")
    return {field: brief.get(field) for field in fields if field in brief}


def generation_brief_digest(brief: Mapping[str, Any]) -> str:
    return canonical_digest(generation_brief_contract(brief))


def _verified_challenge_failures(
    brief: Mapping[str, Any],
    verified_challenges: Mapping[str, Mapping[str, Any]] | None,
) -> list[str]:
    """Validate an externally resolved pre-generation review evidence bundle.

    `verified_challenges` must come from the owner runtime/gateway after it resolves durable
    work-order/review/attestation receipts. Keeping this bundle outside the generation brief
    prevents an inline self-authored PASS from becoming authorization by itself.
    """

    if verified_challenges is None:
        return ["verified_pre_generation_review_evidence_missing"]

    failures: list[str] = []
    expected_brief_digest = generation_brief_digest(brief)
    identities: dict[str, dict[str, str]] = {
        field: {} for field in ("execution_id", "provider_run_id", "context_id", "trace_id")
    }

    for role in CHALLENGE_ROLES:
        proof = verified_challenges.get(role)
        if not isinstance(proof, Mapping):
            failures.append(f"verified_pre_generation_review_missing:{role}")
            continue
        if _text(proof.get("decision")).upper() != "PASS":
            failures.append(f"verified_pre_generation_review_not_pass:{role}")
        for field in CHALLENGE_PROOF_FIELDS:
            if not _text(proof.get(field)):
                failures.append(f"verified_pre_generation_review_field_missing:{role}:{field}")
        if _text(proof.get("brief_digest")) and _text(proof.get("brief_digest")) != expected_brief_digest:
            failures.append(f"verified_pre_generation_review_brief_digest_mismatch:{role}")

        for field in identities:
            value = _text(proof.get(field))
            if not value:
                continue
            other_role = identities[field].get(value)
            if other_role is not None:
                failures.append(
                    f"verified_pre_generation_review_identity_reused:{field}:{value}:{other_role},{role}"
                )
            else:
                identities[field][value] = role

    return failures


def generation_brief_failures(
    brief: dict[str, Any],
    *,
    verified_challenges: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[str]:
    """Return fail-closed reasons before a quality-critical generator call.

    This validator proves brief completeness, explicit prompt consistency and the shape/binding
    of review evidence resolved outside the brief. It does not itself resolve receipts or make
    an untrusted provider trusted; that remains the generation gateway/runtime boundary.
    """

    failures: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in brief:
            failures.append(f"missing_field:{field}")

    for field in ("narrative_job", "before_state", "crossing_state", "after_state", "engine_route", "exact_prompt"):
        if field in brief and not _text(brief.get(field)):
            failures.append(f"empty_field:{field}")

    before = _text(brief.get("before_state")).casefold()
    crossing = _text(brief.get("crossing_state")).casefold()
    after = _text(brief.get("after_state")).casefold()
    if before and crossing and before == crossing:
        failures.append("world_state_not_distinct:before=crossing")
    if crossing and after and crossing == after:
        failures.append("world_state_not_distinct:crossing=after")
    if before and after and before == after:
        failures.append("world_state_not_distinct:before=after")

    for field in ("must_have", "must_not_have", "benchmark_refs", "stop_conditions"):
        if field in brief and not _string_list(brief.get(field)):
            failures.append(f"empty_or_invalid_list:{field}")

    quality_floor = brief.get("quality_floor")
    if quality_floor is not None:
        try:
            value = float(quality_floor)
        except (TypeError, ValueError):
            failures.append("invalid_quality_floor")
        else:
            if not 1 <= value <= 5:
                failures.append("quality_floor_out_of_range")

    prompt = _text(brief.get("exact_prompt")).casefold()
    blocklist = _string_list(brief.get("prompt_blocklist", []))
    for term in blocklist:
        if term.casefold() in prompt:
            failures.append(f"prompt_contains_blocked_term:{term}")

    must_not = _string_list(brief.get("must_not_have", []))
    literal_forbidden = _string_list(brief.get("literal_forbidden_prompt_terms", []))
    for term in literal_forbidden:
        if term.casefold() in prompt:
            failures.append(f"prompt_contradicts_must_not_have:{term}")

    if must_not and not blocklist and not literal_forbidden:
        failures.append("no_machine_prompt_blocklist_for_must_not_have")

    # Inline challenge state is useful for humans, but it is never execution proof.
    challenge = brief.get("pre_generation_challenge")
    if not isinstance(challenge, dict):
        failures.append("pre_generation_challenge_missing")
    else:
        for role in CHALLENGE_ROLES:
            item = challenge.get(role)
            if not isinstance(item, dict):
                failures.append(f"pre_generation_challenge_missing:{role}")
                continue
            if _text(item.get("decision")).upper() != "PASS":
                failures.append(f"pre_generation_challenge_not_pass:{role}")
            if not _text(item.get("notes")):
                failures.append(f"pre_generation_challenge_notes_missing:{role}")

    failures.extend(_verified_challenge_failures(brief, verified_challenges))
    return failures


def assert_generation_brief(
    brief: dict[str, Any],
    *,
    verified_challenges: Mapping[str, Mapping[str, Any]] | None = None,
) -> None:
    failures = generation_brief_failures(brief, verified_challenges=verified_challenges)
    if failures:
        raise ValueError("Generation brief blocked: " + "; ".join(failures))
