#!/usr/bin/env python3
"""カニカマの誕生・スギヨ回（56_カニカマの誕生 / slug=sugiyo-kanikama）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はあんぱん回（gen_anpan_bgs.py）と同じ。
実在メーカーの商標（ロゴ・店名・商品名の文字）は描かない。

実行: PYTHONPATH=. python scripts/gen_kanikama_bgs.py [名前...]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, glow, hanging_bulb, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)
RED = (220, 70, 56)


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


def _stick(d, x, y, w=150, h=26, red=True):
    """カニカマの棒（白い身に赤い表面）。"""
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=(248, 244, 236), outline=(200, 190, 180), width=2)
    if red:
        d.rounded_rectangle([x, y, x + w, y + h // 2], radius=h // 4, fill=RED)


def _flakes(d, x0, y0, x1, y1, n=40):
    """刻んだ白い身。"""
    for k in range(n):
        x = x0 + (k * 53) % (x1 - x0)
        y = y0 + (k * 37) % (y1 - y0)
        d.line([(x, y), (x + 26, y + 6)], fill=(248, 244, 236), width=7)


def _pack(d, x, y, w=130, h=90, flakes=False):
    """文字のないパック。flakes=True なら初期の刻みタイプ（1972〜73年）。"""
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=(236, 240, 244), outline=(160, 170, 180), width=3)
    if flakes:
        for k in range(10):
            xx = x + 14 + (k * 29) % (w - 40)
            yy = y + 16 + (k * 17) % (h - 30)
            d.line([(xx, yy), (xx + 22, yy + 5)], fill=RED if k % 3 == 0 else (248, 244, 236), width=7)
        return
    for k in range(3):
        _stick(d, x + 12, y + 14 + k * 24, w=w - 24, h=18)


# ------------------------------------------------------------ 現代
def ima():
    """現代の食卓。皿のカニカマと、酢の物の小鉢。"""
    img = base((236, 232, 222), (214, 208, 196))
    d = _d(img)
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    d = _d(img)
    _window(d, 700, 120, 1220, 420, sky=(176, 210, 232))
    d.rectangle([640, 580, 1280, 640], fill=(180, 150, 110))              # 机
    d.ellipse([720, 530, 980, 590], fill=(246, 246, 246), outline=(190, 190, 190), width=3)   # 皿
    for k in range(4):
        _stick(d, 760, 540 + k * 10, w=180, h=18)
    d.ellipse([1040, 510, 1200, 580], fill=(120, 150, 180), outline=(80, 100, 130), width=3)  # 小鉢
    _flakes(d, 1070, 520, 1170, 560, n=12)
    return img


def nanao():
    """能登・七尾の港。湾と小舟、家並み。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, 560), (176, 204, 226), (214, 220, 214)), (0, 0))
    img.paste(vgrad((W, H - 560), (80, 130, 150), (56, 100, 124)), (0, 560))
    d = _d(img)
    d.ellipse([-200, 380, 800, 680], fill=(100, 128, 96))
    d.ellipse([1300, 400, 2300, 700], fill=(96, 122, 94))
    for x0, h in ((900, 180), (1080, 220), (1260, 160)):
        d.rectangle([x0, 600 - h, x0 + 160, 600], fill=(120, 100, 80))
        d.polygon([(x0 - 16, 616 - h), (x0 + 80, 550 - h), (x0 + 176, 616 - h)], fill=(80, 70, 62))
    d.rectangle([860, 600, 1480, 640], fill=(170, 156, 126))
    for k in range(3):
        x = 300 + k * 520
        d.polygon([(x, 760), (x + 240, 760), (x + 210, 800), (x + 20, 800)], fill=(120, 90, 64))
    return img


def kamaboko():
    """図解用。竹に巻いたちくわ型と蒲の穂、下に板付きかまぼこ。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (236, 230, 214), (214, 206, 188)), (0, 0))
    d = _d(img)
    d.line([(760, 160), (760, 520)], fill=(110, 140, 80), width=8)      # 蒲の穂
    d.rounded_rectangle([736, 180, 784, 360], radius=24, fill=(120, 80, 50))
    d.line([(830, 330), (1180, 330)], fill=(170, 150, 90), width=10)    # 竹串
    d.rounded_rectangle([880, 290, 1120, 370], radius=40, fill=(200, 150, 90), outline=(140, 96, 56), width=4)
    for k in range(4):
        d.ellipse([900 + k * 55, 300, 930 + k * 55, 322], fill=(160, 110, 60))
    d.rectangle([800, 700, 1140, 740], fill=(200, 170, 120))            # 板
    d.chord([800, 560, 1140, 820], 180, 360, fill=(250, 244, 236), outline=(200, 190, 180), width=3)
    d.chord([800, 560, 1140, 820], 180, 360, outline=(236, 140, 150), width=10)
    d.polygon([(940, 420), (1000, 420), (970, 480)], fill=(150, 130, 100))   # 矢印
    return img


def chikuwa():
    """1950年代のちくわ工場。炭火の焼き台と、竹串のちくわ。"""
    img = base((190, 176, 152), (160, 146, 124))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 96, 70), line=(100, 80, 58))
    d = _d(img)
    d.rectangle([1180, 560, 1400, 700], fill=(70, 60, 54))              # 焼き台
    _glow(img, 1290, 560, 90, (255, 140, 60), 140)
    d = _d(img)
    for k in range(4):
        y = 530 + k * 8
        d.line([(1170, y), (1410, y)], fill=(170, 150, 90), width=5)
        d.rounded_rectangle([1210, y - 14, 1370, y + 10], radius=12, fill=(196, 140, 80))
    d.rectangle([620, 600, 880, 640], fill=(140, 110, 80))              # 台
    for k in range(3):
        d.rounded_rectangle([640 + k * 80, 570, 700 + k * 80, 600], radius=14, fill=(196, 140, 80))
    hanging_bulb(img, 960, ly=60)
    return img


def zukai():
    """図解用。魚→水さらし→砂糖を混ぜる→凍らせたすり身、をキャラの間に縦に並べる。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (34, 44, 60), (18, 24, 34)), (0, 0))
    d = _d(img)
    cx = 960
    d.ellipse([cx - 160, 110, cx + 120, 190], fill=(160, 170, 190))     # 魚
    d.polygon([(cx + 110, 150), (cx + 180, 110), (cx + 180, 190)], fill=(150, 160, 180))
    d.polygon([(cx - 20, 220), (cx + 20, 220), (cx, 256)], fill=(200, 200, 90))
    for k in range(8):                                                   # 水
        x = cx - 160 + k * 44
        d.ellipse([x, 280, x + 24, 316], fill=(120, 180, 230))
    d.polygon([(cx - 20, 340), (cx + 20, 340), (cx, 376)], fill=(200, 200, 90))
    for k in range(4):                                                   # 砂糖
        d.rectangle([cx - 140 + k * 70, 400, cx - 94 + k * 70, 446], fill=(250, 246, 230))
    d.polygon([(cx - 20, 476), (cx + 20, 476), (cx, 512)], fill=(200, 200, 90))
    d.rectangle([cx - 200, 560, cx + 200, 800], fill=(214, 236, 250), outline=(160, 200, 230), width=6)   # 凍ったすり身
    d.rectangle([cx - 170, 590, cx + 170, 770], fill=(236, 230, 222))
    return img


def jimusho():
    """1960〜70年代の事務所。机と黒電話。"""
    img = base((214, 206, 190), (186, 178, 162))
    d = _d(img)
    wood_floor(img, FLOOR, col=(130, 106, 80), line=(110, 90, 66))
    d = _d(img)
    _window(d, 700, 140, 1220, 440, sky=(176, 204, 226))
    for x in (200, 1480):
        d.rectangle([x, 640, x + 280, 680], fill=(120, 110, 100))
        d.rectangle([x + 20, 680, x + 40, 820], fill=(90, 84, 76))
        d.rectangle([x + 240, 680, x + 260, 820], fill=(90, 84, 76))
    d.rectangle([640, 620, 880, 660], fill=(120, 110, 100))
    d.rounded_rectangle([700, 580, 780, 620], radius=10, fill=(30, 30, 34))   # 黒電話
    d.rectangle([790, 560, 880, 618], fill=(250, 248, 240), outline=(170, 160, 150), width=2)   # ラベルの見本
    d.rectangle([790, 560, 880, 574], fill=RED)
    for k in range(3):
        d.rectangle([800, 584 + k * 10, 870 - k * 14, 588 + k * 10], fill=(150, 140, 130))
    d.rectangle([1190, 640, 1350, 668], fill=(120, 110, 100))                 # 小さな台
    d.rectangle([1206, 668, 1220, 820], fill=(90, 84, 76))
    d.rectangle([1320, 668, 1334, 820], fill=(90, 84, 76))
    d.ellipse([1196, 606, 1344, 646], fill=(246, 246, 246), outline=(190, 190, 190), width=3)   # 皿
    for k in range(3):
        _stick(d, 1216, 612 + k * 9, w=110, h=16)
    hanging_bulb(img, 480)
    return img


def _lab(img):
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 150, 150), line=(130, 130, 130))
    d = _d(img)
    d.rectangle([80, 200, 560, 480], fill=(230, 234, 238), outline=(150, 160, 170), width=6)    # 棚
    for k in range(5):
        x = 110 + k * 90
        d.rectangle([x, 380, x + 50, 470], fill=(200, 226, 240), outline=(120, 140, 160), width=3)
    d.rectangle([600, 600, 900, 650], fill=(200, 204, 210))              # 実験台
    return d


def kenkyu():
    """1970年の研究室。実験台に、透き通った人工クラゲのバット。"""
    img = base((226, 230, 234), (196, 200, 206))
    d = _lab(img)
    d.rectangle([668, 500, 888, 600], fill=(160, 170, 180), outline=(110, 120, 130), width=4)   # バット（x≒0.40）
    for k in range(7):
        y = 516 + k * 11
        d.line([(686, y), (870, y + 6)], fill=(230, 240, 250), width=7)
    d.rectangle([1260, 520, 1330, 600], fill=(200, 226, 240), outline=(120, 140, 160), width=3)  # ビーカー
    return img


def kenkyu2():
    """研究室のまな板。刻んだ失敗作。"""
    img = base((226, 230, 234), (196, 200, 206))
    d = _lab(img)
    d.rectangle([620, 540, 880, 600], fill=(236, 214, 170), outline=(160, 130, 90), width=3)    # まな板
    _flakes(d, 640, 552, 860, 590, n=18)
    return img


def zukai2():
    """図解用。アルギン酸の液をカルシウムの液に落として固める。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (34, 44, 60), (18, 24, 34)), (0, 0))
    d = _d(img)
    cx = 960
    d.polygon([(cx - 60, 120), (cx + 60, 120), (cx + 20, 240), (cx - 20, 240)], fill=(200, 200, 210))   # スポイト
    for k in range(4):                                                   # しずく
        d.ellipse([cx - 12, 280 + k * 60, cx + 12, 310 + k * 60], fill=(200, 230, 180))
    d.rectangle([cx - 240, 540, cx + 240, 820], fill=(90, 130, 170), outline=(200, 210, 220), width=6)   # 液
    for k in range(10):                                                  # 固まった粒
        x = cx - 200 + (k * 43) % 400
        y = 600 + (k * 29) % 180
        d.ellipse([x, y, x + 36, y + 36], fill=(220, 240, 220), outline=(170, 200, 170), width=3)
    return img


def koba():
    """1972年の工場。刻む機械と、トレーのかにあし。"""
    img = base((210, 210, 206), (180, 180, 176))
    d = _d(img)
    wood_floor(img, FLOOR, col=(150, 150, 146), line=(130, 130, 126))
    d = _d(img)
    d.rectangle([620, 420, 880, 640], fill=(170, 176, 184), outline=(100, 106, 114), width=5)   # 刻む機械
    d.rectangle([660, 460, 840, 520], fill=(90, 96, 104))
    d.rectangle([620, 640, 880, 680], fill=(120, 126, 134))
    _flakes(d, 640, 600, 860, 636, n=16)
    d.rectangle([1180, 560, 1400, 620], fill=(200, 200, 204))            # トレー（刻んだかにあし）
    _flakes(d, 1195, 568, 1385, 612, n=24)
    return img


def tsukiji():
    """築地市場。木箱と裸電球の並ぶ店先。"""
    img = base((150, 140, 126), (110, 104, 96))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(90, 90, 96))                       # 濡れた床
    for k in range(4):
        x = 120 + k * 460
        d.rectangle([x, 520, x + 360, 760], fill=(170, 134, 90), outline=(110, 84, 56), width=4)
        d.rectangle([x + 20, 470, x + 340, 530], fill=(220, 220, 214))
        for j in range(3):
            d.ellipse([x + 40 + j * 100, 480, x + 110 + j * 100, 520], fill=(160, 170, 190))
    d.rectangle([860, 660, 1060, 740], fill=(186, 150, 104), outline=(120, 90, 60), width=4)   # かにあしの木箱
    for k in range(4):
        _stick(d, 880, 672 + k * 16, w=160, h=16)
    for x in (380, 960, 1540):
        hanging_bulb(img, x, ly=100)
    return img


def tonya():
    """地方の問屋の倉庫。積まれた段ボール。"""
    img = base((200, 190, 170), (170, 160, 140))
    d = _d(img)
    wood_floor(img, FLOOR, col=(130, 106, 80), line=(110, 90, 66))
    d = _d(img)
    for r in range(3):
        for c in range(3):
            x, y = 80 + c * 170, FLOOR - (r + 1) * 130
            d.rectangle([x, y, x + 160, y + 120], fill=(190, 160, 110), outline=(130, 100, 64), width=4)
    for r in range(3):
        for c in range(2):
            x, y = 1500 + c * 170, FLOOR - (r + 1) * 130
            d.rectangle([x, y, x + 160, y + 120], fill=(190, 160, 110), outline=(130, 100, 64), width=4)
    hanging_bulb(img, 960, ly=80)
    return img


def ryoutei():
    """料理屋の板場。まな板に刻んだ赤と白の身。"""
    img = base((214, 200, 176), (184, 170, 148))
    d = _d(img)
    wood_floor(img, FLOOR, col=(120, 96, 70), line=(100, 80, 58))
    d = _d(img)
    d.rectangle([640, 560, 1280, 620], fill=(200, 176, 130))             # 板場の台
    d.rectangle([760, 520, 1060, 560], fill=(236, 214, 170), outline=(160, 130, 90), width=3)   # まな板
    for k in range(10):
        x = 780 + k * 26
        d.line([(x, 530), (x + 12, 550)], fill=RED if k % 2 else (248, 244, 236), width=7)
    d.polygon([(1100, 540), (1230, 530), (1230, 546), (1100, 552)], fill=(200, 204, 210))       # 包丁
    return img


def truck():
    """夜の荷さばき場。ライトを点けたトラック。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (14, 18, 34), (40, 40, 56)), (0, 0))
    d = _d(img)
    d.rectangle([0, 780, W, H], fill=(60, 60, 64))
    d.rectangle([1100, 420, 1700, 760], fill=(220, 220, 226))            # 荷台
    d.rectangle([1700, 520, 1880, 760], fill=(80, 120, 170))             # 運転席
    for x in (1200, 1500, 1780):
        d.ellipse([x - 50, 720, x + 50, 820], fill=(30, 30, 34))
    _glow(img, 1860, 700, 100, (255, 240, 180), 160)
    for k in range(3):
        _glow(img, 300 + k * 350, 120, 80, (255, 220, 150), 120)
    return img


def mise():
    """1970年代の店の冷蔵ケース。文字のないパック。"""
    img = base((230, 232, 234), (200, 204, 208))
    d = _d(img)
    wood_floor(img, FLOOR, col=(170, 170, 166), line=(150, 150, 146))
    d = _d(img)
    d.rectangle([600, 440, 1320, 700], fill=(200, 220, 230), outline=(140, 150, 160), width=6)
    for r in range(2):
        for c in range(4):
            _pack(d, 630 + c * 170, 460 + r * 115, w=150, h=100, flakes=True)
    return img


def hiroshima():
    """広島の工場。細い口の付いた機械。"""
    img = base((206, 200, 190), (176, 170, 160))
    d = _d(img)
    wood_floor(img, FLOOR, col=(140, 130, 116), line=(120, 110, 98))
    d = _d(img)
    d.rectangle([760, 300, 1100, 560], fill=(170, 176, 184), outline=(100, 106, 114), width=6)   # 機械
    d.polygon([(900, 560), (960, 560), (940, 640), (920, 640)], fill=(120, 126, 134))           # 口
    d.ellipse([900, 640, 960, 680], fill=(240, 226, 210))                 # 残った身
    d.rectangle([760, 680, 1100, 720], fill=(150, 150, 150))
    hanging_bulb(img, 480)
    return img


def zukai3():
    """図解用。シート→糸→束→赤いフィルム→切る、を縦に並べる。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (34, 44, 60), (18, 24, 34)), (0, 0))
    d = _d(img)
    cx = 960
    d.rectangle([cx - 220, 100, cx + 220, 150], fill=(248, 244, 236))    # シート
    d.polygon([(cx - 16, 170), (cx + 16, 170), (cx, 200)], fill=(200, 200, 90))
    for k in range(12):                                                  # 糸
        d.line([(cx - 220 + k * 38, 220), (cx - 200 + k * 38, 300)], fill=(248, 244, 236), width=6)
    d.polygon([(cx - 16, 320), (cx + 16, 320), (cx, 350)], fill=(200, 200, 90))
    d.rounded_rectangle([cx - 200, 370, cx + 200, 440], radius=30, fill=(248, 244, 236))      # 束
    d.polygon([(cx - 16, 460), (cx + 16, 460), (cx, 490)], fill=(200, 200, 90))
    d.rounded_rectangle([cx - 210, 510, cx + 210, 590], radius=34, fill=(248, 244, 236))
    d.rounded_rectangle([cx - 210, 510, cx + 210, 550], radius=20, fill=RED)                 # 赤いフィルム
    d.rectangle([cx - 220, 500, cx + 220, 600], outline=(120, 160, 220), width=4)
    d.polygon([(cx - 16, 620), (cx + 16, 620), (cx, 650)], fill=(200, 200, 90))
    for k in range(4):                                                   # 切ったもの
        _stick(d, cx - 230 + k * 120, 690, w=100, h=34)
    return img


def jougai():
    """築地の場外の通り。のれんと店先の棚。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (180, 196, 214), (214, 210, 200)), (0, 0))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(150, 146, 140))
    for k, x in enumerate((0, 460, 1280, 1640)):
        d.rectangle([x, 300, x + 380, 760], fill=(150, 124, 96))
        d.rectangle([x + 20, 340, x + 360, 420], fill=(60, 70, 110) if k % 2 else (120, 50, 50))   # のれん
        d.rectangle([x + 40, 600, x + 340, 640], fill=(200, 176, 130))                               # 棚
        for j in range(3):
            d.rectangle([x + 60 + j * 95, 560, x + 130 + j * 95, 600], fill=(236, 230, 214))
    d.rectangle([840, 660, 1040, 700], fill=(200, 176, 130), outline=(140, 116, 84), width=3)   # 台
    d.rectangle([860, 700, 876, 800], fill=(140, 116, 84))
    d.rectangle([1004, 700, 1020, 800], fill=(140, 116, 84))
    d.rectangle([860, 620, 1020, 662], fill=(236, 240, 244), outline=(160, 170, 180), width=2)   # 皿
    for k in range(2):
        _stick(d, 872, 626 + k * 16, w=136, h=14)
    return img


def noto():
    """今の能登の工場。海沿いの白い工場の建物。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, 560), (170, 204, 232), (214, 224, 232)), (0, 0))
    img.paste(vgrad((W, H - 560), (70, 130, 160), (50, 100, 130)), (0, 560))
    d = _d(img)
    d.ellipse([-200, 380, 900, 660], fill=(100, 130, 100))
    d.rectangle([700, 330, 1300, 620], fill=(236, 238, 240), outline=(170, 176, 184), width=6)
    d.polygon([(680, 340), (1000, 250), (1320, 340)], fill=(120, 130, 140))
    for k in range(5):
        d.rectangle([740 + k * 110, 400, 820 + k * 110, 460], fill=(150, 190, 220))
    d.rectangle([0, 620, W, 700], fill=(180, 176, 166))
    return img


def sekai():
    """暗い地に世界地図の点。海外への広がり。"""
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
    for cx, cy in ((1590, 420), (930, 300), (300, 330), (1030, 250), (1180, 260)):
        _glow(img, cx, cy, 60, (255, 160, 140), 160)
    return img


def yuugure():
    """夕暮れの能登の海。静かな場面で使う。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, 560), (70, 60, 100), (230, 150, 110)), (0, 0))
    img.paste(vgrad((W, H - 560), (110, 80, 90), (40, 36, 56)), (0, 560))
    d = _d(img)
    d.ellipse([860, 470, 1060, 670], fill=(250, 200, 140))
    img.paste(vgrad((W, H - 560), (110, 80, 90), (40, 36, 56)), (0, 560))
    d = _d(img)
    for k in range(10):
        y = 590 + k * 34
        half = 120 - k * 8
        d.line([(960 - half, y), (960 + half, y)], fill=(240, 180, 130), width=5)
    d.ellipse([-100, 500, 600, 640], fill=(50, 44, 60))
    return img


def kaoribako():
    """今の鮮魚売り場。氷の上に並ぶ高級なカニカマのパック。"""
    img = base((236, 240, 244), (210, 216, 222))
    d = _d(img)
    wood_floor(img, FLOOR, col=(180, 180, 176), line=(160, 160, 156))
    d = _d(img)
    d.rectangle([600, 500, 1320, 720], fill=(220, 236, 244), outline=(140, 160, 180), width=6)   # 氷のケース
    for c in range(4):
        x = 630 + c * 170
        d.rounded_rectangle([x, 540, x + 150, 640], radius=8, fill=(30, 30, 34))
        for k in range(5):
            d.line([(x + 20 + k * 24, 560), (x + 30 + k * 24, 620)], fill=RED, width=10)
            d.line([(x + 24 + k * 24, 566), (x + 32 + k * 24, 620)], fill=(248, 244, 236), width=4)
    return img


def gendai():
    """今のスーパーの棚。カニカマのパックとサラダ。"""
    img = base((244, 244, 240), (226, 226, 220))
    d = _d(img)
    wood_floor(img, FLOOR, col=(190, 180, 160), line=(170, 160, 140))
    d = _d(img)
    for row, y in enumerate((250, 450, 650)):
        d.rectangle([620, y + 100, 1300, y + 116], fill=(160, 160, 166))
        for k in range(4):
            if row == 2:
                d.ellipse([650 + k * 160, y + 20, 780 + k * 160, y + 100], fill=(120, 180, 90))   # サラダ
                _stick(d, 670 + k * 160, y + 50, w=90, h=16)
            else:
                _pack(d, 640 + k * 160, y + 5, w=140, h=90)
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
    "kk_ima": ima, "kk_nanao": nanao, "kk_kamaboko": kamaboko, "kk_chikuwa": chikuwa,
    "kk_zukai": zukai, "kk_jimusho": jimusho, "kk_kenkyu": kenkyu, "kk_kenkyu2": kenkyu2,
    "kk_zukai2": zukai2, "kk_koba": koba, "kk_tsukiji": tsukiji, "kk_tonya": tonya,
    "kk_ryoutei": ryoutei, "kk_truck": truck, "kk_mise": mise, "kk_hiroshima": hiroshima,
    "kk_zukai3": zukai3, "kk_jougai": jougai, "kk_noto": noto, "kk_sekai": sekai, "kk_yuugure": yuugure, "kk_kaoribako": kaoribako,
    "kk_gendai": gendai, "kk_shiryo": shiryo,
}

CARDS = ["1952", "1970", "1972", "1974"]


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
        if only and f"kk_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"kk_card_{y}.png")
        print(f"生成完了: kk_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
