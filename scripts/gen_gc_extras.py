#!/usr/bin/env python3
"""胃カメラ再現ドラマ（gastro-camera）用の年号カード3枚+図解アニメ3本を生成する。

クリップ名は gc_/era_g 名義。フェーズ境界は timing.json 実測（spans_from_timing）。
実行: PYTHONPATH=. python3 scripts/gen_gc_extras.py（voice 後）
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
STOMACH = (206, 140, 130)
LESION = (150, 82, 76)

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1949", "相談"), ("1950", "撮影成功"), ("現代", "電子内視鏡")]

CARDS = [
    ("era_g1949", 0, "1949", "胃の中は、闇だった", "東京・大学分院"),
    ("era_g1950", 1, "1950", "胃の中が、写った", "世界初の胃カメラ"),
]


def _tube(d, pts, w=26, col=(120, 128, 140)):
    """柔らかい管（連続線）。"""
    d.line(pts, fill=col, width=w, joint="curve")
    d.line(pts, fill=(150, 158, 170), width=max(4, w - 14), joint="curve")


def _stomach(d, cx, cy, s=1.0, lesion=False):
    """胃のシルエット（そら豆型）。"""
    d.pieslice([cx - 150 * s, cy - 130 * s, cx + 150 * s, cy + 170 * s],
               20, 320, fill=STOMACH, outline=(170, 110, 100), width=4)
    d.ellipse([cx - 120 * s, cy - 150 * s, cx + 40 * s, cy + 30 * s], fill=STOMACH)
    if lesion:
        d.ellipse([cx + 30 * s, cy + 20 * s, cx + 90 * s, cy + 80 * s], fill=LESION)


# ---------------------------------------------------------------- 1. 4つの目標
MK_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_mokuhyou(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "胃カメラ・4つの目標")
    goals = [("① 危険がない", GREEN, "体の中に入れる"),
             ("② 苦しくない", BLUE, "柔らかく、細く"),
             ("③ 速い", AMBER, "胃の中を短時間で"),
             ("④ 鮮明", (230, 130, 200), "病気を見分けられる")]
    for k, (title, col, note) in enumerate(goals):
        st = MK_P[1] + k * 1.6 - 3.0
        if t < st:
            continue
        y = 300 + k * 128
        b = ease(min(1.0, (t - st) / 0.5))
        x0 = 700
        d.rounded_rectangle([x0, y, x0 + 600, y + 108], radius=14,
                            outline=tuple(int(col[i] * b) for i in range(3)), width=4)
        cb = tuple(int(col[i] * b) for i in range(3))
        f = font(46)
        d.text((x0 + 30, y + 28), title, font=f, fill=cb)
        gb = tuple(int(GRAY[i] * b) for i in range(3))
        fn = font(30)
        d.text((x0 + 600 - 30 - d.textlength(note, font=fn), y + 40), note,
               font=fn, fill=gb)
    if t >= MK_P[4]:
        b = ease((t - MK_P[4]) / 0.6)
        ctext(d, 1000, 900, "4つ全部そろって、はじめて胃カメラ", font(44),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. 胃の中が写った
SH_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_shashin(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    if t < SH_P[1]:
        _caption(d, "柔らかい管の先に、超小型カメラと豆電球")
    elif t < SH_P[3]:
        _caption(d, "胃の中で、シャッターを切る")
    else:
        _caption(d, "現像すると……")
    cx, cy = 1000, 520
    if t < SH_P[3]:
        # 管が口から胃へ入る断面図
        _tube(d, [(760, 200), (860, 340), (940, 460), (1000, 560)], w=24)
        _stomach(d, cx, cy + 40, s=1.0, lesion=(t >= SH_P[2]))
        # 先端のカメラ+電球
        d.ellipse([cx - 30, cy + 10, cx + 30, cy + 70], fill=(60, 66, 78))
        d.ellipse([cx - 12, cy + 28, cx + 12, cy + 52], fill=(150, 200, 220))
        if int(t * 3) % 2 == 0 and t >= SH_P[1]:
            d.ellipse([cx - 60, cy - 20, cx + 80, cy + 120], outline=(255, 240, 180),
                      width=4)
        if t >= SH_P[1] and (t - SH_P[1]) % 1.5 < 0.15:
            d.rectangle([cx - 180, cy - 140, cx + 200, cy + 220],
                        fill=(255, 255, 255, 90))
        if t >= SH_P[2]:
            n = min(21, int((t - SH_P[2]) / 0.14) + 1)
            ctext(d, 1000, 880, f"撮影 {n} ／ 21 枚", font(46), AMBER)
    else:
        # 写真として胃壁が浮かぶ
        p = ease(min(1.0, (t - SH_P[3]) / 1.6))
        d.rounded_rectangle([740, 260, 1260, 760], radius=10,
                            fill=(int(230 * p), int(230 * p), int(228 * p)))
        if p > 0.4:
            _stomach(d, 1000, 500, s=1.1, lesion=True)
            if t >= SH_P[4]:
                b = ease((t - SH_P[4]) / 0.6)
                d.ellipse([1030 - 70, 540 - 70, 1030 + 70, 540 + 70],
                          outline=tuple(int(RED[i] * b) for i in range(3)), width=6)
                ctext(d, 1000, 810, "生きた胃が、世界で初めて写った", font(44),
                      tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 3. 現代への進化
SK_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_shinka(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "胃カメラの進化")
    steps = [("フィルム式", "撮って、現像して見る", "1950s"),
             ("ファイバースコープ", "その場で覗いて見る", "1960s〜"),
             ("電子内視鏡", "画面にリアルタイム表示", "現代")]
    for k, (name, note, era) in enumerate(steps):
        st = SK_P[1] + k * 2.4 - 3.0
        if t < st:
            continue
        b = ease(min(1.0, (t - st) / 0.6))
        y = 320 + k * 180
        col = (GRAY, BLUE, GREEN)[k]
        d.rounded_rectangle([730, y, 1290, y + 140], radius=16,
                            outline=tuple(int(col[i] * b) for i in range(3)), width=4)
        ctext(d, 900, y + 26, name, font(46),
              tuple(int(col[i] * b) for i in range(3)))
        ctext(d, 900, y + 84, note, font(32),
              tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 1200, y + 52, era, font(34),
              tuple(int(AMBER[i] * b) for i in range(3)))
        if k < 2 and t >= st + 1.8:
            d.line([1010, y + 140, 1010, y + 180], fill=GRAY, width=6)
            d.polygon([(994, y + 172), (1026, y + 172), (1010, y + 196)], fill=GRAY)
    if t >= SK_P[4]:
        b = ease((t - SK_P[4]) / 0.6)
        ctext(d, 1000, 940, "胃がんは、早期に見つかれば治せる", font(44),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- メイン
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))

    spans = v2.spans_from_timing("gastro-camera")

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

    sync("gc_mokuhyou", MK_P, draw_mokuhyou)
    sync("gc_shashin", SH_P, draw_shashin)
    sync("gc_shinka", SK_P, draw_shinka)
