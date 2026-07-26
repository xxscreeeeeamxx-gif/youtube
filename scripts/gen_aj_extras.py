#!/usr/bin/env python3
"""うま味発見（ajinomoto）用の年号カード2枚+図解アニメ3本を生成する。

クリップ名は aj_/era_aj 名義。尺は timing.json 実測（spans_from_timing）。
図解は単独シーンに置くので、全要素を4秒以内に出し切る詰めたタイミングにする。
実行: PYTHONPATH=. python3 scripts/gen_aj_extras.py（voice 後）
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
KONBU = (70, 100, 70)

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1899", "留学"), ("1908", "うま味発見"), ("1909", "発売")]

CARDS = [
    ("era_aj1899", 0, "1899", "ドイツ留学", "体格の差に、衝撃を受ける"),
    ("era_aj1909", 2, "1909", "味の素、発売", "5月20日・世界初のうま味調味料"),
]


# ---------------------------------------------------------------- 1. 12kg→30g
KS_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_kessho(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "昆布12キロから、結晶30グラム")
    # 左: 昆布の山
    if t >= 0.3:
        b = ease((t - 0.3) / 0.4)
        col = tuple(int(KONBU[i] * b) for i in range(3))
        for k in range(5):
            d.line([700 + k * 40, 620 - (k % 2) * 30, 780 + k * 40, 380 + (k % 3) * 40],
                   fill=col, width=30)
        ctext(d, 800, 680, "昆布 12キロ", font(36),
              tuple(int(AMBER[i] * b) for i in range(3)))
    # 矢印（煮出す→煮詰める→結晶化）
    if t >= 1.2:
        b = ease((t - 1.2) / 0.4)
        col = tuple(int(GRAY[i] * b) for i in range(3))
        d.line([950, 500, 1120, 500], fill=col, width=6)
        d.polygon([(1112, 484), (1112, 516), (1140, 500)], fill=col)
        ctext(d, 1040, 440, "煮出す", font(26), col)
        ctext(d, 1040, 552, "煮詰める", font(26), col)
    # 右: 小さな結晶
    if t >= 1.8:
        b = ease((t - 1.8) / 0.4)
        for k, (dx, dy) in enumerate([(0, 0), (46, 18), (-40, 26), (16, 44), (-16, -30)]):
            x, y = 1250 + dx, 500 + dy
            d.polygon([(x, y - 16), (x + 14, y), (x, y + 16), (x - 14, y)],
                      fill=(int(240 * b), int(240 * b), int(250 * b)))
        ctext(d, 1260, 600, "グルタミン酸 30グラム", font(32),
              tuple(int(GREEN[i] * b) for i in range(3)))
    if t >= 2.6:
        b = ease((t - 2.6) / 0.4)
        ctext(d, 1000, 770, "取れたのは、わずか0.25％", font(38),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= 3.3:
        b = ease((t - 3.3) / 0.5)
        ctext(d, 1000, 860, "この結晶が、うま味の正体", font(44),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. 5基本味
GM_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_gomi(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "基本味は、5つ")
    items = [("甘味", (240, 150, 170), "エネルギーの合図"),
             ("塩味", (150, 190, 240), "ミネラルの合図"),
             ("酸味", (240, 220, 100), "腐敗を見分ける"),
             ("苦味", (150, 220, 150), "毒を見分ける"),
             ("うま味", (240, 170, 90), "タンパク質の合図")]
    for k, (name, col, note) in enumerate(items):
        st = 0.3 + k * 0.55
        if t < st:
            continue
        b = ease(min(1.0, (t - st) / 0.4))
        cx = 720 + (k % 3) * 280
        cy = 360 if k < 3 else 620
        if k >= 3:
            cx = 860 + (k - 3) * 280
        r = 96 if name != "うま味" else 108
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=tuple(int(col[i] * b) for i in range(3)), width=6)
        ctext(d, cx, cy - 28, name, font(40),
              tuple(int(col[i] * b) for i in range(3)))
        ctext(d, cx, cy + 26, note, font(22),
              tuple(int(GRAY[i] * b) for i in range(3)))
    if t >= 3.3:
        b = ease((t - 3.3) / 0.5)
        ctext(d, 1000, 850, "5人目の発見者だけ、名前が分かっている", font(38),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 3. UMAMIの旅路
UM_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_umami(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "UMAMIが、世界の言葉になるまで")
    steps = [("1908", "池田が発見・命名", AMBER),
             ("1985", "国際会議でUMAMI採択", BLUE),
             ("2000", "舌に専用の受容体を発見", GREEN)]
    x0, x1 = 700, 1300
    d.line([x0, 560, x1, 560], fill=GRAY, width=5)
    for k, (year, note, col) in enumerate(steps):
        st = 0.4 + k * 0.9
        if t < st:
            continue
        b = ease(min(1.0, (t - st) / 0.4))
        x = x0 + (x1 - x0) * k / 2
        d.ellipse([x - 16, 544, x + 16, 576], fill=tuple(int(col[i] * b) for i in range(3)))
        ctext(d, x, 480, year, font(44), tuple(int(col[i] * b) for i in range(3)))
        ctext(d, x, 620 + (k % 2) * 54, note, font(28),
              tuple(int(GRAY[i] * b) for i in range(3)))
    if t >= 3.2:
        b = ease((t - 3.2) / 0.5)
        ctext(d, 1000, 790, "発見から92年後の、科学的な証明", font(38),
              tuple(int(GREEN[i] * b) for i in range(3)))
    if t >= 3.8:
        b = ease((t - 3.8) / 0.5)
        ctext(d, 1000, 872, "UMAMIは、日本語のまま世界共通語に", font(40),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- メイン
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))

    spans = v2.spans_from_timing("ajinomoto")

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

    sync("aj_kessho", KS_P, draw_kessho)
    sync("aj_gomi", GM_P, draw_gomi)
    sync("aj_umami", UM_P, draw_umami)
