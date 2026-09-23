#!/usr/bin/env python3
"""魚群探知機の誕生・古野兄弟回（54_魚群探知機の誕生 / slug=furuno-fishfinder）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はカシオ回（gen_casio_bgs.py）と同じ。
実在メーカーの商標（ロゴ・店名の文字）は描かない。

実行: PYTHONPATH=. python scripts/gen_furuno_bgs.py [名前...]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, glow, hanging_bulb, vgrad, wood_floor,
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


def _sky_sea(img, horizon, sky_top, sky_bot, sea_top, sea_bot):
    img.paste(vgrad((W, horizon), sky_top, sky_bot), (0, 0))
    img.paste(vgrad((W, H - horizon), sea_top, sea_bot), (0, horizon))


def _islands(d, y, col):
    for x0, w, h in ((60, 420, 100), (620, 260, 60), (1300, 460, 120), (1780, 200, 50)):
        d.ellipse([x0, y - h, x0 + w, y + h * 0.4], fill=col)


def _deck(d, y0, col=(122, 92, 64), line=(96, 72, 50)):
    """手前の船べりと甲板。"""
    d.rectangle([0, y0, W, H], fill=col)
    for x in range(0, W, 160):
        d.line([(x, y0), (x - 90, H)], fill=line, width=4)
    d.rectangle([0, y0 - 40, W, y0], fill=(92, 70, 50))                 # 船べり


def _radio(d, x, y, s=1.0):
    """昭和初めの箱型ラジオ。丸いスピーカーとつまみ2つ。"""
    w, h = int(150 * s), int(120 * s)
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(14 * s), fill=(110, 76, 48), outline=(70, 48, 30), width=3)
    d.ellipse([x + 20 * s, y + 16 * s, x + 90 * s, y + 86 * s], fill=(190, 170, 130))
    for k in range(4):
        yy = y + 30 * s + k * 14 * s
        d.line([(x + 28 * s, yy), (x + 82 * s, yy)], fill=(140, 120, 90), width=2)
    for k in range(2):
        cx, cy = x + 118 * s, y + 36 * s + k * 40 * s
        d.ellipse([cx - 12 * s, cy - 12 * s, cx + 12 * s, cy + 12 * s], fill=(50, 40, 34))


def _lamp(img, x, y, lit=True):
    """集魚灯（笠つきの大きな電球）。"""
    d = _d(img)
    if lit:
        _glow(img, x, y + 70, 180, (255, 236, 170), 120)
        d = _d(img)
    d.polygon([(x - 70, y + 40), (x + 70, y + 40), (x + 40, y), (x - 40, y)], fill=(70, 74, 80))
    d.ellipse([x - 34, y + 30, x + 34, y + 100], fill=(255, 244, 200) if lit else (210, 210, 200))


def _sounder(d, x, y, s=1.0, noisy=False, school=False):
    """初期の魚群探知機。記録紙が流れる箱。noisy=True なら雑音だらけ、school=True なら群れの濃い影。"""
    w, h = int(260 * s), int(230 * s)
    d.rectangle([x, y, x + w, y + h], fill=(96, 104, 100), outline=(56, 60, 58), width=4)
    d.rectangle([x + 24 * s, y + 24 * s, x + w - 24 * s, y + 150 * s], fill=(236, 230, 210))
    if noisy:
        rnd = random.Random(1947)
        for k in range(5):
            yy = y + (44 + k * 20) * s
            pts = [(x + (30 + i * 11) * s, yy + rnd.uniform(-12, 12) * s) for i in range(19)]
            d.line(pts, fill=(80, 70, 120), width=3)
    elif school:
        d.ellipse([x + 44 * s, y + 52 * s, x + w - 44 * s, y + 118 * s], fill=(80, 70, 120))   # 群れの影
        d.ellipse([x + 70 * s, y + 40 * s, x + w - 90 * s, y + 90 * s], fill=(80, 70, 120))
    else:
        for k in range(6):                                                # 記録紙の影
            cx = x + 50 * s + k * 30 * s
            d.arc([cx - 16 * s, y + 70 * s, cx + 16 * s, y + 110 * s], 200, 340, fill=(80, 70, 120), width=4)
    d.line([(x + 24 * s, y + 132 * s), (x + w - 24 * s, y + 132 * s)], fill=(90, 70, 110), width=5)
    for k in range(3):
        cx = x + 60 * s + k * 70 * s
        d.ellipse([cx - 16 * s, y + 170 * s, cx + 16 * s, y + 202 * s], fill=(40, 42, 44))


def _crates(d, x0, y1, cols, rows, w=150, h=110, col=(170, 134, 90)):
    for r in range(rows):
        for c in range(cols - (r % 2)):
            x = x0 + c * w + (r % 2) * w // 2
            y = y1 - (r + 1) * h
            d.rectangle([x, y, x + w - 8, y + h - 8], fill=col, outline=(110, 84, 56), width=4)
            d.line([(x, y + h // 2), (x + w - 8, y + h // 2)], fill=(130, 100, 66), width=3)


def _boat(d, x, y, s=1.0, col=(120, 90, 64)):
    """木造の小型漁船。"""
    d.polygon([(x, y), (x + 420 * s, y), (x + 380 * s, y + 70 * s), (x + 30 * s, y + 70 * s)], fill=col)
    d.rectangle([x + 150 * s, y - 70 * s, x + 260 * s, y], fill=(200, 196, 184))
    d.line([(x + 320 * s, y), (x + 320 * s, y - 170 * s)], fill=(80, 64, 50), width=max(3, int(6 * s)))


# ------------------------------------------------------------ 現代
def ima():
    """現代の堤防。海と島。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 520, (150, 196, 234), (206, 226, 238), (70, 140, 180), (40, 100, 140))
    d = _d(img)
    _islands(d, 530, (96, 136, 110))
    d.polygon([(0, 760), (W, 700), (W, H), (0, H)], fill=(186, 184, 176))  # 堤防
    d.line([(0, 760), (W, 700)], fill=(140, 138, 130), width=10)
    for x in (360, 1560):                                                # 係船柱
        d.rounded_rectangle([x, 640, x + 70, 740], radius=18, fill=(80, 84, 90))
    return img


def _phone(img, shime=False):
    """人物の間（x790〜1130）に置く、スマホの魚探の画面。"""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 790, 150, 1130, 640
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=(30, 32, 38))
    sx0, sy0, sx1, sy1 = x0 + 18, y0 + 50, x1 - 18, y1 - 50
    img.paste(vgrad((sx1 - sx0, sy1 - sy0), (40, 90, 170), (10, 30, 90)), (sx0, sy0))
    d = ImageDraw.Draw(img)
    d.polygon([(sx0, 490), (sx0 + 90, 480), (sx0 + 200, 494), (sx1, 484), (sx1, 540), (sx0, 540)],
              fill=(220, 60, 40))                                          # 赤い海底
    d.polygon([(sx0, 470), (sx0 + 90, 462), (sx0 + 200, 476), (sx1, 466), (sx1, 492), (sx0 + 200, 500),
               (sx0 + 90, 488), (sx0, 494)], fill=(240, 200, 60))
    d.ellipse([sx0 + 60, 300, sx0 + 230, 380], fill=(80, 190, 110))      # 雲のような群れ
    d.ellipse([sx0 + 90, 316, sx0 + 200, 364], fill=(240, 200, 60))
    if shime:
        for ax, ay in ((sx0 + 50, 230), (sx0 + 170, 250), (sx0 + 240, 410)):   # への字（1匹の魚）
            d.arc([ax - 26, ay, ax + 26, ay + 40], 200, 340, fill=(240, 140, 60), width=7)
        d.rectangle([sx0 + 200, 540, sx0 + 250, sy1], fill=(160, 40, 36))       # 海底の下に伸びる長い影
    d.rounded_rectangle([x0 + 130, y0 + 18, x1 - 130, y0 + 30], radius=6, fill=(60, 62, 70))


def _rod(d):
    """堤防に立てかけた釣り竿（つむぎの左、スマホの右）。"""
    d.line([(1150, 720), (1250, 160)], fill=(60, 50, 44), width=8)
    d.line([(1250, 160), (1262, 110)], fill=(90, 80, 70), width=4)
    d.ellipse([1150, 640, 1190, 680], fill=(120, 120, 130))              # リール


def _jellyfish(d):
    d.ellipse([860, 690, 1060, 770], fill=(226, 228, 246), outline=(180, 184, 210), width=4)
    d.ellipse([920, 706, 1000, 746], fill=(240, 190, 220))
    for k in range(5):
        x = 880 + k * 40
        d.line([(x, 760), (x - 10, 800)], fill=(200, 204, 230), width=4)


def _sardine(d):
    d.ellipse([880, 720, 1040, 760], fill=(170, 190, 206), outline=(110, 130, 150), width=3)
    d.polygon([(1036, 740), (1080, 716), (1080, 764)], fill=(150, 170, 190))
    d.ellipse([896, 730, 910, 744], fill=(30, 30, 40))


def ima_hook():
    """現代の堤防と、スマホの魚探の画面と竿（冒頭）。"""
    img = ima()
    _phone(img)
    _rod(_d(img))
    return img


def ima_hook2():
    """冒頭のオチ。堤防に釣り上げたクラゲ。"""
    img = ima_hook()
    _jellyfish(_d(img))
    return img


def ima_shime():
    """現代の堤防と、スマホの魚探の画面（シメ。への字と長い影が増える）と竿。"""
    img = ima()
    _phone(img, shime=True)
    _rod(_d(img))
    return img


def ima_shime2():
    """シメのオチ。堤防にイワシが1匹。"""
    img = ima_shime()
    _sardine(_d(img))
    return img


def machi():
    """昭和初めの口之津の港町。木造の家並みと小舟。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 560, (176, 204, 226), (214, 220, 214), (80, 130, 150), (60, 104, 124))
    d = _d(img)
    d.ellipse([-200, 380, 900, 700], fill=(100, 128, 96))                 # 山
    for x0, h in ((980, 240), (1230, 280), (1500, 220), (1720, 260)):
        d.rectangle([x0, 640 - h, x0 + 220, 640], fill=(120, 100, 80))
        d.polygon([(x0 - 20, 660 - h), (x0 + 110, 580 - h), (x0 + 240, 660 - h)], fill=(80, 70, 62))
    d.rectangle([900, 640, W, 700], fill=(170, 156, 126))                # 岸
    for k in range(3):
        _boat(d, 120 + k * 280, 700 + k * 40, 0.55)
    d.rectangle([0, 900, W, H], fill=(160, 146, 118))
    return img


def mise():
    """昭和の町の電器屋。棚のラジオと、修理を待つ集魚灯。"""
    img = base((212, 196, 170), (180, 164, 140))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 96, 70), line=(100, 80, 58))
    d = _d(img)
    for y in (220, 420):                                                  # 棚
        d.rectangle([80, y + 130, 640, y + 146], fill=(110, 84, 58))
        for k in range(3):
            _radio(d, 100 + k * 180, y, 1.0)
    d.rectangle([1260, 250, 1840, 266], fill=(110, 84, 58))
    for k in range(3):
        _radio(d, 1280 + k * 185, 130, 1.0)
    d.rectangle([700, 640, 1220, 700], fill=(140, 108, 76))              # 作業台
    for k in range(3):                                                    # 集魚灯
        _lamp(img, 1340 + k * 180, 520, lit=False)
    hanging_bulb(img, 960)
    return img


def tachibana():
    """夜の橘湾。集魚灯をともした漁船の甲板。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 480, (14, 20, 40), (30, 40, 66), (18, 30, 50), (10, 18, 30))
    d = _d(img)
    for k in range(3):                                                    # 沖の漁火
        _glow(img, 300 + k * 600, 470, 60, (255, 230, 160), 120)
    d = _d(img)
    _deck(d, 820, col=(90, 70, 52), line=(70, 54, 40))
    for x in (520, 1400):
        d.line([(x, 820), (x, 360)], fill=(60, 50, 40), width=10)
        _lamp(img, x, 330)
    d = _d(img)
    for k in range(12):                                                   # 海面の照り返し
        x = 380 + (k * 131) % 1200
        d.line([(x, 560 + (k % 5) * 40), (x + 80, 560 + (k % 5) * 40)], fill=(200, 190, 140), width=3)
    return img


def kenkyu():
    """戦後すぐの作業場。海軍の音響測深機と、工具。"""
    img = base((190, 182, 164), (156, 148, 132))
    d = _d(img)
    wood_floor(img, FLOOR, col=(110, 92, 72), line=(92, 76, 60))
    d = _d(img)
    _window(d, 120, 160, 560, 460, sky=(160, 186, 200))
    d.rectangle([560, 600, 1300, 660], fill=(120, 96, 70))               # 作業台
    d.rectangle([610, 330, 890, 600], fill=(90, 100, 96), outline=(52, 58, 56), width=5)    # 測深機
    d.ellipse([640, 370, 760, 490], fill=(220, 214, 196), outline=(60, 60, 60), width=4)
    d.line([(700, 430), (740, 390)], fill=(160, 40, 40), width=4)
    for k in range(4):
        d.ellipse([800, 380 + k * 50, 840, 420 + k * 50], fill=(40, 42, 44))
    d.rectangle([640, 520, 860, 580], fill=(236, 230, 210), outline=(150, 140, 120), width=3)   # 記録紙
    for k in range(2):
        d.line([(660, 540 + k * 20), (840, 540 + k * 20)], fill=(170, 160, 150), width=2)
    for k in range(5):                                                    # 壁の工具
        x = 1400 + k * 90
        d.line([(x, 220), (x, 380)], fill=(80, 80, 84), width=10)
    hanging_bulb(img, 1260, ly=60)
    return img


def goto():
    """昼の五島灘。試験の漁船の甲板。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 470, (150, 190, 226), (204, 220, 230), (60, 120, 160), (36, 86, 120))
    d = _d(img)
    _islands(d, 480, (90, 120, 100))
    _deck(d, 800)
    d.rectangle([1420, 500, 1800, 800], fill=(200, 196, 184), outline=(120, 110, 100), width=6)   # 操舵室
    d.rectangle([1470, 560, 1750, 660], fill=(150, 180, 200))
    d.rectangle([1640, 380, 1690, 500], fill=(60, 56, 54))              # 煙突
    for k in range(4):
        r = 36 + k * 16
        d.ellipse([1660 - r + k * 30, 330 - k * 70 - r, 1660 + r + k * 30, 330 - k * 70 + r], fill=(120, 120, 124))
    _sounder(d, 670, 590, 0.85, noisy=True)
    return img


def chousei():
    """夜の長生丸。甲板の魚探と、集魚灯。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 480, (10, 16, 34), (24, 34, 60), (16, 28, 48), (8, 16, 28))
    d = _d(img)
    _deck(d, 820, col=(86, 66, 50), line=(66, 50, 38))
    d.line([(1500, 820), (1500, 360)], fill=(60, 50, 40), width=10)
    _lamp(img, 1500, 330)
    d = _d(img)
    _glow(img, 950, 700, 200, (240, 230, 200), 60)
    d = _d(img)
    _sounder(d, 820, 590, 0.9, school=True)
    for k in range(30):                                                   # 星
        x, y = (k * 211) % W, (k * 97) % 400
        d.ellipse([x, y, x + 4, y + 4], fill=(220, 224, 240))
    return img


def kurage0():
    """夕方の漁船の甲板。魚探の記録紙に大きな影。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 470, (236, 170, 120), (240, 206, 170), (90, 100, 130), (50, 64, 90))
    d = _d(img)
    _islands(d, 480, (90, 90, 96))
    _deck(d, 800)
    x, y, s = 830, 580, 0.9
    w = int(260 * s)
    d.rectangle([x, y, x + w, y + int(230 * s)], fill=(96, 104, 100), outline=(56, 60, 58), width=4)
    d.rectangle([x + 22, y + 22, x + w - 22, y + 135], fill=(236, 230, 210))
    d.ellipse([x + 40, y + 50, x + w - 40, y + 110], fill=(80, 70, 120))   # 大きな影
    d.line([(x + 22, y + 120), (x + w - 22, y + 120)], fill=(90, 70, 110), width=5)
    for k in range(3):
        cx = x + 54 + k * 63
        d.ellipse([cx - 14, y + 153, cx + 14, y + 181], fill=(40, 42, 44))
    return img


def kurage():
    """夕方の漁船。網にかかったクラゲの群れ。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 470, (236, 170, 120), (240, 206, 170), (90, 100, 130), (50, 64, 90))
    d = _d(img)
    _islands(d, 480, (90, 90, 96))
    _deck(d, 800)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([560, 700, 1000, 900], fill=(90, 110, 90, 255))            # 網
    for k in range(12):
        cx = 610 + (k * 97) % 340
        cy = 740 + (k * 53) % 120
        d.ellipse([cx - 44, cy - 30, cx + 44, cy + 26], fill=(230, 230, 250, 200))
        d.ellipse([cx - 16, cy - 12, cx + 16, cy + 8], fill=(240, 190, 220, 220))
    for x in range(560, 1000, 34):
        d.line([(x, 700), (x + 40, 900)], fill=(60, 80, 60, 180), width=2)
    return img


def jimusho():
    """1948年の長崎駅前の小さな事務所。机が並ぶ。"""
    img = base((214, 206, 190), (186, 178, 162))
    d = _d(img)
    wood_floor(img, FLOOR, col=(130, 106, 80), line=(110, 90, 66))
    d = _d(img)
    _window(d, 640, 140, 1280, 470, sky=(176, 204, 226))
    d.rectangle([700, 360, 1220, 460], fill=(140, 130, 120))              # 窓の外の駅舎
    d.polygon([(680, 360), (960, 280), (1240, 360)], fill=(110, 90, 80))
    for k in range(3):
        x = 200 + k * 560
        d.rectangle([x, 640, x + 420, 680], fill=(140, 108, 76))
        d.rectangle([x + 20, 680, x + 40, 820], fill=(110, 84, 60))
        d.rectangle([x + 380, 680, x + 400, 820], fill=(110, 84, 60))
    hanging_bulb(img, 480)
    hanging_bulb(img, 1440)
    return img


def jimusho55():
    """1955年ごろの事務所。壁に世界地図。"""
    img = base((214, 206, 190), (186, 178, 162))
    d = _d(img)
    wood_floor(img, FLOOR, col=(130, 106, 80), line=(110, 90, 66))
    d = _d(img)
    d.rectangle([620, 110, 1300, 470], fill=(170, 200, 214), outline=(90, 76, 60), width=10)
    for cx, cy, rx, ry in ((760, 220, 90, 50), (800, 360, 40, 60), (940, 210, 40, 30), (950, 330, 50, 70),
                           (1080, 220, 110, 60), (1150, 380, 50, 30)):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(150, 170, 120))
    for k in range(3):
        x = 200 + k * 560
        d.rectangle([x, 640, x + 420, 680], fill=(140, 108, 76))
        d.rectangle([x + 20, 680, x + 40, 820], fill=(110, 84, 60))
        d.rectangle([x + 380, 680, x + 400, 820], fill=(110, 84, 60))
    hanging_bulb(img, 480)
    hanging_bulb(img, 1440)
    return img


def henpin():
    """返品の木箱が積み上がった工業所の中。"""
    img = base((196, 186, 168), (160, 150, 134))
    d = _d(img)
    wood_floor(img, FLOOR, col=(110, 92, 72), line=(92, 76, 60))
    d = _d(img)
    _crates(d, 60, FLOOR, 4, 4)
    _crates(d, 1260, FLOOR, 4, 3)
    _crates(d, 700, FLOOR, 3, 2, col=(160, 126, 86))
    hanging_bulb(img, 960, ly=60)
    return img


def minato():
    """五島・岩瀬浦の港。並んだ漁船と山。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 520, (160, 200, 232), (210, 226, 232), (70, 130, 160), (50, 104, 130))
    d = _d(img)
    d.ellipse([-300, 300, 1100, 700], fill=(90, 126, 92))
    d.ellipse([900, 340, 2300, 720], fill=(100, 136, 100))
    for k in range(4):
        _boat(d, 80 + k * 470, 620 + (k % 2) * 30, 0.8)
    d.rectangle([0, 820, W, H], fill=(170, 164, 150))                   # 岸壁
    d.line([(0, 820), (W, 820)], fill=(130, 124, 112), width=8)
    return img


def mizuage():
    """岩瀬浦の水揚げ。イワシの木箱が岸壁に積まれる。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 460, (170, 206, 232), (214, 226, 230), (70, 130, 160), (50, 104, 130))
    d = _d(img)
    _boat(d, 700, 470, 1.0)
    d.rectangle([0, 640, W, H], fill=(176, 170, 156))
    _crates(d, 40, 900, 4, 2, w=140, h=90, col=(180, 150, 104))
    _crates(d, 1330, 900, 4, 2, w=140, h=90, col=(180, 150, 104))
    for k in range(18):                                                   # 箱の上のイワシ
        x = 60 + (k % 9) * 64 if k < 9 else 1350 + (k % 9) * 64
        d.ellipse([x, 700, x + 56, 716], fill=(196, 206, 214))
    return img


def koujou():
    """1950年ごろの工業所の外観。木造2階建て。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 200, 226), (214, 216, 210)), (0, 0))
    d = _d(img)
    d.rectangle([420, 260, 1500, 760], fill=(150, 124, 96))
    d.polygon([(380, 280), (960, 150), (1540, 280)], fill=(80, 72, 66))
    for k in range(5):
        x = 480 + k * 200
        d.rectangle([x, 330, x + 130, 440], fill=(180, 204, 216), outline=(90, 76, 60), width=6)
    d.rectangle([860, 560, 1060, 760], fill=(90, 72, 54))               # 入口
    d.rectangle([720, 480, 1200, 530], fill=(236, 230, 214), outline=(90, 76, 60), width=5)   # 無地の看板
    d.rectangle([0, 760, W, H], fill=(170, 160, 136))
    return img


def zukai():
    """図解用。船から出た音が群れと海底で跳ね返る図（左）と、それを並べた記録紙（右）。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (40, 90, 140), (10, 24, 50)), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W, 170], fill=(170, 206, 234, 255))              # 空
    cx = 820
    d.polygon([(cx - 150, 150), (cx + 150, 150), (cx + 124, 210), (cx - 124, 210)], fill=(110, 84, 60, 255))   # 船
    d.rectangle([cx - 50, 90, cx + 50, 150], fill=(210, 206, 196, 255))
    d.polygon([(cx, 210), (cx - 170, 860), (cx + 170, 860)], fill=(250, 250, 200, 60))   # 音の広がり
    for k in range(1, 7):
        y = 210 + k * 100
        half = (y - 210) * 170 // 650
        d.arc([cx - half, y - 30, cx + half, y + 30], 20, 160, fill=(250, 250, 210, 170), width=4)
    for k in range(40):                                                   # 群れ
        fx = cx - 70 + (k * 37) % 140
        fy = 520 + (k * 53) % 80
        d.ellipse([fx - 12, fy - 5, fx + 12, fy + 5], fill=(210, 220, 230, 230))
    d.polygon([(0, 900), (500, 870), (960, 880), (1400, 860), (W, 890), (W, H), (0, H)], fill=(120, 96, 70, 255))
    # 記録紙（時間の順に左から右へ並べる）
    x0, x1, y0, y1 = 1040, 1300, 230, 820
    d.rectangle([x0, y0, x1, y1], fill=(236, 230, 210, 255), outline=(150, 140, 120, 255), width=6)
    d.ellipse([x0 + 50, 470, x1 - 50, 600], fill=(80, 70, 120, 255))    # 群れの影
    d.line([(x0 + 6, 740), (x0 + 80, 730), (x0 + 170, 748), (x1 - 6, 736)], fill=(90, 70, 110, 255), width=12)
    return img


def shinka():
    """画面の移り変わり。記録紙→ブラウン管→カラー。キャラの間に縦に積む。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (34, 40, 52), (18, 22, 30)), (0, 0))
    d = _d(img)
    x0, x1 = 740, 1180
    # 記録紙
    d.rectangle([x0, 90, x1, 330], fill=(236, 230, 210))
    for k in range(7):
        cx = x0 + 50 + k * 56
        d.arc([cx - 22, 170, cx + 22, 230], 200, 340, fill=(80, 70, 130), width=5)
    d.line([(x0, 290), (x1, 290)], fill=(90, 70, 120), width=6)
    # ブラウン管
    d.rounded_rectangle([x0, 380, x1, 620], radius=40, fill=(20, 40, 24), outline=(90, 94, 90), width=8)
    for k in range(6):
        cx = x0 + 60 + k * 64
        d.arc([cx - 24, 450, cx + 24, 510], 200, 340, fill=(120, 230, 120), width=5)
    d.line([(x0 + 20, 580), (x1 - 20, 580)], fill=(120, 230, 120), width=6)
    # カラー
    d.rectangle([x0, 670, x1, 910], fill=(16, 30, 90), outline=(90, 94, 90), width=8)
    d.ellipse([x0 + 120, 720, x0 + 300, 800], fill=(230, 190, 60))
    d.ellipse([x0 + 150, 736, x0 + 270, 784], fill=(220, 70, 50))
    d.rectangle([x0 + 8, 850, x1 - 8, 902], fill=(200, 70, 50))
    d.rectangle([x0 + 8, 830, x1 - 8, 850], fill=(230, 190, 60))
    return img


def bridge():
    """今の漁船の操舵室。色つきの魚探の画面が並ぶ。"""
    img = base((70, 80, 92), (40, 46, 56))
    d = _d(img)
    d.rectangle([0, 120, W, 440], fill=(150, 190, 220))                  # 窓
    for x in range(0, W, 380):
        d.rectangle([x, 120, x + 16, 440], fill=(50, 56, 64))
    d.rectangle([0, 600, W, H], fill=(60, 66, 74))                       # 計器盤
    for k in range(3):
        x = 560 + k * 290
        d.rectangle([x, 470, x + 250, 640], fill=(16, 30, 90), outline=(30, 30, 34), width=8)
        d.ellipse([x + 60, 520, x + 170, 570], fill=(230, 190, 60))
        d.ellipse([x + 80, 530, x + 150, 560], fill=(220, 70, 50))
        d.rectangle([x + 8, 600, x + 242, 632], fill=(200, 70, 50))
    return img


def gyokou():
    """今の漁港。鉄の漁船と、岸壁の水揚げ場。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 520, (160, 200, 232), (214, 226, 234), (60, 110, 150), (40, 84, 120))
    d = _d(img)
    d.ellipse([-200, 360, 700, 620], fill=(96, 126, 100))
    for k, (x, y, s) in enumerate(((120, 600, 0.9), (1200, 620, 1.0))):
        d.polygon([(x, y), (x + 520 * s, y), (x + 470 * s, y + 90 * s), (x + 40 * s, y + 90 * s)], fill=(220, 224, 228))
        d.rectangle([x + 200 * s, y - 110 * s, x + 340 * s, y], fill=(236, 238, 240), outline=(120, 130, 140), width=3)
        d.rectangle([x + 214 * s, y - 90 * s, x + 326 * s, y - 50 * s], fill=(120, 160, 190))
        d.line([(x + 280 * s, y - 110 * s), (x + 280 * s, y - 230 * s)], fill=(90, 96, 104), width=6)
    d.rectangle([0, 800, W, H], fill=(176, 178, 176))
    d.line([(0, 800), (W, 800)], fill=(130, 132, 130), width=8)
    d.rectangle([620, 700, 1300, 800], fill=(90, 110, 140))              # 水揚げ場の屋根
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


def yuuhi():
    """夕暮れの海。静かな場面で使う。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 560, (70, 60, 100), (230, 150, 110), (110, 80, 90), (40, 36, 56))
    d = _d(img)
    d.ellipse([860, 470, 1060, 670], fill=(250, 200, 140))
    img.paste(vgrad((W, H - 560), (110, 80, 90), (40, 36, 56)), (0, 560))
    d = _d(img)
    for k in range(10):
        y = 590 + k * 34
        half = 120 - k * 8
        d.line([(960 - half, y), (960 + half, y)], fill=(240, 180, 130), width=5)
    _islands(d, 570, (50, 44, 60))
    return img


def masutomi():
    """夜の桝富丸。集魚灯2つと、甲板の魚探。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 500, (8, 14, 30), (22, 30, 56), (14, 26, 44), (6, 14, 26))
    d = _d(img)
    _islands(d, 505, (16, 22, 34))
    _deck(d, 830, col=(96, 72, 52), line=(74, 56, 40))
    for x in (380, 1560):
        d.line([(x, 830), (x, 380)], fill=(60, 50, 40), width=10)
        _lamp(img, x, 350)
    d = _d(img)
    _glow(img, 960, 700, 200, (240, 230, 200), 60)
    d = _d(img)
    _sounder(d, 830, 600, 0.9, school=True)
    return img


def hatoba():
    """曇り空の、よその港の岸壁。係留された漁船。"""
    img = Image.new("RGB", (W, H))
    _sky_sea(img, 540, (170, 176, 184), (206, 208, 210), (90, 110, 124), (70, 88, 100))
    d = _d(img)
    d.ellipse([1000, 380, 2300, 700], fill=(110, 120, 112))
    _boat(d, 180, 620, 0.9, col=(110, 96, 80))
    _boat(d, 1300, 650, 0.7, col=(100, 84, 70))
    d.rectangle([0, 800, W, H], fill=(160, 156, 148))
    d.line([(0, 800), (W, 800)], fill=(120, 116, 108), width=8)
    _crates(d, 1500, 800, 2, 2, w=130, h=90, col=(150, 130, 100))
    return img


LOCATIONS = {
    "fr_ima_hook": ima_hook, "fr_ima_hook2": ima_hook2, "fr_ima_shime": ima_shime, "fr_ima_shime2": ima_shime2, "fr_machi": machi, "fr_mise": mise, "fr_tachibana": tachibana,
    "fr_kenkyu": kenkyu, "fr_goto": goto, "fr_chousei": chousei, "fr_kurage0": kurage0, "fr_kurage": kurage,
    "fr_jimusho": jimusho, "fr_jimusho55": jimusho55, "fr_henpin": henpin, "fr_minato": minato, "fr_mizuage": mizuage,
    "fr_koujou": koujou, "fr_zukai": zukai, "fr_shinka": shinka, "fr_bridge": bridge,
    "fr_gyokou": gyokou, "fr_shiryo": shiryo, "fr_yuuhi": yuuhi,
    "fr_masutomi": masutomi, "fr_hatoba": hatoba,
}

CARDS = ["1938", "1943", "1945", "1947", "1948", "1949", "1955"]


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
        if only and f"fr_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"fr_card_{y}.png")
        print(f"生成完了: fr_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
