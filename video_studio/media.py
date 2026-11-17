from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import uuid
from typing import Any

from .engine import ContractError, GateError, StudioEngine


def _fraction(value: str | None) -> float | None:
    if not value or value in {"0/0", "N/A"}:
        return None
    try:
        numerator, denominator = value.split("/", 1)
        denominator_value = float(denominator)
        return float(numerator) / denominator_value if denominator_value else None
    except (ValueError, ZeroDivisionError):
        try:
            return float(value)
        except ValueError:
            return None


def probe_media(path: str | Path, requirements: dict[str, Any] | None = None, *, timeout_seconds: int = 120) -> dict[str, Any]:
    """Inspect real media bytes with FFmpeg and FFprobe; this measures technical facts only."""
    media = Path(path).resolve(strict=True)
    if not media.is_file() or media.stat().st_size == 0:
        raise ContractError("media must be a non-empty regular file")
    command = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size,bit_rate,format_name:stream=index,codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,sample_rate,channels,duration",
        "-of", "json", str(media),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, check=False)
    except FileNotFoundError as exc:
        raise GateError("ffprobe is not installed or is not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise GateError(f"ffprobe timed out after {timeout_seconds}s") from exc
    if completed.returncode != 0:
        raise GateError(f"ffprobe failed: {completed.stderr.strip()[:2000]}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise GateError("ffprobe returned invalid JSON") from exc

    streams = payload.get("streams", [])
    video = next((item for item in streams if item.get("codec_type") == "video"), None)
    audio = next((item for item in streams if item.get("codec_type") == "audio"), None)
    fmt = payload.get("format", {})
    duration = float(fmt["duration"]) if fmt.get("duration") not in (None, "N/A") else None
    fps = _fraction((video or {}).get("avg_frame_rate")) or _fraction((video or {}).get("r_frame_rate"))
    req = requirements or {}
    checks: list[dict[str, Any]] = []

    def check(check_id: str, passed: bool, observed: Any, expected: Any = None, note: str = "") -> None:
        checks.append({"check_id": check_id, "status": "PASS" if passed else "FAIL", "observed": observed, "expected": expected, "note": note})

    check("video_stream", video is not None, bool(video), True)
    audio_required = bool(req.get("audio_required", True))
    check("audio_stream", audio is not None or not audio_required, bool(audio), "required" if audio_required else "optional")

    duration_min = req.get("duration_min_seconds")
    duration_max = req.get("duration_max_seconds")
    if duration_min is not None or duration_max is not None:
        duration_ok = duration is not None and (duration_min is None or duration >= float(duration_min)) and (duration_max is None or duration <= float(duration_max))
        check("duration_range", duration_ok, duration, {"min": duration_min, "max": duration_max})
    else:
        check("duration_readable", duration is not None and duration > 0, duration, "> 0 seconds")

    resolution = req.get("resolution")
    if resolution:
        try:
            expected_width, expected_height = (int(part) for part in str(resolution).lower().split("x", 1))
            observed = [video.get("width"), video.get("height")] if video else None
            check("resolution", observed == [expected_width, expected_height], observed, [expected_width, expected_height])
        except (ValueError, TypeError):
            raise ContractError("requirements.resolution must use WIDTHxHEIGHT, e.g. 1080x1920")

    fps_expected = req.get("frame_rate")
    if fps_expected is not None:
        check("frame_rate", fps is not None and abs(fps - float(fps_expected)) < 0.05, fps, float(fps_expected))

    timed_streams = [item for item in streams if item.get("codec_type") in {"video", "audio"}]
    stream_durations = [
        float(item["duration"]) for item in timed_streams
        if item.get("duration") not in (None, "N/A")
    ]
    # Preserve the legacy production hard gates: complete decode, stream timing,
    # true peak and black-frame detection. A metadata-only ffprobe pass is not enough.
    if timed_streams and len(stream_durations) == len(timed_streams):
        tolerance = float(req.get("stream_duration_tolerance_seconds", 0.25))
        delta = max(stream_durations) - min(stream_durations)
        check("stream_duration_match", delta <= tolerance, {
            "stream_durations": stream_durations, "max_delta_seconds": delta,
        }, f"<= {tolerance}s across every audio/video stream")
    else:
        check("stream_duration_match", False, {
            "measurable_durations": stream_durations, "audio_video_stream_count": len(timed_streams),
        }, "measurable duration for every audio/video stream")

    ffmpeg = [
        "ffmpeg", "-hide_banner", "-nostats", "-v", "error", "-xerror",
        "-i", str(media), "-map", "0:v?", "-map", "0:a?", "-f", "null", "-",
    ]
    try:
        decode = subprocess.run(ffmpeg, capture_output=True, text=True, timeout=timeout_seconds, check=False)
    except FileNotFoundError as exc:
        raise GateError("ffmpeg is not installed or is not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise GateError(f"full media decode timed out after {timeout_seconds}s") from exc
    check("full_decode", decode.returncode == 0 and not decode.stderr.strip(), {
        "return_code": decode.returncode,
        "stderr": decode.stderr.strip()[:2000],
    }, "complete decode without errors")

    black_threshold = float(req.get("black_pixel_threshold", 0.10))
    black_min_duration = float(req.get("black_min_duration_seconds", 0.10))
    max_black_duration = float(req.get("max_black_duration_seconds", 0.50))
    black_command = [
        "ffmpeg", "-hide_banner", "-nostats", "-v", "info", "-i", str(media),
        "-vf", f"blackdetect=d={black_min_duration}:pix_th={black_threshold}",
        "-an", "-f", "null", "-",
    ]
    try:
        black_result = subprocess.run(
            black_command, capture_output=True, text=True, timeout=timeout_seconds, check=False,
        )
    except FileNotFoundError as exc:
        raise GateError("ffmpeg is required for black-frame QA") from exc
    except subprocess.TimeoutExpired as exc:
        raise GateError(f"black-frame detection timed out after {timeout_seconds}s") from exc
    black_log = (black_result.stderr or "") + "\n" + (black_result.stdout or "")
    black_segments = [
        {
            "start_seconds": float(match.group(1)),
            "end_seconds": float(match.group(2)),
            "duration_seconds": float(match.group(3)),
        }
        for match in re.finditer(
            r"black_start:([0-9.]+)\s+black_end:([0-9.]+)\s+black_duration:([0-9.]+)",
            black_log,
        )
    ]
    longest_black = max((item["duration_seconds"] for item in black_segments), default=0.0)
    black_ok = black_result.returncode == 0 and longest_black <= max_black_duration
    check("black_frames", black_ok, {
        "segments": black_segments,
        "longest_black_seconds": longest_black,
        "detector_return_code": black_result.returncode,
    }, f"no black segment longer than {max_black_duration}s")

    true_peak: float | None = None
    true_peak_log = ""
    true_peak_ok = not audio_required and audio is None
    true_peak_limit = float(req.get("true_peak_max_dbfs", -1.0))
    if audio is not None:
        peak_command = [
            "ffmpeg", "-hide_banner", "-nostats", "-v", "info", "-i", str(media),
            "-vn", "-af", "ebur128=peak=true", "-f", "null", "-",
        ]
        try:
            peak_result = subprocess.run(
                peak_command, capture_output=True, text=True, timeout=timeout_seconds, check=False,
            )
        except FileNotFoundError as exc:
            raise GateError("ffmpeg is required for true-peak QA") from exc
        except subprocess.TimeoutExpired as exc:
            raise GateError(f"true-peak measurement timed out after {timeout_seconds}s") from exc
        true_peak_log = (peak_result.stderr or "") + "\n" + (peak_result.stdout or "")
        peak_match = re.search(r"True peak:\s*(-?[0-9]+(?:\.[0-9]+)?)\s*dBFS", true_peak_log, re.IGNORECASE)
        if peak_match is None:
            # FFmpeg versions that format ebur128 as a section header followed by
            # an indented "Peak:" value put the measurement on the next line.
            peak_match = re.search(
                r"True peak:\s*\r?\n\s*Peak:\s*(-?[0-9]+(?:\.[0-9]+)?)\s*dBFS",
                true_peak_log,
                re.IGNORECASE,
            )
        if peak_match:
            true_peak = float(peak_match.group(1))
        true_peak_ok = peak_result.returncode == 0 and true_peak is not None and true_peak <= true_peak_limit
    check("true_peak", true_peak_ok, {
        "true_peak_dbfs": true_peak,
        "limit_dbfs": true_peak_limit,
        "measurement_available": true_peak is not None or (audio is None and not audio_required),
        "ffmpeg_return_code": peak_result.returncode if audio is not None else None,
        "diagnostic_excerpt": true_peak_log[-3000:] if audio is not None and true_peak is None else "",
    }, f"<= {true_peak_limit} dBFS")

    hard_failures = [item["check_id"] for item in checks if item["status"] == "FAIL"]
    return {
        "schema_version": 2,
        "metadata": {"checker": "ffmpeg-ffprobe-v1.0"},
        "media_path": str(media),
        "media_sha256": _file_sha256(media),
        "size_bytes": media.stat().st_size,
        "format": fmt,
        "streams": streams,
        "summary": {
            "duration_seconds": duration,
            "video_codec": (video or {}).get("codec_name"),
            "width": (video or {}).get("width"),
            "height": (video or {}).get("height"),
            "frame_rate": fps,
            "audio_codec": (audio or {}).get("codec_name"),
            "audio_channels": (audio or {}).get("channels"),
            "true_peak_dbfs": true_peak,
            "black_segments": black_segments,
        },
        "checks": checks,
        "hard_failures": hard_failures,
        "hard_pass": not hard_failures,
        "scope_warning": "Technical measurement only; it does not prove editorial quality, visual craft, humor, truth, rights or audience response.",
    }


def _file_sha256(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_claimed_media_qa(
    engine: StudioEngine, project_id: str, task_id: str, worker_id: str,
    claim_token: str, input_name: str | None = None,
) -> dict[str, Any]:
    packet = engine.claimed_packet(project_id, task_id, worker_id, claim_token)
    task = packet["task"]
    requirements = task.get("requirements", {})
    if task.get("kind") != "technical_measurement" and requirements.get("tool") != "ffprobe":
        raise ContractError("qa-media can only execute a declared technical_measurement task")
    names = list(packet["input_artifacts"])
    selected = input_name or (names[0] if names else None)
    if selected not in packet["input_artifacts"]:
        raise ContractError(f"QA input {selected!r} is not a declared, available task input")
    if len(task["outputs"]) != 1:
        raise ContractError("qa-media task must declare exactly one output receipt")
    try:
        report = probe_media(packet["input_artifacts"][selected]["path"], requirements)
    except (GateError, ContractError) as exc:
        engine.fail_task(
            project_id, task_id, worker_id, claim_token,
            {"category": "technical_qa_execution_blocked", "message": str(exc)},
            retryable=False,
        )
        raise
    expected_input_digest = packet["input_artifacts"][selected]["sha256"]
    if report["media_sha256"] != expected_input_digest:
        engine.fail_task(
            project_id, task_id, worker_id, claim_token,
            {"category": "technical_qa_input_changed_during_measurement",
             "expected_sha256": expected_input_digest, "observed_sha256": report["media_sha256"]},
            retryable=False,
        )
        raise GateError("media bytes changed while technical QA was running")
    report["project_id"] = project_id
    report["task_id"] = task_id
    report["input_artifact_id"] = packet["input_artifacts"][selected]["artifact_id"]
    output_name = task["outputs"][0]
    output_path = engine._project_dir(project_id) / "artifacts" / f"{task_id}-{report['media_sha256'][:12]}-{uuid.uuid4().hex[:8]}.qa.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    completed = engine.complete_task(
        project_id, task_id, worker_id, claim_token,
        {output_name: {
            "path": str(output_path), "kind": "qa_report", "media_type": "application/json",
            "rights_status": "NOT_APPLICABLE",
            "metadata": {
                "media_sha256": report["media_sha256"],
                "input_artifact_id": report["input_artifact_id"],
                "hard_pass": report["hard_pass"],
                "hard_failures": report["hard_failures"],
                "checker": report["metadata"]["checker"],
            },
        }},
        result={"measurement_completed": True, "hard_pass": report["hard_pass"], "hard_failures": report["hard_failures"]},
    )
    return {"report": report, "task_completion": completed}