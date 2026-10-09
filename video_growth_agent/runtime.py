from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
import json

from .models import Approval, ArtifactRecord, AssetRecord, QAReport, ProjectState
from .orchestrator import GateBlocked, StudioOrchestrator
from .roles import RoleRegistry
from .storage import ProjectStore
from .resources import data_path


class StudioRuntime:
    """Executable authority for project checkpoints, sign-offs and evidence receipts."""

    REQUIRED_MEDIA_QA_CHECKS = {"video_stream", "stream_duration_match", "true_peak", "black_frames"}
    PROCESS_ENFORCED_STAGES = {"LOOKDEV", "VISUAL_PREVIEW", "ROUGH_CUT", "RELEASE"}

    def __init__(self, store: ProjectStore | None = None, orchestrator: StudioOrchestrator | None = None, roles: RoleRegistry | None = None):
        self.store = store or ProjectStore()
        self.orchestrator = orchestrator or StudioOrchestrator()
        self.roles = roles or RoleRegistry()
        self.quality_rubric = json.loads(data_path("quality-rubric.json").read_text(encoding="utf-8"))
        self.execution_plan = json.loads(data_path("execution-plan.json").read_text(encoding="utf-8"))
        errors = self.roles.validate_workflow()
        if errors:
            raise ValueError("Invalid role/workflow configuration: " + "; ".join(errors))

    def create_project(self, project_id: str, title: str = "", metadata: dict[str, Any] | None = None) -> ProjectState:
        return self.store.create(project_id, title=title, metadata=metadata)

    def state(self, project_id: str) -> ProjectState:
        return self.store.load(project_id)

    def current_prompts(self, project_id: str) -> dict[str, str]:
        state = self.state(project_id)
        return {role: self.roles.get(role).prompt for role in self.orchestrator.required_roles(state.stage)}

    def review_packet(self, project_id: str, role: str) -> dict[str, Any]:
        """Return a blind review packet without other reviewers' verdicts."""
        state = self.state(project_id)
        if role not in self.orchestrator.required_roles(state.stage):
            raise ValueError(f"Role {role!r} is not required at stage {state.stage}")
        stage_spec = self.orchestrator.stage_spec(state.stage)
        artifact_names = list(stage_spec.get("required_artifacts", []))
        artifacts = {name: asdict(state.artifacts[name]) for name in artifact_names if name in state.artifacts}
        quality = self.quality_rubric.get("stages", {}).get(state.stage)
        return {"project_id": state.project_id, "stage": state.stage, "role": role, "prompt": self.roles.get(role).prompt, "required_artifacts": artifacts, "quality_rubric": quality, "prior_role_verdicts_hidden": True}

    def sign(self, project_id: str, role: str, decision: str, notes: str = "", evidence: tuple[str, ...] = (), findings: tuple[str, ...] = (), scorecard: dict[str, float] | None = None, benchmark_refs: tuple[str, ...] = (), target_digest: str | None = None, blind_review: bool = False) -> str:
        state = self.state(project_id)
        approval = Approval(role=role, decision=decision, notes=notes, evidence=evidence, findings=findings, scorecard=scorecard or {}, benchmark_refs=benchmark_refs, target_digest=target_digest, blind_review=blind_review)  # type: ignore[arg-type]
        self.orchestrator.sign(state, approval)
        receipt = self.store.append_receipt(project_id, "ROLE_REVIEW", {"stage": state.stage, "approval": asdict(approval)})
        self.store.save(state)
        return receipt

    def advance(self, project_id: str) -> str:
        state = self.state(project_id)
        process = self.process_guard_report(state)
        machine = self.machine_guard_report(state)
        if not process["pass"] or not machine["pass"]:
            raise GateBlocked(
                json.dumps(
                    {
                        "stage": state.stage,
                        "process_guards": process["guards"],
                        "process_failures": process["failures"],
                        "machine_guards": machine["guards"],
                        "machine_failures": machine["failures"],
                        "pass": False,
                    },
                    ensure_ascii=False,
                )
            )
        before = state.stage
        after = self.orchestrator.advance(state)
        self.store.append_receipt(project_id, "STAGE_ADVANCED", {"from": before, "to": after})
        self.store.save(state)
        return after

    def gate_report(self, project_id: str) -> dict:
        state = self.state(project_id)
        role_artifact = self.orchestrator.gate_report(state)
        machine = self.machine_guard_report(state)
        return {**role_artifact, "machine_guards": machine["guards"], "machine_failures": machine["failures"], "pass": role_artifact["pass"] and machine["pass"]}

    def process_guard_report(self, state: ProjectState) -> dict[str, Any]:
        """Require durable AgenticStudio proof before quality-critical stage advancement.

        This intentionally lives below AgenticStudio.advance so a caller cannot bypass the
        specialist execution contract by invoking StudioRuntime.advance directly.
        """
        stage = state.stage
        if stage not in self.PROCESS_ENFORCED_STAGES:
            return {"stage": stage, "guards": [], "failures": [], "pass": True}

        stage_plan = self.execution_plan.get("stages", {}).get(stage)
        if not isinstance(stage_plan, dict):
            return {
                "stage": stage,
                "guards": ["agent_work_order_proof"],
                "failures": [f"process_execution_plan_missing:{stage}"],
                "pass": False,
            }

        failures: list[str] = []
        guards = ["agent_work_order_proof", "review_input_digest_binding", "producer_output_provenance"]
        stage_approvals = state.approvals.get(stage, {})
        quality_spec = self.quality_rubric.get("stages", {}).get(stage)
        quality_target_name = quality_spec.get("target_artifact") if isinstance(quality_spec, dict) else None
        quality_target = state.artifacts.get(quality_target_name) if quality_target_name else None
        quality_roles = set(quality_spec.get("roles", {})) if isinstance(quality_spec, dict) else set()

        for task in stage_plan.get("tasks", []):
            task_id = str(task.get("id", ""))
            if not task_id:
                failures.append("process_task_id_missing")
                continue
            path = self.store.project_dir(state.project_id) / "work_orders" / stage / f"{task_id}.json"
            if not path.exists():
                failures.append(f"process_work_order_missing:{task_id}")
                continue
            try:
                order = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                failures.append(f"process_work_order_unreadable:{task_id}")
                continue

            expected_pairs = {
                "project_id": state.project_id,
                "stage": stage,
                "task_id": task_id,
                "executor": task.get("executor"),
                "task_type": task.get("type"),
                "agent_id": task.get("agent"),
                "tool": task.get("tool"),
                "approval_role": task.get("approval_role"),
                "blind": bool(task.get("blind", False)),
            }
            for key, expected in expected_pairs.items():
                actual = order.get(key)
                if actual != expected:
                    failures.append(f"process_work_order_contract_mismatch:{task_id}:{key}")
            if order.get("status") != "COMPLETED":
                failures.append(f"process_work_order_incomplete:{task_id}:{order.get('status')}")
                continue

            task_type = task.get("type")
            work_order_id = order.get("work_order_id")
            result = order.get("result") if isinstance(order.get("result"), dict) else {}

            if task_type in {"produce", "measure"}:
                for output_name in task.get("outputs", []):
                    artifact = state.artifacts.get(output_name)
                    if artifact is None:
                        failures.append(f"process_output_missing:{task_id}:{output_name}")
                        continue
                    if artifact.metadata.get("work_order_id") != work_order_id:
                        failures.append(f"process_output_provenance_mismatch:{task_id}:{output_name}")

            if task_type in {"review", "meta_review"}:
                input_digests = result.get("input_digests")
                if not isinstance(input_digests, dict):
                    failures.append(f"process_review_input_digests_missing:{task_id}")
                    input_digests = {}
                for input_name in task.get("inputs", []):
                    artifact = state.artifacts.get(input_name)
                    if artifact is None:
                        failures.append(f"process_review_input_missing:{task_id}:{input_name}")
                        continue
                    if input_name not in input_digests:
                        failures.append(f"process_review_input_digest_unbound:{task_id}:{input_name}")
                    elif input_digests.get(input_name) != artifact.digest:
                        failures.append(f"process_review_input_digest_mismatch:{task_id}:{input_name}")

                approval_role = task.get("approval_role")
                if approval_role:
                    approval = stage_approvals.get(approval_role)
                    if approval is None:
                        failures.append(f"process_role_receipt_missing:{task_id}:{approval_role}")
                    else:
                        if approval.decision != result.get("decision"):
                            failures.append(f"process_role_decision_mismatch:{task_id}:{approval_role}")
                        if bool(task.get("blind", False)) and not approval.blind_review:
                            failures.append(f"process_blind_receipt_missing:{task_id}:{approval_role}")
                        if approval_role in quality_roles:
                            if quality_target is None or not quality_target.digest:
                                failures.append(f"process_quality_target_missing:{task_id}:{quality_target_name}")
                            elif result.get("target_digest") != quality_target.digest or approval.target_digest != quality_target.digest:
                                failures.append(f"process_quality_target_digest_mismatch:{task_id}:{approval_role}")

        return {"stage": stage, "guards": guards, "failures": failures, "pass": not failures}

    def machine_guard_report(self, state: ProjectState) -> dict:
        guards = list(self.orchestrator.stage_spec(state.stage).get("machine_guards", []))
        failures: list[str] = []
        for guard in guards:
            if guard == "latest_media_qa_hard_pass":
                qa_payload = self._latest_qa_payload(state)
                target_name = "final_media" if state.stage == "RELEASE" else "final_candidate"
                target = state.artifacts.get(target_name)
                if qa_payload is None or qa_payload.get("hard_pass") is not True:
                    failures.append("latest_media_qa_hard_pass")
                elif not self._qa_evidence_is_complete(qa_payload):
                    failures.append("latest_media_qa_incomplete")
                elif target is None or not self._qa_matches_artifact(qa_payload, target):
                    failures.append(f"latest_media_qa_target_mismatch:{target_name}")
            elif guard == "quality_scorecard_hard_pass":
                failures.extend(self._quality_scorecard_failures(state))
            elif guard == "no_unknown_final_rights":
                unknown = [asset.asset_id for asset in state.assets.values() if asset.used_in_final and asset.rights_status == "UNKNOWN"]
                if unknown:
                    failures.append("no_unknown_final_rights:" + ",".join(sorted(unknown)))
            else:
                failures.append("unknown_machine_guard:" + guard)
        return {"stage": state.stage, "guards": guards, "failures": failures, "pass": not failures}

    def _quality_scorecard_failures(self, state: ProjectState) -> list[str]:
        spec = self.quality_rubric.get("stages", {}).get(state.stage)
        if not isinstance(spec, dict):
            return [f"quality_rubric_missing:{state.stage}"]
        target_name = spec.get("target_artifact")
        target = state.artifacts.get(target_name) if target_name else None
        failures: list[str] = []
        if target is None:
            return [f"quality_target_missing:{target_name}"]
        if spec.get("require_target_digest") and not target.digest:
            failures.append(f"quality_target_digest_missing:{target_name}")
        stage_approvals = state.approvals.get(state.stage, {})
        deferred = [str(x).lower() for x in self.quality_rubric.get("deferred_pass_phrases", [])]
        for role, rspec in spec.get("roles", {}).items():
            approval = stage_approvals.get(role)
            if approval is None or approval.decision != "PASS":
                continue
            if spec.get("blind_review_required") and not approval.blind_review:
                failures.append(f"quality_blind_review_required:{role}")
            if spec.get("require_target_digest") and approval.target_digest != target.digest:
                failures.append(f"quality_target_digest_mismatch:{role}")
            min_bench = int(spec.get("min_benchmarks", 0))
            if len(set(approval.benchmark_refs)) < min_bench:
                failures.append(f"quality_benchmark_count:{role}:{len(set(approval.benchmark_refs))}<{min_bench}")
            min_evidence = int(spec.get("required_evidence_min", 0))
            if len(set(approval.evidence)) < min_evidence:
                failures.append(f"quality_evidence_count:{role}:{len(set(approval.evidence))}<{min_evidence}")
            dims = list(rspec.get("dimensions", []))
            min_each = float(rspec.get("min_each", 0))
            vals: list[float] = []
            for dim in dims:
                if dim not in approval.scorecard:
                    failures.append(f"quality_score_missing:{role}:{dim}")
                    continue
                val = float(approval.scorecard[dim])
                vals.append(val)
                if val < min_each:
                    failures.append(f"quality_score_below_floor:{role}:{dim}:{val:g}<{min_each:g}")
            if vals and len(vals) == len(dims):
                avg = sum(vals) / len(vals)
                min_avg = float(rspec.get("min_average", min_each))
                if avg < min_avg:
                    failures.append(f"quality_average_below_floor:{role}:{avg:.2f}<{min_avg:g}")
            if spec.get("forbid_deferred_pass"):
                text = (approval.notes + " " + " ".join(approval.findings)).lower()
                phrase = next((x for x in deferred if x and x in text), None)
                if phrase:
                    failures.append(f"quality_deferred_pass_language:{role}:{phrase}")
        return failures

    @classmethod
    def _qa_evidence_is_complete(cls, qa_payload: dict[str, Any]) -> bool:
        metadata = qa_payload.get("metadata") if isinstance(qa_payload.get("metadata"), dict) else {}
        if metadata.get("checker") != "ffmpeg-ffprobe-v0.2":
            return False
        checks = qa_payload.get("checks")
        if not isinstance(checks, list):
            return False
        ids = {item.get("check_id") for item in checks if isinstance(item, dict)}
        return cls.REQUIRED_MEDIA_QA_CHECKS.issubset(ids)

    @staticmethod
    def _qa_matches_artifact(qa_payload: dict[str, Any], target: ArtifactRecord) -> bool:
        qa_meta = qa_payload.get("metadata") if isinstance(qa_payload.get("metadata"), dict) else {}
        qa_digest = qa_meta.get("sha256")
        if target.digest:
            return bool(qa_digest) and target.digest == qa_digest
        return qa_payload.get("media_uri") == target.uri

    def _latest_qa_payload(self, state: ProjectState) -> dict[str, Any] | None:
        if not state.qa_receipts:
            return None
        rel = state.qa_receipts[-1]
        path = self.store.project_dir(state.project_id) / rel
        if not path.exists():
            return None
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if receipt.get("event") != "MEDIA_QA":
            return None
        payload = receipt.get("payload")
        return payload if isinstance(payload, dict) else None

    def invalidate_from(self, project_id: str, stage: str, reason: str) -> None:
        state = self.state(project_id)
        old_stage = state.stage
        self.orchestrator.invalidate_from(state, stage)
        self.store.append_receipt(project_id, "DOWNSTREAM_INVALIDATED", {"from_stage": old_stage, "invalidate_from": stage, "reason": reason})
        self.store.save(state)

    def record_artifact(self, project_id: str, name: str, uri: str, stage: str, kind: str = "document", digest: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        state = self.state(project_id)
        if stage not in self.orchestrator.index:
            raise ValueError(f"Unknown artifact stage: {stage}")
        new = ArtifactRecord(name=name, uri=uri, stage=stage, kind=kind, digest=digest, metadata=metadata or {})
        old = state.artifacts.get(name)
        changed = old is not None and (old.uri != new.uri or old.digest != new.digest or old.metadata != new.metadata)
        state.artifacts[name] = new
        if changed and self.orchestrator.index[state.stage] >= self.orchestrator.index[stage]:
            self.orchestrator.invalidate_from(state, stage)
        else:
            state.touch()
        receipt = self.store.append_receipt(project_id, "ARTIFACT_RECORDED", {"artifact": asdict(new), "changed_existing": changed})
        self.store.save(state)
        return receipt

    def record_asset(self, project_id: str, asset: AssetRecord) -> str:
        state = self.state(project_id)
        previous = state.assets.get(asset.asset_id)
        state.assets[asset.asset_id] = asset
        if previous != asset and self.orchestrator.index[state.stage] >= self.orchestrator.index["ASSET_BUILD"]:
            self.orchestrator.invalidate_from(state, "ASSET_BUILD")
        else:
            state.touch()
        receipt = self.store.append_receipt(project_id, "ASSET_RECORDED", {"asset": asdict(asset)})
        self.store.save(state)
        return receipt

    def unknown_final_rights(self, project_id: str) -> list[str]:
        state = self.state(project_id)
        return [asset.asset_id for asset in state.assets.values() if asset.used_in_final and asset.rights_status == "UNKNOWN"]

    def record_qa(self, project_id: str, report: QAReport) -> str:
        state = self.state(project_id)
        receipt = self.store.append_receipt(project_id, "MEDIA_QA", report.to_dict())
        state.qa_receipts.append(receipt)
        state.artifacts["technical_qa"] = ArtifactRecord(name="technical_qa", uri=receipt, stage="TECH_QA", kind="qa_report", metadata={"hard_pass": report.hard_pass, "media_uri": report.media_uri})
        state.touch()
        self.store.save(state)
        return receipt
