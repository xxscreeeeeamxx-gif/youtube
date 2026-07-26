#!/usr/bin/env python3
"""横井軍平（yokoi-gunpei）用の年号カード2枚+図解アニメ2本を生成する。

クリップ名は yg_/era_yg 名義。尺は timing.json 実測（spans_from_timing）。
図解は単独シーンに置くので、全要素を4秒以内に出し切る詰めたタイミングにする。
実行: PYTHONPATH=. python3 scripts/gen_yg_extras.py（voice 後）
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

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1965", "入社"), ("1980", "ゲーム&ウォッチ"), ("1989", "ゲームボーイ")]

CARDS = [
    ("era_yg1965", 0, "1965", "京都・任天堂", "花札の会社の、保守係"),
    ("era_yg1989", 2, "1989", "ゲームボーイ", "白黒画面の、大勝負"),
]


# ---------------------------------------------------------------- 1. 水平思考の図解
TG_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_tetsugaku(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "枯れた技術の、水平思考")
    # 縦軸: 性能競争（上へ）
    if t >= 0.3:
        b = ease((t - 0.3) / 0.4)
        col = tuple(int(RED[i] * b) for i in range(3))
        d.line([860, 700, 860, 320], fill=col, width=6)
        d.polygon([(844, 328), (876, 328), (860, 296)], fill=col)
        ctext(d, 860, 250, "垂直思考", font(34), col)
        ctext(d, 860, 300 - 46, "", font(20), col)
        ctext(d, 660, 380, "最新技術で", font(26), tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 660, 424, "性能を上げる", font(26), tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 660, 480, "高い・不安定", font(26), col)
    # 横軸: 使い道を広げる（右へ）
    if t >= 1.4:
        b = ease((t - 1.4) / 0.4)
        col = tuple(int(GREEN[i] * b) for i in range(3))
        d.line([860, 700, 1280, 700], fill=col, width=6)
        d.polygon([(1272, 684), (1272, 716), (1308, 700)], fill=col)
        ctext(d, 1160, 748, "水平思考", font(34), col)
        ctext(d, 1220, 600, "枯れた技術の", font(26), tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 1220, 644, "使い道を変える", font(26), tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 1220, 540, "安い・確実", font(26), col)
    # 例
    if t >= 2.4:
        b = ease((t - 2.4) / 0.4)
        ctext(d, 1000, 820, "電卓の部品 → ゲーム&ウォッチ", font(34),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= 3.2:
        b = ease((t - 3.2) / 0.5)
        ctext(d, 1000, 884, "性能ではなく、使い方を発明する", font(40),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. GB比較表
GB_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_gb(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "白黒 対 カラー、逆転の成績表")
    # ヘッダ
    if t >= 0.3:
        ctext(d, 1010, 270, "ゲームボーイ", font(32), GREEN)
        ctext(d, 1270, 270, "カラー勢", font(32), RED)
    rows = [("画面", "白黒4階調", "カラー", 0.7),
            ("電池", "約35時間", "数時間", 1.5),
            ("値段", "1万2500円", "倍近い", 2.3)]
    for k, (name, gb, rival, st) in enumerate(rows):
        if t < st:
            continue
        b = ease(min(1.0, (t - st) / 0.4))
        y = 330 + k * 130
        d.rounded_rectangle([640, y, 1400, y + 100], radius=12,
                            outline=(int(80 * b), int(90 * b), int(110 * b)), width=3)
        ctext(d, 740, y + 32, name, font(34), tuple(int(GRAY[i] * b) for i in range(3)))
        ctext(d, 1010, y + 32, gb, font(32), tuple(int(GREEN[i] * b) for i in range(3)))
        ctext(d, 1270, y + 32, rival, font(32), tuple(int(RED[i] * b) for i in range(3)))
    if t >= 3.1:
        b = ease((t - 3.1) / 0.5)
        ctext(d, 1000, 800, "子どもの一日には、白黒が最強", font(40),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= 3.7:
        b = ease((t - 3.7) / 0.5)
        ctext(d, 1000, 872, "シリーズ累計 約1億1900万台", font(42),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- メイン
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))

    spans = v2.spans_from_timing("yokoi-gunpei")

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

    sync("yg_tetsugaku", TG_P, draw_tetsugaku)
    sync("yg_gb", GB_P, draw_gb)
