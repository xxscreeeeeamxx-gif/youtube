#!/usr/bin/env python3
"""第5弾4本（2026-11-13〜16）の背景を生成する。

接頭辞: fn_（船井電機の破産）/ vh_（VHSの誕生・高野鎮雄）/ ya_（ヤオハン・和田一夫）/ cg_（長銀の破綻と頭取の逆転無罪）
方針は gen_now_bgs.py と同じ。実在の会社のロゴ・社名の文字・製品の意匠は描かない（VHS・ベータのマークも描かない）。
差し替え用（_zaiko・_gyoretsu・_akaji・_up など）は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now5_bgs.py [名前...]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import _boxes, _papers, _phone, _window, year_card  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _d, _rgb, kaigi, yakuin  # noqa: E402
from scripts.gen_now2_bgs import heya2, kabunushi_kaijo, shoken  # noqa: E402
from scripts.gen_now_bgs import gms as _gms  # noqa: E402
from scripts.gen_sogo_bgs import ginkou as _sogo_ginkou, kokkai as _sogo_kokkai, saibansho as _sogo_saibansho, uriba as _sogo_uriba  # noqa: E402
from scripts.gen_now3_bgs import _desk, jimusho90, kojo_soto  # noqa: E402
from scripts.gen_now4_bgs import ol_london  # noqa: E402
from scripts.gen_sega_bgs import _glow, _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402

RED = (200, 40, 40)
LINE = (90, 86, 80)


# ---------------------------------------------------------------- 小物
def _deck(d, x, y, s=1.0, col=(196, 192, 184), w=300, h=90):
    """1970年代のビデオデッキの正面（下の端の中央が x, y）。上から差す型、ピアノ鍵盤のボタン。印は描かない。"""
    w2, hh = w * s / 2, h * s
    d.rectangle([x - w2, y - hh, x + w2, y], fill=col, outline=LINE, width=3)
    d.rectangle([x - w2, y - hh, x + w2, y - hh + 14 * s], fill=tuple(max(c - 40, 0) for c in col))   # 上面の差し込み口
    for k in range(6):                                                                                  # 鍵盤のボタン
        bx = x - w2 + 20 * s + k * 26 * s
        d.rectangle([bx, y - 40 * s, bx + 20 * s, y - 14 * s], fill=(236, 234, 228), outline=LINE)
    d.rectangle([x + w2 - 110 * s, y - 60 * s, x + w2 - 20 * s, y - 30 * s], fill=(40, 40, 46))      # 時計の窓
    d.line([(x + w2 - 100 * s, y - 45 * s), (x + w2 - 30 * s, y - 45 * s)], fill=(120, 220, 140), width=max(int(3 * s), 1))


def _tape(d, x, y, s=1.0):
    """ビデオテープ（下の端の中央）。2つのリールの窓だけ。"""
    d.rectangle([x - 60 * s, y - 34 * s, x + 60 * s, y], fill=(30, 30, 34), outline=(70, 70, 76))
    for cx in (x - 28 * s, x + 28 * s):
        d.ellipse([cx - 12 * s, y - 24 * s, cx + 12 * s, y - 6 * s], fill=(90, 90, 96))
    d.rectangle([x - 40 * s, y - 32 * s, x + 40 * s, y - 26 * s], fill=(236, 234, 228))


def _crt_tv(d, x, y, s=1.0, screen=(70, 110, 150)):
    """脚つきのブラウン管テレビ（下の端の中央）。"""
    d.rectangle([x - 110 * s, y - 220 * s, x + 110 * s, y - 40 * s], fill=(140, 100, 70), outline=LINE, width=3)
    d.rounded_rectangle([x - 90 * s, y - 204 * s, x + 50 * s, y - 60 * s], radius=int(20 * s), fill=screen)
    for k in range(2):
        d.ellipse([x + 64 * s, y - 190 * s + k * 50 * s, x + 96 * s, y - 158 * s + k * 50 * s], fill=(60, 50, 40))
    for lx in (x - 80 * s, x + 70 * s):
        d.line([(lx, y - 40 * s), (lx + (10 if lx > x else -10) * s, y)], fill=(70, 60, 50), width=max(int(6 * s), 1))


def _office_wall(top=(214, 222, 214), bottom=(200, 208, 200)):
    """1970年代の事務所の壁と床（うすい緑の壁、灰色の床）。"""
    img = _rgb(base(top, bottom))
    wood_floor(img, FLOOR, col=(170, 166, 156), line=(156, 152, 142))
    return img


# ---------------------------------------------------------------- VHS・高野鎮雄
def vh_heya():
    """今の部屋。机にビデオテープの山、テレビ台にデッキ。"""
    img = heya2("none")
    d = _d(img)
    for k, (x, n) in enumerate(((240, 4), (360, 3), (480, 5))):
        for j in range(n):
            _tape(d, x, 640 - j * 36, 0.9)
    d.rectangle([1460, 628, 1720, 668], fill=(40, 40, 46), outline=(90, 90, 96), width=2)
    d.rectangle([1490, 642, 1620, 650], fill=(20, 20, 22))
    return img


def vh_jigyobu():
    """1970年代のビデオ事業部の事務所。鉄の机と黒電話、黒板に下がり続ける線。"""
    img = _office_wall()
    d = _d(img)
    _window(d, 1440, 120, 1820, 400, sky=(196, 214, 228))
    d.rectangle([140, 110, 760, 420], fill=(46, 70, 56), outline=(120, 96, 70), width=10)        # 黒板
    pts = [(190, 180), (300, 210), (410, 260), (520, 300), (630, 360), (720, 390)]
    d.line(pts, fill=(250, 250, 250), width=6)
    d.line([(190, 380), (730, 380)], fill=(220, 220, 220), width=3)
    _desk(d, 120, 620, 640)
    _desk(d, 1300, 1820, 640)
    _papers(d, 180, 630, n=3)
    _phone(d, 520, 636, 0.9)
    _papers(d, 1360, 630, n=2)
    _phone(d, 1700, 636, 0.9)
    return img


def vh_kaihatsu():
    """開発室。作業台に開いた試作機、波形の出る測定器、壁に12マスの表。"""
    img = _rgb(base((230, 232, 228), (214, 216, 212)))
    wood_floor(img, FLOOR, col=(176, 180, 182), line=(162, 166, 168))
    d = _d(img)
    d.rectangle([120, 100, 760, 430], fill=(250, 250, 248), outline=(150, 150, 146), width=6)    # 12マスの表
    for c in range(1, 4):
        d.line([(120 + c * 160, 100), (120 + c * 160, 430)], fill=(150, 150, 146), width=3)
    for r in range(1, 3):
        d.line([(120, 100 + r * 110), (760, 100 + r * 110)], fill=(150, 150, 146), width=3)
    for c in range(4):
        for r in range(3):
            x, y = 140 + c * 160, 130 + r * 110
            d.line([(x, y), (x + 110, y)], fill=(60, 80, 140), width=5)
            d.line([(x, y + 30), (x + 80, y + 30)], fill=(120, 120, 126), width=4)
    d.rectangle([820, 600, 1840, 640], fill=(220, 214, 200), outline=(150, 146, 136), width=3)   # 作業台
    for x in (860, 1790):
        d.rectangle([x, 640, x + 30, FLOOR], fill=(150, 146, 136))
    d.rectangle([980, 500, 1280, 598], fill=(190, 190, 194), outline=LINE, width=3)              # ふたを開けた試作機
    d.ellipse([1070, 510, 1150, 590], fill=(160, 166, 176), outline=LINE, width=3)               # 回転ヘッドの筒
    d.ellipse([1180, 530, 1230, 580], fill=(120, 120, 126))
    d.ellipse([1010, 530, 1060, 580], fill=(120, 120, 126))
    d.rectangle([1480, 430, 1740, 598], fill=(70, 74, 80), outline=LINE, width=3)                # 測定器
    d.rectangle([1500, 450, 1660, 570], fill=(20, 40, 30))
    wave = [(1500 + i * 10, 510 + (24 if i % 4 < 2 else -24)) for i in range(17)]
    d.line(wave, fill=(120, 240, 140), width=3)
    return img


def vh_osetsu():
    """ビクターの一室。白い布の長机に、大きさの違う3台の機械が並ぶ（冒頭）。"""
    img = _rgb(base((200, 180, 150), (184, 164, 136)))
    wood_floor(img, FLOOR, col=(120, 90, 64), line=(104, 78, 54))
    d = _d(img)
    for k in range(9):                                                                          # 板張りの壁
        d.line([(k * 220, 0), (k * 220, FLOOR)], fill=(176, 156, 128), width=4)
    d.rectangle([780, 120, 1140, 360], fill=(150, 120, 80), outline=(110, 84, 56), width=10)     # 額
    d.rectangle([800, 140, 1120, 340], fill=(110, 140, 120))
    d.rectangle([520, 600, 1400, 640], fill=(248, 248, 244), outline=(200, 200, 196), width=3)   # 長机
    d.rectangle([520, 640, 1400, 720], fill=(240, 240, 236))
    _deck(d, 660, 598, 0.8, col=(200, 196, 188), w=300, h=110)     # いちばん大きい
    _deck(d, 960, 598, 0.8, col=(176, 176, 182), w=280, h=96)
    _deck(d, 1250, 598, 0.8, col=(210, 206, 196), w=250, h=80)     # いちばん小さい
    return img


def vh_soudanyaku():
    """親会社の相談役室。濃い木の壁、掛け軸、応接の椅子。"""
    img = _rgb(base((120, 88, 60), (104, 76, 52)))
    wood_floor(img, FLOOR, col=(90, 64, 44), line=(76, 54, 36))
    d = _d(img)
    for k in range(9):
        d.line([(k * 220, 0), (k * 220, FLOOR)], fill=(96, 70, 46), width=6)
    d.rectangle([860, 90, 1060, 470], fill=(236, 228, 206), outline=(70, 50, 30), width=8)      # 掛け軸
    d.rectangle([880, 110, 1040, 450], fill=(244, 238, 220))
    for k in range(4):
        d.line([(960, 140 + k * 70), (960, 190 + k * 70)], fill=(40, 34, 30), width=8)
    d.rectangle([700, 620, 1220, 660], fill=(70, 50, 34))                                        # 低い机
    for x in (480, 1300):                                                                        # 椅子
        d.rounded_rectangle([x, 520, x + 160, 700], radius=20, fill=(120, 40, 36), outline=(80, 30, 26), width=4)
    return img


def vh_line(yoso=False):
    """工場の組み立てライン。ベルトの上を機械が流れる。yoso は箱に他社の色の帯（文字なし）。"""
    img = vgrad((W, H), (226, 228, 230), (206, 208, 212))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(170, 172, 176))
    for k in range(6):
        d.rectangle([k * 340 + 40, 40, k * 340 + 90, 70], fill=(250, 250, 236))
    d.rectangle([0, 600, W, 640], fill=(70, 74, 80))                                             # ベルト
    for k in range(24):
        d.line([(k * 80, 600), (k * 80, 640)], fill=(100, 104, 110), width=3)
    cols = [(196, 192, 184), (176, 176, 182), (190, 186, 176)]
    for k in range(6):
        x = 160 + k * 320
        _deck(d, x, 598, 0.7, col=cols[k % 3])
        if yoso:
            band = [(40, 90, 170), (200, 60, 50), (40, 140, 90)][k % 3]
            d.rectangle([x - 105, 546, x + 105, 556], fill=band)
    return img


def vh_eigyo(zaiko=False):
    """営業の部屋。机と電話。zaiko は壁ぎわに段ボールの山（在庫）。"""
    img = _office_wall((226, 222, 210), (212, 208, 196))
    d = _d(img)
    _window(d, 760, 120, 1160, 380, sky=(196, 214, 228))
    _desk(d, 120, 640, 640)
    _papers(d, 180, 630, n=4)
    _phone(d, 560, 636, 0.9)
    _boxes(d, 1300, FLOOR, n=3, rows=2)
    if zaiko:
        _boxes(d, 1240, FLOOR, n=4, rows=5)
        _boxes(d, 60, 600, n=3, rows=3)
    return img


def vh_denkiten(gyoretsu=False):
    """1970年代の町の電器店。脚つきのテレビとデッキの見本。gyoretsu は手前に客の行列。"""
    img = _rgb(base((236, 232, 220), (222, 218, 206)))
    wood_floor(img, FLOOR, col=(196, 186, 168), line=(180, 170, 152))
    d = _d(img)
    d.rectangle([0, 40, W, 100], fill=(40, 90, 160))                                            # 帯（文字なし）
    for k in range(5):
        _crt_tv(d, 260 + k * 350, 470, 0.9, screen=[(70, 110, 150), (110, 150, 90), (160, 110, 80)][k % 3])
    d.rectangle([560, 560, 1360, 600], fill=(150, 116, 84))                                      # 見本の台
    _deck(d, 760, 558, 0.8)
    _deck(d, 1160, 558, 0.8, col=(176, 176, 182))
    if gyoretsu:
        _person_line(d, 40, 1020, 11, 1.05)
        _person_line(d, 1040, 1020, 11, 1.05)
    return img


def vh_kojo_niwa():
    """曇り空の工場の庭を、社員の列が埋める（1992年の別れ）。"""
    img = kojo_soto()
    d = _d(img)
    d.rectangle([0, 0, W, 300], fill=(176, 180, 188))
    for row, y in enumerate((760, 860, 960)):
        for x0 in (0, 960):
            _person_line(d, x0 + row * 30, y, 13, 0.75 + row * 0.12,
                         cols=[(40, 40, 46), (56, 56, 62), (30, 30, 36)])
    return img


def vh_hakubutsukan():
    """博物館のガラスの展示ケース。中に古いデッキと説明の板（文字は線）。"""
    img = _rgb(base((236, 236, 238), (222, 222, 226)))
    wood_floor(img, FLOOR, col=(200, 196, 190), line=(186, 182, 176))
    d = _d(img)
    d.rectangle([640, 300, 1280, 700], fill=(214, 226, 232), outline=(150, 160, 170), width=6)   # ケース
    d.rectangle([660, 640, 1260, 700], fill=(240, 240, 240))
    _deck(d, 960, 600, 1.0)
    d.rectangle([740, 660, 1180, 690], fill=(250, 250, 250), outline=(180, 180, 180))
    d.line([(760, 675), (1100, 675)], fill=(120, 120, 126), width=4)
    d.rectangle([640, 700, 1280, FLOOR], fill=(150, 150, 156))
    _glow(img, 960, 280, 300, (255, 250, 230), 70)
    return img


# ---------------------------------------------------------------- ヤオハン・和田一夫
def _veg_crates(d, x0, y, n=6):
    """八百屋の木箱に野菜（トマト・キャベツ・大根・みかん）。"""
    kinds = [((210, 50, 40), "o"), ((130, 180, 90), "o"), ((240, 240, 230), "l"), ((240, 150, 40), "o")]
    for k in range(n):
        x = x0 + k * 170
        d.rectangle([x, y - 60, x + 150, y], fill=(170, 130, 80), outline=(110, 80, 50), width=3)
        col, shape = kinds[k % 4]
        for j in range(4):
            cx = x + 22 + j * 34
            if shape == "o":
                d.ellipse([cx - 16, y - 92, cx + 16, y - 60], fill=col, outline=(90, 70, 50))
            else:
                d.rounded_rectangle([cx - 10, y - 120, cx + 10, y - 60], radius=8, fill=col, outline=(160, 160, 150))


def ya_heya():
    """今の部屋。机に古い封筒と、商品券のような小さな券（文字は線）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([220, 600, 400, 640], fill=(236, 226, 200), outline=(170, 150, 120), width=2)    # 封筒
    for k in range(3):
        x = 430 + k * 60
        d.rectangle([x, 606 - k * 6, x + 110, 640 - k * 6], fill=(250, 244, 226), outline=(190, 150, 90), width=2)
        d.line([(x + 12, 620 - k * 6), (x + 70, 620 - k * 6)], fill=(200, 60, 50), width=3)
    return img


def ya_yaoya(yakeato=False):
    """1950年代の熱海の八百屋の店先。木の店構えに野菜の木箱。yakeato は大火のあと、黒い焼け跡の前の軒下で売る。"""
    if yakeato:
        img = vgrad((W, H), (150, 150, 152), (190, 186, 178))
        d = _d(img)
        d.rectangle([0, 760, W, H], fill=(110, 100, 90))
        for k in range(9):                                                                     # 焼け残りの柱
            x = 120 + k * 210
            d.rectangle([x, 300 + (k % 3) * 60, x + 26, 760], fill=(40, 34, 30))
        d.line([(100, 520), (700, 460)], fill=(40, 34, 30), width=20)
        d.line([(1100, 480), (1800, 560)], fill=(40, 34, 30), width=20)
        d.rectangle([520, 380, 1400, 420], fill=(120, 90, 60))                                 # 旅館の軒
        d.polygon([(480, 380), (1440, 380), (1380, 330), (540, 330)], fill=(80, 70, 66))
        _veg_crates(d, 560, 760, n=5)
        return img
    img = vgrad((W, H), (200, 216, 230), (226, 232, 236))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(150, 140, 126))
    d.rectangle([120, 160, 1800, 760], fill=(160, 124, 84), outline=(100, 74, 50), width=8)
    d.polygon([(80, 160), (1840, 160), (1760, 90), (160, 90)], fill=(90, 80, 74))              # 屋根
    for k in range(5):                                                                          # のれん（文字なし）
        x = 560 + k * 170
        d.rectangle([x, 170, x + 150, 290], fill=(40, 70, 120))
    d.rectangle([200, 320, 1720, 700], fill=(120, 92, 62))
    _veg_crates(d, 240, 700, n=9)
    return img


def ya_saopaulo():
    """1969年のサンパウロの百貨店。アーチの窓、ガラスのショーケースに靴下。"""
    img = _rgb(base((236, 226, 206), (222, 212, 192)))
    wood_floor(img, FLOOR, col=(170, 120, 80), line=(150, 104, 68))
    d = _d(img)
    for x in (260, 960, 1660):
        d.rectangle([x - 150, 160, x + 150, 480], fill=(190, 214, 230), outline=(150, 120, 90), width=10)
        d.pieslice([x - 150, 60, x + 150, 260], 180, 360, fill=(190, 214, 230), outline=(150, 120, 90), width=10)
    d.rectangle([560, 580, 1360, 700], fill=(220, 232, 236), outline=(140, 120, 100), width=5)   # ショーケース
    for k in range(10):
        x = 600 + k * 74
        d.polygon([(x, 600), (x + 24, 600), (x + 24, 660), (x + 44, 676), (x + 34, 690), (x, 670)],
                  fill=[(200, 60, 60), (60, 90, 160), (240, 240, 240), (90, 150, 90)][k % 4])
    return img


def ya_ame():
    """雨の日の家の前（債権者の家）。門と玄関、斜めの雨。"""
    img = vgrad((W, H), (120, 126, 136), (150, 154, 160))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(96, 98, 104))
    d.rectangle([520, 240, 1400, 760], fill=(210, 200, 186), outline=(120, 110, 100), width=6)    # 家
    d.polygon([(460, 240), (1460, 240), (960, 80)], fill=(150, 80, 60))
    d.rectangle([860, 480, 1060, 760], fill=(110, 70, 50))                                       # 玄関
    for x in (620, 1200):
        d.rectangle([x, 340, x + 140, 460], fill=(190, 206, 214), outline=(120, 110, 100), width=4)
    for k in range(160):                                                                         # 雨
        x = (k * 97) % W
        y = (k * 53) % H
        d.line([(x, y), (x - 14, y + 44)], fill=(200, 206, 216), width=2)
    return img


def ya_hk_office():
    """香港の高層ビルの上の階の執務室。窓いっぱいに港と高層ビル。"""
    img = _rgb(base((226, 226, 230), (212, 212, 218)))
    wood_floor(img, FLOOR, col=(150, 130, 110), line=(134, 116, 98))
    d = _d(img)
    d.rectangle([80, 80, 1840, 600], fill=(170, 200, 226))
    d.rectangle([80, 430, 1840, 600], fill=(70, 120, 160))                                       # 港
    for k in range(16):                                                                          # 対岸のビル
        x = 100 + k * 112
        h = 120 + (k * 37) % 200
        d.rectangle([x, 430 - h, x + 80, 430], fill=(130, 140, 156))
    for x in range(80, 1841, 220):
        d.line([(x, 80), (x, 600)], fill=(90, 90, 96), width=8)
    d.rectangle([700, 640, 1220, 680], fill=(90, 60, 40))                                        # 机
    return img


def ya_peak():
    """山の上の洋館の大広間。シャンデリアと並んだ椅子、ピアノ（音楽会）。"""
    img = _rgb(base((236, 222, 196), (222, 206, 178)))
    wood_floor(img, FLOOR, col=(140, 96, 60), line=(120, 80, 48))
    d = _d(img)
    for x in (300, 960, 1620):
        d.rectangle([x - 110, 120, x + 110, 520], fill=(186, 206, 220), outline=(170, 140, 90), width=10)
    for x in (620, 1300):
        _glow(img, x, 120, 160, (255, 240, 190), 120)
        d = _d(img)
        d.ellipse([x - 60, 90, x + 60, 150], fill=(250, 230, 160))
    d.ellipse([820, 560, 1100, 660], fill=(30, 30, 34))                                          # ピアノ
    d.rectangle([840, 600, 860, 720], fill=(30, 30, 34))
    d.rectangle([1060, 600, 1080, 720], fill=(30, 30, 34))
    for r in range(2):
        for k in range(10):
            x = 120 + k * 180
            d.rectangle([x, 760 + r * 80, x + 60, 800 + r * 80], fill=(150, 40, 40))
    return img


def ya_pudong():
    """1991年の浦東の空き地。草地と、川の向こうの古い街、遠くにクレーン。"""
    img = vgrad((W, H), (190, 206, 220), (220, 226, 230))
    d = _d(img)
    d.rectangle([0, 380, W, 440], fill=(120, 140, 150))                                          # 川
    for k in range(14):
        x = 60 + k * 136
        d.rectangle([x, 300 - (k % 4) * 30, x + 100, 380], fill=(150, 146, 140))
    for x in (1300, 1600):                                                                       # クレーン
        d.line([(x, 440), (x, 160)], fill=(220, 160, 40), width=10)
        d.line([(x - 120, 170), (x + 200, 170)], fill=(220, 160, 40), width=8)
    d.rectangle([0, 440, W, H], fill=(150, 170, 110))
    for k in range(40):
        x = (k * 131) % W
        d.line([(x, 1000), (x + 8, 960)], fill=(110, 140, 80), width=4)
    return img


def ya_shanghai(gunshu=False):
    """上海の巨大な百貨店の正面。長い白い弧の壁と12のアーチ。gunshu は前を人の波が埋める（開業の日）。"""
    img = vgrad((W, H), (180, 206, 230), (214, 226, 236))
    d = _d(img)
    d.pieslice([-300, 120, 2220, 900], 180, 360, fill=(244, 244, 240), outline=(190, 190, 186), width=6)
    d.rectangle([0, 510, W, 760], fill=(244, 244, 240))
    for k in range(6):
        d.line([(0, 200 + k * 60), (W, 200 + k * 60)], fill=(214, 220, 228), width=4)
    for k in range(12):                                                                          # アーチ
        x = 60 + k * 152
        d.rectangle([x, 600, x + 110, 760], fill=(110, 130, 150))
        d.pieslice([x, 545, x + 110, 655], 180, 360, fill=(110, 130, 150))
    d.rectangle([0, 760, W, H], fill=(170, 170, 172))
    if gunshu:
        for row, y in enumerate((860, 960, 1060)):
            for x0 in (0, 960):
                _person_line(d, x0 + row * 20, y, 13, 0.8 + row * 0.12)
    return img


def ya_saijo():
    """葬儀の会場。白い花の祭壇（写真は描かない）と並んだ椅子。"""
    img = _rgb(base((226, 226, 228), (212, 212, 216)))
    wood_floor(img, FLOOR, col=(150, 150, 156), line=(136, 136, 142))
    d = _d(img)
    for r in range(4):                                                                           # 花の段
        y = 220 + r * 90
        d.rectangle([520 - r * 60, y, 1400 + r * 60, y + 70], fill=(240, 240, 236))
        for k in range(14 + r * 2):
            x = 540 - r * 60 + k * 64
            d.ellipse([x, y + 10, x + 46, y + 56], fill=(252, 252, 250), outline=(214, 220, 210))
    d.rectangle([880, 140, 1040, 210], fill=(60, 60, 66))
    for r in range(2):
        for k in range(10):
            x = 120 + k * 180
            d.rectangle([x, 780 + r * 80, x + 70, 820 + r * 80], fill=(70, 70, 76))
    return img


def ya_apart():
    """2000年代の小さなアパートの一室。畳、低い机にパソコン、壁ぎわに本の山。"""
    img = _rgb(base((226, 220, 206), (212, 206, 192)))
    from scripts.gen_drama_bgs import tatami_floor
    tatami_floor(img, FLOOR)
    d = _d(img)
    _window(d, 1300, 140, 1700, 420, sky=(200, 214, 226))
    d.rectangle([660, 640, 1260, 680], fill=(140, 100, 66))
    d.rectangle([700, 680, 730, 760], fill=(110, 80, 54))
    d.rectangle([1190, 680, 1220, 760], fill=(110, 80, 54))
    d.rectangle([860, 520, 1040, 636], fill=(214, 210, 196), outline=LINE, width=3)              # パソコン
    d.rectangle([876, 534, 1024, 620], fill=(60, 90, 130))
    for k in range(5):
        d.rectangle([140, 620 - k * 34, 380, 650 - k * 34], fill=[(150, 60, 50), (60, 90, 140), (200, 180, 120)][k % 3])
    return img


def ya_enkai():
    """ホテルの宴会場。丸いテーブルと舞台（お詫びと感謝の会）。"""
    img = _rgb(base((240, 228, 206), (226, 214, 190)))
    wood_floor(img, FLOOR, col=(170, 60, 50), line=(150, 50, 42))
    d = _d(img)
    d.rectangle([560, 160, 1360, 520], fill=(200, 170, 120), outline=(150, 120, 80), width=8)    # 舞台の幕
    d.rectangle([600, 200, 1320, 480], fill=(230, 210, 170))
    d.rectangle([440, 520, 1480, 580], fill=(110, 80, 56))                                       # 舞台
    for x in (260, 960, 1660):
        _glow(img, x, 80, 140, (255, 240, 200), 100)
    d = _d(img)
    for k, x in enumerate((240, 1680)):
        d.ellipse([x - 160, 760, x + 160, 840], fill=(250, 250, 248), outline=(210, 210, 206), width=3)
    return img


# ---------------------------------------------------------------- 長銀・大野木克信
def cg_heya():
    """今の部屋。机に通帳と銀行からの封筒（文字は線）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([220, 606, 330, 640], fill=(40, 90, 150), outline=(30, 60, 110), width=2)        # 通帳
    d.line([(236, 620), (310, 620)], fill=(220, 220, 230), width=3)
    d.rectangle([360, 598, 560, 640], fill=(250, 250, 246), outline=(170, 170, 166), width=2)    # 封筒
    d.rectangle([380, 608, 460, 618], fill=(200, 60, 50))
    return img


def cg_saikosai():
    """最高裁の小法廷。濃い木の壁、高い背もたれの椅子が並ぶ壇。"""
    img = _rgb(base((110, 80, 56), (96, 70, 48)))
    wood_floor(img, FLOOR, col=(120, 90, 62), line=(104, 76, 52))
    d = _d(img)
    for k in range(10):
        d.line([(k * 200, 0), (k * 200, FLOOR)], fill=(90, 64, 42), width=6)
    d.rectangle([380, 420, 1540, 560], fill=(80, 56, 38), outline=(60, 42, 28), width=6)         # 壇
    for k in range(5):                                                                          # 背もたれの高い椅子
        x = 520 + k * 220
        d.rounded_rectangle([x - 60, 200, x + 60, 430], radius=30, fill=(50, 40, 34), outline=(30, 24, 20), width=4)
    d.rectangle([700, 640, 1220, 700], fill=(96, 70, 48))                                        # 手前の机
    return img


def cg_tochiri():
    """1990年代の頭取室。大きな窓にビル街、重い机と書類。"""
    img = yakuin(view=(170, 186, 204))
    d = _d(img)
    _papers(d, 1500, 610, n=4)
    return img


def cg_honten(yoru=False):
    """1993年に建った本店ビルの外観。段になった高いビルと、手前の公園の木。yoru は夜。"""
    img = vgrad((W, H), (24, 28, 52), (50, 52, 80)) if yoru else vgrad((W, H), (160, 196, 230), (214, 228, 238))
    d = _d(img)
    body = (120, 120, 132) if yoru else (196, 196, 204)
    d.rectangle([620, 120, 1300, 860], fill=body, outline=(90, 90, 100), width=4)
    d.rectangle([520, 400, 1400, 860], fill=body, outline=(90, 90, 100), width=4)
    for r in range(14):
        for c in range(8):
            x, y = 660 + c * 80, 150 + r * 50
            if y < 860:
                lit = yoru and (r * 7 + c * 3) % 5 == 0
                d.rectangle([x, y, x + 50, y + 28], fill=(250, 230, 160) if lit else ((60, 64, 80) if yoru else (150, 176, 200)))
    d.rectangle([0, 860, W, H], fill=(90, 90, 96) if yoru else (130, 132, 136))
    for x in (120, 300, 1620, 1800):                                                            # 公園の木
        d.ellipse([x - 110, 640, x + 110, 880], fill=(40, 70, 50) if yoru else (90, 140, 80))
        d.rectangle([x - 12, 860, x + 12, 940], fill=(80, 60, 40))
    return img


def cg_shosai():
    """書斎。本棚と机、ブラウン管のテレビ（ニュースを見る場面）。"""
    img = _rgb(base((206, 196, 178), (192, 182, 164)))
    wood_floor(img, FLOOR, col=(130, 96, 64), line=(112, 82, 54))
    d = _d(img)
    d.rectangle([100, 120, 640, 640], fill=(120, 86, 56), outline=(90, 64, 40), width=6)          # 本棚
    for r in range(5):
        y = 150 + r * 98
        for k in range(12):
            d.rectangle([126 + k * 42, y, 160 + k * 42, y + 80],
                        fill=[(150, 60, 50), (60, 90, 140), (200, 180, 120), (90, 120, 80)][(r + k) % 4])
    d.rectangle([1340, 400, 1700, 640], fill=(60, 60, 66), outline=(40, 40, 44), width=4)         # テレビ
    d.rectangle([1370, 424, 1620, 610], fill=(70, 110, 160))
    d.rectangle([1320, 640, 1720, 700], fill=(110, 80, 54))
    return img


def ya_ousetsu():
    """取材を受ける簡素な応接室。ソファ・低い机・湯のみ。窓の外は見せない。"""
    img = _rgb(base((228, 224, 214), (214, 210, 200)))
    wood_floor(img, FLOOR, col=(150, 120, 90), line=(134, 106, 78))
    d = _d(img)
    d.rectangle([760, 140, 1160, 400], fill=(200, 190, 170), outline=(150, 130, 100), width=8)    # 額（風景の絵）
    d.rectangle([780, 160, 1140, 380], fill=(150, 180, 150))
    d.rounded_rectangle([140, 560, 640, 760], radius=30, fill=(130, 90, 70), outline=(100, 70, 54), width=4)   # ソファ
    d.rounded_rectangle([1280, 560, 1780, 760], radius=30, fill=(130, 90, 70), outline=(100, 70, 54), width=4)
    d.rectangle([760, 660, 1160, 700], fill=(110, 80, 56))                                      # 低い机
    for x in (900, 1020):                                                                      # 湯のみ
        d.rounded_rectangle([x - 18, 620, x + 18, 660], radius=6, fill=(220, 214, 196), outline=(160, 150, 130))
    return img


def ya_jitaku():
    """晩年の自宅の一室。机に便箋とペン、窓の外は木々。"""
    img = _rgb(base((230, 224, 210), (216, 210, 196)))
    wood_floor(img, FLOOR, col=(160, 126, 90), line=(142, 110, 78))
    d = _d(img)
    d.rectangle([1260, 120, 1760, 460], fill=(150, 190, 130), outline=(120, 96, 70), width=10)   # 窓の外の木々
    for k in range(5):
        x = 1290 + k * 100
        d.ellipse([x - 50, 200 + (k % 2) * 40, x + 60, 360], fill=(90, 140, 80))
    d.line([(1510, 120), (1510, 460)], fill=(120, 96, 70), width=8)
    d.rectangle([520, 600, 1100, 640], fill=(120, 86, 56))                                       # 机
    d.rectangle([550, 640, 580, 760], fill=(100, 70, 46))
    d.rectangle([1040, 640, 1070, 760], fill=(100, 70, 46))
    d.rectangle([700, 580, 840, 600], fill=(250, 248, 240), outline=(200, 196, 186))              # 便箋
    for k in range(3):
        d.line([(712, 584 + k * 5), (826, 584 + k * 5)], fill=(150, 160, 190), width=1)
    d.line([(860, 596), (930, 576)], fill=(30, 30, 34), width=5)                                 # ペン
    return img


LOCATIONS = {
    # 長銀・大野木克信
    "cg_heya": cg_heya, "cg_kokkai": _sogo_kokkai, "cg_saikosai": cg_saikosai, "cg_houtei": _sogo_saibansho,
    "cg_tochiri": cg_tochiri, "cg_jomukai": kaigi, "cg_jomukai_akaji": lambda: kaigi(akaji=True),
    "cg_jigyo": jimusho90, "cg_soukai": kabunushi_kaijo, "cg_shoken": shoken, "cg_kaiken": _sega_kaiken,
    "cg_honten": cg_honten, "cg_honten_yoru": lambda: cg_honten(yoru=True), "cg_shosai": cg_shosai,
    "cg_gendai": _sega_gendai,
    # ヤオハン・和田一夫
    "ya_heya": ya_heya, "ya_yaoya": ya_yaoya, "ya_yakeato": lambda: ya_yaoya(yakeato=True),
    "ya_saopaulo": ya_saopaulo, "ya_ame": ya_ame, "ya_hk_office": ya_hk_office, "ya_peak": ya_peak,
    "ya_pudong": ya_pudong, "ya_shanghai": ya_shanghai, "ya_shanghai_gunshu": lambda: ya_shanghai(gunshu=True),
    "ya_uriba": lambda: _sogo_uriba(crowd=True), "ya_saijo": ya_saijo, "ya_apart": ya_apart, "ya_enkai": ya_enkai,
    "ya_yakuin": lambda: yakuin(), "ya_kaigi": kaigi, "ya_kaigi_akaji": lambda: kaigi(akaji=True),
    "ya_kaigi_up": lambda: kaigi(up=True), "ya_ginko": _sogo_ginkou, "ya_kaiken": _sega_kaiken,
    "ya_shoken": shoken, "ya_gendai": _gms, "ya_jimusho": lambda: vh_jigyobu(),
    "ya_ousetsu": ya_ousetsu, "ya_jitaku": ya_jitaku,
    # VHS・高野鎮雄
    "vh_heya": vh_heya, "vh_jigyobu": vh_jigyobu, "vh_kaihatsu": vh_kaihatsu, "vh_osetsu": vh_osetsu,
    "vh_soudanyaku": vh_soudanyaku, "vh_line": vh_line, "vh_line_yoso": lambda: vh_line(yoso=True),
    "vh_eigyo": vh_eigyo, "vh_eigyo_zaiko": lambda: vh_eigyo(zaiko=True), "vh_denkiten": vh_denkiten,
    "vh_denkiten_gyoretsu": lambda: vh_denkiten(gyoretsu=True), "vh_kojo_soto": kojo_soto,
    "vh_kojo_niwa": vh_kojo_niwa, "vh_hakubutsukan": vh_hakubutsukan, "vh_yakuin": lambda: yakuin(),
    "vh_kaigi": kaigi, "vh_kaigi_akaji": lambda: kaigi(akaji=True), "vh_kaigi_up": lambda: kaigi(up=True),
    "vh_kaiken": _sega_kaiken, "vh_europe": ol_london, "vh_gendai": _sega_gendai,
}

# 年号カード（台本ができてから足す）。接頭辞ごとに "vh_card_1976" のように作る
CARDS = {"cg": ["1952", "1959", "1995", "1997", "1998", "1999", "2000", "2002", "2005", "2008", "2017", "2025"],
         "ya": ["1930", "1950", "1956", "1962", "1969", "1971", "1977", "1984", "1989", "1990", "1991", "1993", "1995", "1996", "1997", "1998", "2000", "2001", "2018", "2019"],
         "vh": ["1946", "1970", "1973", "1975", "1976", "1977", "1979", "1982", "1984", "1986", "1988", "1992", "2016"]}


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
