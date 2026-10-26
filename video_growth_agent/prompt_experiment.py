"""Controlled prompt-dialect experiment using the EXISTING experiment domain model.

No paid video generation and no self-awarded artistic score. The compared
policies vary both language and template; never claim a causal language-only
or schema-only effect.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from typing import Any

from .experiments import ExperimentPlan, ExperimentVariant
from .prompt_director import PromptPlanError, compile_prompts, validate_plan


def _digest(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":")).encode("utf-8")).hexdigest()


def h3_dialect_study(plan: dict, *, route: str = "onepass") -> dict:
    """Prepare genuinely matched inputs for a blind H3 prompt-policy test.

    No observations: winner cannot exist until rendered artifact evidence.
    """
    scope = validate_plan(plan)
    if (plan["provider"]["name"], plan["provider"]["model"], plan["provider"]["mode"]) != (
        "MiniMax", "MiniMax-H3", "T2VA"
    ):
        raise PromptPlanError("H3 dialect study requires MiniMax H3 T2VA; model comparisons use a separate study")
    if route != "onepass":
        raise PromptPlanError("initial prompt dialect comparison uses onepass to avoid extra clip/identity confounds")

    selected: list[tuple[str, dict]] = []
    for style in ("chinese", "official"):
        report = compile_prompts(plan, route=route, h3_style=style)
        result = report["routes"][route]
        if result["status"] != "COMPILED":
            raise PromptPlanError(f"{style} candidate blocked: {result['reason']}")
        selected.append((style, result))

    plan_hash = _digest(plan)
    fixed = {
        "provider": "MiniMax",
        "model": "MiniMax-H3",
        "mode": "T2VA",
        "route": route,
        "original_plan_digest": plan_hash,
        "fps_edit": str(plan["brief"]["fps"]),
        "aspect_ratio": plan["brief"]["aspect_ratio"],
        "clip_render_seconds": str(selected[0][1]["generation_seconds"]),
    }
    variants = []
    output_variants = []
    for style, result in selected:
        prompt_text = result["prompts"][0]["prompt"]
        prompt_hash = _digest(prompt_text)
        variants.append(ExperimentVariant(
            variant_id=style,
            artifact_or_plan_ref=f"sha256:{prompt_hash}",
            changed_variables={"prompt_rendering_policy": "CN_TIMECODED" if style == "chinese" else "H3_THREE_SECTION_STRUCTURED"},
            fixed_variables=fixed,
        ))
        output_variants.append({
            "id": style,
            "prompt_digest": prompt_hash,
            "prompt": prompt_text,
            "generated_seconds": result["generation_seconds"],
            "prompt_characters": len(prompt_text),
        })
    exp = ExperimentPlan(
        experiment_id=f"h3-prompt-policy-{plan_hash[:12]}",
        context_id=f"shotplan-sha256:{plan_hash}",
        hypothesis="A complete Chinese timed storyboard and first-party-structured H3 prompt can differ in scene comprehensibility despite identical storyline and runtime.",
        variants=tuple(variants),
        primary_metric="blind_story_comprehension",
        metric_semantics={
            "blind_story_comprehension": "Independent viewer recounts intended causal events before seeing plan, fraction 0..1",
            "identity_continuity": "Fraction 0..1 of planned stable entity/prop states retained across cuts",
            "physical_contact_errors": "Count of impossible extra limbs, missing grip/contact and prop teleportations in final clip",
            "usable_seconds": "Seconds of rendered output acceptable in final edit after review",
            "credits_spent": "Actual credits spent including failed attempts",
        },
        guardrail_metrics=("identity_continuity", "physical_contact_errors", "credits_spent"),
        attribution_mode="BUNDLED_PROMPT_POLICY_NOT_LANGUAGE_CAUSAL",
        minimum_observation_rule="At least 3 rendered takes per policy on identical scene, model, UI settings and budget, then repeat on second contrasting scene. Blind review output files; keep seed paired only if model supports it.",
        stop_rules=("halt if paid generation not explicitly authorized", "halt if one policy violates rights/age/content constraints", "declare INCONCLUSIVE on uncontrolled model or parameter drift"),
        evidence_refs=(f"source-digest:sha256:{_digest(plan['source']['raw'])}",),
    )
    return {
        "experiment_plan": asdict(exp),
        "source_scope": plan["source"]["completeness"],
        "structural_check": scope,
        "candidates": output_variants,
        "uncontrolled_variables": ["different natural language", "different prompt document structure"],
        "inference_limit": "Bundled policy test; cannot isolate language vs prompt formatting without a second factorial design.",
        "rendered_media_evidence": [],
        "quality_winner": None,
        "assurance": "Study designed but not executed. No paid API call or media acceptance occurred.",
    }
