import json
from pathlib import Path

import pytest

from video_growth_agent.program_orchestration import ProgramGraph, ProgramOrchestrator


REPO_ROOT = Path(__file__).resolve().parents[1]


def graph_payload(nodes):
    return {"program_id": "p", "nodes": nodes}


def test_explicit_dependencies_do_not_create_global_wave_barrier(tmp_path):
    graph = ProgramGraph(graph_payload([
        {"id": "a", "workstream": "A", "coordination": "INDEPENDENT_PARALLEL", "outputs": ["a_out"]},
        {"id": "b", "workstream": "B", "coordination": "INDEPENDENT_PARALLEL", "outputs": ["b_out"]},
        {"id": "c", "workstream": "C", "coordination": "SERIAL_DEPENDENCY", "depends_on": ["a"], "inputs": ["a_out"], "outputs": ["c_out"]},
    ]))
    run = ProgramOrchestrator(graph, state_path=tmp_path / "state.json")
    assert {node.node_id for node in run.ready()} == {"a", "b"}

    run.complete("a", outputs={"a_out": "A"})
    assert {node.node_id for node in run.ready()} == {"b", "c"}
    assert run.state.node_status["b"] == "READY"
    assert run.state.node_status["c"] == "READY"


def test_dependency_cycle_is_rejected():
    with pytest.raises(ValueError, match="cycle"):
        ProgramGraph(graph_payload([
            {"id": "a", "workstream": "A", "coordination": "SERIAL_DEPENDENCY", "depends_on": ["b"]},
            {"id": "b", "workstream": "B", "coordination": "SERIAL_DEPENDENCY", "depends_on": ["a"]},
        ]))


def test_competitive_candidates_wait_for_authorized_adjudication(tmp_path):
    graph = ProgramGraph(graph_payload([
        {"id": "candidate_a", "workstream": "COMMERCIAL", "coordination": "COMPETITIVE_CANDIDATES", "decision_group": "offer", "outputs": ["a"]},
        {"id": "candidate_b", "workstream": "COMMERCIAL", "coordination": "COMPETITIVE_CANDIDATES", "decision_group": "offer", "outputs": ["b"]},
        {"id": "judge", "workstream": "COMMERCIAL", "coordination": "OWNER_ADJUDICATION", "depends_on": ["candidate_a", "candidate_b"], "consumes_group": "offer", "adjudicator": "commercial_director", "outputs": ["decision"]},
    ]))
    state_path = tmp_path / "program-state.json"
    run = ProgramOrchestrator(graph, state_path=state_path)
    assert {node.node_id for node in run.ready()} == {"candidate_a", "candidate_b"}
    run.complete("candidate_a", outputs={"a": {"model": "native"}}, result={"score": 8})
    assert "judge" not in {node.node_id for node in run.ready()}
    run.complete("candidate_b", outputs={"b": {"model": "series"}}, result={"score": 7})
    assert "judge" in {node.node_id for node in run.ready()}

    packet = run.packet("judge")
    assert {item["node_id"] for item in packet["candidate_group"]} == {"candidate_a", "candidate_b"}
    assert packet["peer_chat_allowed"] is False

    run.adjudicate(
        "judge",
        decision="SELECT",
        selected_candidate_ids=("candidate_a",),
        rationale="better fit",
        outputs={"decision": {"selected": "candidate_a"}},
    )
    assert run.state.node_status["judge"] == "COMPLETED"
    assert run.state.decisions[-1]["adjudicator"] == "commercial_director"
    persisted = json.loads(state_path.read_text(encoding="utf-8"))
    assert persisted["decisions"][-1]["selected_candidate_ids"] == ["candidate_a"]


def test_consultation_is_advisory_and_peer_chat_is_not_the_protocol(tmp_path):
    graph = ProgramGraph(graph_payload([
        {"id": "research", "workstream": "GROWTH", "coordination": "INDEPENDENT_PARALLEL", "outputs": ["facts"]},
        {"id": "consult", "workstream": "COMMERCIAL", "coordination": "CONSULTATIVE_ADVICE", "depends_on": ["research"], "inputs": ["facts"], "outputs": ["advice"], "advisory_only": True},
    ]))
    run = ProgramOrchestrator(graph, state_path=tmp_path / "state.json")
    run.complete("research", outputs={"facts": ["x"]})
    packet = run.packet("consult")
    assert packet["peer_chat_allowed"] is False
    assert packet["node"]["advisory_only"] is True
    run.complete("consult", outputs={"advice": "consider sponsor fit"})
    assert run.state.node_results["consult"] == {}


def test_upstream_invalidation_only_resets_affected_downstream(tmp_path):
    graph = ProgramGraph(graph_payload([
        {"id": "a", "workstream": "A", "coordination": "INDEPENDENT_PARALLEL", "outputs": ["a_out"]},
        {"id": "b", "workstream": "B", "coordination": "INDEPENDENT_PARALLEL", "outputs": ["b_out"]},
        {"id": "c", "workstream": "A", "coordination": "SERIAL_DEPENDENCY", "depends_on": ["a"], "inputs": ["a_out"], "outputs": ["c_out"]},
    ]))
    run = ProgramOrchestrator(graph, state_path=tmp_path / "state.json")
    run.complete("a", outputs={"a_out": 1})
    run.complete("b", outputs={"b_out": 2})
    run.complete("c", outputs={"c_out": 3})
    run.invalidate_from("a", "upstream changed")
    assert run.state.node_status["b"] == "COMPLETED"
    assert run.state.node_status["a"] == "READY"
    assert run.state.node_status["c"] == "WAITING"
    assert "b_out" in run.state.artifacts
    assert "a_out" not in run.state.artifacts
    assert "c_out" not in run.state.artifacts



def test_declared_superseded_blocked_and_execution_disabled_nodes_never_become_ready():
    graph = ProgramGraph(graph_payload([
        {"id": "retired", "workstream": "IP", "coordination": "SERIAL_DEPENDENCY", "status": "SUPERSEDED_HISTORICAL_ONLY", "execution_allowed": False, "historical_only": True, "superseded_by": "new_task"},
        {"id": "disabled", "workstream": "IP", "coordination": "SERIAL_DEPENDENCY", "status": "READY", "execution_allowed": False},
        {"id": "blocked", "workstream": "IP", "coordination": "SERIAL_DEPENDENCY", "status": "BLOCKED_BY_OWNER", "execution_allowed": True},
        {"id": "new_task", "workstream": "IP", "coordination": "SERIAL_DEPENDENCY", "status": "READY", "outputs": ["new_output"]},
    ]))
    run = ProgramOrchestrator(graph)
    assert {node.node_id for node in run.ready()} == {"new_task"}
    assert run.state.node_status["retired"] == "SUPERSEDED"
    assert run.state.node_status["disabled"] == "BLOCKED"
    assert run.state.node_status["blocked"] == "BLOCKED"

def test_graph_rejects_missing_or_non_ancestor_input_producers():
    with pytest.raises(ValueError, match="input artifact.*exactly one producer"):
        ProgramGraph(graph_payload([{"id": "consumer", "workstream": "A", "coordination": "SERIAL_DEPENDENCY", "inputs": ["missing_artifact"]}]))
    with pytest.raises(ValueError, match="must be a declared dependency ancestor"):
        ProgramGraph(graph_payload([
            {"id": "producer", "workstream": "A", "coordination": "INDEPENDENT_PARALLEL", "outputs": ["shared_artifact"]},
            {"id": "unrelated", "workstream": "B", "coordination": "INDEPENDENT_PARALLEL"},
            {"id": "consumer", "workstream": "C", "coordination": "SERIAL_DEPENDENCY", "depends_on": ["unrelated"], "inputs": ["shared_artifact"]},
        ]))

def test_reject_all_decision_blocks_canon_promotion_and_select_unblocks_it(tmp_path):
    graph = ProgramGraph(graph_payload([
        {"id": "candidate_a", "workstream": "IP", "coordination": "COMPETITIVE_CANDIDATES", "decision_group": "routes", "outputs": ["route_a"]},
        {"id": "candidate_b", "workstream": "IP", "coordination": "COMPETITIVE_CANDIDATES", "decision_group": "routes", "outputs": ["route_b"]},
        {"id": "review", "workstream": "IP", "coordination": "OWNER_ADJUDICATION", "depends_on": ["candidate_a", "candidate_b"], "consumes_group": "routes", "adjudicator": "user", "outputs": ["decision"]},
        {"id": "canon", "workstream": "IP", "coordination": "SERIAL_DEPENDENCY", "depends_on": ["review"], "inputs": ["decision"], "outputs": ["canon_identity"], "required_decision_artifact": "decision", "required_decision_outcomes": ["SELECT"]},
    ]))
    run = ProgramOrchestrator(graph, state_path=tmp_path / "state.json")
    run.complete("candidate_a", outputs={"route_a": {"id": "A"}})
    run.complete("candidate_b", outputs={"route_b": {"id": "B"}})
    run.adjudicate("review", decision="REJECT_ALL", rationale="Neither route survives the identity test.", outputs={"decision": {"accepted": False}})
    assert run.state.node_status["canon"] == "BLOCKED"
    assert "canon" not in {node.node_id for node in run.ready()}
    run.invalidate_from("review", "new visual evidence supplied")
    run.adjudicate("review", decision="SELECT", selected_candidate_ids=("candidate_a",), rationale="Route A survives the visual review.", outputs={"decision": {"accepted": "A"}})
    assert run.state.node_status["canon"] == "READY"
    run.complete("canon", outputs={"canon_identity": {"route": "A"}})
    assert run.state.node_status["canon"] == "COMPLETED"

def test_fail_requires_a_ready_node():
    graph = ProgramGraph(graph_payload([{"id": "blocked", "workstream": "A", "coordination": "SERIAL_DEPENDENCY", "status": "BLOCKED", "execution_allowed": False}]))
    run = ProgramOrchestrator(graph)
    with pytest.raises(RuntimeError, match="not READY"):
        run.fail("blocked", "must not execute")

def test_integrated_program_graph_is_valid_and_has_true_parallel_and_competition():
    graph = ProgramGraph.from_path(REPO_ROOT / "projects/ai-self-media-commercialization/SUBTASK_GRAPH.json")
    assert graph.validate() == []
    groups = graph.decision_groups()
    assert len(groups["commercial_offer_architecture"]) >= 2
    assert len(groups["pilot_topic_slate"]) >= 2
    assert len(groups["g2_character_structure_routes"]) == 3
    assert set(json.loads((REPO_ROOT / "projects/ai-self-media-commercialization/SUBTASK_GRAPH.json").read_text(encoding="utf-8"))["parallel_now"]) == {
        "g2_design_counterreview",
        "growth_baseline_and_topic_hypotheses",
        "commercial_advertiser_map",
    }
