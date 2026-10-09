# Reviewer Execution Attestation

## Why this exists

A role name, role prompt, approval row, or completed work-order file does not prove that an independent reviewer execution occurred. Sample V2 exposed this exact failure mode: one aggregate review could be mistaken for a multi-role review panel.

The studio therefore separates four proofs:

1. **work-order proof** — the configured specialist task existed and completed;
2. **review receipt proof** — the reviewer verdict/result was durably recorded;
3. **artifact binding** — the review is bound to the exact input and target digests;
4. **execution attestation** — the verdict is bound to a distinct external execution identity and context.

A quality-critical gate needs all four.

## Threat model

This control prevents accidental or procedural false claims such as:

- one model changing role labels and being counted as five independent reviewers;
- manually signing all required roles after an aggregate QA pass;
- reusing one model run/context for sibling blind reviewers;
- reviewing version A and silently replacing it with version B;
- deleting the underlying execution proof while keeping the PASS approvals;
- registering a review result without a provider run/trace reference.

It does **not** claim to defend against a malicious repository administrator who can rewrite the code, trust configuration and receipts together. Repository write authority remains a higher trust boundary.

## Production default

`video_growth_agent/data/executors.json` intentionally contains:

```json
"trusted_executors": {}
```

This is not incomplete configuration to paper over. It is the fail-closed production state. Until a real reviewer executor is connected and its provider/run/trace semantics are verified, a critical blind-review gate cannot claim independent-agent review.

Tests may inject a test-only trust registry from `tests/`; no test executor is shipped as trusted production configuration.

## Attestation contract

Each accepted execution must bind:

- `executor_id`
- provider and model
- unique `execution_id`
- unique provider run/request ID
- unique context/session ID
- unique trace ID
- work-order ID
- stage
- agent ID
- review-packet/contract digest
- standardized review-result digest
- all observed input artifact digests
- isolated-context declaration
- sibling-verdict visibility declaration
- provider proof reference

`group_id` may be shared for observability grouping; execution/run/context/trace identities may not be reused within a blind-review wave.

## Reviewer packet digest

The runtime derives the review execution contract from authoritative state rather than trusting a caller-supplied prompt string. The digest includes:

- project/stage/task/work-order identity;
- review wave;
- reviewer agent and approval role;
- blind-review state;
- reviewer prompt fingerprint;
- exact input artifact digests;
- `peer_chat_allowed = false`;
- `project_approvals_hidden = true` for blind review.

If any of these inputs drift after review, the prior attestation no longer matches.

## Provider adapter promotion rule

An executor must NOT be added to production `trusted_executors` merely because it can call a model API. Before registration, its adapter must demonstrate:

1. one provider execution per work order;
2. a provider-issued run/request/trace identifier or equivalent inspectable proof;
3. fresh isolated context for each blind reviewer execution;
4. no sibling verdicts injected into first-wave context;
5. actual access to every artifact modality the reviewer claims to inspect;
6. stable binding between the provider output and the standardized review result;
7. failure-closed behavior when provider tracing/proof is unavailable;
8. integration tests proving context/run reuse is rejected.

For VISUAL_PREVIEW specifically, a reviewer that cannot actually consume the rendered moving media cannot be registered as a full video reviewer. A contact sheet alone may support an image/composition specialist, but it cannot satisfy normal-speed motion, pacing, picture/sound or audiovisual-cohesion review.

## Operational sequence

`WORK ORDER → REVIEW EXECUTION CONTRACT → ISOLATED PROVIDER RUN → STANDARDIZED REVIEW RESULT → EXECUTION ATTESTATION → IMMUTABLE RECEIPTS → GATE`

The Executive Producer may synthesize only after first-wave review executions have produced valid attestations. It cannot manufacture missing execution proof after the fact.

## Current Pilot 002 consequence

Sample V2 remains `PROCESS_INVALID_AND_VISUAL_FAIL`. The new protocol prevents the studio from relabeling the existing aggregate QA as formal five-role review. Pilot 002 may re-enter formal VISUAL_PREVIEW only after a real executor adapter capable of producing valid attestations is connected and registered.
