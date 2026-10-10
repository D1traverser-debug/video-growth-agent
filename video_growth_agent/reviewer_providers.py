from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
import base64
import json
import mimetypes
import os
import urllib.request


JsonTransport = Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]]


def _default_transport(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310 - provider URLs are fixed by adapters
        raw = response.read().decode("utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Reviewer provider returned a non-object JSON response")
    return data


def _data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _inline_data(path: Path) -> dict[str, str]:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return {"mime_type": mime, "data": encoded}


@dataclass(frozen=True)
class ReviewerRequest:
    prompt: str
    media_paths: tuple[Path, ...]
    context_id: str
    trace_id: str
    proof_ref: str

    def validate(self) -> None:
        if not self.prompt.strip():
            raise ValueError("reviewer prompt is required")
        if not self.media_paths:
            raise ValueError("at least one media path is required")
        for path in self.media_paths:
            if not path.exists() or not path.is_file():
                raise FileNotFoundError(path)
        for field_name, value in (
            ("context_id", self.context_id),
            ("trace_id", self.trace_id),
            ("proof_ref", self.proof_ref),
        ):
            if not value.strip():
                raise ValueError(f"{field_name} is required")


@dataclass(frozen=True)
class ProviderReviewRun:
    provider: str
    model: str
    provider_run_id: str
    context_id: str
    trace_id: str
    proof_ref: str
    output_text: str
    usage: dict[str, Any]

    @property
    def execution_id(self) -> str:
        return f"{self.provider}:{self.provider_run_id}"


class GeminiReviewerAdapter:
    """Direct multimodal reviewer adapter for the Gemini Developer API.

    Intended for short video/image review. The API returns responseId and modelVersion,
    which are preserved as provider-backed execution evidence.
    """

    def __init__(
        self,
        *,
        model: str = "gemini-3.8-flash",
        api_key: str | None = None,
        transport: JsonTransport | None = None,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.transport = transport or _default_transport

    def execute(self, request: ReviewerRequest) -> ProviderReviewRun:
        request.validate()
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured; reviewer execution remains fail-closed")

        parts: list[dict[str, Any]] = [{"text": request.prompt}]
        for path in request.media_paths:
            parts.append({"inline_data": _inline_data(path)})
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        raw = self.transport(url, {"Content-Type": "application/json"}, payload)
        provider_run_id = str(raw.get("responseId") or "").strip()
        model_version = str(raw.get("modelVersion") or self.model).strip()
        if not provider_run_id:
            raise ValueError("Gemini response is missing responseId")

        text_parts: list[str] = []
        for candidate in raw.get("candidates", []):
            content = candidate.get("content") if isinstance(candidate, dict) else None
            if not isinstance(content, dict):
                continue
            for part in content.get("parts", []):
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    text_parts.append(part["text"])
        output_text = "\n".join(text_parts).strip()
        if not output_text:
            raise ValueError("Gemini reviewer returned no textual verdict")
        usage = raw.get("usageMetadata") if isinstance(raw.get("usageMetadata"), dict) else {}
        return ProviderReviewRun(
            provider="google-gemini",
            model=model_version,
            provider_run_id=provider_run_id,
            context_id=request.context_id,
            trace_id=request.trace_id,
            proof_ref=request.proof_ref,
            output_text=output_text,
            usage=usage,
        )


class OpenRouterVisionReviewerAdapter:
    """Low-cost still/contact-sheet reviewer using OpenRouter image-capable models.

    This adapter deliberately rejects video inputs. Motion-critical certification must use
    a provider that consumes actual video playback rather than a still-only approximation.
    """

    VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"}

    def __init__(
        self,
        *,
        model: str = "openrouter/free",
        api_key: str | None = None,
        transport: JsonTransport | None = None,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.transport = transport or _default_transport

    def execute(self, request: ReviewerRequest) -> ProviderReviewRun:
        request.validate()
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not configured; reviewer execution remains fail-closed")
        videos = [path for path in request.media_paths if path.suffix.lower() in self.VIDEO_SUFFIXES]
        if videos:
            raise ValueError("OpenRouter vision fallback is still-image only; do not certify motion from extracted frames")

        content: list[dict[str, Any]] = [{"type": "text", "text": request.prompt}]
        for path in request.media_paths:
            content.append({"type": "image_url", "image_url": {"url": _data_url(path)}})
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "temperature": 0.2,
            "trace": {"trace_id": request.trace_id, "trace_name": "video-growth-review"},
        }
        raw = self.transport(
            "https://openrouter.ai/api/v1/chat/completions",
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-OpenRouter-Metadata": "enabled",
            },
            payload,
        )
        provider_run_id = str(raw.get("id") or "").strip()
        resolved_model = str(raw.get("model") or self.model).strip()
        if not provider_run_id:
            raise ValueError("OpenRouter response is missing id")
        choices = raw.get("choices") if isinstance(raw.get("choices"), list) else []
        message = choices[0].get("message") if choices and isinstance(choices[0], dict) else None
        output_text = str(message.get("content") if isinstance(message, dict) else "").strip()
        if not output_text:
            raise ValueError("OpenRouter reviewer returned no textual verdict")
        usage = raw.get("usage") if isinstance(raw.get("usage"), dict) else {}
        return ProviderReviewRun(
            provider="openrouter",
            model=resolved_model,
            provider_run_id=provider_run_id,
            context_id=request.context_id,
            trace_id=request.trace_id,
            proof_ref=request.proof_ref,
            output_text=output_text,
            usage=usage,
        )
