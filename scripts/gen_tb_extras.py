#!/usr/bin/env python3
"""点字ブロック再現ドラマ（tenji-block）用の年号カード2枚+図解アニメ3本を生成する。

クリップ名は tb_/era_tb 名義。尺は timing.json 実測（spans_from_timing）。
図解は単独シーンに置くので、全要素を4秒以内に出し切る詰めたタイミングにする。
実行: PYTHONPATH=. python3 scripts/gen_tb_extras.py（voice 後）
"""

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
DARKBG = (10, 14, 24)
YELLOW = (240, 200, 60)
YELLOW_DK = (196, 156, 40)

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1963", "目撃"), ("1967", "世界初の敷設"), ("現代", "75カ国")]

CARDS = [
    ("era_tb1963", 0, "1963", "ある交差点で", "白い杖と、車の道"),
    ("era_tb1967", 1, "1967", "世界初の点字ブロック", "3月18日・岡山・230枚"),
]


# ---------------------------------------------------------------- 共通部品
def _block(d, x0, y0, size, dot=True, b=1.0):
    """点字ブロック1枚。dot=True で点状(5x5)、False で線状(4本)。"""
    col = tuple(int(YELLOW[i] * b) for i in range(3))
    dk = tuple(int(YELLOW_DK[i] * b) for i in range(3))
    d.rounded_rectangle([x0, y0, x0 + size, y0 + size], radius=10, fill=col)
    if dot:
        step = size / 5
        r = step * 0.28
        for row in range(5):
            for c in range(5):
                cx = x0 + step / 2 + c * step
                cy = y0 + step / 2 + row * step
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dk)
    else:
        step = size / 4
        for c in range(4):
            cx = x0 + step / 2 + c * step
            d.rounded_rectangle([cx - step * 0.18, y0 + size * 0.08,
                                 cx + step * 0.18, y0 + size * 0.92],
                                radius=8, fill=dk)


# ---------------------------------------------------------------- 1. 2種類の図解
KD_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_kinds(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "点字ブロックは、2種類だけ")
    # 点状（左）
    if t >= 0.3:
        b = ease((t - 0.3) / 0.4)
        _block(d, 760, 300, 240, dot=True, b=b)
        ctext(d, 880, 590, "点状ブロック", font(40),
              tuple(int(AMBER[i] * b) for i in range(3)))
        ctext(d, 880, 650, "警告・この先に注意", font(32),
              tuple(int(GRAY[i] * b) for i in range(3)))
    if t >= 1.1:
        b = ease((t - 1.1) / 0.4)
        ctext(d, 880, 710, "「止まれ」", font(44),
              tuple(int(RED[i] * b) for i in range(3)))
    # 線状（右）
    if t >= 1.9:
        b = ease((t - 1.9) / 0.4)
        _block(d, 1120, 300, 240, dot=False, b=b)
        ctext(d, 1240, 590, "線状ブロック", font(40),
              tuple(int(AMBER[i] * b) for i in range(3)))
        ctext(d, 1240, 650, "誘導・この向きに進む", font(32),
              tuple(int(GRAY[i] * b) for i in range(3)))
    if t >= 2.7:
        b = ease((t - 2.7) / 0.4)
        ctext(d, 1240, 710, "「進め」", font(44),
              tuple(int(GREEN[i] * b) for i in range(3)))
    if t >= 3.5:
        b = ease((t - 3.5) / 0.5)
        ctext(d, 1000, 850, "たった2種類だから、体で覚えられる", font(42),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. 普及グラフ
GR_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_graph(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "点字ブロックの、広がり")
    x0, y1 = 700, 780
    steps = [("1967 岡山", "230枚", 0.06, GRAY),
             ("1972 高田馬場", "1万枚", 0.55, AMBER),
             ("現代 世界", "約75カ国", 1.0, GREEN)]
    for k, (label, val, h, col) in enumerate(steps):
        st = 0.3 + k * 0.9
        if t < st:
            continue
        b = ease(min(1.0, (t - st) / 0.4))
        bx = x0 + k * 210
        bh = 400 * h * b
        d.rounded_rectangle([bx, y1 - bh, bx + 140, y1], radius=10,
                            fill=tuple(int(col[i]) for i in range(3)))
        ctext(d, bx + 70, y1 + 36, label, font(28), GRAY)
        ctext(d, bx + 70, y1 - bh - 40, val, font(36),
              tuple(int(col[i] * b) for i in range(3)))
    if t >= 3.2:
        b = ease((t - 3.2) / 0.5)
        ctext(d, 1000, 230, "岡山の交差点から、世界の足元へ", font(46),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 3. JIS規格
JS_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_jis(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "全国で、同じ形に")
    # 大きな点状ブロック（中央）
    size = 380
    x0, y0 = 810, 280
    _block(d, x0, y0, size, dot=True, b=1.0)
    # 寸法線
    if t >= 0.8:
        b = ease((t - 0.8) / 0.4)
        col = tuple(int(BLUE[i] * b) for i in range(3))
        d.line([x0, y0 + size + 40, x0 + size, y0 + size + 40], fill=col, width=4)
        ctext(d, x0 + size / 2, y0 + size + 70, "1辺 30センチ", font(34), col)
    if t >= 1.6:
        b = ease((t - 1.6) / 0.4)
        col = tuple(int(AMBER[i] * b) for i in range(3))
        ctext(d, x0 + size + 170, y0 + 90, "点は 5×5", font(36), col)
        ctext(d, x0 + size + 170, y0 + 150, "25個", font(34), col)
    if t >= 2.4:
        b = ease((t - 2.4) / 0.4)
        col = tuple(int(GREEN[i] * b) for i in range(3))
        ctext(d, x0 - 180, y0 + 90, "高さ 5ミリ", font(36), col)
        ctext(d, x0 - 180, y0 + 150, "つまずかず、読める", font(26), col)
    if t >= 3.4:
        b = ease((t - 3.4) / 0.5)
        ctext(d, 1000, 870, "2001年、国の規格に。どの町でも同じ形", font(42),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- メイン
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))

    spans = v2.spans_from_timing("tenji-block")

    def sync(name, bounds, draw):
        if name not in spans:
            print(f"スキップ（台本に無い）: {name}")
            return
        b, dur = spans[name]
        vals = list(b)
        while len(vals) < 6:
            vals.append(vals[-1] + max(1.5, (dur - vals[-1]) * 0.5))
        bounds[:] = vals
        render(name, dur, draw)

    sync("tb_kinds", KD_P, draw_kinds)
    sync("tb_graph", GR_P, draw_graph)
    sync("tb_jis", JS_P, draw_jis)
