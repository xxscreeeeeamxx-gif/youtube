#!/usr/bin/env python3
"""国産ウイスキー・鳥井信治郎の再現ドラマ（torii-whisky）用の背景3種。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
★商標に触れないため、瓶の意匠・ラベルの figure・銘柄名は描かない。
  瓶は「琥珀色の液体が入った角瓶」までにとどめる。
トーンの設計:
  洋酒店   … 木と琥珀。売る側の世界。赤玉が売れた場所であり、白札が戻ってくる場所
  蒸溜所   … 銅のポットスチルと樽。**作る側の世界**。ここが二人の立っている場所
  現代     … いちばん明るい。棚に瓶が並ぶ

実行: PYTHONPATH=. python3 scripts/gen_wsk_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402
from scripts.gen_yam_bgs import _desk  # noqa: E402


def _bottle(d, x, y, s=1.0, liq=(186, 116, 40)):
    """角瓶。**銘柄が分かる意匠は描かない**。琥珀色の中身と首だけ。"""
    d.rounded_rectangle([x, y - 128 * s, x + 76 * s, y], radius=8 * s,
                        fill=(214, 206, 190), outline=(150, 142, 126),
                        width=max(1, int(4 * s)))
    d.rounded_rectangle([x + 6 * s, y - 96 * s, x + 70 * s, y - 8 * s],
                        radius=6 * s, fill=liq)
    d.rectangle([x + 26 * s, y - 166 * s, x + 50 * s, y - 122 * s],
                fill=(198, 190, 174), outline=(150, 142, 126),
                width=max(1, int(3 * s)))
    d.rectangle([x + 22 * s, y - 180 * s, x + 54 * s, y - 160 * s],
                fill=(120, 96, 60))          # 栓
    d.rectangle([x + 10 * s, y - 74 * s, x + 66 * s, y - 40 * s],
                fill=(238, 234, 224), outline=(160, 152, 136),
                width=max(1, int(3 * s)))    # 無地のラベル


def _cask(d, x, y, s=1.0):
    """樽。横倒しで積む。"""
    d.ellipse([x, y - 104 * s, x + 46 * s, y], fill=(132, 92, 52),
              outline=(92, 62, 32), width=max(1, int(5 * s)))
    d.rectangle([x + 23 * s, y - 104 * s, x + 200 * s, y], fill=(156, 110, 62))
    d.ellipse([x + 177 * s, y - 104 * s, x + 223 * s, y], fill=(176, 126, 72),
              outline=(92, 62, 32), width=max(1, int(5 * s)))
    for k in range(2):                       # たが
        xx = x + 70 * s + k * 74 * s
        d.rectangle([xx, y - 104 * s, xx + 14 * s, y], fill=(92, 92, 96))


def _still(d, x, y, s=1.0):
    """ポットスチル。銅の玉ねぎ型と、斜めに伸びる首。蒸溜所の顔。"""
    cu, dk = (196, 122, 62), (140, 82, 36)
    d.ellipse([x, y - 250 * s, x + 260 * s, y], fill=cu, outline=dk,
              width=max(2, int(8 * s)))
    d.polygon([(x + 84 * s, y - 236 * s), (x + 176 * s, y - 236 * s),
               (x + 152 * s, y - 330 * s), (x + 108 * s, y - 330 * s)],
              fill=cu, outline=dk, width=max(2, int(7 * s)))
    d.line([(x + 130 * s, y - 326 * s), (x + 300 * s, y - 392 * s),
            (x + 360 * s, y - 250 * s)], fill=cu, width=int(26 * s), joint="curve")
    d.rectangle([x + 40 * s, y - 24 * s, x + 220 * s, y + 18 * s], fill=(96, 96, 100))


def mise() -> Image.Image:
    """大阪の洋酒店。木と琥珀。売る側の世界。"""
    img = vgrad((W, H), (196, 172, 136), (168, 144, 110)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 810, (148, 118, 78), (112, 88, 56))
    # 背面の棚（瓶がずらり）
    d.rectangle([80, 150, 900, 810], fill=(140, 106, 66), outline=(100, 74, 44),
                width=8)
    for r in range(3):
        yy = 300 + r * 170
        d.rectangle([100, yy, 880, yy + 16], fill=(110, 82, 50))
        for c in range(6):
            _bottle(d, 130 + c * 122, yy - 4, 0.60,
                    liq=(186, 92, 60) if r == 0 else (186, 116, 40))
    _window(img, d, 1120, 170, 1820, 520, (232, 214, 172), (248, 238, 206),
            frame=(112, 86, 54))
    d = ImageDraw.Draw(img)
    _desk(d, 1060, 660, 1800, 810, (132, 100, 62), (96, 72, 42))
    _bottle(d, 1180, 658, 1.05)
    _bottle(d, 1320, 658, 1.05, liq=(186, 92, 60))
    d.line([1000, 0, 1000, 230], fill=(86, 70, 52), width=6)
    d.ellipse([968, 230, 1032, 294], fill=(252, 236, 186))
    glow(img, 1000, 262, 240, (255, 232, 168), 96)
    return img


def jozo() -> Image.Image:
    """蒸溜所。銅のポットスチルと樽。作る側の世界。"""
    img = vgrad((W, H), (168, 158, 148), (136, 126, 118)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 840, (140, 132, 124), (104, 98, 92))
    for x in (100, 1700):                    # 柱
        d.rectangle([x, 0, x + 56, 840], fill=(120, 112, 106))
    _window(img, d, 640, 120, 1300, 420, (206, 214, 220), (236, 240, 244),
            frame=(112, 106, 100))
    d = ImageDraw.Draw(img)
    _still(d, 620, 836, 1.0)
    _still(d, 1120, 836, 0.82)
    for k in range(3):                       # 樽の山
        _cask(d, 170, 830 - k * 112, 0.9)
    _cask(d, 1500, 830, 0.9)
    _cask(d, 1500, 718, 0.9)
    glow(img, 760, 700, 300, (255, 190, 110), 70)
    return img


def ima() -> Image.Image:
    """現代。明るい棚に瓶が並ぶ。いちばん明るい絵にする。"""
    img = vgrad((W, H), (222, 232, 240), (196, 210, 224)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 820, (186, 190, 196), (150, 156, 164))
    d.rectangle([90, 140, 1830, 820], fill=(206, 212, 220), outline=(160, 168, 178),
                width=8)
    for r in range(3):
        yy = 290 + r * 178
        d.rectangle([110, yy, 1810, yy + 16], fill=(170, 178, 188))
        for c in range(11):
            _bottle(d, 150 + c * 152, yy - 4, 0.66,
                    liq=(196, 130, 48) if c % 3 else (176, 96, 44))
    glow(img, 1700, 160, 420, (255, 250, 226), 88)
    return img


PAINTERS = {
    "il_wsk_mise": mise,
    "il_wsk_jozo": jozo,
    "il_wsk_ima": ima,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
