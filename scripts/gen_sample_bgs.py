#!/usr/bin/env python3
"""食品サンプルの誕生・岩崎瀧三回（62_食品サンプルの誕生 / slug=iwasaki-sample）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はメガスター回（gen_megastar_bgs.py）と同じ。
実在の会社・店の商標（ロゴ・屋号の文字）は描かない。

実行: PYTHONPATH=. python scripts/gen_sample_bgs.py [名前...]
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
EGG = (246, 206, 80)
KETCHUP = (200, 40, 30)


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


def _plate(d, cx, cy, w=150):
    d.ellipse([cx - w / 2, cy - w * 0.16, cx + w / 2, cy + w * 0.16], fill=(250, 250, 246), outline=(190, 190, 186), width=3)


def _omelette(d, cx, cy, w=120, wrinkles=False, ketchup=True):
    _plate(d, cx, cy + 10, w * 1.35)
    d.chord([cx - w / 2, cy - w * 0.36, cx + w / 2, cy + w * 0.28], 180, 360, fill=EGG, outline=(210, 160, 50), width=3)
    d.rectangle([cx - w / 2, cy - 3, cx + w / 2, cy + 6], fill=EGG)
    if wrinkles:
        for k in range(4):
            x = cx - w * 0.3 + k * w * 0.18
            d.arc([x - 12, cy - w * 0.22, x + 12, cy - w * 0.02], 200, 340, fill=(200, 150, 50), width=3)
    if ketchup:
        d.line([(cx - w * 0.25, cy - w * 0.18), (cx, cy - w * 0.24), (cx + w * 0.25, cy - w * 0.16)], fill=KETCHUP, width=7)


def _ramen(d, cx, cy, w=130):
    d.chord([cx - w / 2, cy - w * 0.2, cx + w / 2, cy + w * 0.5], 0, 180, fill=(200, 60, 50))
    d.ellipse([cx - w / 2, cy - w * 0.22, cx + w / 2, cy + w * 0.12], fill=(210, 160, 90))
    for k in range(5):
        d.arc([cx - w * 0.4 + k * 12, cy - w * 0.16, cx + w * 0.1 + k * 12, cy + w * 0.06], 180, 360, fill=(250, 230, 150), width=3)
    d.ellipse([cx + w * 0.1, cy - w * 0.14, cx + w * 0.32, cy + w * 0.02], fill=(250, 250, 240), outline=(240, 200, 60), width=5)


def _spaghetti(d, cx, cy, w=130, floating=True):
    _plate(d, cx, cy + 10, w * 1.3)
    d.chord([cx - w / 2, cy - w * 0.3, cx + w / 2, cy + w * 0.2], 180, 360, fill=(230, 120, 60))
    if not floating:
        d.line([(cx + w * 0.1, cy - w * 0.1), (cx + w * 0.5, cy - w * 0.35)], fill=(200, 200, 206), width=6)
        return
    for k in range(6):                                                     # 宙に浮くフォーク
        d.line([(cx - 12 + k * 5, cy - w * 0.3 - k * 10), (cx - 8 + k * 5, cy - w * 0.9)], fill=(236, 150, 80), width=4)
    d.rectangle([cx - 10, cy - w * 1.35, cx + 10, cy - w * 0.9], fill=(200, 200, 206))


def _tempura(d, cx, cy, w=120):
    _plate(d, cx, cy + 10, w * 1.3)
    for k in range(3):
        x = cx - w * 0.3 + k * w * 0.3
        d.ellipse([x - 26, cy - 34, x + 26, cy + 4], fill=(240, 200, 110), outline=(210, 160, 70), width=3)
        d.polygon([(x + 18, cy - 30), (x + 36, cy - 44), (x + 30, cy - 24)], fill=(230, 90, 60))


def _showcase(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(236, 240, 244), outline=(120, 110, 100), width=8)
    d.rectangle([x0 + 10, y0 + 10, x1 - 10, y0 + 22], fill=(255, 250, 220))  # 照明
    d.line([(x0, (y0 + y1) // 2 + 20), (x1, (y0 + y1) // 2 + 20)], fill=(160, 150, 140), width=6)


def mise():
    """今の飲食店の店先。ガラスケースにオムライスやラーメンのサンプル。"""
    img = _rgb(base((240, 232, 218), (220, 210, 194)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(170, 160, 150))
    d.rectangle([0, 60, W, 150], fill=(90, 50, 40))                        # のれんの上の庇
    for k in range(9):
        d.rectangle([k * 220, 150, k * 220 + 200, 260], fill=(40, 60, 100))
    _showcase(d, 700, 300, 1220, 760)
    _omelette(d, 820, 470, 130)                                            # オムライス
    d.chord([755, 450, 885, 500], 0, 180, fill=(220, 90, 60))
    _ramen(d, 1100, 470, 130)
    _spaghetti(d, 830, 700, 110)
    _tempura(d, 1090, 690, 110)
    return img


def jinja():
    """夜の神社。ろうそく台と、水たまりに落ちたロウの花。手前に畳。"""
    img = vgrad((W, H), (20, 24, 50), (60, 60, 90))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(70, 66, 60))                          # 境内
    d.rectangle([1300, 200, 1900, 700], fill=(110, 60, 40))                 # 社殿
    d.polygon([(1250, 220), (1600, 90), (1950, 220)], fill=(60, 40, 34))
    d.rectangle([80, 260, 120, 700], fill=(190, 50, 40))                    # 鳥居
    d.rectangle([380, 260, 420, 700], fill=(190, 50, 40))
    d.rectangle([40, 240, 460, 280], fill=(190, 50, 40))
    d.rectangle([800, 520, 1080, 540], fill=(120, 90, 60))                  # ろうそく台
    d.rectangle([930, 540, 950, 700], fill=(120, 90, 60))
    for k in range(6):
        x = 820 + k * 46
        d.rectangle([x, 470, x + 16, 520], fill=(250, 246, 236))
        d.ellipse([x + 2, 440, x + 14, 470], fill=(255, 210, 90))
        d.ellipse([x - 20, 420, x + 36, 490], outline=(255, 220, 120), width=2)
    d.ellipse([780, 760, 1040, 840], fill=(70, 90, 130))                    # 水たまり
    for cx, cy in ((860, 796), (940, 790), (990, 810)):                     # ロウの花
        for k in range(5):
            a = k * 2 * math.pi / 5
            d.ellipse([cx + 14 * math.cos(a) - 10, cy + 8 * math.sin(a) - 7, cx + 14 * math.cos(a) + 10, cy + 8 * math.sin(a) + 7],
                      fill=(250, 248, 240))
    d.rectangle([1100, 760, 1400, 900], fill=(170, 160, 100))               # 畳
    for k in range(12):
        d.line([(1100, 766 + k * 12), (1400, 766 + k * 12)], fill=(150, 140, 86), width=2)
    d.ellipse([1200, 800, 1250, 830], fill=(250, 248, 240))                 # 畳に落ちたロウ
    for k in range(3):
        d.line([(1204, 806 + k * 8), (1246, 806 + k * 8)], fill=(210, 206, 196), width=2)
    return img


def hoko():
    """明治末〜大正の大阪の商家。のれんと帳場。"""
    img = _rgb(base((214, 196, 166), (190, 170, 140)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([0, 80, W, 140], fill=(60, 50, 44))
    for k in range(6):
        d.rectangle([80 + k * 300, 140, 340 + k * 300, 260], fill=(110, 60, 50))
    for x in (60, 1460):
        d.rectangle([x, 300, x + 400, 700], fill=(130, 100, 70))
        for r in range(4):
            d.rectangle([x, 380 + r * 90, x + 400, 390 + r * 90], fill=(100, 76, 54))
            for c in range(4):
                d.rectangle([x + 20 + c * 95, 330 + r * 90, x + 95 + c * 95, 380 + r * 90], fill=(200, 180, 140))
    d.rectangle([760, 620, 1160, 680], fill=(120, 90, 60))                 # 帳場
    d.rectangle([900, 560, 1020, 620], fill=(90, 70, 50))                   # そろばん台
    d.chord([1060, 580, 1130, 640], 0, 180, fill=(60, 40, 30))              # 飯茶碗
    d.ellipse([1060, 570, 1130, 600], fill=(250, 250, 246))
    return img


def _ie_base():
    img = _rgb(base((222, 208, 180), (202, 188, 160)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([0, 0, W, 90], fill=(170, 150, 120))
    d.rectangle([1320, 160, 1640, 460], fill=(236, 228, 206), outline=(110, 90, 70), width=10)   # 障子
    for k in range(1, 4):
        d.line([(1320 + k * 80, 160), (1320 + k * 80, 460)], fill=(110, 90, 70), width=4)
        d.line([(1320, 160 + k * 75), (1640, 160 + k * 75)], fill=(110, 90, 70), width=4)
    _table(d, 760, 1160, 620, col=(120, 84, 56))
    return img


def ie():
    """昭和初めの大阪の家。卓の上に弁当箱。"""
    img = _ie_base()
    d = _d(img)
    for k in range(3):
        x = 800 + k * 120
        d.rectangle([x, 560, x + 100, 620], fill=(150, 60, 40), outline=(90, 40, 30), width=3)
        d.rectangle([x + 8, 568, x + 92, 580], fill=(60, 30, 20))
    return img


def ie2():
    """同じ家。卓の上に、肉とグリーンピースの模型。"""
    img = _ie_base()
    d = _d(img)
    _plate(d, 880, 600, 180)
    for k in range(3):
        d.polygon([(820 + k * 36, 590), (850 + k * 36, 575), (870 + k * 36, 598), (840 + k * 36, 608)], fill=(150, 60, 50))
    d.ellipse([1000, 560, 1110, 620], fill=(200, 200, 206), outline=(140, 140, 146), width=3)   # 缶
    rnd = random.Random(5)
    for _ in range(26):
        x, y = rnd.uniform(1015, 1095), rnd.uniform(570, 604)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(90, 170, 60))
    return img


def shisaku():
    """試作の卓。寒天の型、ロウを溶かす鍋、脱脂綿。"""
    img = _ie_base()
    d = _d(img)
    d.rectangle([790, 560, 930, 620], fill=(230, 220, 170), outline=(160, 150, 110), width=3)   # 寒天の型
    d.ellipse([820, 575, 900, 605], fill=(200, 190, 140))
    d.rectangle([960, 520, 1060, 620], fill=(60, 60, 64))                     # 七輪と鍋
    d.ellipse([950, 500, 1070, 540], fill=(90, 90, 96))
    d.ellipse([965, 505, 1055, 530], fill=(250, 240, 200))
    d.ellipse([930, 594, 990, 622], fill=(250, 250, 250))                     # 脱脂綿
    d.polygon([(1080, 600), (1110, 590), (1120, 612), (1090, 618)], fill=(230, 160, 90))   # 割れたロウ
    d.polygon([(1118, 606), (1140, 598), (1146, 616)], fill=(230, 160, 90))
    return img


def omu():
    """同じ家の卓。本物のオムレツと、ロウのオムレツが並ぶ。"""
    img = _ie_base()
    d = _d(img)
    _omelette(d, 860, 580, 130, wrinkles=True)
    _omelette(d, 1060, 580, 130, wrinkles=True)
    return img


def _shokudo_base():
    img = _rgb(base((230, 220, 200), (210, 200, 180)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(150, 130, 110))
    d.rectangle([0, 60, W, 140], fill=(70, 50, 40))
    for k in range(5):
        d.rectangle([80 + k * 380, 140, 360 + k * 380, 260], fill=(230, 230, 220))
    return img


def shokudo():
    """昭和の食堂の店先。窓に並べた本物の料理。"""
    img = _shokudo_base()
    d = _d(img)
    d.rectangle([720, 360, 1200, 640], fill=(210, 220, 226), outline=(110, 90, 70), width=8)
    d.line([(720, 500), (1200, 500)], fill=(150, 130, 110), width=6)
    _omelette(d, 820, 460, 100)
    _ramen(d, 1100, 450, 100)
    _tempura(d, 840, 600, 90)
    d.ellipse([1040, 560, 1160, 620], fill=(250, 250, 246))
    d.chord([1050, 540, 1150, 600], 180, 360, fill=(240, 220, 160))           # 親子丼
    return img


def shokudo2():
    """食堂の台の上に、開けた桐の箱。中にロウのオムレツ。"""
    img = _shokudo_base()
    d = _d(img)
    d.rectangle([700, 600, 1220, 660], fill=(140, 110, 80))                   # 台
    d.rectangle([780, 470, 1140, 600], fill=(230, 210, 170), outline=(170, 150, 110), width=5)   # 桐の箱
    d.polygon([(780, 470), (1140, 470), (1110, 380), (810, 380)], fill=(236, 218, 180), outline=(170, 150, 110))
    _omelette(d, 960, 540, 140)
    return img


def sogo():
    """百貨店の大食堂。大きなサンプルケースとテーブル。"""
    img = _rgb(base((240, 236, 228), (220, 214, 204)))
    wood_floor(img, FLOOR, col=(170, 150, 120), line=(150, 130, 100))
    d = _d(img)
    for x in (100, 1560):
        d.ellipse([x, 90, x + 260, 150], fill=(255, 246, 210))              # 天井の照明
    _showcase(d, 660, 250, 1260, 700)
    _omelette(d, 780, 400, 110)
    _ramen(d, 960, 400, 110)
    _tempura(d, 1140, 390, 100)
    _spaghetti(d, 790, 640, 90, floating=False)
    d.ellipse([920, 620, 1040, 670], fill=(250, 250, 246))
    d.chord([930, 600, 1030, 650], 180, 360, fill=(240, 220, 160))
    _plate(d, 1140, 650, 120)
    d.ellipse([1100, 620, 1180, 660], fill=(240, 180, 190))                   # プリン
    return img


def zukai():
    """図解: 京都・東京・大阪、3つの始まり。"""
    img = _rgb(base((244, 244, 240), (230, 230, 224)))
    d = _d(img)
    ink = (50, 56, 70)
    d.polygon([(620, 700), (760, 600), (900, 560), (1040, 470), (1150, 380), (1260, 300), (1300, 340),
               (1200, 450), (1080, 560), (960, 640), (820, 700), (700, 760)], fill=(200, 216, 196))
    for x, y, lab, yr in ((930, 600, "京都", "1917年"), (1190, 420, "東京", "1923年"), (860, 650, "大阪", "1932年")):
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(220, 70, 70), outline=(255, 255, 255), width=4)
    _text_c(d, 960, 520, "京都 1917年", 40, ink)
    _text_c(d, 1200, 450, "東京 1923年", 40, ink)
    _text_c(d, 800, 690, "大阪 1932年", 40, ink)
    return img


def senji():
    """戦時の郡上の作業場。お膳の供え物の模型。"""
    img = _rgb(base((150, 136, 116), (120, 108, 92)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([1320, 160, 1640, 460], fill=(170, 170, 150), outline=(80, 66, 50), width=10)
    d.rectangle([760, 600, 1160, 640], fill=(80, 50, 36))                    # 低い台
    d.rectangle([830, 540, 1090, 600], fill=(60, 30, 26))                    # お膳
    d.ellipse([850, 500, 930, 560], fill=(250, 250, 246))                    # ご飯
    d.chord([850, 490, 930, 540], 180, 360, fill=(250, 250, 246))
    d.ellipse([960, 510, 1040, 560], fill=(170, 60, 40))                     # 汁椀
    d.ellipse([968, 514, 1032, 534], fill=(200, 170, 120))
    d.ellipse([1050, 530, 1090, 560], fill=(120, 150, 80))                   # 小鉢
    return img


def kojo():
    """昭和30年代の郡上の工場。作業台に作りかけの見本、窓に山。"""
    img = _rgb(base((226, 222, 210), (206, 202, 190)))
    wood_floor(img, FLOOR, col=(140, 120, 96), line=(120, 102, 80))
    d = _d(img)
    for k in range(3):
        x0 = 200 + k * 560
        d.rectangle([x0, 120, x0 + 480, 380], fill=(170, 206, 230), outline=(100, 90, 80), width=8)
        d.polygon([(x0, 380), (x0 + 160, 220), (x0 + 300, 330), (x0 + 400, 240), (x0 + 480, 300), (x0 + 480, 380)], fill=(90, 130, 90))
    _table(d, 720, 1200, 620, col=(130, 110, 90))
    _omelette(d, 820, 580, 100)
    _ramen(d, 960, 570, 100)
    _tempura(d, 1100, 580, 90)
    return img


def koubou():
    """今の工房。部品の棚と、シリコンの型。"""
    img = _rgb(base((240, 240, 238), (224, 224, 220)))
    wood_floor(img, FLOOR, col=(170, 166, 160), line=(150, 146, 140))
    d = _d(img)
    cols = [(90, 170, 60), (246, 206, 80), (240, 150, 150), (250, 250, 240), (200, 80, 60), (230, 120, 60)]
    d.rectangle([640, 120, 1280, 540], fill=(200, 196, 190))
    for r in range(4):
        d.rectangle([640, 210 + r * 100, 1280, 220 + r * 100], fill=(150, 146, 140))
        for c in range(8):
            x = 660 + c * 78
            d.rectangle([x, 150 + r * 100, x + 64, 210 + r * 100], fill=(250, 250, 250), outline=(170, 170, 170), width=2)
            d.ellipse([x + 16, 164 + r * 100, x + 48, 196 + r * 100], fill=cols[(r + c) % 6])
    _table(d, 700, 1220, 640, col=(170, 170, 176))
    for k in range(3):
        d.rounded_rectangle([740 + k * 150, 580, 860 + k * 150, 640], radius=10, fill=(120, 180, 220))   # シリコン型
        d.ellipse([770 + k * 150, 595, 830 + k * 150, 625], fill=(90, 150, 190))
    return img


def zukai2():
    """図解: ぬるま湯の中で、ロウがレタスと天ぷらの衣になる。"""
    img = _rgb(base((244, 244, 240), (230, 230, 224)))
    d = _d(img)
    ink = (50, 56, 70)
    d.chord([700, 300, 1220, 820], 0, 180, fill=(220, 236, 244), outline=ink, width=6)   # 大きなボウル
    d.rectangle([700, 556, 1220, 564], fill=ink)
    for k in range(6):                                                                # レタス
        d.arc([760 + k * 22, 590 - k * 6, 940 + k * 10, 700 - k * 4], 180, 360, fill=(120, 190, 90), width=10)
    d.ellipse([800, 640, 900, 700], fill=(230, 245, 210))
    for k in range(7):                                                                # 衣
        x = 1040 + (k % 3) * 36
        y = 610 + (k // 3) * 30
        d.ellipse([x - 22, y - 12, x + 22, y + 12], fill=(240, 200, 110))
    d.polygon([(960, 330), (990, 330), (975, 540)], fill=(240, 200, 110))                # 注ぐロウ
    _text_c(d, 860, 840, "レタス", 40, ink)
    _text_c(d, 1080, 840, "天ぷらの衣", 40, ink)
    return img


def gendai():
    """合羽橋の店。キーホルダーやマグネットのサンプル。"""
    img = _rgb(base((246, 244, 240), (230, 226, 220)))
    wood_floor(img, FLOOR, col=(200, 186, 166), line=(180, 166, 146))
    d = _d(img)
    d.rectangle([640, 150, 1280, 640], fill=(210, 196, 176))
    for r in range(5):
        for c in range(9):
            x, y = 680 + c * 66, 190 + r * 88
            d.line([(x + 20, y - 20), (x + 20, y)], fill=(170, 170, 176), width=3)
            kind = (r + c) % 4
            if kind == 0:
                d.ellipse([x, y, x + 40, y + 30], fill=EGG)
            elif kind == 1:
                d.ellipse([x, y, x + 44, y + 36], fill=(240, 150, 150))
            elif kind == 2:
                d.ellipse([x, y, x + 40, y + 30], fill=(240, 200, 110))
            else:
                d.rectangle([x + 4, y, x + 40, y + 30], fill=(250, 250, 240), outline=(200, 60, 60), width=4)
    return img


def kara():
    """戦時の大阪の食堂。見本が消えて空になったケースと、貼り紙。"""
    img = _shokudo_base()
    d = _d(img)
    d.rectangle([720, 360, 1200, 640], fill=(210, 220, 226), outline=(110, 90, 70), width=8)
    d.line([(720, 500), (1200, 500)], fill=(150, 130, 110), width=6)
    d.rectangle([880, 400, 1040, 470], fill=(246, 240, 226), outline=(120, 100, 80), width=3)   # 貼り紙（文字なし）
    for k in range(3):
        d.line([(900, 418 + k * 16), (1020, 418 + k * 16)], fill=(90, 80, 70), width=3)
    return img


def _table_base():
    img = _rgb(base((236, 226, 210), (216, 204, 186)))
    wood_floor(img, FLOOR, col=(160, 130, 100), line=(140, 112, 86))
    d = _d(img)
    for k in range(3):
        d.rectangle([300 + k * 480, 140, 560 + k * 480, 360], fill=(250, 240, 200), outline=(150, 120, 90), width=6)   # 壁の品書き（文字なし）
    _table(d, 700, 1220, 620, col=(130, 96, 66))
    return img


def table():
    """店の中のテーブル。運ばれてきたオムライス。"""
    img = _table_base()
    d = _d(img)
    _omelette(d, 960, 570, 150)
    d.chord([878, 548, 1042, 600], 0, 180, fill=(220, 90, 60))
    d.rectangle([1080, 560, 1100, 620], fill=(200, 200, 206))            # スプーン
    return img


def table2():
    """同じ店のテーブル。運ばれてきた本物のオムレツ。"""
    img = _table_base()
    d = _d(img)
    _omelette(d, 960, 570, 150, wrinkles=True)
    d.rectangle([1080, 560, 1100, 620], fill=(200, 200, 206))
    return img


def yakeato():
    """戦後の焼け跡。バラックの食堂が店を開ける。"""
    img = vgrad((W, H), (190, 196, 200), (170, 170, 166))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(120, 110, 100))
    for x, h in ((80, 220), (300, 140), (1500, 200), (1720, 160)):         # 焼け残った壁
        d.rectangle([x, 700 - h, x + 140, 700], fill=(90, 84, 80))
    d.rectangle([700, 360, 1220, 700], fill=(150, 120, 90))                # バラック
    d.polygon([(680, 370), (960, 280), (1240, 370)], fill=(90, 80, 70))
    d.rectangle([760, 440, 1160, 600], fill=(210, 220, 226), outline=(110, 90, 70), width=6)
    _omelette(d, 860, 530, 90)
    _ramen(d, 1060, 520, 90)
    d.rectangle([780, 380, 1140, 420], fill=(60, 60, 90))                  # のれん
    return img


def omu1():
    """同じ家の卓。すゞが焼いた、シワのあるオムレツが1つだけ。"""
    img = _ie_base()
    d = _d(img)
    _omelette(d, 960, 580, 130, wrinkles=True)
    return img


def shucchou():
    """出張先の別の店。この店の名物の天丼と、型取りの道具。"""
    img = _rgb(base((226, 214, 196), (206, 194, 176)))
    wood_floor(img, FLOOR, col=(120, 90, 60), line=(100, 74, 50))
    d = _d(img)
    d.rectangle([0, 60, W, 140], fill=(40, 60, 90))
    for k in range(5):
        d.rectangle([80 + k * 380, 140, 360 + k * 380, 250], fill=(240, 236, 220))
    d.rectangle([700, 600, 1220, 660], fill=(110, 80, 56))                    # 台
    d.chord([800, 470, 960, 630], 0, 180, fill=(40, 70, 120))                 # 名物の丼（藍色）
    d.ellipse([800, 520, 960, 570], fill=(60, 90, 140))
    for k in range(3):
        d.ellipse([820 + k * 40, 500, 870 + k * 40, 540], fill=(240, 200, 110), outline=(210, 160, 70), width=3)
    d.rectangle([1010, 560, 1150, 600], fill=(230, 220, 170), outline=(160, 150, 110), width=3)   # 寒天の型
    d.ellipse([1040, 568, 1120, 592], fill=(200, 190, 140))
    return img


def kojo_mono():
    """亡くなった場面用。郡上の工場を白黒にしたもの。"""
    return kojo().convert("L").convert("RGB")


LOCATIONS = {
    "sp_mise": mise, "sp_jinja": jinja, "sp_hoko": hoko, "sp_ie": ie, "sp_ie2": ie2, "sp_shisaku": shisaku,
    "sp_omu": omu, "sp_shokudo": shokudo, "sp_shokudo2": shokudo2, "sp_sogo": sogo, "sp_zukai": zukai,
    "sp_senji": senji, "sp_kojo": kojo, "sp_koubou": koubou, "sp_zukai2": zukai2, "sp_gendai": gendai,
    "sp_kara": kara, "sp_table": table, "sp_table2": table2, "sp_yakeato": yakeato,
    "sp_omu1": omu1, "sp_shucchou": shucchou, "sp_kojo_mono": kojo_mono,
}

CARDS = ["1895", "1931", "1932", "1939", "1948", "1963"]


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
        if only and f"sp_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"sp_card_{y}.png")
        print(f"生成完了: sp_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
