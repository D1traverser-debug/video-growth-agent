"""Source-linked news x video packaging checks; no new publisher or controller."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

PLATFORMS = frozenset({
    "X", "TIKTOK", "YOUTUBE", "XIAOHONGSHU",
    "WECHAT_CHANNELS", "BILIBILI", "DOUYIN",
})
FACT_CLASSES = frozenset({
    "PRIMARY_CONFIRMED", "ATTRIBUTED_REPORT", "ALLEGATION_UNVERIFIED",
})
VISUAL_MODES = frozenset({
    "FICTIONAL_SYNTHETIC", "EDITORIAL_REAL", "MIXED_DISCLOSED",
})
SYNTHETIC_MODES = frozenset({"FICTIONAL_SYNTHETIC", "MIXED_DISCLOSED"})
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
    "news_replacement_loses_meaning",
    "video_replacement_loses_meaning",
    "primary_satire_target_is_news",
    "visual_is_secondary_expression",
    "not_plot_recitation",
    "no_explanation_after_punchline",
    "natural_language",
    "platform_voice_is_native",
    "humor_mechanism_executes_in_copy",
    "not_generic_template",
    "fact_fiction_not_conflated",
    "unverified_claims_remain_attributed",
    "no_forced_keyword_insertion",
)
REVIEW_DIGEST_VERSION = "news-video-review-v2"
REVIEW_DIGEST_VERSION_V3 = "news-video-review-v3"
FORBIDDEN_PUBLIC_TYPE_LABELS = frozenset({"AI PARODY"})


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _digest(value: object) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def review_digest(case: Mapping[str, object], item: Mapping[str, object]) -> str:
    """Bind review to public text, editorial reasoning, and exact referenced inputs."""
    schema = case.get("schema_version")
    if schema in {"1.1", "1.2"}:
        public_content = item.get("public_fields")
    else:
        public_content = {
            "title": item.get("title"),
            "body": item.get("body"),
        }

    raw_facts = case.get("source_facts")
    raw_visuals = case.get("visual_assets")
    facts_by_id = {
        fact.get("id"): fact
        for fact in (raw_facts if isinstance(raw_facts, list) else [])
        if isinstance(fact, dict) and _nonempty(fact.get("id"))
    }
    visuals_by_id = {
        visual.get("id"): visual
        for visual in (raw_visuals if isinstance(raw_visuals, list) else [])
        if isinstance(visual, dict) and _nonempty(visual.get("id"))
    }
    fact_refs = item.get("fact_ids")
    visual_refs = item.get("visual_ids")
    selected_facts = [
        facts_by_id[ref] for ref in fact_refs
        if isinstance(ref, str) and ref in facts_by_id
    ] if isinstance(fact_refs, list) else []
    selected_visuals = [
        {
            key: value for key, value in visuals_by_id[ref].items()
            if key != "observed_this_session"
        }
        for ref in visual_refs
        if isinstance(ref, str) and ref in visuals_by_id
    ] if isinstance(visual_refs, list) else []

    binding = {
        "digest_version": (
            REVIEW_DIGEST_VERSION_V3 if schema == "1.2"
            else REVIEW_DIGEST_VERSION
        ),
        "schema_version": schema,
        "platform": item.get("platform"),
        "public_content": public_content,
        "editorial_reading": case.get("editorial_reading") if schema == "1.2" else None,
        "editorial_frame": {
            key: item.get(key) for key in (
                "editorial_angle", "humor_mechanism", "speaker_perspective",
                "satire_target", "semantic_bridge", "news_counterfactual",
                "video_counterfactual", "allegation_framing",
            )
        },
        "referenced_facts": selected_facts,
        "referenced_visuals": selected_visuals,
    }
    return _digest(binding)


def _invalid_root_report() -> dict[str, Any]:
    return {
        "status": "INVALID_CONTRACT",
        "contract_valid": False,
        "program_id": None,
        "episode_id": None,
        "platform_count": 0,
        "independent_human_reviews_recorded": 0,
        "errors": ["root_must_be_object"],
        "open_gates": [],
        "warnings": [],
        "release_authorized": False,
        "semantic_quality_proven": False,
        "note": "Malformed input is rejected as a structured contract error.",
    }


def audit_packaging(case: Mapping[str, object]) -> dict[str, Any]:
    """Validate references and review lineage; never self-certify truth, humor or release."""
    if not isinstance(case, Mapping):
        return _invalid_root_report()

    errors: list[str] = []
    gates: list[str] = []
    warnings: list[str] = []
    for field in ("program_id", "episode_id", "author_ref"):
        if not _nonempty(case.get(field)):
            errors.append(f"{field}_required")

    schema = case.get("schema_version")
    if not isinstance(schema, str) or schema not in ("1.0", "1.1", "1.2"):
        errors.append("unsupported_schema")

    raw_facts = case.get("source_facts")
    raw_visuals = case.get("visual_assets")
    raw_copies = case.get("platform_copies")
    for name, value in (
        ("source_facts", raw_facts),
        ("visual_assets", raw_visuals),
        ("platform_copies", raw_copies),
    ):
        if not isinstance(value, list) or not value or not all(
            isinstance(entry, dict) for entry in value
        ):
            errors.append(f"{name}_must_be_nonempty_objects")

    facts = [entry for entry in raw_facts if isinstance(entry, dict)] if isinstance(raw_facts, list) else []
    visuals = [entry for entry in raw_visuals if isinstance(entry, dict)] if isinstance(raw_visuals, list) else []
    copies = [entry for entry in raw_copies if isinstance(entry, dict)] if isinstance(raw_copies, list) else []

    fact_ids: set[str] = set()
    facts_by_id: dict[str, dict] = {}
    for fact in facts:
        ident = fact.get("id")
        if not _nonempty(ident):
            errors.append("fact_id_must_be_nonempty_string")
        elif ident in fact_ids:
            errors.append(f"{ident}:duplicate_fact_id")
        else:
            fact_ids.add(ident)
            facts_by_id[ident] = fact

        classification = fact.get("classification")
        if not isinstance(classification, str) or classification not in FACT_CLASSES:
            errors.append(f"{ident if _nonempty(ident) else 'fact'}:unknown_fact_classification")
        urls = fact.get("source_urls")
        if not isinstance(urls, list) or not urls or not all(
            isinstance(url, str) and url.startswith("https://") for url in urls
        ):
            errors.append(f"{ident if _nonempty(ident) else 'fact'}:https_source_required")
        if not _nonempty(fact.get("claim")):
            errors.append(f"{ident if _nonempty(ident) else 'fact'}:claim_required")

    visual_ids: set[str] = set()
    visuals_by_id: dict[str, dict] = {}
    has_synthetic_asset = False
    for visual in visuals:
        ident = visual.get("id")
        if not _nonempty(ident):
            errors.append("visual_id_must_be_nonempty_string")
        elif ident in visual_ids:
            errors.append(f"{ident}:duplicate_visual_id")
        else:
            visual_ids.add(ident)
            visuals_by_id[ident] = visual

        mode = visual.get("truth_mode")
        if not isinstance(mode, str) or mode not in VISUAL_MODES:
            errors.append(f"{ident if _nonempty(ident) else 'visual'}:unknown_visual_truth_mode")
        else:
            if mode in SYNTHETIC_MODES:
                has_synthetic_asset = True
                if visual.get("platform_disclosure") != "RECORDED":
                    gates.append(f"{ident}:platform_synthetic_disclosure_open")

        if not _nonempty(visual.get("source_ref")):
            errors.append(f"{ident if _nonempty(ident) else 'visual'}:source_ref_required")
        media_digest = visual.get("sha256")
        if media_digest is not None and (
            not isinstance(media_digest, str)
            or len(media_digest) != 64
            or any(char not in "0123456789abcdef" for char in media_digest.lower())
        ):
            errors.append(f"{ident if _nonempty(ident) else 'visual'}:invalid_sha256")
        if not media_digest:
            gates.append(f"{ident if _nonempty(ident) else 'visual'}:media_identity_unverified")
        if visual.get("rights_status") != "VERIFIED" or not _nonempty(visual.get("rights_evidence_ref")):
            gates.append(f"{ident if _nonempty(ident) else 'visual'}:rights_unverified")

    if has_synthetic_asset and case.get("fiction_is_not_real_world_evidence") is not True:
        errors.append("fiction_news_boundary_missing")

    if schema == "1.2":
        reading = case.get("editorial_reading")
        if not isinstance(reading, dict):
            errors.append("editorial_reading_must_be_object")
        else:
            for field in (
                "primary_satirical_target", "selected_observation", "visual_role",
                "fiction_boundary", "audience_assumption",
            ):
                if not _nonempty(reading.get(field)):
                    errors.append(f"editorial_reading:{field}_required")
            rejected = reading.get("rejected_angles")
            if not isinstance(rejected, list) or len(rejected) < 3 or not all(
                _nonempty(value) for value in rejected
            ):
                errors.append("editorial_reading:at_least_three_rejected_angles_required")
            if reading.get("layer_order") != ["FACT", "INTENT", "VISUAL", "PLATFORM"]:
                errors.append("editorial_reading:fact_intent_visual_platform_order_required")

    platforms: set[str] = set()
    angles: set[str] = set()
    mechanisms: set[str] = set()
    creative_signatures: set[tuple[str, str, str]] = set()
    independent_reviews = 0

    for index, item in enumerate(copies):
        prefix = f"copy[{index}]"
        platform = item.get("platform")
        valid_platform = isinstance(platform, str) and platform in PLATFORMS
        if not valid_platform:
            errors.append(f"{prefix}:unknown_platform")
        elif platform in platforms:
            errors.append(f"{prefix}:duplicate_platform")
        else:
            platforms.add(platform)

        if schema in {"1.1", "1.2"}:
            if "title" in item or "body" in item:
                errors.append(f"{prefix}:native_case_mixes_legacy_title_body")
            public_fields = item.get("public_fields")
            required_fields = PUBLIC_FIELDS.get(platform, ()) if valid_platform else ()
            if not isinstance(public_fields, dict) or any(
                not _nonempty(public_fields.get(key)) for key in required_fields
            ):
                errors.append(f"{prefix}:platform_public_fields_missing_or_invalid")
            if isinstance(public_fields, dict) and "tags" in public_fields and not (
                isinstance(public_fields["tags"], list)
                and all(isinstance(tag, str) for tag in public_fields["tags"])
            ):
                errors.append(f"{prefix}:tags_must_be_string_list")
            if schema == "1.2" and isinstance(public_fields, dict):
                for label_field in ("tags", "labels", "type_labels", "categories"):
                    values = public_fields.get(label_field, [])
                    label_values = (
                        [values] if isinstance(values, str)
                        else values if isinstance(values, list)
                        else []
                    )
                    if any(
                        isinstance(value, str)
                        and value.strip().upper() in FORBIDDEN_PUBLIC_TYPE_LABELS
                        for value in label_values
                    ):
                        errors.append(f"{prefix}:forbidden_public_type_label")
            if not _nonempty(item.get("platform_variant_ref")):
                gates.append(f"{prefix}:platform_variant_version_unbound")
            if not _nonempty(item.get("format_review_evidence_ref")):
                gates.append(f"{prefix}:platform_format_review_open")
        elif schema == "1.0":
            if "public_fields" in item:
                errors.append(f"{prefix}:legacy_case_mixes_native_public_fields")
            if not _nonempty(item.get("title")) or not _nonempty(item.get("body")):
                errors.append(f"{prefix}:public_copy_missing")
            warnings.append("legacy_v1_0_copy_needs_platform_native_fields")

        fact_refs = item.get("fact_ids")
        valid_fact_refs = (
            isinstance(fact_refs, list)
            and bool(fact_refs)
            and all(_nonempty(ref) and ref in fact_ids for ref in fact_refs)
            and len(set(fact_refs)) == len(fact_refs)
        )
        if not valid_fact_refs:
            errors.append(f"{prefix}:fact_ref_missing_unknown_or_duplicate")

        visual_refs = item.get("visual_ids")
        valid_visual_refs = (
            isinstance(visual_refs, list)
            and bool(visual_refs)
            and all(_nonempty(ref) and ref in visual_ids for ref in visual_refs)
            and len(set(visual_refs)) == len(visual_refs)
        )
        if not valid_visual_refs:
            errors.append(f"{prefix}:visual_ref_missing_unknown_or_duplicate")

        required_frame_fields = [
            "editorial_angle", "humor_mechanism",
            "news_counterfactual", "video_counterfactual",
        ]
        if schema == "1.2":
            required_frame_fields.extend([
                "speaker_perspective", "satire_target", "semantic_bridge",
            ])
        for key in required_frame_fields:
            if not _nonempty(item.get(key)):
                errors.append(f"{prefix}:{key}_required")
        if _nonempty(item.get("editorial_angle")):
            angles.add(item["editorial_angle"].strip().casefold())
        if _nonempty(item.get("humor_mechanism")):
            mechanisms.add(item["humor_mechanism"].strip().casefold())
        if schema == "1.2" and _nonempty(item.get("humor_mechanism")) and _nonempty(
            item.get("speaker_perspective")
        ):
            creative_signatures.add((
                item["editorial_angle"].strip().casefold(),
                item["humor_mechanism"].strip().casefold(),
                item["speaker_perspective"].strip().casefold(),
            ))

        if valid_fact_refs and any(
            facts_by_id[ref].get("classification") == "ALLEGATION_UNVERIFIED"
            for ref in fact_refs
        ) and item.get("allegation_framing") != "ATTRIBUTED_UNVERIFIED":
            errors.append(f"{prefix}:allegation_framing_not_protected")

        copy_uses_synthetic = valid_visual_refs and any(
            isinstance(visuals_by_id[ref].get("truth_mode"), str)
            and visuals_by_id[ref].get("truth_mode") in SYNTHETIC_MODES
            for ref in visual_refs
        )
        if schema in {"1.1", "1.2"} and copy_uses_synthetic and not _nonempty(
            item.get("synthetic_upload_disclosure_ref")
        ):
            gates.append(f"{prefix}:platform_synthetic_disclosure_receipt_open")

        review = item.get("independent_review", {"status": "PENDING"})
        if not isinstance(review, dict):
            errors.append(f"{prefix}:review_not_object")
            continue
        review_status = review.get("status")
        if review_status == "PASS":
            checks = review.get("semantic_checks")
            if (
                not valid_fact_refs
                or not valid_visual_refs
                or review.get("reviewer_kind") != "HUMAN"
                or not _nonempty(review.get("reviewer_ref"))
                or review.get("reviewer_ref") == case.get("author_ref")
                or review.get("copy_sha256") != review_digest(case, item)
                or not _nonempty(review.get("evidence_ref"))
                or not isinstance(checks, dict)
                or any(checks.get(key) is not True for key in SEMANTIC_TESTS)
            ):
                errors.append(f"{prefix}:invalid_or_stale_independent_review")
            else:
                independent_reviews += 1
        elif review_status == "FAIL":
            gates.append(f"{prefix}:editorial_rewrite_required")
        elif review_status in ("PENDING", "MODEL_PLAN_ONLY"):
            gates.append(f"{prefix}:semantic_review_open")
        else:
            errors.append(f"{prefix}:unknown_review_state")

    if len(copies) >= 3:
        if schema == "1.2":
            minimum_distinct = (5 * len(copies) + 5) // 6
            if len(creative_signatures) < minimum_distinct:
                errors.append("platform_variants_not_substantively_distinct")
        elif len(angles) < 2 or len(mechanisms) < 2:
            warnings.append("platform_angles_or_mechanisms_look_template_based")
    if not _nonempty(case.get("editorial_plan_ref")):
        gates.append("editorial_plan_version_unbound")
    if not _nonempty(case.get("master_timeline_ref")):
        gates.append("master_timeline_version_unbound")

    status = (
        "INVALID_CONTRACT" if errors else
        "EDITORIAL_CANDIDATE_GATES_OPEN" if gates else
        "REVIEW_RECORDS_PRESENT_NOT_RELEASE_AUTHORIZED"
    )
    return {
        "status": status,
        "contract_valid": not errors,
        "program_id": case.get("program_id"),
        "episode_id": case.get("episode_id"),
        "platform_count": len(copies),
        "independent_human_reviews_recorded": independent_reviews,
        "errors": sorted(set(errors)),
        "open_gates": sorted(set(gates)),
        "warnings": sorted(set(warnings)),
        "release_authorized": False,
        "semantic_quality_proven": False,
        "note": "A review receipt is bound to the exact public copy, editorial frame, referenced facts and visual versions. Metadata still cannot prove source truth, authentic reviewer identity, watched-film meaning, rights or publication. Existing Video release admission remains authoritative.",
    }
