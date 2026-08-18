#!/usr/bin/env python3
"""クオーツ時計の誕生（quartz-astron）用の年号カード4枚と図解アニメ3本。

クリップ名は qa_ 名義。フェーズ境界は timing.json 実測（spans_from_timing）。
図解は単独シーンではなく会話に重ねるので、video_span ぶんの尺に同期させる。
実行: PYTHONPATH=. python3 scripts/gen_qz_extras.py（voice 後）
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.gen_momofuku_extras as m  # noqa: E402
from scripts.gen_momofuku_extras import (  # noqa: E402
    W, H, AMBER, GRAY, GREEN, RED, ctext, ease, font, render, _caption,
)
import scripts.gen_momofuku_v2_extras as v2  # noqa: E402

INK = (28, 32, 44)
PAPER = (244, 246, 250)
STEEL = (120, 126, 140)
GOLD = (214, 176, 70)

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1959", "水晶に着手"), ("1964", "144位"), ("1967", "3位"), ("1969", "世界初")]
CARDS = [
    ("qa_era1964", 1, "1964", "スイス・ヌーシャテル", "初参加、諏訪は144位"),
    ("qa_era1959", 0, "1959", "長野県諏訪", "山あいの工場が水晶に手を出す"),
    ("qa_era1964b", 1, "1964", "東京オリンピック", "持ち運べる水晶時計ができた"),
    ("qa_era1967", 2, "1967", "ふたたびヌーシャテル", "3年で144位から3位へ"),
    ("qa_era1969", 3, "1969", "12月25日・銀座", "世界初のクオーツ腕時計が並ぶ"),
]


# ---------------------------------------------------------------- 図解
def kabe(bounds, dur):
    """立ちはだかる2つの壁（体積30万分の1・電力1000万分の1）。"""
    b = bounds

    def draw(d, t):
        ctext(d, 860, 120, "腕に載せるための壁", font(70), INK)
        # ① 大きさ
        if t >= b[0]:
            k = ease((t - b[0]) / 0.8)
            d.rounded_rectangle([500, 240, 660, 540], radius=16,
                                fill=(int(STEEL[0] * k), int(STEEL[1] * k), int(STEEL[2] * k)))
            ctext(d, 580, 580, "いまの水晶時計", font(52), (*INK, int(255 * k)))
        if t >= b[1]:
            k = ease((t - b[1]) / 0.8)
            d.rounded_rectangle([800, 500, 848, 540], radius=6,
                                fill=(int(GOLD[0] * k), int(GOLD[1] * k), int(GOLD[2] * k)))
            ctext(d, 880, 580, "腕時計", font(52), (*INK, int(255 * k)))
            d.line([(680, 400), (780, 500)], fill=(*RED, int(255 * k)), width=10)
        if t >= b[2]:
            k = ease((t - b[2]) / 0.7)
            ctext(d, 860, 640, "体積を30万分の1に", font(62), (*RED, int(255 * k)))
        # ② 電気
        if t >= b[3]:
            k = ease((t - b[3]) / 0.8)
            ctext(d, 1060, 280, "100W", font(80), (*GRAY, int(255 * k)))
        if t >= b[4]:
            k = ease((t - b[4]) / 0.8)
            ctext(d, 1060, 370, "↓", font(70), (*RED, int(255 * k)))
            ctext(d, 1060, 450, "10μW", font(80), (*GREEN, int(255 * k)))
        if t >= b[5] if len(b) > 5 else False:
            k = ease((t - b[5]) / 0.7)
            ctext(d, 860, 730, "電気を1000万分の1に", font(62), (*RED, int(255 * k)))
    return draw


def shikumi(bounds, dur):
    """水晶がふるえる→半分にしていく→1秒→針を1度動かす。"""
    b = bounds

    def draw(d, t):
        ctext(d, 860, 120, "水晶が時を刻むまで", font(70), INK)
        # 音叉型水晶
        if t >= b[0]:
            k = ease((t - b[0]) / 0.8)
            col = (int(180 * k) + 40, int(200 * k) + 40, int(230 * k) + 40)
            d.rounded_rectangle([780, 230, 820, 420], radius=14, fill=col)
            d.rounded_rectangle([870, 230, 910, 420], radius=14, fill=col)
            d.rounded_rectangle([780, 400, 910, 450], radius=14, fill=col)
            sway = math.sin(t * 14) * 10 * k
            d.line([(800, 230), (800 + sway, 200)], fill=(*GREEN, int(255 * k)), width=8)
            d.line([(890, 230), (890 - sway, 200)], fill=(*GREEN, int(255 * k)), width=8)
            ctext(d, 845, 490, "音叉型の水晶", font(52), (*INK, int(255 * k)))
        if t >= b[1]:
            k = ease((t - b[1]) / 0.7)
            ctext(d, 845, 545, "8192回／秒", font(64), (*AMBER, int(255 * k)))
        # 分周
        if t >= b[2]:
            k = ease((t - b[2]) / 0.9)
            for i in range(7):
                x = 760 + i * 74
                a = int(255 * min(1.0, max(0.0, k * 7 - i)))
                if a <= 0:
                    continue
                d.rounded_rectangle([x, 640, x + 60, 700], radius=10, fill=(*STEEL, a))
                d.text((x + 14, 656), "÷2", font=font(34), fill=(*PAPER, a))
        if t >= b[3]:
            k = ease((t - b[3]) / 0.7)
            ctext(d, 860, 750, "半分にするだけ＝電気を食わない", font(52), (*INK, int(255 * k)))
        # 1秒
        if t >= b[4]:
            k = ease((t - b[4]) / 0.7)
            ctext(d, 1180, 300, "1秒", font(96), (*GREEN, int(255 * k)))
        # 針を1度
        if t >= b[5] if len(b) > 5 else False:
            k = ease((t - b[5]) / 0.7)
            cx, cy, r = 1180, 470, 90
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(*INK, int(255 * k)), width=8)
            step = int(t * 1) % 60
            a = math.radians(step * 6 - 90)
            d.line([(cx, cy), (cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.8)],
                   fill=(*RED, int(255 * k)), width=8)
    return draw


def shock(bounds, dur):
    """スイス時計産業の推移（企業数・就業者数）。"""
    b = bounds

    def draw(d, t):
        ctext(d, 860, 120, "スイス時計産業に起きたこと", font(64), INK)
        base_y, top_y = 640, 250
        if t >= b[0]:
            k = ease((t - b[0]) / 0.8)
            h = int((base_y - top_y) * k)
            d.rectangle([560, base_y - h, 700, base_y], fill=(90, 130, 190))
            ctext(d, 630, base_y + 42, "1970年", font(54), (*INK, int(255 * k)))
            ctext(d, 630, base_y - h - 60, "1600社超", font(56), (*INK, int(255 * k)))
        if t >= b[1]:
            k = ease((t - b[1]) / 0.8)
            h = int((base_y - top_y) * 0.37 * k)
            d.rectangle([900, base_y - h, 1040, base_y], fill=(200, 90, 80))
            ctext(d, 970, base_y + 42, "80年代", font(54), (*INK, int(255 * k)))
            ctext(d, 970, base_y - h - 60, "600社割れ", font(56), (*RED, int(255 * k)))
        if t >= b[2]:
            k = ease((t - b[2]) / 0.7)
            ctext(d, 810, base_y + 118, "働く人 9万人 → 3万3千人", font(50), (*INK, int(255 * k)))
        if t >= b[3]:
            k = ease((t - b[3]) / 0.7)
            ctext(d, 810, base_y + 186, "輸出額はピークの半分に", font(50), (*INK, int(255 * k)))
    return draw


CLIPS = {"qa_kabe": kabe, "qa_shikumi": shikumi, "qa_shock": shock}

if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))
    # 単独シーンなので1カット尺しか再生されない。全要素を4秒以内に詰める
    FIXED = {
        "qa_kabe": ([0.2, 0.9, 1.7, 2.4, 3.1, 3.8], 7.5),
        "qa_shikumi": ([0.2, 0.8, 1.4, 2.1, 2.7, 3.3, 3.9], 5.8),
        "qa_shock": ([0.2, 1.1, 2.1, 3.0], 5.8),
    }
    for name, fn in CLIPS.items():
        bounds, dur = FIXED[name]
        render(name, dur, fn(bounds, dur))
