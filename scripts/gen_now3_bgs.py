#!/usr/bin/env python3
"""「いまの話題」第3弾4本（2026-11-05〜08）の背景を生成する。

接頭辞: dc_（ドコモとiモード）/ sh_（シャープの亀山工場）/ nk_（ニコンの露光装置）/ jl_（JALの破綻と稲盛和夫）
方針は gen_now_bgs.py と同じ。実在の会社のロゴ・社名の文字・製品の意匠は描かない。
差し替え用（_yoru・_kara・_nesage・_akaji・_up）は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now3_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import _boxes, _papers, _phone, _window, year_card  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _d, _rgb, kaigi, kuko_yoru, yakuin  # noqa: E402
from scripts.gen_now2_bgs import _price, heya2, shoken  # noqa: E402
from scripts.gen_sega_bgs import _flat_tv, _glow, _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sega_bgs import kojo as _sega_fab  # noqa: E402
from scripts.gen_sogo_bgs import saibansho as _sogo_saibansho  # noqa: E402

LINE = (90, 92, 98)


# ---------------------------------------------------------------- 小物
def _keitai(d, x, y, s=1.0, col=(200, 200, 210), screen=(120, 180, 230)):
    """開いた折りたたみの携帯電話（下の端の中央が x, y）。"""
    w = 56 * s
    d.rounded_rectangle([x - w / 2, y - 110 * s, x + w / 2, y], radius=int(10 * s), fill=col, outline=LINE, width=2)       # 下（ボタン）
    for r in range(4):
        for c in range(3):
            bx, by = x - 18 * s + c * 14 * s, y - 92 * s + r * 18 * s
            d.rectangle([bx, by, bx + 9 * s, by + 10 * s], fill=(240, 240, 244))
    d.rounded_rectangle([x - w / 2, y - 230 * s, x + w / 2, y - 112 * s], radius=int(10 * s), fill=col, outline=LINE, width=2)  # 上（画面）
    d.rectangle([x - w / 2 + 7 * s, y - 214 * s, x + w / 2 - 7 * s, y - 136 * s], fill=screen)


def _sumaho(d, x, y, s=1.0, col=(30, 30, 34), screen=(70, 130, 200)):
    """立てたスマートフォン（下の端の中央が x, y）。"""
    w, h = 70 * s, 140 * s
    d.rounded_rectangle([x - w / 2, y - h, x + w / 2, y], radius=int(12 * s), fill=col)
    d.rounded_rectangle([x - w / 2 + 5 * s, y - h + 8 * s, x + w / 2 - 5 * s, y - 8 * s], radius=int(8 * s), fill=screen)


def _crt(d, x, y, s=1.0):
    """ブラウン管のパソコンの画面（下の端の中央が x, y）。"""
    d.rectangle([x - 70 * s, y - 120 * s, x + 70 * s, y - 10 * s], fill=(214, 210, 196), outline=LINE, width=2)
    d.rectangle([x - 56 * s, y - 106 * s, x + 56 * s, y - 30 * s], fill=(40, 70, 110))
    d.rectangle([x - 30 * s, y - 10 * s, x + 30 * s, y], fill=(200, 196, 182))


def _desk(d, x0, x1, y, col=(186, 180, 168)):
    """事務机の天板と脚。"""
    d.rectangle([x0, y, x1, y + 22], fill=col, outline=(130, 126, 116), width=2)
    d.rectangle([x0 + 10, y + 22, x0 + 30, FLOOR], fill=(150, 146, 136))
    d.rectangle([x1 - 30, y + 22, x1 - 10, FLOOR], fill=(150, 146, 136))


def _plane_side(d, x, y, s=1.0, body=(244, 244, 248), stripe=None):
    """横から見た旅客機（機首の下が x, y。右向き）。会社の塗装は描かない。"""
    d.rounded_rectangle([x - 900 * s, y - 120 * s, x, y], radius=int(60 * s), fill=body, outline=(150, 150, 156), width=3)
    d.polygon([(x - 860 * s, y - 110 * s), (x - 960 * s, y - 330 * s), (x - 860 * s, y - 330 * s), (x - 720 * s, y - 110 * s)],
              fill=body, outline=(150, 150, 156))                                                                      # 尾翼
    d.polygon([(x - 560 * s, y - 40 * s), (x - 380 * s, y - 40 * s), (x - 520 * s, y + 90 * s), (x - 600 * s, y + 90 * s)],
              fill=(220, 220, 226), outline=(150, 150, 156))                                                           # 主翼
    d.rounded_rectangle([x - 520 * s, y + 30 * s, x - 400 * s, y + 80 * s], radius=int(20 * s), fill=(200, 200, 206))  # エンジン
    for k in range(14):
        wx = x - 820 * s + k * 52 * s
        d.ellipse([wx, y - 82 * s, wx + 20 * s, y - 62 * s], fill=(70, 90, 120))
    d.polygon([(x - 70 * s, y - 100 * s), (x - 20 * s, y - 70 * s), (x - 70 * s, y - 70 * s)], fill=(50, 60, 80))         # 操縦席の窓
    if stripe:
        d.rectangle([x - 880 * s, y - 40 * s, x - 30 * s, y - 28 * s], fill=stripe)


def heya3(kind):
    """今の部屋（heya2 の無地に足す）。kind=keitai は机にスマホと古い折りたたみの携帯、tv は大きいテレビ、
    sumaho はスマホとノートパソコン、ryoko は旅行かばん。"""
    img = heya2("none")
    d = _d(img)
    if kind == "keitai":
        _sumaho(d, 320, 636, 0.8)
        _keitai(d, 470, 636, 0.62, col=(220, 60, 90))
    elif kind == "tv":
        d.rectangle([1300, 250, 1880, 610], fill=(232, 228, 220))                       # heya2 のテレビを消して大きく
        _flat_tv(d, 1240, 200, 1880, 580, screen=(30, 110, 170))
    elif kind == "sumaho":
        _sumaho(d, 300, 636, 0.8)
        d.polygon([(420, 640), (600, 640), (610, 630), (430, 630)], fill=(60, 60, 66))
        d.rectangle([430, 540, 600, 628], fill=(40, 44, 52), outline=(90, 90, 96), width=2)
        d.rectangle([438, 548, 592, 620], fill=(70, 120, 180))
    elif kind == "ryoko":
        d.rounded_rectangle([230, 470, 400, 640], radius=14, fill=(40, 70, 130), outline=(20, 40, 80), width=4)
        d.rectangle([300, 430, 330, 470], fill=(60, 60, 66))
        _sumaho(d, 520, 636, 0.8)
    return img


# ---------------------------------------------------------------- ドコモとiモード
def jimusho90(yoru=False):
    """1990年代の後半の事務所。島になった事務机、ブラウン管のパソコン、壁に白板。yoru は窓が暗く机の灯り。"""
    img = _rgb(base((226, 226, 218), (212, 212, 204)) if not yoru else base((120, 120, 130), (100, 100, 110)))
    wood_floor(img, FLOOR, col=(150, 150, 146), line=(132, 132, 128))
    d = _d(img)
    _window(d, 1380, 120, 1840, 420, sky=(196, 214, 230) if not yoru else (20, 26, 50), frame=(120, 120, 126))
    d.rectangle([120, 120, 760, 400], fill=(248, 248, 244), outline=(140, 140, 146), width=6)            # 白板
    for k in range(5):
        d.line([(160, 160 + k * 48), (520 + (k % 3) * 70, 160 + k * 48)], fill=(60, 80, 160), width=5)
    _desk(d, 200, 1720, 620)
    for k in range(6):
        x = 300 + k * 240
        _crt(d, x, 620, 0.9)
        if k % 2:
            _keitai(d, x + 100, 620, 0.32, col=(180, 184, 196))
    _papers(d, 1600, 610, n=3)
    if yoru:
        for k in range(3):
            _glow(img, 400 + k * 500, 520, 160, (255, 240, 190), 80)
    return img


def server_shitsu(akai=False):
    """サーバー室。黒い棚が並び、緑の灯り。akai は赤い灯りが点く（つながりにくくなった場面）。"""
    img = vgrad((W, H), (40, 46, 56), (56, 62, 72))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(140, 146, 154))
    for k in range(9):
        d.line([(k * 240, FLOOR), (k * 240 - 80, H)], fill=(120, 126, 134), width=4)
    rnd = random.Random(7)
    for k in range(7):
        x = 60 + k * 270
        d.rectangle([x, 160, x + 220, FLOOR], fill=(24, 26, 30), outline=(70, 74, 82), width=4)
        for r in range(14):
            y = 190 + r * 46
            d.rectangle([x + 16, y, x + 204, y + 34], fill=(40, 42, 48))
            for c in range(5):
                on = rnd.random()
                col = (230, 50, 40) if (akai and on < 0.5) else ((60, 220, 110) if on < 0.7 else (40, 60, 50))
                d.ellipse([x + 140 + c * 12, y + 12, x + 148 + c * 12, y + 20], fill=col)
    return img


def keitai_shop():
    """携帯電話の店の店内。手前に台の上の見本の携帯、奥に受付のカウンター。"""
    img = _rgb(base((246, 244, 240), (232, 230, 226)))
    wood_floor(img, FLOOR, col=(210, 204, 196), line=(196, 190, 182))
    d = _d(img)
    d.rectangle([0, 60, W, 110], fill=(200, 30, 50))                                  # 店の帯（文字なし）
    d.rectangle([160, 200, 820, 420], fill=(250, 250, 252), outline=(200, 200, 206), width=4)   # 壁のポスター（絵だけ）
    d.ellipse([220, 230, 400, 400], fill=(250, 200, 70))
    d.rectangle([460, 260, 780, 290], fill=(200, 30, 50))
    d.rectangle([1040, 420, 1820, 520], fill=(250, 250, 252), outline=(190, 190, 196), width=4)  # 受付
    for k in range(3):
        d.rectangle([1100 + k * 240, 380, 1180 + k * 240, 420], fill=(60, 60, 66))
    d.rectangle([120, 640, 900, 700], fill=(236, 236, 240), outline=(180, 180, 186), width=3)     # 見本の台
    cols = [(220, 60, 90), (60, 120, 220), (240, 240, 244), (40, 40, 44), (240, 170, 40), (120, 200, 120)]
    for k in range(6):
        _keitai(d, 180 + k * 125, 640, 0.5, col=cols[k])
    return img


def densha():
    """通勤電車の車内。長い座席、つり革、窓の外は明るい。"""
    img = vgrad((W, H), (226, 228, 226), (210, 212, 210))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(150, 140, 120))
    for k in range(4):                                                                 # 窓
        x = 80 + k * 470
        d.rectangle([x, 200, x + 400, 470], fill=(190, 216, 236), outline=(160, 162, 166), width=10)
    d.rectangle([0, 520, W, 640], fill=(70, 100, 160))                                # 座席
    d.rectangle([0, 640, W, 690], fill=(60, 64, 70))
    d.line([(0, 110), (W, 110)], fill=(170, 172, 176), width=10)                      # つり革の棒
    for k in range(16):
        x = 60 + k * 120
        d.line([(x, 110), (x, 170)], fill=(240, 240, 240), width=4)
        d.ellipse([x - 20, 170, x + 20, 210], outline=(240, 240, 240), width=6)
    return img


def keitai_uriba(sumaho=False):
    """量販店の携帯売り場。棚に見本の携帯がずらり。sumaho はスマホが並ぶ。"""
    img = _rgb(base((244, 244, 246), (228, 228, 232)))
    wood_floor(img, FLOOR, col=(220, 220, 224), line=(206, 206, 210))
    d = _d(img)
    for k in range(6):
        d.rectangle([k * 340, 40, k * 340 + 30, 70], fill=(250, 250, 236))
    rnd = random.Random(11)
    for row, y in enumerate((360, 560, 760)):
        d.rectangle([60, y, 1860, y + 26], fill=(200, 200, 206), outline=(160, 160, 166), width=2)
        for k in range(14):
            x = 120 + k * 128 + (row % 2) * 30
            if sumaho:
                _sumaho(d, x, y, 0.85, col=rnd.choice([(30, 30, 34), (220, 220, 226), (60, 80, 130)]))
            else:
                _keitai(d, x, y, 0.55, col=rnd.choice([(220, 60, 90), (60, 120, 220), (240, 240, 244), (40, 40, 44), (240, 170, 40)]))
            _price(d, x, y + 28)
    return img


def machi():
    """駅前の交差点。ビルの壁に大きな画面、横断歩道に人の後ろ姿。"""
    img = vgrad((W, H), (180, 206, 230), (220, 226, 230))
    d = _d(img)
    rnd = random.Random(5)
    for k in range(9):
        x0 = k * 220 - 20
        top = 120 + rnd.randint(0, 220)
        d.rectangle([x0, top, x0 + 200, 700], fill=rnd.choice([(150, 156, 170), (176, 170, 160), (130, 140, 156)]))
        for r in range((700 - top) // 60):
            for c in range(3):
                d.rectangle([x0 + 20 + c * 60, top + 20 + r * 60, x0 + 56 + c * 60, top + 50 + r * 60], fill=(210, 220, 232))
    d.rectangle([700, 180, 1220, 460], fill=(30, 30, 36), outline=(60, 60, 66), width=8)       # ビルの画面
    d.rectangle([720, 200, 1200, 440], fill=(60, 140, 220))
    d.rectangle([0, 700, W, H], fill=(90, 92, 98))
    for k in range(12):                                                                 # 横断歩道
        d.rectangle([k * 170, 760, k * 170 + 100, 900], fill=(236, 236, 236))
    _person_line(d, 140, 1000, 6, 1.0)
    _person_line(d, 1260, 1000, 5, 1.0)
    return img


# ---------------------------------------------------------------- シャープの亀山工場
def ekisho_kojo(kara=False):
    """液晶パネルの工場の中。白い天井と床、ローラーの上を大きなガラスの板が流れ、ロボットの腕が持ち上げる。
    kara は板が無く灯りが落ちている。"""
    img = vgrad((W, H), (240, 242, 244) if not kara else (170, 172, 176), (226, 228, 232) if not kara else (150, 152, 156))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(214, 218, 222) if not kara else (150, 152, 158))
    for k in range(8):
        d.rectangle([k * 260 + 30, 40, k * 260 + 200, 70], fill=(250, 250, 250) if not kara else (120, 120, 124))
    d.rectangle([0, 600, W, 640], fill=(170, 176, 184))                              # ローラーの台
    for k in range(40):
        d.ellipse([k * 50, 590, k * 50 + 20, 610], fill=(120, 126, 136))
    if not kara:
        for x in (120, 1340):                                                          # 流れるガラス板
            d.polygon([(x, 590), (x + 480, 590), (x + 440, 540), (x + 40, 540)], fill=(200, 226, 240, 200), outline=(150, 180, 200))
        d.rectangle([860, 240, 920, 600], fill=(240, 160, 40))                         # ロボットの腕
        d.line([(890, 260), (1100, 200)], fill=(240, 160, 40), width=40)
        d.line([(1100, 200), (1100, 330)], fill=(240, 160, 40), width=30)
        d.polygon([(880, 360), (1320, 360), (1290, 320), (910, 320)], fill=(200, 226, 240, 220), outline=(150, 180, 200))  # 持ち上げた大きな板
    return img


def kojo_soto(umi=False):
    """大きな工場の外観。白く長い建物と駐車場。umi は奥が海（湾岸の工場）、そうでなければ緑の丘。"""
    img = vgrad((W, H), (160, 200, 236), (220, 232, 240))
    d = _d(img)
    if umi:
        d.rectangle([0, 400, W, 470], fill=(70, 120, 170))
    else:
        d.ellipse([-200, 300, 900, 700], fill=(110, 160, 100))
        d.ellipse([700, 330, 2200, 760], fill=(96, 148, 90))
    d.rectangle([160, 300, 1760, 640], fill=(244, 244, 246), outline=(170, 172, 176), width=6)
    d.rectangle([160, 300, 1760, 340], fill=(200, 204, 210))
    for k in range(12):
        d.rectangle([220 + k * 128, 420, 300 + k * 128, 460], fill=(150, 176, 200))
    d.rectangle([0, 640, W, H], fill=(120, 124, 128))
    for k in range(14):
        d.line([(k * 140, 700), (k * 140, 820)], fill=(240, 240, 240), width=4)
    return img


def tv_uriba(nesage=False):
    """量販店のテレビ売り場。壁一面の薄型テレビ。nesage は赤い値札が並ぶ。"""
    img = _rgb(base((236, 236, 240), (220, 220, 226)))
    wood_floor(img, FLOOR, col=(214, 214, 220), line=(200, 200, 206))
    d = _d(img)
    cols = [(40, 110, 180), (200, 90, 60), (60, 160, 100), (230, 180, 60), (120, 80, 170)]
    for r, (y0, y1) in enumerate(((90, 330), (380, 620))):
        for k in range(5):
            x0 = 80 + k * 360
            _flat_tv(d, x0, y0, x0 + 320, y1, screen=cols[(k + r) % 5])
            _price(d, x0 + 160, y1 + 6, red=nesage)
    d.rectangle([0, 700, W, 740], fill=(200, 200, 206))
    return img


def kenkyujo():
    """研究室。実験台の上に試作のパネルと顕微鏡、壁ぎわに測定器。"""
    img = _rgb(base((236, 238, 236), (222, 224, 222)))
    wood_floor(img, FLOOR, col=(180, 184, 186), line=(166, 170, 172))
    d = _d(img)
    for k in range(3):                                                                  # 測定器の棚
        x = 120 + k * 200
        d.rectangle([x, 220, x + 170, 640], fill=(214, 214, 210), outline=(150, 150, 146), width=3)
        for r in range(4):
            d.rectangle([x + 16, 250 + r * 92, x + 154, 320 + r * 92], fill=(60, 66, 72))
            d.ellipse([x + 120, 270 + r * 92, x + 140, 290 + r * 92], fill=(80, 220, 120))
    d.rectangle([760, 600, 1840, 640], fill=(230, 230, 226), outline=(160, 160, 156), width=3)   # 実験台
    d.rectangle([800, 640, 830, FLOOR], fill=(150, 150, 146))
    d.rectangle([1770, 640, 1800, FLOOR], fill=(150, 150, 146))
    d.rectangle([860, 470, 1100, 598], fill=(30, 30, 34), outline=(90, 90, 96), width=4)        # 試作パネル
    d.rectangle([874, 484, 1086, 584], fill=(80, 170, 220))
    d.rectangle([1300, 580, 1420, 598], fill=(60, 60, 66))                                       # 顕微鏡
    d.rectangle([1350, 440, 1380, 580], fill=(70, 70, 76))
    d.line([(1365, 440), (1330, 380)], fill=(70, 70, 76), width=22)
    _papers(d, 1520, 590, n=3)
    return img


def choin():
    """調印式の会場。白い布の長机に2つの席、後ろに無地の幕、手前にカメラの列。"""
    img = _sega_kaiken()
    d = _d(img)
    d.rectangle([0, 0, W, 560], fill=(150, 30, 40))                                  # 幕の色を変える
    for k in range(10):
        d.line([(k * 200, 0), (k * 200 + 40, 560)], fill=(130, 24, 34), width=8)
    for x in (560, 960, 1360):                                                         # マイクを消して書類に
        d.rectangle([x - 70, 460, x + 30, 556], fill=(150, 30, 40))
    for x in (700, 1220):
        d.rectangle([x - 80, 540, x + 80, 560], fill=(250, 250, 246), outline=(160, 160, 156), width=2)
        d.line([(x + 40, 548), (x + 100, 520)], fill=(30, 30, 34), width=6)
    return img


# ---------------------------------------------------------------- ニコンの露光装置
def _roko_sochi(d, x, y, s=1.0):
    """露光装置（左下が x, y）。白い大きな箱、のぞき窓、横に操作の画面。"""
    w, h = 620 * s, 460 * s
    d.rectangle([x, y - h, x + w, y], fill=(244, 244, 240), outline=(150, 150, 146), width=4)
    d.rectangle([x, y - h, x + w, y - h + 40 * s], fill=(210, 212, 214))
    d.rectangle([x + 60 * s, y - h + 90 * s, x + 340 * s, y - h + 260 * s], fill=(60, 66, 74), outline=(120, 120, 126), width=4)   # 窓
    d.ellipse([x + 150 * s, y - h + 130 * s, x + 250 * s, y - h + 230 * s], fill=(150, 156, 176), outline=(210, 214, 226), width=3)  # 中のウエハー
    d.rectangle([x + 400 * s, y - h + 100 * s, x + 560 * s, y - h + 200 * s], fill=(30, 34, 40))
    d.rectangle([x + 410 * s, y - h + 110 * s, x + 550 * s, y - h + 190 * s], fill=(60, 140, 200))
    d.line([(x + 30 * s, y - 60 * s), (x + w - 30 * s, y - 60 * s)], fill=(200, 200, 196), width=4)


def roko_shitsu(kara=False):
    """露光装置が並ぶクリーンルーム。天井から黄色い灯り（感光させないため）。kara は装置が1台だけで奥が空いている。"""
    img = vgrad((W, H), (244, 232, 160), (232, 220, 150))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(214, 206, 160))
    for k in range(20):
        d.line([(k * 100, FLOOR), (k * 100, H)], fill=(196, 188, 146), width=2)
    for k in range(7):
        d.rectangle([k * 280 + 40, 30, k * 280 + 220, 60], fill=(255, 246, 170))
    _roko_sochi(d, 120, FLOOR, 1.0)
    if not kara:
        _roko_sochi(d, 1180, FLOOR, 1.0)
    return img


def kogaku_jikken():
    """光学の実験室。暗い部屋で、台の上にレンズを並べ、光の線が通る。"""
    img = vgrad((W, H), (34, 38, 50), (50, 54, 66))
    d = _d(img)
    d.rectangle([0, 620, W, 680], fill=(120, 124, 132), outline=(80, 84, 90), width=4)       # 光学台
    d.rectangle([0, 680, W, H], fill=(60, 62, 70))
    d.line([(160, 560), (1760, 560)], fill=(120, 200, 255), width=6)                         # 光の線
    _glow(img, 160, 560, 90, (140, 210, 255), 140)
    d = _d(img)
    for x in (520, 880, 1240, 1560):
        d.rectangle([x - 8, 560, x + 8, 620], fill=(150, 150, 156))
        d.ellipse([x - 26, 470, x + 26, 650], fill=(190, 220, 240, 170), outline=(220, 236, 250), width=3)
    d.rectangle([100, 520, 220, 620], fill=(70, 74, 82), outline=(110, 114, 122), width=3)    # 光源
    return img


def lens_kenma():
    """レンズを磨く工場。並んだ研磨の機械と、手元の大きなレンズ。"""
    img = _rgb(base((226, 228, 226), (212, 214, 212)))
    wood_floor(img, FLOOR, col=(170, 174, 176), line=(156, 160, 162))
    d = _d(img)
    for k in range(6):
        x = 100 + k * 300
        d.rectangle([x, 420, x + 220, FLOOR], fill=(90, 120, 110), outline=(60, 80, 74), width=4)
        d.ellipse([x + 40, 360, x + 180, 440], fill=(180, 190, 200), outline=(120, 130, 140), width=4)
        d.ellipse([x + 80, 380, x + 140, 420], fill=(200, 226, 240))
    d.rectangle([700, 640, 1220, 690], fill=(200, 196, 186), outline=(150, 146, 136), width=3)
    d.ellipse([860, 570, 1060, 650], fill=(200, 226, 240, 200), outline=(150, 180, 200), width=4)
    return img


def tenjikai():
    """展示会の会場。区切られた出展の場所、台の上の装置の模型、天井の梁。"""
    img = vgrad((W, H), (60, 66, 80), (90, 96, 110))
    d = _d(img)
    for k in range(12):
        d.line([(k * 180, 0), (k * 180 + 90, 160)], fill=(110, 116, 130), width=6)
    d.rectangle([0, FLOOR, W, H], fill=(150, 140, 130))
    for k, col in enumerate([(40, 90, 170), (200, 60, 50), (60, 140, 90)]):
        x = 60 + k * 620
        d.rectangle([x, 220, x + 560, 620], fill=(244, 244, 246), outline=col, width=10)
        d.rectangle([x, 220, x + 560, 270], fill=col)
        d.rectangle([x + 140, 460, x + 420, 620], fill=(230, 230, 226), outline=(150, 150, 146), width=3)
        d.rectangle([x + 200, 380, x + 360, 460], fill=(214, 214, 210), outline=(150, 150, 146), width=3)
    _person_line(d, 200, 1000, 5, 1.0)
    _person_line(d, 1300, 1000, 4, 1.0)
    return img


def kaigai_kojo():
    """海外の会社の工場（外観）。平たい建物と並木、低い空。"""
    img = vgrad((W, H), (170, 186, 206), (214, 220, 226))
    d = _d(img)
    d.rectangle([0, 620, W, H], fill=(110, 150, 96))
    d.rectangle([200, 300, 1720, 640], fill=(220, 224, 230), outline=(140, 146, 156), width=6)
    d.rectangle([200, 300, 1720, 360], fill=(60, 80, 120))
    for k in range(10):
        d.rectangle([260 + k * 145, 440, 360 + k * 145, 560], fill=(150, 180, 210))
    for k in range(10):                                                                 # 並木
        x = 80 + k * 200
        d.rectangle([x - 8, 640, x + 8, 760], fill=(110, 80, 60))
        d.ellipse([x - 60, 560, x + 60, 680], fill=(70, 120, 70))
    return img


def wafer():
    """ウエハーの大写し。格子に並んだチップ。"""
    img = vgrad((W, H), (20, 26, 40), (36, 44, 60))
    d = _d(img)
    cx, cy, r = 960, 520, 420
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 156, 176), outline=(210, 214, 226), width=8)
    for i in range(-6, 7):
        for j in range(-6, 7):
            x, y = cx + i * 64, cy + j * 64
            if (x - cx) ** 2 + (y - cy) ** 2 > (r - 46) ** 2:
                continue
            d.rectangle([x - 27, y - 27, x + 27, y + 27], fill=[(170, 140, 200), (120, 170, 210), (200, 170, 120)][(i + j) % 3])
    return img


# ---------------------------------------------------------------- JALの破綻と稲盛和夫
def kuko_lobby(sukunai=False):
    """空港の出発ロビー。手荷物を預ける長いカウンター、天井の案内板（文字なし）、窓の外に飛行機。
    sukunai は人がまばら。"""
    img = vgrad((W, H), (226, 230, 236), (210, 214, 222))
    d = _d(img)
    d.rectangle([0, 80, W, 400], fill=(170, 200, 230))                                 # 大きな窓
    for k in range(9):
        d.line([(k * 240, 80), (k * 240, 400)], fill=(140, 146, 156), width=8)
    _plane_side(d, 1500, 330, 0.55)
    for k in range(4):                                                                 # 案内板
        d.rectangle([140 + k * 440, 420, 500 + k * 440, 480], fill=(30, 34, 46))
        for r in range(2):
            d.line([(160 + k * 440, 438 + r * 22), (440 + k * 440, 438 + r * 22)], fill=(250, 210, 80), width=6)
    d.rectangle([0, 560, W, 660], fill=(240, 240, 244), outline=(180, 180, 186), width=4)   # カウンター
    d.rectangle([0, 520, W, 560], fill=(200, 40, 50))
    d.rectangle([0, FLOOR - 120, W, H], fill=(200, 196, 190))
    if not sukunai:
        _person_line(d, 100, 1010, 8, 1.0)
        _person_line(d, 1100, 1010, 7, 1.0)
    return img


def kinai():
    """旅客機の客室。通路の両側に座席、上に荷物の棚、奥に向かって狭まる。"""
    img = vgrad((W, H), (236, 234, 228), (220, 218, 212))
    d = _d(img)
    cx = 960
    d.polygon([(0, 140), (W, 140), (cx + 180, 400), (cx - 180, 400)], fill=(230, 228, 220))       # 天井と棚
    d.polygon([(0, 140), (cx - 180, 400), (cx - 180, 460), (0, 330)], fill=(214, 210, 200), outline=(170, 166, 156))
    d.polygon([(W, 140), (cx + 180, 400), (cx + 180, 460), (W, 330)], fill=(214, 210, 200), outline=(170, 166, 156))
    d.polygon([(cx - 140, 400), (cx + 140, 400), (cx + 140, 640), (cx - 140, 640)], fill=(200, 200, 196))  # 奥の壁
    d.polygon([(cx - 300, H), (cx + 300, H), (cx + 140, 640), (cx - 140, 640)], fill=(70, 80, 120))  # 通路
    for side in (-1, 1):
        for k in range(6):
            t = k / 6
            x_in = cx + side * (160 + 260 * (1 - t) * 0 + 140 * (1 - t))
            w = 200 * (1 - t) + 60
            h = 320 * (1 - t) + 110
            y_b = 1080 - (1080 - 640) * t
            x0, x1 = (x_in - w, x_in) if side < 0 else (x_in, x_in + w)
            d.rounded_rectangle([x0 - side * 0, y_b - h, x1, y_b - 10], radius=int(16 * (1 - t) + 4),
                                fill=(40, 60, 110), outline=(26, 40, 80), width=3)
    for side in (-1, 1):                                                               # 窓
        for k in range(5):
            x = cx + side * (900 - k * 140)
            d.rounded_rectangle([x - 22, 330 + k * 14, x + 22, 390 + k * 14], radius=14, fill=(170, 206, 236))
    return img


def kakunoko():
    """整備の格納庫。高い天井の鉄骨、旅客機の前半分、足場と工具の台。"""
    img = vgrad((W, H), (150, 156, 164), (180, 184, 190))
    d = _d(img)
    for k in range(10):
        d.line([(k * 220, 0), (k * 220 + 110, 140)], fill=(110, 116, 124), width=10)
        d.line([(k * 220 + 220, 0), (k * 220 + 110, 140)], fill=(110, 116, 124), width=10)
    d.rectangle([0, 140, W, 160], fill=(110, 116, 124))
    for k in range(6):
        d.rectangle([k * 340 + 80, 170, k * 340 + 240, 200], fill=(250, 250, 236))
    d.rectangle([0, FLOOR, W, H], fill=(190, 190, 186))
    d.line([(0, FLOOR + 40), (W, FLOOR + 40)], fill=(240, 200, 40), width=8)
    _plane_side(d, 1700, 700, 1.1)
    d.rectangle([300, 520, 700, 540], fill=(240, 180, 40))                              # 足場
    for x in (320, 680):
        d.rectangle([x - 8, 540, x + 8, FLOOR], fill=(240, 180, 40))
    d.rectangle([1600, 760, 1880, 800], fill=(200, 40, 40), outline=(120, 20, 20), width=3)   # 工具の台
    d.rectangle([1620, 800, 1640, FLOOR], fill=(80, 80, 86))
    d.rectangle([1840, 800, 1860, FLOOR], fill=(80, 80, 86))
    return img


def kenshu():
    """研修の部屋。白板の前に机が並び、机に冊子。"""
    img = _rgb(base((232, 232, 226), (218, 218, 212)))
    wood_floor(img, FLOOR, col=(160, 156, 150), line=(146, 142, 136))
    d = _d(img)
    d.rectangle([460, 110, 1460, 440], fill=(250, 250, 248), outline=(140, 140, 146), width=8)
    for k in range(5):
        d.line([(520, 160 + k * 56), (980 + (k % 2) * 300, 160 + k * 56)], fill=(40, 60, 140), width=6)
    for r, y in enumerate((620, 760)):
        for k in range(4):
            x0 = 120 + k * 450 + r * 40
            d.rectangle([x0, y, x0 + 380, y + 24], fill=(214, 200, 176), outline=(160, 146, 120), width=2)
            d.rectangle([x0 + 40, y - 14, x0 + 130, y], fill=(250, 250, 244), outline=(170, 160, 140))
            d.rectangle([x0 + 220, y - 14, x0 + 310, y], fill=(250, 250, 244), outline=(170, 160, 140))
    return img


def konpa():
    """宴会の座敷。畳に長い座卓、瓶とコップ、鍋。"""
    img = _rgb(base((226, 216, 196), (210, 200, 180)))
    tatami_floor(img, int(H * 0.66))
    d = _d(img)
    for k in range(4):                                                                  # ふすま
        d.rectangle([140 + k * 420, 120, 540 + k * 420, 640], fill=(240, 232, 214), outline=(140, 116, 86), width=6)
        d.ellipse([320 + k * 420, 360, 360 + k * 420, 400], outline=(140, 116, 86), width=4)
    d.rectangle([200, 720, 1720, 790], fill=(120, 80, 50), outline=(80, 52, 30), width=4)    # 座卓
    for k in range(6):
        x = 300 + k * 240
        d.rectangle([x, 610, x + 36, 720], fill=(110, 70, 30))                            # 瓶
        d.rectangle([x + 8, 590, x + 28, 612], fill=(110, 70, 30))
        d.rectangle([x + 70, 670, x + 110, 720], fill=(250, 230, 150, 200), outline=(200, 190, 160))  # コップ
    d.ellipse([880, 660, 1040, 730], fill=(60, 60, 66))                                     # 鍋
    return img


def seramikku():
    """セラミックの部品工場。大きな窯と、台の上に並んだ白い小さな部品。"""
    img = _rgb(base((222, 218, 210), (206, 202, 194)))
    wood_floor(img, FLOOR, col=(150, 144, 136), line=(136, 130, 122))
    d = _d(img)
    d.rectangle([120, 240, 760, FLOOR], fill=(150, 140, 130), outline=(90, 84, 76), width=6)   # 窯
    d.rectangle([260, 420, 620, 700], fill=(60, 40, 30))
    _glow(img, 440, 560, 160, (255, 150, 60), 140)
    d = _d(img)
    d.rectangle([980, 620, 1820, 660], fill=(200, 196, 186), outline=(150, 146, 136), width=3)
    for r in range(3):
        for k in range(16):
            d.rectangle([1010 + k * 50, 590 - r * 26, 1040 + k * 50, 610 - r * 26], fill=(250, 250, 246), outline=(200, 200, 196))
    return img


LOCATIONS = {
    # ドコモとiモード
    "dc_heya": lambda: heya3("keitai"), "dc_jimusho": jimusho90, "dc_jimusho_yoru": lambda: jimusho90(yoru=True),
    "dc_server": server_shitsu, "dc_server_akai": lambda: server_shitsu(akai=True), "dc_shop": keitai_shop,
    "dc_densha": densha, "dc_uriba": keitai_uriba, "dc_uriba_sumaho": lambda: keitai_uriba(sumaho=True),
    "dc_machi": machi, "dc_kaiken": _sega_kaiken, "dc_kaigi": kaigi, "dc_kaigi_akaji": lambda: kaigi(akaji=True),
    "dc_kaigi_up": lambda: kaigi(up=True), "dc_yakuin": lambda: yakuin(), "dc_gendai": _sega_gendai,
    # シャープの亀山工場
    "sh_heya": lambda: heya3("tv"), "sh_kojo": ekisho_kojo, "sh_kojo_kara": lambda: ekisho_kojo(kara=True),
    "sh_kojo_soto": kojo_soto, "sh_sakai_soto": lambda: kojo_soto(umi=True), "sh_ryohan": tv_uriba,
    "sh_ryohan_nesage": lambda: tv_uriba(nesage=True), "sh_kenkyujo": kenkyujo, "sh_choin": choin,
    "sh_kaiken": _sega_kaiken, "sh_kaigi": kaigi, "sh_kaigi_akaji": lambda: kaigi(akaji=True),
    "sh_kaigi_up": lambda: kaigi(up=True), "sh_yakuin": lambda: yakuin(), "sh_gendai": _sega_gendai,
    "sh_ooya": lambda: heya2("none"),
    # ニコンの露光装置
    "nk_heya": lambda: heya3("sumaho"), "nk_roko": roko_shitsu, "nk_roko_kara": lambda: roko_shitsu(kara=True),
    "nk_jikken": kogaku_jikken, "nk_kenma": lens_kenma, "nk_fab": _sega_fab, "nk_wafer": wafer,
    "nk_tenji": tenjikai, "nk_kaigai": kaigai_kojo, "nk_kaiken": _sega_kaiken, "nk_kaigi": kaigi,
    "nk_kaigi_akaji": lambda: kaigi(akaji=True), "nk_kaigi_up": lambda: kaigi(up=True),
    "nk_yakuin": lambda: yakuin(), "nk_gendai": _sega_gendai, "nk_houtei": _sogo_saibansho,
    # JALの破綻と稲盛和夫
    "jl_heya": lambda: heya3("ryoko"), "jl_kuko": kuko_lobby, "jl_kuko_sukunai": lambda: kuko_lobby(sukunai=True),
    "jl_kuko_yoru": kuko_yoru, "jl_kinai": kinai, "jl_kakunoko": kakunoko, "jl_kenshu": kenshu, "jl_konpa": konpa,
    "jl_seramikku": seramikku, "jl_houtei": _sogo_saibansho, "jl_shoken": shoken, "jl_kaiken": _sega_kaiken,
    "jl_kaigi": kaigi, "jl_kaigi_akaji": lambda: kaigi(akaji=True), "jl_kaigi_up": lambda: kaigi(up=True),
    "jl_yakuin": lambda: yakuin(), "jl_gendai": _sega_gendai,
}

# 年号カード（台本ができてから埋める）。接頭辞ごとに "dc_card_1999" のように作る
CARDS = {"dc": ["1999", "2008", "2020", "2023", "2026"], "sh": ["1998", "2003", "2004", "2005", "2006", "2007", "2009", "2012", "2016", "2024", "2025", "2026"], "nk": ["1972", "2001", "2002", "2014", "2016", "2026"], "jl": ["1963", "1984", "2009", "2010", "2011", "2012", "2022"]}


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
