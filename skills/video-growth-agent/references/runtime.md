# Runtime and Evidence Contract

The runtime exists to stop a persuasive agent from talking its way around missing work.

## Project checkpoint
Each active project has a durable `state.json` containing current stage, role approvals, artifact references, asset provenance, QA receipts and revision number. State writes are atomic. Important actions also create immutable receipt files and an append-only event log.

## Three-part gate
A stage advances only when all three are true: required artifacts exist, every required professional role records PASS, and deterministic machine guards pass. Human approval cannot override a failed deterministic guard.

## Artifact invalidation
When an already-recorded upstream artifact materially changes, approvals from that production stage and all downstream stages are deleted. The project returns to the affected stage. Never preserve stale approvals merely because a later cut already exists.

## Review receipts
Role reviews record decision, notes, evidence references, findings and UTC timestamp. A reviewer can only sign a stage where that role is required. At `RED_TEAM`, PASS must contain at least three explicit objections/findings.

## Asset provenance
Every final-used external asset has a rights state: `OWNED`, `AUTHORIZED`, `LICENSED`, `PUBLIC_DOMAIN` or `UNKNOWN`. `UNKNOWN` is permitted during exploration but blocks RELEASE when the asset remains in the final cut.

## Media QA
`MediaQAChecker` uses real FFmpeg/ffprobe output. A valid editor timeline or playable MP4 container is not enough. The machine guard trusts only an immutable `MEDIA_QA` receipt created by the Runtime; manually writing a `technical_qa` artifact cannot forge PASS.

QA is bound to the exact media URI. `TECH_QA` requires a hard-pass receipt for the current `final_candidate`; `RELEASE` requires a hard-pass receipt for the actual `final_media`. If the final candidate is transcoded, upscaled, remuxed or has audio replaced, QA must run again on the resulting file.

Long silence is a warning, not automatically a failure, because deliberate silence may be part of sound direction. Long black segments, missing audio when required, stream mismatch, unreadable metering or unsafe true peak are hard technical defects.

## Binary artifacts
Large media may live in the conversation Library, Drive or other project storage. GitHub stores stable references, digests, QA receipts and source/provenance metadata. Never invent a path to a binary that was not actually persisted.
