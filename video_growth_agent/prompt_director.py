"""Evidence-aware prompt direction, not a second production controller.

No model is called here. The module validates authored short-film plans and
compiles MiniMax H3-first prompts or an explicitly selected PixVerse baseline.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .h3_prompt import render_h3_cn_storyboard, render_h3_lean_story, render_h3_t2va

H3 = {
    "provider": "MiniMax",
    "model": "MiniMax-H3",
    "min_duration": 4,
    "max_duration": 15,
    "max_prompt_characters": 7000,  # conservative local cap, not asserted as official
    "native_fps": 24,
    "source": "https://platform.minimax.io/docs/api-reference/video-generation-v2-create",
    "prompt_skill": "https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing",
    "verified_at": "2026-10-23",
}
PIXVERSE_V6 = {
    "provider": "PixVerse",
    "model": "V6",
    "duration_seconds_integer_min": 1,
    "duration_seconds_integer_max": 15,
    "max_prompt_characters": 5000,
    "source": "https://docs.pixverse.ai/PixVerse-V6-User-Guide-3373e99bf35080dfa9d8c44f30fde3bc",
    "verified_at": "2026-10-23",
}
CAMERA_MOVES = {"LOCKED", "PUSH_IN", "PULL_OUT", "PAN_LEFT", "PAN_RIGHT",
                "TILT_UP", "TILT_DOWN", "TRACK_LEFT", "TRACK_RIGHT", "ORBIT",
                "CRANE_UP", "CRANE_DOWN", "HANDHELD", "FOLLOW"}
ROUTES = {"onepass", "shotwise", "compare"}


class PromptPlanError(ValueError):
    pass


def _obj(item: Any, fields: set[str], where: str) -> dict:
    if not isinstance(item, dict):
        raise PromptPlanError(f"{where} must be a mapping")
    unknown = set(item) - fields
    missing = fields - set(item)
    if unknown or missing:
        raise PromptPlanError(f"{where}: missing={sorted(missing)} unknown={sorted(unknown)}")
    return item


def _str(item: Any, where: str) -> str:
    if not isinstance(item, str) or not item.strip():
        raise PromptPlanError(f"{where}: non-empty text required")
    return item.strip()


def _list(item: Any, where: str, *, require: bool = False) -> list:
    if not isinstance(item, list) or (require and not item):
        raise PromptPlanError(f"{where}: list required")
    return item


def _seconds(frame: int, fps: int) -> str:
    return f"{frame / fps:.2f}s"


def validate_plan(plan: dict) -> dict:
    """Static proof: authorship trace, exact frames, distinct alternatives, coverage.

    NOT a semantic theorem and NOT a claim that rendered audio/video has passed QA.
    """
    _obj(plan, {"version", "source", "brief", "visual_language", "alternatives", "selected",
                "required_events", "identity_anchors", "shots", "provider"}, "plan")
    if plan["version"] != 1:
        raise PromptPlanError("unsupported plan version")
    source = _obj(plan["source"], {"type", "raw", "reference", "completeness"}, "source")
    if source["type"] not in {"USER_ORIGINAL", "USER_REFERENCE", "ORIGINAL_SCRIPT", "PRIMARY_DOCUMENT"}:
        raise PromptPlanError("source.type is not admitted")
    if source["completeness"] not in {"FULL", "EXCERPT"}:
        raise PromptPlanError("source.completeness must be FULL or EXCERPT")
    raw = _str(source["raw"], "source.raw")
    _str(source["reference"], "source.reference")
    brief = _obj(plan["brief"], {"title", "goal", "emotion", "audience",
                                 "fps", "total_frames", "aspect_ratio", "ending",
                                 "narrative_strategy", "sound_strategy"}, "brief")
    for key in ("title", "goal", "emotion", "audience", "aspect_ratio",
                "ending", "narrative_strategy", "sound_strategy"):
        _str(brief[key], f"brief.{key}")
    visual = _obj(plan["visual_language"], {
        "style", "world", "palette", "materials", "lighting", "render_finish"
    }, "visual_language")
    for key, value in visual.items():
        _str(value, f"visual_language.{key}")
    fps, total = brief["fps"], brief["total_frames"]
    if type(fps) is not int or type(total) is not int or not 1 <= fps <= 120 or total <= 0:
        raise PromptPlanError("fps and total_frames must be positive integer frame units")

    alternatives = _list(plan["alternatives"], "alternatives", require=True)
    if len(alternatives) < 2:
        raise PromptPlanError("at least two competing creative concepts required")
    seen: set[str] = set()
    for item in alternatives:
        _obj(item, {"id", "premise", "visual_mechanism", "failure_mode", "why_select_or_reject"},
             "concept")
        for key in ("id", "premise", "visual_mechanism", "failure_mode", "why_select_or_reject"):
            _str(item[key], f"concept.{key}")
        if item["id"] in seen:
            raise PromptPlanError("duplicate concept")
        seen.add(item["id"])
    if len({str(a["visual_mechanism"]).strip().casefold() for a in alternatives}) != len(alternatives):
        raise PromptPlanError("creative alternatives repeat the same visual mechanism")
    chosen = _str(plan["selected"], "selected")
    if chosen not in seen:
        raise PromptPlanError("selected concept not found")
    if not any(a["id"] != chosen for a in alternatives):
        raise PromptPlanError("missing a rejected creative treatment")

    event_ids: set[str] = set()
    mandatory: set[str] = set()
    for event in _list(plan["required_events"], "required_events", require=True):
        _obj(event, {"id", "meaning", "origin", "source_quote"}, "required_event")
        event_id = _str(event["id"], "event.id")
        _str(event["meaning"], "event.meaning")
        if event_id in event_ids:
            raise PromptPlanError("duplicate required event")
        event_ids.add(event_id)
        if event["origin"] not in {"SOURCE", "CREATIVE_INFERENCE"}:
            raise PromptPlanError(f"invalid origin for {event_id}")
        if event["origin"] == "SOURCE":
            quote = _str(event["source_quote"], f"{event_id}.source_quote")
            if quote not in raw:
                raise PromptPlanError(f"{event_id}: source quote not found in raw material")
        elif event["source_quote"] != "":
            raise PromptPlanError(f"{event_id}: inferred event must not masquerade as source quote")
        if event["origin"] == "SOURCE":
            mandatory.add(event_id)
    anchors = _list(plan["identity_anchors"], "identity_anchors", require=True)
    for anchor in anchors:
        _str(anchor, "identity_anchor")
    shots = _list(plan["shots"], "shots", require=True)
    current = 0
    coverage: dict[str, list[str]] = {event: [] for event in event_ids}
    shot_ids: set[str] = set()
    sound_cues = 0
    for shot in shots:
        _obj(shot, {"id", "start_frame", "end_frame", "scene", "composition",
                    "action", "camera", "light", "transition", "audio",
                    "event_ids", "continuity"}, "shot")
        shot_id = _str(shot["id"], "shot.id")
        if shot_id in shot_ids:
            raise PromptPlanError("duplicate shot id")
        shot_ids.add(shot_id)
        start, end = shot["start_frame"], shot["end_frame"]
        if type(start) is not int or type(end) is not int or start != current or not start < end <= total:
            raise PromptPlanError(f"{shot_id}: frame gap/overlap or invalid duration")
        current = end
        for key in ("scene", "composition", "continuity"):
            _str(shot[key], f"{shot_id}.{key}")
        action = _obj(shot["action"], {"start", "trigger", "finish"}, f"{shot_id}.action")
        for key in ("start", "trigger", "finish"):
            _str(action[key], f"{shot_id}.action.{key}")
        camera = _obj(shot["camera"], {"framing", "lens", "move", "motivation"}, f"{shot_id}.camera")
        for key in ("framing", "lens", "motivation"):
            _str(camera[key], f"{shot_id}.camera.{key}")
        if camera["move"] not in CAMERA_MOVES:
            raise PromptPlanError(f"{shot_id}: unsupported or conflicting camera movement")
        light = _obj(shot["light"], {"source", "direction", "effect"}, f"{shot_id}.light")
        for key in ("source", "direction", "effect"):
            _str(light[key], f"{shot_id}.light.{key}")
        transition = _obj(shot["transition"], {"kind", "bridge", "purpose"}, f"{shot_id}.transition")
        for key in ("kind", "bridge", "purpose"):
            _str(transition[key], f"{shot_id}.transition.{key}")
        for eid in _list(shot["event_ids"], f"{shot_id}.event_ids", require=True):
            if eid not in event_ids:
                raise PromptPlanError(f"{shot_id}: undeclared story event {eid}")
            coverage[eid].append(shot_id)
        for cue in _list(shot["audio"], f"{shot_id}.audio"):
            if not isinstance(cue, dict):
                raise PromptPlanError(f"{shot_id}: audio cue must be an object")
            category = cue.get("category")
            required_cue = {"at_frame", "category", "description"}
            if category == "VOICE":
                required_cue |= {"speaker", "language", "spoken_text"}
            _obj(cue, required_cue, "audio_cue")
            frame = cue["at_frame"]
            if type(frame) is not int or not start <= frame < end:
                raise PromptPlanError(f"{shot_id}: audio cue falls outside its shot")
            if category not in {"MUSIC", "SFX", "VOICE", "SILENCE", "AMBIENCE"}:
                raise PromptPlanError(f"{shot_id}: unknown sound category")
            _str(cue["description"], "audio_cue.description")
            if category == "VOICE":
                for key in ("speaker", "language", "spoken_text"):
                    _str(cue[key], f"audio_cue.{key}")
                if "<d>" in cue["spoken_text"] or "</d>" in cue["spoken_text"]:
                    raise PromptPlanError("VOICE spoken_text is literal speech, not preformatted <d> markup")
            sound_cues += 1
    if current != total:
        raise PromptPlanError("shots do not reach exact final frame")
    missing = sorted(mandatory - {event for event, used in coverage.items() if used})
    if missing:
        raise PromptPlanError("SOURCE events missing from storyboard: " + ", ".join(missing))

    provider = _obj(plan["provider"], {"name", "model", "mode", "native_audio"}, "provider")
    identity = (provider["name"], provider["model"])
    if identity == ("MiniMax", "MiniMax-H3"):
        # Only text mode is wired until reference assets can be verified and bound.
        if provider["mode"] != "T2VA":
            raise PromptPlanError("MiniMax H3 reference/keyframe mode needs verified bound assets; only T2VA implemented")
        if not provider["native_audio"]:
            raise PromptPlanError("MiniMax H3 native_audio=false is not implemented safely; keep audio on or use a verified silent profile")
    elif identity == ("PixVerse", "V6"):
        if provider["mode"] != "T2V":
            raise PromptPlanError("PixVerse V6 reference mode needs bound assets; only T2V implemented")
    else:
        raise PromptPlanError("no verified adapter for requested provider/model")
    if type(provider["native_audio"]) is not bool:
        raise PromptPlanError("native_audio must be boolean")
    if brief["aspect_ratio"] not in {"16:9", "4:3", "1:1", "3:4", "9:16"}:
        raise PromptPlanError("unsupported aspect ratio")
    return {"events_present_in_plan": {k: coverage[k] for k in sorted(coverage)},
            "source_event_count": len(mandatory),
            "shot_count": len(shots), "duration_seconds": total / fps,
            "sound_cues": sound_cues,
            "source_scope_claim": source["completeness"],
            "whole_original_verified": False,
            "assurance": "Covers only the supplied raw source spans; EXCERPT input cannot prove full original story retention. No film semantic/quality verdict."}


def _shot_text(s: dict, fps: int) -> str:
    a, cam, light, trans = s["action"], s["camera"], s["light"], s["transition"]
    audio = "; ".join(f"{_seconds(c['at_frame'],fps)} {c['category']}: {c['description']}" for c in s["audio"])
    return (
        f"[{_seconds(s['start_frame'],fps)}–{_seconds(s['end_frame'],fps)}] "
        f"Scene: {s['scene']}. Composition: {s['composition']}. "
        f"Start: {a['start']}. Trigger: {a['trigger']}. Finish: {a['finish']}. "
        f"Camera: {cam['framing']}, {cam['lens']}, {cam['move'].lower()}, motivated by {cam['motivation']}. "
        f"Light: {light['source']}, {light['direction']}, creating {light['effect']}. "
        f"Exit: {trans['kind']} using {trans['bridge']} because {trans['purpose']}. "
        f"Continuity: {s['continuity']}. Sound: {audio or 'post-production only'}."
    )


def _render_length(seconds: float, provider: dict) -> int:
    requested = math.ceil(seconds - 1e-9)
    if provider["name"] == "MiniMax" and provider["model"] == "MiniMax-H3":
        requested = max(4, requested)
        if requested > 15:
            raise PromptPlanError(f"MiniMax H3 clip must be an integer 4–15 seconds, got {requested}")
    elif not 1 <= requested <= 15:
        raise PromptPlanError(f"PixVerse V6 clip length outside 1–15 seconds: {requested}")
    return requested


def compile_prompts(plan: dict, route: str = "compare", h3_style: str = "auto") -> dict:
    if h3_style not in {"auto", "lean", "chinese", "official"}:
        raise PromptPlanError("h3_style must be auto, lean, chinese or official")
    validated = validate_plan(plan)
    if h3_style == "auto" and plan["provider"]["name"] == "MiniMax":
        # No anecdotal sample or theoretical formatting guide is a
        # sufficiently strong quality label to choose a global winner.
        # Materialize alternatives and leave production selection open.
        candidates = {
            dialect: compile_prompts(plan, route=route, h3_style=dialect)["routes"]
            for dialect in ("lean", "chinese", "official")
        }
        return {
            "selected_concept": plan["selected"],
            "h3_prompt_dialect": "auto",
            "prompt_candidates": candidates,
            "selection_status": "UNDECIDED_NEEDS_SCENE_SPECIFIC_MEDIA_EVIDENCE",
            "quality_winner": None,
            "visual_winner": None,
            "static_validation": validated,
            "provider_profile": H3,
            "review_targets": build_shot_review_targets(plan),
            "reason": (
                "One positive H3 user example is evidence for that particular scene, "
                "not a universal prompt dialect standard. Compare results by workload."
            ),
        }
    if route not in ROUTES:
        raise PromptPlanError("route must be onepass, shotwise, or compare")
    brief, shots = plan["brief"], plan["shots"]
    fps = brief["fps"]
    concept = next(c for c in plan["alternatives"] if c["id"] == plan["selected"])
    visual = plan["visual_language"]
    header = (
        f"{brief['title']}. Visual style: {visual['style']}. World: {visual['world']}. "
        f"Materials: {visual['materials']}. Palette: {visual['palette']}. "
        f"Lighting grammar: {visual['lighting']}. Finish: {visual['render_finish']}. "
        f"Core intent: {brief['goal']}. Intended emotional change: {brief['emotion']}. "
        f"Chosen visual mechanism: {concept['visual_mechanism']}. Story method: {brief['narrative_strategy']}. "
        f"Stable identity and props: {'; '.join(plan['identity_anchors'])}. "
    )
    ending = f"Final image: {brief['ending']}. Audio approach: {brief['sound_strategy']}."
    output = {}
    for option in (("onepass", "shotwise") if route == "compare" else (route,)):
        try:
            candidate = []
            groups = [shots] if option == "onepass" else [[shot] for shot in shots]
            for group in groups:
                duration = sum(s["end_frame"] - s["start_frame"] for s in group) / fps
                render_seconds = _render_length(duration, plan["provider"])
                is_h3 = plan["provider"]["name"] == "MiniMax"
                if is_h3:
                    renderer = {"lean": render_h3_lean_story, "chinese": render_h3_cn_storyboard, "official": render_h3_t2va}[h3_style]
                    prompt = renderer(
                        plan=plan, shots=group, render_seconds=render_seconds,
                        usable_seconds=duration,
                        continuation=(group[-1]["id"] != shots[-1]["id"]),
                    )
                else:
                    prompt = header + " ".join(_shot_text(s, fps) for s in group) + " " + ending
                max_chars = H3["max_prompt_characters"] if is_h3 else PIXVERSE_V6["max_prompt_characters"]
                if len(prompt) > max_chars:
                    raise PromptPlanError(f"prompt exceeds conservative {max_chars}-character profile bound")
                candidate.append({
                    "shots": [s["id"] for s in group], "prompt": prompt,
                    "edit_duration_seconds": duration, "model_render_seconds": render_seconds,
                    "trim_seconds": render_seconds - duration,
                })
            total_generated = sum(x["model_render_seconds"] for x in candidate)
            output[option] = {
                "status": "COMPILED", "prompts": candidate,
                "generation_seconds": total_generated,
                "final_edit_seconds": validated["duration_seconds"],
                "generation_to_edit_ratio": round(total_generated / validated["duration_seconds"], 3),
                "recommended_use": (
                    "MULTISHOT_NATIVE_DRAFT" if is_h3 and option == "onepass" else
                    "EDITORIAL_TRIM_AND_CONTINUITY_QA" if option == "shotwise" else
                    "VENDOR_BASELINE"
                ),
                "frame_rate_warning": (
                    "MiniMax H3 outputs 24fps; project edit frame rate differs and requires conform."
                    if is_h3 and fps != 24 else None
                ),
                "warning": "Declared shot timing is an edit plan, not a model guarantee.",
            }
        except PromptPlanError as exc:
            output[option] = {"status": "BLOCKED", "reason": str(exc)}
    return {
        "selected_concept": plan["selected"], "h3_prompt_dialect": h3_style if plan["provider"]["name"] == "MiniMax" else None, "static_validation": validated,
        "provider_profile": H3 if plan["provider"]["name"] == "MiniMax" else PIXVERSE_V6, "routes": output,
        "review_targets": build_shot_review_targets(plan),
        "visual_winner": None,
        "reason": "No actual media, blind viewers or comparable render-cost observations were supplied.",
    }


def build_shot_review_targets(plan: dict) -> dict:
    """Build an unscored, artifact-bound review worksheet from directed shots.

    Source-event membership is a declared expectation, not a rendered-media
    observation. The sheet is for a reviewer of real footage to fill in.
    """
    verification = validate_plan(plan)
    sources = {e["id"]: e for e in plan["required_events"]}
    fps = plan["brief"]["fps"]
    targets = []
    for shot in plan["shots"]:
        targets.append({
            "shot_id": shot["id"],
            "edit_frames": [shot["start_frame"], shot["end_frame"]],
            "edit_window_seconds": [shot["start_frame"] / fps, shot["end_frame"] / fps],
            "expected_visible_action": {
                "initial": shot["action"]["start"],
                "physical_trigger": shot["action"]["trigger"],
                "result": shot["action"]["finish"],
            },
            "expected_camera": shot["camera"],
            "expected_transition": shot["transition"],
            "expected_identity_and_props": list(plan["identity_anchors"]),
            "required_source_events": [
                {"id": event_id, "meaning": sources[event_id]["meaning"],
                 "source_quote": sources[event_id]["source_quote"]}
                for event_id in shot["event_ids"] if sources[event_id]["origin"] == "SOURCE"
            ],
            "planned_sound_events": list(shot["audio"]),
            "observed_video_timecodes": None,
            "actual_result": "UNREVIEWED",
            "failure_evidence": [],
        })
    return {
        "source_reference": plan["source"]["reference"],
        "source_scope_claim": verification["source_scope_claim"],
        "expected_length_seconds": verification["duration_seconds"],
        "media_asset_ref": None,
        "reviewer_independence": "NOT_ESTABLISHED",
        "shots": targets,
        "assessment": "NOT_STARTED",
        "note": "An original-script event being tagged in a shot is NOT proof it appeared onscreen.",
    }


def compile_file(path: str | Path, route: str = "compare", h3_style: str = "auto") -> dict:
    return compile_prompts(json.loads(Path(path).read_text(encoding="utf-8")), route, h3_style)
