from pathlib import Path

import pytest

from video_growth_agent.reviewer_providers import (
    GeminiReviewerAdapter,
    OpenRouterVisionReviewerAdapter,
    ReviewerRequest,
)


def _request(tmp_path: Path, suffix: str = ".jpg") -> ReviewerRequest:
    media = tmp_path / f"sample{suffix}"
    media.write_bytes(b"fake-media")
    return ReviewerRequest(
        prompt="Return a strict JSON verdict.",
        media_paths=(media,),
        context_id="ctx-1",
        trace_id="trace-1",
        proof_ref="https://github.com/example/actions/runs/1",
    )


def test_reviewer_request_requires_real_media(tmp_path: Path):
    request = ReviewerRequest(
        prompt="review",
        media_paths=(tmp_path / "missing.jpg",),
        context_id="ctx",
        trace_id="trace",
        proof_ref="proof",
    )
    with pytest.raises(FileNotFoundError):
        request.validate()


def test_gemini_fails_closed_without_key(tmp_path: Path):
    adapter = GeminiReviewerAdapter(api_key="")
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        adapter.execute(_request(tmp_path))


def test_gemini_preserves_provider_response_identity(tmp_path: Path):
    seen = {}

    def transport(url, headers, payload):
        seen.update({"url": url, "headers": headers, "payload": payload})
        return {
            "responseId": "resp-gemini-123",
            "modelVersion": "gemini-3.8-flash-001",
            "candidates": [{"content": {"parts": [{"text": '{"decision":"FAIL"}'}]}}],
            "usageMetadata": {"promptTokenCount": 123},
        }

    run = GeminiReviewerAdapter(api_key="secret", transport=transport).execute(_request(tmp_path))
    assert run.provider == "google-gemini"
    assert run.provider_run_id == "resp-gemini-123"
    assert run.model == "gemini-3.8-flash-001"
    assert run.execution_id == "google-gemini:resp-gemini-123"
    assert run.context_id == "ctx-1"
    assert run.trace_id == "trace-1"
    assert "inline_data" in seen["payload"]["contents"][0]["parts"][1]
    assert "secret" in seen["url"]


def test_gemini_rejects_response_without_response_id(tmp_path: Path):
    def transport(url, headers, payload):
        return {"candidates": [{"content": {"parts": [{"text": "FAIL"}]}}]}

    with pytest.raises(ValueError, match="responseId"):
        GeminiReviewerAdapter(api_key="secret", transport=transport).execute(_request(tmp_path))


def test_openrouter_fails_closed_without_key(tmp_path: Path):
    adapter = OpenRouterVisionReviewerAdapter(api_key="")
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        adapter.execute(_request(tmp_path))


def test_openrouter_rejects_video_for_motion_certification(tmp_path: Path):
    adapter = OpenRouterVisionReviewerAdapter(api_key="secret", transport=lambda *args: {})
    with pytest.raises(ValueError, match="still-image only"):
        adapter.execute(_request(tmp_path, suffix=".mp4"))


def test_openrouter_preserves_provider_identity_and_trace(tmp_path: Path):
    seen = {}

    def transport(url, headers, payload):
        seen.update({"url": url, "headers": headers, "payload": payload})
        return {
            "id": "chatcmpl-openrouter-1",
            "model": "nvidia/example-vision:free",
            "choices": [{"message": {"content": '{"decision":"FAIL"}'}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }

    run = OpenRouterVisionReviewerAdapter(api_key="secret", transport=transport).execute(_request(tmp_path))
    assert run.provider == "openrouter"
    assert run.provider_run_id == "chatcmpl-openrouter-1"
    assert run.model == "nvidia/example-vision:free"
    assert run.execution_id == "openrouter:chatcmpl-openrouter-1"
    assert seen["payload"]["trace"]["trace_id"] == "trace-1"
    image = seen["payload"]["messages"][0]["content"][1]["image_url"]["url"]
    assert image.startswith("data:image/jpeg;base64,")
