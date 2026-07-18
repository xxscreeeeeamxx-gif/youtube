#!/usr/bin/env python3
"""qr-drama（QRコード再現ドラマ）用の年号カード6枚+図解アニメ10本を生成する。

クリップ名は qd_/era_d 名義（旧qr-code解説動画の qr_*・gen_qr_extras.py とは別物）。
フェーズ境界は timing.json 実測（spans_from_timing）。
実行: PYTHONPATH=. python3 scripts/gen_qr_drama_extras.py（voice 後）
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.gen_momofuku_extras as m  # noqa: E402
from scripts.gen_momofuku_extras import (  # noqa: E402
    W, H, AMBER, GRAY, GREEN, RED,
    ctext, ease, font, render, _caption,
)
import scripts.gen_momofuku_v2_extras as v2  # noqa: E402

BLUE = (90, 160, 240)
PAPER = (245, 247, 250)
DARKBG = (10, 14, 24)

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1957", "誕生"), ("1980", "入社"), ("1992", "一本の電話"),
          ("1994", "QRコード"), ("2000", "世界標準"), ("2002", "ケータイ")]

CARDS = [
    ("era_d1957", 0, "1957", "エンジニアの家に", "東京・杉並"),
    ("era_d1980", 1, "1980", "音声認識がやりたくて", "日本電装に入社"),
    ("era_d1992", 2, "1992", "一本の電話", "西尾工場から"),
    ("era_d1994", 3, "1994", "QRコード誕生", "たった2人の発明"),
    ("era_d2000", 4, "2000", "世界標準になる", "国際規格に登録"),
    ("era_d2002", 5, "2002", "ポケットの中へ", "カメラ付き携帯"),
]


# ---------------------------------------------------------------- 共通部品
def _qr(d, cx, cy, size, seed=7, cells=21, damage=None):
    """擬似QRコード（決定的パターン+3隅のファインダ）。"""
    cell = size / cells
    x0, y0 = cx - size / 2, cy - size / 2
    d.rounded_rectangle([x0 - 14, y0 - 14, x0 + size + 14, y0 + size + 14],
                        radius=10, fill=PAPER)
    for i in range(cells):
        for j in range(cells):
            fp = (i < 7 and j < 7) or (i >= cells - 7 and j < 7) or \
                (i < 7 and j >= cells - 7)
            if fp:
                continue
            if (i * 7 + j * 13 + i * j + seed) % 5 < 2:
                d.rectangle([x0 + i * cell, y0 + j * cell,
                             x0 + (i + 1) * cell, y0 + (j + 1) * cell],
                            fill=(24, 28, 36))
    for (fi, fj) in ((0, 0), (cells - 7, 0), (0, cells - 7)):
        fx, fy = x0 + fi * cell, y0 + fj * cell
        d.rectangle([fx, fy, fx + 7 * cell, fy + 7 * cell], fill=(24, 28, 36))
        d.rectangle([fx + cell, fy + cell, fx + 6 * cell, fy + 6 * cell], fill=PAPER)
        d.rectangle([fx + 2 * cell, fy + 2 * cell, fx + 5 * cell, fy + 5 * cell],
                    fill=(24, 28, 36))
    if damage:
        for (dx0, dy0, dx1, dy1) in damage:
            d.ellipse([x0 + size * dx0, y0 + size * dy0,
                       x0 + size * dx1, y0 + size * dy1], fill=(96, 74, 40))


def _bars(d, x0, y0, w, h, seed=3):
    """バーコードの縞。"""
    d.rounded_rectangle([x0 - 16, y0 - 16, x0 + w + 16, y0 + h + 16],
                        radius=8, fill=PAPER)
    x = x0
    i = 0
    while x < x0 + w:
        bw = 6 + ((i * 7 + seed) % 4) * 5
        if i % 2 == 0:
            d.rectangle([x, y0, min(x + bw, x0 + w), y0 + h], fill=(24, 28, 36))
        x += bw
        i += 1


def _phone_g(d, cx, cy, s=1.0):
    """ガラケー（開いた状態）。画面中心はおよそ (cx, cy-100s)。"""
    d.rounded_rectangle([cx - 90 * s, cy - 190 * s, cx + 90 * s, cy + 10 * s],
                        radius=18, fill=(70, 84, 120))
    d.rectangle([cx - 70 * s, cy - 165 * s, cx + 70 * s, cy - 35 * s],
                fill=(190, 220, 210))
    d.rounded_rectangle([cx - 90 * s, cy + 14 * s, cx + 90 * s, cy + 190 * s],
                        radius=18, fill=(70, 84, 120))
    for r in range(3):
        for k in range(3):
            d.rounded_rectangle([cx - 62 * s + k * 45 * s, cy + 34 * s + r * 42 * s,
                                 cx - 28 * s + k * 45 * s, cy + 62 * s + r * 42 * s],
                                radius=6, fill=(120, 134, 168))
    d.line([cx + 78 * s, cy - 190 * s, cx + 95 * s, cy - 245 * s],
           fill=(70, 84, 120), width=max(6, int(10 * s)))


def _smartphone(d, cx, cy, s=1.0, crack=False):
    d.rounded_rectangle([cx - 110 * s, cy - 200 * s, cx + 110 * s, cy + 200 * s],
                        radius=26, fill=(40, 46, 60))
    d.rounded_rectangle([cx - 96 * s, cy - 180 * s, cx + 96 * s, cy + 180 * s],
                        radius=14, fill=PAPER)
    if crack:
        for pts in (((cx - 90 * s, cy - 170 * s), (cx - 30 * s, cy - 90 * s),
                     (cx - 60 * s, cy + 10 * s)),
                    ((cx + 90 * s, cy - 120 * s), (cx + 30 * s, cy - 40 * s),
                     (cx + 66 * s, cy + 80 * s)),
                    ((cx - 40 * s, cy + 170 * s), (cx + 6 * s, cy + 90 * s))):
            d.line(list(pts), fill=(120, 126, 140), width=4)


def _check(d, cx, cy, r=54, p=1.0):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GREEN, width=10)
    if p > 0.3:
        d.line([cx - r * 0.45, cy, cx - r * 0.1, cy + r * 0.38], fill=GREEN, width=12)
    if p > 0.6:
        d.line([cx - r * 0.1, cy + r * 0.38, cx + r * 0.5, cy - r * 0.35],
               fill=GREEN, width=12)


# ---------------------------------------------------------------- 1. かんばん方式
KB_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_kanban(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "かんばん方式")
    d.rounded_rectangle([740, 620, 1280, 680], radius=10, fill=(50, 58, 72))
    for i in range(3):
        bx = 770 + ((i * 190 + int(t * 40)) % 460)
        d.rounded_rectangle([bx, 520, bx + 120, 620], radius=8, fill=(178, 146, 96))
    d.rounded_rectangle([880, 290, 1140, 430], radius=10, fill=PAPER)
    ctext(d, 1010, 320, "かんばん", font(40), (40, 44, 56))
    d.line([905, 385, 1115, 385], fill=(120, 126, 140), width=5)
    d.line([905, 410, 1060, 410], fill=(160, 166, 180), width=4)
    lines = ["必要なものを", "必要なときに", "必要な数だけ"]
    for k, ln in enumerate(lines):
        st = KB_P[1] + k * 1.4
        if t >= st:
            b = ease((t - st) / 0.6)
            ctext(d, 1010, 730 + k * 78, ln, font(54),
                  tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. バーコードの仕組み
BC_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_barcode(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "バーコードの仕組み")
    _bars(d, 760, 300, 480, 200)
    if t >= BC_P[1]:
        sx = 760 + ((t - BC_P[1]) * 260) % 480
        d.line([sx, 270, sx, 530], fill=RED, width=6)
        d.polygon([(sx - 12, 258), (sx + 12, 258), (sx, 276)], fill=RED)
    if t >= BC_P[2]:
        b = ease((t - BC_P[2]) / 0.6)
        ctext(d, 1000, 580, "4 9 0 1 2 3 4 …", font(60),
              tuple(int(BLUE[i] * b) for i in range(3)))
        ctext(d, 1000, 660, "縞の太さ = 数字や文字", font(44),
              tuple(int(GRAY[i] * b) for i in range(3)))
    if t >= BC_P[3]:
        b = ease((t - BC_P[3]) / 0.6)
        d.rounded_rectangle([760, 770, 1240, 830], radius=12, outline=GRAY, width=4)
        fill_w = int(474 * min(1.0, (t - BC_P[3]) / 1.2))
        d.rounded_rectangle([763, 773, 763 + fill_w, 827], radius=10, fill=AMBER)
        ctext(d, 1000, 870, "容量は 英数字20文字ほどで満杯", font(46),
              tuple(int(RED[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 3. 10連バーコードの箱
BD_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_burden(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "1つの箱に、バーコードの列")
    d.rounded_rectangle([760, 290, 1250, 690], radius=12, fill=(178, 146, 96))
    d.rectangle([760, 290, 1250, 330], fill=(150, 122, 78))
    total = 10
    done = 0
    if t >= BD_P[1]:
        done = min(total, int((t - BD_P[1]) / 0.55) + 1)
    for k in range(total):
        bx = 795 + (k % 5) * 92
        by = 360 + (k // 5) * 160
        _bars(d, bx, by, 60, 88, seed=k)
        if k < done:
            d.line([bx - 6, by + 96, bx + 24, by + 122], fill=GREEN, width=8)
            d.line([bx + 24, by + 122, bx + 68, by + 74], fill=GREEN, width=8)
    if t >= BD_P[1] and done < total:
        ctext(d, 1000, 740, f"読み取り {done} ／ {total}", font(50), AMBER)
    elif t >= BD_P[1]:
        ctext(d, 1000, 740, "やっと1箱ぶん……", font(50), GRAY)
    if t >= BD_P[2]:
        b = ease((t - BD_P[2]) / 0.6)
        ctext(d, 1000, 820, "これが1日、何百箱", font(52),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= BD_P[3]:
        b = ease((t - BD_P[3]) / 0.6)
        ctext(d, 1000, 905, "現場の声「読むだけで疲れる」", font(48),
              tuple(int(RED[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 4. 1次元 vs 2次元
D2_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_2d(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "横1列から、面へ")
    _bars(d, 730, 390, 185, 120)
    ctext(d, 822, 570, "横方向だけ", font(38), GRAY)
    if t >= D2_P[1]:
        ctext(d, 822, 636, "20文字ほど", font(42), AMBER)
        d.line([935, 450, 965, 450], fill=GRAY, width=8)
        d.polygon([(965, 434), (965, 466), (991, 450)], fill=GRAY)
        p = ease(min(1.0, (t - D2_P[1]) / 1.6))
        size, celln = 240, 13
        cx0, cy0 = 1005, 320
        cell = size / celln
        d.rounded_rectangle([cx0 - 12, cy0 - 12, cx0 + size + 12, cy0 + size + 12],
                            radius=8, fill=PAPER)
        shown = int(celln * celln * p)
        for k in range(shown):
            i, j = k % celln, k // celln
            if (i * 5 + j * 11 + i * j) % 5 < 2:
                d.rectangle([cx0 + i * cell, cy0 + j * cell,
                             cx0 + (i + 1) * cell, cy0 + (j + 1) * cell],
                            fill=(24, 28, 36))
        ctext(d, 1125, 636, "縦と横の面", font(38), GRAY)
    if t >= D2_P[2]:
        b = ease((t - D2_P[2]) / 0.8)
        val = int(7000 * min(1.0, (t - D2_P[2]) / 1.8))
        ctext(d, 1125, 706, f"{val}文字", font(52),
              tuple(int(GREEN[i] * b) for i in range(3)))
        ctext(d, 1000, 856, "同じ広さで、数百倍の情報", font(46),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 5. ファインダパターン
FD_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_finder(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    if t < FD_P[1]:
        _caption(d, "機械は、コードを探すのが遅い")
        _qr(d, 1000, 500, 300, seed=5)
        mx = 880 + 140 * math.sin(t * 2.2)
        my = 430 + 80 * math.cos(t * 1.7)
        d.ellipse([mx - 70, my - 70, mx + 70, my + 70], outline=BLUE, width=10)
        d.line([mx + 52, my + 52, mx + 118, my + 118], fill=BLUE, width=12)
        ctext(d, 1000, 800, "どこにある？　向きは？", font(50), GRAY)
        return
    _caption(d, "3隅の目印 = ファインダパターン")
    _qr(d, 1000, 500, 300, seed=5)
    if t < FD_P[2]:
        pulse = 1 + 0.15 * math.sin(t * 5)
        for (fx, fy) in ((898, 398), (1102, 398), (898, 602)):
            r = int(58 * pulse)
            d.ellipse([fx - r, fy - r, fx + r, fy + r], outline=AMBER, width=8)
        ctext(d, 1000, 800, "「ここにいるよ」の目印", font(50), AMBER)
        return
    ang_list = [0, 35, 80, 125]
    idx = min(3, int((t - FD_P[2]) / 2.4))
    ang = math.radians(ang_list[idx])
    cx, cy = 1000, 500
    dx, dy = math.cos(ang), math.sin(ang)
    d.line([cx - 240 * dx, cy - 240 * dy, cx + 240 * dx, cy + 240 * dy],
           fill=RED, width=6)
    seq = [("1", 44), ("1", 44), ("3", 132), ("1", 44), ("1", 44)]
    bx = 760
    for k, (s_, w_) in enumerate(seq):
        col = (24, 28, 36) if k % 2 == 0 else PAPER
        d.rectangle([bx, 790, bx + w_, 850], fill=col, outline=GRAY, width=2)
        ctext(d, bx + w_ / 2, 870, s_, font(44), AMBER)
        bx += w_
    ctext(d, 1160, 820, "白黒の幅の比率", font(38), GRAY)
    if t >= FD_P[4]:
        b = ease((t - FD_P[4]) / 0.6)
        ctext(d, 1000, 945, "どの角度でも 1:1:3:1:1", font(54),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 6. 碁盤→QR
GB_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_goban(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    cells = 9
    size = 360
    cx0, cy0 = 1000 - size / 2, 480 - size / 2
    cell = size / (cells - 1)
    morph = 0.0 if t < GB_P[3] else ease(min(1.0, (t - GB_P[3]) / 1.6))
    if t < GB_P[1]:
        _caption(d, "昼休みの碁盤")
    elif t < GB_P[2]:
        _caption(d, "ずれて置いても、どこの石か分かる")
    elif t < GB_P[3]:
        _caption(d, "欠けた石でも、白か黒か分かる")
    else:
        _caption(d, "碁盤の考え方が、マス目に生きた")
    if morph < 1.0:
        d.rounded_rectangle([cx0 - 40, cy0 - 40, cx0 + size + 40, cy0 + size + 40],
                            radius=12, fill=(196, 154, 90))
        for i in range(cells):
            d.line([cx0 + i * cell, cy0, cx0 + i * cell, cy0 + size],
                   fill=(110, 82, 44), width=3)
            d.line([cx0, cy0 + i * cell, cx0 + size, cy0 + i * cell],
                   fill=(110, 82, 44), width=3)
    stones = [(1, 1, 0), (2, 3, 1), (3, 1, 0), (4, 4, 0), (5, 2, 1),
              (6, 5, 0), (2, 6, 1), (5, 6, 0), (7, 3, 1), (3, 7, 0), (7, 7, 1)]
    if morph < 1.0:
        for k, (i, j, col) in enumerate(stones):
            px, py = cx0 + i * cell, cy0 + j * cell
            r = cell * 0.42 * (1 - morph)
            if t >= GB_P[1] and k == 4:
                px += min(1.0, (t - GB_P[1]) / 0.8) * cell * 0.35
            fill = (30, 30, 34) if col == 0 else (240, 240, 244)
            d.ellipse([px - r, py - r, px + r, py + r], fill=fill)
            if t >= GB_P[2] and k == 6 and morph == 0.0:
                d.pieslice([px - r, py - r, px + r, py + r], -60, 30,
                           fill=(196, 154, 90))
        if GB_P[1] <= t < GB_P[2]:
            px = cx0 + 5 * cell + cell * 0.35
            py = cy0 + 2 * cell
            d.ellipse([px - 60, py - 60, px + 60, py + 60], outline=GREEN, width=6)
        if GB_P[2] <= t < GB_P[3]:
            px, py = cx0 + 2 * cell, cy0 + 6 * cell
            d.ellipse([px - 60, py - 60, px + 60, py + 60], outline=GREEN, width=6)
    else:
        _qr(d, 1000, 480, 300, seed=9)
        ctext(d, 1000, 860, "ずれ・かすれに強いコードへ", font(50), AMBER)


# ---------------------------------------------------------------- 7. 誤り訂正
GS_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_gosei(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    if t < GS_P[1]:
        _caption(d, "工場の敵: 油汚れ・破れ")
        _qr(d, 1000, 480, 300, seed=11)
    elif t < GS_P[2]:
        _caption(d, "汚れると、一部が読めない")
        _qr(d, 1000, 480, 300, seed=11,
            damage=[(0.55, 0.5, 0.95, 0.9), (0.1, 0.65, 0.3, 0.85)])
        ctext(d, 1000, 790, "ここが読めない……", font(48), RED)
    else:
        _caption(d, "誤り訂正: 残りから計算で復元")
        _qr(d, 1000, 480, 300, seed=11,
            damage=[(0.55, 0.5, 0.95, 0.9), (0.1, 0.65, 0.3, 0.85)])
        p = min(1.0, (t - GS_P[2]) / 1.6)
        sy = 330 + 300 * p
        d.line([760, sy, 1240, sy], fill=GREEN, width=6)
        if p >= 1.0:
            _check(d, 1210, 330, p=1.0)
        if t >= GS_P[3]:
            b = ease((t - GS_P[3]) / 0.6)
            ctext(d, 1000, 830, "最大 約30％ 欠けても復元", font(54),
                  tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 8. 完成スペック
SP_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_spec(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "QRコードの実力")
    ctext(d, 830, 300, "容量", font(44), GRAY)
    d.rounded_rectangle([760, 340, 800, 620], radius=8, outline=GRAY, width=3)
    d.rectangle([763, 600, 797, 620], fill=GRAY)
    ctext(d, 780, 660, "20字", font(36), GRAY)
    p = ease(min(1.0, t / 1.8))
    d.rounded_rectangle([860, 340, 900, 620], radius=8, outline=AMBER, width=3)
    d.rectangle([863, 620 - int(277 * p), 897, 620], fill=AMBER)
    if t >= SP_P[1]:
        val = int(7000 * min(1.0, (t - SP_P[1]) / 1.6))
        ctext(d, 890, 660, f"{val}字", font(36), AMBER)
    if t >= SP_P[2]:
        ctext(d, 1090, 300, "読み取り速度", font(44), GRAY)
        q = min(1.0, (t - SP_P[2]) / 1.4)
        d.rounded_rectangle([950, 380, 1240, 430], radius=10, outline=GRAY, width=3)
        d.rounded_rectangle([953, 383, 953 + max(6, int(284 * q * 0.1)), 427],
                            radius=8, fill=GRAY)
        ctext(d, 1090, 460, "ほかの2次元コード", font(32), GRAY)
        d.rounded_rectangle([950, 520, 1240, 570], radius=10, outline=AMBER, width=3)
        d.rounded_rectangle([953, 523, 953 + max(6, int(284 * q)), 567],
                            radius=8, fill=AMBER)
        ctext(d, 1090, 600, "QRコード", font(36), AMBER)
    if t >= SP_P[3]:
        b = ease((t - SP_P[3]) / 0.6)
        ctext(d, 1000, 790, "大容量で、10倍以上速い", font(50),
              tuple(int(GREEN[i] * b) for i in range(3)))
        ctext(d, 1000, 866, "しかも漢字も入る", font(42),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 9. ケータイでピッ
KT_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_keitai(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    if t < KT_P[1]:
        _caption(d, "雑誌の隅の、四角い模様")
        d.rounded_rectangle([760, 310, 1050, 710], radius=8, fill=PAPER)
        for j in range(6):
            d.line([790, 360 + j * 44, 1020, 360 + j * 44],
                   fill=(150, 156, 170), width=6)
        _qr(d, 960, 630, 120, seed=13)
        _phone_g(d, 1180, 540)
        return
    _caption(d, "カメラで写すと……")
    _phone_g(d, 880, 540, s=1.3)
    if t < KT_P[2]:
        _qr(d, 880, 410, 110, seed=13)
        if (t - KT_P[1]) % 1.0 < 0.15:
            d.rectangle([790, 330, 970, 500], fill=(255, 255, 255))
        ctext(d, 1160, 470, "ピッ", font(70), AMBER)
    else:
        d.rectangle([800, 350, 960, 480], fill=PAPER)
        for j in range(4):
            d.line([814, 378 + j * 28, 946, 378 + j * 28], fill=BLUE, width=5)
        d.line([1000, 440, 1080, 440], fill=GRAY, width=8)
        d.polygon([(1080, 424), (1080, 456), (1108, 440)], fill=GRAY)
        d.rounded_rectangle([1130, 320, 1310, 580], radius=10, fill=PAPER)
        for j in range(6):
            d.line([1150, 360 + j * 38, 1290, 360 + j * 38],
                   fill=(150, 156, 170), width=5)
        ctext(d, 1000, 750, "URLを打たずに、サイトへ", font(48), AMBER)
    if t >= KT_P[3]:
        b = ease((t - KT_P[3]) / 0.6)
        ctext(d, 1000, 850, "写すだけで、つながる", font(54),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 10. スマホ決済
PM_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_payment(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    crack = t >= PM_P[2]
    if t < PM_P[1]:
        _caption(d, "いちばん広がったのは、決済")
    elif t < PM_P[2]:
        _caption(d, "画面を見せて、ピッ")
    elif t < PM_P[3]:
        _caption(d, "画面が割れていても……")
    else:
        _caption(d, "工場育ちの、頑丈さ")
    _smartphone(d, 950, 500, s=1.0, crack=crack)
    _qr(d, 950, 460, 150, seed=17)
    ctext(d, 950, 620, "PAY", font(40), (90, 100, 120))
    if t >= PM_P[1]:
        beam = (t - PM_P[1]) % 2.2
        if beam < 1.0:
            sy = 360 + 220 * beam
            d.line([850, sy, 1050, sy], fill=RED, width=5)
        else:
            _check(d, 1180, 400, p=1.0)
            ctext(d, 1180, 500, "支払い完了", font(40), GREEN)
    if t >= PM_P[3]:
        b = ease((t - PM_P[3]) / 0.6)
        ctext(d, 1000, 800, "3割欠けても復元できる設計が", font(46),
              tuple(int(AMBER[i] * b) for i in range(3)))
        ctext(d, 1000, 870, "ひび割れ画面で生きた", font(46),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- メイン
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))

    spans = v2.spans_from_timing("qr-drama")

    def sync(name, bounds, draw):
        if name not in spans:
            print(f"スキップ（台本に無い）: {name}")
            return
        b, dur = spans[name]
        # 実測境界で上書き（フェーズ数が足りない分は末尾を等間隔で補う）
        vals = list(b)
        while len(vals) < 6:
            vals.append(vals[-1] + max(1.5, (dur - vals[-1]) * 0.5))
        bounds[:] = vals
        render(name, dur, draw)

    sync("qd_kanban", KB_P, draw_kanban)
    sync("qd_barcode", BC_P, draw_barcode)
    sync("qd_burden", BD_P, draw_burden)
    sync("qd_2d", D2_P, draw_2d)
    sync("qd_finder", FD_P, draw_finder)
    sync("qd_goban", GB_P, draw_goban)
    sync("qd_gosei", GS_P, draw_gosei)
    sync("qd_spec", SP_P, draw_spec)
    sync("qd_keitai", KT_P, draw_keitai)
    sync("qd_payment", PM_P, draw_payment)
