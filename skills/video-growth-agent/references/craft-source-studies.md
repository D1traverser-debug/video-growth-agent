
# Craft source studies — portable mechanisms, not copied workflows

**Scope (2026-10-23):** User-authorized research and incorporation of relevant public production skills. These are examined source sections and specific transfer hypotheses, **not** claims of reading every linked site, mastering all professional film practice or verifying real film performance. The one authoritative runtime technique catalogue remains video_growth_agent/data/techniques.json. These notes document why individual methods are candidates and how they should be falsified, not a second technique register.

## Source admission
Priority: original screenplay/footage and approved reference → first-party model/creator documentation → primary professional production practice → actual generated media → secondary/community comparisons. For each: source URL, mechanism, scope, exclusions, cheapest falsifying test and observed status. Materially changing a production default requires representative verified outputs; reading a website does not grant that evidence.

### Study 01: MiniMax H3 prompt/source modes
Primary: https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md
Catalog: https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/README.md
Examined: T2VA, I2VA, FL2VA, L2VA and Ref2VA; audiovisual field order, local shot timing, reference labels, dialogue and music. **Portable:** provider-specific prompt encoding must preserve story intent, soundtrack and reference assets. **Not portable:** treat this model syntax as universal artistic taste; synthesize fake keyframe bindings. **Test:** timecoded SFX and one literal Mandarin line in the compiled prompt, then inspect rendered sync. **State:** structural tests exist, performance unverified.

<a id="study-02"></a>

### Study 02: graphic, action and sound-matched edits
Primary: https://www.adobe.com/creativecloud/video/discover/match-cut.html
Examined: graphic/action/audio cut relationships, actual post-production alignment and continuity concerns. **Portable:** editor specifies source and destination of match by visible prop geometry, continuing actor motion or precise audible bridge. **Avoid:** artificial transitions that overwhelm acting or spatial legibility. **Test:** one ribbon-to-hand match cut versus straight cut; evaluate viewer comprehension and frame geometry on rendered media. **Candidate:** T-016; not validated in this studio.

<a id="study-03"></a>

### Study 03: editorial dailies reviews with timecodes
Primary: https://workflow.frame.io/guide
Examined: separation of editorial recipients from director/client reviewers and attachment of comments to particular media timecodes. **Portable:** version-bound feedback should name precise clip/shot and observed frame rather than vague role approval. **Avoid:** calling an unscored storyboard sheet proof the video was screened. **Test:** editor locates one intentional grip failure from an independent timecoded review note. **Candidate:** T-015; media sample pending.

### Study 04: story-first multi-shot animation workflow
Primary: https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/3d-animation-short-generator/SKILL.md
Examined: project brief, story turn, character/scene references, six-column shot table, per-second directives, shot generation, editorial assembly and audio. **Portable:** lock character identity, environment landmarks and prop states before the expensive shots; use a standardized handoff at cuts. **Not portable:** its fixed Pixar-inspired style, Hub-only cards, predefined H3 default, 30–60s assumptions and whole canvas orchestration. **Test:** two-shot identity/prop continuity with actual generated output. **State:** original upstream Skill inspected, transfer not independently film-validated.

<a id="study-05"></a>

### Study 05: design-level independent review
Primary: https://google.github.io/eng-practices/review/
Details: https://google.github.io/eng-practices/review/reviewer/looking-for.html
Small changes: https://google.github.io/eng-practices/review/developer/small-cls.html
Examined: independent author/reviewer perspective, design/functionality/edge-case assessment and small reviewable changes. **Portable by analogy:** assign scoped film writer/director/editor/art/sound objections independently against the same plan SHA; collect findings before showrunner resolution. **Avoid:** interpreting printed roles as independently executed people; forcing all seven reviewers onto a trivial prompt request. **Test:** competing art and editor feedback remains present with precise owners, and wrong-version review is blocked. **Candidate:** T-015; film effectiveness unverified.

<a id="study-06"></a>

### Study 06: systemic root-cause learning
Primary: https://sre.google/workbook/postmortem-culture/
Examined: blameless causal analysis, system-level corrective actions with measurable end-state, sharing of recurrence patterns. **Portable:** failure → root cause category → lowest-cost counterexample → repair hypothesis → replay result → revised technique candidate. **Avoid:** making each local aesthetic opinion a new universal restriction or role. **Test:** repeated lost music cue yields a regression test that fails on the old implementation. **Candidate:** T-017; actual recurring media failure evidence needed.

### Study 07: provenance entities, activities, agents
Primary: https://www.w3.org/TR/prov-o/
Primer: https://www.w3.org/TR/prov-primer/
Examined: original/revised artifact (entity), creative/review activity and responsible reviewer role (agent), derived-from/used/associated-with links. **Portable:** exact source ref, plan SHA, role attribution and revision linkage. **Not portable:** rebuilding MediaGraph as another RDF server or asserting full W3C PROV compliance. **Test:** forged review plan digest fails before reconciliation. **State:** structural analog only.

### Study 08: editorial interchange boundaries
Primary: https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/index.rst
Examined: clip range, track, transition and external media references; OTIO does not embed video/audio. **Portable:** future interoperability adapter may read existing editorial_interchange/timeline authority. **Avoid:** a new canonical timeline or describing export metadata as finished cinema. **Test:** lossless two-shot ranges and transition round trip. **State:** source researched; adapter intentionally not built.

### Study 09: task-sized workflows and physical media mechanics
Primary: https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/papercraft-stop-motion-explainer/SKILL.md
Examined: layered visual depth, physical puppet mechanisms and explicit lightweight request bypass. **Portable:** medium-specific movement/foreground-background physics when relevant; prompt-only requests bypass irrelevant full production stages. **Not portable:** mandatory papercraft aesthetics, default Hub canvas/cards, 18-step wizard for all genres. **Test:** prompt-only task stays light; multi-shot short still carries continuity handoffs. **State:** contextual hypothesis.

## Integrated SOP, with a single Video authority

1. SOURCE + INTENT: inherit original brief and intended viewer change; select only relevant disciplines.
2. STORY + DIRECTION: writer and director propose causal scenes, actor reactions, emotional payoff, and alternative cuts/looks.
3. CRAFT HANDOFF: each discipline reads the same **complete original raw source, annotated quote/event inventory, proposed treatments, visuals and exact shot frames**, with no prior peer verdicts. For opt-in model-role simulations, the seven calls must be budgeted and approved; they are not independent human film reviews.  use the existing RoleRegistry roles (not a second controller). For material full-film work, prepare independent writer, director, storyboard, art, editor, sound and red-team packets from the exact same plan revision. For simple requests, skip unnecessary team overhead.
4. INDEPENDENT FIRST PASS: do not share peer verdicts before the first critique. A proposed reviewer must specify observed scope, evidence reference, exact shot, issue, severity, change request. A prepared role prompt is not a completed review.
5. RESOLUTION: reconcile complete submitted role reviews. A version or shot mismatch is invalid, a material veto is assigned to an existing discipline owner, and showrunner resolves only after evidence is collected. Actual rendered-media quality review remains with the existing media QA/attestation process.
6. ITERATION: revised shot plan gets a new SHA; show which shots and look/event fields changed. New plan is a candidate, not certified improvement. Small failure-fixing revisions should be reversible and retested.
7. LEARN: issue classification → external first-party comparison → prototype → actual clip replay and blind viewer evidence → accept/reject or retain candidate → update only the existing TechniqueLibrary and LEARN path. Do not call website reading an in-house validated technique.

## Why this does not create a parallel controller
Existing studio runtime, MediaGraph, LEARN stage, ExperimentPlan and RoleRegistry retain their respective authority. The new craft_round module is a stateless handoff/reconciliation adapter, never a production-state mutator. Study notes are candidate evidence; T-015/016/017 are inserted as candidate entries in the existing runtime library.

**Verification gap:** No seven independent reviewers, human blind audience or actual film-model render was executed merely by writing this SOP or preparing role packets. Only reported real inputs plus version-bound evidence may establish that later.
