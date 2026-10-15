import pytest

from video_growth_agent.owner_behavior_admission import (
    BehaviorAdmissionError,
    HypothesisDisposition,
    ProblemLayer,
    RootScopeHypothesis,
    build_root_scope_receipt,
    finalize_problem_closure,
    record_recovery_attempt,
    require_user_escalation_admission,
)


def hypothesis(hid: str, layer: ProblemLayer, disposition: HypothesisDisposition) -> RootScopeHypothesis:
    return RootScopeHypothesis(
        hypothesis_id=hid,
        layer=layer,
        statement=f"candidate cause {hid}",
        disposition=disposition,
        supporting_evidence_refs=(f"support:{hid}",),
        falsification_or_rejection_refs=(f"probe:{hid}",),
    )


def root_receipt(*, systemic: bool = False):
    items = [hypothesis("local", ProblemLayer.DOMAIN_WORKFLOW, HypothesisDisposition.SELECTED)]
    refs = []
    if systemic:
        items.append(hypothesis("upstream", ProblemLayer.DOMAIN_ARCHITECTURE, HypothesisDisposition.REJECTED))
        refs = ["docs/agent_operability_scenarios.md#root-scope"]
    return build_root_scope_receipt(
        hypotheses=items,
        selected_hypothesis_id="local",
        systemic_signal=systemic,
        architecture_reassessment_refs=refs,
    )


def test_recoverable_video_dependency_cannot_be_externalized_to_user():
    receipt = record_recovery_attempt(
        outcome="PROVISIONAL",
        safe_to_continue=True,
        project_refs=["projects/program/PROGRAM_STATE.json"],
        asset_refs=["asset://character-canon-v2"],
        unknowns=["final 3/4 validation pending"],
        confidence="MEDIUM",
    )
    with pytest.raises(BehaviorAdmissionError, match="safe owner path remains available"):
        require_user_escalation_admission(receipt)


def test_real_user_authorization_gap_can_escalate_after_recovery():
    receipt = record_recovery_attempt(
        outcome="UNRESOLVED",
        safe_to_continue=False,
        project_refs=["projects/program/PROGRAM_STATE.json"],
        external_evidence_refs=["provider://paid-plan-required"],
        unknowns=["paid provider authorization not supplied"],
        confidence="HIGH",
    )
    assert require_user_escalation_admission(
        receipt,
        requires_user_fact_authorization_or_preference=True,
    ) == "ADMITTED_REQUIRED_USER_FACT_AUTHORIZATION_OR_PREFERENCE"


def test_no_recovery_receipt_means_no_user_escalation():
    with pytest.raises(BehaviorAdmissionError, match="no Video recovery receipt"):
        require_user_escalation_admission(None)


def test_repairable_problem_cannot_bypass_root_scope_cognition():
    with pytest.raises(BehaviorAdmissionError, match="root-scope cognition"):
        finalize_problem_closure(
            problem_detected=True,
            repair_path_available=True,
            authority_permits_repair=True,
            explicit_user_choice_required=False,
            repair_attempted=False,
            repair_succeeded=False,
        )


def test_cognitively_admitted_repairable_problem_cannot_end_as_recommendation_only():
    with pytest.raises(BehaviorAdmissionError, match="was not attempted"):
        finalize_problem_closure(
            problem_detected=True,
            repair_path_available=True,
            authority_permits_repair=True,
            explicit_user_choice_required=False,
            repair_attempted=False,
            repair_succeeded=False,
            root_scope_receipt=root_receipt(),
            evolution_disposition="EVIDENCE_ONLY",
        )


def test_repair_and_evidence_backed_no_change_are_valid_after_cognition_and_evolution():
    assert finalize_problem_closure(
        problem_detected=True,
        repair_path_available=True,
        authority_permits_repair=True,
        explicit_user_choice_required=False,
        repair_attempted=True,
        repair_succeeded=True,
        root_scope_receipt=root_receipt(),
        evolution_disposition="EVIDENCE_ONLY",
    ) == "REPAIR_EXECUTED"

    assert finalize_problem_closure(
        problem_detected=True,
        repair_path_available=False,
        authority_permits_repair=False,
        explicit_user_choice_required=False,
        repair_attempted=False,
        repair_succeeded=False,
        no_change_evidence=["architecture://counterexample"],
        root_scope_receipt=root_receipt(),
        evolution_disposition="NO_DURABLE_EVOLUTION",
    ) == "NO_CHANGE_WITH_EVIDENCE"


def test_systemic_video_problem_requires_cross_layer_architecture_reassessment():
    with pytest.raises(BehaviorAdmissionError, match="at least two layers"):
        build_root_scope_receipt(
            hypotheses=[
                hypothesis("a", ProblemLayer.DOMAIN_WORKFLOW, HypothesisDisposition.SELECTED),
                hypothesis("b", ProblemLayer.DOMAIN_WORKFLOW, HypothesisDisposition.REJECTED),
            ],
            selected_hypothesis_id="a",
            systemic_signal=True,
            architecture_reassessment_refs=["docs/agent_operability_scenarios.md"],
        )
    receipt = root_receipt(systemic=True)
    assert ProblemLayer.DOMAIN_ARCHITECTURE in receipt.compared_layers


def test_user_or_external_method_cannot_be_promoted_directly_to_video_root_cause():
    with pytest.raises(BehaviorAdmissionError, match="promoted without falsification"):
        build_root_scope_receipt(
            hypotheses=[hypothesis("architecture", ProblemLayer.DOMAIN_ARCHITECTURE, HypothesisDisposition.SELECTED)],
            selected_hypothesis_id="architecture",
            direct_user_or_external_claim_promoted_without_test=True,
        )


def test_material_video_problem_requires_durable_problem_ref():
    with pytest.raises(BehaviorAdmissionError, match="durable problem evidence"):
        finalize_problem_closure(
            problem_detected=True,
            repair_path_available=True,
            authority_permits_repair=True,
            explicit_user_choice_required=False,
            repair_attempted=True,
            repair_succeeded=True,
            root_scope_receipt=root_receipt(),
            evolution_disposition="DOMAIN_CANDIDATE",
            problem_record_required=True,
        )
