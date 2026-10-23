from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .prompt_director import PromptPlanError, compile_file
from .prompt_experiment import h3_dialect_study
from .source_director import (
    PromptPlanError as DirectorSourceError, accept_authoring_response,
    author_with_model, build_compatible_chat_client, build_director_request,
    prepare_authoring_messages,
)
from .media_qa import MediaQAChecker
from .models import AssetRecord
from .runtime import StudioRuntime
from .system_audit import run_system_audit
from .techniques import TechniqueLibrary
from .craft_round import CraftReviewError, prepare_craft_round, reconcile_craft_round, next_revision_diff


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
    p.add_argument("--h3-style", choices=["auto", "lean", "chinese", "official"], default="auto")
    p.add_argument("--study-h3-dialects", action="store_true", help="design an evidence-bound A/B prompt study; no media generation")
    p.add_argument("--plain", action="store_true", help="print copy-ready prompt text, not JSON")
    p.add_argument("--review-sheet", action="store_true", help="emit unscored shot-level evaluation targets for actual rendered video")

    p = sub.add_parser("author-director", help="convert complete source script to verified H3 director plan via structured model response")
    p.add_argument("source", type=Path, help="UTF-8 raw screenplay or original brief")
    p.add_argument("--seconds", required=True, type=int, help="final film duration, 4–15 seconds for H3")
    p.add_argument("--fps", type=int, default=30, help="director edit timebase")
    p.add_argument("--aspect", default="16:9")
    p.add_argument("--source-ref", default="user-supplied://original")
    p.add_argument("--source-type", choices=["USER_ORIGINAL", "USER_REFERENCE", "ORIGINAL_SCRIPT", "PRIMARY_DOCUMENT"], default="USER_REFERENCE")
    p.add_argument("--model-output", type=Path, help="import a JSON draft produced by a separate authoring model")
    p.add_argument("--execute-model", action="store_true", help="call a configured HTTPS chat-completions text model")
    p.add_argument("--endpoint", help="explicit HTTPS chat-completions URL (only with --execute-model)")
    p.add_argument("--model-name", help="text model name (not the H3 video model)")
    p.add_argument("--api-key-env", default="VIDEO_DIRECTOR_API_KEY")
    p.add_argument("--approve-upload-cost", action="store_true", help="approve sending original script to this text provider and possible charges")
    p.add_argument("--max-revisions", type=int, default=0, choices=[0,1,2,3], help="additional paid authoring calls after rejected JSON")
    p.add_argument("--out-plan", type=Path, help="save accepted full plan JSON after validation")
    p.add_argument("--route", choices=["onepass", "shotwise"], default="onepass")
    p.add_argument("--h3-style", choices=["auto", "lean", "chinese", "official"], default="auto")

    p = sub.add_parser("craft-round", help="prepare independent craft role packets or reconcile submitted reviews on one shot plan")
    p.add_argument("plan", type=Path, help="validated director-plan JSON")
    p.add_argument("--revision", type=int, default=1)
    p.add_argument("--reviews", type=Path, help="JSON list of submitted seven role reviews")
    p.add_argument("--previous", type=Path, help="prior version for shot-level delta")

    p = sub.add_parser("system-audit")
    p.add_argument("--repo-root", type=Path)

    args = parser.parse_args(argv)

    if args.cmd == "craft-round":
        try:
            current = json.loads(args.plan.read_text(encoding="utf-8"))
            packet = prepare_craft_round(current, revision=args.revision)
            result = {"packet": packet}
            if args.reviews is not None:
                reviews = json.loads(args.reviews.read_text(encoding="utf-8"))
                result["reconciliation"] = reconcile_craft_round(packet, reviews)
            if args.previous is not None:
                previous = json.loads(args.previous.read_text(encoding="utf-8"))
                result["revision_diff"] = next_revision_diff(previous, current)
            _json(result)
            return 0
        except (CraftReviewError, PromptPlanError, OSError, ValueError, KeyError) as exc:
            parser.exit(2, f"craft-round: {exc}\n")

    if args.cmd == "author-director":
        try:
            if args.model_output is not None and args.execute_model:
                parser.error("--model-output and --execute-model are mutually exclusive")
            raw = args.source.read_text(encoding="utf-8")
            packet = build_director_request(
                raw, target_seconds=args.seconds, fps=args.fps,
                aspect_ratio=args.aspect, source_reference=args.source_ref,
                source_type=args.source_type,
            )
            if args.model_output is not None:
                response = args.model_output.read_text(encoding="utf-8")
                result = accept_authoring_response(
                    packet, response, prompt_route=args.route, h3_style=args.h3_style,
                )
            elif args.execute_model:
                if not args.endpoint or not args.model_name:
                    parser.error("--execute-model requires --endpoint and --model-name")
                client = build_compatible_chat_client(
                    endpoint=args.endpoint, model_name=args.model_name,
                    api_key=os.environ.get(args.api_key_env, ""),
                    approved=args.approve_upload_cost,
                )
                result = author_with_model(
                    packet, client, prompt_route=args.route, h3_style=args.h3_style,
                    max_revisions=args.max_revisions,
                )
            else:
                _json({"status": "AUTHORING_PACKET_READY", "packet": packet,
                       "model_messages": prepare_authoring_messages(packet),
                       "note": "Model was NOT called. Send model_messages to an authoring LLM; import bare JSON with --model-output."})
                return 0
            if args.out_plan:
                args.out_plan.write_text(json.dumps(result["plan"], ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
            _json(result)
            return 0
        except (DirectorSourceError, OSError, ValueError) as exc:
            parser.exit(2, f"author-director: {exc}\\n")

    if args.cmd == "direct-prompts":
        try:
            if args.study_h3_dialects:
                if args.plain or args.review_sheet:
                    parser.error("--plain/--review-sheet are not available with --study-h3-dialects")
                if args.route not in {"compare", "onepass"}:
                    parser.error("--study-h3-dialects only supports onepass; omit --route or use onepass")
                plan = json.loads(args.plan.read_text(encoding="utf-8"))
                _json(h3_dialect_study(plan))
            else:
                report = compile_file(args.plan, args.route, h3_style=args.h3_style)
                if args.review_sheet:
                    if args.plain:
                        parser.error("--plain and --review-sheet are mutually exclusive")
                    _json(report["review_targets"])
                elif args.plain:
                    if args.route == "compare":
                        parser.error("--plain needs --route onepass or --route shotwise")
                    if "prompt_candidates" in report:
                        sections = []
                        for dialect, routes in report["prompt_candidates"].items():
                            compiled = routes[args.route]
                            if compiled["status"] == "COMPILED":
                                section = "\n\n=== CANDIDATE: " + dialect.upper() + " ===\n\n"
                                section += "\n\n=== NEXT SHOT ===\n\n".join(
                                    item["prompt"] for item in compiled["prompts"]
                                )
                                sections.append(section)
                        if not sections:
                            parser.error("no compilable prompt dialects for requested route")
                        print("".join(sections))
                    else:
                        compiled = report["routes"][args.route]
                        if compiled["status"] != "COMPILED":
                            parser.error(compiled["reason"])
                        print("\n\n=== NEXT SHOT ===\n\n".join(item["prompt"] for item in compiled["prompts"]))
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
