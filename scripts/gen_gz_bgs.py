#!/usr/bin/env python3
"""ゴジラの誕生・円谷英二回（75_ゴジラの誕生 / slug=godzilla-tsuburaya）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はファミコン回（gen_famicom_bgs.py）と同じ。
フラットな絵に黒っぽい細い輪郭、やわらかい色でそろえる。

著作権まわりの決まり:
  - ゴジラやウルトラマン（科学特捜隊も）の姿・顔・背びれ・配色・ロゴ・ポーズは描かない。
    着ぐるみは「黒っぽい大きなゴムの塊」「布をかぶせた大きな何か」にとどめる。
  - 実在のロゴ・店名・劇場名は描かない（看板は無地）。軍艦や旗に国籍の記号を描かない。

立ち絵は左 x≈0.28・右 x≈0.7（現代パートは 0.2 / 0.8）に立ち、頭が y≈220 まで来る。
細かい物は、立ち絵の間（x 770〜1120）・画面の上側・左右の端に置き、
下3分の1（y>720）と立ち絵の後ろには大きな面だけを置く。
左上（x<620, y<130）は章タイトルの帯が出るので空けておく。

実行: PYTHONPATH=. python scripts/gen_gz_bgs.py [名前...]
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

FLOOR = 880
INK = (64, 58, 64)          # 輪郭の色
SOFT_INK = (150, 158, 176)  # 雲など、輪郭を弱くしたい物
OW = 3


# ================================================================ 共通の部品
def _d(img):
    return ImageDraw.Draw(img)


def _font(size):
    from ytf.config import Config, resolve_font
    Config.load()
    return ImageFont.truetype(resolve_font("w9"), size)


def _text_c(d, cx, y, t, size, fill):
    f = _font(size)
    bb = d.textbbox((0, 0), t, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y), t, font=f, fill=fill)


def _shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def R(d, box, fill, ow=OW, r=0, ink=INK):
    """輪郭つきの四角。"""
    if r:
        d.rounded_rectangle(box, radius=r, fill=fill, outline=ink if ow else None, width=ow)
    else:
        d.rectangle(box, fill=fill, outline=ink if ow else None, width=ow)


def P(d, pts, fill, ow=OW, ink=INK):
    d.polygon(pts, fill=fill, outline=ink if ow else None, width=ow)


def E(d, box, fill, ow=OW, ink=INK):
    d.ellipse(box, fill=fill, outline=ink if ow else None, width=ow)


def Ln(d, pts, col=INK, w=OW):
    d.line(pts, fill=col, width=w, joint="curve")


def thick(d, pts, col, w, ow=OW, ink=INK):
    """輪郭つきの太い線（ケーブル・枝・鼻など）。"""
    if ow:
        d.line(pts, fill=ink, width=w + ow * 2, joint="curve")
    d.line(pts, fill=col, width=w, joint="curve")


def blob(img, shapes, fill, ow=OW, ink=INK):
    """円や多角形を合体させた形を、外側だけ輪郭で囲んで塗る（雲・木・布・ゴムの塊）。"""
    m = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(m)
    for kind, g in shapes:
        {"e": md.ellipse, "p": md.polygon, "r": md.rectangle}[kind](g, fill=255)
    bb = m.getbbox()
    if not bb:
        return
    if ow:
        x0, y0 = max(0, bb[0] - ow - 2), max(0, bb[1] - ow - 2)
        x1, y1 = min(W, bb[2] + ow + 2), min(H, bb[3] + ow + 2)
        sub = m.crop((x0, y0, x1, y1)).filter(ImageFilter.MaxFilter(ow * 2 + 1))
        img.paste(ink, (x0, y0, x1, y1), sub)
    img.paste(fill, (0, 0, W, H), m)


def alpha(img, fn, blur=0):
    """半透明の形（光の筋・ほこり・にじみ）を重ねる。fn は RGBA の Draw を受け取って描く。"""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(lay))
    if blur:
        lay = lay.filter(ImageFilter.GaussianBlur(blur))
    rgba = img.convert("RGBA")
    rgba.alpha_composite(lay)
    img.paste(rgba.convert("RGB"))


def _glow(img, cx, cy, r, color, a=110):
    rgba = img.convert("RGBA")
    glow(rgba, int(cx), int(cy), int(r), color, a)
    img.paste(rgba.convert("RGB"))


def _band(img, y0, y1, top, bottom, x0=0, x1=W):
    img.paste(vgrad((x1 - x0, y1 - y0), top, bottom), (x0, y0))


def _cloud(img, cx, cy, s=1.0, col=(250, 250, 248), ink=SOFT_INK, ow=OW):
    blob(img, [("e", [cx - 120 * s, cy - 26 * s, cx + 120 * s, cy + 36 * s]),
               ("e", [cx - 84 * s, cy - 64 * s, cx + 14 * s, cy + 22 * s]),
               ("e", [cx - 14 * s, cy - 86 * s, cx + 86 * s, cy + 12 * s])], col, ow=ow, ink=ink)


def _window(d, x0, y0, x1, y1, sky=(184, 214, 236), frame=(236, 232, 224), bars=1):
    R(d, [x0, y0, x1, y1], sky)
    for k in range(1, bars + 1):
        x = x0 + (x1 - x0) * k / (bars + 1)
        d.line([(x, y0), (x, y1)], fill=frame, width=10)
    R(d, [x0, y0, x1, y1], None, ow=12, ink=frame)
    R(d, [x0 - 6, y0 - 6, x1 + 6, y1 + 6], None)


def _bulb(img, x, y, warm=True, cord_top=0):
    d = _d(img)
    d.line([(x, cord_top), (x, y)], fill=INK, width=4)
    col = (255, 214, 140) if warm else (226, 236, 246)
    _glow(img, x, y + 40, 260, col, 46)
    d = _d(img)
    R(d, [x - 14, y - 6, x + 14, y + 14], (120, 110, 96), ow=2)
    E(d, [x - 26, y + 8, x + 26, y + 66], (255, 238, 180) if warm else (236, 242, 250), ow=2)


def _clock(d, cx, cy, r, face=(246, 242, 230), rim=(120, 90, 64)):
    """数字のない壁時計。"""
    E(d, [cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8], rim)
    E(d, [cx - r, cy - r, cx + r, cy + r], face, ow=2)
    for k in range(12):
        a = k * math.pi / 6
        d.line([(cx + math.cos(a) * r * 0.78, cy + math.sin(a) * r * 0.78),
                (cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9)], fill=INK, width=2)
    d.line([(cx, cy), (cx + r * 0.1, cy - r * 0.6)], fill=INK, width=4)
    d.line([(cx, cy), (cx + r * 0.5, cy + r * 0.2)], fill=INK, width=4)


def _phone(d, x, y, s=1.0, col=(34, 34, 38)):
    """黒電話（左上が x, y）。"""
    R(d, [x, y + 30 * s, x + 130 * s, y + 90 * s], col, r=int(14 * s))
    E(d, [x + 35 * s, y + 38 * s, x + 95 * s, y + 88 * s], (206, 206, 206), ow=2)
    E(d, [x + 55 * s, y + 55 * s, x + 75 * s, y + 72 * s], col, ow=0)
    R(d, [x - 10 * s, y, x + 140 * s, y + 26 * s], col, r=int(12 * s))


def _biplane_side(d, x, y, s=1.0, body=(200, 164, 112), wing=(236, 222, 186)):
    """横から見た複葉機（模型）。x, y は機首の位置。左向き。"""
    L = 200 * s
    P(d, [(x + L - 34 * s, y - 6 * s), (x + L - 12 * s, y - 40 * s), (x + L, y - 40 * s), (x + L, y - 2 * s)], body, ow=2)
    P(d, [(x, y - 14 * s), (x + 0.3 * L, y - 20 * s), (x + L, y - 6 * s), (x + L, y + 2 * s),
          (x + 0.3 * L, y + 16 * s), (x, y + 12 * s)], body, ow=2)
    R(d, [x + L - 52 * s, y - 4 * s, x + L + 8 * s, y + 3 * s], wing, ow=2)
    for k in (0.18, 0.42):
        d.line([(x + k * L, y - 44 * s), (x + k * L, y + 10 * s)], fill=INK, width=2)
    R(d, [x + 0.1 * L, y - 54 * s, x + 0.52 * L, y - 43 * s], wing, ow=2)
    R(d, [x + 0.12 * L, y + 9 * s, x + 0.5 * L, y + 18 * s], wing, ow=2)
    R(d, [x - 9 * s, y - 34 * s, x - 2 * s, y + 30 * s], (130, 96, 64), ow=2)
    d.line([(x + 0.26 * L, y + 16 * s), (x + 0.22 * L, y + 32 * s)], fill=INK, width=3)
    E(d, [x + 0.22 * L - 11 * s, y + 24 * s, x + 0.22 * L + 11 * s, y + 46 * s], (66, 64, 66), ow=2)


def _biplane_front(d, cx, cy, s=1.0, wing=(238, 228, 198), body=(204, 176, 128)):
    """正面から見た複葉機。cy は上の翼の高さ。車輪の下は cy+186*s。"""
    span = 480 * s
    ly = cy + 86 * s
    P(d, [(cx - 6 * s, cy - 8 * s), (cx - 2 * s, cy - 66 * s), (cx + 24 * s, cy - 58 * s), (cx + 28 * s, cy - 8 * s)],
      _shade(body, 0.9))                                                          # 奥の尾翼
    R(d, [cx - span * 0.46, ly - 11 * s, cx + span * 0.46, ly + 11 * s], _shade(wing, 0.94), r=int(10 * s))
    R(d, [cx - span / 2, cy - 12 * s, cx + span / 2, cy + 12 * s], wing, r=int(10 * s))
    for k in (-0.38, -0.2, 0.2, 0.38):                                             # 支柱
        x = cx + span * k
        d.line([(x, cy + 12 * s), (x, ly - 11 * s)], fill=(110, 86, 62), width=max(3, int(7 * s)))
    for a, b in ((-0.38, -0.2), (0.2, 0.38)):                                      # 張り線
        x0, x1 = cx + span * a, cx + span * b
        d.line([(x0, cy + 12 * s), (x1, ly - 11 * s)], fill=(96, 88, 80), width=2)
        d.line([(x1, cy + 12 * s), (x0, ly - 11 * s)], fill=(96, 88, 80), width=2)
    for sx in (-1, 1):                                                             # 脚と車輪
        wx = cx + sx * 74 * s
        d.line([(cx + sx * 22 * s, ly + 24 * s), (wx, ly + 76 * s)], fill=INK, width=max(3, int(6 * s)))
        d.line([(cx + sx * 40 * s, ly), (wx, ly + 76 * s)], fill=INK, width=max(3, int(6 * s)))
        E(d, [wx - 20 * s, ly + 56 * s, wx + 20 * s, ly + 100 * s], (62, 60, 62))
        E(d, [wx - 7 * s, ly + 71 * s, wx + 7 * s, ly + 85 * s], (150, 146, 140), ow=0)
    R(d, [cx - 44 * s, cy - 20 * s, cx + 44 * s, ly + 32 * s], body, r=int(30 * s))   # 胴（正面）
    E(d, [cx - 32 * s, cy + 8 * s, cx + 32 * s, cy + 72 * s], (126, 122, 118))          # エンジン
    E(d, [cx - 10 * s, cy - 70 * s, cx + 10 * s, cy + 150 * s], (156, 114, 72))          # プロペラ
    E(d, [cx - 12 * s, cy + 28 * s, cx + 12 * s, cy + 52 * s], (90, 90, 96), ow=2)


def _cbox(d, x, by, w, h, col=(212, 176, 128), wins=True, door=False):
    """段ボールのビル（左下が x, by）。"""
    dx, dy = int(w * 0.3), int(w * 0.18)
    P(d, [(x + w, by - h), (x + w + dx, by - h - dy), (x + w + dx, by - dy), (x + w, by)], _shade(col, 0.8))
    P(d, [(x, by - h), (x + dx, by - h - dy), (x + w + dx, by - h - dy), (x + w, by - h)], _shade(col, 1.1))
    R(d, [x, by - h, x + w, by], col)
    d.line([(x + dx / 2 + w / 2, by - h - dy / 2), (x + w / 2 + dx / 2 + 1, by - h - dy / 2)], fill=_shade(col, 0.9), width=1)
    mk = (118, 88, 62)
    if wins and w >= 60 and h >= 70:
        cols = max(1, int((w - 16) // 36))
        rows = max(1, int((h - (78 if door else 40)) // 46))
        gx = (w - cols * 20) / (cols + 1)
        for r in range(rows):
            for c in range(cols):
                wx = x + gx + c * (20 + gx)
                wy = by - h + 18 + r * 46
                d.rectangle([wx, wy, wx + 20, wy + 24], fill=mk)
    if door:
        d.rectangle([x + w / 2 - 14, by - 42, x + w / 2 + 14, by - 2], fill=mk)


def _person(d, x, y, s=1.0, coat=(70, 74, 92), hat=(54, 50, 56), skin=(230, 204, 178)):
    """帽子と外套の人（足元の中心が x, y）。小さい人は輪郭なし。"""
    o = 2 if s >= 0.55 else 0
    d.rectangle([x - 12 * s, y - 40 * s, x - 3 * s, y], fill=(52, 50, 56))
    d.rectangle([x + 3 * s, y - 40 * s, x + 12 * s, y], fill=(52, 50, 56))
    P(d, [(x - 19 * s, y - 108 * s), (x + 19 * s, y - 108 * s), (x + 26 * s, y - 34 * s), (x - 26 * s, y - 34 * s)], coat, ow=o)
    E(d, [x - 12 * s, y - 134 * s, x + 12 * s, y - 106 * s], skin, ow=o)
    if hat:
        d.ellipse([x - 20 * s, y - 132 * s, x + 20 * s, y - 122 * s], fill=hat)
        d.rounded_rectangle([x - 12 * s, y - 146 * s, x + 12 * s, y - 126 * s], radius=int(5 * s) + 1, fill=hat)


def _bldg(d, x0, y0, x1, y1, col, win=(214, 222, 230), ow=OW, ww=22, wh=26, gx=40, gy=50, lit=None, rnd=None):
    """窓の並んだビル。lit=(色, 確率) で一部の窓を灯す。"""
    R(d, [x0, y0, x1, y1], col, ow=ow)
    y = y0 + 18
    while y + wh < y1 - 12:
        x = x0 + 14
        while x + ww < x1 - 10:
            c = win
            if lit and rnd and rnd.random() < lit[1]:
                c = lit[0]
            d.rectangle([x, y, x + ww, y + wh], fill=c)
            x += gx
        y += gy


def _house(d, x, by, w, h, wall=(206, 190, 160), roof=(92, 100, 116)):
    """瓦屋根の小さな家（正面）。"""
    R(d, [x, by - h, x + w, by], wall)
    P(d, [(x - 16, by - h + 6), (x + w + 16, by - h + 6), (x + w - 12, by - h - 34), (x + 12, by - h - 34)], roof)
    d.line([(x - 10, by - h - 2), (x + w + 10, by - h - 2)], fill=_shade(roof, 0.8), width=3)
    R(d, [x + w * 0.2, by - h * 0.62, x + w * 0.42, by - h * 0.25], (110, 86, 62), ow=2)


def _vignette(img, a=40):
    alpha(img, lambda dd: (dd.rectangle([0, 0, W, H], fill=(10, 8, 14, a)),
                           dd.ellipse([-260, -220, W + 260, H + 300], fill=(0, 0, 0, 0))), blur=140)


# ================================================================ 場所
def stage():
    """1954年の撮影所のステージ。高い天井と照明の足場、床に角材1本、壁際に黒いゴムの塊。"""
    img = vgrad((W, H), (98, 94, 102), (82, 78, 86))
    d = _d(img)
    d.rectangle([0, 0, W, 236], fill=(62, 62, 72))                              # 高い天井
    for x in range(-160, W + 320, 320):                                         # 鉄骨のトラス
        d.line([(x, 0), (x + 160, 64), (x + 320, 0)], fill=(100, 100, 112), width=6)
    d.line([(0, 64), (W, 64)], fill=(100, 100, 112), width=8)
    R(d, [-10, 148, W + 10, 166], (132, 122, 110))                              # 照明の足場
    R(d, [-10, 214, W + 10, 230], (132, 122, 110))
    for x in range(0, W, 72):
        d.line([(x, 166), (x + 36, 214), (x + 72, 166)], fill=(112, 104, 96), width=4)
    for x in range(60, W, 140):                                                 # 板壁
        d.line([(x, 236), (x, FLOOR)], fill=(90, 86, 94), width=4)
    d.rectangle([0, 600, W, 612], fill=(88, 84, 90))
    wood_floor(img, FLOOR, col=(122, 108, 96), line=(106, 94, 84))
    d = _d(img)
    alpha(img, lambda dd: (dd.polygon([(690, 320), (750, 320), (1080, FLOOR + 60), (720, FLOOR + 60)], fill=(255, 236, 180, 30)),
                           dd.polygon([(1170, 320), (1230, 320), (1200, FLOOR + 60), (840, FLOOR + 60)], fill=(255, 236, 180, 30)),
                           dd.ellipse([700, FLOOR + 10, 1220, FLOOR + 130], fill=(255, 236, 180, 40))), blur=16)
    d = _d(img)
    for lx in (300, 720, 1200, 1640):                                           # 吊った照明
        d.line([(lx, 230), (lx, 252)], fill=INK, width=4)
        R(d, [lx - 38, 250, lx + 38, 312], (72, 72, 80), r=10)
        E(d, [lx - 30, 296, lx + 30, 326], (250, 238, 196))
    # はしご（左端）
    for (bx, tx) in ((100, 150), (190, 232)):
        thick(d, [(bx, FLOOR), (tx, 330)], (156, 122, 82), 10)
    for k in range(1, 9):
        t = k / 9
        y = FLOOR - (FLOOR - 330) * t
        d.line([(100 + 50 * t, y), (190 + 42 * t, y)], fill=(156, 122, 82), width=8)
    # 撮影用ライト（右端）
    for fx in (1720, 1840):
        d.line([(1780, 760), (fx, FLOOR)], fill=INK, width=5)
    d.line([(1780, 470), (1780, FLOOR)], fill=INK, width=6)
    R(d, [1722, 396, 1840, 478], (80, 80, 88), r=12)
    E(d, [1710, 406, 1744, 468], (250, 238, 196))
    # 着ぐるみ（形の分からない黒いゴムの塊）と台
    R(d, [756, 860, 1164, 892], (152, 120, 86))
    blob(img, [("e", [770, 600, 1150, 896]), ("e", [810, 520, 1010, 720]), ("e", [930, 560, 1120, 780]),
               ("e", [750, 740, 920, 892]), ("e", [1000, 730, 1170, 892])], (66, 66, 72))
    d = _d(img)
    for box, a0, a1 in (([836, 540, 980, 690], 200, 280), ([960, 590, 1090, 740], 210, 290),
                        ([790, 690, 930, 860], 190, 250)):
        d.arc(box, a0, a1, fill=(108, 108, 116), width=8)                        # ゴムのてかり
    for y, x0, x1 in ((760, 860, 1080), (810, 800, 1000), (840, 980, 1130)):     # たるんだしわ
        d.arc([x0, y - 24, x1, y + 24], 20, 160, fill=(46, 46, 52), width=4)
    # 床の角材1本
    P(d, [(790, 948), (1140, 948), (1164, 926), (814, 926)], (222, 186, 132))
    R(d, [790, 948, 1140, 978], (192, 154, 106))
    P(d, [(1140, 948), (1164, 926), (1164, 956), (1140, 978)], (162, 128, 88))
    return img


def heya(full=False):
    """現代の子ども部屋。床に段ボールの小さな町。full=True は部屋じゅうが段ボールの町。"""
    img = vgrad((W, H), (242, 238, 228), (230, 224, 212))
    d = _d(img)
    fy = 840
    wood_floor(img, fy, col=(202, 172, 134), line=(184, 154, 118))
    d = _d(img)
    d.rectangle([0, fy - 18, W, fy], fill=(218, 204, 184))                       # 巾木
    # 窓とカーテン
    _band(img, 130, 450, (170, 208, 238), (214, 230, 240), 760, 1160)
    _cloud(img, 900, 260, 0.6)
    _cloud(img, 1080, 360, 0.4)
    d = _d(img)
    _window(d, 760, 130, 1160, 450, sky=None, frame=(246, 244, 238))
    R(d, [680, 96, 1240, 110], (170, 150, 130), r=6)
    P(d, [(690, 110), (790, 110), (772, 470), (690, 484)], (178, 206, 224))
    P(d, [(1230, 110), (1130, 110), (1148, 470), (1230, 484)], (178, 206, 224))
    for x in (720, 750, 1170, 1200):
        d.line([(x, 120), (x - 4, 470)], fill=(150, 182, 204), width=3)
    _clock(d, 1270, 200, 34, rim=(214, 120, 100))
    # 本棚（左端）
    R(d, [30, 300, 330, fy], (198, 162, 120))
    pal = [(214, 104, 92), (96, 142, 196), (236, 196, 96), (120, 176, 124), (170, 120, 180)]
    for k, y in enumerate((330, 420, 510)):
        x = 48
        j = k
        while x < 300:
            bw = 22 + (j * 7) % 16
            R(d, [x, y, x + bw, y + 74], pal[j % len(pal)], ow=2)
            x += bw + 3
            j += 1
        d.rectangle([34, y + 74, 326, y + 86], fill=(170, 134, 96))
    R(d, [44, 600, 176, fy - 10], (210, 176, 134), ow=2)
    R(d, [184, 600, 316, fy - 10], (210, 176, 134), ow=2)
    # ベッド（右）
    R(d, [1830, 460, 1940, fy], (190, 152, 114), r=12)
    R(d, [1300, 640, 1900, fy], (190, 152, 114))
    R(d, [1300, 580, 1880, 660], (246, 246, 242), r=18)
    P(d, [(1300, 604), (1700, 604), (1740, 700), (1300, 700)], (156, 196, 220))
    E(d, [1720, 540, 1860, 612], (250, 250, 248))
    # 床のラグ
    E(d, [540, 880, 1380, 1070], (200, 218, 190))
    if not full:
        boxes =[(770, 930, 80, 130, False), (990, 940, 90, 150, False), (860, 960, 110, 210, True),
                 (1080, 968, 100, 120, False), (1180, 986, 80, 96, True), (690, 992, 70, 90, True)]
        for x, by, w, h, door in sorted(boxes, key=lambda b: b[1]):
            _cbox(d, x, by, w, h, door=door)
        return img
    rnd = random.Random(75)
    for x, w, h in ((40, 90, 80), (140, 70, 130), (220, 90, 70)):              # 本棚の上
        _cbox(d, x, 300, w, h, wins=x == 140)
    x = -30                                                                     # 壁ぎわの高いビル
    while x < W:
        w = rnd.randint(96, 150)
        h = rnd.randint(220, 360)
        if 640 < x + w and x < 1240:
            h = min(h, fy + 10 - 480)
        _cbox(d, x, fy + 10, w, h, wins=True, door=rnd.random() < 0.3)
        x += w + rnd.randint(-6, 14)
    R(d, [1830, 460, 1940, fy], (190, 152, 114), r=12)                          # ベッドをもう一度手前に
    R(d, [1300, 640, 1900, fy], (190, 152, 114))
    R(d, [1300, 580, 1880, 660], (246, 246, 242), r=18)
    for x, w, h in ((1310, 110, 150), (1430, 90, 220), (1530, 120, 120), (1660, 80, 190), (1750, 100, 140)):
        _cbox(d, x, 610, w, h, wins=True)                                       # ベッドの上の町
    for row, by in enumerate((900, 960, 1030, 1110)):                            # 床いっぱいの町
        x = -60 + (row % 2) * 70
        while x < W:
            w = rnd.randint(80, 140) + row * 14
            h = rnd.randint(70, 170) + row * 20
            center = 600 < x < 1240
            _cbox(d, x, by + rnd.randint(-8, 8), w, h, wins=center and row < 2, door=center and rnd.random() < 0.4)
            x += w + rnd.randint(20, 60)
    return img


def heya2():
    return heya(full=True)


def kura():
    """明治末の土蔵の二階。木の梁、小窓、机に水彩画と模型の複葉機と手回しの映写機。"""
    img = vgrad((W, H), (216, 202, 178), (198, 184, 160))
    d = _d(img)
    d.rectangle([0, 0, W, 150], fill=(104, 80, 60))                             # 屋根裏
    for x in range(-40, W + 40, 110):
        d.line([(x, 0), (x, 150)], fill=(86, 66, 50), width=12)
    R(d, [-10, 46, W + 10, 72], (120, 92, 66))
    top = [(x, 150 - 24 * math.sin(math.pi * x / W)) for x in range(0, W + 1, 40)]
    P(d, top + [(x, y + 50) for x, y in reversed(top)], (140, 106, 74))           # 太い梁
    d.line([(x, y + 18) for x, y in top[2:-2]], fill=(120, 90, 62), width=3)
    for x0 in (150, 1720):                                                      # 柱
        R(d, [x0, 170, x0 + 50, FLOOR], (126, 96, 68))
    d.rectangle([0, 660, W, FLOOR], fill=(152, 122, 90))                        # 腰の板壁
    for x in range(40, W, 96):
        d.line([(x, 660), (x, FLOOR)], fill=(138, 110, 80), width=4)
    d.line([(0, 660), (W, 660)], fill=INK, width=3)
    for x0 in (150, 1720):
        R(d, [x0, 170, x0 + 50, FLOOR], (126, 96, 68))
    wood_floor(img, FLOOR, col=(130, 102, 76), line=(112, 88, 64))
    d = _d(img)
    # 小窓（厚い漆喰の扉が開いている）
    R(d, [860, 222, 1060, 382], (234, 226, 208))
    R(d, [888, 248, 1032, 356], (226, 238, 244))
    for bx in (924, 960, 996):
        d.line([(bx, 248), (bx, 356)], fill=(70, 70, 76), width=8)
    P(d, [(1060, 222), (1112, 238), (1112, 398), (1060, 382)], (228, 220, 200))
    alpha(img, lambda dd: dd.polygon([(888, 356), (1032, 356), (1150, 622), (800, 622)], fill=(255, 246, 214, 50)), blur=14)
    d = _d(img)
    # 吊った模型の飛行機
    d.line([(640, 200), (640, 236)], fill=INK, width=2)
    _biplane_side(d, 576, 268, 0.64)
    # 壁にとめた水彩画2枚
    R(d, [760, 412, 920, 532], (246, 242, 230), ow=2)
    d.rectangle([772, 424, 908, 474], fill=(178, 210, 232))
    d.polygon([(772, 484), (820, 450), (860, 472), (908, 446), (908, 520), (772, 520)], fill=(142, 182, 138))
    d.ellipse([872, 430, 898, 456], fill=(246, 206, 150))
    E(d, [834, 406, 846, 418], (210, 70, 60), ow=0)
    R(d, [962, 404, 1110, 522], (246, 242, 230), ow=2)
    d.rectangle([974, 416, 1098, 468], fill=(236, 206, 176))
    d.rectangle([974, 468, 1098, 510], fill=(132, 170, 206))
    d.line([(1010, 440), (1050, 440)], fill=(90, 80, 80), width=3)              # 空の小さな飛行機
    d.line([(1012, 448), (1048, 448)], fill=(90, 80, 80), width=3)
    d.line([(1030, 434), (1030, 454)], fill=(90, 80, 80), width=3)
    E(d, [1030, 398, 1042, 410], (210, 70, 60), ow=0)
    # 机
    R(d, [740, 620, 1180, 648], (148, 108, 72))
    R(d, [752, 648, 1168, 684], (130, 94, 62))
    R(d, [762, 684, 788, FLOOR], (130, 94, 62))
    R(d, [1132, 684, 1158, FLOOR], (130, 94, 62))
    _biplane_side(d, 782, 586, 0.7)                                             # 机の上の模型
    px = 980                                                                    # 手回しの映写機
    for cx in (px + 22, px + 72):
        d.line([(cx, 530), (cx + (8 if cx < px + 50 else -8), 550)], fill=INK, width=3)
        E(d, [cx - 24, 488, cx + 24, 536], (194, 164, 104))
        E(d, [cx - 6, 506, cx + 6, 518], INK, ow=0)
    R(d, [px, 548, px + 100, 618], (78, 90, 84), r=6)
    R(d, [px - 34, 566, px, 592], (54, 56, 60))
    E(d, [px + 60, 566, px + 84, 590], (194, 164, 104), ow=2)
    d.line([(px + 100, 584), (px + 124, 584), (px + 124, 604)], fill=INK, width=4)
    E(d, [px + 118, 600, px + 130, 612], (194, 164, 104), ow=2)
    # 長持とつづら（左端）、棚とかめ（右端）
    R(d, [24, 700, 300, FLOOR], (152, 106, 68))
    d.rectangle([24, 700, 300, 716], fill=(110, 80, 52))
    R(d, [60, 612, 262, 700], (190, 162, 112), r=14)
    for x in range(80, 250, 24):
        d.line([(x, 616), (x, 696)], fill=(170, 142, 96), width=2)
    for y in (430, 560):
        R(d, [1790, y, 1930, y + 14], (126, 96, 68))
    for x, y, c in ((1810, 430, (150, 110, 80)), (1866, 430, (110, 96, 84)), (1820, 560, (176, 150, 110))):
        R(d, [x, y - 70, x + 46, y], c, r=16)
    return img


def ie():
    """大正の福島の商家（糀屋）の座敷。畳、障子、火鉢。"""
    img = vgrad((W, H), (216, 202, 176), (200, 186, 160))
    fy = 860
    tatami_floor(img, fy)
    d = _d(img)
    R(d, [480, 70, 1440, 140], (178, 142, 102))                                 # 欄間
    for x in range(520, 1420, 60):
        d.line([(x, 82), (x, 128)], fill=(120, 90, 62), width=6)
    R(d, [-10, 140, W + 10, 168], (150, 114, 80))                               # 鴨居
    sx0, sx1, sy0, sy1 = 500, 1420, 168, fy
    d.rectangle([sx0, sy0, sx1, sy1], fill=(242, 234, 212))                     # 障子
    _glow(img, 960, 420, 420, (255, 242, 204), 56)
    d = _d(img)
    for x in range(sx0, sx1 + 1, 46):
        d.line([(x, sy0), (x, sy1 - 110)], fill=(156, 124, 90), width=4)
    for y in range(sy0, sy1 - 110, 66):
        d.line([(sx0, y), (sx1, y)], fill=(156, 124, 90), width=4)
    R(d, [sx0, sy1 - 110, sx1, sy1], (172, 138, 100))
    for k in range(5):
        x = sx0 + k * (sx1 - sx0) / 4
        R(d, [x - 8, sy0, x + 8, sy1], (140, 106, 74))
    # 箪笥（左端）
    R(d, [40, 440, 320, fy], (154, 106, 66))
    for k, y in enumerate((450, 540, 630, 720, 790)):
        R(d, [52, y, 308, y + 80 if y < 790 else fy - 10], (166, 116, 72), ow=2)
        if y < 700:
            for hx in (110, 250):
                d.arc([hx - 22, y + 24, hx + 22, y + 60], 200, 340, fill=(70, 60, 52), width=5)
    # 床の間（右端）
    d.rectangle([1520, 168, W, fy], fill=(208, 192, 164))
    R(d, [1500, 140, 1532, fy], (122, 88, 60))
    R(d, [1532, 700, W + 10, 740], (152, 114, 78))
    d.line([(1730, 168), (1730, 204)], fill=INK, width=2)
    R(d, [1664, 204, 1796, 604], (128, 108, 94))
    R(d, [1680, 232, 1780, 574], (242, 236, 218), ow=2)
    d.polygon([(1690, 520), (1720, 440), (1744, 480), (1770, 400), (1772, 520)], fill=(150, 150, 146))
    d.polygon([(1690, 540), (1730, 500), (1772, 540), (1772, 560), (1690, 560)], fill=(196, 196, 190))
    d.ellipse([1700, 270, 1730, 300], fill=(214, 120, 100))
    R(d, [1712, 630, 1752, 700], (150, 186, 168), r=14)                         # 花入れ
    thick(d, [(1732, 632), (1716, 570), (1690, 540)], (96, 120, 70), 4, ow=2)
    for lx, ly in ((1716, 576), (1700, 552), (1726, 600)):
        E(d, [lx - 10, ly - 6, lx + 10, ly + 6], (120, 160, 96), ow=2)
    # 火鉢と鉄瓶（中央）
    cx = 960
    R(d, [cx - 100, 762, cx + 100, 862], (198, 212, 224), r=36)
    for y in (792, 822):
        d.line([(cx - 96, y), (cx + 96, y)], fill=(112, 142, 182), width=5)
    E(d, [cx - 106, 742, cx + 106, 786], (216, 228, 236))
    E(d, [cx - 88, 750, cx + 88, 780], (178, 172, 166), ow=0)
    for ox in (-40, 6, 44):
        E(d, [cx + ox - 14, 754, cx + ox + 14, 770], (222, 104, 64), ow=0)
    d.line([(cx - 40, 758), (cx - 32, 726)], fill=INK, width=5)
    d.line([(cx + 40, 758), (cx + 32, 726)], fill=INK, width=5)
    d.arc([cx - 56, 588, cx + 56, 690], 200, 340, fill=INK, width=6)
    P(d, [(cx + 50, 694), (cx + 100, 662), (cx + 104, 676), (cx + 56, 712)], (76, 72, 70))
    E(d, [cx - 62, 650, cx + 62, 742], (76, 72, 70))
    R(d, [cx - 26, 640, cx + 26, 658], (96, 92, 88), r=6)
    for k in range(2):
        pts = [(cx + 104 + k * 14 + 10 * math.sin(j * 0.9 + k * 2), 656 - j * 18) for j in range(6)]
        d.line(pts, fill=(250, 250, 250), width=5, joint="curve")
    return img


def haneda(kara=False):
    """大正の羽田の海岸。ヨシズ張りの格納小屋と複葉機。kara=True は高潮のあと（小屋は壊れ、飛行機は無い）。"""
    if kara:
        img = vgrad((W, H), (128, 134, 146), (176, 180, 188))
    else:
        img = vgrad((W, H), (150, 200, 236), (212, 230, 240))
    horizon, shore = 440, 600
    if kara:                                                                    # 雲
        for cx, cy, s, c in ((300, 120, 1.6, (150, 154, 164)), (900, 70, 1.9, (140, 144, 154)),
                             (1500, 130, 1.7, (156, 160, 170)), (1150, 250, 1.3, (166, 170, 178)),
                             (500, 300, 1.2, (170, 174, 182)), (1760, 300, 1.1, (164, 168, 176))):
            _cloud(img, cx, cy, s, col=c, ink=(110, 114, 126))
    else:
        for cx, cy, s in ((1360, 120, 0.9), (1700, 230, 0.6), (820, 210, 0.55)):
            _cloud(img, cx, cy, s)
    d = _d(img)
    sea = (88, 108, 124) if kara else (98, 158, 198)
    d.rectangle([0, horizon, W, shore], fill=sea)
    d.line([(0, horizon), (W, horizon)], fill=_shade(sea, 0.8), width=3)
    rnd = random.Random(4)
    for _ in range(26 if kara else 16):
        x, y = rnd.randint(0, W), rnd.randint(horizon + 14, shore - 14)
        ln = rnd.randint(40, 120)
        d.line([(x, y), (x + ln, y)], fill=(236, 240, 244) if kara else _shade(sea, 1.2), width=3)
    _band(img, shore, H, (210, 198, 170) if kara else (230, 212, 170), (194, 182, 156) if kara else (216, 196, 152))
    d = _d(img)
    pts = [(x, shore + 6 * math.sin(x / 70)) for x in range(0, W + 1, 20)]       # 波打ち際
    d.line(pts, fill=(244, 246, 246), width=8, joint="curve")
    d.line([(x, y + 8) for x, y in pts], fill=_shade(sea, 1.1), width=3, joint="curve")
    reed, reed_l, post = (206, 180, 126), (180, 152, 102), (132, 102, 72)
    hx0, hx1, hb, ht = 600, 1320, 650, 300
    if not kara:
        R(d, [hx0, ht + 40, hx1, hb], (100, 86, 68))                           # 小屋の中（暗い）
        for x0, x1 in ((hx0, hx0 + 110), (hx1 - 110, hx1), (hx0, hx1)):
            y1 = hb if x1 - x0 < 200 else ht + 110
            R(d, [x0, ht + 40, x1, y1], reed)
            for x in range(x0 + 8, x1, 9):
                d.line([(x, ht + 44), (x, y1 - 3)], fill=reed_l, width=2)
            for y in (ht + 76, ht + 210, ht + 300):
                if y < y1:
                    d.line([(x0, y), (x1, y)], fill=(140, 110, 74), width=4)
        P(d, [(hx0 - 60, ht + 50), (960, ht - 96), (hx1 + 60, ht + 50)], (166, 140, 100))   # 屋根
        for k in range(1, 6):
            t = k / 6
            d.line([(hx0 - 60 + (960 - hx0 + 60) * t, ht + 50 - 146 * t), (hx1 + 60 - (hx1 + 60 - 960) * t, ht + 50 - 146 * t)],
                   fill=(146, 120, 84), width=3)
        for x in (hx0, hx0 + 110, hx1 - 110, hx1):
            R(d, [x - 9, ht + 30, x + 9, hb], post)
        alpha(img, lambda dd: dd.ellipse([720, 630, 1200, 680], fill=(90, 70, 40, 60)), blur=8)
        d = _d(img)
        _biplane_front(d, 960, 470, 1.0)
        # 吹き流し（右端）
        R(d, [1752, 220, 1766, 650], (220, 220, 214))
        sock = [(1766, 230), (1890, 248), (1890, 270), (1766, 286)]
        P(d, sock, (236, 236, 230))
        for k in (0, 2):
            x0, x1 = 1766 + k * 31, 1766 + (k + 1) * 31
            t0, t1 = k * 31 / 124, (k + 1) * 31 / 124
            d.polygon([(x0, 230 + 18 * t0), (x1, 230 + 18 * t1), (x1, 286 - 16 * t1), (x0, 286 - 16 * t0)], fill=(222, 92, 80))
        P(d, sock, None)
        for x in (80, 180):                                                    # 油の樽（左端）
            R(d, [x - 44, 560, x + 44, 650], (120, 104, 92), r=12)
            d.line([(x - 44, 590), (x + 44, 590)], fill=INK, width=3)
            d.line([(x - 44, 620), (x + 44, 620)], fill=INK, width=3)
        return img
    # ---- 高潮のあと: 小屋は崩れ、飛行機は無い
    P(d, [(560, 650), (640, 520), (980, 470), (1300, 560), (1360, 650)], _shade(reed, 0.86))   # 崩れた屋根
    for k in range(1, 5):
        t = k / 5
        d.line([(600 + 60 * t, 650 - 130 * t + 0), (1330 - 40 * t, 650 - 90 * t)], fill=(150, 124, 86), width=3)
    P(d, [(760, 560), (840, 520), (900, 600), (820, 640)], (110, 94, 76), ow=2)   # 屋根の穴
    P(d, [(1080, 560), (1150, 548), (1170, 610), (1100, 626)], (110, 94, 76), ow=2)
    thick(d, [(610, 650), (676, 400)], post, 16)                                # 傾いた柱
    thick(d, [(1306, 650), (1296, 520)], post, 16)
    thick(d, [(1296, 520), (1270, 506)], post, 10)
    thick(d, [(900, 680), (1180, 700)], post, 14)                               # 倒れた柱
    for (x0, y0, x1, y1) in ((440, 640, 560, 700), (1360, 650, 1500, 700)):     # 散ったヨシズ
        P(d, [(x0, y0 + 20), (x1, y0), (x1 + 10, y1 - 10), (x0 + 6, y1)], reed)
        for x in range(x0 + 10, x1, 10):
            d.line([(x, y0 + 18), (x + 6, y1 - 6)], fill=reed_l, width=2)
    rnd = random.Random(19)                                                     # 波打ち際の木片
    for _ in range(26):
        x = rnd.choice([rnd.randint(20, 330), rnd.randint(770, 1150), rnd.randint(1580, 1900)])
        y = rnd.randint(shore - 10, shore + 26) if rnd.random() < 0.75 else rnd.randint(horizon + 30, shore - 20)
        ln, a = rnd.randint(30, 80), rnd.uniform(-0.5, 0.5)
        x1, y1 = x + ln * math.cos(a), y + ln * math.sin(a)
        thick(d, [(x, y), (x1, y1)], (150, 118, 82), 8, ow=2)
    thick(d, [(1758, 650), (1730, 260)], (220, 220, 214), 12)                   # しおれた吹き流し
    P(d, [(1734, 270), (1756, 276), (1748, 380), (1736, 384)], (226, 226, 220), ow=2)
    R(d, [36, 610, 140, 650], (120, 104, 92), r=12)                             # 倒れた樽
    E(d, [126, 606, 166, 654], (100, 88, 78))
    return img


def haneda_kara():
    return haneda(kara=True)


def hanami():
    """東京・飛鳥山の花見。満開の桜、ござ、提灯（文字なし）。"""
    img = vgrad((W, H), (196, 222, 240), (234, 236, 236))
    d = _d(img)
    _band(img, 500, H, (190, 206, 152), (170, 188, 134))
    blob(img, [("e", [x - 120, 400, x + 120, 540]) for x in range(-40, W + 120, 170)], (240, 214, 220),
         ink=(196, 156, 166))                                                   # 遠くの桜並木
    d = _d(img)
    d.rectangle([0, 500, W, 520], fill=(176, 194, 140))
    for x in (230, 960, 1730):                                                  # 幹と枝
        thick(d, [(x - 10, 640), (x - 4, 420), (x + 10, 300)], (112, 86, 76), 46)
        thick(d, [(x + 6, 420), (x + 120, 300)], (112, 86, 76), 18)
        thick(d, [(x, 380), (x - 110, 280)], (112, 86, 76), 16)
    rnd = random.Random(8)
    shapes = []
    for x in range(-80, W + 120, 120):
        y = rnd.randint(-40, 120)
        shapes.append(("e", [x - 140, y - 40, x + 140, y + 230]))
    for x in (230, 960, 1730):
        shapes += [("e", [x - 260, 120, x + 40, 360]), ("e", [x - 40, 140, x + 260, 370])]
    blob(img, shapes, (246, 210, 218), ink=(170, 124, 138))                     # 満開の桜
    d = _d(img)
    for _ in range(160):
        x, y = rnd.randint(0, W), rnd.randint(0, 340)
        r = rnd.randint(10, 26)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(252, 230, 234))
    for _ in range(60):
        x, y = rnd.randint(0, W), rnd.randint(0, 340)
        r = rnd.randint(8, 16)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(236, 186, 200))
    # 提灯（文字なし）
    sag = lambda x: 300 + 40 * math.sin(math.pi * (x - 640) / (W - 640))
    d.line([(x, sag(x)) for x in range(640, W + 1, 20)], fill=INK, width=3)
    for k, x in enumerate(range(700, W, 120)):
        y = sag(x)
        col = (228, 104, 92) if k % 2 == 0 else (248, 240, 226)
        d.line([(x, y), (x, y + 14)], fill=INK, width=2)
        E(d, [x - 22, y + 14, x + 22, y + 72], col)
        for dy in (28, 44, 58):
            d.line([(x - 18, y + dy), (x + 18, y + dy)], fill=_shade(col, 0.85), width=2)
        R(d, [x - 13, y + 8, x + 13, y + 18], (60, 56, 56), ow=0)
        R(d, [x - 13, y + 68, x + 13, y + 78], (60, 56, 56), ow=0)
    # ござ
    P(d, [(0, 660), (330, 660), (300, 730), (0, 730)], (172, 196, 214))
    P(d, [(1600, 660), (W, 660), (W, 730), (1630, 730)], (222, 204, 146))
    P(d, [(700, 726), (1220, 726), (1280, 810), (640, 810)], (224, 204, 144))
    for k in range(1, 8):
        t = k / 8
        d.line([(700 + 520 * t - 60 * (1 - t) * 0, 726), (640 + 640 * t, 810)], fill=(204, 182, 122), width=2)
    R(d, [880, 676, 1000, 716], (178, 54, 54))                                  # 重箱
    R(d, [880, 652, 1000, 678], (178, 54, 54))
    d.line([(880, 678), (1000, 678)], fill=(60, 30, 30), width=3)
    R(d, [1030, 660, 1060, 716], (246, 242, 230), r=12)                         # とっくり
    for _ in range(40):                                                         # 舞う花びら（上半分）
        x, y = rnd.randint(640, 1300), rnd.randint(360, 640)
        d.ellipse([x, y, x + 10, y + 6], fill=(246, 196, 208))
    return img


def satsueijo():
    """大正の撮影所（ガラス張りのグラスステージ）。手回しの撮影機と三脚。"""
    img = vgrad((W, H), (214, 228, 236), (226, 232, 232))
    d = _d(img)
    P(d, [(-10, -10), (W + 10, -10), (W - 200, 220), (200, 220)], (196, 220, 236))   # ガラスの屋根
    for k in range(0, 13):
        x0 = -10 + (W + 20) * k / 12
        x1 = 200 + (W - 400) * k / 12
        d.line([(x0, -10), (x1, 220)], fill=(96, 106, 114), width=5)
    for y, t in ((70, 70 / 230), (150, 160 / 230)):
        d.line([(-10 + 210 * t, y), (W + 10 - 210 * t, y)], fill=(96, 106, 114), width=5)
    d.rectangle([0, 220, W, 760], fill=(208, 226, 236))                         # ガラスの壁
    for x in range(0, W + 1, 160):
        d.line([(x, 220), (x, 760)], fill=(100, 110, 118), width=6)
    for y in (340, 460, 580, 700):
        d.line([(0, y), (W, y)], fill=(100, 110, 118), width=5)
    d.line([(0, 220), (W, 220)], fill=INK, width=4)
    alpha(img, lambda dd: [dd.polygon([(x, 0), (x + 120, 0), (x + 420, 760), (x + 300, 760)], fill=(255, 252, 236, 40))
                           for x in (640, 980, 1400)], blur=10)
    alpha(img, lambda dd: [dd.rectangle([x, 150, x + 220, 196], fill=(255, 255, 255, 120)) for x in (660, 1000, 1340)], blur=2)
    d = _d(img)
    d.rectangle([0, 760, W, FLOOR], fill=(156, 130, 102))                      # 腰壁
    d.line([(0, 760), (W, 760)], fill=INK, width=3)
    wood_floor(img, FLOOR, col=(150, 122, 92), line=(132, 106, 80))
    d = _d(img)
    # 書き割り（右端）
    R(d, [1590, 380, 1910, FLOOR], (226, 214, 190))
    for x in (1670, 1750, 1830):
        d.line([(x, 380), (x, FLOOR)], fill=(176, 150, 120), width=4)
    d.line([(1590, 560), (1910, 560)], fill=(176, 150, 120), width=4)
    # レフ板（左端）
    d.line([(160, 640), (160, FLOOR)], fill=INK, width=6)
    for fx in (110, 210):
        d.line([(160, 820), (fx, FLOOR)], fill=INK, width=5)
    R(d, [40, 330, 280, 640], (226, 230, 232))
    for k in range(6):
        d.line([(60 + k * 40, 350), (40 + k * 40, 620)], fill=(206, 210, 214), width=4)
    # 手回しの撮影機と三脚（中央）
    for fx in (870, 1050, 960):
        thick(d, [(960, 580), (fx, FLOOR + (20 if fx == 960 else 0))], (150, 112, 74), 10)
    R(d, [924, 566, 996, 590], (120, 90, 60))
    R(d, [904, 446, 1030, 566], (156, 112, 72), r=6)
    for x, y in ((904, 446), (1018, 446), (904, 554), (1018, 554)):
        d.rectangle([x, y, x + 12, y + 12], fill=(206, 172, 96))
    R(d, [864, 486, 904, 524], (52, 52, 56))
    E(d, [852, 484, 876, 526], (80, 84, 92))
    E(d, [914, 380, 974, 440], (110, 84, 58))
    E(d, [964, 380, 1024, 440], (110, 84, 58))
    R(d, [930, 430, 1010, 448], (110, 84, 58))
    d.line([(1030, 506), (1060, 506), (1060, 532)], fill=INK, width=5)
    E(d, [1052, 528, 1068, 544], (206, 172, 96), ow=2)
    return img


def kyoto_set():
    """昭和初期の京都の時代劇セット（町屋の通り）と、木で組んだ手作りの撮影用クレーン。"""
    img = vgrad((W, H), (160, 200, 232), (214, 226, 234))
    _cloud(img, 1560, 150, 0.8)
    _cloud(img, 760, 120, 0.5)
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(212, 192, 156))                            # 土の道
    d.rectangle([0, 700, W, 716], fill=(176, 156, 122))
    wall, wood, roof = (234, 228, 212), (116, 84, 58), (110, 116, 130)
    x = -40
    k = 0
    while x < 1820:                                                             # 町屋の並び（書き割り）
        w = 380 if k % 2 == 0 else 340
        R(d, [x, 320, x + w, 450], wall)
        for sx in range(int(x + 40), int(x + w - 40), 14):                      # 虫籠窓
            if (sx - x) % 120 < 70:
                d.line([(sx, 360), (sx, 420)], fill=wood, width=6)
        P(d, [(x - 10, 330), (x + w + 10, 330), (x + w - 10, 280), (x + 10, 280)], roof)
        P(d, [(x - 20, 470), (x + w + 20, 470), (x + w, 440), (x, 440)], roof)
        R(d, [x, 470, x + w, 700], (136, 100, 70))
        for sx in range(int(x + 10), int(x + w - 6), 16):                       # 格子
            d.line([(sx, 480), (sx, 690)], fill=wood, width=6)
        if k % 2 == 1:
            R(d, [x + w * 0.3, 470, x + w * 0.7, 580], (70, 86, 118))            # 無地ののれん
            for j in range(1, 3):
                xx = x + w * 0.3 + w * 0.4 * j / 3
                d.line([(xx, 474), (xx, 580)], fill=(50, 64, 92), width=3)
        x += w
        k += 1
    # 右端はセットの切れ目（板の裏と支え木）
    d.rectangle([1820, 260, W, 700], fill=(170, 200, 226))
    R(d, [1820, 280, 1840, 700], (196, 170, 130))
    thick(d, [(1840, 330), (1920, 700)], (176, 140, 98), 12)
    thick(d, [(1840, 520), (1910, 700)], (176, 140, 98), 10)
    # 木のクレーン（中央）
    cw = (186, 144, 98)
    for x0 in (926, 994):
        thick(d, [(x0, 690), (x0 + (8 if x0 < 960 else -8), 300)], cw, 12)
    for y in range(330, 690, 60):
        d.line([(932, y), (988, y + 60)], fill=_shade(cw, 0.8), width=5)
        d.line([(988, y), (932, y + 60)], fill=_shade(cw, 0.8), width=5)
    R(d, [880, 680, 1040, 712], (150, 112, 74))
    for wx in (900, 1020):
        E(d, [wx - 18, 698, wx + 18, 734], (90, 80, 70))
    bx0, by0, bx1, by1 = 760, 420, 1330, 126                                     # ブーム
    thick(d, [(bx0, by0), (bx1, by1)], cw, 12)
    thick(d, [(bx0 + 10, by0 + 22), (bx1 + 10, by1 + 22)], cw, 10)
    for k in range(1, 12):
        t = k / 12
        x, y = bx0 + (bx1 - bx0) * t, by0 + (by1 - by0) * t
        d.line([(x, y), (x + 10, y + 22)], fill=_shade(cw, 0.8), width=4)
    R(d, [726, 400, 800, 470], (120, 116, 112))                                # おもり
    E(d, [940, 296, 980, 336], (150, 112, 74))                                  # 支点
    d.line([(960, 300), (960, 220)], fill=INK, width=5)
    d.line([(960, 222), (bx1, by1)], fill=(110, 100, 90), width=2)
    d.line([(960, 222), (bx0 + 30, by0 - 10)], fill=(110, 100, 90), width=2)
    R(d, [1262, 110, 1400, 128], (160, 120, 80))                                # 先の台と撮影機
    d.line([(1262, 110), (1262, 84), (1400, 84), (1400, 110)], fill=INK, width=3)
    R(d, [1300, 58, 1360, 108], (140, 100, 66), r=4)
    R(d, [1280, 70, 1300, 92], (52, 52, 56))
    E(d, [1306, 34, 1334, 62], (110, 84, 58), ow=2)
    E(d, [1330, 34, 1358, 62], (110, 84, 58), ow=2)
    return img


def byoshitsu():
    """昭和初期の病室。白い寝台、窓、花瓶。"""
    img = vgrad((W, H), (238, 236, 228), (226, 224, 214))
    d = _d(img)
    d.rectangle([0, 600, W, FLOOR], fill=(196, 214, 200))                        # 腰の壁
    d.line([(0, 600), (W, 600)], fill=INK, width=3)
    wood_floor(img, FLOOR, col=(176, 172, 162), line=(160, 156, 146))
    d = _d(img)
    _band(img, 130, 440, (166, 204, 234), (206, 226, 238), 760, 1160)
    d = _d(img)
    thick(d, [(1160, 200), (1060, 250), (980, 236)], (110, 90, 70), 10, ow=0)  # 窓の外の枝
    for lx, ly in ((1060, 240), (1010, 230), (1110, 214), (990, 250)):
        d.ellipse([lx - 26, ly - 18, lx + 26, ly + 18], fill=(150, 190, 130))
    _window(d, 760, 130, 1160, 440, sky=None, frame=(246, 246, 242))
    R(d, [700, 100, 1220, 112], (190, 190, 186), r=4)
    P(d, [(706, 112), (800, 112), (770, 300), (740, 470), (706, 470)], (250, 250, 246))   # 白いカーテン
    P(d, [(1214, 112), (1120, 112), (1150, 300), (1180, 470), (1214, 470)], (250, 250, 246))
    d.line([(740, 300), (790, 300)], fill=(200, 190, 170), width=6)
    d.line([(1130, 300), (1180, 300)], fill=(200, 190, 170), width=6)
    _clock(d, 180, 260, 56, rim=(150, 130, 110))
    # 白い寝台
    iron = (236, 238, 240)
    for x0 in (600, 1300):
        top = 470 if x0 == 600 else 540
        R(d, [x0, top, x0 + 22, FLOOR], iron)
        R(d, [x0 + 30, top + 20, x0 + 46, FLOOR - 160], iron, ow=2)
    R(d, [600, 470, 650, 490], iron)
    R(d, [1280, 540, 1330, 560], iron)
    R(d, [620, 640, 1300, 670], iron)
    R(d, [620, 600, 1300, 660], (250, 250, 248), r=12)
    P(d, [(760, 590), (1300, 590), (1300, 700), (760, 700)], (204, 220, 234))   # 毛布
    d.line([(760, 610), (1300, 610)], fill=(240, 244, 248), width=8)
    E(d, [640, 560, 770, 616], (252, 252, 250))
    # 枕元の台と花瓶（右端）
    R(d, [1620, 600, 1800, FLOOR], (210, 200, 180))
    R(d, [1610, 588, 1810, 610], (196, 184, 162))
    R(d, [1682, 500, 1738, 590], (186, 214, 228), r=18)
    for fx, fy, c in ((1680, 440, (230, 110, 110)), (1720, 420, (246, 206, 90)), (1756, 446, (240, 150, 170)),
                      (1700, 470, (230, 110, 110))):
        thick(d, [(1710, 504), (fx, fy + 16)], (96, 140, 84), 4, ow=2)
        E(d, [fx - 18, fy - 14, fx + 18, fy + 18], c)
    return img


def ie_kyoto():
    """撮影所の裏の小さな一軒家の玄関と土間。"""
    img = vgrad((W, H), (220, 206, 182), (204, 190, 166))
    d = _d(img)
    R(d, [-10, 120, W + 10, 148], (140, 104, 72))
    _band(img, 200, 760, (236, 240, 232), (228, 230, 220), 740, 1180)           # 格子戸の向こうの光
    _glow(img, 960, 480, 320, (255, 246, 214), 70)
    d = _d(img)
    for x in range(760, 1180, 26):
        d.line([(x, 200), (x, 560)], fill=(130, 96, 66), width=5)
    for y in (260, 330, 400, 470):
        d.line([(740, y), (1180, y)], fill=(130, 96, 66), width=4)
    d.rectangle([742, 560, 1178, 760], fill=(230, 232, 226))                    # すりガラス
    d.line([(960, 200), (960, 760)], fill=(110, 80, 56), width=10)
    R(d, [740, 200, 1180, 760], None, ow=12, ink=(122, 88, 60))
    R(d, [720, 180, 1200, 200], (130, 96, 66))
    for x0 in (700, 1200):
        R(d, [x0, 148, x0 + 20, 760], (126, 92, 64))
    d.rectangle([0, 760, W, H], fill=(156, 138, 118))                           # 土間
    d.line([(0, 760), (W, 760)], fill=INK, width=3)
    _glow(img, 960, 800, 260, (255, 240, 200), 40)
    d = _d(img)
    R(d, [1380, 790, W + 10, 850], (176, 140, 100))                            # 上がり框
    d.rectangle([1380, 850, W, H], fill=(150, 116, 82))
    _bulb(img, 960, 60, warm=True, cord_top=148)
    d = _d(img)
    R(d, [40, 470, 310, 760], (150, 112, 76))                                   # 下駄箱と祝いの餅
    for y in (530, 620, 700):
        d.line([(40, y), (310, y)], fill=INK, width=3)
    d.line([(175, 470), (175, 760)], fill=INK, width=3)
    R(d, [70, 450, 280, 472], (176, 136, 92))
    for mx in (100, 150, 200, 250):
        E(d, [mx - 24, 422, mx + 24, 458], (250, 248, 240), ow=2)
    R(d, [1640, 300, 1660, 760], (150, 112, 76))                                # 立てかけた番傘（右端）
    P(d, [(1650, 300), (1700, 340), (1690, 640), (1650, 660), (1612, 640), (1602, 340)], (206, 86, 70))
    for x in (1626, 1650, 1674):
        d.line([(1650, 300), (x, 650)], fill=(170, 64, 52), width=2)
    return img


def _screen_room(modern=False):
    """試写室。modern=False は1933年の木の椅子、True は1954年の赤い椅子と幕と譜面台。"""
    top, bot = ((72, 66, 76), (54, 50, 60)) if not modern else ((76, 62, 70), (58, 48, 56))
    img = vgrad((W, H), top, bot)
    d = _d(img)
    P(d, [(1480, -10), (W + 10, -10), (W + 10, H + 10), (1480, 900)], _shade(top, 0.86), ow=0)   # 右の壁（映写室側）
    d.line([(1480, -10), (1480, 900)], fill=INK, width=3)
    pw = [(1650, 150), (1760, 130), (1760, 210), (1650, 222)]                    # 映写窓
    P(d, [(1630, 128), (1780, 104), (1780, 230), (1630, 246)], (90, 80, 86))
    P(d, pw, (255, 246, 214))
    if not modern:
        P(d, [(1800, 120), (1870, 108), (1870, 172), (1800, 182)], (150, 140, 120))
    sx0, sy0, sx1, sy1 = (640, 140, 1300, 500) if not modern else (640, 140, 1340, 520)
    if modern:                                                                  # 幕
        for x0, x1 in ((sx0 - 120, sx0 + 10), (sx1 - 10, sx1 + 120)):
            R(d, [x0, 96, x1, 640], (150, 62, 68))
            for x in range(x0 + 20, x1, 26):
                d.line([(x, 100), (x, 636)], fill=(120, 48, 56), width=4)
        R(d, [sx0 - 130, 84, sx1 + 130, 124], (130, 54, 60))
    _glow(img, (sx0 + sx1) / 2, (sy0 + sy1) / 2, (sx1 - sx0) * 0.62, (240, 244, 255), 60)
    d = _d(img)
    R(d, [sx0 - 14, sy0 - 14, sx1 + 14, sy1 + 14], (36, 34, 40))
    d.rectangle([sx0, sy0, sx1, sy1], fill=(250, 250, 246) if not modern else (255, 255, 255))
    alpha(img, lambda dd: dd.polygon([(1700, 176), (sx0 + 40, sy0 + 10), (sx0 + 40, sy1 - 10)], fill=(255, 248, 220, 26)), blur=20)
    d = _d(img)
    rnd = random.Random(33)
    for _ in range(40):                                                         # 光の中のほこり
        t = rnd.random()
        x = 1700 + (sx0 + 300 - 1700) * t
        y = 176 + rnd.uniform(-1, 1) * 150 * t + 60 * t
        d.ellipse([x, y, x + 4, y + 4], fill=(255, 250, 230))
    if not modern:                                                              # フィルムの缶（左端）
        for k, (x, y) in enumerate(((60, 640), (150, 640), (100, 590), (230, 640))):
            E(d, [x, y, x + 100, y + 34], (150, 150, 156))
            R(d, [x, y + 17, x + 100, y + 60], (150, 150, 156), ow=0)
            d.line([(x, y + 17), (x, y + 60), (x + 100, y + 60), (x + 100, y + 17)], fill=INK, width=3)
            E(d, [x, y, x + 100, y + 34], (176, 176, 182))
    if modern:                                                                  # 譜面台
        cx = 960
        d.line([(cx, 600), (cx, 850)], fill=INK, width=8)
        for fx in (900, 1020):
            d.line([(cx, 820), (fx, 880)], fill=INK, width=6)
        d.line([(cx, 820), (cx, 890)], fill=INK, width=6)
        P(d, [(880, 506), (1040, 506), (1052, 600), (868, 600)], (60, 60, 68))
        R(d, [892, 470, 1028, 586], (252, 250, 240), ow=2)
        for gy in (494, 548):
            for k in range(5):
                d.line([(902, gy + k * 6), (1018, gy + k * 6)], fill=(150, 150, 150), width=1)
        for nx, ny in ((920, 498), (948, 504), (980, 492), (1004, 508), (930, 552), (968, 560), (996, 548)):
            d.ellipse([nx, ny, nx + 8, ny + 6], fill=(40, 40, 44))
    seat = (118, 86, 62) if not modern else (148, 60, 66)                       # 椅子の列
    for row, y in enumerate((730, 860)):
        off = 0 if row == 0 else 55
        for x in range(-60 + off, W, 110):
            R(d, [x, y, x + 100, y + 160], _shade(seat, 0.9 if row == 0 else 1.0), r=28)
            d.line([(x + 14, y + 30), (x + 86, y + 30)], fill=_shade(seat, 0.75), width=3)
    _vignette(img, 50)
    return img


def shishitsu():
    return _screen_room(False)


def shishitsu54():
    return _screen_room(True)


def toho_rouka():
    """1937年の撮影所の屋外の通路。ステージの大きな扉と機材の箱。"""
    img = vgrad((W, H), (168, 204, 232), (212, 224, 232))
    _cloud(img, 1500, 60, 0.6)
    d = _d(img)
    R(d, [-10, 110, W + 10, 860], (216, 206, 188))                              # ステージの壁
    R(d, [-10, 96, W + 10, 122], (152, 148, 142))
    for x in range(160, W, 320):
        d.rectangle([x, 122, x + 36, 860], fill=(200, 190, 172))
        d.line([(x, 122), (x, 860)], fill=_shade((200, 190, 172), 0.85), width=2)
    for x in (300, 1640):                                                       # 高い小窓
        R(d, [x - 70, 160, x + 70, 240], (150, 170, 184))
        d.line([(x, 160), (x, 240)], fill=INK, width=4)
    R(d, [600, 172, 1320, 194], (110, 110, 116))                                # 大扉のレール
    door = (124, 140, 132)
    R(d, [620, 194, 944, 860], door)
    R(d, [990, 194, 1310, 860], door)
    d.rectangle([944, 194, 990, 860], fill=(40, 40, 46))                        # 少し開いた隙間
    for y in range(250, 860, 64):
        d.line([(624, y), (940, y)], fill=_shade(door, 0.85), width=4)
        d.line([(994, y), (1306, y)], fill=_shade(door, 0.85), width=4)
    R(d, [910, 450, 932, 560], (90, 92, 96), r=6)
    R(d, [1002, 450, 1024, 560], (90, 92, 96), r=6)
    R(d, [924, 128, 996, 164], (166, 70, 64), r=8)                              # 撮影中ランプ（消えている）
    d.rectangle([-10, 860, W + 10, H], fill=(188, 184, 176))                    # 通路
    d.line([(0, 860), (W, 860)], fill=INK, width=3)
    d.rectangle([0, 870, W, 884], fill=(170, 166, 158))
    # 機材の箱（右端・左端）
    for x, y, w, h in ((1600, 860, 160, 120), (1770, 860, 150, 150), (1640, 740, 130, 110), (40, 860, 170, 110)):
        R(d, [x, y - h, x + w, y], (178, 138, 92))
        d.line([(x, y - h + 24), (x + w, y - h + 24)], fill=(146, 110, 72), width=4)
        d.rectangle([x + w / 2 - 16, y - h / 2 - 6, x + w / 2 + 16, y - h / 2 + 6], fill=(90, 80, 70))
    d.line([(260, 520), (260, 860)], fill=INK, width=6)                         # ライトの台（左端）
    for fx in (210, 310):
        d.line([(260, 800), (fx, 860)], fill=INK, width=5)
    R(d, [206, 450, 314, 530], (86, 86, 94), r=12)
    E(d, [290, 460, 322, 520], (240, 236, 220))
    return img


def tokugi():
    """誰もいない小さな部屋（特殊技術課）。机ひとつ、箱型の自作の合成機、英語の専門書の山。"""
    img = vgrad((W, H), (186, 190, 192), (166, 170, 172))
    d = _d(img)
    d.rectangle([0, 700, W, FLOOR], fill=(150, 156, 160))
    d.line([(0, 700), (W, 700)], fill=INK, width=3)
    wood_floor(img, FLOOR, col=(116, 104, 94), line=(100, 90, 82))
    d = _d(img)
    _band(img, 150, 380, (176, 186, 196), (196, 202, 208), 120, 300)            # 曇りの小窓
    d = _d(img)
    _window(d, 120, 150, 300, 380, sky=None, frame=(220, 222, 220))
    R(d, [1640, 230, 1860, 250], (132, 110, 90))                                # 何も掛かっていない帽子掛け
    for x in (1680, 1750, 1820):
        thick(d, [(x, 250), (x + 6, 276)], (110, 90, 72), 6, ow=2)
    _bulb(img, 960, 90, warm=False, cord_top=0)
    d = _d(img)
    alpha(img, lambda dd: dd.ellipse([700, 900, 1220, 1000], fill=(30, 30, 40, 40)), blur=20)
    d = _d(img)
    R(d, [720, 620, 1200, 648], (132, 110, 90))                                 # 机
    R(d, [736, 648, 760, FLOOR], (116, 96, 78))
    R(d, [1160, 648, 1184, FLOOR], (116, 96, 78))
    # 自作の合成機（光学機械）
    R(d, [770, 596, 1110, 616], (120, 124, 132))
    R(d, [790, 500, 880, 596], (72, 76, 84), r=6)                               # 撮影機
    E(d, [786, 438, 838, 490], (96, 100, 108))
    E(d, [830, 438, 882, 490], (96, 100, 108))
    d.line([(812, 490), (820, 500)], fill=INK, width=3)
    d.line([(856, 490), (850, 500)], fill=INK, width=3)
    R(d, [880, 534, 900, 566], (52, 54, 58))
    pts = []                                                                    # 蛇腹
    for k in range(9):
        x = 900 + k * 8
        pts += [(x, 524 if k % 2 == 0 else 532)]
    P(d, pts + [(964, 532), (964, 568)] + [(900 + k * 8, 576 if k % 2 == 0 else 568) for k in range(8, -1, -1)], (56, 56, 60), ow=2)
    R(d, [964, 520, 1040, 596], (136, 118, 96), r=6)                           # 映写側
    R(d, [1040, 486, 1100, 596], (90, 92, 100), r=6)                            # ランプの箱
    R(d, [1056, 456, 1084, 486], (90, 92, 100))
    for y in (510, 530, 550):
        d.line([(1048, y), (1092, y)], fill=(60, 62, 70), width=3)
    E(d, [1000, 600, 1024, 624], (180, 170, 150), ow=2)
    # 英語の専門書の山（左右の端と机の端）
    pal = [(70, 84, 120), (128, 60, 60), (110, 120, 80), (150, 130, 90), (60, 90, 96)]
    rnd = random.Random(37)
    for bx, by, n in ((40, FLOOR, 9), (190, FLOOR, 6), (1600, FLOOR, 8), (1760, FLOOR, 11), (1120, 620, 4)):
        y = by
        for k in range(n):
            w = rnd.randint(130, 170) if bx != 1120 else rnd.randint(70, 80)
            h = rnd.randint(26, 40)
            off = rnd.randint(-8, 8)
            R(d, [bx + off, y - h, bx + off + w, y], pal[(k + bx) % len(pal)], ow=2)
            d.line([(bx + off + 10, y - h / 2), (bx + off + w - 10, y - h / 2)], fill=(214, 200, 150), width=2)
            y -= h
    return img


def _lot(full=False):
    """撮影所の野外の空き地。full=True は巨大な港のミニチュア。"""
    img = vgrad((W, H), (172, 206, 232), (222, 228, 232))
    _cloud(img, 1400, 110, 0.8)
    _cloud(img, 860, 190, 0.5)
    d = _d(img)
    for x, w, h, c in ((40, 300, 140, (206, 200, 186)), (360, 260, 110, (196, 190, 176)), (760, 380, 150, (210, 204, 190)),
                       (1180, 300, 120, (198, 192, 178)), (1500, 420, 160, (208, 202, 188))):
        R(d, [x, 460 - h, x + w, 460], c)                                       # 遠くのステージ棟
        for k in range(int(w // 60)):
            P(d, [(x + k * 60, 460 - h), (x + k * 60 + 60, 460 - h), (x + k * 60 + 60, 460 - h - 26)], _shade(c, 0.9), ow=2)
    R(d, [1240, 200, 1300, 300], (150, 140, 130))                                # 給水塔
    for fx in (1240, 1300):
        d.line([(fx + (6 if fx < 1270 else -6), 300), (fx, 400)], fill=INK, width=5)
    for x in range(0, W, 26):                                                   # 板塀
        d.rectangle([x, 430, x + 20, 476], fill=(170, 144, 110))
    d.line([(0, 430), (W, 430)], fill=INK, width=2)
    d.line([(0, 476), (W, 476)], fill=INK, width=3)
    if not full:
        _band(img, 476, H, (204, 184, 146), (186, 166, 128))
        d = _d(img)
        for k in range(6):
            d.line([(880 - k * 90, 480 + k * 10), (420 - k * 160, H)], fill=(190, 170, 132), width=3)
        # 材木の山
        for k in range(5):
            y = 660 - k * 22
            R(d, [790 + k * 8, y - 20, 1130 - k * 6, y], (214, 180, 128), ow=2)
            for x in range(800 + k * 8, 1120 - k * 6, 40):
                d.line([(x, y - 18), (x, y - 2)], fill=(186, 150, 102), width=2)
        R(d, [810, 662, 1120, 676], (150, 118, 82), ow=2)
        for x, c in ((840, (200, 80, 70)), (910, (90, 120, 170)), (980, (230, 200, 110))):   # ペンキ缶
            R(d, [x, 668, x + 50, 716], (196, 198, 202))
            d.rectangle([x + 3, 684, x + 47, 700], fill=c)
            E(d, [x, 660, x + 50, 676], (220, 222, 226), ow=2)
        thick(d, [(70, 640), (290, 640)], (176, 136, 92), 14)                   # 馬（左端）
        for a, b in ((90, 110), (270, 250)):
            thick(d, [(a, 700), (b, 640)], (176, 136, 92), 10)
        R(d, [1640, 610, 1820, 660], (110, 120, 116))                           # 一輪車（右端）
        E(d, [1590, 640, 1640, 690], (60, 60, 64))
        d.line([(1820, 640), (1880, 690)], fill=INK, width=6)
        return img
    # ---- 港のミニチュア
    blob(img, [("e", [x - 200, 380, x + 200, 560]) for x in range(-60, W + 200, 300)], (126, 156, 108))   # 港の裏山
    d = _d(img)
    for x in range(-60, W + 200, 300):
        d.arc([x - 140, 410, x + 140, 560], 200, 300, fill=(150, 178, 128), width=6)
    _band(img, 500, 760, (110, 160, 178), (88, 138, 158))                       # 水面
    d = _d(img)
    d.line([(0, 500), (W, 500)], fill=INK, width=3)
    rnd = random.Random(42)
    for _ in range(70):
        x, y = rnd.randint(0, W), rnd.randint(520, 750)
        d.line([(x, y), (x + rnd.randint(30, 80), y)], fill=(150, 194, 206), width=2)
    for x, w, c in ((60, 200, (176, 176, 172)), (420, 140, (190, 186, 176)), (1560, 220, (182, 180, 174))):  # 岸の建物
        R(d, [x, 470, x + w, 504], c, ow=2)
    for cx in (330, 1460, 1840):                                                # 油のタンク
        R(d, [cx - 40, 470, cx + 40, 504], (206, 206, 200), ow=2)
        E(d, [cx - 40, 462, cx + 40, 478], (222, 222, 216), ow=2)
    for x0, x1, y0, y1 in ((120, 180, 504, 640), (640, 700, 504, 600), (1250, 1310, 504, 620), (1700, 1760, 504, 660)):
        R(d, [x0, y0, x1, y1], (170, 168, 162))                                 # 桟橋
    for cx in (680, 1420):                                                      # クレーン
        d.line([(cx, 504), (cx, 400)], fill=INK, width=6)
        d.line([(cx, 404), (cx + 90, 380)], fill=INK, width=5)
        d.line([(cx + 80, 382), (cx + 80, 430)], fill=INK, width=2)

    def ship(cx, wl, s):
        hull = (132, 138, 146)
        P(d, [(cx - 160 * s, wl - 18 * s), (cx + 150 * s, wl - 18 * s), (cx + 190 * s, wl - 28 * s),
              (cx + 150 * s, wl + 6 * s), (cx - 150 * s, wl + 6 * s)], hull, ow=2)
        R(d, [cx - 70 * s, wl - 52 * s, cx + 30 * s, wl - 18 * s], (156, 160, 168), ow=2)
        R(d, [cx - 40 * s, wl - 86 * s, cx - 4 * s, wl - 52 * s], (156, 160, 168), ow=2)
        P(d, [(cx + 40 * s, wl - 18 * s), (cx + 70 * s, wl - 18 * s), (cx + 66 * s, wl - 74 * s), (cx + 44 * s, wl - 74 * s)],
          (112, 116, 124), ow=2)
        d.line([(cx - 22 * s, wl - 86 * s), (cx - 22 * s, wl - 140 * s)], fill=INK, width=2)
        for gx, dirn in ((cx + 100 * s, 1), (cx - 110 * s, -1)):
            R(d, [gx - 18 * s, wl - 34 * s, gx + 18 * s, wl - 18 * s], (140, 146, 154), ow=2, r=4)
            d.line([(gx, wl - 28 * s), (gx + dirn * 44 * s, wl - 30 * s)], fill=INK, width=3)
        d.line([(cx - 150 * s, wl + 8 * s), (cx + 150 * s, wl + 8 * s)], fill=(196, 222, 230), width=2)

    for cx, wl, s in ((250, 560, 0.55), (1540, 548, 0.5), (1790, 610, 0.7), (960, 640, 0.95), (420, 700, 0.8),
                      (1180, 560, 0.45)):
        ship(cx, wl, s)
    d.rectangle([0, 760, W, 792], fill=(176, 172, 164))                         # ミニチュアのふち
    d.line([(0, 760), (W, 760)], fill=INK, width=3)
    d.line([(0, 792), (W, 792)], fill=INK, width=3)
    _band(img, 793, H, (196, 176, 138), (186, 166, 128))
    return img


def shinjuwan():
    return _lot(False)


def shinjuwan_full():
    return _lot(True)


def ryuchijo():
    """警察署の留置場。鉄格子と、高い小窓からの朝の光。"""
    img = vgrad((W, H), (174, 174, 170), (156, 156, 152))
    d = _d(img)
    for y in range(160, FLOOR, 120):                                            # コンクリートの継ぎ目
        d.line([(0, y), (W, y)], fill=(160, 160, 156), width=2)
    wood_floor(img, FLOOR, col=(140, 140, 136), line=(128, 128, 124))
    d = _d(img)
    R(d, [-10, 640, 420, 700], (150, 120, 92))                                  # 板の腰掛け
    R(d, [-10, 700, 420, 720], (126, 100, 76))
    _band(img, 140, 280, (252, 242, 210), (246, 230, 196), 160, 360)            # 小窓（朝）
    d = _d(img)
    R(d, [160, 140, 360, 280], None, ow=10, ink=(110, 110, 116))
    for x in (200, 240, 280, 320):
        d.line([(x, 140), (x, 280)], fill=(70, 72, 80), width=10)
    alpha(img, lambda dd: dd.polygon([(170, 150), (360, 150), (980, FLOOR), (560, FLOOR)], fill=(255, 244, 206, 46)), blur=16)
    alpha(img, lambda dd: dd.polygon([(560, FLOOR), (980, FLOOR), (1120, H), (640, H)], fill=(255, 244, 206, 40)), blur=10)
    d = _d(img)
    d.rectangle([780, 120, W, FLOOR], fill=(124, 124, 124))                     # 格子の向こうの廊下
    R(d, [1500, 260, 1560, 320], (240, 226, 180), r=10)
    _glow(img, 1530, 290, 120, (255, 236, 180), 50)
    d = _d(img)
    iron = (70, 72, 80)
    R(d, [770, 110, W + 10, 136], iron)
    R(d, [770, 820, W + 10, 846], iron)
    for x in range(790, W + 20, 62):
        R(d, [x, 110, x + 14, FLOOR], iron, ow=2)
    R(d, [1020, 110, 1034, FLOOR], iron)
    R(d, [1270, 110, 1284, FLOOR], iron)
    R(d, [1236, 480, 1290, 560], (90, 92, 100), r=4)                            # 錠前
    E(d, [1252, 500, 1272, 520], (40, 40, 44), ow=0)
    return img


def bokugou():
    """夜の防空壕の中。土の壁、ろうそく、入口の向こうに赤く染まった空。"""
    img = vgrad((W, H), (104, 80, 62), (82, 64, 50))
    d = _d(img)
    ox0, ox1, oy0, oy1 = 780, 1140, 70, 380
    sky = vgrad((ox1 - ox0, oy1 - oy0), (128, 34, 40), (236, 124, 64))         # 入口の向こうの空
    m = Image.new("L", sky.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, sky.width - 1, sky.height + 60], radius=150, fill=255)
    img.paste(sky, (ox0, oy0), m)
    d = _d(img)
    for x, w, h in ((790, 90, 50), (870, 70, 80), (930, 120, 40), (1040, 100, 70)):   # 遠くの屋根の影
        P(d, [(x, oy1), (x, oy1 - h), (x + w / 2, oy1 - h - 30), (x + w, oy1 - h), (x + w, oy1)], (44, 26, 30), ow=0)
    alpha(img, lambda dd: [dd.ellipse([x - 70, y - 40, x + 70, y + 40], fill=(70, 40, 46, 140))
                           for x, y in ((860, 180), (960, 140), (1080, 200))], blur=16)
    d = _d(img)
    d.rounded_rectangle([ox0, oy0, ox1, oy1 + 60], radius=150, outline=INK, width=4)
    for k in range(5):                                                          # 土の段
        y0 = oy1 + k * 36
        inset = 40 - k * 10
        P(d, [(ox0 + inset, y0), (ox1 - inset, y0), (ox1 - inset + 20, y0 + 36), (ox0 + inset - 20, y0 + 36)],
          _mix((150, 116, 88), (120, 92, 70), k / 5), ow=2)
    for x0 in (750, 1140):                                                      # 入口の柱と鴨居
        R(d, [x0, 50, x0 + 32, 560], (120, 92, 64))
    R(d, [740, 40, 1180, 72], (120, 92, 64))
    P(d, [(-10, -10), (560, -10), (300, 160), (-10, 420)], (66, 50, 40), ow=0)  # 丸い天井の暗がり
    P(d, [(W + 10, -10), (1360, -10), (1620, 160), (W + 10, 420)], (66, 50, 40), ow=0)
    for x0 in (230, 1660):                                                      # 支えの木
        R(d, [x0, 120, x0 + 36, 820], (112, 86, 62))
    R(d, [230, 120, 760, 150], (112, 86, 62))
    R(d, [1170, 120, 1696, 150], (112, 86, 62))
    rnd = random.Random(5)
    for _ in range(40):                                                         # 土の粒
        x, y = rnd.randint(0, W), rnd.randint(160, 700)
        if 700 < x < 1220:
            continue
        d.ellipse([x, y, x + 8, y + 5], fill=(92, 70, 54))
    d.rectangle([0, 820, W, H], fill=(76, 60, 48))                              # 床とござ
    d.line([(0, 820), (W, 820)], fill=INK, width=3)
    P(d, [(500, 860), (1420, 860), (1500, H + 10), (420, H + 10)], (150, 130, 90))
    _glow(img, 960, 220, 360, (255, 120, 70), 50)
    R(d := _d(img), [900, 640, 1020, 716], (140, 104, 70))                     # 箱とろうそく
    d.line([(900, 664), (1020, 664)], fill=INK, width=3)
    R(d, [950, 584, 970, 640], (246, 240, 224), ow=2)
    _glow(img, 960, 600, 300, (255, 200, 110), 80)
    d = _d(img)
    P(d, [(960, 548), (972, 574), (960, 584), (948, 574)], (255, 214, 110), ow=2)
    E(d, [956, 566, 964, 580], (255, 250, 220), ow=0)
    return img


def barricade():
    """撮影所の門に、机や板で組んだバリケードと赤い旗（文字なし）。"""
    img = vgrad((W, H), (196, 202, 210), (216, 218, 220))
    _cloud(img, 1300, 100, 0.9, col=(232, 234, 238))
    _cloud(img, 1720, 200, 0.6, col=(232, 234, 238))
    d = _d(img)
    for x, w, h, c in ((0, 420, 330, (190, 186, 178)), (1500, 420, 360, (196, 190, 180)), (560, 800, 260, (202, 198, 188))):
        R(d, [x, 560 - h, x + w, 560], c)                                       # 撮影所の建物
        y = 560 - h + 30
        while y < 520:
            for wx in range(x + 30, x + w - 40, 80):
                d.rectangle([wx, y, wx + 40, y + 30], fill=(150, 162, 172))
            y += 70
    d.rectangle([0, 560, W, 760], fill=(184, 180, 172))                         # 塀
    d.line([(0, 560), (W, 560)], fill=INK, width=3)
    for x in range(0, W, 140):
        d.line([(x, 560), (x, 760)], fill=(170, 166, 158), width=3)
    for x0 in (680, 1180):                                                      # 門柱
        R(d, [x0, 380, x0 + 60, 760], (206, 200, 188))
        R(d, [x0 - 8, 370, x0 + 68, 396], (186, 180, 168))
    _band(img, 760, H, (176, 170, 160), (164, 158, 148))
    d = _d(img)
    d.line([(0, 760), (W, 760)], fill=INK, width=3)
    # 旗竿と赤い旗
    for x, y0, flip in ((830, 150, 1), (1090, 200, -1), (1760, 220, 1)):
        d.line([(x, y0), (x, 700)], fill=(150, 120, 90), width=8)
        pts = [(x, y0 + 4)]
        for k in range(9):
            pts.append((x + flip * (k * 18), y0 + 4 + 10 * math.sin(k * 0.8)))
        pts += [(x + flip * 160, y0 + 104 + 10 * math.sin(8 * 0.8))]
        pts += [(x + flip * (k * 18), y0 + 100 + 10 * math.sin(k * 0.8)) for k in range(8, -1, -1)]
        P(d, pts, (214, 66, 62))
    # バリケード（ひっくり返した机・板・椅子・箱）
    wood = (160, 122, 84)
    P(d, [(560, 760), (620, 560), (1300, 520), (1360, 760)], (120, 96, 72))
    for x0, y0, x1, y1 in ((600, 660, 900, 600), (980, 540, 1300, 660), (700, 520, 1080, 600)):
        thick(d, [(x0, y0), (x1, y1)], (184, 146, 104), 22)
    for x, y in ((760, 560), (1110, 590)):                                      # ひっくり返した机
        R(d, [x - 110, y, x + 110, y + 40], wood)
        for lx in (x - 96, x + 84):
            R(d, [lx, y - 110, lx + 14, y], wood, ow=2)
    R(d, [900, 610, 1040, 700], (178, 138, 92))
    d.line([(900, 640), (1040, 640)], fill=INK, width=3)
    R(d, [840, 470, 880, 560], (140, 110, 80), ow=2)                            # 椅子
    R(d, [820, 540, 900, 560], (140, 110, 80), ow=2)
    for x0, x1 in ((590, 700), (1220, 1340)):                                   # 塀の前の土のう
        for k in range(3):
            E(d, [x0 + k * 30, 700 - k * 26, x0 + k * 30 + 90, 760 - k * 26], (190, 174, 136))
    return img


def soshigaya():
    """昭和の自宅の居間。ちゃぶ台、障子、縁側から庭。"""
    img = vgrad((W, H), (224, 210, 184), (206, 192, 166))
    fy = 760
    tatami_floor(img, fy)
    d = _d(img)
    _band(img, 140, 520, (196, 220, 236), (220, 230, 232), 560, 1360)          # 庭
    d = _d(img)
    d.rectangle([560, 520, 1360, 690], fill=(150, 174, 120))
    blob(img, [("e", [540, 300, 760, 560]), ("e", [700, 360, 880, 560]), ("e", [1140, 320, 1380, 560]),
               ("e", [1040, 400, 1200, 560])], (104, 146, 96))
    d = _d(img)
    for x, y in ((620, 380), (780, 420), (1200, 380), (1100, 440)):
        d.arc([x - 40, y - 30, x + 40, y + 30], 200, 320, fill=(140, 180, 120), width=6)
    R(d, [960, 520, 1020, 540], (176, 176, 170), ow=2)                          # 石灯籠
    R(d, [976, 450, 1004, 520], (176, 176, 170), ow=2)
    R(d, [952, 400, 1028, 450], (190, 190, 184), ow=2)
    R(d, [970, 412, 1010, 436], (110, 110, 106), ow=0)
    P(d, [(938, 404), (1042, 404), (990, 370)], (176, 176, 170), ow=2)
    for x, y in ((880, 600), (980, 620), (1080, 600)):                          # 飛び石
        E(d, [x - 40, y - 12, x + 40, y + 12], (196, 194, 184), ow=2)
    R(d, [540, 690, 1380, 760], (196, 160, 116))                                # 縁側
    for x in range(560, 1380, 90):
        d.line([(x, 692), (x, 758)], fill=(176, 140, 100), width=2)
    for x0 in (420, 1360):                                                      # 開いた障子
        R(d, [x0, 140, x0 + 140, 690], (244, 238, 220))
        for gx in range(x0, x0 + 141, 35):
            d.line([(gx, 140), (gx, 600)], fill=(156, 124, 90), width=3)
        for gy in range(140, 600, 60):
            d.line([(x0, gy), (x0 + 140, gy)], fill=(156, 124, 90), width=3)
        R(d, [x0, 600, x0 + 140, 690], (172, 138, 100))
        R(d, [x0, 140, x0 + 140, 690], None)
    R(d, [-10, 110, W + 10, 140], (150, 114, 80))                               # 鴨居
    for x0 in (400, 1500):
        R(d, [x0, 110, x0 + 22, fy], (140, 104, 72))
    R(d, [60, 420, 300, 530], (140, 96, 62), r=14)                              # ラジオ（左端）
    R(d, [80, 440, 210, 510], (210, 190, 150), ow=2)
    for x in range(90, 206, 14):
        d.line([(x, 446), (x, 504)], fill=(170, 150, 110), width=3)
    E(d, [226, 446, 256, 476], (90, 70, 50), ow=2)
    E(d, [226, 482, 256, 512], (90, 70, 50), ow=2)
    R(d, [40, 530, 320, fy], (150, 112, 76))
    R(d, [1640, 160, 1780, 420], (150, 106, 70), r=10)                          # 柱時計（右端）
    _clock(d, 1710, 240, 50, rim=(150, 106, 70))
    R(d, [1690, 320, 1730, 400], (226, 200, 140), ow=2)
    d.line([(1710, 300), (1710, 380)], fill=INK, width=3)
    E(d, [1700, 372, 1720, 392], (210, 180, 110), ow=2)
    cx = 960                                                                    # ちゃぶ台
    R(d, [cx - 150, 732, cx - 126, 830], (110, 74, 52))
    R(d, [cx + 126, 732, cx + 150, 830], (110, 74, 52))
    E(d, [cx - 190, 700, cx + 190, 752], (128, 88, 60))
    E(d, [cx - 190, 694, cx + 190, 740], (148, 104, 72))
    E(d, [cx - 70, 650, cx - 10, 712], (200, 196, 180))                         # 急須と湯のみ
    d.arc([cx - 60, 630, cx - 20, 670], 200, 340, fill=INK, width=4)
    P(d, [(cx - 12, 680), (cx + 14, 668), (cx + 12, 680), (cx - 10, 692)], (200, 196, 180), ow=2)
    for ux in (cx + 40, cx + 90):
        R(d, [ux, 682, ux + 30, 714], (206, 214, 200), r=4, ow=2)
    return img


def prefab():
    """自宅の庭のトタン屋根の小屋の中。作業台に模型、雨漏りを受けるバケツ。"""
    img = vgrad((W, H), (188, 160, 122), (170, 144, 108))
    d = _d(img)
    for x in range(0, W, 110):                                                  # 板壁
        d.line([(x, 160), (x, FLOOR)], fill=(162, 136, 102), width=4)
    P(d, [(-10, -10), (W + 10, -10), (W + 10, 120), (-10, 200)], (150, 154, 160))   # トタン屋根の裏
    for x in range(-10, W + 10, 48):
        y = 200 - 80 * (x + 10) / (W + 20)
        d.line([(x, -10), (x, y)], fill=(130, 134, 140), width=6)
    d.line([(-10, 200), (W + 10, 120)], fill=INK, width=4)
    R(d, [-10, 180, W + 10, 206], (132, 102, 72))
    wood_floor(img, FLOOR, col=(120, 100, 80), line=(104, 86, 68))
    d = _d(img)
    _band(img, 250, 440, (150, 158, 170), (170, 176, 186), 660, 900)            # 雨の窓
    d = _d(img)
    for k in range(24):
        x = 670 + (k * 37) % 230
        y = 256 + (k * 53) % 170
        d.line([(x, y), (x - 10, y + 24)], fill=(214, 222, 232), width=2)
    _window(d, 660, 250, 900, 440, sky=None, frame=(200, 190, 170))
    R(d, [620, 600, 900, 628], (156, 120, 84))                                  # 作業台
    R(d, [632, 628, 656, FLOOR], (136, 104, 72))
    R(d, [864, 628, 888, FLOOR], (136, 104, 72))
    _biplane_side(d, 650, 566, 0.62)                                            # 模型の飛行機
    R(d, [800, 520, 880, 600], (226, 222, 210))                                 # 模型のビル
    for wy in (534, 564):
        for wx in (812, 846):
            d.rectangle([wx, wy, wx + 18, wy + 18], fill=(120, 130, 150))
    for x, h in ((780, 30), (884, 46)):
        R(d, [x - 18, 600 - h, x, 600], (196, 190, 176), ow=2)
    # 雨漏りとバケツ
    E(d, [1010, 196, 1050, 214], (120, 124, 130), ow=2)
    for k, y in enumerate((260, 380, 520, 660)):
        P(d, [(1030, y - 12), (1038, y + 6), (1030, y + 12), (1022, y + 6)], (160, 200, 232), ow=2)
    alpha(img, lambda dd: dd.ellipse([950, 860, 1110, 900], fill=(130, 170, 200, 110)), blur=3)
    d = _d(img)
    P(d, [(980, 780), (1080, 780), (1068, 880), (992, 880)], (170, 176, 184))
    E(d, [976, 768, 1084, 794], (190, 196, 204))
    E(d, [988, 772, 1072, 790], (130, 170, 200), ow=0)
    d.arc([980, 730, 1080, 800], 190, 350, fill=INK, width=4)
    for x, y in ((1650, 300), (1760, 300), (1700, 430)):                        # 壁の道具（右端）
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=INK)
    R(d, [1620, 306, 1680, 330], (110, 110, 116), ow=2)                         # のこぎり
    P(d, [(1680, 306), (1800, 306), (1800, 340), (1680, 330)], (196, 200, 206), ow=2)
    R(d, [1694, 436, 1706, 540], (150, 112, 76), ow=2)                          # 金づち
    R(d, [1670, 426, 1730, 448], (90, 92, 100), ow=2)
    for k in range(3):                                                          # 端材（左端）
        R(d, [40 + k * 30, 520 + k * 10, 70 + k * 30, FLOOR], (200, 170, 126), ow=2)
    return img


def koryoriya():
    """京都の小料理屋のカウンター。のれん（文字なし）、徳利とおちょこ。"""
    img = vgrad((W, H), (204, 168, 126), (180, 146, 108))
    d = _d(img)
    d.rectangle([0, 0, W, 110], fill=(150, 112, 78))                            # 天井
    for x in range(0, W, 60):
        d.line([(x, 0), (x, 110)], fill=(134, 98, 68), width=3)
    d.line([(0, 110), (W, 110)], fill=INK, width=4)
    for y in (260, 420):                                                        # 酒の棚（ラベル無地）
        R(d, [640, y, 1260, y + 16], (130, 94, 62))
        for k, x in enumerate(range(670, 1230, 64)):
            col = ((70, 100, 74), (110, 76, 50), (60, 70, 90))[(k + y // 10) % 3]
            R(d, [x, y - 120, x + 40, y], col, r=10)
            R(d, [x + 12, y - 150, x + 28, y - 116], col, ow=2)
            d.rectangle([x + 8, y - 80, x + 32, y - 40], fill=(236, 228, 210))
    R(d, [1280, 110, 1760, 300], (62, 82, 122))                                 # のれん（文字なし）
    for k in range(1, 4):
        x = 1280 + 120 * k
        d.line([(x, 120), (x, 300)], fill=(44, 60, 92), width=5)
    R(d, [1266, 100, 1774, 120], (120, 90, 60))
    d.rectangle([1296, 300, 1744, 560], fill=(120, 96, 76))                     # のれんの奥（板場）
    d.line([(1296, 300), (1296, 560)], fill=INK, width=3)
    for x, y in ((300, 140), (1860, 150)):                                      # 提灯（文字なし）
        d.line([(x, 110), (x, y)], fill=INK, width=3)
        E(d, [x - 40, y, x + 40, y + 110], (244, 230, 200))
        for dy in (24, 48, 72, 94):
            d.line([(x - 36, y + dy), (x + 36, y + dy)], fill=(214, 196, 160), width=2)
        R(d, [x - 22, y - 8, x + 22, y + 4], (60, 50, 44), ow=0)
        R(d, [x - 22, y + 106, x + 22, y + 118], (60, 50, 44), ow=0)
        _glow(img, x, y + 55, 160, (255, 210, 140), 50)
        d = _d(img)
    R(d, [-10, 560, W + 10, 590], (110, 80, 56))                                # 奥の台
    R(d, [-10, 636, W + 10, 676], (226, 196, 148))                              # カウンター
    d.rectangle([0, 676, W, H], fill=(120, 86, 58))
    d.line([(0, 676), (W, 676)], fill=INK, width=3)
    for x in range(80, W, 260):
        d.line([(x, 680), (x, H)], fill=(104, 74, 50), width=4)
    R(d, [880, 562, 930, 640], (244, 240, 230), r=16)                          # 徳利とおちょこ
    R(d, [894, 548, 916, 568], (244, 240, 230), ow=2)
    d.line([(882, 600), (928, 600)], fill=(80, 110, 150), width=4)
    for ox in (960, 1010):
        P(d, [(ox, 618), (ox + 34, 618), (ox + 28, 640), (ox + 6, 640)], (244, 240, 230), ow=2)
    E(d, [1050, 626, 1130, 646], (196, 150, 110), ow=2)                         # 小皿
    E(d, [1070, 622, 1110, 636], (120, 160, 100), ow=0)
    return img


def kaigishitsu():
    """1954年の会社の会議室。長机、灰皿、黒板。"""
    img = vgrad((W, H), (222, 216, 202), (206, 200, 186))
    d = _d(img)
    d.rectangle([0, 640, W, FLOOR], fill=(150, 120, 92))                        # 腰板
    d.line([(0, 640), (W, 640)], fill=INK, width=3)
    wood_floor(img, FLOOR, col=(130, 104, 80), line=(112, 90, 70))
    d = _d(img)
    R(d, [640, 140, 1280, 440], (56, 80, 66))                                   # 黒板
    R(d, [626, 126, 1294, 454], None, ow=14, ink=(140, 104, 72))
    R(d, [626, 444, 1294, 462], (140, 104, 72))
    chalk = (234, 236, 228)
    E(d, [720, 190, 840, 290], None, ow=4, ink=chalk)                           # チョークのタコ
    d.ellipse([752, 226, 764, 238], fill=chalk)
    d.ellipse([796, 226, 808, 238], fill=chalk)
    for k in range(6):                                                          # くねくねの足
        x0 = 734 + k * 18
        spread = (k - 2.5) * 30
        pts = [(x0 + spread * (j / 14) + 9 * math.sin(j / 14 * 3 * math.pi + k), 284 + 84 * (j / 14)) for j in range(15)]
        ex, ey = pts[-1]
        side = 1 if spread > 0 else -1
        pts += [(ex + side * (8 - 8 * math.cos(a)), ey - 8 * math.sin(a)) for a in (0.8, 1.6, 2.4, 3.1)]
        d.line(pts, fill=chalk, width=4, joint="curve")
    _text_c(d, 930, 200, "？", 120, chalk)
    for y, w in ((230, 180), (290, 220), (350, 160)):
        d.line([(1050, y), (1050 + w, y)], fill=(180, 196, 186), width=4)
    d.line([(900, 400), (1000, 400)], fill=(180, 196, 186), width=4)
    R(d, [1600, 140, 1880, 520], (200, 220, 232))                               # 窓とブラインド（右端）
    for y in range(150, 520, 22):
        d.line([(1604, y), (1876, y)], fill=(232, 232, 226), width=8)
    R(d, [1600, 140, 1880, 520], None, ow=10, ink=(150, 140, 126))
    _clock(d, 180, 230, 54)
    for x in (700, 1220):                                                       # 椅子の背
        R(d, [x - 40, 500, x + 40, 600], (110, 80, 58), r=10)
    R(d, [560, 600, 1360, 640], (124, 88, 60))                                  # 長机
    d.rectangle([570, 640, 1350, 720], fill=(104, 74, 50))
    d.line([(570, 720), (1350, 720)], fill=INK, width=3)
    for x in (840, 1080):                                                       # 灰皿と煙
        E(d, [x - 34, 588, x + 34, 610], (196, 206, 210))
        E(d, [x - 22, 592, x + 22, 604], (150, 156, 160), ow=0)
        d.line([(x + 4, 594), (x + 30, 586)], fill=(250, 250, 246), width=4)
        pts = [(x + 30 + 8 * math.sin(j * 0.9), 584 - j * 16) for j in range(6)]
        d.line(pts, fill=(236, 236, 236), width=3, joint="curve")
    for x in (930, 1160):                                                       # 湯のみ
        R(d, [x, 572, x + 30, 604], (206, 214, 200), r=4, ow=2)
    R(d, [740, 590, 800, 604], (246, 244, 236), ow=2)                           # 書類
    return img


def happyou():
    """映画の製作発表の会場。壇上の長机に白いテーブルクロス、マイク、後ろの幕（文字なし）。"""
    img = vgrad((W, H), (70, 74, 112), (60, 62, 96))
    d = _d(img)
    for x in range(0, W, 48):                                                   # 幕のひだ
        d.line([(x, 0), (x, 700)], fill=(56, 60, 96), width=8)
    R(d, [640, 60, 1300, 170], (232, 222, 196))                                 # 横断幕（無地）
    R(d, [656, 74, 1284, 156], None, ow=4, ink=(196, 160, 90))
    for x in range(0, W, 120):                                                  # 幕の上の飾り
        d.arc([x, -40, x + 120, 40], 0, 180, fill=(196, 160, 90), width=6)
    d.rectangle([0, 700, W, H], fill=(150, 116, 86))                            # 壇
    d.line([(0, 700), (W, 700)], fill=INK, width=3)
    for y in (760, 840, 940):
        d.line([(0, y), (W, y)], fill=(136, 104, 76), width=3)
    for cx in (200, 1720):                                                      # 花のスタンド
        d.line([(cx, 520), (cx, 700)], fill=INK, width=6)
        for fx in (cx - 40, cx + 40):
            d.line([(cx, 660), (fx, 700)], fill=INK, width=5)
        blob(img, [("e", [cx - 110, 360, cx + 110, 540])], (120, 160, 110))
        d = _d(img)
        for fx, fy, c in ((-60, 400, (236, 120, 120)), (0, 380, (246, 222, 120)), (60, 410, (240, 160, 180)),
                          (-30, 460, (246, 246, 236)), (40, 470, (236, 120, 120)), (-70, 480, (246, 222, 120))):
            E(d, [cx + fx - 26, fy - 26, cx + fx + 26, fy + 26], c, ow=2)
    R(d, [520, 560, 1400, 600], (250, 250, 246))                                # 白いテーブルクロス
    d.rectangle([530, 600, 1390, 760], fill=(244, 244, 240))
    for x in range(560, 1390, 60):
        d.line([(x, 604), (x - 4, 756)], fill=(222, 222, 216), width=4)
    d.line([(530, 600), (530, 760), (1390, 760), (1390, 600)], fill=INK, width=3)
    for x in (800, 960, 1120):                                                  # 卓上マイク
        R(d, [x - 26, 548, x + 26, 562], (60, 60, 66), r=6)
        d.line([(x, 550), (x, 500)], fill=(60, 60, 66), width=6)
        R(d, [x - 18, 452, x + 18, 504], (180, 184, 190), r=16)
        for y in (466, 478, 490):
            d.line([(x - 14, y), (x + 14, y)], fill=(130, 134, 140), width=2)
    for x in (880, 1040):                                                       # 水のコップ
        R(d, [x - 12, 520, x + 12, 560], (210, 230, 240), ow=2)
    return img


def ueno():
    """動物園。象のいる柵と熊の檻。"""
    img = vgrad((W, H), (176, 210, 236), (220, 230, 232))
    _cloud(img, 1300, 90, 0.7)
    blob(img, [("e", [x - 160, 160 + (x * 7) % 80, x + 160, 440]) for x in range(-60, W + 160, 220)], (120, 166, 110))
    d = _d(img)
    for x in range(-60, W + 160, 220):
        d.arc([x - 100, 200 + (x * 7) % 80, x + 100, 360], 200, 320, fill=(150, 190, 130), width=6)
    _band(img, 420, 700, (206, 186, 148), (196, 176, 138))
    d = _d(img)
    d.line([(0, 420), (W, 420)], fill=INK, width=3)
    for x in range(0, W, 30):                                                   # 奥の木の柵
        d.line([(x, 380), (x, 420)], fill=(150, 120, 86), width=6)
    d.line([(0, 384), (W, 384)], fill=(150, 120, 86), width=5)
    # 象（横向き）
    ex, ey, s = 930, 470, 1.0
    gray = (160, 160, 168)
    blob(img, [("e", [ex - 140 * s, ey - 80 * s, ex + 110 * s, ey + 76 * s]),
               ("r", [ex - 116 * s, ey + 10 * s, ex - 74 * s, ey + 150 * s]),
               ("r", [ex - 58 * s, ey + 10 * s, ex - 18 * s, ey + 146 * s]),
               ("r", [ex + 24 * s, ey + 10 * s, ex + 64 * s, ey + 150 * s]),
               ("r", [ex + 74 * s, ey + 10 * s, ex + 108 * s, ey + 146 * s]),
               ("e", [ex + 70 * s, ey - 112 * s, ex + 196 * s, ey + 24 * s])], gray)
    d = _d(img)
    thick(d, [(ex + 180 * s, ey - 10 * s), (ex + 196 * s, ey + 60 * s), (ex + 188 * s, ey + 120 * s), (ex + 166 * s, ey + 134 * s)],
          gray, int(28 * s))
    E(d, [ex + 60 * s, ey - 92 * s, ex + 148 * s, ey + 34 * s], (146, 146, 156))  # 耳
    d.ellipse([ex + 164 * s, ey - 62 * s, ex + 176 * s, ey - 50 * s], fill=INK)
    d.arc([ex + 150 * s, ey - 10 * s, ex + 210 * s, ey + 40 * s], 60, 150, fill=(250, 248, 236), width=6)
    d.line([(ex - 138 * s, ey - 20 * s), (ex - 160 * s, ey + 50 * s)], fill=INK, width=4)
    R(d, [-10, 640, W + 10, 664], (150, 120, 86))                               # 手前の柵
    for x in range(20, W, 80):
        R(d, [x, 600, x + 16, 700], (150, 120, 86), ow=2)
    d.line([(0, 612), (W, 612)], fill=(150, 120, 86), width=8)
    _band(img, 700, H, (214, 206, 188), (200, 192, 174))
    d = _d(img)
    d.line([(0, 700), (W, 700)], fill=INK, width=3)
    # 熊の檻（右端）
    R(d, [1570, 300, 1910, 700], (110, 104, 100))
    blob(img, [("e", [1640, 470, 1840, 690]), ("e", [1670, 380, 1810, 500]),
               ("e", [1664, 370, 1704, 410]), ("e", [1776, 370, 1816, 410])], (126, 92, 64))
    d = _d(img)
    E(d, [1712, 438, 1768, 486], (176, 140, 104), ow=2)
    d.ellipse([1732, 444, 1748, 456], fill=INK)
    d.ellipse([1700, 418, 1710, 428], fill=INK)
    d.ellipse([1770, 418, 1780, 428], fill=INK)
    for x in range(1580, 1910, 40):
        R(d, [x, 300, x + 10, 700], (70, 72, 80), ow=0)
    R(d, [1556, 280, 1924, 304], (70, 72, 80))
    R(d, [1556, 690, 1924, 714], (70, 72, 80))
    blob(img, [("e", [-60, 120, 260, 520])], (110, 156, 100))                   # 木（左端）
    d = _d(img)
    R(d, [80, 480, 120, 700], (120, 92, 70))
    return img


def ijika():
    """三重の漁村。急な坂道、漁師の家、海、後ろに山。"""
    img = vgrad((W, H), (170, 206, 234), (214, 228, 236))
    _cloud(img, 1500, 100, 0.7)
    blob(img, [("p", [(-20, 460), (300, 260), (560, 180), (860, 110), (1100, 150), (1400, 240), (1700, 300), (W + 20, 380),
                      (W + 20, 520), (-20, 520)])], (116, 156, 108))            # 山
    d = _d(img)
    for x0, y0, x1, y1 in ((700, 200, 900, 360), (1000, 200, 1240, 360), (400, 280, 600, 420)):
        d.arc([x0, y0, x1, y1], 200, 330, fill=(140, 180, 126), width=6)
    d.rectangle([1300, 440, W, 640], fill=(96, 156, 196))                       # 海（右）
    d.line([(1300, 440), (W, 440)], fill=INK, width=3)
    for x, y in ((1380, 480), (1600, 520), (1760, 470), (1500, 590), (1820, 580)):
        d.line([(x, y), (x + 70, y)], fill=(150, 196, 222), width=3)
    for x, y in ((1680, 500), (1840, 540)):                                     # 小舟
        P(d, [(x - 40, y), (x + 40, y), (x + 28, y + 14), (x - 28, y + 14)], (150, 112, 80), ow=2)
    _band(img, 520, H, (168, 160, 140), (150, 142, 124), 0, 1300)               # 斜面
    _band(img, 640, H, (168, 160, 140), (150, 142, 124), 1300, W)
    d = _d(img)
    P(d, [(840, H), (1080, H), (990, 430), (950, 430)], (214, 204, 182))        # 急な坂道（石段）
    for k in range(1, 18):
        t = (k / 18) ** 1.6
        y = 430 + (H - 430) * t
        xl, xr = 950 - 110 * t, 990 + 90 * t
        if y < 720:
            d.line([(xl, y), (xr, y)], fill=(186, 176, 154), width=2)
    d.line([(840, H), (950, 430)], fill=INK, width=3)
    d.line([(1080, H), (990, 430)], fill=INK, width=3)
    for x, by, w, h in ((150, 520, 170, 90), (360, 500, 150, 80), (560, 470, 130, 70), (760, 450, 110, 64),
                        (1060, 450, 110, 64), (1200, 480, 120, 70), (1400, 640, 170, 100), (1640, 660, 200, 110),
                        (0, 640, 200, 120), (260, 640, 220, 120), (700, 600, 160, 110), (1110, 600, 160, 110)):
        _house(d, x, by, w, h, wall=(206, 188, 156) if (x // 100) % 2 else (190, 170, 140))
    for x in (40, 1880):                                                        # 干した網
        d.line([(x, 640), (x, 760)], fill=INK, width=4)
    return img


def ginza_okujo():
    """1954年の銀座のビルの屋上から見た町並み。遠くに時計台のあるビル（ロゴや店名なし）。"""
    img = vgrad((W, H), (184, 212, 234), (222, 228, 230))
    _cloud(img, 1200, 90, 0.7)
    d = _d(img)
    E(d, [1680, 50, 1760, 130], (220, 110, 96))                                 # アドバルーン（垂れ幕は無地）
    d.line([(1720, 130), (1720, 160)], fill=INK, width=2)
    R(d, [1700, 160, 1740, 360], (250, 248, 240))
    d.line([(1720, 360), (1760, 600)], fill=INK, width=2)
    rnd = random.Random(54)
    for x, w, top, c in ((0, 200, 380, (196, 190, 180)), (200, 160, 420, (210, 204, 192)), (360, 200, 360, (184, 180, 172)),
                         (560, 140, 400, (204, 196, 182)), (700, 170, 440, (190, 186, 178)),
                         (1100, 180, 380, (200, 194, 184)), (1280, 160, 430, (186, 182, 174)),
                         (1440, 220, 370, (206, 200, 188)), (1660, 260, 410, (194, 188, 178))):
        _bldg(d, x, top, x + w, 620, c, ww=18, wh=22, gx=34, gy=44)
    # 時計台のビル
    R(d, [870, 360, 1090, 620], (230, 220, 200))
    for y in range(386, 600, 44):
        for x in range(890, 1070, 34):
            d.rectangle([x, y, x + 18, y + 24], fill=(170, 184, 196))
    R(d, [926, 250, 1034, 360], (230, 220, 200))
    _clock(d, 980, 300, 36, rim=(150, 130, 100))
    P(d, [(914, 252), (1046, 252), (1024, 216), (936, 216)], (110, 120, 116))
    d.line([(980, 216), (980, 176)], fill=INK, width=4)
    for x in range(0, W, 240):                                                  # 電柱と電線
        d.line([(x + 60, 520), (x + 60, 620)], fill=INK, width=4)
    d.line([(0, 540), (W, 532)], fill=INK, width=2)
    d.rectangle([0, 620, W, 640], fill=(170, 166, 160))
    R(d, [-10, 640, W + 10, 720], (200, 196, 188))                              # 屋上の手すり壁
    d.rectangle([-10, 640, W + 10, 656], fill=(214, 210, 202))
    _band(img, 721, H, (176, 174, 170), (162, 160, 156))
    d = _d(img)
    d.line([(0, 720), (W, 720)], fill=INK, width=3)
    R(d, [1640, 440, 1880, 600], (170, 176, 184), r=16)                         # 屋上の水槽（右端）
    for fx in (1660, 1860):
        R(d, [fx - 8, 600, fx + 8, 640], (120, 124, 130), ow=2)
    return img


def _minia(broken=False):
    """撮影所の中のミニチュアの銀座（夜）。broken=True は時計台のビルが崩れて石膏の破片が散らばる。"""
    img = vgrad((W, H), (32, 38, 64), (56, 60, 88))
    d = _d(img)
    rnd = random.Random(10)
    for _ in range(50):                                                         # 書き割りの星
        x, y = rnd.randint(640, W), rnd.randint(150, 330)
        d.ellipse([x, y, x + 4, y + 4], fill=(210, 214, 230))
    R(d, [-10, 40, W + 10, 62], (90, 90, 100))                                  # 照明の足場
    for x in range(0, W, 60):
        d.line([(x, 62), (x + 30, 100), (x + 60, 62)], fill=(80, 80, 92), width=3)
    R(d, [-10, 96, W + 10, 108], (90, 90, 100))
    for lx in (420, 780, 1140, 1500):
        R(d, [lx - 34, 108, lx + 34, 156], (70, 70, 80), r=8)
        E(d, [lx - 26, 144, lx + 26, 166], (255, 240, 200))
    alpha(img, lambda dd: [dd.polygon([(lx - 26, 160), (lx + 26, 160), (lx + 220, 720), (lx - 220, 720)], fill=(255, 236, 190, 18))
                           for lx in (420, 780, 1140, 1500)], blur=20)
    d = _d(img)
    lit = ((255, 220, 140), 0.55)
    for x, w, top, c in ((-20, 200, 440, (86, 90, 108)), (180, 160, 470, (96, 96, 112)), (340, 190, 420, (80, 86, 104)),
                         (1120, 180, 430, (92, 94, 110)), (1300, 200, 460, (84, 88, 106)), (1500, 180, 410, (96, 96, 112)),
                         (1680, 260, 450, (86, 90, 108))):
        _bldg(d, x, top, x + w, 640, c, win=(60, 64, 80), ww=16, wh=20, gx=30, gy=40, lit=lit, rnd=rnd)
    for x, w, top, c in ((520, 170, 500, (120, 116, 124)), (690, 170, 540, (130, 124, 130)),
                         (1100, 160, 520, (124, 120, 128)), (1260, 170, 560, (116, 114, 124))):
        _bldg(d, x, top, x + w, 680, c, win=(70, 72, 86), ww=18, wh=22, gx=34, gy=44, lit=lit, rnd=rnd)
    # 時計台のビル
    body = (196, 186, 170)
    if not broken:
        R(d, [860, 440, 1060, 690], body)
        R(d, [912, 330, 1008, 440], body)
        _clock(d, 960, 376, 30, face=(255, 244, 210), rim=(130, 110, 90))
        P(d, [(900, 332), (1020, 332), (1000, 300), (920, 300)], (100, 110, 108))
        d.line([(960, 300), (960, 268)], fill=INK, width=4)
    else:
        P(d, [(860, 690), (860, 500), (900, 470), (930, 520), (970, 456), (1010, 510), (1060, 480), (1060, 690)], body)
        d.line([(900, 470), (930, 520), (970, 456), (1010, 510)], fill=(150, 140, 126), width=3)
    for y in range(470 if not broken else 540, 670, 44):
        for x in range(880, 1040, 36):
            d.rectangle([x, y, x + 18, y + 24], fill=(255, 220, 140) if (x + y) % 3 else (90, 90, 104))
    for x in range(560, 1400, 200):                                             # 電柱と電線
        d.line([(x, 560), (x, 690)], fill=INK, width=4)
        d.line([(x - 16, 570), (x + 16, 570)], fill=INK, width=3)
    for dy in (0, 10):
        d.line([(560, 574 + dy), (760, 580 + dy), (960, 574 + dy), (1160, 580 + dy), (1360, 574 + dy)], fill=(30, 30, 36), width=2)
    d.rectangle([0, 690, W, 720], fill=(100, 100, 108))                         # 通りと線路
    d.line([(0, 702), (W, 702)], fill=(140, 140, 150), width=2)
    d.line([(0, 712), (W, 712)], fill=(140, 140, 150), width=2)
    if broken:
        alpha(img, lambda dd: [dd.ellipse([x - 110, y - 70, x + 110, y + 70], fill=(226, 222, 212, 120))
                               for x, y in ((900, 470), (1020, 500), (960, 420), (840, 560), (1080, 600))], blur=26)
        d = _d(img)
        P(d, [(940, 712), (990, 600), (1110, 636), (1080, 716)], body)          # 落ちた塔と時計
        E(d, [1000, 616, 1060, 676], (255, 244, 210), ow=2)
        d.line([(1030, 646), (1046, 630)], fill=INK, width=3)
        d.line([(1030, 646), (1018, 660)], fill=INK, width=3)
        P(d, [(1080, 640), (1112, 620), (1140, 650), (1110, 676)], (100, 110, 108), ow=2)
        rnd2 = random.Random(77)
        for _ in range(46):                                                     # 石膏の破片
            x, y = rnd2.randint(770, 1150), rnd2.randint(560, 740)
            r = rnd2.randint(6, 20)
            pts = [(x + r * math.cos(a) * rnd2.uniform(0.6, 1.1), y + r * math.sin(a) * rnd2.uniform(0.6, 1.1))
                   for a in (0, 1.4, 2.6, 3.8, 5.1)]
            P(d, pts, (236, 232, 222), ow=2)
    R(d, [-10, 720, W + 10, 780], (120, 92, 66))                                # ミニチュアの台のふち
    d.rectangle([0, 780, W, H], fill=(44, 42, 50))
    for x, fx in ((110, 1), (1810, -1)):                                        # 照明（左右の端）
        d.line([(x, 520), (x, 1000)], fill=(20, 20, 24), width=8)
        R(d, [x - 50, 440, x + 50, 520], (70, 70, 80), r=10)
        E(d, [x + fx * 40 - 16, 450, x + fx * 40 + 16, 510], (255, 240, 200))
    return img


def minia():
    return _minia(False)


def minia_kowareta():
    return _minia(True)


def pool():
    """撮影所のトタン張りの撮影用プール。水面、照明、水の中へ伸びるケーブル。秋の空。"""
    img = vgrad((W, H), (140, 192, 232), (206, 222, 232))
    d = _d(img)
    for x, y, ln in ((700, 90, 300), (1100, 140, 360), (1500, 70, 260), (900, 200, 200)):   # すじ雲
        d.line([(x, y), (x + ln, y - 20)], fill=(240, 244, 248), width=6)
        d.line([(x + 40, y + 14), (x + ln - 40, y - 4)], fill=(236, 240, 246), width=4)
    for cx in (140, 1790):                                                      # 塀の向こうの紅葉
        blob(img, [("e", [cx - 160, 160, cx + 160, 360])], (226, 150, 76), ink=(150, 96, 60))
    blob(img, [("e", [1500, 220, 1700, 340])], (236, 196, 90), ink=(150, 120, 60))
    d = _d(img)
    d.rectangle([0, 300, W, 520], fill=(176, 180, 186))                         # トタン塀
    for x in range(0, W, 20):
        d.line([(x, 300), (x, 520)], fill=(156, 160, 168), width=4)
    for x in range(0, W, 300):
        R(d, [x, 290, x + 18, 520], (136, 108, 78), ow=2)
    d.line([(0, 300), (W, 300)], fill=INK, width=3)
    R(d, [-10, 510, W + 10, 532], (190, 188, 182))                              # 向こう岸のふち
    _band(img, 532, 760, (110, 150, 164), (92, 134, 150))                       # 冷たい水面
    d = _d(img)
    rnd = random.Random(21)
    for _ in range(60):
        x, y = rnd.randint(0, W), rnd.randint(548, 750)
        d.line([(x, y), (x + rnd.randint(30, 90), y)], fill=(156, 192, 204), width=2)
    for cx, fx in ((150, 1), (1780, -1)):                                       # 照明
        d.line([(cx, 330), (cx, 760)], fill=INK, width=8)
        R(d, [cx - 56, 250, cx + 56, 336], (80, 80, 90), r=12)
        E(d, [cx + fx * 44 - 18, 262, cx + fx * 44 + 18, 324], (255, 244, 210))
    alpha(img, lambda dd: [dd.polygon([(170, 270), (190, 320), (1000, 760), (700, 760)], fill=(255, 244, 210, 26)),
                           dd.polygon([(1760, 270), (1740, 320), (900, 760), (1200, 760)], fill=(255, 244, 210, 26))], blur=18)
    d = _d(img)
    R(d, [880, 694, 1040, 760], (90, 90, 98))                                  # 分電箱とケーブル
    for k, (ex, ey) in enumerate(((800, 620), (960, 600), (1100, 640))):
        thick(d, [(900 + k * 60, 700), ((900 + k * 60 + ex) / 2, 660), (ex, ey)], (40, 40, 44), 8, ow=2)
        d.ellipse([ex - 26, ey - 6, ex + 26, ey + 8], outline=(176, 206, 216), width=3)
    d.rectangle([0, 760, W, 800], fill=(176, 172, 164))                         # 手前のふち
    d.line([(0, 760), (W, 760)], fill=INK, width=3)
    d.line([(0, 800), (W, 800)], fill=INK, width=3)
    _band(img, 801, H, (188, 172, 140), (176, 160, 128))
    return img


def nakaniwa():
    """撮影所の中庭。大きな布をかぶせた何か（中身は見せない）と、しめ縄・榊・お供え。"""
    img = vgrad((W, H), (186, 214, 236), (222, 230, 234))
    _cloud(img, 1450, 90, 0.7)
    d = _d(img)
    for x, w, h, c in ((-10, 520, 420, (214, 204, 186)), (1400, 530, 440, (206, 198, 182))):
        R(d, [x, 600 - h, x + w, 600], c)                                       # ステージ棟
        R(d, [x + 80, 600 - h + 120, x + w - 80, 600], _shade(c, 0.85))
    R(d, [480, 300, 1440, 600], (222, 214, 198))
    for x in range(520, 1420, 120):
        R(d, [x, 340, x + 60, 400], (160, 176, 186), ow=2)
    _band(img, 600, H, (206, 194, 170), (192, 180, 156))
    d = _d(img)
    d.line([(0, 600), (W, 600)], fill=INK, width=3)
    rnd = random.Random(9)
    for _ in range(80):                                                         # 玉砂利（奥だけ）
        x, y = rnd.randint(0, W), rnd.randint(610, 700)
        d.ellipse([x, y, x + 6, y + 4], fill=(180, 168, 146))
    # 布をかぶせた大きな何か
    cloth = (238, 234, 222)
    blob(img, [("p", [(760, 700), (744, 520), (770, 380), (820, 280), (900, 200)]),
               ("e", [800, 150, 1010, 360]), ("e", [930, 210, 1120, 420]), ("e", [760, 300, 940, 520]),
               ("p", [(760, 700), (744, 520), (790, 330), (1100, 330), (1170, 520), (1170, 700)]),
               ("e", [730, 640, 1190, 724])], cloth)                            # 中身の分からない大きな塊
    d = _d(img)
    for pts in (((870, 200), (830, 450), (800, 690)), ((940, 160), (950, 450), (960, 710)),
                ((1050, 240), (1090, 460), (1120, 700)), ((900, 380), (880, 560), (870, 710)),
                ((1010, 400), (1030, 560), (1040, 710))):
        d.line(pts, fill=(212, 206, 190), width=6, joint="curve")
    for y in (560, 660):                                                       # 布を縛った縄
        d.line([(752, y), (960, y + 14), (1168, y)], fill=(150, 120, 70), width=6, joint="curve")
    alpha(img, lambda dd: dd.ellipse([720, 690, 1200, 740], fill=(80, 70, 60, 50)), blur=8)
    d = _d(img)
    for x in (730, 1190):                                                       # 青竹
        R(d, [x - 10, 300, x + 10, 740], (120, 170, 100))
        for y in (380, 480, 580):
            d.line([(x - 10, y), (x + 10, y)], fill=(90, 140, 76), width=3)
        blob(img, [("e", [x - 50, 260, x + 50, 330])], (96, 150, 90))
        d = _d(img)
    sag = [(x, 340 + 26 * math.sin(math.pi * (x - 740) / 440)) for x in range(740, 1181, 20)]
    d.line(sag, fill=(150, 120, 70), width=18, joint="curve")                  # しめ縄
    d.line(sag, fill=(210, 182, 120), width=12, joint="curve")
    for k in range(0, len(sag) - 1, 3):
        x, y = sag[k]
        d.line([(x - 6, y - 6), (x + 6, y + 6)], fill=(170, 140, 84), width=3)
    for x in (820, 900, 1020, 1100):                                            # 紙垂
        y = 340 + 26 * math.sin(math.pi * (x - 740) / 440) + 8
        P(d, [(x - 8, y), (x + 8, y), (x + 8, y + 18), (x - 4, y + 18), (x - 4, y + 36), (x + 12, y + 36), (x + 12, y + 56),
              (x - 2, y + 56), (x - 2, y + 66), (x - 8, y + 66)], (252, 252, 250), ow=2)
    R(d, [800, 620, 1120, 650], (226, 206, 168))                                # 白木の台
    R(d, [820, 650, 840, 720], (206, 186, 150))
    R(d, [1080, 650, 1100, 720], (206, 186, 150))
    for x in (850, 1070):                                                       # 瓶子と榊
        R(d, [x - 18, 560, x + 18, 620], (250, 250, 246), r=12)
        R(d, [x - 6, 548, x + 6, 562], (250, 250, 246), ow=2)
        thick(d, [(x, 550), (x - 6, 480)], (100, 80, 60), 4, ow=2)
        for lx, ly in ((-20, 500), (12, 488), (-10, 470), (14, 520), (-26, 528)):
            E(d, [x + lx - 14, ly - 8, x + lx + 14, ly + 8], (70, 130, 80), ow=2)
    E(d, [906, 600, 1014, 628], (250, 248, 240))                                # 鏡餅
    E(d, [918, 580, 1002, 608], (250, 248, 240))
    E(d, [946, 562, 974, 586], (246, 170, 70), ow=2)
    for x in (880, 1040):                                                       # 盛り塩
        P(d, [(x - 16, 618), (x + 16, 618), (x, 596)], (252, 252, 252), ow=2)
    return img


def eigakan(retsu=False):
    """1954年の映画館の正面（看板は無地）。retsu=True は前から坂の上まで続く長い行列。"""
    img = vgrad((W, H), (178, 206, 228), (216, 226, 232))
    _cloud(img, 1560, 90, 0.6)
    d = _d(img)
    base, top_x = 700, 1180

    def slope_y(x):
        return base - (x - top_x) * (240 / (W - top_x))

    P(d, [(top_x, base), (W + 10, slope_y(W + 10)), (W + 10, H + 10), (-10, H + 10), (-10, base)], (184, 178, 168), ow=0)
    for k, x in enumerate(range(top_x, W, 150)):                               # 坂の町並み
        by = slope_y(x + 150) + 10
        h = 300 - k * 20
        c = ((206, 196, 178), (190, 184, 172), (214, 202, 186))[k % 3]
        R(d, [x, by - h, x + 150, by + 40], c)
        for wy in range(int(by - h + 24), int(by - 40), 56):
            for wx in (x + 24, x + 84):
                d.rectangle([wx, wy, wx + 36, wy + 28], fill=(160, 176, 190))
        P(d, [(x - 4, by - 40), (x + 154, by - 40), (x + 144, by - 10), (x + 6, by - 10)],
          ((200, 110, 96), (110, 140, 170), (190, 170, 96))[k % 3], ow=2)
    d.line([(top_x, base + 12), (W, slope_y(W) + 12)], fill=INK, width=3)       # 歩道のふち
    # 映画館
    R(d, [100, 60, top_x, base], (228, 216, 192))
    P(d, [(100, 60), (260, 60), (260, 30), (1020, 30), (1020, 60), (top_x, 60), (top_x, 80), (100, 80)], (210, 196, 170))
    oy = 44                                                                     # 章タイトルの帯をよける
    _band(img, 112 + oy, 302 + oy, (52, 72, 110), (230, 150, 96), 280, 1120)    # 看板（無地の絵: 海と町の影）
    d = _d(img)
    d.polygon([(x, y + oy) for x, y in
               [(280, 302), (280, 250), (340, 250), (340, 220), (420, 220), (420, 260), (520, 260), (520, 200), (600, 200),
                (600, 240), (720, 240), (720, 210), (800, 210), (800, 260), (900, 260), (900, 230), (1000, 230), (1000, 250),
                (1120, 250), (1120, 302)]], fill=(54, 50, 66))
    for y in (286, 296):
        d.line([(280, y + oy), (1120, y + oy)], fill=(80, 110, 150), width=3)
    R(d, [270, 102 + oy, 1130, 312 + oy], None, ow=10, ink=(150, 120, 80))
    R(d, [260, 326 + oy, 1140, 372 + oy], (240, 232, 214))                      # 電球の帯（文字なし）
    for x in range(276, 1130, 28):
        d.ellipse([x, 332 + oy, x + 10, 342 + oy], fill=(250, 210, 110))
        d.ellipse([x, 356 + oy, x + 10, 366 + oy], fill=(250, 210, 110))
    R(d, [200, 428, 1170, 456], (160, 70, 64))                                  # ひさし
    R(d, [790, 490, 890, base], (196, 170, 130))                                # 切符売り場
    R(d, [806, 530, 874, 600], (60, 70, 84), r=30)
    for x0 in (910, 1030):                                                      # ガラス戸
        R(d, [x0, 480, x0 + 110, base], (70, 82, 96))
        d.line([(x0 + 55, 480), (x0 + 55, base)], fill=(150, 150, 140), width=4)
    for x in (140, 640):                                                        # 無地のポスター枠
        R(d, [x, 480, x + 110, 650], (210, 190, 150))
        d.rectangle([x + 12, 492, x + 98, 638], fill=(120, 140, 170) if x == 140 else (200, 120, 100))
    d.line([(0, base), (top_x, base)], fill=INK, width=3)
    if not retsu:
        _person(d, 840, 718, 0.8, coat=(90, 84, 76))
        _person(d, 1110, 722, 0.8, coat=(70, 80, 100))
        _person(d, 1720, slope_y(1720) + 14, 0.5, coat=(100, 84, 70))
        return img
    rnd = random.Random(3)
    coats = [(70, 74, 92), (96, 84, 72), (60, 64, 70), (110, 96, 84), (84, 92, 110), (120, 104, 92)]
    far = []
    x = W + 40
    while x > top_x:                                                            # 坂の上から続く列
        t = (x - top_x) / (W - top_x)
        far.append((x, slope_y(x) + 16, 0.78 - 0.4 * t))
        x -= 30 - 12 * t
    for x, y, s in far:
        _person(d, x, y, s, coat=rnd.choice(coats), hat=rnd.choice([(54, 50, 56), (90, 80, 70), None]))
    for row, y in enumerate((706, 728)):                                        # 入口の前の折り返し
        for k in range(10):
            x = 740 + k * 44 + row * 20
            _person(d, x, y, 0.82 + row * 0.04, coat=rnd.choice(coats), hat=rnd.choice([(54, 50, 56), (90, 80, 70), None]))
    return img


def eigakan_retsu():
    return eigakan(retsu=True)


def juyakushitsu():
    """1954年の映画会社の重役室。重厚な机とソファ、壁に風景画、テーブルにビール瓶とグラスと洋酒の瓶。"""
    img = vgrad((W, H), (216, 202, 176), (200, 186, 160))
    d = _d(img)
    for x in range(0, W, 26):                                                   # 壁紙の縦じま
        d.line([(x, 0), (x, 560)], fill=(208, 194, 168), width=6)
    R(d, [-10, 0, W + 10, 40], (110, 72, 50))                                   # 天井の廻り縁
    d.rectangle([0, 560, W, FLOOR], fill=(110, 72, 50))                         # 腰の板張り
    d.line([(0, 560), (W, 560)], fill=INK, width=3)
    for x in range(40, W, 180):
        R(d, [x, 590, x + 140, 850], None, ow=3, ink=(92, 60, 42))
    _band(img, FLOOR, H, (138, 58, 56), (120, 50, 48))                          # 赤い絨毯
    d = _d(img)
    d.line([(0, FLOOR), (W, FLOOR)], fill=INK, width=3)
    d.line([(0, FLOOR + 30), (W, FLOOR + 30)], fill=(196, 160, 90), width=4)
    # 金の額の風景画（中央の上）
    R(d, [720, 110, 1200, 380], (196, 160, 90))
    R(d, [744, 134, 1176, 356], (178, 140, 76), ow=2)
    _band(img, 150, 340, (176, 206, 226), (230, 226, 206), 760, 1160)
    d = _d(img)
    d.polygon([(760, 300), (860, 200), (930, 250), (1020, 170), (1160, 290), (1160, 340), (760, 340)], fill=(120, 150, 130))
    d.polygon([(1000, 190), (1020, 170), (1042, 192)], fill=(248, 248, 244))
    d.rectangle([760, 300, 1160, 340], fill=(110, 156, 190))
    d.line([(800, 318), (880, 318)], fill=(170, 206, 226), width=3)
    d.line([(980, 326), (1080, 326)], fill=(170, 206, 226), width=3)
    R(d, [744, 134, 1176, 356], None, ow=2)
    for x in (640, 1280):                                                       # 壁の燭台
        R(d, [x - 10, 220, x + 10, 280], (196, 160, 90))
        E(d, [x - 24, 176, x + 24, 226], (255, 236, 190))
        _glow(img, x, 200, 120, (255, 220, 150), 50)
        d = _d(img)
    # 窓と厚いカーテン（右端）
    _band(img, 140, 500, (170, 200, 226), (210, 222, 230), 1640, 1860)
    d = _d(img)
    _window(d, 1640, 140, 1860, 500, sky=None, frame=(236, 230, 214))
    R(d, [1590, 100, 1920, 118], (150, 110, 70), r=6)
    for x0, x1 in ((1590, 1660), (1840, 1920)):
        R(d, [x0, 118, x1, 560], (110, 50, 56))
        for x in range(x0 + 16, x1, 20):
            d.line([(x, 122), (x, 556)], fill=(90, 40, 46), width=3)
    # 重厚な机（左端）と電気スタンド
    R(d, [-10, 600, 330, 640], (96, 60, 40))
    d.rectangle([0, 640, 320, FLOOR + 20], fill=(84, 52, 34))
    d.line([(320, 640), (320, FLOOR + 20)], fill=INK, width=3)
    for y in (680, 760):
        R(d, [180, y, 300, y + 60], (96, 60, 40), ow=2)
    R(d, [80, 590, 160, 604], (60, 60, 66), ow=2)
    d.line([(120, 590), (120, 520)], fill=(196, 160, 90), width=6)
    P(d, [(70, 520), (170, 520), (150, 480), (90, 480)], (60, 110, 84))
    _glow(img, 120, 540, 120, (255, 226, 160), 40)
    d = _d(img)
    R(d, [200, 576, 290, 600], (246, 244, 236), ow=2)                           # 書類
    # 革のソファ（奥・中央）
    leather = (122, 70, 54)
    R(d, [560, 470, 1360, 620], _shade(leather, 0.9), r=40)
    for x in range(640, 1340, 100):
        d.ellipse([x - 4, 500, x + 4, 508], fill=(80, 46, 36))
        d.ellipse([x + 46, 540, x + 54, 548], fill=(80, 46, 36))
    R(d, [520, 520, 620, 760], leather, r=34)
    R(d, [1300, 520, 1400, 760], leather, r=34)
    R(d, [600, 600, 1320, 720], _shade(leather, 1.08), r=24)
    for x in (840, 1080):
        d.line([(x, 604), (x, 716)], fill=_shade(leather, 0.85), width=4)
    # 低いテーブルとビール瓶・グラス・洋酒の瓶
    E(d, [720, 640, 1200, 700], (92, 58, 40))
    E(d, [720, 630, 1200, 690], (120, 80, 54))
    R(d, [760, 680, 790, 760], (92, 58, 40))
    R(d, [1130, 680, 1160, 760], (92, 58, 40))
    for x in (800, 850):                                                        # ビール瓶（ラベルは無地）
        R(d, [x, 560, x + 36, 660], (120, 76, 40), r=10)
        R(d, [x + 10, 520, x + 26, 566], (120, 76, 40), ow=2)
        R(d, [x + 9, 512, x + 27, 522], (196, 170, 90), ow=2)
        d.rectangle([x + 4, 596, x + 32, 626], fill=(236, 226, 196))
    for x in (912, 966, 1020):                                                  # ビールのグラス
        R(d, [x, 604, x + 34, 660], (236, 190, 90), ow=2)
        R(d, [x, 596, x + 34, 614], (252, 250, 240), ow=2)
    R(d, [1072, 560, 1132, 660], (176, 110, 50), r=8)                           # 洋酒の瓶
    R(d, [1090, 524, 1114, 562], (176, 110, 50), ow=2)
    R(d, [1088, 512, 1116, 526], (60, 50, 44), ow=2)
    d.rectangle([1080, 590, 1124, 630], fill=(240, 232, 210))
    alpha(img, lambda dd: [dd.line([(x + 6, 560 if x < 900 else 610), (x + 6, 650)], fill=(255, 255, 255, 90), width=4)
                           for x in (800, 850, 912, 966, 1020, 1078)])
    return img


def tsuburayapro():
    """1963年の小さな会社の事務所。机、黒電話、届いたばかりの大きな木箱。"""
    img = vgrad((W, H), (228, 224, 212), (214, 210, 198))
    d = _d(img)
    d.rectangle([0, 680, W, FLOOR], fill=(196, 192, 182))
    d.line([(0, 680), (W, 680)], fill=INK, width=3)
    wood_floor(img, FLOOR, col=(170, 162, 148), line=(156, 148, 136))
    d = _d(img)
    for x in (640, 1280):                                                       # 蛍光灯
        R(d, [x - 140, 30, x + 140, 50], (250, 250, 246))
        d.line([(x - 100, 0), (x - 100, 30)], fill=INK, width=2)
        d.line([(x + 100, 0), (x + 100, 30)], fill=INK, width=2)
    _band(img, 160, 470, (186, 210, 230), (214, 224, 230), 60, 300)             # 窓（左端）
    d = _d(img)
    for x, w, h in ((70, 70, 120), (150, 80, 160), (240, 50, 90)):
        d.rectangle([x, 470 - h, x + w, 470], fill=(176, 180, 186))
    _window(d, 60, 160, 300, 470, sky=None, frame=(236, 236, 230))
    R(d, [1640, 150, 1800, 330], (250, 250, 246))                               # 暦（数字なし）
    d.rectangle([1640, 150, 1800, 190], fill=(200, 80, 70))
    for r in range(4):
        for c in range(5):
            d.rectangle([1654 + c * 29, 202 + r * 30, 1672 + c * 29, 220 + r * 30], fill=(214, 214, 210))
    # 大きな木箱（中央）
    cw = (206, 170, 120)
    R(d, [740, 360, 1180, 860], cw)
    for y in range(400, 860, 52):
        d.line([(744, y), (1176, y)], fill=(184, 148, 100), width=3)
    for x0 in (740, 1140):
        R(d, [x0, 360, x0 + 40, 860], (186, 150, 102))
    R(d, [740, 360, 1180, 396], (186, 150, 102))
    R(d, [740, 824, 1180, 860], (186, 150, 102))
    thick(d, [(780, 396), (1140, 824)], (186, 150, 102), 26)
    for ax in (840, 900):                                                       # 天地無用の矢印
        P(d, [(ax, 470), (ax + 26, 510), (ax + 10, 510), (ax + 10, 560), (ax - 10, 560), (ax - 10, 510), (ax - 26, 510)],
          (60, 60, 66), ow=0)
    d.polygon([(1030, 470), (1090, 470), (1074, 510), (1066, 514), (1066, 548), (1084, 556), (1036, 556), (1054, 548),
               (1054, 514), (1046, 510)], fill=(60, 60, 66))                    # こわれもの（グラス）
    R(d, [960, 640, 1100, 720], (250, 248, 238), ow=2)                          # 無地の送り状
    for y in (660, 680, 700):
        d.line([(976, y), (1084, y)], fill=(190, 190, 186), width=3)
    thick(d, [(1190, 860), (1240, 560)], (150, 60, 50), 8)                      # バール
    # 机と黒電話（右端）
    R(d, [1540, 600, 1940, 630], (150, 118, 86))
    d.rectangle([1560, 630, 1940, FLOOR], fill=(136, 106, 76))
    d.line([(1560, 630), (1560, FLOOR)], fill=INK, width=3)
    _phone(d, 1700, 524, 0.7)
    R(d, [1590, 570, 1680, 600], (246, 244, 236), ow=2)
    return img


def tv_set():
    """1966年のテレビの特撮セット。ミニチュアの町、青空のホリゾント幕、照明。"""
    img = vgrad((W, H), (48, 48, 58), (60, 60, 70))
    d = _d(img)
    _band(img, 40, 720, (110, 170, 228), (206, 228, 244), 100, 1820)            # ホリゾント幕
    for cx, cy, s in ((1300, 160, 0.9), (1620, 280, 0.6), (760, 260, 0.7), (1040, 360, 0.5)):
        _cloud(img, cx, cy, s, ink=(170, 190, 214))
    d = _d(img)
    R(d, [100, 40, 1820, 720], None, ow=4)
    R(d, [-10, 0, W + 10, 30], (80, 80, 90))                                    # 照明のバトン
    for lx in range(240, 1800, 220):
        d.line([(lx, 30), (lx, 50)], fill=INK, width=4)
        R(d, [lx - 32, 48, lx + 32, 96], (70, 70, 80), r=8)
        E(d, [lx - 24, 86, lx + 24, 106], (255, 244, 210))
    blob(img, [("p", [(100, 600), (300, 470), (520, 540), (760, 430), (1000, 520), (1240, 450), (1500, 530), (1820, 470),
                      (1820, 620), (100, 620)])], (150, 190, 160), ink=(110, 140, 120))   # 描いた山
    d = _d(img)
    rnd = random.Random(66)
    cols = [(240, 236, 224), (226, 214, 196), (214, 222, 230), (236, 220, 200), (206, 214, 206)]
    x = 110
    while x < 1800:                                                             # ミニチュアの町
        w = rnd.randint(60, 110)
        h = rnd.randint(70, 170)
        c = rnd.choice(cols)
        _bldg(d, x, 690 - h, x + w, 700, c, win=(130, 160, 196), ww=12, wh=14, gx=22, gy=26, ow=2)
        if rnd.random() < 0.35:
            P(d, [(x - 6, 690 - h), (x + w + 6, 690 - h), (x + w / 2, 690 - h - 30)], (200, 110, 96), ow=2)
        x += w + rnd.randint(4, 30)
    for tx in (300, 840, 1100, 1560):
        E(d, [tx - 26, 640, tx + 26, 690], (110, 160, 100), ow=2)
    R(d, [100, 700, 1820, 740], (130, 100, 74))                                 # 台のふち
    d.rectangle([0, 740, W, H], fill=(56, 56, 64))
    for x, fx in ((50, 1), (1870, -1)):                                         # スタンドの照明（左右の端）
        d.line([(x, 380), (x, 900)], fill=(24, 24, 28), width=8)
        R(d, [x - 40, 300, x + 40, 380], (80, 80, 90), r=10)
        E(d, [x + fx * 30 - 14, 310, x + fx * 30 + 14, 370], (255, 244, 210))
    return img


def bessou(akari=False):
    """冬の夜の伊豆の別荘の外観。akari=False は灯りが消えて暗い。True は窓という窓に灯り（構図は同じ）。"""
    img = vgrad((W, H), (20, 26, 52), (46, 54, 86))
    d = _d(img)
    rnd = random.Random(12)
    for _ in range(120):
        x, y = rnd.randint(0, W), rnd.randint(0, 420)
        if x < 620 and y < 130:
            continue
        r = rnd.choice((2, 2, 3, 4))
        d.ellipse([x, y, x + r, y + r], fill=(220, 226, 246))
    E(d, [1480, 80, 1550, 150], (244, 238, 206), ow=0)                          # 三日月
    d.ellipse([1500, 70, 1570, 140], fill=(22, 29, 56))
    d.rectangle([0, 440, W, 560], fill=(30, 42, 72))                            # 冬の海
    for k in range(6):
        d.line([(1470 + k * 6, 460 + k * 16), (1530 - k * 4, 460 + k * 16)], fill=(150, 156, 170), width=3)
    _band(img, 560, H, (38, 56, 52), (28, 42, 40))                              # 庭の芝
    d = _d(img)
    wall = (92, 94, 112) if not akari else (128, 118, 112)
    dark = (34, 40, 62)
    light = (255, 222, 140)
    P(d, [(600, 236), (1320, 236), (1236, 150), (684, 150)], (52, 50, 62))      # 屋根
    R(d, [640, 236, 1280, 420], wall)
    P(d, [(590, 446), (1330, 446), (1292, 410), (628, 410)], (52, 50, 62))
    R(d, [620, 446, 1300, 680], wall)
    R(d, [608, 676, 1312, 702], (90, 88, 96))
    wins2 = [(690, 280, 780, 380), (850, 280, 940, 380), (980, 280, 1070, 380), (1140, 280, 1230, 380)]
    wins1 = [(660, 490, 860, 650), (900, 490, 1020, 676), (1060, 490, 1260, 650)]
    for b in wins2 + wins1:
        R(d, b, light if akari else dark)
    if akari:
        alpha(img, lambda dd: [dd.polygon([(b[0], b[3]), (b[2], b[3]), (b[2] + 120, H), (b[0] - 120, H)], fill=(255, 220, 140, 40))
                               for b in wins1], blur=14)
        for b in wins2 + wins1:
            _glow(img, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2, max(b[2] - b[0], b[3] - b[1]) * 1.3, (255, 210, 120), 70)
        d = _d(img)
        for b in wins2 + wins1:
            R(d, b, light)
    for b in wins2 + wins1:                                                     # 桟
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        d.line([(cx, b[1]), (cx, b[3])], fill=(60, 56, 64), width=5)
        if b[3] - b[1] < 150:
            d.line([(b[0], cy), (b[2], cy)], fill=(60, 56, 64), width=5)
    R(d, [960 - 14, 236, 960 + 14, 250], (60, 56, 64), ow=0)
    blob(img, [("e", [x - 90, 630, x + 90, 720]) for x in list(range(0, 640, 140)) + list(range(1300, W + 100, 140))],
         (30, 52, 44))                                                          # 生け垣
    d = _d(img)
    for k in range(5):                                                          # 飛び石
        t = k / 5
        y = 720 + 340 * t ** 1.3
        w = 50 + 80 * t
        E(d, [960 - w, y, 960 + w, y + 20 + 30 * t], (70, 78, 86) if not akari else (110, 104, 96), ow=2)
    for pts, w in ((((150, 720), (160, 400), (190, 220)), 26), (((160, 460), (90, 300)), 10), (((170, 380), (260, 250)), 10),
                   (((185, 260), (150, 160)), 6), (((240, 280), (300, 230)), 6)):
        thick(d, list(pts), (60, 54, 56), w)                                    # 葉の落ちた木（左端）
    d.line([(1760, 720), (1760, 420)], fill=(70, 56, 50), width=22)             # 松（右端）
    for cy, w in ((400, 150), (480, 190), (560, 220)):
        blob(img, [("e", [1760 - w, cy - 40, 1760 + w, cy + 40])], (36, 62, 52))
    d = _d(img)
    R(d, [1560, 640, 1600, 720], (96, 96, 104))                                 # 石灯籠
    R(d, [1544, 590, 1616, 640], (110, 110, 118))
    R(d, [1562, 604, 1598, 628], light if akari else (50, 54, 66), ow=0)
    P(d, [(1534, 594), (1626, 594), (1580, 560)], (96, 96, 104))
    if akari:
        _glow(img, 1580, 616, 80, (255, 210, 120), 60)
    return img


def bessou_yoru():
    return bessou(False)


def bessou_akari():
    return bessou(True)


def gendai():
    """現代のミュージアムの展示室。ミニチュアの町のジオラマとガラスケース。"""
    img = vgrad((W, H), (238, 238, 234), (224, 224, 220))
    d = _d(img)
    d.rectangle([0, 860, W, H], fill=(206, 204, 200))                           # 床
    d.line([(0, 860), (W, 860)], fill=INK, width=3)
    for x in range(-200, W, 260):
        d.line([(x + 200, 860), (x, H)], fill=(196, 194, 190), width=2)
    R(d, [-10, 40, W + 10, 54], (60, 60, 66))                                   # 天井のレール照明
    for lx in (720, 960, 1200, 300, 1620):
        d.line([(lx, 54), (lx, 70)], fill=INK, width=4)
        R(d, [lx - 18, 66, lx + 18, 104], (60, 60, 66), r=6)
    alpha(img, lambda dd: [dd.ellipse([lx - 150, 110, lx + 150, 360], fill=(255, 250, 230, 60)) for lx in (720, 960, 1200)], blur=30)
    d = _d(img)
    for x0, c in ((660, (180, 150, 120)), (1000, (130, 150, 170))):             # 壁のパネル（絵は抽象）
        R(d, [x0, 140, x0 + 260, 310], (250, 250, 248))
        d.rectangle([x0 + 16, 156, x0 + 244, 260], fill=c)
        for y in (274, 290):
            d.line([(x0 + 16, y), (x0 + 200, y)], fill=(200, 200, 198), width=4)
    # ジオラマのガラスケース（中央）
    R(d, [660, 600, 1260, 860], (250, 250, 248))
    d.rectangle([680, 560, 1240, 600], fill=(170, 160, 146))
    rnd = random.Random(70)
    x = 690
    while x < 1220:
        w = rnd.randint(30, 60)
        h = rnd.randint(30, 110)
        _bldg(d, x, 600 - h, x + w, 600, rnd.choice([(226, 222, 212), (206, 206, 200), (214, 200, 180)]),
              win=(150, 160, 176), ww=8, wh=10, gx=16, gy=20, ow=2)
        x += w + rnd.randint(4, 18)
    for tx in (760, 1010, 1170):
        E(d, [tx - 14, 566, tx + 14, 594], (120, 166, 110), ow=2)
    alpha(img, lambda dd: (dd.rectangle([672, 380, 1248, 600], fill=(200, 226, 240, 70)),
                           dd.polygon([(700, 600), (760, 600), (900, 380), (840, 380)], fill=(255, 255, 255, 110)),
                           dd.polygon([(1040, 600), (1070, 600), (1210, 380), (1180, 380)], fill=(255, 255, 255, 90))))
    d = _d(img)
    R(d, [672, 380, 1248, 600], None, ow=3, ink=(140, 160, 176))
    for x0, kind in ((60, "plane"), (1630, "camera")):                         # 両端のガラスケース
        R(d, [x0, 640, x0 + 230, 860], (250, 250, 248))
        alpha(img, lambda dd, x0=x0: dd.rectangle([x0 + 10, 360, x0 + 220, 640], fill=(200, 226, 240, 70)))
        d = _d(img)
        R(d, [x0 + 10, 360, x0 + 220, 640], None, ow=3, ink=(140, 160, 176))
        if kind == "plane":
            _biplane_side(d, x0 + 50, 520, 0.7)
        else:
            R(d, [x0 + 60, 470, x0 + 170, 560], (60, 62, 68), r=6)
            E(d, [x0 + 60, 410, x0 + 116, 466], (90, 92, 100))
            E(d, [x0 + 114, 410, x0 + 170, 466], (90, 92, 100))
            R(d, [x0 + 30, 494, x0 + 60, 530], (40, 40, 44))
        d.rectangle([x0 + 14, 620, x0 + 216, 636], fill=(190, 186, 176))
    return img


def ronsou():
    """ゴジラは何から生まれた: はてなの付いた3枚の札と、フィルムのリールと台本。"""
    img = vgrad((W, H), (240, 236, 226), (220, 218, 210))
    d = _d(img)
    for k in range(3):
        cx = 770 + k * 190
        R(d, [cx - 80, 170, cx + 80, 390], (250, 248, 240), r=16, ow=4)
        _text_c(d, cx, 230, "？", 110, (200, 70, 60))
    cx, cy, r = 860, 590, 100                                                   # フィルムのリール
    E(d, [cx - r, cy - r, cx + r, cy + r], (170, 174, 182), ow=4)
    E(d, [cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18], (90, 92, 100), ow=2)
    for k in range(6):
        a = k * math.pi / 3
        E(d, [cx + math.cos(a) * 48 - 20, cy + math.sin(a) * 48 - 20, cx + math.cos(a) * 48 + 20, cy + math.sin(a) * 48 + 20],
          (220, 218, 210), ow=2)
    E(d, [cx - 14, cy - 14, cx + 14, cy + 14], (220, 218, 210), ow=2)
    thick(d, [(cx + r - 10, cy + 40), (1000, 680), (1080, 690)], (60, 54, 50), 18)
    for k in range(3):                                                          # 台本の束
        x, y = 1000 + k * 8, 520 - k * 10
        R(d, [x, y, x + 150, y + 170], (246, 242, 230), ow=3)
    R(d, [1016, 500, 1166, 670], (226, 214, 186), ow=3)
    for y in (540, 560, 580):
        d.line([(1036, y), (1146, y)], fill=(190, 178, 150), width=4)
    for y in (510, 660):
        d.ellipse([1024, y - 4, 1034, y + 6], fill=INK)
    return img


LOCATIONS = {
    "gz_stage": stage, "gz_heya": heya, "gz_heya2": heya2, "gz_kura": kura, "gz_ie": ie,
    "gz_haneda": haneda, "gz_haneda_kara": haneda_kara, "gz_hanami": hanami, "gz_satsueijo": satsueijo,
    "gz_kyoto_set": kyoto_set, "gz_byoshitsu": byoshitsu, "gz_ie_kyoto": ie_kyoto,
    "gz_shishitsu": shishitsu, "gz_shishitsu54": shishitsu54, "gz_toho_rouka": toho_rouka, "gz_tokugi": tokugi,
    "gz_shinjuwan": shinjuwan, "gz_shinjuwan_full": shinjuwan_full, "gz_ryuchijo": ryuchijo, "gz_bokugou": bokugou,
    "gz_barricade": barricade, "gz_soshigaya": soshigaya, "gz_prefab": prefab, "gz_koryoriya": koryoriya,
    "gz_kaigishitsu": kaigishitsu, "gz_happyou": happyou, "gz_ueno": ueno, "gz_ijika": ijika,
    "gz_ginza_okujo": ginza_okujo, "gz_minia": minia, "gz_minia_kowareta": minia_kowareta, "gz_pool": pool,
    "gz_nakaniwa": nakaniwa, "gz_eigakan": eigakan, "gz_eigakan_retsu": eigakan_retsu,
    "gz_juyakushitsu": juyakushitsu, "gz_tsuburayapro": tsuburayapro, "gz_tv_set": tv_set, "gz_bessou_yoru": bessou_yoru,
    "gz_bessou_akari": bessou_akari, "gz_gendai": gendai, "gz_ronsou": ronsou,
}

CARDS = ["1901", "1916", "1919", "1930", "1937", "1942", "1947", "1954", "1963", "1969"]


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
        if only and f"gz_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"gz_card_{y}.png")
        print(f"生成完了: gz_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
