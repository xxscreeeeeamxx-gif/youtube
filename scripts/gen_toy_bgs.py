#!/usr/bin/env python3
"""トヨタ・豊田喜一郎の再現ドラマ（toyoda-kiichiro）用の背景7種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
★商標に触れないため、車体の意匠・エンブレム・型番などは描かない。
  「車らしきもの」は輪郭だけの箱型にとどめ、特定の車種と読めないようにする。
トーンの設計:
  織機工場     … 木と綿ぼこりの暖色。父の世界。ここが出発点であり、父の死の場所でもある
  アメリカ     … 明るい寒色。広くて天井が高い。よそ行きの緊張
  板囲い       … 倉庫の中に板で囲っただけ。薄暗く、狭い。自動車部の出発点
  鋳物場       … この回の主戦場。赤い炉の光と、床に積まれた屑
  挙母の工場   … 広い。板囲いの反対側にある景色
  争議         … 灰色。人の列と、垂れ幕。ここだけ人の気配を線で描く
  現代         … いちばん明るい

実行: PYTHONPATH=. python3 scripts/gen_toy_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402
from scripts.gen_yam_bgs import _building, _person, _desk  # noqa: E402


def _loom(d, x, y, s=1.0):
    """織機。縦framesと、渡した横糸。意匠は作らず骨組みだけにする。"""
    fr = (122, 96, 62)
    d.rectangle([x, y - 300 * s, x + 26 * s, y], fill=fr)
    d.rectangle([x + 330 * s, y - 300 * s, x + 356 * s, y], fill=fr)
    d.rectangle([x, y - 316 * s, x + 356 * s, y - 286 * s], fill=(146, 116, 76))
    for k in range(9):                       # 縦糸
        gx = x + 40 * s + k * 34 * s
        d.line([gx, y - 286 * s, gx, y - 70 * s], fill=(228, 222, 206),
               width=max(1, int(3 * s)))
    d.rectangle([x + 18 * s, y - 150 * s, x + 338 * s, y - 120 * s],
                fill=(100, 78, 50))          # 筬（おさ）
    d.rectangle([x + 18 * s, y - 70 * s, x + 338 * s, y - 40 * s],
                fill=(214, 206, 186))        # 織り上がった布


def _carbox(d, x, y, s=1.0, body=(92, 100, 112)):
    """車らしき箱。**特定の車種に見せない**ため輪郭と窓と車輪だけ。"""
    d.rounded_rectangle([x, y - 96 * s, x + 300 * s, y - 24 * s], radius=10 * s,
                        fill=body, outline=(52, 58, 68), width=int(5 * s))
    d.rounded_rectangle([x + 70 * s, y - 150 * s, x + 220 * s, y - 92 * s],
                        radius=10 * s, fill=body, outline=(52, 58, 68),
                        width=int(5 * s))
    d.rectangle([x + 86 * s, y - 138 * s, x + 204 * s, y - 100 * s],
                fill=(186, 200, 210))
    for cx in (x + 70 * s, x + 236 * s):
        d.ellipse([cx - 28 * s, y - 52 * s, cx + 28 * s, y + 4 * s],
                  fill=(46, 46, 50), outline=(28, 28, 32), width=int(4 * s))


def _scrap(d, x, y, s=1.0, n=7, seed=0):
    """割れて捨てられた鋳物の山。**この回の看板になる絵**。

    等間隔・同サイズで並べると煉瓦を積んだように見えて「捨てた屑」にならない
    （2026-09-17に一度そうなった）。位置・大きさ・傾きを毎個ばらす。
    乱数は使わず seed からの決め打ちで、実行のたびに絵が変わらないようにする。
    """
    for k in range(n):
        j = (k * 37 + seed * 11) % 23        # 決め打ちのばらつき
        ox = x + (k % 4) * 104 * s + (k // 4) * 38 * s + (j - 11) * 5 * s
        oy = y - (k // 4) * 64 * s + (j % 7 - 3) * 6 * s
        w = (86 + j * 3) * s
        h = (40 + (j % 5) * 9) * s
        tilt = ((j % 9) - 4) * 0.09          # 傾き（ラジアン）
        pts = [(-w / 2, -h / 2), (w / 2, -h / 2 - h * 0.25),
               (w / 2 + w * 0.08, h / 2), (-w / 2 + w * 0.06, h / 2 + h * 0.2)]
        co, si = math.cos(tilt), math.sin(tilt)
        poly = [(ox + px * co - py * si, oy + px * si + py * co) for px, py in pts]
        d.polygon(poly, fill=(150 + (j % 4) * 8, 148 + (j % 4) * 8, 154),
                  outline=(88, 86, 92))
        # 割れ口の線。これがあると「壊れて捨てた物」に見える
        d.line([poly[0], poly[2]], fill=(104, 102, 108), width=max(1, int(3 * s)))


def shokki() -> Image.Image:
    """父の織機工場。木と綿ぼこり。生い立ちと、父の死の場所。"""
    img = vgrad((W, H), (206, 186, 156), (176, 154, 124)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 810, (150, 124, 90), (116, 94, 68))
    for x in (150, 1620):                    # 柱
        d.rectangle([x, 0, x + 54, 810], fill=(128, 102, 68))
    _window(img, d, 620, 120, 1300, 470, (226, 214, 180), (244, 236, 208),
            frame=(112, 88, 58))
    d = ImageDraw.Draw(img)
    _loom(d, 300, 812, 1.0)
    _loom(d, 1180, 812, 1.0)
    for k in range(5):                       # 吊り下げの綿
        d.ellipse([420 + k * 220, 60, 470 + k * 220, 110], fill=(230, 226, 214))
    d.line([960, 0, 960, 210], fill=(84, 72, 56), width=6)
    d.ellipse([928, 210, 992, 274], fill=(252, 238, 190))
    glow(img, 960, 242, 230, (255, 236, 176), 92)
    return img


def ford() -> Image.Image:
    """アメリカの自動車工場。天井が高く、組み立ての列が奥まで続く。"""
    img = vgrad((W, H), (214, 224, 232), (186, 198, 210)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 830, (168, 176, 186), (132, 140, 150))
    for k in range(6):                       # 鉄骨の梁
        d.line([0, 90 + k * 26, W, 40 + k * 26], fill=(150, 160, 172), width=6)
    _window(img, d, 120, 170, 780, 520, (208, 222, 232), (238, 244, 248),
            frame=(120, 130, 142))
    _window(img, d, 1140, 170, 1800, 520, (208, 222, 232), (238, 244, 248),
            frame=(120, 130, 142))
    d = ImageDraw.Draw(img)
    # 組み立ての列（奥へ小さくなる）
    d.polygon([(220, 830), (1700, 830), (1500, 700), (420, 700)],
              fill=(148, 156, 166), outline=(110, 118, 128))
    for k, s in enumerate((1.0, 0.72, 0.52)):
        _carbox(d, 300 + k * 430, 828 - k * 56, s)
    for k in range(4):                       # 吊りチェーン
        d.line([420 + k * 300, 40, 420 + k * 300, 300], fill=(120, 128, 138),
               width=5)
    return img


def itaigakoi() -> Image.Image:
    """倉庫の中に板で囲っただけの自動車部。狭く、薄暗い。"""
    img = vgrad((W, H), (128, 118, 104), (156, 146, 130)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 820, (128, 110, 84), (98, 84, 64))
    # 板囲い（縦板を並べただけ）
    for x in range(90, W - 60, 74):
        d.rectangle([x, 150, x + 62, 820], fill=(158, 128, 88),
                    outline=(118, 94, 62), width=4)
        d.line([x + 10, 200, x + 10, 780], fill=(140, 112, 76), width=3)
    d.rectangle([60, 120, W - 60, 168], fill=(112, 90, 60))
    # 板の隙間から漏れる光
    for x in (470, 1080, 1480):
        d.polygon([(x, 150), (x + 22, 150), (x + 78, 820), (x + 40, 820)],
                  fill=(206, 190, 150))
    _carbox(d, 700, 816, 1.05, body=(104, 96, 88))
    # ばらした部品を並べた台
    _desk(d, 180, 700, 620, 830, (110, 88, 60), (80, 62, 40))
    for k in range(6):
        d.ellipse([210 + k * 62, 664, 252 + k * 62, 700], fill=(120, 124, 132),
                  outline=(86, 90, 98), width=3)
    d.line([1580, 0, 1580, 230], fill=(80, 72, 60), width=6)
    d.ellipse([1548, 230, 1612, 294], fill=(250, 234, 178))
    glow(img, 1580, 262, 240, (255, 230, 160), 104)
    return img


def imono() -> Image.Image:
    """鋳物場。赤い炉の光と、床に積まれた屑。この回の主戦場。"""
    img = vgrad((W, H), (92, 78, 72), (128, 104, 92)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 840, (110, 92, 80), (80, 66, 58))
    for x in (120, 1660):
        d.rectangle([x, 0, x + 60, 840], fill=(96, 80, 70))
    # 炉
    d.rounded_rectangle([760, 300, 1160, 840], radius=26, fill=(88, 72, 64),
                        outline=(62, 50, 44), width=8)
    d.rounded_rectangle([830, 430, 1090, 690], radius=18, fill=(238, 132, 48),
                        outline=(196, 88, 28), width=8)
    d.rounded_rectangle([866, 470, 1054, 650], radius=14, fill=(255, 224, 140))
    glow(img, 960, 560, 440, (255, 150, 40), 150)
    d = ImageDraw.Draw(img)
    d.rectangle([700, 180, 1220, 240], fill=(78, 64, 56))   # 煙道
    d.rectangle([930, 0, 990, 200], fill=(78, 64, 56))
    # 砂型の箱
    for k in range(3):
        d.rectangle([250 + k * 150, 690, 370 + k * 150, 800],
                    fill=(138, 116, 86), outline=(98, 80, 58), width=5)
    _scrap(d, 1210, 790, 1.0, 14, seed=1)            # 捨てた9割。右手前に山積み
    _scrap(d, 170, 830, 0.82, 10, seed=5)             # 左にも。床が屑で埋まっている画にする
    return img


def kouba() -> Image.Image:
    """挙母の工場。広い。板囲いの反対側にある景色。"""
    img = vgrad((W, H), (198, 212, 224), (170, 186, 202)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 840, (156, 164, 172), (120, 128, 138))
    _building(d, 60, 300, 520, 840, (150, 152, 158), (112, 114, 120))
    _building(d, 1420, 260, 1860, 840, (144, 148, 156), (106, 110, 118))
    for k in range(7):                       # のこぎり屋根
        x = 520 + k * 130
        d.polygon([(x, 340), (x + 130, 340), (x + 130, 260), (x + 66, 260)],
                  fill=(160, 166, 174), outline=(120, 126, 134))
        d.polygon([(x + 66, 260), (x + 130, 260), (x + 130, 340)],
                  fill=(206, 222, 234))
    d.rectangle([520, 340, 1430, 840], fill=(166, 172, 180),
                outline=(124, 130, 138), width=6)
    _window(img, d, 580, 430, 1370, 640, (196, 212, 224), (232, 240, 246),
            frame=(128, 134, 142))
    d = ImageDraw.Draw(img)
    _carbox(d, 620, 836, 1.0, body=(86, 104, 120))
    _carbox(d, 1020, 836, 1.0, body=(104, 92, 84))
    return img


def sougi() -> Image.Image:
    """1950年の争議。灰色。人の列と、垂れ幕。"""
    img = vgrad((W, H), (150, 150, 154), (120, 120, 126)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 850, (128, 128, 134), (96, 96, 102))
    _building(d, 0, 180, 700, 850, (132, 134, 140), (98, 100, 106))
    _building(d, 1240, 150, 1920, 850, (126, 128, 134), (94, 96, 102))
    d.rectangle([700, 260, 1240, 850], fill=(140, 142, 148),
                outline=(104, 106, 112), width=6)
    # 垂れ幕（文字は描かない。線だけで示す）
    for k, x in enumerate((780, 900, 1020, 1140)):
        d.rectangle([x, 300, x + 64, 640], fill=(226, 226, 228),
                    outline=(150, 150, 154), width=4)
        for r in range(5):
            d.line([x + 16, 340 + r * 56, x + 48, 340 + r * 56],
                   fill=(120, 120, 126), width=6)
    # **_person の第4引数は高さ(px)。倍率ではない**（0.82を渡して消えた 2026-09-17）
    for k in range(10):                      # 手前の列（大きい）
        _person(d, 180 + k * 176, 852, 196, (76, 78, 86))
    for k in range(13):                      # 奥の列（小さくして厚みを出す）
        _person(d, 120 + k * 142, 792, 132, (100, 102, 110))
    return img


def ima() -> Image.Image:
    """現代。明るい駐車場。いちばん明るい絵にする。"""
    img = vgrad((W, H), (214, 232, 244), (188, 212, 230)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 820, (176, 182, 188), (142, 148, 156))
    for k in range(4):                       # 遠景のビル
        _building(d, 80 + k * 470, 260 + (k % 2) * 70, 420 + k * 470, 820,
                  (176, 190, 202), (140, 154, 168))
    # 駐車枠
    for k in range(5):
        d.line([180 + k * 380, 830, 120 + k * 380, H], fill=(236, 240, 244),
               width=8)
    _carbox(d, 320, 900, 1.25, body=(74, 108, 150))
    _carbox(d, 1180, 900, 1.25, body=(180, 186, 192))
    glow(img, 1640, 150, 420, (255, 246, 210), 96)
    return img


PAINTERS = {
    "il_toy_shokki": shokki,
    "il_toy_ford": ford,
    "il_toy_itaigakoi": itaigakoi,
    "il_toy_imono": imono,
    "il_toy_kouba": kouba,
    "il_toy_sougi": sougi,
    "il_toy_ima": ima,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
