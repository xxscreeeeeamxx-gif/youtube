#!/usr/bin/env python3
"""東京タワー・内藤多仲回（46_東京タワーの誕生 / slug=naito-tower）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。

YKK回（gen_ykk_bgs.py）と同じ方針:
- 場所は性質ごとに束ねる。時間帯の差は BGM と表情で出す
- 年号カードは1つの関数で量産する
- gen_drama_bgs.py 本体は触らない（既存背景を再生成しないため）

実行: PYTHONPATH=. python scripts/gen_naito_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, glow, hanging_bulb, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)

TOWER_RED = (214, 92, 52)
TOWER_WHITE = (236, 232, 224)


def _d(img):
    return ImageDraw.Draw(img)


def _glow(img, cx, cy, r, color, alpha=110):
    """glow() は RGBA に合成するので、変換した結果を貼り戻す必要がある。"""
    rgba = img.convert("RGBA")
    glow(rgba, cx, cy, r, color, alpha)
    img.paste(rgba.convert("RGB"), (0, 0))


def _window(d, x0, y0, x1, y1, sky=(150, 186, 214), frame=(70, 62, 56)):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


def _lattice_tower(d, cx, y_base, y_top, half_base, half_top=6, built=1.0,
                   bands=True, width=6, legs_col=None):
    """トラスの塔。built<1 なら途中まで（建設中）。

    脚は下が広く上がすぼまる。一定間隔で水平材とたすき掛けの斜材を入れ、
    bands=True なら東京タワーの赤白の塗り分けにする。
    """
    n = 18
    y_end = y_base - (y_base - y_top) * built
    for i in range(n):
        ya = y_base - (y_base - y_top) * i / n
        yb = y_base - (y_base - y_top) * (i + 1) / n
        if ya <= y_end:
            break
        yb = max(yb, y_end)
        ta = (y_base - ya) / (y_base - y_top)
        tb = (y_base - yb) / (y_base - y_top)
        # 下ほど広がる曲線（東京タワーの裾の広がり）
        wa = half_top + (half_base - half_top) * (1 - ta) ** 1.8
        wb = half_top + (half_base - half_top) * (1 - tb) ** 1.8
        col = legs_col or ((TOWER_RED if (i // 2) % 2 == 0 else TOWER_WHITE)
                           if bands else (96, 96, 100))
        w = max(2, int(width * (1 - ta * 0.6)))
        d.line([(cx - wa, ya), (cx - wb, yb)], fill=col, width=w)
        d.line([(cx + wa, ya), (cx + wb, yb)], fill=col, width=w)
        d.line([(cx - wb, yb), (cx + wb, yb)], fill=col, width=max(2, w - 2))
        d.line([(cx - wa, ya), (cx + wb, yb)], fill=col, width=max(2, w - 3))
        d.line([(cx + wa, ya), (cx - wb, yb)], fill=col, width=max(2, w - 3))
    return y_end


# ------------------------------------------------------------ 現代
def ima():
    """現代の部屋。茶番と現代パート。窓の外に小さく東京タワー。"""
    img = base((248, 242, 232), (226, 216, 200))
    d = _d(img)
    wood_floor(img, FLOOR)
    # 窓は2人の立ち位置（x=0.30 / 0.74）の間に置く。右寄せだと
    # つむぎの頭でタワーが隠れた（2026-09-23 独立検証で指摘）
    d.rectangle([740, 150, 1180, 560], fill=(176, 204, 228))
    _lattice_tower(d, 960, 560, 200, 44, width=3)
    d.rectangle([740, 150, 1180, 560], outline=(70, 62, 56), width=10)
    d.line([(740, 330), (1180, 330)], fill=(70, 62, 56), width=6)
    d.rectangle([620, 760, 1320, 800], fill=(176, 138, 98))
    d.rectangle([660, 800, 690, 1000], fill=(150, 116, 82))
    d.rectangle([1250, 800, 1280, 1000], fill=(150, 116, 82))
    # 床の段ボール箱（茶番の小道具）
    for i, x in enumerate((180, 390)):
        d.rectangle([x, 800 - i * 20, x + 190, 930], fill=(196, 160, 112),
                    outline=(150, 118, 78), width=5)
        d.line([(x, 840 - i * 20), (x + 190, 840 - i * 20)], fill=(170, 136, 92), width=4)
    return img


# ------------------------------------------------------------ 山梨・少年期
def inaka():
    """甲府盆地の村。畑と南アルプスの山並み。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 202, 226), (214, 220, 206)), (0, 0))
    d = _d(img)
    d.polygon([(0, 470), (300, 250), (560, 380), (860, 200), (1220, 390),
               (1520, 230), (W, 420), (W, 640), (0, 640)], fill=(118, 132, 150))
    d.polygon([(760, 250), (860, 200), (960, 250)], fill=(232, 236, 240))    # 雪
    d.polygon([(1440, 280), (1520, 230), (1600, 280)], fill=(232, 236, 240))
    d.rectangle([0, 620, W, H], fill=(142, 156, 104))
    for i, y in enumerate(range(680, H, 60)):                                  # 畑の畝
        d.line([(0, y), (W, y + 30)], fill=(120, 134, 88), width=8)
    d.rectangle([1300, 560, 1720, 760], fill=(126, 100, 76))                  # 農家
    d.polygon([(1260, 570), (1510, 420), (1760, 570)], fill=(96, 82, 66))
    return img


def ie():
    """明治の農家の中。土間と板の間。"""
    img = base((96, 82, 66), (62, 52, 42))
    d = _d(img)
    tatami_floor(img, FLOOR)
    for x in (300, 1560):
        d.rectangle([x, 0, x + 40, FLOOR], fill=(64, 50, 40))
    d.rectangle([420, 170, 1420, 690], fill=(224, 216, 196), outline=(96, 78, 60), width=10)
    for gx in range(520, 1420, 200):
        d.line([(gx, 170), (gx, 690)], fill=(158, 140, 116), width=6)
    for gy in range(280, 690, 140):
        d.line([(420, gy), (1420, gy)], fill=(158, 140, 116), width=5)
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def kyoshitsu():
    """旧制中学・高校の教室。"""
    img = base((212, 204, 184), (184, 174, 154))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 92, 66), line=(100, 76, 54))
    d.rectangle([430, 150, 1490, 610], fill=(46, 58, 50), outline=(88, 70, 52), width=14)
    # 黒板に船の断面の図
    d.polygon([(640, 300), (1280, 300), (1180, 470), (740, 470)], outline=(210, 214, 206), width=5)
    d.line([(960, 300), (960, 470)], fill=(210, 214, 206), width=4)
    _window(d, 60, 200, 330, 560)
    _window(d, 1600, 200, 1870, 560)
    return img


# ------------------------------------------------------------ 大学・研究
def seizu():
    """帝大の製図室。斜めの製図台が並ぶ。"""
    img = base((222, 216, 200), (190, 182, 166))
    d = _d(img)
    wood_floor(img, FLOOR, col=(128, 98, 70), line=(108, 82, 58))
    _window(d, 120, 150, 620, 560, sky=(186, 206, 222))
    _window(d, 1300, 150, 1800, 560, sky=(186, 206, 222))
    for x in (160, 760, 1360):                                   # 製図台
        d.polygon([(x, 640), (x + 420, 600), (x + 420, 700), (x, 740)],
                  fill=(236, 232, 220), outline=(150, 136, 116), width=5)
        d.line([(x + 60, 620), (x + 380, 596)], fill=(120, 120, 128), width=4)
        d.rectangle([x + 40, 740, x + 60, 980], fill=(120, 94, 68))
        d.rectangle([x + 360, 700, x + 380, 980], fill=(120, 94, 68))
    return img


def kenkyushitsu():
    """早稲田の研究室。書棚と、計算式の並んだ黒板。"""
    img = base((210, 202, 186), (178, 168, 152))
    d = _d(img)
    wood_floor(img, FLOOR, col=(116, 88, 62), line=(96, 72, 50))
    d.rectangle([90, 180, 620, 720], fill=(122, 96, 68))         # 書棚
    for sy in range(230, 700, 120):
        d.rectangle([110, sy, 600, sy + 16], fill=(96, 74, 52))
        for x in range(130, 580, 34):
            d.rectangle([x, sy - 86, x + 24, sy], fill=(168 - (x % 40), 140, 110))
    d.rectangle([760, 160, 1760, 560], fill=(46, 58, 50), outline=(88, 70, 52), width=12)
    for y in (230, 310, 390, 470):                               # 式の行
        d.line([(820, y), (1300 + (y % 160), y)], fill=(196, 204, 196), width=4)
    d.rectangle([720, 700, 1560, 748], fill=(140, 108, 76))      # 机
    d.rectangle([760, 748, 800, 990], fill=(118, 90, 64))
    d.rectangle([1480, 748, 1520, 990], fill=(118, 90, 64))
    d.rectangle([980, 672, 1300, 700], fill=(238, 232, 214))     # 計算尺
    d.line([(990, 686), (1290, 686)], fill=(120, 110, 96), width=3)
    return img


def shosai():
    """自宅の書斎。夜。電灯と机、計算尺と紙の山。"""
    img = base((84, 72, 62), (52, 44, 38))
    d = _d(img)
    wood_floor(img, FLOOR, col=(78, 60, 46), line=(62, 48, 36))
    _window(d, 1340, 170, 1780, 520, sky=(34, 42, 66), frame=(60, 50, 42))
    d.rectangle([520, 700, 1400, 748], fill=(112, 84, 60))
    d.rectangle([560, 748, 600, 990], fill=(92, 70, 50))
    d.rectangle([1320, 748, 1360, 990], fill=(92, 70, 50))
    for i in range(5):                                           # 紙の山
        d.rectangle([640 + i * 6, 676 - i * 8, 900 + i * 6, 700 - i * 8],
                    fill=(236, 230, 214), outline=(180, 170, 150), width=2)
    d.rectangle([1000, 676, 1320, 698], fill=(238, 232, 214))    # 計算尺
    d.line([(1010, 687), (1310, 687)], fill=(120, 110, 96), width=3)
    hanging_bulb(img, 900, warm=True, ly=40)
    return img


# ------------------------------------------------------------ アメリカ
def america():
    """1917年のアメリカの街。石とレンガのビル。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (182, 200, 216), (206, 204, 196)), (0, 0))
    d = _d(img)
    d.rectangle([0, 800, W, H], fill=(118, 114, 108))
    specs = [(40, 300, 260, (150, 112, 92)), (300, 160, 240, (172, 160, 142)),
             (580, 380, 200, (140, 106, 88)), (1180, 220, 260, (168, 156, 140)),
             (1480, 120, 200, (150, 118, 96)), (1720, 340, 200, (176, 164, 146))]
    for x, top, w, col in specs:
        d.rectangle([x, top, x + w, 800], fill=col, outline=(96, 86, 78), width=5)
        for wy in range(top + 40, 780, 70):
            for wx in range(x + 24, x + w - 30, 54):
                d.rectangle([wx, wy, wx + 28, wy + 40], fill=(92, 104, 118))
    return img


def eki():
    """アメリカの駅の荷物置き場。トランクが積まれている。"""
    img = base((170, 160, 146), (120, 112, 102))
    d = _d(img)
    wood_floor(img, FLOOR, col=(104, 88, 70), line=(86, 72, 58))
    for x in range(0, W, 320):                                   # 鉄骨の柱とアーチ
        d.rectangle([x + 140, 120, x + 170, FLOOR], fill=(86, 84, 82))
    d.rectangle([0, 100, W, 130], fill=(92, 90, 88))
    for i, (x, y, w, h) in enumerate([(160, 640, 300, 170), (200, 520, 240, 120),
                                       (1380, 660, 340, 160), (1440, 560, 220, 100)]):
        d.rectangle([x, y, x + w, y + h], fill=(128 - i * 6, 88, 60),
                    outline=(86, 60, 42), width=6)
        d.line([(x, y + h // 3), (x + w, y + h // 3)], fill=(180, 150, 90), width=5)
        d.line([(x, y + h * 2 // 3), (x + w, y + h * 2 // 3)], fill=(180, 150, 90), width=5)
    return img


# ------------------------------------------------------------ 建物
def genba():
    """ビルの建設現場。鉄骨の骨組みと足場。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (180, 196, 212), (204, 200, 188)), (0, 0))
    d = _d(img)
    d.rectangle([0, 820, W, H], fill=(132, 120, 102))
    x0, x1 = 560, 1360
    for y in range(260, 820, 110):                               # 階ごとの梁
        d.line([(x0, y), (x1, y)], fill=(92, 88, 86), width=12)
    for x in range(x0, x1 + 1, 160):                             # 柱
        d.line([(x, 260), (x, 820)], fill=(92, 88, 86), width=14)
    # 1本だけ壁を入れた区画（耐震壁の暗示）
    d.rectangle([x0 + 320, 480, x0 + 480, 590], fill=(176, 170, 160))
    d.rectangle([x0 + 320, 700, x0 + 480, 810], fill=(176, 170, 160))
    d.line([(1500, 820), (1500, 140)], fill=(200, 160, 60), width=16)   # クレーン
    d.line([(1500, 150), (1000, 150)], fill=(200, 160, 60), width=12)
    d.line([(1100, 150), (1100, 320)], fill=(80, 80, 80), width=3)
    return img


def ginko():
    """完成した銀行の本店。石張りの重たい外観。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (176, 198, 220), (210, 208, 200)), (0, 0))
    d = _d(img)
    d.rectangle([0, 860, W, H], fill=(140, 136, 128))
    d.rectangle([380, 220, 1540, 860], fill=(206, 198, 180), outline=(150, 142, 126), width=8)
    d.rectangle([340, 180, 1580, 240], fill=(190, 182, 164))
    for x in range(470, 1480, 150):                              # 列柱
        d.rectangle([x, 520, x + 50, 860], fill=(222, 216, 200), outline=(170, 162, 146), width=4)
    for x in range(450, 1480, 150):                              # 上階の窓
        for y in (290, 400):
            d.rectangle([x, y, x + 80, y + 70], fill=(96, 108, 120))
    d.rectangle([860, 700, 1060, 860], fill=(90, 80, 70))       # 入口
    return img


def shinsai():
    """震災直後の街。崩れた建物の間に、無事なビルが残る。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (150, 132, 118), (112, 102, 94)), (0, 0))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(98, 90, 84))
    d.rectangle([760, 250, 1300, 760], fill=(186, 178, 162), outline=(130, 122, 108), width=7)
    for x in range(800, 1270, 110):
        for y in range(300, 720, 100):
            d.rectangle([x, y, x + 60, y + 60], fill=(88, 96, 106))
    for x in range(40, 700, 170):                                # 崩れた建物
        d.polygon([(x, 760), (x + 40, 520 + (x % 90)), (x + 150, 600), (x + 160, 760)],
                  fill=(120, 108, 98))
    for x in range(1380, 1880, 160):
        d.polygon([(x, 760), (x + 30, 560 + (x % 70)), (x + 140, 640), (x + 150, 760)],
                  fill=(120, 108, 98))
    for x, top in ((300, 380), (1560, 420)):                     # 煙
        d.ellipse([x - 120, top - 180, x + 120, top], fill=(132, 124, 118))
    return img


def jimusho():
    """応接室。依頼を受ける場面・会社の場面で共用。"""
    img = base((210, 202, 186), (178, 168, 152))
    d = _d(img)
    wood_floor(img, FLOOR, col=(116, 88, 62), line=(96, 72, 50))
    _window(d, 1300, 160, 1800, 580)
    d.rectangle([160, 200, 700, 560], fill=(226, 220, 206), outline=(140, 120, 96), width=8)
    d.rectangle([220, 260, 640, 500], fill=(186, 200, 212))      # 額の地図
    d.polygon([(300, 470), (380, 330), (470, 400), (560, 300), (600, 470)], fill=(150, 170, 140))
    d.rectangle([720, 700, 1560, 748], fill=(140, 108, 76))
    d.rectangle([760, 748, 800, 990], fill=(118, 90, 64))
    d.rectangle([1480, 748, 1520, 990], fill=(118, 90, 64))
    return img


# ------------------------------------------------------------ 塔
def tettou():
    """山の上のラジオ放送の鉄塔。大正末。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (166, 196, 222), (214, 216, 206)), (0, 0))
    d = _d(img)
    d.polygon([(0, 720), (500, 560), (1100, 540), (1600, 600), (W, 700), (W, H), (0, H)],
              fill=(116, 136, 102))
    for cx in (620, 1300):                                       # 2本の鉄塔とアンテナ線
        _lattice_tower(d, cx, 580, 130, 60, half_top=4, bands=False, width=5)
    d.line([(620, 140), (1300, 140)], fill=(80, 80, 84), width=3)
    d.line([(960, 140), (960, 470)], fill=(80, 80, 84), width=3)
    d.rectangle([860, 470, 1060, 580], fill=(196, 188, 172), outline=(140, 130, 114), width=5)
    return img


def tower_genba():
    """建設中の東京タワー。途中まで組まれた鉄骨。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (160, 190, 220), (212, 208, 196)), (0, 0))
    d = _d(img)
    d.rectangle([0, 900, W, H], fill=(124, 116, 104))
    y_end = _lattice_tower(d, 960, 900, 40, 300, width=9, built=0.45)
    d.line([(960, y_end), (960, y_end - 160)], fill=(200, 160, 60), width=12)   # 頂部のクレーン
    d.line([(960, y_end - 150), (1200, y_end - 150)], fill=(200, 160, 60), width=10)
    d.line([(1180, y_end - 150), (1180, y_end - 40)], fill=(70, 70, 70), width=3)
    for x in range(120, 1800, 220):                              # 足元の資材
        d.rectangle([x, 930, x + 140, 960], fill=(150, 90, 70))
    return img


def tower():
    """完成した東京タワー。夕方の空。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (242, 170, 120), (126, 104, 150)), (0, 0))
    d = _d(img)
    for x in range(0, W, 120):                                   # 街並み
        h = 780 + (x * 37) % 130
        d.rectangle([x, h, x + 110, H], fill=(70, 62, 86))
    _lattice_tower(d, 960, 900, 30, 250, width=8)
    d.rectangle([915, 560, 1005, 610], fill=(236, 228, 214))     # 大展望台
    d.rectangle([940, 300, 980, 326], fill=(236, 228, 214))      # 上の展望台
    _glow(img, 960, 580, 150, (255, 200, 140), 60)
    return img


def jitei():
    """1926年の自邸。柱も梁も見えない、壁と床だけの広間。"""
    img = base((226, 220, 206), (196, 188, 172))
    d = _d(img)
    wood_floor(img, FLOOR, col=(122, 94, 68), line=(102, 78, 56))
    d.rectangle([0, 150, W, 172], fill=(206, 198, 182))            # 天井の回り縁
    for x0 in (160, 1340):                                          # 縦長の洋窓
        d.rectangle([x0, 230, x0 + 360, 640], fill=(182, 204, 222))
        d.rectangle([x0, 230, x0 + 360, 640], outline=(120, 104, 86), width=10)
        for gy in range(330, 640, 100):
            d.line([(x0, gy), (x0 + 360, gy)], fill=(120, 104, 86), width=5)
    d.rectangle([760, 300, 1160, 700], fill=(150, 116, 84),
                outline=(112, 86, 60), width=8)                     # 木目を描いた金属の扉
    for gy in range(330, 690, 34):
        d.line([(780, gy), (1140, gy + 8)], fill=(132, 100, 72), width=3)
    d.ellipse([1098, 490, 1122, 514], fill=(200, 180, 120))
    hanging_bulb(img, 960, warm=True, ly=30)
    return img


def terebitou():
    """大通りの公園に立つテレビ塔。名古屋テレビ塔の場面で使う。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 200, 226), (214, 216, 206)), (0, 0))
    d = _d(img)
    d.rectangle([0, 820, W, H], fill=(128, 146, 108))               # 公園の芝
    d.rectangle([0, 900, W, 960], fill=(150, 146, 138))             # 大通り
    _lattice_tower(d, 960, 860, 90, 190, half_top=5, bands=False, width=7,
                   legs_col=(120, 124, 132))
    d.rectangle([900, 420, 1020, 470], fill=(210, 212, 214),
                outline=(120, 124, 132), width=4)                   # 展望台
    for x in range(60, 1880, 180):                                  # 並木
        if 700 < x < 1220:
            continue
        d.rectangle([x + 34, 760, x + 46, 830], fill=(96, 76, 56))
        d.ellipse([x, 660, x + 80, 780], fill=(92, 128, 84))
    return img


def shiryo():
    """新聞・書類の面。論争の章で使う。"""
    img = base((238, 234, 224), (212, 206, 194))
    d = _d(img)
    d.rectangle([180, 90, 1740, 990], fill=(250, 248, 242), outline=(168, 160, 146), width=8)
    d.rectangle([240, 150, 1680, 170], fill=(120, 112, 100))
    for y in range(230, 950, 46):
        w = 1440 if (y // 46) % 5 else 900
        d.rectangle([240, y, 240 + w, y + 18], fill=(196, 190, 178))
    return img


LOCATIONS = {
    "nt_ima": ima, "nt_inaka": inaka, "nt_ie": ie, "nt_kyoshitsu": kyoshitsu,
    "nt_seizu": seizu, "nt_kenkyushitsu": kenkyushitsu, "nt_shosai": shosai,
    "nt_america": america, "nt_eki": eki, "nt_genba": genba, "nt_ginko": ginko,
    "nt_shinsai": shinsai, "nt_jimusho": jimusho, "nt_tettou": tettou,
    "nt_tower_genba": tower_genba, "nt_tower": tower, "nt_shiryo": shiryo,
    "nt_jitei": jitei, "nt_terebitou": terebitou,
}

CARDS = ["1886", "1910", "1917", "1923", "1925", "1954", "1957", "1958", "1970"]


def year_card(text: str) -> Image.Image:
    """黒地に年号だけのカード。キャラと同居させない単独シーンで使う。"""
    img = Image.new("RGB", (W, H), (18, 18, 20))
    d = _d(img)
    from ytf.config import Config, resolve_font
    Config.load()
    font = ImageFont.truetype(resolve_font("w9"), 150)
    bb = d.textbbox((0, 0), text, font=font)
    d.text(((W - (bb[2] - bb[0])) // 2, (H - (bb[3] - bb[1])) // 2 - 40),
           text, font=font, fill=(238, 234, 226))
    d.line([(W // 2 - 220, H // 2 + 130), (W // 2 + 220, H // 2 + 130)],
           fill=(150, 146, 138), width=4)
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for y in CARDS:
        year_card(f"{y}年").save(OUT / f"nt_card_{y}.png")
        print(f"生成完了: nt_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
