from pathlib import Path
import json
import numpy as np
import soundfile as sf
from kokoro import KPipeline

OUT = Path('tts-output')
OUT.mkdir(exist_ok=True)
# Patch-only generation after phonetic QA isolated risk to S02 and S04.
SCENES = {
    'S02': 'Google 刚发布 Gemini Agent。它能跨邮件、云盘、文档、表格和日历工作。',
    'S04': '以前你要找邮件、看文件、查资料、拉表、做 PPT、再回复。',
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
