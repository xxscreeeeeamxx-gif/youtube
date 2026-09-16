#!/usr/bin/env python3
"""オムロン・立石一真の再現ドラマ（tateishi-omron）用の背景4種。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
★商標に触れないため、製品の意匠・ロゴ・社名の表示は描かない。
★駅の絵は「改札の柵と通路」までにとどめる。**機械の中身は描かない**。
  このチャンネルには自動改札の仕組みを扱った回が別にあり、絵でも重複させない。
トーンの設計:
  熊本の町   … 夜明け前の青。新聞を配る時間。ここが出発点
  町工場     … 作業灯の白。タイマーを作る場所
  駅         … 朝の光と人の流れ。線の終点
  現代       … いちばん明るい

実行: PYTHONPATH=. python3 scripts/gen_omr_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402
from scripts.gen_yam_bgs import _building, _person, _desk  # noqa: E402


def _machiya(d, x0, x1, y, roof=(94, 82, 72), wall=(196, 182, 158)):
    """町家。瓦屋根と格子。熊本の町並みに使う。"""
    d.rectangle([x0, y - 300, x1, y], fill=wall, outline=(140, 126, 106), width=6)
    d.polygon([(x0 - 30, y - 300), (x1 + 30, y - 300), (x1 - 10, y - 380),
               (x0 + 10, y - 380)], fill=roof)
    for k in range(7):                       # 格子
        gx = x0 + 30 + k * (x1 - x0 - 60) / 7
        d.line([gx, y - 230, gx, y - 60], fill=(128, 110, 84), width=5)
    d.rectangle([x0 + 20, y - 250, x1 - 20, y - 236], fill=(128, 110, 84))


def _timer(d, x, y, s=1.0):
    """タイマー。丸い文字盤と、横のつまみ。**数字は描かない**。"""
    d.rounded_rectangle([x, y - 130 * s, x + 200 * s, y], radius=10 * s,
                        fill=(118, 112, 104), outline=(78, 74, 68),
                        width=max(2, int(6 * s)))
    cx, cy, r = x + 84 * s, y - 68 * s, 46 * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 236, 226),
              outline=(78, 74, 68), width=max(2, int(5 * s)))
    d.line([cx, cy, cx + r * 0.62, cy - r * 0.52], fill=(200, 60, 50),
           width=max(2, int(6 * s)))
    d.ellipse([x + 152 * s, y - 92 * s, x + 188 * s, y - 56 * s],
              fill=(86, 82, 78), outline=(56, 54, 50), width=max(2, int(4 * s)))


def _gate(d, x, y, s=1.0):
    """改札の柵。**通路と柵だけ**。機械の中身は描かない（別回と重複させない）。"""
    d.rounded_rectangle([x, y - 170 * s, x + 90 * s, y], radius=10 * s,
                        fill=(168, 176, 186), outline=(118, 126, 136),
                        width=max(2, int(6 * s)))
    d.rounded_rectangle([x + 12 * s, y - 150 * s, x + 78 * s, y - 120 * s],
                        radius=6 * s, fill=(96, 104, 114))
    d.rectangle([x + 20 * s, y - 108 * s, x + 70 * s, y - 96 * s],
                fill=(120, 190, 140))


def kumamoto() -> Image.Image:
    """熊本の町。夜明け前の青。新聞を配る時間。"""
    img = vgrad((W, H), (74, 88, 122), (126, 138, 164)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 830, (108, 112, 128), (82, 86, 100))
    _machiya(d, 60, 520, 830)
    _machiya(d, 560, 1020, 830, roof=(84, 74, 66), wall=(180, 168, 146))
    _machiya(d, 1060, 1520, 830, roof=(100, 88, 76), wall=(190, 176, 152))
    _machiya(d, 1560, 1900, 830, roof=(88, 78, 68), wall=(174, 162, 140))
    for x in (400, 1180):                    # 街灯
        d.line([x, 380, x, 830], fill=(70, 74, 88), width=7)
        d.ellipse([x - 26, 352, x + 26, 404], fill=(252, 238, 190))
        glow(img, x, 378, 200, (255, 232, 160), 78)
    d = ImageDraw.Draw(img)
    for k in range(4):                       # 配り終えた新聞
        d.rectangle([260 + k * 420, 812, 330 + k * 420, 836],
                    fill=(236, 232, 222), outline=(170, 166, 156), width=3)
    glow(img, 1780, 300, 460, (200, 190, 150), 52)   # 夜明けの気配
    return img


def koba() -> Image.Image:
    """大阪の町工場。作業灯の白。タイマーを作る場所。"""
    img = vgrad((W, H), (200, 200, 204), (172, 172, 178)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 820, (150, 150, 156), (116, 116, 122))
    for x in (90, 1700):
        d.rectangle([x, 0, x + 54, 820], fill=(140, 140, 146))
    _window(img, d, 620, 150, 1300, 480, (214, 222, 230), (240, 244, 248),
            frame=(118, 118, 124))
    d = ImageDraw.Draw(img)
    _desk(d, 180, 640, 840, 820, (124, 106, 80), (90, 76, 54))
    _timer(d, 240, 638, 1.0)
    _timer(d, 500, 638, 1.0)
    _desk(d, 1120, 660, 1660, 820, (124, 106, 80), (90, 76, 54))
    _timer(d, 1200, 658, 0.86)
    for k in range(3):                       # 吊り下げの作業灯
        x = 480 + k * 480
        d.line([x, 0, x, 190], fill=(96, 96, 102), width=6)
        d.ellipse([x - 40, 190, x + 40, 246], fill=(250, 246, 226))
        glow(img, x, 220, 260, (255, 250, 210), 88)
    return img


def eki() -> Image.Image:
    """駅の改札口。朝の光と人の流れ。柵と通路だけを描く。"""
    img = vgrad((W, H), (222, 230, 238), (192, 204, 216)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 840, (176, 182, 190), (140, 148, 158))
    d.rectangle([0, 0, W, 150], fill=(164, 172, 182))     # 天井
    for k in range(5):
        d.rectangle([180 + k * 380, 150, 260 + k * 380, 190], fill=(206, 214, 222))
    _window(img, d, 120, 220, 720, 520, (208, 224, 236), (240, 246, 250),
            frame=(128, 136, 146))
    d = ImageDraw.Draw(img)
    for k in range(4):                       # 改札の列
        _gate(d, 760 + k * 250, 838, 1.0)
    for k in range(5):                       # 通る人
        _person(d, 220 + k * 130, 838, 210, (92, 96, 106))
    glow(img, 400, 300, 420, (255, 252, 230), 76)
    return img


def ima() -> Image.Image:
    """現代。明るい駅前。いちばん明るい絵にする。"""
    img = vgrad((W, H), (216, 234, 246), (190, 214, 232)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 820, (182, 188, 194), (146, 152, 160))
    for k in range(4):
        _building(d, 70 + k * 470, 240 + (k % 2) * 80, 410 + k * 470, 820,
                  (178, 192, 204), (142, 156, 170))
    for k in range(3):
        _gate(d, 700 + k * 260, 900, 1.1)
    glow(img, 1680, 150, 420, (255, 250, 226), 92)
    return img


PAINTERS = {
    "il_omr_kumamoto": kumamoto,
    "il_omr_koba": koba,
    "il_omr_eki": eki,
    "il_omr_ima": ima,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
