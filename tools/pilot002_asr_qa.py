from pathlib import Path
import json
import re
from faster_whisper import WhisperModel

ROOT = Path('tts-output')
MANIFEST = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))

model = WhisperModel('small', device='cpu', compute_type='int8')

def han_only(s: str) -> str:
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def edit_distance(a: str, b: str) -> int:
    prev = list(range(len(b)+1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(cur[-1]+1, prev[j]+1, prev[j-1] + (ca != cb)))
        prev = cur
    return prev[-1]

report = {'model':'faster-whisper-small', 'language':'zh', 'scenes':{}, 'hard_pass': True}
for sid, meta in MANIFEST['scenes'].items():
    wav = ROOT / f"pilot002_{MANIFEST['voice']}_{sid}.wav"
    segments, info = model.transcribe(str(wav), language='zh', beam_size=5, vad_filter=False)
    transcript = ''.join(seg.text for seg in segments).strip()
    expected_han = han_only(meta['text'])
    got_han = han_only(transcript)
    dist = edit_distance(expected_han, got_han)
    cer = dist / max(1, len(expected_han))
    scene_pass = cer <= 0.18
    report['scenes'][sid] = {
        'expected': meta['text'],
        'transcript': transcript,
        'han_expected': expected_han,
        'han_transcript': got_han,
        'han_cer': round(cer, 4),
        'pass': scene_pass,
    }
    report['hard_pass'] = report['hard_pass'] and scene_pass
    print(f"{sid} CER={cer:.3f} PASS={scene_pass}\n  REF: {meta['text']}\n  ASR: {transcript}")

(ROOT / 'asr_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
if not report['hard_pass']:
    raise SystemExit('ASR QA failed: one or more scenes exceed Han CER threshold')
