from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
import json

from .execution_attestation import ExecutionAttestation, ExecutionTrustRegistry, canonical_digest
from .models import Approval, ArtifactRecord, AssetRecord, QAReport, ProjectState
from .orchestrator import GateBlocked, StudioOrchestrator
from .roles import RoleRegistry
from .storage import ProjectStore
from .resources import data_path


class StudioRuntime:
    """Executable authority for project checkpoints, sign-offs and evidence receipts."""

    REQUIRED_MEDIA_QA_CHECKS = {"video_stream", "stream_duration_match", "true_peak", "black_frames"}
    PROCESS_ENFORCEMENT_POLICY = "ALL_EXECUTION_PLAN_TASK_STAGES"

    def __init__(
        self,
        store: ProjectStore | None = None,
        orchestrator: StudioOrchestrator | None = None,
        roles: RoleRegistry | None = None,
        execution_trust: ExecutionTrustRegistry | None = None,
    ):
        self.store = store or ProjectStore()
        self.orchestrator = orchestrator or StudioOrchestrator()
        self.roles = roles or RoleRegistry()
        self.execution_trust = execution_trust or ExecutionTrustRegistry()
        self.quality_rubric = json.loads(data_path("quality-rubric.json").read_text(encoding="utf-8"))
        self.execution_plan = json.loads(data_path("execution-plan.json").read_text(encoding="utf-8"))
        self.agents_config = json.loads(data_path("agents.json").read_text(encoding="utf-8"))
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
        process = self.process_guard_report(state)
        machine = self.machine_guard_report(state)
        return {
            **role_artifact,
            "process_guards": process["guards"],
            "process_failures": process["failures"],
            "machine_guards": machine["guards"],
            "machine_failures": machine["failures"],
            "pass": role_artifact["pass"] and process["pass"] and machine["pass"],
        }

    def _stage_task(self, stage: str, task_id: str) -> dict[str, Any] | None:
        stage_plan = self.execution_plan.get("stages", {}).get(stage, {})
        for task in stage_plan.get("tasks", []):
            if task.get("id") == task_id:
                return task
        return None

    def _work_order_path(self, state: ProjectState, task_id: str) -> Path:
        return self.store.project_dir(state.project_id) / "work_orders" / state.stage / f"{task_id}.json"

    def _load_work_order(self, state: ProjectState, task_id: str) -> dict[str, Any]:
        path = self._work_order_path(state, task_id)
        if not path.exists():
            raise FileNotFoundError(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid work order payload: {path}")
        return payload

    def _active_work_order_ids(self, state: ProjectState) -> set[str]:
        ids: set[str] = set()
        stage_plan = self.execution_plan.get("stages", {}).get(state.stage, {})
        for task in stage_plan.get("tasks", []):
            task_id = str(task.get("id") or "")
            if not task_id:
                continue
            path = self._work_order_path(state, task_id)
            if not path.exists():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            work_order_id = payload.get("work_order_id")
            if work_order_id:
                ids.add(str(work_order_id))
        return ids

    def _agent_prompt_digest(self, agent_id: str) -> str:
        raw = self.agents_config.get("agents", {}).get(agent_id)
        if not isinstance(raw, dict):
            return canonical_digest({"agent_id": agent_id, "missing": True})
        role = raw.get("role")
        role_prompt = self.roles.get(role).prompt if role else ""
        payload = {
            "agent_id": agent_id,
            "mandate": str(raw.get("mandate", "")).strip(),
            "role": role,
            "role_prompt": role_prompt,
        }
        return canonical_digest(payload)

    def _review_execution_contract(self, state: ProjectState, task: dict[str, Any], order: dict[str, Any]) -> dict[str, Any]:
        input_digests = {
            name: state.artifacts[name].digest if name in state.artifacts else None
            for name in task.get("inputs", [])
        }
        return {
            "project_id": state.project_id,
            "stage": state.stage,
            "task_id": task.get("id"),
            "work_order_id": order.get("work_order_id"),
            "wave": int(task.get("wave", 0)),
            "agent_id": task.get("agent"),
            "approval_role": task.get("approval_role"),
            "blind": bool(task.get("blind", False)),
            "task_type": task.get("type"),
            "agent_prompt_digest": self._agent_prompt_digest(str(task.get("agent") or "")),
            "input_digests": input_digests,
            "peer_chat_allowed": False,
            "project_approvals_hidden": bool(task.get("blind", False)),
        }

    def review_execution_contract(self, project_id: str, task_id: str) -> dict[str, Any]:
        """Return the immutable contract an external reviewer executor must attest to."""
        state = self.state(project_id)
        task = self._stage_task(state.stage, task_id)
        if task is None or task.get("type") not in {"review", "meta_review"}:
            raise ValueError(f"Unknown review task {state.stage}/{task_id}")
        order = self._load_work_order(state, task_id)
        contract = self._review_execution_contract(state, task, order)
        return {"contract": contract, "packet_digest": canonical_digest(contract)}

    def _review_receipt_matches(self, state: ProjectState, task_id: str, work_order_id: str, result: dict[str, Any]) -> bool:
        receipts_dir = self.store.project_dir(state.project_id) / "receipts"
        if not receipts_dir.exists():
            return False
        for path in receipts_dir.glob("*.json"):
            try:
                receipt = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if receipt.get("event") != "WORK_ORDER_REVIEW_COMPLETED":
                continue
            payload = receipt.get("payload") if isinstance(receipt.get("payload"), dict) else {}
            if payload.get("stage") != state.stage:
                continue
            if payload.get("task_id") != task_id or payload.get("work_order_id") != work_order_id:
                continue
            if payload.get("result") != result:
                continue
            if payload.get("input_digests") != result.get("input_digests"):
                continue
            return True
        return False

    def _execution_attestation_receipts(self, state: ProjectState) -> list[dict[str, Any]]:
        receipts_dir = self.store.project_dir(state.project_id) / "receipts"
        if not receipts_dir.exists():
            return []
        matches: list[dict[str, Any]] = []
        for path in receipts_dir.glob("*.json"):
            try:
                receipt = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if receipt.get("event") != "AGENT_EXECUTION_ATTESTED":
                continue
            payload = receipt.get("payload") if isinstance(receipt.get("payload"), dict) else {}
            if payload.get("stage") == state.stage:
                matches.append(payload)
        return matches

    def _execution_attestation_for(
        self,
        state: ProjectState,
        *,
        task_id: str,
        work_order_id: str,
    ) -> dict[str, Any] | None:
        candidates = [
            payload
            for payload in self._execution_attestation_receipts(state)
            if payload.get("task_id") == task_id and payload.get("work_order_id") == work_order_id
        ]
        if len(candidates) != 1:
            return None
        return candidates[0]

    def _attestation_validation_failures(
        self,
        state: ProjectState,
        task: dict[str, Any],
        order: dict[str, Any],
        result: dict[str, Any],
        payload: dict[str, Any],
    ) -> tuple[list[str], ExecutionAttestation | None]:
        task_id = str(task.get("id", ""))
        try:
            raw = payload.get("attestation")
            if not isinstance(raw, dict):
                return [f"process_execution_attestation_invalid:{task_id}"], None
            attestation = ExecutionAttestation.from_dict(raw)
        except (TypeError, ValueError):
            return [f"process_execution_attestation_invalid:{task_id}"], None

        if payload.get("attestation_digest") != attestation.digest:
            return [f"process_execution_attestation_digest_mismatch:{task_id}"], attestation

        contract = self._review_execution_contract(state, task, order)
        input_digests = result.get("input_digests") if isinstance(result.get("input_digests"), dict) else {}
        raw_failures = self.execution_trust.validate(
            attestation,
            stage=state.stage,
            work_order_id=str(order.get("work_order_id") or ""),
            agent_id=str(task.get("agent") or ""),
            packet_digest=canonical_digest(contract),
            result_digest=canonical_digest(result),
            input_digests=input_digests,
        )
        return [f"process_{failure}:{task_id}" for failure in raw_failures], attestation

    def _attestation_identity_failures(
        self,
        wave_attestations: dict[int, list[tuple[str, ExecutionAttestation]]],
    ) -> list[str]:
        failures: list[str] = []
        policy = self.execution_trust.policy
        fields = [
            ("execution_id", "require_unique_execution_id_within_wave"),
            ("provider_run_id", "require_unique_provider_run_id_within_wave"),
            ("context_id", "require_unique_context_id_within_wave"),
            ("trace_id", "require_unique_trace_id_within_wave"),
        ]
        for wave, items in wave_attestations.items():
            for field, policy_key in fields:
                if not policy.get(policy_key, True):
                    continue
                seen: dict[str, list[str]] = {}
                for task_id, attestation in items:
                    value = str(getattr(attestation, field, ""))
                    seen.setdefault(value, []).append(task_id)
                for value, task_ids in seen.items():
                    if value and len(task_ids) > 1:
                        failures.append(
                            f"process_execution_identity_reused:wave={wave}:{field}={value}:tasks={','.join(sorted(task_ids))}"
                        )
        return failures

    def record_execution_attestation(
        self,
        project_id: str,
        task_id: str,
        attestation: ExecutionAttestation | dict[str, Any],
    ) -> str:
        """Persist provider-backed proof for a completed isolated reviewer execution.

        Production defaults trust no executor. A provider adapter must first be explicitly
        registered in executors.json (or injected into the runtime) before its evidence can
        authorize a critical blind-review gate.
        """
        state = self.state(project_id)
        task = self._stage_task(state.stage, task_id)
        if task is None or task.get("type") not in {"review", "meta_review"}:
            raise ValueError(f"Unknown review task {state.stage}/{task_id}")
        order = self._load_work_order(state, task_id)
        if order.get("status") != "COMPLETED":
            raise ValueError(f"Review work order {task_id} must be COMPLETED before attestation")
        result = order.get("result") if isinstance(order.get("result"), dict) else {}
        input_digests = result.get("input_digests") if isinstance(result.get("input_digests"), dict) else {}
        item = attestation if isinstance(attestation, ExecutionAttestation) else ExecutionAttestation.from_dict(attestation)
        contract = self._review_execution_contract(state, task, order)
        failures = self.execution_trust.validate(
            item,
            stage=state.stage,
            work_order_id=str(order.get("work_order_id") or ""),
            agent_id=str(task.get("agent") or ""),
            packet_digest=canonical_digest(contract),
            result_digest=canonical_digest(result),
            input_digests=input_digests,
        )
        if failures:
            raise ValueError("Invalid execution attestation: " + "; ".join(failures))

        active_work_order_ids = self._active_work_order_ids(state)
        existing = self._execution_attestation_receipts(state)
        for payload in existing:
            if str(payload.get("work_order_id") or "") not in active_work_order_ids:
                continue
            raw = payload.get("attestation")
            if not isinstance(raw, dict):
                continue
            try:
                other = ExecutionAttestation.from_dict(raw)
            except (TypeError, ValueError):
                continue
            if payload.get("task_id") == task_id and payload.get("work_order_id") == order.get("work_order_id"):
                raise ValueError(f"Execution attestation already exists for active run {task_id}")
            other_task = self._stage_task(state.stage, str(payload.get("task_id") or ""))
            if not other_task or int(other_task.get("wave", 0)) != int(task.get("wave", 0)):
                continue
            for field, policy_key in (
                ("execution_id", "require_unique_execution_id_within_wave"),
                ("provider_run_id", "require_unique_provider_run_id_within_wave"),
                ("context_id", "require_unique_context_id_within_wave"),
                ("trace_id", "require_unique_trace_id_within_wave"),
            ):
                if self.execution_trust.policy.get(policy_key, True) and getattr(item, field) == getattr(other, field):
                    raise ValueError(f"Execution identity reused within blind-review wave: {field}={getattr(item, field)}")

        return self.store.append_receipt(
            project_id,
            "AGENT_EXECUTION_ATTESTED",
            {
                "stage": state.stage,
                "task_id": task_id,
                "work_order_id": order.get("work_order_id"),
                "wave": int(task.get("wave", 0)),
                "attestation_digest": item.digest,
                "attestation": item.to_dict(),
            },
        )

    def process_guard_report(self, state: ProjectState) -> dict[str, Any]:
        """Require durable AgenticStudio proof for every configured stage task.

        This intentionally lives below AgenticStudio.advance so a caller cannot bypass the
        specialist execution contract by invoking StudioRuntime.advance directly. Any stage
        with tasks in the execution plan is process-enforced; a terminal/no-task stage is not.
        """
        stage = state.stage
        stage_plan = self.execution_plan.get("stages", {}).get(stage)
        if not isinstance(stage_plan, dict):
            return {
                "stage": stage,
                "guards": ["agent_work_order_proof"],
                "failures": [f"process_execution_plan_missing:{stage}"],
                "pass": False,
            }
        tasks = stage_plan.get("tasks", [])
        if not isinstance(tasks, list):
            return {
                "stage": stage,
                "guards": ["agent_work_order_proof"],
                "failures": [f"process_execution_plan_tasks_invalid:{stage}"],
                "pass": False,
            }
        if not tasks:
            return {"stage": stage, "guards": [], "failures": [], "pass": True}

        failures: list[str] = []
        guards = [
            "agent_work_order_proof",
            "review_receipt_proof",
            "review_execution_attestation",
            "work_order_input_digest_binding",
            "producer_output_provenance",
        ]
        stage_approvals = state.approvals.get(stage, {})
        quality_spec = self.quality_rubric.get("stages", {}).get(stage)
        quality_target_name = quality_spec.get("target_artifact") if isinstance(quality_spec, dict) else None
        quality_target = state.artifacts.get(quality_target_name) if quality_target_name else None
        quality_roles = set(quality_spec.get("roles", {})) if isinstance(quality_spec, dict) else set()
        wave_attestations: dict[int, list[tuple[str, ExecutionAttestation]]] = {}

        for task in tasks:
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
            input_digests = result.get("input_digests")
            if not isinstance(input_digests, dict):
                failures.append(f"process_input_digests_missing:{task_id}")
                input_digests = {}
            for input_name in task.get("inputs", []):
                artifact = state.artifacts.get(input_name)
                if artifact is None:
                    failures.append(f"process_input_missing:{task_id}:{input_name}")
                    continue
                if input_name not in input_digests:
                    failures.append(f"process_input_digest_unbound:{task_id}:{input_name}")
                elif input_digests.get(input_name) != artifact.digest:
                    failures.append(f"process_input_digest_mismatch:{task_id}:{input_name}")

            if task_type in {"produce", "measure"}:
                for output_name in task.get("outputs", []):
                    artifact = state.artifacts.get(output_name)
                    if artifact is None:
                        failures.append(f"process_output_missing:{task_id}:{output_name}")
                        continue
                    if artifact.metadata.get("work_order_id") != work_order_id:
                        failures.append(f"process_output_provenance_mismatch:{task_id}:{output_name}")

            if task_type in {"review", "meta_review"}:
                if not self._review_receipt_matches(state, task_id, str(work_order_id), result):
                    failures.append(f"process_review_receipt_missing_or_mismatch:{task_id}")

                if self.execution_trust.requires_attestation(
                    stage,
                    blind=bool(task.get("blind", False)),
                    task_type=str(task_type),
                ):
                    attestation_payload = self._execution_attestation_for(
                        state,
                        task_id=task_id,
                        work_order_id=str(work_order_id),
                    )
                    if attestation_payload is None:
                        failures.append(f"process_execution_attestation_missing_or_ambiguous:{task_id}")
                    else:
                        attestation_failures, item = self._attestation_validation_failures(
                            state,
                            task,
                            order,
                            result,
                            attestation_payload,
                        )
                        failures.extend(attestation_failures)
                        if item is not None and not attestation_failures:
                            wave_attestations.setdefault(int(task.get("wave", 0)), []).append((task_id, item))

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

        failures.extend(self._attestation_identity_failures(wave_attestations))
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
        retired = sorted(
            name
            for name, artifact in state.artifacts.items()
            if self.orchestrator.index.get(artifact.stage, -1) >= self.orchestrator.index[stage]
        )
        self.orchestrator.invalidate_from(state, stage)
        self.store.append_receipt(
            project_id,
            "DOWNSTREAM_INVALIDATED",
            {
                "from_stage": old_stage,
                "invalidate_from": stage,
                "reason": reason,
                "retired_active_artifacts": retired,
                "historical_receipts_preserved": True,
            },
        )
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
            self.orchestrator.invalidate_from(state, stage, preserve_artifacts={name})
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

    def record_qa(
        self,
        project_id: str,
        report: QAReport,
        *,
        artifact_name: str = "technical_qa",
        stage: str = "TECH_QA",
        work_order_id: str | None = None,
        producer: str | None = None,
    ) -> str:
        state = self.state(project_id)
        receipt = self.store.append_receipt(project_id, "MEDIA_QA", report.to_dict())
        state.qa_receipts.append(receipt)
        metadata: dict[str, Any] = {
            "hard_pass": report.hard_pass,
            "media_uri": report.media_uri,
            "qa_receipt": receipt,
        }
        if work_order_id:
            metadata["work_order_id"] = work_order_id
        if producer:
            metadata["produced_by_agent"] = producer
        state.artifacts[artifact_name] = ArtifactRecord(
            name=artifact_name,
            uri=receipt,
            stage=stage,
            kind="qa_report",
            digest=canonical_digest(report.to_dict()),
            metadata=metadata,
        )
        state.touch()
        self.store.save(state)
        return receipt
