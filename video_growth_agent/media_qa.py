from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from .models import QACheck, QAReport

Runner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


def _run(cmd: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def _float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class MediaQAPolicy:
    duration_delta_s: float = 0.15
    require_audio: bool = True
    max_true_peak_dbfs: float = -1.0
    loudness_min_lufs: float = -20.0
    loudness_max_lufs: float = -13.0
    fail_black_segment_s: float = 0.75
    report_silence_segment_s: float = 1.2


class MediaQAChecker:
    def __init__(self, policy: MediaQAPolicy | None = None, runner: Runner = _run):
        self.policy = policy or MediaQAPolicy()
        self.runner = runner

    @staticmethod
    def tools_available() -> bool:
        return shutil.which("ffprobe") is not None and shutil.which("ffmpeg") is not None

    def probe(self, media: str | Path) -> dict:
        proc = self.runner(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(media)])
        if proc.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {proc.stderr.strip()}")
        return json.loads(proc.stdout)

    def inspect(self, media: str | Path) -> QAReport:
        media = str(media)
        probe = self.probe(media)
        streams = probe.get("streams", [])
        videos = [s for s in streams if s.get("codec_type") == "video"]
        audios = [s for s in streams if s.get("codec_type") == "audio"]
        checks: list[QACheck] = []
        if not videos:
            checks.append(QACheck("video_stream", "FAIL", "No video stream found"))
            return QAReport(media_uri=media, checks=tuple(checks), metadata={"checker": "ffmpeg-ffprobe-v0.2", "probe": probe})
        video = videos[0]
        vdur = _float(video.get("duration"), _float(probe.get("format", {}).get("duration")))
        fps = self._fps(video.get("avg_frame_rate") or video.get("r_frame_rate"))
        frames = int(video.get("nb_frames") or round(vdur * fps)) if fps > 0 else int(video.get("nb_frames") or 0)
        checks.append(QACheck("video_stream", "PASS", f"{video.get('width')}x{video.get('height')}, duration={vdur:.3f}s, fps={fps:.3f}, frames={frames}"))
        if self.policy.require_audio and not audios:
            checks.append(QACheck("audio_stream", "FAIL", "Required audio stream missing"))
        elif audios:
            audio = audios[0]
            adur = _float(audio.get("duration"), _float(probe.get("format", {}).get("duration")))
            delta = abs(vdur - adur)
            checks.append(QACheck("stream_duration_match", "PASS" if delta <= self.policy.duration_delta_s else "FAIL", f"video={vdur:.3f}s audio={adur:.3f}s delta={delta:.3f}s tolerance={self.policy.duration_delta_s:.3f}s"))
            checks.extend(self._audio_checks(media))
        checks.append(self._black_check(media))
        metadata = {"checker": "ffmpeg-ffprobe-v0.2", "video_duration": vdur, "fps": fps, "frame_count": frames}
        path = Path(media)
        if path.is_file():
            metadata["sha256"] = self._sha256(path)
        return QAReport(media_uri=media, checks=tuple(checks), metadata=metadata)

    def extract_frames(self, media: str | Path, output_dir: str | Path, count: int = 9) -> list[str]:
        probe = self.probe(media)
        duration = _float(probe.get("format", {}).get("duration"))
        if duration <= 0:
            raise RuntimeError("Cannot extract QA frames without positive duration")
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        refs: list[str] = []
        streams = probe.get("streams", [])
        video = next((s for s in streams if s.get("codec_type") == "video"), {})
        fps = self._fps(video.get("avg_frame_rate") or video.get("r_frame_rate"))
        safe_end = max(0.0, duration - max(0.10, (2.0 / fps if fps > 0 else 0.10)))
        for i in range(count):
            t = 0.0 if count == 1 else safe_end * i / (count - 1)
            path = out / f"frame-{i+1:02d}-{t:07.3f}s.png"
            proc = self.runner(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(media), "-frames:v", "1", str(path)])
            if proc.returncode != 0 or not path.exists() or path.stat().st_size == 0:
                raise RuntimeError(f"frame extraction failed at {t:.3f}s: {proc.stderr.strip()}")
            refs.append(str(path))
        return refs

    def _black_check(self, media: str) -> QACheck:
        proc = self.runner(["ffmpeg", "-hide_banner", "-i", media, "-vf", f"blackdetect=d={self.policy.fail_black_segment_s}:pix_th=0.10", "-an", "-f", "null", "-"])
        durations = [_float(x) for x in re.findall(r"black_duration:([0-9.]+)", proc.stderr or "")]
        longest = max(durations, default=0.0)
        return QACheck("black_frames", "FAIL" if longest >= self.policy.fail_black_segment_s else "PASS", f"longest_detected_black={longest:.3f}s")

    def _audio_checks(self, media: str) -> list[QACheck]:
        checks: list[QACheck] = []
        loud = self.runner(["ffmpeg", "-hide_banner", "-i", media, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
        payload = self._extract_loudnorm_json(loud.stderr or "")
        if payload:
            integrated = _float(payload.get("input_i"), -99.0)
            true_peak = _float(payload.get("input_tp"), 99.0)
            checks.append(QACheck("integrated_loudness", "PASS" if self.policy.loudness_min_lufs <= integrated <= self.policy.loudness_max_lufs else "WARN", f"input_i={integrated:.2f} LUFS"))
            checks.append(QACheck("true_peak", "PASS" if true_peak <= self.policy.max_true_peak_dbfs else "FAIL", f"input_tp={true_peak:.2f} dBFS"))
        else:
            checks.append(QACheck("audio_metering", "FAIL", "Could not parse loudnorm analysis"))
        silence = self.runner(["ffmpeg", "-hide_banner", "-i", media, "-af", f"silencedetect=n=-50dB:d={self.policy.report_silence_segment_s}", "-vn", "-f", "null", "-"])
        durations = [_float(x) for x in re.findall(r"silence_duration: ([0-9.]+)", silence.stderr or "")]
        longest = max(durations, default=0.0)
        checks.append(QACheck("long_silence", "WARN" if longest >= self.policy.report_silence_segment_s else "PASS", f"longest_detected_silence={longest:.3f}s; warning may be intentional narrative silence"))
        return checks

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _extract_loudnorm_json(text: str) -> dict | None:
        starts = [m.start() for m in re.finditer(r"\{", text)]
        for start in reversed(starts):
            end = text.find("}", start)
            if end == -1:
                continue
            try:
                payload = json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                continue
            if "input_i" in payload and "input_tp" in payload:
                return payload
        return None

    @staticmethod
    def _fps(value: str | None) -> float:
        if not value:
            return 0.0
        if "/" in value:
            a, b = value.split("/", 1)
            den = _float(b)
            return _float(a) / den if den else 0.0
        return _float(value)

def prepare_directed_media_review(
    plan: dict,
    media: str | Path,
    *,
    checker: MediaQAChecker | None = None,
    frames_dir: str | Path | None = None,
    frame_count: int = 9,
) -> dict:
    """Bind an existing shot-review sheet to *bytes* of an actual media take.

    This creates evidence for a future human viewing, not a media-quality
    approval, provider endorsement, blindness attestation or graph promotion.
    The planned frame windows cannot be asserted to match generated footage
    until an editor independently checks/conforms its cuts.
    """
    from .prompt_director import build_shot_review_targets

    sheet = build_shot_review_targets(plan)
    path = Path(media)
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("directed media review needs a nonempty local video file")
    if frames_dir is not None and (type(frame_count) is not int or not 1 <= frame_count <= 60):
        raise ValueError("frame_count must be an integer from 1 through 60")
    inspector = checker or MediaQAChecker()
    inspection = inspector.inspect(path)
    if not any(c.check_id == "video_stream" and c.status == "PASS" for c in inspection.checks):
        raise ValueError("directed media review needs a decodable video stream")
    digest = inspection.metadata.get("sha256") or inspector._sha256(path)
    plan_digest = hashlib.sha256(
        json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    expected = sheet["expected_length_seconds"]
    measured = inspection.metadata.get("video_duration")
    tolerance = max(0.15, 2.0 / plan["brief"]["fps"])
    alignment = (
        "DURATION_UNAVAILABLE"
        if measured is None
        else "DURATION_WITHIN_TOLERANCE__CUTS_UNVERIFIED"
        if abs(measured - expected) <= tolerance
        else "DURATION_MISMATCH__EDIT_CONFORM_REQUIRED"
    )
    ref = {"uri": str(path), "sha256": digest, "byte_count": path.stat().st_size}
    sheet["media_asset_ref"] = ref
    sheet["source_plan_sha256"] = plan_digest
    sheet["actual_length_seconds"] = measured
    sheet["timeline_alignment"] = alignment
    sheet["technical_media_qa"] = inspection.to_dict()
    sheet["frame_samples"] = (
        inspector.extract_frames(path, frames_dir, count=frame_count)
        if frames_dir is not None else []
    )
    sheet["first_pass_viewing"] = {
        "clip": ref,
        "reviewer_blinding_verified": False,
        "responses": None,
        "questions": [
            "Without seeing the planned storyboard, recount the visible story and causal sequence.",
            "Identify the emotional change, identifiable characters and stable props that actually appeared.",
            "Record confusing actions, cuts, visual continuity defects and audio mismatches with observed timestamps.",
        ],
        "status": "NOT_EXECUTED",
    }
    sheet["assessment"] = "NOT_STARTED__REAL_MEDIA_BOUND"
    sheet["reviewer_independence"] = "NOT_ESTABLISHED"
    sheet["note"] = (
        "Real file bytes and mechanical QA are bound; technical QA pass is not cinematic "
        "or semantic quality. Planned shot windows and source tags require actual viewing "
        "and independent editorial alignment. Reviewer blinding is not established."
    )
    return sheet
