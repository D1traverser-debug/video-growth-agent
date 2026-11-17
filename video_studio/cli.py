from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

from .engine import StudioEngine, StudioError


def _read_json(path: str | Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StudioError(f"cannot read JSON file {path}: {exc}") from exc


def _emit(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vga-studio",
        description="Standalone outcome-driven Video Studio. No CAOS runtime or provider lock-in.",
    )
    parser.add_argument("--root", type=Path, help="workspace root (default: VGA_STUDIO_HOME or ~/.vga-studio)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create a project from an outcome brief")
    p.add_argument("project_id")
    p.add_argument("--title", default="")
    p.add_argument("--brief", type=Path, required=True, help="JSON brief with goal, audience and deliverables")

    p = sub.add_parser("revise-brief", help="revise the owner outcome and invalidate only affected dependency descendants")
    p.add_argument("project_id")
    p.add_argument("brief", type=Path)
    p.add_argument("--reason", required=True)
    p.add_argument("--affect-task", action="append", default=[], help="root task affected by the change; omit to invalidate all project tasks")

    p = sub.add_parser("brief-history", help="show immutable project brief revision events")
    p.add_argument("project_id")

    p = sub.add_parser("revise-task", help="revise a task contract and invalidate only dependent descendants")
    p.add_argument("project_id")
    p.add_argument("task_id")
    p.add_argument("patch", type=Path)
    p.add_argument("--reason", required=True)

    p = sub.add_parser("plan", help="add a project-specific dependency graph")
    p.add_argument("project_id")
    p.add_argument("tasks", type=Path, help="JSON array of task contracts")

    p = sub.add_parser("import-asset", help="copy an owner/source asset into the immutable project store")
    p.add_argument("project_id")
    p.add_argument("name")
    p.add_argument("source_path", type=Path)
    p.add_argument("--kind", default="source")
    p.add_argument("--media-type", default="application/octet-stream")
    p.add_argument("--rights-status", choices=["OWNED", "AUTHORIZED", "LICENSED", "PUBLIC_DOMAIN", "UNKNOWN", "NOT_APPLICABLE"], default="UNKNOWN")
    p.add_argument("--metadata", type=Path)

    p = sub.add_parser("import-manifest", help="preflight and import a set of source/context assets from a JSON manifest")
    p.add_argument("project_id")
    p.add_argument("manifest", type=Path, help="JSON manifest; relative asset paths resolve from the manifest directory")

    p = sub.add_parser("transfer-asset", help="transfer one exact immutable artifact between Studio projects")
    p.add_argument("source_project_id")
    p.add_argument("source_name")
    p.add_argument("target_project_id")
    p.add_argument("target_name")
    p.add_argument("--expected-artifact-id", required=True)
    p.add_argument("--expected-version", type=int, required=True)
    p.add_argument("--expected-sha256", required=True)

    p = sub.add_parser("system-audit", help="audit the standalone Video Studio repository contract and example execution")
    p.add_argument("--repo-root", type=Path, help="repository root to audit (default: inferred from the installed source package)")

    p = sub.add_parser("status", help="show project and task readiness")
    p.add_argument("project_id")

    p = sub.add_parser("resume", help="reconstruct the project handoff from durable Video state without chat memory")
    p.add_argument("project_id")
    p.add_argument("--event-limit", type=int, default=40)

    p = sub.add_parser("tasks", help="list the dynamic task graph")
    p.add_argument("project_id")

    p = sub.add_parser("claim", help="atomically claim the next ready task")
    p.add_argument("project_id")
    p.add_argument("--worker", required=True)
    p.add_argument("--lease-seconds", type=int, default=900)
    p.add_argument("--executor", choices=["agent", "human", "tool", "external"])
    p.add_argument("--task-id", help="claim this exact ready task instead of the next matching task")

    p = sub.add_parser("run-ready-tools", help="execute registered local tool tasks concurrently in dependency-ready rounds")
    p.add_argument("project_id")
    p.add_argument("--worker-prefix", default="local-tool")
    p.add_argument("--max-workers", type=int, default=2)
    p.add_argument("--lease-seconds", type=int, default=900)
    p.add_argument("--max-rounds", type=int, default=50)

    p = sub.add_parser("heartbeat", help="extend a current worker lease")
    p.add_argument("project_id")
    p.add_argument("task_id")
    p.add_argument("--worker", required=True)
    p.add_argument("--token", required=True)
    p.add_argument("--lease-seconds", type=int, default=900)

    p = sub.add_parser("complete", help="complete a claimed task with immutable output files")
    p.add_argument("project_id")
    p.add_argument("task_id")
    p.add_argument("--worker", required=True)
    p.add_argument("--token", required=True)
    p.add_argument("--outputs", type=Path, required=True, help="JSON object: output name -> path/kind/media_type/rights_status")
    p.add_argument("--result", type=Path, help="optional JSON result metadata")

    p = sub.add_parser("fail", help="record a task failure and schedule a bounded retry if allowed")
    p.add_argument("project_id")
    p.add_argument("task_id")
    p.add_argument("--worker", required=True)
    p.add_argument("--token", required=True)
    p.add_argument("--error", type=Path, required=True)
    p.add_argument("--non-retryable", action="store_true")

    p = sub.add_parser("wait-input", help="release a task claim while waiting for an external dependency")
    p.add_argument("project_id")
    p.add_argument("task_id")
    p.add_argument("--worker", required=True)
    p.add_argument("--token", required=True)
    p.add_argument("--reason", required=True)

    p = sub.add_parser("decision", help="persist a decision receipt with competing causes, alternatives and falsifier")
    p.add_argument("project_id")
    p.add_argument("payload", type=Path)

    p = sub.add_parser("failure", help="persist a root-cause and method-challenge record")
    p.add_argument("project_id")
    p.add_argument("payload", type=Path)

    p = sub.add_parser("resolve-failure", help="close a failure only with independent verification and regression evidence")
    p.add_argument("project_id")
    p.add_argument("failure_id")
    p.add_argument("resolution", type=Path)

    p = sub.add_parser("review", help="record an artifact-bound independent review")
    p.add_argument("project_id")
    p.add_argument("artifact_id")
    p.add_argument("--reviewer", required=True)
    p.add_argument("--rubric", required=True)
    p.add_argument("--outcome", choices=["PASS", "REVISE", "FAIL", "BLOCKED", "NOT_TESTED"], required=True)
    p.add_argument("--dimensions", type=Path, required=True, help="JSON scorecard/findings object")
    p.add_argument("--attestation", type=Path, help="JSON reviewer attestation: reviewer_kind, execution_mode, blind_review, inspected_artifact_digest, context_id")
    p.add_argument("--evidence", action="append", required=True)
    p.add_argument("--notes", default="")

    p = sub.add_parser("release-check", help="check final artifact against exact-digest reviews, rights, lineage, evidence and technical QA")
    p.add_argument("project_id")
    p.add_argument("artifact_id")
    p.add_argument("--rubric", action="append", default=[])
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--allow-unknown-rights", action="store_true")

    p = sub.add_parser("invalidate", help="invalidate a task and only its dependency descendants")
    p.add_argument("project_id")
    p.add_argument("task_id")
    p.add_argument("--reason", required=True)

    p = sub.add_parser("reopen", help="reopen stale/blocked/failed tasks after the cause is addressed")
    p.add_argument("project_id")
    p.add_argument("task_id")
    p.add_argument("--reason", required=True)

    p = sub.add_parser("learn", help="record a scoped method candidate or validated method")
    p.add_argument("project_id")
    p.add_argument("payload", type=Path)

    p = sub.add_parser("qa-media", help="run full FFmpeg/FFprobe technical QA for a claimed technical_measurement task")
    p.add_argument("project_id")
    p.add_argument("task_id")
    p.add_argument("--worker", required=True)
    p.add_argument("--token", required=True)
    p.add_argument("--input-name", help="declared input artifact name; defaults to the first available input")

    p = sub.add_parser("run-adapter", help="run a declared deterministic Video domain adapter inside a claimed Studio task")
    p.add_argument("project_id")
    p.add_argument("task_id")
    p.add_argument("--worker", required=True)
    p.add_argument("--token", required=True)

    p = sub.add_parser("audit", help="independently check project graph, task outputs and artifact digests")
    p.add_argument("project_id")

    p = sub.add_parser("events", help="show the append-only project event history")
    p.add_argument("project_id")
    p.add_argument("--limit", type=int, default=100)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        command = args.command
        if command == "system-audit":
            from .system_audit import run_system_audit
            report = run_system_audit(args.repo_root)
            _emit(report)
            return 0 if report["pass"] else 2
        engine = StudioEngine(args.root)
        if command == "init":
            _emit(engine.create_project(args.project_id, args.title, _read_json(args.brief)))
        elif command == "revise-brief":
            affected = args.affect_task if args.affect_task else None
            _emit(engine.revise_brief(args.project_id, _read_json(args.brief), reason=args.reason, affected_task_ids=affected))
        elif command == "brief-history":
            _emit(engine.brief_history(args.project_id))
        elif command == "revise-task":
            _emit(engine.revise_task(args.project_id, args.task_id, _read_json(args.patch), reason=args.reason))
        elif command == "plan":
            _emit(engine.add_tasks(args.project_id, _read_json(args.tasks)))
        elif command == "import-asset":
            metadata = _read_json(args.metadata) if args.metadata else {}
            _emit(engine.import_asset(args.project_id, args.name, args.source_path,
                                      kind=args.kind, media_type=args.media_type,
                                      rights_status=args.rights_status, metadata=metadata))
        elif command == "import-manifest":
            manifest_path = args.manifest.expanduser().resolve(strict=True)
            manifest = _read_json(manifest_path)
            if not isinstance(manifest, dict) or manifest.get("schema_version") != "1.0":
                raise StudioError("asset import manifest must be an object with schema_version 1.0")
            entries = manifest.get("assets")
            if not isinstance(entries, list) or not entries:
                raise StudioError("asset import manifest must contain a non-empty assets array")
            prepared = []
            seen_names: set[str] = set()
            for index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    raise StudioError(f"asset import manifest entry {index} must be an object")
                name = entry.get("name")
                relative_path = entry.get("path")
                kind = entry.get("kind", "source")
                media_type = entry.get("media_type", "application/octet-stream")
                rights_status = entry.get("rights_status", "UNKNOWN")
                metadata = entry.get("metadata", {})
                if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", name):
                    raise StudioError(f"asset import manifest entry {index} has an invalid artifact name")
                if name in seen_names:
                    raise StudioError(f"asset import manifest contains duplicate name: {name}")
                seen_names.add(name)
                if not isinstance(relative_path, str) or not relative_path.strip():
                    raise StudioError(f"asset import manifest entry {index} requires a path")
                if not isinstance(kind, str) or not kind.strip() or not isinstance(media_type, str) or not media_type.strip():
                    raise StudioError(f"asset import manifest entry {index} has invalid kind/media_type")
                if (
                    not isinstance(rights_status, str)
                    or rights_status not in {"OWNED", "AUTHORIZED", "LICENSED", "PUBLIC_DOMAIN", "UNKNOWN", "NOT_APPLICABLE"}
                    or not isinstance(metadata, dict)
                ):
                    raise StudioError(f"asset import manifest entry {index} has invalid rights_status/metadata")
                source = Path(relative_path).expanduser()
                if not source.is_absolute():
                    source = manifest_path.parent / source
                source = source.resolve(strict=True)
                if not source.is_file():
                    raise StudioError(f"asset import source is not a regular file: {source}")
                prepared.append({
                    "name": name, "source": source, "kind": kind,
                    "media_type": media_type, "rights_status": rights_status,
                    "metadata": metadata,
                })
            reserved_outputs = {
                output_name
                for task in engine.list_tasks(args.project_id)
                for output_name in task.get("outputs", [])
            }
            collisions = sorted(seen_names & reserved_outputs)
            if collisions:
                raise StudioError(f"manifest asset names are reserved as task outputs: {collisions}")
            imported = [
                engine.import_asset(
                    args.project_id, item["name"], item["source"],
                    kind=item["kind"], media_type=item["media_type"],
                    rights_status=item["rights_status"], metadata=item["metadata"],
                )
                for item in prepared
            ]
            _emit({
                "manifest": str(manifest_path),
                "asset_count": len(imported),
                "artifacts": imported,
            })
        elif command == "transfer-asset":
            _emit(engine.transfer_artifact(
                args.source_project_id, args.source_name,
                args.target_project_id, args.target_name,
                expected_artifact_id=args.expected_artifact_id,
                expected_version=args.expected_version,
                expected_sha256=args.expected_sha256,
            ))
        elif command == "status":
            _emit(engine.status(args.project_id))
        elif command == "resume":
            _emit(engine.resume(args.project_id, event_limit=args.event_limit))
        elif command == "tasks":
            _emit(engine.list_tasks(args.project_id))
        elif command == "claim":
            packet = engine.claim_next(
                args.project_id, args.worker, args.lease_seconds,
                executor=args.executor, task_id=args.task_id,
            )
            _emit(packet or {"claimed": False, "reason": "NO_MATCHING_READY_TASK"})
        elif command == "run-ready-tools":
            from .production.worker_pool import run_ready_tool_tasks
            result = run_ready_tool_tasks(
                engine, args.project_id, worker_prefix=args.worker_prefix,
                max_workers=args.max_workers, lease_seconds=args.lease_seconds,
                max_rounds=args.max_rounds,
            )
            _emit(result)
            if (
                result["failed"]
                or result["ready_tool_tasks_without_registered_executor"]
                or result["remaining_ready_registered_tool_tasks"]
            ):
                return 2
        elif command == "heartbeat":
            _emit({"lease_until": engine.heartbeat(args.project_id, args.task_id, args.worker, args.token, args.lease_seconds)})
        elif command == "complete":
            result = _read_json(args.result) if args.result else {}
            _emit(engine.complete_task(args.project_id, args.task_id, args.worker, args.token,
                                       _read_json(args.outputs), result))
        elif command == "fail":
            _emit(engine.fail_task(args.project_id, args.task_id, args.worker, args.token,
                                   _read_json(args.error), retryable=not args.non_retryable))
        elif command == "wait-input":
            engine.wait_for_input(args.project_id, args.task_id, args.worker, args.token, args.reason)
            _emit({"task_id": args.task_id, "status": "WAITING_INPUT"})
        elif command == "decision":
            _emit(engine.record_decision(args.project_id, _read_json(args.payload)))
        elif command == "failure":
            _emit(engine.record_failure(args.project_id, _read_json(args.payload)))
        elif command == "resolve-failure":
            engine.resolve_failure(args.project_id, args.failure_id, _read_json(args.resolution))
            _emit({"failure_id": args.failure_id, "status": "RESOLVED"})
        elif command == "review":
            _emit(engine.record_review(args.project_id, args.artifact_id,
                                      reviewer_id=args.reviewer, rubric_id=args.rubric,
                                      outcome=args.outcome, dimensions=_read_json(args.dimensions),
                                      evidence_refs=args.evidence, notes=args.notes,
                                      attestation=_read_json(args.attestation) if args.attestation else None))
        elif command == "release-check":
            _emit(engine.release_check(args.project_id, args.artifact_id,
                                       required_rubrics=args.rubric, evidence_refs=args.evidence,
                                       require_rights=not args.allow_unknown_rights))
        elif command == "invalidate":
            _emit(engine.invalidate(args.project_id, args.task_id, args.reason))
        elif command == "reopen":
            _emit({"reopened_tasks": engine.reopen(args.project_id, args.task_id, args.reason)})
        elif command == "learn":
            _emit(engine.record_learning(args.project_id, _read_json(args.payload)))
        elif command == "qa-media":
            from .media import run_claimed_media_qa
            _emit(run_claimed_media_qa(engine, args.project_id, args.task_id, args.worker, args.token, args.input_name))
        elif command == "run-adapter":
            from .adapters import run_claimed_domain_adapter
            _emit(run_claimed_domain_adapter(engine, args.project_id, args.task_id, args.worker, args.token))
        elif command == "audit":
            report = engine.audit(args.project_id)
            _emit(report)
            return 0 if report["pass"] else 2
        elif command == "events":
            _emit(engine.events(args.project_id, args.limit))
        return 0
    except (StudioError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"vga-studio: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())