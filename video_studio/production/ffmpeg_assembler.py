from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .contracts import ProductionContractError, RenderSpec, validate_srt_file


class RenderExecutionError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_exclusive(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def _escape_filter_path(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,").replace("[", "\\[").replace("]", "\\]")


class FfmpegAssembler:
    """Deterministic local master assembler for declared shot assets and audio tracks."""

    @staticmethod
    def tools_available() -> bool:
        return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None

    @staticmethod
    def _run(command: list[str], *, timeout_seconds: int = 900) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, check=False)
        except subprocess.TimeoutExpired as exc:
            raise RenderExecutionError(f"media command timed out after {timeout_seconds}s") from exc
        if result.returncode != 0:
            raise RenderExecutionError(f"media command failed ({result.returncode}): {(result.stderr or result.stdout)[-5000:]}")
        return result

    @staticmethod
    def _probe(path: Path) -> dict[str, Any]:
        result = FfmpegAssembler._run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], timeout_seconds=120)
        return json.loads(result.stdout)

    def render(
        self,
        spec: RenderSpec,
        *,
        input_artifacts: Mapping[str, Mapping[str, Any]],
        output_dir: str | Path,
        expected_outputs: set[str],
    ) -> dict[str, Any]:
        if not self.tools_available():
            raise RenderExecutionError("ffmpeg and ffprobe are required for production assembly")
        spec.validate_inputs(set(input_artifacts))
        if expected_outputs != {spec.video_output, spec.audio_output, spec.receipt_output}:
            raise ProductionContractError("render task outputs must exactly match video_output, audio_output and receipt_output")
        root = Path(output_dir).resolve()
        root.mkdir(parents=True, exist_ok=True)
        video_path = root / f"{spec.video_output}.mp4"
        audio_path = root / f"{spec.audio_output}.wav"
        receipt_path = root / f"{spec.receipt_output}.json"
        if any(path.exists() for path in (video_path, audio_path, receipt_path)):
            raise RenderExecutionError("refusing to overwrite an existing production output")

        inputs: list[Path] = []
        input_meta: list[dict[str, Any]] = []
        input_index: dict[str, int] = {}
        ordered_names: list[str] = []
        for clip in spec.clips:
            if clip.input_name not in ordered_names:
                ordered_names.append(clip.input_name)
        for track in spec.audio_tracks:
            if track.input_name not in ordered_names:
                ordered_names.append(track.input_name)
        video_input_names = {clip.input_name for clip in spec.clips}
        audio_input_names = {track.input_name for track in spec.audio_tracks}
        if video_input_names.intersection(audio_input_names):
            raise ProductionContractError("one artifact cannot be used as both a video clip and an audio track")
        for name in ordered_names:
            artifact = input_artifacts[name]
            kind = str(artifact.get("kind", "")).lower()
            media_type = str(artifact.get("media_type", "")).lower()
            if name in video_input_names and (kind != "video" or not media_type.startswith("video/")):
                raise ProductionContractError(f"video clip input must be a registered video artifact: {name}")
            if name in audio_input_names and (kind != "audio" or not media_type.startswith("audio/")):
                raise ProductionContractError(f"audio track input must be a registered audio artifact: {name}")
            path = Path(str(artifact.get("path", ""))).resolve()
            if not path.is_file() or path.stat().st_size <= 0:
                raise RenderExecutionError(f"declared input artifact is missing or empty: {name}")
            actual_digest = sha256_file(path)
            declared_digest = artifact.get("sha256") or artifact.get("digest")
            if declared_digest and actual_digest != declared_digest:
                raise RenderExecutionError(f"input artifact digest changed: {name}")
            input_index[name] = len(inputs)
            inputs.append(path)
            input_meta.append({
                "name": name, "artifact_id": artifact.get("artifact_id"), "sha256": actual_digest,
                "path_name": path.name, "bytes": path.stat().st_size, "kind": artifact.get("kind"),
                "media_type": artifact.get("media_type"), "rights_status": artifact.get("rights_status"),
            })

        captions_path = None
        captions_qa = None
        if spec.captions_input:
            caption_artifact = input_artifacts[spec.captions_input]
            caption_kind = str(caption_artifact.get("kind", "")).lower()
            caption_type = str(caption_artifact.get("media_type", "")).lower()
            if caption_kind not in {"subtitle", "document"} or not (
                "subrip" in caption_type or caption_type.startswith("text/") or caption_type == "application/octet-stream"
            ):
                raise ProductionContractError("captions_input must be a declared subtitle/document artifact")
            captions_path = Path(str(caption_artifact.get("path", ""))).resolve()
            if not captions_path.is_file() or captions_path.stat().st_size <= 0:
                raise RenderExecutionError(f"caption input is missing or empty: {spec.captions_input}")
            captions_qa = validate_srt_file(captions_path, duration_seconds=spec.duration_seconds)
            input_meta.append({
                "name": spec.captions_input, "artifact_id": caption_artifact.get("artifact_id"),
                "sha256": sha256_file(captions_path), "path_name": captions_path.name,
                "bytes": captions_path.stat().st_size, "kind": caption_artifact.get("kind"),
                "media_type": caption_artifact.get("media_type"), "rights_status": caption_artifact.get("rights_status"),
            })

        filters: list[str] = []
        video_labels: list[str] = []
        for index, clip in enumerate(spec.clips):
            source_index = input_index[clip.input_name]
            if clip.fit == "COVER":
                fit = f"scale={spec.width}:{spec.height}:force_original_aspect_ratio=increase,crop={spec.width}:{spec.height}"
            else:
                fit = f"scale={spec.width}:{spec.height}:force_original_aspect_ratio=decrease,pad={spec.width}:{spec.height}:(ow-iw)/2:(oh-ih)/2:color=black"
            label = f"v{index}"
            filters.append(
                f"[{source_index}:v]trim=start={clip.source_start_seconds:.6f}:duration={clip.duration_seconds:.6f},"
                f"setpts=PTS-STARTPTS,{fit},setsar=1,fps={spec.fps:.6f},format=yuv420p[{label}]"
            )
            video_labels.append(f"[{label}]")
        filters.append("".join(video_labels) + f"concat=n={len(video_labels)}:v=1:a=0[vconcat]")
        video_label = "vconcat"
        if spec.burn_captions and captions_path:
            filters.append(f"[{video_label}]subtitles='{_escape_filter_path(captions_path)}'[vcaptioned]")
            video_label = "vcaptioned"

        audio_labels: list[str] = []
        for index, track in enumerate(spec.audio_tracks):
            source_index = input_index[track.input_name]
            duration = track.duration_seconds or max(0.001, spec.duration_seconds - track.start_seconds)
            delay_ms = int(round(track.start_seconds * 1000))
            label = f"a{index}"
            filters.append(
                f"[{source_index}:a]atrim=start=0:duration={duration:.6f},asetpts=PTS-STARTPTS,"
                f"volume={track.gain_db:.3f}dB,adelay={delay_ms}|{delay_ms},"
                f"apad=whole_dur={spec.duration_seconds:.6f},atrim=duration={spec.duration_seconds:.6f}[{label}]"
            )
            audio_labels.append(f"[{label}]")
        filters.append(
            "".join(audio_labels) + f"amix=inputs={len(audio_labels)}:duration=longest:normalize=0,"
            + "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
            + f"atrim=duration={spec.duration_seconds:.6f},asplit=2[aacmix][wavmix]"
        )

        with tempfile.TemporaryDirectory(prefix="vga-render-", dir=root) as temp_dir:
            filter_script = Path(temp_dir) / "filter-complex.txt"
            filter_script.write_text(";\n".join(filters) + "\n", encoding="utf-8")
            command = ["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-xerror", "-n"]
            for path in inputs:
                command.extend(["-i", str(path)])
            command.extend(["-filter_complex_script", str(filter_script), "-map", f"[{video_label}]", "-map", "[aacmix]"])
            command.extend([
                "-t", f"{spec.duration_seconds:.6f}", "-r", f"{spec.fps:.6f}",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                "-movflags", "+faststart", str(video_path),
                "-map", "[wavmix]", "-vn", "-c:a", "pcm_s24le", "-ar", "48000", "-ac", "2", str(audio_path),
            ])
            self._run(command)

        if not video_path.is_file() or video_path.stat().st_size <= 0:
            raise RenderExecutionError("FFmpeg did not produce a non-empty final video")
        if not audio_path.is_file() or audio_path.stat().st_size <= 0:
            raise RenderExecutionError("FFmpeg did not produce a non-empty audio master")
        probe = self._probe(video_path)
        streams = probe.get("streams", [])
        video_stream = next((item for item in streams if item.get("codec_type") == "video"), None)
        audio_stream = next((item for item in streams if item.get("codec_type") == "audio"), None)
        if video_stream is None:
            raise RenderExecutionError("rendered file has no video stream")
        video_duration = float(video_stream.get("duration") or probe.get("format", {}).get("duration") or 0)
        if abs(video_duration - spec.duration_seconds) > max(0.08, 2.0 / spec.fps):
            raise RenderExecutionError(f"rendered video duration mismatch: {video_duration:.3f}s")
        if spec.audio_required and audio_stream is None:
            raise RenderExecutionError("rendered file has no required audio stream")
        audio_duration = float(audio_stream.get("duration") or probe.get("format", {}).get("duration") or 0) if audio_stream else None
        if audio_duration is None or abs(audio_duration - video_duration) > max(0.08, 2.0 / spec.fps):
            raise RenderExecutionError("rendered audio/video duration mismatch")

        receipt = {
            "schema_version": "1.0", "project_id": spec.project_id, "archetype": spec.archetype,
            "render_spec_sha256": hashlib.sha256(json.dumps(spec, default=lambda o: o.__dict__, sort_keys=True).encode()).hexdigest(),
            "inputs": input_meta,
            "output": {
                "path": video_path.name, "sha256": sha256_file(video_path), "bytes": video_path.stat().st_size,
                "video_duration_seconds": video_duration, "audio_duration_seconds": audio_duration,
                "width": int(video_stream.get("width", 0)), "height": int(video_stream.get("height", 0)),
                "fps": video_stream.get("avg_frame_rate"), "frame_count": int(video_stream.get("nb_frames") or 0),
            },
            "audio_master": {"path": audio_path.name, "sha256": sha256_file(audio_path), "bytes": audio_path.stat().st_size},
            "captions_qa": captions_qa,
            "render_engine": "ffmpeg-local-assembler-v1",
            "candidate_only": True, "promotion_authorized": False, "release_authorized": False,
        }
        _write_json_exclusive(receipt_path, receipt)
        return {"video_path": str(video_path), "audio_path": str(audio_path), "receipt_path": str(receipt_path), "receipt": receipt}
