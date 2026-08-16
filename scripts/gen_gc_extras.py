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
    # 単独シーン（1カット・約6秒）で4項目を出し切る詰めたタイミング
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "胃カメラ・4つの目標")
    goals = [("① 危険がない", GREEN, "体の中に入れる"),
             ("② 苦しくない", BLUE, "柔らかく、細く"),
             ("③ 速い", AMBER, "胃の中を短時間で"),
             ("④ 鮮明", (230, 130, 200), "病気を見分けられる")]
    for k, (title, col, note) in enumerate(goals):
        st = 0.3 + k * 0.75
        if t < st:
            continue
        y = 250 + k * 120
        b = ease(min(1.0, (t - st) / 0.4))
        x0 = 700
        d.rounded_rectangle([x0, y, x0 + 600, y + 104], radius=14,
                            outline=tuple(int(col[i] * b) for i in range(3)), width=4)
        cb = tuple(int(col[i] * b) for i in range(3))
        f = font(46)
        d.text((x0 + 30, y + 26), title, font=f, fill=cb)
        gb = tuple(int(GRAY[i] * b) for i in range(3))
        fn = font(30)
        d.text((x0 + 600 - 30 - d.textlength(note, font=fn), y + 38), note,
               font=fn, fill=gb)
    if t >= 3.6:
        b = ease((t - 3.6) / 0.5)
        ctext(d, 1000, 820, "4つ全部そろって、はじめて胃カメラ", font(44),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. 胃の中が写った
SH_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_shashin(d, t):
    # 単独シーン（約5秒）でクライマックスの「写真が浮かぶ」瞬間を出し切る。
    # 管の挿入・撮影の過程は直前の会話カットで描写済みなので、ここは現像の像に集中。
    d.rectangle([0, 0, W, H], fill=DARKBG)
    if t < 1.0:
        _caption(d, "暗室で、像が浮かんでくる")
    else:
        _caption(d, "生きた胃が、世界で初めて鮮明に")
    # 現像バットに胃壁の写真が浮かび上がる
    p = ease(min(1.0, t / 1.4))
    d.rounded_rectangle([740, 240, 1260, 760], radius=10,
                        fill=(int(228 * p), int(228 * p), int(226 * p)))
    if p > 0.35:
        _stomach(d, 1000, 500, s=1.15, lesion=True)
    if t >= 2.0:
        b = ease((t - 2.0) / 0.5)
        d.ellipse([1030 - 74, 545 - 74, 1030 + 74, 545 + 74],
                  outline=tuple(int(RED[i] * b) for i in range(3)), width=6)
        ctext(d, 1000, 812, "胃潰瘍まで、くっきりと", font(42),
              tuple(int(RED[i] * b) for i in range(3)))
    if t >= 3.4:
        b = ease((t - 3.4) / 0.5)
        ctext(d, 1000, 880, "開腹せずに、胃の中を撮った世界初", font(42),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 3. 現代への進化
SK_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_shinka(d, t):
    # 単独シーン（約5秒）で3段の進化を出し切る。
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "胃カメラの進化")
    steps = [("フィルム式", "撮って、現像して見る", "1950s"),
             ("ファイバースコープ", "その場で覗いて見る", "1960s〜"),
             ("電子内視鏡", "画面にリアルタイム表示", "現代")]
    for k, (name, note, era) in enumerate(steps):
        st = 0.3 + k * 1.0
        if t < st:
            continue
        b = ease(min(1.0, (t - st) / 0.4))
        y = 250 + k * 168
        col = (GRAY, BLUE, GREEN)[k]
        d.rounded_rectangle([700, y, 1300, y + 132], radius=16,
                            outline=tuple(int(col[i] * b) for i in range(3)), width=4)
        ctext(d, 900, y + 24, name, font(46),
              tuple(int(col[i] * b) for i in range(3)))
        ctext(d, 900, y + 80, note, font(32),
              tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 1190, y + 48, era, font(34),
              tuple(int(AMBER[i] * b) for i in range(3)))
        if k < 2 and t >= st + 0.7:
            d.line([1000, y + 132, 1000, y + 168], fill=GRAY, width=6)
            d.polygon([(984, y + 160), (1016, y + 160), (1000, y + 184)], fill=GRAY)
    if t >= 3.6:
        b = ease((t - 3.6) / 0.5)
        ctext(d, 1000, 858, "胃がんは、早期に見つかれば治せる", font(42),
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
