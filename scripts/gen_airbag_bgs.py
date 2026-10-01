#!/usr/bin/env python3
"""エアバッグの誕生回（64_エアバッグの誕生 / slug=kobori-airbag）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針は八木アンテナ回（gen_yagi_bgs.py）と同じ。
実在の会社の商標（ロゴ・社名の文字）は描かない。

実行: PYTHONPATH=. python scripts/gen_airbag_bgs.py [名前...]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)
BAG = (246, 246, 240)
BAG_EDGE = (190, 190, 184)
INK = (60, 60, 66)


def _d(img):
    return ImageDraw.Draw(img)


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


def _font(size):
    from ytf.config import Config, resolve_font
    Config.load()
    return ImageFont.truetype(resolve_font("w9"), size)


def _text_c(d, cx, y, t, size, fill):
    f = _font(size)
    bb = d.textbbox((0, 0), t, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y), t, font=f, fill=fill)


def _table(d, x0, x1, y, col=(150, 116, 80)):
    d.rectangle([x0, y, x1, y + 36], fill=col)
    d.rectangle([x0 + 20, y + 36, x0 + 40, y + 190], fill=tuple(int(c * 0.8) for c in col))
    d.rectangle([x1 - 40, y + 36, x1 - 20, y + 190], fill=tuple(int(c * 0.8) for c in col))


def _window(d, x0, y0, x1, y1, sky=(176, 210, 232), frame=(70, 62, 56)):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


def _papers(d, x0, y0, n=3, col=(244, 240, 228)):
    for k in range(n):
        x, y = x0 + k * 22, y0 - k * 8
        d.rectangle([x, y, x + 120, y + 80], fill=col, outline=(170, 160, 140), width=2)
        for j in range(4):
            d.line([(x + 12, y + 16 + j * 15), (x + 100, y + 16 + j * 15)], fill=(150, 150, 150), width=2)


def _car_side(d, x0, y0, w, col=(90, 120, 170), win=(200, 222, 236)):
    """横から見た乗用車（x0,y0 が車体の左下あたり、w が全長）。"""
    s = w / 1000
    body = [(x0, y0 - 60 * s), (x0 + 40 * s, y0 - 150 * s), (x0 + 270 * s, y0 - 170 * s),
            (x0 + 380 * s, y0 - 300 * s), (x0 + 700 * s, y0 - 300 * s), (x0 + 820 * s, y0 - 170 * s),
            (x0 + 980 * s, y0 - 150 * s), (x0 + w, y0 - 60 * s), (x0 + w, y0), (x0, y0)]
    d.polygon(body, fill=col)
    d.polygon([(x0 + 300 * s, y0 - 175 * s), (x0 + 395 * s, y0 - 285 * s), (x0 + 540 * s, y0 - 285 * s),
               (x0 + 540 * s, y0 - 175 * s)], fill=win)
    d.polygon([(x0 + 560 * s, y0 - 175 * s), (x0 + 560 * s, y0 - 285 * s), (x0 + 690 * s, y0 - 285 * s),
               (x0 + 790 * s, y0 - 175 * s)], fill=win)
    for cx in (x0 + 200 * s, x0 + 800 * s):
        r = 80 * s
        d.ellipse([cx - r, y0 - r, cx + r, y0 + r], fill=(40, 40, 44))
        d.ellipse([cx - r * 0.5, y0 - r * 0.5, cx + r * 0.5, y0 + r * 0.5], fill=(170, 170, 176))
    return s


def _wheel(d, cx, cy, r, label=True):
    """ハンドル。真ん中のパッドに SRS AIRBAG の刻印。"""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(40, 40, 46), width=int(r * 0.16))
    d.line([(cx - r, cy + r * 0.1), (cx + r, cy + r * 0.1)], fill=(40, 40, 46), width=int(r * 0.14))
    d.rectangle([cx - r * 0.07, cy, cx + r * 0.07, cy + r], fill=(40, 40, 46))
    pr = r * 0.46
    d.ellipse([cx - pr, cy - pr * 0.8, cx + pr, cy + pr * 0.8], fill=(56, 56, 62), outline=(30, 30, 34), width=4)
    if label:
        f = _font(int(r * 0.14))
        for k, t in enumerate(("SRS", "AIRBAG")):
            bb = d.textbbox((0, 0), t, font=f)
            d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - pr * 0.36 + k * r * 0.18), t, font=f, fill=(200, 200, 206))


# ---------------------------------------------------------------- 場所
def kuruma():
    """今の車の運転席。ハンドルの真ん中に SRS AIRBAG。"""
    img = vgrad((W, H), (170, 206, 236), (210, 226, 236))
    d = _d(img)
    d.rectangle([0, 520, W, 620], fill=(150, 170, 150))                         # 窓の外の景色
    d.polygon([(0, 0), (W, 0), (W, 120), (0, 200)], fill=(60, 60, 66))          # 天井
    d.polygon([(0, 560), (W, 520), (W, H), (0, H)], fill=(52, 54, 60))           # ダッシュボード
    d.rectangle([0, 640, W, 660], fill=(80, 82, 90))
    d.rectangle([1260, 610, 1500, 700], fill=(30, 32, 36))                      # メーター周り
    _wheel(d, 960, 700, 250)
    return img


def kuruma2():
    """後ろの席から見た車内。前の座席の背もたれと、後席のシートベルト。"""
    img = vgrad((W, H), (170, 206, 236), (210, 226, 236))
    d = _d(img)
    d.rectangle([0, 0, W, 120], fill=(60, 60, 66))
    d.rectangle([0, 360, W, H], fill=(52, 54, 60))
    for cx in (640, 1280):                                                      # 前の座席
        d.rounded_rectangle([cx - 190, 380, cx + 190, 900], radius=60, fill=(90, 86, 92))
        d.rounded_rectangle([cx - 110, 250, cx + 110, 370], radius=40, fill=(96, 92, 98))
        d.rectangle([cx - 20, 370, cx + 20, 390], fill=(70, 70, 74))
    d.rectangle([0, 900, W, H], fill=(110, 104, 112))                           # 後席の座面
    d.line([(900, 900), (1020, 1080)], fill=(40, 40, 44), width=26)              # シートベルト
    d.rectangle([980, 1010, 1060, 1060], fill=(170, 170, 176))
    return img


def mura():
    """明治の栃木の農村。田んぼと茅葺きの家、遠くの山。"""
    img = vgrad((W, H), (170, 206, 230), (224, 232, 226))
    d = _d(img)
    d.polygon([(0, 520), (300, 360), (640, 480), (1000, 330), (1400, 470), (1920, 380), (W, 560), (0, 560)],
              fill=(120, 150, 130))
    d.rectangle([0, 560, W, H], fill=(150, 176, 100))
    for k in range(6):
        d.line([(0, 640 + k * 70), (W, 620 + k * 76)], fill=(126, 150, 84), width=4)
    d.polygon([(760, 560), (960, 380), (1160, 560)], fill=(170, 140, 90))       # 茅葺き屋根
    d.rectangle([800, 560, 1120, 760], fill=(160, 130, 96))
    d.rectangle([920, 640, 1000, 760], fill=(70, 56, 44))
    return img


def fudo():
    """栃木・多功の不動尊。小さなお堂と、境内の大きな榎（棟方志功が歓喜木と名付けた）。"""
    img = vgrad((W, H), (168, 204, 228), (226, 232, 220))
    d = _d(img)
    d.polygon([(0, 560), (500, 420), (1100, 500), (1920, 400), (W, 600), (0, 600)], fill=(122, 150, 128))
    d.rectangle([0, 600, W, H], fill=(196, 182, 150))                       # 境内の土
    d.rectangle([1180, 440, 1640, 700], fill=(150, 92, 60))                 # お堂
    d.polygon([(1120, 450), (1410, 330), (1700, 450)], fill=(80, 70, 66))   # 屋根
    d.rectangle([1340, 560, 1480, 700], fill=(70, 44, 34))
    d.rectangle([1150, 700, 1670, 730], fill=(170, 160, 140))               # 石段
    d.rectangle([330, 300, 420, 720], fill=(104, 82, 60))                   # 榎の幹
    for cx, cy, r in ((380, 260, 210), (240, 330, 150), (520, 320, 160), (380, 150, 150)):
        d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=(78, 120, 72))
    return img


def tsushin():
    """大正の通信社の部屋。机、原稿の山、ろうそく立て型の電話。"""
    img = _rgb(base((222, 212, 192), (200, 190, 170)))
    wood_floor(img, FLOOR, col=(120, 94, 70), line=(100, 78, 58))
    d = _d(img)
    _window(d, 780, 120, 1140, 360, sky=(190, 206, 214))
    for x in (60, 1500):
        _table(d, x, x + 360, 640, col=(120, 90, 64))
        _papers(d, x + 60, 590, 3)
    _table(d, 760, 1160, 660, col=(130, 98, 70))
    _papers(d, 800, 610, 4)
    d.rectangle([1060, 560, 1072, 660], fill=(40, 36, 32))                      # 電話
    d.ellipse([1044, 540, 1088, 572], fill=(40, 36, 32))
    d.rectangle([1040, 648, 1092, 662], fill=(40, 36, 32))
    return img


def kojo():
    """昭和初めのクレーン工場。天井の走行クレーンと鉄の塊、無地の看板。"""
    img = _rgb(base((200, 196, 188), (170, 166, 158)))
    wood_floor(img, FLOOR, col=(110, 104, 96), line=(90, 86, 80))
    d = _d(img)
    d.rectangle([0, 150, W, 190], fill=(90, 70, 50))                            # 走行レール
    d.rectangle([640, 190, 1280, 240], fill=(200, 150, 40))                     # クレーンの桁
    d.rectangle([900, 240, 980, 300], fill=(80, 80, 86))                        # 巻き上げ機
    d.line([(940, 300), (940, 540)], fill=(60, 60, 66), width=6)
    d.arc([915, 530, 965, 580], 0, 180, fill=(60, 60, 66), width=8)             # フック
    d.rectangle([860, 600, 1020, 720], fill=(96, 100, 110))                     # 鉄の塊
    d.line([(940, 575), (880, 600)], fill=(60, 60, 66), width=4)
    d.line([(940, 575), (1000, 600)], fill=(60, 60, 66), width=4)
    d.rectangle([1320, 60, 1740, 130], fill=(236, 226, 200), outline=(90, 70, 50), width=6)  # 無地の看板
    return img


def kojo2():
    """小型クレーンで吊った、飛行機の星形エンジン。"""
    img = _rgb(base((200, 196, 188), (170, 166, 158)))
    wood_floor(img, FLOOR, col=(110, 104, 96), line=(90, 86, 80))
    d = _d(img)
    d.rectangle([760, 180, 790, 760], fill=(200, 150, 40))                      # 小型クレーンの柱
    d.rectangle([760, 180, 1100, 206], fill=(200, 150, 40))                     # 腕
    d.line([(790, 300), (900, 206)], fill=(200, 150, 40), width=10)
    d.line([(1060, 206), (1060, 400)], fill=(60, 60, 66), width=5)
    cx, cy, r = 1060, 480, 80                                                   # 星形エンジン
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 112, 118))
    for k in range(9):
        import math
        a = k * 2 * math.pi / 9
        x, y = cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a)
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(80, 82, 88))
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(60, 60, 64))
    d.rectangle([980, 640, 1160, 760], fill=(120, 110, 96))                     # 取り付け台
    return img


def jimusho():
    """戦後の会社の事務所。壁に炭鉱の機械の図面。"""
    img = _rgb(base((220, 214, 200), (200, 194, 180)))
    wood_floor(img, FLOOR, col=(120, 100, 80), line=(100, 84, 66))
    d = _d(img)
    d.rectangle([760, 140, 1160, 420], fill=(214, 226, 236), outline=(90, 90, 100), width=6)   # 図面
    d.rectangle([820, 300, 1100, 360], outline=(40, 70, 130), width=4)          # 炭車
    for x in (860, 1060):
        d.ellipse([x - 24, 350, x + 24, 398], outline=(40, 70, 130), width=4)
    for k in range(6):                                                          # 石炭
        d.ellipse([840 + k * 40, 270, 880 + k * 40, 305], outline=(40, 70, 130), width=3)
    _table(d, 760, 1160, 640, col=(120, 92, 66))
    _papers(d, 820, 600, 2)
    return img


def mingei():
    """民芸の器と布を飾った座敷。三味線と、版画ふうの額。"""
    img = _rgb(base((226, 214, 190), (206, 194, 170)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([760, 140, 1160, 400], fill=(236, 228, 206), outline=(90, 70, 50), width=10)   # 額
    d.polygon([(820, 360), (900, 200), (980, 360)], fill=(40, 36, 32))          # 版画ふうの模様
    d.ellipse([990, 210, 1100, 320], fill=(40, 36, 32))
    d.rectangle([1000, 330, 1100, 370], fill=(160, 50, 40))
    d.rectangle([740, 600, 1180, 640], fill=(120, 90, 60))                      # 飾り棚
    for k, col in enumerate([(120, 80, 50), (60, 80, 110), (170, 140, 90)]):     # 民芸の器
        x = 790 + k * 130
        d.ellipse([x, 500, x + 90, 600], fill=col)
        d.rectangle([x + 25, 480, x + 65, 510], fill=col)
    d.rectangle([740, 640, 1180, 690], fill=(50, 70, 110))                      # 藍染めの布
    for x in range(760, 1180, 40):
        d.line([(x, 640), (x + 20, 690)], fill=(230, 230, 236), width=3)
    d.line([(1350, 260), (1350, 600)], fill=(60, 40, 30), width=10)             # 三味線の棹
    for k in range(3):
        d.line([(1340, 280 + k * 22), (1366, 276 + k * 22)], fill=(60, 40, 30), width=6)
    d.rounded_rectangle([1296, 590, 1404, 700], radius=12, fill=(236, 226, 200), outline=(60, 40, 30), width=6)
    d.rectangle([1300, 700, 1400, 760], fill=(110, 80, 50))                     # 台
    return img


def _gic_room(img):
    """寺の境内の木造一軒家（GIC）の中。窓の外に寺の屋根。"""
    wood_floor(img, FLOOR, col=(130, 104, 78), line=(110, 88, 66))
    d = _d(img)
    _window(d, 780, 110, 1140, 330, sky=(190, 214, 230))
    d.polygon([(800, 300), (960, 200), (1120, 300)], fill=(70, 70, 76))         # 寺の屋根
    d.rectangle([860, 300, 1060, 330], fill=(150, 110, 70))
    return d


def gic():
    """GIC の仕事場。机にサンドイッチの自動製造機。"""
    img = _rgb(base((226, 216, 196), (206, 196, 176)))
    d = _gic_room(img)
    _table(d, 740, 1180, 640, col=(140, 108, 76))
    d.rectangle([800, 480, 1040, 640], fill=(170, 176, 186), outline=(90, 94, 104), width=5)  # 機械
    for k in range(3):
        d.ellipse([830 + k * 70, 510, 880 + k * 70, 560], fill=(120, 124, 134))
    d.rectangle([1040, 600, 1140, 612], fill=(90, 94, 104))                     # 出口
    d.polygon([(1060, 600), (1130, 600), (1095, 570)], fill=(236, 206, 140))   # 三角のサンドイッチ
    d.rectangle([1062, 586, 1128, 592], fill=(120, 170, 90))
    d.rectangle([820, 440, 900, 480], fill=(236, 206, 140))                     # 食パン
    return img


def gic2():
    """GIC の机。英字新聞と、網と袋の下書き、車の模型。"""
    img = _rgb(base((226, 216, 196), (206, 196, 176)))
    d = _gic_room(img)
    _table(d, 740, 1180, 640, col=(140, 108, 76))
    d.rectangle([780, 560, 960, 640], fill=(236, 234, 226), outline=(160, 156, 146), width=2)  # 新聞
    d.rectangle([790, 570, 950, 586], fill=(60, 60, 66))
    for j in range(4):
        d.line([(792, 598 + j * 10), (948, 598 + j * 10)], fill=(150, 150, 150), width=2)
    d.rectangle([990, 560, 1150, 640], fill=(244, 240, 228), outline=(170, 160, 140), width=2)  # 下書き
    for k in range(5):                                                          # 網
        d.line([(1000 + k * 20, 572), (1000 + k * 20, 628)], fill=(90, 90, 96), width=2)
        d.line([(1000, 572 + k * 14), (1080, 572 + k * 14)], fill=(90, 90, 96), width=2)
    d.ellipse([1090, 575, 1140, 625], outline=(200, 80, 60), width=3)           # 袋のまる
    d.rounded_rectangle([1200, 600, 1320, 640], radius=12, fill=(90, 120, 170))  # 車の模型
    return img


def gic3():
    """GIC の机いっぱいに広げた、各国の特許証。"""
    img = _rgb(base((226, 216, 196), (206, 196, 176)))
    d = _gic_room(img)
    _table(d, 700, 1220, 640, col=(140, 108, 76))
    cols = [(244, 240, 228), (236, 232, 214), (246, 244, 236)]
    for k in range(7):
        x, y = 720 + k * 66, 540 + (k % 2) * 30
        d.rectangle([x, y, x + 110, y + 90], fill=cols[k % 3], outline=(170, 160, 140), width=2)
        d.ellipse([x + 40, y + 50, x + 70, y + 80], fill=(180, 40, 40))         # 封蝋
        d.line([(x + 50, y + 78), (x + 44, y + 100)], fill=(180, 40, 40), width=4)
    return img


def gic_mono():
    """誰もいない GIC の机（白黒）。"""
    img = gic3().convert("L").convert("RGB")
    return img


def hikouki():
    """1960年代の旅客機の客室。座席の背の折り畳みテーブルと、手荷物。"""
    img = _rgb(base((226, 226, 222), (206, 206, 200)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(80, 90, 110))
    d.polygon([(0, 0), (W, 0), (W, 100), (0, 100)], fill=(236, 236, 232))
    for x in (120, 1560):                                                       # 丸い窓
        d.rounded_rectangle([x, 220, x + 140, 380], radius=60, fill=(170, 206, 236), outline=(200, 200, 196), width=10)
    d.rounded_rectangle([760, 300, 1160, 760], radius=40, fill=(60, 90, 140))   # 前の座席の背
    d.rounded_rectangle([830, 240, 1090, 320], radius=30, fill=(236, 236, 232))  # 枕カバー
    d.rectangle([790, 560, 1130, 600], fill=(200, 200, 196))                    # 折り畳みテーブル
    d.rounded_rectangle([860, 470, 1060, 560], radius=14, fill=(120, 80, 50))   # 手荷物
    d.rectangle([930, 450, 990, 470], fill=(80, 56, 36))
    return img


def zukai():
    """図解: 保三郎の概念図ふう。車の中の袋と、前後のバンパーの感知装置。"""
    img = vgrad((W, H), (244, 244, 238), (226, 230, 226))
    d = _d(img)
    x0, y0, w = 620, 720, 800
    _car_side(d, x0, y0, w, col=(200, 206, 214), win=(236, 240, 244))
    s = w / 1000
    fill = (250, 206, 110)
    d.ellipse([x0 + 330 * s, y0 - 260 * s, x0 + 440 * s, y0 - 150 * s], fill=fill, outline=(200, 140, 40), width=4)  # 運転席の前
    d.ellipse([x0 + 380 * s, y0 - 300 * s, x0 + 760 * s, y0 - 250 * s], fill=fill, outline=(200, 140, 40), width=4)  # 天井
    d.ellipse([x0 + 740 * s, y0 - 250 * s, x0 + 820 * s, y0 - 150 * s], fill=fill, outline=(200, 140, 40), width=4)  # 追突用
    for x in (x0 + 10 * s, x0 + w - 40 * s):                                    # バンパーの感知装置
        d.rectangle([x, y0 - 90 * s, x + 30 * s, y0 - 50 * s], fill=(200, 60, 50))
    d.line([(x0 + 40 * s, y0 - 70 * s), (x0 + w - 40 * s, y0 - 70 * s)], fill=(200, 60, 50), width=3)
    _text_c(d, x0 + 120 * s, y0 - 420 * s, "前の席 約220L", 40, INK)
    d.line([(x0 + 150 * s, y0 - 360 * s), (x0 + 360 * s, y0 - 240 * s)], fill=INK, width=3)
    _text_c(d, x0 + 570 * s, y0 - 400 * s, "天井 約270L", 44, INK)
    _text_c(d, x0 + 500 * s, y0 + 100 * s, "バンパーで衝撃を感じる", 42, (200, 60, 50))
    return img


def yanase():
    """1960年代の輸入車の会社。ガラス越しの外国車と、応接の机。"""
    img = _rgb(base((230, 228, 222), (210, 208, 200)))
    wood_floor(img, FLOOR, col=(150, 130, 110), line=(130, 112, 94))
    d = _d(img)
    d.rectangle([640, 120, 1280, 560], fill=(200, 222, 236), outline=(120, 120, 126), width=10)  # ガラス
    d.line([(960, 120), (960, 560)], fill=(120, 120, 126), width=8)
    _car_side(d, 700, 520, 520, col=(40, 40, 50))
    _table(d, 780, 1140, 660, col=(110, 80, 56))
    d.rectangle([900, 630, 1020, 660], fill=(236, 236, 230))                    # 資料
    return img


def jikken():
    """防衛庁の実験施設。座席の人形の前でふくらんだ袋と、高速度カメラ。"""
    img = _rgb(base((210, 212, 214), (180, 182, 186)))
    wood_floor(img, FLOOR, col=(120, 122, 126), line=(100, 102, 106))
    d = _d(img)
    d.rectangle([0, 60, W, 100], fill=(90, 92, 96))
    for x in (400, 1500):
        d.rectangle([x, 100, x + 20, 180], fill=(60, 60, 64))
        d.ellipse([x - 40, 170, x + 60, 230], fill=(250, 240, 200))
    d.rectangle([780, 520, 900, 720], fill=(80, 84, 90))                        # 座席
    d.rectangle([760, 700, 1000, 740], fill=(80, 84, 90))
    d.ellipse([850, 440, 910, 500], fill=(230, 200, 150))                       # 人形
    d.rectangle([850, 500, 910, 640], fill=(230, 200, 150))
    d.ellipse([920, 440, 1080, 620], fill=BAG, outline=BAG_EDGE, width=5)       # ふくらんだ袋
    d.rectangle([1060, 520, 1120, 740], fill=(70, 70, 76))                      # 袋の台
    d.rectangle([1160, 560, 1240, 620], fill=(40, 40, 44))                      # 高速度カメラ
    d.ellipse([1140, 570, 1180, 610], fill=(20, 20, 24))
    for k in (-1, 0, 1):
        d.line([(1200, 620), (1200 + k * 50, 760)], fill=(40, 40, 44), width=5)
    return img


def benz():
    """1960年代の西ドイツの会議室。映写機とスクリーンの袋の映像。"""
    img = _rgb(base((222, 222, 218), (200, 200, 196)))
    wood_floor(img, FLOOR, col=(110, 90, 76), line=(90, 74, 62))
    d = _d(img)
    d.rectangle([760, 120, 1160, 400], fill=(240, 240, 236), outline=(80, 80, 86), width=6)  # スクリーン
    d.rectangle([780, 140, 1140, 380], fill=(70, 70, 76))
    d.ellipse([900, 190, 1060, 330], fill=(230, 230, 224))                      # 映像の袋
    _table(d, 760, 1160, 640, col=(100, 80, 64))
    d.rectangle([900, 570, 1010, 640], fill=(50, 50, 56))                       # 映写機
    for cx in (920, 990):
        d.ellipse([cx - 30, 520, cx + 30, 580], outline=(50, 50, 56), width=8)
    return img


def unyusho():
    """役所の部屋。書類の山と判子、書棚。"""
    img = _rgb(base((226, 222, 212), (206, 202, 192)))
    wood_floor(img, FLOOR, col=(120, 100, 80), line=(100, 84, 66))
    d = _d(img)
    d.rectangle([1500, 200, 1900, 780], fill=(120, 96, 72))
    for r in range(4):
        d.rectangle([1500, 330 + r * 110, 1900, 342 + r * 110], fill=(90, 70, 52))
        for k in range(6):
            d.rectangle([1520 + k * 60, 260 + r * 110, 1560 + k * 60, 330 + r * 110], fill=(236, 230, 214))
    _table(d, 760, 1160, 640, col=(110, 86, 62))
    for k in range(3):
        d.rectangle([790 + k * 120, 560 - k * 20, 900 + k * 120, 640], fill=(240, 236, 224), outline=(170, 160, 140), width=2)
    d.rectangle([1100, 600, 1120, 640], fill=(160, 30, 30))                     # 判子
    return img


def tv():
    """1960年代の茶の間。脚付きテレビに車と袋、座卓に歩行者を守る袋の下書き。"""
    img = _rgb(base((228, 216, 192), (208, 196, 172)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([800, 250, 1120, 520], fill=(120, 86, 56))                      # テレビの箱
    d.rounded_rectangle([830, 280, 1060, 490], radius=30, fill=(60, 70, 66))
    _car_side(d, 850, 450, 180, col=(170, 180, 176), win=(90, 100, 96))
    d.ellipse([905, 350, 950, 395], fill=(230, 236, 230))
    for x in (830, 1090):
        d.line([(x, 520), (x - 10, 620)], fill=(80, 60, 40), width=8)
    d.rectangle([740, 700, 1180, 740], fill=(120, 86, 56))                      # 座卓
    d.rectangle([860, 660, 1080, 700], fill=(244, 240, 228))                    # 下書き
    d.rectangle([880, 684, 960, 696], fill=(90, 120, 170))                      # 車
    d.line([(960, 688), (1040, 668)], fill=(200, 80, 60), width=3)              # 棒の袋と網
    for k in range(4):
        d.line([(990 + k * 14, 680), (990 + k * 14, 696)], fill=(90, 90, 96), width=1)
    return img


def crash():
    """衝突試験場。コンクリートの壁にぶつかった車と、ふくらんだ袋。"""
    img = vgrad((W, H), (200, 206, 212), (170, 176, 182))
    d = _d(img)
    d.rectangle([0, 780, W, H], fill=(120, 120, 124))
    for k in range(-2, 14):
        d.line([(k * 160, 780), (k * 160 - 40, H)], fill=(250, 220, 60), width=4)
    d.rectangle([1120, 380, 1200, 800], fill=(170, 170, 166))                   # 壁
    for y in range(400, 800, 60):
        d.line([(1120, y), (1200, y + 20)], fill=(40, 40, 44), width=6)
    _car_side(d, 620, 780, 500, col=(200, 200, 204), win=(210, 224, 232))
    d.ellipse([820, 590, 900, 660], fill=BAG, outline=BAG_EDGE, width=3)        # 窓越しの袋
    return img


def showroom():
    """1980年代の販売店。展示の乗用車と、エアバッグの説明パネル。"""
    img = _rgb(base((236, 236, 232), (216, 216, 212)))
    d = _d(img)
    d.rectangle([0, FLOOR - 40, W, H], fill=(200, 200, 204))
    for x in range(0, W, 240):
        d.line([(x, FLOOR - 40), (x - 100, H)], fill=(186, 186, 190), width=3)
    d.rectangle([0, 80, W, 520], fill=(200, 220, 236))                          # ガラス
    for x in range(0, W, 320):
        d.line([(x, 80), (x, 520)], fill=(160, 170, 180), width=8)
    _car_side(d, 660, 840, 600, col=(150, 30, 40))
    d.rectangle([860, 170, 1060, 330], fill=(250, 250, 246), outline=(120, 120, 126), width=5)  # 説明パネル
    _wheel(d, 960, 250, 60)
    return img


def nenpyo():
    """年表の板。ふくらむ袋の特許から実用化まで。"""
    img = vgrad((W, H), (244, 242, 236), (226, 226, 220))
    d = _d(img)
    d.rectangle([600, 120, 1320, 760], fill=(250, 250, 246), outline=(120, 120, 126), width=6)
    d.line([(700, 180), (700, 720)], fill=(90, 90, 96), width=6)
    rows = [("1951", "ドイツ リンデラー 出願"), ("1952", "アメリカ ヘトリック 出願"), ("1965", "日本 小堀保三郎 出願"),
            ("1980", "西ドイツ 初めて客のもとへ"), ("1987", "日本 国産車に初めて")]
    f = _font(44)
    for k, (y, t) in enumerate(rows):
        yy = 200 + k * 105
        col = (200, 60, 50) if y == "1965" else INK
        d.ellipse([686, yy + 12, 714, yy + 40], fill=col)
        d.text((730, yy), y, font=f, fill=col)
        d.text((730, yy + 52), t, font=_font(34), fill=col)
    return img


def shikumi():
    """図解: 感知 → 点火 → ふくらむ → しぼむ、と時間の帯。キャラの間（x640〜1280）に収める。"""
    img = vgrad((W, H), (244, 244, 238), (226, 230, 226))
    d = _d(img)
    steps = [("衝撃を感じる", (200, 60, 50)), ("ガスを作る", (230, 140, 40)), ("ふくらむ", (60, 130, 200)),
             ("穴から抜ける", (90, 150, 90))]
    bw, gap, x0, top = 140, 165, 640, 300
    for k, (t, col) in enumerate(steps):
        x = x0 + k * gap
        d.rounded_rectangle([x, top, x + bw, top + 150], radius=20, fill=(250, 250, 246), outline=col, width=6)
        _text_c(d, x + bw / 2, top + 160, t, 26, col)
        if k < 3:
            d.polygon([(x + bw + 4, top + 65), (x + gap - 4, top + 75), (x + bw + 4, top + 85)], fill=INK)
    d.rectangle([x0 + 35, top + 30, x0 + 105, top + 120], fill=(200, 60, 50))            # センサー
    d.rectangle([x0 + gap + 30, top + 45, x0 + gap + 110, top + 105], fill=(120, 120, 126))  # ガス発生器
    d.ellipse([x0 + gap * 2 + 12, top + 22, x0 + gap * 2 + 128, top + 128], fill=BAG, outline=BAG_EDGE, width=4)
    d.ellipse([x0 + gap * 3 + 20, top + 45, x0 + gap * 3 + 120, top + 105], fill=BAG, outline=BAG_EDGE, width=4)
    for k in range(3):                                                           # 穴
        cx = x0 + gap * 3 + 55 + k * 16
        d.ellipse([cx - 5, top + 70, cx + 5, top + 80], fill=INK)
    bx0, bx1, by = 640, 1280, 640
    a, b = bx0 + (bx1 - bx0) * 30 / 110, bx0 + (bx1 - bx0) * 60 / 110
    d.rectangle([bx0, by, a, by + 60], fill=(240, 180, 150), outline=INK, width=3)       # 時間の帯
    d.rectangle([a, by, b, by + 60], fill=(170, 200, 236), outline=INK, width=3)
    d.rectangle([b, by, bx1, by + 60], fill=(190, 220, 190), outline=INK, width=3)
    _text_c(d, (bx0 + a) / 2, by + 70, "約0.03秒", 28, INK)
    _text_c(d, (a + b) / 2, by + 70, "約0.03秒", 28, INK)
    _text_c(d, (b + bx1) / 2, by + 70, "約0.05秒", 28, INK)
    _text_c(d, 960, 560, "合計 約0.11秒", 40, (200, 60, 50))
    return img


def shikumi2():
    """ガス発生器の断面。粒の薬と、暑さ・湿気の印。"""
    img = vgrad((W, H), (236, 236, 232), (216, 220, 220))
    d = _d(img)
    d.rounded_rectangle([760, 300, 1160, 600], radius=60, fill=(170, 172, 180), outline=(100, 100, 110), width=8)
    d.rounded_rectangle([800, 340, 1120, 560], radius=40, fill=(220, 214, 196))
    import random
    rnd = random.Random(3)
    for _ in range(90):
        x, y = rnd.uniform(820, 1100), rnd.uniform(360, 540)
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(150, 140, 110))
    d.ellipse([640, 150, 760, 270], fill=(250, 180, 60))                        # 太陽（暑さ）
    for k in range(3):                                                          # しずく（湿気）
        x = 1200 + k * 60
        d.polygon([(x, 150), (x - 20, 200), (x + 20, 200)], fill=(90, 150, 220))
        d.ellipse([x - 20, 180, x + 20, 220], fill=(90, 150, 220))
    return img


def gendai():
    """今の道路。窓の内側のカーテンエアバッグと、ボンネットの後ろでふくらむ歩行者用の袋。"""
    img = vgrad((W, H), (170, 206, 236), (220, 232, 240))
    d = _d(img)
    d.rectangle([0, 780, W, H], fill=(110, 110, 116))
    for x in range(0, W, 200):
        d.rectangle([x, 900, x + 100, 916], fill=(240, 240, 240))
    x0, w = 780, 560
    _car_side(d, x0, 820, w, col=(60, 110, 160))
    s = w / 1000
    d.rectangle([x0 + 300 * s, 820 - 285 * s, x0 + 790 * s, 820 - 240 * s], fill=BAG)   # カーテンエアバッグ
    d.ellipse([x0 + 220 * s, 820 - 230 * s, x0 + 360 * s, 820 - 150 * s], fill=BAG, outline=BAG_EDGE, width=3)  # 歩行者用
    px = 680
    d.ellipse([px - 25, 520, px + 25, 570], fill=(60, 60, 66))                  # 歩く人
    d.rectangle([px - 20, 570, px + 20, 700], fill=(60, 60, 66))
    d.line([(px - 10, 700), (px - 25, 780)], fill=(60, 60, 66), width=12)
    d.line([(px + 10, 700), (px + 30, 780)], fill=(60, 60, 66), width=12)
    return img


def hotel():
    """昭和30年代のホテルの広間。金屏風の前に見台と三味線。"""
    img = _rgb(base((200, 190, 170), (170, 160, 140)))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(120, 40, 40))                            # 赤い毛氈
    d.rectangle([0, 690, W, 712], fill=(90, 30, 30))
    for k in range(6):                                                          # 金屏風
        x = 560 + k * 134
        col = (214, 184, 100) if k % 2 == 0 else (196, 166, 86)
        d.polygon([(x, 200), (x + 134, 190 if k % 2 else 210), (x + 134, 700), (x, 700)], fill=col)
    for x in (820, 1100):                                                       # 見台
        d.line([(x, 700), (x, 600)], fill=(40, 30, 24), width=6)
        d.polygon([(x - 50, 560), (x + 50, 560), (x + 40, 610), (x - 40, 610)], fill=(40, 30, 24))
    d.line([(960, 420), (960, 640)], fill=(60, 40, 30), width=8)                # 三味線
    d.rounded_rectangle([916, 630, 1004, 700], radius=10, fill=(236, 226, 200), outline=(60, 40, 30), width=5)
    for k in range(3):
        d.line([(952, 436 + k * 18), (972, 432 + k * 18)], fill=(60, 40, 30), width=5)
    return img


# ---- 場面の途中で差し替える「状況が変わった」背景（2026-10-01 ユーザー「煙の演出いいね。こういうの増やしたい」）
def mingei_afure():
    """民芸の座敷。器が棚に入りきらず、畳の上まであふれている。"""
    img = mingei()
    d = _d(img)
    cols = [(120, 80, 50), (60, 80, 110), (170, 140, 90), (90, 110, 90), (150, 70, 50)]
    k = 0
    for row, y in enumerate((830, 760, 900)):                                    # 畳の上に並ぶ器
        for x in range(120 + row * 40, 1800, 150):
            if 700 < x < 1220 and y < 880:
                continue
            col = cols[k % len(cols)]
            k += 1
            d.ellipse([x, y - 80, x + 80, y], fill=col)
            d.rectangle([x + 22, y - 98, x + 58, y - 72], fill=col)
    for x, y in ((820, 470), (900, 420), (1000, 470), (1080, 430)):              # 棚の上にも積む
        col = cols[(x // 10) % len(cols)]
        d.ellipse([x, y - 70, x + 70, y], fill=col)
    return img


def zukai_fukuro():
    """図解: 袋をつけすぎて、車の中が袋でぱんぱん。窓から袋がはみ出している。"""
    img = zukai()
    d = _d(img)
    x0, y0, w = 620, 720, 800
    s = w / 1000
    for cx, cy, r in ((450, -230, 120), (620, -240, 130), (300, -200, 90), (760, -200, 100),
                      (540, -330, 110), (380, -330, 80), (700, -320, 90), (880, -150, 70)):
        d.ellipse([x0 + (cx - r) * s, y0 + (cy - r * 0.8) * s, x0 + (cx + r) * s, y0 + (cy + r * 0.8) * s],
                  fill=(250, 206, 110), outline=(200, 140, 40), width=4)
    return img


def jikken_mae():
    """実験施設。作動の前で、袋はまだたたまれている。"""
    img = jikken()
    d = _d(img)
    d.rectangle([915, 430, 1090, 630], fill=(196, 198, 202))                     # ふくらんだ袋を消す
    d.rectangle([1050, 600, 1100, 660], fill=(240, 236, 220), outline=(170, 160, 140), width=3)  # たたんだ袋
    return img


def gic3_seikyu():
    """GIC の机。特許証の上に、特許料と研究費の請求書が山積み。"""
    img = gic3()
    d = _d(img)
    for pile, (px, n) in enumerate(((760, 16), (960, 22))):                    # 机の上に2つの山
        for k in range(n):
            x, y = px + ((k * 7) % 5 - 2) * 6, 600 - k * 16
            d.rectangle([x, y, x + 170, y + 16], fill=(246, 244, 236), outline=(150, 140, 120), width=2)
            d.line([(x + 14, y + 8), (x + 120, y + 8)], fill=(190, 60, 50), width=3)
    return img


def crash_yama():
    """衝突試験場。ぶつけた試験車が何台も並んでいる。"""
    img = crash()
    d = _d(img)
    for k, x in enumerate((60, 330, 1300, 1560)):
        _car_side(d, x, 780 + (k % 2) * 30, 240, col=(196 - k * 8, 196, 204), win=(210, 224, 232))
        d.line([(x + 230, 700 + (k % 2) * 30), (x + 200, 760 + (k % 2) * 30)], fill=(40, 40, 44), width=6)
    return img


LOCATIONS = {
    "kb_kuruma": kuruma, "kb_kuruma2": kuruma2, "kb_mura": mura, "kb_tsushin": tsushin, "kb_fudo": fudo,
    "kb_mingei_afure": mingei_afure, "kb_zukai_fukuro": zukai_fukuro, "kb_jikken_mae": jikken_mae,
    "kb_gic3_seikyu": gic3_seikyu, "kb_crash_yama": crash_yama,
    "kb_kojo": kojo, "kb_kojo2": kojo2, "kb_jimusho": jimusho, "kb_mingei": mingei,
    "kb_gic": gic, "kb_gic2": gic2, "kb_gic3": gic3, "kb_gic_mono": gic_mono, "kb_hikouki": hikouki,
    "kb_zukai": zukai, "kb_yanase": yanase, "kb_jikken": jikken, "kb_benz": benz,
    "kb_unyusho": unyusho, "kb_tv": tv, "kb_crash": crash, "kb_showroom": showroom,
    "kb_nenpyo": nenpyo, "kb_hotel": hotel, "kb_shikumi": shikumi, "kb_shikumi2": shikumi2, "kb_gendai": gendai,
}

CARDS = ["1899", "1924", "1937", "1962", "1964", "1965", "1975", "1980", "1987"]


def year_card(text: str) -> Image.Image:
    """黒地に年号だけのカード。キャラと同居させない単独シーンで使う。"""
    img = Image.new("RGB", (W, H), (18, 18, 20))
    d = _d(img)
    font = _font(150)
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
        if only and f"kb_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"kb_card_{y}.png")
        print(f"生成完了: kb_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
