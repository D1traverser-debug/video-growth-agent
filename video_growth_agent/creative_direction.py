"""Frame-accurate creative specification and honest AI-video prompt compilation.

This is a craft *projection* of an approved editorial plan, not a competing
episode/business authority and not a claim that generated pixels were verified.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CraftSpecError(ValueError):
    """A shot or editorial-coverage contract is internally inconsistent."""


def _fields(value: Any, required: set[str], optional: set[str] | None = None) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CraftSpecError("expected an object")
    optional = optional or set()
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing or unknown:
        raise CraftSpecError(f"missing fields={sorted(missing)} unexpected fields={sorted(unknown)}")
    return value


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CraftSpecError(f"{field} must be non-empty text")
    return value.strip()


def _words(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise CraftSpecError(f"{field} must be a list of non-empty strings")
    return value


def _time(frame: int, fps: int) -> str:
    return f"{frame / fps:.2f}s"


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Validate what can be *structurally* proved, without claiming aesthetic QA."""
    _fields(spec, {"schema_version", "title", "source_plan_ref", "fps", "duration_frames",
                   "visual_bible", "required_story_events", "shots", "ending", "negative_constraints",
                   "generator"})
    if spec["schema_version"] != 1:
        raise CraftSpecError("unsupported schema_version")
    _text(spec["title"], "title")
    ref = _text(spec["source_plan_ref"], "source_plan_ref")
    if not ref.startswith("editorial-plan://") or "@" not in ref:
        raise CraftSpecError("source_plan_ref must bind an exact versioned editorial plan")
    fps, total = spec["fps"], spec["duration_frames"]
    if type(fps) is not int or fps <= 0 or type(total) is not int or total <= 0:
        raise CraftSpecError("fps and duration_frames must be positive integers")
    bible = _fields(spec["visual_bible"], {"style", "world", "lighting", "palette",
                                          "character_anchors", "prop_anchors"})
    for key in ("style", "world", "lighting", "palette"):
        _text(bible[key], f"visual_bible.{key}")
    for key in ("character_anchors", "prop_anchors"):
        _words(bible[key], f"visual_bible.{key}")
    events = spec["required_story_events"]
    if not isinstance(events, list) or not events:
        raise CraftSpecError("required_story_events cannot be empty")
    event_ids: set[str] = set()
    for event in events:
        _fields(event, {"id", "description"})
        event_id = _text(event["id"], "event.id")
        _text(event["description"], "event.description")
        if event_id in event_ids:
            raise CraftSpecError(f"duplicate event: {event_id}")
        event_ids.add(event_id)
    shots = spec["shots"]
    if not isinstance(shots, list) or not shots:
        raise CraftSpecError("shots cannot be empty")
    seen: set[str] = set()
    covered: dict[str, list[str]] = {event: [] for event in event_ids}
    cursor = 0
    for shot in shots:
        _fields(shot, {"id", "start_frame", "end_frame", "frame", "action", "camera",
                        "lighting", "transition_out", "event_ids", "sound", "continuity"})
        sid = _text(shot["id"], "shot.id")
        if sid in seen:
            raise CraftSpecError(f"duplicate shot: {sid}")
        seen.add(sid)
        a, b = shot["start_frame"], shot["end_frame"]
        if type(a) is not int or type(b) is not int or a != cursor or b <= a or b > total:
            raise CraftSpecError(f"{sid}: gaps, overlaps, invalid frames, or exceeds duration")
        cursor = b
        for key in ("frame", "action", "camera", "lighting", "transition_out"):
            _text(shot[key], f"{sid}.{key}")
        for key in ("event_ids", "sound", "continuity"):
            _words(shot[key], f"{sid}.{key}")
        for event_id in shot["event_ids"]:
            if event_id not in event_ids:
                raise CraftSpecError(f"{sid}: unknown narrative event {event_id}")
            covered[event_id].append(sid)
    if cursor != total:
        raise CraftSpecError(f"timeline must end at frame {total}, ended at {cursor}")
    missing_events = sorted(event_id for event_id, shot_ids in covered.items() if not shot_ids)
    if missing_events:
        raise CraftSpecError(f"story events lost in compression: {missing_events}")
    _text(spec["ending"], "ending")
    _words(spec["negative_constraints"], "negative_constraints")
    gen = _fields(spec["generator"], {"provider", "model", "mode", "aspect_ratio",
                                      "resolution", "audio", "max_prompt_characters"})
    for key in ("provider", "model", "mode", "aspect_ratio", "resolution"):
        _text(gen[key], f"generator.{key}")
    if gen["audio"] not in ("on", "off"):
        raise CraftSpecError("generator.audio must be on or off")
    if type(gen["max_prompt_characters"]) is not int or gen["max_prompt_characters"] <= 0:
        raise CraftSpecError("generator.max_prompt_characters must be positive integer")
    return {"all_events_covered_in_plan": True, "event_to_shots": {key: covered[key] for key in sorted(covered)},
            "shot_count": len(shots), "duration_seconds": total / fps,
            "note": "Planned narrative coverage, NOT proof of generated visual content."}


def _global(spec: dict[str, Any]) -> str:
    b = spec["visual_bible"]
    return (f"{spec['title']}. Visual style: {b['style']}. World: {b['world']}. "
            f"Lighting: {b['lighting']}. Palette: {b['palette']}. "
            f"Character identity anchors: {'; '.join(b['character_anchors'])}. "
            f"Recurring props: {'; '.join(b['prop_anchors'])}. ")


def _shot(shot: dict[str, Any], fps: int) -> str:
    return (f"[{_time(shot['start_frame'], fps)}–{_time(shot['end_frame'], fps)}] "
            f"{shot['frame']}. Action: {shot['action']}. Camera: {shot['camera']}. "
            f"Lighting: {shot['lighting']}. Transition: {shot['transition_out']}. "
            f"Sound cues: {'; '.join(shot['sound']) or 'none'}. "
            f"Continuity: {'; '.join(shot['continuity']) or 'not specified'}.")


def compile_storyboard(spec: dict[str, Any], *, route: str = "shotwise") -> dict[str, Any]:
    """Compile production-facing prompts; fail visibly on unsupported prompt sizes."""
    coverage = validate_spec(spec)
    if route not in ("onepass", "shotwise"):
        raise CraftSpecError("route must be onepass or shotwise")
    gen = spec["generator"]
    header = _global(spec)
    negative = "Avoid: " + "; ".join(spec["negative_constraints"]) + "."
    limit = gen["max_prompt_characters"]
    shots = spec["shots"]
    if route == "onepass":
        prompt = (header + " ".join(_shot(s, spec["fps"]) for s in shots)
                  + f" Ending: {spec['ending']}. " + negative)
        if len(prompt) > limit:
            raise CraftSpecError(f"onepass prompt {len(prompt)} chars exceeds declared {limit}; use shotwise")
        prompts = [{"shot_ids": [s["id"] for s in shots], "prompt": prompt,
                    "duration_seconds": coverage["duration_seconds"]}]
    else:
        prompts = []
        for shot in shots:
            prompt = header + _shot(shot, spec["fps"]) + " " + negative
            if len(prompt) > limit:
                raise CraftSpecError(f"shot {shot['id']} prompt exceeds declared {limit}")
            prompts.append({"shot_ids": [shot["id"]], "prompt": prompt,
                            "duration_seconds": (shot["end_frame"] - shot["start_frame"]) / spec["fps"]})
    findings: list[str] = []
    if len(shots) > coverage["duration_seconds"] / 1.5:
        findings.append("HIGH_CUT_DENSITY: use storyboards and timeline editing; one-pass timing is uncertain")
    for shot in shots:
        seconds = (shot["end_frame"] - shot["start_frame"]) / spec["fps"]
        if len(shot["event_ids"]) > max(1, seconds / 0.7):
            findings.append(f"EVENT_DENSITY_RISK:{shot['id']}")
    if gen["audio"] == "off" and any(s["sound"] for s in shots):
        findings.append("SOUND_POST_REQUIRED: sonic cues must be produced in post")
    return {"source_plan_ref": spec["source_plan_ref"], "route": route,
            "provider_profile": gen, "narrative_coverage": coverage, "prompts": prompts,
            "review_flags": findings,
            "assurance": "Static structural validation only. No model execution, aesthetic score, or frame-level AV verification."}


def compile_from_file(path: str | Path, *, route: str = "shotwise") -> dict[str, Any]:
    return compile_storyboard(json.loads(Path(path).read_text(encoding="utf-8")), route=route)
