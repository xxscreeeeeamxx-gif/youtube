#!/usr/bin/env python3
"""第14弾4本（2026-12-18〜21。題材をゲーム・ネット・スマホにしぼった最初の4本）の背景を生成する。

接頭辞: pk_（ポケモンの誕生）/ nc_（ニコニコ動画の興亡）/ mi_（mixi とモンスト）/ iw_（岩田聡と DS・Wii）
方針は gen_now13_bgs.py と同じ。実在の会社のロゴ・社名の文字・商品のパッケージは描かない。
実在のゲームの画面・キャラクター・ポケモンの姿、サイトやアプリの画面・ロゴは描かない（画面は色の四角か線だけ）。
実在の人の写真や肖像は描かない。差し替え用は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now14_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import _crt, _phone, _shacho_base, _text_c, _window, year_card  # noqa: E402
from scripts.gen_tamagotchi_bgs import _office_base  # noqa: E402
from scripts.gen_now2_bgs import heya2  # noqa: E402
from scripts.gen_now3_bgs import jimusho90, kuko_lobby, server_shitsu  # noqa: E402
from scripts.gen_now_bgs import kaigi as _now_kaigi  # noqa: E402
from scripts.gen_now9_bgs import _light  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _d, _rgb  # noqa: E402
from scripts.gen_ykk_bgs import kyoshitsu as _ykk_kyoshitsu  # noqa: E402
from scripts.gen_now13_bgs import _dark, _lines, _squares  # noqa: E402
from scripts.gen_now13_bgs import pu_kissaten as _pu_kissaten  # noqa: E402
from scripts.gen_sega_bgs import _person_line, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_nf_bgs import kyoshitsu as _nf_kyoshitsu  # noqa: E402

GRAY = (178, 178, 170)          # 携帯ゲーム機・カセットの灰色


def _paper(d, x, y, w, h, col=(250, 248, 238), line=True, rot=0):
    d.rectangle([x, y, x + w, y + h], fill=col, outline=(160, 150, 130), width=2)
    if line:
        _lines(d, x + 10, y + 16, x + w - 10, max(1, (h - 20) // 18), gap=18, col=(150, 150, 160), w=3)


def _handheld(d, x, y, s=1.0):
    """灰色の携帯ゲーム機（架空・ロゴなし）。画面は暗い緑の四角だけ。"""
    w, h = int(150 * s), int(240 * s)
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(14 * s), fill=GRAY, outline=(120, 120, 114), width=3)
    d.rectangle([x + int(18 * s), y + int(20 * s), x + w - int(18 * s), y + int(110 * s)], fill=(90, 110, 80), outline=(70, 70, 70), width=3)
    cx, cy = x + int(42 * s), y + int(160 * s)
    d.rectangle([cx - int(22 * s), cy - int(7 * s), cx + int(22 * s), cy + int(7 * s)], fill=(50, 50, 54))
    d.rectangle([cx - int(7 * s), cy - int(22 * s), cx + int(7 * s), cy + int(22 * s)], fill=(50, 50, 54))
    for k, (bx, by) in enumerate(((104, 150), (124, 136))):
        d.ellipse([x + int(bx * s) - int(10 * s), y + int(by * s) - int(10 * s), x + int(bx * s) + int(10 * s), y + int(by * s) + int(10 * s)], fill=(140, 40, 80))
    return (x + w // 2, y)                                                              # コードの差し口


def _cassette(d, x, y, s=1.0):
    """ラベルの無い灰色のカセット。"""
    w, h = int(90 * s), int(100 * s)
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(6 * s), fill=GRAY, outline=(110, 110, 104), width=3)
    d.rectangle([x + int(14 * s), y + int(14 * s), x + w - int(14 * s), y + int(60 * s)], fill=(206, 206, 200), outline=(140, 140, 134), width=2)
    for k in range(5):
        d.line([(x + int(16 * s) + k * int(14 * s), y + h - 6), (x + int(16 * s) + k * int(14 * s), y + h - int(18 * s))], fill=(120, 120, 114), width=3)


def _whiteboard(d, x0=460, y0=140, x1=1460, y1=560):
    d.rectangle([x0 - 14, y0 - 14, x1 + 14, y1 + 14], fill=(160, 160, 166))
    d.rectangle([x0, y0, x1, y1], fill=(250, 250, 248))
    d.rectangle([x0 + 40, y1 + 14, x1 - 40, y1 + 30], fill=(150, 150, 156))


def _desk_row(d, y, xs, w=230, items=True, seed=1):
    rnd = random.Random(seed)
    for x in xs:
        d.rectangle([x, y, x + w, y + 24], fill=(150, 126, 96))
        d.rectangle([x + 10, y + 24, x + 26, y + 200], fill=(120, 98, 74))
        d.rectangle([x + w - 26, y + 24, x + w - 10, y + 200], fill=(120, 98, 74))
        if items:
            _crt(d, x + 50, y - 150, 130, 120)
            for k in range(rnd.randint(1, 3)):
                d.rectangle([x + 150 + k * 6, y - 30 - k * 8, x + 220 + k * 6, y - k * 8], fill=(246, 242, 230), outline=(160, 150, 130), width=2)


def _heads(d, y0, rows, cols, gap=66, seed=5, col0=20):
    rnd = random.Random(seed)
    for r in range(rows):
        for c in range(cols):
            x = c * gap + (r % 2) * gap // 2 + rnd.randint(-6, 6)
            y = y0 + r * 64
            v = col0 + r * 6
            d.ellipse([x, y, x + 46, y + 46], fill=(v, v - 2, v + 8))


# ---------------------------------------------------------------- ポケモンの誕生
def pk_heya():
    """今の部屋。机にシールの台紙（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([260, 590, 520, 650], fill=(250, 248, 240), outline=(150, 140, 120), width=3)
    for k in range(8):
        x = 274 + (k % 4) * 60
        y = 598 + (k // 4) * 26
        col = [(240, 120, 120), (120, 180, 240), (250, 210, 90), (140, 210, 140)][k % 4] if k not in (2, 5, 7) else (230, 228, 220)
        d.rectangle([x, y, x + 46, y + 20], fill=col, outline=(170, 160, 150))
    return img


def pk_kaigi():
    """会議室（任天堂・架空）。机の上にラベルの無い灰色のカセット。"""
    img = _now_kaigi()
    d = _d(img)
    _cassette(d, 900, 560, 1.15)
    return img


def pk_zokibayashi(zosei=False):
    """1970年代の町田の雑木林。虫取り網が木に立てかけてある。zosei は同じ場所が造成地になり、網だけ残る。"""
    img = vgrad((W, H), (150, 200, 236), (226, 236, 230))
    d = _d(img)
    if not zosei:
        rnd = random.Random(3)
        for k in range(14):
            x = rnd.randint(-60, W)
            h = rnd.randint(420, 620)
            d.rectangle([x + 40, FLOOR - h + 180, x + 70, FLOOR], fill=(110, 80, 56))
            d.ellipse([x - 60, FLOOR - h, x + 170, FLOOR - h + 260], fill=(60 + rnd.randint(0, 40), 120 + rnd.randint(0, 40), 60))
        d.rectangle([0, FLOOR, W, H], fill=(110, 150, 70))
        for k in range(60):
            x = rnd.randint(0, W)
            d.line([(x, FLOOR + 10), (x + 6, FLOOR - 20)], fill=(70, 120, 50), width=4)
    else:
        d.rectangle([0, FLOOR - 120, W, H], fill=(176, 140, 100))
        for x in (300, 760, 1240, 1700):                                                       # 切り株
            d.rectangle([x, FLOOR - 40, x + 70, FLOOR], fill=(130, 96, 66))
            d.ellipse([x, FLOOR - 56, x + 70, FLOOR - 28], fill=(200, 170, 120))
        for x in (520, 1460):                                                                  # 杭と縄
            d.rectangle([x, FLOOR - 160, x + 14, FLOOR - 40], fill=(230, 220, 200))
        d.line([(527, FLOOR - 150), (1467, FLOOR - 150)], fill=(240, 120, 40), width=4)
        d.rectangle([1540, FLOOR - 300, 1800, FLOOR - 160], fill=(230, 180, 40))               # 重機（形だけ）
        d.rectangle([1500, FLOOR - 160, 1840, FLOOR - 90], fill=(60, 60, 60))
        d.line([(1580, FLOOR - 300), (1400, FLOOR - 470)], fill=(200, 150, 30), width=22)
    # 網（立てかけ／地面に）
    if not zosei:
        d.line([(1520, FLOOR - 20), (1430, FLOOR - 360)], fill=(220, 190, 120), width=8)
        d.ellipse([1360, FLOOR - 460, 1500, FLOOR - 340], outline=(220, 220, 220), width=6)
    else:
        d.line([(860, FLOOR + 40), (1160, FLOOR + 10)], fill=(220, 190, 120), width=8)
        d.ellipse([1150, FLOOR - 40, 1270, FLOOR + 50], outline=(220, 220, 220), width=6)
    return img


def pk_doujin():
    """1980年代の勉強部屋。机に手書きの原稿の束とホチキス、スタンド。"""
    img = _rgb(base((226, 214, 190), (206, 192, 166)))
    wood_floor(img, FLOOR, col=(150, 110, 76), line=(126, 92, 64))
    d = _d(img)
    _window(d, 1300, 160, 1700, 470)
    d.rectangle([560, 610, 1340, 640], fill=(140, 104, 70))
    d.rectangle([580, 640, 610, 900], fill=(110, 80, 56))
    d.rectangle([1290, 640, 1320, 900], fill=(110, 80, 56))
    for k in range(6):
        _paper(d, 660 + k * 4, 540 - k * 8, 220, 70)
    d.rectangle([980, 560, 1110, 600], fill=(60, 60, 70))                                     # ホチキス
    d.rectangle([980, 548, 1100, 566], fill=(150, 150, 160))
    d.line([(1220, 610), (1220, 460)], fill=(80, 80, 80), width=8)                            # スタンド
    d.polygon([(1170, 460), (1270, 460), (1250, 420), (1190, 420)], fill=(40, 120, 90))
    img = _light(img, [[(1150, 460), (1290, 460), (1340, 610), (1100, 610)]], (255, 240, 190), alpha=50)
    return img


def pk_mansion():
    """下北沢のマンションの一室の事務所（机3つ、窓、段ボール）。"""
    img = _rgb(base((236, 232, 222), (220, 214, 202)))
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(146, 120, 90))
    d = _d(img)
    _window(d, 120, 150, 520, 470)
    d.rectangle([0, 520, W, 530], fill=(200, 194, 182))
    _desk_row(d, 660, (620, 980, 1340), w=300, seed=2)
    d.rectangle([1100, 630, 1170, 660], fill=(240, 236, 226), outline=(120, 110, 100), width=3)          # 名刺の箱
    d.rectangle([1104, 622, 1166, 632], fill=(250, 250, 248), outline=(150, 150, 150))
    for k in range(3):
        d.rectangle([140 + k * 30, 760 - k * 70, 330 + k * 30, 830 - k * 70], fill=(196, 160, 110), outline=(150, 120, 80), width=3)
    return img


def pk_cable():
    """机の上に灰色の携帯ゲーム機2台、灰色のコードでつないである（寄りの画）。"""
    img = _rgb(base((228, 224, 214), (214, 208, 196)))
    d = _d(img)
    d.rectangle([0, 600, W, H], fill=(170, 136, 100))
    d.line([(0, 600), (W, 600)], fill=(130, 100, 72), width=6)
    a = _handheld(d, 560, 330, 1.25)
    b = _handheld(d, 1180, 330, 1.25)
    d.line([a, (a[0], 280), ((a[0] + b[0]) // 2, 250), (b[0], 280), b], fill=(150, 150, 146), width=10, joint="curve")
    return img


def pk_atama():
    """想像の絵：雑木林の上を、2台の機械をつなぐコードが伸びていく。"""
    img = pk_zokibayashi()
    img = _dark(img, 60, col=(250, 240, 200))
    d = _d(img)
    pts = [(180, 700), (500, 300), (900, 420), (1300, 220), (1740, 600)]
    d.line(pts, fill=(160, 160, 156), width=14, joint="curve")
    rnd = random.Random(4)
    for k in range(18):                                                                      # 行き来する光の粒（生き物の姿は描かない）
        i = rnd.randint(0, len(pts) - 2)
        t = rnd.random()
        x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t
        y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(255, 250, 200), outline=(250, 210, 90), width=3)
    _handheld(d, 100, 640, 0.8)
    _handheld(d, 1680, 560, 0.8)
    return img


def _pk_office():
    img = _office_base()
    d = _d(img)
    return img, d


def pk_board(n=1):
    """事務所のホワイトボード。真ん中に「ポケモン」、横に別の仕事の紙が n 枚。n が増えると「ポケモン」の字があせる。"""
    img, d = _pk_office()
    _whiteboard(d)
    fade = {1: (40, 40, 60), 2: (110, 110, 126), 3: (178, 178, 188)}[n]
    _text_c(d, 960, 230, "カプセル", 100, fade)
    _text_c(d, 960, 360, "モンスター", 100, fade)
    spots = [(520, 190), (1240, 190), (1240, 400)]
    for k in range(n):
        x, y = spots[k]
        _paper(d, x, y, 170, 130, col=(255, 246, 180))
        d.ellipse([x + 76, y - 10, x + 94, y + 8], fill=(220, 60, 60))
    return img


def pk_jimusho(mode="yoru"):
    """事務所（机が8つ）。yoru は夜（卓上の灯り）、kara は翌朝で5つの机が空（物が無く椅子だけ）。"""
    img = _rgb(base((232, 228, 216), (214, 208, 194)))
    wood_floor(img, FLOOR, col=(150, 140, 126), line=(130, 120, 108))
    d = _d(img)
    _window(d, 1520, 150, 1860, 440, sky=(40, 50, 90) if mode == "yoru" else (190, 220, 240))
    xs_back = (140, 470, 800, 1130)
    xs_front = (300, 630, 960, 1290)
    empty = {0, 2, 3, 5, 6} if mode == "kara" else set()
    for r, xs in enumerate((xs_back, xs_front)):
        y = 600 + r * 140
        for k, x in enumerate(xs):
            i = r * 4 + k
            d.rectangle([x, y, x + 260, y + 22], fill=(160, 136, 104))
            d.rectangle([x + 12, y + 22, x + 26, y + 160], fill=(130, 108, 82))
            d.rectangle([x + 234, y + 22, x + 248, y + 160], fill=(130, 108, 82))
            if i in empty:
                d.rectangle([x + 100, y - 60, x + 160, y], fill=(90, 90, 100))                  # 椅子の背だけ
            else:
                _crt(d, x + 60, y - 140, 120, 110)
                d.rectangle([x + 190, y - 40, x + 250, y], fill=(246, 242, 230), outline=(160, 150, 130), width=2)
    if mode == "yoru":
        img = _dark(img, 140)
        img = _light(img, [[(1250, 520), (1430, 520), (1500, 760), (1180, 760)]], (255, 220, 150), alpha=70)
    return img


def pk_kaihatsu(kemuri=False):
    """開発室。パソコンが並ぶ（画面は色の四角）。kemuri は真ん中のパソコンから煙。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([0, 700, W, 730], fill=(170, 160, 146))
    for k in range(5):
        x = 160 + k * 340
        _crt(d, x, 500, 240, 200)
        _squares(d, x + 30, 520, x + 210, 670, n=5, seed=k + 11)
    d.ellipse([1095, 640, 1165, 700], fill=(250, 240, 200), outline=(190, 160, 90), width=3)            # うちわ
    d.line([(1130, 700), (1150, 728)], fill=(150, 110, 60), width=6)
    if kemuri:
        rnd = random.Random(8)
        for k in range(16):
            cx = 820 + rnd.randint(-80, 140)
            cy = 470 - k * 26 + rnd.randint(-10, 10)
            r = 50 + k * 8
            d.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], fill=(120 + k * 4, 120 + k * 4, 126 + k * 4))
    return img


def pk_board_mem(mew=False):
    """ホワイトボードに「容量 残り300」。mew はその下に「151」の札が1枚貼られる。"""
    img, d = _pk_office()
    _whiteboard(d)
    _text_c(d, 960, 165, "容量", 70, (40, 40, 60))
    _text_c(d, 960, 250, "残り 300", 108, (200, 40, 40))
    if mew:
        d.rectangle([880, 420, 1040, 520], fill=(255, 236, 246), outline=(200, 120, 160), width=4)
        _text_c(d, 960, 436, "151", 64, (180, 40, 110))
        d.ellipse([951, 408, 969, 426], fill=(60, 120, 220))
    return img


def pk_mise(shinagire=False):
    """1996年のおもちゃ屋の棚。右の隅の下2段に灰色の小さな箱（ゲーム）、上の段は通信のコードの掛け棚。
    shinagire はゲームの箱はそのままで、コードの掛け棚がフックだけになり「品切れ」の札。"""
    img = _rgb(base((236, 228, 208), (222, 212, 190)))
    wood_floor(img, FLOOR, col=(160, 120, 84), line=(134, 100, 70))
    d = _d(img)
    cols = [(230, 80, 80), (70, 130, 220), (250, 200, 60), (90, 180, 110), (240, 240, 240), (170, 100, 200)]
    rnd = random.Random(6)
    for r in range(3):
        y = 230 + r * 170
        d.rectangle([260, y + 130, 1660, y + 146], fill=(130, 96, 66))
        for c in range(10):
            x = 280 + c * 94
            d.rectangle([x, y + 30, x + 80, y + 130], fill=cols[rnd.randint(0, len(cols) - 1)], outline=(80, 70, 60), width=2)
    # 隅の上の段：コードの掛け棚
    d.rectangle([1220, 236, 1650, 360], fill=(200, 190, 170), outline=(140, 120, 96), width=3)
    for c in range(5):
        x = 1262 + c * 82
        d.line([(x, 248), (x, 272)], fill=(110, 110, 110), width=4)
        if not shinagire:
            d.rectangle([x - 28, 268, x + 28, 350], fill=(236, 236, 230), outline=(150, 150, 146), width=2)
            d.arc([x - 18, 284, x + 18, 330], 0, 360, fill=(150, 150, 146), width=4)
    if shinagire:
        d.rectangle([1300, 270, 1570, 350], fill=(255, 255, 255), outline=(200, 40, 40), width=6)
        _text_c(d, 1435, 282, "品切れ", 50, (200, 30, 30))
    # 隅の下2段：灰色の小さな箱（ゲーム）
    for r in (1, 2):
        y = 230 + r * 170
        for c in range(10, 14):
            x = 280 + c * 94
            d.rectangle([x, y + 66, x + 76, y + 130], fill=GRAY if r == 2 else ((196, 70, 60) if c % 2 else (60, 150, 90)),
                        outline=(110, 110, 104), width=2)
    d.rectangle([1480, 410, 1620, 456], fill=(255, 250, 230), outline=(200, 40, 40), width=3)
    _text_c(d, 1550, 414, "3900円", 34, (200, 30, 30))
    return img


def pk_henshubu(level=0):
    """雑誌の編集部（架空）。level 1 は机にはがきの山、2 は床と通路まではがきの山。"""
    img = _office_base()
    d = _d(img)
    for k in range(3):                                                                         # 壁の掲示（線だけ）
        _paper(d, 260 + k * 520, 170, 300, 200)
    for x in (200, 800, 1400):
        d.rectangle([x, 640, x + 380, 664], fill=(150, 126, 96))
        d.rectangle([x + 14, 664, x + 30, 900], fill=(120, 98, 74))
        d.rectangle([x + 350, 664, x + 366, 900], fill=(120, 98, 74))
        for k in range(3):
            d.rectangle([x + 30 + k * 8, 600 - k * 10, x + 150 + k * 8, 640 - k * 10], fill=(246, 242, 230), outline=(160, 150, 130), width=2)
    rnd = random.Random(12)
    if level >= 1:
        for x in (200, 800, 1400):
            for k in range(40):
                px = x + 170 + rnd.randint(0, 180)
                py = 640 - rnd.randint(0, 150)
                d.rectangle([px, py - 22, px + 34, py], fill=(250, 250, 244), outline=(190, 180, 170))
    if level >= 2:
        for k in range(260):
            px = rnd.randint(0, W)
            py = FLOOR + rnd.randint(-120, 120)
            d.rectangle([px, py - 22, px + 34, py], fill=(250, 250, 244), outline=(190, 180, 170))
    return img


def pk_kyoshitsu():
    """小学校の教室（休み時間）。真ん中の机に灰色の携帯ゲーム機2台、灰色のコードでつないである。"""
    img = _ykk_kyoshitsu()
    d = _d(img)
    d.rectangle([780, 700, 1140, 726], fill=(170, 130, 90))
    d.rectangle([800, 726, 816, 880], fill=(130, 100, 70))
    d.rectangle([1104, 726, 1120, 880], fill=(130, 100, 70))
    a = _handheld(d, 820, 580, 0.5)
    b = _handheld(d, 1030, 580, 0.5)
    d.line([a, (a[0], 560), ((a[0] + b[0]) // 2, 548), (b[0], 560), b], fill=(150, 150, 146), width=6, joint="curve")
    return img


def pk_gendai():
    """現代（30周年）。空港の窓の外に飛行機（塗装の絵柄は描かない）。"""
    return kuko_lobby()


# ---------------------------------------------------------------- ニコニコ動画の興亡
def _screen(d, x0, y0, x1, y1, bg=((70, 110, 150), (140, 180, 200)), comments=True, seed=3):
    """架空の動画の画面（無地のグラデーション）の上を白い文字が右から左へ流れる。"""
    for k in range(y1 - y0):
        t = k / max(1, (y1 - y0))
        c = tuple(int(bg[0][i] + (bg[1][i] - bg[0][i]) * t) for i in range(3))
        d.line([(x0, y0 + k), (x1, y0 + k)], fill=c)
    d.rectangle([x0, y0, x1, y1], outline=(20, 20, 24), width=10)
    if comments:
        rnd = random.Random(seed)
        words = ["ｗｗｗ", "きたー", "うおお", "ｗ", "すげえ", "ここ好き", "おおお", "ｗｗ"]
        lanes = max(3, (y1 - y0 - 40) // 80)
        fs = 52 if (x1 - x0) > 800 else 30
        for r in range(lanes):
            y = y0 + 24 + r * (y1 - y0 - 40) // lanes
            x = x0 + 40 + rnd.randint(0, 260)
            while x < x1 - fs * 5:
                _text_c(d, x + fs * 2, y, words[rnd.randint(0, len(words) - 1)], fs, (255, 255, 255))
                x += fs * 6 + rnd.randint(40, 300)


def nc_heya():
    """今の部屋。机にスマホ（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.rounded_rectangle([380, 590, 450, 650], radius=8, fill=(30, 30, 36), outline=(90, 90, 96), width=3)
    d.rectangle([388, 598, 442, 642], fill=(110, 160, 210))
    return img


def nc_happyokai():
    """発表会の壇。後ろに大きなスクリーン（無地）、暗い客席。"""
    img = vgrad((W, H), (14, 16, 30), (34, 34, 54))
    d = _d(img)
    d.rectangle([380, 90, 1540, 560], fill=(30, 40, 70), outline=(120, 140, 200), width=6)
    for k in range(470):
        t = k / 470
        d.line([(386, 96 + k), (1534, 96 + k)], fill=(int(40 + 60 * t), int(60 + 70 * t), int(110 + 60 * t)))
    d.rectangle([200, 600, 1720, 660], fill=(70, 60, 56))
    d.rectangle([1420, 520, 1560, 600], fill=(60, 56, 54))                                   # 演台
    img = _light(img, [[(860, 0), (1060, 0), (1260, 640), (660, 640)]], (255, 246, 220), alpha=50)
    d = _d(img)
    _heads(d, 820, 4, 30, seed=7, col0=16)
    return img


def nc_tsukue_yoru():
    """夜の机（1人）。ノートパソコンの明かりだけ。"""
    img = _dark(heya2("none"), 180)
    d = _d(img)
    d.rectangle([640, 650, 1280, 680], fill=(70, 56, 46))
    d.polygon([(800, 650), (1120, 650), (1160, 670), (760, 670)], fill=(120, 120, 126))
    d.rectangle([820, 450, 1100, 650], fill=(200, 210, 230), outline=(80, 80, 86), width=6)
    _lines(d, 850, 490, 1070, 7, gap=20, col=(110, 110, 130), w=4)
    img = _light(img, [[(820, 450), (1100, 450), (1300, 700), (620, 700)]], (210, 225, 255), alpha=40)
    return img


def nc_chakumero():
    """2000年ごろの小さな会社。段ボール、机にガラケーが並ぶ。"""
    img = jimusho90()
    d = _d(img)
    for k in range(4):
        d.rectangle([1500 + k * 20, 760 - k * 70, 1720 + k * 20, 830 - k * 70], fill=(196, 160, 110), outline=(150, 120, 80), width=3)
    for k in range(5):
        x = 640 + k * 70
        d.rounded_rectangle([x, 580, x + 40, 650], radius=8, fill=[(200, 200, 210), (80, 120, 200), (220, 90, 120), (60, 60, 70), (230, 190, 60)][k],
                            outline=(60, 60, 66), width=2)
        d.rectangle([x + 6, 588, x + 34, 612], fill=(170, 210, 230))
    return img


def nc_kaigi(kami=False):
    """会議室のホワイトボード（案の線）。kami は壁一面に紙が貼られる。"""
    img = _office_base()
    d = _d(img)
    _whiteboard(d, 560, 170, 1360, 520)
    _lines(d, 610, 220, 1300, 6, gap=46, col=(50, 70, 150), w=6)
    d.rectangle([660, 680, 1260, 706], fill=(120, 96, 70))
    if kami:
        rnd = random.Random(21)
        for k in range(46):
            x = rnd.randint(40, W - 200)
            y = rnd.randint(80, 520)
            if 540 < x < 1380 and 150 < y < 540 and rnd.random() < 0.6:
                continue
            _paper(d, x, y, 150, 110, col=[(255, 246, 180), (250, 248, 238), (220, 240, 255)][k % 3])
    return img


def nc_kaihatsu(n=1):
    """開発の机。パソコンが n 台（画面は架空のコメントの線）。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([260, 680, 1660, 706], fill=(150, 126, 96))
    xs = {1: [820], 3: [420, 820, 1220]}[n]
    for k, x in enumerate(xs):
        d.rectangle([x, 470, x + 280, 660], fill=(40, 40, 46), outline=(130, 130, 136), width=5)
        _screen(d, x + 12, 482, x + 268, 648, comments=False)
        for j in range(3 + k):
            d.line([(x + 240 - j * 50, 510 + j * 34), (x + 200 - j * 50, 510 + j * 34)], fill=(255, 255, 255), width=5)
        d.rectangle([x + 120, 660, x + 160, 680], fill=(120, 120, 126))
    return img


def nc_gamen(jiho=False):
    """架空の大きな画面。動画（無地）の上をコメントが流れる。jiho は画面いっぱいに大きな時計。"""
    img = vgrad((W, H), (24, 26, 34), (40, 42, 52))
    d = _d(img)
    if not jiho:
        _screen(d, 220, 80, 1700, 760, seed=5)
    else:
        _screen(d, 220, 80, 1700, 760, bg=((20, 30, 60), (40, 50, 90)), comments=False)
        d.ellipse([760, 170, 1160, 570], fill=(250, 250, 248), outline=(60, 60, 70), width=12)
        for k in range(12):
            import math
            a = math.radians(k * 30)
            d.line([(960 + 170 * math.sin(a), 370 - 170 * math.cos(a)), (960 + 190 * math.sin(a), 370 - 190 * math.cos(a))], fill=(40, 40, 50), width=8)
        d.line([(960, 370), (960, 220)], fill=(30, 30, 40), width=16)
        d.line([(960, 370), (960, 250)], fill=(200, 40, 40), width=6)
        _text_c(d, 960, 610, "0:00", 96, (255, 255, 255))
    d.rectangle([0, 800, W, H], fill=(30, 30, 36))
    return img


def nc_server(aka=False):
    """小さなサーバーの棚（2本）。aka はランプが全部赤。"""
    img = _office_base(wall=(210, 214, 220), floor=(140, 144, 150))
    d = _d(img)
    rnd = random.Random(9)
    for x in (760, 1000):
        d.rectangle([x, 300, x + 200, 900], fill=(40, 42, 50), outline=(90, 90, 100), width=4)
        for r in range(12):
            y = 320 + r * 46
            d.rectangle([x + 14, y, x + 186, y + 34], fill=(26, 28, 34))
            for j in range(4):
                c = (230, 50, 50) if aka else ((80, 220, 120) if rnd.random() < 0.8 else (250, 200, 60))
                d.ellipse([x + 120 + j * 14, y + 12, x + 130 + j * 14, y + 22], fill=c)
    if aka:
        img = _light(img, [[(700, 280), (1260, 280), (1300, 920), (660, 920)]], (255, 40, 40), alpha=40, blur=10)
    return img


def nc_server_room(kara=False):
    """サーバー室。kara は棚だけで中が空っぽ。"""
    if not kara:
        return server_shitsu()
    img = vgrad((W, H), (38, 42, 54), (52, 56, 70))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(130, 136, 146))
    for k in range(7):
        x = 60 + k * 270
        d.rectangle([x, 160, x + 200, FLOOR], outline=(90, 96, 110), width=6)
        for r in range(8):
            d.line([(x + 6, 220 + r * 80), (x + 194, 220 + r * 80)], fill=(70, 74, 86), width=3)
    return img


def nc_chokaigi():
    """大きな展示場の人波（架空）。天井の照明と、ブースの柱。"""
    img = vgrad((W, H), (90, 96, 110), (150, 150, 160))
    d = _d(img)
    for k in range(12):
        x = k * 170
        d.line([(x, 0), (x + 80, 260)], fill=(70, 74, 84), width=6)
    for k in range(9):
        x = 60 + k * 220
        d.rectangle([x, 300, x + 160, 560], fill=[(230, 90, 90), (80, 140, 230), (250, 200, 70), (90, 190, 120)][k % 4], outline=(60, 60, 60), width=3)
    _heads(d, 560, 8, 31, gap=64, seed=11, col0=40)
    return img


def nc_board_256():
    """数字のボード「256万」。"""
    img = _office_base()
    d = _d(img)
    _whiteboard(d, 520, 150, 1400, 560)
    _text_c(d, 960, 200, "有料会員", 76, (40, 40, 60))
    _text_c(d, 960, 300, "256万", 170, (200, 40, 40))
    return img


def nc_shachoshitsu_kara():
    """空になった社長室（机の上に何も無い、椅子が引かれている）。"""
    img = _shacho_base()
    img = _dark(img, 70, col=(30, 34, 50))
    return img


def nc_server_yoru(cable=False):
    """2024年。暗いデータセンターに赤い警告灯。cable は床に抜かれたケーブルの山。"""
    img = _dark(server_shitsu(akai=True), 120)
    img = _light(img, [[(860, 0), (1060, 0), (1300, 700), (620, 700)]], (255, 30, 30), alpha=45, blur=12)
    d = _d(img)
    d.ellipse([920, 40, 1000, 100], fill=(255, 60, 50), outline=(120, 20, 20), width=4)
    if cable:
        rnd = random.Random(17)
        for k in range(70):
            x = rnd.randint(200, 1720)
            y = FLOOR + rnd.randint(-10, 120)
            col = [(40, 120, 220), (230, 200, 60), (60, 60, 64), (220, 60, 60)][k % 4]
            d.arc([x - 120, y - 30, x + 120, y + 40], rnd.randint(0, 180), rnd.randint(200, 360), fill=col, width=7)
    return img


def nc_karifuda(fuda="（Re:仮）"):
    """机の上に手書きの札。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([560, 660, 1360, 690], fill=(150, 126, 96))
    d.polygon([(760, 660), (1160, 660), (1130, 470), (790, 470)], fill=(250, 248, 238), outline=(150, 140, 120))
    _text_c(d, 960, 520, fuda, 84, (40, 40, 60))
    return img


def nc_gendai():
    """現代。夜の銀座の高いビルの窓から見た街の明かり。"""
    img = vgrad((W, H), (10, 14, 34), (30, 30, 60))
    d = _d(img)
    rnd = random.Random(23)
    for k in range(40):
        x = rnd.randint(-40, W)
        w = rnd.randint(80, 200)
        h = rnd.randint(200, 640)
        d.rectangle([x, 900 - h, x + w, 900], fill=(20, 22, 40))
        for r in range(h // 30):
            for c in range(w // 26):
                if rnd.random() < 0.35:
                    d.rectangle([x + 6 + c * 26, 900 - h + 10 + r * 30, x + 18 + c * 26, 900 - h + 24 + r * 30], fill=(250, 220, 140))
    for x in (0, 640, 1280, 1910):                                                            # 窓枠
        d.rectangle([x - 10, 0, x + 10, H], fill=(60, 60, 70))
    d.rectangle([0, 900, W, H], fill=(50, 46, 44))
    return img


# ---------------------------------------------------------------- mixi とモンスト
def _phone_flat(d, x, y, s=1.0, down=True):
    """机に置いたスマホ（画面は伏せる＝黒い板）。"""
    w, h = int(70 * s), int(130 * s)
    d.rounded_rectangle([x, y, x + w, y + h // 3], radius=int(8 * s), fill=(30, 30, 36) if down else (60, 90, 140),
                        outline=(110, 110, 120), width=2)


def mi_heya():
    """今の部屋。机にスマホが4台、みんな別々に置かれている（茶番）。"""
    img = heya2("none")
    d = _d(img)
    for k in range(4):
        _phone_flat(d, 280 + k * 70, 612 + (k % 2) * 10, 0.8)
    return img


def mi_hashikko():
    """2004年、会社の隅。右の隅に机が3つ寄せてある。ほかは広い通路。"""
    img = _office_base()
    d = _d(img)
    for k in range(3):
        x = 1100 + k * 230
        d.rectangle([x, 690, x + 200, 712], fill=(150, 126, 96))
        _crt(d, x + 40, 560, 120, 110)
    return img


def mi_board(midori=False, kai=False):
    """株価のボード（架空）。赤い数字が並ぶ／緑の数字が並ぶ。kai は上場の日の買い気配（値段の欄は空で「買」の札）。
    社名の文字は描かない。"""
    img = vgrad((W, H), (20, 22, 30), (34, 36, 46))
    d = _d(img)
    d.rectangle([180, 100, 1740, 700], fill=(10, 12, 16), outline=(90, 90, 100), width=8)
    rnd = random.Random(31 if midori else 30)
    col = (70, 220, 120) if midori else (240, 70, 60)
    for r in range(7):
        y = 140 + r * 76
        _lines(d, 220, y + 30, 600, 1, col=(170, 170, 180), w=6)
        if kai:
            _text_c(d, 960, y, "− − −", 58, (150, 150, 160))
            d.rectangle([1400, y + 4, 1520, y + 64], fill=(250, 200, 60))
            _text_c(d, 1460, y + 2, "買", 50, (40, 30, 10))
            continue
        num = f"{rnd.randint(1, 19)},{rnd.randint(100, 999)}"
        _text_c(d, 960, y, num, 58, col)
        sign = "+" if midori else "−"
        _text_c(d, 1460, y, f"{sign}{rnd.randint(10, 990)}", 58, col)
    d.rectangle([0, 760, W, H], fill=(40, 40, 46))
    return img


def mi_shima(game=False):
    """2008年のオフィスの島。明るい島（観葉植物と並んだ机）／game は隅の島（段ボールが机に積まれる）。"""
    img = _office_base(wall=(238, 236, 228))
    d = _d(img)
    if not game:
        for k in range(4):
            x = 520 + k * 230
            d.rectangle([x, 680, x + 210, 702], fill=(200, 196, 186))
            d.rectangle([x + 60, 560, x + 150, 660], fill=(40, 44, 56), outline=(150, 150, 156), width=4)
        for x in (440, 1460):
            d.ellipse([x - 60, 420, x + 60, 560], fill=(80, 150, 90))
            d.rectangle([x - 26, 560, x + 26, 700], fill=(170, 120, 80))
    else:
        img = _dark(img, 40, col=(60, 50, 40))
        d = _d(img)
        for k in range(2):
            x = 760 + k * 260
            d.rectangle([x, 680, x + 230, 702], fill=(160, 140, 110))
        for k in range(5):
            d.rectangle([700 + k * 18, 600 - k * 50, 900 + k * 18, 650 - k * 50], fill=(196, 160, 110), outline=(150, 120, 80), width=3)
        d.rectangle([1050, 560, 1150, 660], fill=(40, 44, 56), outline=(150, 150, 156), width=4)
    return img


def mi_meishi(han=False):
    """机の上の名刺の山（寄り）。han は山が半分に減る。"""
    img = _rgb(base((228, 224, 214), (214, 208, 196)))
    d = _d(img)
    d.rectangle([0, 560, W, H], fill=(170, 136, 100))
    rnd = random.Random(41)
    n = 9 if not han else 4
    for k in range(n):
        x = 420 + k * 120
        h = rnd.randint(8, 18) * (1 if not han else 0.5)
        for j in range(int(h)):
            d.rectangle([x + rnd.randint(-4, 4), 600 - j * 9, x + 100 + rnd.randint(-4, 4), 600 - j * 9 + 58], fill=(250, 250, 246), outline=(170, 170, 170))
    return img


def mi_kaijo(kara=False):
    """交流会の明るい会場（無地の横断幕、丸テーブル）。kara は片付いたあと（椅子だけが壁際に）。"""
    img = _rgb(base((236, 232, 222), (224, 218, 206)))
    wood_floor(img, FLOOR, col=(170, 150, 120), line=(150, 130, 104))
    d = _d(img)
    d.rectangle([460, 110, 1460, 220], fill=(250, 180, 60) if not kara else (230, 226, 216), outline=(200, 140, 40) if not kara else (210, 206, 196), width=4)
    if not kara:
        for x in (320, 960, 1600):
            d.ellipse([x - 170, 650, x + 170, 710], fill=(250, 250, 246), outline=(190, 190, 186), width=3)
            d.rectangle([x - 10, 690, x + 10, 840], fill=(150, 150, 150))
        for k in range(8):
            x = 120 + k * 230
            d.ellipse([x, 300, x + 60, 360], fill=[(240, 120, 120), (120, 180, 240), (250, 210, 90)][k % 3])
    else:
        for k in range(12):
            x = 200 + k * 130
            d.rectangle([x, 640, x + 70, 760], fill=(120, 110, 100))
    return img


def mi_kaihatsu(n=1, yoru=False):
    """開発室の机。スマホが n 台（画面は伏せる）。yoru は夜で、机のまわりだけ明るい。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([520, 660, 1400, 690], fill=(150, 126, 96))
    d.rectangle([540, 690, 560, 900], fill=(120, 98, 74))
    d.rectangle([1360, 690, 1380, 900], fill=(120, 98, 74))
    xs = {1: [930], 4: [700, 860, 1020, 1180]}[n]
    for x in xs:
        _phone_flat(d, x, 636, 1.0)
    d.rectangle([600, 560, 760, 660], fill=(40, 44, 56), outline=(150, 150, 156), width=4)   # ノートパソコン
    if yoru:
        img = _dark(img, 150)
        img = _light(img, [[(700, 300), (1220, 300), (1460, 900), (460, 900)]], (255, 220, 160), alpha=60)
    return img


def mi_eki():
    """冬の夜の駅のホーム。柱と蛍光灯、黄色い線、ベンチ。"""
    img = vgrad((W, H), (14, 18, 40), (30, 34, 60))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(120, 120, 126))
    d.rectangle([0, 700, W, 720], fill=(240, 200, 40))
    d.rectangle([0, 80, W, 120], fill=(90, 90, 100))
    for k in range(6):
        x = 100 + k * 340
        d.rectangle([x, 120, x + 40, 700], fill=(150, 150, 160))
        d.rectangle([x - 60, 130, x + 100, 150], fill=(250, 250, 240))
    img = _light(img, [[(0, 150), (W, 150), (W, 700), (0, 700)]], (220, 230, 255), alpha=25)
    d = _d(img)
    d.rectangle([1480, 760, 1820, 790], fill=(80, 120, 170))
    for x in (1500, 1790):
        d.rectangle([x, 790, x + 16, 860], fill=(60, 60, 66))
    return img


def mi_gendai():
    """現代。昼の渋谷の高いビルの窓から見た街。"""
    img = vgrad((W, H), (150, 196, 236), (220, 232, 240))
    d = _d(img)
    rnd = random.Random(29)
    for k in range(36):
        x = rnd.randint(-40, W)
        w = rnd.randint(90, 220)
        h = rnd.randint(200, 620)
        c = rnd.randint(150, 200)
        d.rectangle([x, 900 - h, x + w, 900], fill=(c, c + 4, c + 12), outline=(120, 124, 134))
        for r in range(h // 34):
            d.line([(x + 6, 900 - h + 14 + r * 34), (x + w - 6, 900 - h + 14 + r * 34)], fill=(110, 140, 170), width=3)
    for x in (0, 640, 1280, 1910):
        d.rectangle([x - 10, 0, x + 10, H], fill=(90, 90, 100))
    d.rectangle([0, 900, W, H], fill=(140, 136, 130))
    return img


# ---------------------------------------------------------------- 岩田聡と DS・Wii
def _clamshell(d, x, y, s=1.0, pen=False):
    """折りたたみの2画面の機械（架空・ロゴなし）。開いた形を正面から。"""
    w = int(200 * s)
    d.rounded_rectangle([x, y, x + w, y + int(130 * s)], radius=int(10 * s), fill=(220, 222, 228), outline=(140, 140, 150), width=3)
    d.rectangle([x + int(30 * s), y + int(18 * s), x + w - int(30 * s), y + int(112 * s)], fill=(60, 70, 90))
    d.rounded_rectangle([x, y + int(140 * s), x + w, y + int(270 * s)], radius=int(10 * s), fill=(220, 222, 228), outline=(140, 140, 150), width=3)
    d.rectangle([x + int(40 * s), y + int(158 * s), x + w - int(40 * s), y + int(252 * s)], fill=(200, 210, 220))
    if pen:
        d.line([(x + w + int(30 * s), y + int(280 * s)), (x + w - int(50 * s), y + int(200 * s))], fill=(120, 120, 130), width=int(8 * s))


def iw_heya():
    """今の部屋。テレビの下にゲーム機と電源コード、壁のコンセント（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([1640, 660, 1680, 690], fill=(250, 250, 250), outline=(150, 150, 150), width=2)
    d.line([(1500, 640), (1580, 700), (1650, 676)], fill=(40, 40, 40), width=5)
    d.rectangle([1440, 610, 1540, 640], fill=(240, 240, 244), outline=(150, 150, 156), width=2)
    return img


def iw_gyoretsu():
    """朝の量販店の前の行列（後ろ姿のシルエット）。看板の文字は描かない。"""
    img = vgrad((W, H), (180, 206, 230), (230, 230, 226))
    d = _d(img)
    d.rectangle([200, 120, 1720, 700], fill=(220, 214, 204), outline=(150, 146, 140), width=6)
    d.rectangle([200, 120, 1720, 220], fill=(200, 50, 50))
    for k in range(4):
        d.rectangle([300 + k * 360, 300, 560 + k * 360, 700], fill=(150, 180, 200), outline=(110, 120, 130), width=4)
    d.rectangle([0, 700, W, H], fill=(150, 150, 150))
    _person_line(d, 120, 900, 24, 1.05)
    return img


def iw_kenkyushitsu(yugata=False):
    """大学の研究室。本棚、机に折りたたみの機械が1台。yugata は窓の外が夕方。"""
    img = _rgb(base((226, 224, 216), (210, 206, 196)))
    wood_floor(img, FLOOR, col=(140, 120, 96), line=(120, 102, 82))
    d = _d(img)
    _window(d, 160, 140, 600, 470, sky=(240, 170, 110) if yugata else (180, 214, 236))
    for k in range(3):
        y = 220 + k * 150
        d.rectangle([1360, y, 1820, y + 14], fill=(110, 90, 70))
        for j in range(10):
            d.rectangle([1370 + j * 44, y - 100, 1404 + j * 44, y], fill=((80, 90, 130), (140, 60, 50), (190, 170, 120))[j % 3])
    d.rectangle([660, 660, 1260, 690], fill=(150, 126, 96))
    d.rectangle([680, 690, 700, 900], fill=(120, 98, 74))
    d.rectangle([1220, 690, 1240, 900], fill=(120, 98, 74))
    _clamshell(d, 870, 470, 0.68)
    if yugata:
        img = _light(img, [[(160, 140), (600, 140), (1100, 900), (0, 900)]], (255, 170, 90), alpha=40)
    return img


def iw_kyoshitsu():
    """1970年代の高校の教室。手前の机に、数字だけの小さな画面のプログラム電卓（機種名・ロゴなし）。"""
    img = _nf_kyoshitsu()
    d = _d(img)
    d.rectangle([760, 720, 1160, 748], fill=(170, 130, 90))
    d.rectangle([780, 748, 796, 900], fill=(130, 100, 70))
    d.rectangle([1124, 748, 1140, 900], fill=(130, 100, 70))
    d.rounded_rectangle([890, 560, 1030, 718], radius=10, fill=(60, 60, 64), outline=(30, 30, 30), width=3)
    d.rectangle([904, 574, 1016, 606], fill=(40, 20, 20))
    _text_c(d, 960, 574, "0123", 26, (255, 70, 60))
    for r in range(4):
        for c in range(4):
            x, y = 906 + c * 28, 616 + r * 24
            d.rectangle([x, y, x + 20, y + 16], fill=(200, 200, 196) if c < 3 else (230, 150, 60))
    return img


def iw_shachoshitsu(mode="shorui"):
    """小さな会社の社長室。shorui は机に書類の束、kikaku は企画書だけ。kyoto は京都の社長室（窓の外に低い山）。"""
    img = _shacho_base()
    d = _d(img)
    if mode in ("shorui", "kikaku"):                                                  # 東京の窓（ビルの景色）
        d.rectangle([790, 130, 1170, 410], fill=(186, 206, 226))
        rnd = random.Random(53)
        for k in range(9):
            x = 790 + k * 44 + rnd.randint(-6, 6)
            h = rnd.randint(90, 240)
            d.rectangle([x, 410 - h, x + 40, 410], fill=(150, 156, 170), outline=(120, 124, 136))
        d.line([(980, 120), (980, 420)], fill=(70, 62, 56), width=10)
        d.line([(780, 270), (1180, 270)], fill=(70, 62, 56), width=10)
        d.rectangle([780, 120, 1180, 420], outline=(70, 62, 56), width=10)
    if mode == "shorui":
        rnd = random.Random(51)
        for k in range(14):
            x = 640 + rnd.randint(0, 680)
            d.rectangle([x, 560 - rnd.randint(0, 60), x + 130, 660], fill=(246, 242, 230), outline=(170, 160, 140), width=2)
    elif mode == "kikaku":
        for k in range(3):
            _paper(d, 760 + k * 170, 590, 140, 70, col=(255, 246, 200))
    return img


def iw_kaihatsu():
    """開発室。机に試作の箱と配線。"""
    img = _office_base()
    d = _d(img)
    d.rectangle([420, 660, 1500, 690], fill=(150, 126, 96))
    for k in range(4):
        x = 500 + k * 240
        d.rectangle([x, 580, x + 140, 660], fill=(90, 96, 110), outline=(50, 50, 60), width=3)
        d.line([(x + 140, 620), (x + 240, 640)], fill=[(220, 60, 60), (60, 120, 220), (230, 200, 60)][k % 3], width=5)
    d.rectangle([700, 420, 1000, 560], fill=(40, 44, 56), outline=(150, 150, 156), width=5)
    _squares(d, 720, 440, 980, 545, n=5, seed=61)
    return img


def iw_kaigi(up=False):
    """会議室。ホワイトボードに右肩下がりの折れ線（数字なし）。up は右肩上がりの青い線（DS・Wii のころ）。"""
    img = _office_base()
    d = _d(img)
    _whiteboard(d, 560, 150, 1360, 520)
    pts = [(620, 230), (760, 250), (900, 300), (1040, 350), (1180, 420), (1300, 470)]
    col = (200, 50, 50)
    if up:
        pts = [(x, 700 - y) for x, y in pts]
        col = (40, 110, 210)
    d.line(pts, fill=col, width=10)
    for x, y in pts:
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col)
    d.rectangle([660, 680, 1260, 706], fill=(120, 96, 70))
    return img


def iw_kaihatsu_pen():
    """開発の机に2画面の試作機とペン（寄り）。"""
    img = _rgb(base((226, 224, 216), (210, 206, 196)))
    d = _d(img)
    d.rectangle([0, 640, W, H], fill=(160, 130, 96))
    _clamshell(d, 800, 330, 1.4, pen=True)
    for k in range(3):
        _paper(d, 260 + k * 30, 600 - k * 10, 220, 120)
    return img


def iw_gdc():
    """海外の大きな講演の壇。暗い客席、大きなスクリーン（無地）。"""
    img = vgrad((W, H), (10, 12, 26), (26, 26, 50))
    d = _d(img)
    d.rectangle([300, 70, 1620, 560], fill=(20, 30, 60), outline=(200, 160, 80), width=6)
    for k in range(480):
        t = k / 480
        d.line([(306, 76 + k), (1614, 76 + k)], fill=(int(30 + 40 * t), int(40 + 30 * t), int(90 + 50 * t)))
    d.rectangle([150, 600, 1770, 660], fill=(60, 50, 46))
    d.rectangle([1500, 520, 1620, 600], fill=(50, 46, 44))
    img = _light(img, [[(860, 0), (1060, 0), (1260, 640), (660, 640)]], (255, 246, 220), alpha=55)
    d = _d(img)
    _heads(d, 780, 5, 31, gap=64, seed=71, col0=14)
    return img


def iw_uriba(otona=False):
    """年末のゲーム売り場。棚に色の箱。客のシルエット（若い客／大人やお年寄りも）。"""
    img = _rgb(base((240, 236, 226), (226, 220, 206)))
    wood_floor(img, FLOOR, col=(170, 160, 146), line=(150, 140, 126))
    d = _d(img)
    cols = [(230, 80, 80), (70, 130, 220), (250, 200, 60), (90, 180, 110), (240, 240, 240)]
    rnd = random.Random(81)
    for r in range(3):
        y = 200 + r * 150
        d.rectangle([200, y + 110, 1720, y + 124], fill=(140, 120, 96))
        for c in range(18):
            x = 220 + c * 82
            d.rectangle([x, y + 30, x + 66, y + 110], fill=cols[rnd.randint(0, len(cols) - 1)], outline=(90, 80, 70), width=2)
    if not otona:
        _person_line(d, 260, 900, 9, 0.85)
    else:
        _person_line(d, 160, 920, 6, 1.0, cols=[(80, 80, 100), (110, 90, 80), (90, 100, 90)])
        for k in range(6):                                                         # 白髪まじりの頭
            x = 160 + k * 70
            d.ellipse([x, 920 - 150, x + 46, 920 - 104], fill=(190, 190, 190) if k % 2 else (40, 34, 30))
        _person_line(d, 1100, 900, 7, 0.85)
    return img


def iw_ima():
    """居間のテレビの前。机に白い棒の形のリモコンが転がっている。"""
    img = heya2("none")
    d = _d(img)
    d.rounded_rectangle([600, 640, 1240, 700], radius=14, fill=(160, 120, 90))
    d.rounded_rectangle([760, 640, 790, 660], radius=6, fill=(250, 250, 250), outline=(160, 160, 170), width=2)
    d.rounded_rectangle([780, 624, 960, 642], radius=8, fill=(250, 250, 250), outline=(160, 160, 170), width=2)
    d.rounded_rectangle([1000, 620, 1110, 642], radius=6, fill=(40, 40, 40))                  # テレビのリモコン
    d.rounded_rectangle([140, 600, 520, 760], radius=30, fill=(120, 140, 170))                # ソファ
    return img


def iw_kanbai():
    """夜明けの店先に「完売」の札。"""
    img = vgrad((W, H), (90, 110, 160), (240, 190, 150))
    d = _d(img)
    d.rectangle([200, 140, 1720, 700], fill=(200, 194, 186), outline=(140, 136, 130), width=6)
    d.rectangle([200, 140, 1720, 230], fill=(200, 50, 50))
    for k in range(4):
        d.rectangle([300 + k * 360, 300, 560 + k * 360, 700], fill=(110, 130, 150), outline=(90, 100, 110), width=4)
    d.rectangle([780, 330, 1140, 470], fill=(255, 255, 255), outline=(200, 40, 40), width=8)
    _text_c(d, 960, 350, "完売", 86, (200, 30, 30))
    d.rectangle([0, 700, W, H], fill=(140, 140, 146))
    return img


def iw_sokai():
    """株主総会の会場。壇上に長い議長席、客席の頭。"""
    img = _rgb(base((220, 214, 200), (204, 196, 182)))
    d = _d(img)
    d.rectangle([300, 120, 1620, 420], fill=(120, 40, 50), outline=(90, 30, 40), width=6)       # 幕
    d.rectangle([260, 440, 1660, 520], fill=(250, 250, 246), outline=(190, 190, 186), width=4)
    for k in range(6):
        d.ellipse([400 + k * 220, 420, 430 + k * 220, 450], fill=(60, 60, 60))
    d.rectangle([0, 600, W, H], fill=(150, 140, 126))
    _heads(d, 760, 5, 31, gap=64, seed=91, col0=30)
    return img


def iw_ame():
    """雨の夜、傘の列（顔は描かない）。"""
    img = vgrad((W, H), (20, 24, 40), (40, 44, 60))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(50, 52, 60))
    for k in range(22):
        x = 60 + k * 84
        y = 640 + (k % 2) * 16
        d.pieslice([x - 60, y - 50, x + 60, y + 50], 180, 360, fill=[(40, 44, 60), (70, 70, 90), (30, 40, 50)][k % 3], outline=(90, 90, 110), width=2)
        d.line([(x, y), (x, y + 140)], fill=(30, 30, 30), width=4)
        d.rounded_rectangle([x - 22, y + 20, x + 22, y + 140], radius=10, fill=(24, 24, 30))
    rnd = random.Random(101)
    for k in range(260):
        x = rnd.randint(0, W)
        y = rnd.randint(0, H)
        d.line([(x, y), (x - 10, y + 40)], fill=(160, 170, 200), width=2)
    return img


def iw_gendai():
    """現代。昼の京都の街（低い建物と、向こうの山並み）。"""
    img = vgrad((W, H), (160, 200, 236), (226, 234, 238))
    d = _d(img)
    d.polygon([(0, 520), (300, 380), (640, 470), (980, 360), (1340, 460), (1700, 380), (W, 450), (W, 620), (0, 620)], fill=(110, 150, 120))
    rnd = random.Random(111)
    for k in range(30):
        x = rnd.randint(-40, W)
        w = rnd.randint(100, 240)
        h = rnd.randint(80, 260)
        c = rnd.randint(170, 220)
        d.rectangle([x, 760 - h, x + w, 760], fill=(c, c - 6, c - 14), outline=(130, 120, 110))
        d.polygon([(x - 10, 760 - h), (x + w // 2, 760 - h - 40), (x + w + 10, 760 - h)], fill=(90, 90, 100))
    d.rectangle([0, 760, W, H], fill=(150, 146, 140))
    return img


LOCATIONS = {
    # mixi とモンスト
    "mi_heya": mi_heya, "mi_hashikko": mi_hashikko, "mi_board": mi_board, "mi_board_midori": lambda: mi_board(midori=True), "mi_board_kai": lambda: mi_board(kai=True),
    "mi_sns_shima": mi_shima, "mi_game_shima": lambda: mi_shima(game=True),
    "mi_meishi": mi_meishi, "mi_meishi_han": lambda: mi_meishi(han=True),
    "mi_kaijo": mi_kaijo, "mi_kaijo_kara": lambda: mi_kaijo(kara=True), "mi_kissaten": _pu_kissaten, "mi_kaigi": _now_kaigi,
    "mi_kaihatsu_1": mi_kaihatsu, "mi_kaihatsu_4": lambda: mi_kaihatsu(4), "mi_kaihatsu_yoru": lambda: mi_kaihatsu(4, yoru=True),
    "mi_kaikenjo": _sega_kaiken, "mi_eki": mi_eki, "mi_kyoshitsu": _nf_kyoshitsu, "mi_gendai": mi_gendai,
    # 岩田聡と DS・Wii
    "iw_heya": iw_heya, "iw_gyoretsu": iw_gyoretsu, "iw_kenkyushitsu": iw_kenkyushitsu,
    "iw_kenkyushitsu_yugata": lambda: iw_kenkyushitsu(yugata=True), "iw_kyoshitsu": iw_kyoshitsu,
    "iw_shachoshitsu_shorui": iw_shachoshitsu, "iw_shachoshitsu_kikaku": lambda: iw_shachoshitsu("kikaku"),
    "iw_shachoshitsu_kyoto": lambda: iw_shachoshitsu("kyoto"), "iw_kaihatsu": iw_kaihatsu, "iw_kaigi": iw_kaigi, "iw_kaigi_up": lambda: iw_kaigi(up=True),
    "iw_kaihatsu_pen": iw_kaihatsu_pen, "iw_gdc": iw_gdc, "iw_uriba": iw_uriba, "iw_uriba_otona": lambda: iw_uriba(otona=True),
    "iw_ima": iw_ima, "iw_kanbai": iw_kanbai, "iw_setsumeikai": _sega_kaiken, "iw_sokai": iw_sokai, "iw_ame": iw_ame,
    "iw_gendai": iw_gendai,
    # ポケモンの誕生
    "pk_heya": pk_heya, "pk_kaigi": pk_kaigi, "pk_zokibayashi": pk_zokibayashi,
    "pk_zokibayashi_zosei": lambda: pk_zokibayashi(zosei=True), "pk_doujin": pk_doujin, "pk_mansion": pk_mansion,
    "pk_cable": pk_cable, "pk_atama": pk_atama,
    "pk_board": lambda: pk_board(1), "pk_board_2": lambda: pk_board(2), "pk_board_3": lambda: pk_board(3),
    "pk_jimusho_yoru": lambda: pk_jimusho("yoru"), "pk_jimusho_kara": lambda: pk_jimusho("kara"),
    "pk_kaihatsu": pk_kaihatsu, "pk_kaihatsu_kemuri": lambda: pk_kaihatsu(kemuri=True),
    "pk_board_300": pk_board_mem, "pk_board_mew": lambda: pk_board_mem(mew=True),
    "pk_mise": pk_mise, "pk_mise_shinagire": lambda: pk_mise(shinagire=True),
    "pk_henshubu": pk_henshubu, "pk_henshubu_hagaki": lambda: pk_henshubu(1), "pk_henshubu_yuka": lambda: pk_henshubu(2),
    "pk_kyoshitsu": pk_kyoshitsu, "pk_gendai": pk_gendai,
    # ニコニコ動画の興亡
    "nc_heya": nc_heya, "nc_happyokai": nc_happyokai, "nc_tsukue_yoru": nc_tsukue_yoru, "nc_chakumero": nc_chakumero,
    "nc_kaigi": nc_kaigi, "nc_kaigi_kami": lambda: nc_kaigi(kami=True),
    "nc_kaihatsu": nc_kaihatsu, "nc_kaihatsu_3": lambda: nc_kaihatsu(3),
    "nc_gamen": nc_gamen, "nc_jiho": lambda: nc_gamen(jiho=True),
    "nc_server": nc_server, "nc_server_aka": lambda: nc_server(aka=True),
    "nc_server_kara": lambda: nc_server_room(kara=True), "nc_server_ippai": nc_server_room,
    "nc_chokaigi": nc_chokaigi, "nc_board_256": nc_board_256, "nc_shachoshitsu_kara": nc_shachoshitsu_kara,
    "nc_server_yoru": nc_server_yoru, "nc_server_cable": lambda: nc_server_yoru(cable=True),
    "nc_karifuda": nc_karifuda, "nc_karifuda_2006": lambda: nc_karifuda("（仮）"), "nc_gendai": nc_gendai,
}

# 年号カード。接頭辞ごとに "pk_card_1996" のように作る（台本を見て足す）
CARDS = {"pk": ["1989", "1990", "1995", "1996", "1997", "1998", "2026"],
         "nc": ["2001", "2006", "2007", "2010", "2012", "2014", "2017", "2019", "2024", "2026"],
         "mi": ["2004", "2006", "2008", "2012", "2013", "2014", "2015", "2018", "2024", "2026"],
         "iw": ["2002", "2003", "2004", "2005", "2006", "2009", "2011", "2013", "2014", "2015", "2026"]}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        _rgb(fn()).save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for pre, years in CARDS.items():
        for y in years:
            nm = f"{pre}_card_{y}"
            if only and nm not in only:
                continue
            year_card(f"{y}年").save(OUT / f"{nm}.png")
            print(f"生成完了: {nm}.png")
