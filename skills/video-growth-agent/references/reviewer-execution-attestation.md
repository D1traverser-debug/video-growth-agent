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
- registering a review result without an inspectable provider execution reference.

It does **not** claim to defend against a malicious repository administrator who can rewrite the code, trust configuration and receipts together. Repository write authority remains a higher trust boundary.

## Production default

`video_growth_agent/data/executors.json` intentionally contains:

```json
"trusted_executors": {}
```

This is not incomplete configuration to paper over. It is the fail-closed production state. Until a real reviewer executor is connected and its provider/run/isolation semantics are verified, a critical blind-review gate cannot claim independent-agent review.

Tests may inject a test-only trust registry from `tests/`; no test executor is shipped as trusted production configuration.

## Evidence classes

Do not collapse all execution identifiers into the phrase “provider trace”. The trust model distinguishes:

- **provider-issued execution evidence** — request/run/response IDs and resolved model identity actually returned or verifiably exposed by the provider;
- **owner/local correlation identity** — locally created `context_id`, `trace_id`, group IDs or request correlation IDs used to prove non-reuse and bind receipts across the owner runtime;
- **artifact/request/result binding** — packet, input, request and result digests that prove what was reviewed;
- **inspectable proof reference** — immutable or stable evidence that lets the owner verify the provider run/request/response rather than trusting an adapter’s self-report.

A local correlation ID may be required and unique without being provider-issued. Uniqueness alone is not proof of context isolation. Trust registration must document how the adapter creates an actually fresh execution context and which identifiers the provider itself issues.

## Attestation contract

Each accepted execution must bind:

- `executor_id`
- provider and model
- unique `execution_id`
- unique provider run/request ID where the provider exposes one
- unique owner/runtime context correlation ID
- unique owner/runtime trace correlation ID
- work-order ID
- stage
- agent ID
- review-packet/contract digest
- standardized review-result digest
- all observed input artifact digests
- isolated-context declaration
- sibling-verdict visibility declaration
- inspectable provider proof reference

`group_id` may be shared for observability grouping; execution/run/context/trace identities may not be reused within a blind-review wave.

The attestation field names are a normalized owner schema. Their presence does not itself prove that every field was provider-issued. Source semantics are established by the trusted-executor registration and the adapter’s live validation evidence.

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
2. the exact provider-issued request/run/response identity available from that API, without relabeling local IDs as provider evidence;
3. a documented construction that creates fresh isolated execution for each blind reviewer, plus unique owner correlation IDs;
4. no sibling verdicts injected into first-wave context;
5. actual access to every artifact modality the reviewer claims to inspect;
6. stable binding between exact request/input digests, provider output and the standardized review result;
7. an inspectable raw request/response or equivalent provider proof reference;
8. failure-closed behavior when required provider proof or modality access is unavailable;
9. integration tests proving execution/run/context reuse and input drift are rejected.

For VISUAL_PREVIEW specifically, a reviewer that cannot actually consume the rendered moving media cannot be registered as a full video reviewer. A contact sheet alone may support an image/composition specialist, but it cannot satisfy normal-speed motion, pacing, picture/sound or audiovisual-cohesion review.

## Operational sequence

`WORK ORDER → REVIEW EXECUTION CONTRACT → ISOLATED PROVIDER RUN → RAW/INSPECTABLE PROVIDER PROOF → STANDARDIZED REVIEW RESULT → EXECUTION ATTESTATION → IMMUTABLE RECEIPTS → GATE`

The Executive Producer may synthesize only after first-wave review executions have produced valid attestations. It cannot manufacture missing execution proof after the fact.

## Current Pilot 002 consequence

Sample V2 remains `PROCESS_INVALID_AND_VISUAL_FAIL`. The protocol prevents the studio from relabeling the existing aggregate QA as formal five-role review. Pilot 002 may re-enter formal VISUAL_PREVIEW only after a real executor adapter capable of producing valid attestations is connected and registered.
