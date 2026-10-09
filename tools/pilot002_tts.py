from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro import KPipeline

OUT = Path('tts-output')
OUT.mkdir(exist_ok=True)

TEXT = '''你每天打开的 App 不会消失。先消失的，可能是你一个个打开它们的动作。
Google 刚发布 Gemini Agent。它能跨 Gmail、Drive、Docs、Sheets、Calendar 工作。
老板只要说：明天下午，给客户做份市场更新。
以前你得找邮件、翻文件、查资料、拉表、做 PPT、再回复。
Agent 想把这些步骤藏到后台。你只说：把它准备好。
它自己规划、调用工具、带着上下文把结果送回来。
所以变的不是 App，而是操作层：界面退到后面，工具被 Agent 调用。
软件下一轮争的，也许不只是桌面第一屏，而是谁更容易被 Agent 找到、授权、调用。
但越方便，权限越危险：它能看什么、改什么、替你做什么？谁能撤销？
Agent 时代真正值钱的，不只是谁的模型更聪明。还有，谁掌握入口，谁掌握权限。'''

pipeline = KPipeline(lang_code='z', device='cpu')
for voice in ('zf_001', 'zm_010'):
    chunks = []
    for _, _, audio in pipeline(TEXT, voice=voice, speed=1.08, split_pattern=r'\n+'):
        chunks.append(audio)
    if not chunks:
        raise RuntimeError(f'No audio produced for {voice}')
    wav = np.concatenate(chunks)
    sf.write(OUT / f'pilot002_{voice}.wav', wav, 24000, subtype='PCM_16')
    print(voice, f'{len(wav)/24000:.3f}s')
