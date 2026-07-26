#!/usr/bin/env python3
"""新幹線×カワセミ再現ドラマ（shinkansen-bird）用のイラスト背景9種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_sb_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402

STEEL = (120, 126, 138)


def _nose(d, x0, y, ln=760, h=150, col=(210, 216, 226), win=(60, 70, 90)):
    """500系風の長いノーズ（左向き先頭+車体）。"""
    d.polygon([(x0, y), (x0 + ln, y - h), (x0 + ln + 600, y - h), (x0 + ln + 600, y),
               ], fill=col)
    d.polygon([(x0, y), (x0 + ln, y - h), (x0 + ln, y)], fill=col)
    # 窓帯とコックピット
    d.polygon([(x0 + ln * 0.55, y - h * 0.62), (x0 + ln * 0.8, y - h * 0.92),
               (x0 + ln * 0.98, y - h * 0.92), (x0 + ln * 0.72, y - h * 0.5)], fill=win)
    for k in range(5):
        d.rounded_rectangle([x0 + ln + 80 + k * 110, y - h * 0.72,
                             x0 + ln + 150 + k * 110, y - h * 0.42], radius=8, fill=win)
    # 青帯
    d.rectangle([x0 + ln, y - 26, x0 + ln + 600, y - 8], fill=(70, 90, 160))
    d.line([x0, y, x0 + ln + 600, y], fill=(90, 96, 108), width=6)


def homu_now() -> Image.Image:
    """現代の新幹線ホーム（フック/現代/締め）。500系風ノーズ。"""
    img = vgrad((W, H), (214, 224, 234), (238, 242, 246)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 屋根と柱
    d.rectangle([0, 0, W, 84], fill=(96, 104, 118))
    for k in range(4):
        d.rectangle([180 + k * 500, 84, 216 + k * 500, 560], fill=(150, 158, 170))
    # 電光掲示板
    d.rounded_rectangle([780, 150, 1240, 240], radius=10, fill=(30, 34, 44))
    d.rectangle([810, 175, 1000, 215], fill=(90, 200, 120))
    _floor(d, 640, (206, 208, 212), (182, 184, 190))
    _nose(d, 120, 630, col=(214, 220, 230))
    # ホーム端の点字ブロック風の帯
    d.rectangle([0, 660, W, 700], fill=(232, 198, 80))
    d.rectangle([0, 700, W, H], fill=(196, 198, 204))
    for k in range(6):
        d.line([260 + k * 300, 700, 260 + k * 300, H], fill=(176, 178, 184), width=6)
    return img


def kaigi() -> Image.Image:
    """JR西日本の会議室（計画始動）。"""
    img = vgrad((W, H), (86, 92, 104), (62, 68, 80)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (96, 90, 82), (74, 70, 64))
    _window(img, d, 1420, 130, 1840, 520, (150, 176, 200), (196, 214, 228), (80, 84, 96))
    # ホワイトボード（速度グラフ）
    d.rounded_rectangle([220, 150, 900, 560], radius=10, fill=(236, 238, 242))
    d.rectangle([220, 150, 900, 190], fill=(190, 194, 202))
    d.line([300, 500, 820, 500], fill=(120, 126, 138), width=5)
    d.line([300, 500, 300, 240], fill=(120, 126, 138), width=5)
    d.line([300, 480, 480, 420, ], fill=(90, 140, 220), width=7)
    d.line([480, 420, 700, 300], fill=(90, 140, 220), width=7)
    d.line([700, 300, 820, 250], fill=(220, 90, 90), width=7)
    # 長机
    d.rounded_rectangle([420, 620, 1500, int(H * 0.78)], radius=10, fill=(116, 92, 66))
    d.rectangle([420, 620, 1500, 656], fill=(96, 76, 54))
    for k in range(3):
        d.rectangle([520 + k * 300, 560, 720 + k * 300, 600], fill=(228, 230, 234))
    return img


def tonneru() -> Image.Image:
    """トンネル出口と沿線の民家（ドン問題）。"""
    img = vgrad((W, H), (150, 176, 200), (206, 218, 228)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 山
    d.polygon([(0, 620), (500, 180), (1100, 620)], fill=(110, 140, 100))
    d.polygon([(700, 620), (1300, 260), (1920, 620)], fill=(90, 120, 86))
    # トンネル坑口
    d.ellipse([340, 330, 700, 700], fill=(50, 46, 50))
    d.rectangle([340, 520, 700, 620], fill=(50, 46, 50))
    d.arc([330, 320, 710, 710], 180, 360, fill=(180, 184, 190), width=16)
    # 線路
    d.polygon([(430, 620), (610, 620), (760, H), (240, H)], fill=(120, 116, 110))
    d.line([470, 640, 330, H], fill=(90, 92, 100), width=10)
    d.line([575, 640, 690, H], fill=(90, 92, 100), width=10)
    # 民家（沿線）
    for bx in (1180, 1500):
        d.rectangle([bx, 470, bx + 240, 620], fill=(222, 214, 196))
        d.polygon([(bx - 20, 470), (bx + 120, 380), (bx + 260, 470)], fill=(150, 100, 80))
        d.rectangle([bx + 40, 520, bx + 110, 600], fill=(140, 170, 200))
    _floor(d, 620, (150, 160, 130), (126, 136, 110))
    return img


def lab() -> Image.Image:
    """技術研究室（図面・模型・計算）。"""
    img = vgrad((W, H), (72, 78, 92), (52, 58, 70)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (88, 84, 78), (66, 62, 58))
    _window(img, d, 180, 120, 600, 480, (150, 176, 200), (200, 216, 230), (80, 84, 96))
    # 製図板（ノーズの図面）
    d.rounded_rectangle([720, 200, 1360, 560], radius=8, fill=(238, 240, 244))
    d.rectangle([720, 200, 1360, 236], fill=(190, 194, 202))
    d.line([780, 480, 1040, 340], fill=(90, 140, 220), width=5)
    d.line([1040, 340, 1300, 330], fill=(90, 140, 220), width=5)
    d.line([780, 480, 1300, 480], fill=(150, 156, 168), width=4)
    for k in range(4):
        d.line([880 + k * 110, 480, 880 + k * 110, 380], fill=(200, 204, 212), width=2)
    # 机上の模型（小さなノーズ）
    d.rounded_rectangle([1480, 500, 1860, 560], radius=8, fill=(116, 92, 66))
    _nose(d, 1500, 552, ln=180, h=44, col=(214, 220, 230))
    # 資料棚
    d.rectangle([40, 260, 240, int(H * 0.77)], fill=(96, 88, 78))
    for r in range(5):
        d.rectangle([56, 290 + r * 130, 224, 380 + r * 130], fill=(150, 142, 128))
    return img


def shaken() -> Image.Image:
    """試験走行の現場（線路と計測機器）。"""
    img = vgrad((W, H), (130, 160, 190), (196, 210, 224)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 遠景の架線柱
    for k in range(6):
        x = 140 + k * 330
        d.line([x, 240, x, 620], fill=(110, 116, 128), width=10)
        d.line([x - 60, 280, x + 60, 280], fill=(110, 116, 128), width=8)
    d.line([0, 300, W, 300], fill=(90, 96, 108), width=4)
    _floor(d, 620, (160, 150, 130), (136, 128, 112))
    # 線路2本
    for y0, sp in ((700, 60), (850, 90)):
        d.rectangle([0, y0, W, y0 + 16], fill=(96, 98, 106))
        d.rectangle([0, y0 + sp, W, y0 + sp + 16], fill=(96, 98, 106))
        for x in range(0, W, 120):
            d.rectangle([x, y0 - 10, x + 70, y0 + sp + 26], fill=(120, 96, 66))
    # 計測機器のワゴン
    d.rounded_rectangle([1520, 460, 1860, 620], radius=10, fill=(90, 96, 110))
    d.rectangle([1550, 490, 1690, 560], fill=(120, 200, 160))
    d.ellipse([1720, 490, 1780, 550], fill=(220, 200, 90))
    return img


def kawa() -> Image.Image:
    """川辺（カワセミ観察・昼）。"""
    img = vgrad((W, H), (150, 200, 230), (210, 232, 240)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    glow(img, 300, 180, 150, (255, 244, 200), 70)
    d.ellipse([250, 130, 350, 230], fill=(255, 248, 214))
    # 対岸の緑
    d.rectangle([0, 480, W, 620], fill=(120, 160, 100))
    for k in range(7):
        d.ellipse([k * 300 - 60, 420, k * 300 + 220, 560], fill=(104, 146, 90))
    # 川面
    d.rectangle([0, 620, W, H], fill=(110, 160, 200))
    for k in range(14):
        d.line([80 + k * 140, 700 + (k % 4) * 70, 200 + k * 140, 700 + (k % 4) * 70],
               fill=(160, 200, 226), width=6)
    # 枝とカワセミ（青い小鳥）
    d.line([1420, 300, 1780, 420], fill=(110, 84, 56), width=16)
    d.ellipse([1560, 300, 1650, 372], fill=(60, 140, 220))
    d.ellipse([1622, 296, 1668, 338], fill=(60, 140, 220))
    d.polygon([(1664, 312), (1730, 320), (1664, 330)], fill=(220, 120, 60))
    d.ellipse([1636, 306, 1648, 318], fill=(30, 34, 44))
    d.ellipse([1580, 330, 1630, 366], fill=(230, 150, 90))
    return img


def mori() -> Image.Image:
    """夜の森（フクロウ観察）。"""
    img = vgrad((W, H), (26, 32, 52), (44, 52, 74)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    glow(img, 1600, 180, 140, (240, 240, 210), 80)
    d.ellipse([1540, 120, 1660, 240], fill=(240, 242, 220))
    # 木々のシルエット
    for k, bx in enumerate((100, 420, 820, 1200, 1700)):
        d.rectangle([bx, 300 + (k % 2) * 60, bx + 60, 760], fill=(34, 40, 54))
        d.ellipse([bx - 120, 160 + (k % 2) * 60, bx + 180, 420 + (k % 2) * 60],
                  fill=(40, 48, 64))
    _floor(d, 760, (36, 42, 56), (28, 34, 46))
    # 枝のフクロウ
    d.line([760, 420, 1150, 480], fill=(50, 42, 36), width=18)
    d.ellipse([900, 300, 1030, 452], fill=(150, 128, 100))
    d.ellipse([912, 296, 1018, 392], fill=(170, 148, 118))
    for ex in (936, 984):
        d.ellipse([ex - 16, 320, ex + 16, 352], fill=(240, 234, 210))
        d.ellipse([ex - 6, 330, ex + 6, 342], fill=(40, 36, 32))
    d.polygon([(954, 348), (966, 348), (960, 364)], fill=(220, 180, 90))
    return img


def eki_1997() -> Image.Image:
    """1997年の駅ホーム（500系デビュー・祝賀ムード）。"""
    img = vgrad((W, H), (226, 220, 206), (242, 238, 228)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W, 80], fill=(120, 112, 100))
    for k in range(4):
        d.rectangle([200 + k * 480, 80, 236 + k * 480, 560], fill=(170, 162, 148))
    # 祝賀の垂れ幕と旗
    d.rectangle([760, 120, 1180, 260], fill=(220, 80, 90))
    d.rectangle([790, 150, 1150, 230], fill=(240, 236, 226))
    for k in range(8):
        d.polygon([(200 + k * 220, 90), (240 + k * 220, 90), (220 + k * 220, 140)],
                  fill=(230, 110, 110) if k % 2 else (110, 140, 220))
    _floor(d, 640, (212, 206, 194), (188, 182, 170))
    _nose(d, 60, 630, col=(220, 226, 234))
    d.rectangle([0, 660, W, 700], fill=(226, 196, 90))
    d.rectangle([0, 700, W, H], fill=(202, 196, 184))
    return img


def kawa_yu() -> Image.Image:
    """夕暮れの川辺（名言の場）。"""
    img = vgrad((W, H), (250, 180, 110), (255, 220, 170)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    glow(img, 960, 300, 220, (255, 210, 130), 100)
    d.ellipse([880, 220, 1040, 380], fill=(255, 234, 180))
    # 山並みシルエット
    d.polygon([(0, 560), (400, 330), (820, 560)], fill=(150, 110, 90))
    d.polygon([(600, 560), (1200, 280), (1920, 560)], fill=(130, 96, 82))
    # 川面（夕色）
    d.rectangle([0, 560, W, H], fill=(220, 150, 100))
    for k in range(12):
        d.line([100 + k * 160, 640 + (k % 4) * 80, 240 + k * 160, 640 + (k % 4) * 80],
               fill=(255, 200, 140), width=6)
    # 手前の枝と鳥のシルエット
    d.line([1420, 360, 1820, 470], fill=(80, 56, 40), width=14)
    d.ellipse([1600, 360, 1680, 424], fill=(80, 56, 40))
    d.polygon([(1676, 380), (1730, 388), (1676, 396)], fill=(80, 56, 40))
    return img


PAINTERS = {
    "il_sb_homu": homu_now,
    "il_sb_kaigi": kaigi,
    "il_sb_tonneru": tonneru,
    "il_sb_lab": lab,
    "il_sb_shaken": shaken,
    "il_sb_kawa": kawa,
    "il_sb_mori": mori,
    "il_sb_eki": eki_1997,
    "il_sb_kawa_yu": kawa_yu,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
