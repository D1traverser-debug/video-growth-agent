from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from .editorial_planning import EditorialPlan
from .media_graph import AssetRef, AssetVersion, MediaGraph


class PlanGraphBridgeError(ValueError):
    pass


def editorial_plan_digest(plan: EditorialPlan) -> str:
    payload = json.dumps(asdict(plan), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=list).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def editorial_plan_asset_ref(plan: EditorialPlan) -> AssetRef:
    return AssetRef(asset_id=f"editorial-plan:{plan.intent.episode_id}", version_id=plan.plan_version)


def register_editorial_plan_asset(
    graph: MediaGraph,
    *,
    plan: EditorialPlan,
    context_id: str,
    uri: str,
    rights_refs: tuple[str, ...] = (),
    provenance_refs: tuple[str, ...] = (),
) -> AssetRef:
    """Register one immutable editorial-plan version in the existing MediaGraph.

    Production assets/tasks can bind this AssetRef as an input/derived_from edge. A
    later plan version does not mutate the old version; invalidating the old plan can
    mechanically stale its downstream production assets.
    """
    if context_id not in graph.contexts:
        raise PlanGraphBridgeError(f"plan context missing: {context_id}")
    if not uri.strip():
        raise PlanGraphBridgeError("durable plan uri is required")
    ref = editorial_plan_asset_ref(plan)
    graph.add_asset(
        AssetVersion(
            ref=ref,
            context_id=context_id,
            kind="EDITORIAL_PLAN",
            uri=uri,
            digest=editorial_plan_digest(plan),
            rights_refs=rights_refs,
            provenance_refs=provenance_refs,
            metadata={
                "episode_id": plan.intent.episode_id,
                "series_id": plan.intent.series_id,
                "plan_ref": plan.plan_ref,
            },
        )
    )
    return ref
