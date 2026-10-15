import pytest

from video_growth_agent.owner_behavior_admission import (
    BehaviorAdmissionError,
    EvolutionDisposition,
    HypothesisDisposition,
    ProblemLayer,
    RootScopeHypothesis,
    finalize_problem_closure,
    record_recovery_attempt,
    require_root_scope_admission,
    require_user_escalation_admission,
)


def hypothesis(hypothesis_id, layer, disposition):
    return RootScopeHypothesis(
        hypothesis_id=hypothesis_id,
        layer=layer,
        statement=f"candidate root at {layer.value}",
        disposition=disposition,
        supporting_evidence_refs=(f"evidence:support:{hypothesis_id}",),
        falsification_or_rejection_refs=(f"evidence:probe:{hypothesis_id}",),
    )


def local_root():
    return require_root_scope_admission(
        hypotheses=(hypothesis("asset", ProblemLayer.ASSET_OR_TOOL, HypothesisDisposition.SELECTED),),
        selected_hypothesis_id="asset",
    )


def systemic_root():
    return require_root_scope_admission(
        hypotheses=(
            hypothesis("workflow", ProblemLayer.WORK_ORDER_OR_EDITORIAL_WORKFLOW, HypothesisDisposition.SELECTED),
            hypothesis("architecture", ProblemLayer.MEDIA_BUSINESS_ARCHITECTURE, HypothesisDisposition.REJECTED),
        ),
        selected_hypothesis_id="workflow",
        material_problem=True,
        architecture_reassessment_refs=["docs/media_business_os.md#reassessment"],
        current_agent_dogfood_refs=["docs/agent_operability_scenarios.md#current-agent-walkthrough"],
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


def test_repairable_problem_cannot_skip_root_scope():
    with pytest.raises(BehaviorAdmissionError, match="root-scope admission"):
        finalize_problem_closure(
            problem_detected=True,
            repair_path_available=True,
            authority_permits_repair=True,
            explicit_user_choice_required=False,
            repair_attempted=True,
            repair_succeeded=True,
        )


def test_admitted_repair_cannot_end_as_recommendation_only():
    with pytest.raises(BehaviorAdmissionError, match="was not attempted"):
        finalize_problem_closure(
            problem_detected=True,
            repair_path_available=True,
            authority_permits_repair=True,
            explicit_user_choice_required=False,
            repair_attempted=False,
            repair_succeeded=False,
            root_scope_receipt=local_root(),
            evolution_disposition=EvolutionDisposition.LOCAL_LEARNING_ONLY,
        )


def test_repair_and_evidence_backed_no_change_are_valid_after_admission():
    assert finalize_problem_closure(
        problem_detected=True,
        repair_path_available=True,
        authority_permits_repair=True,
        explicit_user_choice_required=False,
        repair_attempted=True,
        repair_succeeded=True,
        root_scope_receipt=local_root(),
        evolution_disposition=EvolutionDisposition.LOCAL_LEARNING_ONLY,
    ) == "REPAIR_EXECUTED"

    assert finalize_problem_closure(
        problem_detected=True,
        repair_path_available=False,
        authority_permits_repair=False,
        explicit_user_choice_required=False,
        repair_attempted=False,
        repair_succeeded=False,
        no_change_evidence=["architecture://counterexample"],
        root_scope_receipt=local_root(),
        evolution_disposition=EvolutionDisposition.NO_DURABLE_EVOLUTION_WITH_EVIDENCE,
    ) == "NO_CHANGE_WITH_EVIDENCE"


def test_user_or_external_claim_cannot_be_promoted_directly_to_root_cause():
    with pytest.raises(BehaviorAdmissionError, match="promoted without falsification"):
        require_root_scope_admission(
            hypotheses=(hypothesis("arch", ProblemLayer.MEDIA_BUSINESS_ARCHITECTURE, HypothesisDisposition.SELECTED),),
            selected_hypothesis_id="arch",
            direct_user_or_external_claim_promoted_without_test=True,
        )


def test_systemic_video_problem_requires_current_agent_operability_evidence():
    with pytest.raises(BehaviorAdmissionError, match="operability/dogfood evidence"):
        require_root_scope_admission(
            hypotheses=(
                hypothesis("workflow", ProblemLayer.WORK_ORDER_OR_EDITORIAL_WORKFLOW, HypothesisDisposition.SELECTED),
                hypothesis("architecture", ProblemLayer.MEDIA_BUSINESS_ARCHITECTURE, HypothesisDisposition.REJECTED),
            ),
            selected_hypothesis_id="workflow",
            material_problem=True,
            architecture_reassessment_refs=["docs/media_business_os.md#reassessment"],
        )


def test_material_video_problem_requires_durable_causal_evidence():
    with pytest.raises(BehaviorAdmissionError, match="durable causal evidence"):
        finalize_problem_closure(
            problem_detected=True,
            repair_path_available=True,
            authority_permits_repair=True,
            explicit_user_choice_required=False,
            repair_attempted=True,
            repair_succeeded=True,
            root_scope_receipt=systemic_root(),
            evolution_disposition=EvolutionDisposition.DOMAIN_EVOLUTION_CANDIDATE,
        )


def test_material_video_problem_can_close_with_owner_native_evolution_evidence():
    assert finalize_problem_closure(
        problem_detected=True,
        repair_path_available=True,
        authority_permits_repair=True,
        explicit_user_choice_required=False,
        repair_attempted=True,
        repair_succeeded=True,
        root_scope_receipt=systemic_root(),
        evolution_disposition=EvolutionDisposition.DOMAIN_EVOLUTION_UPDATED,
        durable_problem_ref="audits/EVOLUTION_INDEX.json#EVO-20261016-COMMON-BEHAVIOR-1-3",
    ) == "REPAIR_EXECUTED"
