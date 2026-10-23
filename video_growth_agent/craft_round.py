"""Evidence-bound cross-discipline craft reviews on existing Video domain roles.

NOT a new orchestrator, authority, model executor or claim of independently
performed human review. Packages existing RoleRegistry prompts for review.
Results remain review proposals until actual editorial-plan revisions pass the
original validator and are independently inspected in their new version.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

from .prompt_director import validate_plan
from .roles import RoleRegistry
from .techniques import TechniqueLibrary


class CraftReviewError(ValueError):
    pass


REVIEWERS = (
    "writer", "director", "storyboard_artist", "art_director",
    "editor", "sound_director", "red_team",
)
OWNERS = {
    "STORY": "writer",
    "EMOTION": "director",
    "ACTION": "storyboard_artist",
    "ART": "art_director",
    "CAMERA": "director",
    "EDIT": "editor",
    "SOUND": "sound_director",
    "CONTINUITY": "asset_director",
    "MODEL": "technical_director",
    "FACT": "fact_checker",
    "RIGHTS": "compliance_editor",
}
SEVERITIES = {"BLOCKER", "MAJOR", "MINOR"}
VERDICTS = {"ACCEPT_PLAN", "REVISE_PLAN", "BLOCKED"}
FOCI = {
    "writer": "story causality, original meaning, emotions, story consequences and omissions",
    "director": "actor behavior, payoff, camera intentions and audio-visual unity",
    "storyboard_artist": "shot jobs, tangible physical triggers, readable spatial connections",
    "art_director": "world shape, material, motivated light, actor/prop identity and style",
    "editor": "actual shot count, readable rhythm, matched cut geometry and action-axis",
    "sound_director": "exact speech, sound-source policy, timed physical hits, background score",
    "red_team": "strongest falsifiable reasons this plan may fail before credits are spent",
}


def _digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + sha256(payload.encode("utf-8")).hexdigest()


def prepare_craft_round(
    plan: dict,
    *,
    revision: int = 1,
    technique_tags: set[str] | None = None,
) -> dict:
    """Prepare independent discipline handoffs; do not pretend roles ran."""
    validate_plan(plan)
    if type(revision) is not int or revision < 1:
        raise CraftReviewError("revision must be a positive integer")
    registry = RoleRegistry()
    plan_ref = _digest(plan)
    study_tags = technique_tags if technique_tags is not None else {
        "shot-brief", "revision", "quality", "continuity",
    }
    if not isinstance(study_tags, set) or not all(isinstance(t, str) for t in study_tags):
        raise CraftReviewError("technique_tags must be a set of strings")
    proposals = TechniqueLibrary().find(study_tags, validated_only=False)
    orders = []
    for role in REVIEWERS:
        owner = registry.get(role)
        orders.append({
            "reviewer_role": role,
            "source_plan_digest": plan_ref,
            "revision": revision,
            "discipline_focus": FOCI[role],
            "role_mandate": owner.prompt,
            "veto_conditions": list(owner.veto),
            "review_input": {
                "plan_digest": plan_ref,
                "source_reference": plan["source"]["reference"],
                "full_film_goal": plan["brief"]["goal"],
                "global_look": plan["visual_language"],
                "shots": [
                    {
                        "id": shot["id"], "action": shot["action"],
                        "camera": shot["camera"], "light": shot["light"],
                        "transition": shot["transition"], "audio": shot["audio"],
                        "events": shot["event_ids"], "continuity": shot["continuity"],
                    } for shot in plan["shots"]
                ],
                "other_reviewers_opinions": None,
            },
            "required_review_fields": [
                "reviewer_role", "source_plan_digest", "verdict", "artifact_ref",
                "observed_scope", "review_method", "findings",
            ],
            "review_constraint": (
                "Review ONLY this exact plan; evidence for generated pixels must reference "
                "actual media and frames. Do not use other reviewers' opinions before "
                "independent review. No rubric-based self-awarded film PASS."
            ),
            "status": "NOT_EXECUTED",
        })
    return {
        "source_plan_digest": plan_ref,
        "revision": revision,
        "source_ref": plan["source"]["reference"],
        "stage": "CRAFT_PLAN_REVIEW",
        "authority": "Existing RoleRegistry; proposed review, not another Video stage gate.",
        "orders": orders,
        "candidate_techniques": [
            {"id": t.technique_id, "status": t.status, "use_when": t.use_when,
             "avoid_when": t.avoid_when, "evidence_refs": list(t.evidence_refs)}
            for t in proposals
        ],
        "execution_status": "PREPARED_NOT_REVIEWED",
    }


def reconcile_craft_round(packet: dict, reviews: list[dict]) -> dict:
    """Turn actual submitted role critiques into explicit owner handoffs.

    This does not modify plan, claim reviewer independence, verify real media,
    waive vetoes or promote new studio technique knowledge.
    """
    expected = {item["reviewer_role"] for item in packet["orders"]}
    if not isinstance(reviews, list) or len(reviews) != len(expected):
        raise CraftReviewError("one report from each required role is needed")
    observed: set[str] = set()
    findings: list[dict] = []
    role_verdicts: dict[str, str] = {}
    for review in reviews:
        fields = {"reviewer_role", "source_plan_digest", "verdict",
                  "artifact_ref", "observed_scope", "review_method", "findings"}
        if not isinstance(review, dict) or set(review) != fields:
            raise CraftReviewError("review fields missing, extra or malformed")
        role = review["reviewer_role"]
        if role not in expected or role in observed:
            raise CraftReviewError("reviewer role duplicated or not in source packet")
        observed.add(role)
        if review["source_plan_digest"] != packet["source_plan_digest"]:
            raise CraftReviewError("review references wrong plan version")
        if review["verdict"] not in VERDICTS:
            raise CraftReviewError("invalid reviewer verdict")
        if review["observed_scope"] not in {"PLAN_ONLY", "RENDERED_MEDIA"}:
            raise CraftReviewError("review scope must be explicit")
        if not isinstance(review["artifact_ref"], str) or not review["artifact_ref"].strip():
            raise CraftReviewError("review requires immutable artifact evidence ref")
        if review["observed_scope"] == "RENDERED_MEDIA":
            raise CraftReviewError("media quality must be assessed in the existing video review system, not self-attested in a craft plan packet")
        if not isinstance(review["review_method"], str) or not review["review_method"].strip():
            raise CraftReviewError("review method is required")
        if not isinstance(review["findings"], list):
            raise CraftReviewError("findings must be a list")
        role_verdicts[role] = review["verdict"]
        if review["verdict"] in {"BLOCKED", "REVISE_PLAN"} and not review["findings"]:
            raise CraftReviewError("blocking/revision verdict requires falsifiable findings")
        for finding in review["findings"]:
            fields = {"shot_id", "category", "severity", "observation",
                      "evidence_ref", "change_request"}
            if not isinstance(finding, dict) or set(finding) != fields:
                raise CraftReviewError("finding contract invalid")
            if finding["category"] not in OWNERS or finding["severity"] not in SEVERITIES:
                raise CraftReviewError("invalid finding category or severity")
            if not all(isinstance(finding[x], str) and finding[x].strip()
                       for x in ("shot_id", "observation", "evidence_ref", "change_request")):
                raise CraftReviewError("finding lacks actionable location, proof or change")
            if finding["shot_id"] != "WHOLE_FILM":
                shot_ids = {shot["id"] for shot in packet["orders"][0]["review_input"]["shots"]}
                if finding["shot_id"] not in shot_ids:
                    raise CraftReviewError("finding references unknown shot")
            if finding["evidence_ref"] == "UNVERIFIED" or finding["evidence_ref"].startswith("TODO"):
                raise CraftReviewError("finding evidence must be an actual reference")
            findings.append({
                **finding, "raised_by": role,
                "assigned_owner": OWNERS[finding["category"]],
                "source_plan_digest": packet["source_plan_digest"],
                "resolution_status": "OPEN",
            })
    # These are submitted claims, not a substitute for independent attestations.
    blockers = [f for f in findings if f["severity"] in {"BLOCKER", "MAJOR"}]
    status = (
        "REVISION_REQUIRED"
        if blockers or any(v != "ACCEPT_PLAN" for v in role_verdicts.values())
        else "PLAN_REVIEW_REPORTED_CLEAN__INDEPENDENCE_NOT_ESTABLISHED"
    )
    return {
        "plan_digest": packet["source_plan_digest"],
        "revision": packet["revision"],
        "role_verdicts": role_verdicts,
        "issues": findings,
        "role_handoffs": [
            {
                "assigned_owner": owner,
                "issue_indices": [i for i, issue in enumerate(findings)
                                  if issue["assigned_owner"] == owner],
                "action": "Propose a new plan version with evidence; never silently patch the approved plan.",
            } for owner in sorted({f["assigned_owner"] for f in findings})
        ],
        "showrunner_resolution_required": status == "REVISION_REQUIRED",
        "status": status,
        "artifact_promotion": "NOT_AUTHORIZED",
        "learning_promotion": "NOT_AUTHORIZED",
        "reviewer_independence": "NOT_ESTABLISHED",
    }


def next_revision_diff(previous: dict, current: dict) -> dict:
    """Small, deterministic history boundary between two complete shot plans."""
    validate_plan(previous)
    validate_plan(current)
    old, new = _digest(previous), _digest(current)
    if old == new:
        raise CraftReviewError("revision did not change the plan")
    if previous["source"] != current["source"]:
        raise CraftReviewError("source must not change in a same-story revision")
    if previous["brief"]["total_frames"] != current["brief"]["total_frames"]:
        raise CraftReviewError("runtime change requires a separate re-brief and source approval")
    old_shots = {s["id"]: s for s in previous["shots"]}
    new_shots = {s["id"]: s for s in current["shots"]}
    changes = [
        {"shot_id": key, "action": "ADDED" if key not in old_shots else
         "REMOVED" if key not in new_shots else "CHANGED"}
        for key in sorted(set(old_shots) | set(new_shots))
        if old_shots.get(key) != new_shots.get(key)
    ]
    return {
        "from_digest": old,
        "to_digest": new,
        "shot_changes": changes,
        "changed_visual_language": previous["visual_language"] != current["visual_language"],
        "changed_story_events": previous["required_events"] != current["required_events"],
        "next_review_required": True,
        "verification": "Static diff only; changes are not automatically approved or improvements.",
    }
