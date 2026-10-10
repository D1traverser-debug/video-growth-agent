from __future__ import annotations

from typing import Any


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


def _text(value: Any) -> str:
    return str(value or "").strip()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def generation_brief_failures(brief: dict[str, Any]) -> list[str]:
    """Return fail-closed reasons before a quality-critical generator call.

    The validator is intentionally conservative. It proves basic contract completeness and
    catches explicit prompt contradictions. It does not replace Art/Creative/Red-Team review.
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

    challenge = brief.get("pre_generation_challenge")
    if not isinstance(challenge, dict):
        failures.append("pre_generation_challenge_missing")
    else:
        for role in ("art_creative", "red_team"):
            item = challenge.get(role)
            if not isinstance(item, dict):
                failures.append(f"pre_generation_challenge_missing:{role}")
                continue
            if _text(item.get("decision")).upper() != "PASS":
                failures.append(f"pre_generation_challenge_not_pass:{role}")
            if not _text(item.get("notes")):
                failures.append(f"pre_generation_challenge_notes_missing:{role}")

    return failures


def assert_generation_brief(brief: dict[str, Any]) -> None:
    failures = generation_brief_failures(brief)
    if failures:
        raise ValueError("Generation brief blocked: " + "; ".join(failures))
