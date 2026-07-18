#!/usr/bin/env python3
"""kaiten-sushi（回転寿司再現ドラマ）用の年号カード5枚+図解アニメ8本を生成する。

クリップ名は ks_/era_k 名義。フェーズ境界は timing.json 実測（spans_from_timing）。
実行: PYTHONPATH=. python3 scripts/gen_ks_extras.py（voice 後）
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
WOOD = (150, 116, 74)

# ---------------------------------------------------------------- 年号カード
m.ERAS = [("1913", "誕生"), ("1947", "大阪"), ("1958", "一号店"),
          ("1970", "万博"), ("1978", "解禁"), ("2021", "機械遺産")]

CARDS = [
    ("era_k1913", 0, "1913", "海の町に生まれる", "愛媛"),
    ("era_k1947", 1, "1947", "大阪へ", "34歳の再出発"),
    ("era_k1958", 2, "1958", "寿司が、回った", "布施・一号店"),
    ("era_k1970", 3, "1970", "万博の行列", "全国区へ"),
    ("era_k1978", 4, "1978", "回転寿司、解禁", "権利が切れた日"),
]


# ---------------------------------------------------------------- 共通部品
def _plate(d, cx, cy, s=1.0, neta=(236, 120, 100)):
    d.ellipse([cx - 60 * s, cy - 16 * s, cx + 60 * s, cy + 18 * s], fill=PAPER,
              outline=(170, 176, 186), width=3)
    for k in (-26, 12):
        d.rounded_rectangle([cx + (k - 14) * s, cy - 16 * s,
                             cx + (k + 18) * s, cy - 4 * s],
                            radius=int(5 * s), fill=(244, 240, 230))
        d.rounded_rectangle([cx + (k - 16) * s, cy - 24 * s,
                             cx + (k + 20) * s, cy - 12 * s],
                            radius=int(5 * s), fill=neta)


def _bottle(d, cx, cy, s=1.0):
    d.rounded_rectangle([cx - 22 * s, cy - 50 * s, cx + 22 * s, cy + 50 * s],
                        radius=int(8 * s), fill=(150, 96, 40))
    d.rectangle([cx - 10 * s, cy - 80 * s, cx + 10 * s, cy - 44 * s],
                fill=(130, 82, 34))


def _belt(d, x0, y0, x1, h=64):
    d.rectangle([x0, y0, x1, y0 + h], fill=(72, 80, 92))
    d.line([x0, y0, x1, y0], fill=(52, 58, 68), width=5)
    d.line([x0, y0 + h, x1, y0 + h], fill=(52, 58, 68), width=5)


def _fan_plates(d, cx, cy, r_in, r_out, a0, a1, n, col=(150, 158, 170)):
    """扇形のウロコ板を弧に沿って並べる。"""
    for k in range(n):
        a = a0 + (a1 - a0) * k / max(1, n - 1)
        ar = math.radians(a)
        px = cx + (r_in + r_out) / 2 * math.cos(ar)
        py = cy + (r_in + r_out) / 2 * math.sin(ar)
        d.pieslice([px - 46, py - 46, px + 46, py + 46],
                   a - 210, a - 150, fill=col, outline=(96, 104, 116))


# ---------------------------------------------------------------- 1. ビール瓶の行進
BL_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_beerline(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    if t < BL_P[2]:
        _caption(d, "ベルトコンベアの上を、瓶が行進")
    else:
        _caption(d, "運んでいるのは、人ではない")
    _belt(d, 710, 560, 1240)
    off = int(t * 60) % 160
    for k in range(5):
        bx = 760 + k * 160 - off + 80
        if 710 <= bx <= 1230:
            if t < BL_P[2]:
                _bottle(d, bx, 500)
            else:
                _plate(d, bx, 530)
    if t >= BL_P[1]:
        b = ease((t - BL_P[1]) / 0.6)
        ctext(d, 960, 700, "人が運ばず、次々届く", font(48),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= BL_P[2]:
        b = ease((t - BL_P[2]) / 0.6)
        ctext(d, 1000, 780, "瓶を、皿に変えたら……？", font(48),
              tuple(int(BLUE[i] * b) for i in range(3)))
    if t >= BL_P[3]:
        b = ease((t - BL_P[3]) / 0.5)
        ctext(d, 1000, 880, "「これや！」", font(72),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 2. カーブの壁
CV_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_curve(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    if t < CV_P[1]:
        _caption(d, "直線は、うまくいく")
    elif t < CV_P[3]:
        _caption(d, "角で、皿が詰まる")
    else:
        _caption(d, "四角い板のままでは、曲がれない")
    # L字レーン（上面図）
    d.rectangle([760, 420, 1120, 500], fill=(72, 80, 92))
    d.rectangle([1040, 420, 1120, 820], fill=(72, 80, 92))
    d.rectangle([760, 420, 1120, 500], outline=(52, 58, 68), width=5)
    d.rectangle([1040, 500, 1120, 820], outline=(52, 58, 68), width=5)
    # 四角い板
    for k in range(4):
        bx = 800 + k * 90
        d.rectangle([bx, 432, bx + 74, 488], fill=(150, 158, 170),
                    outline=(96, 104, 116), width=3)
    if t >= CV_P[1]:
        # 角に皿が到達して詰まる
        p = min(1.0, (t - CV_P[1]) / 1.6)
        px = 800 + p * 280
        _plate(d, px, 460, s=0.8)
        if p >= 1.0:
            d.rectangle([1042, 432, 1116, 488], fill=(150, 158, 170),
                        outline=RED, width=5)
            d.line([1044, 434, 1114, 486], fill=RED, width=8)
            d.line([1114, 434, 1044, 486], fill=RED, width=8)
    if t >= CV_P[2]:
        b = ease((t - CV_P[2]) / 0.6)
        ctext(d, 950, 880, "板と板が、角で喧嘩する", font(46),
              tuple(int(RED[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 3. 扇のひらめき
FN_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_fan(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    if t < FN_P[1]:
        _caption(d, "トランプを、扇に広げると……")
        # 直線に並んだカード→扇
        p = ease(min(1.0, t / 2.0))
        for k in range(9):
            ang = (k - 4) * 16 * p
            ar = math.radians(ang - 90)
            cx = 1000 + 220 * p * math.cos(math.radians(ang + 90 - 180)) * 0
            px = 1000 + (k - 4) * (60 * (1 - p)) + 190 * p * math.sin(math.radians(ang))
            py = 560 - 150 * p * (math.cos(math.radians(ang)) - 1) * -1
            d.rounded_rectangle([px - 40, py - 120, px + 40, py + 20],
                                radius=10, fill=PAPER, outline=(120, 126, 140), width=3)
            d.ellipse([px - 12, py - 66, px + 12, py - 42], outline=RED, width=4)
        ctext(d, 1000, 800, "1枚1枚は四角。ぜんたいは曲線", font(46), AMBER)
        return
    if t < FN_P[3]:
        _caption(d, "板を扇形にして、うろこのように重ねる")
    else:
        _caption(d, "どの角も、なめらかに曲がる")
    # カーブレーンをウロコ板が流れる（上面図・四分円）
    cx, cy = 900, 760
    d.arc([cx - 360, cy - 360, cx + 360, cy + 360], -90, 0, fill=(72, 80, 92), width=90)
    off = (t * 20) % 12
    _fan_plates(d, cx, cy, 270, 350, -90 + off, 0 - 6 + off, 8)
    d.rectangle([cx - 4, cy - 405, 1240, cy - 315], fill=(72, 80, 92))
    for k in range(3):
        bx = cx + 60 + k * 130 + int(t * 30) % 130
        if bx < 1190:
            d.pieslice([bx - 46, cy - 406, bx + 46, cy - 314], -30, 30,
                       fill=(150, 158, 170), outline=(96, 104, 116))
    if t >= FN_P[2]:
        _plate(d, cx + 310 * math.cos(math.radians(-45)),
               cy + 310 * math.sin(math.radians(-45)), s=0.9)
    if t >= FN_P[3]:
        b = ease((t - FN_P[3]) / 0.6)
        ctext(d, 930, 210, "うろこ板は、いまも現役", font(44),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 4. 毎秒8センチ
SP_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_speed(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "ちょうどいい速さを探せ")
    rows = [("速すぎ", 300, 260, RED, "取れない・目が回る"),
            ("遅すぎ", 520, 18, GRAY, "じれったい・ネタが乾く"),
            ("毎秒8センチ", 740, 80, GREEN, "吟味できて、子どもも取れる")]
    for k, (label, y, speed, col, note) in enumerate(rows):
        if t < SP_P[k + 1] - 2.0:
            continue
        _belt(d, 760, y, 1240, 56)
        ctext(d, 830, y - 40, label, font(40), col)
        off = int(t * speed) % 240
        for i in range(3):
            bx = 800 + i * 240 - off + 120
            if 770 <= bx <= 1230:
                _plate(d, bx, y - 4, s=0.7)
        b = ease((t - (SP_P[k + 1] - 2.0)) / 0.6)
        ctext(d, 1000, y + 96, note, font(38),
              tuple(int(col[i] * b) for i in range(3)))
    if t >= SP_P[4]:
        b = ease((t - SP_P[4]) / 0.6)
        ctext(d, 1000, 930, "おいしさまで計算した速度", font(46),
              tuple(int(AMBER[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 5. 一号店レーン
LN_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_lane(d, t):
    d.rectangle([0, 0, W, H], fill=(26, 22, 18))
    _caption(d, "人工衛星廻る寿司", col=(255, 220, 120))
    # 楕円レーン上面図
    cx, cy = 1000, 560
    d.ellipse([cx - 290, cy - 170, cx + 290, cy + 170], outline=(96, 104, 116), width=64)
    d.ellipse([cx - 290, cy - 170, cx + 290, cy + 170], outline=WOOD, width=10)
    # 皿が周回
    n = 8
    for k in range(n):
        a = math.radians(t * 26 + k * 360 / n)
        px = cx + 258 * math.cos(a)
        py = cy + 138 * math.sin(a)
        _plate(d, px, py, s=0.72)
    # 客（白丸）
    if t >= LN_P[1]:
        cnt = min(10, int((t - LN_P[1]) / 0.5) + 1)
        for k in range(cnt):
            a = math.radians(k * 36 + 18)
            px = cx + 360 * math.cos(a)
            py = cy + 230 * math.sin(a)
            d.ellipse([px - 26, py - 26, px + 26, py + 26], fill=(228, 230, 236))
    if t >= LN_P[2]:
        b = ease((t - LN_P[2]) / 0.6)
        ctext(d, 1000, 850, "好きな皿を取って、あとで数える", font(46),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= LN_P[3]:
        b = ease((t - LN_P[3]) / 0.6)
        ctext(d, 1000, 930, "安い・早い・おもろい", font(50),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 6. 万博の行列
EX_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_expo(d, t):
    d.rectangle([0, 0, W, H], fill=(180, 214, 240))
    d.rectangle([0, 700, W, H], fill=(196, 190, 180))
    _caption(d, "万博会場・モノレール西口前", col=(40, 46, 60))
    # 店（幟）
    d.rectangle([730, 330, 950, 700], fill=(226, 216, 196))
    d.rectangle([730, 330, 950, 400], fill=(196, 60, 54))
    d.rectangle([712, 300, 742, 700], fill=(196, 60, 54))
    # 行列
    if t >= EX_P[1]:
        cnt = min(12, int((t - EX_P[1]) / 0.4) + 1)
        for k in range(cnt):
            px = 985 + k * 26 + (k % 3) * 4
            py = 640 + (k % 2) * 14
            col = (228, 230, 236) if k % 4 else (240, 200, 120)
            d.ellipse([px - 18, py - 70, px + 18, py - 34], fill=col)
            d.rounded_rectangle([px - 22, py - 40, px + 22, py + 10],
                                radius=14, fill=col)
    if t >= EX_P[2]:
        b = ease((t - EX_P[2]) / 0.6)
        ctext(d, 1000, 810, "連日の大行列・店じまいは午前0時", font(44),
              tuple(int((40, 46, 60)[i] * b) for i in range(3)))
    if t >= EX_P[3]:
        b = ease((t - EX_P[3]) / 0.6)
        ctext(d, 1000, 890, "世界中のお客が、回る寿司を初体験", font(44),
              tuple(int((150, 60, 50)[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 7. 全国へ
SD_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_spread(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    _caption(d, "1978年、権利が切れて")
    # 抽象日本列島（丸の連なり）
    blobs = [(870, 700, 90), (960, 620, 100), (1060, 540, 95),
             (1150, 450, 85), (1230, 370, 70), (800, 780, 60)]
    for (bx, by, r) in blobs:
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(46, 66, 56))
    # 店の灯りが増える
    import random
    rnd = random.Random(7)
    pts = [(rnd.randint(780, 1260), rnd.randint(380, 800)) for _ in range(26)]
    if t >= SD_P[1]:
        cnt = min(len(pts), int((t - SD_P[1]) / 0.28) + 1)
        for k in range(cnt):
            px, py = pts[k]
            r = 10 + (k % 3) * 3
            d.ellipse([px - r, py - r, px + r, py + r], fill=AMBER)
    if t >= SD_P[2]:
        b = ease((t - SD_P[2]) / 0.6)
        ctext(d, 1000, 880, "回転寿司の看板が、全国へ", font(50),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- 8. 現代の進化
NW_P = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0]


def draw_now(d, t):
    d.rectangle([0, 0, W, H], fill=DARKBG)
    if t < NW_P[2]:
        _caption(d, "現代の回転寿司")
    else:
        _caption(d, "足元の板は、60年前のまま")
    # タッチパネル
    d.rounded_rectangle([760, 300, 1000, 470], radius=12, fill=(50, 56, 70))
    d.rectangle([780, 320, 980, 430], fill=(120, 200, 220))
    for j in range(3):
        d.line([796, 346 + j * 30, 964, 346 + j * 30], fill=PAPER, width=7)
    ctext(d, 880, 505, "タッチパネル注文", font(34), GRAY)
    # 特急レーン
    if t >= NW_P[1]:
        _belt(d, 1040, 330, 1300, 44)
        p = ((t - NW_P[1]) * 300) % 300
        px = 1060 + p
        if px < 1280:
            _plate(d, px, 322, s=0.7)
        ctext(d, 1170, 410, "特急レーンが直送", font(34), GRAY)
    # 下段: うろこ板レーン（不変）
    _belt(d, 740, 660, 1300, 70)
    for k in range(6):
        bx = 780 + k * 100 + int(t * 30) % 100
        if bx < 1280:
            d.pieslice([bx - 48, 656, bx + 48, 736], -35, 35,
                       fill=(150, 158, 170), outline=(96, 104, 116))
    if t >= NW_P[2]:
        b = ease((t - NW_P[2]) / 0.6)
        ctext(d, 1000, 790, "うろこ板は、開発当時とほぼ同じ形", font(44),
              tuple(int(AMBER[i] * b) for i in range(3)))
    if t >= NW_P[3]:
        b = ease((t - NW_P[3]) / 0.6)
        ctext(d, 1000, 880, "2021年、機械遺産に認定", font(50),
              tuple(int(GREEN[i] * b) for i in range(3)))


# ---------------------------------------------------------------- メイン
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))

    spans = v2.spans_from_timing("kaiten-sushi")

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

    sync("ks_beerline", BL_P, draw_beerline)
    sync("ks_curve", CV_P, draw_curve)
    sync("ks_fan", FN_P, draw_fan)
    sync("ks_speed", SP_P, draw_speed)
    sync("ks_lane", LN_P, draw_lane)
    sync("ks_expo", EX_P, draw_expo)
    sync("ks_spread", SD_P, draw_spread)
    sync("ks_now", NW_P, draw_now)
