"""MiniMax H3 vendor-native prompt projection for authored shot groups.

Adapted from first-party MiniMax-AI/MiniMax-H3 h3-prompt-writing SKILL and
base-en.txt, consulted 2026-10-23. This is *prompt text*, not an API call.
"""
from __future__ import annotations


def _at(seconds: float) -> str:
    minutes = int(seconds // 60)
    whole = int(seconds) % 60
    milliseconds = round((seconds - int(seconds)) * 1000)
    if milliseconds == 1000:
        whole += 1
        milliseconds = 0
    return f"{minutes:02d}:{whole:02d}.{milliseconds:03d}"


def render_h3_t2va(
    *,
    plan: dict,
    shots: list[dict],
    render_seconds: int,
    usable_seconds: float,
    continuation: bool,
) -> str:
    """Follow vendor T2VA sections and per-clip *local* cut timestamps."""
    if not shots:
        raise ValueError("at least one shot required")
    brief = plan["brief"]
    concept = next(x for x in plan["alternatives"] if x["id"] == plan["selected"])
    fps = brief["fps"]
    start_frame = shots[0]["start_frame"]
    story = (
        f"integrated_multimodal_description: "
        f"[Shot 1] {concept['premise']}. "
        f"Visual mechanism: {concept['visual_mechanism']}. "
        f"Identity and physical anchors: {'; '.join(plan['identity_anchors'])}. "
    )
    sound_bed: list[str] = []
    for index, shot in enumerate(shots):
        cam, action, light, trans = (
            shot["camera"], shot["action"], shot["light"], shot["transition"]
        )
        if index > 0:
            local = (shot["start_frame"] - start_frame) / fps
            story += f"[Shot {index + 1}] At {_at(local)}, the camera cuts to "
        story += (
            f"{shot['composition']} in {shot['scene']}. "
            f"Initially {action['start']}; then {action['trigger']}; "
            f"finally {action['finish']}. "
            f"The camera uses {cam['framing']} on {cam['lens']} and performs "
            f"{cam['move'].lower().replace('_',' ')} with deliberate modest amplitude, "
            f"because {cam['motivation']}. "
            f"Light comes from {light['source']} ({light['direction']}), revealing {light['effect']}. "
            f"Transition uses {trans['kind']}, matching {trans['bridge']}; "
            f"its purpose is {trans['purpose']}. "
            f"Keep continuity: {shot['continuity']}. "
        )
        for sound in shot["audio"]:
            local = (sound["at_frame"] - start_frame) / fps
            cue = f"At {_at(local)}, {sound['description']}."
            if sound["category"] == "MUSIC":
                continue
            sound_bed.append(cue)
    if render_seconds - usable_seconds > 0.001:
        story += (
            f"Complete the intended action by {usable_seconds:.2f} seconds; "
            f"then hold the resulting pose and environment continuously until "
            f"{render_seconds:.2f} seconds so the editor can trim the approved "
            f"{usable_seconds:.2f}-second segment from the beginning. "
        )
    if not continuation:
        story += f"Conclude on {brief['ending']}. "
    story += f"The creative objective is {brief['goal']}. "
    if not sound_bed:
        sound_bed = ["Quiet environment and realistic physical sounds accompany the movement."]
    music = brief["sound_strategy"]
    return (
        story
        + "\n\noverall_soundscape: "
        + " ".join(sound_bed)
        + "\n\nnon_diegetic_music: "
        + (music if music.strip() else "N/A")
    )
