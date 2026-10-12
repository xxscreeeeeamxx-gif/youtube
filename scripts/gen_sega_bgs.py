#!/usr/bin/env python3
"""セガとドリームキャストの回（88_ドリームキャストの撤退 / slug=sega-dreamcast）の背景を生成する。

方針はファミコン回（gen_famicom_bgs.py）と同じで、部品もそこから借りる。
実在の会社の商標（ロゴ・社名の文字・渦巻きマーク）は描かない。ゲーム機は白い箱に丸いふた、
相手のゲーム機は黒い箱、と形と色だけで分かるようにし、実在の機械やキャラクターの絵柄は写さない。
差し替え用（_urikire・_wafer・_akaji・_kowareta など）は元の絵を呼んで要素を足し、
切り替わりの差が一目で分かるようにする（SKILL.md「場面の途中で背景を差し替える」）。

実行: PYTHONPATH=. python scripts/gen_sega_bgs.py [名前...]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import H, OUT, W, base, glow, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import (  # noqa: E402
    _board, _boxes, _crt, _font, _papers, _phone, _table, _window, year_card,
)

FLOOR = int(H * 0.86)
INK = (60, 60, 66)
DC_WHITE = (238, 238, 234)
DC_GRAY = (196, 198, 200)
PS_BLACK = (34, 34, 40)


def _d(img):
    return ImageDraw.Draw(img, "RGBA")


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


# ---------------------------------------------------------------- 部品
def _glow(img, cx, cy, r, color, alpha=110):
    """gen_drama_bgs.glow は RGBA の画にしか描けないので、いったん RGBA にして描き戻す。"""
    rgba = img.convert("RGBA")
    glow(rgba, cx, cy, r, color, alpha)
    img.paste(rgba.convert("RGB"))


def _dc(d, x, y, s=1.0):
    """白いゲーム機（左上が x, y）。四角い本体に丸いふた、前に4つの差し込み口。"""
    w, h = 300 * s, 110 * s
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(26 * s), fill=DC_WHITE, outline=(170, 172, 174), width=3)
    d.ellipse([x + w * 0.22, y - h * 0.18, x + w * 0.78, y + h * 0.62], fill=(226, 226, 222), outline=(176, 178, 180), width=3)
    d.ellipse([x + w * 0.42, y + h * 0.10, x + w * 0.58, y + h * 0.34], fill=(206, 206, 202))
    for k in range(4):
        px = x + w * (0.14 + k * 0.215)
        d.rounded_rectangle([px, y + h * 0.72, px + w * 0.12, y + h * 0.88], radius=4, fill=(150, 152, 156))


def _dc_box(d, x, y, s=1.0, col=(240, 240, 236)):
    """白い箱（左上が x, y）。"""
    d.rectangle([x, y, x + 140 * s, y + 100 * s], fill=col, outline=(160, 160, 160), width=2)
    d.rectangle([x + 10 * s, y + 10 * s, x + 130 * s, y + 46 * s], fill=(214, 220, 228))
    d.ellipse([x + 52 * s, y + 52 * s, x + 88 * s, y + 88 * s], fill=(222, 120, 60))


def _ps_box(d, x, y, s=1.0):
    """黒い箱（相手のゲーム機）。"""
    d.rectangle([x, y, x + 140 * s, y + 100 * s], fill=PS_BLACK, outline=(70, 70, 80), width=2)
    d.rectangle([x + 10 * s, y + 10 * s, x + 130 * s, y + 40 * s], fill=(50, 70, 140))


def _flat_tv(d, x0, y0, x1, y1, screen=(40, 80, 150)):
    d.rectangle([x0, y0, x1, y1], fill=(28, 28, 32), outline=(18, 18, 22), width=10)
    d.rectangle([x0 + 18, y0 + 18, x1 - 18, y1 - 18], fill=screen)
    return x0 + 18, y0 + 18, x1 - 18, y1 - 18


def _person_line(d, x0, y, n, s=1.0, cols=None):
    """行列の人影（後ろ姿の簡略形）。"""
    cols = cols or [(70, 74, 90), (90, 70, 66), (60, 84, 70), (100, 96, 86)]
    for k in range(n):
        x = x0 + k * 70 * s
        c = cols[k % len(cols)]
        d.ellipse([x, y - 150 * s, x + 46 * s, y - 104 * s], fill=(40, 34, 30))
        d.rounded_rectangle([x - 10 * s, y - 104 * s, x + 56 * s, y], radius=int(18 * s), fill=c)


def _chart(d, x0, y0, x1, y1, pts, col=(220, 60, 50), grid=(200, 200, 196)):
    d.rectangle([x0, y0, x1, y1], fill=(250, 250, 246), outline=(120, 120, 116), width=4)
    for k in range(1, 4):
        y = y0 + (y1 - y0) * k / 4
        d.line([(x0 + 10, y), (x1 - 10, y)], fill=grid, width=2)
    xs = [x0 + 30 + (x1 - x0 - 60) * i / (len(pts) - 1) for i in range(len(pts))]
    ys = [y1 - 30 - (y1 - y0 - 60) * p for p in pts]
    d.line(list(zip(xs, ys)), fill=col, width=10)
    for x, y in zip(xs, ys):
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col)


# ---------------------------------------------------------------- 今の部屋
def heya():
    """今の部屋。薄型テレビと押し入れ。"""
    img = _rgb(base((230, 228, 220), (214, 212, 204)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([80, 120, 560, 800], fill=(214, 200, 170), outline=(120, 96, 70), width=8)
    d.line([(80, 440), (560, 440)], fill=(120, 96, 70), width=8)
    _boxes(d, 110, 430, n=3, rows=2)
    _flat_tv(d, 760, 230, 1180, 490)
    d.rectangle([720, 560, 1220, 600], fill=(120, 90, 64))
    d.rectangle([740, 600, 1200, 700], fill=(140, 106, 76))
    return img


def heya_dc():
    """同じ部屋。床に白いゲーム機が出ている。"""
    img = heya()
    d = _d(img)
    _dc(d, 820, 760, 1.0)
    d.line([(1120, 820), (1300, 900)], fill=(60, 60, 64), width=6)
    d.rounded_rectangle([1280, 880, 1420, 950], radius=20, fill=DC_WHITE, outline=(160, 160, 160), width=3)
    return img


# ---------------------------------------------------------------- 1970〜80年代
def kaisha70():
    """1970年代の事務所。スチール机と黒電話、窓。"""
    img = _rgb(base((222, 216, 200), (206, 200, 186)))
    wood_floor(img, FLOOR, col=(120, 110, 96), line=(100, 92, 80))
    d = _d(img)
    _window(d, 760, 120, 1160, 400, sky=(196, 212, 222))
    for k, x in enumerate((420, 1260)):
        d.rectangle([x, 640, x + 360, 680], fill=(150, 156, 160))
        d.rectangle([x + 10, 680, x + 350, 800], fill=(136, 142, 146))
        _papers(d, x + 40, 630, n=2)
        _phone(d, x + 220, 560, 0.6)
    d.rectangle([1580, 300, 1860, 640], fill=(156, 160, 164), outline=(110, 114, 118), width=4)  # キャビネット
    for k in range(4):
        d.line([(1590, 380 + k * 80), (1850, 380 + k * 80)], fill=(110, 114, 118), width=3)
    return img


def gamecenter():
    """1970〜80年代のゲームセンター。暗い店内に筐体が並び、画面が光る。"""
    img = _rgb(base((30, 26, 44), (44, 38, 60)))
    wood_floor(img, FLOOR, col=(60, 40, 56), line=(48, 32, 46))
    d = _d(img)
    cols = [(40, 60, 130), (130, 40, 50), (40, 110, 70), (120, 90, 30)]
    for k in range(6):
        x = 60 + k * 310
        d.polygon([(x, 220), (x + 220, 220), (x + 240, 380), (x + 240, FLOOR), (x - 20, FLOOR), (x - 20, 380)], fill=cols[k % 4])
        d.rectangle([x + 10, 260, x + 210, 480], fill=(10, 10, 16))
        _glow(img, x + 110, 370, 140, (120, 200, 255), 60)
        d = _d(img)
        for j in range(5):
            yy = 290 + j * 36
            d.rectangle([x + 30 + (j * 23) % 120, yy, x + 70 + (j * 23) % 120, yy + 14], fill=(240, 220, 80))
        d.rectangle([x - 10, 520, x + 230, 580], fill=(50, 50, 60))
        d.ellipse([x + 40, 528, x + 80, 568], fill=(220, 60, 60))
    return img


def kaihatsu(night=False, mega=False):
    """ハード開発室。基板・オシロスコープ・ブラウン管。night は夜、mega は机に黒い本体とトロフィー。"""
    img = _rgb(base((40, 44, 60), (60, 62, 76)) if night else base((222, 224, 220), (204, 206, 202)))
    wood_floor(img, FLOOR, col=(60, 58, 64) if night else (118, 114, 106), line=(48, 46, 52) if night else (98, 94, 88))
    d = _d(img)
    _window(d, 760, 110, 1160, 380, sky=(20, 24, 50) if night else (196, 214, 228))
    _table(d, 560, 1500, 640, col=(90, 86, 80) if night else (126, 122, 112))
    d.rectangle([1260, 520, 1440, 640], fill=(90, 96, 100))                     # オシロスコープ
    d.rectangle([1278, 538, 1400, 622], fill=(40, 70, 50))
    d.line([(1284, 590), (1310, 556), (1336, 604), (1362, 560), (1394, 590)], fill=(120, 240, 150), width=3)
    _crt(d, 600, 420, 260, 210, screen=(30, 50, 80) if night else (40, 90, 140))
    if mega:
        d.rounded_rectangle([900, 560, 1180, 640], radius=10, fill=(30, 30, 34), outline=(80, 80, 86), width=3)
        d.ellipse([1000, 570, 1080, 620], fill=(60, 60, 66))
        d.rectangle([1200, 470, 1240, 640], fill=(200, 160, 40))                # トロフィー
        d.polygon([(1180, 430), (1260, 430), (1240, 480), (1200, 480)], fill=(230, 190, 60))
    else:
        _board(d, 900, 520, 0.9)
        _board(d, 1080, 548, 0.6)
    if night:
        d.ellipse([1300, 380, 1400, 430], fill=(250, 230, 150))
        _glow(img, 1350, 440, 260, (255, 230, 150), 70)
    for x in (300, 1560):
        d = _d(img)
        d.rectangle([x, 640, x + 90, 660], fill=(70, 70, 76))
        d.rectangle([x + 70, 540, x + 90, 660], fill=(70, 70, 76))
        d.rectangle([x + 40, 660, x + 50, 780], fill=(60, 60, 64))
    return img


def kaihatsu_yoru():
    return kaihatsu(night=True)


def kaihatsu_mega():
    return kaihatsu(mega=True)


# ---------------------------------------------------------------- 会社の上の階
def yakuinkai():
    """役員会議室。長い机と椅子、壁に2枚の図（左右の案）。"""
    img = _rgb(base((206, 200, 190), (190, 184, 174)))
    wood_floor(img, FLOOR, col=(96, 74, 58), line=(80, 60, 46))
    d = _d(img)
    for k, x in enumerate((560, 1040)):
        d.rectangle([x, 150, x + 360, 400], fill=(248, 248, 244), outline=(110, 110, 106), width=5)
        col = (60, 100, 170) if k == 0 else (170, 70, 60)
        for j in range(3):
            d.rectangle([x + 40 + j * 110, 230, x + 120 + j * 110, 330], outline=col, width=6)
        d.line([(x + 120, 280), (x + 150, 280)], fill=col, width=5)
        d.line([(x + 230, 280), (x + 260, 280)], fill=col, width=5)
    d.rectangle([380, 640, 1540, 700], fill=(110, 80, 56))                      # 長い机
    for k in range(6):
        x = 440 + k * 190
        d.rectangle([x, 560, x + 90, 640], fill=(60, 50, 46))
    return img


def kaichoshitsu(net=False):
    """会長室。大きな机と41インチのテレビ。net=True はテレビにウェブページ。"""
    img = _rgb(base((212, 204, 188), (196, 188, 172)))
    wood_floor(img, FLOOR, col=(98, 74, 56), line=(82, 60, 46))
    d = _d(img)
    _window(d, 1360, 120, 1820, 420, sky=(200, 214, 226))
    d.polygon([(1370, 400), (1480, 330), (1560, 380), (1700, 300), (1810, 400)], fill=(150, 156, 170))  # ビル街
    sx0, sy0, sx1, sy1 = _flat_tv(d, 140, 200, 760, 560, screen=(30, 40, 60))
    if net:
        d.rectangle([sx0, sy0, sx1, sy0 + 40], fill=(200, 204, 210))           # ブラウザの枠
        d.rectangle([sx0 + 60, sy0 + 10, sx1 - 20, sy0 + 30], fill=(250, 250, 250))
        d.rectangle([sx0, sy0 + 40, sx1, sy1], fill=(250, 250, 246))
        d.rectangle([sx0 + 30, sy0 + 70, sx0 + 260, sy0 + 200], fill=(150, 190, 220))
        for k in range(6):
            d.rectangle([sx0 + 290, sy0 + 76 + k * 34, sx1 - 40 - (k % 3) * 60, sy0 + 90 + k * 34], fill=(150, 150, 156))
        d.rectangle([sx0 + 30, sy0 + 230, sx0 + 200, sy0 + 250], fill=(60, 90, 200))
    d.rectangle([380, 600, 520, 640], fill=(80, 60, 44))                       # テレビ台
    d.rectangle([800, 640, 1500, 700], fill=(90, 60, 40))                       # 大きな机
    d.rectangle([820, 700, 860, 860], fill=(70, 48, 32))
    d.rectangle([1440, 700, 1480, 860], fill=(70, 48, 32))
    _papers(d, 900, 630, n=3)
    _phone(d, 1260, 570, 0.6)
    return img


def kaichoshitsu_net():
    return kaichoshitsu(net=True)


def shinbun():
    """新聞の一面広告を大きく写した画。文字は描かず、灰色の帯と大きな余白で見せる。"""
    img = vgrad((W, H), (60, 58, 56), (40, 38, 36))
    d = _d(img)
    d.polygon([(380, 80), (1560, 60), (1600, 1020), (340, 1040)], fill=(238, 234, 222))
    rnd = random.Random(7)
    for k in range(14):                                                          # 上の記事の細い行
        y = 110 + k * 12
        d.line([(420, y), (1540, y - 2)], fill=(170, 166, 156), width=4)
    d.rectangle([520, 330, 1420, 520], fill=(28, 28, 30))                       # 大きな黒い見出し帯（文字なし）
    for k in range(3):
        y = 600 + k * 60
        d.rectangle([600 + rnd.randint(0, 60), y, 1340 - rnd.randint(0, 120), y + 26], fill=(90, 88, 84))
    for k in range(18):
        y = 820 + k * 10
        d.line([(440, y), (1520, y + 2)], fill=(190, 186, 176), width=3)
    return img


def happyokai():
    """ホテルの発表会場。壇上に白い本体、後ろに大きな幕（文字なし）、客席。"""
    img = _rgb(base((40, 36, 52), (60, 54, 74)))
    d = _d(img)
    d.rectangle([0, 600, W, H], fill=(70, 50, 60))                               # 絨毯
    d.rectangle([360, 110, 1560, 470], fill=(30, 60, 140))                      # 幕
    _glow(img, 960, 290, 420, (120, 170, 255), 60)
    d = _d(img)
    d.ellipse([820, 180, 1100, 400], outline=(230, 230, 236), width=10)        # 丸い飾り（マークではない）
    d.rectangle([700, 520, 1220, 620], fill=(30, 30, 40))                       # 壇
    _dc(d, 820, 440, 0.95)
    for r in range(3):                                                           # 客席の頭
        for k in range(14):
            x = 120 + k * 130 + (r % 2) * 60
            y = 820 + r * 80
            d.ellipse([x, y, x + 70, y + 70], fill=(30, 26, 34))
    return img


def cm_machi():
    """CM 撮影の街角セット。商店の軒先、カメラと照明。"""
    img = vgrad((W, H), (190, 210, 228), (226, 230, 232))
    d = _d(img)
    d.rectangle([0, FLOOR - 40, W, H], fill=(150, 150, 146))                   # 道
    for k, x in enumerate((100, 600, 1100)):                                     # 店の軒
        d.rectangle([x, 220, x + 440, FLOOR - 40], fill=((200, 186, 160), (186, 196, 206), (210, 196, 176))[k], outline=(120, 110, 96), width=4)
        d.polygon([(x - 20, 220), (x + 460, 220), (x + 440, 300), (x, 300)], fill=((180, 60, 60), (60, 110, 160), (70, 140, 90))[k])
        d.rectangle([x + 60, 380, x + 380, 640], fill=(160, 190, 210))
    d.rectangle([1640, 560, 1720, 620], fill=(30, 30, 34))                       # カメラ
    d.rectangle([1600, 576, 1640, 604], fill=(50, 50, 56))
    d.line([(1660, 620), (1620, 880)], fill=(40, 40, 44), width=6)
    d.line([(1680, 620), (1680, 880)], fill=(40, 40, 44), width=6)
    d.line([(1700, 620), (1740, 880)], fill=(40, 40, 44), width=6)
    d.polygon([(1780, 220), (1880, 200), (1880, 330), (1780, 310)], fill=(240, 236, 210))  # 照明
    d.line([(1830, 330), (1830, 880)], fill=(60, 60, 64), width=6)
    return img


def cm_kuruma():
    """車の後部座席。窓の外を夕方の街が流れる。"""
    img = vgrad((W, H), (238, 160, 110), (120, 90, 110))
    d = _d(img)
    for k in range(9):                                                            # 窓の外のビル
        x = 120 + k * 200
        d.rectangle([x, 300 - (k * 37) % 120, x + 150, 640], fill=(80, 70, 90))
    for k in range(10):                                                           # 流れる線
        y = 260 + k * 38
        d.line([(0, y), (W, y + 6)], fill=(255, 220, 190, 60), width=3)
    d.rectangle([0, 0, W, 180], fill=(40, 36, 40))                               # 天井
    d.rectangle([0, 640, W, H], fill=(56, 48, 52))                               # 座席
    d.rounded_rectangle([200, 600, 1720, 760], radius=40, fill=(76, 64, 70))
    d.rectangle([900, 160, 1020, 700], fill=(40, 36, 40))                         # 窓の柱
    return img


def cm_bar():
    """落ち込む場面。夜の屋台のカウンターに、ぽつんとグラス。"""
    img = vgrad((W, H), (20, 22, 40), (40, 34, 50))
    d = _d(img)
    d.rectangle([200, 120, 1720, 220], fill=(150, 40, 40))                        # のれん
    for k in range(7):
        d.line([(200 + k * 217, 120), (200 + k * 217, 220)], fill=(110, 26, 26), width=6)
    _glow(img, 960, 300, 380, (255, 200, 120), 80)
    d = _d(img)
    d.rectangle([0, 620, W, 700], fill=(120, 86, 56))                             # カウンター
    d.rectangle([0, 700, W, H], fill=(70, 50, 36))
    d.rectangle([900, 520, 960, 620], fill=(220, 230, 240, 180), outline=(180, 190, 200), width=3)
    d.rectangle([904, 560, 956, 616], fill=(220, 170, 60, 200))
    d.ellipse([1320, 560, 1440, 620], fill=(240, 236, 226))                       # 小皿
    return img


# ---------------------------------------------------------------- 工場・店
def kojo(wafer=False):
    """半導体工場のクリーンルーム。wafer=True は大写しのウエハーで、良品が数個だけ光る。"""
    if wafer:
        img = vgrad((W, H), (20, 26, 40), (36, 44, 60))
        d = _d(img)
        cx, cy, r = 960, 520, 420
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 156, 176), outline=(210, 214, 226), width=8)
        good = {(2, 3), (5, 6), (7, 2), (4, 8), (8, 5), (3, 7)}
        step = 70
        for i in range(-6, 7):
            for j in range(-6, 7):
                x, y = cx + i * step, cy + j * step
                if (x - cx) ** 2 + (y - cy) ** 2 > (r - 50) ** 2:
                    continue
                key = (i + 6) % 10, (j + 6) % 10
                if key in good:
                    d.rectangle([x - 28, y - 28, x + 28, y + 28], fill=(250, 210, 80))
                else:
                    d.rectangle([x - 28, y - 28, x + 28, y + 28], fill=(110, 116, 134))
                    d.line([(x - 18, y - 18), (x + 18, y + 18)], fill=(200, 70, 70), width=4)
                    d.line([(x + 18, y - 18), (x - 18, y + 18)], fill=(200, 70, 70), width=4)
        return img
    img = vgrad((W, H), (236, 236, 222), (220, 222, 210))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(200, 204, 196))
    for k in range(6):
        x = 80 + k * 300
        d.rectangle([x, 300, x + 240, FLOOR], fill=(214, 216, 210), outline=(156, 160, 154), width=4)
        d.rectangle([x + 30, 340, x + 210, 440], fill=(60, 66, 72))
        d.ellipse([x + 180, 470, x + 210, 500], fill=(240, 180, 60) if k % 2 else (110, 116, 120))
    d.rectangle([0, 0, W, 90], fill=(250, 240, 170))                            # 黄色い照明（クリーンルーム）
    return img


def kojo_wafer():
    return kojo(wafer=True)


def mise(urikire=False, ps2=False):
    """ゲーム店。棚に白い箱。urikire は棚が空で売り切れ札、ps2 は黒い箱の山と行列。"""
    img = _rgb(base((236, 232, 220), (220, 216, 204)))
    wood_floor(img, FLOOR, col=(160, 150, 136), line=(140, 130, 118))
    d = _d(img)
    for r in range(3):                                                            # 棚
        y = 240 + r * 200
        d.rectangle([120, y + 150, 1800, y + 166], fill=(150, 120, 90))
        if urikire:
            continue
        for k in range(11):
            x = 150 + k * 150
            if ps2:
                _ps_box(d, x, y + 50, 0.9)
            else:
                _dc_box(d, x, y + 50, 0.9)
    if urikire:
        d.rectangle([700, 380, 1220, 560], fill=(250, 240, 120), outline=(200, 60, 60), width=10)
        d.line([(740, 470), (1180, 470)], fill=(200, 60, 60), width=14)
        d.line([(740, 520), (1080, 520)], fill=(200, 60, 60), width=10)
    if ps2:
        d = _d(img)
        d.rectangle([0, 760, W, H], fill=(160, 150, 136, 120))
        _person_line(d, 80, 1000, 26, 1.0)
    d.rectangle([1500, 760, 1860, 880], fill=(200, 180, 150))                     # レジ台
    return img


def mise_urikire():
    return mise(urikire=True)


def mise_ps2():
    return mise(ps2=True)


def america():
    """アメリカの店の夜。明るい店先に長い行列。"""
    img = vgrad((W, H), (10, 14, 40), (30, 30, 60))
    d = _d(img)
    d.rectangle([300, 200, 1620, 760], fill=(250, 240, 210))                     # 明るい店
    _glow(img, 960, 480, 700, (255, 240, 200), 80)
    d = _d(img)
    d.rectangle([300, 160, 1620, 230], fill=(200, 40, 50))                        # 赤い看板（文字なし）
    for k in range(9):
        _dc_box(d, 380 + k * 140, 560, 0.85)
    d.rectangle([0, 760, W, H], fill=(60, 60, 70))
    _person_line(d, 40, 1020, 27, 1.0)
    for k in range(40):
        x, y = (k * 97) % W, (k * 53) % 150
        d.ellipse([x, y, x + 4, y + 4], fill=(250, 250, 220))
    return img


def kaigi(akaji=False):
    """会議室。ボードに下がるグラフ。akaji=True はグラフが赤く崩れ、紙が散らばる。"""
    img = _rgb(base((214, 212, 206), (198, 196, 190)))
    wood_floor(img, FLOOR, col=(106, 96, 86), line=(88, 80, 72))
    d = _d(img)
    if akaji:
        _chart(d, 560, 120, 1360, 520, [0.8, 0.62, 0.40, 0.18, 0.02], col=(220, 30, 40))
        d.rectangle([560, 120, 1360, 520], fill=(220, 40, 40, 50))
        rnd = random.Random(3)
        for k in range(14):
            x, y = rnd.randint(300, 1600), rnd.randint(720, 900)
            d.polygon([(x, y), (x + 120, y - 20), (x + 130, y + 60), (x + 10, y + 80)], fill=(244, 240, 228), outline=(170, 160, 140))
    else:
        _chart(d, 560, 120, 1360, 520, [0.8, 0.7, 0.55, 0.42, 0.30], col=(60, 90, 170))
    d.rectangle([420, 640, 1500, 700], fill=(120, 108, 96))
    _papers(d, 600, 630, n=3)
    _papers(d, 1100, 630, n=2)
    return img


def kaigi_akaji():
    return kaigi(akaji=True)


def kaiken():
    """記者会見場。長机とマイク、後ろに無地の幕、手前にカメラの列。"""
    img = _rgb(base((70, 74, 96), (90, 92, 110)))
    d = _d(img)
    d.rectangle([0, 0, W, 560], fill=(56, 70, 110))                              # 幕
    for k in range(10):
        d.line([(k * 200, 0), (k * 200 + 40, 560)], fill=(48, 60, 98), width=8)
    d.rectangle([260, 560, 1660, 660], fill=(240, 240, 236))                     # 長机（白布）
    d.rectangle([260, 660, 1660, 760], fill=(220, 220, 214))
    for x in (560, 960, 1360):
        d.line([(x, 560), (x - 30, 470)], fill=(40, 40, 44), width=6)
        d.ellipse([x - 52, 450, x - 10, 490], fill=(40, 40, 44))
        d.rectangle([x - 60, 600, x + 60, 640], fill=(250, 250, 250), outline=(160, 160, 160))  # 名札（文字なし）
    d.rectangle([0, 860, W, H], fill=(40, 40, 50))
    for k in range(12):                                                           # カメラの列
        x = 40 + k * 160
        d.rectangle([x, 820, x + 110, 900], fill=(30, 30, 34))
        d.ellipse([x + 70, 836, x + 120, 886], fill=(60, 70, 90))
    return img


def soko():
    """倉庫。白い箱が天井まで積まれている。"""
    img = vgrad((W, H), (190, 190, 186), (160, 160, 156))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(140, 140, 136))
    for k in range(5):
        d.line([(0, 100 + k * 30), (W, 100 + k * 30)], fill=(120, 120, 120), width=6)  # 梁
    for col in range(13):
        for row in range(9):
            x = 20 + col * 146
            y = FLOOR - (row + 1) * 88
            _dc_box(d, x, y, 1.0, col=(242, 242, 236) if (col + row) % 3 else (232, 232, 226))
    return img


def sushi(kowareta=False):
    """回転寿司の店。カウンターの席ごとに注文用の画面。kowareta は画面が割れて煙。"""
    img = _rgb(base((240, 232, 214), (226, 216, 196)))
    wood_floor(img, FLOOR, col=(160, 130, 96), line=(140, 112, 82))
    d = _d(img)
    d.rectangle([0, 520, W, 560], fill=(190, 196, 200))                          # レーン
    for k in range(12):
        x = 40 + k * 160
        d.ellipse([x, 500, x + 100, 540], fill=(250, 250, 248), outline=(180, 180, 180))
        d.ellipse([x + 20, 490, x + 80, 520], fill=(230, 110, 80))
    d.rectangle([0, 560, W, 640], fill=(150, 110, 76))                           # カウンター
    for k in range(5):
        x = 140 + k * 360
        d.rectangle([x, 380, x + 180, 500], fill=(30, 30, 34))
        if kowareta and k == 2:
            d.rectangle([x + 10, 390, x + 170, 490], fill=(60, 60, 70))
            for a in range(7):
                ang = a * 0.9
                d.line([(x + 90, 440), (x + 90 + math.cos(ang) * 80, 440 + math.sin(ang) * 50)], fill=(230, 230, 236), width=3)
            for j in range(6):
                d.ellipse([x + 40 + j * 20, 300 - j * 30, x + 120 + j * 20, 380 - j * 30], fill=(150, 150, 150, 120))
        else:
            d.rectangle([x + 10, 390, x + 170, 490], fill=(80, 150, 210))
            d.rectangle([x + 24, 404, x + 90, 440], fill=(240, 200, 120))
    return img


def sushi_kowareta():
    return sushi(kowareta=True)


def eigakan():
    """映画館。暗い客席と光るスクリーン（中身は青い流れる光だけ）。"""
    img = vgrad((W, H), (14, 12, 22), (24, 20, 34))
    d = _d(img)
    d.rectangle([260, 80, 1660, 620], fill=(40, 90, 200))
    _glow(img, 960, 350, 700, (120, 170, 255), 70)
    d = _d(img)
    for k in range(5):
        d.line([(300, 200 + k * 70), (1620, 160 + k * 90)], fill=(160, 210, 255), width=12)
    for r in range(4):
        for k in range(16):
            x = 40 + k * 120 + (r % 2) * 50
            y = 700 + r * 90
            d.rounded_rectangle([x, y, x + 96, y + 110], radius=20, fill=(90, 20, 30))
            d.ellipse([x + 20, y - 40, x + 76, y + 16], fill=(20, 16, 24))
    return img


def gendai():
    """今の会社のロビー。ガラスの壁と観葉植物、壁に大きなモニター（中身は抽象）。"""
    img = vgrad((W, H), (230, 236, 240), (214, 220, 226))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(200, 204, 210))
    for k in range(8):
        d.line([(k * 260, 0), (k * 260, FLOOR)], fill=(190, 200, 210), width=6)
    sx0, sy0, sx1, sy1 = _flat_tv(d, 620, 160, 1300, 540, screen=(30, 60, 140))
    for k in range(4):
        d.rectangle([sx0 + 40 + k * 150, sy0 + 120 - k * 20, sx0 + 140 + k * 150, sy1 - 40], fill=(80 + k * 30, 150, 230))
    for x in (200, 1650):
        d.rectangle([x, 760, x + 120, FLOOR], fill=(150, 120, 90))
        for j in range(6):
            d.ellipse([x - 60 + j * 30, 560 + (j % 2) * 40, x + 60 + j * 30, 760], fill=(60, 140, 80))
    d.rectangle([760, 700, 1160, 780], fill=(240, 240, 244))                     # 受付
    return img


LOCATIONS = {
    "sg_heya": heya, "sg_heya_dc": heya_dc, "sg_kaisha70": kaisha70, "sg_gamecenter": gamecenter,
    "sg_kaihatsu": kaihatsu, "sg_kaihatsu_yoru": kaihatsu_yoru, "sg_kaihatsu_mega": kaihatsu_mega,
    "sg_yakuinkai": yakuinkai, "sg_kaichoshitsu": kaichoshitsu, "sg_kaichoshitsu_net": kaichoshitsu_net,
    "sg_shinbun": shinbun, "sg_happyokai": happyokai, "sg_cm_machi": cm_machi, "sg_cm_kuruma": cm_kuruma,
    "sg_cm_bar": cm_bar, "sg_kojo": kojo, "sg_kojo_wafer": kojo_wafer, "sg_mise": mise,
    "sg_mise_urikire": mise_urikire, "sg_mise_ps2": mise_ps2, "sg_america": america,
    "sg_kaigi": kaigi, "sg_kaigi_akaji": kaigi_akaji, "sg_kaiken": kaiken, "sg_soko": soko,
    "sg_sushi": sushi, "sg_sushi_kowareta": sushi_kowareta, "sg_eigakan": eigakan, "sg_gendai": gendai,
}

# 台本で使った年に合わせる（台本ができたら足す）
CARDS = ["1950", "1971", "1973", "1983", "1984", "1994", "1997", "1998", "1999", "2000", "2001"]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for y in CARDS:
        if only and f"sg_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"sg_card_{y}.png")
        print(f"生成完了: sg_card_{y}.png")
