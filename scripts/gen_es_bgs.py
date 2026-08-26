#!/usr/bin/env python3
"""非常口マークの再現ドラマ（exit-sign）用のイラスト背景13種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
惨事の場面は暗く低彩度、デザインの場面は白い紙の明るさ、で章のトーンを分けている。
実行: PYTHONPATH=. python3 scripts/gen_es_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402

GREEN = (30, 150, 90)


def _exit_sign(d, x, y, w=180, h=96, lit=True):
    """緑の誘導標識を1枚。人影は簡略なシルエットで描く（正確な複製ではない）。"""
    body = GREEN if lit else (28, 62, 46)
    ink = (238, 246, 240) if lit else (140, 156, 148)
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=body,
                        outline=(18, 90, 56), width=4)
    cx, cy = x + w * 0.42, y + h * 0.52
    s = h / 96.0
    d.ellipse([cx - 9 * s, cy - 30 * s, cx + 9 * s, cy - 12 * s], fill=ink)   # 頭
    d.polygon([(cx - 14 * s, cy - 10 * s), (cx + 10 * s, cy - 14 * s),
               (cx + 4 * s, cy + 10 * s), (cx - 18 * s, cy + 6 * s)], fill=ink)
    d.polygon([(cx + 2 * s, cy + 6 * s), (cx + 20 * s, cy + 26 * s),
               (cx + 10 * s, cy + 30 * s), (cx - 6 * s, cy + 14 * s)], fill=ink)
    d.polygon([(cx - 16 * s, cy + 2 * s), (cx - 6 * s, cy + 26 * s),
               (cx - 18 * s, cy + 30 * s), (cx - 26 * s, cy + 8 * s)], fill=ink)
    # ドア枠
    d.rectangle([x + w * 0.66, y + h * 0.18, x + w * 0.90, y + h * 0.86], fill=ink)
    d.rectangle([x + w * 0.72, y + h * 0.26, x + w * 0.90, y + h * 0.78], fill=body)


def _kanji_sign(d, x, y, w=150, h=54):
    """1970年代の「非常口」表示。小さく、文字だけ、白地に赤。"""
    d.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=(238, 234, 228),
                        outline=(150, 146, 140), width=3)
    for k in range(3):
        bx = x + 16 + k * (w - 40) / 3.0
        d.rectangle([bx, y + 14, bx + (w - 46) / 3.0, y + h - 14],
                    fill=(196, 60, 50))


# ---------------------------------------------------------------- 惨事の側
def depart() -> Image.Image:
    """1972年、夜のデパートの売り場。華やかだが表示は文字だけで小さい。"""
    img = vgrad((W, H), (196, 178, 152), (172, 154, 130)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 760, (150, 128, 104), (128, 108, 86))
    # 天井の照明
    for k in range(5):
        d.rounded_rectangle([180 + k * 360, 90, 420 + k * 360, 130], radius=10,
                            fill=(248, 240, 214))
        glow(img, 300 + k * 360, 118, 260, (255, 240, 190), 46)
    d = ImageDraw.Draw(img, "RGBA")
    # 陳列棚とマネキン台
    for k in range(3):
        x = 120 + k * 560
        d.rounded_rectangle([x, 470, x + 400, 780], radius=8, fill=(206, 190, 168))
        d.rectangle([x, 470, x + 400, 508], fill=(184, 166, 142))
        for r in range(2):
            d.rectangle([x + 24, 540 + r * 110, x + 376, 552 + r * 110],
                        fill=(178, 160, 138))
            for j in range(4):
                d.rounded_rectangle([x + 40 + j * 84, 500 + r * 110,
                                     x + 100 + j * 84, 540 + r * 110],
                                    radius=6, fill=(150 + j * 18, 120, 110))
    # 小さすぎる非常口表示（梁の上のほう）
    _kanji_sign(d, 1560, 180)
    return img


def kemuri() -> Image.Image:
    """煙に満ちた通路。文字の表示は煙に沈んで読めない。"""
    img = vgrad((W, H), (58, 54, 52), (34, 32, 32)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 790, (46, 42, 42), (36, 33, 33))
    # 奥へ続く壁
    d.polygon([(0, 120), (620, 330), (620, 800), (0, 980)], fill=(64, 58, 56))
    d.polygon([(W, 120), (1300, 330), (1300, 800), (W, 980)], fill=(64, 58, 56))
    d.rectangle([620, 330, 1300, 800], fill=(48, 44, 44))
    # 読めない文字表示
    _kanji_sign(d, 890, 380, 120, 44)
    # 逃げ口の扉（煙の向こうにかろうじて見える）
    d.rounded_rectangle([900, 420, 1020, 800], radius=4, fill=(70, 62, 58))
    # 煙。輪郭が出ると輪に見えるので、必ずぼかしてから重ねる
    from PIL import ImageFilter
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for k in range(9):
        y = 40 + k * 88
        a = 26 + k * 10
        ld.ellipse([-360 + (k % 3) * 220, y, W + 260 - (k % 4) * 150, y + 300],
                   fill=(190, 184, 176, a))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(70)))
    # 上ほど濃くたまる（煙は天井から下りてくる）
    top = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(top).rectangle([0, 0, W, 430], fill=(196, 190, 182, 150))
    img.alpha_composite(top.filter(ImageFilter.GaussianBlur(110)))
    return img


def hotel() -> Image.Image:
    """1982年、ホテルの夜の廊下。赤い絨毯と扉が並ぶ。"""
    img = vgrad((W, H), (62, 46, 46), (40, 30, 30)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 806, W, H], fill=(112, 46, 44))
    for k in range(9):
        d.line([k * 240, 806, k * 240 - 120, H], fill=(96, 38, 36), width=6)
    d.polygon([(0, 100), (560, 300), (560, 820), (0, 1000)], fill=(76, 60, 58))
    d.polygon([(W, 100), (1360, 300), (1360, 820), (W, 1000)], fill=(76, 60, 58))
    d.rectangle([560, 300, 1360, 820], fill=(58, 46, 44))
    for k, x in enumerate((120, 470, 1450)):
        d.rounded_rectangle([x, 380, x + 210, 810], radius=6, fill=(92, 66, 54),
                            outline=(66, 48, 40), width=5)
        d.ellipse([x + 170, 590, x + 194, 614], fill=(200, 180, 120))
    # 壁付けの照明
    for x in (620, 1240):
        d.rounded_rectangle([x, 380, x + 60, 430], radius=8, fill=(210, 190, 140))
        glow(img, x + 30, 405, 190, (255, 224, 160), 60)
    d = ImageDraw.Draw(img, "RGBA")
    _kanji_sign(d, 900, 330, 120, 44)
    return img


# ---------------------------------------------------------------- 役所・審査
def shobo() -> Image.Image:
    """消防庁の会議室。灰色、長机、資料の山。"""
    img = vgrad((W, H), (188, 190, 196), (162, 164, 172)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 740, (140, 138, 144), (120, 118, 124))
    d.rectangle([0, 700, W, 748], fill=(150, 148, 154))
    # 掲示板
    d.rounded_rectangle([120, 170, 780, 560], radius=6, fill=(206, 202, 194),
                        outline=(140, 136, 130), width=8)
    for r in range(3):
        for c in range(4):
            d.rectangle([160 + c * 150, 210 + r * 116, 270 + c * 150,
                         300 + r * 116], fill=(240, 238, 232))
    # 窓
    _window(img, d, 1180, 180, 1740, 520, (176, 194, 214), (216, 226, 236))
    d = ImageDraw.Draw(img, "RGBA")
    # 長机と書類
    d.rounded_rectangle([200, 760, 1720, 900], radius=8, fill=(150, 136, 112))
    d.rectangle([200, 760, 1720, 796], fill=(132, 118, 96))
    for k in range(4):
        d.rounded_rectangle([300 + k * 340, 706, 470 + k * 340, 764], radius=4,
                            fill=(244, 242, 238), outline=(200, 196, 190), width=3)
    return img


def koubo() -> Image.Image:
    """公募の審査会場。応募作が壁一面に並ぶ。"""
    img = vgrad((W, H), (216, 214, 208), (190, 188, 182)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 800, (160, 152, 140), (138, 130, 120))
    # パネルに貼られた大量の応募作。全部そっくりだと色見本に見えるので、
    # 案ごとに地色も中の図形も変える（人型・扉・矢印・文字だけ、が混ざる想定）
    pal = [(206, 62, 54), (56, 116, 178), (46, 148, 96), (226, 178, 56),
           (86, 78, 150), (216, 116, 60), (60, 140, 152)]
    for r in range(4):
        for c in range(9):
            i = r * 9 + c
            x, y = 90 + c * 200, 130 + r * 168
            col = pal[i % len(pal)]
            d.rounded_rectangle([x, y, x + 156, y + 128], radius=4,
                                fill=(248, 248, 244), outline=(178, 176, 170), width=3)
            d.rectangle([x + 18, y + 20, x + 138, y + 108], fill=col)
            k = i % 4
            ink = (250, 250, 246)
            if k == 0:            # 人型
                d.ellipse([x + 62, y + 32, x + 82, y + 52], fill=ink)
                d.polygon([(x + 56, y + 56), (x + 90, y + 56), (x + 80, y + 96),
                           (x + 64, y + 96)], fill=ink)
            elif k == 1:          # 扉
                d.rectangle([x + 58, y + 32, x + 100, y + 98], fill=ink)
                d.rectangle([x + 66, y + 40, x + 100, y + 90], fill=col)
            elif k == 2:          # 矢印
                d.polygon([(x + 40, y + 54), (x + 88, y + 54), (x + 88, y + 38),
                           (x + 120, y + 64), (x + 88, y + 90), (x + 88, y + 74),
                           (x + 40, y + 74)], fill=ink)
            else:                 # 文字だけの案
                for j in range(3):
                    d.rectangle([x + 34 + j * 32, y + 44, x + 58 + j * 32, y + 84],
                                fill=ink)
    return img


def shiken() -> Image.Image:
    """視認性の実験室。暗室にスクリーン、煙、測定席。"""
    img = vgrad((W, H), (38, 42, 50), (24, 26, 34)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 780, (44, 46, 54), (34, 36, 42))
    # 投影スクリーン
    d.rounded_rectangle([560, 150, 1400, 640], radius=8, fill=(230, 232, 228),
                        outline=(120, 124, 132), width=8)
    _exit_sign(d, 830, 320, 300, 160)
    glow(img, 980, 400, 460, (90, 230, 150), 46)
    d = ImageDraw.Draw(img, "RGBA")
    # 煙の層（薄く）
    for k in range(4):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse([-200, 300 + k * 130, W + 200, 500 + k * 130],
                                    fill=(180, 184, 190, 26))
        img.alpha_composite(lay)
    d = ImageDraw.Draw(img, "RGBA")
    # 測定席
    for x in (160, 1600):
        d.rounded_rectangle([x, 700, x + 200, 900], radius=8, fill=(58, 62, 72))
        d.rectangle([x + 20, 720, x + 180, 800], fill=(40, 70, 60))
        d.ellipse([x + 150, 820, x + 180, 850], fill=(120, 220, 150))
    return img


def iso() -> Image.Image:
    """ISOの国際会議場。円卓と各国の名札、演台。"""
    img = vgrad((W, H), (72, 84, 104), (48, 56, 72)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 760, (66, 60, 72), (52, 48, 58))
    # 背面の壁と旗の列（旗は無地の色面にとどめる）
    d.rectangle([0, 120, W, 700], fill=(60, 70, 88))
    for k in range(7):
        x = 180 + k * 250
        d.line([x + 40, 170, x + 40, 520], fill=(150, 156, 170), width=6)
        cols = [(180, 60, 60), (60, 90, 170), (220, 220, 220), (70, 150, 90),
                (200, 170, 70), (150, 80, 160), (90, 160, 180)][k]
        d.polygon([(x + 46, 180), (x + 190, 210), (x + 190, 330), (x + 46, 300)],
                  fill=cols)
    # 円卓
    d.ellipse([260, 720, 1660, 1060], fill=(120, 96, 72), outline=(92, 72, 54), width=8)
    d.ellipse([420, 770, 1500, 1010], fill=(138, 112, 84))
    for k in range(6):
        a = math.radians(200 + k * 28)
        cx = 960 + math.cos(a) * 620
        cy = 890 + math.sin(a) * 150
        d.rounded_rectangle([cx - 60, cy - 22, cx + 60, cy + 16], radius=4,
                            fill=(238, 236, 230))
    return img


# ---------------------------------------------------------------- デザインの側
def atelier() -> Image.Image:
    """太田のデザイン事務所。製図台、トレース紙、ポスター。"""
    img = vgrad((W, H), (222, 216, 204), (198, 192, 180)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 780, (166, 146, 118), (142, 124, 100))
    # ポスターの壁
    for k, (x, col) in enumerate(((140, (200, 80, 70)), (400, (60, 110, 180)),
                                  (660, (230, 190, 70)))):
        d.rounded_rectangle([x, 140, x + 200, 430], radius=6, fill=(246, 244, 240),
                            outline=(190, 186, 180), width=4)
        d.ellipse([x + 40, 190, x + 160, 310], fill=col)
        d.rectangle([x + 40, 340, x + 160, 356], fill=(120, 118, 114))
        d.rectangle([x + 40, 374, x + 120, 388], fill=(150, 148, 144))
    _window(img, d, 1300, 160, 1800, 470, (180, 200, 220), (224, 232, 240))
    d = ImageDraw.Draw(img, "RGBA")
    # 製図台（傾いた天板）
    d.polygon([(560, 800), (1360, 800), (1300, 560), (620, 560)],
              fill=(240, 238, 232), outline=(190, 186, 180), width=6)
    d.polygon([(700, 760), (1220, 760), (1180, 600), (740, 600)], fill=(252, 252, 250))
    for k in range(3):
        d.line([760 + k * 20, 740, 800 + k * 20, 620], fill=(180, 184, 190), width=3)
    d.rounded_rectangle([640, 800, 1340, 860], radius=6, fill=(150, 128, 100))
    # ペン立て
    d.rounded_rectangle([1420, 700, 1520, 800], radius=8, fill=(120, 116, 110))
    for k in range(4):
        d.line([1440 + k * 20, 700, 1436 + k * 20, 640], fill=(60 + k * 40, 90, 140),
               width=8)
    return img


def daigaku() -> Image.Image:
    """美大の教室。イーゼルと石膏、大きな窓。"""
    img = vgrad((W, H), (226, 222, 212), (200, 196, 186)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 790, (172, 152, 124), (148, 130, 106))
    _window(img, d, 1120, 130, 1820, 560, (186, 206, 226), (228, 236, 244))
    d = ImageDraw.Draw(img, "RGBA")
    # イーゼル3台。脚だけだと棒に見えるので、受け木と描きかけの絵まで入れる
    for k, x in enumerate((150, 520, 890)):
        d.line([x + 60, 830, x + 96, 300], fill=(146, 120, 90), width=14)
        d.line([x + 250, 830, x + 118, 300], fill=(146, 120, 90), width=14)
        d.line([x + 150, 300, x + 176, 870], fill=(126, 102, 76), width=12)
        d.rounded_rectangle([x + 20, 560, x + 260, 592], radius=6, fill=(158, 132, 100))
        d.rounded_rectangle([x + 34, 330, x + 250, 566], radius=4, fill=(250, 248, 244),
                            outline=(196, 192, 186), width=5)
        if k == 0:
            d.ellipse([x + 90, 380, x + 196, 486], outline=(140, 142, 150), width=6)
            d.line([x + 90, 520, x + 196, 520], fill=(170, 172, 178), width=5)
        elif k == 1:
            for j in range(3):
                d.rectangle([x + 70 + j * 60, 380, x + 110 + j * 60, 520],
                            fill=(196, 170, 140 + j * 20))
        else:
            d.polygon([(x + 80, 520), (x + 142, 370), (x + 204, 520)],
                      fill=(150, 168, 190))
    # 石膏像の台
    d.rounded_rectangle([1300, 640, 1480, 830], radius=6, fill=(196, 192, 184))
    d.ellipse([1330, 540, 1450, 660], fill=(240, 238, 232))
    return img


def venezia() -> Image.Image:
    """ベニス。運河と建物、ゴンドラ。留学時代。"""
    img = vgrad((W, H), (196, 216, 234), (232, 224, 204)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 700, W, H], fill=(96, 140, 150))
    for k in range(9):
        d.line([0, 740 + k * 40, W, 740 + k * 40], fill=(112, 156, 164), width=5)
    # 建物の列
    for k, x in enumerate((60, 380, 700, 1080, 1440)):
        hgt = 300 + (k % 3) * 90
        col = [(214, 168, 130), (198, 146, 118), (222, 188, 150),
               (204, 158, 124), (216, 176, 140)][k]
        d.rectangle([x, 700 - hgt, x + 280, 700], fill=col)
        d.rectangle([x, 700 - hgt, x + 280, 700 - hgt + 24], fill=(178, 130, 104))
        for r in range(2):
            for c in range(3):
                d.rounded_rectangle([x + 40 + c * 80, 700 - hgt + 70 + r * 110,
                                     x + 90 + c * 80, 700 - hgt + 160 + r * 110],
                                    radius=22, fill=(92, 106, 120))
    # ゴンドラ
    d.polygon([(700, 900), (1200, 900), (1120, 950), (760, 950)], fill=(40, 42, 48))
    d.line([760, 900, 720, 800], fill=(60, 56, 52), width=8)
    return img


def jitaku() -> Image.Image:
    """夜の自宅の机。スタンドの下でスケッチを重ねる。"""
    img = vgrad((W, H), (54, 52, 62), (36, 34, 44)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 800, (72, 58, 48), (58, 46, 38))
    d.rounded_rectangle([380, 760, 1540, 900], radius=8, fill=(120, 96, 70))
    d.rectangle([380, 760, 1540, 796], fill=(102, 82, 60))
    # スタンドライト
    d.line([1330, 760, 1330, 500], fill=(90, 94, 104), width=10)
    d.polygon([(1240, 500), (1420, 500), (1390, 430), (1270, 430)],
              fill=(120, 126, 138))
    glow(img, 1170, 700, 520, (255, 226, 160), 66)
    d = ImageDraw.Draw(img, "RGBA")
    # 重ねたスケッチ
    for k in range(4):
        d.rounded_rectangle([620 + k * 24, 690 - k * 12, 1040 + k * 24, 790 - k * 12],
                            radius=4, fill=(246, 242, 232), outline=(190, 184, 172),
                            width=3)
    d.ellipse([760, 700, 820, 760], fill=(180, 184, 190))
    return img


# ---------------------------------------------------------------- 現代
def machi1982() -> Image.Image:
    """1982年、標識を取り替える現場。脚立と古い表示の箱。"""
    img = vgrad((W, H), (200, 202, 206), (176, 176, 182)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 800, (146, 144, 150), (126, 124, 130))
    d.rectangle([0, 140, W, 800], fill=(190, 188, 190))
    for k in range(6):
        d.line([320 * k, 140, 320 * k, 800], fill=(176, 174, 178), width=6)
    # 新しい標識（点灯）と、外された古い表示
    _exit_sign(d, 1420, 250, 220, 118)
    glow(img, 1530, 310, 320, (90, 230, 150), 46)
    d = ImageDraw.Draw(img, "RGBA")
    _kanji_sign(d, 300, 700, 170, 62)
    # 脚立
    d.line([1180, 860, 1300, 420], fill=(190, 160, 70), width=14)
    d.line([1420, 860, 1310, 420], fill=(190, 160, 70), width=14)
    for k in range(3):
        d.line([1216 + k * 12, 760 - k * 110, 1390 - k * 12, 760 - k * 110],
               fill=(200, 172, 84), width=10)
    return img


def ima() -> Image.Image:
    """現代の駅の通路。緑の誘導標識が光っている。"""
    img = vgrad((W, H), (222, 226, 232), (198, 202, 210)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 820, (176, 178, 184), (156, 158, 164))
    d.polygon([(0, 150), (620, 340), (620, 830), (0, 1010)], fill=(210, 214, 220))
    d.polygon([(W, 150), (1300, 340), (1300, 830), (W, 1010)], fill=(210, 214, 220))
    d.rectangle([620, 340, 1300, 830], fill=(196, 200, 208))
    # 天井の照明
    for k in range(4):
        d.rounded_rectangle([700 + k * 130, 300, 780 + k * 130, 320], radius=6,
                            fill=(250, 250, 244))
    # 誘導標識
    _exit_sign(d, 1330, 300, 210, 112)
    glow(img, 1435, 356, 300, (90, 230, 150), 52)
    d = ImageDraw.Draw(img, "RGBA")
    # 案内サインの柱
    d.rounded_rectangle([500, 360, 560, 830], radius=6, fill=(150, 154, 162))
    d.rounded_rectangle([380, 380, 660, 480], radius=8, fill=(60, 90, 150))
    for r in range(2):
        d.rectangle([410, 404 + r * 34, 630, 420 + r * 34], fill=(230, 234, 240))
    return img


PAINTERS = {
    "il_es_depart": depart,
    "il_es_kemuri": kemuri,
    "il_es_hotel": hotel,
    "il_es_shobo": shobo,
    "il_es_koubo": koubo,
    "il_es_shiken": shiken,
    "il_es_iso": iso,
    "il_es_atelier": atelier,
    "il_es_daigaku": daigaku,
    "il_es_venezia": venezia,
    "il_es_jitaku": jitaku,
    "il_es_machi1982": machi1982,
    "il_es_ima": ima,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
