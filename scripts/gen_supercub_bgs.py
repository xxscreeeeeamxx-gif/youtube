#!/usr/bin/env python3
"""スーパーカブの誕生回（65_スーパーカブの誕生 / slug=fujisawa-supercub）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はエアバッグ回（gen_airbag_bgs.py）と同じ。
実在の会社の商標（ロゴ・社名の文字）は描かない。カブの絵にも社名やマークは入れない。

実行: PYTHONPATH=. python scripts/gen_supercub_bgs.py [名前...]
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
INK = (60, 60, 66)
CUB_BLUE = (96, 150, 200)
SHIELD = (238, 238, 230)
SEAT = (130, 40, 60)


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


def _papers(d, x0, y0, n=3, col=(244, 240, 228)):
    for k in range(n):
        x, y = x0 + k * 22, y0 - k * 8
        d.rectangle([x, y, x + 120, y + 80], fill=col, outline=(170, 160, 140), width=2)
        for j in range(4):
            d.line([(x + 12, y + 16 + j * 15), (x + 100, y + 16 + j * 15)], fill=(150, 150, 150), width=2)


def _cub(d, x0, yg, s=1.0, body=CUB_BLUE, shield=SHIELD, seat=SEAT, demae=False):
    """横から見たスーパーカブ（右向き）。x0 は後ろの端、yg は地面の高さ。"""
    r = 62 * s
    rx, fx = x0 + 70 * s, x0 + 330 * s
    cy = yg - r
    P = lambda pts: [(x0 + a * s, cy + b * s) for a, b in pts]  # noqa: E731
    for cx in (rx, fx):                                                         # 17インチの大きな車輪
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 40, 44))
        d.ellipse([cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72], outline=(170, 170, 176), width=int(3 * s) + 1)
        d.ellipse([cx - r * 0.15, cy - r * 0.15, cx + r * 0.15, cy + r * 0.15], fill=(170, 170, 176))
    d.chord([rx - r * 1.08, cy - r * 1.08, rx + r * 1.08, cy + r * 1.08], 190, 290, fill=body)   # 後ろの泥よけ
    d.polygon(P([(10, -40), (60, -112), (205, -118), (222, -48), (150, -18)]), fill=body)          # 座席の下（タンク）
    d.rounded_rectangle([x0 + 70 * s, cy - 138 * s, x0 + 205 * s, cy - 110 * s], radius=int(10 * s), fill=seat)
    d.rectangle([x0 + 5 * s, cy - 124 * s, x0 + 78 * s, cy - 114 * s], fill=(60, 60, 64))           # 荷台
    d.ellipse([x0 + 165 * s, cy - 40 * s, x0 + 255 * s, cy + 8 * s], fill=(150, 150, 156))         # 横置きのエンジン
    d.polygon(P([(205, -62), (262, -42), (302, -165), (286, -175)]), fill=body)                     # 低いフレーム
    d.polygon(P([(248, -14), (266, -150), (298, -182), (322, -150), (304, -18)]), fill=shield)       # 樹脂のレッグシールド
    d.line([(x0 + 306 * s, cy - 175 * s), (fx, cy)], fill=(90, 90, 96), width=int(8 * s) + 1)    # 前フォーク
    d.chord([fx - r * 1.08, cy - r * 1.08, fx + r * 1.08, cy + r * 1.08], 205, 335, fill=shield)  # 前の泥よけ
    d.polygon(P([(282, -205), (336, -210), (342, -186), (288, -182)]), fill=body)                   # ハンドルまわり
    d.ellipse([x0 + 328 * s, cy - 210 * s, x0 + 354 * s, cy - 184 * s], fill=(250, 240, 180))      # ライト
    d.line([(x0 + 262 * s, cy - 212 * s), (x0 + 296 * s, cy - 200 * s)], fill=(40, 40, 44), width=int(6 * s) + 1)
    if demae:                                                                  # 出前機とせいろ
        d.rectangle([x0 + 30 * s, cy - 210 * s, x0 + 38 * s, cy - 120 * s], fill=(70, 70, 76))
        d.line([(x0 + 34 * s, cy - 210 * s), (x0 + 34 * s, cy - 250 * s)], fill=(70, 70, 76), width=int(4 * s) + 1)
        for k in range(4):
            d.line([(x0 + 22 * s + k * 8 * s, cy - 250 * s), (x0 + 30 * s + k * 8 * s, cy - 262 * s)],
                   fill=(120, 120, 126), width=2)                              # ばね
        d.rounded_rectangle([x0 - 20 * s, cy - 330 * s, x0 + 90 * s, cy - 262 * s], radius=int(6 * s),
                            fill=(150, 90, 50), outline=(100, 60, 30), width=3)
        for k in range(1, 3):
            y = cy - 330 * s + k * 22 * s
            d.line([(x0 - 20 * s, y), (x0 + 90 * s, y)], fill=(100, 60, 30), width=2)


# ---------------------------------------------------------------- 場所
def machi(close=False):
    """今の町。のれんのそば屋と、出前機付きのカブ、赤い郵便のカブ。"""
    img = vgrad((W, H), (170, 206, 236), (220, 232, 240))
    d = _d(img)
    d.rectangle([0, 820, W, H], fill=(150, 150, 154))
    d.rectangle([420, 180, 1500, 820], fill=(200, 180, 150))                   # 店
    d.polygon([(380, 180), (960, 90), (1540, 180)], fill=(80, 70, 66))
    d.rectangle([760, 300, 1160, 420], fill=(40, 60, 90))                      # のれん（文字なし）
    for x in range(800, 1160, 80):
        d.line([(x, 300), (x, 420)], fill=(200, 200, 210), width=4)
    d.rectangle([760, 420, 1160, 820], fill=(90, 70, 50))
    if close:
        _cub(d, 700, 900, 1.3, demae=True)
    else:
        _cub(d, 640, 880, 0.95, demae=True)
        _cub(d, 1000, 880, 0.95, body=(200, 40, 40), shield=(200, 40, 40), seat=(40, 40, 44))
    return img


def machi2():
    return machi(close=True)


def ie():
    """大正の町家の座敷。ちゃぶ台と障子。"""
    img = _rgb(base((222, 210, 186), (202, 190, 166)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    for k in range(4):                                                          # 障子
        x = 700 + k * 130
        d.rectangle([x, 150, x + 120, 560], fill=(240, 236, 222), outline=(120, 90, 60), width=6)
        for j in range(1, 5):
            d.line([(x, 150 + j * 82), (x + 120, 150 + j * 82)], fill=(120, 90, 60), width=3)
    d.ellipse([820, 700, 1100, 770], fill=(110, 76, 50))                       # ちゃぶ台
    d.rectangle([850, 735, 870, 820], fill=(90, 60, 40))
    d.rectangle([1050, 735, 1070, 820], fill=(90, 60, 40))
    return img


def kouzai():
    """昭和初めの鋼材店。棚に並ぶ鉄の棒と板、帳場の机とそろばん。"""
    img = _rgb(base((214, 208, 196), (194, 188, 176)))
    wood_floor(img, FLOOR, col=(110, 96, 80), line=(90, 78, 64))
    d = _d(img)
    for k in range(5):                                                          # 鉄の棒の棚
        y = 200 + k * 70
        d.rectangle([1380, y, 1880, y + 12], fill=(90, 70, 50))
        for j in range(10):
            d.ellipse([1400 + j * 46, y - 26, 1430 + j * 46, y + 4], fill=(120, 124, 132), outline=(80, 84, 90))
    for k in range(4):                                                          # 鉄の板
        d.rectangle([60 + k * 20, 260 + k * 10, 360 + k * 20, 700], fill=(130 - k * 6, 134 - k * 6, 142 - k * 6), outline=(80, 84, 90))
    _table(d, 780, 1140, 640, col=(120, 90, 64))
    d.rectangle([840, 600, 1000, 640], fill=(80, 56, 36))                       # そろばん
    for k in range(8):
        d.line([(850 + k * 20, 604), (850 + k * 20, 636)], fill=(200, 180, 140), width=3)
    _papers(d, 1010, 580, 2)
    return img


def kiko():
    """福島に疎開した工場。旋盤と木箱、棚の上のラジオ。"""
    img = _rgb(base((200, 196, 186), (172, 168, 158)))
    wood_floor(img, FLOOR, col=(110, 100, 86), line=(90, 82, 70))
    d = _d(img)
    for x in (80, 1480):                                                        # 旋盤
        d.rectangle([x, 560, x + 360, 640], fill=(80, 90, 96))
        d.rectangle([x + 20, 640, x + 60, 800], fill=(70, 76, 80))
        d.rectangle([x + 300, 640, x + 340, 800], fill=(70, 76, 80))
        d.rectangle([x + 40, 500, x + 120, 560], fill=(90, 100, 106))
    for k in range(3):                                                          # 木箱
        d.rectangle([760 + k * 130, 640, 880 + k * 130, 760], fill=(170, 130, 80), outline=(110, 80, 50), width=4)
        d.line([(760 + k * 130, 640), (880 + k * 130, 760)], fill=(110, 80, 50), width=3)
    d.rectangle([860, 380, 1060, 400], fill=(110, 80, 50))                      # 棚
    d.rounded_rectangle([900, 290, 1020, 380], radius=16, fill=(120, 80, 50), outline=(70, 50, 30), width=4)  # ラジオ
    d.ellipse([920, 305, 970, 355], fill=(230, 220, 190))
    d.ellipse([985, 320, 1005, 340], fill=(60, 50, 40))
    return img


def zashiki():
    """阿佐ヶ谷の家の座敷。座卓にお茶、床の間。"""
    img = _rgb(base((226, 214, 190), (206, 194, 170)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([1500, 140, 1900, 700], fill=(200, 180, 150), outline=(110, 80, 50), width=8)   # 床の間
    d.rectangle([1640, 180, 1760, 520], fill=(236, 230, 214))                   # 掛け軸（文字なし）
    d.ellipse([1600, 600, 1700, 690], fill=(90, 110, 90))
    d.rectangle([620, 680, 1300, 720], fill=(110, 70, 44))                      # 座卓
    for x in (660, 1240):
        d.rectangle([x, 720, x + 20, 800], fill=(90, 56, 34))
    for x in (800, 960, 1120):                                                  # 湯のみ
        d.rounded_rectangle([x - 20, 640, x + 20, 680], radius=6, fill=(160, 170, 150))
    return img


def honsha(later=False):
    """1950年代の本社の部屋。机に手紙の束、壁に日本地図。later=True は重役室。"""
    img = _rgb(base((226, 222, 212), (206, 202, 192)))
    wood_floor(img, FLOOR, col=(120, 100, 80), line=(100, 84, 66))
    d = _d(img)
    if later:
        _window(d, 740, 120, 1180, 420, sky=(190, 210, 226))
        for k in range(5):                                                      # 窓の外のビル
            d.rectangle([760 + k * 84, 260 - (k % 3) * 40, 820 + k * 84, 410], fill=(150, 160, 170))
        _table(d, 700, 1220, 640, col=(90, 60, 40))
        d.rectangle([900, 610, 1020, 640], fill=(236, 236, 230))
        return img
    d.rectangle([760, 120, 1160, 440], fill=(236, 236, 226), outline=(90, 90, 96), width=6)    # 日本地図
    d.polygon([(1080, 150), (1120, 190), (1070, 260), (1000, 300), (940, 330), (880, 360), (820, 400),
               (800, 380), (860, 330), (930, 290), (1000, 250), (1050, 200)], fill=(170, 200, 160))
    rnd = random.Random(5)
    for _ in range(30):                                                         # 販売店のピン
        x, y = rnd.uniform(830, 1100), rnd.uniform(180, 380)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(200, 60, 50))
    _table(d, 740, 1180, 640, col=(130, 98, 70))
    for k in range(5):                                                          # 封筒の山
        d.rectangle([780 + k * 12, 600 - k * 8, 900 + k * 12, 640 - k * 8], fill=(236, 226, 200), outline=(170, 150, 120))
    for k in range(4):
        d.rectangle([980 + k * 10, 606 - k * 8, 1100 + k * 10, 640 - k * 8], fill=(244, 240, 228), outline=(170, 160, 140))
    return img


def honsha2():
    return honsha(later=True)


def kinai():
    """1950年代の旅客機の客室。窓の外にプロペラ。"""
    img = _rgb(base((226, 222, 212), (206, 202, 192)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(110, 90, 80))
    d.rectangle([0, 0, W, 90], fill=(236, 232, 222))
    for x in (720, 1040):                                                       # 窓
        d.rounded_rectangle([x, 200, x + 160, 380], radius=60, fill=(170, 206, 236), outline=(200, 196, 186), width=10)
    d.ellipse([1070, 270, 1130, 300], fill=(160, 160, 166))                    # プロペラ
    d.line([(1100, 230), (1100, 340)], fill=(60, 60, 66), width=6)
    for x in (80, 1540):                                                        # 座席
        d.rounded_rectangle([x, 320, x + 300, 800], radius=40, fill=(130, 90, 60))
        d.rounded_rectangle([x + 40, 280, x + 260, 360], radius=30, fill=(236, 232, 222))
    return img


def europe():
    """1950年代のヨーロッパの町。石畳と、モペッドやスクーター。"""
    img = vgrad((W, H), (180, 206, 230), (224, 230, 232))
    d = _d(img)
    for k in range(8):                                                          # 建物
        x = k * 250 - 30
        h = 420 + (k % 3) * 80
        d.rectangle([x, 780 - h, x + 240, 780], fill=((200, 180, 160), (180, 170, 150), (210, 196, 170))[k % 3])
        for r in range(3):
            for c in range(3):
                d.rectangle([x + 30 + c * 70, 780 - h + 40 + r * 110, x + 70 + c * 70, 780 - h + 110 + r * 110], fill=(90, 100, 120))
    d.rectangle([0, 780, W, H], fill=(150, 140, 130))
    for y in range(800, H, 40):
        d.line([(0, y), (W, y)], fill=(130, 120, 110), width=2)
    # モペッド（自転車にエンジン）
    for cx in (820, 960):
        d.ellipse([cx - 50, 770, cx + 50, 870], outline=(40, 40, 44), width=6)
    d.line([(820, 820), (880, 760), (960, 820)], fill=(60, 60, 66), width=6)
    d.line([(880, 760), (870, 730)], fill=(60, 60, 66), width=6)
    d.rectangle([860, 790, 900, 820], fill=(120, 120, 126))
    # スクーター
    d.ellipse([1040, 820, 1100, 880], fill=(40, 40, 44))
    d.ellipse([1180, 820, 1240, 880], fill=(40, 40, 44))
    d.polygon([(1030, 840), (1060, 780), (1140, 780), (1150, 820), (1210, 820), (1230, 760), (1250, 850), (1030, 850)],
              fill=(170, 60, 60))
    return img


def kenkyujo(done=False):
    """研究所の作業場。台の上の実物大の粘土模型。done=True は完成した模型。"""
    img = _rgb(base((220, 216, 206), (200, 196, 186)))
    wood_floor(img, FLOOR, col=(120, 110, 96), line=(100, 92, 80))
    d = _d(img)
    d.rectangle([700, 760, 1220, 800], fill=(110, 90, 70))                      # 作業台
    if done:
        _cub(d, 760, 760, 1.05)
        d.rectangle([1300, 180, 1600, 380], fill=(244, 240, 228), outline=(160, 150, 130), width=4)  # 図面
        d.line([(1330, 300), (1570, 300)], fill=(90, 110, 160), width=3)
    else:
        clay = (170, 140, 110)
        _cub(d, 760, 760, 1.05, body=clay, shield=clay, seat=(140, 110, 84))
        for k in range(4):                                                      # 削りくず
            d.ellipse([820 + k * 90, 770, 850 + k * 90, 790], fill=(160, 130, 100))
        d.line([(1180, 600), (1230, 520)], fill=(90, 90, 96), width=6)          # へら
    return img


def mockup():
    return kenkyujo(done=True)


def zukai():
    """図解: スーパーカブの工夫。キャラの間（x480〜1440）に収める。"""
    img = vgrad((W, H), (244, 244, 238), (226, 230, 226))
    d = _d(img)
    s = 1.3
    x0, yg = 760, 780
    _cub(d, x0, yg, s)
    r = 62 * s
    cy = yg - r
    items = [
        ("クラッチレバーなし", (x0 + 272 * s, cy - 208 * s), (x0 + 300 * s, 170)),
        ("タンクは座席の下", (x0 + 140 * s, cy - 90 * s), (640, 300)),
        ("樹脂のカバー", (x0 + 290 * s, cy - 90 * s), (1320, 420)),
        ("17インチ", (x0 + 330 * s + r, cy), (1350, 700)),
        ("4ストローク 50cc", (x0 + 210 * s, cy - 16 * s), (660, 820)),
    ]
    for t, (px, py), (tx, ty) in items:
        d.line([(px, py), (tx, ty + 20)], fill=INK, width=3)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=(200, 60, 50))
        _text_c(d, tx, ty, t, 36, INK)
    return img


def zaimoku():
    """町の材木屋の店先。立てかけた材木と、帳場の手紙。"""
    img = _rgb(base((216, 206, 186), (196, 186, 166)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(140, 120, 96))
    for k in range(14):                                                         # 立てかけた材木
        x = 60 + k * 44
        d.polygon([(x, FLOOR), (x + 30, FLOOR), (x + 60, 200), (x + 34, 200)], fill=(214, 180, 130), outline=(170, 136, 90))
    for k in range(10):
        x = 1320 + k * 56
        d.polygon([(x, FLOOR), (x + 36, FLOOR), (x + 10, 220), (x - 20, 220)], fill=(204, 170, 120), outline=(160, 126, 84))
    _table(d, 760, 1160, 640, col=(120, 90, 64))
    d.rectangle([880, 600, 1040, 640], fill=(244, 240, 228), outline=(170, 160, 140), width=2)  # 手紙
    d.rectangle([860, 620, 960, 650], fill=(236, 226, 200), outline=(170, 150, 120))           # 封筒
    return img


def hanbaiten():
    """1958年の販売店（材木屋の店先）。飾られた新しいカブと値札。"""
    img = zaimoku()
    d = _d(img)
    d.rectangle([740, 600, 1180, 820], fill=(140, 120, 96))                     # 机をどけて床
    _cub(d, 760, 860, 1.0)
    d.rectangle([860, 540, 1000, 600], fill=(250, 250, 244), outline=(120, 120, 126), width=3)   # 値札
    _text_c(d, 930, 550, "55,000円", 30, (200, 40, 40))
    return img


def soba():
    """昭和のそば屋の店内。せいろの山と、雑誌の広告（カブの絵）。"""
    img = _rgb(base((226, 214, 190), (206, 194, 170)))
    wood_floor(img, FLOOR, col=(120, 90, 64), line=(100, 76, 54))
    d = _d(img)
    d.rectangle([60, 260, 400, 300], fill=(100, 70, 44))
    for k in range(6):                                                          # せいろ
        d.rectangle([100, 700 - k * 40, 300, 736 - k * 40], fill=(160, 110, 60), outline=(110, 76, 40), width=3)
    _table(d, 760, 1160, 660, col=(120, 90, 64))
    d.rectangle([860, 520, 1060, 660], fill=(244, 240, 228), outline=(150, 140, 120), width=3)  # 雑誌の広告
    _cub(d, 880, 640, 0.42)
    d.line([(880, 540), (1040, 540)], fill=(90, 90, 96), width=4)
    d.rectangle([1500, 200, 1860, 260], fill=(236, 226, 200), outline=(100, 70, 44), width=4)   # 品書き（文字なし）
    return img


def suzuka():
    """1960年の鈴鹿。広い更地に建ちかけの工場と、クレーン。"""
    img = vgrad((W, H), (170, 206, 236), (224, 232, 236))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(180, 160, 120))
    d.polygon([(0, 700), (400, 620), (900, 680), (1400, 610), (W, 690), (W, 700)], fill=(120, 150, 110))
    d.rectangle([700, 420, 1240, 700], fill=(200, 200, 204))                    # 工場の骨組み
    for x in range(700, 1260, 60):
        d.line([(x, 420), (x, 700)], fill=(120, 120, 126), width=6)
    d.polygon([(680, 420), (970, 340), (1260, 420)], fill=(150, 150, 156))
    d.line([(1320, 700), (1320, 260)], fill=(210, 160, 40), width=14)           # クレーン
    d.line([(1320, 270), (1000, 300)], fill=(210, 160, 40), width=10)
    d.line([(1050, 296), (1050, 400)], fill=(60, 60, 66), width=4)
    return img


def la():
    """1960年代のロサンゼルス。やしの木と、看板のカブの絵（文字なし）。"""
    img = vgrad((W, H), (150, 200, 240), (240, 226, 200))
    d = _d(img)
    d.rectangle([0, 800, W, H], fill=(120, 120, 126))
    for x in (120, 360, 1560, 1800):                                            # やしの木
        d.line([(x, 800), (x + 30, 260)], fill=(120, 90, 60), width=18)
        for a in range(0, 360, 45):
            ex, ey = x + 30 + 110 * math.cos(math.radians(a)), 260 + 50 * math.sin(math.radians(a))
            d.line([(x + 30, 260), (ex, ey)], fill=(60, 130, 70), width=14)
    d.rectangle([700, 180, 1220, 480], fill=(250, 246, 236), outline=(90, 90, 96), width=8)    # 看板
    d.line([(820, 480), (820, 800)], fill=(90, 90, 96), width=10)
    d.line([(1100, 480), (1100, 800)], fill=(90, 90, 96), width=10)
    _cub(d, 770, 440, 0.8, body=(200, 60, 60))
    d.ellipse([1040, 230, 1100, 290], fill=(250, 200, 80))                      # 太陽の絵
    _cub(d, 760, 870, 0.9)                                                      # 道を走るカブ
    return img


def kaigou():
    """1973年の集まりの会場の廊下。ふすまと、奥の明るい広間。"""
    img = _rgb(base((220, 206, 180), (196, 182, 156)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    for k in range(6):                                                          # ふすま
        x = 560 + k * 134
        d.rectangle([x, 160, x + 130, 760], fill=(236, 226, 196), outline=(120, 90, 60), width=5)
        d.ellipse([x + 100, 440, x + 116, 470], fill=(120, 90, 60))
    d.rectangle([860, 160, 1060, 760], fill=(255, 236, 190))                     # 開いたふすまの奥の明かり
    for x in (900, 1000):
        d.ellipse([x - 20, 460, x + 20, 520], fill=(200, 170, 120))
    return img


def kotto():
    """六本木の骨董の店。棚の壺と皿、衣桁の着物、三味線。"""
    img = _rgb(base((224, 212, 190), (204, 192, 170)))
    wood_floor(img, FLOOR, col=(110, 84, 60), line=(90, 68, 48))
    d = _d(img)
    for r in range(3):                                                          # 棚
        y = 260 + r * 170
        d.rectangle([680, y, 1240, y + 14], fill=(100, 70, 44))
        for k in range(4):
            x = 720 + k * 130
            col = [(120, 80, 50), (60, 80, 110), (170, 140, 90), (90, 110, 90)][(k + r) % 4]
            d.ellipse([x, y - 90, x + 70, y], fill=col)
    d.line([(1400, 200), (1760, 200)], fill=(110, 70, 44), width=10)            # 衣桁と着物
    d.polygon([(1420, 210), (1740, 210), (1700, 640), (1460, 640)], fill=(70, 80, 110))
    d.line([(1320, 300), (1320, 640)], fill=(60, 40, 30), width=8)              # 三味線
    d.rounded_rectangle([1280, 620, 1360, 700], radius=10, fill=(236, 226, 200), outline=(60, 40, 30), width=5)
    return img


def kuko():
    """羽田空港のロビー（1950〜70年代）。大きな窓の外に旅客機、長椅子。"""
    img = _rgb(base((214, 214, 206), (196, 196, 188)))
    wood_floor(img, FLOOR, col=(150, 146, 136), line=(130, 126, 118))
    d = _d(img)
    d.rectangle([120, 150, 1800, 620], fill=(176, 206, 230))                    # 大きな窓
    for x in range(120, 1801, 280):
        d.line([(x, 150), (x, 620)], fill=(90, 90, 96), width=10)
    d.rectangle([120, 150, 1800, 620], outline=(90, 90, 96), width=12)
    d.ellipse([700, 430, 1260, 500], fill=(236, 238, 240))                       # 旅客機の胴体
    d.polygon([(900, 460), (1060, 460), (1000, 360), (960, 360)], fill=(214, 216, 220))
    d.polygon([(1220, 470), (1300, 380), (1320, 470)], fill=(214, 216, 220))
    d.rectangle([0, 600, W, 630], fill=(150, 150, 140))                          # 滑走路
    for x in (200, 1460):                                                        # 長椅子
        d.rectangle([x, 760, x + 300, 800], fill=(110, 90, 70))
    return img


def butsudan():
    """藤沢の家の座敷。仏壇と位牌。本田が殿堂のメダルを掛ける場面。"""
    img = _rgb(base((214, 202, 180), (196, 184, 160)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([760, 180, 1160, 700], fill=(70, 46, 30))                       # 仏壇
    d.rectangle([800, 220, 1120, 660], fill=(120, 84, 40))
    d.rectangle([930, 300, 990, 520], fill=(30, 24, 20))                         # 位牌
    d.rectangle([920, 290, 1000, 310], fill=(190, 150, 70))
    d.ellipse([850, 560, 900, 610], fill=(196, 160, 80))                         # 花立て・香炉
    d.ellipse([1020, 560, 1070, 610], fill=(196, 160, 80))
    return img


def nenpi():
    """図解: 1リットルで何キロ走るか。キャラの間（x600〜1320）に収める。"""
    img = vgrad((W, H), (244, 244, 238), (226, 230, 226))
    d = _d(img)
    d.rounded_rectangle([620, 200, 700, 330], radius=12, fill=(250, 210, 90), outline=INK, width=4)  # 1リットルの缶
    _text_c(d, 660, 340, "1L", 40, INK)
    rows = [("最初のカブ（1958）", 90, (120, 170, 220)), ("1983年のカブ", 180, (240, 150, 90)),
            ("今の110（測り方が今）", 68, (130, 190, 130))]
    for k, (t, km, col) in enumerate(rows):
        y = 430 + k * 140
        _text_c(d, 960, y - 50, t, 34, INK)
        d.rectangle([640, y, 640 + km * 3.0, y + 50], fill=col)
        _text_c(d, 640 + km * 3.0 + 70, y + 4, f"{km}km", 36, INK)
    return img


def ronsou():
    """誰の言葉か: 二つの吹き出しとはてな。"""
    img = vgrad((W, H), (240, 236, 226), (220, 218, 210))
    d = _d(img)
    for cx, col in ((800, (200, 220, 240)), (1120, (240, 220, 200))):
        d.ellipse([cx - 140, 220, cx + 140, 420], fill=col, outline=INK, width=4)
        d.polygon([(cx - 20, 410), (cx + 20, 410), (cx, 470)], fill=col)
    _text_c(d, 800, 280, "？", 90, INK)
    _text_c(d, 1120, 280, "？", 90, INK)
    _cub(d, 770, 820, 0.9, demae=True)
    return img


def gendai():
    """今の町の働くカブ。郵便の赤いカブ、新聞のカブ、出前のカブ。"""
    img = vgrad((W, H), (170, 206, 236), (220, 232, 240))
    d = _d(img)
    for k in range(7):
        x = k * 300 - 40
        h = 300 + (k % 3) * 70
        d.rectangle([x, 800 - h, x + 280, 800], fill=((226, 222, 214), (210, 214, 222), (232, 220, 204))[k % 3])
    d.rectangle([0, 800, W, H], fill=(140, 140, 146))
    _cub(d, 600, 900, 0.75, body=(200, 40, 40), shield=(200, 40, 40), seat=(40, 40, 44))
    _cub(d, 880, 900, 0.75, body=(80, 90, 110))
    d.rectangle([905, 900 - 46 - 150, 960, 900 - 46 - 95], fill=(236, 236, 228), outline=INK)  # 新聞の束
    _cub(d, 1140, 900, 0.75, demae=True)
    return img


def kumiai():
    """1954年の組合集会。演台と、並んで座る組合員の後ろ姿。"""
    img = _rgb(base((206, 200, 186), (180, 174, 160)))
    wood_floor(img, FLOOR, col=(120, 100, 80), line=(100, 84, 66))
    d = _d(img)
    d.rectangle([0, 80, W, 110], fill=(150, 60, 50))                          # 幕（文字なし）
    d.rectangle([760, 560, 1160, 600], fill=(110, 80, 56))                      # 演台
    d.rectangle([800, 600, 1120, 760], fill=(130, 96, 66))
    rnd = random.Random(9)
    for row in range(3):                                                        # 組合員の後ろ姿
        y = 840 + row * 70
        for k in range(22):
            x = k * 92 - 20 + (row % 2) * 46 + rnd.uniform(-6, 6)
            col = (60 + row * 10, 60 + row * 10, 70 + row * 10)
            d.ellipse([x, y - 60, x + 56, y - 4], fill=col)
            d.rectangle([x - 10, y - 10, x + 66, y + 60], fill=col)
    return img


def koukoku():
    """広告の事務所。製図台と、壁に貼った広告の原画（出前の小僧さんとカブ）。"""
    img = _rgb(base((230, 228, 220), (210, 208, 200)))
    wood_floor(img, FLOOR, col=(140, 120, 100), line=(120, 102, 84))
    d = _d(img)
    d.rectangle([720, 120, 1200, 520], fill=(250, 248, 240), outline=(90, 90, 96), width=8)    # 原画
    _cub(d, 800, 495, 0.85, demae=True)
    d.ellipse([975, 285, 1020, 330], fill=(240, 210, 180))                     # 小僧さんの顔
    d.arc([984, 298, 1011, 320], 20, 160, fill=(80, 60, 50), width=3)          # にっこり
    d.rectangle([977, 330, 1018, 392], fill=(240, 240, 236))
    d.polygon([(760, 780), (1160, 780), (1120, 620), (800, 620)], fill=(200, 190, 170))  # 製図台
    d.line([(820, 780), (800, 900)], fill=(90, 80, 70), width=8)
    d.line([(1100, 780), (1120, 900)], fill=(90, 80, 70), width=8)
    return img


# ---- 場面の途中で差し替える「状況が変わった」背景（2026-10-01 ユーザー「煙の演出いいね。こういうの増やしたい」）
def ie_hikkou():
    """座敷のちゃぶ台に、宛名書きの封筒の山と筆と硯。"""
    img = ie()
    d = _d(img)
    for pile, (px, n) in enumerate(((835, 12), (975, 16))):                     # ちゃぶ台の上に2つの山
        for k in range(n):
            x, y = px + ((k * 5) % 3 - 1) * 5, 700 - k * 14
            d.rectangle([x, y, x + 120, y + 14], fill=(236, 226, 200), outline=(170, 150, 120))
    d.rectangle([1150, 950, 1230, 970], fill=(40, 40, 44))                       # 硯（畳の上）
    d.line([(1240, 960), (1320, 930)], fill=(60, 40, 30), width=6)               # 筆
    return img


def honsha_henji():
    """本社の机に、全国の自転車店からの返事の封筒が山になっている。"""
    img = honsha()
    d = _d(img)
    import random as _r
    rnd = _r.Random(8)
    for _ in range(160):
        x, y = rnd.uniform(560, 1360), rnd.uniform(420, 900)
        if y < 600 and not (700 < x < 1220):
            continue
        d.rectangle([x, y, x + 90, y + 56], fill=rnd.choice([(236, 226, 200), (244, 240, 230), (226, 214, 190)]),
                    outline=(170, 150, 120))
    return img


def kinai_yoru():
    """夜の客室。明かりを落とし、窓の外は真っ暗。"""
    img = kinai()
    d = _d(img)
    for x in (720, 1040):
        d.rounded_rectangle([x, 200, x + 160, 380], radius=60, fill=(24, 30, 60), outline=(120, 116, 110), width=10)
    d.ellipse([760, 230, 790, 260], fill=(240, 240, 210))                        # 窓の月
    from PIL import Image as _I
    veil = _I.new("RGB", img.size, (30, 34, 60))
    return _I.blend(img, veil, 0.45)


def koukoku_mae():
    """広告の事務所。原画の板はまだ白紙。"""
    img = koukoku()
    d = _d(img)
    d.rectangle([728, 128, 1192, 512], fill=(250, 248, 240))
    return img


def koukoku_yama():
    """広告の事務所。白紙の板の前に、丸めたボツ案が山になっている。"""
    img = koukoku_mae()
    d = _d(img)
    import random as _r
    rnd = _r.Random(4)
    for _ in range(70):
        x, y = rnd.uniform(560, 1360), rnd.uniform(760, 960)
        r = rnd.uniform(26, 44)
        d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=(246, 244, 236), outline=(170, 166, 156), width=3)
        d.line([(x - r * 0.5, y), (x + r * 0.3, y - r * 0.3)], fill=(190, 186, 176), width=2)
    for k in range(10):                                                          # 製図台の上にも
        x = 820 + k * 32
        d.ellipse([x, 590 - (k % 3) * 18, x + 50, 630 - (k % 3) * 18], fill=(246, 244, 236), outline=(170, 166, 156), width=3)
    return img


def suzuka_full():
    """鈴鹿製作所が完成。工場の前に、できたてのスーパーカブがずらりと並ぶ。"""
    img = suzuka()
    d = _d(img)
    d.rectangle([700, 420, 1240, 700], fill=(220, 222, 226))                    # 壁を張った工場
    for x in range(720, 1240, 90):
        d.rectangle([x, 480, x + 50, 540], fill=(160, 190, 220))
    for row in range(2):
        for k in range(9):
            _cub(d, 120 + k * 200 + row * 60, 860 + row * 100, 0.55)
    return img


LOCATIONS = {
    "sc_machi": machi, "sc_machi2": machi2, "sc_ie": ie, "sc_kouzai": kouzai, "sc_kiko": kiko,
    "sc_zashiki": zashiki, "sc_honsha": honsha, "sc_honsha2": honsha2, "sc_kinai": kinai,
    "sc_europe": europe, "sc_kenkyujo": kenkyujo, "sc_mockup": mockup, "sc_zukai": zukai,
    "sc_zaimoku": zaimoku, "sc_hanbaiten": hanbaiten, "sc_soba": soba, "sc_suzuka": suzuka,
    "sc_la": la, "sc_kaigou": kaigou, "sc_kotto": kotto, "sc_nenpi": nenpi, "sc_ronsou": ronsou,
    "sc_gendai": gendai, "sc_kumiai": kumiai, "sc_koukoku": koukoku,
    "sc_kuko": kuko, "sc_butsudan": butsudan, "sc_ie_hikkou": ie_hikkou, "sc_honsha_henji": honsha_henji,
    "sc_kinai_yoru": kinai_yoru, "sc_koukoku_mae": koukoku_mae, "sc_koukoku_yama": koukoku_yama,
    "sc_suzuka_full": suzuka_full,
}

CARDS = ["1910", "1934", "1939", "1949", "1956", "1957", "1958", "1960", "1973", "1988"]


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
        if only and f"sc_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"sc_card_{y}.png")
        print(f"生成完了: sc_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
