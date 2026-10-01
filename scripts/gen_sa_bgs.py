#!/usr/bin/env python3
"""三洋電機が消えた日（74_三洋電機が消えた日 / slug=sanyo-end）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と章替わりの年号カードを書き出す。
方針はファミコン回（gen_famicom_bgs.py）と同じ。
- 実在の会社のロゴ・商標は描かない。看板の「SANYO」の文字だけは史実の再現として描く
  （書体はロゴを真似ず、ふつうの極太ゴシック）。Panasonic・ナショナル・eneloop・GOPAN・
  AQUA などの文字は描かない。
- 人物が立つ位置（x=0.2〜0.28 と 0.56〜0.8）の下3分の1（y>720）には物を置かない。
  小物はキャラの間（x=700〜1220）か、上の方に寄せる。
- 場面の途中で差し替える背景（_kasa / _jishin / _ato / _yama / _kara）は、
  元の背景を呼んで要素を足す・変える（同じ構図なので変化が一目で分かる）。

実行: PYTHONPATH=. python scripts/gen_sa_bgs.py [名前...]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, glow, hanging_bulb, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)
INK = (60, 60, 66)
SIGN_BLUE = (28, 66, 150)

_FONTS: dict = {}


def _d(img):
    return ImageDraw.Draw(img)


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


def _font(size, kind="w9"):
    key = (size, kind)
    if key not in _FONTS:
        from ytf.config import Config, resolve_font
        Config.load()
        _FONTS[key] = ImageFont.truetype(resolve_font(kind), size)
    return _FONTS[key]


def _text_c(d, cx, cy, t, size, fill, kind="w9"):
    """cx, cy を中心に文字を置く（字の実際の外形で上下中央を取る）。"""
    f = _font(size, kind)
    bb = d.textbbox((0, 0), t, font=f)
    d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), t, font=f, fill=fill)


def _shade(col, k):
    return tuple(max(0, min(255, int(c * k))) for c in col)


def _window(d, x0, y0, x1, y1, sky=(176, 210, 232), frame=(70, 62, 56), cross=True):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    if cross:
        d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


def _desk(d, x0, x1, y, col=(150, 116, 80), leg=130):
    """机（天板の上端が y）。脚は短めにして下3分の1を空ける。"""
    d.rectangle([x0, y, x1, y + 28], fill=col)
    dark = _shade(col, 0.78)
    d.rectangle([x0 + 16, y + 28, x0 + 34, y + leg], fill=dark)
    d.rectangle([x1 - 34, y + 28, x1 - 16, y + leg], fill=dark)


def _shelf(d, x0, x1, y, col=(110, 86, 62)):
    d.rectangle([x0, y, x1, y + 12], fill=col)


def _papers(d, x0, y0, n=3, col=(244, 240, 228)):
    for k in range(n):
        x, y = x0 + k * 18, y0 - k * 7
        d.rectangle([x, y - 50, x + 100, y + 14], fill=col, outline=(170, 160, 140), width=2)


def _phone(d, x, y, s=1.0, col=(30, 30, 34)):
    d.rounded_rectangle([x, y + 30 * s, x + 130 * s, y + 90 * s], radius=int(14 * s), fill=col)
    d.ellipse([x + 35 * s, y + 38 * s, x + 95 * s, y + 88 * s], fill=(200, 200, 200))
    d.rounded_rectangle([x - 10 * s, y, x + 140 * s, y + 26 * s], radius=int(12 * s), fill=col)


def _monitor(d, x, y, w=150, h=100, screen=(70, 110, 160)):
    """薄型のモニター（左上が x, y）。"""
    d.rectangle([x, y, x + w, y + h], fill=(40, 40, 46))
    d.rectangle([x + 8, y + 8, x + w - 8, y + h - 8], fill=screen)
    d.rectangle([x + w / 2 - 10, y + h, x + w / 2 + 10, y + h + 22], fill=(60, 60, 66))
    d.rectangle([x + w / 2 - 40, y + h + 22, x + w / 2 + 40, y + h + 30], fill=(60, 60, 66))


def _battery(d, x, y, horiz=True, body=(236, 238, 240), band=(120, 170, 210), L=56, R=18):
    """単3形くらいの円筒形電池（ロゴ・文字なし）。"""
    if horiz:
        d.rounded_rectangle([x, y, x + L, y + R], radius=6, fill=body, outline=(130, 130, 136), width=2)
        d.rectangle([x + L * 0.62, y + 2, x + L - 4, y + R - 2], fill=band)
        d.rectangle([x + L, y + R * 0.3, x + L + 5, y + R * 0.7], fill=(170, 170, 176))
    else:
        d.rounded_rectangle([x, y, x + R, y + L], radius=6, fill=body, outline=(130, 130, 136), width=2)
        d.rectangle([x + 2, y + L * 0.38, x + R - 2, y + L - 4], fill=band)
        d.rectangle([x + R * 0.3, y - 5, x + R * 0.7, y], fill=(170, 170, 176))


def _washer_round(d, cx, top, s=1.0, col=(238, 238, 232)):
    """丸い桶の洗濯機（攪拌式の試作機・昔の輸入品のイメージ）。top は桶の上端。"""
    w, h = 200 * s, 190 * s
    d.ellipse([cx - w / 2, top - 22 * s, cx + w / 2, top + 22 * s], fill=_shade(col, 0.82), outline=(140, 140, 136), width=3)
    d.rectangle([cx - w / 2, top, cx + w / 2, top + h], fill=col)
    d.line([(cx - w / 2, top), (cx - w / 2, top + h)], fill=(140, 140, 136), width=3)
    d.line([(cx + w / 2, top), (cx + w / 2, top + h)], fill=(140, 140, 136), width=3)
    d.ellipse([cx - w / 2, top + h - 22 * s, cx + w / 2, top + h + 22 * s], fill=col, outline=(140, 140, 136), width=3)
    d.rectangle([cx - 6 * s, top - 60 * s, cx + 6 * s, top], fill=(150, 150, 156))       # かき回す軸
    for k in (-1, 1):                                                                    # 脚
        d.line([(cx + k * 70 * s, top + h + 10 * s), (cx + k * 90 * s, top + h + 60 * s)], fill=(90, 90, 96), width=int(8 * s))


def _washer_square(d, x, y, s=1.0, col=(232, 236, 230), lid=True):
    """角型の洗濯機（噴流式のイメージ。左上が x, y）。"""
    w, h = 190 * s, 210 * s
    d.rectangle([x, y, x + w, y + h], fill=col, outline=(130, 136, 132), width=4)
    d.rectangle([x, y, x + w, y + 30 * s], fill=_shade(col, 0.9), outline=(130, 136, 132), width=3)
    d.ellipse([x + w * 0.66, y + h * 0.3, x + w * 0.86, y + h * 0.42], fill=(90, 96, 104))       # つまみ
    d.rectangle([x + w * 0.12, y + h * 0.32, x + w * 0.56, y + h * 0.40], fill=(200, 206, 200))  # 銘板（文字なし）
    for k in (0, 1):                                                                              # 脚
        lx = x + 12 * s + k * (w - 36 * s)
        d.rectangle([lx, y + h, lx + 24 * s, y + h + 20 * s], fill=(90, 90, 96))
    if lid:
        d.rectangle([x + 8 * s, y - 10 * s, x + w - 8 * s, y + 2 * s], fill=_shade(col, 0.85), outline=(130, 136, 132), width=2)


def _bike_lamp(d, cx, cy, r=26):
    """自転車の発電ランプ（丸いランプと、タイヤに当てる発電機）。"""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(196, 200, 206), outline=(110, 114, 120), width=3)
    d.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62], fill=(250, 236, 170))
    d.rounded_rectangle([cx + r * 0.8, cy - r * 0.35, cx + r * 2.4, cy + r * 0.35], radius=6, fill=(150, 154, 160))


def _bicycle(d, x, y, s=1.0, col=(40, 40, 46)):
    """横から見た自転車（後輪の中心が x, y）。"""
    r = 70 * s
    for cx in (x, x + 200 * s):
        d.ellipse([cx - r, y - r, cx + r, y + r], outline=col, width=int(6 * s))
        d.ellipse([cx - 8 * s, y - 8 * s, cx + 8 * s, y + 8 * s], fill=col)
    fx, fy = x + 200 * s, y
    seat, pedal = (x + 70 * s, y - 100 * s), (x + 90 * s, y)
    d.line([(x, y), pedal, (fx - 20 * s, y - 110 * s), seat, (x, y)], fill=col, width=int(6 * s))
    d.line([(fx - 20 * s, y - 110 * s), (fx, fy)], fill=col, width=int(6 * s))
    d.line([seat, (seat[0] - 10 * s, seat[1] - 20 * s)], fill=col, width=int(6 * s))
    d.rectangle([seat[0] - 34 * s, seat[1] - 28 * s, seat[0] + 14 * s, seat[1] - 18 * s], fill=col)
    d.line([(fx - 20 * s, y - 110 * s), (fx - 30 * s, y - 140 * s), (fx + 10 * s, y - 145 * s)], fill=col, width=int(6 * s))
    _bike_lamp(d, fx + 18 * s, y - 112 * s, r=14 * s)


def _umbrella(d, cx, cy, r, col=(244, 240, 228)):
    """開いた傘（cx, cy が骨の中心）。"""
    d.pieslice([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], 180, 360, fill=col, outline=(150, 140, 120), width=3)
    for k in range(5):
        a = math.pi + math.pi * (k + 0.5) / 5
        d.line([(cx, cy), (cx + r * math.cos(a), cy + r * 0.7 * math.sin(a))], fill=(190, 180, 160), width=2)
    d.line([(cx, cy - r * 0.7), (cx, cy + r * 0.9)], fill=(90, 70, 50), width=4)
    d.arc([cx, cy + r * 0.8, cx + r * 0.3, cy + r * 1.05], 0, 180, fill=(90, 70, 50), width=4)


def _boxes(d, x, y, n=4, rows=3, col=(186, 150, 104)):
    for r in range(rows):
        for k in range(n - r):
            bx, by = x + k * 110 + r * 55, y - (r + 1) * 80
            d.rectangle([bx, by, bx + 104, by + 76], fill=col, outline=(120, 90, 60), width=3)


# ---------------------------------------------------------------- 守口の本社ビル
def _honsha(sky_top, sky_bot, sign="full", crane=False, ground=(150, 150, 152)):
    """1999年に建て替えた守口の本社ビル。sign: full=SANYO / kara=外したあと / none=看板なし。"""
    img = vgrad((W, H), sky_top, sky_bot)
    d = _d(img)
    d.rectangle([0, 880, W, H], fill=ground)                                      # 歩道
    d.rectangle([0, 868, W, 884], fill=_shade(ground, 0.8))
    bx0, bx1, by0 = 500, 1420, 110
    d.rectangle([bx0, by0, bx1, 880], fill=(216, 218, 222), outline=(150, 154, 160), width=4)
    for r in range(8):                                                              # 窓
        y = 380 + r * 58
        for c in range(11):
            x = bx0 + 34 + c * 80
            d.rectangle([x, y, x + 56, y + 38], fill=(126, 156, 186))
    d.rectangle([860, 800, 1060, 880], fill=(96, 116, 136))                        # 入口
    d.line([(960, 800), (960, 880)], fill=(70, 86, 100), width=4)
    if sign != "none":
        sx0, sy0, sx1, sy1 = 650, 140, 1270, 340                                     # 縦3m×横9.3m の比
        d.rectangle([sx0 - 10, sy0 - 10, sx1 + 10, sy1 + 10], fill=(190, 192, 198))
        d.rectangle([sx0, sy0, sx1, sy1], fill=(244, 245, 248))
        if sign == "full":
            _text_c(d, (sx0 + sx1) / 2, (sy0 + sy1) / 2, "SANYO", 170, SIGN_BLUE)
        else:                                                                       # 文字を外した跡だけ残る
            _text_c(d, (sx0 + sx1) / 2, (sy0 + sy1) / 2, "SANYO", 170, (228, 230, 234))
            for k in range(5):
                bx = sx0 + 80 + k * 115
                for yy in (sy0 + 40, sy1 - 40):
                    d.ellipse([bx - 5, yy - 5, bx + 5, yy + 5], fill=(170, 172, 178))
    if crane:                                                                       # 画面の左上から入るクレーンの腕
        d.line([(-40, 380), (600, 60)], fill=(230, 170, 40), width=26)
        for k in range(12):
            t = k / 12
            x = -40 + 640 * t
            y = 380 - 320 * t
            d.line([(x, y - 12), (x + 50, y - 34)], fill=(170, 120, 20), width=4)
        d.line([(600, 60), (612, 96)], fill=(60, 60, 60), width=4)
        d.line([(612, 96), (612, 240)], fill=(60, 60, 60), width=4)                 # ワイヤー（看板の左わき）
        d.rectangle([598, 240, 626, 272], fill=(230, 170, 40), outline=(90, 70, 20), width=3)
        d.arc([596, 264, 628, 300], 0, 180, fill=(70, 70, 70), width=6)              # フック
    # 植え込み（細い帯だけ）
    d.rectangle([0, 846, bx0 - 20, 868], fill=(96, 140, 96))
    d.rectangle([bx1 + 20, 846, W, 868], fill=(96, 140, 96))
    return img


def kanban():
    """2011年12月23日の朝。冬の空、SANYO の看板とクレーン。"""
    return _honsha((196, 214, 230), (226, 232, 238), sign="full", crane=True)


def kanban_kara():
    """夕方4時半。文字の外れた看板、空のフック、冬の夕焼け。"""
    return _honsha((92, 96, 140), (238, 170, 120), sign="kara", crane=True, ground=(126, 120, 124))


def honsha():
    """1999年8月。新しい本社ビルと SANYO の看板、夏の空。"""
    img = _honsha((110, 170, 226), (196, 224, 244), sign="full", crane=False)
    d = _d(img)
    for cx, cy in ((180, 300), (1740, 260)):                                       # 入道雲
        for k, (dx, dy, r) in enumerate(((0, 0, 90), (-90, 40, 70), (90, 40, 74), (0, 70, 80))):
            d.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], fill=(250, 250, 252))
    return img


def gendai():
    """今。旧本社ビルは市役所に。看板は無く、木が育っている。"""
    img = _honsha((140, 190, 232), (210, 228, 242), sign="none", crane=False)
    d = _d(img)
    for cx in (110, 1810):                                                          # 木（画面の端に）
        d.rectangle([cx - 14, 520, cx + 14, 846], fill=(110, 84, 60))
        for dx, dy, r in ((0, 440, 120), (-80, 500, 90), (80, 500, 90)):
            d.ellipse([cx + dx - r, dy - r, cx + dx + r, dy + r], fill=(86, 140, 90))
    return img


# ---------------------------------------------------------------- 今の部屋
def _heya(charging=False):
    img = _rgb(base((238, 234, 224), (224, 220, 210)))
    wood_floor(img, FLOOR, col=(182, 148, 110), line=(156, 124, 92))
    d = _d(img)
    _window(d, 110, 130, 470, 500, sky=(190, 214, 234), frame=(214, 210, 200))
    d.rectangle([90, 120, 160, 560], fill=(150, 176, 160))                         # カーテン
    d.rectangle([420, 120, 490, 560], fill=(150, 176, 160))
    d.rectangle([730, 250, 1190, 500], fill=(30, 30, 36))                          # テレビ
    d.rectangle([746, 266, 1174, 484], fill=(54, 60, 72))
    d.rectangle([700, 520, 1220, 700], fill=(170, 130, 92), outline=(120, 90, 62), width=4)   # テレビ台
    d.line([(960, 520), (960, 700)], fill=(120, 90, 62), width=3)
    d.rounded_rectangle([1080, 494, 1170, 516], radius=8, fill=(50, 50, 56))      # リモコン
    for k in range(4):
        d.ellipse([1092 + k * 18, 500, 1102 + k * 18, 510], fill=(140, 140, 150))
    # 冷蔵庫（右）
    d.rounded_rectangle([1250, 300, 1420, FLOOR], radius=14, fill=(238, 240, 242), outline=(170, 174, 180), width=4)
    d.line([(1250, 520), (1420, 520)], fill=(170, 174, 180), width=4)
    d.rectangle([1262, 400, 1272, 480], fill=(180, 184, 190))
    d.rectangle([1262, 560, 1272, 680], fill=(180, 184, 190))
    if not charging:
        # 引き出しを引き出して、中に使いかけの電池
        d.rectangle([740, 590, 960, 690], fill=(150, 112, 78), outline=(110, 80, 52), width=4)
        d.rectangle([752, 600, 948, 680], fill=(120, 88, 60))
        for r in range(3):
            for k in range(3):
                _battery(d, 762 + k * 62, 610 + r * 22, horiz=True, L=50, R=16)
        # 冷蔵庫の上に、実は充電器がある
        d.rounded_rectangle([1290, 270, 1380, 300], radius=6, fill=(244, 244, 244), outline=(120, 120, 130), width=3)
        for k in range(4):
            d.rectangle([1300 + k * 20, 276, 1312 + k * 20, 292], fill=(90, 90, 100))
        d.line([(1380, 290), (1420, 330)], fill=(60, 60, 66), width=3)
    else:
        # 充電器をテレビ台の上へ。電池を挿して、ランプが緑
        d.rounded_rectangle([860, 470, 1020, 520], radius=8, fill=(244, 244, 244), outline=(120, 120, 130), width=3)
        for k in range(4):
            _battery(d, 878 + k * 34, 432, horiz=False, L=46, R=18)
            d.ellipse([882 + k * 34, 504, 894 + k * 34, 514], fill=(70, 200, 100))
        d.line([(1020, 510), (1060, 560), (1060, 700)], fill=(60, 60, 66), width=3)
    return img


def heya():
    return _heya(charging=False)


def heya_jyuden():
    return _heya(charging=True)


# ---------------------------------------------------------------- 1917 淡路島
def awaji():
    img = vgrad((W, H), (150, 196, 228), (216, 232, 240))
    d = _d(img)
    d.polygon([(0, 470), (260, 380), (520, 440), (820, 360), (1100, 430), (1400, 350),
               (1700, 420), (W, 380), (W, 520), (0, 520)], fill=(118, 150, 128))          # 向こうの山
    d.rectangle([0, 510, W, 700], fill=(70, 126, 170))                                     # 海
    for k in range(6):
        y = 530 + k * 28
        for x in range(40 + (k % 2) * 60, W, 220):
            d.arc([x, y, x + 80, y + 20], 200, 340, fill=(120, 170, 204), width=3)
    for x, s in ((760, 1.0), (1080, 0.8)):                                                 # 漁船
        d.polygon([(x, 600), (x + 220 * s, 600), (x + 190 * s, 640), (x + 30 * s, 640)], fill=(120, 86, 60))
        d.line([(x + 110 * s, 600), (x + 110 * s, 470)], fill=(90, 70, 50), width=6)
        d.polygon([(x + 116 * s, 480), (x + 190 * s, 580), (x + 116 * s, 580)], fill=(236, 230, 214))
    for k, x in enumerate((40, 170, 300)):                                                 # 浜辺の家（左上・小さく）
        y = 430 - k * 6
        d.rectangle([x, y, x + 110, y + 60], fill=(200, 186, 160))
        d.polygon([(x - 14, y), (x + 55, y - 40), (x + 124, y)], fill=(80, 84, 96))
    d.polygon([(0, 700), (W, 680), (W, H), (0, H)], fill=(216, 198, 158))                 # 砂浜
    d.line([(0, 700), (W, 680)], fill=(236, 230, 214), width=6)
    for x in range(820, 1110, 36):                                                         # 網干し（キャラの間）
        d.line([(x, 560), (x, 690)], fill=(110, 86, 60), width=4)
    d.line([(820, 570), (1110, 570)], fill=(110, 86, 60), width=3)
    for k in range(7):
        d.line([(820 + k * 42, 572), (840 + k * 42, 660)], fill=(150, 140, 110), width=2)
    return img


# ---------------------------------------------------------------- 1918 大阪の借家
def shakuya():
    img = base((212, 194, 162), (194, 176, 146))
    tatami_floor(img, FLOOR)
    d = ImageDraw.Draw(img)
    for k, x in enumerate((140, 1560)):                                                   # 柱
        d.rectangle([x, 0, x + 60, FLOOR], fill=(110, 82, 56))
    d.rectangle([0, 70, W, 100], fill=(110, 82, 56))                                      # 鴨居
    sx0, sy0, sx1, sy1 = 760, 150, 1160, 470                                               # 障子
    d.rectangle([sx0, sy0, sx1, sy1], fill=(238, 230, 206))
    for x in range(sx0, sx1 + 1, 100):
        d.line([(x, sy0), (x, sy1)], fill=(120, 92, 66), width=6)
    for y in range(sy0, sy1 + 1, 80):
        d.line([(sx0, y), (sx1, y)], fill=(120, 92, 66), width=6)
    _shelf(d, 300, 640, 300)                                                               # 部品の棚
    _shelf(d, 300, 640, 430)
    for r, y in enumerate((300, 430)):
        for k in range(5):
            x = 316 + k * 64
            d.rectangle([x, y - 54, x + 50, y], fill=(170, 140, 100), outline=(110, 86, 60), width=2)
            d.ellipse([x + 15, y - 40, x + 35, y - 20], fill=(244, 242, 236))
    d.rectangle([780, 600, 1140, 640], fill=(140, 104, 72))                               # 低い作業台
    d.rectangle([800, 640, 820, 700], fill=(110, 82, 56))
    d.rectangle([1100, 640, 1120, 700], fill=(110, 82, 56))
    for k in range(6):                                                                     # 白い器具の部品
        cx = 820 + k * 52
        d.ellipse([cx - 16, 566, cx + 16, 598], fill=(246, 244, 238), outline=(150, 146, 140), width=2)
    d.ellipse([1040, 560, 1100, 598], outline=(170, 100, 50), width=6)                    # 電線の束
    hanging_bulb(img, 960, ly=70)
    return _rgb(img)


# ---------------------------------------------------------------- 1930〜40年代の松下の事務所
def _matsushita(mode="day"):
    if mode == "day":
        img = _rgb(base((224, 214, 192), (206, 196, 174)))
        sky, floor, fl = (196, 214, 228), (126, 98, 72), (104, 82, 60)
    elif mode == "sengo":
        img = _rgb(base((176, 168, 150), (156, 148, 132)))
        sky, floor, fl = (170, 176, 180), (100, 82, 66), (84, 70, 56)
    else:
        img = _rgb(base((54, 52, 62), (40, 40, 48)))
        sky, floor, fl = (24, 28, 52), (60, 52, 46), (48, 42, 38)
    wood_floor(img, FLOOR, col=floor, line=fl)
    d = _d(img)
    d.rectangle([0, 640, W, 660], fill=_shade(floor, 0.9))
    _window(d, 760, 120, 1160, 420, sky=sky, frame=(80, 64, 50))
    if mode == "sengo":                                                                    # 割れた窓に板
        d.line([(980, 140), (1140, 400)], fill=(90, 90, 96), width=3)
        d.rectangle([1000, 250, 1150, 290], fill=(150, 116, 80))
    d.ellipse([360, 140, 460, 240], fill=(240, 236, 224), outline=(80, 64, 50), width=6)  # 柱時計
    d.line([(410, 190), (410, 156)], fill=INK, width=4)
    d.line([(410, 190), (436, 200)], fill=INK, width=5)
    d.rectangle([396, 240, 424, 330], fill=(110, 82, 56))
    _shelf(d, 1300, 1640, 260)                                                             # ラジオと乾電池の棚
    _shelf(d, 1300, 1640, 400)
    for k in range(3):
        x = 1320 + k * 106
        d.rectangle([x, 186, x + 90, 260], fill=(120, 84, 56), outline=(80, 56, 36), width=3)
        d.ellipse([x + 12, 200, x + 50, 238], fill=(70, 60, 50))
        d.ellipse([x + 62, 212, x + 78, 228], fill=(200, 180, 120))
    for k in range(9):
        _battery(d, 1316 + k * 36, 344, horiz=False, L=50, R=22, body=(80, 80, 88), band=(190, 60, 50))
    _desk(d, 700, 1220, 620, col=(126, 94, 66))
    _papers(d, 760, 610, n=3)
    _phone(d, 1060, 556, 0.6)
    if mode == "sengo":                                                                    # 壁に貼られた通達の紙（文字なし）
        for k, (x, y) in enumerate(((520, 300), (600, 330), (540, 420))):
            d.rectangle([x, y, x + 90, y + 120], fill=(236, 230, 214), outline=(150, 140, 120), width=2)
            for j in range(5):
                d.line([(x + 12, y + 20 + j * 18), (x + 78, y + 20 + j * 18)], fill=(170, 160, 140), width=3)
    if mode == "yoru":
        d.polygon([(860, 520), (940, 520), (920, 470), (880, 470)], fill=(60, 90, 70))   # 電気スタンド
        d.line([(900, 520), (900, 610)], fill=(50, 50, 54), width=6)
        d.ellipse([872, 518, 928, 540], fill=(255, 226, 150))
    return img


def matsushita():
    return _matsushita("day")


def matsushita_sengo():
    return _matsushita("sengo")


def matsushita_yoru():
    img = _matsushita("yoru").convert("RGBA")
    glow(img, 900, 560, 260, (255, 210, 140), 70)
    return _rgb(img)


# ---------------------------------------------------------------- 1946〜47 仮の作業場
def _sagyoba(kasa=False):
    img = _rgb(base((150, 120, 90), (128, 102, 76)))
    wood_floor(img, FLOOR, col=(110, 88, 66), line=(92, 72, 54))
    d = _d(img)
    for x in range(0, W, 120):                                                              # 板壁
        d.line([(x, 0), (x, FLOOR)], fill=(118, 94, 70), width=5)
    _window(d, 1400, 130, 1660, 330, sky=(196, 206, 212), frame=(90, 70, 50))
    if not kasa:                                                                            # 壁に吊るした落下傘
        cx0, cy0, r = 960, 280, 210
        d.pieslice([cx0 - r, cy0 - r * 0.75, cx0 + r, cy0 + r * 0.75], 180, 360, fill=(246, 244, 238), outline=(190, 186, 176), width=4)
        for k in range(7):
            a = math.pi + math.pi * k / 6
            ex, ey = cx0 + r * math.cos(a), cy0 + r * 0.75 * math.sin(a)
            d.line([(cx0, cy0 - r * 0.75), (ex, ey)], fill=(214, 210, 200), width=3)    # 縫い目
            d.line([(ex, max(ey, cy0)), (cx0, cy0 + 220)], fill=(150, 140, 110), width=2)  # つり索
        d.line([(cx0 - r, cy0), (cx0 + r, cy0)], fill=(190, 186, 176), width=4)
        d.line([(cx0, 0), (cx0, cy0 - r * 0.75)], fill=(80, 66, 50), width=4)
    # 落下傘の絹の山（キャラの間）
    pile = 0.55 if kasa else 1.0
    cx, by = 960, 760
    for k, (dx, r, col) in enumerate(((-120, 150, (238, 236, 228)), (110, 140, (230, 228, 220)), (0, 190, (246, 244, 238)))):
        rr = r * pile
        d.pieslice([cx + dx - rr * 1.3, by - rr, cx + dx + rr * 1.3, by + rr * 0.4], 180, 360, fill=col, outline=(190, 186, 176), width=3)
    for k in range(7):                                                                      # ひも
        x = cx - 200 * pile + k * 66 * pile
        d.line([(x, by - 40 * pile), (x + 30, by + 4)], fill=(150, 140, 110), width=2)
    d.rectangle([1180, 560, 1250, 600], fill=(60, 60, 64))                                 # 古いミシン（小さく）
    if kasa:
        d.line([(200, 170), (1340, 170)], fill=(80, 66, 50), width=4)                       # 傘を吊るす縄
        for k in range(7):
            cx = 280 + k * 160
            _umbrella(d, cx, 300, 88, col=(246, 242, 232) if k % 2 == 0 else (232, 226, 212))
            d.line([(cx, 170), (cx, 238)], fill=(80, 66, 50), width=3)
        for k in range(5):                                                                  # 開いて干した傘（2段目）
            cx = 360 + k * 200
            _umbrella(d, cx, 470, 80, col=(240, 236, 224))
        _shelf(d, 1300, 1700, 520)                                                          # 電気スタンドの棚
        for k in range(4):
            x = 1330 + k * 92
            d.polygon([(x, 470), (x + 60, 470), (x + 48, 430), (x + 12, 430)], fill=(90, 120, 100))
            d.line([(x + 30, 470), (x + 30, 512)], fill=(60, 60, 64), width=5)
            d.rectangle([x + 10, 508, x + 50, 520], fill=(60, 60, 64))
    return img


def sagyoba():
    return _sagyoba(kasa=False)


def sagyoba_kasa():
    return _sagyoba(kasa=True)


# ---------------------------------------------------------------- 1947 北条工場
def hojo():
    img = _rgb(base((206, 190, 160), (186, 170, 142)))
    wood_floor(img, FLOOR, col=(132, 110, 86), line=(112, 92, 72))
    d = _d(img)
    for x in range(0, W, 160):
        d.line([(x, 0), (x, 300)], fill=(150, 124, 94), width=6)                         # 梁
    d.rectangle([0, 0, W, 60], fill=(120, 96, 70))
    for k, x0 in enumerate((180, 760, 1340)):                                             # 窓の外は田んぼ
        x1 = x0 + 400
        d.rectangle([x0, 120, x1, 380], fill=(196, 220, 236))
        d.rectangle([x0, 290, x1, 380], fill=(120, 170, 100))
        for j in range(4):
            d.line([(x0, 300 + j * 22), (x1, 300 + j * 22)], fill=(100, 150, 84), width=3)
        d.rectangle([x0, 120, x1, 380], outline=(100, 78, 56), width=10)
        d.line([((x0 + x1) // 2, 120), ((x0 + x1) // 2, 380)], fill=(100, 78, 56), width=8)
    _desk(d, 700, 1220, 600, col=(140, 108, 76))                                          # ランプを並べた台
    for r in range(2):
        for k in range(8):
            _bike_lamp(d, 736 + k * 56, 572 - r * 64, r=22)
    wx, wy = 1250, 470                                                                     # 窓の間の壁に掛けた車輪
    d.ellipse([wx - 72, wy - 72, wx + 72, wy + 72], outline=(40, 40, 46), width=8)
    d.ellipse([wx - 7, wy - 7, wx + 7, wy + 7], fill=(40, 40, 46))
    for k in range(8):
        a = k * math.pi / 4
        d.line([(wx, wy), (wx + 66 * math.cos(a), wy + 66 * math.sin(a))], fill=(90, 90, 96), width=2)
    return img


def hojo_2005():
    """2005年の北條工場（外観）。のこぎり屋根の古い工場、秋の曇り空。"""
    img = vgrad((W, H), (178, 186, 196), (214, 216, 218))
    d = _d(img)
    d.rectangle([0, 860, W, H], fill=(150, 146, 140))
    d.rectangle([380, 380, 1540, 860], fill=(196, 190, 178), outline=(140, 134, 124), width=4)
    for k in range(8):                                                                      # のこぎり屋根
        x = 380 + k * 145
        d.polygon([(x, 380), (x + 145, 380), (x + 145, 290)], fill=(120, 116, 112))
        d.rectangle([x + 128, 296, x + 140, 380], fill=(176, 196, 210))
    for k in range(9):                                                                      # 窓
        x = 430 + k * 122
        d.rectangle([x, 470, x + 80, 560], fill=(130, 150, 166), outline=(110, 104, 96), width=3)
    d.rectangle([820, 660, 1100, 860], fill=(110, 104, 98))                                # シャッター
    for y in range(670, 860, 16):
        d.line([(820, y), (1100, y)], fill=(130, 124, 118), width=3)
    for cx in (220, 1700):                                                                  # 秋の木
        d.rectangle([cx - 12, 560, cx + 12, 860], fill=(100, 76, 56))
        d.ellipse([cx - 110, 420, cx + 110, 600], fill=(196, 130, 70))
    return img


def hojo_ato():
    """跡地は商業施設に。広い駐車場と、発祥の地の碑。"""
    img = vgrad((W, H), (150, 196, 232), (212, 228, 240))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(96, 98, 104))                                        # 駐車場
    d.line([(0, 800), (W, 800)], fill=(200, 200, 204), width=4)
    for x in range(-100, W + 200, 260):
        d.line([(x, 800), (x - 40, 900)], fill=(176, 176, 180), width=3)
    d.rectangle([200, 330, 1720, 760], fill=(232, 228, 220), outline=(170, 166, 158), width=4)  # 商業施設
    d.rectangle([200, 330, 1720, 400], fill=(170, 60, 110))                                # 色の帯（文字なし）
    d.rectangle([780, 520, 1140, 760], fill=(120, 160, 190), outline=(90, 110, 130), width=4)   # ガラスの入口
    d.line([(960, 520), (960, 760)], fill=(90, 110, 130), width=4)
    for k in range(6):
        x = 260 + k * 90
        d.rectangle([x, 470, x + 60, 640], fill=(150, 176, 196))
        d.rectangle([1340 + k * 60, 470, 1384 + k * 60, 640], fill=(150, 176, 196))
    # 碑（キャラの間に、小さめに）
    d.rectangle([900, 560, 1020, 800], fill=(150, 150, 146), outline=(110, 110, 106), width=4)
    d.rectangle([880, 800, 1040, 836], fill=(130, 130, 126))
    f = _font(26)
    for k, ch in enumerate("三洋電機発祥の地"):
        bb = d.textbbox((0, 0), ch, font=f)
        d.text((960 - (bb[0] + bb[2]) / 2, 580 + k * 27 - bb[1]), ch, font=f, fill=(60, 60, 58))
    return img


# ---------------------------------------------------------------- 1950年代の洗濯機
def shonin():
    """知人の商人の家。洋風の部屋に、丸い桶の洗濯機。"""
    img = _rgb(base((226, 214, 196), (210, 198, 180)))
    wood_floor(img, FLOOR, col=(140, 104, 76), line=(118, 88, 64))
    d = _d(img)
    for x in range(0, W, 60):                                                               # 壁紙の縦じま
        d.line([(x, 0), (x, 620)], fill=(216, 204, 186), width=3)
    d.rectangle([0, 620, W, 650], fill=(150, 116, 86))
    _window(d, 1240, 140, 1600, 460, sky=(200, 220, 234), frame=(120, 92, 66))
    d.rectangle([820, 690, 1100, 720], fill=(120, 90, 62))                                # 洗い場の台
    d.rectangle([836, 720, 856, 760], fill=(100, 74, 50))
    d.rectangle([1064, 720, 1084, 760], fill=(100, 74, 50))
    _washer_round(d, 940, 440, 0.95)
    d.rectangle([1050, 630, 1090, 690], fill=(196, 170, 120), outline=(150, 120, 80), width=3)   # 洗濯かご（台の上）
    d.rectangle([1044, 620, 1096, 640], fill=(246, 246, 240))
    d.rectangle([380, 220, 560, 380], fill=(196, 176, 140), outline=(120, 92, 66), width=8)  # 額（絵だけ）
    d.polygon([(400, 360), (460, 270), (520, 360)], fill=(120, 150, 120))
    return img


def kaihatsu():
    """1953年の開発室。台の上に丸い試作機、壁に角型の図面。"""
    img = _rgb(base((222, 222, 214), (204, 204, 196)))
    wood_floor(img, FLOOR, col=(120, 112, 100), line=(100, 94, 84))
    d = _d(img)
    _window(d, 300, 130, 640, 400, sky=(196, 214, 228))
    d.rectangle([1240, 150, 1600, 420], fill=(236, 240, 244), outline=(110, 110, 116), width=6)   # 製図の紙
    d.rectangle([1320, 200, 1470, 370], outline=(70, 90, 140), width=4)                   # 角型の箱の図
    d.line([(1320, 200), (1360, 170), (1510, 170), (1470, 200)], fill=(70, 90, 140), width=4)
    d.line([(1510, 170), (1510, 340), (1470, 370)], fill=(70, 90, 140), width=4)
    d.ellipse([1360, 260, 1410, 310], outline=(200, 80, 60), width=4)
    _desk(d, 700, 1220, 640, col=(126, 118, 104))
    _washer_round(d, 960, 470, 0.72)
    for k in range(3):                                                                      # 工具
        d.rectangle([760 + k * 40, 620, 774 + k * 40, 640], fill=(90, 90, 96))
    d.ellipse([1110, 600, 1170, 640], fill=(150, 150, 156))
    return img


def niwa():
    """井植家の庭。縁側に角型の試作機、物干しに洗ったラグビーシャツ。"""
    img = vgrad((W, H), (160, 204, 232), (220, 234, 240))
    d = _d(img)
    d.rectangle([0, 520, W, 700], fill=(150, 120, 90))                                     # 板塀
    for x in range(0, W, 70):
        d.line([(x, 520), (x, 700)], fill=(126, 100, 74), width=4)
    d.rectangle([0, 700, W, H], fill=(140, 170, 110))                                      # 庭の地面
    d.rectangle([0, 420, 420, 700], fill=(200, 184, 150))                                  # 家と縁側（左奥）
    d.polygon([(-20, 420), (210, 330), (440, 420)], fill=(80, 84, 96))
    d.rectangle([0, 660, 440, 700], fill=(140, 104, 72))
    d.line([(980, 250), (1700, 250)], fill=(90, 80, 70), width=4)                         # 物干し
    for x in (980, 1700):
        d.rectangle([x - 8, 240, x + 8, 700], fill=(110, 90, 70))
    sx = 1180                                                                               # 横じまのラグビーシャツ
    d.polygon([(sx, 260), (sx + 220, 260), (sx + 270, 320), (sx + 230, 350), (sx + 210, 330),
               (sx + 210, 480), (sx + 10, 480), (sx + 10, 330), (sx - 10, 350), (sx - 50, 320)], fill=(30, 50, 110))
    for k in range(4):
        y = 300 + k * 44
        d.rectangle([sx + 10, y, sx + 210, y + 18], fill=(236, 236, 230))
    d.rectangle([sx + 80, 260, sx + 140, 278], fill=(236, 236, 230))                       # えり
    _washer_square(d, 840, 470, 0.9)                                                        # 角型の試作機（キャラの間）
    d.ellipse([760, 640, 860, 680], fill=(170, 176, 180), outline=(120, 126, 130), width=3)  # たらい
    return img


def jitenshaya():
    """1950年代の自転車店の店先。店の奥に自転車、表に角型の洗濯機で実演。"""
    img = vgrad((W, H), (190, 210, 226), (226, 230, 232))
    d = _d(img)
    d.rectangle([0, 860, W, H], fill=(160, 154, 146))                                      # 道
    d.rectangle([300, 160, 1700, 860], fill=(200, 184, 156))                              # 店
    d.polygon([(260, 160), (1000, 70), (1740, 160)], fill=(84, 72, 66))
    d.rectangle([520, 200, 1480, 270], fill=(96, 74, 54))                                 # 看板（文字なし）
    for k in range(10):                                                                     # 日よけ
        col = (196, 80, 70) if k % 2 == 0 else (240, 236, 226)
        d.polygon([(400 + k * 120, 290), (520 + k * 120, 290), (500 + k * 120, 360), (380 + k * 120, 360)], fill=col)
    d.rectangle([420, 360, 1580, 760], fill=(120, 100, 80))                               # 店の中
    _bicycle(d, 520, 640, 0.9)
    _bicycle(d, 1120, 640, 0.9, col=(110, 40, 40))
    for k in range(6):                                                                      # 吊るしたランプ
        _bike_lamp(d, 900 + k * 40, 400, r=14)
    d.rectangle([620, 700, 880, 740], fill=(110, 86, 62))                                 # 実演の台（キャラの間）
    _washer_square(d, 650, 500, 0.95)
    return img


# ---------------------------------------------------------------- 1963 淡路島の港
def minato():
    img = vgrad((W, H), (140, 192, 232), (214, 232, 242))
    d = _d(img)
    d.polygon([(0, 430), (400, 400), (900, 420), (1400, 390), (W, 420), (W, 470), (0, 470)], fill=(140, 160, 150))  # 向こう岸
    d.rectangle([0, 460, W, 760], fill=(60, 120, 166))
    for k in range(5):
        y = 480 + k * 40
        for x in range((k % 2) * 80, W, 240):
            d.arc([x, y, x + 90, y + 22], 200, 340, fill=(110, 164, 200), width=3)
    hx0, hx1, hy = 620, 1320, 640                                                          # フェリー
    d.polygon([(hx0, hy - 110), (hx1, hy - 110), (hx1 - 60, hy), (hx0 + 30, hy)], fill=(246, 246, 244), outline=(150, 150, 150))
    d.rectangle([hx0 + 30, hy - 60, hx1 - 40, hy - 44], fill=(40, 90, 170))
    d.rectangle([hx0 + 120, hy - 200, hx1 - 160, hy - 110], fill=(236, 236, 232), outline=(150, 150, 150), width=3)
    for k in range(8):
        d.rectangle([hx0 + 140 + k * 52, hy - 180, hx0 + 172 + k * 52, hy - 150], fill=(110, 150, 190))
    d.rectangle([hx0 + 400, hy - 270, hx0 + 450, hy - 200], fill=(196, 60, 50))           # 煙突
    for x, y in ((380, 230), (460, 200), (1500, 250)):                                      # かもめ
        d.arc([x, y, x + 40, y + 24], 200, 340, fill=(250, 250, 250), width=4)
        d.arc([x + 36, y, x + 76, y + 24], 200, 340, fill=(250, 250, 250), width=4)
    d.rectangle([0, 740, W, H], fill=(170, 170, 166))                                      # 桟橋
    d.line([(0, 740), (W, 740)], fill=(120, 120, 118), width=6)
    for x in (300, 1620):
        d.rectangle([x, 700, x + 40, 744], fill=(80, 80, 84))                              # 係船柱（端に小さく）
    return img


def shachoshitsu():
    """1968年の社長室。大きな机、窓の外の街、本棚。"""
    img = _rgb(base((214, 204, 186), (196, 186, 168)))
    wood_floor(img, FLOOR, col=(100, 76, 58), line=(84, 62, 48))
    d = _d(img)
    _window(d, 760, 110, 1160, 420, sky=(196, 214, 228), frame=(90, 66, 48))
    for k in range(7):                                                                      # 窓の外のビル
        x = 780 + k * 54
        top = 260 + (k * 37) % 90
        d.rectangle([x, top, x + 44, 410], fill=(150, 160, 172))
    for side in (0, 1):                                                                     # 本棚
        x0 = 300 if side == 0 else 1400
        for k in range(3):
            y = 200 + k * 140
            d.rectangle([x0, y, x0 + 260, y + 12], fill=(90, 64, 44))
            for j in range(8):
                d.rectangle([x0 + 8 + j * 31, y - 96, x0 + 32 + j * 31, y], fill=((120, 60, 50), (60, 80, 110), (150, 130, 80))[(j + k) % 3])
    _desk(d, 660, 1260, 620, col=(96, 64, 44))
    _papers(d, 740, 610)
    _phone(d, 1110, 556, 0.6)
    return img


# ---------------------------------------------------------------- 1970 万博のパビリオン
def banpaku():
    img = vgrad((W, H), (30, 36, 80), (70, 60, 120))
    d = _d(img)
    for k in range(6):                                                                      # アーチ
        r = 900 - k * 120
        d.arc([960 - r, 520 - r * 0.7, 960 + r, 520 + r * 0.7], 180, 360, fill=(110 + k * 20, 120 + k * 16, 200), width=10)
    img = img.convert("RGBA")
    for x, col in ((360, (255, 120, 160)), (960, (120, 220, 255)), (1560, (255, 220, 120))):
        glow(img, x, 160, 260, col, 70)
    d = ImageDraw.Draw(img)
    d.ellipse([700, 700, 1220, 780], fill=(196, 200, 214), outline=(140, 146, 170), width=4)   # 台
    d.ellipse([760, 240, 1160, 740], fill=(170, 220, 240, 255), outline=(220, 250, 255), width=8)  # カプセル
    d.ellipse([800, 280, 1120, 700], fill=(150, 206, 230))
    d.rounded_rectangle([880, 470, 1040, 600], radius=20, fill=(240, 240, 246))           # 座席
    d.rounded_rectangle([890, 390, 1030, 480], radius=20, fill=(240, 240, 246))
    for x, y in ((850, 360), (1060, 420), (900, 620), (1040, 300)):                         # 泡
        d.ellipse([x, y, x + 30, y + 30], outline=(250, 250, 255), width=3)
    d.rectangle([0, FLOOR, W, H], fill=(60, 56, 96))
    return _rgb(img)


# ---------------------------------------------------------------- 2004 小千谷の半導体工場
def _cleanroom(quake=False):
    img = _rgb(base((236, 230, 196), (226, 220, 186)))                                     # 黄色い照明
    d = _d(img)
    for x in range(0, W, 160):                                                              # 天井のフィルター
        for y in (0, 60):
            d.rectangle([x + 4, y + 4, x + 156, y + 56], fill=(246, 242, 220), outline=(200, 194, 160), width=3)
    d.rectangle([0, FLOOR, W, H], fill=(214, 208, 184))
    for x in range(0, W, 120):
        d.line([(x, FLOOR), (x, H)], fill=(196, 190, 166), width=3)
    ang = 4 if quake else 0
    dx = 40 if quake else 0
    # 露光装置（大きな箱）
    box = Image.new("RGBA", (520, 420), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    bd.rectangle([0, 0, 519, 419], fill=(222, 224, 226), outline=(150, 154, 160), width=5)
    bd.rectangle([40, 50, 300, 190], fill=(70, 80, 96))
    bd.rectangle([340, 50, 480, 380], fill=(200, 204, 210), outline=(150, 154, 160), width=3)
    for k in range(4):
        bd.ellipse([370, 90 + k * 60, 400, 120 + k * 60], fill=(90, 200, 110) if not quake else (220, 60, 50))
    bd.rectangle([40, 240, 300, 260], fill=(170, 174, 180))
    box = box.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.paste(box, (700 + dx, 260), box)
    d = _d(img)
    # マスクの保管棚（左奥）
    if not quake:
        d.rectangle([430, 230, 640, 640], fill=(210, 212, 214), outline=(150, 154, 160), width=4)
        for k in range(6):
            y = 260 + k * 62
            d.rectangle([446, y, 624, y + 8], fill=(150, 154, 160))
            for j in range(5):
                d.rectangle([452 + j * 34, y - 40, 480 + j * 34, y], fill=(170, 200, 220))
    else:
        tilt = Image.new("RGBA", (220, 420), (0, 0, 0, 0))
        td = ImageDraw.Draw(tilt)
        td.rectangle([0, 0, 209, 409], fill=(210, 212, 214), outline=(150, 154, 160), width=4)
        for k in range(6):
            td.rectangle([16, 30 + k * 62, 194, 38 + k * 62], fill=(150, 154, 160))
        tilt = tilt.rotate(-28, expand=True, resample=Image.BICUBIC)
        img.paste(tilt, (420, 300), tilt)
        d = _d(img)
    # テスター（右奥の背の高い箱）
    if not quake:
        d.rectangle([1260, 250, 1440, 640], fill=(70, 76, 90), outline=(40, 44, 52), width=4)
        for k in range(6):
            d.rectangle([1280, 280 + k * 56, 1420, 310 + k * 56], fill=(110, 120, 140))
            d.ellipse([1400, 288 + k * 56, 1414, 302 + k * 56], fill=(90, 200, 110))
    else:
        d.rectangle([880, FLOOR - 92, 1140, FLOOR + 4], fill=(70, 76, 90), outline=(40, 44, 52), width=4)  # 倒れたテスター
        for k in range(4):
            d.rectangle([900 + k * 58, FLOOR - 78, 940 + k * 58, FLOOR - 16], fill=(110, 120, 140))
        rnd = random.Random(11)
        for _ in range(16):                                                                  # 床に散らばったマスク
            x, y = rnd.uniform(700, 1180), rnd.uniform(FLOOR + 10, FLOOR + 110)
            a = rnd.uniform(0, math.pi)
            pts = [(x + 22 * math.cos(a + t * math.pi / 2), y + 14 * math.sin(a + t * math.pi / 2)) for t in range(4)]
            d.polygon(pts, fill=(170, 200, 220), outline=(110, 130, 150))
        img = img.convert("RGBA")
        glow(img, 960, 100, 420, (255, 60, 40), 60)                                         # 赤い警告灯
        d = ImageDraw.Draw(img)
        d.ellipse([930, 80, 990, 140], fill=(240, 60, 40))
        rnd = random.Random(5)
        for _ in range(140):                                                                 # 舞うほこり
            x, y = rnd.uniform(0, W), rnd.uniform(120, 700)
            d.ellipse([x, y, x + 4, y + 4], fill=(150, 140, 110, 160))
        img = _rgb(img)
    return img


def cleanroom():
    return _cleanroom(False)


def cleanroom_jishin():
    return _cleanroom(True)


def kojo_soto():
    """地震の翌日、工場の外。曇り空、入口に張られた立入禁止のテープ。"""
    img = vgrad((W, H), (150, 154, 162), (196, 198, 202))
    d = _d(img)
    d.rectangle([0, 800, W, H], fill=(110, 110, 114))
    d.rectangle([300, 260, 1620, 800], fill=(226, 228, 230), outline=(160, 164, 170), width=4)
    d.rectangle([300, 260, 1620, 300], fill=(190, 194, 200))
    for k in range(12):
        x = 340 + k * 106
        d.rectangle([x, 360, x + 70, 420], fill=(90, 100, 112))
    d.rectangle([840, 560, 1080, 800], fill=(80, 88, 100))                                 # 入口
    for k in range(10):                                                                     # 黄色と黒のテープ
        x = 760 + k * 40
        d.polygon([(x, 600), (x + 20, 600), (x + 40, 630), (x + 20, 630)], fill=(240, 200, 40) if k % 2 == 0 else (30, 30, 30))
    d.rectangle([760, 600, 1160, 630], outline=(40, 40, 40), width=2)
    for x in (760, 1160):                                                                   # コーン（キャラの間）
        d.polygon([(x - 26, 790), (x + 26, 790), (x + 8, 660), (x - 8, 660)], fill=(240, 110, 40))
        d.rectangle([x - 20, 716, x + 20, 732], fill=(250, 250, 250))
    for k in range(3):                                                                      # ひびの入った壁
        d.line([(500 + k * 400, 300), (520 + k * 400, 380), (500 + k * 400, 450)], fill=(120, 120, 126), width=4)
    return img


# ---------------------------------------------------------------- 2000年代のオフィス
def _office_base():
    img = _rgb(base((226, 228, 230), (210, 212, 216)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(150, 156, 166))
    for x in range(0, W, 240):
        for y in (20,):
            d.rectangle([x + 40, y, x + 200, y + 18], fill=(250, 250, 246))                 # 蛍光灯
    _window(d, 300, 120, 640, 440, sky=(176, 200, 222), frame=(150, 154, 160))
    for k in range(5):
        x = 320 + k * 62
        top = 250 + (k * 41) % 120
        d.rectangle([x, top, x + 48, 430], fill=(140, 150, 166))
    d.rectangle([1300, 140, 1640, 380], fill=(246, 248, 250), outline=(140, 146, 154), width=6)   # ホワイトボード
    for k in range(4):
        d.line([(1330, 190 + k * 44), (1600 - k * 40, 190 + k * 44)], fill=(150, 160, 190), width=4)
    _desk(d, 700, 1220, 620, col=(196, 196, 200))
    _monitor(d, 760, 470)
    _monitor(d, 1000, 470, screen=(90, 130, 170))
    return img


def office():
    img = _office_base()
    d = _d(img)
    d.rectangle([920, 590, 1000, 620], fill=(244, 242, 234), outline=(160, 156, 146), width=2)   # 新聞
    d.line([(930, 600), (990, 600)], fill=(120, 120, 126), width=3)
    _phone(d, 1160, 566, 0.45, col=(60, 60, 66))
    return img


def uketsuke():
    """1985年、回収の電話を受ける部屋。電話の並ぶ机と、戻ってきた石油ファンヒーター。"""
    img = _rgb(base((214, 210, 196), (198, 194, 180)))
    wood_floor(img, FLOOR, col=(120, 112, 100), line=(100, 94, 84))
    d = _d(img)
    for x in range(0, W, 240):
        d.rectangle([x + 40, 20, x + 200, 36], fill=(250, 250, 240))                       # 蛍光灯
    d.rectangle([300, 140, 640, 400], fill=(240, 238, 230), outline=(120, 116, 106), width=6)   # 予定表（文字なし）
    for r in range(5):
        for c in range(7):
            d.rectangle([316 + c * 46, 160 + r * 46, 352 + c * 46, 196 + r * 46], outline=(170, 166, 156), width=2)
    for k in (3, 9, 16, 22, 27):
        r, c = divmod(k, 7)
        d.line([(320 + c * 46, 164 + r * 46), (348 + c * 46, 192 + r * 46)], fill=(200, 70, 60), width=4)
    _shelf(d, 1300, 1660, 300)                                                             # ファイルの棚
    for k in range(9):
        d.rectangle([1312 + k * 38, 200, 1340 + k * 38, 300], fill=((70, 90, 130), (150, 120, 70), (110, 120, 110))[k % 3])
    for k in range(3):                                                                      # 戻ってきたファンヒーター
        x = 760 + k * 140
        d.rectangle([x, 430, x + 120, 560], fill=(236, 232, 222), outline=(150, 146, 136), width=3)
        for j in range(5):
            d.line([(x + 14, 470 + j * 16), (x + 106, 470 + j * 16)], fill=(150, 146, 136), width=3)
        d.rectangle([x + 14, 440, x + 60, 456], fill=(120, 126, 136))
    _desk(d, 700, 1220, 600, col=(150, 146, 136))
    for x in (760, 1100):                                                                   # 電話
        d.rounded_rectangle([x, 556, x + 100, 600], radius=10, fill=(226, 218, 196), outline=(150, 140, 120), width=2)
        d.rounded_rectangle([x - 6, 540, x + 106, 560], radius=10, fill=(226, 218, 196), outline=(150, 140, 120), width=2)
        for j in range(3):
            d.rectangle([x + 22 + j * 20, 570, x + 34 + j * 20, 582], fill=(150, 140, 120))
    _papers(d, 920, 598, n=3)
    return img


def kaigi():
    """2005年の会議室。長い机に電池の試作、正面の画面に電池の絵と「？」。"""
    img = _rgb(base((222, 224, 228), (206, 208, 214)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(120, 126, 140))
    d.rectangle([700, 110, 1220, 400], fill=(250, 250, 252), outline=(90, 94, 104), width=8)   # 画面
    for k in range(3):
        _battery(d, 780 + k * 90, 180, horiz=False, L=150, R=54, band=(110, 160, 210))
    _text_c(d, 1110, 255, "？", 150, (200, 70, 60))
    d.polygon([(660, 560), (1260, 560), (1300, 640), (620, 640)], fill=(150, 116, 86))        # 長い机
    d.rectangle([620, 640, 1300, 660], fill=(120, 92, 68))
    for k in range(6):
        _battery(d, 760 + k * 70, 576, horiz=True, L=50, R=16)
    return img


def kaiken():
    """2008年、大阪のホテルの会見場。白い布の長机とマイク、無地の背景幕。"""
    img = _rgb(base((206, 190, 160), (186, 170, 142)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(140, 60, 60))                                      # じゅうたん
    for y in range(FLOOR + 20, H, 40):
        d.line([(0, y), (W, y)], fill=(124, 52, 52), width=3)
    d.rectangle([480, 120, 1440, 560], fill=(40, 70, 130))                                 # 背景幕（文字なし）
    d.rectangle([480, 120, 1440, 150], fill=(196, 170, 90))
    for x in (300, 1620):                                                                    # シャンデリア
        d.line([(x, 0), (x, 60)], fill=(150, 130, 90), width=4)
        for k in range(5):
            d.ellipse([x - 60 + k * 26, 60, x - 44 + k * 26, 90], fill=(255, 236, 180))
    img = img.convert("RGBA")
    for x, y in ((380, 300), (1540, 260)):                                                   # カメラのフラッシュ
        glow(img, x, y, 140, (255, 255, 255), 90)
    d = ImageDraw.Draw(img)
    d.rectangle([640, 560, 1280, 640], fill=(248, 248, 246), outline=(200, 200, 196), width=3)   # 長机
    d.rectangle([640, 640, 1280, 700], fill=(236, 236, 232))
    for x in (800, 1120):                                                                    # マイク
        d.line([(x, 560), (x - 20, 500)], fill=(40, 40, 44), width=5)
        d.ellipse([x - 32, 486, x - 10, 508], fill=(30, 30, 34))
        d.rectangle([x - 30, 546, x + 30, 560], fill=(60, 60, 64))
    d.ellipse([920, 500, 1000, 560], fill=(240, 200, 210))                                 # 花
    d.rectangle([944, 540, 976, 560], fill=(90, 130, 90))
    return _rgb(img)


def eigyo():
    """2010年の営業部。机に白いパン焼き機、電話とモニター。"""
    img = _office_base()
    d = _d(img)
    d.rounded_rectangle([880, 520, 1000, 620], radius=12, fill=(246, 246, 244), outline=(150, 150, 150), width=3)  # パン焼き機
    d.rectangle([900, 540, 980, 580], fill=(70, 70, 76))
    d.ellipse([948, 590, 962, 604], fill=(90, 200, 110))
    _phone(d, 1160, 566, 0.45, col=(60, 60, 66))
    return img


def eigyo_yama():
    """注文の紙が机に山積み。ファクスから紙がのびる。"""
    img = eigyo()
    d = _d(img)
    rnd = random.Random(3)
    for x0, h in ((710, 9), (1080, 11), (1180, 7)):                                         # 机の上の山
        for k in range(h):
            x = x0 + rnd.uniform(-8, 8)
            y = 610 - k * 16
            d.rectangle([x, y - 12, x + 100, y + 2], fill=(250, 248, 238), outline=(170, 164, 150), width=2)
    for k in range(9):                                                                       # 壁の注文票
        x, y = 1310 + (k % 3) * 110, 150 + (k // 3) * 80
        d.rectangle([x, y, x + 90, y + 66], fill=(252, 246, 200), outline=(180, 170, 120), width=2)
    d.rectangle([520, 520, 640, 580], fill=(220, 220, 214), outline=(140, 140, 136), width=3)   # ファクス
    pts = [(560, 520), (556, 470), (590, 430), (570, 380), (610, 330)]
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=(252, 250, 240), width=26)
    for x, y in ((780, FLOOR + 20), (870, FLOOR + 60), (1000, FLOOR + 30), (1110, FLOOR + 70)):   # 床に落ちた紙（キャラの間）
        d.rectangle([x, y, x + 70, y + 40], fill=(250, 248, 238), outline=(170, 164, 150), width=2)
    return img


def sentaku_kojo():
    """2011年、洗濯機の工場。流れてくる洗濯機の列。"""
    img = _rgb(base((206, 214, 222), (190, 198, 206)))
    d = _d(img)
    for x in range(0, W, 240):
        d.rectangle([x + 40, 20, x + 200, 36], fill=(250, 250, 246))
    for x in range(0, W, 320):                                                               # 鉄骨
        d.line([(x, 0), (x, 520)], fill=(150, 160, 170), width=10)
    d.rectangle([0, 600, W, 650], fill=(80, 86, 96))                                       # ベルトコンベヤー
    for x in range(0, W, 60):
        d.line([(x, 600), (x, 650)], fill=(100, 106, 116), width=3)
    for k in range(9):                                                                       # 洗濯機
        x = 40 + k * 210
        d.rectangle([x, 420, x + 160, 600], fill=(244, 246, 248), outline=(150, 156, 164), width=3)
        if k % 2 == 0:
            d.ellipse([x + 30, 470, x + 130, 570], fill=(180, 196, 212), outline=(120, 130, 146), width=5)
        else:
            d.rectangle([x + 10, 430, x + 150, 456], fill=(210, 216, 222))
        d.ellipse([x + 120, 434, x + 140, 450], fill=(90, 96, 106))
    d.rectangle([0, FLOOR, W, H], fill=(150, 160, 150))
    return img


def ronsou():
    """地震で潰れたのか: 揺れの波形の札、赤い印の帳簿の札、真ん中に「？」。"""
    img = vgrad((W, H), (240, 236, 226), (220, 218, 210))
    d = _d(img)
    for cx in (740, 1180):
        d.rounded_rectangle([cx - 150, 170, cx + 150, 560], radius=18, fill=(250, 248, 240), outline=INK, width=5)
    pts = []
    for k in range(60):                                                                      # 揺れの波形
        x = 610 + k * 4.4
        amp = 90 * math.exp(-((k - 22) / 14) ** 2)
        pts.append((x, 360 + amp * math.sin(k * 1.3)))
    d.line(pts, fill=(200, 70, 60), width=5)
    d.line([(600, 360), (880, 360)], fill=(160, 160, 166), width=2)
    for k in range(8):                                                                       # 帳簿の行
        y = 220 + k * 40
        d.line([(1060, y), (1300, y)], fill=(160, 160, 166), width=3)
        d.rectangle([1220, y + 8, 1290, y + 30], fill=(120, 120, 126) if k % 3 else (210, 70, 60))
    d.ellipse([1150, 330, 1250, 400], outline=(210, 70, 60), width=6)
    _text_c(d, 960, 380, "？", 150, (200, 70, 60))
    return img


LOCATIONS = {
    "sa_kanban": kanban, "sa_kanban_kara": kanban_kara, "sa_honsha": honsha, "sa_gendai": gendai,
    "sa_heya": heya, "sa_heya_jyuden": heya_jyuden, "sa_awaji": awaji, "sa_shakuya": shakuya,
    "sa_matsushita": matsushita, "sa_matsushita_sengo": matsushita_sengo, "sa_matsushita_yoru": matsushita_yoru,
    "sa_sagyoba": sagyoba, "sa_sagyoba_kasa": sagyoba_kasa,
    "sa_hojo": hojo, "sa_hojo_2005": hojo_2005, "sa_hojo_ato": hojo_ato,
    "sa_shonin": shonin, "sa_kaihatsu": kaihatsu, "sa_niwa": niwa, "sa_jitenshaya": jitenshaya,
    "sa_minato": minato, "sa_shachoshitsu": shachoshitsu, "sa_banpaku": banpaku,
    "sa_cleanroom": cleanroom, "sa_cleanroom_jishin": cleanroom_jishin, "sa_kojo_soto": kojo_soto,
    "sa_office": office, "sa_uketsuke": uketsuke, "sa_kaigi": kaigi, "sa_kaiken": kaiken,
    "sa_eigyo": eigyo, "sa_eigyo_yama": eigyo_yama, "sa_sentaku_kojo": sentaku_kojo, "sa_ronsou": ronsou,
}

CARDS = ["1917", "1918", "1947", "1963", "1969", "2004", "2005", "2008", "2011"]


def year_card(text: str) -> Image.Image:
    """黒地に年号だけのカード。キャラと同居させない単独シーンで使う。"""
    img = Image.new("RGB", (W, H), (18, 18, 20))
    d = _d(img)
    font = _font(150)
    bb = d.textbbox((0, 0), text, font=font)
    d.text(((W - (bb[2] - bb[0])) // 2 - bb[0], (H - (bb[3] - bb[1])) // 2 - 40 - bb[1]),
           text, font=font, fill=(238, 234, 226))
    d.line([(W // 2 - 220, H // 2 + 110), (W // 2 + 220, H // 2 + 110)],
           fill=(150, 146, 138), width=4)
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    n = 0
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        img = _rgb(fn())
        assert img.size == (W, H), (name, img.size)
        img.save(OUT / f"{name}.png")
        n += 1
        print(f"生成完了: {name}.png")
    for y in CARDS:
        if only and f"sa_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"sa_card_{y}.png")
        n += 1
        print(f"生成完了: sa_card_{y}.png")
    print(f"合計 {n} 枚")
