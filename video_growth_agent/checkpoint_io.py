"""Atomic, compare-and-swap JSON checkpoints for owner-local state stores.

Protects against fixed .tmp collisions and stale snapshots across CLI/processes.
A completed rename is the commit point. Receipts/media bytes have their own
lifecycles; this module does not attest remote or distributed durability.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class CheckpointConflict(ValueError):
    """A different writer changed the snapshot after this reader loaded it."""


def _digest(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def read_snapshot(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    path = Path(path)
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return None, None
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("checkpoint must be a JSON object: " + str(path))
    return value, _digest(raw)


@contextmanager
def _writer_lock(lock_path: Path) -> Iterator[None]:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as handle:
        if os.name == "posix":
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        elif os.name == "nt":
            import msvcrt
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            raise RuntimeError("checkpoint filesystem locking is unsupported on this OS")


def write_snapshot(
    path: Path,
    payload: dict[str, Any],
    *,
    expected_revision: str | None,
) -> str:
    """One-owner CAS commit. A stale writer fails instead of losing a newer state.

    For an existing file callers must have obtained expected_revision from
    read_snapshot. New-file creation uses None; it cannot overwrite an
    existing file. The lock is cross-process on supported local filesystems.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    lock_path = path.with_name(path.name + ".lock")
    with _writer_lock(lock_path):
        try:
            existing = path.read_bytes()
        except FileNotFoundError:
            existing = None
        actual = _digest(existing)
        if actual != expected_revision:
            raise CheckpointConflict(
                f"stale checkpoint write for {path}: reload current owner state before retry"
            )
        tmp_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False
            ) as handle:
                tmp_name = handle.name
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, path)
            tmp_name = None
            # POSIX directory fsync gives stronger rename durability where
            # supported. Do not hide failures before the physical commit.
            if os.name == "posix":
                dir_fd = os.open(str(path.parent), os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
        finally:
            if tmp_name is not None:
                Path(tmp_name).unlink(missing_ok=True)
    return _digest(encoded) or ""
