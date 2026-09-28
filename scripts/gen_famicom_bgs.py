#!/usr/bin/env python3
"""ファミコンの誕生回（67_ファミコンの誕生 / slug=famicom-uemura）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はスーパーカブ回（gen_supercub_bgs.py）と同じ。
実在の会社の商標（ロゴ・社名の文字）は描かない。ゲーム機・カセット・ゲーム画面も
簡略化した自作の絵にとどめ、実在のゲームの絵柄は写さない。

実行: PYTHONPATH=. python scripts/gen_famicom_bgs.py [名前...]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)
INK = (60, 60, 66)
ENJI = (128, 30, 42)          # 本体のえんじ色
CREAM = (236, 228, 208)       # 本体の白
GOLD = (196, 164, 96)


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


def _dpad(d, cx, cy, r, col=(40, 40, 44)):
    """十字ボタン。r は腕の長さ。"""
    w = r * 0.36
    d.rectangle([cx - w, cy - r, cx + w, cy + r], fill=col)
    d.rectangle([cx - r, cy - w, cx + r, cy + w], fill=col)


def _pad(d, x, y, s=1.0, body=ENJI, face=GOLD):
    """コントローラー（左上が x, y）。十字ボタンと丸ボタン2つ。"""
    d.rounded_rectangle([x, y, x + 200 * s, y + 86 * s], radius=int(10 * s), fill=body)
    d.rounded_rectangle([x + 10 * s, y + 10 * s, x + 190 * s, y + 76 * s], radius=int(6 * s), fill=face)
    _dpad(d, x + 48 * s, y + 43 * s, 22 * s)
    for k in range(2):
        cx = x + (132 + k * 34) * s
        d.ellipse([cx - 12 * s, y + 38 * s, cx + 12 * s, y + 62 * s], fill=(190, 40, 40))


def _console(d, x, y, s=1.0, pads=True, cart=True):
    """ゲーム機の本体（左上が x, y）。白い上面とえんじの帯、上にカセット、手前にコントローラー2つ。"""
    w, h = 380 * s, 150 * s
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(12 * s), fill=CREAM, outline=(170, 160, 140), width=2)
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=ENJI)                      # えんじの帯
    d.rectangle([x + w * 0.3, y - 6 * s, x + w * 0.7, y + 14 * s], fill=(60, 60, 64))  # 差し込み口
    if cart:
        d.rectangle([x + w * 0.33, y - 70 * s, x + w * 0.67, y + 4 * s], fill=(210, 190, 60), outline=(120, 100, 30), width=2)
        d.rectangle([x + w * 0.37, y - 60 * s, x + w * 0.63, y - 22 * s], fill=(244, 240, 230))
    for k in range(2):                                                          # 前面のスイッチ
        d.rectangle([x + (40 + k * 60) * s, y + h * 0.3, x + (80 + k * 60) * s, y + h * 0.45], fill=ENJI)
    if pads:
        for k in range(2):
            px, py = x + (-40 + k * 260) * s, y + h + 80 * s
            d.line([(x + (60 + k * 260) * s, y + h * 0.8), (px + 100 * s, py)], fill=(40, 40, 44), width=int(4 * s) + 1)
            _pad(d, px, py, 0.8 * s)


def _cart(d, x, y, s=1.0, col=(210, 190, 60)):
    d.rectangle([x, y, x + 110 * s, y + 70 * s], fill=col, outline=(110, 100, 60), width=2)
    d.rectangle([x + 12 * s, y + 10 * s, x + 98 * s, y + 46 * s], fill=(244, 240, 230))


def _crt(d, x, y, w, h, screen=(40, 60, 90), body=(150, 120, 90)):
    """ブラウン管テレビ（左上が x, y）。画面の矩形を返す。"""
    d.rounded_rectangle([x, y, x + w, y + h], radius=24, fill=body, outline=(80, 60, 44), width=4)
    sx0, sy0, sx1, sy1 = x + w * 0.08, y + h * 0.1, x + w * 0.72, y + h * 0.88
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=30, fill=screen)
    for k in range(2):                                                          # つまみ
        cy = y + h * (0.3 + k * 0.3)
        d.ellipse([x + w * 0.8, cy - 20, x + w * 0.8 + 40, cy + 20], fill=(90, 70, 50))
    return sx0, sy0, sx1, sy1


def _gw(d, x, y, s=1.0):
    """携帯ゲーム機（左上が x, y）。液晶と十字ボタン。"""
    d.rounded_rectangle([x, y, x + 150 * s, y + 90 * s], radius=int(8 * s), fill=(200, 196, 186), outline=(120, 116, 106), width=2)
    d.rectangle([x + 40 * s, y + 14 * s, x + 110 * s, y + 64 * s], fill=(170, 186, 160))
    _dpad(d, x + 20 * s, y + 60 * s, 12 * s)
    d.ellipse([x + 122 * s, y + 52 * s, x + 140 * s, y + 70 * s], fill=(190, 40, 40))


def _phone(d, x, y, s=1.0, col=(30, 30, 34)):
    """黒電話（左上が x, y）。"""
    d.rounded_rectangle([x, y + 30 * s, x + 130 * s, y + 90 * s], radius=int(14 * s), fill=col)
    d.ellipse([x + 35 * s, y + 38 * s, x + 95 * s, y + 88 * s], fill=(200, 200, 200))
    d.ellipse([x + 55 * s, y + 55 * s, x + 75 * s, y + 72 * s], fill=col)
    d.rounded_rectangle([x - 10 * s, y, x + 140 * s, y + 26 * s], radius=int(12 * s), fill=col)


def _board(d, x, y, s=1.0):
    """基板（左上が x, y）。"""
    d.rectangle([x, y, x + 180 * s, y + 110 * s], fill=(40, 110, 70), outline=(20, 70, 40), width=2)
    for k in range(3):
        d.rectangle([x + (20 + k * 54) * s, y + 30 * s, x + (60 + k * 54) * s, y + 60 * s], fill=(30, 30, 34))
    for k in range(8):
        d.line([(x + 10 * s, y + (75 + k * 3) * s), (x + 170 * s, y + (75 + k * 3) * s)], fill=(190, 170, 90), width=1)


def _boxes(d, x, y, n=4, rows=3, col=(186, 150, 104)):
    """段ボールの山（左下が x, y）。"""
    for r in range(rows):
        for k in range(n - r):
            bx, by = x + k * 110 + r * 55, y - (r + 1) * 80
            d.rectangle([bx, by, bx + 104, by + 76], fill=col, outline=(120, 90, 60), width=3)
            d.line([(bx, by + 30), (bx + 104, by + 30)], fill=(150, 116, 80), width=3)


# ---------------------------------------------------------------- 場所
def heya():
    """今の部屋。薄型テレビと、開いた押し入れ、床のゲーム機。"""
    img = _rgb(base((230, 226, 214), (214, 210, 198)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([80, 120, 560, 800], fill=(214, 200, 170), outline=(120, 96, 70), width=8)  # 押し入れ
    d.line([(80, 440), (560, 440)], fill=(120, 96, 70), width=8)
    _boxes(d, 110, 430, n=3, rows=2)
    d.rectangle([740, 240, 1180, 500], fill=(30, 30, 36), outline=(20, 20, 24), width=10)   # 薄型テレビ
    d.rectangle([760, 260, 1160, 480], fill=(40, 80, 150))
    d.rectangle([700, 560, 1220, 600], fill=(120, 90, 64))                     # テレビ台
    d.rectangle([720, 600, 1200, 700], fill=(140, 106, 76))
    _console(d, 790, 770, 0.8)
    _cart(d, 1300, 880, 0.9)
    return img


def heya_on():
    """締めの部屋。テレビに野球場（緑の芝と白い線）が映っている。"""
    img = heya()
    d = _d(img)
    d.rectangle([760, 260, 1160, 480], fill=(60, 150, 70))
    d.polygon([(960, 300), (1060, 380), (960, 460), (860, 380)], outline=(245, 245, 245), width=5)
    d.polygon([(960, 330), (1030, 380), (960, 430), (890, 380)], fill=(190, 150, 100))
    return img


def denkiya():
    """1950年代の町の電器屋。店先に置いたテレビ。"""
    img = vgrad((W, H), (190, 210, 226), (226, 230, 232))
    d = _d(img)
    d.rectangle([0, 860, W, H], fill=(150, 146, 140))
    d.rectangle([420, 160, 1500, 860], fill=(196, 176, 146))                   # 店
    d.polygon([(380, 160), (960, 70), (1540, 160)], fill=(84, 72, 66))
    d.rectangle([520, 240, 1400, 300], fill=(90, 70, 50))                      # 看板（文字なし）
    d.rectangle([540, 340, 1380, 860], fill=(170, 196, 206), outline=(90, 70, 50), width=10)  # ガラス戸
    sx0, sy0, sx1, sy1 = _crt(d, 780, 560, 340, 260, screen=(150, 156, 160))
    for k in range(6):                                                          # 画面の走査線
        y = sy0 + 20 + k * 30
        d.line([(sx0 + 20, y), (sx1 - 20, y)], fill=(180, 186, 190), width=4)
    return img


def sharp():
    """1960年代の電機メーカーの事務所。机と、部品の見本が並ぶ棚。"""
    img = _rgb(base((226, 224, 218), (208, 206, 200)))
    wood_floor(img, FLOOR, col=(130, 120, 106), line=(110, 100, 88))
    d = _d(img)
    _window(d, 740, 120, 1180, 440, sky=(190, 212, 230))
    for k in range(4):                                                          # 見本の棚
        y = 220 + k * 110
        d.rectangle([1440, y, 1860, y + 12], fill=(110, 96, 80))
        for j in range(6):
            x = 1460 + j * 66
            d.rectangle([x, y - 50, x + 50, y], fill=(80, 90, 110), outline=(50, 56, 70))
            d.rectangle([x + 12, y - 38, x + 38, y - 18], fill=(150, 170, 200))
    _table(d, 700, 1220, 640, col=(120, 110, 96))
    for k in range(3):                                                          # 机の上の部品
        d.rectangle([780 + k * 110, 600, 840 + k * 110, 640], fill=(70, 80, 100))
        d.rectangle([790 + k * 110, 608, 830 + k * 110, 628], fill=(140, 160, 200))
    return img


def nintendo68():
    """1968年の開発室。木の机に光線銃と的。"""
    img = _rgb(base((222, 212, 194), (204, 194, 176)))
    wood_floor(img, FLOOR, col=(120, 96, 72), line=(100, 80, 60))
    d = _d(img)
    for k, r in enumerate((150, 110, 70, 32)):                                  # 壁の的
        col = (220, 60, 50) if k % 2 == 0 else (244, 240, 230)
        d.ellipse([760 - r, 330 - r, 760 + r, 330 + r], fill=col)
    _table(d, 620, 900, 640, col=(140, 104, 72))
    for k in range(1):                                                          # 光線銃
        x = 660
        d.polygon([(x, 600), (x + 170, 600), (x + 170, 625), (x + 60, 625), (x + 40, 670), (x + 10, 670), (x + 20, 625), (x, 625)],
                  fill=(60, 60, 66))
    return img


def ousetsu():
    """応接室。ソファと、お茶の載ったテーブル。"""
    img = _rgb(base((226, 218, 204), (208, 200, 186)))
    wood_floor(img, FLOOR, col=(116, 92, 70), line=(96, 76, 58))
    d = _d(img)
    _window(d, 760, 120, 1160, 420, sky=(196, 214, 228))
    d.rounded_rectangle([640, 600, 1280, 760], radius=30, fill=(120, 60, 50))  # ソファ
    d.rounded_rectangle([640, 520, 1280, 620], radius=30, fill=(140, 72, 60))
    d.rectangle([760, 800, 1160, 830], fill=(90, 60, 40))                      # テーブル
    for x in (860, 1060):
        d.rounded_rectangle([x - 20, 770, x + 20, 800], radius=6, fill=(170, 176, 160))
    return img


def bowling():
    """元ボウリング場の射撃場。奥の幕に飛ぶ皿の映像、手前に光線銃の台。"""
    img = vgrad((W, H), (60, 56, 70), (90, 84, 96))
    d = _d(img)
    for k in range(5):                                                          # レーン
        x0 = 260 + k * 300
        d.polygon([(x0, H), (x0 + 260, H), (880 + k * 40, 560), (840 + k * 40, 560)], fill=(196, 160, 110))
        d.line([(x0 + 260, H), (880 + k * 40, 560)], fill=(150, 120, 80), width=4)
    d.rectangle([640, 140, 1280, 520], fill=(40, 60, 90), outline=(20, 20, 26), width=8)   # 幕
    for cx, cy in ((780, 260), (980, 330), (1140, 230)):                       # 飛ぶ皿
        d.ellipse([cx - 40, cy - 14, cx + 40, cy + 14], fill=(236, 120, 50))
    d.rectangle([860, 760, 1060, 800], fill=(80, 76, 84))                      # 銃の台
    d.polygon([(900, 740), (1030, 740), (1030, 760), (940, 760), (925, 790), (905, 790), (912, 760), (900, 760)], fill=(40, 40, 44))
    return img


def kaihatsu77():
    """1977年の開発室。雑音の走るテレビと、つまみの付いたゲーム機。"""
    img = _rgb(base((220, 218, 210), (202, 200, 192)))
    wood_floor(img, FLOOR, col=(120, 112, 100), line=(100, 94, 84))
    d = _d(img)
    sx0, sy0, sx1, sy1 = _crt(d, 620, 240, 300, 230, screen=(120, 126, 130))
    import random
    rnd = random.Random(3)
    for _ in range(260):                                                        # 砂あらし
        x, y = rnd.uniform(sx0 + 10, sx1 - 10), rnd.uniform(sy0 + 10, sy1 - 10)
        g = rnd.randint(150, 240)
        d.rectangle([x, y, x + 6, y + 3], fill=(g, g, g))
    _table(d, 610, 930, 640, col=(130, 110, 90))
    d.rectangle([640, 580, 860, 640], fill=(230, 140, 50), outline=(150, 80, 30), width=3)  # つまみのゲーム機
    for k in range(4):
        d.ellipse([662 + k * 50, 596, 692 + k * 50, 626], fill=(250, 240, 220))
    d.line([(860, 610), (900, 560), (880, 480)], fill=(40, 40, 44), width=4)   # アンテナ線
    return img


def kaihatsu(proto=False, night=False):
    """1980年代の開発室。基板とオシロスコープ、空いた椅子。proto=True は試作機と携帯ゲーム機。"""
    img = _rgb(base((40, 44, 60), (60, 62, 76)) if night else base((222, 222, 216), (204, 204, 198)))
    wood_floor(img, FLOOR, col=(116, 110, 100) if not night else (60, 58, 60), line=(96, 92, 84) if not night else (48, 46, 50))
    d = _d(img)
    _window(d, 760, 110, 1160, 380, sky=(20, 24, 50) if night else (196, 214, 228))
    _table(d, 600, 1460, 640, col=(126, 118, 104) if not night else (90, 84, 76))
    ox = 1280 if (proto or night) else 700
    d.rectangle([ox, 540, ox + 160, 640], fill=(90, 96, 100))                  # オシロスコープ
    d.rectangle([ox + 16, 556, ox + 110, 624], fill=(40, 70, 50))
    d.line([(ox + 20, 600), (ox + 40, 570), (ox + 60, 610), (ox + 80, 575), (ox + 105, 600)], fill=(120, 240, 150), width=3)
    if night:
        sx0, sy0, sx1, sy1 = _crt(d, 640, 440, 250, 190, screen=(60, 140, 70))
        d.line([(sx0 + 60, sy1 - 30), ((sx0 + sx1) / 2, sy0 + 40)], fill=(60, 140, 70), width=4)  # 消えかけた白線
        d.line([((sx0 + sx1) / 2, sy0 + 40), (sx1 - 60, sy1 - 30)], fill=(236, 236, 236), width=4)
        d.ellipse([1300, 380, 1400, 430], fill=(250, 230, 150))               # 電気スタンド
    elif proto:
        _gw(d, 636, 552, 0.8)
        _board(d, 770, 540, 0.7)
        d.line([(756, 580), (770, 575)], fill=(200, 60, 50), width=3)
        d.line([(756, 596), (770, 600)], fill=(50, 80, 200), width=3)
    else:
        _board(d, 900, 520, 0.9)
        _board(d, 1080, 540, 0.7)
    for x in (340, 1500):                                                       # 空いた椅子
        d.rectangle([x, 640, x + 90, 660], fill=(70, 70, 76))
        d.rectangle([x + 70, 540, x + 90, 660], fill=(70, 70, 76))
        d.rectangle([x + 40, 660, x + 50, 780], fill=(60, 60, 64))
    return img


def kaihatsu2():
    return kaihatsu(proto=True)


def kaihatsu_yoru():
    return kaihatsu(night=True)


def denwa():
    """電話の場面。左が夜の自宅、右が社長室。キャラの配置（0.2 / 0.56 / 0.84）に合わせて割る。"""
    img = Image.new("RGB", (W, H))
    left = _rgb(base((40, 46, 70), (56, 60, 80)))
    tatami_floor(left, FLOOR)
    right = _shacho_base()
    img.paste(left.crop((0, 0, 730, H)), (0, 0))
    img.paste(right.crop((730, 0, W, H)), (730, 0))
    d = _d(img)
    d.rectangle([60, 140, 360, 420], fill=(20, 24, 50), outline=(80, 70, 60), width=8)       # 夜の窓
    d.ellipse([250, 180, 310, 240], fill=(240, 236, 200))
    d.rectangle([540, 700, 710, 730], fill=(110, 80, 56))                      # 電話台
    _phone(d, 560, 610, 1.0)
    d.rectangle([1250, 700, 1430, 730], fill=(90, 60, 40))
    _phone(d, 1270, 610, 1.0)
    d.rectangle([722, 0, 738, H], fill=(20, 20, 24))                           # 仕切り
    return img


def _shacho_base():
    img = _rgb(base((214, 206, 190), (196, 188, 172)))
    wood_floor(img, FLOOR, col=(100, 76, 58), line=(84, 62, 48))
    d = _d(img)
    _window(d, 780, 120, 1180, 420, sky=(200, 216, 226))
    d.polygon([(790, 400), (900, 300), (1010, 380), (1100, 320), (1170, 400)], fill=(120, 150, 120))  # 窓の外の山
    for k in range(3):                                                          # 本棚
        y = 200 + k * 150
        d.rectangle([1500, y, 1880, y + 14], fill=(90, 64, 44))
        for j in range(9):
            d.rectangle([1510 + j * 40, y - 100, 1540 + j * 40, y], fill=((120, 60, 50), (60, 80, 110), (150, 130, 80))[j % 3])
    _table(d, 600, 1400, 660, col=(90, 60, 40))
    return img


def shachoshitsu(scarf=False):
    """社長室。大きな机と窓の外の山、本棚。scarf=True は机の上にえんじのマフラーと試作の本体。"""
    img = _shacho_base()
    d = _d(img)
    if scarf:
        d.rounded_rectangle([640, 590, 880, 662], radius=18, fill=ENJI)            # たたんだマフラー
        for k in range(3):
            d.line([(652, 606 + k * 18), (868, 606 + k * 18)], fill=(96, 20, 30), width=4)
        d.rectangle([840, 640, 880, 700], fill=ENJI)                            # 垂れた端
        for k in range(6):                                                      # 房
            d.line([(842 + k * 7, 700), (842 + k * 7, 730)], fill=ENJI, width=3)
    else:
        _papers(d, 960, 640)
        _phone(d, 1220, 590, 0.6)
    return img


def shachoshitsu2():
    return shachoshitsu(scarf=True)


def _papers(d, x0, y0, n=3, col=(244, 240, 228)):
    for k in range(n):
        x, y = x0 + k * 22, y0 - k * 8
        d.rectangle([x, y - 60, x + 120, y + 20], fill=col, outline=(170, 160, 140), width=2)


def ricoh():
    """半導体工場。止まった装置が並び、表示灯がわずかに点く。"""
    img = vgrad((W, H), (232, 236, 238), (214, 220, 224))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(196, 204, 210))
    for k in range(6):                                                          # 装置
        x = 80 + k * 300
        d.rectangle([x, 300, x + 240, FLOOR], fill=(206, 212, 216), outline=(150, 158, 164), width=4)
        d.rectangle([x + 30, 340, x + 210, 440], fill=(60, 66, 72))
        lamp = (80, 200, 110) if k in (1, 4) else (110, 116, 120)
        d.ellipse([x + 180, 470, x + 210, 500], fill=lamp)
        d.rectangle([x + 40, 520, x + 200, 540], fill=(170, 176, 182))
    return img


def arcade():
    """開発室のゲームセンター用の筐体。画面は斜めの足場とはしご（抽象）。机にストップウォッチ。"""
    img = _rgb(base((214, 214, 210), (196, 196, 192)))
    wood_floor(img, FLOOR, col=(110, 104, 96), line=(90, 86, 80))
    d = _d(img)
    d.polygon([(650, 120), (890, 120), (910, 300), (910, FLOOR), (630, FLOOR), (630, 300)], fill=(40, 60, 130))  # 筐体
    d.rectangle([660, 180, 880, 500], fill=(10, 10, 16))
    for k in range(4):                                                          # 斜めの足場
        y = 230 + k * 70
        d.line([(675, y + (16 if k % 2 else 0)), (865, y + (0 if k % 2 else 16))], fill=(210, 60, 90), width=8)
    for x, y in ((710, 250), (830, 320), (730, 390)):                           # はしご
        d.line([(x, y), (x, y + 56)], fill=(80, 200, 220), width=3)
        d.line([(x + 16, y), (x + 16, y + 56)], fill=(80, 200, 220), width=3)
    d.rectangle([645, 540, 895, 600], fill=(60, 60, 70))                       # 操作盤
    d.rectangle([1262, 700, 1352, 730], fill=(120, 96, 70))                    # 小机
    d.rectangle([1296, 730, 1318, 860], fill=(100, 80, 60))
    d.ellipse([1270, 620, 1344, 694], fill=(200, 200, 204), outline=INK, width=4)   # ストップウォッチ
    d.rectangle([1299, 602, 1315, 622], fill=(160, 160, 164))
    d.line([(1307, 657), (1307, 630)], fill=INK, width=3)
    return img


def setsumeikai():
    """説明会の会場。床まで布を垂らした台に本体、横にテレビ。"""
    img = _rgb(base((218, 214, 206), (200, 196, 188)))
    wood_floor(img, FLOOR, col=(120, 106, 90), line=(100, 88, 74))
    d = _d(img)
    d.rectangle([520, 110, 1400, 200], fill=(40, 70, 120))                     # 幕（文字なし）
    d.rectangle([600, 640, 1000, FLOOR + 30], fill=(40, 60, 110))              # 布を垂らした台
    d.rectangle([600, 620, 1000, 650], fill=(60, 84, 140))
    _console(d, 650, 560, 0.55, pads=False)
    sx0, sy0, sx1, sy1 = _crt(d, 660, 330, 220, 170, screen=(20, 20, 30))
    d.rectangle([sx0 + 20, sy1 - 30, sx1 - 20, sy1 - 22], fill=(210, 60, 90))
    return img


def toyshop():
    """1983年のおもちゃ屋。棚に箱が並び、値札に 14,800円。"""
    img = _rgb(base((236, 230, 214), (220, 214, 198)))
    wood_floor(img, FLOOR, col=(150, 120, 90), line=(130, 104, 78))
    d = _d(img)
    for k in range(3):                                                          # 棚
        y = 260 + k * 170
        d.rectangle([640, y, 1300, y + 16], fill=(120, 90, 60))
        for j in range(5):
            x = 660 + j * 128
            col = ((230, 230, 226), (220, 70, 60), (70, 120, 200), (240, 200, 60), (120, 180, 110))[(j + k) % 5]
            d.rectangle([x, y - 130, x + 110, y], fill=col, outline=(90, 90, 96), width=2)
    d.rectangle([1340, 520, 1560, 600], fill=(250, 250, 240), outline=(200, 60, 50), width=5)   # 値札
    _text_c(d, 1450, 536, "14,800円", 40, (200, 50, 40))
    return img


def kojo():
    """年の瀬の外注先の工場。作業台に開いた本体、戻ってきた箱の山。"""
    img = _rgb(base((206, 206, 202), (186, 186, 182)))
    wood_floor(img, FLOOR, col=(110, 108, 104), line=(92, 90, 86))
    d = _d(img)
    _window(d, 780, 120, 1140, 360, sky=(200, 206, 214))
    for x, y in ((840, 180), (960, 250), (1060, 170), (900, 300)):             # 雪
        d.ellipse([x, y, x + 10, y + 10], fill=(250, 250, 250))
    _table(d, 700, 1220, 660, col=(110, 116, 120))
    _board(d, 760, 560, 0.8)
    _console(d, 960, 610, 0.5, pads=False, cart=False)
    _boxes(d, 40, FLOOR, n=4, rows=3)
    _boxes(d, 1440, FLOOR, n=4, rows=3)
    return img


def eigyo():
    """営業所。電話の並ぶ机と、注文票の束。"""
    img = _rgb(base((226, 224, 218), (208, 206, 200)))
    wood_floor(img, FLOOR, col=(120, 110, 96), line=(100, 92, 80))
    d = _d(img)
    d.rectangle([760, 130, 1160, 400], fill=(244, 244, 240), outline=(120, 120, 126), width=8)  # 黒板代わりの白板
    for k in range(5):
        d.line([(800, 180 + k * 44), (1120, 180 + k * 44)], fill=(160, 160, 170), width=4)
    _table(d, 660, 1260, 650, col=(126, 118, 104))
    for x in (720, 1100):
        _phone(d, x, 570, 0.6)
    for k in range(4):                                                          # 注文票
        d.rectangle([900 + k * 10, 610 - k * 10, 1020 + k * 10, 650 - k * 10], fill=(250, 246, 226), outline=(170, 160, 130))
    return img


def hotel():
    """東京のホテルの部屋。夜景の窓と、机の電話。"""
    img = _rgb(base((200, 190, 176), (182, 172, 158)))
    wood_floor(img, FLOOR, col=(120, 90, 70), line=(100, 74, 56))
    d = _d(img)
    d.rectangle([720, 110, 1200, 460], fill=(16, 20, 44), outline=(90, 70, 54), width=10)   # 夜景
    import random
    rnd = random.Random(8)
    for k in range(8):
        x = 740 + k * 56
        top = rnd.randint(250, 380)
        d.rectangle([x, top, x + 44, 450], fill=(40, 44, 70))
        for _ in range(6):
            wx, wy = rnd.uniform(x + 4, x + 36), rnd.uniform(top + 8, 440)
            d.rectangle([wx, wy, wx + 6, wy + 8], fill=(250, 220, 140))
    _table(d, 620, 900, 660, col=(110, 80, 60))
    _phone(d, 700, 580, 0.6, col=(236, 232, 224))
    return img


def daigaku():
    """大学の教室。黒板にコントローラーの絵。"""
    img = _rgb(base((222, 218, 210), (204, 200, 192)))
    wood_floor(img, FLOOR, col=(130, 110, 90), line=(110, 94, 76))
    d = _d(img)
    d.rectangle([640, 120, 1280, 460], fill=(40, 70, 56), outline=(120, 96, 70), width=12)   # 黒板
    d.rounded_rectangle([780, 230, 1080, 360], radius=12, outline=(236, 236, 230), width=5)  # チョークのコントローラー
    _dpad(d, 850, 295, 30, col=(236, 236, 230))
    for k in range(2):
        d.ellipse([960 + k * 50, 280, 990 + k * 50, 310], outline=(236, 236, 230), width=4)
    d.line([(1100, 290), (1220, 250)], fill=(236, 236, 230), width=4)
    d.rectangle([700, 700, 1220, 730], fill=(140, 110, 80))                    # 教卓
    d.rectangle([740, 730, 1180, 860], fill=(120, 94, 68))
    return img


def gendai():
    """今の棚。十字ボタンのあるコントローラーがいくつかと、小さなゲーム機。"""
    img = _rgb(base((232, 232, 228), (214, 214, 210)))
    wood_floor(img, FLOOR, col=(170, 150, 120), line=(150, 132, 104))
    d = _d(img)
    for k in range(2):                                                          # 棚
        y = 330 + k * 220
        d.rectangle([600, y, 1320, y + 18], fill=(150, 120, 90))
    for k, col in enumerate(((40, 40, 44), (230, 230, 232), (60, 90, 170))):  # 今のコントローラー
        x = 650 + k * 220
        d.rounded_rectangle([x, 220, x + 180, 320], radius=40, fill=col, outline=(120, 120, 126), width=2)
        _dpad(d, x + 50, 270, 22, col=(120, 120, 126) if k == 0 else (40, 40, 44))
        for j in range(2):
            d.ellipse([x + 110 + j * 30, 256, x + 130 + j * 30, 276], fill=(200, 60, 60))
    _console(d, 820, 470, 0.4)                                                  # 小さなゲーム機
    _pad(d, 1100, 450, 0.5)
    return img


def zukai_chip():
    """図解: 2つの専用チップと、背景の上に重ねるスプライト。キャラの間（x480〜1440）に収める。"""
    img = vgrad((W, H), (244, 244, 238), (226, 230, 226))
    d = _d(img)
    for cx, name, sub, col in ((720, "CPU", "計算する頭の係", (90, 130, 200)), (1120, "PPU", "絵を描く係", (220, 110, 80))):
        d.rectangle([cx - 150, 140, cx + 150, 300], fill=(40, 40, 46))
        for k in range(8):                                                      # 足
            d.rectangle([cx - 140 + k * 38, 300, cx - 128 + k * 38, 330], fill=(170, 170, 176))
            d.rectangle([cx - 140 + k * 38, 110, cx - 128 + k * 38, 140], fill=(170, 170, 176))
        _text_c(d, cx, 180, name, 64, col)
        _text_c(d, cx, 350, sub, 38, INK)
    d.rectangle([600, 520, 1320, 900], fill=(110, 170, 230))                   # 背景（空と地面）
    d.rectangle([600, 820, 1320, 900], fill=(170, 110, 60))
    for k in range(6):
        d.rectangle([600 + k * 120, 820, 600 + k * 120 + 116, 858], outline=(120, 70, 30), width=3)
    d.ellipse([700, 560, 860, 620], fill=(250, 250, 250))                      # 雲
    d.rectangle([980, 700, 1060, 820], fill=(230, 60, 60), outline=(40, 40, 44), width=4)   # スプライト（動くキャラ）
    d.rectangle([996, 716, 1044, 748], fill=(250, 220, 180))
    d.line([(1060, 760), (1150, 700)], fill=INK, width=3)
    _text_c(d, 1220, 660, "スプライト", 36, INK)
    _text_c(d, 700, 470, "背景", 36, INK)
    return img


def zukai_sales():
    """図解: 国内出荷台数の推移（1983〜1986年・万台）。キャラの間（x560〜1360）に収める。"""
    img = vgrad((W, H), (244, 244, 238), (226, 230, 226))
    d = _d(img)
    rows = [("1983", 44), ("1984", 211), ("1985", 579), ("1986", 969)]
    base_y = 880
    for k, (y, v) in enumerate(rows):
        x = 620 + k * 190
        h = v * 0.62
        col = (200, 90, 80) if k == 0 else (90, 140, 200)
        d.rectangle([x, base_y - h, x + 120, base_y], fill=col)
        _text_c(d, x + 60, base_y + 14, f"{y}年", 36, INK)
        _text_c(d, x + 60, base_y - h - 56, f"{v}万台", 38, INK)
    d.line([(580, base_y), (1380, base_y)], fill=INK, width=4)
    _text_c(d, 960, 120, "国内の出荷台数（累計）", 44, INK)
    return img


def ronsou():
    """よくある話は本当か: はてなの付いた3枚の札と、本体。"""
    img = vgrad((W, H), (240, 236, 226), (220, 218, 210))
    d = _d(img)
    for k in range(3):
        cx = 690 + k * 190
        d.rounded_rectangle([cx - 80, 180, cx + 80, 400], radius=16, fill=(250, 248, 240), outline=INK, width=4)
        _text_c(d, cx, 240, "？", 110, (200, 70, 60))
    _console(d, 770, 640, 0.9)
    return img


LOCATIONS = {
    "fc_heya": heya, "fc_heya_on": heya_on, "fc_denkiya": denkiya, "fc_sharp": sharp, "fc_nintendo68": nintendo68,
    "fc_ousetsu": ousetsu, "fc_bowling": bowling, "fc_kaihatsu77": kaihatsu77,
    "fc_kaihatsu": kaihatsu, "fc_kaihatsu2": kaihatsu2, "fc_kaihatsu_yoru": kaihatsu_yoru,
    "fc_denwa": denwa, "fc_shachoshitsu": shachoshitsu, "fc_shachoshitsu2": shachoshitsu2,
    "fc_ricoh": ricoh, "fc_arcade": arcade, "fc_setsumeikai": setsumeikai, "fc_toyshop": toyshop,
    "fc_kojo": kojo, "fc_eigyo": eigyo, "fc_hotel": hotel, "fc_daigaku": daigaku, "fc_gendai": gendai,
    "fc_zukai_chip": zukai_chip, "fc_zukai_sales": zukai_sales, "fc_ronsou": ronsou,
}

CARDS = ["1943", "1967", "1968", "1971", "1977", "1981", "1983", "1984", "1985", "1990"]


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
        if only and f"fc_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"fc_card_{y}.png")
        print(f"生成完了: fc_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
