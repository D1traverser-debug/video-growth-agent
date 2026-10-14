---
name: video-growth-agent-uaos
scope: AI video production, growth systems, original digital-IP incubation and media QA
---

# Video Growth Agent — Current UAOS Entry

Controller: `D1traverser-debug/universal-agent-os@main`.
Domain repository: `D1traverser-debug/video-growth-agent@main`.

UAOS owns task/project routing, requirements, cross-chat continuation and controller action lineage. This repository owns video/domain runtime code, media rules, project-local design truth, shot/work-order evidence and production artifacts.

## Start
After UAOS resolves the exact task/project, read:
1. `.uaos/ADAPTER.json`;
2. `.uaos/MANIFEST.json`;
3. `.uaos/CAPABILITIES.json`;
4. the selected project `PROJECT_MANIFEST.json` / current progress / decision artifacts;
5. only the references/runtime files required by the current action.

Do not infer current project from repository search or old continuity task files. Project-local manifests are business truth; UAOS is controller truth.

## Current project isolation
`projects/ai-self-media-commercialization` is an independent original-digital-IP incubation project. It must not be merged with Pilot 001/002 or the older `video-growth:main` program unless the user explicitly requests such an import.

Always reread the selected project's current manifest immediately before material work. Do not copy a cached next action into a new session and assume it is still current.

## Generation and QA
Quality-critical generation is fail-closed. Prompts, role labels and configured adapters are not execution proof. Image/video review claims require actual modality access and evidence bound to the produced artifact identity.

Asset continuity is explicit: character, wardrobe, scene, prop, style, light, action and shot-state changes must bind to versioned project assets/work orders rather than prompt memory.

Exploration/candidate outputs do not overwrite production/current assets until accepted. Rejected/process-invalid media must never silently return as accepted progress.

## Cost and providers
Use included/free current-session capabilities first when they meet the quality/permission floor. Paid or unknown-cost providers require explicit authorization. Missing hard capability blocks only the affected work unit; never fabricate generation/review.

## Learning
A successful/failing shot or project creates evidence/candidates. Promote durable production rules only after appropriate replay/cross-case evidence; avoid one-example overfitting.

## Completion
Completion requires UAOS task/action evidence plus current project/media artifact verification. Do not create a parallel controller, task registry, lease, resume epoch or cross-chat continuation protocol in this repository.
