#!/usr/bin/env python3
"""チャンネル「日常研究所」のバナー（チャンネルアート）を生成する。

2560x1440（YouTube推奨）。全デバイスで見えるセーフエリアは中央1546x423なので、
ずんだもん・つむぎ・チャンネル名・サブタイトルはすべてその帯に収める。
デザインはアイコン（gen_channel_icon.py）と同じ、ずんだ緑の放射＋白抜き文字。
実行: PYTHONPATH=. python3 scripts/gen_channel_banner.py
出力: assets/branding/channel_banner.png（+ セーフエリア確認用プレビュー）
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

FP = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
W, H = 2560, 1440
SAFE_W, SAFE_H = 1546, 423
SX0, SY0 = (W - SAFE_W) // 2, (H - SAFE_H) // 2  # 507, 508
ZUNDA = (108, 190, 88)
ZUNDA_DK = (74, 150, 60)
CREAM = (248, 246, 238)
AMBER = (255, 196, 60)
OUT = Path("assets/branding")


def font(sz):
    return ImageFont.truetype(FP, sz, index=0)


def ctext(d, cx, cy, s, f, fill, stroke=None, sw=0):
    bb = d.textbbox((0, 0), s, font=f)
    x, y = cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]
    d.text((x, y), s, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)


def sprite(name, emotion, w):
    im = Image.open(f"assets/characters/{name}/{emotion}.png")
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def make_banner() -> Image.Image:
    img = Image.new("RGB", (W, H), ZUNDA)
    d = ImageDraw.Draw(img)
    # 放射背景（中心=バナー中央）
    for k in range(16):
        a = math.pi * 2 * k / 16
        a2 = a + math.pi / 16
        d.polygon([(W / 2, H / 2),
                   (W / 2 + math.cos(a) * 2400, H / 2 + math.sin(a) * 2400),
                   (W / 2 + math.cos(a2) * 2400, H / 2 + math.sin(a2) * 2400)],
                  fill=ZUNDA_DK)
    # セーフエリア外の飾り（薄い？と！を散らす）
    deco = [(300, 260, "？", 150), (2260, 240, "！", 140), (240, 1180, "！", 130),
            (2300, 1180, "？", 150), (1280, 170, "？", 110), (1280, 1290, "！", 110)]
    for cx, cy, s, sz in deco:
        ctext(d, cx, cy, s, font(sz), (255, 255, 255, 0), stroke=None)
        ctext(d, cx, cy, s, font(sz), ZUNDA)
    # キャラ（頭部+肩のクロップをセーフエリアの左右端に。顔は必ず帯内・文字と重ねない）
    def head_crop(name, emotion, w, head_ratio):
        im = Image.open(f"assets/characters/{name}/{emotion}.png")
        im = im.crop((0, 0, im.width, int(im.height * head_ratio)))
        return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)

    zw = 430
    zu = head_crop("zundamon", "happy", zw, 0.40)
    img.paste(zu, (SX0 + 6, SY0 + SAFE_H - zu.height + 8), zu)
    tw = 440
    ts = head_crop("tsumugi", "happy", tw, 0.38)
    ts = ts.transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(ts, (SX0 + SAFE_W - tw - 6, SY0 + SAFE_H - ts.height + 8), ts)
    # 中央の文字（キャラと横に並ぶ幅に抑える）
    d = ImageDraw.Draw(img)
    ctext(d, W / 2, SY0 + 140, "日常研究所", font(150), (255, 255, 255),
          stroke=ZUNDA_DK, sw=16)
    ctext(d, W / 2, SY0 + 268, "身近な当たり前を、再現ドラマで",
          font(56), CREAM, stroke=ZUNDA_DK, sw=9)
    # 豆電球ワンポイント（タイトルの真上・セーフエリア内）
    bx, by = W / 2, SY0 + 44
    d.ellipse([bx - 26, by - 26, bx + 26, by + 26], fill=(255, 232, 150))
    ctext(d, bx, by - 2, "！", font(32), ZUNDA_DK)
    for k in range(6):
        a = math.pi * 2 * k / 6 - math.pi / 2
        d.line([bx + math.cos(a) * 34, by + math.sin(a) * 34,
                bx + math.cos(a) * 46, by + math.sin(a) * 46], fill=AMBER, width=6)
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    banner = make_banner()
    banner.save(OUT / "channel_banner.png")
    # セーフエリア確認プレビュー（枠線+デスクトップ表示帯の切り出し）
    prev = banner.copy()
    d = ImageDraw.Draw(prev)
    d.rectangle([SX0, SY0, SX0 + SAFE_W, SY0 + SAFE_H], outline=(255, 80, 80), width=6)
    prev.resize((1280, 720)).save(OUT / "channel_banner_guide.png")
    banner.crop((0, SY0, W, SY0 + SAFE_H)).save(OUT / "channel_banner_mobile.png")
    print("生成:", OUT / "channel_banner.png")
