#!/usr/bin/env python3
"""カッターナイフ（cutter-knife）用の年号カード2枚+図解アニメ2本を生成する。

クリップ名は ck_/era_ck 名義。尺は timing.json 実測（spans_from_timing）。
図解は単独シーンに置くので、全要素を4秒以内に出し切る詰めたタイミングにする。
実行: PYTHONPATH=. python3 scripts/gen_ck_extras.py（voice 後）
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
STEEL = (185, 190, 202)
STEEL_DK = (120, 126, 140)

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1956", "発明"), ("1959", "特許"), ("1967", "オルファ")]

CARDS = [
    ("era_ck1950", 0, "1956", "折る刃の、ひらめき", "印刷工・30歳の発明"),
    ("era_ck1967", 2, "1967", "オルファ、誕生", "6月8日・兄弟と妻の会社"),
]


def _blade(d, x0, y0, ln=520, hh=64, b=1.0, seg=5, worn_first=False):
    """折り筋入りの刃を描く。"""
    col = tuple(int(STEEL[i] * b) for i in range(3))
    dk = tuple(int(STEEL_DK[i] * b) for i in range(3))
    d.polygon([(x0, y0), (x0 + ln, y0), (x0 + ln, y0 + hh * 0.55),
               (x0 + 40, y0 + hh)], fill=col)
    d.polygon([(x0, y0 + hh * 0.7), (x0 + 40, y0 + hh), (x0 + ln, y0 + hh * 0.55),
               (x0 + ln, y0 + hh * 0.72)], fill=(230, 234, 240) if b > 0.5 else col)
    step = ln / seg
    for k in range(1, seg):
        sx = x0 + k * step
        d.line([sx + 18, y0, sx - 18, y0 + hh], fill=dk, width=5)
    if worn_first:
        d.ellipse([x0 - 14, y0 + hh - 26, x0 + 30, y0 + hh + 14],
                  outline=tuple(int(RED[i] * b) for i in range(3)), width=5)


# ---------------------------------------------------------------- 1. 折る刃の仕組み
OR_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_ore(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "折ると、切れ味が戻る仕組み")
    # 上: すり減った先端
    if t >= 0.3:
        b = ease((t - 0.3) / 0.4)
        _blade(d, 720, 300, b=b, worn_first=True)
        ctext(d, 660, 300, "刃先だけ", font(26), tuple(int(RED[i] * b) for i in range(3)))
        ctext(d, 660, 344, "すり減る", font(26), tuple(int(RED[i] * b) for i in range(3)))
    # 矢印
    if t >= 1.3:
        b = ease((t - 1.3) / 0.4)
        col = tuple(int(GRAY[i] * b) for i in range(3))
        d.line([1000, 420, 1000, 500], fill=col, width=6)
        d.polygon([(984, 492), (1016, 492), (1000, 522)], fill=col)
        ctext(d, 1120, 450, "折り筋で、ポキッ", font(30),
              tuple(int(AMBER[i] * b) for i in range(3)))
    # 下: 折った後（1セグメント分短く・新品の先端）
    if t >= 2.0:
        b = ease((t - 2.0) / 0.4)
        _blade(d, 720, 560, ln=416, seg=4, b=b)
        seg = 104
        d.polygon([(1180, 560), (1240, 560), (1200, 624)],
                  fill=(int(80 * b), int(84 * b), int(96 * b)))
        ctext(d, 1290, 580, "折れた先は", font(24), tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 1290, 620, "捨てる", font(24), tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 660, 580, "新品の", font(26), tuple(int(GREEN[i] * b) for i in range(3)))
        ctext(d, 660, 624, "刃先が登場", font(26), tuple(int(GREEN[i] * b) for i in range(3)))
    if t >= 3.0:
        b = ease((t - 3.0) / 0.5)
        ctext(d, 1000, 790, "研がない。換えない。折る。", font(44),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= 3.6:
        b = ease((t - 3.6) / 0.5)
        ctext(d, 1000, 866, "一本の刃が、何本ぶんにもなる", font(38),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. 世界標準
ST_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_std(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "大阪生まれの、世界標準")
    # 小さい刃 9mm
    if t >= 0.3:
        b = ease((t - 0.3) / 0.4)
        _blade(d, 740, 330, ln=340, hh=42, seg=5, b=b)
        ctext(d, 1200, 340, "小型刃 幅9ミリ", font(34),
              tuple(int(GREEN[i] * b) for i in range(3)))
    # 大きい刃 18mm
    if t >= 1.2:
        b = ease((t - 1.2) / 0.4)
        _blade(d, 740, 470, ln=460, hh=76, seg=6, b=b)
        ctext(d, 1330, 490, "大型刃 幅18ミリ", font(34),
              tuple(int(BLUE[i] * b) for i in range(3)))
    # 59度
    if t >= 2.1:
        b = ease((t - 2.1) / 0.4)
        col = tuple(int(AMBER[i] * b) for i in range(3))
        d.line([840, 700, 1000, 700], fill=col, width=5)
        d.line([840, 700, 940, 620], fill=col, width=5)
        d.arc([840 - 40, 660, 920, 740], 320, 360, fill=col, width=5)
        ctext(d, 1120, 660, "折れ線の角度 59度", font(34), col)
    if t >= 3.0:
        b = ease((t - 3.0) / 0.5)
        ctext(d, 1000, 800, "決めた寸法に、世界が合わせた", font(40),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= 3.6:
        b = ease((t - 3.6) / 0.5)
        ctext(d, 1000, 872, "事実上の、世界標準規格", font(40),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- メイン
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))

    spans = v2.spans_from_timing("cutter-knife")

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

    sync("ck_ore", OR_P, draw_ore)
    sync("ck_std", ST_P, draw_std)
