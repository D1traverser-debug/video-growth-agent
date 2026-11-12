# Red Silk Date — Reusable Production Method v11

This is the project-specific execution method recovered from the v11 handoff. Reuse the process, not the Red Silk visual assets, for other productions.

## A. Task contract before execution
Every task must state:
- goal: what outcome changes, not just which command runs;
- scope: assets, shots, frames and files affected;
- inputs: exact source files, versions, hashes, licenses and upstream state;
- method: approved route and tool versions;
- outputs: path, format, frame range and specifications;
- acceptance: independent measurable thresholds;
- rollback: prior version and recovery/re-run node.

No output contract or acceptance method means no execution.

## B. Production workflow
1. Requirement recovery: read Project Bible, requirement ledger, approved ADRs, current state and prior audits. Separate goals, ideas, suggestions, commands and corrections.
2. Risk ordering: prioritize failures with high probability, impact and discovery delay. For this project: character identity, male hand rig, ribbon state machine, contact slice and cloud Runtime.
3. Research/selection: use primary documentation for versions, license and capabilities; compare at least two routes; use counterexamples; record the decision in an ADR.
4. Vertical Slice: select the highest-risk shot (S04 catch) and run the full path with formal/near-formal assets: asset → rig → animation → FX → camera → lookdev → render → composite → QA. Do not expand the seven shots before it passes.
5. Production: lock asset and solver versions; execute the dependency graph; each node emits cache, manifest, logs and QA. Do not reset global physical state at cuts.
6. Final delivery: independent QA checks image sequence, sound, specifications, continuity, project reopenability, cache dependencies and hashes.

## C. Defect handling
1. Freeze failed inputs and logs so retries cannot overwrite evidence.
2. Classify the defect: requirement, data, implementation, environment, tool limitation or acceptance.
3. Build a minimal reproduction; check whether implementation and test share the same wrong assumption.
4. Add counterfactual tests so the repair cannot pass only on the original sample.
5. Run current tests, adjacent-state regression and downstream affected-node regression.
6. Independent QA reviews; update state, defect record and ADR/method.

## D. Independent QA
- Producer and reviewer are not the same role for critical physics/render sign-off.
- A numeric pass proves only what the test actually measured.
- Technical previews, proxy geometry and pre-scripted trajectories are not final physical or artistic proof.
- Final delivery binds artifact identity, tool versions, caches, manifest and SHA-256.

## E. XPBD v15 event-driven ribbon state
State sequence:
R0 ATTACHED → R1 RELEASE → R2 FLIGHT → R3 CATCH_APPROACH → R4 GRIP_CAPTURE → R5 HAND_CARRY → R6 RETIE → R7 SETTLE.

Frame windows are directing targets, not forced contact frames. Actual contact time is solver-detected. If it differs from the target, adjust hand animation/guide forces and re-simulate; never overwrite the free-end trajectory to manufacture a pass.

Capture contract:
- independent hand collision geometry must contact the actual ribbon surface;
- validate two-finger contact timing, normal direction, relative velocity and ribbon position between pads;
- create grasp constraint only after the solver emits a valid contact event;
- retie establishes hair attachment before finger grasp release;
- preserve remaining cloth inertia and self/environment collision.
