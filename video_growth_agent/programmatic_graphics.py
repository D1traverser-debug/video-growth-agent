"""Local, deterministic programmatic graphics candidate renderer.

This is a constrained non-AI route for information/explainer shots. It never
claims to replace generative video, never promotes assets, and never authorizes
release. Rendering is local FFmpeg execution with an explicit ShotContract.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import textwrap
from typing import Any, Mapping

from .media_graph import (
    AssetRef,
    AssetVersion,
    EvidenceRecord,
    MediaGraph,
    TaskRecord,
)
from .media_qa import MediaQAChecker
from .models import utcnow_iso
from .production_os import ReferenceBinding, ShotContract

RENDERER_VERSION = "0.1.0"
KINDS = frozenset({"TITLE_CARD", "STAT_CARD", "BAR_CHART", "QUOTE_CARD"})
FPS_OPTIONS = frozenset({24, 25, 30, 50, 60})
HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
CLAIM_BACKED_KINDS = frozenset({"STAT_CARD", "BAR_CHART", "QUOTE_CARD"})


class ProgrammaticGraphicsError(RuntimeError):
    pass


@dataclass(frozen=True)
class ChartDatum:
    label: str
    value: float
    display_value: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.label, str) or not self.label.strip():
            raise ProgrammaticGraphicsError("chart labels must be nonempty strings")
        if not math.isfinite(float(self.value)) or float(self.value) < 0:
            raise ProgrammaticGraphicsError("chart values must be finite and nonnegative")


@dataclass(frozen=True)
class GraphicSpec:
    spec_id: str
    kind: str
    title: str
    subtitle: str = ""
    kicker: str = ""
    metric: str = ""
    metric_label: str = ""
    chart_data: tuple[ChartDatum, ...] = ()
    duration_seconds: float = 5.0
    width: int = 1080
    height: int = 1920
    fps: int = 30
    background: str = "#0B1020"
    foreground: str = "#F4F7FB"
    accent: str = "#43D9C3"
    muted: str = "#93A4BC"

    def __post_init__(self) -> None:
        if not isinstance(self.spec_id, str) or not self.spec_id.strip():
            raise ProgrammaticGraphicsError("spec_id is required")
        if self.kind not in KINDS:
            raise ProgrammaticGraphicsError(f"unsupported graphic kind: {self.kind}")
        if not isinstance(self.title, str) or not self.title.strip():
            raise ProgrammaticGraphicsError("title is required")
        if not math.isfinite(float(self.duration_seconds)) or not 2.0 <= self.duration_seconds <= 15.0:
            raise ProgrammaticGraphicsError("shot graphic duration must be between 2 and 15 seconds")
        if (
            not isinstance(self.width, int) or not isinstance(self.height, int)
            or self.width < 640 or self.height < 640
            or self.width > 3840 or self.height > 3840
            or self.width % 2 or self.height % 2
        ):
            raise ProgrammaticGraphicsError("width/height must be even integers in [640, 3840]")
        if self.fps not in FPS_OPTIONS:
            raise ProgrammaticGraphicsError(f"fps must be one of {sorted(FPS_OPTIONS)}")
        for name in ("background", "foreground", "accent", "muted"):
            value = getattr(self, name)
            if not isinstance(value, str) or not HEX_COLOR.fullmatch(value):
                raise ProgrammaticGraphicsError(f"{name} must be a #RRGGBB color")
        if self.kind == "STAT_CARD" and (
            not isinstance(self.metric, str) or not self.metric.strip()
            or not isinstance(self.metric_label, str) or not self.metric_label.strip()
        ):
            raise ProgrammaticGraphicsError("STAT_CARD requires metric and metric_label")
        if self.kind == "BAR_CHART":
            if not 2 <= len(self.chart_data) <= 6:
                raise ProgrammaticGraphicsError("BAR_CHART requires 2 to 6 data points")
            if not any(float(item.value) > 0 for item in self.chart_data):
                raise ProgrammaticGraphicsError("BAR_CHART requires at least one positive value")
        elif self.chart_data:
            raise ProgrammaticGraphicsError("chart_data is only valid for BAR_CHART")
        if self.kind in {"QUOTE_CARD", "TITLE_CARD"} and not self.subtitle.strip():
            raise ProgrammaticGraphicsError(f"{self.kind} requires a subtitle/attribution")


def graphic_spec_from_dict(payload: Mapping[str, Any]) -> GraphicSpec:
    data = dict(payload)
    points = data.get("chart_data", [])
    if not isinstance(points, list):
        raise ProgrammaticGraphicsError("chart_data must be a list")
    data["chart_data"] = tuple(
        point if isinstance(point, ChartDatum) else ChartDatum(**point)
        for point in points
    )
    return GraphicSpec(**data)


def shot_contract_from_dict(payload: Mapping[str, Any]) -> ShotContract:
    data = dict(payload)
    references = data.get("references", [])
    if not isinstance(references, list):
        raise ProgrammaticGraphicsError("ShotContract references must be a list")
    data["references"] = tuple(
        ref if isinstance(ref, ReferenceBinding) else ReferenceBinding(**ref)
        for ref in references
    )
    for key in (
        "allowed_modes", "required_capabilities", "must_have", "must_not_have",
        "graceful_degradation", "stop_conditions", "source_claim_ids",
        "ip_identity_invariants", "ip_identity_forbidden_drift",
    ):
        data[key] = tuple(data.get(key, ())) if key in {
            "must_have", "must_not_have", "graceful_degradation", "stop_conditions",
            "source_claim_ids", "ip_identity_invariants", "ip_identity_forbidden_drift",
        } else frozenset(data.get(key, ()))
    data.setdefault("quality_targets", {})
    data.setdefault("value_vector", {})
    return ShotContract(**data)


def _jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(_jsonable(item) for item in value)
    return value


def _digest(value: Any) -> str:
    raw = json.dumps(
        _jsonable(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _wrapped(text: str, width: int, max_lines: int, field: str) -> str:
    paragraphs = text.splitlines() or [text]
    lines: list[str] = []
    for paragraph in paragraphs:
        if not paragraph:
            lines.append("")
        else:
            lines.extend(textwrap.wrap(
                paragraph, width=width, break_long_words=True,
                break_on_hyphens=False,
            ) or [""])
    if len(lines) > max_lines:
        raise ProgrammaticGraphicsError(
            f"{field} wraps to {len(lines)} lines; maximum is {max_lines}"
        )
    return "\n".join(lines)


def _color(value: str) -> str:
    return "0x" + value[1:].upper()


def _drawtext(
    text_file: str,
    *,
    font_size: int,
    x: str,
    y: str,
    color: str,
    line_spacing: int = 12,
) -> str:
    return (
        f"drawtext=fontfile=font.ttf:textfile={text_file}:"
        f"fontcolor={_color(color)}:fontsize={font_size}:"
        f"x={x}:y={y}:line_spacing={line_spacing}:"
        "shadowcolor=0x000000@0.32:shadowx=2:shadowy=3:"
        "alpha='if(lt(t,0.18),0,if(lt(t,0.78),(t-0.18)/0.60,1))'"
    )


def _filter_script(spec: GraphicSpec) -> tuple[str, dict[str, str]]:
    title_width = max(12, int(spec.width / 54))
    subtitle_width = max(18, int(spec.width / 38))
    title = _wrapped(spec.title, title_width, 3, "title")
    subtitle = _wrapped(spec.subtitle, subtitle_width, 4, "subtitle") if spec.subtitle else ""
    kicker = _wrapped(spec.kicker, subtitle_width, 1, "kicker") if spec.kicker else ""
    text_files: dict[str, str] = {
        "title.txt": title,
        "subtitle.txt": subtitle,
        "kicker.txt": kicker,
        "metric.txt": spec.metric,
        "metric_label.txt": spec.metric_label,
    }
    filters: list[str] = [
        f"drawbox=x=0:y=0:w=iw:h={max(5, int(spec.height * 0.006))}:color={_color(spec.accent)}@0.96:t=fill"
    ]
    if kicker:
        filters.append(_drawtext(
            "kicker.txt", font_size=max(18, int(spec.height * 0.018)),
            x="(w-text_w)/2", y=str(int(spec.height * 0.19)),
            color=spec.accent, line_spacing=4,
        ))

    if spec.kind in {"TITLE_CARD", "QUOTE_CARD"}:
        filters.append(_drawtext(
            "title.txt", font_size=max(42, int(spec.height * 0.052)),
            x="(w-text_w)/2", y=str(int(spec.height * 0.32)),
            color=spec.foreground, line_spacing=max(12, int(spec.height * 0.012)),
        ))
        if subtitle:
            filters.append(_drawtext(
                "subtitle.txt", font_size=max(24, int(spec.height * 0.027)),
                x="(w-text_w)/2", y=str(int(spec.height * 0.57)),
                color=spec.muted, line_spacing=max(8, int(spec.height * 0.008)),
            ))
    elif spec.kind == "STAT_CARD":
        filters.append(_drawtext(
            "title.txt", font_size=max(34, int(spec.height * 0.038)),
            x="(w-text_w)/2", y=str(int(spec.height * 0.25)),
            color=spec.foreground,
        ))
        filters.append(_drawtext(
            "metric.txt", font_size=max(72, int(spec.height * 0.13)),
            x="(w-text_w)/2", y=str(int(spec.height * 0.43)),
            color=spec.accent, line_spacing=0,
        ))
        filters.append(_drawtext(
            "metric_label.txt", font_size=max(24, int(spec.height * 0.028)),
            x="(w-text_w)/2", y=str(int(spec.height * 0.60)),
            color=spec.muted,
        ))
        if subtitle:
            filters.append(_drawtext(
                "subtitle.txt", font_size=max(20, int(spec.height * 0.022)),
                x="(w-text_w)/2", y=str(int(spec.height * 0.72)),
                color=spec.foreground,
            ))
    elif spec.kind == "BAR_CHART":
        filters.append(_drawtext(
            "title.txt", font_size=max(34, int(spec.height * 0.038)),
            x="(w-text_w)/2", y=str(int(spec.height * 0.25)),
            color=spec.foreground,
        ))
        if subtitle:
            filters.append(_drawtext(
                "subtitle.txt", font_size=max(20, int(spec.height * 0.022)),
                x="(w-text_w)/2", y=str(int(spec.height * 0.34)),
                color=spec.muted,
            ))
        max_value = max(float(point.value) for point in spec.chart_data)
        left = int(spec.width * 0.08)
        bar_x = int(spec.width * 0.29)
        bar_max = int(spec.width * 0.57)
        start_y = int(spec.height * 0.47)
        bar_h = max(18, int(spec.height * 0.018))
        row_gap = max(64, int(spec.height * 0.075))
        for index, point in enumerate(spec.chart_data):
            label_name = f"chart-label-{index}.txt"
            value_name = f"chart-value-{index}.txt"
            text_files[label_name] = _wrapped(point.label, max(8, int(spec.width / 90)), 1, "chart label")
            text_files[value_name] = point.display_value or f"{point.value:g}"
            y = start_y + index * row_gap
            filters.append(_drawtext(
                label_name, font_size=max(18, int(spec.height * 0.019)),
                x=str(left), y=str(y - int(bar_h * 0.15)), color=spec.foreground,
                line_spacing=2,
            ))
            filters.append(
                f"drawbox=x={bar_x}:y={y}:w={bar_max}:h={bar_h}:color=0x29354A:t=fill"
            )
            ratio = float(point.value) / max_value if max_value else 0.0
            filters.append(
                f"drawbox=x={bar_x}:y={y}:w={max(1, int(bar_max * ratio))}:"
                f"h={bar_h}:color={_color(spec.accent)}:t=fill:enable='gte(t,0.65)'"
            )
            filters.append(_drawtext(
                value_name, font_size=max(18, int(spec.height * 0.019)),
                x=str(bar_x + bar_max + int(spec.width * 0.025)),
                y=str(y - int(bar_h * 0.15)), color=spec.accent,
                line_spacing=2,
            ))

    progress_y = spec.height - max(8, int(spec.height * 0.008))
    filters.append(
        f"drawbox=x=0:y={progress_y}:w='iw*min(max(t/{spec.duration_seconds:.3f},0),1)':"
        f"h={max(8, int(spec.height * 0.008))}:color={_color(spec.accent)}:t=fill"
    )
    filters.append("format=yuv420p[v]")
    return "[0:v]" + ",".join(filters), text_files


def _validate_shot(shot: ShotContract, spec: GraphicSpec) -> None:
    if "PROGRAMMATIC_GRAPHICS" not in shot.allowed_modes:
        raise ProgrammaticGraphicsError("ShotContract does not allow PROGRAMMATIC_GRAPHICS")
    if not shot.editorially_traceable:
        raise ProgrammaticGraphicsError("programmatic graphics require EditorialPlan and beat binding")
    if abs(float(shot.duration_seconds) - float(spec.duration_seconds)) > 0.01:
        raise ProgrammaticGraphicsError("GraphicSpec duration must match the ShotContract")
    if shot.truth_mode not in {"SYNTHETIC", "MIXED_DISCLOSED"}:
        raise ProgrammaticGraphicsError(
            "programmatic graphics are synthetic explanatory visuals, not observed real/product-truth evidence"
        )
    if not shot.disclosure_required:
        raise ProgrammaticGraphicsError("synthetic graphic candidates require disclosure_required=true")
    if shot.ip_identity_required:
        raise ProgrammaticGraphicsError(
            "this non-character renderer cannot satisfy an IPOS identity-dependent ShotContract"
        )
    if spec.kind in CLAIM_BACKED_KINDS and not shot.source_claim_ids:
        raise ProgrammaticGraphicsError(f"{spec.kind} requires source_claim_ids")
    if shot.truth_mode == "MIXED_DISCLOSED" and not shot.references:
        raise ProgrammaticGraphicsError("MIXED_DISCLOSED graphics require explicit source/reference bindings")


def render_programmatic_graphic(
    shot: ShotContract,
    spec: GraphicSpec,
    *,
    output_path: str | Path,
    font_path: str | Path,
) -> dict[str, Any]:
    """Render a silent visual candidate locally and return exact-byte QA evidence."""
    _validate_shot(shot, spec)
    output = Path(output_path).expanduser().resolve()
    font = Path(font_path).expanduser().resolve()
    if output.suffix.lower() != ".mp4":
        raise ProgrammaticGraphicsError("output_path must end in .mp4")
    if not font.is_file():
        raise ProgrammaticGraphicsError(f"font file not found: {font}")
    if not MediaQAChecker.tools_available():
        raise ProgrammaticGraphicsError("ffmpeg and ffprobe must both be installed")
    receipt_path = output.with_suffix(output.suffix + ".receipt.json")
    if output.exists() or receipt_path.exists():
        raise FileExistsError("renderer is non-destructive; output or receipt already exists")

    output.parent.mkdir(parents=True, exist_ok=True)
    graph, text_files = _filter_script(spec)
    with tempfile.TemporaryDirectory(prefix="vga-graphic-") as work:
        workdir = Path(work)
        shutil.copyfile(font, workdir / "font.ttf")
        for name, value in text_files.items():
            (workdir / name).write_text(value, encoding="utf-8")
        (workdir / "filters.txt").write_text(graph, encoding="utf-8")
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-n",
            "-f", "lavfi", "-i",
            f"color=c={_color(spec.background)}:s={spec.width}x{spec.height}:r={spec.fps}:d={spec.duration_seconds:.3f}",
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-filter_complex_script", "filters.txt",
            "-map", "[v]", "-map", "1:a:0",
            "-t", f"{spec.duration_seconds:.3f}", "-shortest",
            "-r", str(spec.fps),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            "-metadata", "comment=VIDEO_CANDIDATE_ONLY__INTENTIONAL_SILENCE",
            str(output),
        ]
        proc = subprocess.run(command, cwd=workdir, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            output.unlink(missing_ok=True)
            raise ProgrammaticGraphicsError(f"ffmpeg render failed: {proc.stderr.strip()}")
    if not output.is_file() or output.stat().st_size == 0:
        raise ProgrammaticGraphicsError("ffmpeg returned without a nonempty output file")

    qa = MediaQAChecker().inspect(output).to_dict()
    digest = _sha256(output)
    rendered_at = utcnow_iso()
    receipt = {
        "receipt_version": "1.0",
        "receipt_id": f"programmatic-graphics:{digest[:20]}",
        "renderer": "video_growth_agent.programmatic_graphics",
        "renderer_version": RENDERER_VERSION,
        "rendered_at": rendered_at,
        "shot_id": shot.shot_id,
        "sequence_id": shot.sequence_id,
        "editorial_plan_ref": shot.editorial_plan_ref,
        "beat_id": shot.beat_id,
        "source_claim_ids": list(shot.source_claim_ids),
        "truth_mode": shot.truth_mode,
        "graphic_spec": _jsonable(spec),
        "graphic_spec_digest": _digest(spec),
        "shot_contract_digest": _digest(shot),
        "font_sha256": _sha256(font),
        "media_path": str(output),
        "media_sha256": digest,
        "duration_seconds": spec.duration_seconds,
        "width": spec.width,
        "height": spec.height,
        "fps": spec.fps,
        "audio_mode": "INTENTIONAL_SILENCE_FOR_VISUAL_PREVIEW",
        "qa": qa,
        "qa_hard_pass": bool(qa.get("hard_pass")),
        "candidate_only": True,
        "promotion_authorized": False,
        "release_authorized": False,
        "paid_service_used": False,
        "network_access_used": False,
        "limitations": [
            "This renderer creates deterministic typography/data graphics only.",
            "It is not generative video, live footage, product-truth evidence, voice generation or final sound mix.",
            "Silent preview is intentional; the separate SOUND stage must author/approve final audio.",
            "A technical QA pass does not prove editorial, visual-craft, rights, continuity or release quality.",
        ],
    }
    return receipt


def register_graph_candidate(
    graph: MediaGraph,
    shot: ShotContract,
    spec: GraphicSpec,
    receipt: Mapping[str, Any],
) -> str:
    """Register a rendered take as CANDIDATE with exact lineage; never promote it."""
    context = graph.contexts.get(shot.shot_id)
    if context is None or context.kind != "SHOT":
        raise ProgrammaticGraphicsError(
            f"MediaGraph must already contain SHOT context {shot.shot_id}"
        )
    refs = tuple(AssetRef(ref.asset_id, ref.version_id) for ref in shot.references)
    missing = [ref.key() for ref in refs if ref not in graph.assets]
    if missing:
        raise ProgrammaticGraphicsError("MediaGraph reference assets missing: " + ", ".join(missing))

    digest = str(receipt.get("media_sha256") or "")
    media_path = Path(str(receipt.get("media_path") or ""))
    if len(digest) != 64 or not media_path.is_file() or _sha256(media_path) != digest:
        raise ProgrammaticGraphicsError("render receipt does not match the current media bytes")
    asset_ref = AssetRef(
        asset_id=f"{shot.shot_id}:programmatic-graphic:{spec.spec_id}",
        version_id=digest[:16],
    )
    if asset_ref in graph.assets:
        raise ProgrammaticGraphicsError(f"MediaGraph asset version already exists: {asset_ref.key()}")

    media_uri = media_path.resolve().as_uri()
    graph.add_asset(AssetVersion(
        ref=asset_ref,
        context_id=shot.shot_id,
        kind="PROGRAMMATIC_GRAPHIC_VIDEO",
        uri=media_uri,
        digest=digest,
        state="CANDIDATE",
        derived_from=refs,
        rights_refs=tuple(dict.fromkeys(ref.rights_ref for ref in shot.references)),
        consent_refs=tuple(dict.fromkeys(
            ref.consent_ref for ref in shot.references if ref.consent_ref
        )),
        provenance_refs=tuple(dict.fromkeys((
            shot.editorial_plan_ref, shot.beat_id, *shot.source_claim_ids,
        ))),
        metadata={
            "renderer": "video_growth_agent.programmatic_graphics",
            "receipt_id": receipt.get("receipt_id"),
            "qa_hard_pass": receipt.get("qa_hard_pass") is True,
            "candidate_only": True,
            "truth_mode": shot.truth_mode,
            "audio_mode": receipt.get("audio_mode"),
        },
    ))
    evidence_id = f"evidence:{asset_ref.key()}"
    graph.add_evidence(EvidenceRecord(
        evidence_id=evidence_id,
        subject_type="ASSET_VERSION",
        subject_id=asset_ref.key(),
        action="PROGRAMMATIC_GRAPHIC_RENDERED",
        refs=(media_uri, f"sha256:{digest}", str(receipt.get("receipt_id") or "")),
        observed_at=str(receipt.get("rendered_at") or utcnow_iso()),
        metadata={
            "qa_hard_pass": receipt.get("qa_hard_pass") is True,
            "renderer_version": RENDERER_VERSION,
            "candidate_only": True,
        },
    ))
    task_id = f"task:programmatic-graphics:{shot.shot_id}:{spec.spec_id}:{digest[:12]}"
    graph.add_task(TaskRecord(
        task_id=task_id,
        context_id=shot.shot_id,
        task_type="PROGRAMMATIC_GRAPHIC_RENDER",
        input_assets=refs,
        output_assets=(asset_ref,),
        state="COMPLETED",
        executor_ref="local:ffmpeg",
        metadata={
            "evidence_id": evidence_id,
            "receipt_id": receipt.get("receipt_id"),
            "promotion_authorized": False,
        },
    ))
    return asset_ref.key()
