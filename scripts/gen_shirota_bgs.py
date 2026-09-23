#!/usr/bin/env python3
"""ヤクルトの誕生・代田稔回（50_ヤクルトの誕生 / slug=yakult-shirota）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針は蚊取り線香回（gen_katori_bgs.py）と同じ。
実在メーカーの商標（ロゴ・文字・容器の立体商標そのままの形）は描かない。
小瓶は胴にくびれの無い汎用の形で描く。

実行: PYTHONPATH=. python scripts/gen_shirota_bgs.py [名前...]
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


def _bottle(d, x, y, s=1.0, body=(236, 226, 196), cap=(200, 60, 50)):
    """汎用の小瓶（下端中央が x, y）。"""
    w, h = 26 * s, 64 * s
    d.rounded_rectangle([x - w / 2, y - h, x + w / 2, y], radius=8 * s, fill=body,
                        outline=(150, 140, 120), width=max(1, int(2 * s)))
    d.rectangle([x - w / 2 + 3 * s, y - h - 10 * s, x + w / 2 - 3 * s, y - h + 4 * s], fill=cap)


def _big_bottle(d, x, y, s=1.0, col=(180, 200, 190)):
    """ガラスの大瓶（720ml の希釈用瓶のイメージ）。"""
    d.rounded_rectangle([x - 34 * s, y - 150 * s, x + 34 * s, y], radius=14 * s, fill=col,
                        outline=(110, 130, 120), width=3)
    d.rectangle([x - 12 * s, y - 196 * s, x + 12 * s, y - 146 * s], fill=col,
                outline=(110, 130, 120), width=3)
    d.rectangle([x - 14 * s, y - 206 * s, x + 14 * s, y - 192 * s], fill=(120, 96, 70))


def _mountains(d, y, col, peaks):
    pts = [(0, H)]
    for x, py in peaks:
        pts.append((x, py))
    pts += [(W, y), (W, H)]
    d.polygon(pts, fill=col)


# ------------------------------------------------------------ 現代
def ima():
    """現代の台所。開いた冷蔵庫に小瓶が並ぶ。"""
    img = base((236, 232, 222), (214, 208, 196))
    d = _d(img)
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    d.rectangle([0, 560, 760, 660], fill=(200, 196, 186))                # 調理台
    d.rectangle([0, 660, 760, FLOOR], fill=(150, 130, 108))
    _window(d, 140, 170, 560, 470, sky=(176, 210, 232))
    d.rectangle([1240, 150, 1720, FLOOR], fill=(226, 230, 232), outline=(170, 176, 180), width=6)
    d.rectangle([1270, 190, 1690, 880], fill=(246, 250, 252))           # 冷蔵庫の中
    _glow(img, 1480, 420, 260, (230, 244, 255), 90)
    d = _d(img)
    for y in (400, 600, 800):
        d.rectangle([1270, y, 1690, y + 8], fill=(200, 208, 214))
    for k in range(10):                                                  # 小瓶10本
        _bottle(d, 1300 + k * 38, 596, 0.9)
    d.rectangle([1290, 700, 1400, 798], fill=(240, 236, 220))           # 牛乳パック
    d.rectangle([1500, 330, 1670, 398], fill=(250, 210, 140))
    return img


# ------------------------------------------------------------ 長野・少年期
def ie():
    """明治の農家の座敷。蚕を飼う棚と、紙の束。"""
    img = base((206, 190, 162), (172, 154, 128))
    d = _d(img)
    tatami_floor(img, FLOOR)
    for y in (230, 350, 470, 590, 710):                                  # 蚕棚（左）
        d.rectangle([80, y, 760, y + 16], fill=(120, 96, 70))
        d.rectangle([100, y - 60, 740, y], fill=(214, 204, 180), outline=(150, 126, 96), width=3)
        for x in range(120, 730, 34):
            d.ellipse([x, y - 34, x + 18, y - 22], fill=(248, 246, 238))
    d.rectangle([1260, 520, 1780, 700], fill=(110, 84, 58))             # 紙の束（右）
    for k in range(6):
        d.rectangle([1290 + k * 80, 440 - (k % 2) * 30, 1360 + k * 80, 520], fill=(240, 234, 214),
                    outline=(170, 156, 130), width=3)
        d.line([(1325 + k * 80, 440 - (k % 2) * 30), (1325 + k * 80, 520)], fill=(170, 90, 60), width=4)
    hanging_bulb(img, 1000, warm=True, ly=40)
    return img


def mura():
    """長野の山あいの村。桑畑と、かやぶきの家。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (166, 196, 222), (206, 214, 206)), (0, 0))
    d = _d(img)
    _mountains(d, 360, (120, 140, 150), [(0, 380), (300, 200), (640, 330), (980, 170), (1400, 320), (1700, 210)])
    _mountains(d, 470, (96, 128, 96), [(0, 480), (420, 380), (900, 470), (1300, 360), (1920, 450)])
    d.rectangle([0, 560, W, H], fill=(142, 152, 100))
    for row, y in enumerate(range(600, H, 70)):                          # 桑畑の畝
        r = 16 + row * 5
        for x in range(40 + (row % 2) * 60, W, 130 + row * 10):
            d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(78, 118, 66))
    for x0 in (1320, 1600):                                              # かやぶき屋根
        d.rectangle([x0, 470, x0 + 220, 580], fill=(120, 96, 72))
        d.polygon([(x0 - 40, 480), (x0 + 110, 380), (x0 + 260, 480)], fill=(150, 126, 84))
    return img


def michi():
    """山あいの道。中学へ通う道。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (172, 204, 228), (214, 220, 204)), (0, 0))
    d = _d(img)
    _mountains(d, 380, (116, 136, 148), [(0, 400), (360, 230), (760, 360), (1160, 200), (1600, 330), (1920, 260)])
    d.rectangle([0, 520, W, H], fill=(110, 140, 90))
    d.polygon([(860, 520), (1060, 520), (1500, H), (420, H)], fill=(186, 166, 126))   # 道
    for x in (160, 360, 1620, 1800):                                      # 木
        d.rectangle([x - 12, 420, x + 12, 620], fill=(96, 74, 52))
        d.ellipse([x - 90, 300, x + 90, 470], fill=(70, 110, 64))
    return img


# ------------------------------------------------------------ 京都帝大
def kyoshitsu():
    """大学の微生物学の研究室。棚にフラスコ、机に顕微鏡。"""
    img = base((218, 214, 200), (186, 180, 164))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 94, 70), line=(100, 78, 58))
    _window(d, 700, 150, 1220, 520, sky=(184, 206, 222))
    for y in (250, 400):                                                 # 棚（左）
        d.rectangle([60, y, 560, y + 14], fill=(110, 88, 64))
        for x in range(90, 540, 70):
            d.ellipse([x, y - 60, x + 44, y], fill=(200, 222, 214), outline=(130, 150, 146), width=3)
            d.rectangle([x + 14, y - 90, x + 30, y - 56], fill=(200, 222, 214), outline=(130, 150, 146), width=3)
    d.rectangle([1320, 620, 1860, 660], fill=(140, 108, 76))             # 実験台（右）
    d.rectangle([1340, 660, 1370, FLOOR], fill=(110, 84, 60))
    d.rectangle([1810, 660, 1840, FLOOR], fill=(110, 84, 60))
    d.rectangle([1500, 560, 1560, 620], fill=(60, 64, 70))              # 顕微鏡
    d.rectangle([1520, 460, 1545, 560], fill=(60, 64, 70))
    d.line([(1532, 470), (1600, 420)], fill=(60, 64, 70), width=16)
    hanging_bulb(img, 960, warm=False, ly=40)
    return img


def baichi():
    """夜の実験台。並んだ培養皿と、ランプの明かり。"""
    img = base((70, 72, 84), (46, 48, 58))
    d = _d(img)
    d.rectangle([0, 640, W, 700], fill=(120, 100, 80))                   # 実験台の天板
    d.rectangle([0, 700, W, H], fill=(76, 66, 58))
    for row in range(3):                                                 # 培養皿
        for k in range(9):
            x = 520 + k * 110 - row * 30
            y = 600 + row * 26
            d.ellipse([x - 44, y - 16, x + 44, y + 16], fill=(214, 220, 214), outline=(160, 170, 166), width=3)
            if (k + row) % 4 == 0:
                d.ellipse([x - 14, y - 6, x + 14, y + 6], fill=(236, 214, 150))
    d.rectangle([80, 300, 380, 640], fill=(150, 156, 160), outline=(100, 104, 108), width=6)   # 培養器
    d.rectangle([110, 340, 350, 600], fill=(120, 126, 130))
    d.rectangle([1560, 420, 1590, 640], fill=(60, 60, 64))              # 卓上ランプ
    d.polygon([(1500, 420), (1650, 420), (1610, 360), (1540, 360)], fill=(200, 160, 80))
    _glow(img, 1575, 470, 260, (255, 214, 140), 90)
    return img


def chou():
    """図解用。暗い地に胃と腸の形。仕組みの章で使う。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (34, 38, 50), (20, 22, 30)), (0, 0))
    d = _d(img)
    d.line([(960, 60), (960, 200)], fill=(170, 120, 110), width=30)       # 食道
    d.ellipse([820, 180, 1140, 420], fill=(196, 110, 100))               # 胃
    d.ellipse([870, 230, 1090, 380], fill=(236, 206, 90))                # 胃液
    d.line([(1100, 360), (1180, 470), (1060, 520)], fill=(176, 120, 104), width=34, joint="curve")  # 十二指腸
    d.ellipse([1180, 400, 1250, 460], fill=(120, 160, 70))               # 胆汁
    pts = []                                                             # 小腸
    for i in range(260):
        t = i / 259
        a = t * 7 * math.pi
        pts.append((960 + 170 * math.sin(a) * (1 - 0.25 * t), 560 + t * 360))
    d.line(pts, fill=(210, 150, 130), width=26, joint="curve")
    return img


# ------------------------------------------------------------ 福岡・1935
def tonin():
    """1935年、福岡の小さな工場。大瓶と仕込みの樽。"""
    img = base((212, 200, 180), (178, 166, 146))
    d = _d(img)
    wood_floor(img, FLOOR, col=(126, 96, 68), line=(104, 80, 56))
    for y in (360, 560):                                                 # 大瓶の棚（左）
        d.rectangle([60, y, 820, y + 16], fill=(112, 88, 62))
        for x in range(120, 800, 110):
            _big_bottle(d, x, y, 0.8)
    for x in (1300, 1600):                                               # 仕込みの樽（右）
        d.rectangle([x, 520, x + 220, FLOOR - 20], fill=(150, 112, 74), outline=(100, 76, 50), width=6)
        for yy in (560, 700, 840):
            d.line([(x, yy), (x + 220, yy)], fill=(90, 70, 50), width=8)
    hanging_bulb(img, 1040, warm=True, ly=40)
    return img


def hanbai():
    """販売店の棚。ビール瓶・牛乳瓶・小さな薬瓶まで混ざって並ぶ。"""
    img = base((226, 214, 190), (194, 180, 156))
    d = _d(img)
    wood_floor(img, FLOOR, col=(128, 98, 68), line=(106, 80, 54))
    d.rectangle([0, 100, W, 230], fill=(70, 90, 80))                      # のれん
    for x in range(140, W, 280):
        d.line([(x, 100), (x, 230)], fill=(52, 68, 60), width=6)
    for sy in (460, 660):
        d.rectangle([80, sy, 900, sy + 18], fill=(112, 88, 64))
        x = 110
        k = 0
        while x < 880:
            kind = k % 3
            if kind == 0:                                                # ビール瓶
                d.rectangle([x, sy - 130, x + 34, sy], fill=(110, 70, 36))
                d.rectangle([x + 10, sy - 175, x + 24, sy - 128], fill=(110, 70, 36))
                x += 60
            elif kind == 1:                                              # 牛乳瓶
                d.rounded_rectangle([x, sy - 90, x + 44, sy], radius=10, fill=(236, 236, 230),
                                    outline=(160, 160, 150), width=3)
                x += 66
            else:                                                        # 薬瓶
                for j in range(3):
                    d.rectangle([x + j * 22, sy - 44, x + j * 22 + 16, sy], fill=(170, 130, 70))
                x += 80
            k += 1
    d.rectangle([1160, 650, 1820, 700], fill=(150, 118, 84))              # 帳場
    return img


# ------------------------------------------------------------ 戦中・戦後
def senji():
    """戦時中の暗い工場。空の牛乳缶と、目張りした窓。"""
    img = base((88, 84, 80), (60, 58, 56))
    d = _d(img)
    wood_floor(img, FLOOR, col=(80, 66, 54), line=(64, 54, 44))
    for x0 in (140, 620):                                                # 目張りの窓
        d.rectangle([x0, 170, x0 + 360, 470], fill=(50, 52, 58), outline=(40, 36, 34), width=10)
        d.line([(x0, 170), (x0 + 360, 470)], fill=(220, 214, 196), width=10)
        d.line([(x0 + 360, 170), (x0, 470)], fill=(220, 214, 196), width=10)
    for k in range(6):                                                   # 空の牛乳缶
        x = 1180 + (k % 3) * 200
        y = FLOOR - (k // 3) * 10
        d.rectangle([x, y - 200, x + 130, y], fill=(150, 150, 146), outline=(100, 100, 98), width=5)
        d.rectangle([x + 30, y - 236, x + 100, y - 198], fill=(150, 150, 146), outline=(100, 100, 98), width=5)
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def omuta():
    """戦後に立て直した明るい工場。銀色のタンク。"""
    img = base((222, 226, 226), (190, 196, 196))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 150, 146), line=(130, 130, 126))
    for x0 in (120, 560):
        _window(d, x0, 140, x0 + 360, 440, sky=(186, 214, 236), frame=(120, 124, 128))
    for x in (1160, 1480):                                               # タンク
        d.rounded_rectangle([x, 300, x + 260, FLOOR - 30], radius=60, fill=(200, 206, 210),
                            outline=(140, 146, 150), width=6)
        d.rectangle([x + 110, 250, x + 150, 300], fill=(160, 166, 170))
    d.line([(1290, 260), (1610, 260)], fill=(150, 156, 160), width=14)
    return img


# ------------------------------------------------------------ 本社・1955〜
def honsha():
    """1955年の本社の事務所。机と、窓の外のビル。"""
    img = base((226, 222, 210), (196, 190, 176))
    d = _d(img)
    wood_floor(img, FLOOR, col=(132, 104, 76), line=(112, 88, 64))
    d.rectangle([600, 140, 1320, 520], fill=(170, 196, 216), outline=(90, 84, 78), width=12)
    for k, (bx, bh) in enumerate(((640, 200), (760, 280), (900, 180), (1040, 300), (1180, 220))):
        d.rectangle([bx, 520 - bh, bx + 110, 520], fill=(140 + k * 6, 146 + k * 6, 156 + k * 6))
    d.line([(960, 140), (960, 520)], fill=(90, 84, 78), width=10)
    for x in (120, 1440):                                                # 机
        d.rectangle([x, 660, x + 400, 700], fill=(120, 90, 62))
        d.rectangle([x + 20, 700, x + 50, FLOOR], fill=(100, 76, 52))
        d.rectangle([x + 350, 700, x + 380, FLOOR], fill=(100, 76, 52))
        d.rectangle([x + 60, 620, x + 200, 660], fill=(240, 236, 222))
    return img


def kaigi():
    """1960年代の会議室。長机と黒板。"""
    img = base((220, 216, 204), (190, 184, 170))
    d = _d(img)
    wood_floor(img, FLOOR, col=(126, 100, 74), line=(106, 84, 62))
    d.rectangle([560, 150, 1360, 480], fill=(54, 70, 62), outline=(110, 90, 66), width=14)
    for y in (230, 300, 370):
        d.line([(640, y), (1180, y)], fill=(210, 216, 210), width=4)
    d.rectangle([200, 700, 1720, 750], fill=(140, 108, 76))              # 長机
    for x in range(260, 1700, 240):
        d.rectangle([x, 620, x + 90, 700], fill=(96, 110, 120))
    return img


def danchi():
    """1960年代の団地。配達の場面。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 204, 230), (218, 222, 214)), (0, 0))
    d = _d(img)
    d.rectangle([0, 200, W, 760], fill=(212, 208, 196))                  # 棟
    for y in (200, 390, 580):
        d.rectangle([0, y, W, y + 18], fill=(170, 166, 156))
        for x in range(80, W, 240):
            d.rectangle([x, y + 50, x + 110, y + 170], fill=(116, 134, 150))    # ドア
            d.rectangle([x + 140, y + 70, x + 200, y + 130], fill=(170, 200, 222))  # 小窓
    d.rectangle([0, 760, W, H], fill=(170, 164, 150))
    return img


def youki():
    """容器をデザインする机。壁に瓶の輪郭の図面。"""
    img = base((232, 230, 222), (204, 200, 190))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 124, 94), line=(128, 106, 80))
    for k in range(5):                                                   # 壁の図面
        x0 = 120 + k * 330
        d.rectangle([x0, 150, x0 + 260, 470], fill=(246, 246, 240), outline=(170, 170, 160), width=4)
        cx, top, bot = x0 + 130, 200, 430
        waist = 22 + k * 6
        d.line([(cx - 50, bot), (cx - 50, 330), (cx - waist, 290), (cx - 44, 240), (cx - 30, top)],
               fill=(70, 90, 140), width=4)
        d.line([(cx + 50, bot), (cx + 50, 330), (cx + waist, 290), (cx + 44, 240), (cx + 30, top)],
               fill=(70, 90, 140), width=4)
        d.line([(cx - 50, bot), (cx + 50, bot)], fill=(70, 90, 140), width=4)
    d.polygon([(560, 640), (1360, 640), (1300, 720), (620, 720)], fill=(170, 150, 120))   # 製図台
    d.rectangle([640, 720, 670, FLOOR], fill=(110, 90, 66))
    d.rectangle([1250, 720, 1280, FLOOR], fill=(110, 90, 66))
    return img


def genkan():
    """古い家の玄関先。一人暮らしのお年寄りの家。"""
    img = base((214, 204, 184), (182, 170, 150))
    d = _d(img)
    d.rectangle([0, FLOOR - 60, W, H], fill=(150, 146, 136))             # 土間
    d.rectangle([520, 150, 1400, FLOOR - 60], fill=(120, 96, 70))        # 引き戸の枠
    for x0 in (560, 980):
        d.rectangle([x0, 190, x0 + 380, FLOOR - 70], fill=(226, 218, 196), outline=(96, 76, 56), width=8)
        for gy in range(250, FLOOR - 70, 90):
            d.line([(x0, gy), (x0 + 380, gy)], fill=(160, 140, 110), width=4)
    d.rectangle([1540, 700, 1640, FLOOR - 60], fill=(150, 110, 80))      # 植木鉢
    d.ellipse([1480, 560, 1700, 720], fill=(90, 130, 80))
    d.rectangle([200, 820, 420, 860], fill=(176, 170, 160))              # 踏み石
    return img


def enkai():
    """慰労会の広間。長い座卓と座布団。"""
    img = base((214, 196, 166), (182, 162, 132))
    d = _d(img)
    tatami_floor(img, int(H * 0.62))
    d.rectangle([300, 120, 1620, 210], fill=(180, 60, 50))                # 横断幕（文字なし）
    for y in (700, 900):                                                 # 座卓と座布団
        d.rectangle([200, y, 1720, y + 40], fill=(120, 80, 50))
        for x in range(240, 1700, 180):
            d.rounded_rectangle([x, y + 50, x + 110, y + 80], radius=10, fill=(170, 70, 70))
            d.ellipse([x + 30, y - 20, x + 60, y], fill=(236, 230, 214))
    for x in (160, 1760):
        _glow(img, x, 300, 120, (255, 220, 150), 90)
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


def sekai():
    """暗い地に世界地図の点。現代の広がりの章で使う。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (24, 40, 66), (14, 24, 42)), (0, 0))
    d = _d(img)
    lands = [(330, 330, 300, 170), (470, 700, 130, 190), (960, 330, 140, 110),
             (1010, 620, 160, 210), (1330, 360, 330, 180), (1500, 640, 90, 60),
             (1620, 780, 150, 90), (1590, 400, 30, 60)]
    for y in range(120, 980, 26):
        for x in range(60, 1880, 26):
            for cx, cy, rx, ry in lands:
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1:
                    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(90, 150, 200))
                    break
    for cx, cy in ((1590, 420), (1560, 610), (1450, 520), (470, 560), (1030, 330), (1500, 380)):
        _glow(img, cx, cy, 60, (255, 210, 120), 150)
    return img


LOCATIONS = {
    "sr_ima": ima, "sr_ie": ie, "sr_mura": mura, "sr_michi": michi,
    "sr_kyoshitsu": kyoshitsu, "sr_baichi": baichi, "sr_chou": chou,
    "sr_tonin": tonin, "sr_hanbai": hanbai, "sr_senji": senji, "sr_omuta": omuta,
    "sr_honsha": honsha, "sr_kaigi": kaigi, "sr_danchi": danchi, "sr_youki": youki,
    "sr_genkan": genkan, "sr_enkai": enkai, "sr_shiryo": shiryo, "sr_sekai": sekai,
}

CARDS = ["1899", "1921", "1930", "1935", "1941", "1955", "1963", "1968"]


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
        if only and f"sr_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"sr_card_{y}.png")
        print(f"生成完了: sr_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
