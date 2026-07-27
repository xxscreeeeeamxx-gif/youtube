#!/usr/bin/env python3
"""チャンネル「日常研究所」のアイコンを生成する（2026-07採用デザイン）。

ずんだ緑の放射背景＋ずんだもん顔アップ（中央）＋「！？」＋上部にチャンネル名。
800x800（YouTubeは円形マスク表示・中央セーフエリアに要素を配置）。
ずんだもん立ち絵の出典・利用条件は assets/characters/SOURCES.md を参照。
実行: PYTHONPATH=. python3 scripts/gen_channel_icon.py
出力: assets/branding/channel_icon.png
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

FP = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
S = 800
ZUNDA = (108, 190, 88)
ZUNDA_DK = (74, 150, 60)
OUT = Path("assets/branding")


def font(sz):
    return ImageFont.truetype(FP, sz, index=0)


def ctext(d, cx, cy, s, f, fill, stroke=None, sw=0):
    bb = d.textbbox((0, 0), s, font=f)
    x, y = cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]
    d.text((x, y), s, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)


def make_icon() -> Image.Image:
    img = Image.new("RGB", (S, S), ZUNDA)
    d = ImageDraw.Draw(img)
    # 放射背景（12本）
    for k in range(12):
        a = math.pi * 2 * k / 12
        a2 = a + math.pi / 12
        d.polygon([(S / 2, S / 2),
                   (S / 2 + math.cos(a) * 900, S / 2 + math.sin(a) * 900),
                   (S / 2 + math.cos(a2) * 900, S / 2 + math.sin(a2) * 900)],
                  fill=ZUNDA_DK)
    # ずんだもん顔アップ（顔の重心を実測して水平センタリング）
    sp = Image.open("assets/characters/zundamon/happy.png")
    import numpy as np
    alpha = np.array(sp)[:, :, 3]
    hh, ww = alpha.shape
    band = alpha[int(hh * 0.22):int(hh * 0.42), :].sum(axis=0).astype(float)
    face_cx = (band * np.arange(ww)).sum() / band.sum()
    w = 760
    sp = sp.resize((w, int(sp.height * w / sp.width)), Image.LANCZOS)
    # 前髪と尻尾髪の非対称のぶんは目視で補正（+55px）
    FACE_OFFSET = 55
    px = int(S / 2 - face_cx * w / ww) + FACE_OFFSET
    img.paste(sp, (px, 150), sp)
    d = ImageDraw.Draw(img)
    # チャンネル名と！？
    ctext(d, S / 2, 80, "日常研究所", font(84), (255, 255, 255), stroke=ZUNDA_DK, sw=12)
    ctext(d, 668, 250, "？", font(120), (255, 255, 255), stroke=ZUNDA_DK, sw=10)
    ctext(d, 132, 264, "！", font(110), (255, 255, 255), stroke=ZUNDA_DK, sw=10)
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    icon = make_icon()
    icon.save(OUT / "channel_icon.png")
    # 円形プレビューも出力
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S, S], fill=255)
    circ = Image.new("RGB", (S, S), (250, 250, 250))
    circ.paste(icon, (0, 0), mask)
    circ.save(OUT / "channel_icon_preview.png")
    print("生成:", OUT / "channel_icon.png")
