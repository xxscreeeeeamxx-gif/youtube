#!/usr/bin/env python3
"""グリコの誕生・江崎利一回（51_グリコの誕生 / slug=glico-ezaki）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針は蚊取り線香回（gen_katori_bgs.py）と同じ。
実在メーカーの商標（ゴールインマーク・ロゴ・箱の意匠）は描かない。
道頓堀の看板も、走る人の絵は描かずに光の枠だけにする。

実行: PYTHONPATH=. python scripts/gen_glico_bgs.py [名前...]
"""

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


def _redbox(d, x, y, s=1.0):
    """赤い小箱（文字や絵は入れない）。下端中央が x, y。"""
    d.rectangle([x - 40 * s, y - 70 * s, x + 40 * s, y], fill=(206, 40, 44), outline=(140, 24, 28), width=3)
    d.rectangle([x - 40 * s, y - 70 * s, x + 40 * s, y - 56 * s], fill=(236, 200, 60))


def _drawers(d, x0, y0, cols, rows, cw=90, ch=60, col=(120, 86, 56)):
    """薬箪笥の引き出し。"""
    d.rectangle([x0, y0, x0 + cols * cw, y0 + rows * ch], fill=col, outline=(80, 56, 36), width=6)
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * cw, y0 + r * ch
            d.rectangle([x + 6, y + 6, x + cw - 6, y + ch - 6], outline=(86, 60, 40), width=3)
            d.ellipse([x + cw / 2 - 5, y + ch / 2 - 5, x + cw / 2 + 5, y + ch / 2 + 5], fill=(200, 170, 90))


# ------------------------------------------------------------ 現代
def ima():
    """現代の居間。卓の上に赤い小箱と、おもちゃの小箱。"""
    img = base((236, 230, 218), (212, 204, 190))
    d = _d(img)
    wood_floor(img, FLOOR, col=(176, 144, 108), line=(154, 126, 94))
    _window(d, 700, 150, 1220, 520, sky=(180, 212, 234))
    d.rectangle([520, 700, 1400, 740], fill=(150, 112, 78))             # 座卓
    d.rectangle([560, 740, 600, FLOOR], fill=(120, 90, 62))
    d.rectangle([1320, 740, 1360, FLOOR], fill=(120, 90, 62))
    for k in range(3):
        _redbox(d, 820 + k * 110, 700, 0.9)
    d.rectangle([1150, 650, 1230, 700], fill=(246, 240, 220), outline=(180, 170, 150), width=3)
    return img


# ------------------------------------------------------------ 佐賀・少年期
def ie():
    """明治の貧しい薬屋の座敷。薬箪笥と土間。"""
    img = base((200, 184, 158), (168, 150, 124))
    d = _d(img)
    tatami_floor(img, FLOOR)
    _drawers(d, 90, 230, 6, 6)
    d.rectangle([1300, 330, 1780, 620], fill=(222, 212, 190), outline=(110, 90, 70), width=8)
    for gx in range(1380, 1780, 100):
        d.line([(gx, 330), (gx, 620)], fill=(170, 150, 124), width=4)
    d.rectangle([1360, 700, 1560, 760], fill=(160, 130, 90))            # 行商の荷
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def ie_yoru():
    """夜の座敷。布団と行灯。病の場面。"""
    img = base((96, 84, 72), (60, 52, 46))
    d = _d(img)
    tatami_floor(img, FLOOR)
    d.rectangle([380, 170, 1160, 600], fill=(170, 156, 130), outline=(90, 74, 58), width=10)
    d.rounded_rectangle([600, 760, 1320, 900], radius=30, fill=(214, 206, 196))   # 布団
    d.rectangle([640, 740, 780, 790], fill=(236, 232, 224))
    d.rectangle([1480, 560, 1580, 740], fill=(236, 214, 150), outline=(120, 96, 64), width=6)  # 行灯
    _glow(img, 1530, 650, 200, (255, 206, 130), 90)
    return img


def machi():
    """夜明けの村の通り。塩売りの場面。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (236, 190, 150), (206, 206, 214)), (0, 0))
    d = _d(img)
    _glow(img, 1500, 480, 200, (255, 214, 150), 120)
    d = _d(img)
    for x0, h in ((0, 260), (330, 300), (1180, 280), (1520, 320)):      # 家並み
        d.rectangle([x0, 640 - h, x0 + 300, 640], fill=(96, 84, 76))
        d.polygon([(x0 - 30, 660 - h), (x0 + 150, 560 - h), (x0 + 330, 660 - h)], fill=(70, 62, 58))
    d.rectangle([0, 640, W, H], fill=(170, 150, 120))                    # 道
    return img


def juku():
    """明治の学校の教室。低い机と黒板。"""
    img = base((214, 204, 184), (184, 172, 150))
    d = _d(img)
    wood_floor(img, FLOOR, col=(128, 98, 70), line=(108, 82, 58))
    d.rectangle([560, 170, 1360, 480], fill=(52, 66, 58), outline=(110, 88, 64), width=14)
    _window(d, 100, 170, 440, 480, sky=(186, 208, 224))
    _window(d, 1480, 170, 1820, 480, sky=(186, 208, 224))
    for x in range(180, 1780, 300):
        d.rectangle([x, 760, x + 200, 790], fill=(140, 108, 76))
    return img


def mise():
    """ぶどう酒と薬の店。樽と瓶。"""
    img = base((218, 204, 180), (186, 170, 146))
    d = _d(img)
    wood_floor(img, FLOOR, col=(126, 96, 68), line=(104, 80, 56))
    for x in (120, 380, 640):                                            # 樽
        d.ellipse([x, 540, x + 220, FLOOR - 10], fill=(150, 104, 64), outline=(96, 66, 40), width=6)
        for yy in (600, 700, 800):
            d.line([(x + 10, yy), (x + 210, yy)], fill=(90, 64, 40), width=6)
    for sy in (300, 460):                                                # 瓶の棚
        d.rectangle([1140, sy, 1820, sy + 16], fill=(112, 88, 62))
        for x in range(1170, 1800, 60):
            d.rectangle([x, sy - 100, x + 30, sy], fill=(90, 50, 60))
            d.rectangle([x + 9, sy - 130, x + 21, sy - 98], fill=(90, 50, 60))
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def kawara():
    """有明海にそそぐ川の河原。牡蠣を煮る小屋と大釜。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (190, 208, 222), (214, 214, 204)), (0, 0))
    d = _d(img)
    d.rectangle([0, 470, W, 640], fill=(130, 150, 150))                  # 川
    for x in range(0, W, 140):
        d.line([(x, 520), (x + 80, 520)], fill=(170, 186, 186), width=4)
    d.rectangle([0, 640, W, H], fill=(176, 162, 128))                    # 河原
    d.rectangle([1150, 380, 1760, 700], fill=(120, 98, 70))              # 小屋
    d.polygon([(1100, 400), (1455, 270), (1810, 400)], fill=(96, 80, 60))
    d.ellipse([1300, 640, 1560, 760], fill=(60, 58, 56))                 # 大釜
    d.ellipse([1320, 640, 1540, 690], fill=(120, 110, 90))
    for k in range(3):                                                   # 湯気
        _glow(img, 1400 + k * 60, 560 - k * 40, 60, (250, 250, 250), 120)
    d = _d(img)
    for x in range(80, 700, 70):                                         # 葦
        d.line([(x, 640), (x - 10, 520)], fill=(120, 130, 80), width=5)
    return img


def zukai():
    """図解用。暗い地に、枝分かれしてつながった粒（グリコーゲンの形）。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (34, 40, 52), (20, 22, 30)), (0, 0))
    d = _d(img)

    beads = []

    def chain(x, y, dx, dy, n):
        pts = [(x + dx * i, y + dy * i) for i in range(n)]
        for a, b in zip(pts, pts[1:]):
            d.line([a, b], fill=(120, 150, 190), width=6)
        beads.extend(pts)
        return pts

    trunk = chain(600, 560, 40, 0, 19)                                   # 幹
    for k, i in enumerate(range(3, 19, 4)):                              # 枝（上下交互に斜め）
        sign = -1 if k % 2 == 0 else 1
        px, py = trunk[i]
        br = chain(px, py, 26, 30 * sign, 7)
        qx, qy = br[3]
        chain(qx, qy, 34, 12 * sign, 4)                                  # 枝の枝
    for px, py in beads:
        d.ellipse([px - 13, py - 13, px + 13, py + 13], fill=(236, 206, 90))
    return img


# ------------------------------------------------------------ 大阪
def koba():
    """1920年代のキャラメル工場。煮詰める鍋と、赤い箱の山。"""
    img = base((214, 204, 186), (180, 168, 150))
    d = _d(img)
    wood_floor(img, FLOOR, col=(124, 98, 72), line=(104, 82, 60))
    d.ellipse([160, 520, 520, 640], fill=(150, 150, 150))                # 大鍋
    d.rectangle([180, 580, 500, 760], fill=(140, 140, 140))
    d.rectangle([200, 760, 480, FLOOR], fill=(90, 80, 70))
    d.rectangle([640, 640, 1160, 690], fill=(170, 150, 120))             # 冷やし台
    d.rectangle([660, 690, 690, FLOOR], fill=(110, 90, 66))
    d.rectangle([1110, 690, 1140, FLOOR], fill=(110, 90, 66))
    for row in range(4):                                                 # 箱の山
        for k in range(5 - row):
            _redbox(d, 1350 + k * 90 + row * 45, FLOOR - 10 - row * 74, 1.0)
    hanging_bulb(img, 900, warm=True, ly=40)
    return img


def jinja():
    """故郷の神社の境内。かけっこの場面。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (172, 204, 228), (214, 220, 208)), (0, 0))
    d = _d(img)
    for x in (100, 300, 1620, 1820):                                     # 杉
        d.rectangle([x - 14, 260, x + 14, 700], fill=(96, 72, 50))
        d.polygon([(x - 110, 520), (x, 140), (x + 110, 520)], fill=(64, 104, 66))
    d.rectangle([0, 660, W, H], fill=(200, 184, 150))                    # 境内
    d.rectangle([760, 250, 790, 660], fill=(190, 60, 44))                # 鳥居
    d.rectangle([1130, 250, 1160, 660], fill=(190, 60, 44))
    d.rectangle([700, 230, 1220, 262], fill=(190, 60, 44))
    d.rectangle([740, 300, 1180, 322], fill=(190, 60, 44))
    d.line([(420, 900), (1500, 900)], fill=(250, 250, 250), width=6)     # ゴールの線
    return img


def depart():
    """大正の百貨店の売り場。ガラスの陳列台と柱。"""
    img = base((232, 222, 200), (206, 194, 170))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 116, 80), line=(128, 98, 68))
    for x in (160, 1700):                                                # 柱
        d.rectangle([x, 100, x + 90, FLOOR], fill=(214, 200, 170), outline=(170, 150, 120), width=4)
    for x0 in (360, 1160):                                               # 陳列台
        d.rectangle([x0, 620, x0 + 420, 760], fill=(130, 96, 64))
        d.rectangle([x0, 520, x0 + 420, 620], fill=(206, 226, 226), outline=(150, 170, 170), width=4)
        for k in range(4):
            _redbox(d, x0 + 70 + k * 95, 612, 0.7)
    for x in (560, 1360):                                                # 照明
        _glow(img, x, 120, 90, (255, 236, 190), 120)
    return img


def tonya():
    """菓子の問屋の倉庫。積み上がった木箱。"""
    img = base((196, 184, 164), (164, 150, 130))
    d = _d(img)
    wood_floor(img, FLOOR, col=(118, 92, 66), line=(98, 76, 54))
    for col in range(5):
        for row in range(5):
            x, y = 80 + col * 170, FLOOR - (row + 1) * 110
            d.rectangle([x, y, x + 160, y + 104], fill=(170, 136, 96), outline=(110, 84, 58), width=5)
    d.rectangle([1200, 640, 1800, 690], fill=(150, 116, 84))             # 帳場
    return img


def mise_osaka():
    """大阪の菓子屋の店先。ガラス瓶と赤い小箱。"""
    img = base((230, 216, 192), (198, 182, 158))
    d = _d(img)
    wood_floor(img, FLOOR, col=(130, 98, 68), line=(108, 80, 54))
    d.rectangle([0, 100, W, 220], fill=(160, 60, 50))                    # のれん
    for x in range(160, W, 300):
        d.line([(x, 100), (x, 220)], fill=(120, 40, 34), width=6)
    d.rectangle([100, 600, 900, 640], fill=(120, 90, 62))                # 陳列台
    for k in range(5):
        x = 160 + k * 150
        d.rounded_rectangle([x, 470, x + 100, 600], radius=20, fill=(214, 230, 230), outline=(150, 170, 170), width=4)
        d.rectangle([x + 10, 450, x + 90, 474], fill=(200, 170, 120))
    for k in range(6):
        _redbox(d, 1220 + k * 95, 640, 0.9)
    d.rectangle([1160, 640, 1800, 680], fill=(120, 90, 62))
    return img


def dotonbori():
    """夜の道頓堀。川面に映る光の看板（絵柄は描かない）。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (20, 22, 44), (40, 34, 60)), (0, 0))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(24, 30, 50))                        # 川
    for x0, h in ((0, 380), (260, 300), (1480, 340), (1720, 400)):      # ビル
        d.rectangle([x0, 700 - h, x0 + 240, 700], fill=(34, 36, 56))
    d.rectangle([760, 90, 1160, 640], fill=(30, 30, 44), outline=(90, 90, 110), width=6)   # 看板の枠
    cols = [(255, 80, 80), (255, 200, 60), (80, 220, 120), (80, 160, 255), (220, 100, 255), (255, 255, 255)]
    for i, y in enumerate(range(130, 620, 60)):
        for j, x in enumerate(range(800, 1130, 60)):
            c = cols[(i + j) % len(cols)]
            d.ellipse([x, y, x + 26, y + 26], fill=c)
    _glow(img, 960, 360, 360, (255, 170, 120), 60)
    d = _d(img)
    for k in range(10):                                                  # 川面の反射
        y = 730 + k * 30
        d.line([(820 + (k % 3) * 20, y), (1100 - (k % 2) * 30, y)], fill=(200, 140, 120), width=4)
    return img


def yakeato():
    """空襲で焼けた工場の跡。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (150, 146, 140), (110, 104, 98)), (0, 0))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(84, 78, 72))
    for x, h, ang in ((200, 380, 10), (520, 300, -12), (1300, 420, 6), (1640, 260, -8)):   # 焼けた柱
        d.polygon([(x, 700), (x + 40, 700), (x + 40 + ang, 700 - h), (x + ang, 700 - h)], fill=(44, 38, 34))
    d.line([(160, 400), (720, 470)], fill=(50, 44, 40), width=26)        # 落ちた梁
    d.rectangle([900, 560, 1200, 700], fill=(120, 110, 96), outline=(70, 64, 58), width=6)  # 焼け残った食堂
    d.rectangle([980, 600, 1060, 700], fill=(70, 62, 56))
    return img


def kaigi():
    """1960年代の会議室。長机と黒板。"""
    img = base((220, 216, 204), (190, 184, 170))
    d = _d(img)
    wood_floor(img, FLOOR, col=(126, 100, 74), line=(106, 84, 62))
    d.rectangle([560, 150, 1360, 480], fill=(54, 70, 62), outline=(110, 90, 66), width=14)
    d.rectangle([200, 700, 1720, 750], fill=(140, 108, 76))
    for x in range(260, 1700, 240):
        d.rectangle([x, 620, x + 90, 700], fill=(96, 110, 120))
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
    img.paste(vgrad((W, H), (40, 24, 40), (22, 14, 24)), (0, 0))
    d = _d(img)
    lands = [(330, 330, 300, 170), (470, 700, 130, 190), (960, 330, 140, 110),
             (1010, 620, 160, 210), (1330, 360, 330, 180), (1500, 640, 90, 60),
             (1620, 780, 150, 90), (1590, 400, 30, 60)]
    for y in range(120, 980, 26):
        for x in range(60, 1880, 26):
            for cx, cy, rx, ry in lands:
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1:
                    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(210, 110, 110))
                    break
    for cx, cy in ((1590, 420), (1450, 520), (960, 330), (330, 330), (1560, 610)):
        _glow(img, cx, cy, 60, (255, 220, 140), 150)
    return img


def koba0():
    """箱の色を決める前の工場。赤い箱はまだ無く、木箱だけ。"""
    img = base((214, 204, 186), (180, 168, 150))
    d = _d(img)
    wood_floor(img, FLOOR, col=(124, 98, 72), line=(104, 82, 60))
    d.ellipse([160, 520, 520, 640], fill=(150, 150, 150))
    d.rectangle([180, 580, 500, 760], fill=(140, 140, 140))
    d.rectangle([200, 760, 480, FLOOR], fill=(90, 80, 70))
    d.rectangle([640, 640, 1160, 690], fill=(170, 150, 120))
    d.rectangle([660, 690, 690, FLOOR], fill=(110, 90, 66))
    d.rectangle([1110, 690, 1140, FLOOR], fill=(110, 90, 66))
    for row in range(3):
        for k in range(4 - row):
            x, y = 1360 + k * 110 + row * 55, FLOOR - 10 - row * 90
            d.rectangle([x - 50, y - 86, x + 50, y], fill=(170, 136, 96), outline=(110, 84, 58), width=4)
    hanging_bulb(img, 900, warm=True, ly=40)
    return img


def depart0():
    """グリコが並ぶ前の百貨店の売り場。陳列台には別の菓子の缶。"""
    img = base((232, 222, 200), (206, 194, 170))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 116, 80), line=(128, 98, 68))
    for x in (160, 1700):
        d.rectangle([x, 100, x + 90, FLOOR], fill=(214, 200, 170), outline=(170, 150, 120), width=4)
    for x0 in (360, 1160):
        d.rectangle([x0, 620, x0 + 420, 760], fill=(130, 96, 64))
        d.rectangle([x0, 520, x0 + 420, 620], fill=(206, 226, 226), outline=(150, 170, 170), width=4)
        for k in range(4):
            cx = x0 + 70 + k * 95
            d.ellipse([cx - 30, 560, cx + 30, 612], fill=(190, 176, 120), outline=(140, 126, 80), width=3)
    for x in (560, 1360):
        _glow(img, x, 120, 90, (255, 236, 190), 120)
    return img


def track():
    """陸上競技場のトラック。一粒300メートルの計算の章で使う。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 204, 230), (214, 222, 214)), (0, 0))
    d = _d(img)
    d.rectangle([0, 380, W, 520], fill=(120, 130, 140))                  # スタンド
    for y in range(400, 520, 24):
        d.line([(0, y), (W, y)], fill=(150, 160, 170), width=4)
    d.rectangle([0, 520, W, H], fill=(186, 84, 64))                      # トラック
    for k in range(6):
        y = 560 + k * 90
        d.line([(0, y), (W, y + k * 12)], fill=(246, 240, 230), width=5)
    d.line([(1500, 520), (1640, H)], fill=(246, 240, 230), width=10)     # ゴールライン
    return img


LOCATIONS = {
    "gl_koba0": koba0, "gl_depart0": depart0, "gl_track": track,
    "gl_ima": ima, "gl_ie": ie, "gl_ie_yoru": ie_yoru, "gl_machi": machi, "gl_juku": juku,
    "gl_mise": mise, "gl_kawara": kawara, "gl_zukai": zukai, "gl_koba": koba, "gl_jinja": jinja,
    "gl_depart": depart, "gl_tonya": tonya, "gl_mise_osaka": mise_osaka, "gl_dotonbori": dotonbori,
    "gl_yakeato": yakeato, "gl_kaigi": kaigi, "gl_shiryo": shiryo, "gl_sekai": sekai,
}

CARDS = ["1882", "1901", "1919", "1921", "1922", "1945", "1966"]


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
        if only and f"gl_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"gl_card_{y}.png")
        print(f"生成完了: gl_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
