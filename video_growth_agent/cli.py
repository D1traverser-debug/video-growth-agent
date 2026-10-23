from __future__ import annotations

import argparse
import json
from pathlib import Path

from .prompt_director import PromptPlanError, compile_file
from .prompt_experiment import h3_dialect_study
from .media_qa import MediaQAChecker
from .models import AssetRecord
from .runtime import StudioRuntime
from .system_audit import run_system_audit
from .techniques import TechniqueLibrary


def _json(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vga")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("project_id")
    p.add_argument("--title", default="")

    p = sub.add_parser("status")
    p.add_argument("project_id")

    p = sub.add_parser("prompts")
    p.add_argument("project_id")

    p = sub.add_parser("sign")
    p.add_argument("project_id")
    p.add_argument("role")
    p.add_argument("decision", choices=["PASS", "FAIL", "BLOCKED", "NOT_RUN"])
    p.add_argument("--notes", default="")
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--finding", action="append", default=[])
    p.add_argument("--score", action="append", default=[], help="quality score as dimension=value")
    p.add_argument("--benchmark", action="append", default=[])
    p.add_argument("--target-digest")
    p.add_argument("--blind-review", action="store_true")

    p = sub.add_parser("review-packet")
    p.add_argument("project_id")
    p.add_argument("role")

    p = sub.add_parser("advance")
    p.add_argument("project_id")

    p = sub.add_parser("artifact")
    p.add_argument("project_id")
    p.add_argument("name")
    p.add_argument("uri")
    p.add_argument("stage")
    p.add_argument("--kind", default="document")
    p.add_argument("--digest")

    p = sub.add_parser("asset")
    p.add_argument("project_id")
    p.add_argument("asset_id")
    p.add_argument("uri")
    p.add_argument("asset_type")
    p.add_argument("rights_status", choices=["OWNED", "AUTHORIZED", "LICENSED", "PUBLIC_DOMAIN", "UNKNOWN"])
    p.add_argument("--source-ref", default="")
    p.add_argument("--license-ref", default="")
    p.add_argument("--cost", type=float, default=0.0)
    p.add_argument("--not-final", action="store_true")

    p = sub.add_parser("qa-media")
    p.add_argument("media")
    p.add_argument("--frames-dir")
    p.add_argument("--frame-count", type=int, default=9)

    p = sub.add_parser("techniques")
    p.add_argument("--tag", action="append", default=[])
    p.add_argument("--max-cost", type=int, default=5)
    candidate_mode = p.add_mutually_exclusive_group()
    candidate_mode.add_argument("--validated-only", action="store_true", help="production-safe default; retained for compatibility")
    candidate_mode.add_argument("--include-candidates", action="store_true", help="explicit learning/prototype opt-in")

    p = sub.add_parser("direct-prompts", help="compile H3-first/PixVerse baseline film prompts with explicit scope and timing")
    p.add_argument("plan", type=Path)
    p.add_argument("--route", choices=["compare", "onepass", "shotwise"], default="compare")
    p.add_argument("--h3-style", choices=["chinese", "official"], default="chinese")
    p.add_argument("--study-h3-dialects", action="store_true", help="design an evidence-bound A/B prompt study; no media generation")
    p.add_argument("--plain", action="store_true", help="print copy-ready prompt text, not JSON")

    p = sub.add_parser("system-audit")
    p.add_argument("--repo-root", type=Path)

    args = parser.parse_args(argv)

    if args.cmd == "direct-prompts":
        try:
            if args.study_h3_dialects:
                if args.plain:
                    parser.error("--plain is not available with --study-h3-dialects")
                if args.route not in {"compare", "onepass"}:
                    parser.error("--study-h3-dialects only supports onepass; omit --route or use onepass")
                plan = json.loads(args.plan.read_text(encoding="utf-8"))
                _json(h3_dialect_study(plan))
            else:
                report = compile_file(args.plan, args.route, h3_style=args.h3_style)
                if args.plain:
                    if args.route == "compare":
                        parser.error("--plain needs --route onepass or --route shotwise")
                    compiled = report["routes"][args.route]
                    if compiled["status"] != "COMPILED":
                        parser.error(compiled["reason"])
                    print("\\n\\n=== NEXT SHOT ===\\n\\n".join(item["prompt"] for item in compiled["prompts"]))
                else:
                    _json(report)
            return 0
        except (PromptPlanError, OSError, ValueError) as exc:
            parser.exit(2, f"direct-prompts: {exc}\n")

    if args.cmd == "system-audit":
        report = run_system_audit(args.repo_root)
        _json(report)
        return 0 if report["pass"] else 2

    runtime = StudioRuntime()

    if args.cmd == "init":
        _json(runtime.create_project(args.project_id, title=args.title).to_dict())
    elif args.cmd == "status":
        state = runtime.state(args.project_id)
        _json({"state": state.to_dict(), "gate": runtime.gate_report(args.project_id), "unknown_final_rights": runtime.unknown_final_rights(args.project_id)})
    elif args.cmd == "prompts":
        _json(runtime.current_prompts(args.project_id))
    elif args.cmd == "sign":
        scorecard = {}
        for item in args.score:
            if "=" not in item:
                parser.error("--score must use dimension=value")
            key, value = item.split("=", 1)
            scorecard[key] = float(value)
        print(runtime.sign(
            args.project_id, args.role, args.decision, args.notes, tuple(args.evidence), tuple(args.finding),
            scorecard=scorecard, benchmark_refs=tuple(args.benchmark), target_digest=args.target_digest,
            blind_review=args.blind_review,
        ))
    elif args.cmd == "review-packet":
        _json(runtime.review_packet(args.project_id, args.role))
    elif args.cmd == "advance":
        print(runtime.advance(args.project_id))
    elif args.cmd == "artifact":
        print(runtime.record_artifact(args.project_id, args.name, args.uri, args.stage, args.kind, args.digest))
    elif args.cmd == "asset":
        asset = AssetRecord(
            asset_id=args.asset_id,
            uri=args.uri,
            asset_type=args.asset_type,
            rights_status=args.rights_status,
            source_ref=args.source_ref,
            license_ref=args.license_ref,
            cost=args.cost,
            used_in_final=not args.not_final,
        )
        print(runtime.record_asset(args.project_id, asset))
    elif args.cmd == "qa-media":
        checker = MediaQAChecker()
        report = checker.inspect(args.media)
        payload = report.to_dict()
        if args.frames_dir:
            payload["frames"] = checker.extract_frames(args.media, args.frames_dir, args.frame_count)
        _json(payload)
        return 0 if report.hard_pass else 2
    elif args.cmd == "techniques":
        library = TechniqueLibrary()
        _json([
            tech.__dict__
            for tech in library.find(
                set(args.tag),
                args.max_cost,
                validated_only=not args.include_candidates,
            )
        ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
