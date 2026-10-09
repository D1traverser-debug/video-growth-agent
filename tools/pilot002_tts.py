from pathlib import Path
import json
import numpy as np
import soundfile as sf
from kokoro import KPipeline

OUT = Path('tts-output')
OUT.mkdir(exist_ok=True)
TEXT = '应用不会消失。先消失的，是你一个个打开它们的动作。'

en_pipeline = KPipeline(lang_code='a', model=False)
def english_phonemes(text: str) -> str:
    return ' '.join(r.phonemes for r in en_pipeline(text, model=False, split_pattern=None) if r.phonemes)

pipeline = KPipeline(
    lang_code='z',
    repo_id='hexgrad/Kokoro-82M-v1.1-zh',
    device='cpu',
    en_callable=english_phonemes,
)
voice='zf_001'
chunks=[]
for result in pipeline(TEXT, voice=voice, speed=1.08, split_pattern=None):
    if result.audio is not None:
        chunks.append(result.audio.numpy() if hasattr(result.audio,'numpy') else np.asarray(result.audio))
if not chunks:
    raise RuntimeError('No audio produced for S01')
wav=np.concatenate(chunks)
path=OUT/'pilot002_zf_001_S01.wav'
sf.write(path,wav,24000,subtype='PCM_16')
duration=len(wav)/24000
(OUT/'manifest.json').write_text(json.dumps({'patch':'S01','voice':voice,'duration':round(duration,3),'target':5.2,'text':TEXT},ensure_ascii=False,indent=2),encoding='utf-8')
print(voice,'S01',f'{duration:.3f}s target=5.2s')
