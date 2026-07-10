"""チャンネルOP（5秒）の生成。

    ytf op          # assets/op.mp4 を生成（映像+音声）

channel.yaml のチャンネル名とアクセント色から、
光のストリーク → フラッシュ → ロゴ出現 → グロー呼吸 → 暗転
のオープニングを Pillow + FFmpeg で決定的にレンダリングする。

ビルド時は hook シーンの直後に自動挿入される（video.op.enabled）。
"""

from __future__ import annotations

import math
import random
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from .config import Config, ffmpeg_bin

W, H, FPS, DUR = 1920, 1080, 30, 5.0
IMPACT = 1.2          # ロゴが出る瞬間（秒）
FADE_OUT = 4.2        # 暗転開始（秒）


def _hex_rgb(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _bg(t: float) -> Image.Image:
    """濃紺のラジアルグラデーション背景。"""
    img = Image.new("RGB", (W // 4, H // 4))
    cx, cy = img.width / 2, img.height / 2
    maxd = math.hypot(cx, cy)
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            d = math.hypot(x - cx, y - cy) / maxd
            k = 1 - d * 0.85
            px[x, y] = (int(10 * k), int(15 * k), int(28 * k))
    return img.resize((W, H), Image.BILINEAR)


def render_op(cfg: Config, out_path: Path) -> None:
    accent = _hex_rgb(
        next((c.get("color") for c in cfg.characters.values() if c.get("color")),
             "#3AA0FF"))
    name = cfg.get("channel", "name", default="CHANNEL")
    title = re.sub(r"[（(].*?[)）]", "", name).strip()  # （仮）などを除去

    font_path = cfg.find_pillow_font()
    from PIL import ImageFont
    f_main = ImageFont.truetype(font_path, size=150, index=0)
    f_sub = ImageFont.truetype(font_path, size=42, index=0)

    rng = random.Random(7)
    streaks = [  # (y, 速度, 長さ, 太さ, 開始遅れ)
        (rng.uniform(0.08, 0.92) * H, rng.uniform(2200, 4200),
         rng.uniform(180, 520), rng.uniform(2, 5), rng.uniform(0.0, 0.5))
        for _ in range(26)
    ]

    n = int(DUR * FPS)
    tmp = Path(tempfile.mkdtemp(prefix="ytf_op_"))
    base = _bg(0)

    sub_text = "SCIENCE & MYSTERY"
    for i in range(n):
        t = i / FPS
        frame = base.copy().convert("RGB")
        d = ImageDraw.Draw(frame, "RGBA")

        # --- 光のストリーク（導入〜インパクトまで左右から走り抜ける） ---
        if t < IMPACT + 0.3:
            for (sy, spd, ln, wd, delay) in streaks:
                tt = t - delay
                if tt < 0:
                    continue
                from_left = sy % 2 < 1
                x = tt * spd if from_left else W - tt * spd
                x2 = x - ln if from_left else x + ln
                fade = max(0.0, 1 - t / (IMPACT + 0.3))
                # 外側: アクセント色の太いグロー / 内側: 白いコア
                d.line([x2, sy, x, sy], fill=(*accent, int(160 * fade)),
                       width=int(wd * 2.6))
                d.line([x2, sy, x, sy], fill=(235, 245, 255, int(230 * fade)),
                       width=max(1, int(wd)))
                # 先端の光点
                r = wd * 1.6
                d.ellipse([x - r, sy - r, x + r, sy + r],
                          fill=(255, 255, 255, int(230 * fade)))

        # --- インパクトの白フラッシュ＆リング ---
        if IMPACT <= t < IMPACT + 0.5:
            k = (t - IMPACT) / 0.5
            r = 80 + 1400 * k
            a = int(230 * (1 - k))
            d.ellipse([W/2 - r, H/2 - r*0.62, W/2 + r, H/2 + r*0.62],
                      outline=(*accent, a), width=max(2, int(14 * (1 - k))))
        if IMPACT <= t < IMPACT + 0.14:
            a = int(220 * (1 - (t - IMPACT) / 0.14))
            d.rectangle([0, 0, W, H], fill=(255, 255, 255, a))

        # --- ロゴ ---
        if t >= IMPACT:
            k = min(1.0, (t - IMPACT) / 0.35)          # 出現アニメ 0→1
            ease = 1 - (1 - k) ** 3
            scale = 1.12 - 0.12 * ease
            breathe = 1 + 0.012 * math.sin((t - IMPACT) * 2.2)

            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            tw = ld.textlength(title, font=f_main)
            x, y = (W - tw) / 2, H / 2 - 150
            ld.text((x, y), title, font=f_main, fill=(245, 248, 255, 255))
            # アクセント下線
            uw = tw * ease
            ld.rounded_rectangle([W/2 - uw/2, y + 190, W/2 + uw/2, y + 198],
                                 radius=4, fill=(*accent, 255))
            # サブテキスト（字間を空ける）
            spaced = " ".join(sub_text)
            sw = ld.textlength(spaced, font=f_sub)
            ld.text(((W - sw) / 2, y + 230), spaced, font=f_sub,
                    fill=(*accent, 235))

            s = scale * breathe
            if abs(s - 1) > 0.001:
                nw, nh = int(W * s), int(H * s)
                layer = layer.resize((nw, nh), Image.LANCZOS)
                layer = layer.crop(((nw - W) // 2, (nh - H) // 2,
                                    (nw - W) // 2 + W, (nh - H) // 2 + H))
            # グロー（ぼかした自身を下に重ねて光らせる）
            glow = layer.filter(ImageFilter.GaussianBlur(14))
            frame_rgba = frame.convert("RGBA")
            frame_rgba.alpha_composite(glow)
            frame_rgba.alpha_composite(layer)
            frame = frame_rgba.convert("RGB")
            d = ImageDraw.Draw(frame, "RGBA")

        # --- 暗転 ---
        if t >= FADE_OUT:
            a = int(255 * min(1.0, (t - FADE_OUT) / (DUR - FADE_OUT)))
            d.rectangle([0, 0, W, H], fill=(0, 0, 0, a))

        frame.save(tmp / f"{i:03d}.png")

    # --- 音: ライザー(0-1.2s) → インパクト(1.2s) → 余韻パッド → フェード ---
    fc = (
        # ライザー: 上昇サイン + ノイズスウェル
        "[1]volume='0.5*t/1.2':eval=frame,lowpass=f=2500[riser];"
        "[2]volume='0.25*t/1.2':eval=frame,lowpass=f=1800[nz];"
        # インパクト: 低音ドン + 高い煌めき（1.2sに配置）
        "[3]afade=t=out:st=0:d=1.4,adelay=1200|1200[boom];"
        "[4]afade=t=out:st=0:d=0.9,volume=0.4,adelay=1200|1200[shine];"
        # 余韻パッド（1.2s以降ゆっくり）
        "[5]volume=0.22,afade=t=in:st=1.2:d=0.6,adelay=1200|1200[pad];"
        "[riser][nz][boom][shine][pad]amix=inputs=5:normalize=0,"
        f"afade=t=out:st={FADE_OUT}:d={DUR - FADE_OUT},"
        "loudnorm=I=-13:TP=-1.0,aresample=44100[aout]"
    )
    cmd = [
        ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
        "-framerate", str(FPS), "-i", str(tmp / "%03d.png"),
        "-f", "lavfi", "-i", f"aevalsrc=sin(2*PI*(70+260*t*t)*t):d={IMPACT}:s=44100",
        "-f", "lavfi", "-i", f"anoisesrc=color=pink:amplitude=0.5:d={IMPACT}",
        "-f", "lavfi", "-i", "sine=frequency=52:duration=1.6",
        "-f", "lavfi", "-i", "sine=frequency=1244:duration=1.0",
        "-f", "lavfi", "-i", f"sine=frequency=220:duration={DUR - IMPACT}",
        "-filter_complex", fc,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-t", str(DUR), str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    for p in tmp.glob("*.png"):
        p.unlink()
    tmp.rmdir()
    if r.returncode != 0:
        raise SystemExit(f"OPの書き出しに失敗:\n{r.stderr[-800:]}")
    print(f"OP生成完了: {out_path}（{DUR}秒）")


def run_op(cfg: Config) -> None:
    out = cfg.root / cfg.get("video", "op", "file", default="assets/op.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    render_op(cfg, out)
