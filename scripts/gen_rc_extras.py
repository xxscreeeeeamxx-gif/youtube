#!/usr/bin/env python3
"""電気炊飯器再現ドラマ（rice-cooker）用の年号カード2枚+図解アニメ5本を生成する。

クリップ名は rc_/era_r 名義。フェーズ境界は timing.json 実測（spans_from_timing）。
図解は単独シーンに置くので、全要素を4秒以内に出し切る詰めたタイミングにする。
実行: PYTHONPATH=. python3 scripts/gen_rc_extras.py（voice 後）
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
STEEL = (120, 126, 138)
WATER = (90, 160, 220)
FIRE = (240, 150, 50)

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1950", "依頼"), ("1955", "発売"), ("現代", "進化")]

CARDS = [
    ("era_r1950", 0, "1950", "ごはんは、重労働だった", "夜明け前の火の番"),
    ("era_r1955", 1, "1955", "自動式電気釜、発売", "12月10日・3200円"),
]


# ---------------------------------------------------------------- 共通部品
def _pot(d, cx, cy, w, h, col=STEEL, lid=True):
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                        radius=18, fill=col, outline=(70, 74, 84), width=4)
    if lid:
        d.rounded_rectangle([cx - w / 2 - 8, cy - h / 2 - 22, cx + w / 2 + 8, cy - h / 2 + 8],
                            radius=12, fill=(90, 94, 104))


def _heat(d, cx, y, w):
    """下部のヒーター（波線）。"""
    pts = []
    for i in range(int(w / 12)):
        pts.append((cx - w / 2 + i * 12, y + (6 if i % 2 else -6)))
    d.line(pts, fill=(200, 90, 60), width=6)


# ---------------------------------------------------------------- 1. 98度20分グラフ
DT_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_data(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "おいしいごはんの、温度と時間")
    x0, y0, x1, y1 = 700, 300, 1300, 760
    d.line([x0, y1, x1, y1], fill=GRAY, width=5)   # 時間軸
    d.line([x0, y1, x0, y0], fill=GRAY, width=5)   # 温度軸
    ctext(d, x0 - 60, 340, "100", font(30), GRAY)
    ctext(d, x0 - 50, y1 - 20, "0", font(30), GRAY)
    ctext(d, x1 - 40, y1 + 36, "時間", font(30), GRAY)
    # 温度曲線: 立ち上がり→98度で20分保持
    prog = min(1.0, t / 2.6)
    pts = []
    for i in range(int(600 * prog)):
        px = x0 + i
        f = i / 600.0
        if f < 0.25:
            temp = f / 0.25
        else:
            temp = 0.96 + 0.02 * math.sin(f * 20)
        py = y1 - temp * (y1 - y0) * 0.98
        pts.append((px, py))
    if len(pts) > 1:
        d.line(pts, fill=AMBER, width=6)
    # 98度ライン
    if t >= 1.2:
        yy = y1 - 0.96 * (y1 - y0)
        d.line([x0, yy, x1, yy], fill=(GREEN[0], GREEN[1], GREEN[2]), width=2)
        ctext(d, x1 - 90, yy - 30, "98度", font(34), GREEN)
    # 20分の保持帯
    if t >= 2.2:
        bx0 = x0 + 0.25 * 600
        d.rectangle([bx0, y0 + 20, x1, y1 - 0.9 * (y1 - y0)], fill=(40, 70, 55, 90))
        ctext(d, (bx0 + x1) / 2, y0 + 40, "この20分で、芯までふっくら", font(38), GREEN)
    if t >= 3.4:
        b = ease((t - 3.4) / 0.5)
        ctext(d, 1000, 850, "98度を、20分。それが、うまいごはん", font(44),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. 二重釜間接炊き
FG_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_futagama(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    if t < 1.4:
        _caption(d, "外の釜に水、内の釜にお米")
    elif t < 3.0:
        _caption(d, "水があるうちは、100度で炊ける")
    else:
        _caption(d, "水が尽きると、温度が跳ね上がる")
    cx, cy = 1000, 480
    # 外釜
    _pot(d, cx, cy, 380, 300, col=(96, 100, 112), lid=False)
    # 内釜
    _pot(d, cx, cy - 10, 240, 210, col=STEEL, lid=False)
    # お米（内釜）
    d.rounded_rectangle([cx - 100, cy - 50, cx + 100, cy + 70], radius=10,
                        fill=(238, 232, 220))
    ctext(d, cx, cy + 10, "お米", font(36), (90, 80, 60))
    # 外釜の水（蒸発する）
    water_h = max(0, 60 * (1 - min(1.0, max(0, t - 0.8) / 2.6)))
    if water_h > 2:
        d.rectangle([cx - 180, cy + 90 - water_h, cx - 130, cy + 90], fill=WATER)
        d.rectangle([cx + 130, cy + 90 - water_h, cx + 180, cy + 90], fill=WATER)
        ctext(d, cx - 250, cy + 60, "水", font(30), WATER)
    # ヒーター
    _heat(d, cx, cy + 170, 400)
    # 湯気
    for k in range(2):
        ph = t * 1.6 + k * 2
        pts = [(cx - 40 + k * 80 + 14 * math.sin(ph + j * 0.5), cy - 130 - j * 16)
               for j in range(7)]
        d.line(pts, fill=(220, 224, 230, 140), width=7)
    # 温度計
    tempC = 100 if water_h > 2 else min(140, 100 + (t - 3.4) * 40)
    col = GREEN if water_h > 2 else RED
    if t >= 1.0:
        ctext(d, cx + 300, cy - 40, f"{int(tempC)}度", font(50), col)
    # 水が尽きたらバイメタルOFF
    if t >= 3.2:
        b = ease((t - 3.2) / 0.5)
        ctext(d, 1000, 800, "その熱を感じて、スイッチが切れる", font(44),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= 4.2:
        b = ease((t - 4.2) / 0.5)
        ctext(d, 1000, 880, "一杯の水が、いちばん正直なタイマー", font(42),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 3. 三重釜
SJ_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_sanju(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "寒い日も、暑い日も、同じごはん")
    cx, cy = 1000, 500
    # 三層
    if t >= 0.3:
        _pot(d, cx, cy, 460, 340, col=(70, 76, 92), lid=False)  # 外気を防ぐ層
    _pot(d, cx, cy, 360, 280, col=(96, 100, 112), lid=False)    # 水の釜
    _pot(d, cx, cy - 10, 230, 200, col=STEEL, lid=False)        # 米の釜
    d.rounded_rectangle([cx - 95, cy - 46, cx + 95, cy + 66], radius=10,
                        fill=(238, 232, 220))
    ctext(d, cx, cy + 8, "お米", font(34), (90, 80, 60))
    labels = [("内: お米の釜", cx, cy - 130, STEEL),
              ("中: 水の釜", cx - 250, cy + 150, WATER),
              ("外: 空気の層", cx + 250, cy + 190, (140, 150, 180))]
    for k, (lab, lx, ly, col) in enumerate(labels):
        if t >= 0.6 + k * 0.7:
            ctext(d, lx, ly, lab, font(32), col)
    # 外の寒さ（青い矢印が外層で止まる）
    if t >= 2.6:
        for sx in (720, 1280):
            d.line([sx, cy, sx + (60 if sx < cx else -60), cy], fill=BLUE, width=6)
        ctext(d, cx, 300, "外の寒さを、空気の層がさえぎる", font(34), BLUE)
    if t >= 3.6:
        b = ease((t - 3.6) / 0.5)
        ctext(d, 1000, 860, "どこでも、必ず炊ける箱へ", font(46),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 4. 普及グラフ
GR_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_graph(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "自動式電気釜の、広がり")
    x0, y1 = 700, 800
    steps = [("発売時", "700台", 0.05, GRAY),
             ("最盛期", "月20万台", 0.85, AMBER),
             ("4年後", "全家庭の半分", 1.0, GREEN)]
    for k, (label, val, h, col) in enumerate(steps):
        st = 0.3 + k * 0.9
        if t < st:
            continue
        b = ease(min(1.0, (t - st) / 0.4))
        bx = x0 + k * 200
        bh = 420 * h * b
        d.rounded_rectangle([bx, y1 - bh, bx + 130, y1], radius=10,
                            fill=tuple(int(col[i]) for i in range(3)))
        ctext(d, bx + 65, y1 + 34, label, font(32), GRAY)
        ctext(d, bx + 65, y1 - bh - 40, val, font(34),
              tuple(int(col[i] * b) for i in range(3)))
    if t >= 3.4:
        b = ease((t - 3.4) / 0.5)
        ctext(d, 1000, 210, "4年で、日本の半分の家に", font(46),
              tuple(int(AMBER[i] * b) for i in range(3)))
        ctext(d, 1000, 280, "朝の火の番が、消えていった", font(40),
              tuple(int(GRAY[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 5. 進化
SK_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_shinka(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "炊飯器の進化")
    steps = [("電気釜", "水の蒸発でスイッチOFF", "1950s", GRAY),
             ("マイコン式", "温度を細かく操る", "1970s〜", BLUE),
             ("IH式", "釜ごと電気で発熱", "現代", GREEN)]
    for k, (name, note, era, col) in enumerate(steps):
        st = 0.3 + k * 1.0
        if t < st:
            continue
        b = ease(min(1.0, (t - st) / 0.4))
        y = 250 + k * 168
        d.rounded_rectangle([700, y, 1300, y + 132], radius=16,
                            outline=tuple(int(col[i] * b) for i in range(3)), width=4)
        ctext(d, 900, y + 24, name, font(46),
              tuple(int(col[i] * b) for i in range(3)))
        ctext(d, 900, y + 82, note, font(30),
              tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 1190, y + 48, era, font(32),
              tuple(int(AMBER[i] * b) for i in range(3)))
        if k < 2 and t >= st + 0.7:
            d.line([1000, y + 132, 1000, y + 168], fill=GRAY, width=6)
            d.polygon([(984, y + 160), (1016, y + 160), (1000, y + 184)], fill=GRAY)
    if t >= 3.6:
        b = ease((t - 3.6) / 0.5)
        ctext(d, 1000, 858, "土台は、あの二重釜のひらめき", font(42),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- メイン
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))

    spans = v2.spans_from_timing("rice-cooker")

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

    sync("rc_data", DT_P, draw_data)
    sync("rc_futagama", FG_P, draw_futagama)
    sync("rc_sanju", SJ_P, draw_sanju)
    sync("rc_graph", GR_P, draw_graph)
    sync("rc_shinka", SK_P, draw_shinka)
