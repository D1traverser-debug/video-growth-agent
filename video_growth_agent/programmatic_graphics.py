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
from typing import Any, Mapping

from PIL import ImageFont

from .media_graph import (
    AssetRef,
    AssetVersion,
    EvidenceRecord,
    MediaGraph,
    TaskRecord,
)
from .media_qa import MediaQAChecker
from .models import utcnow_iso
from .production_os import ProductionAdmissionError, ReferenceBinding, ShotContract

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
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise ProgrammaticGraphicsError("chart values must be numeric")
        if not math.isfinite(float(self.value)) or float(self.value) < 0:
            raise ProgrammaticGraphicsError("chart values must be finite and nonnegative")
        if not isinstance(self.display_value, str):
            raise ProgrammaticGraphicsError("display_value must be a string")


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
    background: str = "#1B2940"
    foreground: str = "#F4F7FB"
    accent: str = "#43D9C3"
    muted: str = "#93A4BC"

    def __post_init__(self) -> None:
        if not isinstance(self.spec_id, str) or not self.spec_id.strip():
            raise ProgrammaticGraphicsError("spec_id is required")
        if not isinstance(self.kind, str) or self.kind not in KINDS:
            raise ProgrammaticGraphicsError(f"unsupported graphic kind: {self.kind}")
        if not isinstance(self.title, str) or not self.title.strip():
            raise ProgrammaticGraphicsError("title is required")
        for field_name in ("subtitle", "kicker", "metric", "metric_label"):
            if not isinstance(getattr(self, field_name), str):
                raise ProgrammaticGraphicsError(f"{field_name} must be a string")
        if (
            isinstance(self.duration_seconds, bool)
            or not isinstance(self.duration_seconds, (int, float))
            or not math.isfinite(float(self.duration_seconds))
            or not 2.0 <= float(self.duration_seconds) <= 15.0
        ):
            raise ProgrammaticGraphicsError("shot graphic duration must be between 2 and 15 seconds")
        if (
            not isinstance(self.width, int) or not isinstance(self.height, int)
            or self.width < 640 or self.height < 640
            or self.width > 3840 or self.height > 3840
            or self.width % 2 or self.height % 2
        ):
            raise ProgrammaticGraphicsError("width/height must be even integers in [640, 3840]")
        if not isinstance(self.fps, int) or self.fps not in FPS_OPTIONS:
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
        if not isinstance(self.chart_data, tuple) or not all(isinstance(point, ChartDatum) for point in self.chart_data):
            raise ProgrammaticGraphicsError("chart_data must contain ChartDatum values")
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
    if not isinstance(payload, Mapping):
        raise ProgrammaticGraphicsError("graphic must be an object")
    data = dict(payload)
    points = data.get("chart_data", [])
    if not isinstance(points, list) or not all(isinstance(point, dict) for point in points):
        raise ProgrammaticGraphicsError("chart_data must be a list of objects")
    try:
        data["chart_data"] = tuple(ChartDatum(**point) for point in points)
        return GraphicSpec(**data)
    except (TypeError, AttributeError, ValueError, ProgrammaticGraphicsError) as exc:
        if isinstance(exc, ProgrammaticGraphicsError):
            raise
        raise ProgrammaticGraphicsError(f"invalid GraphicSpec: {exc}") from exc


def shot_contract_from_dict(payload: Mapping[str, Any]) -> ShotContract:
    if not isinstance(payload, Mapping):
        raise ProgrammaticGraphicsError("shot_contract must be an object")
    data = dict(payload)
    references = data.get("references", [])
    if not isinstance(references, list) or not all(isinstance(ref, dict) for ref in references):
        raise ProgrammaticGraphicsError("ShotContract references must be a list of objects")
    try:
        data["references"] = tuple(ReferenceBinding(**ref) for ref in references)
        set_fields = ("allowed_modes", "required_capabilities")
        tuple_fields = (
            "must_have", "must_not_have", "graceful_degradation", "stop_conditions",
            "source_claim_ids", "ip_identity_invariants", "ip_identity_forbidden_drift",
        )
        for key in set_fields + tuple_fields:
            raw = data.get(key, [])
            if not isinstance(raw, (list, tuple)) or not all(isinstance(item, str) for item in raw):
                raise ProgrammaticGraphicsError(f"ShotContract {key} must be a list of strings")
            data[key] = frozenset(raw) if key in set_fields else tuple(raw)
        for key in ("quality_targets", "value_vector"):
            data.setdefault(key, {})
            if not isinstance(data[key], dict):
                raise ProgrammaticGraphicsError(f"ShotContract {key} must be an object")
        return ShotContract(**data)
    except (TypeError, AttributeError, ValueError, ProductionAdmissionError) as exc:
        raise ProgrammaticGraphicsError(f"invalid ShotContract: {exc}") from exc


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


def _load_font(font_path: str | Path, font_size: int, field: str) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(font_path), font_size)
    except OSError as exc:
        raise ProgrammaticGraphicsError(
            f"cannot measure {field} with the supplied font: {exc}"
        ) from exc


def _wrap_pixel_text(
    text: str,
    *,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    field: str,
) -> list[str]:
    """Greedy pixel-accurate wrapping; preserves words where possible and supports CJK."""
    lines: list[str] = []
    for paragraph in text.splitlines() or [text]:
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for token in re.findall(r"\s+|\S+", paragraph):
            if token.isspace():
                if current and not current.endswith(" "):
                    current += " "
                continue
            for char in token:
                candidate = current + char
                if font.getlength(candidate) <= max_width:
                    current = candidate
                    continue
                line = current.rstrip()
                if line:
                    lines.append(line)
                current = char
                if font.getlength(current) > max_width:
                    raise ProgrammaticGraphicsError(
                        f"{field} contains a glyph wider than its {max_width}px text budget"
                    )
        if current or not lines:
            lines.append(current.rstrip())
    return lines


def _fit_wrapped_text(
    text: str,
    *,
    font_path: str | Path,
    base_font_size: int,
    min_font_size: int,
    max_width: int,
    max_lines: int,
    field: str,
    max_height_px: int | None = None,
    line_spacing: int = 0,
) -> tuple[str, int, dict[str, Any]]:
    if not text:
        return "", base_font_size, {
            "font_size": base_font_size,
            "max_width_px": max_width,
            "max_height_px": max_height_px,
            "line_widths_px": [],
            "line_count": 0,
            "line_height_px": 0,
            "total_height_px": 0,
            "fit": True,
        }
    last_error: Exception | None = None
    for size in range(base_font_size, min_font_size - 1, -1):
        font = _load_font(font_path, size, field)
        try:
            lines = _wrap_pixel_text(
                text, font=font, max_width=max_width, field=field,
            )
        except ProgrammaticGraphicsError as exc:
            last_error = exc
            continue
        if len(lines) <= max_lines:
            widths = [round(float(font.getlength(line)), 2) for line in lines]
            ascent, descent = font.getmetrics()
            line_height = ascent + descent
            total_height = line_height * len(lines) + line_spacing * max(0, len(lines) - 1)
            height_fits = max_height_px is None or total_height <= max_height_px
            if not height_fits:
                continue
            return "\n".join(lines), size, {
                "font_size": size,
                "max_width_px": max_width,
                "max_height_px": max_height_px,
                "line_widths_px": widths,
                "line_count": len(lines),
                "line_height_px": line_height,
                "total_height_px": total_height,
                "fit": all(width <= max_width for width in widths) and height_fits,
            }
    detail = f": {last_error}" if last_error else ""
    raise ProgrammaticGraphicsError(
        f"{field} cannot fit within {max_width}px, {max_lines} lines"
        f"{f' and {max_height_px}px height' if max_height_px is not None else ''} "
        f"at font sizes {base_font_size}..{min_font_size}{detail}"
    )


def _fit_single_line_text(
    text: str,
    *,
    font_path: str | Path,
    base_font_size: int,
    min_font_size: int,
    max_width: int,
    field: str,
) -> tuple[int, dict[str, Any]]:
    if not text or "\n" in text or "\r" in text:
        raise ProgrammaticGraphicsError(f"{field} must be nonempty single-line text")
    for size in range(base_font_size, min_font_size - 1, -1):
        font = _load_font(font_path, size, field)
        measured = round(float(font.getlength(text)), 2)
        if measured <= max_width:
            return size, {
                "font_size": size,
                "max_width_px": max_width,
                "measured_width_px": measured,
                "fit": True,
            }
    raise ProgrammaticGraphicsError(
        f"{field} cannot fit within {max_width}px at font sizes "
        f"{base_font_size}..{min_font_size}"
    )


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
        "expansion=none:shadowcolor=0x000000@0.32:shadowx=2:shadowy=3:"
        "alpha='if(lt(t,0.18),0,if(lt(t,0.78),(t-0.18)/0.60,1))'"
    )


def _filter_script(
    spec: GraphicSpec,
    *,
    font_path: str | Path,
) -> tuple[str, dict[str, str], dict[str, Any]]:
    center_width = int(spec.width * 0.84)
    text_files: dict[str, str] = {}
    layout: dict[str, Any] = {}

    def wrapped_field(
        key: str,
        value: str,
        base_size: int,
        *,
        width: int = center_width,
        max_lines: int,
        min_size: int | None = None,
        max_height_px: int | None = None,
        line_spacing: int = 0,
    ) -> int:
        content, size, evidence = _fit_wrapped_text(
            value,
            font_path=font_path,
            base_font_size=base_size,
            min_font_size=min_size or max(14, int(base_size * 0.55)),
            max_width=width,
            max_lines=max_lines,
            field=key,
            max_height_px=max_height_px,
            line_spacing=line_spacing,
        )
        text_files[f"{key}.txt"] = content
        layout[key] = evidence
        return size

    def single_line_field(
        key: str,
        value: str,
        base_size: int,
        *,
        width: int,
        min_size: int | None = None,
    ) -> int:
        size, evidence = _fit_single_line_text(
            value,
            font_path=font_path,
            base_font_size=base_size,
            min_font_size=min_size or max(12, int(base_size * 0.55)),
            max_width=width,
            field=key,
        )
        text_files[f"{key}.txt"] = value
        layout[key] = evidence
        return size

    kicker_size = 0
    if spec.kicker:
        kicker_size = wrapped_field(
            "kicker", spec.kicker, max(18, int(spec.height * 0.018)),
            max_lines=1,
        )

    if spec.kind in {"TITLE_CARD", "QUOTE_CARD"}:
        title_base = max(42, int(spec.height * 0.052))
        subtitle_base = max(24, int(spec.height * 0.027))
        title_lines, subtitle_lines = 3, 4
    else:
        title_base = max(34, int(spec.height * 0.038))
        subtitle_base = max(20, int(spec.height * 0.022))
        title_lines, subtitle_lines = 2, 2

    title_size = wrapped_field(
        "title", spec.title, title_base, max_lines=title_lines,
    )
    subtitle_size = 0
    if spec.subtitle:
        subtitle_size = wrapped_field(
            "subtitle", spec.subtitle, subtitle_base,
            max_lines=subtitle_lines,
        )

    metric_size = 0
    metric_label_size = 0
    if spec.kind == "STAT_CARD":
        metric_size = single_line_field(
            "metric", spec.metric, max(72, int(spec.height * 0.13)),
            width=center_width,
            min_size=max(28, int(spec.height * 0.03)),
        )
        metric_label_size = wrapped_field(
            "metric_label", spec.metric_label,
            max(24, int(spec.height * 0.028)),
            max_lines=2,
        )

    chart_layout: list[tuple[str, str, int, int, dict[str, int]]] = []
    chart_geometry: dict[str, Any] = {}
    if spec.kind == "BAR_CHART":
        left = int(spec.width * 0.08)
        bar_x = int(spec.width * 0.29)
        bar_max = int(spec.width * 0.57)
        label_width = max(24, bar_x - left - int(spec.width * 0.03))
        value_x = bar_x + bar_max + int(spec.width * 0.015)
        value_width = max(24, spec.width - value_x - int(spec.width * 0.02))
        chart_top = int(spec.height * 0.47)
        chart_bottom = int(spec.height * 0.92)
        row_height = (chart_bottom - chart_top) / len(spec.chart_data)
        label_height_budget = max(14, int(row_height) - 6)
        bar_h = max(12, min(18, int(row_height * 0.34)))
        for index, point in enumerate(spec.chart_data):
            label_key = f"chart_label_{index}"
            value_key = f"chart_value_{index}"
            label_size = wrapped_field(
                label_key, point.label,
                max(18, int(spec.height * 0.019)),
                width=label_width, max_lines=2,
                min_size=12, max_height_px=label_height_budget,
                line_spacing=2,
            )
            display_value = point.display_value or f"{point.value:g}"
            value_size = single_line_field(
                value_key, display_value,
                max(18, int(spec.height * 0.019)),
                width=value_width,
            )
            row_top = round(chart_top + index * row_height)
            row_bottom = round(chart_top + (index + 1) * row_height)
            row_center = (row_top + row_bottom) / 2
            label_height = int(layout[label_key]["total_height_px"])
            value_height = int(layout[value_key]["line_height_px"])
            bar_y = round(row_center - bar_h / 2)
            label_y = round(row_center - label_height / 2)
            value_y = round(row_center - value_height / 2)
            row = {
                "row_top_px": row_top,
                "row_bottom_px": row_bottom,
                "row_center_px": round(row_center, 2),
                "bar_y_px": bar_y,
                "bar_height_px": bar_h,
                "label_y_px": label_y,
                "label_height_px": label_height,
                "value_y_px": value_y,
                "value_height_px": value_height,
            }
            if (
                label_height > label_height_budget
                or label_y < row_top
                or label_y + label_height > row_bottom
                or value_y < row_top
                or value_y + value_height > row_bottom
                or bar_y < row_top
                or bar_y + bar_h > row_bottom
            ):
                raise ProgrammaticGraphicsError(
                    f"chart row {index} text/bar exceeds its vertical allocation"
                )
            layout[label_key]["max_height_px"] = label_height_budget
            layout[label_key]["total_height_px"] = label_height
            chart_layout.append((label_key, value_key, label_size, value_size, row))
        chart_geometry = {
            "top_px": chart_top,
            "bottom_px": chart_bottom,
            "row_height_px": round(row_height, 2),
            "label_height_budget_px": label_height_budget,
            "rows": [item[4] for item in chart_layout],
            "fit": True,
        }
        layout["chart_geometry"] = chart_geometry

    filters: list[str] = [
        f"drawbox=x=0:y=0:w=iw:h={max(5, int(spec.height * 0.006))}:color={_color(spec.accent)}@0.96:t=fill"
    ]
    if kicker_size:
        filters.append(_drawtext(
            "kicker.txt", font_size=kicker_size,
            x="(w-text_w)/2", y=str(int(spec.height * 0.19)),
            color=spec.accent, line_spacing=4,
        ))

    if spec.kind in {"TITLE_CARD", "QUOTE_CARD"}:
        filters.append(_drawtext(
            "title.txt", font_size=title_size,
            x="(w-text_w)/2", y=str(int(spec.height * 0.32)),
            color=spec.foreground, line_spacing=max(12, int(spec.height * 0.012)),
        ))
        if subtitle_size:
            filters.append(_drawtext(
                "subtitle.txt", font_size=subtitle_size,
                x="(w-text_w)/2", y=str(int(spec.height * 0.57)),
                color=spec.muted, line_spacing=max(8, int(spec.height * 0.008)),
            ))
    elif spec.kind == "STAT_CARD":
        filters.append(_drawtext(
            "title.txt", font_size=title_size,
            x="(w-text_w)/2", y=str(int(spec.height * 0.25)),
            color=spec.foreground,
        ))
        filters.append(_drawtext(
            "metric.txt", font_size=metric_size,
            x="(w-text_w)/2", y=str(int(spec.height * 0.43)),
            color=spec.accent, line_spacing=0,
        ))
        filters.append(_drawtext(
            "metric_label.txt", font_size=metric_label_size,
            x="(w-text_w)/2", y=str(int(spec.height * 0.60)),
            color=spec.muted,
        ))
        if subtitle_size:
            filters.append(_drawtext(
                "subtitle.txt", font_size=subtitle_size,
                x="(w-text_w)/2", y=str(int(spec.height * 0.72)),
                color=spec.foreground,
            ))
    elif spec.kind == "BAR_CHART":
        filters.append(_drawtext(
            "title.txt", font_size=title_size,
            x="(w-text_w)/2", y=str(int(spec.height * 0.25)),
            color=spec.foreground,
        ))
        if subtitle_size:
            filters.append(_drawtext(
                "subtitle.txt", font_size=subtitle_size,
                x="(w-text_w)/2", y=str(int(spec.height * 0.36)),
                color=spec.muted,
            ))
        max_value = max(float(point.value) for point in spec.chart_data)
        bar_x = int(spec.width * 0.29)
        bar_max = int(spec.width * 0.57)
        for index, point in enumerate(spec.chart_data):
            label_key, value_key, label_size, value_size, row = chart_layout[index]
            label_name = f"{label_key}.txt"
            value_name = f"{value_key}.txt"
            y = row["bar_y_px"]
            filters.append(_drawtext(
                label_name, font_size=label_size,
                x=str(left), y=str(row["label_y_px"]), color=spec.foreground,
                line_spacing=2,
            ))
            filters.append(
                f"drawbox=x={bar_x}:y={y}:w={bar_max}:h={row['bar_height_px']}:color=0x29354A:t=fill"
            )
            ratio = float(point.value) / max_value if max_value else 0.0
            filters.append(
                f"drawbox=x={bar_x}:y={y}:w={max(1, int(bar_max * ratio))}:"
                f"h={row['bar_height_px']}:color={_color(spec.accent)}:t=fill:enable='gte(t,0.65)'"
            )
            filters.append(_drawtext(
                value_name, font_size=value_size,
                x=str(bar_x + bar_max + int(spec.width * 0.015)),
                y=str(row["value_y_px"]), color=spec.accent,
                line_spacing=2,
            ))

    progress_y = spec.height - max(8, int(spec.height * 0.008))
    filters.append(
        f"drawbox=x=0:y={progress_y}:w='iw*min(max(t/{spec.duration_seconds:.3f},0),1)':"
        f"h={max(8, int(spec.height * 0.008))}:color={_color(spec.accent)}:t=fill"
    )
    filters.append("format=yuv420p[v]")
    return "[0:v]" + ",".join(filters), text_files, layout


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
    graph, text_files, text_layout = _filter_script(spec, font_path=font)
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
        "reference_bindings": [
            {
                "asset_id": ref.asset_id,
                "version_id": ref.version_id,
                "digest": ref.digest,
                "role": ref.role,
                "rights_ref": ref.rights_ref,
                "consent_ref": ref.consent_ref,
            }
            for ref in shot.references
        ],
        "truth_mode": shot.truth_mode,
        "graphic_spec": _jsonable(spec),
        "graphic_spec_digest": _digest(spec),
        "text_layout": text_layout,
        "text_layout_digest": _digest(text_layout),
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


def _normalize_reference_digest(value: object) -> str:
    normalized = str(value).strip().lower()
    return normalized[7:] if normalized.startswith("sha256:") else normalized


def validate_shot_graph_bindings(graph: MediaGraph, shot: ShotContract) -> None:
    """Require exact, promoted MediaGraph versions and matching contract digests."""
    context = graph.contexts.get(shot.shot_id)
    if context is None or context.kind != "SHOT":
        raise ProgrammaticGraphicsError(
            f"MediaGraph must already contain SHOT context {shot.shot_id}"
        )
    missing: list[str] = []
    mismatches: list[str] = []
    unpromoted: list[str] = []
    for binding in shot.references:
        ref = AssetRef(binding.asset_id, binding.version_id)
        asset = graph.assets.get(ref)
        if asset is None:
            missing.append(ref.key())
            continue
        if graph.asset_state(ref) != "PROMOTED":
            unpromoted.append(ref.key())
        if _normalize_reference_digest(asset.digest) != _normalize_reference_digest(binding.digest):
            mismatches.append(
                f"{ref.key()} contract={binding.digest} graph={asset.digest}"
            )
    if missing:
        raise ProgrammaticGraphicsError("MediaGraph reference assets missing: " + ", ".join(missing))
    if unpromoted:
        raise ProgrammaticGraphicsError("MediaGraph reference assets are not promoted: " + ", ".join(unpromoted))
    if mismatches:
        raise ProgrammaticGraphicsError("MediaGraph reference digest mismatch: " + "; ".join(mismatches))


def register_graph_candidate(
    graph: MediaGraph,
    shot: ShotContract,
    spec: GraphicSpec,
    receipt: Mapping[str, Any],
) -> str:
    """Register a rendered take as CANDIDATE with exact lineage; never promote it."""
    validate_shot_graph_bindings(graph, shot)
    refs = tuple(AssetRef(ref.asset_id, ref.version_id) for ref in shot.references)

    digest = str(receipt.get("media_sha256") or "")
    media_path = Path(str(receipt.get("media_path") or ""))
    if (
        receipt.get("candidate_only") is not True
        or receipt.get("promotion_authorized") is not False
        or receipt.get("release_authorized") is not False
        or receipt.get("renderer") != "video_growth_agent.programmatic_graphics"
        or receipt.get("shot_contract_digest") != _digest(shot)
        or receipt.get("graphic_spec_digest") != _digest(spec)
        or len(digest) != 64
        or not media_path.is_file()
        or _sha256(media_path) != digest
    ):
        raise ProgrammaticGraphicsError("render receipt does not match the exact ShotContract/spec/media candidate")
    actual_qa = MediaQAChecker().inspect(media_path).to_dict()
    if actual_qa.get("hard_pass") is not True or receipt.get("qa_hard_pass") is not True:
        raise ProgrammaticGraphicsError("technical QA must hard-pass before graph candidate registration")
    asset_ref = AssetRef(
        asset_id=f"{shot.shot_id}:programmatic-graphic:{spec.spec_id}",
        version_id=digest[:16],
    )
    evidence_id = f"evidence:{asset_ref.key()}"
    task_id = f"task:programmatic-graphics:{shot.shot_id}:{spec.spec_id}:{digest[:12]}"
    if asset_ref in graph.assets:
        raise ProgrammaticGraphicsError(f"MediaGraph asset version already exists: {asset_ref.key()}")
    if evidence_id in graph.evidence:
        raise ProgrammaticGraphicsError(f"MediaGraph evidence already exists: {evidence_id}")
    if task_id in graph.tasks:
        raise ProgrammaticGraphicsError(f"MediaGraph task already exists: {task_id}")

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
            "shot_contract_digest": receipt.get("shot_contract_digest"),
            "graphic_spec_digest": receipt.get("graphic_spec_digest"),
            "qa_hard_pass": receipt.get("qa_hard_pass") is True,
            "candidate_only": True,
            "truth_mode": shot.truth_mode,
            "audio_mode": receipt.get("audio_mode"),
        },
    ))
    graph.add_evidence(EvidenceRecord(
        evidence_id=evidence_id,
        subject_type="ASSET_VERSION",
        subject_id=asset_ref.key(),
        action="PROGRAMMATIC_GRAPHIC_RENDERED",
        refs=(media_uri, f"sha256:{digest}", str(receipt.get("receipt_id") or "")),
        observed_at=str(receipt.get("rendered_at") or utcnow_iso()),
        metadata={
            "renderer_version": RENDERER_VERSION,
            "shot_contract_digest": receipt.get("shot_contract_digest"),
            "graphic_spec_digest": receipt.get("graphic_spec_digest"),
            "qa_hard_pass": actual_qa.get("hard_pass") is True,
            "candidate_only": True,
        },
    ))
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
            "shot_contract_digest": receipt.get("shot_contract_digest"),
            "graphic_spec_digest": receipt.get("graphic_spec_digest"),
            "promotion_authorized": False,
        },
    ))
    return asset_ref.key()
