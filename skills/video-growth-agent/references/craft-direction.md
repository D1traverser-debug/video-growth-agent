# Craft Direction — evidence-driven film-making Skill (candidate)

**Scope:** This reference belongs to the existing Video domain. It does not create another controller, stage gate, project state, or canonical timeline. A creative storyboard must bind an immutable `editorial-plan://episode@version` before generation. Existing MediaGraph, Continuity, Timeline, rights, promotion and release decisions retain authority.

## 1. Study and select methods — do not fix one house style

For every non-trivial creative request, compare at least:
1. **Continuous cinematic blocking** — one changing physical situation, readable action and actor reaction; useful for 5 s emotional moments, simple hands/face/props.
2. **Match-cut montage / audiovisual identity reveal** — image/action/sound geometry binds otherwise unrelated worlds; good for an IP bumper, visual surprise and editing display.
3. **Storyboard-first multi-shot narrative** — preserve causality, spatial continuity and required story events across compressed run time; especially useful when a user demands no lost plot information.

Possible styles (document candidates before choosing): live-action cinematic, 2D/3D anime, painterly 3A CG, Y2K, cyberpunk, clay, stop-motion, film-grain realism, cosmic opera, surreal studio advertising. Style is an independent design choice, **not** a direct implication of trading/AI interests. Do not assign generic theme colors to financial/crypto brands in lieu of representative physical/motion details.

Produce an explicit one-sentence thesis, emotion/tension transformation, viewing context, signature mnemonic, references, reject reasons for alternatives, and the reason the chosen mode best serves *this* outcome.

## 2. Professional artifact handoffs

| Craft owner | Input | Output that another craft can actually execute | Verification |
| --- | --- | --- | --- |
| Showrunner/writer | audience/intent/claim constraints | story premise, event inventory, emotional turn, payoff | cold viewer can retell arc |
| Director | premise, constraints | beat/shot progression, actor blocking, screen direction, spatial and temporal logic | causal event progression |
| Cinematographer | blocking/art world | lens, shot size, camera path, focus, light motivation, exposure/contrast priorities | no contradictory simultaneous camera commands |
| Art/production designer | premise/refs | visual bible: shapes, materials, props, costumes, spatial grammar | repeatable anchor references |
| Motion/VFX designer | blocking, edit geometry | object origin, trajectory, contact, acceleration, material change, exit and transition masks | effect has trigger and legible outcome |
| Editor | shots and audio map | frame-indexed cut/hold structure, match point, screen axis, L/J cuts as appropriate | action continuity and exact run time |
| Sound director | emotional beat, cut map | dialogue/foley/music/ambience/silence cues with durations, stems and rights | synchronised sound after actual assembly |
| Producer | budget/provider evidence | routing candidates, asset plan, rights and verification plan | spend tied to highest-risk uncertainty |
| QA/review | actual rendered media | per-shot timecode findings, frame references, evidence | NEVER infer success from prompts alone |

Use `vga storyboard SPEC.json --route onepass|shotwise|compare` for structural frame/event checks and platform prompt compilation. `verify_editorial_binding(spec, editorial_plan)` is a separate typed audit of the real EditorialPlan version and all required beat IDs; declaring `source_plan_ref` alone is NOT upstream verification. The tool cannot create a movie, infer high artistic quality, prove story semantics, or attest provider execution.

### Frame accounting

Use integer frame offsets, half-open intervals `[start_frame, end_frame)`, positive fps and exact coverage of 0..total_frames; timecode decimal rendering is presentation only. Map every explicit required narrative event to at least one shot. This **proves planned coverage only**: a 10-second output may still be visually unreadable. Check event density, edit count, legibility and viewer comprehension independently.

### Prompt structure

Write literal **subject + observable geometry/material + triggering action + path and result + environment + light + camera + sound + transition + carryover**. Never use only adjective piles, ungrounded financial iconography, simultaneous incompatible camera commands or unverified optical claims.

For 5s: favor one coherent act and one strong payoff. For 10s with many events: storyboard and montage rather than pretending a slow emotional hold can be preserved at 3x compression.

## 3. Compare execution routes: no fake winner

| Route | Strength | Expected failure | Use when |
| --- | --- | --- | --- |
| ONEPASS native multi-shot | quick coherent experimental draft, potentially native sound | rapid many-object scenes may skip actions and violate shot duration | low-density preliminary concept |
| SHOTWISE separately generated + editorial timeline | localized repair and explicit shot/cue control | reference drift and handoff workload | high event count, strict re-tying/handoff, complex match cuts |
| ANCHOR-FIRST reference/keyframe generation + shotwise edit | repeatable faces, props, entry/exit topology | higher initial asset effort, not always worth it for disposable tests | hero IP/brand critical continuity |

Each selected route must record: exact model/version/operation, documented prompt and duration limits, seed where supported, reference role, actual credits/cost, licenses, output digest, required storyboard events, quality failures and follow-up changes. A provider official page proves capabilities/limits, not studio quality superiority. Do not spend credits or make live media-generation calls without budget admission.

### Empirical comparison protocol
- Use a fixed source plan plus two different content cases: **5-second Shiba editor IP** and **10-second red-ribbon romantic montage** (`tests/fixtures/`).
- Compare basic deterministic measures: exact frame coverage, missing required events, invalid transitions/shot specifications and provider prompt length.
- Then, *only after actual authorized render*, blind-evaluate readability, physical interaction, entity continuity, shot/cue accuracy, audio sync, artifact counts, accepted seconds and retry spend with frame-indexed evidence.
- Promote a route only after observed wins across more than one scene type. Structural tests are not independent artistic adjudicators.

## 4. Tool/provider learning: external sources and transfer boundaries

- [PixVerse V6 guide](https://docs.pixverse.ai/PixVerse-V6-User-Guide-3373e99bf35080dfa9d8c44f30fde3bc) — authoritative for native 1–15s, multi-shot, supported aspect/resolution and PixVerse *web* 5,000-character input. Do not conflate with a third-party hosted endpoint that caps bytes differently.
- [PixVerse V6 prompt practice](https://pixverse.ai/en/blog/pixverse-v6-ai-video-generator-review) — concrete camera/subject/action/light/sound guidance and record-retry logic. Vendor testing does not independently certify comparative aesthetic scores.
- [Adobe match cut](https://www.adobe.com/creativecloud/video/discover/match-cut.html) — graphic/action/audio match types, repeatable visual grammar; evaluate geometric alignment at the actual edit point.
- [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) — professional editor-neutral timeline interchange; existing `timeline.py` and `editorial_interchange.py` remain canonical, OTIO should be evaluated only as an adapter.
- [Netflix delivery QC](https://studiopartner.netflix.net/studio/backlot-imf-delivery) — useful model for separating media existence, technical conform, and acceptance; NOT a claim this studio meets Netflix delivery standard.
- Existing local `production-intelligence.md` includes DramaClaw, Toonflow, MiniMax H3, Utopai and BigBanana methods. Each remains candidate methodology until tested here; do not copy entire external architectures.

## 5. Rejection/learning loop

Record `hypothesis -> competing method -> source + mechanism -> controlled scene fixture -> generated artifact evidence -> independent blinded QA -> accepted/rejected route -> regression test`. Human/LLM-only review should be labelled as such and must never masquerade as isolated verification.

Fail or request revision when:
- story events disappear from a compressed plan;
- the story can only be understood from narration, but the brief requires silent comprehension;
- a key prop teleports / changes identity or exits inconsistently;
- editing relies on generic white flashes rather than a motivated visual/audio correspondence;
- voice/text accuracy or downbeat sync is asserted without post-production evidence;
- the system reports creative quality PASS using only its own prompt or role checklist.

Research depth escalates with novelty, ambiguity and production cost. No single style, vendor or Skill controls all creative decisions.
