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

# ---------------------------------------------------------------- 境界の自動計測
def spans_from_timing(slug="momofuku-v2"):
    """timing.json と script.yaml から各クリップの (フェーズ境界, DUR) を実測で返す。

    台本のセリフを直したら voice → 本スクリプト再実行だけで同期が取り直される。
    """
    import json
    import yaml
    root = Path(__file__).resolve().parent.parent / "projects" / slug
    t = json.loads((root / "audio" / "timing.json").read_text())
    s = yaml.safe_load((root / "script.yaml").read_text())
    cuts = [c for sc in s["scenes"] for c in sc["cuts"]]
    out = {}
    for i, (c, ti) in enumerate(zip(cuts, t)):
        v = c.get("video") or ""
        if "/mf" not in v:
            continue
        span = c.get("video_span", 1)
        seg = t[i:i + span]
        bounds, acc = [], 0.0
        for x in seg:
            bounds.append(round(acc, 2))
            acc += x["total_dur"]
        out[Path(v).stem] = (bounds, round(acc + 1.0, 1))
    return out


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
    # 行列がフェーズごとに伸びる（見出しテロップは出さない・セリフが担う）
    if t < Q_P[1]:
        n = int(ease(t / 2.6) * 8)
    elif t < Q_P[2]:
        n = 8 + int(ease((t - Q_P[1]) / 2.0) * 6)
    else:
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


# ---------------------------------------------------------------- 5つの目標
J_P = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0]
J_DUR = 16.0
JOKEN = ["うまいこと", "日持ちすること", "手間いらずなこと", "安いこと", "安全なこと"]


def draw_joken(d, t):
    d.rectangle([0, 0, W, H], fill=(10, 14, 24))
    ctext(d, W / 2, 90, "百福の5つの目標", font(64), INK)
    done = t >= J_P[6] if len(J_P) > 6 else False
    for i, item in enumerate(JOKEN):
        bi = min(i + 1, len(J_P) - 1)
        if t < J_P[bi]:
            continue
        a = ease((t - J_P[bi]) / 0.5)
        y0 = 210 + i * 150
        col = AMBER if done else BROTH
        d.rounded_rectangle([560, y0, 560 + int(800 * a), y0 + 116], radius=20,
                            fill=(30, 38, 54), outline=col, width=4)
        if a > 0.6:
            num = ["一", "二", "三", "四", "五"][i]
            d.ellipse([590, y0 + 24, 658, y0 + 92], fill=col)
            f = font(44)
            d.text((624 - d.textlength(num, font=f) / 2, y0 + 32), num,
                   font=f, fill=(20, 24, 34))
            f2 = font(52)
            d.text((700, y0 + 28), item, font=f2, fill=INK)


# ---------------------------------------------------------------- 失敗の物語3連
# 各フェーズは spans_from_timing で実測同期
F1_P = [0.0, 2.0, 4.0, 6.0]
F2_P = [0.0, 2.0, 4.0, 6.0]
F3_P = [0.0, 2.0, 4.0]


def draw_fail1(d, t):
    """スープ練り込み: こねる→自信→ぼろぼろに切れる。"""
    g = (200, 204, 214)
    d.rectangle([0, 0, W, H], fill=(16, 18, 28))
    if t < F1_P[3]:
        _caption(d, "作戦1　スープを麺に練り込む", g)
        m._noodle_block(d, W / 2, 560, col=NOODLE)
        # スープの粉を振り込む手つき（渦）
        ang = t * 2.4
        for i in range(3):
            x = W / 2 + 230 * math.cos(ang + i * 2.1)
            y = 560 + 80 * math.sin(ang + i * 2.1)
            d.ellipse([x - 22, y - 22, x + 22, y + 22],
                      outline=(214, 150, 80), width=6)
        if t >= F1_P[2]:
            b = ease((t - F1_P[2]) / 0.6)
            ctext(d, W / 2, 850, "うまくいく気しかしない",
                  font(46), tuple(int(GRAY[i] * b) for i in range(3)))
    else:
        lt = t - F1_P[3]
        _caption(d, "→ 麺が、ぼろぼろに切れた", g)
        m._noodle_block(d, W / 2, 560, col=(150, 154, 164), broken=True)
        m._batsu(d, W / 2, 560, 90, lt / 0.5)


def draw_fail2(d, t):
    """天日干し: 干す→三日三晩→硬い。"""
    g = (200, 204, 214)
    d.rectangle([0, 0, W, H], fill=(16, 18, 28))
    if t < F2_P[3]:
        _caption(d, "作戦2　天日で干す", g)
        # 太陽が弧を描く（時間経過）
        prog = min(t / max(F2_P[3], 0.1), 1.0)
        sx = 400 + prog * 1100
        sy = 360 - math.sin(prog * math.pi) * 160
        d.ellipse([sx - 70, sy - 70, sx + 70, sy + 70], fill=(244, 214, 120))
        for i in range(8):
            a = i * math.pi / 4 + t * 0.4
            d.line([sx + 92 * math.cos(a), sy + 92 * math.sin(a),
                    sx + 126 * math.cos(a), sy + 126 * math.sin(a)],
                   fill=(244, 214, 120), width=7)
        m._noodle_block(d, W / 2, 700, col=NOODLE)
        if t >= F2_P[2]:
            b = ease((t - F2_P[2]) / 0.6)
            ctext(d, W / 2, 880, "三日三晩",
                  font(54), tuple(int(GRAY[i] * b) for i in range(3)))
    else:
        lt = t - F2_P[3]
        _caption(d, "→ 乾いても、お湯で戻らない", g)
        m._noodle_block(d, W / 2 - 200, 560, col=(150, 154, 164))
        cx, cy, r = W / 2 + 240, 560, 130
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=g, width=10)
        a = -math.pi / 2 + min(lt / 2.2, 1.0) * 2 * math.pi
        d.line([cx, cy, cx + (r - 34) * math.cos(a), cy + (r - 34) * math.sin(a)],
               fill=g, width=9)
        ctext(d, cx, cy + r + 30, "10分…", font(52), g)
        m._batsu(d, W / 2, 560, 90, (lt - 1.4) / 0.5 if lt > 1.4 else 0)


def draw_fail3(d, t):
    """蒸し+干し: 期待→カビ→3連敗。"""
    g = (200, 204, 214)
    d.rectangle([0, 0, W, H], fill=(16, 18, 28))
    if t < F3_P[1]:
        _caption(d, "作戦3　蒸してから干す", g)
        m._noodle_block(d, W / 2, 560, col=NOODLE)
        for k in range(3):
            pts = []
            for j in range(8):
                yy = 440 - j * 18
                pts.append((W / 2 - 90 + k * 90 + 14 * math.sin(t * 2 + j * 0.7 + k), yy))
            d.line(pts, fill=(235, 240, 248, 140), width=8)
    elif t < F3_P[2]:
        lt = t - F3_P[1]
        _caption(d, "→ 保存中にカビ", g)
        m._noodle_block(d, W / 2, 560, col=(150, 154, 164))
        import random
        rnd = random.Random(3)
        n = int(min(lt / 1.0, 1.0) * 26)
        for i in range(n):
            x = W / 2 - 170 + rnd.random() * 340
            y = 480 + rnd.random() * 160
            r = 8 + rnd.random() * 14
            d.ellipse([x - r, y - r, x + r, y + r], fill=(96, 128, 96))
        m._batsu(d, W / 2, 560, 100, (lt - 1.0) / 0.5 if lt > 1.0 else 0)
    else:
        lt = t - F3_P[2]
        _caption(d, "ここまで、3連敗", g)
        for k in range(3):
            b = ease((lt - k * 0.3) / 0.4) if lt > k * 0.3 else 0
            if b > 0:
                m._batsu(d, 720 + k * 240, 540, int(90 * b), 1.0)


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    # 年号カード（DUR 6.5s固定・カット側で切り出される）
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))

    # フェーズ同期アニメ: 境界は timing.json から自動計測
    spans = spans_from_timing()

    def bounds(name, default):
        return spans.get(name, (default, default[-1] + 4.0))

    def sync_render(name, const_setter, draw):
        if name not in spans:
            print(f"スキップ（台本に無い）: {name}")
            return
        b, dur = spans[name]
        const_setter(b)
        render(name, dur, draw)

    sync_render("mf2_gyoretsu", lambda b: globals().update(Q_P=b), draw_gyoretsu)
    sync_render("mf2_ana", lambda b: setattr(m, "A_P", b), m.draw_ana)
    sync_render("mf2_gyakusama", lambda b: setattr(m, "G_P", b), m.draw_gyakusama)
    sync_render("mf2_asama", lambda b: setattr(m, "S_P", b), m.draw_asama)
    sync_render("mf2_graph", lambda b: globals().update(G2_P=b), draw_graph)
    sync_render("mf2_gohan", lambda b: globals().update(GH_P=b), draw_gohan)
    sync_render("mf2_kenko", lambda b: globals().update(K_P=b), draw_kenko)
    sync_render("mf3_joken", lambda b: globals().update(J_P=b), draw_joken)
    sync_render("mf3_fail1", lambda b: globals().update(F1_P=b), draw_fail1)
    sync_render("mf3_fail2", lambda b: globals().update(F2_P=b), draw_fail2)
    sync_render("mf3_fail3", lambda b: globals().update(F3_P=b), draw_fail3)

    def set_timer(b):
        globals().update(T2_P=b)
        globals().update(T2_END=spans["mf2_timer3"][1] - 1.4)
    sync_render("mf2_timer3", set_timer, draw_timer3_v2)
