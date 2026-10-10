# Reviewer Execution Attestation

## Purpose
A role name, prompt, approval row or completed work-order file does not prove that an independent reviewer execution occurred. Critical review therefore separates four evidence classes:

1. **work-order proof** — the configured specialist task existed and completed;
2. **review receipt proof** — the verdict/result was durably recorded;
3. **artifact binding** — the review is bound to exact input and target digests;
4. **execution attestation** — the verdict is bound to a distinct trusted execution identity and context where the stage requires isolation.

A critical gate that requires attestation needs all four.

## Threat model
This prevents procedural false claims such as one model changing role labels and being counted as several independent reviewers, manually signing missing reviewers after aggregate QA, reusing one blind-review context for sibling specialists, reviewing version A and silently replacing it with version B, or retaining PASS after deleting the underlying proof.

It does not defend against a malicious repository administrator who can rewrite code, trust configuration and receipts together. Repository write authority is a higher trust boundary.

## Production default
`video_growth_agent/data/executors.json` intentionally ships with an empty `trusted_executors` map. This is the fail-closed state, not incomplete configuration. A provider adapter becomes trusted only after its live identity, modality, isolation and proof semantics are verified.

## Evidence classes
Do not collapse all identifiers into “provider trace”. Distinguish:

- **provider-issued execution evidence** — request/run/response IDs and resolved model identity actually returned or inspectably exposed by the provider;
- **owner correlation identity** — local context/trace/group IDs used to bind owner receipts and prove non-reuse;
- **artifact/request/result binding** — exact packet, input, request and result digests;
- **inspectable proof reference** — stable evidence that lets the owner verify what the provider actually processed and returned.

A unique local correlation ID is useful but is not provider-issued proof and does not by itself prove context isolation.

## Attestation contract
Each accepted isolated review execution binds at least:

- executor ID, provider and model;
- unique execution ID;
- provider run/request identity when exposed;
- owner context and trace correlation IDs;
- work-order ID, stage and agent ID;
- review packet digest and standardized result digest;
- all observed input artifact digests;
- isolated-context declaration;
- sibling-verdict visibility declaration;
- inspectable proof reference.

`group_id` may be shared for observability. Execution/run/context/trace identities may not be reused where the active policy requires uniqueness within a blind-review wave.

## Reviewer packet digest
The runtime derives the review execution contract from authoritative state. It includes project/stage/task/work-order identity, wave, agent and approval role, blind state, prompt fingerprint, exact input digests, peer-chat prohibition and approval-visibility boundary. If any bound input drifts, prior attestation is stale.

## Provider promotion rule
A provider adapter must not enter production `trusted_executors` merely because it can call an API. Before trust registration it must demonstrate:

1. one provider execution per work order;
2. truthful provider-issued versus owner-local identity semantics;
3. a fresh isolated execution construction for each blind reviewer;
4. no sibling verdicts in first-wave context;
5. actual access to every artifact modality the reviewer claims to inspect;
6. stable exact-input/request/result binding;
7. inspectable raw request/response or equivalent provider proof;
8. failure-closed behavior when required proof or modality is unavailable;
9. regression tests for identity reuse and input drift.

A still/contact-sheet-only reviewer cannot certify normal-speed motion, pacing, picture/sound interaction or audiovisual cohesion.

## Operational sequence
`WORK ORDER -> REVIEW CONTRACT -> ISOLATED PROVIDER RUN -> PROVIDER PROOF -> STANDARDIZED RESULT -> EXECUTION ATTESTATION -> IMMUTABLE RECEIPTS -> GATE`

The Executive Producer may synthesize only after required first-wave executions produce valid evidence. It cannot manufacture missing execution proof after the fact.
