# Red Silk Date — Production Status v11

Updated: 2026-11-12 migration snapshot
Latest known full engineering baseline: v11 (2026-11-05)
Status: ACTIVE_BLOCKED; not a finished video.

## 1. Frozen creative target
- 10 seconds, 16:9, 30fps, 300 frames.
- Seven production shots must preserve all ten one-second story beats.
- One continuous red ribbon is the central narrative state carrier.
- Male/female identity, hair, wardrobe, environment and ribbon topology must remain consistent.
- No static image push/pull, slideshow, PPT-like montage or editing trick that hides missing physical interaction.
- Original brief asks for 8K-class visual quality. The v11 production system defines 1920×1080 as the initial master; evaluate 4K only after the 1080p quality gate. Do not claim native 8K from upscaling.

## 2. Latest v11 engineering decisions
- Blender 5.2.3 LTS is the main DCC.
- Ribbon physics is behind an independent Solver Adapter.
- XPBD v15 is the preferred development route.
- Houdini Vellum is a gated professional upgrade, not the default. Confirm the relevant gate failure, Indie eligibility and cost, then obtain explicit user approval.
- UE 5.8 Chaos is the second fallback and must be compared on the same shot.
- AI video does not own critical character identity or ribbon physical state. AI 3D may supply base-mesh candidates only.
- User-local machine is not a compute node. Use cloud Runtime/Worker; any paid compute or third-party upload requires explicit approval.

## 3. The v14 false-positive root cause
The old 15/15 QA did not establish dynamic capture:
- the free-end ribbon vertices were overwritten by a preset tip trajectory each substep;
- the root endpoint was also kinematically clamped;
- after capture, tip path was constructed from the hand path, making near-zero grip error tautological;
- hand collision projection excluded the end row;
- QA checked preset path equality/near-distance, not a solver-generated contact event.

Therefore v14 is retained as a kinematic cloth-shape reference. It is not deleted, but it is not promoted to production physics.

## 4. XPBD v15 requirements
- Before capture, the free end remains dynamic and is not overwritten by the hand path.
- Independent visible hand-rig collision geometry (index distal pad, middle distal pad, palm) collides with the actual ribbon surface.
- The solver emits a contact event with frame/substep, collider, ribbon face, barycentric coordinate, contact point, normal, relative velocity and penetration depth.
- Only after a valid contact event may a hand-local grasp constraint be created.
- Retie establishes a hair-bow attachment before releasing the finger grasp.
- Required counterfactual tests: offset the hand path, disable one finger pad, remove collision geometry; capture must fail or occur at a different frame.
- Include hand, hair, bridge, curtain and ribbon self-collision.

## 5. Current gate state
| Gate | State | Evidence |
|---|---|---|
| G0 Requirements | BASELINE ESTABLISHED | Project Bible and v11 production contract |
| G1 Visual development | NOT LOCKED | Formal character candidates still required |
| G2 Formal assets | BLOCKED | Formal male/female candidate meshes not yet approved |
| G3 Rig/animation | BLOCKED | Formal male right-hand rig not yet established |
| G4 Ribbon solver | DESIGN ONLY | XPBD v15 spec exists; implementation not complete |
| G5 S04 vertical slice | BLOCKED | Must prove actual dynamic catch before expansion |
| G6 Key action slices | BLOCKED | Release and retie not proven on same assets |
| G7 Seven-shot production | BLOCKED | Do not expand before S04 passes |
| G8 Render | BLOCKED | No accepted render sequence |
| G9 Composite/sound | BLOCKED | No final composite or audio master |
| G10 Final QA/delivery | BLOCKED | No final approved MP4 |

## 6. Current next action
Recover/verify the v11 archive's raw bytes through an authorized route without requiring a repeat upload. Inspect formal character candidates and establish the male right-hand rig. Then implement XPBD v15 and complete the S04 Vertical Slice with independent physical and visual QA.

The v11 archive is 86,272,805 bytes and is reported to contain 252 files. The current migration could read the indexed v11 documents but could not materialize the archive bytes. Do not claim the 252 files have been inspected.
