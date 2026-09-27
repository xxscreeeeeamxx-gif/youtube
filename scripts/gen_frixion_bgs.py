#!/usr/bin/env python3
"""消せるボールペンの誕生回（66_消せるボールペンの誕生 / slug=frixion-metamo）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はスーパーカブ回（gen_supercub_bgs.py）と同じ。
実在の会社の商標（ロゴ・社名の文字）は描かない。ペンの絵にも社名や商品名は入れない。

実行: PYTHONPATH=. python scripts/gen_frixion_bgs.py [名前...]
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


def _pen(d, x, y, length=220, body=(40, 60, 120), rubber=(230, 230, 224), w=22):
    """横向きのボールペン（右がペン先、左の端にこする用のラバー）。"""
    d.rounded_rectangle([x, y - w / 2, x + length, y + w / 2], radius=int(w / 2), fill=body)
    d.polygon([(x + length, y - w / 2 + 3), (x + length + 30, y), (x + length, y + w / 2 - 3)], fill=(200, 200, 206))
    d.rounded_rectangle([x - 22, y - w / 2 + 2, x + 4, y + w / 2 - 2], radius=6, fill=rubber)
    d.rectangle([x + 30, y - w / 2 - 6, x + 110, y - w / 2 + 2], fill=(170, 170, 176))   # クリップ


def _notebook(d, x, y, wd=280, ht=190, lines=True, written=True):
    d.rectangle([x, y, x + wd, y + ht], fill=(250, 250, 244), outline=(170, 170, 176), width=3)
    if lines:
        for k in range(1, 7):
            d.line([(x + 14, y + k * ht / 7), (x + wd - 14, y + k * ht / 7)], fill=(190, 210, 230), width=2)
    if written:
        rnd = random.Random(x + y)
        for k in range(1, 6):
            yy = y + k * ht / 7 - 8
            xx = x + 24
            while xx < x + wd - 60:
                seg = rnd.uniform(14, 40)
                d.line([(xx, yy), (xx + seg, yy)], fill=(40, 50, 90), width=4)
                xx += seg + rnd.uniform(6, 14)


def _test_tube(d, x, y, h=150, liquid=(200, 60, 60)):
    d.rounded_rectangle([x, y, x + 36, y + h], radius=18, outline=(160, 170, 180), width=4)
    d.rounded_rectangle([x + 4, y + h * 0.45, x + 32, y + h - 4], radius=14, fill=liquid)


def _beaker(d, x, y, s=1.0, liquid=None):
    w, h = 90 * s, 110 * s
    d.polygon([(x, y), (x + w, y), (x + w - 6 * s, y + h), (x + 6 * s, y + h)], outline=(150, 170, 180), fill=(236, 244, 248))
    if liquid:
        d.polygon([(x + 4 * s, y + h * 0.5), (x + w - 4 * s, y + h * 0.5), (x + w - 8 * s, y + h - 3), (x + 8 * s, y + h - 3)], fill=liquid)


# ---------------------------------------------------------------- 場所
def heya():
    """今の勉強机。書き込んだノートと、消せるボールペン。"""
    img = _rgb(base((236, 232, 222), (216, 212, 202)))
    wood_floor(img, FLOOR, col=(150, 120, 90), line=(130, 104, 78))
    d = _d(img)
    _window(d, 780, 110, 1140, 360, sky=(180, 214, 236))
    _table(d, 700, 1220, 620, col=(170, 136, 100))
    _notebook(d, 760, 440, 300, 180)
    _pen(d, 1080, 600, 150, body=(40, 60, 120))
    d.rectangle([1100, 520, 1180, 600], fill=(220, 90, 90))                     # 付箋の手帳
    return img


def heya2():
    """1960年ごろの勉強部屋。机の上の受験の参考書。"""
    img = _rgb(base((226, 214, 190), (206, 194, 170)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    _window(d, 780, 110, 1140, 360, sky=(190, 206, 214))
    d.rectangle([720, 640, 1200, 680], fill=(120, 86, 56))                      # 座卓
    for x in (740, 1160):
        d.rectangle([x, 680, x + 20, 800], fill=(100, 70, 44))
    d.rectangle([860, 560, 1060, 640], fill=(190, 40, 40), outline=(120, 20, 20), width=3)   # 赤本
    d.rectangle([870, 570, 1050, 630], outline=(240, 220, 200), width=2)
    return img


def kombinat():
    """夜の石油化学コンビナート。パイプ、タンク、たくさんの明かり。"""
    img = vgrad((W, H), (30, 36, 70), (80, 70, 90))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(40, 40, 50))
    rnd = random.Random(4)
    for k in range(9):                                                          # 塔
        x = 120 + k * 200
        h = 240 + (k % 4) * 90
        d.rectangle([x, 760 - h, x + 40, 760], fill=(70, 74, 90))
        for y in range(760 - h, 760, 36):
            d.ellipse([x + 14, y, x + 26, y + 12], fill=(255, 220, 140))
    for cx in (560, 1360):                                                      # タンク
        d.ellipse([cx - 110, 620, cx + 110, 700], fill=(90, 96, 110))
        d.rectangle([cx - 110, 660, cx + 110, 760], fill=(90, 96, 110))
    d.line([(0, 640), (W, 640)], fill=(110, 110, 124), width=10)
    d.line([(0, 680), (W, 680)], fill=(110, 110, 124), width=6)
    for _ in range(60):
        x, y = rnd.uniform(0, W), rnd.uniform(420, 750)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 230, 160))
    return img


def daigaku():
    """1960年代の大学の化学の実験室。流しとビーカー。"""
    img = _rgb(base((222, 224, 220), (200, 202, 198)))
    wood_floor(img, FLOOR, col=(120, 110, 96), line=(100, 92, 80))
    d = _d(img)
    d.rectangle([720, 560, 1200, 620], fill=(70, 80, 86))                       # 実験台
    d.rectangle([740, 620, 1180, 800], fill=(90, 100, 106))
    d.rectangle([800, 500, 960, 560], fill=(200, 206, 210))                     # 流し
    d.line([(880, 420), (880, 500)], fill=(150, 150, 156), width=8)
    d.arc([860, 400, 920, 460], 180, 360, fill=(150, 150, 156), width=8)
    for k in range(3):
        _beaker(d, 990 + k * 60, 450, 0.55)
    for x in (100, 1500):                                                       # 薬品の棚
        d.rectangle([x, 200, x + 320, 700], fill=(150, 120, 90))
        for r in range(4):
            d.rectangle([x, 300 + r * 100, x + 320, 310 + r * 100], fill=(110, 86, 62))
            for k in range(5):
                d.rectangle([x + 20 + k * 60, 250 + r * 100, x + 50 + k * 60, 300 + r * 100], fill=(180 - k * 12, 150, 110 + k * 16))
    return img


def kenkyu(night=False):
    """インキの研究室。棚の瓶と実験台。night=True は夜の研究室に試験管と加熱器。"""
    top, bot = ((200, 202, 206), (176, 178, 184)) if not night else ((120, 126, 140), (96, 100, 112))
    img = _rgb(base(top, bot))
    wood_floor(img, FLOOR, col=(110, 104, 96), line=(90, 86, 80))
    d = _d(img)
    if night:
        _window(d, 1300, 120, 1640, 360, sky=(30, 36, 70))
        d.ellipse([1480, 160, 1520, 200], fill=(240, 240, 210))                # 月
    for x in (60, 360) if not night else (60,):
        d.rectangle([x, 220, x + 260, 700], fill=(140, 116, 90))
        for r in range(4):
            d.rectangle([x, 320 + r * 100, x + 260, 330 + r * 100], fill=(100, 80, 60))
            for k in range(4):
                col = [(60, 70, 140), (160, 40, 40), (40, 110, 70), (60, 60, 66)][(k + r) % 4]
                d.rounded_rectangle([x + 20 + k * 60, 260 + r * 100, x + 60 + k * 60, 320 + r * 100], radius=8, fill=col)
    d.rectangle([720, 600, 1200, 640], fill=(70, 80, 86))                       # 実験台
    d.rectangle([740, 640, 1180, 800], fill=(90, 100, 106))
    if night:
        for k, col in enumerate([(200, 60, 60), (230, 150, 60), (240, 236, 220), (60, 90, 170)]):
            _test_tube(d, 780 + k * 60, 440, 150, col)
        d.rectangle([1040, 540, 1140, 600], fill=(60, 60, 66))                  # 加熱器
        d.ellipse([1070, 520, 1110, 546], fill=(250, 140, 60))
        d.ellipse([1150, 300, 1190, 340], fill=(255, 240, 180))                # 電灯
    else:
        for k in range(3):
            _beaker(d, 780 + k * 120, 490, 0.9, liquid=[(60, 70, 140), (160, 40, 40), (40, 110, 70)][k])
    return img


def kenkyu2():
    return kenkyu(night=True)


def kouyou():
    """秋の渓谷。赤と黄色の紅葉と、谷川。"""
    img = vgrad((W, H), (170, 206, 236), (230, 226, 210))
    d = _d(img)
    d.polygon([(0, 700), (0, 300), (500, 420), (900, 700)], fill=(120, 80, 60))
    d.polygon([(W, 700), (W, 280), (1400, 420), (1000, 700)], fill=(110, 76, 56))
    rnd = random.Random(10)
    for _ in range(260):                                                        # 紅葉
        x, y = rnd.uniform(0, W), rnd.uniform(180, 700)
        if 700 < x < 1220 and y > 420:
            continue
        col = rnd.choice([(220, 60, 40), (240, 120, 40), (250, 190, 60), (200, 40, 40), (120, 150, 70)])
        r = rnd.uniform(18, 46)
        d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=col)
    d.polygon([(700, 700), (1220, 700), (1120, H), (800, H)], fill=(110, 170, 200))  # 谷川
    d.rectangle([0, 820, 700, H], fill=(120, 110, 90))
    d.rectangle([1220, 820, W, H], fill=(120, 110, 90))
    for k in range(5):                                                          # 手前の赤い葉と緑の葉
        x = 820 + k * 70
        col = (220, 50, 40) if k % 2 == 0 else (90, 150, 70)
        d.polygon([(x, 430), (x + 24, 470), (x, 510), (x - 24, 470)], fill=col)
    return img


def kaigi():
    """会議室。机の書類と、色の変わる試作品。"""
    img = _rgb(base((226, 222, 212), (206, 202, 192)))
    wood_floor(img, FLOOR, col=(120, 100, 80), line=(100, 84, 66))
    d = _d(img)
    d.rectangle([760, 140, 1160, 380], fill=(60, 80, 70), outline=(110, 90, 60), width=10)   # 黒板
    d.line([(800, 220), (1100, 220)], fill=(230, 230, 220), width=3)
    _table(d, 700, 1220, 640, col=(110, 86, 62))
    for k in range(3):
        d.rectangle([760 + k * 150, 600, 880 + k * 150, 640], fill=(244, 240, 228), outline=(170, 160, 140))
    d.rounded_rectangle([1150, 560, 1200, 640], radius=10, fill=(220, 120, 160))   # 試作品
    return img


def shouhin():
    """1970年代の商品の台。冷水で色が変わる紙コップ。"""
    img = _rgb(base((236, 230, 216), (216, 210, 196)))
    wood_floor(img, FLOOR, col=(140, 116, 90), line=(120, 98, 76))
    d = _d(img)
    _table(d, 700, 1220, 640, col=(150, 116, 80))
    for k, col in enumerate([(240, 240, 236), (120, 170, 230), (240, 240, 236), (240, 150, 190)]):
        x = 740 + k * 120
        d.polygon([(x, 520), (x + 90, 520), (x + 78, 640), (x + 12, 640)], fill=col, outline=(150, 150, 156))
    d.line([(900, 500), (940, 470)], fill=(90, 150, 230), width=4)               # 水
    return img


def shouhin2():
    """メタモカラーのおもちゃの棚。人形、フライのおもちゃ、湯船。"""
    img = _rgb(base((240, 232, 226), (220, 212, 206)))
    wood_floor(img, FLOOR, col=(170, 140, 110), line=(150, 122, 96))
    d = _d(img)
    d.rectangle([700, 200, 1220, 760], fill=(200, 170, 140))
    for r in range(3):
        d.rectangle([700, 360 + r * 170, 1220, 372 + r * 170], fill=(150, 116, 86))
    d.ellipse([760, 260, 830, 330], fill=(250, 220, 200))                       # 人形の顔
    d.ellipse([740, 240, 850, 300], fill=(240, 150, 190))                      # 髪（色が変わる）
    d.rectangle([770, 330, 820, 360], fill=(120, 170, 230))
    d.ellipse([900, 300, 1000, 350], fill=(220, 170, 80))                      # フライ
    d.ellipse([1040, 470, 1180, 530], fill=(160, 210, 240))                    # 湯船
    d.rectangle([1040, 500, 1180, 540], fill=(250, 250, 250))
    d.ellipse([760, 460, 820, 520], fill=(250, 220, 200))
    d.ellipse([746, 440, 834, 490], fill=(90, 70, 150))                        # 髪の色が変わった人形
    return img


def zukai1():
    """図解: 色を保つ温度の幅（ヒステリシス）。キャラの間に収める。"""
    img = vgrad((W, H), (244, 244, 238), (226, 230, 226))
    d = _d(img)
    x0, x1, y = 520, 1400, 560
    d.line([(x0, y), (x1, y)], fill=INK, width=5)
    d.polygon([(x1, y - 12), (x1 + 24, y), (x1, y + 12)], fill=INK)
    t2x = lambda t: x0 + (t + 30) / 105 * (x1 - x0)                          # noqa: E731
    for t in (-20, 0, 40, 65):
        x = t2x(t)
        d.line([(x, y - 10), (x, y + 10)], fill=INK, width=4)
        _text_c(d, x, y + 20, f"{t}℃", 30, INK)
    d.rectangle([t2x(-20), y - 170, t2x(65), y - 110], fill=(200, 230, 200))
    _text_c(d, (t2x(-20) + t2x(65)) / 2, y - 158, "この間は、色がそのまま", 32, (40, 110, 60))
    d.rectangle([t2x(0), y - 90, t2x(40), y - 40], fill=(230, 230, 200))
    _text_c(d, (t2x(0) + t2x(40)) / 2, y - 82, "2002年ごろ", 28, INK)
    _text_c(d, t2x(-20), y - 250, "色が戻る", 32, (60, 90, 170))
    _text_c(d, t2x(65), y - 250, "色が消える", 32, (200, 60, 50))
    d.line([(t2x(-20), y - 205), (t2x(-20), y - 175)], fill=(60, 90, 170), width=4)
    d.line([(t2x(65), y - 205), (t2x(65), y - 175)], fill=(200, 60, 50), width=4)
    return img


def zukai0():
    """図解: 初期（差が数度）と1988年のメモリータイプ（約20℃の幅）。まだ −20〜65℃ は出さない。"""
    img = vgrad((W, H), (244, 244, 238), (226, 230, 226))
    d = _d(img)
    x0, x1, y = 520, 1400, 560
    d.line([(x0, y), (x1, y)], fill=INK, width=5)
    d.polygon([(x1, y - 12), (x1 + 24, y), (x1, y + 12)], fill=INK)
    _text_c(d, x1 - 40, y + 20, "温度", 30, INK)
    d.rectangle([860, y - 250, 900, y - 190], fill=(230, 200, 200))
    _text_c(d, 880, y - 300, "最初: 差は数度", 32, (200, 60, 50))
    d.rectangle([760, y - 150, 1000, y - 90], fill=(200, 230, 200))
    _text_c(d, 880, y - 180, "1988年: 約20℃の幅", 32, (40, 110, 60))
    _text_c(d, 880, y - 138, "色をそのまま保つ", 28, (40, 110, 60))
    return img


def office():
    """2000年代の会社の打ち合わせ。机に色が変わるペンの見本。"""
    img = _rgb(base((230, 230, 226), (210, 210, 206)))
    wood_floor(img, FLOOR, col=(140, 130, 120), line=(120, 112, 104))
    d = _d(img)
    _window(d, 760, 120, 1160, 380, sky=(190, 214, 236))
    _table(d, 700, 1220, 640, col=(120, 100, 84))
    for k, col in enumerate([(200, 60, 60), (60, 90, 170), (40, 130, 80)]):
        _pen(d, 780 + k * 10, 560 + k * 26, 200, body=col, w=18)
    d.rectangle([1040, 580, 1180, 640], fill=(244, 240, 228), outline=(170, 160, 140))
    return img


def zukai3():
    """図解: ボールペンのインクの種類。油性・水性・ゲル・消せる。"""
    img = vgrad((W, H), (244, 244, 238), (226, 230, 226))
    d = _d(img)
    cols = [("油性", (60, 60, 66)), ("水性", (60, 110, 200)), ("ゲル", (40, 140, 90)), ("消せる", (200, 60, 50))]
    for k, (t, c) in enumerate(cols):
        x = 540 + k * 230
        d.rounded_rectangle([x, 300, x + 190, 620], radius=24, fill=(250, 250, 246), outline=c, width=6)
        _text_c(d, x + 95, 330, t, 40, c)
        d.rounded_rectangle([x + 80, 400, x + 110, 580], radius=12, fill=c)
        d.polygon([(x + 84, 580), (x + 106, 580), (x + 95, 604)], fill=(190, 190, 196))
    _text_c(d, 540 + 3 * 230 + 95, 640, "第4のインキ", 32, (200, 60, 50))
    return img


def fuyajo():
    """2000年代の夜の研究室。明かりのついた窓、机に並ぶペンと冷凍庫。"""
    img = _rgb(base((150, 156, 170), (120, 126, 140)))
    wood_floor(img, FLOOR, col=(110, 110, 116), line=(90, 90, 96))
    d = _d(img)
    for k in range(3):
        _window(d, 560 + k * 300, 120, 800 + k * 300, 330, sky=(24, 30, 60))
    d.rectangle([700, 600, 1220, 640], fill=(80, 86, 96))
    d.rectangle([720, 640, 1200, 800], fill=(96, 100, 110))
    for k in range(5):
        _pen(d, 740 + k * 18, 520 + k * 16, 170, body=[(40, 60, 120), (200, 60, 60), (40, 130, 80), (230, 150, 60), (60, 60, 66)][k], w=16)
    d.rectangle([1380, 360, 1560, 800], fill=(220, 226, 232), outline=(150, 156, 164), width=4)   # 冷凍庫
    d.line([(1380, 500), (1560, 500)], fill=(150, 156, 164), width=4)
    d.rectangle([1530, 400, 1542, 470], fill=(150, 156, 164))
    return img


def france():
    """フランスの小学校の教室。机の万年筆とインク瓶、インク消し。"""
    img = _rgb(base((236, 228, 210), (216, 208, 190)))
    wood_floor(img, FLOOR, col=(150, 110, 80), line=(130, 94, 66))
    d = _d(img)
    d.rectangle([700, 130, 1220, 400], fill=(50, 80, 70), outline=(120, 90, 60), width=10)   # 黒板
    for k in range(3):
        d.line([(760, 190 + k * 60), (1120, 190 + k * 60)], fill=(230, 230, 220), width=3)
    _table(d, 720, 1200, 640, col=(150, 110, 80))
    _pen(d, 780, 610, 170, body=(20, 30, 60), w=20)                            # 万年筆
    d.rounded_rectangle([990, 570, 1050, 640], radius=8, fill=(40, 60, 140))   # インク瓶
    d.rectangle([1005, 556, 1035, 572], fill=(30, 30, 30))
    _pen(d, 1070, 600, 90, body=(240, 240, 236), rubber=(120, 170, 230), w=16)  # インク消し
    return img


def bunguten():
    """文房具店の売り場。空になった棚と、段ボール箱。"""
    img = _rgb(base((240, 238, 232), (222, 220, 214)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(200, 196, 190))
    d.rectangle([700, 180, 1220, 760], fill=(250, 250, 248), outline=(170, 170, 176), width=6)
    for r in range(4):
        y = 300 + r * 120
        d.rectangle([700, y, 1220, y + 10], fill=(170, 170, 176))
        if r == 3:
            for k in range(6):
                _pen(d, 740 + k * 72, y - 30, 50, body=(40, 60, 120), w=10)
    d.rectangle([760, 190, 1160, 240], fill=(230, 80, 80))                     # 売り場の札（文字なし）
    d.rectangle([1260, 660, 1440, 800], fill=(200, 160, 110), outline=(150, 116, 76), width=4)   # 段ボール
    d.line([(1260, 700), (1440, 700)], fill=(150, 116, 76), width=4)
    return img


def zukai2():
    """図解: インクの粒の中の3つの成分。温めると離れ、冷やすとくっつく。"""
    img = vgrad((W, H), (244, 244, 238), (226, 230, 226))
    d = _d(img)

    def capsule(cx, cy, colored):
        d.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], fill=(250, 250, 246), outline=INK, width=5)
        if colored:
            d.ellipse([cx - 70, cy - 40, cx - 10, cy + 20], fill=(40, 50, 90))       # 色のもと＋相棒＝色
            d.ellipse([cx - 20, cy - 30, cx + 30, cy + 20], fill=(90, 140, 230))
            for k in range(5):
                d.ellipse([cx + 40 + (k % 3) * 22, cy + 40 + (k // 3) * 22, cx + 58 + (k % 3) * 22, cy + 58 + (k // 3) * 22], fill=(240, 160, 60))
        else:
            d.ellipse([cx - 90, cy - 50, cx - 30, cy + 10], outline=(150, 150, 156), width=4)   # 色のもと（無色）
            d.ellipse([cx + 30, cy + 10, cx + 80, cy + 60], fill=(90, 140, 230))              # 相棒は調整剤の側へ
            for k in range(5):
                d.ellipse([cx + 20 + (k % 3) * 22, cy + 60 + (k // 3) * 22, cx + 38 + (k % 3) * 22, cy + 78 + (k // 3) * 22], fill=(240, 160, 60))

    capsule(700, 430, True)
    capsule(1220, 430, False)
    d.line([(880, 380), (1040, 380)], fill=(200, 60, 50), width=6)
    d.polygon([(1040, 368), (1066, 380), (1040, 392)], fill=(200, 60, 50))
    _text_c(d, 960, 320, "60℃〜 こする", 30, (200, 60, 50))
    d.line([(1040, 480), (880, 480)], fill=(60, 90, 170), width=6)
    d.polygon([(880, 468), (854, 480), (880, 492)], fill=(60, 90, 170))
    _text_c(d, 960, 496, "−20℃ 冷やす", 30, (60, 90, 170))
    _text_c(d, 700, 600, "色が見える", 34, INK)
    _text_c(d, 1220, 600, "透明になる", 34, INK)
    for k, (t, c) in enumerate([("色のもと", (40, 50, 90)), ("相棒", (90, 140, 230)), ("温度を決める成分", (240, 160, 60))]):
        x = 560 + k * 260
        d.ellipse([x, 700, x + 30, 730], fill=c)
        d.text((x + 40, 696), t, font=_font(30), fill=INK)
    return img


def ronsou():
    """使ってはいけない書類。証書と印鑑、ペンにばつ印。"""
    img = vgrad((W, H), (240, 236, 226), (220, 218, 210))
    d = _d(img)
    d.rectangle([700, 200, 1000, 600], fill=(250, 248, 238), outline=(170, 150, 110), width=6)   # 証書
    for k in range(6):
        d.line([(740, 280 + k * 45), (960, 280 + k * 45)], fill=(160, 160, 160), width=3)
    d.ellipse([900, 500, 970, 570], outline=(200, 40, 40), width=6)            # 印
    _pen(d, 1040, 420, 160, body=(40, 60, 120))
    d.line([(1030, 340), (1240, 500)], fill=(200, 40, 40), width=14)            # ばつ
    d.line([(1240, 340), (1030, 500)], fill=(200, 40, 40), width=14)
    return img


def gendai():
    """温度で色が変わる技術の今。温度を知らせるラベルと、消せるコピー用紙。"""
    img = _rgb(base((236, 236, 232), (216, 216, 212)))
    wood_floor(img, FLOOR, col=(150, 140, 130), line=(130, 122, 114))
    d = _d(img)
    d.rectangle([700, 420, 1000, 800], fill=(200, 204, 210), outline=(120, 124, 130), width=4)   # 複合機
    d.rectangle([720, 380, 980, 430], fill=(230, 232, 236))
    d.rectangle([740, 460, 960, 520], fill=(80, 90, 110))
    d.rectangle([1060, 520, 1220, 660], fill=(200, 160, 110), outline=(150, 116, 76), width=4)   # 荷物
    for k, col in enumerate([(60, 160, 90), (240, 200, 60), (200, 60, 50)]):
        d.rectangle([1080 + k * 44, 560, 1116 + k * 44, 600], fill=col)       # 温度ラベル
    return img


def gendai2():
    """今の筆記具の売り場。色とりどりのペンと手帳。"""
    img = _rgb(base((244, 242, 238), (226, 224, 220)))
    wood_floor(img, FLOOR, col=(170, 150, 130), line=(150, 132, 114))
    d = _d(img)
    _table(d, 700, 1220, 640, col=(180, 150, 120))
    cols = [(40, 60, 120), (200, 60, 60), (40, 130, 80), (230, 150, 60), (140, 80, 170), (60, 60, 66)]
    for k, c in enumerate(cols):
        _pen(d, 760, 360 + k * 40, 220, body=c, w=18)
    d.rectangle([1040, 520, 1200, 640], fill=(120, 40, 50), outline=(80, 20, 30), width=4)       # 手帳
    d.rectangle([1060, 540, 1180, 620], outline=(230, 200, 150), width=2)
    return img


LOCATIONS = {
    "fx_heya": heya, "fx_heya2": heya2, "fx_kombinat": kombinat, "fx_daigaku": daigaku,
    "fx_kenkyu": kenkyu, "fx_kenkyu2": kenkyu2, "fx_kouyou": kouyou, "fx_kaigi": kaigi,
    "fx_shouhin": shouhin, "fx_shouhin2": shouhin2, "fx_zukai1": zukai1, "fx_zukai0": zukai0, "fx_office": office,
    "fx_zukai3": zukai3, "fx_fuyajo": fuyajo, "fx_france": france, "fx_bunguten": bunguten,
    "fx_zukai2": zukai2, "fx_ronsou": ronsou, "fx_gendai": gendai, "fx_gendai2": gendai2,
}

CARDS = ["1966", "1970", "1976", "2002", "2006", "2007"]


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
        if only and f"fx_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"fx_card_{y}.png")
        print(f"生成完了: fx_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
