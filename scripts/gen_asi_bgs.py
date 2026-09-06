#!/usr/bin/env python3
"""アシックス・鬼塚喜八郎の再現ドラマ（onitsuka-asics）用の背景5種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
★商標に配慮: 靴のストライプ意匠やロゴは描かない。一般的な形状のみ。
トーンの設計:
  焼け跡     … 彩度を落とす。ここが出発点
  体育館     … 木の床の温かい黄土色。タコの発見の章
  路上       … 朝の水色。マラソンの章
  工場       … 作業灯の白
  現代       … いちばん明るい

実行: PYTHONPATH=. python3 scripts/gen_asi_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402
from scripts.gen_yam_bgs import _building, _person, _desk  # noqa: E402


def _shoe(d, x, y, s=1.0, body=(238, 240, 244), sole=(70, 74, 84)):
    """運動靴を横から。意匠は付けず、輪郭と靴底だけにする。"""
    d.polygon([(x, y), (x + 300 * s, y), (x + 310 * s, y - 60 * s),
               (x + 210 * s, y - 110 * s), (x + 90 * s, y - 120 * s),
               (x + 20 * s, y - 70 * s)], fill=body,
              outline=(150, 152, 160), width=int(6 * s))
    d.rounded_rectangle([x - 10 * s, y - 26 * s, x + 316 * s, y + 14 * s],
                        radius=16 * s, fill=sole)
    # 靴底の吸盤（へこみ）
    for k in range(6):
        cx = x + 30 * s + k * 48 * s
        d.ellipse([cx - 14 * s, y - 14 * s, cx + 14 * s, y + 6 * s],
                  fill=(48, 52, 62), outline=(96, 100, 112), width=int(3 * s))
    for k in range(4):
        d.line([x + 90 * s + k * 34 * s, y - 108 * s,
                x + 120 * s + k * 34 * s, y - 66 * s],
               fill=(160, 164, 172), width=int(5 * s))


def _octopus(d, x, y, s=1.0):
    """タコの足。吸盤が並んでいるのが分かる形にする。"""
    pts = [(x, y)]
    for i in range(1, 12):
        pts.append((x + i * 30 * s, y - math.sin(i * 0.5) * 34 * s))
    d.line(pts, fill=(206, 96, 96), width=int(40 * s), joint="curve")
    for i, (px, py) in enumerate(pts):
        if i % 2:
            continue
        r = 13 * s
        d.ellipse([px - r, py - r + 8 * s, px + r, py + r + 8 * s],
                  fill=(240, 176, 176), outline=(170, 70, 70), width=int(4 * s))


def yakeato() -> Image.Image:
    img = vgrad((W, H), (176, 172, 164), (204, 198, 188)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 820, (152, 146, 138), (120, 116, 110))
    _building(d, 1400, 380, 1880, 820, (176, 170, 162), (140, 142, 148), 3, 5)
    # 焼け残りの柱
    for k, x in enumerate((220, 620, 1020)):
        d.rectangle([x, 300 + k * 60, x + 46, 820], fill=(140, 132, 124))
    # 靴の入った木箱
    for k in range(4):
        bx = 260 + (k % 2) * 200
        by = 820 - (k // 2) * 130
        d.rectangle([bx, by - 120, bx + 180, by], fill=(170, 140, 100),
                    outline=(126, 100, 66), width=6)
    _shoe(d, 900, 880, 0.62, (216, 212, 204), (110, 108, 108))
    img = Image.blend(img.convert("RGB"), img.convert("L").convert("RGB"),
                      0.40).convert("RGBA")
    return img


def taiikukan() -> Image.Image:
    """体育館。木の床。タコの発見はここでの相談から始まる。"""
    img = vgrad((W, H), (226, 210, 176), (206, 186, 148)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 740], fill=(214, 198, 168))
    # 高窓
    for k in range(5):
        x = 130 + k * 340
        d.rounded_rectangle([x, 130, x + 220, 420], radius=8,
                            fill=(206, 224, 238), outline=(168, 152, 122), width=7)
        d.line([x + 110, 130, x + 110, 420], fill=(168, 152, 122), width=6)
    # 木の床とライン
    d.rectangle([0, 740, W, H], fill=(214, 176, 116))
    for c in range(24):
        d.line([c * 84, 740, c * 84, H], fill=(198, 160, 102), width=4)
    d.line([0, 830, W, 830], fill=(226, 226, 224), width=9)
    d.arc([620, 760, 1300, 1100], 180, 360, fill=(226, 226, 224), width=9)
    # ゴールのリング
    d.rectangle([1560, 200, 1580, 460], fill=(140, 142, 150))
    d.rounded_rectangle([1460, 430, 1680, 560], radius=6, fill=(246, 246, 242),
                        outline=(160, 160, 158), width=7)
    d.ellipse([1520, 550, 1620, 590], outline=(214, 108, 40), width=10)
    glow(img, 500, 220, 340, (255, 244, 208), 66)
    return img


def road() -> Image.Image:
    """マラソンの路上。朝の水色。"""
    img = vgrad((W, H), (176, 212, 244), (232, 234, 224)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for base, col in ((560, (156, 178, 168)), (620, (132, 158, 146))):
        pts = [(0, base)]
        for i in range(9):
            pts.append((i * W / 8, base - 110 - 70 * math.sin(i * 1.5 + base)))
        pts += [(W, base), (W, H), (0, H)]
        d.polygon(pts, fill=col)
    _building(d, 60, 400, 380, 720, (206, 200, 190), (150, 168, 190), 3, 3)
    _building(d, 1560, 420, 1880, 720, (200, 194, 184), (146, 164, 188), 3, 3)
    d.rectangle([0, 700, W, H], fill=(120, 120, 126))
    for k in range(11):
        d.polygon([(k * 190 - 40, 900), (k * 190 + 70, 896),
                   (k * 190 + 74, 918), (k * 190 - 36, 922)],
                  fill=(236, 236, 232))
    # 沿道の人
    for i in range(10):
        _person(d, 140 + i * 190, 720 + (i % 3) * 10, 110, (92, 88, 96))
    _shoe(d, 700, 1000, 1.0)
    glow(img, 1500, 180, 400, (255, 250, 226), 84)
    return img


def kojo() -> Image.Image:
    img = vgrad((W, H), (218, 216, 210), (194, 192, 188)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 800], fill=(208, 206, 202)) 
    for k in range(5):
        x = k * 400
        d.polygon([(x, 250), (x + 400, 250), (x + 400, 110), (x + 200, 110)],
                  fill=(166, 164, 160))
        d.polygon([(x + 200, 110), (x + 400, 110), (x + 400, 250)],
                  fill=(194, 210, 224))
    _floor(d, 800, (162, 146, 122), (128, 116, 96))
    _desk(d, 200, 800, 840, 940, (132, 106, 74), (98, 78, 54))
    # 作業台に、靴型と型抜き
    for k in range(4):
        cx = 280 + k * 150
        d.rounded_rectangle([cx, 726, cx + 110, 800], radius=22,
                            fill=(196, 170, 132), outline=(140, 116, 80), width=5)
    _octopus(d, 1180, 700, 0.7)
    _shoe(d, 1360, 900, 0.86)
    glow(img, 700, 200, 340, (252, 250, 244), 48)
    return img


def ima() -> Image.Image:
    img = vgrad((W, H), (240, 242, 246), (216, 220, 226)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 780, (194, 176, 152), (160, 144, 122))
    _window(img, d, 700, 160, 1230, 540, (170, 206, 242), (228, 238, 248))
    d = ImageDraw.Draw(img)
    # 玄関に、靴が並んでいる
    d.rounded_rectangle([1300, 420, 1800, 800], radius=10, fill=(196, 184, 168))
    d.rectangle([1316, 600, 1784, 614], fill=(162, 152, 138))
    _shoe(d, 1340, 596, 0.5, (238, 240, 244), (70, 74, 84))
    _shoe(d, 1340, 790, 0.5, (232, 216, 196), (110, 96, 88))
    glow(img, 960, 300, 400, (255, 253, 246), 54)
    return img


PAINTERS = {
    "il_asi_yakeato": yakeato,
    "il_asi_taiikukan": taiikukan,
    "il_asi_road": road,
    "il_asi_kojo": kojo,
    "il_asi_ima": ima,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
