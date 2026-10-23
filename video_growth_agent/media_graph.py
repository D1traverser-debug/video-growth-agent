from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping


class MediaGraphError(ValueError):
    pass


CONTEXT_KINDS = {"PROGRAM", "SERIES", "EPISODE", "SEQUENCE", "SCENE", "SHOT", "TAKE"}
ASSET_STATES = {"CANDIDATE", "PROMOTED", "REJECTED", "STALE", "RETIRED"}
TASK_STATES = {"PLANNED", "READY", "RUNNING", "COMPLETED", "BLOCKED", "CANCELLED"}


@dataclass(frozen=True, order=True)
class AssetRef:
    asset_id: str
    version_id: str

    def __post_init__(self) -> None:
        if not self.asset_id.strip() or not self.version_id.strip():
            raise MediaGraphError("asset_id and version_id are required")

    def key(self) -> str:
        return f"{self.asset_id}@{self.version_id}"

    @classmethod
    def from_key(cls, value: str) -> "AssetRef":
        asset_id, sep, version_id = value.partition("@")
        if not sep:
            raise MediaGraphError(f"invalid asset ref key: {value}")
        return cls(asset_id=asset_id, version_id=version_id)


@dataclass(frozen=True)
class ContextRecord:
    context_id: str
    kind: str
    parent_context_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.context_id.strip():
            raise MediaGraphError("context_id is required")
        if self.kind not in CONTEXT_KINDS:
            raise MediaGraphError(f"unsupported context kind: {self.kind}")
        if self.parent_context_id == self.context_id:
            raise MediaGraphError("context cannot parent itself")


@dataclass(frozen=True)
class AssetVersion:
    ref: AssetRef
    context_id: str
    kind: str
    uri: str
    digest: str
    state: str = "CANDIDATE"
    derived_from: tuple[AssetRef, ...] = ()
    rights_refs: tuple[str, ...] = ()
    consent_refs: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.context_id.strip() or not self.kind.strip() or not self.uri.strip() or not self.digest.strip():
            raise MediaGraphError("asset context/kind/uri/digest are required")
        if self.state not in ASSET_STATES:
            raise MediaGraphError(f"unsupported asset state: {self.state}")
        if self.ref in self.derived_from:
            raise MediaGraphError("asset cannot derive from itself")


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    subject_type: str
    subject_id: str
    action: str
    refs: tuple[str, ...]
    observed_at: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (
                self.evidence_id,
                self.subject_type,
                self.subject_id,
                self.action,
                self.observed_at,
            )
        ):
            raise MediaGraphError("evidence identity/subject/action/time are required")
        if not self.refs:
            raise MediaGraphError("evidence requires durable refs")


@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    decision_type: str
    owner: str
    subject_refs: tuple[str, ...]
    criteria_refs: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    result: str
    decided_at: str
    notes: str = ""

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (
                self.decision_id,
                self.decision_type,
                self.owner,
                self.result,
                self.decided_at,
            )
        ):
            raise MediaGraphError("decision identity/type/owner/result/time are required")
        if not self.subject_refs:
            raise MediaGraphError("decision requires subject_refs")
        if not self.criteria_refs:
            raise MediaGraphError("decision requires declared criteria")
        if not self.evidence_ids:
            raise MediaGraphError("decision requires evidence")


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    context_id: str
    task_type: str
    input_assets: tuple[AssetRef, ...] = ()
    output_assets: tuple[AssetRef, ...] = ()
    depends_on: tuple[str, ...] = ()
    state: str = "PLANNED"
    executor_ref: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.context_id.strip() or not self.task_type.strip():
            raise MediaGraphError("task_id, context_id and task_type are required")
        if self.state not in TASK_STATES:
            raise MediaGraphError(f"unsupported task state: {self.state}")
        if self.task_id in self.depends_on:
            raise MediaGraphError("task cannot depend on itself")


class MediaGraph:
    """Owner-native graph for stable media context, assets, evidence, tasks and decisions.

    Records are append-only by identity. Promotion/current-state pointers may change, but old
    asset versions and decisions remain inspectable. This is intentionally independent of any
    provider, editor or repository filename convention.
    """

    def __init__(self) -> None:
        self.contexts: dict[str, ContextRecord] = {}
        self.assets: dict[AssetRef, AssetVersion] = {}
        self.evidence: dict[str, EvidenceRecord] = {}
        self.decisions: dict[str, DecisionRecord] = {}
        self.tasks: dict[str, TaskRecord] = {}
        self.promoted_versions: dict[str, str] = {}
        self.asset_state_overrides: dict[AssetRef, str] = {}

    def add_context(self, record: ContextRecord) -> None:
        if record.context_id in self.contexts:
            raise MediaGraphError(f"context already exists: {record.context_id}")
        if record.parent_context_id and record.parent_context_id not in self.contexts:
            raise MediaGraphError(f"parent context missing: {record.parent_context_id}")
        self.contexts[record.context_id] = record
        self._assert_context_acyclic()

    def add_asset(self, record: AssetVersion) -> None:
        if record.ref in self.assets:
            raise MediaGraphError(f"asset version already exists: {record.ref.key()}")
        if record.context_id not in self.contexts:
            raise MediaGraphError(f"asset context missing: {record.context_id}")
        missing = [ref.key() for ref in record.derived_from if ref not in self.assets]
        if missing:
            raise MediaGraphError("derived source assets missing: " + ",".join(missing))
        self.assets[record.ref] = record
        self._assert_asset_lineage_acyclic()

    def add_evidence(self, record: EvidenceRecord) -> None:
        if record.evidence_id in self.evidence:
            raise MediaGraphError(f"evidence already exists: {record.evidence_id}")
        self.evidence[record.evidence_id] = record

    def add_task(self, record: TaskRecord) -> None:
        if record.task_id in self.tasks:
            raise MediaGraphError(f"task already exists: {record.task_id}")
        if record.context_id not in self.contexts:
            raise MediaGraphError(f"task context missing: {record.context_id}")
        missing_inputs = [ref.key() for ref in record.input_assets if ref not in self.assets]
        if missing_inputs:
            raise MediaGraphError("task input assets missing: " + ",".join(missing_inputs))
        missing_outputs = [ref.key() for ref in record.output_assets if ref not in self.assets]
        if missing_outputs:
            raise MediaGraphError("task output assets missing: " + ",".join(missing_outputs))
        missing_dependencies = [task for task in record.depends_on if task not in self.tasks]
        if missing_dependencies:
            raise MediaGraphError("task dependencies missing: " + ",".join(missing_dependencies))
        self.tasks[record.task_id] = record
        self._assert_task_acyclic()

    def add_decision(self, record: DecisionRecord) -> None:
        if record.decision_id in self.decisions:
            raise MediaGraphError(f"decision already exists: {record.decision_id}")
        missing = [eid for eid in record.evidence_ids if eid not in self.evidence]
        if missing:
            raise MediaGraphError("decision evidence missing: " + ",".join(missing))
        self.decisions[record.decision_id] = record

    def promote_asset(self, ref: AssetRef, *, decision_id: str) -> None:
        asset = self.assets.get(ref)
        if asset is None:
            raise MediaGraphError(f"asset missing: {ref.key()}")
        decision = self.decisions.get(decision_id)
        if decision is None:
            raise MediaGraphError(f"promotion decision missing: {decision_id}")
        if decision.result.upper() not in {"PROMOTE", "ACCEPT", "SELECT"}:
            raise MediaGraphError("promotion decision result is not promotive")
        if ref.key() not in decision.subject_refs:
            raise MediaGraphError("promotion decision does not bind the asset version")
        if self.asset_state(ref) in {"REJECTED", "RETIRED", "STALE"}:
            raise MediaGraphError("rejected/retired/stale asset cannot be promoted without a current version")
        prior_version = self.promoted_versions.get(ref.asset_id)
        if prior_version and prior_version != ref.version_id:
            self.asset_state_overrides[AssetRef(ref.asset_id, prior_version)] = "STALE"
        self.promoted_versions[ref.asset_id] = ref.version_id
        self.asset_state_overrides[ref] = "PROMOTED"

    def reject_asset(self, ref: AssetRef, *, decision_id: str) -> None:
        if ref not in self.assets:
            raise MediaGraphError(f"asset missing: {ref.key()}")
        decision = self.decisions.get(decision_id)
        if decision is None or decision.result.upper() not in {"REJECT", "REJECT_ALL", "FAIL"}:
            raise MediaGraphError("valid rejection decision required")
        if ref.key() not in decision.subject_refs:
            raise MediaGraphError("rejection decision does not bind the asset version")
        self.asset_state_overrides[ref] = "REJECTED"
        if self.promoted_versions.get(ref.asset_id) == ref.version_id:
            del self.promoted_versions[ref.asset_id]

    def asset_state(self, ref: AssetRef) -> str:
        asset = self.assets.get(ref)
        if asset is None:
            raise MediaGraphError(f"asset missing: {ref.key()}")
        return self.asset_state_overrides.get(ref, asset.state)

    def current_promoted(self, asset_id: str) -> AssetVersion | None:
        version_id = self.promoted_versions.get(asset_id)
        if version_id is None:
            return None
        return self.assets[AssetRef(asset_id, version_id)]

    def downstream_asset_closure(self, changed_ref: AssetRef) -> tuple[AssetRef, ...]:
        if changed_ref not in self.assets:
            raise MediaGraphError(f"asset missing: {changed_ref.key()}")
        affected: set[AssetRef] = set()
        frontier = [changed_ref]
        while frontier:
            current = frontier.pop()
            children = {
                ref
                for ref, asset in self.assets.items()
                if current in asset.derived_from
            }
            for task in self.tasks.values():
                if current in task.input_assets:
                    children.update(task.output_assets)
            for child in children:
                if child != changed_ref and child not in affected:
                    affected.add(child)
                    frontier.append(child)
        return tuple(sorted(affected))

    def invalidate_downstream(self, changed_ref: AssetRef) -> tuple[AssetRef, ...]:
        affected = self.downstream_asset_closure(changed_ref)
        for ref in affected:
            if self.asset_state(ref) not in {"REJECTED", "RETIRED"}:
                self.asset_state_overrides[ref] = "STALE"
                if self.promoted_versions.get(ref.asset_id) == ref.version_id:
                    del self.promoted_versions[ref.asset_id]
        return affected

    def to_dict(self) -> dict[str, Any]:
        return {
            "contexts": [asdict(item) for item in self.contexts.values()],
            "assets": [
                {
                    **asdict(item),
                    "ref": asdict(item.ref),
                    "derived_from": [asdict(ref) for ref in item.derived_from],
                }
                for item in self.assets.values()
            ],
            "evidence": [asdict(item) for item in self.evidence.values()],
            "decisions": [asdict(item) for item in self.decisions.values()],
            "tasks": [
                {
                    **asdict(item),
                    "input_assets": [asdict(ref) for ref in item.input_assets],
                    "output_assets": [asdict(ref) for ref in item.output_assets],
                }
                for item in self.tasks.values()
            ],
            "promoted_versions": dict(self.promoted_versions),
            "asset_state_overrides": {
                ref.key(): state for ref, state in self.asset_state_overrides.items()
            },
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "MediaGraph":
        graph = cls()
        for raw in payload.get("contexts", []):
            graph.add_context(ContextRecord(**raw))
        for raw in payload.get("assets", []):
            item = dict(raw)
            item["ref"] = AssetRef(**item["ref"])
            item["derived_from"] = tuple(AssetRef(**ref) for ref in item.get("derived_from", []))
            graph.add_asset(AssetVersion(**item))
        for raw in payload.get("evidence", []):
            graph.add_evidence(EvidenceRecord(**raw))
        for raw in payload.get("tasks", []):
            item = dict(raw)
            item["input_assets"] = tuple(AssetRef(**ref) for ref in item.get("input_assets", []))
            item["output_assets"] = tuple(AssetRef(**ref) for ref in item.get("output_assets", []))
            graph.add_task(TaskRecord(**item))
        for raw in payload.get("decisions", []):
            graph.add_decision(DecisionRecord(**raw))
        graph.promoted_versions = {str(k): str(v) for k, v in payload.get("promoted_versions", {}).items()}
        graph.asset_state_overrides = {
            AssetRef.from_key(key): str(state)
            for key, state in payload.get("asset_state_overrides", {}).items()
        }
        return graph

    def _assert_context_acyclic(self) -> None:
        for start in self.contexts:
            seen: set[str] = set()
            current: str | None = start
            while current:
                if current in seen:
                    raise MediaGraphError(f"context cycle detected at {current}")
                seen.add(current)
                record = self.contexts.get(current)
                current = record.parent_context_id if record else None

    def _assert_asset_lineage_acyclic(self) -> None:
        def visit(ref: AssetRef, stack: set[AssetRef], done: set[AssetRef]) -> None:
            if ref in done:
                return
            if ref in stack:
                raise MediaGraphError(f"asset lineage cycle detected at {ref.key()}")
            stack.add(ref)
            for parent in self.assets[ref].derived_from:
                visit(parent, stack, done)
            stack.remove(ref)
            done.add(ref)

        done: set[AssetRef] = set()
        for ref in self.assets:
            visit(ref, set(), done)

    def _assert_task_acyclic(self) -> None:
        def visit(task_id: str, stack: set[str], done: set[str]) -> None:
            if task_id in done:
                return
            if task_id in stack:
                raise MediaGraphError(f"task dependency cycle detected at {task_id}")
            stack.add(task_id)
            for dependency in self.tasks[task_id].depends_on:
                visit(dependency, stack, done)
            stack.remove(task_id)
            done.add(task_id)

        done: set[str] = set()
        for task_id in self.tasks:
            visit(task_id, set(), done)


class MediaGraphStore:
    """Atomic JSON persistence for the canonical media graph metadata."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> MediaGraph:
        if not self.path.is_file():
            return MediaGraph()
        return MediaGraph.from_dict(json.loads(self.path.read_text(encoding="utf-8")))

    def save(self, graph: MediaGraph) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(graph.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.path)
