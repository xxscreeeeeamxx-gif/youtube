#!/usr/bin/env python3
"""蚊取り線香の誕生・上山英一郎回（49_蚊取り線香の誕生 / slug=mosquito-coil）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針は東京タワー回（gen_naito_bgs.py）と同じ。
実在メーカーの商標（鶏のマーク・箱の意匠）は描かない。

実行: PYTHONPATH=. python scripts/gen_katori_bgs.py [名前...]
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, glow, hanging_bulb, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)


def _d(img):
    return ImageDraw.Draw(img)


def _glow(img, cx, cy, r, color, alpha=110):
    """glow() は RGBA に合成するので、変換した結果を貼り戻す必要がある。"""
    rgba = img.convert("RGBA")
    glow(rgba, cx, cy, r, color, alpha)
    img.paste(rgba.convert("RGB"), (0, 0))


def _window(d, x0, y0, x1, y1, sky=(150, 186, 214), frame=(70, 62, 56)):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


def _coil(d, cx, cy, r, width=10, col=(70, 110, 70), turns=4.2):
    """渦巻きの線香。外から内へ、アルキメデス螺旋で描く。"""
    pts = []
    n = 240
    for i in range(n + 1):
        t = i / n
        ang = t * turns * 2 * math.pi
        rr = r * (1 - t * 0.86)
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang) * 0.9))
    d.line(pts, fill=col, width=width, joint="curve")


def _mikan_tree(d, x, base_y, s=1.0):
    d.rectangle([x - 8 * s, base_y - 70 * s, x + 8 * s, base_y], fill=(100, 78, 54))
    d.ellipse([x - 70 * s, base_y - 170 * s, x + 70 * s, base_y - 50 * s], fill=(62, 110, 60))
    for dx, dy in ((-30, -120), (20, -140), (35, -95), (-10, -85), (-45, -90)):
        d.ellipse([x + dx * s - 10 * s, base_y + dy * s - 10 * s,
                   x + dx * s + 10 * s, base_y + dy * s + 10 * s], fill=(240, 150, 40))


# ------------------------------------------------------------ 現代
def ima():
    """夏の夜の部屋。床に蚊取り線香、窓の外は暗い。"""
    img = base((70, 72, 96), (46, 46, 66))
    d = _d(img)
    tatami_floor(img, FLOOR)
    _window(d, 740, 150, 1180, 520, sky=(28, 34, 60), frame=(60, 52, 48))
    d.ellipse([900, 240, 930, 270], fill=(236, 230, 190))              # 月
    d.rectangle([1320, 560, 1760, 620], fill=(120, 96, 70))             # 扇風機の台
    d.ellipse([1420, 380, 1640, 600], outline=(200, 200, 206), width=8)
    d.ellipse([880, 820, 1040, 870], fill=(150, 150, 156))              # 線香皿
    _coil(d, 960, 842, 70, width=6)
    _glow(img, 1020, 836, 30, (255, 150, 60), 120)
    hanging_bulb(img, 480, warm=True, ly=40)
    return img


# ------------------------------------------------------------ 有田・少年期
def mikan():
    """有田のミカン山。段々畑。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 204, 230), (214, 220, 200)), (0, 0))
    d = _d(img)
    d.polygon([(0, 420), (700, 240), (1400, 300), (W, 380), (W, H), (0, H)], fill=(120, 146, 96))
    for k, y in enumerate(range(460, H, 130)):                           # 石垣の段
        d.rectangle([0, y, W, y + 18], fill=(170, 160, 140))
        for x in range(80 + (k % 2) * 90, W, 220):
            _mikan_tree(d, x, y, 0.8)
    return img


def juku():
    """慶應義塾の洋風の教室。"""
    img = base((222, 214, 196), (190, 180, 162))
    d = _d(img)
    wood_floor(img, FLOOR, col=(126, 96, 70), line=(106, 80, 58))
    _window(d, 120, 160, 520, 560, sky=(186, 206, 222))
    _window(d, 1400, 160, 1800, 560, sky=(186, 206, 222))
    d.rectangle([640, 170, 1280, 520], fill=(50, 60, 56), outline=(96, 76, 56), width=12)
    for y in (250, 330, 410):
        d.line([(700, y), (1140, y)], fill=(200, 206, 200), width=4)
    for x in range(200, 1800, 300):                                    # 机
        d.rectangle([x, 760, x + 200, 790], fill=(140, 108, 76))
    return img


def ie():
    """明治の商家の座敷。上山家。"""
    img = base((204, 188, 160), (170, 152, 126))
    d = _d(img)
    tatami_floor(img, FLOOR)
    d.rectangle([380, 170, 1160, 640], fill=(226, 216, 196), outline=(110, 90, 70), width=10)
    for gx in range(480, 1160, 130):
        d.line([(gx, 170), (gx, 640)], fill=(170, 150, 124), width=5)
    d.rectangle([1320, 520, 1760, 640], fill=(110, 84, 58))            # 帳場机
    d.rectangle([1360, 460, 1560, 520], fill=(236, 230, 214))          # 帳面
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def hatake():
    """除虫菊の畑。白い花が一面に咲く。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (174, 206, 230), (220, 222, 208)), (0, 0))
    d = _d(img)
    d.polygon([(0, 480), (800, 400), (W, 460), (W, H), (0, H)], fill=(96, 140, 80))
    for row, y in enumerate(range(520, H, 50)):
        r = 5 + row * 1.6
        for x in range(int((row * 37) % 60), W, int(26 + row * 6)):
            d.ellipse([x - r, y - r, x + r, y + r], fill=(248, 248, 240))
            d.ellipse([x - r * 0.35, y - r * 0.35, x + r * 0.35, y + r * 0.35], fill=(240, 200, 60))
    return img


def nouka():
    """農家の庭先。種を配りに行く場面。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (176, 204, 226), (214, 214, 198)), (0, 0))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(170, 150, 110))
    d.rectangle([1100, 300, 1820, 700], fill=(120, 96, 72), outline=(90, 72, 54), width=6)
    d.polygon([(1040, 320), (1460, 160), (1880, 320)], fill=(150, 130, 90))
    d.rectangle([1360, 460, 1560, 700], fill=(70, 56, 42))
    for x in (200, 420):
        d.rectangle([x, 520, x + 16, 700], fill=(100, 78, 54))
        d.ellipse([x - 90, 360, x + 106, 560], fill=(96, 130, 80))
    return img


def yado():
    """東京・本郷の宿の部屋。夜、行灯。"""
    img = base((120, 100, 80), (80, 66, 54))
    d = _d(img)
    tatami_floor(img, FLOOR)
    d.rectangle([380, 170, 1160, 620], fill=(206, 190, 160), outline=(100, 80, 60), width=10)
    d.rectangle([1380, 560, 1480, 720], fill=(236, 214, 150), outline=(120, 96, 64), width=6)  # 行灯
    _glow(img, 1430, 640, 170, (255, 210, 130), 80)
    for k in range(5):                                                  # 線香の束
        d.rectangle([700 + k * 14, 700, 706 + k * 14, 820], fill=(120, 150, 100))
    return img


def koba():
    """線香の作業場。棚に乾かす線香、金網。"""
    img = base((196, 184, 164), (156, 144, 126))
    d = _d(img)
    wood_floor(img, FLOOR, col=(118, 92, 66), line=(96, 74, 52))
    for k, y in enumerate((260, 400, 540)):                             # 乾燥の金網棚
        d.rectangle([140, y, 900, y + 12], fill=(110, 90, 70))
        for x in range(160, 900, 36):
            d.line([(x, y - 60), (x, y)], fill=(150, 150, 156), width=2)
        for x in range(200, 860, 140):
            _coil(d, x, y - 30, 40, width=5, col=(96, 130, 84), turns=3)
    d.rectangle([1100, 640, 1800, 690], fill=(150, 116, 84))            # 作業台
    for k in range(8):
        d.rectangle([1150 + k * 70, 600, 1160 + k * 70, 640], fill=(96, 130, 84))
    hanging_bulb(img, 1400, warm=True, ly=40)
    return img


def _sticks(d, x0, y, n, col=(96, 130, 84)):
    """棒状の線香の束。渦巻きが生まれる前の場面で使う。"""
    for k in range(n):
        d.rectangle([x0 + k * 12, y - 90, x0 + k * 12 + 5, y], fill=col)


def koba0():
    """棒状の線香を作っていたころの作業場。棚には棒の束だけ。"""
    img = base((196, 184, 164), (156, 144, 126))
    d = _d(img)
    wood_floor(img, FLOOR, col=(118, 92, 66), line=(96, 74, 52))
    for y in (300, 440, 580):
        d.rectangle([140, y, 900, y + 12], fill=(110, 90, 70))
        for x in range(180, 860, 130):
            _sticks(d, x, y, 7)
    d.rectangle([1100, 640, 1800, 690], fill=(150, 116, 84))
    for k in range(8):
        d.rectangle([1150 + k * 70, 600, 1160 + k * 70, 640], fill=(96, 130, 84))
    hanging_bulb(img, 1400, warm=True, ly=40)
    return img


def mise0():
    """棒状の線香を売っていたころの店先。"""
    img = base((224, 210, 184), (192, 176, 150))
    d = _d(img)
    wood_floor(img, FLOOR, col=(128, 96, 66), line=(106, 80, 54))
    d.rectangle([0, 110, W, 260], fill=(70, 84, 94))
    for x in range(120, W, 260):
        d.line([(x, 110), (x, 260)], fill=(52, 64, 72), width=6)
    for sy in (440, 620):
        d.rectangle([140, sy, 900, sy + 20], fill=(112, 88, 64))
        for x in range(170, 860, 110):
            _sticks(d, x, sy, 6)
    d.rectangle([1120, 640, 1800, 690], fill=(150, 118, 84))
    return img


def niwa():
    """家の庭と蔵。夏の夕方。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (236, 200, 150), (200, 180, 150)), (0, 0))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(150, 136, 104))
    d.rectangle([1200, 260, 1760, 700], fill=(236, 230, 214), outline=(150, 140, 120), width=6)  # 蔵
    d.polygon([(1150, 280), (1480, 150), (1810, 280)], fill=(80, 80, 86))
    d.rectangle([1200, 560, 1760, 700], fill=(80, 80, 86))
    for x in (160, 420, 700):
        d.ellipse([x - 70, 600, x + 70, 720], fill=(100, 130, 80))    # 植え込み
    for x in range(100, 1100, 90):                                     # 飛び石
        d.ellipse([x, 780 + (x % 3) * 10, x + 60, 810 + (x % 3) * 10], fill=(170, 164, 150))
    return img


def mise():
    """明治の店先。棚に渦巻きの線香の束が並ぶ（箱の意匠は描かない）。"""
    img = base((224, 210, 184), (192, 176, 150))
    d = _d(img)
    wood_floor(img, FLOOR, col=(128, 96, 66), line=(106, 80, 54))
    d.rectangle([0, 110, W, 260], fill=(70, 84, 94))                    # 暖簾
    for x in range(120, W, 260):
        d.line([(x, 110), (x, 260)], fill=(52, 64, 72), width=6)
    for sy in (440, 620):
        d.rectangle([140, sy, 900, sy + 20], fill=(112, 88, 64))
        for x in range(190, 880, 120):
            _coil(d, x, sy - 40, 38, width=5, col=(96, 130, 84), turns=3)
    d.rectangle([1120, 640, 1800, 690], fill=(150, 118, 84))
    return img


def uzu():
    """図解用。暗い地に大きな渦巻き。仕組みの章で使う。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (30, 36, 44), (18, 22, 28)), (0, 0))
    d = _d(img)
    _coil(d, 960, 520, 330, width=26, col=(88, 132, 86), turns=4.4)
    _glow(img, 1290, 520, 70, (255, 140, 50), 150)
    return img


def shiryo():
    """新聞・書類の面。論争の章で使う。"""
    img = base((238, 234, 224), (212, 206, 194))
    d = _d(img)
    d.rectangle([180, 90, 1740, 990], fill=(250, 248, 242), outline=(168, 160, 146), width=8)
    d.rectangle([240, 150, 1680, 170], fill=(120, 112, 100))
    for y in range(230, 950, 46):
        w = 1440 if (y // 46) % 5 else 900
        d.rectangle([240, y, 240 + w, y + 18], fill=(196, 190, 178))
    return img


LOCATIONS = {
    "kt_ima": ima, "kt_mikan": mikan, "kt_juku": juku, "kt_ie": ie, "kt_hatake": hatake,
    "kt_nouka": nouka, "kt_yado": yado, "kt_koba": koba, "kt_niwa": niwa, "kt_mise": mise,
    "kt_uzu": uzu, "kt_shiryo": shiryo, "kt_koba0": koba0, "kt_mise0": mise0,
}

CARDS = ["1862", "1886", "1890", "1895", "1902", "1910"]


def year_card(text: str) -> Image.Image:
    """黒地に年号だけのカード。キャラと同居させない単独シーンで使う。"""
    img = Image.new("RGB", (W, H), (18, 18, 20))
    d = _d(img)
    from ytf.config import Config, resolve_font
    Config.load()
    font = ImageFont.truetype(resolve_font("w9"), 150)
    bb = d.textbbox((0, 0), text, font=font)
    d.text(((W - (bb[2] - bb[0])) // 2, (H - (bb[3] - bb[1])) // 2 - 40),
           text, font=font, fill=(238, 234, 226))
    d.line([(W // 2 - 220, H // 2 + 130), (W // 2 + 220, H // 2 + 130)],
           fill=(150, 146, 138), width=4)
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for y in CARDS:
        if only and f"kt_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"kt_card_{y}.png")
        print(f"生成完了: kt_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
