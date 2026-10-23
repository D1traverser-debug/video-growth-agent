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
    sound_inventory: list[str] = []
    score_changes: list[str] = []
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
        for cue in shot["audio"]:
            local = (cue["at_frame"] - start_frame) / fps
            moment = f"At {_at(local)}"
            category, detail = cue["category"], cue["description"]
            if category == "MUSIC":
                # Score is only audible to the audience, not a physical sound.
                score_changes.append(f"{moment}, {detail}.")
            elif category == "SILENCE":
                story += f"{moment}, an intentional silence: {detail}. "
            else:
                # An action synced to a beat must live on that shot's timeline,
                # not only in the undated environmental sound bed.
                story += f"{moment}, synced {category.lower()}: {detail}. "
                if category in {"AMBIENCE", "SFX"} and detail not in sound_inventory:
                    sound_inventory.append(detail)
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
    soundscape = (
        "Environmental and physical sound palette: " + "; ".join(sound_inventory) + "."
        if sound_inventory else "Quiet environment with minimal physical movement noise."
    )
    music = brief["sound_strategy"]
    if score_changes:
        music += " Timed score events: " + " ".join(score_changes)
    return (
        story
        + "\\n\\noverall_soundscape: "
        + soundscape
        + "\\n\\nnon_diegetic_music: "
        + (music if music.strip() else "N/A")
    )



def render_h3_cn_storyboard(
    *,
    plan: dict,
    shots: list[dict],
    render_seconds: int,
    usable_seconds: float,
    continuation: bool,
) -> str:
    """Preserve the user's successful Chinese timecoded full-storyboard idiom.

    This deliberately competes with, rather than claiming to be identical to,
    the vendor-native three-field guide. Its source is owner reported quality.
    """
    brief = plan["brief"]
    concept = next(c for c in plan["alternatives"] if c["id"] == plan["selected"])
    first = shots[0]["start_frame"]
    fps = brief["fps"]
    lines = [
        f"作品：《{brief['title']}》。总生成时长{render_seconds}秒；后期有效时长{usable_seconds:.2f}秒，"
        f"最终画幅{brief['aspect_ratio']}，导演剪辑时间基准{fps}fps。",
        f"故事核心：{brief['goal']}。情绪变化：{brief['emotion']}。",
        f"美术与叙事机制：{concept['premise']}；{concept['visual_mechanism']}。",
        "全片一致性： " + "；".join(plan["identity_anchors"]) + "。",
        "逐时段分镜（时间表示该生成片段内的本地时间，不代表模型一定按帧切镜）：",
    ]
    for i, shot in enumerate(shots, 1):
        start = (shot["start_frame"] - first) / fps
        stop = (shot["end_frame"] - first) / fps
        a, c, l, t = shot["action"], shot["camera"], shot["light"], shot["transition"]
        cues = "；".join(
            f"{(s['at_frame'] - first) / fps:.2f}秒 {s['description']}"
            for s in shot["audio"]
        )
        lines.append(
            f"{start:.2f}–{stop:.2f}秒，分镜{i}：{shot['scene']}。"
            f"画面构图：{shot['composition']}。起始状态：{a['start']}；"
            f"触发动作：{a['trigger']}；动作结果：{a['finish']}。"
            f"摄影：{c['lens']}，{c['framing']}，主运镜{c['move']}；"
            f"运镜目的：{c['motivation']}。"
            f"光照：{l['source']}，方向{l['direction']}，呈现{l['effect']}。"
            f"转场：{t['kind']}，通过{t['bridge']}，用以{t['purpose']}。"
            f"连续性：{shot['continuity']}。"
            f"声音事件：{cues or '后期制作'}。"
        )
    if render_seconds - usable_seconds > 0.001:
        lines.append(
            f"动作必须在{usable_seconds:.2f}秒之前完成；后续画面稳定保持至"
            f"{render_seconds}秒，后期只保留开头{usable_seconds:.2f}秒。"
        )
    if not continuation:
        lines.append(f"结尾画面：{brief['ending']}。")
    lines.append(
        f"音乐与声音：{brief['sound_strategy']}。"
        "禁止人物变脸、手部错乱、道具断裂瞬移或无因果的随机闪白；"
        "所有镜头服务故事，避免新增没有分镜依据的角色与场景。"
    )
    return "\n".join(lines)
