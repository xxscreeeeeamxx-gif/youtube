#!/usr/bin/env python3
"""ウォシュレット（washlet）用の年号カード2枚+図解アニメ2本を生成する。

クリップ名は wl_/era_wl 名義。尺は timing.json 実測（spans_from_timing）。
図解は単独シーンに置くので、全要素を4秒以内に出し切る詰めたタイミングにする。
実行: PYTHONPATH=. python3 scripts/gen_wl_extras.py（voice 後）
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

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1964", "輸入"), ("1980", "ウォシュレット"), ("1982", "伝説のCM")]

CARDS = [
    ("era_wl1964", 0, "1964", "輸入品との出会い", "12月・医療向けの洗う便座"),
    ("era_wl1980", 1, "1980", "ウォシュレット、発売", "6月・300人のデータを込めて"),
]


# ---------------------------------------------------------------- 1. 300人データ
DT_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_data(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "約300人の、実測データ")
    cx, cy = 1000, 500
    # 便座の輪郭
    if t >= 0.3:
        b = ease((t - 0.3) / 0.4)
        col = (int(200 * b), int(206 * b), int(214 * b))
        d.rounded_rectangle([cx - 260, cy - 180, cx + 260, cy + 180], radius=150,
                            outline=col, width=8)
        d.rounded_rectangle([cx - 170, cy - 110, cx + 170, cy + 110], radius=100,
                            outline=col, width=6)
    # データ点（ばらつき→意味のある散らばり）
    import random
    rnd = random.Random(43)
    if t >= 1.0:
        n = int(min(1.0, (t - 1.0) / 1.6) * 90)
        for k in range(n):
            ang = rnd.uniform(0, math.pi * 2)
            r = abs(rnd.gauss(0, 46))
            px, py = cx + math.cos(ang) * r * 1.4, cy + 40 + math.sin(ang) * r
            b2 = 1.0
            d.ellipse([px - 7, py - 7, px + 7, py + 7],
                      fill=(int(AMBER[0] * b2), int(AMBER[1] * b2), int(AMBER[2] * b2)))
    # 平均の一点
    if t >= 2.8:
        b = ease((t - 2.8) / 0.4)
        d.ellipse([cx - 20, cy + 20, cx + 20, cy + 60],
                  outline=(int(GREEN[0] * b), int(GREEN[1] * b), int(GREEN[2] * b)), width=8)
        ctext(d, cx + 240, cy + 30, "狙うべき一点", font(36),
              tuple(int(GREEN[i] * b) for i in range(3)))
    if t >= 3.5:
        b = ease((t - 3.5) / 0.5)
        ctext(d, 1000, 860, "ばらばらの体にも、共通の答えがあった", font(40),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. 黄金比率
GL_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_golden(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "体が教えた、黄金比率")
    rows = [("噴射の角度", "43度", GREEN, "届いて、跳ねない角度"),
            ("お湯の温度", "38度", AMBER, "体温より、ほんの少し上"),
            ("便座の温度", "36度", BLUE, "人の肌と、ほぼ同じ")]
    for k, (name, val, col, note) in enumerate(rows):
        st = 0.4 + k * 0.9
        if t < st:
            continue
        b = ease(min(1.0, (t - st) / 0.4))
        y = 300 + k * 165
        d.rounded_rectangle([620, y, 1380, y + 125], radius=16,
                            outline=tuple(int(col[i] * b) for i in range(3)), width=4)
        ctext(d, 790, y + 40, name, font(38), tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 1030, y + 38, val, font(56), tuple(int(col[i] * b) for i in range(3)))
        ctext(d, 1240, y + 44, note, font(24), tuple(int(GRAY[i] * b) for i in range(3)))
    if t >= 3.4:
        b = ease((t - 3.4) / 0.5)
        ctext(d, 1000, 850, "計算ではなく、300人の実測から", font(42),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- メイン
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))

    spans = v2.spans_from_timing("washlet")

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

    sync("wl_data", DT_P, draw_data)
    sync("wl_golden", GL_P, draw_golden)
