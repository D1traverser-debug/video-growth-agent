"""Real local-file commit/restart/concurrency tests; no external provider calls."""
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from video_growth_agent.checkpoint_io import CheckpointConflict, read_snapshot, write_snapshot
from video_growth_agent.media_graph import ContextRecord, MediaGraph, MediaGraphStore
from video_growth_agent.storage import ProjectStore


def test_graph_stale_writers_cannot_silently_lose_a_newer_edit(tmp_path):
    store = MediaGraphStore(tmp_path / "graph.json")
    graph = MediaGraph()
    graph.add_context(ContextRecord("root", "PROGRAM"))
    store.save(graph)
    first = store.load()
    second = store.load()
    first.add_context(ContextRecord("branch-A", "EPISODE", "root"))
    second.add_context(ContextRecord("branch-B", "EPISODE", "root"))
    store.save(first)
    with pytest.raises(CheckpointConflict, match="stale checkpoint"):
        store.save(second)
    assert "branch-A" in store.load().contexts
    assert "branch-B" not in store.load().contexts


def test_project_state_stale_writer_cannot_overwrite_committed_state(tmp_path):
    store = ProjectStore(tmp_path / "projects")
    store.create("real-project")
    first = store.load("real-project")
    stale = store.load("real-project")
    first.stage = "PLAN"
    first.touch()
    store.save(first)
    stale.stage = "RELEASE"
    stale.touch()
    with pytest.raises(CheckpointConflict, match="stale checkpoint"):
        store.save(stale)
    assert store.load("real-project").stage == "PLAN"


def test_concurrent_graph_writers_are_serialized_and_one_conflicts(tmp_path):
    store = MediaGraphStore(tmp_path / "graph.json")
    root = MediaGraph()
    root.add_context(ContextRecord("program", "PROGRAM"))
    store.save(root)
    snap_a, snap_b = store.load(), store.load()
    snap_a.add_context(ContextRecord("A", "EPISODE", "program"))
    snap_b.add_context(ContextRecord("B", "EPISODE", "program"))
    barrier = Barrier(2)
    def commit(snapshot):
        barrier.wait(timeout=10)
        try:
            store.save(snapshot)
        except CheckpointConflict:
            return "CONFLICT"
        return "COMMITTED"
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(commit, snap_a)
        second = executor.submit(commit, snap_b)
        result = sorted((first.result(), second.result()))
    assert result == ["COMMITTED", "CONFLICT"]
    loaded = store.load()
    assert ("A" in loaded.contexts) != ("B" in loaded.contexts)
    assert set(loaded.contexts).intersection({"A", "B"}) in ({"A"}, {"B"})


def test_failed_rename_preserves_last_good_checkpoint_and_removes_temp(tmp_path, monkeypatch):
    from video_growth_agent import checkpoint_io
    path = tmp_path / "checkpoint.json"
    revision = write_snapshot(path, {"version": 1}, expected_revision=None)
    original = path.read_bytes()
    def unavailable_rename(_source, _destination):
        raise OSError("simulated filesystem rename failure")
    monkeypatch.setattr(checkpoint_io.os, "replace", unavailable_rename)
    with pytest.raises(OSError, match="simulated filesystem"):
        write_snapshot(path, {"version": 2}, expected_revision=revision)
    assert path.read_bytes() == original
    assert read_snapshot(path)[0] == {"version": 1}
    assert list(tmp_path.glob("checkpoint.json.*.tmp")) == []


def test_stale_writer_without_prior_read_cannot_overwrite_existing_checkpoint(tmp_path):
    path = tmp_path / "state.json"
    write_snapshot(path, {"first": 1}, expected_revision=None)
    with pytest.raises(CheckpointConflict):
        write_snapshot(path, {"second": 2}, expected_revision=None)
    assert json.loads(path.read_text(encoding="utf-8")) == {"first": 1}
