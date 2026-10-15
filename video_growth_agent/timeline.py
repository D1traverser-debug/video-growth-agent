from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .media_graph import AssetRef, MediaGraph, MediaGraphError


class TimelineError(ValueError):
    pass


@dataclass(frozen=True)
class TimelineClip:
    clip_id: str
    asset_ref: AssetRef
    track_id: str
    timeline_start_seconds: float
    source_start_seconds: float
    duration_seconds: float
    speed: float = 1.0
    transform: Mapping[str, object] = field(default_factory=dict)
    audio_enabled: bool = True
    video_enabled: bool = True

    def __post_init__(self) -> None:
        if not self.clip_id.strip() or not self.track_id.strip():
            raise TimelineError("clip_id and track_id are required")
        if self.timeline_start_seconds < 0 or self.source_start_seconds < 0:
            raise TimelineError("timeline/source starts cannot be negative")
        if self.duration_seconds <= 0:
            raise TimelineError("clip duration must be positive")
        if self.speed <= 0:
            raise TimelineError("clip speed must be positive")
        if not self.audio_enabled and not self.video_enabled:
            raise TimelineError("clip cannot disable both audio and video")

    @property
    def timeline_end_seconds(self) -> float:
        return self.timeline_start_seconds + self.duration_seconds


@dataclass(frozen=True)
class TimelineMarker:
    marker_id: str
    time_seconds: float
    kind: str
    note: str = ""

    def __post_init__(self) -> None:
        if not self.marker_id.strip() or not self.kind.strip():
            raise TimelineError("marker_id and kind are required")
        if self.time_seconds < 0:
            raise TimelineError("marker time cannot be negative")


@dataclass(frozen=True)
class TimelineSpec:
    timeline_id: str
    version_id: str
    context_id: str
    clips: tuple[TimelineClip, ...]
    markers: tuple[TimelineMarker, ...] = ()
    derived_from_version: str | None = None
    edit_reason: str = ""
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.timeline_id.strip() or not self.version_id.strip() or not self.context_id.strip():
            raise TimelineError("timeline_id, version_id and context_id are required")
        if not self.clips:
            raise TimelineError("timeline requires at least one clip")
        clip_ids = [clip.clip_id for clip in self.clips]
        if len(clip_ids) != len(set(clip_ids)):
            raise TimelineError("clip_id values must be unique within a timeline version")
        if self.derived_from_version == self.version_id:
            raise TimelineError("timeline version cannot derive from itself")
        if self.derived_from_version and not self.edit_reason.strip():
            raise TimelineError("derived timeline requires edit_reason")

    @property
    def duration_seconds(self) -> float:
        return max(clip.timeline_end_seconds for clip in self.clips)

    def asset_refs(self) -> tuple[AssetRef, ...]:
        return tuple(dict.fromkeys(clip.asset_ref for clip in self.clips))

    def validate_against_graph(self, graph: MediaGraph, *, require_promoted_assets: bool = True) -> None:
        if self.context_id not in graph.contexts:
            raise TimelineError(f"timeline context missing: {self.context_id}")
        for ref in self.asset_refs():
            if ref not in graph.assets:
                raise TimelineError(f"timeline asset missing: {ref.key()}")
            if require_promoted_assets and graph.asset_state(ref) != "PROMOTED":
                raise TimelineError(f"timeline asset is not promoted: {ref.key()}")

    def derive(
        self,
        *,
        version_id: str,
        clips: tuple[TimelineClip, ...] | None = None,
        markers: tuple[TimelineMarker, ...] | None = None,
        edit_reason: str,
        metadata: Mapping[str, object] | None = None,
    ) -> "TimelineSpec":
        if not version_id.strip() or version_id == self.version_id:
            raise TimelineError("derived timeline needs a new version_id")
        if not edit_reason.strip():
            raise TimelineError("derived timeline requires edit_reason")
        return TimelineSpec(
            timeline_id=self.timeline_id,
            version_id=version_id,
            context_id=self.context_id,
            clips=clips if clips is not None else self.clips,
            markers=markers if markers is not None else self.markers,
            derived_from_version=self.version_id,
            edit_reason=edit_reason,
            metadata=dict(metadata or self.metadata),
        )


def assert_platform_variant_lineage(
    *,
    master: TimelineSpec,
    variant: TimelineSpec,
    platform: str,
) -> None:
    if not platform.strip():
        raise TimelineError("platform is required")
    if variant.timeline_id == master.timeline_id and variant.version_id == master.version_id:
        raise TimelineError("platform variant must be a new timeline version or identity")
    if variant.derived_from_version != master.version_id:
        raise TimelineError("platform variant must declare the master version as its direct source")
    if not variant.edit_reason.strip():
        raise TimelineError("platform variant requires authored edit_reason")
