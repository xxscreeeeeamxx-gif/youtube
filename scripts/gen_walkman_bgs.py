#!/usr/bin/env python3
"""ウォークマンの誕生回（58_ウォークマンの誕生 / slug=sony-walkman）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はオセロ回（gen_othello_bgs.py）と同じ。
実在メーカーの商標（ロゴ・商品名の文字）は描かない。

実行: PYTHONPATH=. python scripts/gen_walkman_bgs.py [名前...]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, glow, make_ginza, make_kinai, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)
BLUE = (70, 110, 170)        # 初代の青い金属色
BLUE_L = (130, 170, 220)
ORANGE = (240, 140, 40)      # ヘッドホンのパッドとホットラインのボタン


def _d(img):
    return ImageDraw.Draw(img)


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


def _glow(img, cx, cy, r, color, alpha=110):
    rgba = img.convert("RGBA")
    glow(rgba, cx, cy, r, color, alpha)
    img.paste(rgba.convert("RGB"), (0, 0))


def _window(d, x0, y0, x1, y1, sky=(150, 186, 214), frame=(70, 62, 56)):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


def _walkman(d, x, y, w=110, h=150, col=BLUE):
    """初代の再生機（青い金属の箱・カセット窓・オレンジのボタン）。文字は描かない。"""
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=col, outline=(40, 60, 90), width=3)
    d.rounded_rectangle([x + w * 0.12, y + h * 0.18, x + w * 0.88, y + h * 0.62], radius=6,
                        fill=(30, 36, 44))
    for k in (0.32, 0.68):
        d.ellipse([x + w * k - 9, y + h * 0.36, x + w * k + 9, y + h * 0.36 + 18], outline=(200, 200, 200), width=3)
    for k in range(4):
        d.rectangle([x + 8 + k * (w - 16) / 4, y - 10, x + 4 + (k + 1) * (w - 16) / 4, y], fill=(190, 196, 206))
    d.ellipse([x + w * 0.62, y + h * 0.72, x + w * 0.62 + 22, y + h * 0.72 + 22], fill=ORANGE)


def _pressman(d, x, y, w=110, h=150):
    """元になった小型録音機（銀色・スピーカーの穴・赤い録音ボタン）。"""
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=(190, 192, 196), outline=(110, 112, 118), width=3)
    for r in range(4):
        for c in range(5):
            d.ellipse([x + 16 + c * 17, y + 18 + r * 14, x + 24 + c * 17, y + 26 + r * 14], fill=(90, 92, 98))
    d.rounded_rectangle([x + 14, y + 86, x + w - 14, y + 120], radius=4, fill=(40, 44, 50))
    d.ellipse([x + w - 34, y + 126, x + w - 14, y + 146], fill=(210, 50, 50))


def _headphone(d, cx, cy, size=120, light=True):
    """ヘッドホン。light=True は軽いオレンジのパッド、False は大きく重い黒。"""
    if light:
        d.arc([cx - size * 0.6, cy - size * 0.7, cx + size * 0.6, cy + size * 0.5], 190, 350,
              fill=(150, 156, 166), width=7)
        for sx in (-1, 1):
            d.ellipse([cx + sx * size * 0.58 - 26, cy - 10, cx + sx * size * 0.58 + 26, cy + 42], fill=ORANGE)
    else:
        d.arc([cx - size * 0.7, cy - size * 0.8, cx + size * 0.7, cy + size * 0.5], 190, 350,
              fill=(40, 40, 44), width=22)
        for sx in (-1, 1):
            d.rounded_rectangle([cx + sx * size * 0.66 - 44, cy - 30, cx + sx * size * 0.66 + 44, cy + 70],
                                radius=26, fill=(30, 30, 34))


def _phone(d, x, y):
    """黒い電話（ダイヤル式）。x, y は本体の左上。"""
    d.rounded_rectangle([x, y + 30, x + 110, y + 80], radius=14, fill=(20, 20, 22))
    d.rounded_rectangle([x - 8, y, x + 118, y + 34], radius=16, fill=(30, 30, 34))
    d.ellipse([x + 30, y + 36, x + 80, y + 78], fill=(60, 60, 64))
    d.ellipse([x + 46, y + 48, x + 64, y + 66], fill=(200, 200, 196))


def _table(d, x0, x1, y, col=(150, 116, 80)):
    d.rectangle([x0, y, x1, y + 40], fill=col)
    d.rectangle([x0 + 20, y + 40, x0 + 40, y + 190], fill=tuple(int(c * 0.8) for c in col))
    d.rectangle([x1 - 40, y + 40, x1 - 20, y + 190], fill=tuple(int(c * 0.8) for c in col))


def _box(d, x, y, w=120, h=80):
    """文字のない製品の箱（青と白）。"""
    d.rectangle([x, y, x + w, y + h], fill=(236, 238, 242), outline=(120, 130, 150), width=3)
    d.rectangle([x, y, x + w, y + h * 0.35], fill=BLUE)
    d.ellipse([x + w * 0.35, y + h * 0.45, x + w * 0.65, y + h * 0.9], outline=ORANGE, width=4)


# ------------------------------------------------------------ 場所
def ima_base():
    """今の居間（窓と机まで）。"""
    img = _rgb(base((236, 232, 222), (214, 208, 196)))
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    d = _d(img)
    _window(d, 740, 110, 1180, 400, sky=(176, 210, 232))
    for k in range(5):
        d.rectangle([770 + k * 80, 300 - (k * 37) % 90, 830 + k * 80, 386], fill=(150, 160, 176))
    _table(d, 780, 1140, 640)
    return img


def ima():
    """今の居間。机にスマホとワイヤレスイヤホン、窓の外は街。"""
    img = ima_base()
    d = _d(img)
    d.rounded_rectangle([860, 600, 920, 640], radius=6, fill=(30, 30, 34))       # スマホ（寝かせる）
    d.rounded_rectangle([990, 610, 1060, 640], radius=12, fill=(246, 246, 246))    # イヤホンのケース
    for k in range(2):
        d.ellipse([1070 + k * 30, 612, 1090 + k * 30, 632], fill=(246, 246, 246))
    return img


def ima2():
    """締め用の居間。机の上にイヤホンが片方ずつ2つ。"""
    img = ima_base()
    d = _d(img)
    _headphone(d, 900, 590, 70, light=True)
    _headphone(d, 1030, 590, 70, light=True)
    return img


def kinai():
    """機内。前の座席の背にテーブル、重い録音機と大きなヘッドホン。"""
    img = make_kinai()
    d = _d(img)
    d.rectangle([840, 640, 1240, 680], fill=(120, 124, 134))                      # テーブル
    d.rounded_rectangle([880, 540, 1060, 640], radius=8, fill=(170, 172, 178), outline=(90, 92, 98), width=4)
    for k in range(3):
        d.ellipse([900 + k * 50, 560, 930 + k * 50, 590], fill=(60, 60, 64))
    d.rectangle([900, 600, 1040, 626], fill=(40, 44, 50))
    _headphone(d, 1150, 580, 110, light=False)
    return img


def yakuin():
    """役員室。机の上に、大きなヘッドホンを付けた小さな試作機。"""
    img = _rgb(base((206, 196, 176), (182, 172, 152)))
    wood_floor(img, FLOOR, col=(110, 80, 60), line=(90, 64, 48))
    d = _d(img)
    _window(d, 780, 110, 1140, 420, sky=(170, 196, 220), frame=(90, 70, 56))
    d.rectangle([760, 640, 1160, 690], fill=(96, 64, 44))                          # 重厚な机
    d.rectangle([780, 690, 1140, 860], fill=(80, 54, 38))
    _pressman(d, 800, 500, 90, 130)
    _headphone(d, 1010, 560, 120, light=False)
    return img


def yakuin0():
    """1978年の役員室。机の上には書類だけ。"""
    img = _rgb(base((206, 196, 176), (182, 172, 152)))
    wood_floor(img, FLOOR, col=(110, 80, 60), line=(90, 64, 48))
    d = _d(img)
    _window(d, 780, 110, 1140, 420, sky=(170, 196, 220), frame=(90, 70, 56))
    d.rectangle([760, 640, 1160, 690], fill=(96, 64, 44))
    d.rectangle([780, 690, 1140, 860], fill=(80, 54, 38))
    for k in range(3):
        d.rectangle([800 + k * 12, 610 - k * 6, 940 + k * 12, 630 - k * 6], fill=(246, 244, 236),
                    outline=(170, 166, 156), width=2)
    _phone(d, 1000, 560)
    return img


def jitaku0():
    """1978年の盛田の家。机の上に、大きなヘッドホンを付けた改造プレスマン。"""
    img = jitaku_base()
    d = _d(img)
    _pressman(d, 820, 510, 90, 130)
    _headphone(d, 1050, 570, 110, light=False)
    return img


def koba():
    """芝浦の職場。作業台に分解したプレスマンと、はんだごて。"""
    img = _rgb(base((214, 216, 212), (190, 192, 188)))
    wood_floor(img, FLOOR, col=(140, 140, 136), line=(120, 120, 116))
    d = _d(img)
    for x in (120, 1500):
        _window(d, x, 130, x + 300, 420, sky=(180, 206, 226), frame=(120, 120, 116))
    d.rectangle([760, 640, 1160, 680], fill=(150, 150, 140))                       # 作業台
    d.rectangle([780, 680, 800, 860], fill=(110, 110, 104))
    d.rectangle([1120, 680, 1140, 860], fill=(110, 110, 104))
    _pressman(d, 800, 500, 100, 136)
    d.rectangle([930, 590, 1010, 636], fill=(40, 120, 70))                         # 基板
    for k in range(6):
        d.rectangle([940 + k * 11, 600, 946 + k * 11, 626], fill=(200, 180, 90))
    d.line([(1030, 600), (1120, 560)], fill=(80, 80, 84), width=10)                # はんだごて
    _headphone(d, 1040, 470, 100, light=False)
    return img


def akiba():
    """秋葉原の電気街。電池や部品の棚が並ぶ店先。"""
    img = _rgb(base((210, 214, 222), (186, 190, 198)))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(120, 120, 126))
    for k, x in enumerate((60, 520, 1000, 1460)):
        d.rectangle([x, 220, x + 400, 760], fill=(150, 140, 130))
        d.rectangle([x + 20, 240, x + 380, 300], fill=((200, 60, 60), (60, 110, 180), (230, 190, 60), (70, 150, 100))[k])
        for r in range(4):
            for c in range(8):
                col = ((220, 200, 80), (200, 80, 60), (80, 120, 200))[(r + c + k) % 3]
                d.rectangle([x + 30 + c * 44, 340 + r * 90, x + 60 + c * 44, 400 + r * 90], fill=col)
    d.rectangle([760, 560, 1160, 620], fill=(236, 230, 214))                       # 電池の台
    for k in range(8):
        d.rounded_rectangle([780 + k * 46, 520, 810 + k * 46, 560], radius=6, fill=(40, 40, 44))
        d.rectangle([780 + k * 46, 520, 810 + k * 46, 530], fill=(220, 190, 60))
    return img


def jitaku_base():
    """盛田の自宅の居間（机まで）。"""
    img = _rgb(base((226, 214, 192), (204, 190, 166)))
    wood_floor(img, FLOOR, col=(150, 110, 76), line=(130, 94, 64))
    d = _d(img)
    for x in (80, 1640):                                                          # 大きなスピーカー
        d.rectangle([x, 380, x + 200, 800], fill=(70, 50, 40))
        d.ellipse([x + 40, 440, x + 160, 560], fill=(40, 30, 26))
        d.ellipse([x + 60, 600, x + 140, 680], fill=(40, 30, 26))
    _window(d, 800, 120, 1120, 400, sky=(186, 206, 226), frame=(120, 90, 66))
    _table(d, 780, 1140, 650, col=(130, 96, 66))
    return img


def jitaku():
    """盛田の自宅の居間。机の上の試作機（差し込み口が2つ）。"""
    img = jitaku_base()
    d = _d(img)
    _walkman(d, 820, 500, 100, 140)
    _headphone(d, 1000, 580, 70, light=True)
    _headphone(d, 1100, 580, 70, light=True)
    return img


def kaigi():
    """1979年の本社の会議室。長机と、真ん中に試作機。"""
    img = _rgb(base((220, 220, 214), (196, 196, 190)))
    wood_floor(img, FLOOR, col=(130, 124, 116), line=(110, 106, 100))
    d = _d(img)
    d.rectangle([700, 120, 1220, 420], fill=(236, 236, 230), outline=(140, 140, 136), width=6)   # 黒板代わりの白板
    for k in range(4):
        d.rectangle([740, 170 + k * 60, 740 + (380 - k * 60), 184 + k * 60], fill=(170, 170, 176))
    d.rectangle([740, 640, 1180, 690], fill=(120, 96, 70))
    d.rectangle([760, 690, 1160, 700], fill=(96, 76, 56))
    _pressman(d, 820, 500, 90, 130)
    _headphone(d, 1060, 560, 110, light=False)
    return img


def zukai():
    """図解。元の録音機から、録音とスピーカーを外して再生専用に。"""
    img = _rgb(base((236, 232, 222), (214, 208, 196)))
    d = _d(img)
    _pressman(d, 620, 220, 220, 300)
    d.line([(650, 240), (810, 500)], fill=(220, 60, 60), width=10)              # 取り去るものに×
    d.line([(810, 240), (650, 500)], fill=(220, 60, 60), width=10)
    d.polygon([(900, 340), (1000, 340), (1000, 310), (1060, 370), (1000, 430), (1000, 400), (900, 400)],
              fill=(150, 140, 120))
    _walkman(d, 1100, 220, 200, 300)
    _headphone(d, 1200, 640, 200, light=True)
    return img


def zukai2():
    """図解。重い大きなヘッドホンと、軽いヘッドホン。"""
    img = _rgb(base((236, 232, 222), (214, 208, 196)))
    d = _d(img)
    _headphone(d, 800, 360, 220, light=False)
    _headphone(d, 1160, 380, 170, light=True)
    d.rectangle([640, 560, 880, 580], fill=(140, 130, 120))                        # はかり
    d.polygon([(700, 580), (820, 580), (840, 640), (680, 640)], fill=(120, 110, 100))
    d.rectangle([1060, 560, 1260, 580], fill=(140, 130, 120))
    d.polygon([(1110, 580), (1210, 580), (1230, 640), (1090, 640)], fill=(120, 110, 100))
    return img


def line():
    """製造ライン。ベルトの上を流れる青い再生機。"""
    img = _rgb(base((222, 226, 226), (198, 202, 202)))
    wood_floor(img, FLOOR, col=(150, 156, 156), line=(130, 136, 136))
    d = _d(img)
    for x in (140, 760, 1380):
        d.rectangle([x, 120, x + 400, 200], fill=(240, 244, 244), outline=(170, 176, 176), width=4)
    d.rectangle([0, 620, W, 660], fill=(60, 64, 70))                               # ベルト
    d.rectangle([0, 660, W, 700], fill=(110, 114, 120))
    for k in range(9):
        _walkman(d, 60 + k * 210, 530, 70, 90)
    return img


def mise():
    """1979年の町の電器店。ラジカセの棚と、カウンターの上の新製品。"""
    img = _rgb(base((232, 226, 212), (210, 202, 186)))
    wood_floor(img, FLOOR, col=(170, 150, 120), line=(150, 130, 100))
    d = _d(img)
    for x in (40, 1480):
        d.rectangle([x, 150, x + 400, 620], fill=(190, 170, 140))
        for r in range(3):
            y = 180 + r * 150
            d.rectangle([x + 10, y + 110, x + 390, y + 120], fill=(150, 130, 100))
            for c in range(2):
                bx = x + 30 + c * 180
                d.rounded_rectangle([bx, y + 20, bx + 160, y + 110], radius=10, fill=(60, 60, 66))
                d.ellipse([bx + 12, y + 36, bx + 62, y + 86], fill=(120, 120, 126))
                d.ellipse([bx + 98, y + 36, bx + 148, y + 86], fill=(120, 120, 126))
    d.rectangle([760, 640, 1160, 690], fill=(236, 230, 214))                       # カウンター
    d.rectangle([780, 690, 1140, 860], fill=(120, 96, 70))
    _walkman(d, 900, 510, 90, 124)
    _headphone(d, 1060, 570, 80, light=True)
    return img


def kuruma():
    """車の後部座席。窓の外を景色が流れる。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (60, 60, 66), (40, 40, 46)), (0, 0))
    d = _d(img)
    for x0 in (120, 1060):                                                         # 窓
        d.rounded_rectangle([x0, 140, x0 + 740, 520], radius=60, fill=(150, 190, 220))
        d.ellipse([x0 + 40, 380, x0 + 400, 560], fill=(110, 150, 100))
        d.ellipse([x0 + 360, 400, x0 + 760, 560], fill=(100, 140, 96))
    d.rectangle([0, 600, W, H], fill=(120, 96, 76))                                # 座席
    d.rounded_rectangle([60, 560, 1860, 700], radius=40, fill=(140, 112, 88))
    d.rounded_rectangle([780, 620, 1140, 700], radius=10, fill=(100, 80, 64))      # 肘掛け
    _walkman(d, 910, 520, 80, 100)
    _headphone(d, 830, 580, 70, light=True)
    _headphone(d, 1080, 580, 70, light=True)
    return img


def senden():
    """宣伝部。ポスター（文字なし）と、机の上の箱。"""
    img = _rgb(base((226, 222, 212), (204, 200, 190)))
    wood_floor(img, FLOOR, col=(150, 140, 126), line=(130, 120, 108))
    d = _d(img)
    for k, x in enumerate((120, 520, 1160, 1560)):
        d.rectangle([x, 140, x + 260, 480], fill=(236, 238, 242), outline=(150, 150, 156), width=4)
        d.rectangle([x + 20, 160, x + 240, 360], fill=((80, 150, 220), (240, 180, 60), (230, 100, 90), (90, 170, 110))[k])
        _walkman(d, x + 90, 200, 80, 110)
    d.rectangle([760, 640, 1160, 690], fill=(140, 120, 96))
    d.rectangle([780, 690, 1140, 860], fill=(120, 100, 80))
    for k in range(3):
        _box(d, 800 + k * 110, 560 - (k % 2) * 30, 100, 70)
    return img


def shiryo():
    """資料。古い本と書類。"""
    img = _rgb(base((238, 234, 224), (212, 206, 194)))
    d = _d(img)
    d.rectangle([560, 110, 1360, 760], fill=(250, 248, 242), outline=(168, 160, 146), width=8)
    d.rectangle([600, 150, 1320, 170], fill=(120, 112, 100))
    for y in range(220, 720, 44):
        w = 700 if (y // 44) % 5 else 420
        d.rectangle([600, y, 600 + w, y + 16], fill=(196, 190, 178))
    return img


def koen():
    """代々木公園。緑と、止まったバス、2人乗りの自転車。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, 600), (150, 200, 236), (210, 228, 236)), (0, 0))
    img.paste(vgrad((W, H - 600), (120, 170, 90), (90, 140, 70)), (0, 600))
    d = _d(img)
    for k in range(9):
        x = 40 + k * 220
        d.rectangle([x + 70, 400, x + 100, 620], fill=(110, 80, 56))
        d.ellipse([x, 220, x + 170, 440], fill=(70, 130, 70))
    d.rounded_rectangle([60, 520, 560, 700], radius=24, fill=(236, 236, 230), outline=(120, 120, 126), width=4)   # バス
    for k in range(5):
        d.rectangle([90 + k * 90, 550, 160 + k * 90, 610], fill=(150, 190, 220))
    for cx in (140, 480):
        d.ellipse([cx - 36, 670, cx + 36, 742], fill=(40, 40, 44))
    for cx in (720, 1080):                                                         # 2人乗りの自転車
        d.ellipse([cx - 44, 760, cx + 44, 848], outline=(40, 40, 44), width=8)
    d.line([(720, 804), (1080, 804)], fill=(200, 60, 60), width=10)
    for k, hx in enumerate((830, 990)):                                          # 乗っている2人
        d.line([(hx, 804), (hx, 730)], fill=(200, 60, 60), width=8)
        d.rounded_rectangle([hx - 26, 640, hx + 26, 730], radius=14, fill=((240, 240, 240), (90, 140, 200))[k])
        d.ellipse([hx - 24, 590, hx + 24, 638], fill=(240, 200, 170))
        d.arc([hx - 30, 580, hx + 30, 630], 190, 350, fill=(150, 156, 166), width=5)
        for sx in (-1, 1):
            d.ellipse([hx + sx * 28 - 10, 604, hx + sx * 28 + 10, 628], fill=ORANGE)
        d.rounded_rectangle([hx - 12, 690, hx + 12, 722], radius=3, fill=BLUE)     # 腰の再生機
    _table(d, 1580, 1820, 640, col=(236, 230, 214))                              # 試聴の台（宣伝部員の右）
    _walkman(d, 1610, 530, 80, 100)
    _headphone(d, 1750, 600, 70, light=True)
    return img


def hokoten():
    """銀座の歩行者天国。真ん中に、試聴用の台。"""
    img = make_ginza()
    d = _d(img)
    d.rectangle([780, 700, 1140, 740], fill=(236, 230, 214))
    d.rectangle([800, 740, 820, 860], fill=(150, 130, 100))
    d.rectangle([1100, 740, 1120, 860], fill=(150, 130, 100))
    for k in range(3):
        _walkman(d, 820 + k * 100, 600, 70, 96)
    _headphone(d, 1080, 660, 70, light=True)
    return img


def marui():
    """若者向けの百貨店の売り場。青い箱が積み上がる。"""
    img = _rgb(base((244, 236, 230), (224, 214, 206)))
    wood_floor(img, FLOOR, col=(190, 170, 150), line=(170, 150, 130))
    d = _d(img)
    d.rectangle([0, 80, W, 150], fill=(200, 50, 60))                               # 赤い帯（文字なし）
    for x in (60, 1500):
        d.rectangle([x, 220, x + 360, 640], fill=(220, 210, 200))
        for r in range(3):
            for c in range(3):
                _box(d, x + 20 + c * 114, 240 + r * 130, 100, 70)
    d.rectangle([760, 640, 1160, 690], fill=(236, 230, 214))
    d.rectangle([780, 690, 1140, 860], fill=(200, 50, 60))
    for k in range(4):
        _box(d, 800 + (k % 2) * 170, 560 - (k // 2) * 76, 150, 72)
    return img


def europe():
    """ヨーロッパのホテルのロビー。"""
    img = _rgb(base((150, 120, 100), (110, 88, 74)))
    d = _d(img)
    for x in range(100, W, 360):
        d.rectangle([x, 120, x + 220, 600], fill=(200, 176, 140))
        d.pieslice([x, 60, x + 220, 280], 180, 360, fill=(200, 176, 140))
        d.rectangle([x + 30, 160, x + 190, 580], fill=(150, 180, 210))
    d.rectangle([0, 760, W, H], fill=(120, 40, 40))
    for lx in (560, 1360):
        d.line([lx, 0, lx, 90], fill=(70, 58, 52), width=6)
        _glow(img, lx, 160, 200, (255, 214, 150), 60)
        d = _d(img)
        for k in range(3):
            d.ellipse([lx - 60 + k * 40, 110, lx - 30 + k * 40, 150], fill=(255, 228, 170))
    _table(d, 780, 1140, 640, col=(90, 60, 40))
    _walkman(d, 900, 510, 90, 124)
    return img


def europe_denwa():
    """ヨーロッパのホテルのロビー。机の上に電話。"""
    img = europe()
    d = _d(img)
    _phone(d, 1020, 560)
    return img


def sekai():
    """暗い地に世界地図の点。日本・アメリカ・イギリス・フランスが光る。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (20, 36, 50), (12, 20, 30)), (0, 0))
    d = _d(img)
    lands = [(330, 330, 300, 170), (470, 700, 130, 190), (960, 330, 140, 110),
             (1010, 620, 160, 210), (1330, 360, 330, 180), (1500, 640, 90, 60),
             (1620, 780, 150, 90), (1590, 400, 30, 60)]
    for y in range(120, 980, 26):
        for x in range(60, 1880, 26):
            for cx, cy, rx, ry in lands:
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1:
                    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(90, 140, 200))
                    break
    for cx, cy in ((1590, 420), (910, 290), (440, 330), (930, 330)):
        _glow(img, cx, cy, 60, (255, 180, 90), 170)
    return img


def gendai():
    """今の売り場。音楽プレーヤーとイヤホン、カセットテープ。"""
    img = _rgb(base((244, 244, 240), (226, 226, 220)))
    wood_floor(img, FLOOR, col=(190, 180, 160), line=(170, 160, 140))
    d = _d(img)
    for row, y in enumerate((180, 400)):
        d.rectangle([600, y + 150, 1320, y + 166], fill=(160, 160, 166))
        for k in range(5):
            x = 640 + k * 136
            if row == 0:
                d.rounded_rectangle([x, y + 20, x + 70, y + 150], radius=10, fill=(40, 40, 46))   # 今のプレーヤー
                d.rectangle([x + 8, y + 32, x + 62, y + 100], fill=(90, 130, 190))
            else:
                d.rectangle([x, y + 70, x + 110, y + 146], fill=(236, 230, 214), outline=(120, 110, 100), width=3)   # カセット
                d.ellipse([x + 20, y + 94, x + 44, y + 118], outline=(80, 80, 84), width=4)
                d.ellipse([x + 66, y + 94, x + 90, y + 118], outline=(80, 80, 84), width=4)
    return img


LOCATIONS = {
    "wm_ima": ima, "wm_ima2": ima2, "wm_kinai": kinai, "wm_yakuin": yakuin, "wm_yakuin0": yakuin0,
    "wm_jitaku0": jitaku0, "wm_koba": koba,
    "wm_akiba": akiba, "wm_jitaku": jitaku, "wm_kaigi": kaigi, "wm_zukai": zukai,
    "wm_zukai2": zukai2, "wm_line": line, "wm_mise": mise, "wm_kuruma": kuruma,
    "wm_senden": senden, "wm_shiryo": shiryo, "wm_koen": koen, "wm_hokoten": hokoten,
    "wm_marui": marui, "wm_europe": europe, "wm_europe_denwa": europe_denwa, "wm_sekai": sekai, "wm_gendai": gendai,
}

CARDS = ["1978", "1979", "1980"]


def year_card(text: str) -> Image.Image:
    """黒地に年号だけのカード。キャラと同居させない単独シーンで使う。"""
    img = Image.new("RGB", (W, H), (18, 18, 20))
    d = _d(img)
    from ytf.config import Config, resolve_font
    Config.load()
    font = ImageFont.truetype(resolve_font("w9"), 150)
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
        if only and f"wm_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"wm_card_{y}.png")
        print(f"生成完了: wm_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
