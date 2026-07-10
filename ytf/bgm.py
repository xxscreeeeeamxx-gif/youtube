"""BGM生成（MusicGen の部分採用。transformers経由なので依存が軽い）。

テキストの雰囲気指定からローカルでBGMを生成し、assets/bgm/ に配置する。
編集画面の 🎵BGM からそのまま選べるようになる。

    ytf bgm "calm curious ambient, science documentary" --name curious
    ytf bgm "warm acoustic guitar, relaxed" --name acoustic --duration 40

必要: pip install torch transformers scipy sentencepiece
（初回はモデル約2GBをダウンロード。生成はMac(MPS)/CPUでも動く）
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .config import Config, ffmpeg_bin


def run_bgm(cfg: Config, prompt: str, name: str | None, duration: int) -> None:
    try:
        import torch
        from transformers import AutoProcessor, MusicgenForConditionalGeneration
    except ImportError:
        raise SystemExit(
            "依存がありません: pip install torch transformers scipy sentencepiece\n"
            "（初回実行時にモデル約2GBをダウンロードします）"
        )

    duration = max(8, min(60, duration))
    out_name = name or "generated"
    bgm_dir = cfg.root / "assets" / "bgm"
    bgm_dir.mkdir(parents=True, exist_ok=True)

    print(f"MusicGenでBGM生成中…（{duration}秒 / 初回はモデルDLで数分かかります）")
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = model.to(device)

    inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
    # MusicGen はおよそ 50 トークン/秒
    audio = model.generate(**inputs, max_new_tokens=int(duration * 50),
                           do_sample=True, guidance_scale=3.0)
    sr = model.config.audio_encoder.sampling_rate
    data = audio[0, 0].cpu().float().numpy()

    import scipy.io.wavfile as wavfile
    tmp = bgm_dir / f"_{out_name}_raw.wav"
    wavfile.write(str(tmp), sr, data)

    # mp3化 + ラウドネス正規化 + フェード（既存BGMと同じ扱いに揃える）
    dst = bgm_dir / f"{out_name}.mp3"
    fade_out = max(0.0, duration - 3.0)
    r = subprocess.run(
        [ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(tmp),
         "-af", f"loudnorm=I=-16:TP=-1.5,afade=t=in:d=2,"
                f"afade=t=out:st={fade_out}:d=3",
         "-ar", "44100", "-b:a", "160k", str(dst)],
        capture_output=True, text=True,
    )
    tmp.unlink(missing_ok=True)
    if r.returncode != 0:
        raise SystemExit(f"mp3変換に失敗: {r.stderr[-300:]}")
    print(f"生成完了: {dst}")
    print("編集画面の 🎵BGM から選択するか、channel.yaml の video.bgm.file に設定してください")
