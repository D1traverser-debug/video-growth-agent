from pathlib import Path
import json
import re
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
from pypinyin import Style, lazy_pinyin

ROOT = Path('tts-output')
MANIFEST = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))

model = WhisperModel('small', device='cpu', compute_type='int8')

def han_only(s: str) -> str:
    return ''.join(re.findall(r'[\u4e00-\u9fff]', s))

def edit_distance(a, b) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]

def lcs_length(a, b) -> int:
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if x == y else max(cur[-1], prev[j]))
        prev = cur
    return prev[-1]

def pinyin_tokens(s: str):
    # The purpose of this gate is spoken intelligibility/pronunciation, not
    # orthographic identity. Traditional/simplified and homophones should not
    # falsely fail a voice that is acoustically correct.
    return lazy_pinyin(
        han_only(s),
        style=Style.TONE3,
        neutral_tone_with_five=True,
        errors=lambda _: [],
    )

def read_16k_mono(path: Path) -> np.ndarray:
    audio, sr = sf.read(path, dtype='float32', always_2d=False)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    if sr != 16000:
        from math import gcd
        g = gcd(int(sr), 16000)
        audio = resample_poly(audio, 16000 // g, int(sr) // g).astype(np.float32)
    return np.ascontiguousarray(audio, dtype=np.float32)

report = {
    'model': 'faster-whisper-small',
    'language': 'zh',
    'decoder': 'soundfile+scipy-resample-direct-numpy',
    'gate_semantics': 'phonetic intelligibility and omission check; Han CER is diagnostic only',
    'threshold_pinyin_recall': 0.90,
    'minimum_han_length_ratio': 0.75,
    'scenes': {},
    'hard_pass': True,
}

for sid, meta in MANIFEST['scenes'].items():
    wav = ROOT / f"pilot002_{MANIFEST['voice']}_{sid}.wav"
    audio = read_16k_mono(wav)
    segments, info = model.transcribe(audio, language='zh', beam_size=5, vad_filter=False)
    transcript = ''.join(seg.text for seg in segments).strip()

    expected_han = han_only(meta['text'])
    got_han = han_only(transcript)
    han_cer = edit_distance(expected_han, got_han) / max(1, len(expected_han))

    expected_py = pinyin_tokens(meta['text'])
    got_py = pinyin_tokens(transcript)
    lcs = lcs_length(expected_py, got_py)
    pinyin_recall = lcs / max(1, len(expected_py))
    han_length_ratio = len(got_han) / max(1, len(expected_han))

    scene_pass = (
        bool(got_han)
        and pinyin_recall >= report['threshold_pinyin_recall']
        and han_length_ratio >= report['minimum_han_length_ratio']
    )

    report['scenes'][sid] = {
        'expected': meta['text'],
        'transcript': transcript,
        'han_expected': expected_han,
        'han_transcript': got_han,
        'han_cer_diagnostic': round(han_cer, 4),
        'pinyin_expected': expected_py,
        'pinyin_transcript': got_py,
        'pinyin_recall': round(pinyin_recall, 4),
        'han_length_ratio': round(han_length_ratio, 4),
        'pass': scene_pass,
    }
    report['hard_pass'] = report['hard_pass'] and scene_pass

    (ROOT / 'asr_report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print(
        f"{sid} PINYIN_RECALL={pinyin_recall:.3f} LEN_RATIO={han_length_ratio:.3f} "
        f"HAN_CER_DIAG={han_cer:.3f} PASS={scene_pass}\n"
        f"  REF: {meta['text']}\n  ASR: {transcript}"
    )

if not report['hard_pass']:
    raise SystemExit('ASR phonetic QA failed: one or more scenes have insufficient spoken-content coverage')
