# Production and Cost Strategy — V3

Status: `MEDIA_BUSINESS_OS_0_8_RELEASE_CANDIDATE__0_7_PRODUCTION_BASELINE`
Owner: `DOMAIN:video`
Architecture: `docs/media_business_os.md`
Agent-operability scenarios: `docs/agent_operability_scenarios.md`
Benchmark method: `docs/provider_benchmark_protocol.md`

## Objective

Maximize **published audience/business value per unit of cash and creator attention** while protecting editorial truth, audiovisual quality, distinctive IP and reusable rights.

The objective is not to maximize AI-video percentage, cheapest generated seconds, one quality scalar or cinematic spectacle.

The account is an AI-native technology-business media product. AI is the studio/infrastructure; the audience proposition is explanation, story, mechanisms, distinctive IP and trustworthy production.

## 1. Value-aware production allocation

Do not freeze a permanent percentage of premium video / ordinary I2V / still motion / graphics.

For every shot, choose from the admissible mode set:

- verified real/editorial/product asset;
- premium video generation;
- ordinary video generation;
- video modify/edit/extend;
- image generation + I2V;
- still + camera/parallax/local motion;
- programmatic motion graphics/diagram/typography;
- reusable environment/IP asset;
- archive/licensed asset;
- hybrid composite.

Allocation is driven by:

1. narrative/explanatory job inherited from the exact EditorialPlan/Beat/ShotIntent;
2. risk/truth class;
3. identity/continuity need;
4. expected audience/IP/commercial leverage;
5. measured provider acceptance/retry rate for this shot archetype;
6. editability/reuse;
7. current cost/latency;
8. rights/provenance constraints.

A prior rough range may be used as a planning prior when no project evidence exists, but it is not production doctrine.

## 2. Shot investment classes

### HERO / signature
Use top admissible production resources when the shot materially drives:
- opening stop-rate/retention promise;
- major reveal/payoff;
- distinctive IP/series memory;
- impossible/invisible mechanism visualization;
- sponsor-defining hero moment;
- signature transition/world-building asset with high reuse value.

Hero does not mean "always use the most expensive model". A verified real product macro, programmatic simulation or reusable 3D/graphic asset can be the correct hero route.

### CORE narrative
Use the lowest expected accepted-take cost among routes that repeatedly clear all hard constraints and the shot-specific quality vector. Favor editable/reusable assets over one-off spectacle when audience value is equivalent.

### SUPPORT / bridge
Prefer still-motion, graphics, archive, reusable environments, crop/reframe, edit/extend or low-cost generation. Support shots should not consume hero retry budgets by default.

### INFORMATION / truth
Prefer diagrams, charts, labels, code/system schematics, verified product media and source-bound graphics when they communicate more accurately than synthetic cinema.

## 3. Exploration vs production economics

### Exploration

Goal: reduce uncertainty cheaply.

- low resolution/keyframes/stills/short takes encouraged;
- cheapest sufficient current engine after hard rights/capability/operation-profile gates;
- no release-grade reviewer requirement merely to create a candidate;
- strict retry/credit ceilings;
- outputs remain candidate-only.

### Production

Goal: produce promotable takes.

- quality/continuity/truth first after hard constraints;
- compare only evidence that is sufficiently compatible in rubric/calibration scope;
- apply uncertainty-aware floors before ranking;
- keep the non-dominated/Pareto set when models trade quality dimensions rather than hiding the tradeoff in one weighted average;
- use explicit shot priorities to resolve remaining tradeoffs;
- calculate cost per **accepted** take, not only provider cost per second;
- retries create new takes and accumulate cost/waste evidence.

### Release

Goal: minimize expensive downstream failure.

- no unresolved rights/product-truth/provenance/disclosure gap;
- final technical QA;
- platform deliverable validation;
- explicit release owner.

## 4. Model/provider strategy

Never hard-code a vendor as the permanent default.

Provider/model observations are dated and evidence-bound. Current external model capabilities justify fields in the registry but not permanent quality rankings.

Use `model_registry.py` + the owner benchmark protocol to compare:

- operation-specific generation/edit/reference modes and legal combinations;
- identity/continuity quality;
- motion/physics;
- prompt/shot adherence;
- camera execution;
- audio;
- editability/extension;
- reference fidelity;
- duration/resolution;
- current API/session availability;
- cost and latency;
- commercial-use/terms/provenance;
- deprecation risk.

A provider feature list is not a Cartesian-product capability guarantee. Reference count, source type, resolution, duration, extension and audio constraints travel with the relevant operation profile.

Provider lifecycle is a first-class risk. A discontinued provider never forces a business-architecture rewrite.

## 5. Reference, continuity and asset strategy

The highest leverage cost reduction is often **asset reuse and controlled editing**, not a cheaper fresh generation.

Build reusable:

- character canon/reference views;
- wardrobe/prop/environment packs;
- visual motif/style assets;
- diagrams/system components;
- intro/outro/transition families;
- voice/audio identity;
- sound motifs;
- verified sponsor/product assets;
- platform-safe layout/caption systems.

Every reuse keeps exact version/rights lineage. Cross-shot continuity is dimension-level state with explicit preserve/expect/allow-change semantics rather than prompt memory.

When a generated take is close, prefer a controlled edit/modify/extend/local repair when the provider/tool supports the exact operation and the expected acceptance cost is lower than regeneration.

## 6. Editorial-plan change cost

Production begins from a versioned EditorialPlan rather than hidden Agent memory. Material claim/beat/shot changes create a new plan version. The old plan asset remains historical, and the MediaGraph invalidates only descendants that actually consumed the superseded version.

Track downstream waste caused by upstream changes separately from ordinary generation rejection. Do not re-render unaffected shots merely because one beat changed.

## 7. Cost accounting

Track by episode, sequence, shot, provider and asset:

### Cash/compute
- image generations;
- video generation seconds;
- input/reference charges;
- retries/rejected takes;
- edit/modify/extend operations;
- upscale/interpolation;
- voice/audio/music/SFX;
- research/LLM cost where material;
- editor/render/storage/service cost.

### Human time
- research/fact review;
- script/story review;
- shot/reference planning;
- candidate selection;
- IP/lookdev approval;
- edit/sound review;
- commercial/rights review;
- final QA.

### Waste
- rejected attempts;
- superseded shots;
- downstream work invalidated by upstream changes;
- unused paid capacity;
- abandoned sponsor deliverables;
- unreusable one-off assets.

## 8. Core economics metrics

At minimum:

- cost per accepted generated take;
- rejection/retry rate by provider × operation profile × shot archetype;
- cash cost per published minute;
- creator minutes per published minute;
- premium-generation seconds per published minute;
- reusable-asset use rate;
- marginal cost per platform derivative;
- production latency per accepted minute;
- sponsor production uplift;
- episode commercial gross margin where applicable;
- rights/licensing revenue separately;
- repeat-buy signal.

Do not collapse these into one permanent score.

## 9. Product-truth and sponsor mode

When exact physical sponsor/product truth matters:

- use verified real/authorized product imagery/footage or explicit brand sources for appearance, UI, materials, dimensions/configuration and demonstrated behavior;
- AI may build the surrounding world, explain invisible mechanisms or create clearly framed hypothetical/future scenes;
- synthetic material must not impersonate factual product evidence;
- commercial deliverables bind rights, usage duration, territory, paid-media/whitelisting/cutdown permissions and exclusivity where relevant.

## 10. Resolution and master strategy

Do not default every source operation to native 4K.

Choose generation resolution by expected delivered value and provider acceptance economics. Maintain a canonical master timeline/output policy (normally platform-appropriate 1080-class delivery unless a specific release/shot requires more) and upscale selectively.

High resolution is not a substitute for temporal consistency, identity, good edit or truthful visual explanation.

## 11. Audio economics

Audio is not an afterthought. Scene-level generated audio can reduce assembly work, but reusable voice/music/rights-critical components may be independently versioned.

Track:
- voice generation/repair cost;
- audio-scene generation;
- music/SFX cost and licensing;
- localization cost;
- human mix/review time;
- regeneration due to timing/performance failures.

## 12. External editor roundtrip

The canonical timeline remains internal owner state even when Descript, Premiere, DaVinci, Final Cut or another editor performs an edit.

A handoff binds the exact timeline version and asset digests plus the external project/composition identity. Returned work needs an execution receipt/change summary and becomes a new derived timeline/artifact state; the external editor does not silently replace canonical truth.

Track marginal external-editor time/cost and avoid manual reassembly where a verified interchange/roundtrip path exists.

## 13. Platform derivatives and experiments

Budget platform variants as transforms of one master asset/story graph:

- Bilibili long-form master;
- Douyin/Channels/XHS re-authored short variants;
- localized YouTube/other variants when strategically justified.

Measure marginal derivative cost and incremental audience/commercial value. Stop producing a derivative if repeated evidence shows poor marginal value.

Where causal learning matters, pre-register variant identities, changed/fixed variables, primary metric semantics, guardrails and stop/observation rules. Treat `NO_CLEAR_WINNER` and `INCONCLUSIVE` as legitimate outcomes. A multivariable packaging test must not be retrospectively narrated as proof of one changed variable.

## 14. Portfolio-level investment

Episode budgets compete across a portfolio. Premium capacity should follow expected information/story leverage, distinctive-IP value, audience potential, sponsor value and reusable asset creation.

A visually expensive episode can be rational if it creates durable series/IP assets; a cheap viral post can be strategically weak if it attracts the wrong audience and creates no reusable value.

## 15. Learning loop

After every formal episode or material production batch:

1. ingest platform receipts;
2. ingest production economics/retry evidence;
3. ingest IP/recognition qualitative or experiment evidence;
4. ingest commercial outcomes if present;
5. compare against the pre-production hypotheses;
6. create scoped learning candidates;
7. test/replay before changing durable domain rules.

Provider-specific lessons expire faster than storytelling/business mechanisms.

## 16. Human gates

Long-term preferred creator gates remain few and high leverage:

1. portfolio/topic commitment where strategic;
2. script/claim truth for material pieces;
3. core IP/look/hero-shot promotion where distinctive assets are at stake;
4. sponsor/product-truth/rights approval where applicable;
5. final release.

Everything else is an automation candidate only after quality and recovery can be measured.

## 17. Stop conditions

A shot or method stops consuming budget when:

- its configured retry/credit/time ceiling is reached;
- repeated attempts fail the same quality dimension without a changed mechanism;
- a lower-cost graceful-degradation route achieves the narrative job;
- upstream story/claim/asset truth changes and invalidates the shot;
- provider evidence becomes stale/unavailable/deprecated;
- marginal audience/business value no longer justifies the production complexity.
