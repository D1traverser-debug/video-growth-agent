from __future__ import annotations

from dataclasses import dataclass

from .media_graph import AssetRef, MediaGraph
from .timeline import TimelineSpec


class InterchangeError(ValueError):
    pass


@dataclass(frozen=True)
class EditorAdapterCapability:
    adapter_id: str
    observed_at: str
    executable_now: bool
    import_formats: frozenset[str]
    export_formats: frozenset[str]
    supports_roundtrip: bool
    capability_evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.adapter_id.strip() or not self.observed_at.strip():
            raise InterchangeError("adapter identity and observed_at are required")
        if not self.capability_evidence_refs:
            raise InterchangeError("editor adapter capability requires evidence")


@dataclass(frozen=True)
class EditorialHandoff:
    handoff_id: str
    adapter_id: str
    timeline_id: str
    timeline_version: str
    interchange_format: str
    asset_refs: tuple[AssetRef, ...]
    asset_digests: tuple[str, ...]
    source_refs: tuple[str, ...]
    purpose: str

    def __post_init__(self) -> None:
        if not all(str(value).strip() for value in (self.handoff_id, self.adapter_id, self.timeline_id, self.timeline_version, self.interchange_format, self.purpose)):
            raise InterchangeError("handoff identity/adapter/timeline/format/purpose are required")
        if not self.asset_refs or not self.asset_digests:
            raise InterchangeError("handoff requires asset refs and digests")
        if len(self.asset_refs) != len(self.asset_digests):
            raise InterchangeError("handoff asset refs and digests must align")
        if not self.source_refs:
            raise InterchangeError("handoff requires source_refs")


@dataclass(frozen=True)
class EditorialRoundTripReceipt:
    handoff_id: str
    adapter_id: str
    imported_timeline_version: str
    returned_timeline_ref: str
    returned_timeline_digest: str
    returned_format: str
    change_summary_ref: str
    executable_receipt_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all(
            str(value).strip()
            for value in (
                self.handoff_id,
                self.adapter_id,
                self.imported_timeline_version,
                self.returned_timeline_ref,
                self.returned_timeline_digest,
                self.returned_format,
                self.change_summary_ref,
            )
        ):
            raise InterchangeError("roundtrip receipt fields are required")
        if not self.executable_receipt_refs:
            raise InterchangeError("roundtrip requires execution evidence")


def prepare_editorial_handoff(
    *,
    timeline: TimelineSpec,
    graph: MediaGraph,
    adapter: EditorAdapterCapability,
    handoff_id: str,
    interchange_format: str,
    purpose: str,
    source_refs: tuple[str, ...],
) -> EditorialHandoff:
    if not adapter.executable_now:
        raise InterchangeError("editor adapter is not executable in the current session")
    if interchange_format not in adapter.import_formats and interchange_format not in adapter.export_formats:
        raise InterchangeError("interchange format is not supported by the current adapter evidence")
    timeline.validate_against_graph(graph, require_promoted_assets=True)
    refs = timeline.asset_refs()
    digests: list[str] = []
    for ref in refs:
        asset = graph.assets[ref]
        digests.append(asset.digest)
    return EditorialHandoff(
        handoff_id=handoff_id,
        adapter_id=adapter.adapter_id,
        timeline_id=timeline.timeline_id,
        timeline_version=timeline.version_id,
        interchange_format=interchange_format,
        asset_refs=refs,
        asset_digests=tuple(digests),
        source_refs=source_refs,
        purpose=purpose,
    )


def validate_roundtrip(
    *,
    handoff: EditorialHandoff,
    adapter: EditorAdapterCapability,
    receipt: EditorialRoundTripReceipt,
) -> str:
    if not adapter.executable_now:
        raise InterchangeError("roundtrip cannot be verified against a non-executable adapter")
    if not adapter.supports_roundtrip:
        raise InterchangeError("adapter does not attest roundtrip support")
    if receipt.handoff_id != handoff.handoff_id or receipt.adapter_id != handoff.adapter_id:
        raise InterchangeError("roundtrip receipt does not bind the originating handoff")
    if receipt.imported_timeline_version != handoff.timeline_version:
        raise InterchangeError("roundtrip imported the wrong timeline version")
    if receipt.returned_format not in adapter.export_formats:
        raise InterchangeError("returned format is not currently supported")
    return "ROUNDTRIP_VERIFIED"
