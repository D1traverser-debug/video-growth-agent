# Pilot 002 — Sample 01 Execution Log

Status: ACTIVE / NOT PASSED  
Date: 2026-10-09  
Stage: LOOKDEV / near-final VISUAL_PREVIEW prototype

## Objective

Produce a 5–12 second near-final sample that tests the hardest foreground-human/app → background-agent/service-world transition before any 59.5-second full rebuild.

Authoritative shot contract: `projects/pilot-002/SAMPLE_01_SHOT_CONTRACT.md`.

## Work completed

1. Locked target format from historical release evidence: 1080×1920, 30 fps, vertical 9:16.
2. Selected the high-risk narrative interval corresponding to the prior 15.76–25.98 s section: manual mail/file/data/PPT work → Agent hides steps in the background → user delegates outcome.
3. Wrote a new audiovisual shot contract that intentionally breaks V4's premium-UI/motion-board failure mode.
4. Identified a suitable licensed stock reference for the opening human-scale shot: Pexels video 7551959, vertical close-up of hands typing on a laptop, free-use page metadata.
5. Created Descript project `Pilot 002 — Sample 01 — Agent World Transition`.
6. Descript imported a licensed stock clip `Woman typing on keyboard close up` and created composition `Agent Delegation Explainer - 9x16 Sample` at 1080×1920 / 30 fps.
7. First Descript pass stopped at a decision request rather than building; studio autonomously chose the semantically correct desk-work stock route and rejected unrelated hand/berries footage.
8. Native Descript Mandarin TTS made the historical wording 15.6 s, exceeding the hard 3–12 s preview limit. The studio refused to loosen the preview gate and approved a sample-only compressed line preserving the mechanism:
   `以前你要找邮件、拉表、做PPT。Agent把步骤藏到后台。你只说：把它准备好。`
9. Subsequent Agent Underlord execution failed because the connected Descript account had insufficient AI credits. No upgrade/purchase was authorized or attempted.
10. A private Descript QA render was produced from the partially changed 10.4 s composition for inspection only; it is not publication authority and is not a release candidate.

## Descript project evidence

- project_id: `36a6b665-dba9-4db9-b51f-a07837fdb03c`
- project URL: `https://web.descript.com/36a6b665-dba9-4db9-b51f-a07837fdb03c`
- target composition_id: `5e435387-4436-4b00-ab64-221e130716f4`
- composition name: `Agent Delegation Explainer - 9x16 Sample`
- reported composition duration after partial execution: 10.4 s
- private QA share URL: `https://share.descript.com/view/l1TYMG4A4c8`
- stock media present in project: `Stock Media/Woman typing on keyboard close up`, duration 12.72 s
- AI-credit failure: `Insufficient AI credits to complete the request`

## Fail-closed QA result

**NO PASS.**

The current runtime could not retrieve the private rendered MP4 pixels for frame/contact-sheet inspection:
- the Descript connector returned a signed download URL, but the current container download bridge would not accept the connector-returned URL without web visibility;
- web retrieval could not open the Descript media/share URL;
- Opera Browser Connector was unavailable because the browser connection was not enabled.

Therefore the studio cannot satisfy the mandatory real-render loop (`RENDER → EXTRACT FRAMES → VISUAL INSPECT → AUDIO INSPECT → TECH PROBE → FIX → RERENDER → RECHECK`). A Descript agent response, project duration, or private share link is not visual-quality evidence.

The partially rendered Descript composition must be treated as `UNREVIEWED_INCOMPLETE`, not as a visual-preview candidate that passed or failed on aesthetics.

## Cost / tool-routing lesson

For this account/runtime, Descript Agent Underlord is not currently a reliable primary production engine for autonomous low-cost visual-preview builds because:
- AI credits can stop execution mid-build;
- a project can be partially changed despite an agent error;
- private render pixels may not be retrievable into the QA runtime even when a share/download URL exists.

Use Descript only when the available credits and media-return path are verified before quality-critical work. Do not purchase/upgrade merely to preserve a tool choice.

## Current next action

Keep the full 59.5-second build frozen.

Produce Sample 01 through a **no-new-spend, inspectable production path** where the final MP4 can be consumed by the QA runtime. Preserve the same shot contract and benchmark gate. Preferred order:

1. reuse already-authorized human/work footage only if its bytes can be obtained into the production runtime;
2. otherwise use another connected production surface that can return/export inspectable media without new payment;
3. render the 10.22 s vertical sample with representative sound;
4. extract frames/contact sheet and inspect normal-speed playback;
5. score every hard VISUAL_PREVIEW dimension; any score <4 remains FAIL;
6. only after a genuine PASS promote the technique and expand the film.

Do not ask the user to upgrade Descript as a prerequisite. Tool choice must remain replaceable.
