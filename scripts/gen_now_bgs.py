#!/usr/bin/env python3
"""「いまの話題」4本（2026-10-28〜31）の背景を生成する。

接頭辞: tr_（日本トイザらス）/ ns_（日産）/ sv_（セブン&アイ）/ hd_（ホンダのEV撤回）
方針はこれまでの回と同じ。実在の会社のロゴ・社名の文字・車種の意匠は描かない。
店や車は「色と形」だけで見せ、差し替え用（_kara・_heiten・_teishi・_akaji）は元の絵に要素を足す。

実行: PYTHONPATH=. python scripts/gen_now_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import ImageDraw, ImageFilter  # noqa: E402

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import _boxes, _papers, _phone, _window, year_card  # noqa: E402
from scripts.gen_sega_bgs import _chart, _flat_tv, _glow, _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import saibansho as _sogo_saibansho, kokkai as _sogo_kokkai  # noqa: E402

FLOOR = int(H * 0.86)
TOY = [(230, 60, 60), (40, 120, 220), (250, 200, 40), (60, 170, 90), (240, 130, 30), (150, 80, 200)]


def _d(img):
    return ImageDraw.Draw(img, "RGBA")


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


def _banner(d, x0, y0, x1, y1, col=(220, 30, 40)):
    """赤い垂れ幕（文字は描かない。白い線で文字があるように見せる）。"""
    d.rectangle([x0, y0, x1, y1], fill=col, outline=(120, 10, 20), width=4)
    for k in range(3):
        y = y0 + (y1 - y0) * (0.25 + k * 0.25)
        d.line([(x0 + 20, y), (x1 - 20, y)], fill=(255, 240, 240), width=8)


def _car(d, x, y, s=1.0, col=(200, 200, 206)):
    """横向きの乗用車（左下が x, y）。車種の形は描かない。"""
    d.rounded_rectangle([x, y - 60 * s, x + 260 * s, y - 14 * s], radius=int(16 * s), fill=col, outline=(60, 60, 66), width=3)
    d.polygon([(x + 60 * s, y - 60 * s), (x + 95 * s, y - 100 * s), (x + 185 * s, y - 100 * s), (x + 215 * s, y - 60 * s)],
              fill=col, outline=(60, 60, 66))
    d.polygon([(x + 75 * s, y - 62 * s), (x + 102 * s, y - 92 * s), (x + 140 * s, y - 92 * s), (x + 140 * s, y - 62 * s)],
              fill=(150, 190, 220))
    d.polygon([(x + 148 * s, y - 62 * s), (x + 148 * s, y - 92 * s), (x + 180 * s, y - 92 * s), (x + 202 * s, y - 62 * s)],
              fill=(150, 190, 220))
    for wx in (x + 55 * s, x + 205 * s):
        d.ellipse([wx - 26 * s, y - 40 * s, wx + 26 * s, y + 12 * s], fill=(30, 30, 34))
        d.ellipse([wx - 12 * s, y - 26 * s, wx + 12 * s, y - 2 * s], fill=(150, 150, 156))


# ---------------------------------------------------------------- 共通の場所
def heya(kind="toy"):
    """今の部屋。kind=toy はおもちゃ箱、car は机に車の鍵、conbini はレジ袋とおにぎり。"""
    img = _rgb(base((232, 228, 220), (216, 212, 204)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    _window(d, 760, 140, 1160, 420, sky=(200, 220, 236))
    _flat_tv(d, 1380, 360, 1800, 600, screen=(40, 80, 150))
    d.rectangle([1420, 620, 1760, 680], fill=(140, 106, 76))
    d.rectangle([160, 640, 640, 700], fill=(150, 116, 84))
    if kind == "toy":
        d.rectangle([220, 560, 420, 640], fill=(240, 200, 60), outline=(150, 110, 20), width=4)
        for k in range(5):
            d.rectangle([236 + k * 34, 520 + (k % 2) * 14, 262 + k * 34, 560], fill=TOY[k])
    elif kind == "car":
        d.ellipse([300, 610, 340, 640], fill=(40, 40, 46))
        d.rectangle([336, 618, 380, 630], fill=(180, 180, 186))
    elif kind == "conbini":
        d.polygon([(260, 640), (300, 540), (420, 540), (460, 640)], fill=(250, 250, 250), outline=(180, 180, 180))
        d.polygon([(480, 640), (520, 590), (560, 640)], fill=(250, 250, 246), outline=(60, 60, 60))
        d.polygon([(492, 640), (520, 606), (548, 640)], fill=(30, 30, 34))
    return img


def kaigi(akaji=False, up=False):
    """取締役会・会議室。長机とボードのグラフ。akaji は赤く急落、up は上がっていく。"""
    img = _rgb(base((214, 212, 206), (198, 196, 190)))
    wood_floor(img, FLOOR, col=(106, 96, 86), line=(88, 80, 72))
    d = _d(img)
    pts = [0.9, 0.85, 0.6, 0.35, 0.2, 0.08] if akaji else ([0.1, 0.2, 0.35, 0.55, 0.75, 0.95] if up else [0.5, 0.6, 0.68, 0.72, 0.7, 0.66])
    _chart(d, 560, 110, 1360, 500, pts, col=(220, 30, 40) if akaji else (40, 90, 200))
    if akaji:
        d.rectangle([560, 110, 1360, 500], fill=(220, 40, 40, 50))
    d.rectangle([300, 640, 1620, 700], fill=(90, 70, 56))
    for k in range(6):
        d.rectangle([360 + k * 210, 600, 420 + k * 210, 640], fill=(60, 60, 66))
    _papers(d, 600, 630, n=3)
    _papers(d, 1100, 630, n=2)
    return img


def yakuin(view=(196, 214, 230), city=True):
    """本社の役員室。ガラス張りの窓に都市の眺め。"""
    img = _rgb(base((200, 204, 210), (186, 190, 196)))
    wood_floor(img, FLOOR, col=(96, 74, 56), line=(80, 60, 46))
    d = _d(img)
    d.rectangle([120, 90, 1800, 520], fill=view, outline=(90, 94, 100), width=10)
    for k in range(1, 4):
        d.line([(120 + k * 420, 90), (120 + k * 420, 520)], fill=(90, 94, 100), width=8)
    if city:
        rnd = random.Random(3)
        for k in range(16):
            x0 = 140 + k * 104
            top = 280 + rnd.randint(-120, 120)
            d.rectangle([x0, top, x0 + 84, 520], fill=(130, 144, 166))
        d.ellipse([1500, 230, 1700, 430], outline=(160, 170, 190), width=12)       # 観覧車（みなとみらい風）
    d.rectangle([600, 650, 1320, 704], fill=(70, 50, 36))
    _papers(d, 700, 640, n=3)
    _phone(d, 1200, 580, 0.6)
    return img


# ---------------------------------------------------------------- 店
def omocha_ten(kara=False):
    """大型のおもちゃ専門店の中。高い棚にカラフルな箱がびっしり。kara は棚が空で赤い垂れ幕。"""
    img = _rgb(base((236, 236, 240), (222, 222, 228)))
    wood_floor(img, FLOOR, col=(200, 200, 204), line=(184, 184, 190))
    d = _d(img)
    rnd = random.Random(1)
    for side, x0 in (("l", 40), ("r", 1180)):
        for r in range(6):
            y = 120 + r * 100
            d.rectangle([x0, y + 84, x0 + 700, y + 92], fill=(150, 150, 160))
            n = 2 if kara else 14
            for k in range(n):
                x = x0 + (rnd.randint(0, 640) if kara else k * 50)
                h = rnd.randint(50, 84)
                d.rectangle([x, y + 84 - h, x + 44, y + 84], fill=rnd.choice(TOY), outline=(60, 60, 70))
    d.rectangle([760, 100, 1160, 160], fill=(40, 120, 220))                           # 通路の案内板（文字なし）
    if kara:
        _banner(d, 720, 200, 1200, 320)
    else:
        _person_line(d, 820, FLOOR + 30, 3, 1.1)
    return img


def omocha_ten_kara():
    return omocha_ten(kara=True)


def mise_soto(kind="toy", heiten=False):
    """郊外の大型店と駐車場。kind=toy は青い壁、gms は白い箱型。heiten はシャッターと赤い垂れ幕、車も無い。"""
    img = vgrad((W, H), (160, 200, 236), (220, 232, 240))
    d = _d(img)
    d.rectangle([0, 640, W, H], fill=(120, 124, 130))
    for k in range(12):
        d.line([(k * 170, 700), (k * 170 + 60, H)], fill=(230, 230, 220), width=6)    # 駐車場の白線
    wall = (40, 90, 200) if kind == "toy" else (236, 236, 232)
    d.rectangle([260, 260, 1660, 640], fill=wall, outline=(80, 80, 90), width=6)
    d.rectangle([260, 220, 1660, 280], fill=(250, 200, 40) if kind == "toy" else (220, 60, 50))
    d.rectangle([840, 460, 1080, 640], fill=(120, 160, 190) if not heiten else (150, 150, 156))
    if heiten:
        for r in range(8):
            d.line([(840, 470 + r * 22), (1080, 470 + r * 22)], fill=(120, 120, 126), width=4)
        _banner(d, 380, 320, 760, 420)
        _banner(d, 1160, 320, 1540, 420)
    else:
        for k, x in enumerate((180, 520, 1240, 1600)):
            _car(d, x, 900, 1.0, col=[(200, 40, 40), (220, 220, 226), (40, 60, 120), (120, 120, 126)][k])
    return img


def mise_soto_heiten():
    return mise_soto("toy", True)


def denki_ryohan():
    """家電量販店の中。壁一面のテレビと、奥におもちゃの棚。"""
    img = _rgb(base((240, 240, 244), (226, 226, 232)))
    wood_floor(img, FLOOR, col=(210, 210, 214), line=(194, 194, 200))
    d = _d(img)
    for r in range(3):
        for c in range(6):
            _flat_tv(d, 80 + c * 200, 110 + r * 150, 250 + c * 200, 220 + r * 150,
                     screen=[(40, 90, 170), (200, 80, 60), (60, 150, 90)][(r + c) % 3])
    rnd = random.Random(4)
    for r in range(4):
        y = 180 + r * 110
        d.rectangle([1360, y + 90, 1840, y + 96], fill=(150, 150, 160))
        for k in range(9):
            d.rectangle([1370 + k * 52, y + 30, 1414 + k * 52, y + 90], fill=rnd.choice(TOY))
    d.rectangle([1360, 120, 1840, 170], fill=(250, 200, 40))
    return img


def butsuryu():
    """ネット通販の物流倉庫。ベルトコンベアに段ボールが流れる。"""
    img = vgrad((W, H), (196, 198, 202), (170, 172, 176))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(150, 152, 156))
    for k in range(5):
        d.line([(0, 90 + k * 30), (W, 90 + k * 30)], fill=(140, 142, 146), width=6)
    d.rectangle([0, 560, W, 600], fill=(60, 60, 66))
    for k in range(14):
        d.rectangle([20 + k * 140, 500, 120 + k * 140, 560], fill=(206, 168, 112), outline=(120, 90, 60), width=3)
    for x0 in (80, 1400):
        _boxes(d, x0, 480, n=4, rows=3)
    return img


def gekiyasu():
    """今の激安の総合ディスカウント店の中。天井まで商品、手書き風の黄色い札がびっしり。"""
    img = _rgb(base((250, 236, 120), (240, 220, 100)))
    wood_floor(img, FLOOR, col=(200, 190, 170), line=(184, 174, 156))
    d = _d(img)
    rnd = random.Random(7)
    for r in range(7):
        y = 60 + r * 96
        d.rectangle([0, y + 80, W, y + 86], fill=(120, 110, 90))
        for k in range(40):
            x = k * 48 + rnd.randint(0, 6)
            d.rectangle([x, y + 30, x + 40, y + 80], fill=rnd.choice(TOY + [(240, 240, 240)]))
        for k in range(6):
            x = rnd.randint(0, W - 120)
            d.rectangle([x, y + 4, x + 110, y + 30], fill=(255, 240, 40), outline=(200, 30, 30), width=3)
    return img


def america_mise():
    """冬のアメリカの大型店の外観（雪）。"""
    img = mise_soto("toy")
    d = _d(img)
    rnd = random.Random(2)
    for k in range(260):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 255, 220))
    d.rectangle([0, 640, W, 700], fill=(240, 244, 248))
    return img


# ---------------------------------------------------------------- 車
def kojo_line(teishi=False):
    """自動車の組立工場。ラインに車体、両側にロボットのアーム。teishi はラインが止まって暗く、車体も無い。"""
    img = vgrad((W, H), (200, 206, 214), (176, 182, 190)) if not teishi else vgrad((W, H), (40, 44, 52), (60, 64, 72))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(150, 154, 160) if not teishi else (50, 52, 58))
    for k in range(6):
        d.rectangle([k * 340 + 40, 60, k * 340 + 80, 100], fill=(250, 250, 236) if not teishi else (70, 70, 70))
    d.rectangle([0, 660, W, 700], fill=(90, 94, 100))
    if not teishi:
        for k in range(5):
            _car(d, 60 + k * 380, 680, 1.1, col=(236, 236, 240))
    for k in range(4):                                                              # ロボットのアーム
        x = 230 + k * 440
        col = (250, 160, 30) if not teishi else (90, 80, 60)
        d.rectangle([x - 30, 520, x + 30, 660], fill=col)
        d.line([(x, 520), (x + 80, 420), (x + 150, 470)], fill=col, width=24)
    if teishi:
        _glow(img, 960, 80, 300, (255, 230, 160), 40)
    return img


def kojo_teishi():
    return kojo_line(teishi=True)


def showroom(kara=False):
    """自動車の販売店のショールーム。ガラス越しの車2台。kara は車が無く、がらんとしている。"""
    img = vgrad((W, H), (236, 240, 244), (220, 226, 232))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(210, 214, 220))
    d.rectangle([80, 100, 1840, 560], fill=(200, 222, 240), outline=(140, 150, 160), width=8)
    for k in range(1, 5):
        d.line([(80 + k * 352, 100), (80 + k * 352, 560)], fill=(140, 150, 160), width=6)
    if not kara:
        _car(d, 280, 800, 1.5, col=(200, 30, 40))
        _car(d, 1100, 800, 1.5, col=(230, 230, 236))
    d.rectangle([860, 640, 1060, 720], fill=(240, 240, 244), outline=(170, 170, 176))
    return img


def america_lot(chargers=False):
    """アメリカの販売店の駐車場。在庫の車がずらり。chargers は空いた充電器の列。"""
    img = vgrad((W, H), (150, 196, 240), (230, 236, 240))
    d = _d(img)
    d.rectangle([0, 520, W, H], fill=(130, 134, 140))
    if chargers:
        for k in range(8):
            x = 120 + k * 220
            d.rounded_rectangle([x, 520, x + 70, 720], radius=12, fill=(240, 240, 244), outline=(80, 80, 86), width=4)
            d.rectangle([x + 14, 560, x + 56, 610], fill=(40, 140, 220))
            d.line([(x + 70, 640), (x + 120, 760)], fill=(30, 30, 34), width=8)
            d.line([(x + 150, 730), (x + 150, 900)], fill=(250, 250, 250), width=6)
    else:
        rnd = random.Random(5)
        for r in range(3):
            for k in range(8):
                _car(d, k * 240 - 20 + r * 60, 650 + r * 130, 0.85,
                     col=rnd.choice([(220, 220, 226), (40, 40, 46), (160, 30, 40), (90, 100, 120)]))
    return img


def america_ev():
    return america_lot(chargers=True)


def kuko_yoru():
    """夜の空港の駐機場。小型の飛行機と照明。"""
    img = vgrad((W, H), (10, 14, 30), (30, 34, 60))
    d = _d(img)
    d.rectangle([0, 640, W, H], fill=(40, 42, 50))
    d.polygon([(700, 560), (1300, 520), (1360, 560), (760, 600)], fill=(230, 230, 236))     # 胴体
    d.polygon([(960, 560), (1100, 470), (1140, 470), (1060, 565)], fill=(220, 220, 226))     # 翼
    d.polygon([(1280, 525), (1340, 430), (1370, 430), (1350, 540)], fill=(220, 220, 226))     # 尾翼
    for x in (300, 1600):
        _glow(img, x, 300, 220, (255, 230, 170), 90)
        d = _d(img)
        d.line([(x, 640), (x, 320)], fill=(90, 90, 96), width=10)
    return img


def paris():
    """ヨーロッパの本社の会議室。窓の外に石造りの街並み。"""
    img = _rgb(base((214, 206, 196), (198, 190, 180)))
    wood_floor(img, FLOOR, col=(110, 80, 56), line=(92, 66, 46))
    d = _d(img)
    d.rectangle([200, 100, 1720, 500], fill=(200, 214, 228), outline=(110, 90, 70), width=10)
    rnd = random.Random(9)
    for k in range(10):
        x0 = 220 + k * 150
        top = 300 + rnd.randint(-40, 40)
        d.rectangle([x0, top, x0 + 130, 500], fill=(226, 214, 190))
        d.polygon([(x0, top), (x0 + 65, top - 40), (x0 + 130, top)], fill=(90, 100, 120))
    d.rectangle([500, 640, 1420, 700], fill=(90, 64, 44))
    _papers(d, 700, 630, n=3)
    return img


def kenkyujo_engine():
    """エンジンの研究室。台に載ったエンジンと計測器。"""
    img = _rgb(base((214, 218, 222), (198, 202, 208)))
    wood_floor(img, FLOOR, col=(170, 174, 180), line=(150, 154, 160))
    d = _d(img)
    d.rectangle([600, 560, 1320, 600], fill=(90, 94, 100))
    d.rectangle([700, 400, 1200, 560], fill=(120, 124, 130), outline=(60, 62, 68), width=5)
    for k in range(4):
        d.rectangle([740 + k * 110, 340, 820 + k * 110, 400], fill=(150, 154, 160), outline=(60, 62, 68), width=4)
    d.rectangle([1400, 360, 1760, 600], fill=(60, 64, 70))
    _chart(d, 1420, 380, 1740, 560, [0.3, 0.5, 0.45, 0.7, 0.6, 0.8], col=(60, 200, 120))
    return img


def denchi_kojo():
    """電池の工場。白いクリーンルームに、電池のセルが並ぶライン。"""
    img = vgrad((W, H), (236, 240, 244), (220, 226, 232))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(214, 220, 226))
    d.rectangle([0, 600, W, 640], fill=(160, 166, 174))
    for k in range(40):
        x = 20 + k * 48
        d.rounded_rectangle([x, 540, x + 34, 600], radius=6, fill=(60, 140, 220), outline=(30, 70, 120), width=2)
    for k in range(3):
        d.rectangle([200 + k * 600, 260, 520 + k * 600, 520], fill=(250, 250, 252), outline=(170, 176, 184), width=6)
    return img


def test_course():
    """テストコース。曲がった路面と、走る車。"""
    img = vgrad((W, H), (150, 196, 236), (220, 232, 240))
    d = _d(img)
    d.rectangle([0, 520, W, H], fill=(110, 160, 90))
    d.polygon([(0, 900), (700, 620), (1400, 600), (W, 700), (W, 860), (1400, 760), (720, 800), (0, H)], fill=(80, 82, 88))
    _car(d, 860, 760, 1.3, col=(230, 230, 236))
    return img


# ---------------------------------------------------------------- 小売
def gms(kara=False):
    """総合スーパーの売り場。手前に衣料のラック、奥に食品の棚。kara は棚が空で赤い垂れ幕。"""
    img = _rgb(base((246, 244, 238), (232, 230, 224)))
    wood_floor(img, FLOOR, col=(220, 214, 200), line=(204, 198, 184))
    d = _d(img)
    rnd = random.Random(6)
    for r in range(4):
        y = 160 + r * 100
        d.rectangle([1000, y + 80, 1860, y + 86], fill=(160, 160, 166))
        for k in range(0 if kara else 18):
            d.rectangle([1010 + k * 47, y + 30, 1050 + k * 47, y + 80], fill=rnd.choice(TOY + [(250, 250, 250)]))
    for k in range(3):                                                             # 衣料のラック
        x = 120 + k * 280
        d.line([(x, 360), (x + 220, 360)], fill=(120, 120, 126), width=8)
        for j in range(0 if kara else 8):
            d.rectangle([x + 6 + j * 26, 364, x + 28 + j * 26, 500], fill=rnd.choice([(80, 100, 160), (200, 200, 200), (160, 60, 60), (60, 120, 80)]))
    if kara:
        _banner(d, 1060, 60, 1800, 150)
    return img


def gms_kara():
    return gms(kara=True)


def gms_soto(heiten=False):
    return mise_soto("gms", heiten)


def gms_soto_heiten():
    return gms_soto(True)


def conbini(old=False):
    """コンビニの店内。レジと棚。old は1970年代（木の棚と白熱灯）。"""
    img = _rgb(base((244, 246, 248), (230, 232, 236)) if not old else base((236, 226, 200), (220, 210, 184)))
    wood_floor(img, FLOOR, col=(214, 216, 220) if not old else (150, 120, 90), line=(198, 200, 204) if not old else (130, 100, 76))
    d = _d(img)
    rnd = random.Random(8)
    for r in range(4):
        y = 180 + r * 100
        d.rectangle([700, y + 80, 1840, y + 86], fill=(160, 160, 166) if not old else (120, 90, 60))
        for k in range(24):
            d.rectangle([710 + k * 47, y + 34, 750 + k * 47, y + 80], fill=rnd.choice(TOY + [(250, 250, 250)]))
    d.rectangle([80, 560, 600, 660], fill=(240, 240, 244) if not old else (170, 130, 90), outline=(150, 150, 156), width=4)  # レジ台
    d.rectangle([200, 500, 320, 560], fill=(60, 60, 66))
    if old:
        for x in (400, 1100, 1600):
            _glow(img, x, 70, 160, (255, 220, 150), 80)
    return img


def conbini_1974():
    return conbini(old=True)


def gas_store():
    """アメリカのガソリンスタンド併設のコンビニ。給油機と小さな店舗。"""
    img = vgrad((W, H), (150, 196, 240), (230, 236, 240))
    d = _d(img)
    d.rectangle([0, 600, W, H], fill=(130, 134, 140))
    d.rectangle([100, 220, 1000, 300], fill=(240, 240, 244), outline=(120, 120, 126), width=6)   # 屋根
    for x in (240, 520, 800):
        d.rectangle([x - 8, 300, x + 8, 600], fill=(200, 200, 206))
        d.rounded_rectangle([x - 50, 470, x + 50, 640], radius=10, fill=(230, 60, 40), outline=(100, 20, 10), width=4)
    d.rectangle([1160, 300, 1840, 640], fill=(240, 236, 226), outline=(120, 120, 126), width=6)
    d.rectangle([1200, 360, 1800, 520], fill=(140, 180, 210))
    d.rectangle([1160, 280, 1840, 320], fill=(240, 120, 30))
    _car(d, 300, 820, 1.2, col=(60, 70, 90))
    return img


LOCATIONS = {
    # 日本トイザらス
    "tr_heya": lambda: heya("toy"), "tr_mise": omocha_ten, "tr_mise_kara": omocha_ten_kara,
    "tr_mise_soto": lambda: mise_soto("toy"), "tr_mise_soto_heiten": mise_soto_heiten,
    "tr_denki": denki_ryohan, "tr_butsuryu": butsuryu, "tr_gekiyasu": gekiyasu, "tr_america": america_mise,
    "tr_yakuin": lambda: yakuin(), "tr_kaigi": kaigi, "tr_kaigi_akaji": lambda: kaigi(akaji=True),
    "tr_kaiken": _sega_kaiken, "tr_kokkai": _sogo_kokkai, "tr_houtei": _sogo_saibansho,
    # 日産
    "ns_heya": lambda: heya("car"), "ns_kojo": kojo_line, "ns_kojo_teishi": kojo_teishi,
    "ns_showroom": showroom, "ns_showroom_kara": lambda: showroom(kara=True),
    "ns_yakuin": lambda: yakuin(), "ns_kaigi": kaigi, "ns_kaigi_akaji": lambda: kaigi(akaji=True),
    "ns_kaigi_up": lambda: kaigi(up=True), "ns_kaiken": _sega_kaiken, "ns_kuko": kuko_yoru,
    "ns_houtei": _sogo_saibansho, "ns_paris": paris, "ns_america": america_lot, "ns_gendai": _sega_gendai,
    # セブン&アイ
    "sv_heya": lambda: heya("conbini"), "sv_conbini": conbini, "sv_conbini_1974": conbini_1974,
    "sv_gms": gms, "sv_gms_kara": gms_kara, "sv_gms_soto": gms_soto, "sv_gms_soto_heiten": gms_soto_heiten,
    "sv_yakuin": lambda: yakuin(), "sv_kaigi": kaigi, "sv_kaigi_akaji": lambda: kaigi(akaji=True),
    "sv_kaigi_up": lambda: kaigi(up=True), "sv_kaiken": _sega_kaiken, "sv_america": gas_store, "sv_gendai": _sega_gendai,
    # ホンダ
    "hd_heya": lambda: heya("car"), "hd_kaiken": _sega_kaiken, "hd_kenkyujo": kenkyujo_engine,
    "hd_denchi": denchi_kojo, "hd_test": test_course, "hd_kojo": kojo_line, "hd_showroom": showroom,
    "hd_america_ev": america_ev, "hd_yakuin": lambda: yakuin(), "hd_kaigi": kaigi,
    "hd_kaigi_akaji": lambda: kaigi(akaji=True), "hd_gendai": _sega_gendai,
}

# 年号カード（台本ができてから埋める）。接頭辞ごとに "tr_card_1991" のように作る
CARDS = {"tr": ["1989", "1992", "2000", "2017", "2026"], "ns": ["1999", "2016", "2018", "2024", "2025", "2026"], "sv": ["1972", "1974", "1982", "2016", "2023", "2024", "2025", "2026"], "hd": ["1971", "2021", "2024", "2025", "2026"]}


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
