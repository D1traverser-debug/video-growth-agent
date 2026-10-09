from pathlib import Path
import json
import numpy as np
import soundfile as sf
from kokoro import KPipeline

OUT = Path('tts-output')
OUT.mkdir(exist_ok=True)
SCENES = {
    'S01': '应用不会消失。先消失的，是你一个个打开它们的动作。',
    'S02': 'Google 刚发布 Gemini Agent。它能跨 Gmail、Drive、Docs、Sheets、Calendar 工作。',
    'S03': '老板只要说：明天下午，给客户做份市场更新。',
    'S04': '以前你得找邮件、翻文件、查资料、拉表、做 PPT、再回复。',
    'S05': 'Agent 想把这些步骤藏到后台。你只说：把它准备好。',
    'S06': '它自己规划、调用工具、带着上下文把结果送回来。',
    'S07': '所以变的不是 App，而是操作层：界面退到后面，工具被 Agent 调用。',
    'S08': '软件下一轮争的，也许不只是桌面第一屏，而是谁更容易被 Agent 找到、授权、调用。',
    'S09': '但越方便，权限越危险：它能看什么、改什么、替你做什么？谁能撤销？',
    'S10': 'Agent 时代真正值钱的，不只是谁的模型更聪明。还有，谁掌握入口，谁掌握权限。',
}

en_pipeline = KPipeline(lang_code='a', model=False)
def english_phonemes(text: str) -> str:
    return ' '.join(r.phonemes for r in en_pipeline(text, model=False, split_pattern=None) if r.phonemes)

pipeline = KPipeline(
    lang_code='z',
    repo_id='hexgrad/Kokoro-82M-v1.1-zh',
    device='cpu',
    en_callable=english_phonemes,
)
voice = 'zf_001'
manifest = {'voice': voice, 'scenes': {}}
for sid, text in SCENES.items():
    chunks = []
    for result in pipeline(text, voice=voice, speed=1.08, split_pattern=None):
        if result.audio is not None:
            chunks.append(result.audio.numpy() if hasattr(result.audio, 'numpy') else np.asarray(result.audio))
    if not chunks:
        raise RuntimeError(f'No audio produced for {sid}')
    wav = np.concatenate(chunks)
    path = OUT / f'pilot002_{voice}_{sid}.wav'
    sf.write(path, wav, 24000, subtype='PCM_16')
    duration = len(wav) / 24000
    manifest['scenes'][sid] = {'duration': round(duration, 3), 'text': text}
    print(voice, sid, f'{duration:.3f}s')

(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
