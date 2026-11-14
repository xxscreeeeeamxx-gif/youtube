#!/usr/bin/env python3
"""第8弾4本（2026-11-25〜28。方向転換の実験の9〜12本目：会社の転落・破綻・裁判）の背景を生成する。

接頭辞: ld_（ライブドア事件）/ dz_（大王製紙のカジノ）/ tj_（西武鉄道の上場廃止）/ mx_（マウントゴックスの破綻）
方針は gen_now7_bgs.py と同じ。実在の会社のロゴ・社名の文字・店の意匠・商品のパッケージは描かない。
実在の人の写真や肖像は描かない（壁の写真は人の形だけ）。差し替え用は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now8_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import year_card  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _d, _rgb, kaigi, yakuin  # noqa: E402
from scripts.gen_now2_bgs import heya2, kabunushi_kaijo, shoken  # noqa: E402
from scripts.gen_now3_bgs import jimusho90  # noqa: E402
from scripts.gen_now5_bgs import cg_saikosai  # noqa: E402
from scripts.gen_sega_bgs import _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import kokkai as _sogo_kokkai, saibansho as _sogo_saibansho  # noqa: E402


# ---------------------------------------------------------------- 大王製紙のカジノ
def dz_heya():
    """今の部屋。机にスマホ（ゲームのくじの画面＝色の光だけ）と、ティッシュの箱（無地）。"""
    img = heya2("none")
    d = _d(img)
    d.rounded_rectangle([230, 560, 300, 640], radius=10, fill=(30, 30, 34))
    d.rectangle([238, 570, 292, 630], fill=(250, 200, 60))
    for k in range(4):
        d.ellipse([244 + k * 12, 590, 252 + k * 12, 598], fill=(240, 80, 120))
    d.rectangle([360, 590, 520, 640], fill=(240, 240, 248), outline=(170, 170, 180), width=3)
    d.polygon([(420, 590), (440, 560), (460, 590)], fill=(252, 252, 252), outline=(190, 190, 196))
    return img


def dz_kojo(old=False):
    """海沿いの製紙工場。煙突と白い煙、倉庫の屋根、手前に海。old は煙突1本と小さな建屋だけ（昔の三島）。"""
    img = vgrad((W, H), (170, 200, 228), (222, 230, 236))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(80, 130, 170))
    for k in range(6):
        d.line([(0, 800 + k * 40), (W, 800 + k * 40)], fill=(110, 156, 190), width=3)
    d.rectangle([0, 600, W, 760], fill=(150, 150, 146))
    stacks = [(900,)] if old else [(300,), (620,), (900,), (1180,), (1500,)]
    for (x,) in stacks:
        d.rectangle([x - 26, 220, x + 26, 600], fill=(200, 196, 190), outline=(140, 136, 130), width=3)
        for r in range(3):
            d.rectangle([x - 26, 260 + r * 110, x + 26, 278 + r * 110], fill=(200, 60, 50))
        for k in range(4):
            d.ellipse([x - 40 - k * 30, 120 - k * 30, x + 50 - k * 20, 210 - k * 30], fill=(244, 244, 246))
    if old:
        d.rectangle([700, 470, 1180, 600], fill=(170, 150, 120), outline=(120, 100, 80), width=4)
    else:
        for k in range(4):
            d.polygon([(100 + k * 460, 600), (100 + k * 460, 470), (420 + k * 460, 430), (420 + k * 460, 600)],
                      fill=(214, 216, 220), outline=(150, 150, 156))
    return img


def _chips(d, x, y, n, col):
    for k in range(n):
        d.ellipse([x, y - k * 10 - 12, x + 60, y - k * 10 + 8], fill=col, outline=(40, 30, 20), width=2)


def dz_vip(yama=False, kara=False):
    """海外のカジノの VIP ルーム。緑の台（カードの台）、赤い壁、シャンデリア。
    yama は台の上にチップの山（天井近くまで）。kara は台の上に何も無く、椅子も空。"""
    img = vgrad((W, H), (90, 20, 26), (60, 12, 18))
    d = _d(img)
    for k in range(5):                                                                          # シャンデリア
        x = 260 + k * 350
        d.line([(x, 0), (x, 90)], fill=(200, 170, 90), width=4)
        d.ellipse([x - 70, 90, x + 70, 150], fill=(250, 220, 140), outline=(200, 170, 90), width=3)
        for j in range(5):
            d.ellipse([x - 60 + j * 28, 150, x - 48 + j * 28, 170], fill=(255, 240, 200))
    for k in range(8):                                                                          # 壁の金の線
        d.line([(k * 260, 180), (k * 260, 640)], fill=(150, 110, 60), width=6)
    d.rectangle([0, 640, W, H], fill=(40, 10, 14))
    d.ellipse([360, 560, 1560, 900], fill=(30, 110, 60), outline=(120, 80, 40), width=24)       # 台
    for k in range(5):
        d.rectangle([520 + k * 200, 700, 620 + k * 200, 760], fill=(250, 250, 240), outline=(200, 190, 160), width=2)
    if not kara:
        cols = [(220, 40, 40), (250, 210, 60), (40, 90, 200), (30, 30, 34)]
        n = 26 if yama else 5
        for k in range(8):
            _chips(d, 560 + k * 100, 680, n - (k % 3) * (6 if yama else 1), cols[k % 4])
        for k in range(4):
            d.rounded_rectangle([420 + k * 300, 900, 540 + k * 300, 1000], radius=20, fill=(120, 20, 30))
    return img


def dz_keiri(soshiki=True):
    """子会社の経理部。机と書類、壁に組織図（四角と線。名前は線）。"""
    img = jimusho90()
    d = _d(img)
    if soshiki:
        d.rectangle([1260, 140, 1820, 520], fill=(250, 250, 246), outline=(150, 150, 150), width=4)
        d.rectangle([1490, 170, 1590, 220], fill=(230, 80, 70))
        for k in range(4):
            x = 1290 + k * 130
            d.line([(1540, 220), (x + 50, 300)], fill=(80, 80, 80), width=3)
            d.rectangle([x, 300, x + 100, 350], fill=(230, 80, 70) if k in (0, 2) else (200, 210, 230))
            for j in range(2):
                d.line([(x + 50, 350), (x + 20 + j * 60, 420)], fill=(80, 80, 80), width=2)
                d.rectangle([x + j * 60, 420, x + 40 + j * 60, 450], fill=(230, 80, 70))
    return img


def dz_jigyobu(denwa=False):
    """本社の関連事業部の島（机が向かい合う）。denwa は全部の机で受話器が上がる（人の形は描かない）。"""
    img = _rgb(base((236, 236, 232), (222, 222, 218)))
    wood_floor(img, FLOOR, col=(190, 190, 186), line=(176, 176, 172))
    d = _d(img)
    for k in range(10):
        d.rectangle([60 + k * 190, 90, 120 + k * 190, 110], fill=(250, 250, 240))
    d.rectangle([260, 600, 1660, 700], fill=(200, 196, 186), outline=(150, 146, 136), width=4)
    for k in range(6):
        x = 320 + k * 220
        d.rectangle([x, 520, x + 120, 600], fill=(40, 40, 44))
        d.rectangle([x + 8, 528, x + 112, 590], fill=(140, 170, 200))
        if denwa:
            d.rounded_rectangle([x + 130, 470, x + 160, 560], radius=10, fill=(30, 30, 34))
            for j in range(3):
                d.arc([x + 160 + j * 10, 470 - j * 10, x + 200 + j * 14, 530 + j * 10], -60, 60, fill=(230, 60, 50), width=4)
        else:
            d.rounded_rectangle([x + 130, 570, x + 200, 600], radius=8, fill=(30, 30, 34))
    return img


def dz_uriba():
    """ドラッグストアの棚。ティッシュの箱が並ぶ（無地・色違い。商品名は描かない）。"""
    img = vgrad((W, H), (246, 246, 244), (232, 232, 230))
    d = _d(img)
    for r in range(4):
        y = 200 + r * 180
        d.rectangle([80, y + 140, 1840, y + 160], fill=(200, 200, 204))
        for k in range(14):
            x = 100 + k * 124
            col = [(240, 240, 250), (210, 230, 250), (250, 220, 230), (230, 245, 225)][(k + r) % 4]
            d.rectangle([x, y + 40, x + 110, y + 140], fill=col, outline=(170, 170, 180), width=2)
            d.ellipse([x + 35, y + 50, x + 75, y + 70], fill=(252, 252, 252), outline=(190, 190, 196))
    d.rectangle([0, 920, W, H], fill=(214, 214, 210))
    return img



# ---------------------------------------------------------------- 西武鉄道の上場廃止
def tj_heya():
    """今の部屋。机にノートパソコン（株価のグラフ＝線だけ）と、定期券のような券。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([200, 560, 380, 640], fill=(40, 40, 46), outline=(20, 20, 24), width=3)
    d.rectangle([210, 566, 370, 630], fill=(230, 240, 250))
    d.line([(220, 620), (260, 600), (300, 610), (340, 580), (360, 590)], fill=(220, 40, 40), width=4)
    d.rounded_rectangle([420, 610, 500, 640], radius=6, fill=(250, 220, 120), outline=(160, 130, 60))
    return img


def tj_bunsitsu(hako=False):
    """1960年代の個人の事務所。木の棚に株券の束（紐でくくった紙）。hako は棚が空になり、床に段ボール箱。"""
    img = _rgb(base((222, 208, 184), (204, 188, 162)))
    wood_floor(img, FLOOR, col=(130, 96, 64), line=(110, 80, 52))
    d = _d(img)
    d.rectangle([260, 160, 1660, 720], fill=(120, 84, 52), outline=(80, 56, 34), width=6)
    for r in range(4):
        y = 200 + r * 130
        d.rectangle([280, y + 110, 1640, y + 122], fill=(90, 62, 38))
        if not hako:
            for k in range(16):
                x = 300 + k * 82
                d.rectangle([x, y + 30, x + 70, y + 110], fill=(236, 226, 196), outline=(170, 150, 110), width=2)
                d.line([(x + 35, y + 30), (x + 35, y + 110)], fill=(170, 60, 50), width=3)
    if hako:
        for k in range(5):
            d.rectangle([340 + k * 260, 800, 560 + k * 260, 960], fill=(196, 160, 110), outline=(140, 110, 70), width=3)
            d.rectangle([400 + k * 260, 840, 500 + k * 260, 880], fill=(250, 250, 246))
    return img


def tj_kabushiki(new=False, kara=False):
    """鉄道会社の株式の事務の部屋。壁の棚に印鑑の箱と封筒の束、机。new は20年後（机の上が新しいパソコン）。
    kara は印鑑の棚が空。"""
    img = _rgb(base((232, 230, 222), (218, 216, 208)))
    wood_floor(img, FLOOR, col=(170, 160, 140), line=(150, 140, 122))
    d = _d(img)
    d.rectangle([200, 140, 1000, 640], fill=(150, 120, 90), outline=(100, 80, 60), width=5)
    for r in range(5):
        y = 170 + r * 92
        d.rectangle([220, y + 80, 980, y + 88], fill=(110, 84, 60))
        if not kara:
            for k in range(14):
                d.rectangle([236 + k * 52, y + 30, 276 + k * 52, y + 80], fill=(60, 40, 30))
                d.ellipse([244 + k * 52, y + 20, 268 + k * 52, y + 36], fill=(200, 40, 40))
    d.rectangle([1200, 560, 1800, 620], fill=(200, 190, 170), outline=(150, 140, 120), width=3)
    if not kara:
        for k in range(6):
            d.rectangle([1220 + k * 30, 470 - k * 6, 1400 + k * 30, 560 - k * 6], fill=(250, 248, 236), outline=(170, 160, 140))
    if new:
        d.rectangle([1500, 430, 1720, 560], fill=(40, 40, 44))
        d.rectangle([1510, 440, 1710, 545], fill=(160, 190, 220))
    else:
        d.rectangle([1500, 470, 1700, 560], fill=(200, 196, 180), outline=(120, 116, 100), width=3)
        for k in range(4):
            d.line([(1520, 490 + k * 18), (1680, 490 + k * 18)], fill=(140, 136, 120), width=3)
    return img


def tj_kaiken():
    """ホテルの宴会場での会見。金の屏風、白い布の長い机とマイク、手前に記者席とフラッシュ。"""
    img = vgrad((W, H), (120, 96, 70), (90, 70, 50))
    d = _d(img)
    for k in range(5):
        d.ellipse([260 + k * 350, 40, 340 + k * 350, 90], fill=(255, 240, 200))
    d.rectangle([360, 160, 1560, 560], fill=(220, 180, 80), outline=(160, 120, 40), width=6)
    for k in range(1, 6):
        d.line([(360 + k * 200, 160), (360 + k * 200, 560)], fill=(180, 140, 60), width=4)
    d.rectangle([300, 560, 1620, 640], fill=(250, 250, 250), outline=(190, 190, 196), width=3)
    d.rectangle([300, 640, 1620, 700], fill=(236, 236, 240))
    for k in range(6):
        d.line([(500 + k * 200, 560), (500 + k * 200, 510)], fill=(30, 30, 34), width=6)
        d.ellipse([488 + k * 200, 494, 512 + k * 200, 518], fill=(30, 30, 34))
    d.rectangle([0, 760, W, H], fill=(60, 44, 30))
    _person_line(d, 60, 1040, 12, 1.0)
    for x, y in ((240, 820), (900, 780), (1600, 830)):
        d.ellipse([x - 40, y - 40, x + 40, y + 40], fill=(255, 255, 240, 200))
    return img


def tj_board(kanri=False):
    """株価のボード（数字は線）。kanri は1行だけ赤く光り、横に赤い札（監理）。"""
    img = vgrad((W, H), (20, 24, 34), (14, 16, 24))
    d = _d(img)
    for r in range(8):
        for c in range(4):
            x, y = 160 + c * 420, 140 + r * 100
            hi = kanri and r == 3 and c == 1
            d.rectangle([x, y, x + 380, y + 80], fill=(80, 20, 20) if hi else (34, 40, 54), outline=(60, 70, 90), width=2)
            d.rectangle([x + 20, y + 25, x + 140, y + 55], fill=(230, 230, 236))
            d.rectangle([x + 200, y + 25, x + 360, y + 55], fill=(240, 60, 60) if hi else (60, 220, 120))
    if kanri:
        d.rectangle([1020, 430, 1160, 490], fill=(220, 30, 30))
        d.rectangle([1040, 448, 1140, 472], fill=(255, 255, 255))
    return img


def tj_osetsu(henpin=False):
    """取引先の会社の応接室。机の上に大きな封筒が1つ。henpin は封筒が返品の箱に入っている。"""
    img = _rgb(yakuin(view=(190, 210, 230), city=True))
    d = _d(img)
    d.rectangle([520, 820, 1400, 870], fill=(110, 80, 56))
    for x in (380, 1420):
        d.rounded_rectangle([x, 740, x + 220, 900], radius=26, fill=(90, 60, 44), outline=(60, 40, 28), width=4)
    if henpin:
        d.rectangle([820, 720, 1100, 820], fill=(196, 160, 110), outline=(140, 110, 70), width=3)
        d.rectangle([860, 700, 1060, 740], fill=(240, 230, 200), outline=(150, 140, 110))
    else:
        d.rectangle([860, 790, 1060, 820], fill=(240, 230, 200), outline=(150, 140, 110), width=2)
    return img


def tj_shinbun():
    """机の上に広げた新聞（大見出しは黒い太い帯、記事は線）。"""
    img = vgrad((W, H), (150, 120, 90), (120, 92, 66))
    d = _d(img)
    d.polygon([(260, 160), (1680, 120), (1720, 940), (220, 980)], fill=(240, 236, 224), outline=(180, 170, 150))
    d.rectangle([340, 220, 1000, 330], fill=(30, 30, 30))
    d.rectangle([1060, 220, 1600, 300], fill=(200, 40, 40))
    for k in range(14):
        d.line([(340, 380 + k * 38), (1000, 380 + k * 38)], fill=(120, 120, 120), width=4)
        d.line([(1060, 340 + k * 38), (1600, 340 + k * 38)], fill=(120, 120, 120), width=4)
    return img


def tj_biru(kind=0):
    """本社のビルの正面。kind=0 は古い看板（緑の板）、1 は新しい看板（青の板）。文字は描かない。"""
    img = vgrad((W, H), (170, 200, 230), (226, 232, 238))
    d = _d(img)
    d.rectangle([460, 100, 1460, 900], fill=(210, 206, 198), outline=(150, 146, 140), width=6)
    for r in range(7):
        for c in range(6):
            d.rectangle([520 + c * 156, 140 + r * 90, 620 + c * 156, 200 + r * 90], fill=(150, 180, 206))
    d.rectangle([840, 760, 1080, 900], fill=(120, 150, 176), outline=(90, 90, 96), width=4)
    col = (40, 120, 70) if kind == 0 else (30, 80, 170)
    d.rectangle([700, 690, 1220, 750], fill=col, outline=(80, 80, 86), width=4)
    d.line([(740, 720), (1180, 720)], fill=(255, 255, 255), width=8)
    d.rectangle([0, 900, W, H], fill=(190, 186, 180))
    return img



# ---------------------------------------------------------------- マウントゴックスの破綻
def mx_heya():
    """今の部屋。机にゲームセンターのメダルの預かりカードと、メダルが数枚（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.rounded_rectangle([220, 590, 340, 640], radius=8, fill=(60, 120, 200), outline=(30, 60, 120), width=3)
    d.rectangle([236, 604, 324, 616], fill=(250, 250, 250))
    for k in range(5):
        d.ellipse([370 + k * 26, 610 - (k % 2) * 8, 400 + k * 26, 640 - (k % 2) * 8], fill=(220, 180, 60), outline=(160, 120, 30))
    return img


def _screen(d, x0, y0, x1, y1, bar=0.5, red=False):
    """架空の取引所の画面（ロゴも文字も無い）。左に残高の帯、右に値動きの線。"""
    d.rectangle([x0, y0, x1, y1], fill=(24, 28, 40), outline=(60, 64, 80), width=4)
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0 + 20, y0 + 20, x0 + int(w * 0.45), y0 + 60], fill=(60, 70, 96))
    d.rectangle([x0 + 20, y0 + 80, x0 + 20 + int((w * 0.45 - 20) * bar), y0 + 130],
                fill=(230, 70, 70) if red else (70, 210, 140))
    pts = [(x0 + int(w * 0.52) + k * int(w * 0.06), y1 - 40 - int(h * 0.55 * ((k * 37) % 7) / 7)) for k in range(8)]
    d.line(pts, fill=(250, 200, 70), width=4)


def mx_jimusho_s(yama=False):
    """2011年の渋谷の小さな事務所。机1つにパソコン1台。yama は机の上にモニターとサーバーが山積み（差し替え用）。"""
    img = _rgb(base((230, 228, 222), (214, 212, 206)))
    wood_floor(img, FLOOR, col=(170, 160, 146), line=(152, 142, 128))
    d = _d(img)
    d.rectangle([1200, 160, 1560, 420], fill=(180, 210, 236), outline=(120, 120, 126), width=6)
    d.line([(1380, 160), (1380, 420)], fill=(120, 120, 126), width=4)
    d.rectangle([520, 620, 1160, 680], fill=(150, 120, 90), outline=(110, 84, 60), width=3)
    if yama:
        for r in range(3):
            for c in range(4 - r):
                x, y = 560 + c * 140 + r * 70, 520 - r * 110
                _screen(d, x, y, x + 130, y + 100, bar=0.3 + 0.2 * ((c + r) % 3))
        for k in range(3):
            d.rectangle([1180 + k * 70, 480, 1240 + k * 70, 680], fill=(50, 52, 60), outline=(30, 30, 34), width=3)
            for j in range(6):
                d.ellipse([1200 + k * 70, 500 + j * 28, 1208 + k * 70, 508 + j * 28], fill=(80, 230, 120))
    else:
        _screen(d, 700, 470, 960, 620)
    return img


def mx_jimusho(kami=False):
    """2013年の事務所。社員の机が並ぶ。奥の壁に「払い戻し待ち」の紙が1枚。kami は壁一面が紙（差し替え用）。"""
    img = _rgb(base((236, 236, 232), (222, 222, 218)))
    wood_floor(img, FLOOR, col=(190, 190, 186), line=(176, 176, 172))
    d = _d(img)
    d.rectangle([160, 120, 1760, 460], fill=(244, 244, 240), outline=(200, 200, 196), width=3)
    sheets = [(x, y) for y in range(140, 440, 70) for x in range(190, 1740, 60)] if kami else [(900, 220)]
    rnd = random.Random(7)
    for x, y in sheets:
        dx = rnd.randint(-6, 6)
        d.rectangle([x + dx, y, x + dx + 46, y + 58], fill=(255, 250, 220), outline=(200, 190, 150))
        d.line([(x + dx + 8, y + 18), (x + dx + 38, y + 18)], fill=(200, 60, 50), width=3)
        d.line([(x + dx + 8, y + 32), (x + dx + 38, y + 32)], fill=(150, 150, 150), width=2)
    for r in range(2):
        d.rectangle([220, 600 + r * 160, 1700, 660 + r * 160], fill=(200, 196, 186), outline=(150, 146, 136), width=3)
        for k in range(6):
            x = 280 + k * 240
            _screen(d, x, 520 + r * 160, x + 150, 600 + r * 160, bar=0.6)
    return img


def mx_kinko(hikari=False):
    """金庫の部屋。並んだ金庫の扉がみな閉じている（中は空の札）。hikari は1つだけ扉が開いて光る（古い財布）。"""
    img = vgrad((W, H), (40, 44, 56), (24, 26, 34))
    d = _d(img)
    for k in range(5):
        x = 200 + k * 320
        d.rectangle([x, 300, x + 260, 760], fill=(110, 116, 128), outline=(70, 74, 84), width=6)
        if hikari and k == 3:
            d.rectangle([x + 20, 320, x + 240, 740], fill=(255, 236, 150))
            for j in range(8):
                d.ellipse([x + 50 + (j % 4) * 44, 520 + (j // 4) * 60, x + 90 + (j % 4) * 44, 560 + (j // 4) * 60],
                          fill=(240, 180, 40), outline=(180, 120, 20))
            d.polygon([(x + 240, 320), (x + 340, 280), (x + 340, 800), (x + 240, 740)], fill=(130, 136, 148), outline=(70, 74, 84))
        else:
            d.ellipse([x + 90, 460, x + 170, 540], fill=(150, 156, 168), outline=(80, 84, 94), width=5)
            d.line([(x + 130, 470), (x + 130, 530)], fill=(80, 84, 94), width=5)
            d.rectangle([x + 70, 620, x + 190, 660], fill=(240, 240, 236))
    d.rectangle([0, 800, W, H], fill=(50, 52, 60))
    return img


def mx_biru(kamera=False):
    """渋谷の雑居ビルの入口。歩道に札を持つ人の形が1人。kamera は報道のカメラと人の列（差し替え用）。"""
    img = vgrad((W, H), (190, 200, 214), (224, 226, 230))
    d = _d(img)
    d.rectangle([520, 60, 1400, 880], fill=(196, 190, 182), outline=(140, 134, 126), width=6)
    for r in range(6):
        for c in range(4):
            d.rectangle([580 + c * 200, 100 + r * 110, 720 + c * 200, 170 + r * 110], fill=(140, 166, 190))
    d.rectangle([820, 740, 1100, 880], fill=(90, 110, 130), outline=(60, 60, 66), width=4)
    d.rectangle([0, 880, W, H], fill=(170, 168, 164))
    # 札を持つ人（人の形と白い板。文字は描かない）
    d.ellipse([300, 700, 360, 760], fill=(70, 70, 80))
    d.rectangle([290, 760, 370, 960], fill=(70, 70, 80))
    d.rectangle([220, 720, 440, 820], fill=(250, 250, 250), outline=(120, 120, 120), width=4)
    d.line([(240, 750), (420, 750)], fill=(30, 30, 30), width=6)
    d.line([(240, 785), (400, 785)], fill=(30, 30, 30), width=6)
    if kamera:
        _person_line(d, 1300, 1000, 8, 1.0)
        for k in range(5):
            x = 1180 + k * 140
            d.rectangle([x, 880, x + 70, 930], fill=(30, 30, 34))
            d.ellipse([x - 20, 890, x + 10, 920], fill=(60, 60, 70))
    return img


def mx_gamen(shiro=False, plus=False):
    """壁いっぱいの架空の取引所の画面。shiro はサイトが閉じて真っ白。plus は残高の帯が一気に伸びる（画面の上だけの30万枚）。"""
    img = vgrad((W, H), (34, 36, 44), (20, 22, 28))
    d = _d(img)
    if shiro:
        d.rectangle([260, 120, 1660, 860], fill=(252, 252, 252), outline=(80, 84, 96), width=8)
        return img
    _screen(d, 260, 120, 1660, 860, bar=1.0 if plus else 0.12)
    if plus:
        d.polygon([(1100, 260), (1180, 200), (1260, 260)], fill=(70, 210, 140))
        d.rectangle([1160, 260, 1200, 360], fill=(70, 210, 140))
    return img


def mx_ryuchijo(jisho=False):
    """留置所の部屋。高い所に鉄格子の窓、壁に日数の線。jisho は線が増え、床に辞書が積み上がる（差し替え用）。"""
    img = _rgb(base((200, 198, 190), (184, 182, 174)))
    d = _d(img)
    d.rectangle([0, 820, W, H], fill=(150, 146, 138))
    d.rectangle([780, 120, 1140, 320], fill=(200, 220, 236), outline=(90, 90, 96), width=8)
    for k in range(1, 6):
        d.line([(780 + k * 60, 120), (780 + k * 60, 320)], fill=(70, 70, 76), width=8)
    n = 40 if jisho else 8
    for k in range(n):
        x = 260 + (k % 20) * 26
        y = 460 + (k // 20) * 90
        d.line([(x, y), (x, y + 60)], fill=(110, 106, 98), width=4)
    if jisho:
        for k in range(7):
            d.rectangle([1300 - k * 4, 800 - k * 40, 1520 + k * 3, 838 - k * 40], fill=(150 - k * 8, 40, 40), outline=(80, 20, 20))
    return img


def mx_genkan():
    """早朝の住宅街の路地。建物の入口の前に報道陣の列（人の形）とカメラ。家の中は描かない。"""
    img = vgrad((W, H), (120, 140, 176), (196, 200, 212))
    d = _d(img)
    d.rectangle([700, 140, 1500, 820], fill=(176, 172, 166), outline=(120, 116, 110), width=6)
    d.rectangle([1000, 600, 1200, 820], fill=(90, 80, 70), outline=(60, 50, 40), width=4)
    d.rectangle([0, 820, W, H], fill=(140, 140, 144))
    _person_line(d, 0, 1000, 14, 1.0)
    for k in range(6):
        x = 80 + k * 140
        d.rectangle([x, 860, x + 70, 910], fill=(30, 30, 34))
        d.ellipse([x - 20, 870, x + 10, 900], fill=(60, 60, 70))
    return img


def mx_oshirase():
    """管財人のお知らせの紙と、弁済のお知らせの画面（どちらも文字は線だけ）。"""
    img = vgrad((W, H), (226, 228, 232), (206, 208, 214))
    d = _d(img)
    d.rectangle([240, 140, 900, 940], fill=(255, 255, 255), outline=(170, 170, 176), width=4)
    d.rectangle([300, 200, 840, 240], fill=(40, 40, 46))
    for k in range(16):
        d.line([(300, 300 + k * 38), (840 - (k % 3) * 60, 300 + k * 38)], fill=(150, 150, 156), width=4)
    d.rectangle([1040, 260, 1700, 760], fill=(30, 34, 44), outline=(80, 84, 96), width=6)
    d.rectangle([1080, 300, 1660, 350], fill=(70, 110, 200))
    for k in range(7):
        d.line([(1080, 400 + k * 46), (1620 - (k % 2) * 120, 400 + k * 46)], fill=(200, 204, 214), width=4)
    d.rectangle([1080, 700, 1400, 730], fill=(230, 70, 70))
    return img



# ---------------------------------------------------------------- ライブドア事件
def ld_heya():
    """今の部屋。机に細かく切った丸いピザ（茶番）。"""
    import math

    img = heya2("none")
    d = _d(img)
    cx, cy, r = 330, 612, 70
    d.ellipse([cx - r, cy - 26, cx + r, cy + 26], fill=(230, 170, 70), outline=(170, 110, 40), width=4)
    d.ellipse([cx - r + 10, cy - 20, cx + r - 10, cy + 20], fill=(220, 80, 50))
    for k in range(24):
        a = math.pi * 2 * k / 24
        d.line([(cx, cy), (cx + int(r * math.cos(a)), cy + int(26 * math.sin(a)))], fill=(250, 230, 180), width=2)
    for k in range(6):
        d.ellipse([cx - 50 + k * 18, cy - 8 + (k % 2) * 8, cx - 42 + k * 18, cy + (k % 2) * 8], fill=(250, 240, 200))
    return img


def ld_tower(yoake=False, sosaku=False):
    """超高層ビルの入口（ガラスの壁）。yoake は夜明けの空と報道陣、sosaku は夜の入口から段ボールが運び出される。"""
    if sosaku:
        img = vgrad((W, H), (16, 20, 40), (40, 44, 70))
    elif yoake:
        img = vgrad((W, H), (90, 110, 170), (250, 190, 150))
    else:
        img = vgrad((W, H), (150, 190, 230), (220, 230, 240))
    d = _d(img)
    d.polygon([(560, 0), (1360, 0), (1300, 880), (620, 880)], fill=(70, 90, 120) if sosaku else (120, 150, 180),
              outline=(60, 70, 90))
    for r in range(20):
        y = 20 + r * 42
        light = (230, 220, 150) if (sosaku and (r * 7) % 3 == 0) else ((90, 110, 140) if sosaku else (170, 200, 226))
        d.line([(570 + r * 3, y), (1350 - r * 3, y)], fill=light, width=6)
    d.rectangle([820, 740, 1100, 880], fill=(200, 220, 236) if not sosaku else (230, 230, 200), outline=(60, 60, 66), width=4)
    d.rectangle([0, 880, W, H], fill=(120, 120, 126) if sosaku else (170, 168, 164))
    if yoake or sosaku:
        _person_line(d, 0, 1010, 8, 1.0)
        _person_line(d, 1360, 1010, 8, 1.0)
        for k in range(4):
            x = 80 + k * 140
            d.rectangle([x, 870, x + 70, 920], fill=(30, 30, 34))
    if sosaku:
        for k in range(6):
            x, y = 840 + (k % 3) * 80, 800 + (k // 3) * 50
            d.rectangle([x, y, x + 70, y + 46], fill=(196, 160, 110), outline=(140, 110, 70), width=3)
    return img


def ld_gamen(aka=False):
    """ネット証券の画面（パソコン2台）。値動きの線と、数字の代わりの帯。aka は帯が全部ストップ高の赤。"""
    img = _rgb(base((236, 236, 232), (222, 222, 218)))
    wood_floor(img, FLOOR, col=(190, 186, 176), line=(176, 172, 162))
    d = _d(img)
    d.rectangle([260, 640, 1660, 700], fill=(200, 196, 186), outline=(150, 146, 136), width=4)
    for k in range(2):
        x0 = 420 + k * 600
        d.rectangle([x0, 280, x0 + 480, 600], fill=(24, 28, 40), outline=(60, 64, 80), width=6)
        d.rectangle([x0 + 220, 600, x0 + 260, 640], fill=(60, 60, 66))
        for r in range(8):
            col = (230, 50, 50) if (aka or r in (0, 3)) else (70, 200, 130)
            d.rectangle([x0 + 20, 300 + r * 34, x0 + 120, 322 + r * 34], fill=(200, 204, 214))
            d.rectangle([x0 + 140, 300 + r * 34, x0 + 220, 322 + r * 34], fill=col)
        pts = [(x0 + 250 + j * 28, 560 - j * (30 if aka else 12) - (j % 2) * 10) for j in range(8)]
        d.line(pts, fill=(250, 80, 80) if aka else (250, 200, 70), width=4)
    return img


def ld_kumiai():
    """古いビルの廊下。たくさんの郵便受けと、表札だけの小さな扉（名前だけの事務所）。文字は線だけ。"""
    img = _rgb(base((214, 210, 200), (196, 192, 182)))
    d = _d(img)
    d.rectangle([0, 820, W, H], fill=(150, 146, 138))
    for r in range(4):
        for c in range(8):
            x, y = 200 + c * 110, 300 + r * 80
            d.rectangle([x, y, x + 96, y + 66], fill=(170, 172, 176), outline=(110, 112, 118), width=3)
            d.rectangle([x + 10, y + 10, x + 86, y + 20], fill=(250, 250, 246))
    d.rectangle([1260, 260, 1560, 820], fill=(140, 110, 80), outline=(90, 70, 50), width=6)
    d.ellipse([1500, 520, 1530, 550], fill=(220, 200, 120))
    d.rectangle([1320, 330, 1500, 380], fill=(250, 250, 246), outline=(160, 160, 160), width=2)
    d.line([(1340, 355), (1480, 355)], fill=(60, 60, 60), width=4)
    return img


def ld_radio(nuri=False):
    """ラジオ局の会議室。ホワイトボードに株主の円グラフ（文字なし）。nuri は円グラフの3分の1が新しい色に塗り替わる。"""
    img = _rgb(kaigi())
    d = _d(img)
    d.rectangle([700, 90, 1220, 420], fill=(250, 250, 250), outline=(150, 150, 156), width=6)
    cx, cy, r = 960, 255, 130
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=(170, 190, 220))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], -90, -90 + 72, fill=(240, 170, 60))
    if nuri:
        d.pieslice([cx - r, cy - r, cx + r, cy + r], -18, -18 + 126, fill=(220, 50, 60))
    for k in range(4):
        d.line([(1110, 160 + k * 40), (1200, 160 + k * 40)], fill=(120, 120, 126), width=4)
    return img


def ld_wakai():
    """和解の会見。白い壁の前に長い机、マイク4本と名札の台（文字なし）、手前に記者席。"""
    img = vgrad((W, H), (226, 228, 232), (200, 202, 208))
    d = _d(img)
    d.rectangle([200, 560, 1720, 640], fill=(250, 250, 250), outline=(180, 180, 186), width=3)
    d.rectangle([200, 640, 1720, 700], fill=(234, 234, 238))
    for k in range(4):
        x = 420 + k * 360
        d.line([(x, 560), (x, 500)], fill=(30, 30, 34), width=6)
        d.ellipse([x - 12, 484, x + 12, 508], fill=(30, 30, 34))
        d.rectangle([x + 40, 520, x + 160, 560], fill=(246, 246, 240), outline=(170, 170, 170), width=2)
    d.rectangle([0, 780, W, H], fill=(70, 70, 80))
    _person_line(d, 60, 1040, 12, 1.0)
    for x, y in ((300, 820), (1100, 790), (1700, 830)):
        d.ellipse([x - 40, y - 40, x + 40, y + 40], fill=(255, 255, 240))
    return img


def ld_torihikijo(kie=False):
    """取引所の監視の部屋。大きな電光板と、手前に監視の机とモニター。kie は電光板が全部消える。"""
    img = vgrad((W, H), (30, 34, 46), (18, 20, 28))
    d = _d(img)
    d.rectangle([160, 80, 1760, 520], fill=(10, 12, 16), outline=(70, 76, 90), width=6)
    if not kie:
        for r in range(9):
            for c in range(8):
                x, y = 190 + c * 196, 100 + r * 46
                d.rectangle([x, y, x + 80, y + 26], fill=(220, 220, 226))
                d.rectangle([x + 96, y, x + 176, y + 26], fill=(230, 60, 60) if (r + c) % 3 else (70, 200, 130))
    d.rectangle([200, 700, 1720, 760], fill=(80, 84, 96), outline=(50, 52, 60), width=3)
    for k in range(6):
        x = 260 + k * 250
        d.rectangle([x, 590, x + 180, 690], fill=(24, 28, 40), outline=(70, 74, 86), width=4)
        d.rectangle([x + 10, 600, x + 170, 680], fill=(40, 40, 50) if kie else (60, 100, 160))
    d.rectangle([0, 760, W, H], fill=(40, 42, 50))
    return img


def ld_kanmae():
    """霞が関の官庁街の歩道。石の建物の前に、報道陣の列とカメラ。"""
    img = vgrad((W, H), (160, 190, 226), (226, 230, 236))
    d = _d(img)
    d.rectangle([300, 120, 1620, 800], fill=(206, 198, 186), outline=(150, 142, 130), width=6)
    for r in range(5):
        for c in range(9):
            d.rectangle([360 + c * 140, 170 + r * 110, 440 + c * 140, 240 + r * 110], fill=(120, 140, 160))
    d.rectangle([0, 800, W, H], fill=(176, 174, 170))
    _person_line(d, 0, 1000, 9, 1.0)
    _person_line(d, 1300, 1000, 9, 1.0)
    for k in range(5):
        x = 60 + k * 150
        d.rectangle([x, 860, x + 70, 910], fill=(30, 30, 34))
    return img


def ld_hei(kisetsu="natsu"):
    """刑務所の高い塀と、手前の木1本（建物の中は描かない）。kisetsu: natsu / yuki / sakura。"""
    sky = {"natsu": ((120, 170, 230), (210, 230, 246)), "yuki": ((176, 184, 196), (226, 228, 232)),
           "sakura": ((170, 200, 236), (236, 240, 246))}[kisetsu]
    img = vgrad((W, H), *sky)
    d = _d(img)
    d.rectangle([0, 360, W, 860], fill=(196, 192, 184), outline=(150, 146, 140), width=4)
    for k in range(12):
        d.line([(k * 170, 360), (k * 170, 860)], fill=(176, 172, 164), width=3)
    d.rectangle([0, 340, W, 362], fill=(150, 146, 140))
    ground = (240, 242, 246) if kisetsu == "yuki" else (120, 150, 90)
    d.rectangle([0, 860, W, H], fill=ground)
    d.rectangle([1440, 560, 1480, 900], fill=(100, 72, 50))
    leaf = {"natsu": (60, 140, 70), "yuki": (240, 242, 246), "sakura": (246, 190, 210)}[kisetsu]
    for k in range(7):
        d.ellipse([1330 + (k % 4) * 60, 400 + (k // 4) * 90, 1470 + (k % 4) * 60, 540 + (k // 4) * 90], fill=leaf)
    if kisetsu == "yuki":
        d.rectangle([0, 330, W, 346], fill=(250, 250, 252))
        rnd = random.Random(3)
        for _ in range(140):
            x, y = rnd.randint(0, W), rnd.randint(0, H)
            d.ellipse([x, y, x + 6, y + 6], fill=(255, 255, 255))
    return img


LOCATIONS = {
    # 大王製紙のカジノ
    "dz_heya": dz_heya, "dz_kojo": dz_kojo, "dz_kojo_old": lambda: dz_kojo(old=True),
    "dz_vip": dz_vip, "dz_vip_yama": lambda: dz_vip(yama=True), "dz_vip_kara": lambda: dz_vip(kara=True),
    "dz_keiri": dz_keiri, "dz_jigyobu": dz_jigyobu, "dz_jigyobu_denwa": lambda: dz_jigyobu(denwa=True),
    "dz_yakuin": lambda: yakuin(), "dz_komon": lambda: yakuin(view=(200, 210, 200), city=False),
    "dz_kaigi": kaigi, "dz_kaigi_akaji": lambda: kaigi(akaji=True), "dz_kaiken": _sega_kaiken,
    "dz_houtei": _sogo_saibansho, "dz_saikosai": cg_saikosai, "dz_jimusho": jimusho90,
    "dz_uriba": dz_uriba, "dz_gendai": _sega_gendai,
    # 西武鉄道の上場廃止
    "tj_heya": tj_heya, "tj_bunsitsu": tj_bunsitsu, "tj_bunsitsu_hako": lambda: tj_bunsitsu(hako=True),
    "tj_kabushiki": tj_kabushiki, "tj_kabushiki_new": lambda: tj_kabushiki(new=True),
    "tj_kabushiki_kara": lambda: tj_kabushiki(new=True, kara=True),
    "tj_kaiken": tj_kaiken, "tj_board": tj_board, "tj_board_kanri": lambda: tj_board(kanri=True),
    "tj_osetsu": tj_osetsu, "tj_osetsu_henpin": lambda: tj_osetsu(henpin=True), "tj_shinbun": tj_shinbun,
    "tj_biru": tj_biru, "tj_biru_new": lambda: tj_biru(1),
    "tj_yakuin": lambda: yakuin(), "tj_kaigi": kaigi, "tj_kaigi_akaji": lambda: kaigi(akaji=True),
    "tj_kaijo": _sega_kaiken, "tj_houtei": _sogo_saibansho, "tj_shoken": shoken, "tj_jimusho": jimusho90,
    "tj_gendai": _sega_gendai,
    # マウントゴックスの破綻
    "mx_heya": mx_heya, "mx_jimusho_s": mx_jimusho_s, "mx_jimusho_s_yama": lambda: mx_jimusho_s(yama=True),
    "mx_jimusho": mx_jimusho, "mx_jimusho_kami": lambda: mx_jimusho(kami=True),
    "mx_kinko": mx_kinko, "mx_kinko_hikari": lambda: mx_kinko(hikari=True),
    "mx_biru": mx_biru, "mx_biru_kamera": lambda: mx_biru(kamera=True),
    "mx_gamen": mx_gamen, "mx_gamen_plus": lambda: mx_gamen(plus=True), "mx_gamen_shiro": lambda: mx_gamen(shiro=True),
    "mx_denwa": lambda: dz_jigyobu(denwa=True), "mx_ryuchijo": mx_ryuchijo,
    "mx_ryuchijo_jisho": lambda: mx_ryuchijo(jisho=True), "mx_genkan": mx_genkan, "mx_oshirase": mx_oshirase,
    "mx_kaiken": _sega_kaiken, "mx_kaijo": lambda: kabunushi_kaijo(), "mx_houtei": _sogo_saibansho,
    "mx_kaigi": kaigi, "mx_yakuin": lambda: yakuin(), "mx_gendai": _sega_gendai,
    # ライブドア事件
    "ld_heya": ld_heya, "ld_tower": ld_tower, "ld_tower_yoake": lambda: ld_tower(yoake=True),
    "ld_tower_sosaku": lambda: ld_tower(sosaku=True), "ld_gamen": ld_gamen, "ld_gamen_aka": lambda: ld_gamen(aka=True),
    "ld_kumiai": ld_kumiai, "ld_radio": ld_radio, "ld_radio_nuri": lambda: ld_radio(nuri=True),
    "ld_wakai": ld_wakai, "ld_torihikijo": ld_torihikijo, "ld_torihikijo_kie": lambda: ld_torihikijo(kie=True),
    "ld_kanmae": ld_kanmae, "ld_hei": ld_hei, "ld_hei_yuki": lambda: ld_hei("yuki"),
    "ld_hei_sakura": lambda: ld_hei("sakura"),
    "ld_shacho": lambda: yakuin(view=(170, 196, 230), city=True), "ld_zaimu": jimusho90, "ld_kaigi": kaigi,
    "ld_shoken": shoken, "ld_kaiken": _sega_kaiken, "ld_houtei": _sogo_saibansho, "ld_saikosai": cg_saikosai,
    "ld_gendai": _sega_gendai,
}

# 年号カード。接頭辞ごとに "dz_card_2011" のように作る
CARDS = {"dz": ["1943", "1987", "2007", "2010", "2011", "2012", "2013", "2016", "2019", "2026"],
         "tj": ["1957", "1964", "1977", "1983", "1987", "2004", "2005", "2006", "2014", "2016", "2026"],
         "mx": ["2011", "2013", "2014", "2015", "2017", "2018", "2019", "2020", "2024", "2026"],
         "ld": ["1996", "2000", "2004", "2005", "2006", "2007", "2008", "2011", "2013", "2026"]}


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
