#!/usr/bin/env python3
"""新幹線×カワセミ（shinkansen-bird）用の年号カード2枚+図解アニメ3本を生成する。

クリップ名は sb_/era_sb 名義。尺は timing.json 実測（spans_from_timing）。
図解は単独シーンに置くので、全要素を4秒以内に出し切る詰めたタイミングにする。
実行: PYTHONPATH=. python3 scripts/gen_sb_extras.py（voice 後）
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
DARKBG = (10, 14, 24)
KAWASEMI = (60, 140, 220)

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1990", "挑戦"), ("1997", "500系デビュー"), ("現代", "継承")]

CARDS = [
    ("era_sb1990", 0, "1990", "最速への挑戦", "時速300キロと、騒音の壁"),
    ("era_sb1997", 1, "1997", "500系、デビュー", "3月・鳥から生まれた最速"),
]


# ---------------------------------------------------------------- 1. カワセミ→ノーズ
KC_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_kuchibashi(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "くちばしの形を、先頭にうつす")
    # 左: カワセミのダイブ（水面へ）
    if t >= 0.3:
        b = ease((t - 0.3) / 0.4)
        d.line([700, 620, 1300, 620], fill=BLUE, width=4)
        ctext(d, 760, 650, "水面", font(26), BLUE)
        # くちばし+頭（斜め下向き）
        cx, cy = 880, 480
        d.polygon([(cx - 130, cy - 60), (cx, cy - 10), (cx - 40, cy + 40)],
                  fill=tuple(int(KAWASEMI[i] * b) for i in range(3)))
        d.ellipse([cx - 60, cy - 70, cx + 60, cy + 40],
                  fill=tuple(int(KAWASEMI[i] * b) for i in range(3)))
        d.polygon([(cx - 10, cy + 30), (cx + 40, cy + 130), (cx + 80, cy + 90)],
                  fill=(int(230 * b),) * 3)
        ctext(d, 880, 330, "カワセミ", font(34),
              tuple(int(KAWASEMI[i] * b) for i in range(3)))
        ctext(d, 880, 386, "しぶきの出ないダイブ", font(26),
              tuple(int(GRAY[i] * b) for i in range(3)))
    # 矢印
    if t >= 1.3:
        d.line([980, 500, 1080, 500], fill=GRAY, width=6)
        d.polygon([(1080, 484), (1080, 516), (1108, 500)], fill=GRAY)
    # 右: ノーズ断面（なだらかな断面積）
    if t >= 1.6:
        b = ease((t - 1.6) / 0.4)
        x0, y = 1120, 560
        d.polygon([(x0, y), (x0 + 240, y - 90), (x0 + 320, y - 90), (x0 + 320, y)],
                  fill=(int(210 * b), int(216 * b), int(226 * b)))
        d.rectangle([x0 + 240, y - 26, x0 + 320, y - 10], fill=(70, 90, 160))
        ctext(d, 1280, 620, "500系の鼻 15m", font(30),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= 2.4:
        b = ease((t - 2.4) / 0.4)
        ctext(d, 1000, 730, "先から根元へ、少しずつ太くなる", font(36),
              tuple(int(GREEN[i] * b) for i in range(3)))
    if t >= 3.2:
        b = ease((t - 3.2) / 0.5)
        ctext(d, 1000, 850, "空気をそっと押しのけて、ドンを消す", font(42),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. セレーション
SR_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_serration(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "フクロウの羽の、ギザギザの技")
    # 上: つるつるの棒 → 大きな渦
    if t >= 0.3:
        b = ease((t - 0.3) / 0.4)
        y = 330
        d.rounded_rectangle([760, y, 1000, y + 44], radius=20,
                            fill=(int(120 * b), int(126 * b), int(138 * b)))
        for k in range(2):
            r = 46
            cxx = 1090 + k * 120
            d.arc([cxx - r, y - r + 22, cxx + r, y + r + 22], 0, 300,
                  fill=tuple(int(RED[i] * b) for i in range(3)), width=7)
        ctext(d, 880, y - 56, "つるつるの棒", font(30),
              tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 1160, y - 56, "大きな渦 = 騒音", font(30),
              tuple(int(RED[i] * b) for i in range(3)))
    # 下: ギザギザ付き → 小さな渦
    if t >= 1.5:
        b = ease((t - 1.5) / 0.4)
        y = 590
        d.rounded_rectangle([760, y, 1000, y + 44], radius=20,
                            fill=(int(120 * b), int(126 * b), int(138 * b)))
        for k in range(6):
            d.polygon([(770 + k * 38, y), (784 + k * 38, y - 22), (798 + k * 38, y)],
                      fill=tuple(int(AMBER[i] * b) for i in range(3)))
        for k in range(5):
            r = 14
            cxx = 1050 + k * 56
            d.arc([cxx - r, y + 8 - r, cxx + r, y + 8 + r], 0, 300,
                  fill=tuple(int(GREEN[i] * b) for i in range(3)), width=5)
        ctext(d, 880, y - 66, "ギザギザ付き", font(30),
              tuple(int(AMBER[i] * b) for i in range(3)))
        ctext(d, 1160, y - 66, "小さな渦だけ = 静か", font(30),
              tuple(int(GREEN[i] * b) for i in range(3)))
    if t >= 2.6:
        b = ease((t - 2.6) / 0.5)
        ctext(d, 1000, 760, "小さな渦が、音の元の大きな渦を防ぐ", font(38),
              tuple(int(GREEN[i] * b) for i in range(3)))
    if t >= 3.4:
        b = ease((t - 3.4) / 0.5)
        ctext(d, 1000, 862, "翼型パンタグラフに応用", font(40),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 3. 成果
SK_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_seika(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "鳥に学んだ、500系の成績表")
    rows = [("空気抵抗", "30％減", GREEN),
            ("消費電力", "1割速くても 15％減", BLUE),
            ("騒音", "世界一厳しい基準クリア", AMBER)]
    for k, (name, val, col) in enumerate(rows):
        st = 0.4 + k * 0.9
        if t < st:
            continue
        b = ease(min(1.0, (t - st) / 0.4))
        y = 300 + k * 170
        d.rounded_rectangle([640, y, 1360, y + 130], radius=16,
                            outline=tuple(int(col[i] * b) for i in range(3)), width=4)
        ctext(d, 780, y + 42, name, font(38),
              tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 1130, y + 42, val, font(36),
              tuple(int(col[i] * b) for i in range(3)))
    if t >= 3.3:
        b = ease((t - 3.3) / 0.5)
        ctext(d, 1000, 860, "速く、静かに、省エネで", font(44),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- メイン
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))

    spans = v2.spans_from_timing("shinkansen-bird")

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

    sync("sb_kuchibashi", KC_P, draw_kuchibashi)
    sync("sb_serration", SR_P, draw_serration)
    sync("sb_seika", SK_P, draw_seika)
