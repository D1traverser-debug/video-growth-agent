from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import zipfile
from typing import Any, Mapping

from .contracts import ProductionContractError
from .ffmpeg_assembler import sha256_file


class DeliveryPackageError(RuntimeError):
    pass


def _safe_archive_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ProductionContractError(f"unsafe delivery path: {value}")
    return str(path)


def create_delivery_package(
    *,
    input_artifacts: Mapping[str, Mapping[str, Any]],
    package_map: Mapping[str, str],
    package_path: str | Path,
    manifest_path: str | Path,
    project_id: str,
    expected_types: Mapping[str, Mapping[str, str]] | None = None,
) -> dict[str, Any]:
    if not package_map:
        raise ProductionContractError("delivery package requires a non-empty artifact-to-path map")
    root = Path(package_path).resolve().parent
    root.mkdir(parents=True, exist_ok=True)
    zip_path = Path(package_path).resolve()
    manifest_file = Path(manifest_path).resolve()
    if zip_path.exists() or manifest_file.exists():
        raise DeliveryPackageError("refusing to overwrite an existing delivery package")

    entries: list[dict[str, Any]] = []
    files: list[tuple[str, Path]] = []
    for artifact_name, archive_name in package_map.items():
        if artifact_name not in input_artifacts:
            raise ProductionContractError(f"delivery artifact is not a declared task input: {artifact_name}")
        artifact = input_artifacts[artifact_name]
        expected = (expected_types or {}).get(artifact_name, {})
        if expected.get("kind") and artifact.get("kind") != expected["kind"]:
            raise ProductionContractError(f"delivery artifact {artifact_name} has kind {artifact.get('kind')!r}; expected {expected['kind']!r}")
        if expected.get("media_type") and artifact.get("media_type") != expected["media_type"]:
            raise ProductionContractError(f"delivery artifact {artifact_name} has media_type {artifact.get('media_type')!r}; expected {expected['media_type']!r}")
        source = Path(str(artifact.get("path", ""))).resolve()
        if not source.is_file() or source.stat().st_size <= 0:
            raise DeliveryPackageError(f"delivery artifact is missing or empty: {artifact_name}")
        digest = sha256_file(source)
        declared = artifact.get("sha256") or artifact.get("digest")
        if declared and digest != declared:
            raise DeliveryPackageError(f"delivery artifact digest mismatch: {artifact_name}")
        safe_name = _safe_archive_path(str(archive_name))
        files.append((safe_name, source))
        entries.append({
            "artifact_name": artifact_name,
            "archive_path": safe_name,
            "artifact_id": artifact.get("artifact_id"),
            "sha256": digest,
            "bytes": source.stat().st_size,
            "kind": artifact.get("kind"),
            "media_type": artifact.get("media_type"),
            "rights_status": artifact.get("rights_status"),
        })
    archive_paths = [name for name, _ in files]
    if len(archive_paths) != len(set(archive_paths)):
        raise ProductionContractError("delivery archive paths must be unique")

    manifest = {
        "schema_version": "1.0",
        "project_id": project_id,
        "status": "PACKAGE_CANDIDATE",
        "artifact_count": len(entries),
        "artifacts": entries,
        "release_authorized": False,
    }
    with zipfile.ZipFile(zip_path, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for archive_name, source in files:
            archive.write(source, arcname=archive_name)
        archive.writestr("delivery-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    manifest["package_sha256"] = sha256_file(zip_path)
    with manifest_file.open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return {"package_path": str(zip_path), "manifest_path": str(manifest_file), "manifest": manifest}
