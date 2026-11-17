from __future__ import annotations

from dataclasses import dataclass
import json
import math
import re
from pathlib import Path
from typing import Any, Mapping


class ProductionContractError(ValueError):
    pass


ARCHETYPES = {"ENGINEERING_PROOF", "CINEMATIC_EXPLAINER", "NEWS_FICTION_MEME", "HYBRID", "CUSTOM"}


def _number(value: Any, field: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProductionContractError(f"{field} must be numeric")
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise ProductionContractError(f"{field} must be finite and >= {minimum}")
    return result


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProductionContractError(f"{field} must be a non-empty string")
    return value.strip()


def _strict_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ProductionContractError(f"{field} must be a boolean")
    return value


@dataclass(frozen=True)
class VideoClip:
    input_name: str
    source_start_seconds: float
    duration_seconds: float
    fit: str = "cover"

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "VideoClip":
        if not isinstance(raw, Mapping):
            raise ProductionContractError("each video clip must be an object")
        fit = str(raw.get("fit", "cover")).upper()
        if fit not in {"COVER", "CONTAIN"}:
            raise ProductionContractError("clip.fit must be COVER or CONTAIN")
        return cls(
            input_name=_string(raw.get("input_name"), "clip.input_name"),
            source_start_seconds=_number(raw.get("source_start_seconds", 0), "clip.source_start_seconds"),
            duration_seconds=_number(raw.get("duration_seconds"), "clip.duration_seconds", minimum=0.001),
            fit=fit,
        )


@dataclass(frozen=True)
class AudioTrack:
    input_name: str
    start_seconds: float = 0.0
    duration_seconds: float | None = None
    gain_db: float = 0.0
    role: str = "MIX"

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "AudioTrack":
        if not isinstance(raw, Mapping):
            raise ProductionContractError("each audio track must be an object")
        duration = raw.get("duration_seconds")
        if duration is not None:
            duration = _number(duration, "audio_track.duration_seconds", minimum=0.001)
        gain = raw.get("gain_db", 0.0)
        if isinstance(gain, bool) or not isinstance(gain, (int, float)) or not math.isfinite(float(gain)):
            raise ProductionContractError("audio_track.gain_db must be finite numeric")
        role = str(raw.get("role", "MIX")).upper()
        if role not in {"VOICE", "MUSIC", "SFX", "MIX", "AMBIENCE"}:
            raise ProductionContractError(f"unsupported audio role: {role}")
        return cls(
            input_name=_string(raw.get("input_name"), "audio_track.input_name"),
            start_seconds=_number(raw.get("start_seconds", 0), "audio_track.start_seconds"),
            duration_seconds=duration,
            gain_db=float(gain),
            role=role,
        )


@dataclass(frozen=True)
class RenderSpec:
    project_id: str
    archetype: str
    width: int
    height: int
    fps: float
    duration_seconds: float
    clips: tuple[VideoClip, ...]
    audio_tracks: tuple[AudioTrack, ...]
    audio_required: bool = True
    captions_input: str | None = None
    burn_captions: bool = False
    video_output: str = "final-video"
    audio_output: str = "audio-master"
    receipt_output: str = "render-receipt"

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "RenderSpec":
        if not isinstance(raw, Mapping):
            raise ProductionContractError("render spec must be an object")
        if str(raw.get("schema_version", "1.0")) != "1.0":
            raise ProductionContractError("render spec schema_version must be 1.0")
        archetype = _string(raw.get("archetype"), "archetype").upper()
        if archetype not in ARCHETYPES:
            raise ProductionContractError(f"unsupported production archetype: {archetype}")
        width, height = raw.get("width"), raw.get("height")
        if isinstance(width, bool) or not isinstance(width, int) or width < 16:
            raise ProductionContractError("width must be an integer >= 16")
        if isinstance(height, bool) or not isinstance(height, int) or height < 16:
            raise ProductionContractError("height must be an integer >= 16")
        fps = _number(raw.get("fps"), "fps", minimum=1)
        duration = _number(raw.get("duration_seconds"), "duration_seconds", minimum=0.1)
        clips_raw, audio_raw = raw.get("clips"), raw.get("audio_tracks", [])
        if not isinstance(clips_raw, list) or not clips_raw:
            raise ProductionContractError("clips must be a non-empty array")
        if not isinstance(audio_raw, list):
            raise ProductionContractError("audio_tracks must be an array")
        captions_input = raw.get("captions_input")
        if captions_input is not None:
            captions_input = _string(captions_input, "captions_input")
        return cls(
            project_id=_string(raw.get("project_id"), "project_id"),
            archetype=archetype,
            width=width,
            height=height,
            fps=fps,
            duration_seconds=duration,
            clips=tuple(VideoClip.from_dict(item) for item in clips_raw),
            audio_tracks=tuple(AudioTrack.from_dict(item) for item in audio_raw),
            audio_required=_strict_bool(raw.get("audio_required", True), "audio_required"),
            captions_input=captions_input,
            burn_captions=_strict_bool(raw.get("burn_captions", False), "burn_captions"),
            video_output=_string(raw.get("video_output", "final-video"), "video_output"),
            audio_output=_string(raw.get("audio_output", "audio-master"), "audio_output"),
            receipt_output=_string(raw.get("receipt_output", "render-receipt"), "receipt_output"),
        )

    def validate_inputs(self, input_names: set[str]) -> None:
        required = {clip.input_name for clip in self.clips}
        required.update(track.input_name for track in self.audio_tracks)
        if self.captions_input:
            required.add(self.captions_input)
        missing = sorted(required - input_names)
        if missing:
            raise ProductionContractError(f"render spec references undeclared task inputs: {missing}")
        if not self.audio_tracks:
            raise ProductionContractError("a final master requires an explicit audio track; intentional silence must be supplied as an audio asset")
        if self.burn_captions and not self.captions_input:
            raise ProductionContractError("burn_captions=true requires captions_input")
        clip_total = sum(clip.duration_seconds for clip in self.clips)
        if abs(clip_total - self.duration_seconds) > max(0.05, 1.0 / self.fps):
            raise ProductionContractError(
                f"clip durations total {clip_total:.3f}s but project duration is {self.duration_seconds:.3f}s"
            )
        for track in self.audio_tracks:
            if track.start_seconds >= self.duration_seconds:
                raise ProductionContractError(f"audio track starts after project end: {track.input_name}")
            if track.duration_seconds is not None and track.start_seconds + track.duration_seconds > self.duration_seconds + 0.05:
                raise ProductionContractError(f"audio track exceeds project duration: {track.input_name}")


def validate_srt_file(path: str | Path, *, duration_seconds: float) -> dict[str, Any]:
    source = Path(path)
    try:
        text = source.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ProductionContractError(f"cannot read subtitle file: {exc}") from exc
    blocks = [block.strip() for block in re.split(r"\r?\n\s*\r?\n", text) if block.strip()]
    if not blocks:
        raise ProductionContractError("subtitle file is empty")
    timestamp = re.compile(r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})$")
    def seconds(value: str) -> float:
        match = timestamp.match(value.strip())
        if not match:
            raise ProductionContractError(f"invalid SRT timestamp: {value}")
        hours, minutes, secs, millis = (int(part) for part in match.groups())
        return hours * 3600 + minutes * 60 + secs + millis / 1000.0
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3 or not lines[0].strip().isdigit() or " --> " not in lines[1]:
            raise ProductionContractError("invalid SRT cue: expected index, time range and text")
        left, right = lines[1].split(" --> ", 1)
        start, end = seconds(left), seconds(right)
        if end <= start or start < 0 or end > duration_seconds + 0.05:
            raise ProductionContractError("SRT cue is outside the video duration or has non-positive duration")
        if not any(line.strip() for line in lines[2:]):
            raise ProductionContractError("SRT cue has no text")
    return {"cue_count": len(blocks), "duration_seconds": duration_seconds, "encoding": "utf-8"}


@dataclass(frozen=True)
class FrameRenderSpec:
    project_id: str
    renderer_input: str
    entrypoint: str
    width: int
    height: int
    fps: float
    duration_seconds: float
    asset_inputs: tuple[str, ...]
    params: Mapping[str, Any]
    trusted_code_execution: bool
    video_output: str = "shot-video"
    receipt_output: str = "shot-render-receipt"

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "FrameRenderSpec":
        if not isinstance(raw, Mapping) or str(raw.get("schema_version", "1.0")) != "1.0":
            raise ProductionContractError("frame render spec must be an object with schema_version 1.0")
        width, height = raw.get("width"), raw.get("height")
        if isinstance(width, bool) or not isinstance(width, int) or width < 16:
            raise ProductionContractError("frame render width must be an integer >= 16")
        if isinstance(height, bool) or not isinstance(height, int) or height < 16:
            raise ProductionContractError("frame render height must be an integer >= 16")
        fps = _number(raw.get("fps"), "frame_render.fps", minimum=1)
        duration = _number(raw.get("duration_seconds"), "frame_render.duration_seconds", minimum=0.1)
        frames = duration * fps
        if abs(frames - round(frames)) > 1e-6:
            raise ProductionContractError("duration_seconds * fps must be an integer frame count")
        entrypoint = _string(raw.get("entrypoint", "render_frame"), "entrypoint")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", entrypoint):
            raise ProductionContractError("entrypoint must be a simple Python identifier")
        assets = raw.get("asset_inputs", [])
        if not isinstance(assets, list) or not all(isinstance(item, str) and item.strip() for item in assets):
            raise ProductionContractError("asset_inputs must be an array of non-empty artifact names")
        params = raw.get("params", {})
        if not isinstance(params, Mapping):
            raise ProductionContractError("params must be an object")
        return cls(
            project_id=_string(raw.get("project_id"), "project_id"),
            renderer_input=_string(raw.get("renderer_input"), "renderer_input"),
            entrypoint=entrypoint,
            width=width, height=height, fps=fps, duration_seconds=duration,
            asset_inputs=tuple(assets), params=dict(params),
            trusted_code_execution=_strict_bool(raw.get("trusted_code_execution", False), "trusted_code_execution"),
            video_output=_string(raw.get("video_output", "shot-video"), "video_output"),
            receipt_output=_string(raw.get("receipt_output", "shot-render-receipt"), "receipt_output"),
        )

    @property
    def frame_count(self) -> int:
        return int(round(self.duration_seconds * self.fps))

    def validate_inputs(self, input_names: set[str]) -> None:
        required = {self.renderer_input, *self.asset_inputs}
        missing = sorted(required - input_names)
        if missing:
            raise ProductionContractError(f"frame render spec references undeclared task inputs: {missing}")
        if not self.trusted_code_execution:
            raise ProductionContractError("trusted_code_execution=true is required for project Python renderer code")
