from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import Approval, ArtifactRecord, AssetRecord, QAReport, ProjectState
from .orchestrator import GateBlocked, StudioOrchestrator
from .roles import RoleRegistry
from .storage import ProjectStore


class StudioRuntime:
    """Executable authority for project checkpoints, sign-offs and evidence receipts."""

    REQUIRED_MEDIA_QA_CHECKS = {"video_stream", "stream_duration_match", "true_peak", "black_frames"}

    def __init__(self, store: ProjectStore | None = None, orchestrator: StudioOrchestrator | None = None, roles: RoleRegistry | None = None):
        self.store = store or ProjectStore()
        self.orchestrator = orchestrator or StudioOrchestrator()
        self.roles = roles or RoleRegistry()
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

    def sign(self, project_id: str, role: str, decision: str, notes: str = "", evidence: tuple[str, ...] = (), findings: tuple[str, ...] = ()) -> str:
        state = self.state(project_id)
        approval = Approval(role=role, decision=decision, notes=notes, evidence=evidence, findings=findings)  # type: ignore[arg-type]
        self.orchestrator.sign(state, approval)
        receipt = self.store.append_receipt(project_id, "ROLE_REVIEW", {"stage": state.stage, "approval": asdict(approval)})
        self.store.save(state)
        return receipt

    def advance(self, project_id: str) -> str:
        state = self.state(project_id)
        machine = self.machine_guard_report(state)
        if not machine["pass"]:
            raise GateBlocked(__import__("json").dumps(machine, ensure_ascii=False))
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
            elif guard == "no_unknown_final_rights":
                unknown = [asset.asset_id for asset in state.assets.values() if asset.used_in_final and asset.rights_status == "UNKNOWN"]
                if unknown:
                    failures.append("no_unknown_final_rights:" + ",".join(sorted(unknown)))
            else:
                failures.append("unknown_machine_guard:" + guard)
        return {"stage": state.stage, "guards": guards, "failures": failures, "pass": not failures}

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
            import json
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
