#!/usr/bin/env python3
"""ソニー・井深大の再現ドラマ（ibuka-sony）用の背景5種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
★商標に触れないため、製品の意匠・ロゴ・型番などは描かない。
トーンの設計:
  白木屋（デパートの一室） … 焼け残りの薄暗さ。ここが出発点
  工場                     … 作業灯の白
  アメリカ                 … 明るい寒色。よそ行きの緊張
  役所                     … 灰と石。ここがこの回の敵
  現代                     … いちばん明るい

実行: PYTHONPATH=. python3 scripts/gen_son_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402
from scripts.gen_yam_bgs import _building, _person, _desk  # noqa: E402


def _radio(d, x, y, s=1.0, body=(176, 140, 96)):
    """真空管ラジオ。木の箱に丸いダイヤル。意匠は作らず一般的な形にする。"""
    d.rounded_rectangle([x, y - 200 * s, x + 320 * s, y], radius=14 * s,
                        fill=body, outline=(116, 88, 56), width=int(7 * s))
    d.ellipse([x + 34 * s, y - 168 * s, x + 168 * s, y - 34 * s],
              fill=(92, 74, 54), outline=(64, 50, 36), width=int(6 * s))
    for a in range(12):
        ang = a * math.pi / 6
        d.line([x + 101 * s + math.cos(ang) * 44 * s,
                y - 101 * s + math.sin(ang) * 44 * s,
                x + 101 * s + math.cos(ang) * 60 * s,
                y - 101 * s + math.sin(ang) * 60 * s],
               fill=(70, 56, 40), width=int(4 * s))
    d.ellipse([x + 210 * s, y - 140 * s, x + 290 * s, y - 60 * s],
              fill=(226, 216, 190), outline=(116, 88, 56), width=int(6 * s))
    d.line([x + 250 * s, y - 100 * s, x + 250 * s, y - 132 * s],
           fill=(150, 60, 50), width=int(6 * s))


def shirokiya() -> Image.Image:
    """焼け残ったデパートの一室。柱と、寄せ集めの机。"""
    img = vgrad((W, H), (150, 140, 128), (186, 174, 158)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (140, 122, 100), (108, 94, 76))
    # 太い角柱（デパートらしさ）
    for x in (240, 1560):
        d.rectangle([x, 0, x + 150, 800], fill=(168, 156, 140))
        d.rectangle([x - 20, 100, x + 170, 150], fill=(184, 172, 154))
    # 割れた窓と、外の明るさ
    _window(img, d, 640, 160, 1240, 540, (196, 206, 214), (228, 232, 232),
            frame=(120, 112, 100))
    d = ImageDraw.Draw(img)
    for k in range(4):
        d.line([700 + k * 130, 180, 780 + k * 130, 520], fill=(150, 150, 148),
               width=5)
    _desk(d, 560, 810, 1160, 950, (120, 96, 66), (88, 68, 44))
    _radio(d, 700, 810, 0.6)
    # 裸電球
    d.line([420, 0, 420, 260], fill=(80, 76, 70), width=6)
    d.ellipse([388, 260, 452, 324], fill=(252, 236, 180))
    glow(img, 420, 292, 220, (255, 232, 160), 96)
    return img


def kojo() -> Image.Image:
    img = vgrad((W, H), (216, 218, 222), (192, 194, 198)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 800], fill=(206, 208, 212))
    for k in range(5):
        x = k * 400
        d.polygon([(x, 250), (x + 400, 250), (x + 400, 110), (x + 200, 110)],
                  fill=(162, 166, 174))
        d.polygon([(x + 200, 110), (x + 400, 110), (x + 400, 250)],
                  fill=(192, 212, 230))
    _floor(d, 800, (152, 150, 148), (120, 118, 118))
    _desk(d, 220, 800, 820, 940, (120, 100, 76), (88, 72, 54))
    # 作業台の上に、小さい部品の山
    for k in range(9):
        cx = 280 + k * 58
        d.ellipse([cx - 12, 770, cx + 12, 794], fill=(90, 94, 104))
        d.line([cx, 794, cx - 6, 812], fill=(150, 154, 162), width=4)
        d.line([cx, 794, cx + 6, 812], fill=(150, 154, 162), width=4)
    _radio(d, 1240, 840, 0.8)
    glow(img, 700, 200, 340, (250, 252, 255), 46)
    return img


def america() -> Image.Image:
    """アメリカの研究所。寒色で、こちらより整った画にする。"""
    img = vgrad((W, H), (196, 212, 232), (222, 228, 234)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (176, 178, 184), (144, 146, 152))
    d.rectangle([0, 0, W, 800], fill=(216, 224, 232))
    # 大きい窓が並ぶ
    for k in range(4):
        x = 120 + k * 440
        d.rounded_rectangle([x, 150, x + 320, 560], radius=8,
                            fill=(168, 200, 232), outline=(140, 148, 158), width=8)
        d.line([x + 160, 150, x + 160, 560], fill=(140, 148, 158), width=7)
    _desk(d, 640, 810, 1280, 950, (150, 152, 158), (112, 114, 120))
    # 台の上に、極端に小さい部品を1つだけ置く（対比）
    d.ellipse([940, 762, 990, 806], fill=(64, 68, 78))
    for k in range(3):
        d.line([950 + k * 15, 806, 946 + k * 15, 840], fill=(150, 154, 162),
               width=5)
    glow(img, 960, 260, 400, (240, 248, 255), 60)
    return img


def yakusho() -> Image.Image:
    """役所。この回の敵。灰と石で人の気配を消す。"""
    img = vgrad((W, H), (78, 80, 88), (54, 56, 62)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 820, (92, 90, 88), (66, 64, 64))
    for c in range(4):
        x = 200 + c * 470
        d.rectangle([x, 90, x + 118, 820], fill=(110, 108, 104))
        d.rectangle([x - 20, 90, x + 138, 140], fill=(126, 124, 120))
    # カウンターと、積まれた書類
    d.rectangle([0, 820, W, 920], fill=(96, 84, 68))
    for k in range(11):
        d.polygon([(320 + k * 9, 820 - k * 13), (600 + k * 9, 810 - k * 13),
                   (604 + k * 9, 826 - k * 13), (324 + k * 9, 836 - k * 13)],
                  fill=(232, 230, 220) if k % 2 else (214, 212, 204))
    glow(img, 960, 300, 400, (146, 158, 182), 32)
    return img


def ima() -> Image.Image:
    img = vgrad((W, H), (240, 242, 246), (216, 220, 226)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 780, (194, 176, 152), (160, 144, 122))
    _window(img, d, 700, 160, 1230, 540, (170, 206, 242), (228, 238, 248))
    d = ImageDraw.Draw(img)
    # 棚に、古いラジオが1台
    d.rounded_rectangle([1320, 380, 1760, 780], radius=10, fill=(192, 180, 164))
    d.rectangle([1336, 560, 1744, 574], fill=(158, 148, 132))
    _radio(d, 1380, 556, 0.52)
    glow(img, 960, 300, 400, (255, 253, 246), 54)
    return img


PAINTERS = {
    "il_son_shirokiya": shirokiya,
    "il_son_kojo": kojo,
    "il_son_america": america,
    "il_son_yakusho": yakusho,
    "il_son_ima": ima,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
