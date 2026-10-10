from video_growth_agent.execution_attestation import ExecutionAttestation, ExecutionTrustRegistry


def attestation():
    return ExecutionAttestation(
        executor_id="reviewer",
        provider="provider",
        model="model",
        execution_id="exec-1",
        provider_run_id="run-1",
        context_id="ctx-1",
        trace_id="trace-1",
        work_order_id="wo-1",
        stage="VISUAL_PREVIEW",
        agent_id="creative_director_agent",
        packet_digest="packet",
        result_digest="result",
        observed_input_digests=("input",),
        isolated_context=True,
        sibling_verdicts_visible=False,
        proof_ref="proof://run-1",
    )


def config(executor):
    return {
        "policy": {
            "attestation_required_stages": ["VISUAL_PREVIEW"],
            "blind_reviews_only": True,
            "require_isolated_context": True,
            "forbid_sibling_verdict_visibility": True,
            "require_all_input_digests_observed": True,
            "require_proof_ref": True,
            "require_trust_identity_semantics": True,
        },
        "trusted_executors": {"reviewer": executor},
    }


def validate(registry):
    return registry.validate(
        attestation(),
        stage="VISUAL_PREVIEW",
        work_order_id="wo-1",
        agent_id="creative_director_agent",
        packet_digest="packet",
        result_digest="result",
        input_digests={"visual_preview": "input"},
    )


def test_trusted_executor_without_identity_semantics_fails_closed():
    registry = ExecutionTrustRegistry(
        config=config({"provider": "provider", "models": ["model"]})
    )
    failures = validate(registry)
    assert "execution_identity_semantics_missing:reviewer" in failures


def test_trusted_executor_with_truthful_identity_semantics_can_validate():
    registry = ExecutionTrustRegistry(
        config=config(
            {
                "provider": "provider",
                "models": ["model"],
                "identity_semantics": {
                    "provider_run_id": "PROVIDER_ISSUED",
                    "context_id": "OWNER_CORRELATION",
                    "trace_id": "OWNER_CORRELATION",
                    "proof_ref": "PROVIDER_INSPECTABLE_REF",
                },
                "isolation_mechanism": "one-shot stateless request per work order",
            }
        )
    )
    assert validate(registry) == []


def test_invalid_provider_claim_is_rejected():
    registry = ExecutionTrustRegistry(
        config=config(
            {
                "provider": "provider",
                "models": ["model"],
                "identity_semantics": {
                    "provider_run_id": "OWNER_CORRELATION",
                    "context_id": "OWNER_CORRELATION",
                    "trace_id": "OWNER_CORRELATION",
                    "proof_ref": "PROVIDER_INSPECTABLE_REF",
                },
                "isolation_mechanism": "one-shot stateless request per work order",
            }
        )
    )
    failures = validate(registry)
    assert "execution_identity_semantics_invalid:reviewer:provider_run_id:OWNER_CORRELATION" in failures
