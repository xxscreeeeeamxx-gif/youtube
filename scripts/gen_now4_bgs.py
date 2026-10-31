#!/usr/bin/env python3
"""第4弾4本（2026-11-09〜12）の背景を生成する。

接頭辞: tk_（北海道拓殖銀行の破綻）/ md_（日本マクドナルド・藤田田）/ tt_（タカタの破綻）/ ol_（オリンパスの損失隠し）
方針は gen_now_bgs.py と同じ。実在の会社のロゴ・社名の文字・製品の意匠は描かない（マクドナルドの M の形も描かない）。
差し替え用（_yoru・_kara・_konzatsu・_akaji・_up）は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now4_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, washitsu_1957, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import _boxes, _papers, _phone, _window, year_card  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _car, _d, _rgb, kaigi, yakuin  # noqa: E402
from scripts.gen_now2_bgs import heya2, kabunushi_kaijo, shoken  # noqa: E402
from scripts.gen_now3_bgs import jimusho90, kuko_lobby  # noqa: E402
from scripts.gen_drama_bgs import make_kojo  # noqa: E402
from scripts.gen_sega_bgs import _flat_tv, _glow, _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import gaikan as _sogo_gaikan, kokkai as _sogo_kokkai, saibansho as _sogo_saibansho  # noqa: E402

RED = (200, 40, 40)
YEL = (244, 196, 40)


# ---------------------------------------------------------------- 小物
def _burger(d, x, y, s=1.0):
    """ハンバーガー（下の端の中央が x, y）。"""
    d.ellipse([x - 40 * s, y - 50 * s, x + 40 * s, y - 14 * s], fill=(214, 150, 70))           # 上のパン
    d.rectangle([x - 42 * s, y - 22 * s, x + 42 * s, y - 12 * s], fill=(110, 170, 70))         # レタス
    d.rectangle([x - 40 * s, y - 14 * s, x + 40 * s, y - 2 * s], fill=(110, 60, 40))           # 肉
    d.rounded_rectangle([x - 40 * s, y - 4 * s, x + 40 * s, y + 6 * s], radius=int(5 * s), fill=(206, 140, 66))


def _paper_bag(d, x, y, s=1.0):
    """持ち帰りの紙袋（下の端の中央）。文字・印は描かない。"""
    d.polygon([(x - 40 * s, y), (x + 40 * s, y), (x + 34 * s, y - 100 * s), (x - 34 * s, y - 100 * s)],
              fill=(214, 186, 140), outline=(150, 120, 80))
    d.line([(x - 34 * s, y - 92 * s), (x + 34 * s, y - 92 * s)], fill=(170, 140, 96), width=2)


def _menu_board(d, x0, y0, x1, y1, cols=4):
    """店のメニュー板（文字は線だけ）。"""
    d.rectangle([x0, y0, x1, y1], fill=(250, 246, 230), outline=(140, 40, 30), width=6)
    w = (x1 - x0) / cols
    for c in range(cols):
        cx = x0 + w * c + w / 2
        _burger(d, cx, y0 + 70, 0.55)
        d.line([(cx - 40, y0 + 92), (cx + 40, y0 + 92)], fill=(90, 60, 40), width=5)
        d.line([(cx - 26, y0 + 112), (cx + 26, y0 + 112)], fill=RED, width=6)


# ---------------------------------------------------------------- 日本マクドナルド・藤田田
def md_heya():
    """今の部屋。机にハンバーガーと紙袋。"""
    img = heya2("none")
    d = _d(img)
    _paper_bag(d, 260, 640, 0.9)
    _burger(d, 420, 636, 1.0)
    return img


def md_mise(konzatsu=False):
    """1号店の持ち帰り専門の売店（1971年）。赤と白の小さなカウンター、メニュー板、席は無い。
    konzatsu は手前に客の列。"""
    img = _rgb(base((240, 236, 226), (226, 222, 212)))
    wood_floor(img, FLOOR, col=(200, 196, 188), line=(184, 180, 172))
    d = _d(img)
    d.rectangle([0, 40, W, 110], fill=RED)                                            # 軒の帯（文字なし）
    for k in range(12):
        d.rectangle([k * 160, 110, k * 160 + 80, 150], fill=(250, 250, 250))       # 白赤の日よけ
        d.rectangle([k * 160 + 80, 110, k * 160 + 160, 150], fill=RED)
    _menu_board(d, 480, 190, 1440, 400)
    d.rectangle([300, 560, 1620, 640], fill=(250, 250, 250), outline=(180, 40, 30), width=6)   # カウンター
    d.rectangle([300, 640, 1620, 760], fill=RED)
    for k in range(4):                                                                # レジ
        x = 420 + k * 320
        d.rectangle([x, 510, x + 110, 560], fill=(60, 60, 66))
        d.rectangle([x + 10, 480, x + 100, 510], fill=(90, 90, 96))
    if konzatsu:
        _person_line(d, 60, 1010, 12, 1.05)
        _person_line(d, 1000, 1010, 12, 1.05)
    return img


def md_koji():
    """閉店後の夜の工事。骨組みと足場、作業灯、床に資材。"""
    img = vgrad((W, H), (40, 42, 52), (60, 62, 72))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(110, 106, 100))
    for x in (260, 760, 1260, 1700):                                                 # 骨組み
        d.rectangle([x - 10, 160, x + 10, FLOOR], fill=(150, 150, 156))
    d.line([(200, 180), (1760, 180)], fill=(150, 150, 156), width=14)
    d.rectangle([420, 420, 1100, 440], fill=(240, 180, 40))                          # 足場
    for x in (440, 1080):
        d.rectangle([x - 6, 440, x + 6, FLOOR], fill=(240, 180, 40))
    _boxes(d, 1300, FLOOR, n=3, rows=2)
    d.rectangle([600, FLOOR - 40, 980, FLOOR], fill=(190, 170, 140))               # 板材
    for x in (500, 1400):                                                            # 作業灯
        _glow(img, x, 260, 260, (255, 236, 170), 120)
        d = _d(img)
        d.rectangle([x - 30, 240, x + 30, 280], fill=(250, 240, 200))
    return img


def md_ginza(hokoten=False, yoru=False):
    """銀座の大通りと百貨店の角。hokoten は車道に人（歩行者天国）、yoru は閉店後の夜。"""
    img = _sogo_gaikan(night=yoru)
    d = _d(img)
    if not yoru:
        d.rectangle([0, 860, W, H], fill=(120, 122, 126))
        for k in range(10):
            d.rectangle([k * 200 + 40, 940, k * 200 + 140, 960], fill=(240, 240, 240))
        if hokoten:
            _person_line(d, 80, 1060, 9, 1.0)
            _person_line(d, 1080, 1060, 9, 1.0)
            for x in (300, 900, 1500):                                               # 道に置いたパラソル
                d.polygon([(x - 90, 900), (x + 90, 900), (x, 840)], fill=RED)
                d.line([(x, 900), (x, 980)], fill=(80, 80, 86), width=6)
        else:
            _car(d, 300, 1000, 1.1, col=(60, 90, 160))
            _car(d, 1300, 1000, 1.1, col=(200, 200, 206))
    return img


def md_shoten():
    """1960年代の藤田商店の事務所。輸入雑貨の箱とハンドバッグの棚、黒電話。"""
    img = _rgb(base((226, 218, 200), (210, 202, 186)))
    wood_floor(img, FLOOR, col=(130, 100, 70), line=(110, 84, 58))
    d = _d(img)
    d.rectangle([100, 160, 820, 640], fill=(150, 116, 84), outline=(110, 84, 60), width=6)    # 棚
    for r in range(3):
        d.rectangle([100, 300 + r * 140, 820, 312 + r * 140], fill=(110, 84, 60))
        for k in range(5):
            x = 150 + k * 135
            y = 300 + r * 140
            d.rounded_rectangle([x, y - 70, x + 90, y], radius=10,
                                fill=[(160, 40, 40), (40, 40, 44), (190, 150, 90), (60, 80, 130), (120, 90, 60)][(k + r) % 5])
            d.arc([x + 20, y - 100, x + 70, y - 50], 180, 360, fill=(80, 60, 40), width=5)
    d.rectangle([1100, 600, 1800, 640], fill=(110, 76, 50))
    d.rectangle([1120, 640, 1780, 780], fill=(96, 66, 44))
    _papers(d, 1180, 590, n=3)
    _phone(d, 1580, 520, 0.7)
    _window(d, 1100, 140, 1800, 440, sky=(190, 210, 226))
    _boxes(d, 860, FLOOR, n=2, rows=2)
    return img


def md_daigaku():
    """研修の教室（ハンバーガー大学）。黒板の前に机、教卓に見本のハンバーガー。"""
    img = _rgb(base((232, 230, 224), (218, 216, 210)))
    wood_floor(img, FLOOR, col=(170, 150, 120), line=(150, 132, 104))
    d = _d(img)
    d.rectangle([420, 100, 1500, 440], fill=(40, 70, 56), outline=(120, 100, 70), width=10)
    for k in range(4):
        d.line([(480, 160 + k * 60), (900 + (k % 2) * 300, 160 + k * 60)], fill=(240, 240, 230), width=5)
    d.rectangle([820, 520, 1100, 600], fill=(150, 116, 84))
    _burger(d, 960, 520, 1.1)
    for r, y in enumerate((700, 820)):
        for k in range(5):
            x0 = 100 + k * 360 + r * 40
            d.rectangle([x0, y, x0 + 300, y + 22], fill=(200, 180, 150), outline=(150, 130, 100), width=2)
    return img


def md_drive():
    """郊外の道ぞいの店とドライブスルー。車が並ぶ。"""
    img = vgrad((W, H), (170, 200, 226), (220, 226, 230))
    d = _d(img)
    d.rectangle([0, 620, W, H], fill=(110, 112, 118))
    d.rectangle([360, 300, 1180, 620], fill=(244, 240, 230), outline=(160, 150, 140), width=6)
    d.rectangle([360, 300, 1180, 360], fill=RED)
    d.rectangle([1180, 440, 1260, 620], fill=(244, 240, 230), outline=(160, 150, 140), width=4)  # 受け取り窓
    d.rectangle([1190, 470, 1250, 540], fill=(150, 190, 220))
    for k in range(6):
        d.rectangle([420 + k * 125, 420, 500 + k * 125, 520], fill=(160, 196, 222))
    for k in range(3):
        _car(d, 1300 + k * 220, 760, 0.8, col=[(60, 90, 160), (200, 200, 206), (160, 50, 50)][k])
    d.line([(1250, 680), (1900, 680)], fill=(240, 240, 240), width=6)
    return img


def md_ghq():
    """戦後すぐの進駐軍の事務所。木の机にタイプライター、天井の扇風機。"""
    img = _rgb(base((214, 210, 196), (198, 194, 180)))
    wood_floor(img, FLOOR, col=(120, 96, 70), line=(100, 80, 58))
    d = _d(img)
    _window(d, 220, 120, 740, 460, sky=(200, 216, 226))
    _window(d, 1180, 120, 1700, 460, sky=(200, 216, 226))
    d.line([(960, 0), (960, 120)], fill=(80, 80, 80), width=6)                           # 扇風機
    d.ellipse([900, 110, 1020, 140], fill=(90, 90, 96))
    d.rectangle([560, 620, 1360, 660], fill=(110, 80, 56))
    d.rectangle([580, 660, 1340, 790], fill=(96, 70, 48))
    d.rectangle([860, 560, 1060, 620], fill=(40, 40, 44))                               # タイプライター
    d.rectangle([880, 530, 1040, 560], fill=(240, 240, 236))
    _papers(d, 620, 610, n=3)
    return img


# ---------------------------------------------------------------- 北海道拓殖銀行
def _snow(img, n=220, seed=3):
    rnd = random.Random(seed)
    d = _d(img)
    for _ in range(n):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(2, 6)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 200))


def tk_honten(konzatsu=False):
    """銀行の本店の営業室。石の柱、高い天井、長い窓口のカウンター。konzatsu は預金を下ろす客の列。"""
    img = _rgb(base((228, 222, 210), (214, 208, 196)))
    wood_floor(img, FLOOR, col=(170, 160, 146), line=(150, 142, 130))
    d = _d(img)
    for x in (160, 640, 1280, 1760):                                                 # 石の柱
        d.rectangle([x - 50, 60, x + 50, FLOOR], fill=(236, 232, 222), outline=(180, 174, 160), width=4)
        d.rectangle([x - 70, 60, x + 70, 100], fill=(220, 214, 202))
    d.rectangle([0, 520, W, 620], fill=(150, 116, 84), outline=(110, 84, 60), width=6)    # 窓口
    for k in range(8):
        x = 120 + k * 230
        d.rectangle([x, 440, x + 140, 520], fill=(210, 226, 232, 160), outline=(160, 170, 176), width=3)
        d.rectangle([x + 40, 470, x + 100, 490], fill=(250, 250, 244))
    d.rectangle([760, 160, 1160, 300], fill=(60, 66, 80))                           # 金利の掲示（文字は線）
    for r in range(4):
        d.line([(790, 190 + r * 30), (1130, 190 + r * 30)], fill=(240, 220, 120), width=6)
    if konzatsu:
        _person_line(d, 40, 1010, 13, 1.05)
        _person_line(d, 980, 1010, 13, 1.05)
    return img


def tk_honten_soto(yuki=True):
    """札幌の本店の外観。石造りの重い建物、雪の歩道。"""
    img = vgrad((W, H), (150, 160, 176) if yuki else (170, 200, 226), (200, 206, 214))
    d = _d(img)
    d.rectangle([260, 160, 1660, 760], fill=(196, 190, 176), outline=(140, 134, 120), width=8)
    d.polygon([(220, 160), (1700, 160), (960, 60)], fill=(176, 170, 156), outline=(140, 134, 120))
    for k in range(6):
        x = 380 + k * 230
        d.rectangle([x, 260, x + 70, 760], fill=(220, 214, 200), outline=(160, 154, 140), width=3)
    d.rectangle([840, 520, 1080, 760], fill=(70, 56, 46))                          # 入口
    d.rectangle([0, 760, W, H], fill=(240, 242, 246) if yuki else (130, 130, 134))
    if yuki:
        d.rectangle([260, 150, 1660, 172], fill=(250, 250, 252))
        _snow(img)
    return img


def tk_tv_yoru():
    """夜の役員室。明かりを落とし、テレビだけが光っている（サッカーの中継）。"""
    img = yakuin(view=(20, 26, 46), city=False)
    d = _d(img)
    d.rectangle([0, 0, W, H], fill=(0, 0, 20, 110))
    _flat_tv(d, 1280, 420, 1760, 690, screen=(60, 150, 80))
    _glow(img, 1520, 555, 320, (140, 220, 160), 70)
    d = _d(img)
    d.rectangle([1500, 520, 1540, 560], fill=(250, 250, 250))                      # ボール
    return img


def tk_hotel():
    """リゾートのホテル（融資先）。大きな建物と玄関、雪山。"""
    img = vgrad((W, H), (160, 190, 222), (220, 226, 232))
    d = _d(img)
    d.polygon([(0, 520), (420, 220), (900, 520)], fill=(236, 240, 246))
    d.polygon([(700, 520), (1260, 160), (1920, 520)], fill=(226, 232, 240))
    d.rectangle([340, 300, 1580, 760], fill=(232, 222, 206), outline=(170, 160, 146), width=6)
    for r in range(5):
        for k in range(12):
            d.rectangle([400 + k * 98, 340 + r * 72, 450 + k * 98, 384 + r * 72], fill=(170, 196, 220))
    d.rectangle([860, 640, 1060, 760], fill=(110, 84, 60))
    d.rectangle([0, 760, W, H], fill=(240, 242, 246))
    return img


def tk_keimusho():
    """刑務所の部屋。灰色の壁、高い小さな窓の鉄格子、机と布団。"""
    img = _rgb(base((176, 178, 176), (160, 162, 160)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([780, 120, 1140, 320], fill=(196, 216, 230), outline=(100, 100, 104), width=10)
    for k in range(5):
        d.line([(820 + k * 70, 120), (820 + k * 70, 320)], fill=(80, 80, 86), width=10)
    d.rectangle([200, 640, 620, 700], fill=(150, 130, 100))
    _papers(d, 260, 630, n=2)
    d.rectangle([1260, 700, 1760, 780], fill=(230, 230, 236), outline=(170, 170, 176), width=3)
    return img


def tk_sapporo():
    """冬の札幌の大通り。雪のビル街。"""
    img = vgrad((W, H), (150, 160, 176), (200, 206, 214))
    d = _d(img)
    rnd = random.Random(8)
    for k in range(10):
        x0 = k * 200 - 20
        top = 160 + rnd.randint(0, 220)
        d.rectangle([x0, top, x0 + 180, 760], fill=rnd.choice([(150, 156, 170), (170, 166, 160), (130, 140, 156)]))
        d.rectangle([x0, top - 12, x0 + 180, top], fill=(250, 250, 252))
        for r in range((760 - top) // 70):
            for c in range(3):
                d.rectangle([x0 + 20 + c * 55, top + 20 + r * 70, x0 + 52 + c * 55, top + 54 + r * 70], fill=(220, 214, 180))
    d.rectangle([0, 760, W, H], fill=(240, 242, 246))
    _person_line(d, 200, 1040, 5, 1.0)
    _snow(img, seed=9)
    return img


def tk_okurasho():
    """霞が関の役所の部屋。木の壁、書類の棚、重い机と応接の椅子。"""
    img = _rgb(base((196, 186, 168), (180, 170, 152)))
    wood_floor(img, FLOOR, col=(110, 86, 62), line=(92, 72, 52))
    d = _d(img)
    for k in range(9):
        d.line([(k * 220, 0), (k * 220, FLOOR)], fill=(170, 158, 138), width=4)
    d.rectangle([120, 160, 700, 640], fill=(120, 92, 64), outline=(90, 68, 46), width=6)     # 書類の棚
    for r in range(4):
        d.rectangle([120, 260 + r * 110, 700, 272 + r * 110], fill=(90, 68, 46))
        for k in range(10):
            d.rectangle([140 + k * 54, 200 + r * 110, 180 + k * 54, 260 + r * 110], fill=(232, 226, 210), outline=(180, 170, 150))
    _window(d, 1160, 120, 1760, 440, sky=(180, 196, 212))
    d.rectangle([980, 600, 1700, 650], fill=(90, 62, 40))
    d.rectangle([1000, 650, 1680, 790], fill=(78, 54, 34))
    _papers(d, 1060, 590, n=3)
    _phone(d, 1520, 520, 0.6)
    return img


def tk_jitaku():
    """札幌の自宅の居間（昼）。ソファと棚の上の電話。"""
    img = heya2("none")
    d = _d(img)
    d.rounded_rectangle([140, 560, 760, 720], radius=24, fill=(150, 120, 96), outline=(110, 86, 66), width=4)
    d.rounded_rectangle([160, 480, 740, 580], radius=24, fill=(170, 140, 112))
    d.rectangle([900, 600, 1120, 700], fill=(120, 90, 64))
    _phone(d, 940, 520, 0.6)
    return img


# ---------------------------------------------------------------- タカタ
def tt_heya():
    """今の部屋。机に車の鍵と、届いたはがき（リコールの案内）。"""
    img = heya2("none")
    d = _d(img)
    d.ellipse([280, 610, 320, 640], fill=(40, 40, 46))
    d.rectangle([316, 618, 360, 630], fill=(180, 180, 186))
    d.rectangle([420, 600, 560, 640], fill=(252, 250, 244), outline=(180, 170, 150), width=2)
    d.line([(436, 614), (540, 614)], fill=(200, 40, 40), width=4)
    return img


def tt_kojo():
    """部品の工場。作業台に小さな金属の筒（ガス発生装置）が並ぶ。"""
    img = vgrad((W, H), (222, 224, 226), (204, 206, 210))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(176, 178, 182))
    for k in range(6):
        d.rectangle([k * 340 + 40, 50, k * 340 + 80, 80], fill=(250, 250, 236))
    for row, y in enumerate((440, 620)):
        d.rectangle([40, y, 1880, y + 30], fill=(110, 130, 150))
        for k in range(22):
            x = 70 + k * 82 + row * 30
            d.rounded_rectangle([x, y - 50, x + 46, y], radius=8, fill=(170, 174, 180), outline=(110, 114, 120), width=2)
            d.ellipse([x + 10, y - 60, x + 36, y - 44], fill=(140, 144, 150))
    _boxes(d, 1560, FLOOR, n=3, rows=2)
    return img


def tt_shiken():
    """試験の部屋。分厚いガラスの向こうに試験の台、手前に計測の画面。"""
    img = vgrad((W, H), (190, 196, 204), (170, 176, 184))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(150, 154, 160))
    d.rectangle([260, 120, 1180, 560], fill=(120, 140, 160), outline=(80, 86, 96), width=14)   # 厚いガラス
    d.rectangle([560, 360, 880, 460], fill=(90, 94, 100))                                      # 試験の台
    d.rounded_rectangle([660, 300, 780, 360], radius=10, fill=(176, 180, 186))
    d.rectangle([1300, 360, 1760, 640], fill=(40, 44, 52), outline=(90, 94, 100), width=6)    # 計測の画面
    d.line([(1330, 560), (1420, 520), (1480, 540), (1560, 420), (1640, 470), (1730, 450)], fill=(90, 230, 140), width=6)
    d.rectangle([1260, 640, 1800, 680], fill=(110, 116, 124))
    return img


def tt_gikai():
    """米国議会の公聴会の部屋。高い段に議員の席、正面に証人の机とマイク。旗は無地。"""
    img = _rgb(base((206, 196, 176), (190, 180, 160)))
    wood_floor(img, FLOOR, col=(120, 90, 64), line=(100, 74, 52))
    d = _d(img)
    d.rectangle([0, 0, W, 120], fill=(150, 120, 90))
    d.rectangle([120, 220, 1800, 380], fill=(110, 76, 50), outline=(80, 56, 36), width=6)      # 高い段
    for k in range(9):
        x = 220 + k * 180
        d.rectangle([x, 180, x + 70, 220], fill=(40, 40, 44))
    for x in (60, 1820):                                                                     # 無地の旗
        d.line([(x, 120), (x, 600)], fill=(200, 180, 120), width=8)
        d.rectangle([x - 50, 130, x + 50, 230], fill=(60, 70, 120))
    d.rectangle([660, 640, 1260, 700], fill=(96, 66, 44))                                    # 証人の机
    for x in (760, 1160):
        d.line([(x, 640), (x - 20, 580)], fill=(30, 30, 34), width=6)
    return img


def tt_seibi():
    """自動車の整備工場。持ち上げた車と工具の棚（交換の作業）。"""
    img = _rgb(base((206, 208, 210), (190, 192, 196)))
    wood_floor(img, FLOOR, col=(150, 150, 150), line=(136, 136, 136))
    d = _d(img)
    d.rectangle([0, FLOOR - 10, W, FLOOR + 10], fill=(240, 200, 40))
    d.rectangle([700, 560, 1260, 600], fill=(200, 60, 50))                                   # リフト
    for x in (740, 1220):
        d.rectangle([x - 14, 600, x + 14, FLOOR], fill=(200, 60, 50))
    _car(d, 820, 560, 1.6, col=(200, 200, 206))
    d.rectangle([100, 260, 560, 640], fill=(70, 80, 96), outline=(50, 56, 66), width=6)        # 工具の棚
    for r in range(4):
        d.line([(120, 330 + r * 80), (540, 330 + r * 80)], fill=(150, 160, 176), width=6)
    return img


def tt_kaiken_heya():
    """法律事務所の会議室での会見。窓の外に高層ビル、細長い机とマイク、手前にカメラ。"""
    img = yakuin(view=(186, 206, 226))
    d = _d(img)
    d.rectangle([520, 600, 1400, 700], fill=(240, 240, 236), outline=(170, 170, 166), width=4)
    for x in (700, 960, 1220):
        d.line([(x, 600), (x - 24, 530)], fill=(40, 40, 44), width=6)
        d.ellipse([x - 44, 510, x - 8, 546], fill=(40, 40, 44))
    d.rectangle([0, 860, W, H], fill=(40, 40, 50))
    for k in range(12):
        x = 40 + k * 160
        d.rectangle([x, 820, x + 110, 900], fill=(30, 30, 34))
    return img


# ---------------------------------------------------------------- オリンパス
def ol_torishimari():
    """高層の本社の取締役会の部屋。楕円の長い机、窓の外に高層ビル。"""
    img = yakuin(view=(176, 196, 220))
    d = _d(img)
    d.rectangle([600, 650, 1320, 704], fill=(200, 196, 204))
    d.ellipse([260, 600, 1660, 760], fill=(96, 70, 52), outline=(70, 50, 36), width=6)
    for k in range(10):
        x = 340 + k * 132
        d.rounded_rectangle([x, 560, x + 70, 620], radius=10, fill=(40, 40, 46))
    _papers(d, 880, 650, n=2)
    return img


def ol_oze():
    """尾瀬の湿原の木道。山と草原。"""
    img = vgrad((W, H), (160, 196, 230), (226, 232, 236))
    d = _d(img)
    d.polygon([(0, 520), (380, 260), (780, 520)], fill=(110, 140, 120))
    d.polygon([(600, 520), (1180, 200), (1920, 520)], fill=(96, 128, 110))
    d.rectangle([0, 520, W, H], fill=(170, 186, 110))
    for k in range(10):                                                                   # 木道
        y = 1080 - k * 52
        w = 520 - k * 40
        d.polygon([(960 - w / 2, y), (960 + w / 2, y), (960 + (w - 40) / 2, y - 44), (960 - (w - 40) / 2, y - 44)],
                  fill=(176, 146, 104), outline=(130, 104, 70))
    return img


def ol_london():
    """ロンドンの通り。れんがの建物と街灯（実在の名所は描かない）。"""
    img = vgrad((W, H), (170, 180, 196), (210, 214, 220))
    d = _d(img)
    for k in range(6):
        x0 = k * 330 - 20
        d.rectangle([x0, 200, x0 + 310, 780], fill=[(150, 80, 66), (170, 100, 80), (140, 120, 110)][k % 3])
        for r in range(4):
            for c in range(3):
                d.rectangle([x0 + 30 + c * 95, 240 + r * 130, x0 + 90 + c * 95, 330 + r * 130], fill=(220, 226, 230))
    d.rectangle([0, 780, W, H], fill=(120, 122, 126))
    for x in (300, 1400):
        d.line([(x, 780), (x, 520)], fill=(40, 40, 44), width=10)
        d.rectangle([x - 26, 490, x + 26, 530], fill=(240, 220, 150))
    return img


def ol_hotel():
    """ホテルの部屋（ドイツの出張先）。ベッドと机のノートパソコン。"""
    img = _rgb(base((226, 220, 210), (212, 206, 196)))
    wood_floor(img, FLOOR, col=(150, 120, 90), line=(130, 104, 78))
    d = _d(img)
    _window(d, 1260, 140, 1760, 460, sky=(40, 50, 80))
    d.rectangle([140, 560, 900, 720], fill=(240, 240, 244), outline=(190, 190, 196), width=4)   # ベッド
    d.rectangle([140, 470, 900, 560], fill=(150, 116, 84))
    d.rectangle([1100, 600, 1700, 640], fill=(120, 90, 64))
    d.polygon([(1300, 600), (1500, 600), (1510, 590), (1310, 590)], fill=(60, 60, 66))
    d.rectangle([1310, 500, 1500, 588], fill=(40, 44, 52), outline=(90, 90, 96), width=2)
    d.rectangle([1318, 508, 1492, 580], fill=(200, 214, 230))
    return img


LOCATIONS = {
    # 日本マクドナルド・藤田田
    "md_heya": md_heya, "md_mise": md_mise, "md_mise_konzatsu": lambda: md_mise(konzatsu=True),
    "md_koji": md_koji, "md_ginza": md_ginza, "md_ginza_hokoten": lambda: md_ginza(hokoten=True),
    "md_ginza_yoru": lambda: md_ginza(yoru=True), "md_shoten": md_shoten, "md_daigaku": md_daigaku,
    "md_drive": md_drive, "md_ghq": md_ghq, "md_osaka": washitsu_1957, "md_kaiken": _sega_kaiken,
    "md_kaigi": kaigi, "md_kaigi_akaji": lambda: kaigi(akaji=True), "md_kaigi_up": lambda: kaigi(up=True),
    "md_yakuin": lambda: yakuin(), "md_gendai": _sega_gendai,
    # 北海道拓殖銀行
    "tk_heya": lambda: heya2("none"), "tk_honten": tk_honten, "tk_honten_konzatsu": lambda: tk_honten(konzatsu=True),
    "tk_honten_soto": tk_honten_soto, "tk_yakuin": lambda: yakuin(view=(150, 160, 176)), "tk_tv_yoru": tk_tv_yoru,
    "tk_hotel": tk_hotel, "tk_kaigi": kaigi, "tk_kaigi_akaji": lambda: kaigi(akaji=True),
    "tk_kaiken": _sega_kaiken, "tk_kokkai": _sogo_kokkai, "tk_houtei": _sogo_saibansho,
    "tk_keimusho": tk_keimusho, "tk_sapporo": tk_sapporo, "tk_shoken": shoken, "tk_gendai": _sega_gendai,
    "tk_okurasho": tk_okurasho, "tk_jitaku": tk_jitaku,
    # タカタ
    "tt_heya": tt_heya, "tt_kojo": tt_kojo, "tt_kojo_old": make_kojo, "tt_shiken": tt_shiken, "tt_gikai": tt_gikai,
    "tt_seibi": tt_seibi, "tt_kaiken_heya": tt_kaiken_heya, "tt_kaiken": _sega_kaiken, "tt_soukai": kabunushi_kaijo,
    "tt_kaigi": kaigi, "tt_kaigi_akaji": lambda: kaigi(akaji=True), "tt_yakuin": lambda: yakuin(),
    "tt_shoken": shoken, "tt_houtei": _sogo_saibansho, "tt_gendai": _sega_gendai,
    # オリンパス
    "ol_heya": lambda: heya2("none"), "ol_torishimari": ol_torishimari, "ol_yakuin": lambda: yakuin(),
    "ol_henshubu": jimusho90, "ol_henshubu_yoru": lambda: jimusho90(yoru=True), "ol_oze": ol_oze,
    "ol_hotel": ol_hotel, "ol_london": ol_london, "ol_kuko": kuko_lobby, "ol_kaiken": _sega_kaiken,
    "ol_kaigi": kaigi, "ol_kaigi_akaji": lambda: kaigi(akaji=True), "ol_shoken": shoken,
    "ol_houtei": _sogo_saibansho, "ol_soukai": kabunushi_kaijo, "ol_gendai": _sega_gendai,
}

# 年号カード（台本ができてから埋める）。接頭辞ごとに "md_card_1971" のように作る
CARDS = {"tk": ["1993", "1994", "1997", "1999", "2006", "2009", "2017", "2025"], "md": ["1969", "1972", "1975", "1977", "1994", "2000", "2001", "2002", "2003"], "tt": ["1933", "2004", "2009", "2014", "2015", "2016", "2017", "2018"], "ol": ["2009", "2011", "2012", "2013", "2019"]}


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
