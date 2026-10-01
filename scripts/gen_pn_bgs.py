#!/usr/bin/env python3
"""パナソニックの誕生・松下幸之助回（73_パナソニックの誕生 / slug=matsushita-socket）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はファミコン回（gen_famicom_bgs.py）と同じ。
実在の会社の商標（Panasonic・National の字体やマーク、M矢・三松葉の社章）は描かない。
看板・幕・のぼりは無地にする。二股ソケットの図は「二灯用差込みプラグ」の形を簡略化して描く。

人物が立つ下3分の1（y>720）は床・地面だけにして、小道具は画面の中ほど
（キャラの間 x700〜1250 と上半分）に置く。

実行: PYTHONPATH=. python scripts/gen_pn_bgs.py [名前...]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, glow, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)
INK = (60, 56, 52)
WOOD = (110, 80, 54)
WOOD_D = (84, 60, 40)
PLASTER = (220, 206, 180)
SOCKET = (92, 64, 44)        # 煉物のソケットの茶色
SOCKET_TOP = (226, 216, 196)


# ---------------------------------------------------------------- 基本
def _d(img):
    return ImageDraw.Draw(img, "RGBA")


def _base(top, bottom):
    return vgrad((W, H), top, bottom).convert("RGBA")


def _font(size):
    from ytf.config import Config, resolve_font
    Config.load()
    return ImageFont.truetype(resolve_font("w9"), size)


def _text_c(d, cx, y, t, size, fill):
    f = _font(size)
    bb = d.textbbox((0, 0), t, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y), t, font=f, fill=fill)


def _glow(img, cx, cy, r, color, alpha=110):
    glow(img, cx, cy, r, color, alpha)


def _shade(col, k):
    return tuple(max(0, min(255, int(c * k))) for c in col)


def _tint(img, col, alpha):
    """全体に色をかぶせる（夜・夕方の空気）。"""
    return Image.alpha_composite(img, Image.new("RGBA", img.size, (*col, alpha)))


def _vignette(img, alpha=60):
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    vd.rectangle([0, 0, W, H], fill=(8, 6, 4, alpha))
    vd.ellipse([-260, -200, W + 260, H + 300], fill=(0, 0, 0, 0))
    return Image.alpha_composite(img, vig.filter(ImageFilter.GaussianBlur(150)))


# ---------------------------------------------------------------- 部品
def _pillar(d, x, w=44, col=WOOD, y0=0, y1=FLOOR):
    d.rectangle([x, y0, x + w, y1], fill=col)
    d.line([(x + w, y0), (x + w, y1)], fill=_shade(col, 0.75), width=5)


def _beam(d, y, h=34, col=WOOD, x0=0, x1=W):
    d.rectangle([x0, y, x1, y + h], fill=col)
    d.line([(x0, y + h), (x1, y + h)], fill=_shade(col, 0.7), width=4)


def _shoji(d, x0, y0, x1, y1, paper=(236, 228, 206), frame=(128, 98, 70), cols=4, rows=5, torn=False):
    d.rectangle([x0, y0, x1, y1], fill=paper)
    for k in range(1, cols):
        x = x0 + (x1 - x0) * k / cols
        d.line([(x, y0), (x, y1)], fill=frame, width=5)
    for k in range(1, rows):
        y = y0 + (y1 - y0) * k / rows
        d.line([(x0, y), (x1, y)], fill=frame, width=5)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    if torn:                                                                # 破れに貼った継ぎ紙
        for px, py in ((x0 + 40, y0 + 60), (x1 - 90, y1 - 120), ((x0 + x1) / 2, y0 + 150)):
            d.rectangle([px, py, px + 36, py + 30], fill=_shade(paper, 0.9), outline=_shade(paper, 0.8), width=2)


def _window(d, x0, y0, x1, y1, sky=(176, 206, 226), frame=(96, 74, 54), bars=1):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    for k in range(1, bars + 1):
        x = x0 + (x1 - x0) * k / (bars + 1)
        d.line([(x, y0), (x, y1)], fill=frame, width=8)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=12)


def _noren(d, x0, x1, y0, h, col, n=4):
    w = (x1 - x0) / n
    d.rectangle([x0 - 10, y0 - 12, x1 + 10, y0], fill=WOOD_D)
    for k in range(n):
        d.rectangle([x0 + k * w + 4, y0, x0 + (k + 1) * w - 4, y0 + h], fill=col)


def _lantern(img, cx, cy, r=34, col=(236, 120, 70), lit=True):
    if lit:
        _glow(img, cx, cy, int(r * 3.4), (255, 190, 110), 70)
    d = _d(img)
    d.line([(cx, cy - r - 30), (cx, cy - r)], fill=INK, width=3)
    d.ellipse([cx - r * 0.85, cy - r * 1.2, cx + r * 0.85, cy + r * 1.2], fill=col)
    for k in (-0.6, 0, 0.6):
        d.line([(cx - r * 0.8, cy + k * r), (cx + r * 0.8, cy + k * r)], fill=_shade(col, 0.75), width=2)
    d.rectangle([cx - r * 0.4, cy - r * 1.3, cx + r * 0.4, cy - r * 1.15], fill=INK)
    d.rectangle([cx - r * 0.4, cy + r * 1.15, cx + r * 0.4, cy + r * 1.3], fill=INK)


def _bike(d, x, y, s=1.0, col=(40, 44, 50), wheel=(50, 50, 54)):
    """明治・大正の自転車（後輪の接地点が x, y）。"""
    r = 70 * s
    rx, fx = x, x + 200 * s
    cy = y - r
    for cx in (rx, fx):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=wheel, width=max(3, int(7 * s)))
        d.ellipse([cx - 8 * s, cy - 8 * s, cx + 8 * s, cy + 8 * s], fill=wheel)
        for a in range(0, 180, 30):
            t = math.radians(a)
            d.line([(cx - r * math.cos(t), cy - r * math.sin(t)), (cx + r * math.cos(t), cy + r * math.sin(t))],
                   fill=(130, 130, 136), width=1)
    bx, by = x + 90 * s, cy                                                 # ペダルの軸
    seat = (x + 60 * s, cy - 110 * s)
    head = (fx - 30 * s, cy - 120 * s)
    w = max(3, int(8 * s))
    d.line([(rx, cy), (bx, by), seat, (rx, cy)], fill=col, width=w)
    d.line([seat, head, (bx, by)], fill=col, width=w)
    d.line([head, (fx, cy)], fill=col, width=w)
    d.rounded_rectangle([seat[0] - 26 * s, seat[1] - 12 * s, seat[0] + 22 * s, seat[1] + 2 * s], radius=int(6 * s), fill=(70, 50, 36))
    d.line([(head[0] - 10 * s, head[1] - 22 * s), (head[0] + 40 * s, head[1] - 30 * s)], fill=col, width=w)
    return head


def _socket(d, cx, cy, r=14):
    """煉物のソケット（上から見た茶色い筒）。"""
    d.rounded_rectangle([cx - r, cy - r * 0.6, cx + r, cy + r * 0.9], radius=int(r * 0.4), fill=SOCKET, outline=_shade(SOCKET, 0.7), width=2)
    d.ellipse([cx - r, cy - r * 0.95, cx + r, cy - r * 0.25], fill=SOCKET_TOP, outline=_shade(SOCKET, 0.7), width=2)
    d.ellipse([cx - r * 0.35, cy - r * 0.75, cx + r * 0.35, cy - r * 0.45], fill=(150, 140, 120))


def _socket_pile(d, cx, base_y, rows, r=14, seed=1):
    rnd = random.Random(seed)
    for k in range(rows):
        n = rows - k
        y = base_y - k * r * 1.3
        for j in range(n):
            x = cx - (n - 1) * r * 1.05 + j * r * 2.1 + rnd.uniform(-3, 3)
            _socket(d, x, y + rnd.uniform(-2, 2), r)


def _shichirin(d, cx, y, s=1.0):
    """七輪と鍋（煉物を煮る）。y は七輪の下端。"""
    d.polygon([(cx - 50 * s, y), (cx + 50 * s, y), (cx + 60 * s, y - 70 * s), (cx - 60 * s, y - 70 * s)], fill=(196, 170, 130))
    d.rectangle([cx - 20 * s, y - 40 * s, cx + 20 * s, y - 14 * s], fill=(60, 40, 30))
    d.ellipse([cx - 12 * s, y - 36 * s, cx + 12 * s, y - 18 * s], fill=(240, 120, 50))
    d.chord([cx - 70 * s, y - 120 * s, cx + 70 * s, y - 40 * s], 0, 180, fill=(70, 72, 80))
    d.ellipse([cx - 72 * s, y - 92 * s, cx + 72 * s, y - 66 * s], fill=(90, 92, 100))
    d.ellipse([cx - 60 * s, y - 88 * s, cx + 60 * s, y - 70 * s], fill=(120, 96, 70))


def _press(d, x, y, s=1.0, col=(70, 72, 78)):
    """型押しの手押しプレス（ポンス）。x, y は台の左下。"""
    d.rectangle([x, y - 30 * s, x + 150 * s, y], fill=col)
    d.rectangle([x + 60 * s, y - 170 * s, x + 90 * s, y - 30 * s], fill=_shade(col, 1.15))
    d.rectangle([x + 40 * s, y - 190 * s, x + 110 * s, y - 160 * s], fill=col)
    d.rectangle([x + 66 * s, y - 70 * s, x + 84 * s, y - 40 * s], fill=(180, 180, 186))
    d.line([(x + 110 * s, y - 175 * s), (x + 200 * s, y - 230 * s)], fill=col, width=int(10 * s))
    d.ellipse([x + 188 * s, y - 244 * s, x + 214 * s, y - 218 * s], fill=(150, 40, 40))


def _bench(d, x0, x1, y, col=WOOD, legs=True, h=28):
    d.rectangle([x0, y, x1, y + h], fill=col)
    d.line([(x0, y + h), (x1, y + h)], fill=_shade(col, 0.7), width=3)
    if legs:
        for x in (x0 + 16, x1 - 40):
            d.rectangle([x, y + h, x + 24, y + h + 120], fill=_shade(col, 0.8))


def _hibachi(d, cx, cy, r, col, band=None):
    """丸火鉢（横から）。"""
    d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=col)
    d.ellipse([cx - r * 0.86, cy - r * 0.95, cx + r * 0.86, cy - r * 0.5], fill=_shade(col, 0.7))
    d.ellipse([cx - r * 0.7, cy - r * 0.88, cx + r * 0.7, cy - r * 0.58], fill=(80, 70, 64))
    if band:
        d.arc([cx - r * 0.95, cy - r * 0.5, cx + r * 0.95, cy + r * 0.4], 10, 170, fill=band, width=max(3, int(r * 0.12)))
    d.ellipse([cx - r * 0.3, cy + r * 0.05, cx + r * 0.3, cy + r * 0.35], outline=_shade(col, 1.25), width=3)


def _crate(d, x, y, w, h, col=(176, 140, 96)):
    d.rectangle([x, y, x + w, y + h], fill=col, outline=_shade(col, 0.65), width=3)
    d.line([(x, y + h * 0.5), (x + w, y + h * 0.5)], fill=_shade(col, 0.8), width=3)
    d.line([(x + 6, y + 6), (x + w - 6, y + h - 6)], fill=_shade(col, 0.85), width=2)


def _crate_wall(d, x0, x1, top, bottom, w=110, h=72, seed=3, col=(176, 140, 96)):
    rnd = random.Random(seed)
    y = bottom - h
    row = 0
    while y >= top:
        off = (row % 2) * w // 2
        x = x0 - off
        while x < x1:
            c = _shade(col, rnd.uniform(0.86, 1.08))
            _crate(d, x, y, w - 4, h - 4, c)
            x += w
        y -= h
        row += 1


def _box(d, x, y, w, h, col):
    d.rectangle([x, y, x + w, y + h], fill=col, outline=_shade(col, 0.68), width=3)
    d.rectangle([x + w * 0.44, y, x + w * 0.56, y + h], fill=_shade(col, 0.86))


def _box_stack(d, x, base, w, h, n, col=(190, 156, 110), seed=1):
    rnd = random.Random(seed)
    for k in range(n):
        dx = rnd.randint(-8, 8)
        _box(d, x + dx, base - (k + 1) * h, w, h - 4, _shade(col, rnd.uniform(0.88, 1.06)))


def _person(d, cx, y, s=1.0, coat=(52, 72, 112)):
    """法被姿の人（足元が cx, y）。顔は描かない。"""
    d.rectangle([cx - 22 * s, y - 92 * s, cx - 6 * s, y], fill=(56, 50, 48))         # 脚
    d.rectangle([cx + 6 * s, y - 92 * s, cx + 22 * s, y], fill=(56, 50, 48))
    d.polygon([(cx - 40 * s, y - 92 * s), (cx + 40 * s, y - 92 * s), (cx + 32 * s, y - 200 * s),
               (cx - 32 * s, y - 200 * s)], fill=coat)                               # 法被
    d.line([(cx, y - 200 * s), (cx, y - 92 * s)], fill=_shade(coat, 1.4), width=max(2, int(4 * s)))
    d.rectangle([cx - 40 * s, y - 120 * s, cx + 40 * s, y - 108 * s], fill=(200, 180, 120))  # 帯


def _head(d, cx, y, s=1.0):
    d.ellipse([cx - 25 * s, y - 252 * s, cx + 25 * s, y - 202 * s], fill=(226, 196, 166))
    d.rectangle([cx - 25 * s, y - 238 * s, cx + 25 * s, y - 228 * s], fill=(240, 240, 236))  # はちまき


def _carriers(d, x, y, s=1.0, coat=(52, 72, 112)):
    """丸太を肩にかついで運ぶ2人組（左の人の足元が x, y）。"""
    a, b = x + 40 * s, x + 220 * s
    _person(d, a, y, s, coat)
    _person(d, b, y + 6 * s, s, _shade(coat, 1.15))
    d.rounded_rectangle([x - 40 * s, y - 226 * s, x + 300 * s, y - 192 * s], radius=int(16 * s),
                        fill=(186, 144, 96), outline=(130, 96, 60), width=max(2, int(4 * s)))
    d.ellipse([x + 280 * s, y - 226 * s, x + 312 * s, y - 192 * s], fill=(214, 178, 128), outline=(130, 96, 60), width=2)
    _head(d, a, y, s)
    _head(d, b, y + 6 * s, s)


def _pine(d, cx, base_y, s=1.0):
    """枝ぶりの大きな松。"""
    trunk = (96, 70, 52)
    d.polygon([(cx - 26 * s, base_y), (cx + 26 * s, base_y), (cx + 14 * s, base_y - 200 * s),
               (cx + 60 * s, base_y - 330 * s), (cx + 30 * s, base_y - 340 * s),
               (cx - 10 * s, base_y - 210 * s), (cx - 50 * s, base_y - 300 * s), (cx - 70 * s, base_y - 290 * s),
               (cx - 18 * s, base_y - 190 * s)], fill=trunk)
    green, dark = (52, 96, 66), (40, 76, 52)
    for dx, dy, rw, rh in ((-220, -300, 200, 70), (60, -380, 240, 80), (-60, -470, 220, 74),
                           (180, -270, 170, 60), (-300, -200, 150, 52), (40, -560, 160, 60)):
        cy = base_y + dy * s
        d.ellipse([cx + (dx - rw / 2) * s, cy - rh / 2 * s, cx + (dx + rw / 2) * s, cy + rh / 2 * s], fill=dark)
        d.ellipse([cx + (dx - rw / 2 + 12) * s, cy - (rh / 2 + 10) * s,
                   cx + (dx + rw / 2 - 12) * s, cy + (rh / 2 - 14) * s], fill=green)


def _mountains(d, y, cols=((120, 150, 130), (96, 128, 108)), seed=2):
    rnd = random.Random(seed)
    for k, col in enumerate(cols):
        pts = [(0, H)]
        x = -100
        while x < W + 200:
            pts.append((x, y + k * 40 - rnd.randint(40, 160)))
            x += rnd.randint(180, 320)
        pts += [(W + 200, H)]
        d.polygon(pts, fill=col)


def _clouds(d, seed=4, n=4, y0=60, y1=240, col=(250, 250, 250, 220)):
    rnd = random.Random(seed)
    for _ in range(n):
        cx, cy = rnd.randint(100, W - 100), rnd.randint(y0, y1)
        for k in range(4):
            r = rnd.randint(30, 60)
            d.ellipse([cx + k * 40 - r, cy - r * 0.6, cx + k * 40 + r, cy + r * 0.6], fill=col)


def _futon(d, cx, y, w=440, col=(200, 120, 110)):
    """敷き布団と掛け布団（畳の上。y は布団の下端）。"""
    d.polygon([(cx - w / 2 + 40, y - 90), (cx + w / 2 - 40, y - 90), (cx + w / 2, y), (cx - w / 2, y)], fill=(236, 236, 230))
    d.polygon([(cx - w / 2 + 120, y - 84), (cx + w / 2 - 44, y - 84), (cx + w / 2 - 10, y - 8), (cx - w / 2 + 80, y - 8)], fill=col)
    d.ellipse([cx - w / 2 + 50, y - 86, cx - w / 2 + 130, y - 56], fill=(250, 250, 246))


def _bullet_lamp(img, cx, cy, s=1.0, lit=True, beam=False):
    """砲弾型の電池ランプ（横向き。右が光る面）。"""
    d = _d(img)
    if lit:
        _glow(img, cx + 60 * s, cy, int(150 * s), (255, 236, 160), 120)
        if beam:
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            ld.polygon([(cx + 60 * s, cy - 20 * s), (cx + 520 * s, cy - 150 * s), (cx + 520 * s, cy + 150 * s),
                        (cx + 60 * s, cy + 20 * s)], fill=(255, 240, 170, 70))
            img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))
        d = _d(img)
    d.rounded_rectangle([cx - 70 * s, cy - 26 * s, cx + 40 * s, cy + 26 * s], radius=int(24 * s), fill=(40, 42, 48))
    d.pieslice([cx - 10 * s, cy - 28 * s, cx + 90 * s, cy + 28 * s], -90, 90, fill=(60, 62, 70))
    d.ellipse([cx + 40 * s, cy - 24 * s, cx + 74 * s, cy + 24 * s], fill=(255, 246, 200) if lit else (170, 170, 160))
    d.rectangle([cx - 30 * s, cy + 26 * s, cx - 14 * s, cy + 50 * s], fill=(70, 70, 76))


def _paper_bundle(d, x, y, w=120, h=90, col=(246, 242, 228)):
    """紐でくくった書類の束（左下が x, y）。"""
    for k in range(int(h / 9)):
        yy = y - k * 9
        d.rectangle([x + (k % 2) * 3, yy - 9, x + w + (k % 2) * 3, yy], fill=col if k % 3 else _shade(col, 0.94),
                    outline=_shade(col, 0.78), width=1)
    d.line([(x + w * 0.5, y), (x + w * 0.5, y - h)], fill=(160, 70, 60), width=4)
    d.line([(x, y - h * 0.5), (x + w, y - h * 0.5)], fill=(160, 70, 60), width=4)


def _scroll(d, cx, y0, h=300, w=110):
    d.rectangle([cx - w / 2, y0, cx + w / 2, y0 + h], fill=(232, 224, 200), outline=(120, 96, 70), width=4)
    d.rectangle([cx - w / 2 - 8, y0 - 10, cx + w / 2 + 8, y0], fill=(90, 70, 50))
    d.rectangle([cx - w / 2 - 8, y0 + h, cx + w / 2 + 8, y0 + h + 10], fill=(90, 70, 50))
    d.line([(cx, y0 + 40), (cx - 10, y0 + 120), (cx + 6, y0 + 170)], fill=(70, 70, 70), width=6)


def _ikebana(d, cx, y):
    d.polygon([(cx - 36, y), (cx + 36, y), (cx + 24, y - 60), (cx - 24, y - 60)], fill=(70, 90, 110))
    for dx, dy, col in ((-60, -170, (220, 90, 90)), (10, -210, (240, 200, 90)), (60, -150, (220, 120, 140))):
        d.line([(cx, y - 60), (cx + dx, y + dy)], fill=(70, 110, 60), width=5)
        d.ellipse([cx + dx - 16, y + dy - 16, cx + dx + 16, y + dy + 16], fill=col)


# ---------------------------------------------------------------- 和室・板の間の型
def _japanese_room(wall=PLASTER, wall2=None, floor="tatami", floor_y=FLOOR, pillars=(140, 1736)):
    img = _base(wall, wall2 or _shade(wall, 0.9))
    d = _d(img)
    for x in pillars:
        _pillar(d, x)
    _beam(d, 90, 36)
    if floor == "tatami":
        tatami_floor(img, floor_y)
    else:
        wood_floor(img, floor_y, col=(126, 96, 68), line=(104, 78, 54))
    return img


# ---------------------------------------------------------------- 現代
def heya():
    """今の部屋。壁のコンセントから延長コード、その先にまた延長コード。"""
    img = _base((236, 234, 226), (222, 220, 212))
    wood_floor(img, FLOOR, col=(178, 150, 116), line=(160, 132, 100))
    d = _d(img)
    _window(d, 1460, 130, 1820, 520, sky=(190, 220, 240), frame=(240, 240, 236))
    d.rectangle([1440, 110, 1840, 130], fill=(200, 196, 188))                    # カーテンレール
    d.rectangle([1430, 130, 1490, 600], fill=(150, 180, 200))                    # カーテン
    d.rectangle([140, 160, 420, 420], fill=(250, 250, 248), outline=(200, 196, 188), width=6)  # 壁の絵
    d.polygon([(160, 400), (260, 260), (330, 340), (400, 400)], fill=(150, 190, 160))
    # 棚と、その上の延長コードの連なり
    d.rectangle([640, 620, 1280, 660], fill=(196, 168, 128))
    d.rectangle([660, 660, 1260, 780], fill=(176, 148, 110))
    d.rectangle([930, 400, 1010, 490], fill=(250, 250, 246), outline=(180, 180, 176), width=4)  # 壁のコンセント
    for k in (0, 1):
        d.rectangle([950 + k * 28, 420, 960 + k * 28, 440], fill=(60, 60, 60))
        d.rectangle([950 + k * 28, 450, 960 + k * 28, 470], fill=(60, 60, 60))
    d.line([(970, 490), (970, 560), (1180, 590)], fill=(240, 240, 240), width=8)
    for x, y in ((1000, 572), (760, 572)):                                      # 延長コードに延長コード
        d.rounded_rectangle([x, y, x + 230, y + 48], radius=12, fill=(250, 250, 248), outline=(150, 150, 146), width=4)
        for j in range(4):
            d.rectangle([x + 22 + j * 52, y + 14, x + 42 + j * 52, y + 34], fill=(70, 70, 74))
    d.line([(1004, 596), (990, 640), (900, 650), (870, 620)], fill=(240, 240, 240), width=7)   # つなぎのコード
    for x, col in ((1022, (220, 90, 70)), (1074, (80, 90, 110)), (1126, (60, 150, 90)),
                   (782, (230, 170, 60)), (834, (150, 90, 160))):
        d.rectangle([x - 2, 576, x + 22, 606], fill=col)                        # 挿さったプラグ
        d.line([(x + 10, 576), (x + 10 + (x - 960) * 0.25, 480)], fill=col, width=6)
    d.rounded_rectangle([1150, 470, 1240, 560], radius=16, fill=(230, 120, 80))  # ドライヤー
    d.rectangle([1180, 540, 1204, 620], fill=(230, 120, 80))
    d.rounded_rectangle([1290, 760, 1400, 928], radius=12, fill=(236, 236, 232), outline=(150, 150, 146), width=4)  # 電気ストーブ
    for y in range(790, 900, 26):
        d.rectangle([1310, y, 1380, y + 10], fill=(240, 120, 60))
    return img


def gendai():
    """今の家電の売り場。家電と電動アシスト自転車（ロゴは描かない）。"""
    img = _base((244, 244, 242), (230, 232, 232))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(214, 214, 210))
    for x in range(0, W, 160):
        d.line([(x, FLOOR), (x - 90, H)], fill=(200, 200, 196), width=3)
    d.rectangle([0, 80, W, 110], fill=(220, 222, 224))
    for x in range(160, W, 320):                                                # 天井の照明
        d.rectangle([x, 110, x + 160, 124], fill=(255, 255, 250))
    # 冷蔵庫・洗濯機・テレビ（キャラの間）
    d.rounded_rectangle([640, 260, 820, 700], radius=16, fill=(236, 238, 240), outline=(170, 176, 180), width=4)
    d.line([(640, 420), (820, 420)], fill=(170, 176, 180), width=4)
    d.rectangle([800, 300, 808, 390], fill=(160, 166, 170))
    d.rounded_rectangle([1080, 480, 1280, 700], radius=18, fill=(236, 238, 240), outline=(170, 176, 180), width=4)
    d.ellipse([1120, 540, 1240, 660], fill=(190, 200, 210), outline=(150, 160, 170), width=6)
    d.rectangle([860, 250, 1220, 450], fill=(30, 32, 40), outline=(20, 20, 24), width=8)
    d.rectangle([878, 268, 1202, 432], fill=(70, 130, 190))
    d.rectangle([1010, 450, 1070, 470], fill=(40, 40, 44))
    _bike(d, 860, 700, 0.62, col=(60, 120, 150))                                # 電動アシスト自転車
    d.rectangle([905, 610, 935, 650], fill=(50, 50, 56))                        # バッテリー
    return img


# ---------------------------------------------------------------- 和歌山
def wasa():
    """和佐村の生家。田んぼの中の藁葺きの家と大きな松、奥にミカンの山。"""
    img = vgrad((W, H), (160, 200, 232), (222, 232, 226)).convert("RGBA")
    d = _d(img)
    _clouds(d, seed=7, n=3)
    _mountains(d, 470, cols=((150, 176, 140), (120, 150, 112)), seed=5)
    for x in range(40, W, 90):                                                  # 山のミカン
        d.ellipse([x, 420 + (x * 7) % 50, x + 10, 430 + (x * 7) % 50], fill=(240, 150, 50))
    d.rectangle([0, 640, W, H], fill=(120, 164, 92))                            # 田んぼ
    for y in range(680, H, 60):
        d.line([(0, y), (W, y)], fill=(108, 150, 82), width=3)
    d.line([(0, 640), (W, 640)], fill=(100, 136, 76), width=5)
    # 藁葺きの家（右奥）
    x0, x1, y0 = 1220, 1860, 430
    d.rectangle([x0 + 40, y0 + 110, x1 - 40, 660], fill=(214, 196, 160))
    d.polygon([(x0, y0 + 130), ((x0 + x1) / 2, y0 - 120), (x1, y0 + 130)], fill=(176, 150, 96))
    d.polygon([(x0 + 60, y0 + 100), ((x0 + x1) / 2, y0 - 90), (x1 - 60, y0 + 100)], fill=(196, 170, 110))
    for x in range(x0 + 120, x1 - 80, 110):
        d.rectangle([x, y0 + 170, x + 60, 660], fill=(110, 84, 58))
    _pine(d, 940, 640, 1.0)                                                     # 大きな松
    return img


def nagaya():
    """和歌山市の裏長屋。狭く暗い一間、継ぎを当てた障子、小さな仏壇。"""
    img = _japanese_room(wall=(170, 156, 134), wall2=(150, 138, 118), pillars=(120, 1760))
    d = _d(img)
    _shoji(d, 230, 190, 640, 700, paper=(214, 204, 180), torn=True)
    d.rectangle([1300, 170, 1640, 330], fill=(120, 100, 76))                    # 小さな高窓
    d.line([(1300, 250), (1640, 250)], fill=(90, 70, 52), width=6)
    for x in range(1340, 1640, 60):
        d.line([(x, 170), (x, 330)], fill=(90, 70, 52), width=6)
    # 仏壇（中央の棚の上）
    d.rectangle([800, 470, 1120, 500], fill=WOOD_D)
    d.rectangle([860, 300, 1060, 470], fill=(60, 40, 28), outline=(150, 120, 60), width=6)
    d.rectangle([880, 320, 1040, 450], fill=(40, 28, 20))
    for k, h in enumerate((90, 110, 90)):                                       # 位牌
        x = 905 + k * 50
        d.rectangle([x, 440 - h, x + 30, 440], fill=(30, 22, 16), outline=(190, 160, 80), width=2)
    _glow(img, 960, 380, 120, (255, 200, 120), 50)
    d = _d(img)
    d.rectangle([950, 300 - 40, 970, 300], fill=(240, 236, 220))               # ろうそく
    return _vignette(img, 70)


def kinokawa():
    """南海・紀ノ川駅。晩秋の小さな駅と、停まっている汽車。"""
    img = vgrad((W, H), (210, 214, 220), (232, 222, 206)).convert("RGBA")
    d = _d(img)
    _mountains(d, 500, cols=((170, 150, 130), (150, 128, 108)), seed=11)
    rnd = random.Random(9)
    for x in range(30, W, 120):                                                 # 紅葉の木
        y = 470 + rnd.randint(-20, 20)
        d.ellipse([x - 60, y - 70, x + 60, y + 40], fill=rnd.choice([(214, 120, 60), (200, 90, 50), (226, 170, 70)]))
    # 汽車（中央の奥）
    d.rectangle([0, 700, W, 720], fill=(120, 110, 100))                         # 線路の敷石
    for x in range(-40, W, 60):
        d.rectangle([x, 704, x + 36, 716], fill=(96, 76, 60))
    d.line([(0, 700), (W, 700)], fill=(80, 80, 86), width=5)
    d.rectangle([520, 470, 1180, 690], fill=(90, 50, 40), outline=(50, 30, 24), width=6)   # 客車
    for x in range(560, 1150, 110):
        d.rectangle([x, 510, x + 70, 580], fill=(236, 226, 196), outline=(50, 30, 24), width=4)
    d.rectangle([1200, 520, 1440, 690], fill=(40, 40, 44))                      # 機関車
    d.rectangle([1260, 440, 1420, 520], fill=(50, 50, 54))
    d.rectangle([1380, 380, 1420, 440], fill=(40, 40, 44))
    for cx in (1250, 1340, 1420):
        d.ellipse([cx - 34, 640, cx + 34, 708], fill=(30, 30, 34), outline=(120, 40, 40), width=6)
    for k in range(4):                                                          # 煙
        d.ellipse([1360 - k * 80, 300 - k * 40, 1460 - k * 80, 370 - k * 40], fill=(236, 236, 236, 200 - k * 30))
    # 駅舎のひさし（左上）と柱
    d.polygon([(0, 140), (520, 140), (480, 220), (0, 220)], fill=(110, 90, 70))
    for x in (60, 420):
        d.rectangle([x, 220, x + 26, 720], fill=WOOD_D)
    d.rectangle([0, 720, W, H], fill=(176, 168, 156))                           # ホーム
    d.line([(0, 720), (W, 720)], fill=(236, 230, 210), width=10)
    return img


# ---------------------------------------------------------------- 大阪の奉公先
def hibachi():
    """宮田火鉢店。段の棚に丸火鉢が並ぶ。"""
    img = _japanese_room(wall=(210, 196, 170), floor="wood")
    d = _d(img)
    _noren(d, 220, 1700, 126, 70, (60, 70, 90), n=8)
    rnd = random.Random(4)
    pal = [(150, 110, 80), (120, 90, 70), (180, 150, 110), (90, 100, 110), (160, 70, 60)]
    for row, (y, x0, x1) in enumerate(((420, 640, 1300), (600, 620, 1320))):
        d.rectangle([x0 - 20, y + 50, x1 + 20, y + 74], fill=WOOD)
        d.rectangle([x0 - 20, y + 74, x1 + 20, y + 90], fill=WOOD_D)
        for x in range(x0 + 50, x1, 140):
            _hibachi(d, x, y, 56, rnd.choice(pal), band=(200, 180, 120))
    for x in (1480, 1640):                                                      # 右の床に置いた大火鉢（上半分だけ見える）
        _hibachi(d, x, 640, 70, (110, 84, 62), band=(210, 190, 130))
    d.rectangle([1400, 700, 1760, 720], fill=WOOD)
    return img


def godai():
    """五代自転車商会。舶来の自転車が並び、奥に修理の工具。"""
    img = _japanese_room(wall=(222, 210, 186), floor="wood")
    d = _d(img)
    _noren(d, 220, 1700, 126, 60, (40, 70, 110), n=8)
    d.rectangle([560, 200, 1360, 230], fill=WOOD_D)                             # 工具掛け
    for k, x in enumerate(range(600, 1340, 70)):
        if k % 3 == 0:
            d.line([(x, 236), (x + 10, 330)], fill=(120, 124, 130), width=8)
            d.ellipse([x - 4, 320, x + 24, 346], outline=(120, 124, 130), width=6)
        elif k % 3 == 1:
            d.rectangle([x, 236, x + 12, 320], fill=(110, 80, 50))
            d.rectangle([x - 10, 320, x + 22, 340], fill=(120, 124, 130))
        else:
            d.ellipse([x - 20, 240, x + 30, 290], outline=(60, 60, 64), width=5)   # 予備のタイヤ
    for k, x in enumerate((660, 980)):                                          # 自転車（中央の奥）
        _bike(d, x, 720, 1.05, col=((40, 44, 50), (110, 40, 40))[k])
    d.rectangle([600, 720, 1320, 740], fill=WOOD)                               # 展示の台
    return img


def tenma():
    """天満の母の住まい（1906年）。石油ランプの灯る小さな座敷。"""
    img = _japanese_room(wall=(196, 182, 156))
    d = _d(img)
    _shoji(d, 600, 180, 1300, 690, paper=(232, 222, 196))
    d.rectangle([1400, 520, 1640, 560], fill=WOOD)                              # 小箪笥
    d.rectangle([1410, 560, 1630, 700], fill=WOOD_D)
    for y in (590, 640):
        d.rectangle([1500, y, 1540, y + 10], fill=(200, 170, 90))
    d.rectangle([1500, 440, 1530, 520], fill=(130, 110, 80))                    # 石油ランプ
    d.ellipse([1480, 400, 1550, 450], fill=(250, 220, 150))
    d.rectangle([1495, 360, 1535, 410], fill=(240, 236, 220, 160))
    _glow(img, 1515, 425, 200, (255, 200, 120), 80)
    return img


def kaya():
    """本町の蚊帳問屋の店先。緑の蚊帳を吊り、店先に売り込みの自転車。"""
    img = _japanese_room(wall=(214, 202, 176), floor="wood")
    d = _d(img)
    _noren(d, 200, 1720, 126, 64, (90, 60, 50), n=8)
    for x0 in (560, 960):                                                       # 吊った蚊帳
        d.polygon([(x0, 230), (x0 + 360, 230), (x0 + 400, 620), (x0 - 40, 620)], fill=(110, 160, 120, 210))
        for k in range(14):
            t = k / 13
            d.line([(x0 + 360 * t, 230), (x0 - 40 + 440 * t, 620)], fill=(90, 140, 100, 160), width=2)
        for y in range(250, 620, 30):
            d.line([(x0 - 40 * (y - 230) / 390, y), (x0 + 360 + 40 * (y - 230) / 390, y)], fill=(90, 140, 100, 160), width=2)
        d.rectangle([x0 - 8, 220, x0 + 368, 232], fill=(170, 60, 50))
    for k, y in enumerate((300, 440)):                                          # 反物の棚（右）
        d.rectangle([1440, y + 80, 1840, y + 96], fill=WOOD)
        for j in range(5):
            col = ((110, 160, 120), (220, 220, 210), (90, 120, 150), (180, 160, 120), (150, 190, 160))[(j + k) % 5]
            d.rounded_rectangle([1452 + j * 76, y, 1518 + j * 76, y + 80], radius=10, fill=col)
    _bike(d, 790, 720, 0.95)
    d.rectangle([560, 720, 1360, 736], fill=WOOD)
    return img


def shiden():
    """明治末の大阪の大通り。架線の下を走る市電。"""
    img = vgrad((W, H), (176, 204, 226), (226, 228, 220)).convert("RGBA")
    d = _d(img)
    for x0, w, h, col in ((0, 380, 430, (176, 150, 120)), (380, 300, 360, (120, 110, 104)),
                          (1300, 320, 470, (190, 170, 140)), (1620, 300, 380, (150, 130, 110))):
        d.rectangle([x0, 690 - h, x0 + w, 690], fill=col)                       # 町並み
        for y in range(690 - h + 40, 650, 90):
            for x in range(x0 + 30, x0 + w - 50, 80):
                d.rectangle([x, y, x + 40, y + 50], fill=_shade(col, 0.7))
    d.polygon([(380, 330), (680, 330), (660, 290), (400, 290)], fill=(80, 70, 66))
    d.line([(0, 250), (W, 230)], fill=(50, 50, 54), width=3)                    # 架線
    d.line([(0, 268), (W, 248)], fill=(50, 50, 54), width=2)
    for x in (300, 1500):
        d.rectangle([x, 200, x + 14, 690], fill=(80, 76, 72))
    # 市電（中央）
    x0, y0 = 1060, 400
    d.rounded_rectangle([x0, y0, x0 + 560, y0 + 250], radius=24, fill=(210, 190, 140), outline=(110, 80, 50), width=6)
    d.rectangle([x0, y0 + 160, x0 + 560, y0 + 250], fill=(120, 70, 50))
    for x in range(x0 + 40, x0 + 520, 90):
        d.rectangle([x, y0 + 40, x + 60, y0 + 120], fill=(230, 236, 236), outline=(110, 80, 50), width=4)
    d.polygon([(x0 + 40, y0), (x0 + 520, y0), (x0 + 490, y0 - 40), (x0 + 70, y0 - 40)], fill=(100, 70, 50))
    d.line([(x0 + 280, y0 - 40), (x0 + 420, 246)], fill=(40, 40, 44), width=6)  # ポール
    for cx in (x0 + 110, x0 + 450):
        d.ellipse([cx - 30, y0 + 230, cx + 30, y0 + 290], fill=(40, 40, 44))
    d.rectangle([0, 690, W, H], fill=(170, 162, 150))                           # 道
    for y in (760, 800):
        d.line([(0, y), (W, y)], fill=(130, 126, 120), width=6)
    return img


# ---------------------------------------------------------------- 大阪電灯
def dento():
    """大阪電灯の職工の詰所。電線の束と白い碍子、材料を積んだ丁稚車。"""
    img = _base((206, 198, 180), (188, 180, 162))
    wood_floor(img, FLOOR, col=(120, 100, 80), line=(100, 84, 66))
    d = _d(img)
    _window(d, 120, 150, 460, 460, sky=(196, 212, 222), bars=2)
    for k, x in enumerate(range(620, 1300, 150)):                               # 電線の束（壁の釘）
        d.rectangle([x + 40, 160, x + 52, 180], fill=INK)
        d.ellipse([x, 180, x + 92, 290], outline=(60, 60, 64), width=10)
        d.ellipse([x + 12, 192, x + 80, 278], outline=(140, 80, 50), width=6)
    d.rectangle([600, 380, 1320, 400], fill=WOOD)                               # 碍子の棚
    for x in range(630, 1300, 46):
        d.rounded_rectangle([x, 330, x + 30, 380], radius=10, fill=(244, 244, 240), outline=(170, 170, 170), width=2)
    for x in (1420, 1520):                                                      # 立てかけたはしご
        d.line([(x, 160), (x + 60, 720)], fill=WOOD, width=12)
    for y in range(220, 700, 80):
        d.line([(1420 + 60 * (y - 160) / 560, y), (1520 + 60 * (y - 160) / 560, y)], fill=WOOD, width=8)
    # 丁稚車（中央）
    d.rectangle([760, 560, 1160, 600], fill=(150, 116, 80))
    d.line([(1160, 580), (1300, 520)], fill=(150, 116, 80), width=10)
    for cx in (840, 1080):
        d.ellipse([cx - 60, 560, cx + 60, 680], outline=(90, 70, 50), width=10)
    for k in range(3):
        d.ellipse([800 + k * 90, 500, 880 + k * 90, 560], outline=(60, 60, 64), width=8)  # 積んだ電線
    d.rectangle([1080, 520, 1150, 560], fill=(176, 140, 96))
    return img


def dento_jimu():
    """大阪電灯の事務所。机に帳面と硯、壁に時計。"""
    img = _base((222, 214, 196), (204, 196, 178))
    wood_floor(img, FLOOR, col=(130, 104, 80), line=(110, 88, 66))
    d = _d(img)
    _window(d, 1400, 150, 1800, 500, sky=(200, 216, 226), bars=2)
    d.ellipse([880, 150, 1040, 310], fill=(240, 236, 220), outline=WOOD_D, width=10)  # 柱時計
    d.line([(960, 230), (960, 180)], fill=INK, width=6)
    d.line([(960, 230), (1000, 250)], fill=INK, width=6)
    d.rectangle([930, 310, 990, 420], fill=WOOD_D)
    d.ellipse([945, 380, 975, 410], fill=(200, 170, 90))
    _bench(d, 640, 1280, 600, col=(120, 90, 62))                                # 机
    for k in range(3):                                                          # 帳面の山
        d.rectangle([700 + k * 6, 560 - k * 14, 860 + k * 6, 574 - k * 14], fill=(236, 230, 210), outline=(170, 160, 140))
    d.rectangle([920, 570, 1000, 600], fill=(50, 50, 54))                       # 硯
    d.line([(1040, 600), (1110, 540)], fill=(90, 70, 50), width=6)              # 筆
    d.rectangle([1150, 520, 1240, 600], fill=(230, 226, 210), outline=(150, 140, 120), width=3)  # 書類
    for y in range(536, 590, 12):
        d.line([(1160, y), (1230, y)], fill=(150, 150, 150), width=2)
    for k, y in enumerate((260, 380)):                                          # 書類棚（左）
        d.rectangle([140, y + 70, 500, y + 84], fill=WOOD)
        for j in range(6):
            d.rectangle([150 + j * 58, y, 196 + j * 58, y + 70], fill=((200, 190, 160), (160, 150, 130))[(j + k) % 2])
    return img


# ---------------------------------------------------------------- 見合い・新婚
def yachiyoza():
    """松島の芝居小屋・八千代座の前。のぼりと提灯（字は入れない）。"""
    img = vgrad((W, H), (190, 210, 230), (230, 226, 214)).convert("RGBA")
    d = _d(img)
    d.rectangle([300, 140, 1620, 720], fill=(150, 100, 70))                     # 小屋の正面
    d.polygon([(240, 160), (960, 40), (1680, 160)], fill=(80, 70, 70))
    d.rectangle([300, 150, 1620, 180], fill=(60, 50, 50))
    d.rectangle([520, 220, 1400, 340], fill=(236, 226, 200), outline=(90, 60, 40), width=8)  # 看板（無地）
    for k in range(4):
        d.rectangle([560 + k * 210, 250, 720 + k * 210, 310], fill=(200, 80, 70) if k % 2 else (60, 90, 140))
    d.rectangle([760, 430, 1160, 720], fill=(60, 40, 30))                       # 木戸口
    _noren(d, 780, 1140, 440, 90, (170, 50, 50), n=4)
    rnd = random.Random(15)
    for x in (360, 470, 1450, 1560):                                            # のぼり
        col = rnd.choice([(200, 60, 60), (240, 200, 80), (80, 120, 180), (240, 240, 230)])
        d.rectangle([x, 220, x + 8, 720], fill=(90, 70, 50))
        d.rectangle([x + 8, 240, x + 70, 620], fill=col)
    img2 = img
    for x in range(360, 1600, 140):                                             # 提灯の列
        _lantern(img2, x, 400, 26, col=(236, 120, 70), lit=False)
    d = _d(img2)
    d.rectangle([0, 720, W, H], fill=(180, 168, 148))                           # 通り
    d.line([(0, 720), (W, 720)], fill=(150, 138, 118), width=6)
    return img2


def nikai():
    """結婚後の2階借り。低い天井、窓の外に屋根の連なり、文机に試作のソケット。"""
    img = _japanese_room(wall=(214, 200, 176), pillars=(110, 1760))
    d = _d(img)
    _beam(d, 70, 60, col=(96, 70, 48))                                          # 低い天井
    _window(d, 1200, 210, 1640, 560, sky=(196, 214, 228), bars=1)
    for k in range(4):                                                          # 外の瓦屋根
        x = 1214 + k * 104
        d.polygon([(x, 548), (x + 18, 468), (x + 86, 468), (x + 104, 548)], fill=(90, 96, 110))
        for j in range(1, 4):
            d.line([(x + 4 + j * 4, 468 + j * 20), (x + 100 - j * 4, 468 + j * 20)], fill=(70, 76, 90), width=3)
    _bench(d, 700, 1100, 640, col=(126, 94, 64), legs=False, h=24)              # 文机
    d.rectangle([720, 664, 744, 740], fill=(104, 78, 52))
    d.rectangle([1056, 664, 1080, 740], fill=(104, 78, 52))
    for k in range(3):
        _socket(d, 790 + k * 70, 618, 16)
    d.rectangle([980, 600, 1060, 640], fill=(200, 190, 160))                    # 図面
    d.line([(990, 612), (1050, 612)], fill=(120, 120, 140), width=2)
    d.line([(990, 626), (1040, 626)], fill=(120, 120, 140), width=2)
    return img


# ---------------------------------------------------------------- 猪飼野の借家
def _ikaino(night=False):
    """2畳と4畳半。4畳半の半分を土間の仕事場にした借家。七輪の鍋と型押しのポンス。"""
    img = _base((206, 190, 162), (186, 170, 144))
    d = _d(img)
    _pillar(d, 120)
    _pillar(d, 1760)
    _beam(d, 90, 36)
    _shoji(d, 190, 200, 560, 700, paper=(228, 218, 192))
    d.rectangle([1300, 190, 1660, 380], fill=(150, 170, 186) if not night else (24, 30, 56))  # 格子窓
    for x in range(1330, 1660, 44):
        d.line([(x, 190), (x, 380)], fill=WOOD_D, width=8)
    d.rectangle([1300, 190, 1660, 380], outline=WOOD_D, width=10)
    # 床: 左は畳の上がり、右は土間
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([700, FLOOR - 6, W, H], fill=(150, 126, 100))                   # 土間
    d.rectangle([700, FLOOR - 16, 716, H], fill=WOOD_D)                         # 上がり框
    rnd = random.Random(21)
    for _ in range(40):
        x, y = rnd.randint(730, W), rnd.randint(FLOOR + 10, H - 10)
        d.ellipse([x, y, x + 6, y + 4], fill=(136, 112, 88))
    # 仕事台（中央）
    _bench(d, 700, 1240, 600, col=(120, 90, 62))
    _press(d, 1010, 600, 1.0)
    _shichirin(d, 820, 600, 0.9)
    d.rectangle([1150, 570, 1236, 600], fill=(150, 116, 80))                    # できたソケットの箱
    for k in range(3):
        _socket(d, 1168 + k * 30, 566, 11)
    if night:
        img = _tint(img, (20, 30, 70), 120)
        d = _d(img)
        d.line([(960, 0), (960, 120)], fill=(40, 34, 28), width=6)
        _glow(img, 960, 220, 380, (255, 200, 120), 60)
        d = _d(img)
        d.ellipse([930, 120, 990, 190], fill=(255, 226, 150))
        d.rectangle([946, 104, 974, 130], fill=(120, 110, 96))
        d.ellipse([60, 820, 300, 900], fill=(140, 104, 70), outline=(100, 72, 48), width=6)   # 行水のたらい
        d.ellipse([84, 830, 276, 880], fill=(120, 150, 170))
    return img


def ikaino():
    return _ikaino()


def ikaino_yoru():
    return _ikaino(night=True)


def ikaino_yama():
    """売れ残ったソケットの山。仕事台の上も下も、茶色いソケットでいっぱい。"""
    img = _ikaino()
    d = _d(img)
    for cx, base, rows, r, seed in ((960, 600, 10, 22, 1), (770, 600, 6, 20, 2), (1160, 600, 7, 20, 3)):
        _socket_pile(d, cx, base - 18, rows, r, seed)
    _socket_pile(d, 960, FLOOR - 12, 7, 24, 4)                                  # 土間にもこぼれた山
    for k, y in enumerate((300, 420)):                                          # 壁の棚にも
        d.rectangle([600, y + 18, 1320, y + 32], fill=WOOD)
        for x in range(620, 1310, 32):
            _socket(d, x, y + 4, 13)
    return img


# ---------------------------------------------------------------- 大開町
def _ohiraki():
    """大開町の創業の家。1階の作業場に小型プレス機2台、奥に2階への階段。"""
    img = _base((214, 200, 174), (196, 182, 156))
    wood_floor(img, FLOOR, col=(130, 100, 72), line=(110, 84, 60))
    d = _d(img)
    _pillar(d, 110)
    _pillar(d, 1770)
    _beam(d, 80, 40)
    _window(d, 170, 180, 520, 470, sky=(200, 214, 224), bars=3)
    for k in range(7):                                                          # 2階への階段（右）
        x, y = 1460 + k * 46, 720 - k * 80
        d.rectangle([x, y, 1760, y + 22], fill=(140, 106, 76))
        d.rectangle([x, y + 22, x + 10, max(y + 22, 742)], fill=(110, 84, 60))
    _bench(d, 640, 1300, 600, col=(124, 94, 64))
    _press(d, 700, 600, 0.9)
    _press(d, 1000, 600, 0.9, col=(80, 84, 92))
    for k in range(5):                                                          # 差し込みの部品
        d.ellipse([1220 + (k % 3) * 22, 572 - (k // 3) * 16, 1240 + (k % 3) * 22, 590 - (k // 3) * 16], fill=(70, 60, 54))
    return img


def ohiraki():
    return _ohiraki()


def ohiraki_tana():
    """狭い作業場に棚を吊って上下で作業する。蒸気船の船室のよう。"""
    img = _ohiraki()
    d = _d(img)
    for y, x0, x1 in ((300, 560, 1400), (430, 600, 1360)):
        for x in (x0 + 20, x1 - 20):                                            # 吊り紐
            d.line([(x, 120), (x, y)], fill=(90, 70, 50), width=6)
        d.rectangle([x0, y, x1, y + 26], fill=(150, 114, 78))
        d.line([(x0, y + 26), (x1, y + 26)], fill=WOOD_D, width=4)
        for x in range(x0 + 40, x1 - 60, 120):                                  # 棚の上の箱と部品
            d.rectangle([x, y - 50, x + 80, y], fill=(176, 140, 96), outline=_shade((176, 140, 96), 0.7), width=3)
            for j in range(3):
                d.ellipse([x + 8 + j * 24, y - 64, x + 26 + j * 24, y - 48], fill=(70, 60, 54))
    for x in range(560, 1400, 90):                                              # 上の棚の板の陰
        d.line([(x, 326), (x + 20, 340)], fill=(0, 0, 0, 40), width=3)
    return img


# ---------------------------------------------------------------- 問屋
def tonya_tokyo():
    """東京の問屋の帳場。帳場格子とそろばん、電気器具の箱が並ぶ棚。"""
    img = _japanese_room(wall=(190, 176, 152), floor="wood", pillars=(120, 1760))
    d = _d(img)
    _noren(d, 200, 1720, 126, 54, (40, 50, 70), n=8)
    for k, y in enumerate((230, 380, 530)):                                     # 箱の棚
        d.rectangle([560, y + 90, 1360, y + 106], fill=WOOD_D)
        for j in range(8):
            col = ((210, 196, 160), (180, 164, 130), (160, 180, 190))[(j + k) % 3]
            d.rectangle([572 + j * 98, y + 10, 652 + j * 98, y + 90], fill=col, outline=_shade(col, 0.7), width=3)
    d.rectangle([1420, 520, 1800, 720], fill=(110, 80, 54))                     # 帳場
    for x in range(1430, 1800, 34):                                             # 帳場格子
        d.line([(x, 440), (x, 520)], fill=WOOD_D, width=6)
    d.rectangle([1420, 430, 1800, 446], fill=WOOD_D)
    d.rectangle([1450, 490, 1640, 520], fill=(90, 60, 40))                      # そろばん
    for x in range(1460, 1630, 18):
        d.ellipse([x, 496, x + 12, 514], fill=(40, 30, 24))
    return img


def tonya_osaka():
    """大阪の電気器具の問屋（1923年）。電池の箱、天井から下がる電球の見本。"""
    img = _base((210, 200, 180), (192, 182, 162))
    wood_floor(img, FLOOR, col=(116, 92, 70), line=(96, 76, 58))
    d = _d(img)
    _beam(d, 70, 40)
    for x in range(600, 1340, 120):                                             # 電球の見本
        d.line([(x, 110), (x, 230)], fill=INK, width=3)
        d.ellipse([x - 20, 230, x + 20, 280], fill=(240, 236, 210), outline=(150, 150, 140), width=2)
        d.rectangle([x - 8, 222, x + 8, 236], fill=(150, 140, 120))
    for x0 in (120, 1420):                                                       # 電池の箱の棚（左右）
        d.rectangle([x0, 300, x0 + 14, 720], fill=WOOD_D)
        d.rectangle([x0 + 400, 300, x0 + 414, 720], fill=WOOD_D)
        for k, y in enumerate((300, 440, 580)):
            d.rectangle([x0, y + 110, x0 + 414, y + 124], fill=WOOD_D)
            for j in range(4):
                col = ((70, 90, 120), (190, 160, 110), (120, 60, 50), (200, 190, 160))[(j + k) % 4]
                _box(d, x0 + 22 + j * 96, y + 34, 84, 76, col)
    _bench(d, 640, 1300, 600, col=(120, 90, 62))                               # 帳場の机
    for k in range(4):
        d.rectangle([700 + k * 80, 556, 760 + k * 80, 600], fill=(60, 70, 90), outline=(40, 46, 60), width=3)  # 電池
    _bullet_lamp(img, 1120, 570, 0.7, lit=False)
    return img


# ---------------------------------------------------------------- 自転車屋の店先
def _jitenshaya(night=False):
    """大正の自転車店の店先。自転車のハンドルに砲弾型ランプ。"""
    sky = (24, 32, 60) if night else (186, 210, 228)
    img = vgrad((W, H), sky, _shade(sky, 1.1) if night else (226, 226, 216)).convert("RGBA")
    d = _d(img)
    d.rectangle([0, 160, W, 720], fill=(176, 150, 116))                         # 店
    d.polygon([(0, 180), (W, 180), (W, 110), (0, 110)], fill=(80, 70, 66))      # ひさし
    _noren(d, 160, 1760, 190, 60, (120, 50, 40), n=10)
    d.rectangle([120, 280, 560, 700], fill=(70, 60, 54))                        # 店の中（左）
    d.rectangle([1360, 280, 1800, 700], fill=(70, 60, 54))                      # 店の中（右）
    for x in (180, 1420):
        _bike(d, x, 700, 0.95, col=(150, 150, 156))
    d.rectangle([560, 280, 1360, 720], fill=(150, 126, 96))                     # 店先の柱間
    _bike(d, 760, 720, 1.25)
    if night:
        img = _tint(img, (10, 20, 60), 110)
    head = (760 + 200 * 1.25 - 30 * 1.25, 720 - 70 * 1.25 - 120 * 1.25)
    _bullet_lamp(img, int(head[0]) + 20, int(head[1]) + 4, 0.9, lit=True, beam=night)
    d = _d(img)
    d.rectangle([0, 720, W, H], fill=(150, 140, 126) if not night else (70, 70, 84))  # 通り
    d.line([(0, 720), (W, 720)], fill=_shade((150, 140, 126), 0.8), width=6)
    if night:
        _glow(img, 1080, 560, 260, (255, 236, 160), 60)
        d = _d(img)
        for x, y in ((240, 60), (520, 90), (1400, 70), (1700, 50)):
            d.ellipse([x, y, x + 6, y + 6], fill=(230, 230, 250))
    return img


def jitenshaya():
    return _jitenshaya()


def jitenshaya_yoru():
    return _jitenshaya(night=True)


# ---------------------------------------------------------------- 1929年
def byosho():
    """病床の座敷。床の間に掛け軸、枕元に薬の盆、敷いた布団。"""
    img = _japanese_room(wall=(208, 196, 172))
    d = _d(img)
    d.rectangle([1340, 170, 1700, 720], fill=(186, 170, 140))                   # 床の間
    d.rectangle([1340, 690, 1700, 720], fill=WOOD)
    _scroll(d, 1520, 220, h=340)
    _ikebana(d, 1440, 690)
    _shoji(d, 230, 190, 700, 700, paper=(230, 222, 200))
    _futon(d, 830, 800, w=500)
    d.rectangle([1100, 700, 1200, 720], fill=(110, 80, 54))                     # 薬の盆
    d.ellipse([1120, 680, 1150, 702], fill=(240, 240, 236))
    d.rectangle([1164, 672, 1184, 702], fill=(140, 180, 200))
    return img


def soko():
    """第2次本店の倉庫。天井まで積み上がった在庫の箱。"""
    img = _base((178, 172, 160), (160, 154, 142))
    d = _d(img)
    for x in range(0, W, 320):                                                  # 屋根のトラス
        d.line([(x, 60), (x + 160, 10), (x + 320, 60)], fill=(110, 100, 90), width=8)
    d.rectangle([0, 56, W, 70], fill=(110, 100, 90))
    for x in (500, 1300):                                                       # 高窓
        d.rectangle([x, 90, x + 120, 150], fill=(210, 220, 226), outline=(110, 100, 90), width=6)
    d.rectangle([0, FLOOR, W, H], fill=(140, 132, 120))
    for k, (x, n) in enumerate(((-60, 5), (150, 6), (360, 5), (570, 6), (780, 7), (990, 7),
                                (1200, 6), (1410, 5), (1620, 6), (1830, 5))):
        _box_stack(d, x, FLOOR, 200, 118, n, seed=10 + k)
    return img


def soko_kara():
    """空っぽになった倉庫。床と、隅に空の台だけ。"""
    img = _base((182, 176, 164), (164, 158, 146))
    d = _d(img)
    for x in range(0, W, 320):
        d.line([(x, 60), (x + 160, 10), (x + 320, 60)], fill=(110, 100, 90), width=8)
    d.rectangle([0, 56, W, 70], fill=(110, 100, 90))
    for x in (500, 1300):
        d.rectangle([x, 90, x + 120, 150], fill=(230, 236, 240), outline=(110, 100, 90), width=6)
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon([(x, 150), (x + 120, 150), (x + 320, FLOOR), (x - 160, FLOOR)], fill=(255, 250, 230, 40))
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(20)))
    d = _d(img)
    for x in range(140, W, 300):                                                # 壁の柱
        d.rectangle([x, 70, x + 30, FLOOR], fill=(150, 140, 126))
    d.rectangle([0, FLOOR, W, H], fill=(140, 132, 120))
    d.rectangle([880, 690, 1040, 720], fill=(150, 120, 86))                     # 空の台
    return img


# ---------------------------------------------------------------- 1932年
def tenri():
    """大きな本殿を望む製材所。献木の丸太の山。"""
    img = vgrad((W, H), (170, 200, 226), (226, 228, 218)).convert("RGBA")
    d = _d(img)
    _mountains(d, 360, cols=((150, 170, 150),), seed=12)
    d.rectangle([420, 230, 1500, 420], fill=(170, 140, 100))                    # 大きな殿舎
    d.polygon([(300, 260), (960, 90), (1620, 260)], fill=(70, 70, 80))
    d.polygon([(360, 250), (960, 110), (1560, 250)], fill=(90, 90, 100))
    for x in range(470, 1480, 90):
        d.rectangle([x, 270, x + 22, 420], fill=(130, 100, 70))
    d.rectangle([0, 420, W, H], fill=(196, 182, 150))                           # 製材所の地面
    d.polygon([(1300, 330), (1900, 330), (1900, 520), (1300, 520)], fill=(130, 110, 86))  # 製材の小屋
    d.polygon([(1260, 340), (1600, 250), (1940, 340)], fill=(90, 80, 70))
    for row in range(5):                                                        # 丸太の山（中央）
        n = 7 - row
        for j in range(n):
            cx = 1290 - (n - 1) * 46 + j * 92
            cy = 680 - row * 74
            d.ellipse([cx - 44, cy - 38, cx + 44, cy + 38], fill=(200, 160, 110), outline=(130, 96, 60), width=5)
            d.ellipse([cx - 22, cy - 18, cx + 22, cy + 18], outline=(170, 130, 86), width=3)
    _carriers(d, 330, 600, 0.72, coat=(70, 60, 100))                            # 材木を運ぶ人たち
    _carriers(d, 60, 720, 0.95)
    _carriers(d, 1610, 712, 0.86, coat=(90, 60, 56))
    return img


def kodo():
    """中央電気倶楽部の講堂。演壇と幕、横にドラ。"""
    img = _base((200, 186, 160), (180, 166, 140))
    wood_floor(img, FLOOR, col=(120, 90, 64), line=(100, 74, 52))
    d = _d(img)
    d.rectangle([380, 60, 1540, 640], fill=(120, 40, 40))                       # 幕
    for x in range(400, 1540, 60):
        d.line([(x, 60), (x, 640)], fill=(100, 30, 30), width=6)
    d.polygon([(380, 60), (1540, 60), (1540, 140), (380, 140)], fill=(150, 120, 60))
    d.rectangle([300, 600, 1620, 700], fill=(140, 104, 70))                     # 壇
    d.rectangle([300, 600, 1620, 616], fill=(170, 130, 90))
    d.rectangle([900, 470, 1100, 600], fill=(110, 80, 54))                      # 演壇
    d.rectangle([890, 460, 1110, 480], fill=(140, 104, 70))
    gx = 660                                                                    # ドラ（キャラの間に見える位置）
    d.rectangle([gx, 360, gx + 16, 600], fill=(90, 70, 50))
    d.rectangle([gx + 176, 360, gx + 192, 600], fill=(90, 70, 50))
    d.line([(gx, 370), (gx + 192, 370)], fill=(90, 70, 50), width=8)
    d.ellipse([gx + 28, 384, gx + 164, 520], fill=(196, 160, 70), outline=(150, 110, 40), width=6)
    d.ellipse([gx + 68, 424, gx + 124, 480], outline=(220, 190, 100), width=4)
    for x in (200, 1720):                                                       # 花
        _ikebana(d, x, 600)
    return img


# ---------------------------------------------------------------- 戦時・戦後
def zosen():
    """木造船の造船所。船台に組みかけの木の船、奥に海。"""
    img = vgrad((W, H), (160, 168, 176), (200, 200, 196)).convert("RGBA")
    d = _d(img)
    d.rectangle([0, 360, W, 470], fill=(100, 118, 130))                         # 海
    for y in range(380, 470, 24):
        d.line([(0, y), (W, y)], fill=(116, 134, 146), width=3)
    d.rectangle([0, 470, W, H], fill=(170, 160, 140))                           # 造船所の地面
    for x in (200, 1720):                                                       # 足場
        for y in range(240, 700, 80):
            d.line([(x - 60, y), (x + 60, y)], fill=WOOD_D, width=8)
        d.line([(x - 60, 220), (x - 60, 720)], fill=WOOD_D, width=10)
        d.line([(x + 60, 220), (x + 60, 720)], fill=WOOD_D, width=10)
    # 組みかけの船体（中央）
    d.polygon([(560, 420), (1360, 420), (1300, 640), (640, 640)], fill=(170, 130, 86))
    d.polygon([(1360, 420), (1460, 360), (1300, 640)], fill=(150, 112, 74))
    for y in range(440, 640, 34):
        d.line([(560 + (y - 420) * 0.36, y), (1360 - (y - 420) * 0.27, y)], fill=(130, 96, 60), width=4)
    for x in range(640, 1300, 70):                                              # 肋材
        d.line([(x, 300), (x, 420)], fill=(150, 112, 74), width=10)
    d.line([(600, 300), (1340, 300)], fill=(150, 112, 74), width=10)
    d.rectangle([600, 640, 1340, 680], fill=(110, 90, 70))                      # 船台
    return img


def kokaido():
    """中之島の中央公会堂の大ホール。アーチの舞台、2階席まで満員。"""
    img = _base((150, 90, 70), (120, 70, 56))
    wood_floor(img, FLOOR, col=(110, 80, 60), line=(90, 64, 48))
    d = _d(img)
    d.rectangle([0, 330, W, 380], fill=(110, 64, 50))                           # 2階席の手すり
    rnd = random.Random(31)
    for row, (y0, off) in enumerate(((262, 17), (300, 0))):                    # 2階席の頭（2列）
        for x in range(-10 + off, W, 34):
            y = y0 + rnd.randint(-6, 6)
            d.ellipse([x, y, x + 30, y + 34], fill=(56, 46, 42) if row == 0 else (40, 34, 32))
    d.rectangle([520, 120, 1400, 700], fill=(210, 190, 150))                    # 舞台のアーチ
    d.pieslice([520, 20, 1400, 300], 180, 360, fill=(210, 190, 150))
    d.rectangle([570, 170, 1350, 700], fill=(70, 40, 34))
    d.pieslice([570, 70, 1350, 300], 180, 360, fill=(70, 40, 34))
    d.rectangle([640, 240, 1280, 300], fill=(236, 230, 214))                    # 垂れ幕（無地）
    d.rectangle([600, 640, 1320, 700], fill=(140, 100, 70))                     # 舞台の縁
    d.rectangle([900, 540, 1020, 640], fill=(110, 80, 54))                      # 演台
    for x in (120, 1680):                                                       # 壁の柱
        d.rectangle([x, 380, x + 120, FLOOR], fill=(170, 110, 86))
    return img


def jimusho():
    """戦後の社長室。机と書類棚、窓の外は灰色の町。"""
    img = _base((214, 210, 200), (196, 192, 182))
    wood_floor(img, FLOOR, col=(120, 104, 86), line=(100, 86, 70))
    d = _d(img)
    _window(d, 760, 120, 1160, 420, sky=(170, 176, 182), bars=1)
    for k in range(4):                                                          # 外の焼け跡の町
        x = 770 + k * 100
        d.rectangle([x, 330 - k % 2 * 40, x + 70, 420], fill=(120, 120, 124))
    for k, y in enumerate((200, 330, 460)):                                     # 書類棚（右）
        d.rectangle([1440, y + 100, 1820, y + 114], fill=WOOD_D)
        for j in range(7):
            d.rectangle([1452 + j * 52, y + 20, 1494 + j * 52, y + 100], fill=((190, 180, 150), (150, 150, 130))[(j + k) % 2])
    _bench(d, 640, 1280, 600, col=(110, 80, 56))
    d.rectangle([700, 570, 820, 600], fill=(236, 232, 220), outline=(170, 160, 140), width=2)
    d.rectangle([1160, 540, 1200, 600], fill=(40, 40, 44))                      # 電話
    return img


def jimusho_tangan():
    """社長室に、組合が集めた嘆願書の束が積み上がる。"""
    img = jimusho()
    d = _d(img)
    for k in range(5):                                                          # 机の上の山
        _paper_bundle(d, 660 + k * 120, 600, 110, 90 + (k % 3) * 40)
    for k in range(4):
        _paper_bundle(d, 700 + k * 130, 600 - 140, 110, 70 + (k % 2) * 30)
    for x in (130, 260, 1440, 1570, 1700):                                      # 壁ぎわにも
        for j in range(3):
            _paper_bundle(d, x, 720 - j * 100, 110, 90)
    return img


def niwa():
    """1948年の秋の夜。友人宅の庭の築山と、縁側のすき焼き。"""
    img = vgrad((W, H), (20, 26, 50), (44, 40, 52)).convert("RGBA")
    d = _d(img)
    d.ellipse([1540, 90, 1620, 170], fill=(240, 232, 200))                      # 月
    d.ellipse([-200, 380, 900, 900], fill=(50, 70, 56))                         # 築山
    d.ellipse([-100, 420, 760, 860], fill=(60, 82, 64))
    for x, y, r in ((160, 600, 50), (420, 560, 40), (300, 680, 34)):            # 庭石
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(110, 110, 110))
    d.rectangle([240, 430, 270, 520], fill=(130, 126, 120))                     # 灯籠
    d.rectangle([210, 400, 300, 432], fill=(130, 126, 120))
    d.polygon([(200, 400), (310, 400), (255, 360)], fill=(110, 106, 100))
    for x, y, col in ((1720, 260, (190, 60, 40)), (1640, 320, (210, 100, 40)), (1800, 330, (180, 50, 40))):  # 紅葉
        d.ellipse([x - 90, y - 60, x + 90, y + 60], fill=col)
    d.rectangle([1700, 380, 1720, 720], fill=(70, 50, 40))
    # 縁側と障子の明かり（中央の奥）
    d.rectangle([620, 230, 1340, 600], fill=(240, 210, 150))
    _shoji(d, 620, 230, 1340, 600, paper=(246, 220, 160), frame=(110, 84, 60), cols=6, rows=4)
    _glow(img, 980, 460, 460, (255, 200, 120), 70)
    d = _d(img)
    d.rectangle([560, 600, 1400, 640], fill=(120, 90, 60))                      # 縁側
    d.ellipse([860, 560, 1100, 620], fill=(40, 40, 44))                         # すき焼き鍋
    d.ellipse([880, 566, 1080, 606], fill=(150, 90, 60))
    for k in range(3):
        d.line([(920 + k * 50, 560), (930 + k * 50, 500)], fill=(240, 240, 240, 140), width=6)
    d.rectangle([0, 720, W, H], fill=(40, 46, 40))
    return img


# ---------------------------------------------------------------- 1964年以降
def atami():
    """熱海のホテルの大広間。高い壇に金屏風、窓の外に海。"""
    img = _base((220, 210, 190), (200, 190, 170))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(150, 60, 56))                           # 絨毯
    for y in range(FLOOR + 20, H, 40):
        d.line([(0, y), (W, y)], fill=(130, 50, 46), width=3)
    for x in (100, 1600):                                                       # 海の見える窓
        _window(d, x, 160, x + 220, 520, sky=(150, 190, 220), frame=(150, 130, 100), bars=1)
        d.rectangle([x + 12, 380, x + 208, 508], fill=(70, 120, 170))
    for x in (520, 1400):                                                       # シャンデリア
        d.line([(x, 0), (x, 80)], fill=(150, 130, 90), width=4)
        _glow(img, x, 120, 160, (255, 230, 170), 70)
        d = _d(img)
        for k in range(5):
            d.ellipse([x - 70 + k * 30, 100, x - 50 + k * 30, 130], fill=(255, 240, 200))
    d.rectangle([520, 600, 1400, 720], fill=(130, 96, 66))                      # 高い壇
    d.rectangle([520, 600, 1400, 620], fill=(160, 120, 84))
    for k in range(6):                                                          # 金屏風
        x = 600 + k * 120
        d.polygon([(x, 220), (x + 120, 220 + (k % 2) * 16), (x + 120, 600 + (k % 2) * 0), (x, 600)],
                  fill=(214, 180, 90) if k % 2 else (196, 162, 76))
    d.rectangle([600, 210, 1320, 226], fill=(90, 60, 40))
    d.line([(960, 600), (960, 470)], fill=(60, 60, 64), width=6)                # マイク
    d.ellipse([948, 450, 972, 478], fill=(60, 60, 64))
    return img


def taiikukan():
    """枚方の体育館の式典。紅白幕の舞台、天井のトラス。"""
    img = _base((214, 214, 206), (196, 196, 188))
    wood_floor(img, FLOOR, col=(196, 160, 110), line=(176, 140, 96))
    d = _d(img)
    for x in range(-100, W, 240):                                               # トラス
        d.line([(x, 40), (x + 240, 40)], fill=(150, 150, 150), width=8)
        d.line([(x, 40), (x + 120, 110), (x + 240, 40)], fill=(150, 150, 150), width=5)
    d.line([(0, 110), (W, 110)], fill=(150, 150, 150), width=6)
    d.rectangle([340, 220, 1580, 620], fill=(236, 226, 200))                    # 舞台の奥
    for k, x in enumerate(range(340, 1580, 60)):                                # 紅白幕
        d.rectangle([x, 520, x + 60, 640], fill=(200, 50, 50) if k % 2 else (250, 250, 250))
    d.rectangle([340, 200, 1580, 240], fill=(120, 40, 40))
    for x in (480, 1440):                                                       # 花
        _ikebana(d, x, 520)
    d.rectangle([860, 400, 1060, 520], fill=(140, 104, 70))                     # 演台
    d.rectangle([300, 640, 1620, 700], fill=(150, 116, 80))                     # 舞台の縁
    return img


def zashiki():
    """晩年の自宅の座敷。床の間の花と、ガラス戸の外の庭。"""
    img = _japanese_room(wall=(222, 210, 184))
    d = _d(img)
    d.rectangle([220, 170, 1000, 700], fill=(150, 196, 140))                    # 庭（ガラス戸）
    for k in range(6):
        d.ellipse([240 + k * 130, 300 + (k % 2) * 60, 380 + k * 130, 460 + (k % 2) * 60], fill=(96, 150, 96))
    d.ellipse([500, 560, 720, 640], fill=(140, 140, 136))
    for x in range(220, 1001, 195):
        d.line([(x, 170), (x, 700)], fill=(130, 100, 70), width=10)
    d.rectangle([220, 170, 1000, 700], outline=(130, 100, 70), width=12)
    d.rectangle([1260, 170, 1700, 720], fill=(196, 180, 150))                   # 床の間
    d.rectangle([1260, 690, 1700, 720], fill=WOOD)
    _scroll(d, 1480, 220, h=330)
    _ikebana(d, 1360, 690)
    d.rectangle([1040, 640, 1220, 660], fill=(120, 84, 54))                     # 茶托と湯のみ
    d.rectangle([1070, 610, 1100, 640], fill=(110, 140, 120))
    d.rectangle([1150, 610, 1180, 640], fill=(110, 140, 120))
    return img


def byoin():
    """1989年の病室。白いベッドと点滴、春の窓。"""
    img = _base((236, 238, 236), (222, 226, 224))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(206, 210, 206))
    _window(d, 1300, 140, 1740, 500, sky=(200, 224, 240), frame=(230, 232, 230), bars=1)
    for x, y in ((1360, 400), (1440, 360), (1560, 420), (1660, 380)):           # 窓の外の桜
        d.ellipse([x - 50, y - 40, x + 50, y + 40], fill=(244, 200, 210))
    d.rectangle([1260, 120, 1300, 640], fill=(210, 220, 226))                   # カーテン
    # ベッド（中央の奥）
    d.rectangle([700, 560, 1240, 640], fill=(250, 250, 250), outline=(200, 204, 206), width=4)
    d.rectangle([700, 640, 1240, 680], fill=(180, 190, 196))
    d.rectangle([690, 460, 720, 700], fill=(170, 180, 186))
    d.rounded_rectangle([730, 530, 880, 572], radius=14, fill=(255, 255, 255), outline=(210, 210, 214), width=3)
    d.rectangle([600, 200, 610, 700], fill=(170, 176, 180))                     # 点滴台
    d.rounded_rectangle([570, 210, 640, 300], radius=10, fill=(220, 236, 244), outline=(170, 180, 186), width=3)
    d.line([(605, 300), (720, 540)], fill=(190, 200, 206), width=3)
    return img


def ronsou():
    """二股ソケットは発明か。二灯用差込みプラグの簡略図と、はてなの札。キャラの間に収める。"""
    img = vgrad((W, H), (242, 238, 228), (224, 222, 212)).convert("RGBA")
    d = _d(img)
    cx = 960
    # ねじ込み口（天井の電灯のソケットに入る側）
    d.rectangle([cx - 46, 150, cx + 46, 250], fill=(200, 184, 120), outline=INK, width=4)
    for y in range(162, 250, 18):
        d.line([(cx - 46, y), (cx + 46, y + 8)], fill=(150, 130, 70), width=4)
    d.rounded_rectangle([cx - 120, 250, cx + 120, 420], radius=30, fill=SOCKET, outline=INK, width=5)   # 胴
    d.rounded_rectangle([cx + 110, 330, cx + 230, 400], radius=14, fill=SOCKET, outline=INK, width=5)   # 横の差し込み口
    d.rectangle([cx + 214, 350, cx + 230, 380], fill=(60, 50, 44))
    d.rectangle([cx - 40, 420, cx + 40, 470], fill=(200, 184, 120), outline=INK, width=4)                # 下の電球口
    d.ellipse([cx - 70, 460, cx + 70, 600], fill=(250, 246, 220), outline=INK, width=4)
    _text_c(d, cx, 640, "二灯用差込みプラグ", 52, INK)
    _text_c(d, cx, 712, "（形を簡略にした図）", 32, (110, 104, 96))
    for k, x in enumerate((620, 1300)):                                         # はてなの札
        d.rounded_rectangle([x - 70, 200 + k * 40, x + 70, 380 + k * 40], radius=16, fill=(250, 248, 240), outline=INK, width=4)
        _text_c(d, x, 230 + k * 40, "？", 100, (200, 70, 60))
    return img


def densha():
    """1932年、帰りの電車の車内。長い座席と吊り革、窓の外に夕方の田畑。"""
    img = _base((206, 192, 160), (184, 168, 136))
    d = _d(img)
    d.rectangle([0, 0, W, 110], fill=(226, 218, 196))                           # 天井
    d.line([(0, 110), (W, 110)], fill=(150, 130, 100), width=6)
    for x in range(240, W, 480):                                                # 天井の電灯
        _glow(img, x, 70, 120, (255, 226, 160), 60)
        d = _d(img)
        d.ellipse([x - 26, 46, x + 26, 92], fill=(255, 240, 200))
    d.rectangle([0, 150, W, 162], fill=(150, 130, 100))                         # 網棚
    for x in range(60, W, 120):
        d.line([(x, 162), (x, 176)], fill=(150, 130, 100), width=3)
    for x in range(120, W, 160):                                                # 吊り革
        d.line([(x, 176), (x, 230)], fill=(110, 96, 80), width=4)
        d.ellipse([x - 16, 226, x + 16, 258], outline=(236, 230, 214), width=6)
    for k, x0 in enumerate(range(20, W, 300)):                                  # 窓と外の夕景
        x1 = x0 + 250
        sky = vgrad((x1 - x0, 300), (236, 170, 110), (180, 130, 140)).convert("RGBA")
        img.alpha_composite(sky, (x0, 280))
        d = _d(img)
        d.polygon([(x0, 520), (x0 + 90, 470), (x0 + 180, 500), (x1, 480), (x1, 580), (x0, 580)], fill=(110, 96, 110))
        d.rectangle([x0, 540, x1, 580], fill=(120, 130, 90))
        for j in range(3):                                                      # 流れていく景色の線
            y = 300 + j * 40 + (k % 2) * 16
            d.line([(x0 + 20, y), (x0 + 140, y)], fill=(255, 236, 210, 120), width=3)
        d.rectangle([x0, 280, x1, 580], outline=(110, 80, 52), width=12)
    d.rectangle([0, 600, W, 640], fill=(70, 110, 80))                           # 座席の背
    d.rectangle([0, 640, W, 700], fill=(60, 96, 70))                            # 座席
    d.rectangle([0, 700, W, 760], fill=(90, 64, 44))
    d.rectangle([0, 760, W, H], fill=(124, 96, 70))                             # 床
    for x in range(0, W, 140):
        d.line([(x, 760), (x - 60, H)], fill=(108, 82, 58), width=3)
    return img


def butsuma():
    """母の死を聞く仏間。扉を開いた仏壇、ろうそくと白い菊。"""
    img = _japanese_room(wall=(150, 140, 124), wall2=(126, 118, 104))
    d = _d(img)
    _shoji(d, 200, 200, 560, 700, paper=(196, 188, 168))
    cx = 1220
    d.rectangle([cx - 230, 600, cx + 230, 640], fill=WOOD_D)                     # 仏壇の台
    d.rectangle([cx - 180, 230, cx + 180, 600], fill=(50, 34, 24), outline=(170, 140, 70), width=8)
    d.rectangle([cx - 150, 260, cx + 150, 580], fill=(30, 22, 16))
    d.polygon([(cx - 180, 230), (cx - 280, 260), (cx - 280, 590), (cx - 180, 600)], fill=(60, 42, 30))   # 開いた扉
    d.polygon([(cx + 180, 230), (cx + 280, 260), (cx + 280, 590), (cx + 180, 600)], fill=(60, 42, 30))
    for k, h in enumerate((120, 150, 120)):                                     # 位牌
        x = cx - 75 + k * 60
        d.rectangle([x, 540 - h, x + 34, 540], fill=(24, 18, 12), outline=(200, 170, 90), width=3)
    for x in (cx - 120, cx + 100):                                              # ろうそく
        d.rectangle([x, 470, x + 18, 540], fill=(244, 240, 228))
        _glow(img, x + 9, 455, 70, (255, 200, 120), 110)
        d = _d(img)
        d.ellipse([x + 3, 440, x + 15, 466], fill=(255, 210, 120))
    for x in (cx - 250, cx + 230):                                              # 白い菊
        d.rectangle([x - 6, 520, x + 24, 600], fill=(90, 100, 110))
        for dx, dy in ((-20, -40), (10, -60), (36, -36), (4, -20)):
            d.ellipse([x + dx - 14, 520 + dy - 14, x + dx + 14, 520 + dy + 14], fill=(244, 244, 236))
    for k in range(3):                                                          # 線香の煙
        d.line([(cx - 4 + k * 4, 420 - k * 40), (cx + 10 - k * 4, 380 - k * 40)], fill=(220, 220, 220, 120), width=4)
    return _vignette(img, 80)


def ie():
    """1926年ごろの住まいの座敷。床の間と障子、吊り下げの電灯。"""
    img = _japanese_room(wall=(218, 204, 178))
    d = _d(img)
    _shoji(d, 200, 190, 640, 700, paper=(240, 232, 210))
    d.rectangle([1300, 170, 1720, 720], fill=(196, 180, 150))                   # 床の間
    d.rectangle([1300, 690, 1720, 720], fill=WOOD)
    _scroll(d, 1510, 220, h=320)
    _ikebana(d, 1400, 690)
    d.rectangle([780, 560, 1120, 720], fill=(120, 84, 56))                      # 茶箪笥
    d.rectangle([790, 570, 1110, 640], fill=(100, 70, 46))
    for x in (900, 1000):
        d.ellipse([x, 670, x + 16, 686], fill=(200, 170, 90))
    d.ellipse([920, 500, 980, 560], fill=(110, 140, 120))                       # 花瓶
    d.line([(950, 0), (950, 220)], fill=(60, 50, 40), width=4)                  # 電灯
    d.polygon([(890, 220), (1010, 220), (980, 180), (920, 180)], fill=(236, 226, 196))
    _glow(img, 950, 250, 200, (255, 220, 150), 60)
    d = _d(img)
    d.ellipse([934, 216, 966, 248], fill=(255, 240, 200))
    return img


LOCATIONS = {
    "pn_heya": heya, "pn_gendai": gendai,
    "pn_wasa": wasa, "pn_nagaya": nagaya, "pn_kinokawa": kinokawa,
    "pn_hibachi": hibachi, "pn_godai": godai, "pn_tenma": tenma, "pn_kaya": kaya, "pn_shiden": shiden,
    "pn_dento": dento, "pn_dento_jimu": dento_jimu, "pn_yachiyoza": yachiyoza, "pn_nikai": nikai,
    "pn_ikaino": ikaino, "pn_ikaino_yama": ikaino_yama, "pn_ikaino_yoru": ikaino_yoru,
    "pn_ohiraki": ohiraki, "pn_ohiraki_tana": ohiraki_tana,
    "pn_tonya_tokyo": tonya_tokyo, "pn_tonya_osaka": tonya_osaka,
    "pn_jitenshaya": jitenshaya, "pn_jitenshaya_yoru": jitenshaya_yoru,
    "pn_byosho": byosho, "pn_soko": soko, "pn_soko_kara": soko_kara,
    "pn_tenri": tenri, "pn_kodo": kodo, "pn_zosen": zosen, "pn_kokaido": kokaido,
    "pn_jimusho": jimusho, "pn_jimusho_tangan": jimusho_tangan, "pn_niwa": niwa,
    "pn_atami": atami, "pn_taiikukan": taiikukan, "pn_zashiki": zashiki, "pn_byoin": byoin,
    "pn_ronsou": ronsou, "pn_densha": densha, "pn_butsuma": butsuma, "pn_ie": ie,
}

CARDS = ["1894", "1904", "1910", "1915", "1917", "1918", "1923", "1929", "1932", "1946", "1964"]


def year_card(text: str) -> Image.Image:
    """黒地に年号だけのカード。キャラと同居させない単独シーンで使う。"""
    img = Image.new("RGB", (W, H), (18, 18, 20))
    d = ImageDraw.Draw(img)
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
        fn().convert("RGB").save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for y in CARDS:
        if only and f"pn_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"pn_card_{y}.png")
        print(f"生成完了: pn_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
