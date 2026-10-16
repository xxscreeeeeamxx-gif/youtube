#!/usr/bin/env python3
"""そごうの回（89_そごうの破綻 / slug=sogo-mizushima）の背景を生成する。

方針はセガ回（gen_sega_bgs.py）と同じで、部品もそこから借りる。
実在の会社の商標（ロゴ・社名の文字・看板の店名）は描かない。百貨店は建物の形と
垂れ幕・紙袋の色だけで分かるようにする。差し替え用（_pins・_akaji・_shutter など）は
元の絵を呼んで要素を足し、切り替わりの差が一目で分かるようにする。

実行: PYTHONPATH=. python scripts/gen_sogo_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import _papers, _phone, _table, _window, year_card  # noqa: E402
from scripts.gen_sega_bgs import (  # noqa: E402
    _chart, _flat_tv, _glow, _person_line, kaiken as _sega_kaiken,
)

FLOOR = int(H * 0.86)
INK = (60, 60, 66)
BAG = (190, 40, 60)          # 紙袋の赤（社名・マークは描かない）


def _d(img):
    return ImageDraw.Draw(img, "RGBA")


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


def _bag(d, x, y, s=1.0, col=BAG):
    """百貨店の紙袋（左上が x, y）。"""
    d.rectangle([x, y, x + 120 * s, y + 150 * s], fill=col, outline=(120, 20, 30), width=3)
    d.arc([x + 30 * s, y - 50 * s, x + 90 * s, y + 20 * s], 180, 360, fill=(80, 20, 30), width=int(6 * s))
    d.rectangle([x + 20 * s, y + 50 * s, x + 100 * s, y + 70 * s], fill=(240, 230, 220))


def _store(d, x0, y0, x1, y1, col=(226, 220, 206), banners=True, lights=True):
    """百貨店の建物（正面）。窓の列と垂れ幕（文字なし）。"""
    d.rectangle([x0, y0, x1, y1], fill=col, outline=(150, 146, 136), width=4)
    rows = max(3, (y1 - y0) // 90)
    for r in range(rows):
        y = y0 + 30 + r * 80
        if y + 50 > y1 - 140:
            break
        for k in range((x1 - x0 - 40) // 70):
            x = x0 + 30 + k * 70
            d.rectangle([x, y, x + 46, y + 46], fill=(250, 236, 170) if lights else (150, 170, 190))
    if banners:
        for k, c in enumerate(((200, 40, 50), (40, 90, 170), (220, 160, 40))):
            bx = x0 + 60 + k * ((x1 - x0 - 160) // 3)
            d.rectangle([bx, y0 + 40, bx + 60, y0 + 260], fill=c)
    d.rectangle([x0 + (x1 - x0) // 2 - 120, y1 - 140, x0 + (x1 - x0) // 2 + 120, y1], fill=(60, 60, 70))  # 入口


# ---------------------------------------------------------------- 今
def heya():
    """今の部屋。テーブルに赤い紙袋。"""
    img = _rgb(base((232, 228, 220), (216, 212, 204)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    _window(d, 760, 140, 1160, 420, sky=(200, 220, 236))
    d.rectangle([640, 640, 1280, 680], fill=(140, 106, 76))
    d.rectangle([660, 680, 700, 820], fill=(120, 90, 64))
    d.rectangle([1220, 680, 1260, 820], fill=(120, 90, 64))
    _bag(d, 900, 490, 1.0)
    return img


def heya_tv():
    """同じ部屋。テレビにニュース（デパートの外観とテロップの帯、文字なし）。"""
    img = heya()
    d = _d(img)
    sx0, sy0, sx1, sy1 = _flat_tv(d, 1360, 220, 1820, 500, screen=(40, 50, 70))
    _store(d, sx0 + 40, sy0 + 20, sx1 - 40, sy1 - 60, banners=False)
    d.rectangle([sx0, sy1 - 50, sx1, sy1], fill=(200, 30, 40))
    return img


# ---------------------------------------------------------------- 戦前〜高度成長
def ginkou():
    """戦前〜戦後の銀行の事務室。木の机とそろばん、天井の高い窓。"""
    img = _rgb(base((214, 206, 188), (198, 190, 172)))
    wood_floor(img, FLOOR, col=(110, 84, 60), line=(90, 68, 48))
    d = _d(img)
    for x in (300, 960, 1620):
        d.rectangle([x - 140, 80, x + 140, 460], fill=(206, 216, 222), outline=(110, 90, 70), width=10)
        d.line([(x, 80), (x, 460)], fill=(110, 90, 70), width=8)
    for k, x in enumerate((360, 1200)):
        d.rectangle([x, 640, x + 400, 680], fill=(110, 76, 50))
        d.rectangle([x + 10, 680, x + 390, 800], fill=(96, 66, 44))
        _papers(d, x + 30, 630, n=3)
        d.rectangle([x + 230, 610, x + 370, 640], fill=(80, 56, 36))          # そろばん
        for j in range(8):
            d.ellipse([x + 236 + j * 16, 616, x + 248 + j * 16, 634], fill=(30, 24, 20))
    return img


def kenkyushitsu(night=False):
    """大学の研究室。壁一面の法律書、机に原稿用紙の束。night は夜で電気スタンド。"""
    img = _rgb(base((40, 40, 56), (54, 52, 66)) if night else base((222, 214, 196), (206, 198, 180)))
    wood_floor(img, FLOOR, col=(70, 58, 50) if night else (120, 96, 72), line=(56, 46, 40) if night else (100, 80, 60))
    d = _d(img)
    rnd = random.Random(5)
    for r in range(4):                                                          # 本棚
        y = 140 + r * 150
        d.rectangle([60, y + 120, 1860, y + 134], fill=(90, 64, 44))
        x = 70
        while x < 1840:
            w = rnd.randint(18, 34)
            c = rnd.choice([(110, 40, 40), (40, 60, 100), (60, 80, 60), (120, 100, 60), (80, 60, 90)])
            d.rectangle([x, y + 120 - rnd.randint(90, 115), x + w, y + 120], fill=c)
            x += w + 2
    d.rectangle([520, 660, 1400, 700], fill=(100, 70, 46))                      # 机
    d.rectangle([540, 700, 580, 860], fill=(84, 58, 38))
    d.rectangle([1340, 700, 1380, 860], fill=(84, 58, 38))
    for k in range(5):
        d.rectangle([700 + k * 6, 620 - k * 10, 900 + k * 6, 660 - k * 10], fill=(244, 238, 222), outline=(170, 160, 140))
    if night:
        d.line([(1240, 660), (1240, 560)], fill=(60, 60, 60), width=8)
        d.polygon([(1190, 560), (1290, 560), (1260, 520), (1220, 520)], fill=(80, 90, 60))
        _glow(img, 1240, 600, 300, (255, 230, 150), 90)
    return img


def kenkyushitsu_yoru():
    return kenkyushitsu(night=True)


def uriba(crowd=False, empty=False):
    """百貨店の売り場。ガラスケースと照明。crowd は客でいっぱい、empty は品物の無い棚。"""
    img = _rgb(base((244, 238, 226), (230, 224, 212)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(214, 206, 192))
    for k in range(8):                                                          # 天井の照明
        x = 120 + k * 240
        d.ellipse([x, 40, x + 120, 80], fill=(255, 250, 220))
    for k in range(4):                                                          # ガラスケース
        x = 120 + k * 450
        d.rectangle([x, 620, x + 360, FLOOR], fill=(200, 186, 160), outline=(150, 136, 110), width=4)
        d.rectangle([x + 10, 560, x + 350, 620], fill=(220, 236, 244, 160), outline=(170, 190, 200), width=3)
        if not empty:
            for j in range(4):
                d.rectangle([x + 30 + j * 80, 580, x + 80 + j * 80, 616], fill=((200, 60, 60), (60, 100, 180), (220, 180, 60), (90, 150, 90))[j])
    for k in range(3):                                                          # 壁の棚
        y = 200 + k * 120
        d.rectangle([80, y + 90, 1840, y + 100], fill=(170, 140, 100))
        if not empty:
            for j in range(22):
                d.rectangle([100 + j * 80, y + 30, 150 + j * 80, y + 90], fill=((220, 200, 170), (180, 120, 120), (140, 160, 200))[j % 3])
    if crowd:
        _person_line(d, 40, 1010, 27, 1.0)
        _person_line(d, 80, 900, 26, 0.8)
    return img


def uriba_konzatsu():
    return uriba(crowd=True)


def uriba_kara():
    return uriba(empty=True)


def shachoshitsu(pins=0, night=False):
    """社長室。壁に日本地図（形は抽象）、pins の数だけ赤い画鋲（店）。"""
    img = _rgb(base((40, 38, 50), (56, 52, 64)) if night else base((216, 206, 188), (200, 190, 172)))
    wood_floor(img, FLOOR, col=(94, 70, 52), line=(78, 58, 42))
    d = _d(img)
    d.rectangle([560, 90, 1360, 520], fill=(236, 232, 214), outline=(120, 100, 76), width=8)  # 地図の額
    pts = [(1180, 150), (1240, 210), (1210, 270), (1150, 300), (1080, 330), (1000, 360), (920, 380),
           (840, 400), (760, 430), (700, 470), (660, 450), (720, 400), (800, 360), (880, 330),
           (960, 300), (1040, 260), (1110, 210)]
    d.polygon(pts, fill=(170, 196, 160), outline=(110, 130, 100))
    rnd = random.Random(11)
    spots = [(1150, 230), (1100, 260), (1060, 290), (1000, 320), (950, 340), (900, 355), (860, 370),
             (820, 385), (780, 410), (740, 440), (1120, 240), (980, 330), (1020, 300), (930, 345),
             (880, 360), (800, 395), (760, 425), (1080, 275), (1170, 200), (700, 455), (840, 378),
             (960, 325), (1040, 285), (1130, 225), (720, 445), (900, 342), (1060, 300), (990, 312)]
    for (x, y) in spots[:pins]:
        x += rnd.randint(-6, 6)
        d.line([(x, y), (x, y - 26)], fill=(60, 60, 60), width=3)
        d.ellipse([x - 12, y - 40, x + 12, y - 16], fill=(220, 30, 40))
    d.rectangle([700, 640, 1500, 700], fill=(90, 60, 40))                        # 机
    d.rectangle([720, 700, 760, 860], fill=(70, 48, 32))
    d.rectangle([1440, 700, 1480, 860], fill=(70, 48, 32))
    _papers(d, 800, 630, n=3)
    _phone(d, 1300, 570, 0.6)
    if night:
        _glow(img, 1100, 620, 320, (255, 220, 150), 80)
    return img


def shachoshitsu_pin3():
    return shachoshitsu(pins=3)


def shachoshitsu_pins():
    return shachoshitsu(pins=28)


def shachoshitsu_yoru():
    return shachoshitsu(pins=28, night=True)


def kaitenshiki():
    """新しい店の開店式。建物の前に紅白のテープと花輪、人だかり。"""
    img = vgrad((W, H), (170, 206, 236), (220, 232, 240))
    d = _d(img)
    _store(d, 300, 80, 1620, 800)
    d.rectangle([0, 800, W, H], fill=(170, 170, 166))
    for k in range(18):                                                          # 紅白のテープ
        x = 360 + k * 70
        d.rectangle([x, 760, x + 70, 790], fill=(220, 40, 50) if k % 2 else (250, 250, 250))
    for x in (160, 1700):                                                        # 花輪
        for r, c in ((120, (230, 80, 120)), (80, (250, 220, 230)), (40, (230, 200, 60))):
            d.ellipse([x - r, 420 - r, x + r, 420 + r], fill=c)
        d.line([(x, 540), (x, 800)], fill=(60, 50, 40), width=8)
    _person_line(d, 60, 1060, 27, 1.0)
    return img


def gaikan(night=False, shutter=False):
    """大きな百貨店の外観。night は夜のネオン、shutter は閉店（シャッターと貼り紙）。"""
    img = vgrad((W, H), (20, 24, 50), (40, 40, 70)) if night else vgrad((W, H), (150, 196, 236), (210, 228, 240))
    d = _d(img)
    _store(d, 260, 60, 1660, FLOOR, banners=not shutter, lights=not shutter)
    if night and not shutter:
        _glow(img, 960, 400, 800, (255, 230, 160), 60)
        d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(120, 120, 126))
    if shutter:
        x0, x1 = 960 - 260, 960 + 260
        d.rectangle([x0, FLOOR - 300, x1, FLOOR], fill=(150, 152, 156))
        for k in range(14):
            d.line([(x0, FLOOR - 300 + k * 22), (x1, FLOOR - 300 + k * 22)], fill=(120, 122, 126), width=4)
        d.rectangle([900, FLOOR - 220, 1020, FLOOR - 120], fill=(250, 250, 246), outline=(160, 160, 160))
        for k in range(4):
            d.line([(912, FLOOR - 200 + k * 20), (1008, FLOOR - 200 + k * 20)], fill=(90, 90, 90), width=4)
    return img


def gaikan_yoru():
    return gaikan(night=True)


def gaikan_heiten():
    return gaikan(shutter=True)


def ginkou_kaigi(akaji=False):
    """銀行との会議。長机に書類の山、ボードに借入のグラフ。akaji は赤く崩れたグラフ。"""
    img = _rgb(base((206, 204, 198), (190, 188, 182)))
    wood_floor(img, FLOOR, col=(100, 92, 84), line=(84, 76, 70))
    d = _d(img)
    if akaji:
        _chart(d, 600, 110, 1320, 480, [0.3, 0.45, 0.62, 0.8, 0.97], col=(220, 30, 40))
        d.rectangle([600, 110, 1320, 480], fill=(220, 40, 40, 50))
    else:
        _chart(d, 600, 110, 1320, 480, [0.15, 0.3, 0.42, 0.58, 0.75], col=(60, 90, 170))
    d.rectangle([300, 640, 1620, 700], fill=(110, 90, 72))
    for k in range(6):
        _papers(d, 360 + k * 210, 630, n=2 + (k % 3))
    return img


def ginkou_kaigi_akaji():
    return ginkou_kaigi(akaji=True)


def kokkai():
    """国会の委員会室。半円に並ぶ机と、中央の答弁台。"""
    img = _rgb(base((150, 120, 96), (130, 104, 84)))
    d = _d(img)
    d.rectangle([0, 0, W, 300], fill=(120, 92, 70))
    for k in range(12):
        d.rectangle([k * 170, 40, k * 170 + 120, 260], fill=(200, 196, 180), outline=(100, 80, 60), width=4)
    d.rectangle([0, 600, W, H], fill=(70, 90, 70))                                # 緑の絨毯
    for r in range(2):
        for k in range(9):
            x = 60 + k * 210
            y = 640 + r * 140
            d.rectangle([x, y, x + 170, y + 40], fill=(110, 76, 52))
    d.rectangle([860, 520, 1060, 640], fill=(96, 66, 44))                        # 答弁台
    d.line([(960, 520), (940, 460)], fill=(40, 40, 44), width=6)
    return img


def kaiken():
    """記者会見場（セガ回と同じ構図を借りる）。"""
    return _sega_kaiken()


def saibansho():
    """法廷。正面に裁判官の高い席、手前に証言台。"""
    img = _rgb(base((196, 176, 150), (180, 160, 136)))
    wood_floor(img, FLOOR, col=(120, 90, 64), line=(100, 74, 52))
    d = _d(img)
    d.rectangle([0, 0, W, 120], fill=(150, 120, 90))
    d.rectangle([360, 260, 1560, 460], fill=(120, 86, 58))                       # 裁判官席
    d.rectangle([340, 240, 1580, 270], fill=(100, 70, 46))
    for x in (640, 960, 1280):
        d.rectangle([x - 50, 140, x + 50, 260], fill=(80, 56, 40))               # 椅子の背
    d.rectangle([880, 640, 1040, 760], fill=(110, 80, 56))                       # 証言台
    d.rectangle([0, 760, W, 800], fill=(130, 100, 70))                           # 柵
    for k in range(24):
        d.line([(k * 80, 760), (k * 80, 920)], fill=(110, 84, 58), width=6)
    return img


def eki():
    """駅前の広場。人の流れと、奥に百貨店の建物（夕方）。"""
    img = vgrad((W, H), (236, 170, 120), (180, 150, 160))
    d = _d(img)
    _store(d, 600, 120, 1500, 780, col=(210, 196, 176))
    d.rectangle([0, 780, W, H], fill=(150, 146, 140))
    for k in range(10):
        d.line([(0, 800 + k * 26), (W, 800 + k * 26)], fill=(140, 136, 130), width=3)
    _person_line(d, 30, 1040, 27, 1.0)
    return img


def enkaijo():
    """ホテルの宴会場。シャンデリアと丸テーブル、正面に金屏風（文字なし）。"""
    img = _rgb(base((120, 90, 70), (100, 74, 58)))
    d = _d(img)
    d.rectangle([0, 620, W, H], fill=(140, 40, 50))                              # 赤い絨毯
    for k in range(6):                                                            # 金屏風
        x = 560 + k * 140
        d.rectangle([x, 160, x + 136, 600], fill=(214, 176, 80), outline=(160, 120, 50), width=4)
    for x in (360, 960, 1560):                                                    # シャンデリア
        _glow(img, x, 90, 220, (255, 236, 180), 90)
        d = _d(img)
        d.ellipse([x - 70, 50, x + 70, 120], fill=(250, 236, 190))
    for k in range(4):                                                            # 丸テーブル
        x = 160 + k * 480
        d.ellipse([x, 700, x + 300, 800], fill=(248, 246, 240), outline=(200, 196, 190), width=3)
        d.rectangle([x + 140, 800, x + 160, 900], fill=(200, 196, 190))
        for j in range(3):
            d.ellipse([x + 60 + j * 70, 690, x + 90 + j * 70, 720], fill=(220, 200, 160))
    return img


def gendai():
    """今の百貨店の売り場（落ち着いた照明）。"""
    img = uriba()
    d = _d(img)
    d.rectangle([0, 0, W, H], fill=(255, 240, 210, 40))
    return img


LOCATIONS = {
    "so_heya": heya, "so_heya_tv": heya_tv, "so_ginkou": ginkou, "so_kenkyushitsu": kenkyushitsu,
    "so_kenkyushitsu_yoru": kenkyushitsu_yoru, "so_uriba": uriba, "so_uriba_konzatsu": uriba_konzatsu,
    "so_uriba_kara": uriba_kara, "so_shachoshitsu": shachoshitsu, "so_shachoshitsu_pin3": shachoshitsu_pin3,
    "so_shachoshitsu_pins": shachoshitsu_pins, "so_shachoshitsu_yoru": shachoshitsu_yoru,
    "so_kaitenshiki": kaitenshiki, "so_gaikan": gaikan, "so_gaikan_yoru": gaikan_yoru,
    "so_gaikan_heiten": gaikan_heiten, "so_ginkou_kaigi": ginkou_kaigi,
    "so_ginkou_kaigi_akaji": ginkou_kaigi_akaji, "so_kokkai": kokkai, "so_kaiken": kaiken,
    "so_saibansho": saibansho, "so_eki": eki, "so_gendai": gendai, "so_enkaijo": enkaijo,
}

# 台本で使った年に合わせる（台本ができたら足す）
CARDS = ["1912", "1936", "1953", "1957", "1958", "1962", "1967", "1985", "1992", "1994", "1995", "1998", "2000", "2001", "2012"]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for y in CARDS:
        if only and f"so_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"so_card_{y}.png")
        print(f"生成完了: so_card_{y}.png")
