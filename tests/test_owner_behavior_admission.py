import pytest

from video_growth_agent.owner_behavior_admission import (
    BehaviorAdmissionError,
    finalize_problem_closure,
    record_recovery_attempt,
    require_user_escalation_admission,
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


def test_repairable_problem_cannot_end_as_recommendation_only():
    with pytest.raises(BehaviorAdmissionError, match="was not attempted"):
        finalize_problem_closure(
            problem_detected=True,
            repair_path_available=True,
            authority_permits_repair=True,
            explicit_user_choice_required=False,
            repair_attempted=False,
            repair_succeeded=False,
        )


def test_repair_and_evidence_backed_no_change_are_valid_terminals():
    assert finalize_problem_closure(
        problem_detected=True,
        repair_path_available=True,
        authority_permits_repair=True,
        explicit_user_choice_required=False,
        repair_attempted=True,
        repair_succeeded=True,
    ) == "REPAIR_EXECUTED"

    assert finalize_problem_closure(
        problem_detected=True,
        repair_path_available=False,
        authority_permits_repair=False,
        explicit_user_choice_required=False,
        repair_attempted=False,
        repair_succeeded=False,
        no_change_evidence=["architecture://counterexample"],
    ) == "NO_CHANGE_WITH_EVIDENCE"
