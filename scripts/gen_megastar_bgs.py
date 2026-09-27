#!/usr/bin/env python3
"""メガスターの誕生・大平貴之回（61_メガスターの誕生 / slug=ohira-megastar）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はたまごっち回（gen_tamagotchi_bgs.py）と同じ。
実在メーカーの商標（ロゴ・商品名の文字）は描かない。投影機は汎用の形にとどめる。

実行: PYTHONPATH=. python scripts/gen_megastar_bgs.py [名前...]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)
NIGHT = ((10, 14, 36), (30, 40, 80))


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


def _stars(d, box, n, seed, rmax=2.2, col=(255, 255, 240)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.random() ** 3 * rmax + 0.6
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def _milkyway(img, box, n, seed, angle=-0.25, width=160):
    """星の粒でできた天の川の帯。"""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for _ in range(60):
        t = rnd.uniform(-1, 1)
        x = cx + t * (x1 - x0) / 2
        y = cy + t * (x1 - x0) / 2 * angle + rnd.gauss(0, width * 0.3)
        r = rnd.uniform(width * 0.4, width * 0.9)
        g.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], fill=(150, 160, 210, 18))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    d = _d(img)
    for _ in range(n):
        t = rnd.uniform(-1, 1)
        x = cx + t * (x1 - x0) / 2
        y = cy + t * (x1 - x0) / 2 * angle + rnd.gauss(0, width * 0.28)
        r = rnd.random() ** 4 * 1.8 + 0.5
        c = 200 + int(rnd.random() * 55)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(c, c, 255))


def _night(size=(W, H)):
    return vgrad(size, *NIGHT)


def _window(d, x0, y0, x1, y1, sky=(176, 210, 232), frame=(70, 62, 56)):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


def _table(d, x0, x1, y, col=(150, 116, 80)):
    d.rectangle([x0, y, x1, y + 40], fill=col)
    d.rectangle([x0 + 20, y + 40, x0 + 40, y + 190], fill=tuple(int(c * 0.8) for c in col))
    d.rectangle([x1 - 40, y + 40, x1 - 20, y + 190], fill=tuple(int(c * 0.8) for c in col))


def _starball(d, cx, cy, r, col=(60, 64, 76)):
    """レンズがたくさん付いた恒星球（汎用の形）。"""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=(30, 30, 36), width=4)
    for i in range(-2, 3):
        for j in range(-2, 3):
            if i * i + j * j <= 5:
                x, y = cx + i * r * 0.36, cy + j * r * 0.36
                rr = r * 0.12
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(170, 200, 230), outline=(30, 30, 36), width=2)
    d.rectangle([cx - r * 0.12, cy + r, cx + r * 0.12, cy + r * 1.9], fill=(80, 80, 90))
    d.rectangle([cx - r * 0.6, cy + r * 1.9, cx + r * 0.6, cy + r * 2.05], fill=(80, 80, 90))


def _dome_inside(seed, milky=False, n=900):
    img = _night()
    d = _d(img)
    if milky:
        _milkyway(img, (-100, 80, W + 100, 620), 5000, seed, angle=0.18, width=150)
        d = _d(img)
    _stars(d, (0, 0, W, 760), n, seed + 1)
    d.rectangle([0, 780, W, H], fill=(20, 22, 34))
    for k in range(4):                                                     # 客席
        d.arc([-400 + k * 30, 800 + k * 60, W + 400 - k * 30, 1400 + k * 60], 180, 360, fill=(40, 44, 64), width=26)
    return img


def beranda(binoculars=False):
    """夜のベランダ。都会の空に星が3つ。締めの回だけ手すりに双眼鏡。"""
    img = vgrad((W, H), (26, 30, 58), (80, 70, 100))
    d = _d(img)
    for i, (x, y) in enumerate(((860, 160), (1010, 230), (1130, 130))):   # 見える星は3つ
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 250, 220))
        d.line([(x - 14, y), (x + 14, y)], fill=(255, 250, 220), width=2)
        d.line([(x, y - 14), (x, y + 14)], fill=(255, 250, 220), width=2)
    rnd = random.Random(3)
    for k in range(22):                                                    # ビル
        x = k * 90 - 20
        h = rnd.randint(200, 460)
        d.rectangle([x, 700 - h, x + 84, 700], fill=(34, 34, 48))
        for r in range(700 - h + 20, 690, 36):
            for c in range(3):
                if rnd.random() < 0.55:
                    d.rectangle([x + 10 + c * 24, r, x + 24 + c * 24, r + 16], fill=(250, 220, 140))
    d.rectangle([0, 700, W, H], fill=(120, 118, 124))                      # ベランダの床
    d.rectangle([0, 640, W, 660], fill=(170, 170, 176))                    # 手すり
    for x in range(0, W, 60):
        d.rectangle([x, 660, x + 8, 760], fill=(150, 150, 156))
    d.rectangle([0, 760, W, 772], fill=(150, 150, 156))
    if binoculars:                                                         # 双眼鏡
        for cx in (915, 1005):
            d.rounded_rectangle([cx - 36, 566, cx + 36, 640], radius=14, fill=(210, 210, 216), outline=(90, 90, 100), width=4)
            d.ellipse([cx - 30, 620, cx + 30, 646], fill=(120, 170, 220), outline=(90, 90, 100), width=3)
        d.rectangle([951, 582, 969, 612], fill=(170, 170, 176))
    return img


def beranda2():
    return beranda(binoculars=True)


def rekishi():
    """初期のプラネタリウム。ドームの下に鉄アレイ形の投影機。"""
    img = _dome_inside(11)
    d = _d(img)
    cx = 960
    d.rectangle([cx - 14, 430, cx + 14, 740], fill=(90, 90, 100))
    for cy in (360, 520):
        d.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=(70, 74, 86), outline=(30, 30, 36), width=4)
        for k in range(8):
            a = k * math.pi / 4
            x, y = cx + 60 * math.cos(a), cy + 60 * math.sin(a)
            d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(170, 200, 230))
    d.polygon([(cx - 120, 740), (cx + 120, 740), (cx + 80, 700), (cx - 80, 700)], fill=(80, 80, 90))
    return img


def heya70():
    """1970年代の子ども部屋（7畳）。壁の上に夜光の星、机に紙のドームと黒電話と電話帳。"""
    img = _rgb(base((226, 214, 188), (206, 194, 168)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([0, 0, W, 120], fill=(190, 176, 150))                      # 天井の梁
    for x, y in ((820, 170), (880, 210), (930, 160), (1000, 200), (1060, 170), (1100, 230), (960, 250)):
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(200, 250, 150))   # 夜光の星
    d.line([(820, 170), (880, 210), (960, 250), (1000, 200)], fill=(200, 220, 170), width=2)
    _window(d, 1300, 180, 1620, 460, sky=(160, 196, 220))
    d.rectangle([760, 560, 1160, 600], fill=(130, 96, 60))                 # 机
    d.rectangle([780, 600, 800, 760], fill=(110, 80, 50))
    d.rectangle([1120, 600, 1140, 760], fill=(110, 80, 50))
    d.chord([790, 470, 930, 610], 180, 360, fill=(240, 236, 220), outline=(150, 140, 120), width=3)  # 紙のドーム
    for k in range(9):
        d.ellipse([806 + k * 13, 520 + (k % 3) * 12, 812 + k * 13, 526 + (k % 3) * 12], fill=(40, 40, 40))
    d.rounded_rectangle([980, 520, 1070, 560], radius=10, fill=(30, 30, 30))   # 黒電話
    d.ellipse([1005, 505, 1045, 545], fill=(30, 30, 30))
    d.ellipse([1014, 516, 1036, 538], fill=(230, 230, 230))
    d.rectangle([1080, 530, 1150, 560], fill=(240, 220, 90), outline=(150, 130, 50), width=2)  # 電話帳
    return img


def heya70d():
    """明かりを消した子ども部屋。夜光の星座だけが光る。"""
    img = heya70()
    dark = Image.new("RGB", img.size, (14, 16, 30))
    img = Image.blend(img, dark, 0.78)
    d = _d(img)
    for x, y in ((820, 170), (880, 210), (930, 160), (1000, 200), (1060, 170), (1100, 230), (960, 250)):
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(70, 110, 60))
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(200, 255, 150))
    d.line([(820, 170), (880, 210), (960, 250), (1000, 200)], fill=(150, 220, 120), width=3)
    return img


def kagakukan():
    """科学館のプラネタリウム。星空のドームと、ダイヤルの並ぶ解説台。"""
    img = _dome_inside(21)
    d = _d(img)
    d.chord([700, 380, 1220, 700], 180, 360, fill=(90, 70, 110))           # 夕焼け投影機の光
    d.rounded_rectangle([760, 560, 1160, 740], radius=16, fill=(70, 70, 80), outline=(40, 40, 46), width=4)
    for k in range(6):                                                     # ダイヤル
        x = 800 + k * 62
        d.ellipse([x, 600, x + 44, 644], fill=(200, 200, 206), outline=(60, 60, 66), width=3)
        d.line([(x + 22, 622), (x + 22 + 14 * math.cos(k), 622 - 14 * abs(math.sin(k)))], fill=(200, 60, 60), width=3)
    for k in range(8):
        d.ellipse([800 + k * 44, 670, 820 + k * 44, 690], fill=((80, 200, 120), (240, 180, 60), (220, 70, 70))[k % 3])
    return img


def kawara(launched=False):
    """夕暮れの河原。打ち上げ後は、空に上っていくロケットの煙。"""
    img = vgrad((W, H), (250, 170, 110), (170, 110, 140))
    d = _d(img)
    d.rectangle([0, 700, W, 800], fill=(90, 110, 150))                      # 川
    d.rectangle([0, 800, W, H], fill=(110, 130, 70))
    d.rectangle([0, 660, W, 700], fill=(120, 140, 80))
    if not launched:                                                       # 発射台の上のロケット
        d.line([(940, 700), (960, 610)], fill=(90, 80, 70), width=4)
        d.line([(980, 700), (960, 610)], fill=(90, 80, 70), width=4)
        d.rectangle([954, 600, 966, 660], fill=(240, 240, 236))
        d.polygon([(960, 580), (952, 600), (968, 600)], fill=(220, 60, 50))
        return img
    pts = [(960 + 30 * math.sin(t / 60), 700 - t) for t in range(0, 520, 10)]
    for i, (x, y) in enumerate(pts):                                       # 煙の跡
        r = 10 + i * 0.35
        d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 230, 220))
    x, y = pts[-1]
    d.polygon([(x, y - 40), (x - 10, y), (x + 10, y)], fill=(220, 60, 50))
    return img


def kawara2():
    return kawara(launched=True)


def bunkasai():
    """高校の文化祭。教室の真ん中に、黒い手作りドーム。"""
    img = _rgb(base((236, 232, 220), (216, 210, 196)))
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    d = _d(img)
    for k in range(12):                                                    # 紙の輪飾り
        x = 40 + k * 160
        for j in range(5):
            d.ellipse([x + j * 26, 90 + (j % 2) * 8, x + j * 26 + 30, 110 + (j % 2) * 8],
                      outline=((230, 90, 90), (240, 200, 60), (90, 160, 220))[(k + j) % 3], width=5)
    d.rectangle([80, 180, 520, 420], fill=(40, 80, 60))                     # 黒板
    d.chord([700, 330, 1220, 850], 180, 360, fill=(30, 32, 46), outline=(20, 20, 26), width=6)  # ドーム
    _stars(d, (760, 400, 1160, 580), 90, 5)
    d.rectangle([930, 520, 990, 590], fill=(10, 10, 16))                    # 入口
    return img


def australia():
    """オーストラリアの夜空。地平線まで星と、濃い天の川、小さなハレー彗星。"""
    img = _night()
    _milkyway(img, (-200, 100, W + 200, 700), 9000, 31, angle=-0.35, width=190)
    d = _d(img)
    _stars(d, (0, 0, W, 820), 1400, 32)
    d.line([(1400, 260), (1520, 200)], fill=(220, 230, 255), width=3)       # 彗星の尾
    d.ellipse([1392, 254, 1408, 270], fill=(250, 250, 255))
    d.polygon([(0, 860), (400, 820), (900, 850), (1400, 810), (W, 850), (W, H), (0, H)], fill=(40, 30, 26))
    return img


def kousha(launched=False):
    """高校の校庭。発射後は、校舎の前から上るロケットの煙。"""
    img = vgrad((W, H), (170, 206, 236), (214, 226, 236))
    d = _d(img)
    d.rectangle([200, 260, 1720, 700], fill=(226, 222, 210))                # 校舎
    for r in range(3):
        for c in range(14):
            d.rectangle([240 + c * 104, 300 + r * 130, 320 + c * 104, 380 + r * 130], fill=(170, 200, 220))
    d.rectangle([900, 200, 1020, 260], fill=(226, 222, 210))
    d.ellipse([930, 210, 990, 250], fill=(250, 250, 250), outline=(90, 90, 90), width=3)   # 時計
    d.rectangle([0, 700, W, H], fill=(200, 176, 140))                       # 校庭
    if not launched:                                                       # 発射台の上のロケット
        d.line([(940, 780), (960, 690)], fill=(90, 80, 70), width=4)
        d.line([(980, 780), (960, 690)], fill=(90, 80, 70), width=4)
        d.rectangle([954, 680, 966, 740], fill=(240, 240, 236))
        d.polygon([(960, 660), (952, 680), (968, 680)], fill=(220, 60, 50))
        return img
    for i in range(40):
        x, y = 960 + 8 * math.sin(i / 3), 690 - i * 12
        r = 8 + i * 0.4
        d.ellipse([x - r, y - r, x + r, y + r], fill=(245, 245, 245))
    d.polygon([(960, 170), (950, 210), (970, 210)], fill=(220, 60, 50))
    return img


def kousha2():
    return kousha(launched=True)


def akiba():
    """秋葉原の電源装置メーカーの作業場。棚に電源と測定器、机に修理中の電源装置。"""
    img = _rgb(base((220, 222, 214), (200, 202, 194)))
    wood_floor(img, FLOOR, col=(130, 130, 124), line=(110, 110, 104))
    d = _d(img)
    for x in (60, 1480):
        d.rectangle([x, 200, x + 380, 800], fill=(120, 124, 130))
        for r in range(4):
            d.rectangle([x, 320 + r * 120, x + 380, 334 + r * 120], fill=(90, 94, 100))
            for k in range(3):
                d.rectangle([x + 20 + k * 120, 250 + r * 120, x + 120 + k * 120, 320 + r * 120], fill=(200, 200, 196))
                d.rectangle([x + 34 + k * 120, 262 + r * 120, x + 70 + k * 120, 290 + r * 120], fill=(40, 60, 40))
    _table(d, 760, 1160, 620, col=(110, 104, 96))
    d.rectangle([820, 480, 1100, 620], fill=(200, 200, 196), outline=(90, 90, 96), width=4)   # 修理中の電源装置
    for k in range(2):
        d.rectangle([845 + k * 110, 505, 935 + k * 110, 565], fill=(40, 60, 40))           # メーター
        d.line([(860 + k * 110, 555), (910 + k * 110, 520)], fill=(120, 220, 120), width=3)
    for k in range(4):
        d.ellipse([850 + k * 60, 580, 874 + k * 60, 604], fill=(60, 60, 66))              # つまみ
    d.rectangle([1110, 560, 1150, 620], fill=(40, 60, 40))
    return img


def daigaku():
    """大学の文化祭。キャンパスの中庭に膨らませた白いドーム。"""
    img = vgrad((W, H), (160, 196, 232), (210, 224, 236))
    d = _d(img)
    for x in (0, 1420):
        d.rectangle([x, 220, x + 500, 760], fill=(210, 200, 186))
        for r in range(4):
            for c in range(4):
                d.rectangle([x + 30 + c * 118, 250 + r * 120, x + 100 + c * 118, 330 + r * 120], fill=(170, 196, 216))
    d.rectangle([0, 760, W, H], fill=(150, 170, 110))
    d.chord([680, 420, 1240, 980], 180, 360, fill=(246, 246, 246), outline=(200, 200, 204), width=6)  # エアドーム
    for k in range(5):
        d.arc([680 + k * 56, 420 + k * 28, 1240 - k * 56, 980 - k * 28], 180, 360, fill=(226, 226, 230), width=3)
    d.rectangle([930, 620, 990, 700], fill=(60, 60, 70))
    return img


def airdome_in():
    """手作りのエアドームの中。膜の継ぎ目と、2つの球の小さな投影機。"""
    img = _night()
    d = _d(img)
    _stars(d, (0, 0, W, 720), 700, 91, rmax=2.0)
    for k in range(7):                                                     # 膜の継ぎ目
        x = 160 + k * 267
        d.arc([x - 900, -300, x + 900, 1500], 250, 290, fill=(50, 56, 80), width=3)
    d.rectangle([0, 760, W, H], fill=(46, 44, 50))                          # 床のシート
    cx = 960
    d.rectangle([cx - 10, 560, cx + 10, 760], fill=(110, 110, 120))
    for cy in (520, 620):
        d.ellipse([cx - 55, cy - 55, cx + 55, cy + 55], fill=(200, 200, 206), outline=(90, 90, 100), width=3)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if i * i + j * j <= 1:
                    d.ellipse([cx + i * 24 - 9, cy + j * 24 - 9, cx + i * 24 + 9, cy + j * 24 + 9], fill=(150, 190, 230))
    d.polygon([(cx - 80, 760), (cx + 80, 760), (cx + 50, 730), (cx - 50, 730)], fill=(110, 110, 120))
    return img


def kaijou():
    """国際会議の会場。演台と、投影機の図を映したスクリーン。"""
    img = _rgb(base((200, 196, 210), (170, 166, 180)))
    wood_floor(img, FLOOR, col=(100, 90, 100), line=(84, 76, 84))
    d = _d(img)
    d.rectangle([740, 110, 1180, 400], fill=(250, 250, 252), outline=(90, 90, 100), width=6)
    d.ellipse([880, 170, 1040, 330], outline=(40, 70, 140), width=6)       # スクリーンの投影機の図
    for k in range(6):
        a = k * math.pi / 3
        x, y = 960 + 60 * math.cos(a), 250 + 60 * math.sin(a)
        d.ellipse([x - 14, y - 14, x + 14, y + 14], outline=(40, 70, 140), width=4)
    d.polygon([(1080, 520), (1180, 520), (1170, 760), (1090, 760)], fill=(120, 90, 70))   # 演台
    for r in range(3):                                                    # 客席の頭
        for c in range(14):
            x = 60 + c * 140 + (r % 2) * 70
            d.ellipse([x, 800 + r * 70, x + 70, 870 + r * 70], fill=(70, 66, 80))
    return img


def heya96():
    """大人になった7畳の自室。作業台に恒星球と部品。"""
    img = _rgb(base((226, 218, 200), (206, 198, 180)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    _window(d, 1320, 180, 1640, 460, sky=(40, 50, 90))
    for x in (60,):
        d.rectangle([x, 240, x + 360, 780], fill=(150, 120, 90))
        for r in range(4):
            d.rectangle([x, 360 + r * 110, x + 360, 372 + r * 110], fill=(120, 96, 72))
            for k in range(3):
                d.rectangle([x + 20 + k * 115, 300 + r * 110, x + 110 + k * 115, 360 + r * 110], fill=(196, 170, 120))
    _table(d, 760, 1160, 640, col=(120, 100, 80))
    _starball(d, 960, 470, 90)
    for k in range(5):                                                    # 部品
        d.rectangle([790 + k * 70, 612, 830 + k * 70, 640], fill=(180, 184, 190), outline=(100, 100, 110), width=2)
    return img


def zukai():
    """図解: 光源 → 穴をあけた板 → レンズ → ドーム。大きな穴は明るい星。"""
    img = _rgb(base((244, 244, 240), (230, 230, 224)))
    d = _d(img)
    ink = (50, 56, 70)
    d.ellipse([640, 470, 700, 530], fill=(255, 220, 90), outline=ink, width=4)  # 光源
    for k in range(8):
        a = k * math.pi / 4
        d.line([(670 + 38 * math.cos(a), 500 + 38 * math.sin(a)), (670 + 56 * math.cos(a), 500 + 56 * math.sin(a))], fill=(240, 180, 40), width=4)
    d.rectangle([790, 360, 820, 640], fill=(40, 40, 46))                   # 恒星原板
    for y, r in ((400, 9), (460, 6), (520, 3), (580, 1.5)):
        d.ellipse([805 - r, y - r, 805 + r, y + r], fill=(255, 250, 200))
    d.ellipse([900, 420, 950, 580], fill=(170, 210, 240), outline=ink, width=4)   # レンズ
    d.arc([980, 200, 1580, 800], 120, 240, fill=ink, width=8)              # ドーム
    for y, r in ((400, 12), (460, 8), (520, 4), (580, 2)):
        d.line([(820, y), (925, 500 + (y - 490) * 0.3), (1060, 300 + (y - 400) * 2.2)], fill=(250, 220, 120), width=2)
        d.ellipse([1060 - r, 300 + (y - 400) * 2.2 - r, 1060 + r, 300 + (y - 400) * 2.2 + r], fill=(250, 200, 60))
    _text_c(d, 670, 580, "光源", 36, ink)
    _text_c(d, 805, 660, "穴をあけた板", 36, ink)
    _text_c(d, 925, 600, "レンズ", 36, ink)
    _text_c(d, 1130, 740, "ドーム", 36, ink)
    return img


def zukai2():
    """図解: 穴をあけた原板と、等級ごとの穴の大きさ。"""
    img = _rgb(base((244, 244, 240), (230, 230, 224)))
    d = _d(img)
    ink = (50, 56, 70)
    d.ellipse([740, 300, 980, 540], fill=(40, 40, 46))                     # 板
    _stars(d, (764, 324, 956, 516), 500, 41, rmax=1.4, col=(255, 250, 210))
    _text_c(d, 860, 556, "原板1枚", 40, ink)
    for k, (lab, r) in enumerate((("1等星", 36), ("6等星", 12), ("11等星", 4))):
        y = 340 + k * 90
        d.ellipse([1060 - r, y - r, 1060 + r, y + r], fill=(250, 200, 60), outline=ink, width=2)
        _text_c(d, 1150, y - 22, lab, 36, ink)
    _text_c(d, 960, 640, "最小の穴 0.7ミクロン", 42, (170, 50, 50))
    return img


def london():
    """ロンドンの会議の前夜のパーティー会場。シャンデリアと丸テーブル。"""
    img = _rgb(base((120, 70, 70), (90, 50, 56)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(70, 40, 40))
    for x in (300, 960, 1620):                                             # シャンデリア
        d.line([(x, 0), (x, 90)], fill=(220, 190, 110), width=4)
        for k in range(7):
            a = math.pi * k / 6
            d.ellipse([x - 90 * math.cos(a) - 8, 110 + 20 * math.sin(a) - 8, x - 90 * math.cos(a) + 8, 110 + 20 * math.sin(a) + 8],
                      fill=(255, 230, 150))
    for x0 in (200, 1560):
        d.rectangle([x0, 180, x0 + 160, 520], fill=(60, 60, 100))
    d.ellipse([760, 600, 1160, 680], fill=(246, 244, 236))                 # 丸テーブル
    d.rectangle([950, 660, 970, 820], fill=(90, 70, 60))
    for k in range(4):
        x = 820 + k * 90
        d.polygon([(x, 560), (x + 30, 560), (x + 22, 600), (x + 8, 600)], fill=(230, 220, 170))
        d.rectangle([x + 13, 600, x + 17, 630], fill=(220, 220, 220))
    return img


def dome():
    """上映中のドーム。星の粒でできた天の川と、真ん中の恒星球。"""
    img = _dome_inside(51, milky=True, n=1500)
    d = _d(img)
    _starball(d, 960, 640, 60)
    return img


def spiral():
    """ギャラリーに置いたドームの中。ぼんやり光る天の川の帯。"""
    img = _dome_inside(61, milky=True, n=700)
    return img


def airdome():
    """科学館のホールに膨らませた、直径10メートルの白いドーム。"""
    img = _rgb(base((226, 230, 236), (204, 208, 216)))
    wood_floor(img, FLOOR, col=(150, 146, 140), line=(132, 128, 122))
    d = _d(img)
    for k in range(6):
        d.rectangle([k * 330, 80, k * 330 + 300, 380], fill=(200, 214, 228), outline=(170, 180, 190), width=4)
    d.chord([640, 380, 1280, 1020], 180, 360, fill=(248, 248, 250), outline=(200, 200, 206), width=6)
    for k in range(5):
        d.arc([640 + k * 64, 380 + k * 32, 1280 - k * 64, 1020 - k * 32], 180, 360, fill=(228, 228, 234), width=3)
    d.rectangle([920, 600, 1000, 700], fill=(50, 50, 60))
    return img


def sony():
    """2000年代初めの会社のオフィス（ロゴなし）。"""
    img = _rgb(base((232, 234, 236), (212, 214, 218)))
    wood_floor(img, FLOOR, col=(140, 140, 146), line=(122, 122, 128))
    d = _d(img)
    _window(d, 760, 110, 1160, 360, sky=(170, 200, 226), frame=(120, 120, 126))
    for x in (60, 1440):
        d.rectangle([x, 600, x + 420, 640], fill=(200, 200, 204))
        d.rectangle([x + 20, 640, x + 40, 800], fill=(150, 150, 156))
        d.rectangle([x + 380, 640, x + 400, 800], fill=(150, 150, 156))
        d.rectangle([x + 120, 470, x + 300, 590], fill=(60, 60, 66))        # モニター
        d.rectangle([x + 132, 482, x + 288, 578], fill=(120, 170, 220))
        d.rectangle([x + 195, 590, x + 225, 600], fill=(60, 60, 66))
    _table(d, 780, 1140, 640, col=(170, 170, 176))
    for k in range(3):
        d.rectangle([820 + k * 110, 612, 900 + k * 110, 640], fill=(250, 250, 250), outline=(180, 180, 180))
    return img


def giken():
    """大平技研の作業場を兼ねた事務所。棚に恒星球、机に図面。"""
    img = _rgb(base((230, 232, 236), (210, 212, 218)))
    wood_floor(img, FLOOR, col=(150, 146, 140), line=(132, 128, 122))
    d = _d(img)
    for x in (80, 1480):
        d.rectangle([x, 220, x + 360, 760], fill=(170, 170, 176))
        for r in range(3):
            d.rectangle([x, 380 + r * 140, x + 360, 392 + r * 140], fill=(130, 130, 136))
    for x, y in ((170, 330), (330, 330), (1570, 330), (1730, 330)):
        _starball(d, x, y, 34)
    _window(d, 760, 120, 1160, 340, sky=(170, 200, 226), frame=(120, 120, 126))
    _table(d, 760, 1160, 640, col=(150, 150, 156))
    d.rectangle([800, 600, 1000, 640], fill=(240, 244, 250), outline=(140, 150, 170), width=2)   # 図面
    d.ellipse([840, 606, 890, 634], outline=(60, 90, 160), width=2)
    return img


def miraikan():
    """科学館の大きな傾いたドーム。満天の星と恒星球。"""
    img = _dome_inside(71, milky=True, n=2200)
    d = _d(img)
    _starball(d, 960, 600, 70, col=(80, 84, 96))
    return img


def homestar():
    """おもちゃ会社の会議室。机の上の家庭用プラネタリウムが、壁に星を映す。"""
    img = _rgb(base((70, 70, 96), (50, 50, 70)))
    wood_floor(img, FLOOR, col=(90, 80, 76), line=(76, 68, 64))
    d = _d(img)
    _stars(d, (620, 60, 1300, 460), 260, 81, rmax=2.0)
    _table(d, 760, 1160, 640, col=(120, 100, 84))
    d.chord([900, 540, 1020, 660], 180, 360, fill=(40, 40, 46), outline=(20, 20, 26), width=3)   # 家庭用
    d.rectangle([890, 600, 1030, 640], fill=(40, 40, 46))
    d.ellipse([948, 548, 972, 572], fill=(170, 210, 240))
    for k in range(3):
        d.polygon([(960, 560), (800 + k * 160, 300), (830 + k * 160, 300)], fill=(90, 90, 130))
    return img


def stadium():
    """ドーム球場。屋根いっぱいの星と、グラウンドに置いた鏡の球。"""
    img = _night()
    d = _d(img)
    _stars(d, (0, 0, W, 640), 1800, 91, rmax=2.0)
    for k in range(6):
        d.arc([-300 + k * 40, -500 + k * 30, W + 300 - k * 40, 900 - k * 30], 200, 340, fill=(60, 66, 100), width=4)
    d.rectangle([0, 640, W, 760], fill=(50, 50, 70))                         # スタンド
    for r in range(3):
        for c in range(40):
            d.rectangle([c * 48 + (r % 2) * 24, 652 + r * 34, c * 48 + 36 + (r % 2) * 24, 676 + r * 34], fill=(70, 70, 96))
    d.rectangle([0, 760, W, H], fill=(40, 90, 50))                           # グラウンド
    cx, cy, r = 960, 600, 70                                                # 鏡の球
    d.rectangle([cx - 8, cy + r, cx + 8, 780], fill=(120, 120, 130))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(170, 176, 190), outline=(90, 90, 100), width=3)
    for i in range(-3, 4):
        for j in range(-3, 4):
            if i * i + j * j <= 10:
                x, y = cx + i * 17, cy + j * 17
                d.rectangle([x - 6, y - 6, x + 6, y + 6], fill=(230, 236, 250) if (i + j) % 2 else (140, 150, 170))
    return img


def zukai3():
    """図解: 映せる星の数の移り変わり（高さは桁で表す）。"""
    img = _rgb(base((244, 244, 240), (230, 230, 224)))
    d = _d(img)
    ink = (50, 56, 70)
    data = [("1998", "170万", 6.23), ("2004", "560万", 6.75), ("2008", "2200万", 7.34), ("2015", "10億", 9.0), ("2022", "12億", 9.08)]
    d.line([(740, 760), (1200, 760)], fill=ink, width=4)
    for k, (y, lab, lg) in enumerate(data):
        x = 760 + k * 88
        h = (lg - 5) * 150
        d.rectangle([x, 760 - h, x + 64, 760], fill=(70, 90, 170))
        _text_c(d, x + 32, 770, y, 30, ink)
        _text_c(d, x + 32, 760 - h - 44, lab, 28, ink)
    return img


def zukai4():
    """図解: 暗い空と街の空。見える星の数のちがい。"""
    img = _rgb(base((244, 244, 240), (230, 230, 224)))
    d = _d(img)
    ink = (50, 56, 70)
    for x0, n, lab in ((640, 700, "暗い空"), (990, 18, "街の空")):
        sky = vgrad((290, 360), (12, 16, 40), (40, 50, 90))
        img.paste(sky, (x0, 220))
        d = _d(img)
        _stars(d, (x0 + 10, 230, x0 + 280, 570), n, x0, rmax=1.8)
        _text_c(d, x0 + 145, 600, lab, 40, ink)
    return img


def gendai():
    """世界地図に、メガスターが入った国と地域の印。"""
    img = _rgb(base((236, 242, 248), (220, 230, 240)))
    d = _d(img)
    land = (190, 206, 190)
    def M(x, y):
        return 720 + (x - 560) * 0.6, 260 + (y - 220) * 0.8
    for box in ((560, 250, 760, 470), (700, 470, 820, 700), (880, 230, 1060, 420), (900, 420, 1020, 640),
                (1040, 220, 1340, 450), (1200, 560, 1320, 660)):
        x0, y0 = M(box[0], box[1])
        x1, y1 = M(box[2], box[3])
        d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=land)
    for x, y in ((660, 360), (720, 520), (930, 300), (980, 330), (1010, 290), (1040, 380), (1130, 350), (1180, 330),
                 (1230, 360), (1250, 420), (1170, 420), (1270, 610), (1210, 380), (960, 470)):
        x, y = M(x, y)
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(220, 70, 70), outline=(255, 255, 255), width=3)
    return img


LOCATIONS = {
    "mg_beranda": beranda, "mg_beranda2": beranda2, "mg_kawara2": kawara2, "mg_kousha2": kousha2,
    "mg_heya70d": heya70d, "mg_airdome_in": airdome_in, "mg_giken": giken, "mg_rekishi": rekishi, "mg_heya70": heya70, "mg_kagakukan": kagakukan,
    "mg_kawara": kawara, "mg_bunkasai": bunkasai, "mg_australia": australia, "mg_kousha": kousha,
    "mg_akiba": akiba, "mg_daigaku": daigaku, "mg_kaijou": kaijou, "mg_heya96": heya96,
    "mg_zukai": zukai, "mg_zukai2": zukai2, "mg_london": london, "mg_dome": dome, "mg_spiral": spiral,
    "mg_airdome": airdome, "mg_sony": sony, "mg_miraikan": miraikan, "mg_homestar": homestar,
    "mg_stadium": stadium, "mg_zukai3": zukai3, "mg_zukai4": zukai4, "mg_gendai": gendai,
}

CARDS = ["1970", "1986", "1996", "1998", "2000", "2004"]


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
        if only and f"mg_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"mg_card_{y}.png")
        print(f"生成完了: mg_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
