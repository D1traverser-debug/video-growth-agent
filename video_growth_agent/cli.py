from __future__ import annotations

import argparse
import json

from .media_qa import MediaQAChecker
from .models import AssetRecord
from .runtime import StudioRuntime
from .techniques import TechniqueLibrary


def _json(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vga")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("project_id"); p.add_argument("--title", default="")
    p = sub.add_parser("status"); p.add_argument("project_id")
    p = sub.add_parser("prompts"); p.add_argument("project_id")
    p = sub.add_parser("sign"); p.add_argument("project_id"); p.add_argument("role"); p.add_argument("decision", choices=["PASS","FAIL","BLOCKED","NOT_RUN"]); p.add_argument("--notes", default=""); p.add_argument("--evidence", action="append", default=[]); p.add_argument("--finding", action="append", default=[])
    p = sub.add_parser("advance"); p.add_argument("project_id")
    p = sub.add_parser("artifact"); p.add_argument("project_id"); p.add_argument("name"); p.add_argument("uri"); p.add_argument("stage"); p.add_argument("--kind", default="document"); p.add_argument("--digest")
    p = sub.add_parser("asset"); p.add_argument("project_id"); p.add_argument("asset_id"); p.add_argument("uri"); p.add_argument("asset_type"); p.add_argument("rights_status", choices=["OWNED","AUTHORIZED","LICENSED","PUBLIC_DOMAIN","UNKNOWN"]); p.add_argument("--source-ref", default=""); p.add_argument("--license-ref", default=""); p.add_argument("--cost", type=float, default=0.0); p.add_argument("--not-final", action="store_true")
    p = sub.add_parser("qa-media"); p.add_argument("media"); p.add_argument("--frames-dir"); p.add_argument("--frame-count", type=int, default=9)
    p = sub.add_parser("techniques"); p.add_argument("--tag", action="append", default=[]); p.add_argument("--max-cost", type=int, default=5); p.add_argument("--validated-only", action="store_true")
    args = parser.parse_args(argv)
    runtime = StudioRuntime()
    if args.cmd == "init": _json(runtime.create_project(args.project_id, title=args.title).to_dict())
    elif args.cmd == "status":
        state = runtime.state(args.project_id); _json({"state": state.to_dict(), "gate": runtime.gate_report(args.project_id), "unknown_final_rights": runtime.unknown_final_rights(args.project_id)})
    elif args.cmd == "prompts": _json(runtime.current_prompts(args.project_id))
    elif args.cmd == "sign": print(runtime.sign(args.project_id, args.role, args.decision, args.notes, tuple(args.evidence), tuple(args.finding)))
    elif args.cmd == "advance": print(runtime.advance(args.project_id))
    elif args.cmd == "artifact": print(runtime.record_artifact(args.project_id, args.name, args.uri, args.stage, args.kind, args.digest))
    elif args.cmd == "asset":
        asset = AssetRecord(asset_id=args.asset_id, uri=args.uri, asset_type=args.asset_type, rights_status=args.rights_status, source_ref=args.source_ref, license_ref=args.license_ref, cost=args.cost, used_in_final=not args.not_final)
        print(runtime.record_asset(args.project_id, asset))
    elif args.cmd == "qa-media":
        checker = MediaQAChecker(); report = checker.inspect(args.media); payload = report.to_dict()
        if args.frames_dir: payload["frames"] = checker.extract_frames(args.media, args.frames_dir, args.frame_count)
        _json(payload); return 0 if report.hard_pass else 2
    elif args.cmd == "techniques":
        library = TechniqueLibrary(); _json([tech.__dict__ for tech in library.find(set(args.tag), args.max_cost, args.validated_only)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
