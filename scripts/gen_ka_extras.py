#!/usr/bin/env python3
"""カラオケ（karaoke）用の年号カード5枚+図解アニメ2本を生成する。

クリップ名は ka_ 名義。尺は timing.json 実測（spans_from_timing）。
実行: PYTHONPATH=. python3 scripts/gen_ka_extras.py（voice 後）
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
PINK = (235, 120, 170)
DARKBG = (10, 14, 24)

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1940", "誕生"), ("1956", "ドラム"), ("1971", "8JUKE"),
          ("1999", "タイム誌"), ("2004", "イグノーベル")]

CARDS = [
    ("ka_era1940", 0, "1940", "大阪・十三に生まれる", "5月10日・のちの井上大佑"),
    ("ka_era1956", 1, "1956", "ドラム少年", "楽譜は読めない・16歳"),
    ("ka_era1971", 2, "1971", "8JUKE誕生", "手作りの11台・100円で5分"),
    ("ka_era1999", 3, "1999", "タイム誌が選ぶ20人", "アジアの夜を変えた男"),
    ("ka_era2004", 4, "2004", "イグノーベル平和賞", "ハーバードの講堂・1100人"),
]


# ---------------------------------------------------------------- 1. 8JUKEの中身
JB_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_jbox(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "ありものだけで作った、8JUKE")
    # 本体の箱（中央帯 x710-1300 に収める）
    d.rounded_rectangle([760, 200, 1240, 840], radius=18,
                        outline=(150, 156, 168), width=8)
    rows = [
        (JB_P[0] + 0.3, "8トラックデッキ", "車用・伴奏テープ入れ", AMBER, 250),
        (JB_P[1], "100円コインボックス", "入れたら5分動く", GREEN, 400),
        (JB_P[2], "アンプ+マイク", "声と伴奏を一緒に鳴らす", BLUE, 550),
        (JB_P[3], "エコー", "誰でも3割うまく聞こえる", PINK, 700),
    ]
    for st, name, note, col, y in rows:
        if t < st:
            continue
        b = ease(min(1.0, (t - st) / 0.45))
        c3 = tuple(int(col[i] * b) for i in range(3))
        g3 = tuple(int(GRAY[i] * b) for i in range(3))
        d.rounded_rectangle([800, y, 1200, y + 110], radius=12, outline=c3, width=5)
        ctext(d, 1000, y + 34, name, font(38), c3)
        ctext(d, 1000, y + 80, note, font(24), g3)
    if t >= JB_P[3] + 1.2:
        b = ease((t - JB_P[3] - 1.2) / 0.5)
        ctext(d, 1000, 930, "全部、よそ様の発明の組み合わせ", font(40),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. 神戸から全国へ
SP_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_spread(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "神戸のスナックから、全国へ")
    cx, cy = 1000, 560
    # 広がりの同心円
    if t >= SP_P[0] + 0.3:
        b = ease(min(1.0, (t - SP_P[0] - 0.3) / 0.5))
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16],
                  fill=tuple(int(RED[i] * b) for i in range(3)))
        ctext(d, cx, cy + 60, "神戸", font(34),
              tuple(int(GRAY[i] * b) for i in range(3)))
    if t >= SP_P[1]:
        n = int(min(1.0, (t - SP_P[1]) / 1.8) * 3) + 1
        for k in range(n):
            r = 90 + k * 70
            d.ellipse([cx - r, cy - r * 0.62, cx + r, cy + r * 0.62],
                      outline=AMBER, width=4)
        b = ease(min(1.0, (t - SP_P[1]) / 0.6))
        ctext(d, cx, 300, "1年で、約200店", font(44),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= SP_P[2]:
        rnd_pts = []
        import random
        rnd = random.Random(11)
        for _ in range(26):
            ang = rnd.uniform(0, math.pi * 2)
            r = rnd.uniform(120, 300)
            rnd_pts.append((cx + math.cos(ang) * r * 1.35, cy + math.sin(ang) * r * 0.6))
        n = int(min(1.0, (t - SP_P[2]) / 1.6) * len(rnd_pts))
        for px, py in rnd_pts[:n]:
            d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=GREEN)
        b = ease(min(1.0, (t - SP_P[2]) / 0.6))
        ctext(d, cx, 900, "後継機まで、累計約2万5000台", font(42),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- メイン
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 13.0, m.make_era(idx, year, title, sub))

    spans = v2.spans_from_timing("karaoke")

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

    sync("ka_jbox", JB_P, draw_jbox)
    sync("ka_spread", SP_P, draw_spread)
