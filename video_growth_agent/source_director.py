"""Bridge a raw screenplay to a source-anchored, verifiable director brief.

The authoring packet is executable as a structured request to an external LLM.
Model output is untrusted: verify the exact immutable source, quote positions,
frame contract, and coverage. Do not pretend a deterministic parser directs art.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any, Callable

from .prompt_director import PromptPlanError, compile_prompts, validate_plan


_CLOCK = re.compile(r"(?<![\d])(?P<start>\d{1,2})\s*[-–]\s*(?P<end>\d{1,2})秒")


def _source_digest(raw: str) -> str:
    return "sha256:" + sha256(raw.encode("utf-8")).hexdigest()


def inventory_source(raw: str) -> dict[str, Any]:
    """Lexically identify every timestamped source span, with exact offsets.

    These are *candidates* for semantic coverage, not model-created events.
    Overlapping original clock intervals are preserved and never silently
    interpreted as a single sequential timeline.
    """
    if not isinstance(raw, str) or not raw.strip():
        raise PromptPlanError("raw source text must not be empty")
    matches = list(_CLOCK.finditer(raw))
    units = []
    for i, match in enumerate(matches):
        start, end = int(match["start"]), int(match["end"])
        if end <= start:
            raise PromptPlanError(f"source timestamp {match.group()} has nonpositive duration")
        stop = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        content = raw[match.end():stop]
        units.append({
            "unit_id": f"U{i + 1:03}",
            "kind": "SOURCE_TIMECODE",
            "clock": [start, end],
            "source_span": [match.start(), stop],
            "exact_excerpt": raw[match.start():stop],
            "content": content,
        })
    if not matches:
        # Real authoring requests are often ideas or prose with no original
        # timecodes. Split lexically, preserve offsets, and NEVER claim these
        # textual slices were independently understood as dramatic events.
        for part in re.finditer(r"[^。；\\n]+[。；\\n]?", raw):
            if not part.group().strip():
                continue
            units.append({
                "unit_id": f"U{len(units) + 1:03}",
                "kind": "UNTIMED_SOURCE_SENTENCE",
                "clock": None,
                "source_span": [part.start(), part.end()],
                "exact_excerpt": raw[part.start():part.end()],
                "content": part.group(),
            })
    return {
        "source_digest": _source_digest(raw),
        "total_characters": len(raw),
        "untimed_prefix": raw[:matches[0].start()] if matches else "",
        "source_timing_units": units,
        "source_timing_unit_count": len(units),
        "nested_or_overlapping_clock_marks": any(
            units[i]["clock"][0] < units[i - 1]["clock"][1]
            for i in range(1, len(units))
        ),
        "claim": "Clock segmentation is lexical, not scene semantics or a correct rendered timeline.",
    }


def build_director_request(
    raw: str,
    *, target_seconds: int,
    fps: int = 30,
    aspect_ratio: str = "16:9",
    source_reference: str = "user-supplied://original",
    provider: str = "MiniMax-H3",
    source_type: str = "USER_REFERENCE",
) -> dict[str, Any]:
    """Create one self-contained, source-locked authoring task."""
    if type(target_seconds) is not int or not 4 <= target_seconds <= 15:
        raise PromptPlanError("H3 target duration must be an integer 4–15s")
    if type(fps) is not int or not 1 <= fps <= 120:
        raise PromptPlanError("fps must be integer in range 1..120")
    if aspect_ratio not in {"16:9", "9:16", "1:1", "4:3", "3:4"}:
        raise PromptPlanError("unsupported aspect ratio")
    if source_type not in {"USER_ORIGINAL", "USER_REFERENCE", "ORIGINAL_SCRIPT", "PRIMARY_DOCUMENT"}:
        raise PromptPlanError("unsupported source type")
    if provider != "MiniMax-H3":
        raise PromptPlanError("raw director authoring currently targets MiniMax-H3")
    inventory = inventory_source(raw)
    task = {
        "source_contract": {
            "type": source_type,
            "raw": raw,
            "reference": source_reference,
            "completeness": "FULL",
            "digest": inventory["source_digest"],
        },
        "target": {
            "duration_seconds": target_seconds,
            "fps": fps,
            "total_frames": target_seconds * fps,
            "aspect_ratio": aspect_ratio,
            "provider": {"name": "MiniMax", "model": "MiniMax-H3", "mode": "T2VA", "native_audio": True},
        },
        "source_inventory": inventory,
        "instructions": [
            "Act as director, writer, editor, cinematographer, sound designer and independent critic; output ONLY a JSON object matching the exact prompt_director plan contract, no Markdown fences.",
            "Preserve source.raw verbatim and source.reference exactly: do not rewrite, compress, trim or invent source quotes.",
            "Distinguish original SOURCE events (literal source_quote, origin SOURCE) from CREATIVE_INFERENCE (source_quote empty). Create explicit event IDs and map each to actual shot IDs.",
            "Inventory every distinct physical/emotional event in the original. Audit every source unit (timecoded or plain prose) against event IDs; if a unit cannot be expressed in the target running time, do not falsely promise all content survived.",
            "Compare at least two genuinely different directorial treatments, articulate cause, affect, visual mechanism and concrete failure mode; then select one and state why.",
            "Specify one coherent full-film visual_language (style/world/palette/materials/lighting/render_finish) derived from the original, not generic cyberpunk imagery.",
            "Frame the edited film with half-open integer [start_frame,end_frame), no overlaps, full 0..total_frames coverage; original 30s timing is reference content, not a physically executable 10s duration.",
            "For each shot write cause-effect action.start/trigger/finish; lens, framing, exactly one camera.move, motivated light, grounded transition, continuity and frame-indexed audio cues.",
            "Honor requested silent dialogue policy unless original explicitly has speech; a final written subtitle is NOT spoken dialogue; implement tricky Chinese typography in post, not trust generated letterforms.",
            "Keep clip resolution claims honest; 8K look language is an art direction, not proof that the video generator outputs 8K.",
            "Do not self-declare actual AI video quality or a winning provider; flag action density and important sensory/acting beats that remain hard to perceive at target duration.",
        ],
        "required_plan_fields": {
            "version": "integer=1",
            "source": {"type": "copy", "raw": "copy exact original", "reference": "copy",
                       "completeness": "FULL"},
            "brief": ["title", "goal", "emotion", "audience", "fps",
                      "total_frames", "aspect_ratio", "ending",
                      "narrative_strategy", "sound_strategy"],
            "visual_language": ["style", "world", "palette", "materials",
                                "lighting", "render_finish"],
            "alternatives": ["id", "premise", "visual_mechanism",
                             "failure_mode", "why_select_or_reject"],
            "selected": "id of chosen alternative",
            "required_events": ["id", "meaning", "origin", "source_quote"],
            "identity_anchors": "nonempty list of exact repeated characters/props",
            "shots": ["id", "start_frame", "end_frame", "scene", "composition",
                      "action:{start,trigger,finish}",
                      "camera:{framing,lens,move,motivation}",
                      "light:{source,direction,effect}",
                      "transition:{kind,bridge,purpose}", "audio", "event_ids",
                      "continuity"],
            "provider": "copy target.provider",
        },
    }
    return task


def prepare_authoring_messages(packet: dict[str, Any]) -> list[dict[str, str]]:
    """Vendor-neutral chat message contract. Not a provider API call."""
    instructions = packet["instructions"]
    return [
        {"role": "system", "content":
         "You are a senior film director and production writer. Produce one syntactically valid JSON object only. "
         "Do not make up first-party sources, asset refs, model execution, or film-quality evidence."},
        {"role": "user", "content":
         "\n".join(instructions) + "\nCOMPLETE_SOURCE_AND_OUTPUT_CONTRACT:\n"
         + json.dumps({
             "source_contract": packet["source_contract"],
             "source_timing_units": packet["source_inventory"]["source_timing_units"],
             "untimed_prefix": packet["source_inventory"]["untimed_prefix"],
             "target": packet["target"],
             "required_plan_fields": packet["required_plan_fields"],
         }, ensure_ascii=False)},
    ]


def audit_authored_plan(packet: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """Reject source swapping, timing drift and unknown external plan roots.

    Report source-unit coverage separately: lexical quote coverage is not a
    semantic guarantee that the actual film contains the source events.
    """
    source = packet["source_contract"]
    target = packet["target"]
    if not isinstance(plan, dict):
        raise PromptPlanError("authored plan is not an object")
    if plan.get("source") != {k: source[k] for k in ("type", "raw", "reference", "completeness")}:
        raise PromptPlanError("authored plan altered or substituted the original source")
    brief = plan.get("brief")
    if not isinstance(brief, dict) or any(
        brief.get(key) != value for key, value in (
            ("fps", target["fps"]), ("total_frames", target["total_frames"]),
            ("aspect_ratio", target["aspect_ratio"])
        )
    ):
        raise PromptPlanError("authored plan does not obey the agreed editorial timebase/aspect")
    if plan.get("provider") != target["provider"]:
        raise PromptPlanError("authored plan changed video generation provider settings")
    structure = validate_plan(plan)
    original = source["raw"]
    soundtrack_categories = [cue["category"] for shot in plan["shots"] for cue in shot["audio"]]
    if "无台词" in original and "VOICE" in soundtrack_categories:
        raise PromptPlanError("original specifies no dialogue, but authored shot added VOICE")
    if "仅配背景音乐" in original and any(
        category not in {"MUSIC", "SILENCE"} for category in soundtrack_categories
    ):
        raise PromptPlanError("original specifies background-music-only; authored Foley/ambience/voice would violate it")
    spans = packet["source_inventory"]["source_timing_units"]
    all_source_quotes = [e["source_quote"] for e in plan["required_events"] if e["origin"] == "SOURCE"]
    # This does not demand every comma-separated phrase is its own independent
    # event. It identifies unclaimed time-marked intervals for director review.
    coverage = [{
        "unit_id": unit["unit_id"], "original_clock": unit["clock"],
        "source_span": unit["source_span"],
        "source_events_quoted": [
            quote for quote in all_source_quotes
            if quote and quote in unit["exact_excerpt"]
        ],
        "status": "LEXICALLY_ANCHORED" if any(
            quote and quote in unit["exact_excerpt"] for quote in all_source_quotes
        ) else "NEEDS_SOURCE_EVENT_REVIEW",
    } for unit in spans]
    gaps = [unit["unit_id"] for unit in coverage if unit["status"] != "LEXICALLY_ANCHORED"]
    return {
        "source_digest": source["digest"],
        "source_units": coverage,
        "unit_count": len(coverage),
        "unanchored_units": gaps,
        "source_unit_anchor_fraction": (len(coverage) - len(gaps)) / len(coverage) if coverage else 0,
        "timeline_valid": True,
        "narrative_tag_coverage": structure["events_present_in_plan"],
        "independent_story_semantics_verified": False,
        "visual_model_execution_verified": False,
        "risk_notes": (
            ["Long source compressed into " + str(target["duration_seconds"]) +
             "s: each original beat may not remain legible at native viewing speed."]
            if len(coverage) > target["duration_seconds"] else []
        ) + (["Review missing literal anchors in: " + ", ".join(gaps)] if gaps else []) + (
            ["SOURCE_AUDIO_CONFLICT: original says music-only yet mentions audible claps; music-only global specification prevails, keep the hand gesture visibly."]
            if "仅配背景音乐" in original and "拍手带响" in original else []
        ),
    }


def accept_authoring_response(
    packet: dict[str, Any], model_response: str,
    *, prompt_route: str = "onepass",
    h3_style: str = "chinese",
) -> dict[str, Any]:
    """Treat model response as untrusted JSON; validate before prompt export."""
    if not isinstance(model_response, str):
        raise PromptPlanError("authoring model returned a non-text response")
    try:
        plan = json.loads(model_response)
    except json.JSONDecodeError as exc:
        raise PromptPlanError(f"authoring model response is not a bare JSON object: {exc}") from exc
    audit = audit_authored_plan(packet, plan)
    if audit["unanchored_units"]:
        raise PromptPlanError(
            "original source passages lack traceable event anchors: "
            + ", ".join(audit["unanchored_units"])
        )
    compiled = compile_prompts(plan, route=prompt_route, h3_style=h3_style)
    routes = compiled["routes"]
    if not any(v["status"] == "COMPILED" for v in routes.values()):
        raise PromptPlanError("model returned a structurally valid but unrenderable prompt plan")
    return {"plan": plan, "source_audit": audit, "compiled": compiled}


def build_compatible_chat_client(
    *, endpoint: str, model_name: str, api_key: str, approved: bool,
    timeout_seconds: int = 120,
) -> Callable[[list[dict[str, str]]], str]:
    """Opt-in remote text model; compatible chat-completions protocol only.

    The caller must explicitly approve external transmission of source text
    and any provider cost. Credentials are not persisted or printed.
    """
    from urllib.parse import urlparse
    from urllib.request import Request, urlopen

    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.fragment:
        raise PromptPlanError("remote text model endpoint must be a public HTTPS URL without userinfo/fragment")
    if not isinstance(model_name, str) or not model_name.strip():
        raise PromptPlanError("text model name required")
    if not api_key or not api_key.strip():
        raise PromptPlanError("text model API credential is missing")
    if not approved:
        raise PromptPlanError("remote text-model calls require explicit operator approval of upload/cost")
    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 300:
        raise PromptPlanError("timeout must be between 1 and 300 seconds")

    def complete(messages: list[dict[str, str]]) -> str:
        payload = json.dumps({
            "model": model_name,
            "messages": messages,
            "temperature": 0.25,
            "response_format": {"type": "json_object"},
        }, ensure_ascii=False).encode("utf-8")
        request = Request(endpoint, data=payload, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        }, method="POST")
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                result = json.loads(response.read(8 * 1024 * 1024).decode("utf-8"))
        except Exception as exc:
            # Sanitized: never serialize urllib exceptions that could contain
            # user-authored source, full prompt, raw response or API secret.
            raise PromptPlanError("remote text-model request failed; provider request was not accepted") from None
        try:
            content = result["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("empty response")
            return content
        except (KeyError, IndexError, TypeError, ValueError):
            raise PromptPlanError("text model response missing nonempty choices[0].message.content") from None
    return complete


def author_with_model(
    packet: dict[str, Any],
    model: Callable[[list[dict[str, str]]], str],
    *, prompt_route: str = "onepass",
    h3_style: str = "chinese",
    max_revisions: int = 0,
) -> dict[str, Any]:
    """Call a real model through an injected client and repair invalid drafts.

    Each retry is a NEW (possibly paid) API call and must be budgeted explicitly.
    Untrusted invalid output never silently enters production.
    """
    if type(max_revisions) is not int or not 0 <= max_revisions <= 3:
        raise PromptPlanError("max_revisions must be 0..3")
    messages = prepare_authoring_messages(packet)
    for attempt in range(max_revisions + 1):
        response = model(messages)
        try:
            accepted = accept_authoring_response(
                packet, response, prompt_route=prompt_route, h3_style=h3_style,
            )
            accepted["authoring_attempts"] = attempt + 1
            return accepted
        except PromptPlanError as exc:
            if attempt == max_revisions:
                raise
            # Never copy the invalid response back into a trusted contract.
            # Supply only the error and immutable source/timing requirements.
            messages = messages + [{
                "role": "user",
                "content": (
                    "The previous candidate was REJECTED: " + str(exc) + ". "
                    "Return a complete corrected bare JSON object. Keep source.raw, "
                     "source.reference, agreed edit timebase and model provider unchanged; "
                    "map ALL original source units to source-quoted narrative events."
                ),
            }]
    raise PromptPlanError("unreachable authoring state")
