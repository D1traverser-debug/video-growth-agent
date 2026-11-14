"""Source-linked news x video packaging checks; no new publisher or controller."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

PLATFORMS = {"X", "TIKTOK", "YOUTUBE", "XIAOHONGSHU", "WECHAT_CHANNELS", "BILIBILI", "DOUYIN"}
FACT_CLASSES = {"PRIMARY_CONFIRMED", "ATTRIBUTED_REPORT", "ALLEGATION_UNVERIFIED"}
VISUAL_MODES = {"FICTIONAL_SYNTHETIC", "EDITORIAL_REAL", "MIXED_DISCLOSED"}
PUBLIC_FIELDS = {
    "X": ("post_text",),
    "TIKTOK": ("caption",),
    "YOUTUBE": ("title", "description"),
    "XIAOHONGSHU": ("title", "note"),
    "WECHAT_CHANNELS": ("short_title", "description"),
    "BILIBILI": ("title", "description"),
    "DOUYIN": ("caption",),
}
SEMANTIC_TESTS = (
    "news_replacement_loses_meaning", "video_replacement_loses_meaning",
    "not_plot_recitation", "natural_language", "fact_fiction_not_conflated",
)

def copy_digest(item: Mapping[str, object]) -> str:
    public = item.get("public_fields")
    content = public if isinstance(public, dict) else [item.get("title"), item.get("body")]
    raw = json.dumps(content, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def audit_packaging(case: Mapping[str, object]) -> dict:
    """Validate contract/lineage, never self-certify humor, truth or release."""
    errors, gates, warnings = [], [], []
    for field in ("program_id", "episode_id", "author_ref"):
        if not str(case.get(field) or "").strip():
            errors.append(f"{field}_required")
    schema = case.get("schema_version")
    if schema not in {"1.0", "1.1"}:
        errors.append("unsupported_schema")
    facts = case.get("source_facts")
    visuals = case.get("visual_assets")
    copies = case.get("platform_copies")
    for name, value in (("source_facts", facts), ("visual_assets", visuals), ("platform_copies", copies)):
        if not isinstance(value, list) or not value or not all(isinstance(x, dict) for x in value):
            errors.append(f"{name}_must_be_nonempty_objects")
    facts = [x for x in facts if isinstance(x, dict)] if isinstance(facts, list) else []
    visuals = [x for x in visuals if isinstance(x, dict)] if isinstance(visuals, list) else []
    copies = [x for x in copies if isinstance(x, dict)] if isinstance(copies, list) else []

    fact_ids, visual_ids = set(), set()
    for fact in facts:
        ident = fact.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in fact_ids:
            errors.append("duplicate_or_missing_fact_id")
        fact_ids.add(ident)
        if fact.get("classification") not in FACT_CLASSES:
            errors.append(f"{ident}:unknown_fact_classification")
        urls = fact.get("source_urls")
        if not isinstance(urls, list) or not urls or not all(
            isinstance(x, str) and x.startswith("https://") for x in urls
        ):
            errors.append(f"{ident}:https_source_required")
        if not str(fact.get("claim") or "").strip():
            errors.append(f"{ident}:claim_required")

    synthetic = False
    for visual in visuals:
        ident = visual.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in visual_ids:
            errors.append("duplicate_or_missing_visual_id")
        visual_ids.add(ident)
        mode = visual.get("truth_mode")
        if mode not in VISUAL_MODES:
            errors.append(f"{ident}:unknown_visual_truth_mode")
        synthetic |= mode in {"FICTIONAL_SYNTHETIC", "MIXED_DISCLOSED"}
        if not str(visual.get("source_ref") or "").strip():
            errors.append(f"{ident}:source_ref_required")
        digest = visual.get("sha256")
        if digest is not None and (
            not isinstance(digest, str) or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest.lower())
        ):
            errors.append(f"{ident}:invalid_sha256")
        if not digest:
            gates.append(f"{ident}:media_identity_unverified")
        if visual.get("rights_status") != "VERIFIED" or not visual.get("rights_evidence_ref"):
            gates.append(f"{ident}:rights_unverified")
        if mode in {"FICTIONAL_SYNTHETIC", "MIXED_DISCLOSED"} and visual.get("platform_disclosure") != "RECORDED":
            gates.append(f"{ident}:platform_synthetic_disclosure_open")

    if synthetic and case.get("fiction_is_not_real_world_evidence") is not True:
        errors.append("fiction_news_boundary_missing")

    platforms, angles, mechanisms = set(), set(), set()
    independent_reviews = 0
    for index, item in enumerate(copies):
        prefix = f"copy[{index}]"
        platform = item.get("platform")
        if platform not in PLATFORMS or platform in platforms:
            errors.append(f"{prefix}:unknown_or_duplicate_platform")
        platforms.add(platform)
        if schema == "1.1":
            fields = item.get("public_fields")
            required = PUBLIC_FIELDS.get(platform, ())
            if not isinstance(fields, dict) or any(
                not isinstance(fields.get(key), str) or not fields[key].strip() for key in required
            ):
                errors.append(f"{prefix}:platform_public_fields_missing_or_invalid")
            if isinstance(fields, dict) and "tags" in fields and not (
                isinstance(fields["tags"], list) and all(isinstance(tag, str) for tag in fields["tags"])
            ):
                errors.append(f"{prefix}:tags_must_be_string_list")
            if not str(item.get("platform_variant_ref") or "").strip():
                gates.append(f"{prefix}:platform_variant_version_unbound")
            if not str(item.get("format_review_evidence_ref") or "").strip():
                gates.append(f"{prefix}:platform_format_review_open")
            if synthetic and not str(item.get("synthetic_upload_disclosure_ref") or "").strip():
                gates.append(f"{prefix}:platform_synthetic_disclosure_receipt_open")
        else:
            if not str(item.get("title") or "").strip() or not str(item.get("body") or "").strip():
                errors.append(f"{prefix}:public_copy_missing")
            warnings.append("legacy_v1_0_copy_needs_platform_native_fields")
        fids, vids = item.get("fact_ids"), item.get("visual_ids")
        if not isinstance(fids, list) or not fids or not all(x in fact_ids for x in fids):
            errors.append(f"{prefix}:fact_ref_missing_or_unknown")
        if not isinstance(vids, list) or not vids or not all(x in visual_ids for x in vids):
            errors.append(f"{prefix}:visual_ref_missing_or_unknown")
        for key in ("editorial_angle", "humor_mechanism", "news_counterfactual", "video_counterfactual"):
            if not str(item.get(key) or "").strip():
                errors.append(f"{prefix}:{key}_required")
        angles.add(str(item.get("editorial_angle") or "").strip().casefold())
        mechanisms.add(str(item.get("humor_mechanism") or "").strip().casefold())
        if isinstance(fids, list) and any(
            fact.get("id") in fids and fact.get("classification") == "ALLEGATION_UNVERIFIED"
            for fact in facts
        ) and item.get("allegation_framing") != "ATTRIBUTED_UNVERIFIED":
            errors.append(f"{prefix}:allegation_framing_not_protected")

        review = item.get("independent_review", {"status": "PENDING"})
        if not isinstance(review, dict):
            errors.append(f"{prefix}:review_not_object")
            continue
        if review.get("status") == "PASS":
            checks = review.get("semantic_checks")
            if (review.get("reviewer_kind") != "HUMAN"
                or not review.get("reviewer_ref")
                or review.get("reviewer_ref") == case.get("author_ref")
                or review.get("copy_sha256") != copy_digest(item)
                or not review.get("evidence_ref")
                or not isinstance(checks, dict)
                or any(checks.get(key) is not True for key in SEMANTIC_TESTS)):
                errors.append(f"{prefix}:invalid_or_stale_independent_review")
            else:
                independent_reviews += 1
        elif review.get("status") == "FAIL":
            gates.append(f"{prefix}:editorial_rewrite_required")
        elif review.get("status") in {"PENDING", "MODEL_PLAN_ONLY"}:
            gates.append(f"{prefix}:semantic_review_open")
        else:
            errors.append(f"{prefix}:unknown_review_state")

    if len(copies) >= 3 and (len(angles) < 2 or len(mechanisms) < 2):
        warnings.append("platform_angles_or_mechanisms_look_template_based")
    if not case.get("editorial_plan_ref"):
        gates.append("editorial_plan_version_unbound")
    if not case.get("master_timeline_ref"):
        gates.append("master_timeline_version_unbound")
    status = ("INVALID_CONTRACT" if errors else
              "EDITORIAL_CANDIDATE_GATES_OPEN" if gates else
              "REVIEW_RECORDS_PRESENT_NOT_RELEASE_AUTHORIZED")
    return {
        "status": status, "contract_valid": not errors,
        "program_id": case.get("program_id"), "episode_id": case.get("episode_id"),
        "platform_count": len(copies),
        "independent_human_reviews_recorded": independent_reviews,
        "errors": sorted(set(errors)), "open_gates": sorted(set(gates)),
        "warnings": sorted(set(warnings)),
        "release_authorized": False, "semantic_quality_proven": False,
        "note": "Readback of metadata cannot prove watched-film meaning, source truth, reviewer identity, rights or publication. Existing Video promotion/release gate stays authoritative.",
    }
