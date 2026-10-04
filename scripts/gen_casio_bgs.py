#!/usr/bin/env python3
"""カシオの誕生・樫尾四兄弟回（53_カシオの誕生 / slug=casio-kashio）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針は蚊取り線香回（gen_katori_bgs.py）と同じ。
実在メーカーの商標（ロゴ・製品名の文字）は描かない。

実行: PYTHONPATH=. python scripts/gen_casio_bgs.py [名前...]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, glow, hanging_bulb, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)


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


def _desk(d, x0, y, w, col=(130, 100, 72)):
    d.rectangle([x0, y, x0 + w, y + 36], fill=col)
    d.rectangle([x0 + 20, y + 36, x0 + 50, FLOOR], fill=(100, 76, 54))
    d.rectangle([x0 + w - 50, y + 36, x0 + w - 20, FLOOR], fill=(100, 76, 54))


def _big_calc(d, x, y, s=1.0):
    """大きな事務机型の計算機（文字は描かない）。下端中央が x, y。"""
    w, h = 300 * s, 200 * s
    d.rectangle([x - w / 2, y - h, x + w / 2, y], fill=(170, 176, 170), outline=(110, 116, 110), width=5)
    d.rectangle([x - w / 2 + 20 * s, y - h + 20 * s, x + w / 2 - 20 * s, y - h + 60 * s], fill=(40, 44, 40))
    for r in range(3):
        for c in range(4):
            cx = x - 90 * s + c * 60 * s
            cy = y - h + 90 * s + r * 34 * s
            d.rectangle([cx, cy, cx + 40 * s, cy + 24 * s], fill=(230, 226, 214))


def _lathe(d, x, y):
    """旋盤（横長の機械）。"""
    d.rectangle([x, y - 60, x + 420, y], fill=(90, 100, 96), outline=(60, 66, 64), width=5)
    d.rectangle([x + 20, y - 150, x + 120, y - 60], fill=(110, 120, 116), outline=(60, 66, 64), width=5)
    d.ellipse([x + 110, y - 130, x + 170, y - 70], fill=(150, 150, 146))
    d.rectangle([x + 30, y, x + 70, FLOOR], fill=(70, 76, 74))
    d.rectangle([x + 350, y, x + 390, FLOOR], fill=(70, 76, 74))


# ------------------------------------------------------------ 現代
def ima():
    """現代の勉強机。電卓とノート。"""
    img = base((236, 232, 222), (214, 208, 196))
    d = _d(img)
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    _window(d, 700, 150, 1220, 470, sky=(176, 210, 232))
    _desk(d, 520, 640, 880, col=(180, 150, 110))
    d.rectangle([700, 580, 900, 640], fill=(246, 246, 240), outline=(170, 170, 160), width=3)   # ノート
    d.rounded_rectangle([1000, 560, 1120, 640], radius=10, fill=(60, 64, 72))                   # 電卓
    d.rectangle([1014, 572, 1106, 592], fill=(170, 186, 160))
    for r in range(3):
        for c in range(4):
            d.rectangle([1014 + c * 24, 600 + r * 12, 1030 + c * 24, 608 + r * 12], fill=(200, 200, 204))
    return img


def machi():
    """昭和初めの東京の下町。木造の家並み。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (178, 204, 224), (216, 214, 204)), (0, 0))
    d = _d(img)
    for x0, h in ((0, 300), (320, 260), (620, 320), (1260, 280), (1560, 330)):
        d.rectangle([x0, 640 - h, x0 + 290, 640], fill=(120, 100, 80))
        d.polygon([(x0 - 20, 660 - h), (x0 + 145, 570 - h), (x0 + 310, 660 - h)], fill=(80, 70, 62))
        d.rectangle([x0 + 40, 640 - h + 70, x0 + 250, 640 - h + 110], fill=(200, 190, 170))
    d.line([(0, 200), (W, 240)], fill=(60, 60, 60), width=3)                # 電線
    d.rectangle([0, 640, W, H], fill=(176, 160, 130))
    return img


def koba():
    """戦後の小さな町工場。旋盤と作業台。"""
    img = base((196, 186, 168), (160, 150, 134))
    d = _d(img)
    wood_floor(img, FLOOR, col=(110, 96, 80), line=(92, 80, 66))
    _window(d, 700, 140, 1220, 440, sky=(170, 196, 214))
    _lathe(d, 80, 700)
    _desk(d, 1200, 660, 560)
    for k in range(5):
        d.ellipse([1240 + k * 90, 620, 1300 + k * 90, 660], fill=(150, 150, 150))   # 部品
    hanging_bulb(img, 960, warm=True, ly=40)
    return img


def tenji():
    """展示会の会場。台の上の大きな計算機。"""
    img = base((230, 224, 210), (204, 196, 180))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 120, 88), line=(128, 102, 74))
    d.rectangle([300, 110, 1620, 190], fill=(60, 80, 120))                  # 横幕（文字なし）
    for x in (120, 1720):
        d.rectangle([x, 100, x + 80, FLOOR], fill=(206, 196, 176))
    d.rectangle([760, 660, 1160, 720], fill=(130, 100, 72))                 # 展示台
    _big_calc(d, 960, 660, 1.0)
    for x in (560, 1360):
        _glow(img, x, 120, 90, (255, 236, 190), 120)
    return img


def _gear_calc(d, x, y, s=1.0):
    """歯車で動く大型の計算機（数字キーではなく、けたごとの縦の列のキー）。"""
    import math as _m
    w, h = 320 * s, 220 * s
    d.rectangle([x - w / 2, y - h, x + w / 2, y], fill=(110, 106, 100), outline=(70, 66, 62), width=5)
    for c in range(8):                                                     # けたごとのキーの列
        for r in range(5):
            cx = x - 140 * s + c * 34 * s
            cy = y - h + 70 * s + r * 26 * s
            d.ellipse([cx, cy, cx + 20 * s, cy + 20 * s], fill=(220, 214, 200))
    for k, gx in enumerate((x - 120 * s, x + 110 * s)):                    # 上にのぞく歯車
        r = 36 * s
        pts = []
        for i in range(24):
            a = i / 24 * 2 * _m.pi
            rr = r * (1.0 if i % 2 == 0 else 0.8)
            pts.append((gx + rr * _m.cos(a), y - h - 10 * s + rr * _m.sin(a)))
        d.polygon(pts, fill=(196, 170, 90), outline=(120, 100, 50))


def tenji0():
    """1949年の展示会の会場。台の上の歯車式の計算機。"""
    img = base((230, 224, 210), (204, 196, 180))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 120, 88), line=(128, 102, 74))
    d.rectangle([300, 110, 1620, 190], fill=(60, 80, 120))
    for x in (120, 1720):
        d.rectangle([x, 100, x + 80, FLOOR], fill=(206, 196, 176))
    d.rectangle([760, 660, 1160, 720], fill=(130, 100, 72))
    _gear_calc(d, 960, 660, 1.0)
    for x in (560, 1360):
        _glow(img, x, 120, 90, (255, 236, 190), 120)
    return img


def shousha():
    """昭和30年代の商社の応接。机と書類棚。"""
    img = base((222, 216, 202), (194, 186, 170))
    d = _d(img)
    wood_floor(img, FLOOR, col=(132, 104, 76), line=(112, 88, 64))
    _window(d, 640, 140, 1280, 460, sky=(176, 200, 218))
    for x in (90, 1560):                                                     # 書類棚
        d.rectangle([x, 260, x + 270, FLOOR], fill=(150, 120, 88), outline=(110, 86, 60), width=5)
        for y in range(300, FLOOR - 40, 90):
            d.line([(x, y), (x + 270, y)], fill=(110, 86, 60), width=5)
    _desk(d, 660, 660, 600)
    return img


def zukai():
    """図解用。リレー（電磁石と接点）と、そろばんの珠。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (32, 38, 50), (18, 22, 30)), (0, 0))
    d = _d(img)
    d.rectangle([760, 380, 880, 620], fill=(180, 110, 60))                  # コイル
    for y in range(390, 620, 16):
        d.line([(760, y), (880, y)], fill=(140, 80, 40), width=4)
    d.line([(820, 360), (1120, 330)], fill=(200, 200, 210), width=10)       # 接点の板
    d.ellipse([1100, 310, 1140, 350], fill=(236, 206, 90))
    d.ellipse([1100, 380, 1140, 420], fill=(236, 206, 90))
    d.line([(1120, 420), (1120, 560)], fill=(200, 200, 210), width=6)
    for k in range(5):                                                      # そろばんの珠
        d.ellipse([700 + k * 110, 700, 780 + k * 110, 760], fill=(160, 120, 80))
    d.ellipse([700 + 5 * 110 + 40, 640, 780 + 5 * 110 + 40, 700], fill=(200, 150, 90))
    d.line([(680, 730), (1360, 730)], fill=(120, 110, 100), width=4)
    return img


def haneda():
    """昭和30年代の空港。プロペラ機。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (170, 200, 226), (214, 218, 216)), (0, 0))
    d = _d(img)
    d.rectangle([0, 620, W, H], fill=(150, 150, 146))
    d.ellipse([1000, 440, 1760, 560], fill=(210, 214, 220))                # 胴体
    d.polygon([(1240, 500), (1520, 500), (1420, 620), (1320, 620)], fill=(190, 194, 200))   # 翼
    d.polygon([(1700, 470), (1780, 360), (1800, 470)], fill=(190, 194, 200))                 # 尾翼
    for x in (1300, 1460):
        d.ellipse([x - 10, 460, x + 10, 540], fill=(80, 80, 86))
    d.rectangle([120, 520, 600, 620], fill=(190, 176, 150))                # 荷物台
    for k in range(3):
        d.rectangle([160 + k * 140, 450, 280 + k * 140, 520], fill=(150, 120, 90), outline=(110, 86, 60), width=4)
    return img


def hotel():
    """夜の宿の部屋。机に広げた計算機と工具。"""
    img = base((100, 92, 84), (66, 60, 56))
    d = _d(img)
    tatami_floor(img, FLOOR)
    _window(d, 700, 150, 1220, 440, sky=(40, 46, 70), frame=(70, 60, 54))
    d.rectangle([500, 640, 1420, 690], fill=(120, 92, 66))                  # 座卓
    _big_calc(d, 960, 640, 0.8)
    for k in range(20):                                                     # 配線
        d.line([(830 + k * 13, 640), (800 + k * 17, 700 + (k % 4) * 10)], fill=(200, 60 + k * 8, 60), width=3)
    _glow(img, 1500, 300, 180, (255, 210, 140), 80)
    return img


def jimusho():
    """1957年の事務所。机と黒板。"""
    img = base((224, 218, 204), (196, 188, 172))
    d = _d(img)
    wood_floor(img, FLOOR, col=(130, 102, 76), line=(110, 86, 64))
    d.rectangle([600, 170, 1320, 460], fill=(54, 70, 62), outline=(110, 90, 66), width=12)
    for x in (120, 1440):
        _desk(d, x, 660, 380)
    return img


def setsumei():
    """販売店向けの説明会の会場。並んだ椅子と演台。"""
    img = base((218, 214, 204), (190, 184, 172))
    d = _d(img)
    wood_floor(img, FLOOR, col=(140, 112, 84), line=(120, 94, 70))
    d.rectangle([300, 120, 1620, 200], fill=(120, 60, 60))
    d.rectangle([820, 560, 1100, 700], fill=(130, 100, 72))                 # 演台
    for row in range(2):
        for k in range(8):
            x = 160 + k * 220
            y = 760 + row * 80
            d.rectangle([x, y, x + 120, y + 20], fill=(90, 100, 110))
    return img


def kaigi():
    """1970年代の会議室。長机とホワイトボード。"""
    img = base((226, 226, 222), (198, 198, 194))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 132, 110), line=(130, 114, 94))
    d.rectangle([600, 170, 1320, 460], fill=(246, 246, 244), outline=(160, 160, 156), width=10)
    d.rectangle([200, 700, 1720, 750], fill=(160, 130, 96))
    for x in range(260, 1700, 240):
        d.rectangle([x, 620, x + 90, 700], fill=(80, 96, 120))
    return img


def kinenkan():
    """記念館の展示室。台の上の古い計算機に光。"""
    img = base((70, 66, 64), (40, 38, 38))
    d = _d(img)
    wood_floor(img, FLOOR, col=(80, 64, 52), line=(64, 52, 42))
    d.rectangle([740, 640, 1180, 720], fill=(110, 90, 70))
    _big_calc(d, 960, 640, 1.0)
    _glow(img, 960, 420, 320, (255, 230, 180), 90)
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


def sekai():
    """暗い地に世界地図の点。現代の広がりの章で使う。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (20, 36, 50), (12, 20, 30)), (0, 0))
    d = _d(img)
    lands = [(330, 330, 300, 170), (470, 700, 130, 190), (960, 330, 140, 110),
             (1010, 620, 160, 210), (1330, 360, 330, 180), (1500, 640, 90, 60),
             (1620, 780, 150, 90), (1590, 400, 30, 60)]
    for y in range(120, 980, 26):
        for x in range(60, 1880, 26):
            for cx, cy, rx, ry in lands:
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1:
                    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(110, 190, 170))
                    break
    for cx, cy in ((1590, 420), (1450, 520), (960, 330), (330, 330), (1030, 620)):
        _glow(img, cx, cy, 60, (255, 220, 140), 150)
    return img


LOCATIONS = {
    "cs_ima": ima, "cs_machi": machi, "cs_tenji0": tenji0, "cs_koba": koba, "cs_tenji": tenji, "cs_shousha": shousha,
    "cs_zukai": zukai, "cs_haneda": haneda, "cs_hotel": hotel, "cs_jimusho": jimusho,
    "cs_setsumei": setsumei, "cs_kaigi": kaigi, "cs_kinenkan": kinenkan, "cs_shiryo": shiryo,
    "cs_sekai": sekai,
}

CARDS = ["1946", "1949", "1954", "1956", "1957", "1964", "1972"]


# ------------------------------------------------------------ 作り直し版（77_カシオの誕生 / casio-kashio-v2）で足した背景
# 既存の絵は変えない。場面の途中の差し替え用は「元の背景を呼んで要素を足す」形にして、
# 同じ構図のまま状態の変化が一目で分かるようにする。
def _small_calc(d, x, y, s=1.0, body=(60, 64, 72), key=(200, 200, 204)):
    """手のひらの電卓。左上が x, y（文字は描かない）。"""
    d.rounded_rectangle([x, y, x + 120 * s, y + 80 * s], radius=int(10 * s), fill=body)
    d.rectangle([x + 14 * s, y + 10 * s, x + 106 * s, y + 30 * s], fill=(170, 186, 160))
    for r in range(3):
        for c in range(4):
            kx, ky = x + 14 * s + c * 24 * s, y + 38 * s + r * 13 * s
            d.rectangle([kx, ky, kx + 16 * s, ky + 8 * s], fill=key)


def ima3():
    """現代の勉強机に、100円の電卓が3台。"""
    img = ima()
    d = _d(img)
    _small_calc(d, 560, 560, 1.0, body=(70, 120, 190))
    _small_calc(d, 1180, 560, 1.0, body=(232, 228, 220), key=(150, 150, 156))
    return img


def shousha_shisaku():
    """商社の応接の机に、ランドセルほどの試作機。"""
    img = shousha()
    d = _d(img)
    x0, x1, y0, y1 = 820, 1100, 500, 660
    d.rectangle([x0, y0, x1, y1], fill=(120, 132, 120), outline=(70, 80, 70), width=5)
    d.rectangle([x0 + 30, y0 + 22, x1 - 30, y0 + 52], fill=(40, 44, 40))
    for c in range(7):                                                     # けたごとのキーの列
        for r in range(3):
            cx, cy = x0 + 36 + c * 32, y0 + 70 + r * 26
            d.ellipse([cx, cy, cx + 18, cy + 18], fill=(226, 220, 204))
    d.line([(x1, y1 - 30), (x1 + 60, y1 - 4)], fill=(30, 30, 30), width=5)    # 電源コード
    return img


def _relay_rack(d, x0, y0, cols=10, rows=4):
    """リレーをぎっしり並べた枠（銅色のコイルと黒い台）。"""
    d.rectangle([x0 - 16, y0 - 16, x0 + cols * 38 + 6, y0 + rows * 44 + 4], fill=(70, 74, 72), outline=(40, 42, 40), width=4)
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * 38, y0 + r * 44
            d.rectangle([x, y, x + 26, y + 30], fill=(36, 36, 38))
            d.rectangle([x + 6, y + 4, x + 20, y + 22], fill=(184, 112, 62))


def koba_haisen():
    """町工場の真ん中の作業台に、ふたを開けたリレー計算機と色つきの配線の束。"""
    img = koba()
    d = _d(img)
    d.rectangle([720, 700, 1200, 736], fill=(130, 100, 72))                 # 作業台
    d.rectangle([740, 736, 770, FLOOR], fill=(100, 76, 54))
    d.rectangle([1150, 736, 1180, FLOOR], fill=(100, 76, 54))
    _relay_rack(d, 770, 500, cols=10, rows=4)
    cols = [(210, 60, 60), (240, 240, 236), (60, 100, 200), (236, 206, 60), (70, 160, 80),
            (140, 80, 170), (30, 30, 30), (140, 96, 60), (236, 140, 50), (150, 150, 150)]
    for k in range(20):                                                    # 台から垂れる配線
        c = cols[k % 10]
        x = 760 + k * 22
        d.line([(x, 700), (x + 10, 760), (x - 6, 820 + (k % 5) * 14)], fill=c, width=5)
    return img


def koba_yama():
    """koba_haisen の作業台と床に、相談の図面と書類が山になった状態。"""
    img = koba_haisen()
    d = _d(img)
    import random
    rnd = random.Random(7)
    for bx, by, n in ((700, 700, 14), (880, 500, 10), (1060, 700, 16), (640, FLOOR + 10, 18),
                      (1140, FLOOR + 20, 20), (900, FLOOR + 30, 12)):
        y = by
        for i in range(n):                                                 # 書類の束を積む
            w = rnd.randint(150, 200)
            off = rnd.randint(-14, 14)
            d.rectangle([bx + off, y - 16, bx + off + w, y], fill=(246, 244, 236), outline=(170, 166, 156), width=2)
            if i % 3 == 0:
                d.line([(bx + off + 12, y - 8), (bx + off + w - 20, y - 8)], fill=(120, 140, 190), width=2)
            y -= 16
    for k in range(6):                                                     # 丸めた図面
        x = 760 + k * 70
        d.rounded_rectangle([x, 640 - k % 2 * 30, x + 160, 664 - k % 2 * 30], radius=12,
                            fill=(214, 226, 240), outline=(120, 140, 170), width=2)
    return img


def toko():
    """畳の部屋に敷いた布団。障子の窓。"""
    img = base((214, 204, 184), (182, 170, 150))
    d = ImageDraw.Draw(img, "RGBA")
    fy = 700                                                               # この部屋は床を高めに取る
    tatami_floor(img, fy)
    d.rectangle([660, 120, 1260, 420], fill=(240, 236, 222), outline=(120, 96, 70), width=10)   # 障子
    for x in range(660, 1260, 100):
        d.line([(x, 120), (x, 420)], fill=(140, 116, 88), width=4)
    for y in range(120, 420, 75):
        d.line([(660, y), (1260, y)], fill=(140, 116, 88), width=4)
    d.polygon([(720, 740), (1200, 740), (1290, 900), (630, 900)], fill=(246, 246, 240))         # 敷き布団
    d.polygon([(735, 790), (1185, 790), (1265, 900), (655, 900)], fill=(110, 130, 170))         # 掛け布団
    d.line([(735, 790), (1185, 790)], fill=(236, 236, 230), width=10)
    d.rounded_rectangle([880, 730, 1040, 776], radius=18, fill=(236, 226, 200))                 # 枕
    d.rectangle([1300, 760, 1420, 796], fill=(120, 90, 60))                                     # 盆と湯のみ
    d.rectangle([1340, 730, 1372, 762], fill=(220, 214, 200))
    return img.convert("RGB")


def _machine_box(d, x, y, s=0.45):
    """倉庫の棚に置く、売れ残りのリレー計算機。下端中央が x, y。"""
    _big_calc(d, x, y, s)


def soko(full=False):
    """内田洋行の倉庫。棚にリレー計算機。full=True で天井まで積み上がった状態。"""
    img = base((150, 150, 146), (116, 116, 112))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(120, 118, 112))
    d.line([(0, FLOOR), (W, FLOOR)], fill=(80, 80, 76), width=6)
    for x in range(0, W, 320):                                             # 天井の梁
        d.line([(x, 0), (x + 160, 90)], fill=(96, 96, 92), width=10)
    d.rectangle([0, 80, W, 100], fill=(96, 96, 92))
    shelves = ((60, 520), (720, 1200), (1400, 1860))
    levels = (300, 480, 660, 840)
    for x0, x1 in shelves:                                                 # 金属の棚
        for xx in (x0, x1):
            d.rectangle([xx, 200, xx + 16, FLOOR], fill=(70, 80, 96))
        for ly in levels:
            d.rectangle([x0, ly, x1 + 16, ly + 14], fill=(84, 94, 110))
    for (x0, x1) in shelves:
        span = x1 - x0
        n = max(2, span // 150)
        for li, ly in enumerate(levels):
            for k in range(n):
                if not full and (k + li) % 3 == 0:
                    continue
                _machine_box(d, x0 + 80 + k * (span - 80) / max(1, n - 1) * 0.86, ly, 0.42)
    if full:
        for x0, x1 in shelves:                                             # 棚の上にも積む
            for k in range(3):
                for j in range(2):
                    _machine_box(d, x0 + 90 + k * (x1 - x0 - 80) / 2.4, 200 - j * 90, 0.42)
        import random
        rnd = random.Random(3)
        for row in range(8):                                               # 床から天井まで段ボールの山
            y = FLOOR - row * 100
            for k in range(5 - row // 3):
                x = 560 + row * 18 + k * 170 + rnd.randint(-10, 10)
                d.rectangle([x, y - 96, x + 160, y], fill=(196, 160, 112), outline=(140, 108, 70), width=4)
                d.line([(x, y - 60), (x + 160, y - 60)], fill=(170, 136, 92), width=6)
    return img


def soko_yama():
    return soko(full=True)


def bunguten(kara=False):
    """昭和の文房具屋。奥の棚の真ん中の段に小さな電卓。kara=True で電卓の段が空っぽ。"""
    img = base((232, 222, 200), (206, 194, 170))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 120, 88), line=(128, 102, 74))
    d.rectangle([160, 120, 1760, 600], fill=(150, 112, 76), outline=(100, 74, 50), width=8)   # 奥の棚
    for y in (240, 360, 480):
        d.rectangle([160, y, 1760, y + 12], fill=(100, 74, 50))
    import random
    rnd = random.Random(5)
    pal = [(200, 60, 60), (60, 110, 190), (236, 196, 60), (70, 150, 90), (240, 240, 236)]
    for x in range(180, 1740, 26):                                         # 上の段: ノート
        if 700 < x < 1220:
            continue
        d.rectangle([x, 150, x + 20, 238], fill=rnd.choice(pal))
    for x in range(190, 1740, 14):                                         # 2段目: 鉛筆
        if 700 < x < 1220:
            continue
        h = rnd.randint(60, 100)
        d.rectangle([x, 358 - h, x + 7, 358], fill=rnd.choice(pal))
    for x in range(180, 1740, 60):                                         # 3段目: 消しゴムの箱
        d.rectangle([x, 440, x + 50, 478], fill=(236, 232, 220), outline=(60, 110, 190), width=4)
    d.rectangle([700, 130, 1220, 370], fill=(250, 236, 180), outline=(200, 60, 60), width=8)   # 真ん中: 電卓の段（明るい台紙）
    d.rectangle([706, 244, 1214, 256], fill=(100, 74, 50))
    if not kara:
        for row, y in enumerate((150, 268)):
            for k in range(5):
                _small_calc(d, 724 + k * 98, y, 0.76, body=(54, 58, 66) if (k + row) % 2 else (70, 120, 190))
    else:
        for x, y in ((760, 238), (1010, 238), (880, 358), (1110, 358)):    # 空いた箱が転がっているだけ
            d.polygon([(x, y), (x + 80, y), (x + 92, y - 44), (x - 12, y - 44)], fill=(214, 196, 160), outline=(150, 130, 96))
    d.rectangle([640, 660, 1280, 800], fill=(190, 210, 214), outline=(110, 90, 66), width=8)   # ガラスの陳列台
    d.rectangle([640, 800, 1280, FLOOR], fill=(130, 100, 72))
    for k in range(5):
        d.rectangle([680 + k * 120, 700, 760 + k * 120, 760], fill=rnd.choice(pal))
    return img


def bunguten_kara():
    return bunguten(kara=True)


def hamura(asa=False):
    """技術センターの会長室。夜は窓が暗く机の灯りだけ。asa=True で窓が白んで紙くずが増える。"""
    img = base((206, 208, 212), (176, 178, 184)) if asa else base((96, 100, 112), (66, 70, 80))
    d = _d(img)
    wood_floor(img, FLOOR, col=(130, 116, 100) if asa else (80, 72, 64), line=(110, 98, 84) if asa else (64, 58, 52))
    if asa:
        win = vgrad((1320, 420), (250, 214, 170), (196, 220, 240))
    else:
        win = vgrad((1320, 420), (20, 26, 52), (40, 48, 84))
    img.paste(win, (300, 120))
    d = _d(img)
    d.rectangle([300, 120, 1620, 540], outline=(60, 60, 64), width=12)
    for x in (630, 960, 1290):
        d.line([(x, 120), (x, 540)], fill=(60, 60, 64), width=8)
    if not asa:
        for x, y in ((380, 470), (520, 500), (700, 480), (1100, 490), (1400, 470), (1530, 505)):
            d.ellipse([x, y, x + 8, y + 8], fill=(255, 220, 140))
    else:
        d.ellipse([1380, 400, 1500, 520], fill=(255, 236, 190))
    d.rectangle([660, 660, 1260, 700], fill=(120, 96, 72))                  # 机
    d.rectangle([690, 700, 730, FLOOR], fill=(96, 76, 58))
    d.rectangle([1190, 700, 1230, FLOOR], fill=(96, 76, 58))
    d.line([(1160, 660), (1160, 560), (1100, 530)], fill=(40, 40, 44), width=8)   # 電気スタンド
    d.polygon([(1060, 520), (1130, 500), (1140, 550), (1080, 560)], fill=(50, 52, 58))
    _glow(img, 1060, 640, 200, (255, 214, 150), 110 if not asa else 50)
    d = _d(img)
    for k in range(4):                                                     # 紙の束と鉛筆
        d.rectangle([760 + k * 6, 640 - k * 6, 940 + k * 6, 656 - k * 6], fill=(246, 244, 236), outline=(170, 166, 156))
    for k in range(3):
        d.line([(980 + k * 22, 650), (1040 + k * 22, 620)], fill=(220, 180, 60), width=6)
    balls = ((800, 600), (1000, 610), (1210, 640), (560, 990), (640, 1010), (1300, 1000), (900, 1030)) if asa else ((820, 610), (1220, 640))
    for x, y in balls:                                                     # 丸めた紙
        d.ellipse([x, y, x + 46, y + 40], fill=(240, 238, 230), outline=(160, 156, 148), width=3)
    return img


def hamura_yoru():
    return hamura(asa=False)


def hamura_asa():
    return hamura(asa=True)


def hotel_haisen():
    """札幌の宿。計算機をばらして、配線と部品が座卓から畳一面に広がった状態。

    座卓の本体はキーと表示を外して中身がのぞく形にし、外したキーと表示は畳の上に置く。
    配線は座卓の縁から垂れて、畳の上を這わせる（壁の前で宙に浮かせない）。
    """
    img = hotel()
    d = _d(img)
    import random
    rnd = random.Random(11)
    d.rectangle([836, 476, 1084, 640], fill=(170, 176, 170), outline=(110, 116, 110), width=5)   # キーと表示を外した本体
    d.rectangle([862, 496, 1058, 624], fill=(46, 48, 46))
    for r in range(3):                                                     # のぞいているリレー
        for c in range(6):
            x, y = 874 + c * 30, 508 + r * 36
            d.rectangle([x, y, x + 20, y + 24], fill=(36, 36, 38))
            d.rectangle([x + 5, y + 3, x + 15, y + 18], fill=(184, 112, 62))
    cols = [(210, 60, 60), (240, 240, 236), (60, 110, 210), (236, 206, 60), (70, 170, 90),
            (150, 90, 180), (230, 140, 50), (160, 160, 160)]
    floor_top = FLOOR + 6
    for k in range(80):                                                    # 畳の上を這う配線（宙には浮かせない）
        c = rnd.choice(cols)
        x0 = rnd.randint(-60, W + 60)
        y0 = rnd.randint(floor_top, H)
        x1 = rnd.randint(-60, W + 60)
        y1 = rnd.randint(floor_top, H)
        xm = (x0 + x1) / 2 + rnd.randint(-160, 160)
        ym = rnd.randint(floor_top, H)
        d.line([(x0, y0), (xm, ym), (x1, y1)], fill=c, width=rnd.choice((3, 4, 5)), joint="curve")
    for k in range(26):                                                    # 外したリレー（畳の上）
        x, y = rnd.randint(80, W - 120), rnd.randint(floor_top + 10, H - 40)
        d.rectangle([x, y, x + 26, y + 30], fill=(36, 36, 38))
        d.rectangle([x + 6, y + 4, x + 20, y + 22], fill=(184, 112, 62))
    d.rectangle([1420, 960, 1700, 1050], fill=(170, 176, 170), outline=(110, 116, 110), width=4)  # 外したキーの部分
    for r in range(2):
        for c in range(5):
            d.rectangle([1442 + c * 50, 974 + r * 34, 1478 + c * 50, 998 + r * 34], fill=(230, 226, 214))
    d.rectangle([220, 970, 480, 1040], fill=(40, 44, 40), outline=(110, 116, 110), width=4)       # 外した表示の部分
    return img


def zashiki(yoru=False):
    """畳の座敷。床の間に掛け軸と白い花（遺影は描かない）。yoru=True で夜の灯りの別の絵。"""
    img = base((196, 186, 168), (160, 150, 134)) if not yoru else base((120, 108, 92), (78, 70, 62))
    d = ImageDraw.Draw(img, "RGBA")
    tatami_floor(img, FLOOR)
    d.rectangle([720, 120, 1200, FLOOR - 4], fill=(170, 156, 132) if not yoru else (112, 100, 84),
                outline=(96, 76, 56), width=12)                            # 床の間
    d.rectangle([700, 100, 1220, 130], fill=(96, 76, 56))
    d.rectangle([700, FLOOR - 70, 1220, FLOOR - 40], fill=(110, 84, 60))    # 床板
    sx = 900 if not yoru else 880
    d.rectangle([sx, 170, sx + 120, 640], fill=(232, 226, 210) if not yoru else (190, 182, 166))   # 掛け軸
    d.rectangle([sx - 10, 160, sx + 130, 176], fill=(80, 60, 44))
    d.rectangle([sx - 10, 634, sx + 130, 650], fill=(80, 60, 44))
    if not yoru:
        d.line([(sx + 40, 230), (sx + 60, 380), (sx + 50, 560)], fill=(60, 60, 60), width=8)   # 墨の一筆
        for x in (790, 1130):                                              # 白い菊
            d.rectangle([x - 18, 700, x + 18, FLOOR - 70], fill=(60, 70, 60))
            for k in range(7):
                fx, fy = x - 40 + (k % 4) * 26, 610 + (k // 4) * 40
                d.ellipse([fx, fy, fx + 34, fy + 34], fill=(246, 244, 236))
    else:
        d.ellipse([sx + 30, 260, sx + 90, 320], outline=(70, 66, 60), width=6)   # 丸の一筆
        d.rectangle([980, 760, 1040, FLOOR - 70], fill=(70, 80, 70))       # 白百合を一輪
        d.line([(1010, 760), (1010, 620)], fill=(70, 110, 70), width=6)
        d.polygon([(1010, 620), (980, 570), (1010, 590), (1040, 570)], fill=(246, 244, 236))
        d.rectangle([380, 600, 470, 760], fill=(236, 220, 180), outline=(96, 76, 56), width=6)   # 行灯
        d.rectangle([410, 760, 440, FLOOR], fill=(96, 76, 56))
    out = img
    if yoru:
        _glow(out, 425, 680, 260, (255, 210, 140), 120)
    return out.convert("RGB")


def zashiki_yoru():
    return zashiki(yoru=True)


def setsumei_2dai():
    """説明会の演台に、リレー式の81型と、研究中の電子式の電卓を並べた状態。"""
    img = setsumei()
    d = _d(img)
    d.rectangle([700, 560, 1220, 700], fill=(130, 100, 72), outline=(100, 76, 54), width=4)   # 広げた演台
    _big_calc(d, 820, 560, 0.62)                                           # 左: リレー式の81型
    x0, x1, y0, y1 = 950, 1190, 430, 560                                   # 右: 研究中の電子式
    d.rectangle([x0, y0, x1, y1], fill=(222, 214, 196), outline=(140, 132, 116), width=5)
    d.rectangle([x0 + 18, y0 + 14, x1 - 18, y0 + 50], fill=(30, 26, 24))
    for k in range(10):                                                    # 光る表示管
        cx = x0 + 30 + k * 19
        d.ellipse([cx, y0 + 21, cx + 11, y0 + 43], fill=(255, 150, 60))
    for r in range(3):
        for c in range(5):
            kx, ky = x0 + 34 + c * 38, y0 + 62 + r * 22
            d.rectangle([kx, ky, kx + 26, ky + 14], fill=(90, 92, 98))
    _glow(img, 1070, y0 + 32, 70, (255, 170, 90), 90)
    return img


def bowling():
    """1970年代のボウリング場。奥にピン、手前の小机に手書きのスコア用紙。"""
    img = base((70, 96, 110), (52, 70, 82))
    d = _d(img)
    d.rectangle([0, 0, W, 90], fill=(236, 140, 60))                        # 70年代のオレンジの天井帯
    back = 430
    d.rectangle([0, back - 120, W, back], fill=(26, 30, 36))               # ピンの奥の暗がり
    d.rectangle([0, back, W, H], fill=(196, 160, 112))                     # レーンの床
    vx = W / 2
    for i in range(-4, 5):                                                 # 遠近のレーンの溝
        xb = vx + i * 520
        xt = vx + i * 150
        d.line([(xt, back), (xb, H)], fill=(120, 96, 66), width=8)
    for lane in (-1, 0, 1):                                                # ピン（三角に10本）
        cx = vx + lane * 150 + 75 * (1 if lane >= 0 else -1) * 0 + (75 if lane == 0 else 0) - 75
        cx = vx + (lane - 0.5) * 150 + 75
        for row in range(4):
            for j in range(row + 1):
                px = cx + (j - row / 2) * 22
                py = back - 18 - (3 - row) * 12
                d.ellipse([px - 7, py - 22, px + 7, py], fill=(246, 244, 238))
                d.line([(px - 6, py - 15), (px + 6, py - 15)], fill=(200, 40, 40), width=2)
    for x, c in ((220, (40, 80, 160)), (300, (160, 40, 40)), (380, (30, 30, 30))):   # 球を戻す台
        d.ellipse([x, 700, x + 70, 770], fill=c)
    d.rectangle([180, 770, 480, 800], fill=(90, 90, 96))
    d.rectangle([780, 760, 1140, 800], fill=(120, 96, 72))                 # 手前の小机とスコア用紙
    d.rectangle([800, 790, 830, FLOOR], fill=(96, 76, 58))
    d.rectangle([1090, 790, 1120, FLOOR], fill=(96, 76, 58))
    d.polygon([(830, 700), (1090, 700), (1110, 762), (810, 762)], fill=(248, 246, 238), outline=(150, 146, 136))
    for k in range(1, 10):
        x = 830 + k * 26
        d.line([(x, 702), (x + 2, 760)], fill=(150, 146, 136), width=2)
    d.line([(822, 730), (1100, 730)], fill=(150, 146, 136), width=2)
    for k in range(6):                                                     # 書きなぐった数字の跡
        x = 838 + k * 26
        d.line([(x, 740), (x + 10, 752)], fill=(60, 60, 140), width=3)
    return img


def ousetsu():
    """1970年代の会社の応接室。壁の真ん中に丸い掛け時計、ソファと低い机。"""
    img = base((226, 216, 196), (198, 186, 164))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 92, 66), line=(100, 76, 54))
    d.rectangle([0, 600, W, FLOOR], fill=(150, 112, 76))                   # 腰の板張り
    for x in range(0, W, 120):
        d.line([(x, 600), (x, FLOOR)], fill=(128, 94, 62), width=3)
    cx, cy, r = 960, 300, 120                                              # 丸い掛け時計
    d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], fill=(110, 80, 52))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(248, 246, 238))
    import math
    for i in range(12):
        a = i / 12 * 2 * math.pi
        d.line([(cx + (r - 22) * math.sin(a), cy - (r - 22) * math.cos(a)),
                (cx + (r - 8) * math.sin(a), cy - (r - 8) * math.cos(a))], fill=(60, 56, 52), width=6)
    d.line([(cx, cy), (cx + 60, cy - 30)], fill=(40, 40, 40), width=8)
    d.line([(cx, cy), (cx - 10, cy - 90)], fill=(40, 40, 40), width=5)
    d.rounded_rectangle([640, 640, 1280, 780], radius=30, fill=(130, 70, 50))     # ソファ
    d.rounded_rectangle([620, 700, 1300, 840], radius=24, fill=(150, 82, 58))
    d.rectangle([760, 860, 1160, 900], fill=(90, 66, 46))                  # 低い机
    d.rectangle([780, 900, 800, FLOOR + 30], fill=(70, 52, 36))
    d.rectangle([1120, 900, 1140, FLOOR + 30], fill=(70, 52, 36))
    for x in (860, 1020):                                                  # 湯のみ
        d.rectangle([x, 830, x + 30, 860], fill=(236, 230, 214))
    return img


def gakki():
    """1970年代末の開発室。作業台に試作の鍵盤、棚にオシロスコープ。"""
    img = base((214, 218, 220), (186, 190, 194))
    d = _d(img)
    wood_floor(img, FLOOR, col=(140, 136, 128), line=(120, 116, 108))
    d.rectangle([560, 140, 1360, 480], fill=(196, 182, 150))               # 有孔ボード
    for y in range(160, 480, 30):
        for x in range(580, 1360, 30):
            d.ellipse([x, y, x + 6, y + 6], fill=(150, 136, 108))
    d.rectangle([600, 360, 1320, 380], fill=(110, 96, 80))                 # 棚
    d.rectangle([660, 240, 860, 360], fill=(80, 86, 92), outline=(50, 54, 58), width=4)   # オシロスコープ
    d.rectangle([680, 256, 800, 340], fill=(20, 40, 30))
    import math
    pts = [(684 + t, 298 - 26 * math.exp(-t / 40) * math.sin(t / 4)) for t in range(0, 112, 2)]
    d.line(pts, fill=(110, 255, 150), width=3)
    d.rectangle([1100, 250, 1220, 360], fill=(60, 56, 52))                 # スピーカー
    d.ellipse([1124, 270, 1196, 342], fill=(30, 28, 26))
    d.rectangle([600, 640, 1320, 680], fill=(130, 110, 86))                # 作業台
    d.rectangle([630, 680, 670, FLOOR], fill=(100, 84, 66))
    d.rectangle([1250, 680, 1290, FLOOR], fill=(100, 84, 66))
    kx0, kx1, ky0, ky1 = 680, 1240, 560, 640                               # 試作の鍵盤
    d.rectangle([kx0 - 20, ky0 - 30, kx1 + 20, ky1], fill=(70, 72, 78))
    n = 28
    w = (kx1 - kx0) / n
    for i in range(n):
        d.rectangle([kx0 + i * w, ky0, kx0 + (i + 1) * w - 2, ky1 - 4], fill=(246, 246, 242))
    for i in range(n - 1):
        if i % 7 in (0, 1, 3, 4, 5):
            bx = kx0 + (i + 1) * w - w * 0.3
            d.rectangle([bx, ky0, bx + w * 0.6, ky0 + 46], fill=(30, 30, 34))
    d.line([(1240, 600), (1300, 640), (1330, 700)], fill=(30, 30, 30), width=5)    # 配線
    return img


LOCATIONS.update({
    "cs_hotel_haisen": hotel_haisen,
    "cs_ima3": ima3, "cs_shousha_shisaku": shousha_shisaku, "cs_koba_haisen": koba_haisen,
    "cs_koba_yama": koba_yama, "cs_toko": toko, "cs_soko": soko, "cs_soko_yama": soko_yama,
    "cs_setsumei_denshi": setsumei_2dai, "cs_bunguten": bunguten, "cs_bunguten_kara": bunguten_kara,
    "cs_zashiki": zashiki, "cs_hamura_yoru": hamura_yoru, "cs_hamura_asa": hamura_asa,
    "cs_zashiki_yoru": zashiki_yoru, "cs_bowling": bowling, "cs_ousetsu": ousetsu, "cs_gakki": gakki,
})
CARDS += ["1974", "1988"]


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
        if only and f"cs_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"cs_card_{y}.png")
        print(f"生成完了: cs_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
