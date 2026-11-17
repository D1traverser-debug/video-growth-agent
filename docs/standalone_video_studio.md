# Standalone Video Studio — Product, Method and Runtime Contract

Status: `ACTIVE_CANDIDATE_1.0`
Runtime: `video_studio.engine`
Entry: `STUDIO_ENTRY.md`
CLI: `vga-studio`
Manifest: `video_studio/data/studio_manifest.json`

## 1. Product outcome

Video Studio turns an owner's media goal into finished media and release materials. Its primary success oracle is the delivered work, not the presence of roles, stages, prompts, diagrams, task counts or passing tests.

Supported work may include cinematic explainers, technology/business documentaries, engineering demonstrations, news × fictional-video satire, meme and entertainment edits, product/brand films, animation, trailers, tutorials, shorts, long-form videos, platform-native derivatives and mixed-media work.

No single visual style, runtime, aspect ratio, duration, model, editor or production method is universal.

## 1.1 Business-domain scope

The Studio is the standalone control plane for the complete Video Growth Agent domain, not only a clip renderer. A project graph may cover one workstream or connect several:

- **MEDIA_GROWTH** — audience/problem research, demand signals, platform strategy, portfolio and series hypotheses, packaging, distribution, retention and audience outcomes.
- **ORIGINAL_DIGITAL_IP** — video-side use of approved IP, recognition/performance evidence, character/asset usage strategy and licensing-use value. Canon, likeness and identity rights remain owned by IPOS.
- **COMMERCIALIZATION** — sponsor/category fit, offer hypotheses, deliverable obligations, product-truth requirements, rights scope, measurement and commercial outcomes.
- **PRODUCTION_SYSTEM** — editorial research and claims, story/shot design, assets/takes, generation, compositing, edit, sound, QA and release.

Cross-workstream decisions must be explicit. Audience evidence may change a series hypothesis; IP performance may change packaging or licensing strategy; sponsor obligations may change format and product-asset requirements; production cost, failure and reuse evidence may change future portfolio allocation. Editorial truth, rights and owner authority remain hard constraints. Do not optimize one proxy such as views, CTR, cinematic quality, AI-video percentage or lowest credit cost.

The `video_studio` engine supplies the durable project control plane: briefs, dynamic task DAGs, leases, artifacts, decisions, reviews, failures and learning receipts. It does **not** silently recreate every legacy domain object. When Program/Series/Episode/Shot/Timeline, continuity, provider routing, business metrics or IP identity semantics are required, reuse the corresponding Video-owned domain module through an explicit, tested adapter and register its outputs as versioned Studio artifacts. Do not use the legacy fixed-stage `StudioOrchestrator` as the new controller. Existing specialized modules are optional capability libraries, not a hidden parent workflow.

The standalone runtime now exposes those explicit adapters through `vga-studio run-adapter`: EditorialPlan validation, ShotContract materialization/validation, IPOS bundle inspection/import, exact-version IPOS shot binding and canon continuity snapshot/link creation, MediaGraph bootstrap, TimelineSpec validation, shot continuity assessment, operation-specific shot routing, business outcome metrics, supplementary loudness/silence QA and deterministic programmatic-graphics rendering. Each adapter reads only declared, digest-verified task inputs and registers exact outputs through the Studio artifact transaction. The graphic renderer creates a silent candidate only; a separate sound task, canonical technical QA, human review and release check remain required.

This is not a claim that every external provider is connected. The repository currently has no trusted external generative-video executor registered. Provider generation remains a tool/session capability operation; the router can select only from supplied, current, evidence-backed engine profiles. The standalone runtime does not invent availability or invoke paid providers implicitly.


## 2. Authority and independence

- **Owner request and corrections** define the goal and constraints.
- **Project brief** is the current executable outcome contract. Revisions are recorded in the append-only event history with old/new digests and reason.
- **Decision receipts** explain material choices and their falsifiers; they do not override owner requirements.
- **Task graph** owns execution dependencies and task state.
- **Artifact records** own exact file identity, digest, version, rights and producer lineage.
- **Review records** own artifact-bound evaluation evidence.
- **Event log** is append-only operational history.
- **IPOS** remains the sole authority for original character/identity canon.

The new runtime is standalone. It has no CAOS imports, network calls, API, parent task identity, parent lease, hidden chat-memory dependency or external governance callback. The old 0.8 controller, `vga` CLI and fixed-stage workflow remain compatibility/history surfaces and are not loaded as a controller by `vga-studio`. Specialized domain modules are imported only through the explicit `video_studio.adapters` bridge when a task declares a tested adapter. CAOS integration notes remain historical documentation only.

## 3. Goal recovery and requirement governance

Every project brief should record:

- `goal`: the observable result the owner wants;
- `audience`: intended viewer and their prior knowledge;
- `deliverables`: exact files or publication packages expected;
- `format`: duration, aspect ratio, resolution, frame rate, language and platform when known;
- `content_contract`: topic, argument, emotional effect, narrative promise and content boundaries;
- `craft_contract`: visual, motion, editing, sound, voice, typography and continuity expectations;
- `hard_constraints`: non-negotiable facts, rights, identity, budget, deadline, tool and safety limits;
- `preferences`: ranked preferences that may be traded off transparently;
- `examples`: references or examples, not automatically hard requirements;
- `unknowns`: unresolved facts or decisions;
- `success_criteria`: observable acceptance conditions;
- `release_policy`: required review rubrics, rights states and publication evidence.

When requirements conflict, do not silently choose one. Record the conflict, identify which source has authority, compare the consequences, and ask one concise question only if the owner must decide. Never convert an illustrative example into a universal rule.

## 4. Recursive decision method

Decision work is a revisitable graph responsibility, not a fixed pre-production stage. Use it when a material uncertainty, repeated failure, creative fork, expensive commitment or architectural choice exists.

A material decision receipt contains:

1. the exact question and scope;
2. source references and their freshness/authority;
3. at least two competing root-cause or interpretation hypotheses;
4. a discriminating observation/test for each hypothesis;
5. at least two viable alternatives, with benefits, costs and counterevidence;
6. the selected option and why it fits the whole outcome;
7. a falsifier that would overturn the choice;
8. a rollback or recovery route.

Rechallenge the preferred solution and the research coverage before execution. New evidence may invalidate a downstream decision and reopen an upstream one. Do not repeat analysis without new evidence; do not stop while a material discriminator remains available.

## 5. Dynamic task graph, not a fixed production pipeline

The planner creates nodes around the work actually needed. A node declares:

- stable `task_id`, title and task kind;
- executor class (`agent`, `tool`, `human` or `external`);
- dependencies (`depends_on`);
- exact input artifact names;
- exact output artifact names;
- `requirements` such as capability, source, rights, model operation, cost or quality constraints;
- non-empty `acceptance` conditions;
- priority and bounded retry count.

The graph must be acyclic. Each output name has one producer. Independent nodes are eligible concurrently. A task with missing inputs waits; a task whose dependency fails or becomes stale is blocked. The engine does not force every project through research → script → storyboard → lookdev → generation → rough cut → sound → QA. Those are possible tasks only when the project needs them.

Typical parallel lanes may include:

- factual/editorial research;
- audience and competitor research;
- alternative creative concepts;
- visual reference and art-direction research;
- audio/voice/music research;
- tool/provider capability and cost checks;
- rights/product/likeness checks;
- cover and platform packaging.

Their outputs converge only where there is a real decision or production dependency.

## 6. Production strategy

Choose the medium per story beat or shot, not per project. Admissible methods may include real footage, licensed archive, image generation, video generation, image-to-video, 3D, procedural animation, kinetic typography, diagrams, code-driven graphics, compositing, practical photography, screen capture, NLE editing, generated voice, human narration, music, sound effects and deliberate silence.

A hybrid film may use different methods for different shots. The most expensive engine is not automatically best; the cheapest engine is not acceptable if it misses the required craft ceiling. Tool feature declarations are not proof of the exact operation combination, current availability, rights or output quality.

For high-risk creative assumptions, build a 3–12 second near-final sample or a small set of hero shots before full production. The sample should represent the final visual language, camera/motion, material quality, typography, sound and transition where relevant. A technical proof that a tool runs is not a quality proof.

## 7. Execution, leases and recovery

The runtime uses SQLite with WAL, foreign keys, busy timeout and `BEGIN IMMEDIATE` for task claims. Each worker receives a unique claim token and time-bounded lease. Heartbeats extend leases. Expired claims are recoverable within the task's retry budget. A worker whose token is no longer current cannot complete or overwrite the task.

The work packet contains only the declared task, acceptance contract, requirements and exact input artifacts/digests. Workers do not peer-chat as an authority mechanism; handoffs occur through artifacts and receipts.

A task completes only when all declared output names are supplied and each output is a real regular file inside the project workspace. The runtime computes SHA-256 and size itself. Registered artifact paths are immutable; a new take or revision gets a new path and version. Files outside the project must first be imported as source assets.

## 8. Asset, rights and provenance contract

Each asset has a stable ID, logical name, version, relative path, SHA-256, byte size, media type, kind, status, rights state, producer and metadata. Rights states include `OWNED`, `AUTHORIZED`, `LICENSED`, `PUBLIC_DOMAIN`, `UNKNOWN` and `NOT_APPLICABLE`.

`UNKNOWN` is allowed for exploration but blocks release when rights clearance is required. Source origin, permission, consent, likeness, product-truth, synthetic-content disclosure and licensing terms must be recorded as evidence, not inferred from the existence of a file.

An upstream change invalidates only the affected task and dependency descendants. Their prior files and event history remain for audit; unaffected work remains current.

## 9. Independent quality review and release

A review is bound to the exact artifact ID and SHA-256, reviewer identity, producer identity, rubric, dimensions, evidence references, outcome and notes. A producer cannot review its own artifact. A review on stale bytes cannot authorize the current artifact.

The runtime does not impose one global quality score. The brief selects relevant rubrics and may name every required final/package artifact and every source asset whose rights must be cleared. Conflicting PASS and FAIL reviews on the same exact artifact/rubric block release; a single PASS cannot erase a conflicting independent review. Typical rubrics include:

- editorial truth and source quality;
- argument/story clarity and retention;
- humor/naturalness/platform voice;
- visual craft, composition, motion and continuity;
- voice, music, sound design and mix;
- editing, pacing and transitions;
- technical playback/encoding/audio/subtitle QA;
- rights, likeness, provenance and disclosure;
- platform format and packaging.

The built-in FFmpeg/FFprobe adapter measures stream presence, stream-duration agreement, complete video/audio decode, black-frame segments and audio true peak. When the brief specifies them, it also checks duration range, resolution and frame rate. Subtitle geometry, caption safe-area compliance, integrated loudness, visual continuity and editorial craft require separate declared analyzers or human review; do not claim those checks ran unless their receipts exist. No technical tool proves that a film is compelling, funny, emotionally coherent or commercially effective. Human or genuinely independent multimodal review must inspect the actual media when the rubric requires it.

`release-check` verifies the exact current file digest, required independent PASS reviews, rights state and configured release evidence. It records acceptance evidence; it does not publish to a platform. Publication remains a separate authorized action.

## 10. Failure diagnosis and method repair

A material failure record contains the observed symptom, at least two competing root-cause hypotheses, discriminating tests, selected cause, a challenge to the previous method/diagnostic, repair plan, falsifier, rollback and evidence references.

Do not assume every failure needs another prompt, reviewer, role, gate or stage. Distinguish:

- local execution lapse;
- missing/incorrect source or requirement;
- capability/tool limitation;
- weak quality standard or benchmark;
- dependency/coordination defect;
- architecture defect;
- incorrect goal interpretation.

Repair at the causal layer supported by evidence. A failure cannot be marked resolved without independent verification and regression/replay references.

## 11. Learning and method promotion

Learning sources must be explicitly admitted and source-bound. A method candidate records the problem it solves, mechanism, evidence, applicability, counterexamples, failure conditions and replay references.

A candidate remains `CANDIDATE` until there is independent validation evidence and at least one counterexample trial. A successful single project or a model's self-rating does not establish a universal rule. Provider-specific knowledge expires faster than durable storytelling or production principles. Rejected approaches remain recorded with the reason they failed.

## 12. Hard release gates and provenance

The task graph is a scheduler, not the authority that decides whether a deliverable may be released. Release policy is declared in the owner brief and enforced against exact registered artifacts.

### Artifact lineage and source changes

When a task completes, the runtime records each declared input artifact ID and SHA-256 as an immutable `DERIVED_FROM` edge for every output. The lineage is recursive. The release check verifies all bytes and recorded parent digests. Re-importing a new version of an existing source name marks the prior version stale and invalidates every task that declared or consumed it, plus dependency descendants; old outputs and receipts remain historical evidence. Workers must reopen and regenerate affected tasks rather than reusing stale outputs.

### Rights and provenance

For public release, the final deliverable and every used media asset in its lineage must have one of `OWNED`, `AUTHORIZED`, `LICENSED` or `PUBLIC_DOMAIN`. `UNKNOWN` is fail-closed. By default, media artifacts also require non-empty `metadata.rights_evidence_refs`; each reference must resolve to a registered current artifact name/ID or an explicit HTTP(S) source URL. Briefs may name mandatory source assets and evidence artifacts. Required source assets must actually occur in the final artifact's recorded lineage, not merely exist elsewhere in the project.

The rights status field is a declaration backed by evidence, not an automatic legal opinion. Likeness, voice, music, font, stock footage, product truth, territory, duration, paid-media and derivative-use scope still require a competent human review.

### Technical media QA

A video artifact automatically requires a current technical QA receipt at release, even if the brief forgets to set `require_technical_qa`. A project can also explicitly require QA for a non-video output. The receipt must identify the exact target artifact ID and SHA-256, contain a recognized `ffmpeg-ffprobe-v1.0` checker identity, have `hard_pass=true`, no hard failures, and PASS for every mandatory check.

Mandatory checks are:

- `video_stream` — a video stream exists;
- `stream_duration_match` — measurable stream durations agree within the declared tolerance;
- `true_peak` — audio true peak is measured and stays within the configured ceiling;
- `black_frames` — black segments are detected and remain within the configured maximum;
- `full_decode` — FFmpeg can decode the complete selected video/audio streams without errors.

The brief may add mandatory checks such as duration range, resolution and frame rate; it cannot remove the five core checks. Missing FFmpeg/FFprobe, timeout, malformed reports, unavailable measurements or digest mismatch block release. The QA adapter does not certify editorial truth, craft, rights, continuity or audience response.

### Independent reviews and Red Team

A review is bound to the exact artifact digest and must not be written by its producer. A brief can require reviewer kind, execution mode, blind review, inspected digest, context ID, score floors and reviewer quorum. Human cold-read contracts require `reviewer_kind=HUMAN`, `execution_mode=INDEPENDENT_COLD_READ`, `blind_review=true`, a matching inspected digest and a context ID.

The Red Team contract can require at least three concrete findings. Each finding must contain a description, evidence reference, severity and disposition. When `require_resolvable_evidence_refs` is enabled, both review-level evidence refs and every finding's evidence ref must resolve to a current registered artifact ID/name; a free-form URI is not accepted as proof. A PASS with unresolved CRITICAL/HIGH findings is rejected. Findings are not decorative checklist entries; unresolved material risks block release.

These reviewer attributes are recorded as attestations. The runtime can validate their structure and consistency but cannot cryptographically prove that a named person actually performed the review or remained blind to other verdicts. Do not describe self-attested metadata as cryptographic independence.

### Evidence and publication boundary

`required_evidence_artifact_names` requires registered, current, digest-verified artifacts of an allowed evidence/document/report/decision/timeline/domain-state kind. `required_artifact_names` requires every declared deliverable. `required_asset_names` requires source assets to be in final lineage and rights-cleared. String-only `required_evidence_refs` remain compatibility references; use artifact names/IDs for evidence that must be machine-verified.

A successful release check marks the exact artifact ACCEPTED; it does not upload, publish, schedule or spend money. Publication remains a separate owner-authorized action. The CLI's `--allow-unknown-rights` compatibility switch cannot override a hard requirement in the owner brief.

### Review and QA CLI

Review dimensions and scores are supplied as JSON. Independence metadata is supplied separately:

```bash
vga-studio review PROJECT ARTIFACT_ID \
  --reviewer human-reviewer-01 --rubric human-cold-read --outcome PASS \
  --dimensions review-scores.json --attestation review-attestation.json \
  --evidence frame://00:00:02 --notes "Blind cold read of exact final digest"
```

The attestation JSON should identify `reviewer_kind`, `execution_mode`, `blind_review`, `inspected_artifact_digest` and `context_id`. Red Team review dimensions should include a `findings` array with at least three evidence-backed findings when the brief requires it.

## 13. Operational commands

### 13.1 Import digest-bound Program context

A task's `requirements.authority_refs` are descriptive references, not automatically verified inputs. When a worker must rely on a repository document or source file, import it as a Studio artifact and declare its artifact name in the task's `inputs`. The engine then binds the exact artifact ID, version and SHA-256 at claim time and verifies the same bytes at completion.

`import-manifest` preflights every listed file before importing any of them. Relative `path` values resolve from the manifest's directory. Re-importing identical bytes with identical type, rights and metadata is a no-op; a changed source or metadata creates a new immutable version and invalidates its consumers.

```bash
vga-studio --root ./studio-work init ai-self-media-commercialization --title "AI Self-Media Commercialization" --brief examples/ai-self-media-commercialization.brief.json
vga-studio --root ./studio-work import-manifest ai-self-media-commercialization examples/ai-self-media-commercialization.context.json
vga-studio --root ./studio-work plan ai-self-media-commercialization examples/ai-self-media-commercialization.tasks.json
vga-studio --root ./studio-work status ai-self-media-commercialization

# audit the repository contract without relying on the legacy vga controller
vga-studio system-audit --repo-root .
```

The standalone repository audit reports structural integrity separately from production readiness. A structural PASS does not imply provider generation, a finished media deliverable or owner approvals have been completed.

The context manifest imports only existing Video/IPOS state and reference documents. It deliberately does not invent or import the missing `jensen-source-video` or `ipos-ready-for-video-bundle`; dependent tasks remain `WAITING_INPUT` while independent Program work can proceed. The legacy subtask graph is labelled as historical context, not as the active scheduler.

### 13.2 Episode-specific example

```bash
# create a project from an outcome brief
vga-studio --root ./studio-work init episode-001 --title "Episode 001" --brief examples/technology-explainer.brief.json

# create a dynamic dependency graph
vga-studio --root ./studio-work plan episode-001 examples/technology-explainer.tasks.json

# inspect ready/blocked work
vga-studio --root ./studio-work status episode-001
vga-studio --root ./studio-work tasks episode-001

# atomically claim the next ready task
vga-studio --root ./studio-work claim episode-001 --worker researcher-01 --lease-seconds 900

# record an artifact-bound independent review
vga-studio --root ./studio-work review episode-001 ARTIFACT_ID --reviewer reviewer-01 --rubric craft --outcome PASS --dimensions review-dimensions.json --evidence frame://01 --evidence frame://02

# inspect current state and durable event history
vga-studio --root ./studio-work audit episode-001
vga-studio --root ./studio-work events episode-001
```

`vga-studio --help` lists brief revision/history, task-contract revision, claim heartbeat, complete, fail, wait-input, decision, failure, resolve-failure, invalidate, reopen, learn and release-check commands. `qa-media` runs the built-in FFmpeg/FFprobe measurement adapter against a claimed `technical_measurement` task, writes a digest-bound QA receipt and completes that measurement task. It checks technical properties only; it cannot approve craft, truth, rights or release.

`run-adapter` executes a task's declared `requirements.domain_adapter` against its registered inputs and completes the task with immutable output artifacts. Example task requirement:

```json
{
  "domain_adapter": {
    "name": "programmatic_graphic_render",
    "editorial_plan_input": "editorial-plan",
    "shot_contract_input": "shot-contract",
    "graphic_spec_input": "graphic-spec",
    "font_input": "font-asset",
    "rights_evidence_input": "rights-clearance",
    "video_output": "graphic-candidate",
    "receipt_output": "graphic-render-receipt"
  }
}
```

Run it only after claiming the task:

```bash
vga-studio run-adapter PROJECT TASK_ID --worker local-renderer --token CLAIM_TOKEN
```

The adapter verifies the ShotContract against the exact EditorialPlan, requires the font and rights evidence as declared inputs, and emits a candidate plus receipt. It does not promote the asset. A later `qa-media` task must bind canonical FFmpeg/FFprobe QA to the registered candidate artifact ID and digest.


### Standalone adapter proof

The repository includes `examples/standalone-domain-adapters.brief.json` and `examples/standalone-domain-adapters.tasks.json`. They demonstrate a real, deterministic local render rather than a mocked task completion:

1. An agent authors an EditorialPlan and GraphicSpec.
2. The `editorial_plan_validate` adapter validates claims, beats and shots.
3. The `shot_contract_materialize` adapter derives a ShotContract from the exact plan.
4. The `programmatic_graphic_render` adapter checks the plan binding, font input and rights evidence, then writes a silent MP4 candidate and render receipt.
5. The `qa-media` command runs the canonical digest-bound FFmpeg/FFprobe checks against that registered candidate.

Import a licensed font and its rights evidence before claiming the renderer task:

```bash
vga-studio --root ./studio-work init adapter-demo --title "Standalone adapter demo" --brief examples/standalone-domain-adapters.brief.json
vga-studio --root ./studio-work plan adapter-demo examples/standalone-domain-adapters.tasks.json
vga-studio --root ./studio-work import-asset adapter-demo rights-clearance ./font-license-evidence.txt --kind document --media-type text/plain --rights-status OWNED
vga-studio --root ./studio-work import-asset adapter-demo font-asset ./DejaVuSans.ttf --kind font --media-type font/ttf --rights-status LICENSED --metadata examples/adapter-demo-font.metadata.json
```

The example is an adapter integration proof, not a claim that a title card alone is a finished film or that external generative-video providers are connected.

## 14. Migration and compatibility

The existing `vga` CLI and 0.8 Media Business OS remain available for historical Pilot recovery and proven specialized capabilities. They are not the new Studio's controller or task graph. Reuse old modules only through explicit adapters after verifying their current behavior, compatibility, real outputs and failure cases. Do not migrate old fixed stage order or role assignments merely because they exist.

## 15. Known limits of this first standalone runtime

The core supplies durable project governance, DAG scheduling, worker leases, artifact identity, review evidence, failure records and learning admission. It does not itself contain a universal LLM, image/video generation model, NLE, music library or paid provider credential. Nor does the core itself implement every business-domain object; the Skill coordinates those domain capabilities through explicit adapters and evidence-bound artifacts. The active worker must use the actual available media tools/provider adapters, report capability gaps honestly, and return files into the project workspace. The absence of a provider blocks only the affected operation or triggers an explicitly accepted degradation path; it never fabricates media output.

This boundary is intentional: the orchestration core remains provider-neutral and independently operable instead of pretending a generic task scheduler can create cinematic video by itself.