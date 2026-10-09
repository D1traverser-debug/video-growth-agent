# Self-Learning Protocol

Use when a quality gap, tool limitation, superior external example, or repeated production failure appears.

## Prevention-first rule
Do not turn every failure into another role, gate, prompt or permanent rule. Before changing the global system, classify the failure:

- **local execution** — the project failed to apply an already-correct rule; fix the project, not the architecture.
- **capability/tool gap** — the method or tool cannot reach the required ceiling; search and replace/augment the method.
- **quality-standard gap** — the team lacked a benchmark, measurable threshold or evidence contract; improve the standard.
- **systemic architecture gap** — the workflow can repeatedly permit the same class of bad outcome; only this category normally justifies a global runtime change.

Prefer simplifying, replacing or deleting weak mechanisms over stacking new patches on top of them. Any proposed global rule must state what class of failures it prevents and whether it can replace or merge an existing rule.

Before a high-cost or quality-critical stage, run a short **pre-mortem**: list the most plausible ways the next stage could fail, identify which are cheap to test early, and prototype those risks before full production. The purpose is to move discovery upstream, not add ceremony.

## Learning loop
1. DIAGNOSE the exact bottleneck: idea, research, script, art, motion, asset quality, sound, editing, render engineering, QA or commercial fit.
2. Decide whether the defect is local, capability, standard, or systemic before mutating the global Skill/runtime.
3. SEARCH for at least two plausible approaches using official docs, GitHub Skills/source, credible creator breakdowns, Reddit/X/YouTube discussions and current tools when relevant.
4. COMPARE quality ceiling, cash cost, token/credit cost, licensing, repeatability, observability, coordination cost and lock-in.
5. INSPECT SOURCE rather than trusting promotional claims.
6. PRE-MORTEM the next expensive stage and PROTOTYPE only its highest-risk assumptions first.
7. QA the real output against external benchmarks, not merely the previous internal version.
8. ACCEPT or REJECT with an explicit reason.
9. PERSIST verified lessons in code/config/reference docs only when they generalize; keep project-specific fixes inside the project. Rejected approaches remain recorded so they are not rediscovered as if new.

Do not run background surveillance. Refresh knowledge during active work. Tool choice and organizational structure are replaceable; the quality contract and evidence standard are not.
