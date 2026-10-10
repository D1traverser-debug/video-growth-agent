# System Self-Audit — 2026-10-11

Status: **HARDENED_WITH_REMAINING_FAIL_CLOSED_GAPS**

Scope: control plane, learning admission, execution evidence, generation authorization. This maintenance pass does not advance the active business stage and does not treat maintenance activity as production progress.

## Audit method

The pass used the control-plane sequence: challenge assumptions -> search for bypasses -> classify local vs systemic defects -> apply the smallest durable fix -> add adversarial regression coverage -> preserve unresolved gaps as explicit blockers.

No ad-hoc session material is used as learning evidence merely because it was visible to the operator during this pass.

## Fixed defect 1 — pre-generation evidence could be mounted under the wrong specialist slot

`generation_guard.py` required separate Art Director, Creative Director and Red Team evidence plus independent execution/context identities, but the external proof bundle did not itself declare and bind the reviewer role. A proof object could therefore be placed under the wrong role key without a direct role-identity mismatch failure.

Fix:

- `reviewer_role` is now required in every verified pre-generation challenge proof.
- `reviewer_role` must equal the challenge slot being authorized.
- Missing or mismatched role identity fails closed.
- Regression tests cover both missing-role and swapped-role evidence.

Distilled rule: **evidence must bind subject, action, artifact and role; dictionary position is not identity proof.**

## Fixed defect 2 — transient session content had no explicit learning-admission boundary

The self-learning protocol defined what useful external material looks like, but did not explicitly distinguish "seen during a session" from "authorized learning source". That creates a contamination risk for ad-hoc conversation, temporary research and side tasks.

Fix:

- learning-source admission is now default deny;
- internal project evidence must be present in the declared work packet;
- external material requires explicit import plus affirmative learning authorization and a durable source reference;
- ambient conversation, unlisted browsing context and undeclared side-task material are outside the durable learning boundary;
- user-declared no-learn/no-persist material must be excluded before durable serialization;
- the system must not persist a content-specific denylist merely to remember an exclusion, because the denylist would itself preserve a trace.

Regression tests pin the policy language so future edits cannot silently collapse this boundary.

Distilled rule: **visibility is not admission; learning must be opt-in at the source boundary.**

## Fixed defect 3 — producer completion could masquerade as role approval

Several `produce` work orders declared an `approval_role`. `AgenticStudio.complete_work()` automatically signs `PASS` for such tasks. This conflated two different facts:

1. the producer completed the assigned artifact contract; and
2. a role approved the resulting artifact/stage.

That is structurally unsafe because successful production is not independent approval.

Fix:

- all producer `approval_role` declarations were removed from `execution-plan.json`;
- workflow required-role gates now contain review/meta-review roles only;
- producer completion remains enforced by work-order completion, artifact existence and producer-output provenance;
- regression tests require that no `produce` task can declare an approval role and that workflow required roles are a subset of actual review/meta-review approval roles.

Distilled rule: **production provenance and approval authority are different evidence classes.**

## Remaining fail-closed gaps

### Producer execution identity is still not provider-attested

Producer work orders prove declared packet, completion and output provenance, but the current provider-backed `ExecutionAttestation` path is enforced primarily for critical review work. Therefore the system must not claim that every producer persona has independently executed merely because a work order and artifact exist.

Required future evolution: generalize execution attestation or introduce an equally strong producer-execution receipt bound to provider/model/run identity, work-order digest, exact input digests and output/result digests.

### Learning-source admission is policy-pinned but not yet a universal runtime guard

The declared work packet already limits normal agent inputs, and the new policy forbids ambient learning. However a universal runtime mechanism that rejects a `learning_candidate` containing undeclared external provenance is not yet wired at the lowest boundary.

Required future evolution: machine-validate learning candidate source manifests against the declared work packet plus explicitly imported learning sources before LEARN can pass.

### Quality-critical generation gateway remains unavailable

The generation guard is stronger, but a single enforced generation gateway that resolves durable review receipts/attestations and then authorizes generator calls is still unavailable. Quality-critical generation therefore remains fail closed.

### Trusted reviewer executors remain empty

Configured reviewer roles and provider adapters do not equal trusted isolated execution. No executor should be promoted to trusted status until live media access, provider/model identity, run/request identity semantics, context/trace semantics and inspectable proof are verified.

## Business-state preservation

This audit is maintenance only. It does not authorize the frozen full rebuild, does not mark the active visual-preview work as passed, and does not substitute governance hardening for actual isolated Art Director / Creative Director / Red Team execution.

## Net evolution

The system moved from:

- challenge-slot key as implicit reviewer identity -> explicit reviewer-role binding;
- session visibility as an ambiguous learning source -> default-deny learning admission;
- producer completion plus automatic PASS -> producer provenance separated from review authority.

The remaining gaps are preserved as blockers rather than represented as completed capability.
