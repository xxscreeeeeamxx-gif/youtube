#!/usr/bin/env python3
"""フラッシュメモリの誕生（masuoka-flash）用のイラスト背景8種を生成する。

実行: PYTHONPATH=. python3 scripts/gen_ms_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402


def _rgba(img):
    return img.convert("RGBA")


def takasaki() -> Image.Image:
    """1940年代の地方都市（生誕地）。"""
    img = _rgba(vgrad((W, H), (196, 176, 150), (232, 216, 190)))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 520), (420, 300), (860, 520)], fill=(150, 146, 132))
    d.polygon([(700, 520), (1180, 330), (1660, 520)], fill=(138, 134, 122))
    for x0, w_ in [(40, 300), (380, 260), (700, 320), (1080, 280), (1420, 340)]:
        d.rectangle([x0, 520, x0 + w_, 800], fill=(112, 88, 68))
        d.polygon([(x0 - 24, 520), (x0 + w_ // 2, 420), (x0 + w_ + 24, 520)], fill=(74, 60, 48))
        for wx in range(x0 + 36, x0 + w_ - 36, 104):
            d.rectangle([wx, 580, wx + 58, 648], fill=(232, 206, 148))
    d.rectangle([0, 800, W, H], fill=(150, 132, 106))
    d.rectangle([0, 800, W, 818], fill=(126, 110, 88))
    return img


def lab() -> Image.Image:
    """大学の研究室（1960年代）。"""
    img = _rgba(vgrad((W, H), (86, 92, 86), (58, 64, 60)))
    d = ImageDraw.Draw(img)
    d.rectangle([80, 140, 760, 560], fill=(52, 60, 56), outline=(120, 128, 120), width=8)
    for i in range(4):
        y = 200 + i * 90
        d.rectangle([110, y, 730, y + 12], fill=(96, 104, 98))
        for x in range(140, 700, 84):
            d.rectangle([x, y - 54, x + 56, y], fill=(150, 142, 118),
                        outline=(90, 96, 90), width=4)
    d.rectangle([1180, 160, 1800, 500], fill=(120, 146, 168))
    d.rectangle([1480, 160, 1500, 500], fill=(74, 80, 76))
    d.rectangle([1180, 322, 1800, 342], fill=(74, 80, 76))
    d.rectangle([0, 760, W, H], fill=(96, 78, 58))
    d.rectangle([0, 738, W, 772], fill=(116, 96, 72))
    d.rectangle([820, 620, 1120, 760], fill=(60, 66, 62), outline=(120, 128, 120), width=6)
    d.ellipse([880, 646, 1060, 700], fill=(150, 200, 180))
    return img


def lab2() -> Image.Image:
    """企業の設計室（1980年代・図面と端末）。"""
    img = _rgba(vgrad((W, H), (72, 78, 92), (48, 54, 66)))
    d = ImageDraw.Draw(img)
    for i, x0 in enumerate([70, 470, 870, 1270]):
        d.rectangle([x0, 150, x0 + 320, 470], fill=(238, 236, 226),
                    outline=(120, 126, 140), width=7)
        for gy in range(180, 460, 34):
            d.line([(x0 + 14, gy), (x0 + 306, gy)], fill=(198, 202, 214), width=2)
        d.rectangle([x0 + 40, 200, x0 + 150, 300], outline=(70, 90, 160), width=5)
        d.rectangle([x0 + 170, 240, x0 + 280, 400], outline=(160, 70, 70), width=5)
    d.rectangle([0, 720, W, H], fill=(92, 74, 58))
    d.rectangle([0, 700, W, 732], fill=(112, 92, 70))
    d.rounded_rectangle([760, 520, 1120, 720], radius=12, fill=(52, 58, 70),
                        outline=(140, 146, 160), width=7)
    d.rectangle([790, 548, 1090, 668], fill=(30, 44, 38))
    for ly in range(566, 660, 22):
        d.line([(806, ly), (1000, ly)], fill=(90, 220, 140), width=4)
    return img


def office() -> Image.Image:
    """会社の執務室（部長席・書棚）。"""
    img = _rgba(vgrad((W, H), (96, 92, 84), (66, 64, 58)))
    d = ImageDraw.Draw(img)
    d.rectangle([90, 150, 700, 640], fill=(104, 82, 60))
    for y in (280, 400, 520):
        d.rectangle([90, y, 700, y + 16], fill=(78, 60, 44))
        for x in range(120, 660, 42):
            d.rectangle([x, y - 96, x + 30, y], fill=[(150, 90, 70), (90, 110, 140),
                                                      (140, 130, 90), (110, 90, 120)][x % 4])
    d.rectangle([1200, 170, 1820, 500], fill=(140, 160, 180))
    d.rectangle([1500, 170, 1520, 500], fill=(84, 80, 74))
    d.rectangle([1200, 328, 1820, 348], fill=(84, 80, 74))
    d.rectangle([0, 740, W, H], fill=(88, 68, 50))
    d.rectangle([0, 716, W, 752], fill=(108, 86, 64))
    d.rectangle([820, 620, 1180, 740], fill=(120, 96, 70), outline=(80, 62, 44), width=6)
    d.rectangle([870, 596, 1010, 624], fill=(240, 238, 228))
    return img


def conf() -> Image.Image:
    """国際学会の会場（暗い客席とスクリーン）。"""
    img = _rgba(vgrad((W, H), (30, 34, 48), (18, 22, 34)))
    d = ImageDraw.Draw(img)
    d.rectangle([230, 90, 1690, 560], fill=(226, 230, 240), outline=(90, 96, 116), width=9)
    d.rectangle([300, 150, 1100, 190], fill=(70, 90, 150))
    d.rectangle([300, 230, 1420, 262], fill=(180, 186, 200))
    d.rectangle([300, 286, 1300, 318], fill=(180, 186, 200))
    for i in range(5):
        d.rectangle([300 + i * 230, 380, 300 + i * 230 + 170, 500], fill=(150, 170, 200))
    glow(img, 960, 320, 520, (200, 220, 255), alpha=42)
    for row, y in enumerate([640, 700]):
        for x in range(60, 1900, 150):
            d.ellipse([x, y, x + 92, y + 78], fill=(24, 28, 42))
            d.ellipse([x + 16, y - 34, x + 76, y + 26], fill=(30, 36, 52))
    return img


def court() -> Image.Image:
    """米国の法廷（証言台と傍聴席）。"""
    img = _rgba(vgrad((W, H), (86, 68, 54), (58, 46, 38)))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 300], fill=(96, 76, 58))
    for x in range(0, W, 220):
        d.rectangle([x, 0, x + 14, 300], fill=(72, 56, 42))
    d.rectangle([560, 60, 1360, 300], fill=(78, 60, 46), outline=(120, 96, 72), width=8)
    d.ellipse([880, 100, 1040, 260], fill=(150, 124, 96))
    d.rectangle([300, 380, 1620, 560], fill=(112, 88, 66), outline=(74, 58, 44), width=8)
    d.rectangle([700, 300, 1220, 400], fill=(96, 76, 58), outline=(74, 58, 44), width=7)
    d.rectangle([0, 700, W, H], fill=(70, 56, 44))
    for x in range(80, 1900, 260):
        d.rectangle([x, 600, x + 200, 700], fill=(90, 72, 56), outline=(64, 50, 38), width=5)
    return img


def kaden() -> Image.Image:
    """家電の研究所（試作カメラと工具）。"""
    img = _rgba(vgrad((W, H), (78, 96, 106), (54, 68, 78)))
    d = ImageDraw.Draw(img)
    d.rectangle([100, 150, 780, 560], fill=(210, 214, 222), outline=(120, 128, 142), width=8)
    for i, y in enumerate([200, 320, 440]):
        d.rectangle([120, y, 760, y + 14], fill=(150, 156, 170))
        for x in range(150, 720, 130):
            d.rounded_rectangle([x, y - 74, x + 96, y], radius=8, fill=(70, 76, 90))
            d.ellipse([x + 26, y - 58, x + 70, y - 16], fill=(150, 190, 220))
    d.rectangle([1260, 170, 1840, 480], fill=(150, 176, 196))
    d.rectangle([1550, 170, 1570, 480], fill=(84, 92, 104))
    d.rectangle([0, 740, W, H], fill=(96, 100, 112))
    d.rectangle([0, 716, W, 752], fill=(120, 124, 136))
    d.rounded_rectangle([820, 596, 1160, 740], radius=14, fill=(56, 60, 72),
                        outline=(140, 146, 162), width=7)
    d.ellipse([900, 630, 1010, 726], fill=(30, 36, 48), outline=(170, 176, 190), width=7)
    d.ellipse([926, 656, 984, 700], fill=(120, 170, 210))
    d.rectangle([1060, 616, 1120, 646], fill=(220, 200, 120))
    return img


def univ() -> Image.Image:
    """大学の教授室（1990年代後半）。"""
    img = _rgba(vgrad((W, H), (108, 100, 88), (74, 70, 62)))
    d = ImageDraw.Draw(img)
    d.rectangle([70, 130, 720, 620], fill=(112, 88, 64))
    for y in (250, 370, 490):
        d.rectangle([70, y, 720, y + 15], fill=(84, 64, 46))
        for x in range(100, 690, 38):
            d.rectangle([x, y - 92, x + 28, y], fill=[(140, 80, 66), (86, 106, 136),
                                                      (132, 124, 86), (104, 86, 116)][x % 4])
    d.rectangle([1180, 150, 1830, 520], fill=(150, 176, 200))
    d.rectangle([1500, 150, 1518, 520], fill=(86, 82, 74))
    d.rectangle([1180, 330, 1830, 348], fill=(86, 82, 74))
    d.rectangle([0, 750, W, H], fill=(92, 74, 56))
    d.rectangle([0, 726, W, 762], fill=(114, 92, 70))
    d.rectangle([800, 616, 1200, 750], fill=(118, 94, 68), outline=(84, 66, 48), width=6)
    d.rectangle([850, 588, 1000, 620], fill=(242, 240, 232))
    d.rounded_rectangle([1040, 560, 1180, 620], radius=8, fill=(60, 66, 78))
    return img


def now() -> Image.Image:
    """現代の部屋（スマホとメモリカード）。"""
    img = _rgba(vgrad((W, H), (44, 50, 68), (28, 32, 46)))
    d = ImageDraw.Draw(img)
    d.rectangle([1200, 130, 1840, 520], fill=(20, 26, 44))
    for bx, bh in [(1240, 130), (1330, 190), (1430, 100), (1540, 170), (1660, 140), (1760, 200)]:
        d.rectangle([bx, 520 - bh, bx + 66, 520], fill=(36, 44, 68))
        for wy in range(520 - bh + 16, 512, 32):
            d.rectangle([bx + 12, wy, bx + 30, wy + 15], fill=(238, 212, 140))
    d.rectangle([1190, 120, 1850, 140], fill=(72, 78, 98))
    d.rectangle([0, 748, W, H], fill=(92, 72, 54))
    d.rectangle([0, 724, W, 760], fill=(112, 88, 66))
    # スマホ
    d.rounded_rectangle([560, 520, 800, 748], radius=26, fill=(30, 34, 46),
                        outline=(150, 156, 172), width=7)
    d.rounded_rectangle([578, 546, 782, 726], radius=12, fill=(90, 150, 200))
    for gy in range(566, 700, 42):
        for gx in range(596, 760, 42):
            d.rounded_rectangle([gx, gy, gx + 30, gy + 30], radius=6, fill=(220, 232, 244))
    # メモリカードとUSB
    d.rounded_rectangle([880, 640, 1010, 748], radius=8, fill=(60, 66, 82),
                        outline=(150, 156, 172), width=5)
    d.rectangle([900, 664, 990, 700], fill=(200, 170, 70))
    d.rounded_rectangle([1060, 660, 1140, 748], radius=8, fill=(46, 50, 62),
                        outline=(150, 156, 172), width=5)
    d.rectangle([1076, 634, 1124, 664], fill=(180, 186, 200))
    return img


PAINTERS = {
    "il_ms_takasaki": takasaki,
    "il_ms_lab": lab,
    "il_ms_lab2": lab2,
    "il_ms_office": office,
    "il_ms_conf": conf,
    "il_ms_court": court,
    "il_ms_kaden": kaden,
    "il_ms_univ": univ,
    "il_ms_now": now,
    "il_ms_room": now,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
