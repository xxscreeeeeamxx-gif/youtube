#!/usr/bin/env python3
"""momofuku-v2（完全版）用のアニメクリップを生成する。

既存 gen_momofuku_extras.py の描画関数を流用し、フェーズ境界だけ
momofuku-v2 の timing.json 実測値に差し替える。加えて完全版専用の
新規アニメ（年号カード11枚・闇市の行列・売上グラフ・ご飯系/健康系カード）を描く。

フェーズ境界は timing.json のカット実測に同期（コメントの秒数）。
実行: PYTHONPATH=. python3 scripts/gen_momofuku_v2_extras.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.gen_momofuku_extras as m  # noqa: E402
from scripts.gen_momofuku_extras import (  # noqa: E402
    W, H, INK, ACCENT, AMBER, GREEN, RED, GRAY, NOODLE, BROTH, CUPW,
    ctext, ease, font, render, _caption, _cup, _men_cross, _timer,
)
from PIL import ImageDraw  # noqa: E402

# ---------------------------------------------------------------- 年号カード
# 完全版の年表ドット（誕生→起業→どん底→発明→カップ→宇宙）
m.ERAS = [("1910", "誕生"), ("1932", "起業"), ("1948", "どん底"),
          ("1958", "チキンラーメン"), ("1971", "カップヌードル"), ("2005", "宇宙")]

CARDS = [
    # (名前, ドット位置, 年, タイトル, サブ)
    ("era_v1910", 0, "1910", "布問屋の孫", "台湾・嘉義に生まれる"),
    ("era_v1932", 1, "1932", "22歳の起業", "台北・東洋莫大小"),
    ("era_v1941", 2, "戦時中", "時代が暗転する", ""),
    ("era_v1945", 2, "1945", "焼け跡の行列", "大阪・闇市"),
    ("era_v1948", 2, "1948", "一度目のゼロ", "収監・財産没収"),
    ("era_v1957", 2, "1957", "すべてを失う", "二度目のゼロ・47歳"),
    ("era_v1958a", 3, "1958", "再出発", "裏庭の研究小屋"),
    ("era_v1958", 3, "1958", "チキンラーメン誕生", "8月25日発売・35円"),
    ("era_v1966", 3, "1966", "どんぶりのない国へ", "単身、アメリカ"),
    ("era_v1971", 4, "1971", "カップヌードル誕生", "9月18日発売・100円"),
    ("era_v1972", 4, "1972", "雪の中継", ""),
]

# ---------------------------------------------------------------- 闇市の行列
# 境界(実測): [0, 3.43, 6.58, 9.59] / DUR 13.0
Q_P = [0.0, 3.43, 6.58, 9.59]
Q_DUR = 13.0


def _stall(d, sx, sy):
    """屋台のシルエット（のれんと提灯）。"""
    d.rectangle([sx, sy, sx + 420, sy + 300], fill=(56, 46, 40))
    d.polygon([(sx - 26, sy), (sx + 446, sy), (sx + 410, sy - 90), (sx + 10, sy - 90)],
              fill=(78, 62, 48))
    for i in range(3):
        d.rectangle([sx + 40 + i * 130, sy + 10, sx + 140 + i * 130, sy + 140],
                    fill=(150, 60, 54))
    for lx in (sx + 40, sx + 380):
        d.ellipse([lx - 28, sy - 66, lx + 28, sy], fill=(240, 160, 76))


def _person(d, px, py, s=1.0, col=(228, 230, 236)):
    """白シルエットの人（頭+胴）。"""
    r = int(26 * s)
    d.ellipse([px - r, py - int(120 * s), px + r, py - int(120 * s) + 2 * r], fill=col)
    d.rounded_rectangle([px - int(30 * s), py - int(66 * s), px + int(30 * s), py],
                        radius=int(20 * s), fill=col)


def draw_gyoretsu(d, t):
    d.rectangle([0, 0, W, H], fill=(22, 24, 36))
    d.rectangle([0, 760, W, H], fill=(34, 30, 32))
    _stall(d, 180, 460)
    # 提灯の光
    if t < Q_P[1]:
        _caption(d, "闇市のラーメン屋台", GRAY)
        n = int(ease(t / 2.6) * 8)
    elif t < Q_P[2]:
        _caption(d, "行列は、途切れない")
        n = 8 + int(ease((t - Q_P[1]) / 2.0) * 6)
    elif t < Q_P[3]:
        _caption(d, "一杯のために、何時間も")
        n = 14
    else:
        _caption(d, "この行列を、百福は忘れなかった", AMBER)
        n = 14
    # 行列（屋台の右へ伸びる）
    for i in range(n):
        px = 700 + i * 88
        py = 760 + (i % 3) * 8
        sway = 4 * math.sin(t * 1.6 + i)
        _person(d, px + sway, py, s=1.0 - i * 0.02)
    # 湯気（P2以降、丼から）
    if t >= Q_P[2]:
        for k in range(2):
            pts = []
            for j in range(9):
                yy = 420 - j * 18
                pts.append((320 + k * 120 + 16 * math.sin(t * 1.8 + j * 0.6 + k), yy))
            d.line(pts, fill=(235, 240, 248, 150), width=8)


# ---------------------------------------------------------------- 売上グラフ
# 境界(実測): [0, 4.21, 7.6] / DUR 11.0
G2_P = [0.0, 4.21, 7.6]
G2_DUR = 11.0


def draw_graph(d, t):
    d.rectangle([0, 0, W, H], fill=(10, 14, 24))
    _caption(d, "チキンラーメンの売れ行き")
    x0, y0, x1, y1 = 420, 260, 1500, 860
    d.line([x0, y1, x1, y1], fill=GRAY, width=6)
    d.line([x0, y1, x0, y0], fill=GRAY, width=6)
    # 12本の月次バーが次々伸びる
    total_p = ease(min(t / (G2_P[2] - 0.4), 1.0))
    for i in range(12):
        bp = max(0.0, min(1.0, total_p * 12 - i))
        bh = (30 + (i / 11) ** 2 * 460) * ease(bp)
        bx = x0 + 40 + i * 86
        d.rounded_rectangle([bx, y1 - bh, bx + 56, y1], radius=10,
                            fill=BROTH if i < 11 else AMBER)
    if t >= G2_P[1]:
        b = ease((t - G2_P[1]) / 0.8)
        val = int(1300 * min((t - G2_P[1]) / 2.2, 1.0))
        col = tuple(int(AMBER[i] * b) for i in range(3))
        ctext(d, 960, 350, f"年間 {val}万食", font(110), col)
    if t >= G2_P[2]:
        b = ease((t - G2_P[2]) / 0.6)
        ctext(d, 960, 500, "※発売翌年・当時の記録より",
              font(40), tuple(int(GRAY[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 商品カード共通
def _product_card(d, cx, cy, w, h, band_col, title, sub, year, reveal=1.0):
    a = ease(reveal)
    if a <= 0:
        return
    yoff = int((1 - a) * 60)
    x0, y0 = cx - w // 2, cy - h // 2 + yoff
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=24,
                        fill=(250, 250, 248), outline=(70, 76, 90), width=4)
    d.rectangle([x0, y0 + h * 0.30, x0 + w, y0 + h * 0.46], fill=band_col)
    f1 = font(46)
    d.text((cx - d.textlength(title, font=f1) / 2, y0 + h * 0.32), title,
           font=f1, fill=(255, 255, 255))
    f2 = font(34)
    d.text((cx - d.textlength(sub, font=f2) / 2, y0 + h * 0.56), sub,
           font=f2, fill=(60, 64, 76))
    f3 = font(50)
    d.text((cx - d.textlength(year, font=f3) / 2, y0 + h * 0.72), year,
           font=f3, fill=(40, 44, 56))


# ---------------------------------------------------------------- ご飯系カード
# 境界(実測): [0, 3.28, 6.22, 9.2] / DUR 12.2
GH_P = [0.0, 3.28, 6.22, 9.2]
GH_DUR = 12.2


def draw_gohan(d, t):
    d.rectangle([0, 0, W, H], fill=(12, 16, 26))
    if t < GH_P[1]:
        _caption(d, "麺の次は、ご飯")
        _product_card(d, 960, 560, 560, 420, (196, 90, 60),
                      "カップカレーライス", "お湯で作るカレーライス", "2013年",
                      reveal=(t - 0.4) / 0.8)
    elif t < GH_P[2]:
        _caption(d, "名前を変えて、大ヒット")
        _product_card(d, 960, 560, 560, 420, (222, 120, 40),
                      "カレーメシ", "混ぜれば本格カレー", "2014年",
                      reveal=(t - GH_P[1]) / 0.8)
    else:
        _caption(d, "ご飯系は、定番になった")
        _product_card(d, 620, 560, 480, 380, (196, 90, 60),
                      "カップカレーライス", "はじまりの一杯", "2013年")
        _product_card(d, 1300, 560, 480, 380, (222, 120, 40),
                      "カレーメシ", "シリーズ展開へ", "2014年",
                      reveal=(t - GH_P[2]) / 0.8)


# ---------------------------------------------------------------- 健康系カード
# 境界(実測): [0, 4.12, 7.9, 11.99] / DUR 14.8
K_P = [0.0, 4.12, 7.9, 11.99]
K_DUR = 14.8


def draw_kenko(d, t):
    d.rectangle([0, 0, W, H], fill=(12, 16, 26))
    if t < K_P[1]:
        _caption(d, "最近の主戦場は、健康")
        _product_card(d, 960, 560, 620, 420, (60, 130, 110),
                      "カップヌードルPRO", "高たんぱく・低糖質", "2021年",
                      reveal=(t - 0.4) / 0.8)
    elif t < K_P[2]:
        _caption(d, "栄養バランスを、一食に")
        _product_card(d, 960, 560, 620, 420, (70, 90, 150),
                      "完全メシ", "栄養とおいしさの両立", "2022年",
                      reveal=(t - K_P[1]) / 0.8)
    else:
        _caption(d, "おいしい×体にいい、へ")
        _product_card(d, 620, 560, 500, 380, (60, 130, 110),
                      "カップヌードルPRO", "高たんぱく・低糖質", "2021年")
        _product_card(d, 1300, 560, 500, 380, (70, 90, 150),
                      "完全メシ", "栄養とおいしさの両立", "2022年",
                      reveal=(t - K_P[2]) / 0.8)


# ---------------------------------------------------------------- 3分タイマー
# 境界(実測): [0, 3.85, 8.17] / DUR 11.5
T2_P = [0.0, 3.85, 8.17]
T2_DUR = 11.5
T2_END = 10.2


def draw_timer3_v2(d, t):
    cx = W / 2 + 60
    caps = ["今日は、ちゃんと3分待つ", "96年の人生が詰まった3分",
            "待った分だけ、おいしい"]
    ph = 0 if t < T2_P[1] else (1 if t < T2_P[2] else 2)
    _caption(d, caps[ph])
    remain = max(180.0 * (1 - t / T2_END), 0.0)
    _timer(d, cx, 560, 230, remain)
    gx0, gx1, gy = cx - 160, cx + 160, 880
    d.rounded_rectangle([gx0, gy - 20, gx1, gy + 20], radius=20,
                        outline=GRAY, width=4)
    pr = 1 - remain / 180.0
    d.rounded_rectangle([gx0 + 5, gy - 15, gx0 + 5 + (gx1 - gx0 - 10) * pr, gy + 15],
                        radius=15, fill=BROTH)
    ctext(d, cx, gy - 76, "麺のもどり", font(38), GRAY)
    if remain <= 0:
        for i in range(3):
            phw = t * 1.8 + i * 2.1
            pts = []
            for j in range(10):
                yy = 300 - j * 14
                pts.append((cx - 70 + i * 70 + 20 * math.sin(phw + j * 0.5), yy))
            d.line(pts, fill=(230, 236, 246, 180), width=9)


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    # 年号カード（DUR 6.5s固定・カット側で切り出される）
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))
    # 実測フェーズ差し替えの再生成
    m.F_P = [0.0, 3.06, 5.39, 7.38, 10.65, 14.47, 16.87]
    render("mf2_fail", 20.1, m.draw_fail)
    m.A_P = [0.0, 3.27, 7.26, 10.92]
    render("mf2_ana", 15.9, m.draw_ana)
    m.G_P = [0.0, 3.45, 7.55]
    render("mf2_gyakusama", 13.2, m.draw_gyakusama)
    m.S_P = [0.0, 4.38, 6.84, 9.11, 12.92]
    render("mf2_asama", 17.7, m.draw_asama)
    # 完全版の新規アニメ
    render("mf2_gyoretsu", Q_DUR, draw_gyoretsu)
    render("mf2_graph", G2_DUR, draw_graph)
    render("mf2_gohan", GH_DUR, draw_gohan)
    render("mf2_kenko", K_DUR, draw_kenko)
    render("mf2_timer3", T2_DUR, draw_timer3_v2)
