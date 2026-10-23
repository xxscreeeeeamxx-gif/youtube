#!/usr/bin/env python3
"""「いまの話題」第2弾4本（2026-11-01〜04）の背景を生成する。

接頭辞: hk_（日立の家電とノジマ）/ ng_（年賀状の75年）/ tb_（東芝）/ sy_（西友とトライアル）
方針は gen_now_bgs.py と同じ。実在の会社のロゴ・社名の文字・製品の意匠は描かない。
差し替え用（_kara・_heiten・_shutter・_nesage・_sukunai・_akaji）は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now2_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, washitsu_1957, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import _boxes, _papers, _phone, _window, year_card  # noqa: E402
from scripts.gen_now_bgs import (FLOOR, TOY, _banner, _car, _d, _rgb, gekiyasu, gms, gms_kara,  # noqa: E402
                                 kaigi, mise_soto, yakuin)
from scripts.gen_sega_bgs import _chart, _flat_tv, _glow, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import saibansho as _sogo_saibansho  # noqa: E402

WHITE = (244, 244, 240)
LINE = (90, 92, 98)


# ---------------------------------------------------------------- 家電の部品
def _washer(d, x, y, s=1.0, drum=True, col=WHITE):
    """洗濯機（左下が x, y）。drum はドラム式（前に丸い扉）、そうでなければ縦型（上にふた）。"""
    w, h = 180 * s, 230 * s
    d.rounded_rectangle([x, y - h, x + w, y], radius=int(14 * s), fill=col, outline=LINE, width=3)
    if drum:
        cx, cy, r = x + w / 2, y - h * 0.48, 62 * s
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 210, 220), outline=LINE, width=4)
        d.ellipse([cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7], fill=(150, 170, 190))
        d.rectangle([x + 14 * s, y - h + 12 * s, x + w - 14 * s, y - h + 34 * s], fill=(210, 214, 220))
    else:
        d.rectangle([x + 6 * s, y - h, x + w - 6 * s, y - h + 26 * s], fill=(214, 218, 224), outline=LINE, width=2)
        d.rectangle([x + 30 * s, y - h + 40 * s, x + w - 30 * s, y - h + 70 * s], fill=(190, 200, 214))


def _fridge(d, x, y, s=1.0, col=(236, 238, 240)):
    """冷蔵庫（左下が x, y）。上下2つの扉。"""
    w, h = 170 * s, 380 * s
    d.rounded_rectangle([x, y - h, x + w, y], radius=int(10 * s), fill=col, outline=LINE, width=3)
    d.line([(x, y - h * 0.62), (x + w, y - h * 0.62)], fill=LINE, width=3)
    for yy in (y - h * 0.8, y - h * 0.4):
        d.rectangle([x + w - 26 * s, yy - 30 * s, x + w - 16 * s, yy + 30 * s], fill=(170, 174, 180))


def _aircon(d, x, y, s=1.0):
    """壁かけのエアコン（左上が x, y）。"""
    d.rounded_rectangle([x, y, x + 300 * s, y + 90 * s], radius=int(20 * s), fill=(250, 250, 250), outline=LINE, width=3)
    d.line([(x + 20 * s, y + 70 * s), (x + 280 * s, y + 70 * s)], fill=(180, 186, 194), width=4)


def _price(d, x, y, red=False):
    """値札（上の辺の中央が x, y）。文字は線だけ。"""
    col = (230, 40, 40) if red else (255, 236, 60)
    d.rectangle([x - 50, y, x + 50, y + 44], fill=col, outline=(120, 30, 20) if red else (150, 120, 20), width=3)
    d.line([(x - 34, y + 22), (x + 34, y + 22)], fill=(255, 255, 255) if red else (60, 40, 20), width=6)


def _card_stack(d, x, y, n=6, s=1.0):
    """はがきの束（左下が x, y）。"""
    for k in range(n):
        d.rectangle([x + k * 2, y - 14 * s - k * 6 * s, x + 90 * s + k * 2, y - k * 6 * s],
                    fill=(252, 250, 244), outline=(180, 170, 150), width=1)


def _bike(d, x, y, s=1.0, col=(214, 40, 40)):
    """配達用の赤いバイク（左下が x, y）。形だけ。"""
    for wx in (x + 30 * s, x + 170 * s):
        d.ellipse([wx - 32 * s, y - 64 * s, wx + 32 * s, y], fill=(40, 40, 44))
        d.ellipse([wx - 14 * s, y - 46 * s, wx + 14 * s, y - 18 * s], fill=(160, 160, 166))
    d.polygon([(x + 30 * s, y - 40 * s), (x + 90 * s, y - 110 * s), (x + 150 * s, y - 110 * s), (x + 170 * s, y - 40 * s)], fill=col)
    d.rectangle([x + 150 * s, y - 150 * s, x + 220 * s, y - 100 * s], fill=col, outline=(110, 20, 20), width=2)  # 後ろの箱
    d.line([(x + 80 * s, y - 110 * s), (x + 60 * s, y - 150 * s)], fill=(40, 40, 44), width=int(6 * s))


# ---------------------------------------------------------------- 共通
def heya2(kind):
    """今の部屋。kind=kaden は洗濯機とエアコン、nenga は机にはがきの束とスマホ、souzai はレジ袋と惣菜。"""
    img = _rgb(base((232, 228, 220), (216, 212, 204)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    _window(d, 760, 140, 1160, 420, sky=(200, 220, 236))
    _flat_tv(d, 1380, 360, 1800, 600, screen=(40, 80, 150))
    d.rectangle([1420, 620, 1760, 680], fill=(140, 106, 76))
    if kind == "kaden":
        _aircon(d, 260, 110, 1.0)
        _washer(d, 200, 700, 1.0, drum=True)
    else:
        d.rectangle([160, 640, 640, 700], fill=(150, 116, 84))
        if kind == "nenga":
            _card_stack(d, 220, 640, n=8)
            _card_stack(d, 340, 640, n=4)
            d.rounded_rectangle([480, 600, 540, 636], radius=6, fill=(30, 30, 34))
        elif kind == "souzai":
            d.polygon([(220, 640), (260, 540), (380, 540), (420, 640)], fill=(250, 250, 250), outline=(180, 180, 180))
            d.rectangle([450, 600, 600, 640], fill=(30, 30, 34))
            d.rectangle([460, 590, 590, 606], fill=(220, 230, 240, 180))
            d.rectangle([470, 612, 520, 632], fill=(200, 130, 50))
            d.rectangle([530, 612, 580, 632], fill=(250, 240, 220))
    return img


def kaigi_room(akaji=False, up=False):
    return kaigi(akaji=akaji, up=up)


# ---------------------------------------------------------------- 日立の家電
def omise(old=False):
    """町の電器屋（系列店）の店内。壁ぞいに冷蔵庫と洗濯機、テレビの棚、奥にカウンター。"""
    img = _rgb(base((238, 234, 224), (224, 220, 210)))
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    d = _d(img)
    d.rectangle([0, 60, W, 110], fill=(230, 120, 40))                                  # 店の帯（文字なし）
    for k in range(3):
        _fridge(d, 60 + k * 190, 700, 1.0, col=[(236, 238, 240), (220, 232, 236), (240, 230, 226)][k])
    for k in range(3):
        _washer(d, 1260 + k * 200, 700, 0.95, drum=not old and k != 1)
    d.rectangle([700, 200, 1220, 216], fill=(130, 100, 70))
    for k in range(3):
        _flat_tv(d, 720 + k * 170, 110, 860 + k * 170, 196, screen=[(40, 90, 170), (200, 80, 60), (60, 150, 90)][k])
    d.rectangle([760, 480, 1160, 560], fill=(150, 116, 84), outline=(110, 84, 60), width=4)   # カウンター
    d.rectangle([800, 440, 900, 480], fill=(60, 60, 66))
    _papers(d, 960, 470, n=2)
    return img


def omise_soto(shutter=False):
    """商店街の町の電器屋の外観。真ん中が電器屋（ウインドーに洗濯機とテレビ）、両隣も小さな店。
    shutter は両隣がシャッターを下ろしている。"""
    img = vgrad((W, H), (170, 204, 232), (226, 232, 236))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(150, 146, 140))
    for x0, kind in ((0, "l"), (660, "c"), (1300, "r")):
        x1 = x0 + 620
        d.rectangle([x0 + 10, 160, x1 - 10, 760], fill=(232, 222, 204) if kind != "c" else (240, 236, 226),
                    outline=(120, 110, 96), width=4)
        if kind == "c":
            d.rectangle([x0 + 10, 160, x1 - 10, 240], fill=(230, 120, 40))            # 看板（文字なし）
            d.rectangle([x0 + 50, 300, x1 - 50, 700], fill=(196, 216, 230), outline=(120, 120, 126), width=6)
            _washer(d, x0 + 90, 690, 0.9, drum=True)
            _fridge(d, x0 + 300, 690, 0.95)
            _flat_tv(d, x0 + 450, 420, x0 + 560, 500, screen=(40, 90, 170))
            for k in range(8):
                d.polygon([(x0 + 10 + k * 76, 250), (x0 + 86 + k * 76, 250), (x0 + 76 + k * 76, 290), (x0 + 20 + k * 76, 290)],
                          fill=(230, 120, 40) if k % 2 == 0 else (250, 250, 250))
        else:
            col = (180, 80, 70) if kind == "l" else (70, 110, 150)
            d.rectangle([x0 + 10, 160, x1 - 10, 230], fill=col)
            if shutter:
                d.rectangle([x0 + 50, 300, x1 - 50, 760], fill=(170, 172, 176), outline=(120, 120, 126), width=4)
                for r in range(18):
                    d.line([(x0 + 50, 320 + r * 24), (x1 - 50, 320 + r * 24)], fill=(140, 142, 146), width=3)
                d.rectangle([x0 + 220, 420, x1 - 220, 500], fill=(250, 250, 244), outline=(150, 150, 150), width=2)  # 貼り紙
            else:
                d.rectangle([x0 + 50, 300, x1 - 50, 760], fill=(200, 214, 224), outline=(120, 120, 126), width=6)
                rnd = random.Random(len(kind))
                for k in range(10):
                    d.rectangle([x0 + 80 + k * 48, 560, x0 + 116 + k * 48, 640], fill=rnd.choice(TOY))
    return img


def ryohan(nesage=False):
    """家電量販店の白物の売り場。洗濯機と冷蔵庫の列、上に値札。nesage は赤い値下げ札と垂れ幕だらけ。"""
    img = _rgb(base((246, 246, 248), (232, 232, 236)))
    wood_floor(img, FLOOR, col=(214, 214, 218), line=(198, 198, 204))
    d = _d(img)
    for k in range(6):
        d.rectangle([k * 330 + 60, 40, k * 330 + 220, 60], fill=(255, 255, 240))      # 天井の明かり
    for k in range(5):
        _fridge(d, 40 + k * 190, 560, 0.9, col=[(236, 238, 240), (210, 220, 230), (240, 236, 230), (60, 60, 66), (236, 238, 240)][k])
        _price(d, 117 + k * 190, 150, red=nesage and k % 2 == 0)
    for k in range(4):
        _washer(d, 1060 + k * 210, 560, 0.95, drum=k != 2)
        _price(d, 1146 + k * 210, 300, red=nesage)
    d.rectangle([0, 560, W, 580], fill=(200, 200, 206))
    if nesage:
        _banner(d, 640, 80, 1280, 170)
        rnd = random.Random(11)
        for k in range(10):
            _price(d, rnd.randint(80, W - 80), rnd.randint(380, 520), red=True)
    return img


def kaden_kojo(product="washer"):
    """家電の組立工場。コンベアに洗濯機（product=fridge は冷蔵庫）の本体、作業台。"""
    img = vgrad((W, H), (210, 214, 220), (186, 190, 196))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(160, 164, 170))
    for k in range(6):
        d.rectangle([k * 340 + 40, 60, k * 340 + 80, 100], fill=(250, 250, 236))
    d.rectangle([0, 640, W, 680], fill=(80, 84, 90))
    for k in range(8):
        d.line([(k * 250, 680), (k * 250, 740)], fill=(70, 74, 80), width=10)
    for k in range(7):
        if product == "fridge":
            _fridge(d, 50 + k * 270, 640, 0.85)
        else:
            _washer(d, 30 + k * 270, 640, 0.9, drum=True)
    for x in (300, 1000, 1600):
        d.rectangle([x, 380, x + 180, 400], fill=(120, 124, 130))
        d.line([(x + 90, 400), (x + 90, 460)], fill=(250, 180, 40), width=8)
    return img


def kaihatsu(product="washer"):
    """開発室。机にパソコンと図面、壁に図面、奥に試作の洗濯機（product=fridge は冷蔵庫）。"""
    img = _rgb(base((226, 230, 234), (212, 216, 222)))
    wood_floor(img, FLOOR, col=(150, 150, 156), line=(134, 134, 140))
    d = _d(img)
    for k in range(4):
        x = 120 + k * 260
        d.rectangle([x, 120, x + 220, 300], fill=(250, 250, 252), outline=(150, 156, 170), width=3)
        for r in range(5):
            d.line([(x + 20, 150 + r * 30), (x + 200 - r * 20, 150 + r * 30)], fill=(90, 120, 180), width=3)
        d.ellipse([x + 120, 200, x + 190, 270], outline=(90, 120, 180), width=3)
    d.rectangle([200, 600, 1100, 640], fill=(190, 194, 200))
    for k in range(3):
        d.rectangle([260 + k * 280, 480, 420 + k * 280, 590], fill=(40, 44, 50), outline=(90, 90, 96), width=4)
        d.rectangle([272 + k * 280, 492, 408 + k * 280, 578], fill=(60, 110, 170))
    if product == "fridge":
        _fridge(d, 1440, 700, 1.0, col=(226, 230, 236))
    else:
        _washer(d, 1400, 700, 1.15, drum=True, col=(226, 230, 236))
    d.rectangle([1380, 260, 1660, 290], fill=(250, 200, 60))                           # 試作の札
    return img


def happyou():
    """新製品の発表会の舞台。スポットライトと、台の上の洗濯機。"""
    img = vgrad((W, H), (24, 30, 50), (40, 46, 70))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(60, 64, 84))
    d.rectangle([300, 120, 1620, 600], fill=(30, 60, 120), outline=(90, 120, 180), width=6)   # 背景のスクリーン
    for k in range(5):
        d.line([(360, 200 + k * 70), (1560, 200 + k * 70)], fill=(70, 110, 180), width=4)
    d.rectangle([780, 560, 1140, 700], fill=(240, 240, 246), outline=(160, 160, 170), width=4)   # 台
    _washer(d, 860, 560, 1.1, drum=True, col=(250, 250, 252))
    _glow(img, 960, 380, 420, (255, 250, 220), 60)
    return img


# ---------------------------------------------------------------- 年賀状
def madoguchi(kara=False):
    """郵便局の窓口。カウンターとガラスの仕切り、後ろの棚に年賀はがきの箱。kara は棚がすかすか。"""
    img = _rgb(base((236, 240, 238), (222, 226, 224)))
    wood_floor(img, FLOOR, col=(196, 190, 176), line=(180, 174, 160))
    d = _d(img)
    d.rectangle([0, 60, W, 110], fill=(214, 40, 40))                                   # 帯（文字なし）
    rnd = random.Random(5)
    for r in range(3):
        y = 160 + r * 110
        d.rectangle([140, y + 90, 1780, y + 96], fill=(150, 150, 156))
        n = 6 if kara else 30
        for k in range(n):
            x = 160 + (rnd.randint(0, 1560) if kara else k * 54)
            d.rectangle([x, y + 30, x + 46, y + 90], fill=(252, 250, 244), outline=(214, 40, 40), width=3)
    d.rectangle([0, 520, W, 600], fill=(170, 150, 120), outline=(120, 100, 80), width=4)       # カウンター
    for k in range(4):
        d.rectangle([60 + k * 470, 420, 450 + k * 470, 520], fill=(214, 232, 240, 140), outline=(150, 160, 170), width=4)
    _card_stack(d, 300, 520, n=6)
    _card_stack(d, 1400, 520, n=4)
    return img


def kubun(kara=False):
    """年末の区分の作業場。壁ぞいの区分棚（細かい升目）と、はがきの山を入れた箱。kara は箱が少ない。"""
    img = vgrad((W, H), (214, 216, 212), (196, 198, 194))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(170, 168, 160))
    for k in range(6):
        d.rectangle([k * 340 + 40, 40, k * 340 + 80, 70], fill=(250, 250, 236))
    for k in range(3):                                                                  # 区分棚
        x0 = 80 + k * 620
        d.rectangle([x0, 120, x0 + 520, 560], fill=(150, 130, 100), outline=(100, 84, 64), width=4)
        for r in range(8):
            for c in range(10):
                cx, cy = x0 + 10 + c * 51, 130 + r * 53
                d.rectangle([cx, cy, cx + 44, cy + 46], fill=(120, 100, 76))
                if not kara or (r + c) % 5 == 0:
                    d.rectangle([cx + 6, cy + 18, cx + 38, cy + 46], fill=(252, 250, 244))
    rnd = random.Random(9)
    for k in range(3 if kara else 10):                                                 # はがきの箱
        x = 60 + k * 186
        d.rectangle([x, 620, x + 160, 700], fill=(60, 110, 180), outline=(30, 60, 110), width=3)
        if not kara:
            for j in range(rnd.randint(3, 6)):
                d.rectangle([x + 10, 610 - j * 8, x + 150, 620 - j * 8], fill=(252, 250, 244), outline=(200, 190, 170))
    return img


def kyukei():
    """局の休憩室。長机、ロッカー、壁のホワイトボードに下がっていくグラフ。"""
    img = _rgb(base((230, 232, 228), (216, 218, 214)))
    wood_floor(img, FLOOR, col=(170, 170, 166), line=(154, 154, 150))
    d = _d(img)
    for k in range(5):
        x = 60 + k * 110
        d.rectangle([x, 160, x + 100, 640], fill=(150, 160, 176), outline=(100, 110, 126), width=3)
        d.rectangle([x + 70, 380, x + 82, 420], fill=(90, 96, 110))
    d.rectangle([760, 120, 1500, 460], fill=(250, 250, 252), outline=(150, 150, 156), width=6)
    _chart(d, 800, 150, 1460, 430, [0.9, 0.86, 0.78, 0.68, 0.55, 0.36, 0.24], col=(220, 30, 40))
    d.rectangle([640, 620, 1700, 660], fill=(190, 160, 120))
    for k in range(5):
        d.rectangle([700 + k * 200, 660, 740 + k * 200, 720], fill=(80, 80, 86))
    d.rectangle([1560, 520, 1660, 620], fill=(250, 250, 250), outline=(150, 150, 156), width=3)   # ポット
    return img


def shuppatsu(sukunai=False):
    """元日の朝、局の前の出発式。紅白の幕、並んだ赤いバイクと配達車。sukunai はバイクが少ない。"""
    img = vgrad((W, H), (190, 212, 236), (236, 236, 232))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(150, 150, 150))
    d.rectangle([160, 160, 1760, 560], fill=(232, 230, 222), outline=(120, 120, 126), width=6)   # 局の建物
    d.rectangle([160, 160, 1760, 220], fill=(214, 40, 40))
    for k in range(32):                                                                 # 紅白の幕
        d.rectangle([160 + k * 50, 470, 210 + k * 50, 560], fill=(214, 40, 40) if k % 2 == 0 else (250, 250, 250))
    for k in range(5):
        d.rectangle([240 + k * 300, 260, 420 + k * 300, 400], fill=(190, 210, 226), outline=(120, 120, 126), width=4)
    n = 3 if sukunai else 8
    for k in range(n):
        _bike(d, 80 + k * 230, 880, 0.9)
    if not sukunai:
        d.rectangle([1500, 600, 1860, 720], fill=(214, 40, 40), outline=(110, 20, 20), width=4)   # 配達車
        for wx in (1560, 1800):
            d.ellipse([wx - 34, 690, wx + 34, 758], fill=(40, 40, 44))
    return img


def jutaku():
    """住宅街の朝。家の門と郵便受け。"""
    img = vgrad((W, H), (200, 220, 240), (240, 236, 228))
    d = _d(img)
    d.rectangle([0, 720, W, H], fill=(160, 158, 152))
    for k, x0 in enumerate((40, 680, 1320)):
        col = [(214, 200, 180), (236, 230, 220), (200, 210, 214)][k]
        d.rectangle([x0, 260, x0 + 560, 640], fill=col, outline=(110, 100, 90), width=4)
        d.polygon([(x0 - 30, 260), (x0 + 280, 120), (x0 + 590, 260)], fill=[(120, 70, 60), (60, 70, 90), (90, 90, 96)][k])
        d.rectangle([x0 + 60, 340, x0 + 220, 460], fill=(190, 210, 226), outline=(110, 100, 90), width=3)
        d.rectangle([x0, 600, x0 + 560, 720], fill=(170, 160, 150))                     # 塀
        d.rectangle([x0 + 380, 560, x0 + 460, 620], fill=(214, 40, 40), outline=(110, 20, 20), width=3)  # 郵便受け
        d.rectangle([x0 + 396, 576, x0 + 444, 584], fill=(40, 20, 20))
    return img


def mise_1949():
    """戦後の洋服の店先（1949年）。木の店構え、反物と吊るした洋服、セピア寄り。"""
    img = vgrad((W, H), (196, 184, 160), (214, 204, 184))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(130, 116, 96))
    d.rectangle([200, 140, 1720, 760], fill=(150, 120, 86), outline=(90, 70, 50), width=6)
    d.rectangle([200, 140, 1720, 230], fill=(90, 70, 50))
    d.rectangle([260, 280, 1660, 720], fill=(210, 196, 170), outline=(100, 80, 60), width=4)
    for k in range(6):                                                                 # 反物の棚
        x = 300 + k * 100
        d.rectangle([x, 330, x + 80, 640], fill=[(120, 80, 70), (80, 90, 120), (150, 140, 120), (90, 110, 90), (130, 100, 80), (100, 100, 110)][k])
    for k in range(3):                                                                 # 吊るした洋服
        x = 1050 + k * 200
        d.line([(x + 60, 300), (x + 60, 330)], fill=(60, 50, 40), width=4)
        d.polygon([(x, 340), (x + 120, 340), (x + 140, 600), (x - 20, 600)], fill=[(70, 70, 90), (110, 90, 70), (60, 80, 70)][k])
    return img


def shingikai():
    """1949年の会議室（審議会）。板張りの壁、緑の布をかけた長机。"""
    img = _rgb(base((176, 150, 116), (160, 134, 100)))
    wood_floor(img, FLOOR, col=(110, 86, 60), line=(90, 70, 50))
    d = _d(img)
    for k in range(10):
        d.line([(k * 200, 0), (k * 200, FLOOR)], fill=(150, 124, 92), width=4)
    _window(d, 760, 120, 1160, 400, sky=(210, 214, 206))
    d.rectangle([200, 600, 1720, 680], fill=(60, 110, 70), outline=(40, 80, 50), width=4)
    for k in range(6):
        _papers(d, 300 + k * 240, 590, n=2)
    return img


def chusen():
    """抽せん会の舞台。赤い幕、真ん中に回すくじの円盤。"""
    img = vgrad((W, H), (60, 20, 24), (90, 30, 34))
    d = _d(img)
    for k in range(20):
        d.rectangle([k * 100, 0, k * 100 + 60, 640], fill=(170, 30, 40))
    d.rectangle([0, 0, W, 90], fill=(200, 160, 60))
    d.rectangle([0, 640, W, H], fill=(120, 80, 50))
    cx, cy, r = 960, 420, 180                                                           # くじの円盤
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 240, 220), outline=(120, 90, 40), width=8)
    for k in range(10):
        import math
        a = k * math.pi / 5
        d.line([(cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a))], fill=(200, 60, 60), width=4)
    d.rectangle([cx - 20, cy + r, cx + 20, 640], fill=(120, 90, 40))
    return img


def tenji():
    """博物館の展示室。壁のガラスケースに並んだはがき、スポットライト。"""
    img = _rgb(base((60, 58, 56), (44, 42, 40)))
    wood_floor(img, FLOOR, col=(90, 80, 70), line=(76, 68, 60))
    d = _d(img)
    for k in range(4):
        x = 120 + k * 440
        d.rectangle([x, 180, x + 380, 560], fill=(30, 30, 32), outline=(140, 140, 146), width=4)
        for r in range(2):
            for c in range(3):
                d.rectangle([x + 30 + c * 116, 220 + r * 170, x + 120 + c * 116, 360 + r * 170],
                            fill=(244, 236, 214), outline=(180, 160, 120), width=2)
        _glow(img, x + 190, 160, 200, (255, 240, 200), 50)
    return img


# ---------------------------------------------------------------- 西友とトライアル
def reji():
    """スーパーのレジの前。並んだレジ台、奥にサービスカウンター。"""
    img = _rgb(base((244, 244, 240), (230, 230, 226)))
    wood_floor(img, FLOOR, col=(214, 210, 200), line=(198, 194, 184))
    d = _d(img)
    for k in range(6):
        d.rectangle([k * 330 + 60, 40, k * 330 + 220, 60], fill=(255, 255, 240))
    for k in range(4):
        x = 100 + k * 330
        d.rectangle([x, 520, x + 240, 600], fill=(220, 220, 226), outline=(120, 120, 126), width=3)
        d.rectangle([x + 150, 440, x + 230, 520], fill=(60, 60, 66))
        d.rectangle([x + 20, 200, x + 70, 250], fill=(230, 60, 50))                     # レジ番号の札（文字なし）
    d.rectangle([1440, 300, 1860, 560], fill=(236, 230, 214), outline=(120, 110, 96), width=4)   # サービスカウンター
    d.rectangle([1440, 240, 1860, 300], fill=(60, 120, 80))
    d.rectangle([1500, 340, 1620, 440], fill=(252, 252, 246), outline=(160, 160, 150), width=2)   # 貼り紙
    return img


def souzai():
    """惣菜の売り場。冷ケースに弁当と揚げ物のパック。"""
    img = _rgb(base((246, 244, 238), (232, 230, 224)))
    wood_floor(img, FLOOR, col=(214, 210, 200), line=(198, 194, 184))
    d = _d(img)
    d.rectangle([0, 80, W, 140], fill=(220, 120, 40))
    rnd = random.Random(12)
    for r in range(3):
        y = 200 + r * 130
        d.rectangle([60, y + 100, 1860, y + 110], fill=(150, 150, 156))
        for k in range(22):
            x = 80 + k * 82
            d.rectangle([x, y + 40, x + 70, y + 100], fill=(30, 30, 34))
            d.rectangle([x + 4, y + 50, x + 34, y + 94], fill=rnd.choice([(200, 130, 50), (230, 190, 90), (250, 240, 220)]))
            d.rectangle([x + 36, y + 50, x + 66, y + 94], fill=rnd.choice([(250, 240, 220), (90, 150, 70), (200, 60, 50)]))
        for k in range(5):
            _price(d, 200 + k * 380, y + 4, red=False)
    d.rectangle([0, 600, W, 640], fill=(200, 210, 220))
    return img


def soto_yoru():
    """郊外の総合スーパーの外観、夜。明かりがついて24時間開いている。"""
    img = mise_soto("gms")
    d = _d(img)
    d.rectangle([0, 0, W, H], fill=(10, 16, 40, 170))
    d.rectangle([840, 460, 1080, 640], fill=(255, 240, 180))
    for x in (400, 700, 1220, 1520):
        d.rectangle([x, 330, x + 120, 420], fill=(255, 236, 170, 220))
    _glow(img, 960, 560, 360, (255, 230, 160), 50)
    return img


def america_super():
    """アメリカの郊外の巨大スーパーの外観。横に長い箱型と、広い駐車場。"""
    img = vgrad((W, H), (120, 180, 236), (220, 232, 240))
    d = _d(img)
    d.rectangle([0, 560, W, H], fill=(120, 124, 130))
    for k in range(14):
        d.line([(k * 150, 620), (k * 150 + 40, H)], fill=(230, 230, 220), width=6)
    d.rectangle([40, 300, 1880, 560], fill=(214, 216, 220), outline=(90, 90, 96), width=6)
    d.rectangle([40, 300, 1880, 340], fill=(40, 90, 170))
    d.rectangle([820, 420, 1100, 560], fill=(140, 170, 196))
    for k, x in enumerate((120, 420, 1300, 1620)):
        _car(d, x, 860, 1.0, col=[(200, 40, 40), (220, 220, 226), (40, 60, 120), (120, 120, 126)][k])
    return img


def sy_kyukei():
    """店の休憩室。テレビとロッカー、長机。"""
    img = _rgb(base((230, 230, 226), (216, 216, 212)))
    wood_floor(img, FLOOR, col=(176, 172, 164), line=(160, 156, 148))
    d = _d(img)
    for k in range(5):
        x = 60 + k * 110
        d.rectangle([x, 160, x + 100, 640], fill=(160, 170, 160), outline=(110, 120, 110), width=3)
    _flat_tv(d, 1300, 140, 1700, 380, screen=(40, 80, 150))
    d.rectangle([640, 620, 1700, 660], fill=(190, 160, 120))
    for k in range(5):
        d.rectangle([700 + k * 200, 660, 740 + k * 200, 720], fill=(80, 80, 86))
    return img


# ---------------------------------------------------------------- 東芝
def tb_heya():
    """今の部屋。冷蔵庫とテレビ。"""
    img = heya2("none")
    d = _d(img)
    _fridge(d, 200, 700, 1.05)
    return img


def pc_kojo():
    """パソコンの組立工場（海外の委託先）。作業台に開いたノートパソコンが並ぶ。"""
    img = vgrad((W, H), (220, 224, 228), (196, 200, 206))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(170, 174, 180))
    for k in range(6):
        d.rectangle([k * 340 + 40, 50, k * 340 + 80, 80], fill=(250, 250, 236))
    for row, y in enumerate((420, 600)):
        d.rectangle([40, y, 1880, y + 30], fill=(120, 140, 160))
        for k in range(12):
            x = 70 + k * 152 + (row * 40)
            d.polygon([(x, y), (x + 110, y), (x + 120, y - 10), (x + 10, y - 10)], fill=(60, 60, 66))
            d.rectangle([x + 10, y - 90, x + 110, y - 12], fill=(40, 44, 52), outline=(90, 90, 96), width=2)
            d.rectangle([x + 16, y - 84, x + 104, y - 18], fill=(70, 120, 180))
    _boxes(d, 1600, 760, n=2, rows=2)
    return img


def getsurei(akaji=False):
    """社長月例の大会議室。コの字の長机、正面のスクリーンに数字の表。akaji はスクリーンが赤い。"""
    img = _rgb(base((206, 206, 210), (190, 190, 196)))
    wood_floor(img, FLOOR, col=(96, 84, 76), line=(80, 70, 62))
    d = _d(img)
    d.rectangle([520, 80, 1400, 440], fill=(240, 244, 250) if not akaji else (250, 220, 220), outline=(80, 80, 90), width=8)
    for r in range(6):
        y = 120 + r * 50
        d.line([(560, y), (1360, y)], fill=(170, 176, 190), width=3)
        for c in range(4):
            d.rectangle([700 + c * 170, y + 12, 800 + c * 170, y + 34],
                        fill=(220, 40, 40) if (akaji and (r + c) % 2 == 0) else (60, 70, 90))
    d.rectangle([200, 600, 1720, 650], fill=(110, 84, 60))                            # 長机（コの字の奥）
    d.rectangle([200, 600, 260, 760], fill=(110, 84, 60))
    d.rectangle([1660, 600, 1720, 760], fill=(110, 84, 60))
    for k in range(7):
        _papers(d, 300 + k * 200, 590, n=2)
    if akaji:
        d.rectangle([0, 0, W, H], fill=(160, 0, 0, 30))
    return img


def genpatsu():
    """海外の原子力発電所の建設現場。冷却塔、建屋、クレーン、手前に柵。"""
    img = vgrad((W, H), (170, 196, 222), (226, 228, 224))
    d = _d(img)
    d.rectangle([0, 680, W, H], fill=(170, 160, 140))
    d.polygon([(200, 680), (260, 300), (230, 160), (560, 160), (530, 300), (590, 680)], fill=(220, 220, 214), outline=(150, 150, 146))  # 冷却塔
    d.rectangle([760, 340, 1240, 680], fill=(200, 200, 204), outline=(120, 120, 126), width=4)  # 建屋
    d.ellipse([860, 220, 1140, 460], fill=(214, 214, 218), outline=(120, 120, 126), width=4)    # ドーム
    for x in (1380, 1660):                                                              # クレーン
        d.line([(x, 680), (x, 140)], fill=(240, 180, 40), width=16)
        d.line([(x - 200, 160), (x + 160, 160)], fill=(240, 180, 40), width=12)
        d.line([(x + 120, 160), (x + 120, 360)], fill=(60, 60, 60), width=4)
    for k in range(20):                                                                 # 柵
        d.line([(k * 100, 720), (k * 100, 820)], fill=(120, 120, 126), width=6)
    d.line([(0, 740), (W, 740)], fill=(120, 120, 126), width=6)
    return img


def kabunushi_kaijo():
    """株主総会の会場。舞台に長机、手前に並んだ椅子の背。"""
    img = vgrad((W, H), (60, 70, 96), (80, 90, 116))
    d = _d(img)
    d.rectangle([0, 0, W, 120], fill=(40, 46, 66))
    d.rectangle([200, 200, 1720, 420], fill=(30, 40, 70), outline=(90, 100, 130), width=6)   # 背景の幕
    d.rectangle([300, 400, 1620, 470], fill=(240, 240, 244), outline=(160, 160, 170), width=4)  # 舞台の長机
    for k in range(8):
        d.rectangle([380 + k * 150, 360, 440 + k * 150, 400], fill=(80, 80, 90))
    d.rectangle([0, 470, W, 520], fill=(110, 90, 70))                                  # 舞台の縁
    for r in range(3):                                                                  # 客席の背
        for k in range(16):
            x = 20 + k * 120 + (r % 2) * 60
            y = 640 + r * 90
            d.rounded_rectangle([x, y, x + 96, y + 70], radius=10, fill=(150, 40, 50), outline=(90, 20, 30), width=3)
    return img


def shoken():
    """株価のボードのある部屋。暗い壁に、緑と赤の数字の行。"""
    img = vgrad((W, H), (20, 24, 34), (34, 38, 50))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(50, 54, 64))
    d.rectangle([140, 100, 1780, 560], fill=(8, 10, 16), outline=(80, 90, 110), width=6)
    rnd = random.Random(21)
    for r in range(8):
        y = 130 + r * 54
        for c in range(6):
            x = 180 + c * 265
            d.rectangle([x, y, x + 120, y + 30], fill=(220, 220, 230))
            d.rectangle([x + 140, y, x + 230, y + 30], fill=rnd.choice([(40, 200, 90), (230, 50, 50)]))
    return img


LOCATIONS = {
    # 日立の家電とノジマ
    "hk_heya": lambda: heya2("kaden"), "hk_omise": omise, "hk_omise_soto": omise_soto,
    "hk_omise_soto_shutter": lambda: omise_soto(shutter=True), "hk_ryohan": ryohan,
    "hk_ryohan_nesage": lambda: ryohan(nesage=True), "hk_chanoma": washitsu_1957, "hk_kojo": kaden_kojo,
    "hk_kaihatsu": kaihatsu, "hk_happyou": happyou, "hk_kaiken": _sega_kaiken, "hk_kaigi": kaigi,
    "hk_kaigi_akaji": lambda: kaigi(akaji=True), "hk_yakuin": lambda: yakuin(), "hk_gendai": _sega_gendai,
    # 年賀状の75年
    "ng_heya": lambda: heya2("nenga"), "ng_madoguchi": madoguchi, "ng_madoguchi_kara": lambda: madoguchi(kara=True),
    "ng_kubun": kubun, "ng_kubun_kara": lambda: kubun(kara=True), "ng_kyukei": kyukei,
    "ng_shuppatsu": shuppatsu, "ng_shuppatsu_sukunai": lambda: shuppatsu(sukunai=True), "ng_jutaku": jutaku,
    "ng_mise_1949": mise_1949, "ng_shingikai": shingikai, "ng_chusen": chusen, "ng_tenji": tenji,
    "ng_kaiken": _sega_kaiken, "ng_kaigi": kaigi, "ng_kaigi_akaji": lambda: kaigi(akaji=True), "ng_gendai": _sega_gendai,
    # 西友とトライアル
    "sy_heya": lambda: heya2("souzai"), "sy_uriba": gms, "sy_uriba_kara": gms_kara, "sy_reji": reji,
    "sy_souzai": souzai, "sy_soto": lambda: mise_soto("gms"), "sy_soto_heiten": lambda: mise_soto("gms", True),
    "sy_soto_yoru": soto_yoru, "sy_trial": gekiyasu, "sy_america": america_super, "sy_kaigi": kaigi,
    "sy_kaigi_akaji": lambda: kaigi(akaji=True), "sy_kaigi_up": lambda: kaigi(up=True), "sy_kyukei": sy_kyukei,
    "sy_kaiken": _sega_kaiken, "sy_yakuin": lambda: yakuin(), "sy_gendai": _sega_gendai,
    # 東芝のチャレンジ
    "tb_heya": tb_heya, "tb_sekkei": lambda: kaihatsu("fridge"), "tb_kojo": lambda: kaden_kojo("fridge"),
    "tb_pc_kojo": pc_kojo, "tb_getsurei": getsurei, "tb_getsurei_akaji": lambda: getsurei(akaji=True),
    "tb_genpatsu": genpatsu, "tb_kabunushi": kabunushi_kaijo, "tb_shoken": shoken, "tb_houtei": _sogo_saibansho,
    "tb_ryohan": ryohan, "tb_kaiken": _sega_kaiken, "tb_kaigi": kaigi, "tb_kaigi_akaji": lambda: kaigi(akaji=True),
    "tb_kaigi_up": lambda: kaigi(up=True), "tb_yakuin": lambda: yakuin(), "tb_gendai": _sega_gendai,
}

# 年号カード（台本ができてから埋める）。接頭辞ごとに "hk_card_2023" のように作る
CARDS = {"hk": ["1959", "1982", "2009", "2023", "2026"], "ng": ["1949", "1993", "2024", "2025", "2026"], "tb": ["2015", "2016", "2017", "2020", "2023", "2024", "2026"], "sy": ["1963", "2002", "2008", "2021", "2025", "2026"]}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for pre, years in CARDS.items():
        for y in years:
            nm = f"{pre}_card_{y}"
            if only and nm not in only:
                continue
            year_card(f"{y}年").save(OUT / f"{nm}.png")
            print(f"生成完了: {nm}.png")
