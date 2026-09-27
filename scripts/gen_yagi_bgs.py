#!/usr/bin/env python3
"""八木アンテナの誕生回（63_八木アンテナの誕生 / slug=yagi-uda-antenna）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針は食品サンプル回（gen_sample_bgs.py）と同じ。
実在の会社の商標（ロゴ・社名の文字）は描かない。

実行: PYTHONPATH=. python scripts/gen_yagi_bgs.py [名前...]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)
METAL = (170, 172, 180)
BRASS = (200, 170, 80)


def _d(img):
    return ImageDraw.Draw(img)


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


def _font(size):
    from ytf.config import Config, resolve_font
    Config.load()
    return ImageFont.truetype(resolve_font("w9"), size)


def _text_c(d, cx, y, t, size, fill):
    f = _font(size)
    bb = d.textbbox((0, 0), t, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y), t, font=f, fill=fill)


def _table(d, x0, x1, y, col=(150, 116, 80)):
    d.rectangle([x0, y, x1, y + 36], fill=col)
    d.rectangle([x0 + 20, y + 36, x0 + 40, y + 190], fill=tuple(int(c * 0.8) for c in col))
    d.rectangle([x1 - 40, y + 36, x1 - 20, y + 190], fill=tuple(int(c * 0.8) for c in col))


def _window(d, x0, y0, x1, y1, sky=(176, 210, 232), frame=(70, 62, 56)):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


def _yagi(d, x0, y, length, n=6, facing=1, col=METAL, w=4, scale=1.0):
    """横から見た八木アンテナ。facing=1 で右向き（導波器が右）。"""
    x1 = x0 + length * facing
    d.line([(x0, y), (x1, y)], fill=col, width=w + 2)                     # ブーム
    step = length / (n + 1)
    for k in range(n + 2):
        x = x0 + k * step * facing
        if k == 0:
            h = 46 * scale                                              # 反射器（長い）
        elif k == 1:
            h = 40 * scale                                              # 本体
        else:
            h = 34 * scale - k * 0.8 * scale                            # 導波器（短い）
        d.line([(x, y - h), (x, y + h)], fill=col, width=w)
    return x1


def _tube(d, cx, cy, s=1.0):
    """真空管。"""
    d.ellipse([cx - 22 * s, cy - 50 * s, cx + 22 * s, cy + 10 * s], fill=(220, 230, 240), outline=(120, 130, 140), width=3)
    d.rectangle([cx - 22 * s, cy - 20 * s, cx + 22 * s, cy + 30 * s], fill=(220, 230, 240), outline=(120, 130, 140), width=3)
    d.rectangle([cx - 26 * s, cy + 30 * s, cx + 26 * s, cy + 46 * s], fill=(60, 50, 40))
    d.ellipse([cx - 8 * s, cy - 20 * s, cx + 8 * s, cy - 4 * s], fill=(255, 190, 90))


def _meter(d, cx, cy, r=34):
    d.rectangle([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6], fill=(80, 60, 44))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(246, 240, 226), outline=(60, 50, 40), width=3)
    d.line([(cx, cy + r * 0.3), (cx + r * 0.6, cy - r * 0.5)], fill=(200, 40, 30), width=3)


def yane(facing=-1):
    """おばあちゃんの家の屋根。遠くに電波塔。facing=-1 は塔と逆向き。"""
    img = vgrad((W, H), (150, 196, 236), (214, 230, 240))
    d = _d(img)
    d.polygon([(1560, 760), (1620, 260), (1680, 760)], fill=(200, 80, 60))     # 遠くの電波塔
    for y in range(320, 760, 60):
        d.line([(1560 + (y - 260) * 0.12, y), (1680 - (y - 260) * 0.12, y)], fill=(240, 240, 240), width=4)
    d.polygon([(0, 760), (W, 760), (W, H), (0, H)], fill=(120, 110, 100))
    d.polygon([(300, 760), (960, 520), (1620, 760)], fill=(90, 70, 60))          # 屋根
    d.polygon([(420, 760), (960, 560), (1500, 760)], fill=(110, 86, 70))
    d.rectangle([950, 360, 962, 560], fill=(120, 120, 126))                     # マスト
    for k in range(4):                                                          # 塔から来る電波
        d.arc([1380 - k * 60, 200 - k * 30, 1560 + k * 20, 520 + k * 30], 150, 210, fill=(240, 160, 60), width=5)
    if facing < 0:
        _yagi(d, 1170, 360, 420, n=8, facing=-1, w=7, scale=1.4)
    else:
        _yagi(d, 750, 360, 420, n=8, facing=1, w=7, scale=1.4)
    return img


def yane2():
    return yane(facing=1)


def gakkou():
    """大正の中学校の職員室。"""
    img = _rgb(base((226, 214, 190), (206, 194, 170)))
    wood_floor(img, FLOOR, col=(140, 110, 80), line=(120, 94, 66))
    d = _d(img)
    d.rectangle([760, 150, 1160, 400], fill=(40, 70, 56), outline=(110, 80, 50), width=10)   # 黒板
    d.line([(800, 230), (1000, 230)], fill=(230, 230, 220), width=3)
    d.line([(800, 290), (1100, 290)], fill=(230, 230, 220), width=3)
    for x in (80, 1480):
        d.rectangle([x, 600, x + 360, 640], fill=(150, 116, 80))
        for k in range(4):
            d.rectangle([x + 40 + k * 70, 560, x + 90 + k * 70, 600], fill=(236, 228, 206), outline=(160, 150, 130))
    _table(d, 780, 1140, 640, col=(150, 116, 80))
    return img


def lab():
    """1920年代の大学の研究室。真空管の発振器、電流計、金属の棒。"""
    img = _rgb(base((222, 216, 200), (202, 196, 180)))
    wood_floor(img, FLOOR, col=(120, 96, 72), line=(100, 80, 60))
    d = _d(img)
    _window(d, 760, 110, 1160, 330, sky=(170, 196, 214))
    for x in (60, 1500):
        d.rectangle([x, 220, x + 360, 760], fill=(140, 110, 80))
        for r in range(4):
            d.rectangle([x, 330 + r * 110, x + 360, 342 + r * 110], fill=(110, 86, 62))
            for k in range(5):
                d.rectangle([x + 20 + k * 66, 272 + r * 110, x + 70 + k * 66, 330 + r * 110], fill=(90 + k * 20, 60, 50))
    _table(d, 740, 1180, 620, col=(110, 86, 62))
    d.rectangle([780, 520, 900, 620], fill=(70, 56, 44))                        # 発振器
    _tube(d, 840, 500, 0.9)
    _meter(d, 980, 570)                                                         # 電流計
    for k in range(3):                                                          # 金属の棒
        d.line([(1040 + k * 40, 540), (1060 + k * 40, 616)], fill=BRASS, width=6)
    return img


def jikken():
    """実験場。反射器と、真鍮の導波器をずらりと並べた列。"""
    img = _rgb(base((226, 222, 210), (206, 202, 190)))
    wood_floor(img, FLOOR, col=(130, 110, 90), line=(110, 92, 74))
    d = _d(img)
    d.rectangle([0, 80, W, 120], fill=(100, 90, 80))
    y = 470
    d.line([(640, y), (1280, y)], fill=(120, 110, 100), width=4)                 # 台の横木
    for k in range(12):
        x = 660 + k * 52
        h = 130 if k == 0 else (116 if k == 1 else 104)
        d.line([(x, y - h), (x, y + h)], fill=BRASS if k > 1 else METAL, width=6)
        d.line([(x, y + h), (x, 760)], fill=(110, 90, 70), width=3)             # 支柱
    _table(d, 700, 900, 640, col=(110, 86, 62))
    _tube(d, 760, 620, 0.7)
    _meter(d, 850, 612, 26)
    return img


def kaigan():
    """海の見える丘。受信機と、遠くに島。"""
    img = vgrad((W, H), (160, 200, 236), (220, 232, 240))
    d = _d(img)
    d.rectangle([0, 560, W, 700], fill=(80, 130, 170))                          # 海
    d.polygon([(1100, 560), (1200, 470), (1320, 560)], fill=(90, 120, 90))       # 島
    d.polygon([(0, 700), (W, 660), (W, H), (0, H)], fill=(110, 140, 80))         # 丘
    _table(d, 780, 1140, 640, col=(120, 96, 70))
    d.rectangle([820, 560, 960, 640], fill=(70, 56, 44))                         # 受信機
    _meter(d, 890, 600, 26)
    d.rectangle([1040, 380, 1048, 640], fill=(120, 120, 126))
    _yagi(d, 1000, 390, 150, n=4, facing=1, w=3, scale=0.6)
    return img


def zukai():
    """図解: 反射器・本体・導波器と、前へ進む電波。"""
    img = _rgb(base((244, 244, 240), (230, 230, 224)))
    d = _d(img)
    ink = (50, 56, 70)
    y = 470
    d.line([(700, y), (1220, y)], fill=ink, width=6)
    xs = [720, 800] + [880 + k * 70 for k in range(5)]
    hs = [150, 130] + [110 - k * 4 for k in range(5)]
    cols = [(90, 110, 170), (200, 60, 60)] + [(60, 140, 80)] * 5
    for x, h, c in zip(xs, hs, cols):
        d.line([(x, y - h), (x, y + h)], fill=c, width=10)
    d.line([(800, y + 130), (800, y + 200)], fill=(200, 60, 60), width=4)       # 給電線
    for k in range(3):                                                        # 電波
        d.arc([1160 + k * 40, y - 80 - k * 20, 1240 + k * 40, y + 80 + k * 20], -40, 40, fill=(240, 160, 60), width=6)
    _text_c(d, 720, 250, "反射器", 36, (90, 110, 170))
    _text_c(d, 800, 690, "本体", 36, (200, 60, 60))
    _text_c(d, 1020, 250, "導波器", 36, (60, 140, 80))
    return img


def zukai2():
    """黒板に描いた八木アンテナと、はてな。"""
    img = _rgb(base((226, 222, 210), (206, 202, 190)))
    wood_floor(img, FLOOR, col=(140, 120, 100), line=(120, 102, 84))
    d = _d(img)
    d.rectangle([640, 150, 1280, 560], fill=(40, 70, 56), outline=(110, 80, 50), width=12)
    _yagi(d, 740, 360, 400, n=6, facing=1, col=(236, 236, 226), w=5, scale=1.2)
    _text_c(d, 1200, 220, "？", 90, (236, 220, 120))
    return img


def kaijou():
    """1926年の学術会議の会場。演台と、アンテナの図のかかった黒板。"""
    img = _rgb(base((220, 212, 196), (196, 188, 172)))
    wood_floor(img, FLOOR, col=(120, 96, 72), line=(100, 80, 60))
    d = _d(img)
    d.rectangle([740, 110, 1180, 380], fill=(40, 70, 56), outline=(110, 80, 50), width=10)
    _yagi(d, 800, 250, 300, n=5, facing=1, col=(236, 236, 226), w=4, scale=0.9)
    for k in range(3):
        d.arc([1110 + k * 20, 200 - k * 10, 1150 + k * 20, 300 + k * 10], -40, 40, fill=(236, 220, 120), width=4)
    d.polygon([(1080, 520), (1180, 520), (1170, 760), (1090, 760)], fill=(120, 90, 70))   # 演台
    for r in range(3):
        for c in range(14):
            x = 60 + c * 140 + (r % 2) * 70
            d.ellipse([x, 800 + r * 70, x + 70, 870 + r * 70], fill=(70, 60, 56))
    return img


def oka():
    """松島の丘の上。無線の機械と、海に浮かぶ島々。"""
    img = vgrad((W, H), (170, 206, 236), (226, 236, 240))
    d = _d(img)
    d.rectangle([0, 540, W, 700], fill=(70, 120, 170))
    rnd = random.Random(4)
    for _ in range(9):
        x = rnd.uniform(0, W)
        w = rnd.uniform(60, 160)
        d.chord([x - w, 520, x + w, 580], 180, 360, fill=(70, 110, 70))
    d.polygon([(0, 720), (W, 690), (W, H), (0, H)], fill=(100, 130, 70))
    _table(d, 780, 1140, 640, col=(120, 96, 70))
    d.rectangle([800, 540, 980, 640], fill=(70, 56, 44))
    _tube(d, 850, 520, 0.7)
    _meter(d, 930, 590, 26)
    d.rectangle([1060, 360, 1068, 640], fill=(120, 120, 126))
    _yagi(d, 1000, 370, 170, n=4, facing=1, w=3, scale=0.6)
    return img


def singapore():
    """シンガポールの英軍陣地の跡。やしの木と、地面に落ちた手帳。"""
    img = vgrad((W, H), (200, 220, 230), (230, 226, 210))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(170, 150, 110))
    for x in (160, 1700):                                                    # やしの木
        d.rectangle([x, 300, x + 24, 700], fill=(110, 80, 50))
        for k in range(6):
            a = -math.pi / 2 + (k - 2.5) * 0.5
            d.line([(x + 12, 300), (x + 12 + 160 * math.cos(a), 300 + 90 * math.sin(a) + 60)], fill=(60, 120, 60), width=14)
    d.rectangle([700, 560, 1220, 700], fill=(140, 130, 110))                  # 砲座の跡
    d.rectangle([760, 520, 1160, 560], fill=(120, 110, 96))
    d.line([(900, 520), (1060, 420)], fill=(80, 80, 70), width=18)            # 壊れた砲身
    d.polygon([(900, 740), (1010, 730), (1020, 790), (908, 800)], fill=(90, 70, 50))   # 手帳
    d.line([(916, 750), (1000, 742)], fill=(200, 190, 170), width=3)
    return img


def sf():
    """サンフランシスコの坂の町。屋根という屋根にアンテナ。"""
    img = vgrad((W, H), (170, 206, 236), (226, 236, 240))
    d = _d(img)
    d.rectangle([0, 620, W, 700], fill=(80, 130, 170))                        # 湾
    rnd = random.Random(8)
    for row in range(3):
        for k in range(10):
            x = k * 200 + (row % 2) * 100 - 60
            y = 520 + row * 140
            w, h = 170, 140
            col = ((236, 226, 206), (220, 200, 190), (200, 214, 226), (240, 230, 180))[(k + row) % 4]
            d.rectangle([x, y, x + w, y + h], fill=col)
            d.polygon([(x - 10, y), (x + w / 2, y - 60), (x + w + 10, y)], fill=(150, 90, 70))
            d.rectangle([x + w / 2 - 3, y - 130, x + w / 2 + 3, y - 60], fill=(120, 120, 126))
            _yagi(d, x + w / 2 - 50, y - 120, 100, n=4, facing=1, w=3, scale=0.4)
    return img


def kaisha():
    """1950年代のアンテナ会社の事務所。机にテレビ用アンテナ。"""
    img = _rgb(base((232, 230, 222), (212, 210, 200)))
    wood_floor(img, FLOOR, col=(140, 130, 116), line=(120, 110, 98))
    d = _d(img)
    _window(d, 760, 110, 1160, 330, sky=(170, 200, 226), frame=(120, 120, 126))
    _table(d, 720, 1200, 640, col=(140, 120, 96))
    _yagi(d, 760, 600, 400, n=7, facing=1, w=4, scale=0.8)
    for x in (80, 1480):
        d.rectangle([x, 600, x + 360, 640], fill=(170, 160, 146))
        d.rectangle([x + 120, 500, x + 240, 600], fill=(90, 80, 70))           # テレビ
        d.rectangle([x + 132, 512, x + 228, 580], fill=(170, 190, 200))
    return img


def kenkyushitsu():
    """1960年代の研究室。本棚と、机の上の小さなテレビ。"""
    img = _rgb(base((230, 224, 210), (210, 204, 190)))
    wood_floor(img, FLOOR, col=(130, 110, 90), line=(110, 92, 74))
    d = _d(img)
    for x in (60, 1500):
        d.rectangle([x, 200, x + 360, 780], fill=(140, 110, 80))
        for r in range(5):
            d.rectangle([x, 300 + r * 100, x + 360, 310 + r * 100], fill=(110, 86, 62))
            for k in range(9):
                d.rectangle([x + 14 + k * 38, 240 + r * 100, x + 44 + k * 38, 300 + r * 100],
                            fill=((160, 60, 50), (60, 90, 140), (200, 170, 90))[(k + r) % 3])
    _window(d, 760, 110, 1160, 330, sky=(176, 206, 226))
    _table(d, 760, 1160, 640, col=(120, 96, 72))
    d.rectangle([900, 540, 1020, 640], fill=(80, 76, 72))                     # 小さなテレビ
    d.rectangle([912, 552, 1008, 620], fill=(180, 200, 210))
    d.rectangle([800, 610, 880, 640], fill=(240, 236, 226))                   # 原稿
    return img


def hibun():
    """青葉山の像の前。台座と碑文の板、木々。"""
    img = vgrad((W, H), (176, 206, 226), (220, 230, 226))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(130, 140, 110))
    for x in (100, 330, 1500, 1730):
        d.rectangle([x, 300, x + 30, 700], fill=(100, 80, 60))
        d.ellipse([x - 110, 160, x + 140, 420], fill=(80, 130, 80))
    d.rectangle([860, 470, 1060, 700], fill=(150, 146, 140))                  # 台座
    d.rectangle([880, 520, 1040, 640], fill=(120, 100, 60))                   # 碑文の板
    for k in range(5):
        d.line([(896, 540 + k * 20), (1024, 540 + k * 20)], fill=(210, 190, 130), width=3)
    d.ellipse([900, 300, 1020, 420], fill=(110, 90, 60))                      # 胸像
    d.rectangle([880, 400, 1040, 470], fill=(110, 90, 60))
    return img


def gendai():
    """今の町。屋根のアンテナと、アマチュア無線の塔。"""
    img = vgrad((W, H), (150, 196, 236), (214, 230, 240))
    d = _d(img)
    for k in range(9):
        x = k * 220 - 40
        h = 260 + (k % 3) * 60
        d.rectangle([x, 800 - h, x + 200, 800], fill=((230, 226, 216), (210, 214, 222), (236, 220, 200))[k % 3])
        if 3 <= k <= 5:
            d.rectangle([x + 97, 800 - h - 120, x + 103, 800 - h], fill=(120, 120, 126))
            _yagi(d, x + 50, 800 - h - 110, 110, n=5, facing=1, w=3, scale=0.45)
    d.rectangle([0, 800, W, H], fill=(150, 150, 156))
    return img


def yane3():
    """地デジのころの住宅街。どの屋根にも、骨の短いUHFの八木アンテナが同じ向きに立つ。"""
    img = vgrad((W, H), (160, 200, 236), (220, 232, 240))
    d = _d(img)
    d.polygon([(1700, 700), (1740, 330), (1780, 700)], fill=(200, 80, 60))     # 遠くの電波塔
    for y in range(380, 700, 50):
        d.line([(1700 + (y - 330) * 0.1, y), (1780 - (y - 330) * 0.1, y)], fill=(240, 240, 240), width=3)
    d.rectangle([0, 700, W, H], fill=(130, 124, 116))
    cols = [(96, 76, 64), (70, 80, 96), (110, 86, 70), (84, 90, 80)]
    for k, cx in enumerate((180, 560, 950, 1340)):
        top = 520 + (k % 2) * 40
        d.polygon([(cx - 200, 760), (cx, top), (cx + 200, 760)], fill=cols[k])
        d.rectangle([cx - 150, 760, cx + 150, H], fill=(226, 220, 206))
        d.rectangle([cx - 4, top - 170, cx + 4, top], fill=(120, 120, 126))
        _yagi(d, cx - 90, top - 160, 200, n=12, facing=1, w=3, scale=0.55)
    return img


def mori():
    """森の中。手に持った八木アンテナで電波を探す人と、首輪を付けた鹿。"""
    img = vgrad((W, H), (170, 206, 170), (120, 160, 110))
    d = _d(img)
    for x in (60, 300, 1500, 1760):
        d.rectangle([x, 120, x + 70, 880], fill=(96, 70, 50))
        d.ellipse([x - 150, 0, x + 220, 380], fill=(70, 120, 70))
    d.rectangle([0, 860, W, H], fill=(96, 120, 70))
    # 手前の人（影絵）とアンテナ
    ink = (50, 56, 50)
    ox = -120
    d.ellipse([760 + ox, 470, 830 + ox, 540], fill=ink)
    d.rectangle([765 + ox, 540, 825 + ox, 720], fill=ink)
    d.rectangle([770 + ox, 720, 795 + ox, 860], fill=ink)
    d.rectangle([800 + ox, 720, 825 + ox, 860], fill=ink)
    d.line([(820 + ox, 580), (880 + ox, 540)], fill=ink, width=18)              # 腕
    _yagi(d, 870 + ox, 540, 190, n=2, facing=1, col=(200, 200, 206), w=5, scale=1.1)
    for k in range(3):                                                           # 鹿から来る電波
        r = 30 + k * 26
        d.arc([1010 - r, 560 - r, 1010 + r, 560 + r], 150, 210, fill=(240, 200, 80), width=4)
    # 奥の鹿と首輪
    deer = (150, 110, 80)
    dx = -190
    d.ellipse([1220 + dx, 560, 1380 + dx, 640], fill=deer)
    d.rectangle([1240 + dx, 620, 1254 + dx, 720], fill=deer)
    d.rectangle([1350 + dx, 620, 1364 + dx, 720], fill=deer)
    d.polygon([(1350 + dx, 580), (1400 + dx, 480), (1420 + dx, 500), (1384 + dx, 600)], fill=deer)   # 首
    d.ellipse([1392 + dx, 460, 1440 + dx, 504], fill=deer)
    d.line([(1400 + dx, 470), (1390 + dx, 430)], fill=deer, width=5)
    d.line([(1420 + dx, 468), (1432 + dx, 428)], fill=deer, width=5)
    d.line([(1368 + dx, 540), (1398 + dx, 552)], fill=(230, 80, 60), width=10)   # 首輪
    d.rectangle([1374 + dx, 548, 1392 + dx, 566], fill=(60, 60, 66))            # 発信器
    return img


LOCATIONS = {
    "yg_yane": yane, "yg_yane2": yane2, "yg_gakkou": gakkou, "yg_lab": lab, "yg_jikken": jikken,
    "yg_kaigan": kaigan, "yg_zukai": zukai, "yg_zukai2": zukai2, "yg_kaijou": kaijou, "yg_oka": oka,
    "yg_singapore": singapore, "yg_sf": sf, "yg_kaisha": kaisha, "yg_kenkyushitsu": kenkyushitsu,
    "yg_hibun": hibun, "yg_gendai": gendai, "yg_yane3": yane3, "yg_mori": mori,
}

CARDS = ["1896", "1924", "1925", "1942", "1951", "1976"]


def year_card(text: str) -> Image.Image:
    """黒地に年号だけのカード。キャラと同居させない単独シーンで使う。"""
    img = Image.new("RGB", (W, H), (18, 18, 20))
    d = _d(img)
    font = _font(150)
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
        if only and f"yg_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"yg_card_{y}.png")
        print(f"生成完了: yg_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
