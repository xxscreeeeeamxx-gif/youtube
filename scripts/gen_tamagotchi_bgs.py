#!/usr/bin/env python3
"""たまごっちの誕生・横井昭裕回（60_たまごっちの誕生 / slug=tamagotchi-yokoi）の背景を生成する。
作り直し版（84_たまごっちの誕生 / slug=tamagotchi-yokoi-v2）の差し替え背景と2009年の事務所もここで描く。
既存の絵を描き直さないよう、作り直し版の分は名前を指定して実行する:
  PYTHONPATH=. python scripts/gen_tamagotchi_bgs.py tg_bandai_botsu tg_wiz_chirashi tg_kaigi_kazu \
      tg_mise_retsu tg_soko_yama tg_wiz2009

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針は鉛筆回（gen_pencil_bgs.py）と同じ。
実在メーカーの商標（ロゴ・商品名の文字）と、実在キャラクターの絵柄は描かない。
卵形の携帯ゲーム機と、中の生き物は、この回用に描いた汎用の形にとどめる。

実行: PYTHONPATH=. python scripts/gen_tamagotchi_bgs.py [名前...]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)
LCD = (186, 200, 170)         # 白黒液晶の地の色
INK = (40, 46, 40)            # 液晶の点の色

# 中の生き物（この回用の架空の形。8×8の点）
BLOB = [
    "..####..",
    ".######.",
    "##.##.##",
    "########",
    "##....##",
    ".######.",
    ".##..##.",
    "........",
]


def _d(img):
    return ImageDraw.Draw(img)


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


def _font(size):
    from ytf.config import Config, resolve_font
    Config.load()
    return ImageFont.truetype(resolve_font("w9"), size)


def _window(d, x0, y0, x1, y1, sky=(176, 210, 232), frame=(70, 62, 56)):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


def _table(d, x0, x1, y, col=(150, 116, 80)):
    d.rectangle([x0, y, x1, y + 40], fill=col)
    d.rectangle([x0 + 20, y + 40, x0 + 40, y + 190], fill=tuple(int(c * 0.8) for c in col))
    d.rectangle([x1 - 40, y + 40, x1 - 20, y + 190], fill=tuple(int(c * 0.8) for c in col))


def _pix(d, x, y, cell, pattern=BLOB, col=INK):
    for r, row in enumerate(pattern):
        for c, ch in enumerate(row):
            if ch == "#":
                d.rectangle([x + c * cell, y + r * cell, x + (c + 1) * cell - 1, y + (r + 1) * cell - 1], fill=col)


def _egg(d, cx, cy, h, col=(236, 120, 150), chain=True):
    """卵形の携帯ゲーム機（文字なし）。cx, cy は中心、h は高さ。"""
    w = h * 0.82
    top = cy - h / 2
    d.ellipse([cx - w / 2, top + h * 0.12, cx + w / 2, top + h], fill=col,
              outline=tuple(int(c * 0.7) for c in col), width=max(2, int(h / 60)))
    d.ellipse([cx - w * 0.38, top, cx + w * 0.38, top + h * 0.6], fill=col)
    sw, sh = w * 0.46, h * 0.26
    sx, sy = cx - sw / 2, top + h * 0.34
    d.rounded_rectangle([sx - 6, sy - 6, sx + sw + 6, sy + sh + 6], radius=6, fill=(250, 248, 240))
    d.rectangle([sx, sy, sx + sw, sy + sh], fill=LCD)
    cell = max(1, int(sh / 10))
    _pix(d, int(cx - cell * 4), int(sy + sh / 2 - cell * 4), cell)
    for k in (-1, 0, 1):
        bx, by = cx + k * w * 0.2, top + h * 0.78 + (0 if k else h * 0.04)
        r = h * 0.045
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(250, 214, 80), outline=(160, 130, 40), width=2)
    if chain:
        for k in range(7):
            d.ellipse([cx - 4 + (k - 3) * 9, top - 34 + abs(k - 3) * 9, cx + 4 + (k - 3) * 9, top - 26 + abs(k - 3) * 9],
                      fill=(190, 190, 196))


def _box(d, x, y, w, h, erased=True):
    """段ボール箱。商品名は消してある（白い紙を貼った跡）。"""
    d.rectangle([x, y, x + w, y + h], fill=(196, 160, 110), outline=(140, 110, 70), width=3)
    d.line([(x, y + h * 0.3), (x + w, y + h * 0.3)], fill=(160, 126, 80), width=3)
    if erased:
        d.rectangle([x + w * 0.2, y + h * 0.45, x + w * 0.8, y + h * 0.75], fill=(236, 232, 222))


def _shelf(d, x0, x1, y, col=(120, 96, 72)):
    d.rectangle([x0, y, x1, y + 16], fill=col)


def ima():
    """今の居間。机の上に卵形のゲーム機。"""
    img = _rgb(base((236, 232, 222), (214, 208, 196)))
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    d = _d(img)
    _window(d, 740, 110, 1180, 400)
    _table(d, 760, 1160, 660)
    _egg(d, 960, 570, 150, (236, 236, 232))
    d.ellipse([1060, 630, 1120, 656], fill=(200, 80, 60))       # お菓子の皿
    d.ellipse([800, 624, 880, 660], fill=(230, 230, 236))
    return img


def bandai():
    """1977年のおもちゃ会社の企画室。机の上にびっしり書いたノートと小さな液晶ゲーム。"""
    img = _rgb(base((226, 222, 204), (206, 200, 180)))
    wood_floor(img, FLOOR, col=(120, 100, 80), line=(100, 84, 66))
    d = _d(img)
    for x in (60, 1500):                                                   # 両側の棚とおもちゃ
        d.rectangle([x, 220, x + 360, 760], fill=(150, 120, 90))
        for r in range(4):
            _shelf(d, x, x + 360, 330 + r * 110)
            for k in range(3):
                c = ((200, 60, 60), (60, 90, 170), (230, 190, 60))[(r + k) % 3]
                if r % 2:
                    d.rectangle([x + 30 + k * 110, 270 + r * 110, x + 100 + k * 110, 330 + r * 110], fill=c)
                else:
                    d.rounded_rectangle([x + 30 + k * 110, 290 + r * 110, x + 110 + k * 110, 330 + r * 110], radius=10, fill=c)
                    d.ellipse([x + 38 + k * 110, 318 + r * 110, x + 58 + k * 110, 338 + r * 110], fill=(30, 30, 30))
                    d.ellipse([x + 82 + k * 110, 318 + r * 110, x + 102 + k * 110, 338 + r * 110], fill=(30, 30, 30))
    _window(d, 760, 120, 1160, 380, sky=(170, 196, 214))
    _table(d, 760, 1160, 640, col=(110, 96, 84))
    d.polygon([(800, 632), (960, 612), (980, 640), (820, 660)], fill=(250, 248, 238))  # 開いたノート
    d.polygon([(960, 612), (1100, 604), (1110, 632), (980, 640)], fill=(244, 242, 232))
    for k in range(6):
        d.line([(812 + k * 2, 622 + k * 6), (956 + k * 2, 604 + k * 6)], fill=(90, 90, 110), width=2)
        d.line([(968 + k * 2, 612 + k * 5), (1098 + k * 2, 604 + k * 5)], fill=(90, 90, 110), width=2)
    d.rounded_rectangle([1112, 596, 1150, 636], radius=6, fill=(60, 60, 70))       # 小さな液晶ゲーム
    d.rectangle([1118, 602, 1144, 618], fill=LCD)
    return img


def _office_base(wall=(232, 228, 216), floor=(150, 140, 126)):
    img = _rgb(base(wall, tuple(max(0, c - 18) for c in wall)))
    wood_floor(img, FLOOR, col=floor, line=tuple(max(0, c - 20) for c in floor))
    d = _d(img)
    for x in (80, 1480):                                                   # 両側の机と紙の山
        d.rectangle([x, 620, x + 360, 660], fill=(160, 150, 136))
        d.rectangle([x + 20, 660, x + 40, 800], fill=(120, 112, 100))
        d.rectangle([x + 320, 660, x + 340, 800], fill=(120, 112, 100))
        for k in range(4):
            d.rectangle([x + 40 + k * 70, 580 - k * 6, x + 100 + k * 70, 620], fill=(244, 240, 228), outline=(180, 176, 166))
    return img


def _tank(d, x0, y0, x1, y1):
    d.rectangle([x0 - 10, y1, x1 + 10, y1 + 140], fill=(90, 80, 70))       # 台
    d.rectangle([x0, y0, x1, y1], fill=(120, 190, 210), outline=(60, 70, 80), width=6)
    d.rectangle([x0 + 6, y1 - 40, x1 - 6, y1 - 6], fill=(214, 200, 160))  # 砂
    for k, (fx, fy, c) in enumerate(((x0 + 80, y0 + 70, (240, 140, 40)), (x0 + 220, y0 + 120, (240, 220, 60)),
                                     (x0 + 300, y0 + 60, (60, 120, 220)))):
        d.ellipse([fx, fy, fx + 44, fy + 22], fill=c)
        d.polygon([(fx, fy + 11), (fx - 16, fy), (fx - 16, fy + 22)], fill=c)
    for k in range(3):                                                     # サンゴ
        bx = x0 + 60 + k * 120
        d.polygon([(bx, y1 - 40), (bx + 10, y1 - 90), (bx + 20, y1 - 60), (bx + 32, y1 - 100), (bx + 40, y1 - 40)],
                  fill=(236, 110, 120))


def wiz():
    """ウィズの事務所。両側に紙の山、真ん中に水槽。"""
    img = _office_base()
    d = _d(img)
    _window(d, 760, 110, 1160, 330, sky=(180, 204, 222))
    _tank(d, 780, 420, 1140, 640)
    return img


def pc():
    """情報会議。机の真ん中に、熱帯魚が泳ぐ画面のパソコン。"""
    img = _office_base()
    d = _d(img)
    _window(d, 760, 110, 1160, 300, sky=(180, 204, 222))
    _table(d, 760, 1160, 660, col=(140, 130, 118))
    d.rounded_rectangle([800, 360, 1120, 620], radius=18, fill=(214, 208, 190), outline=(150, 144, 130), width=4)
    d.rectangle([830, 384, 1090, 580], fill=(30, 90, 150))
    for fx, fy, c in ((870, 430, (240, 140, 40)), (980, 500, (240, 220, 60)), (1020, 420, (120, 220, 200))):
        d.ellipse([fx, fy, fx + 40, fy + 20], fill=c)
        d.polygon([(fx, fy + 10), (fx - 14, fy), (fx - 14, fy + 20)], fill=c)
    for k in range(5):
        d.ellipse([850 + k * 50, 540 - (k % 2) * 10, 866 + k * 50, 556 - (k % 2) * 10], outline=(180, 220, 240), width=2)
    d.rectangle([930, 620, 990, 660], fill=(190, 184, 168))
    d.rectangle([840, 668, 1080, 690], fill=(200, 196, 180))                # キーボード
    return img


def _creature(d, cx, cy, k=1.0, ln=(60, 60, 70), w=5):
    """卵の殻に入った、ぶかっこうな生き物の線画（この回用の架空の形）。cx, cy は体の中心。"""
    P = lambda x, y: (cx + x * k, cy + y * k)
    d.polygon([P(-100, 95), P(-70, 55), P(-40, 95), P(-10, 50), P(20, 95), P(50, 55), P(100, 95), P(80, 175),
               P(-80, 175)], outline=ln, width=w)                                   # 割れた殻
    d.ellipse([*P(-80, -85), *P(80, 85)], outline=ln, width=w)                      # 体
    d.ellipse([*P(-40, -35), *P(-16, -11)], fill=ln)
    d.ellipse([*P(22, -39), *P(40, -19)], fill=ln)
    d.arc([*P(-30, -5), *P(30, 45)], 20, 160, fill=ln, width=w)
    d.line([P(-80, -5), P(-120, -35)], fill=ln, width=w)
    d.line([P(80, -5), P(120, 25)], fill=ln, width=w)


def sketch():
    """デザインの部屋。壁のボードに、卵の殻に入った不格好な生き物のスケッチ。"""
    img = _office_base(wall=(238, 236, 230), floor=(160, 150, 136))
    d = _d(img)
    d.rectangle([815, 270, 1105, 590], fill=(250, 250, 246), outline=(120, 110, 100), width=8)
    _creature(d, 960, 390, 0.85)
    for k in range(3):
        d.rectangle([838 + k * 40, 292, 868 + k * 40, 310], fill=((236, 120, 150), (120, 180, 230), (250, 214, 80))[k])
    return img


def kaigi():
    """おもちゃ会社の会議室。ホワイトボードに卵形の腕時計と、中の生き物の絵。"""
    img = _rgb(base((226, 230, 234), (204, 208, 214)))
    wood_floor(img, FLOOR, col=(130, 124, 118), line=(112, 106, 100))
    d = _d(img)
    d.rectangle([760, 130, 1160, 480], fill=(252, 252, 250), outline=(150, 156, 164), width=10)
    ln = (40, 70, 140)
    d.rectangle([780, 250, 960, 280], outline=ln, width=5)                  # 腕時計のバンド
    d.ellipse([820, 200, 920, 330], fill=(252, 252, 250), outline=ln, width=6)   # 卵形の本体
    d.rectangle([845, 240, 895, 280], outline=ln, width=4)
    _pix(d, 858, 246, 3, col=ln)
    _creature(d, 1055, 330, 0.55, ln=(200, 60, 60), w=4)                     # 中の生き物の絵
    d.rectangle([700, 640, 1220, 690], fill=(120, 100, 84))                 # 長机
    for x in (740, 1160):
        d.rectangle([x, 690, x + 20, 820], fill=(90, 76, 64))
    for k in range(4):
        d.rectangle([760 + k * 110, 612, 840 + k * 110, 640], fill=(244, 244, 240), outline=(180, 180, 176))
    return img


def kaigi2():
    """2004年の会議室。机の上で、2台の卵形ゲーム機が赤外線で通信している。"""
    img = _rgb(base((234, 238, 242), (214, 220, 226)))
    wood_floor(img, FLOOR, col=(150, 146, 140), line=(132, 128, 122))
    d = _d(img)
    for k in range(4):                                                     # ガラスの壁
        d.rectangle([640 + k * 170, 120, 790 + k * 170, 440], fill=(200, 222, 236), outline=(160, 170, 180), width=4)
    _table(d, 740, 1180, 660, col=(90, 90, 96))
    _egg(d, 860, 570, 130, (120, 180, 230), chain=False)
    _egg(d, 1060, 570, 130, (236, 120, 150), chain=False)
    for k in range(3):
        r = 16 + k * 14
        d.arc([960 - r, 540 - r, 960 + r, 540 + r], -50, 50, fill=(220, 60, 60), width=4)
        d.arc([960 - r, 540 - r, 960 + r, 540 + r], 130, 230, fill=(220, 60, 60), width=4)
    return img


def harajuku():
    """1990年代の原宿の通り。机の上に12色の色見本。"""
    img = _rgb(vgrad((W, H), (170, 206, 236), (214, 226, 236)))
    d = _d(img)
    cols = [(240, 170, 190), (250, 230, 150), (170, 220, 200), (200, 180, 230), (250, 200, 150), (180, 210, 240)]
    for k in range(8):                                                     # 店の並び
        x = k * 250 - 40
        d.rectangle([x, 160 + (k % 3) * 30, x + 240, 780], fill=cols[k % 6])
        d.rectangle([x + 20, 520, x + 220, 780], fill=(250, 250, 250))
        d.rectangle([x + 30, 530, x + 210, 770], fill=(200, 220, 230))
        for j in range(2):
            d.rectangle([x + 40 + j * 100, 240 + (k % 3) * 30, x + 110 + j * 100, 320 + (k % 3) * 30], fill=(230, 240, 246))
    d.rectangle([0, 780, W, H], fill=(170, 170, 176))
    for k in range(10):                                                    # 横断歩道
        d.rectangle([k * 200, 900, k * 200 + 110, 960], fill=(236, 236, 236))
    d.rectangle([770, 640, 1150, 670], fill=(236, 236, 236))              # 折りたたみ机
    d.rectangle([790, 670, 806, 800], fill=(150, 150, 150))
    d.rectangle([1114, 670, 1130, 800], fill=(150, 150, 150))
    samples = [(236, 120, 150), (120, 180, 230), (250, 214, 80), (140, 210, 140), (190, 140, 220), (250, 160, 90),
               (240, 240, 236), (90, 90, 100), (250, 190, 210), (160, 220, 230), (230, 90, 80), (180, 180, 120)]
    for k, c in enumerate(samples):
        x, y = 790 + (k % 6) * 52, 548 + (k // 6) * 48
        d.ellipse([x, y, x + 40, y + 46], fill=c, outline=(120, 120, 120), width=2)
    return img


def henshu():
    """雑誌の編集部。机に雑誌の山。"""
    img = _office_base(wall=(236, 230, 224), floor=(140, 126, 116))
    d = _d(img)
    for x in (700, 1000):
        d.rectangle([x, 150, x + 220, 480], fill=(150, 120, 90))
        for r in range(3):
            _shelf(d, x, x + 220, 250 + r * 110)
            for k in range(8):
                d.rectangle([x + 10 + k * 25, 180 + r * 110, x + 30 + k * 25, 250 + r * 110],
                            fill=((230, 120, 150), (120, 170, 220), (250, 210, 90), (160, 210, 160))[(k + r) % 4])
    _table(d, 760, 1160, 640, col=(150, 140, 126))
    for k in range(4):
        c = ((240, 150, 180), (250, 220, 120), (150, 200, 240), (200, 170, 230))[k]
        d.rectangle([790 + k * 90, 576 - k * 4, 870 + k * 90, 636], fill=c, outline=(120, 120, 120), width=2)
        d.rectangle([800 + k * 90, 590 - k * 4, 860 + k * 90, 606 - k * 4], fill=(250, 250, 250))
    return img


def mise():
    """おもちゃ屋の売り場。空っぽの棚と「入荷未定」の札。"""
    img = _rgb(base((246, 240, 230), (230, 222, 210)))
    wood_floor(img, FLOOR, col=(190, 170, 140), line=(170, 150, 122))
    d = _d(img)
    for x in (60, 1480):
        d.rectangle([x, 200, x + 380, 800], fill=(220, 210, 196))
        for r in range(4):
            _shelf(d, x, x + 380, 330 + r * 120, col=(160, 140, 120))
            for k in range(6):
                d.line([(x + 30 + k * 58, 300 + r * 120), (x + 30 + k * 58, 330 + r * 120)], fill=(150, 150, 156), width=3)
    d.rectangle([760, 560, 1160, 700], fill=(200, 170, 130))              # レジ台
    d.rectangle([760, 540, 1160, 560], fill=(170, 140, 104))
    d.rectangle([810, 330, 1110, 520], fill=(250, 246, 236), outline=(200, 60, 60), width=10)
    f = _font(58)
    for i, t in enumerate(("売り切れ", "入荷未定")):
        bb = d.textbbox((0, 0), t, font=f)
        d.text((960 - (bb[2] - bb[0]) // 2 - bb[0], 352 + i * 80), t, font=f, fill=(200, 50, 50))
    return img


def soko():
    """倉庫。商品名を白い紙で消した段ボールの山。"""
    img = _rgb(base((200, 196, 188), (170, 166, 158)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(130, 128, 124))
    for k in range(9):
        d.line([(k * 240, 0), (k * 240, FLOOR)], fill=(180, 176, 168), width=6)
    for x in (40, 1480):
        for r in range(4):
            for c in range(2):
                _box(d, x + c * 200, FLOOR - 150 - r * 150, 190, 145)
    for r in range(2):
        for c in range(2):
            _box(d, 780 + c * 190, FLOOR - 300 - r * 150 + 150, 180, 140)
    return img


def ny():
    """ニューヨークの通り。ビルと、大きなおもちゃ屋の窓。"""
    img = _rgb(vgrad((W, H), (150, 186, 220), (200, 214, 226)))
    d = _d(img)
    for k in range(10):
        x = k * 200 - 20
        h = 300 + (k * 137) % 360
        d.rectangle([x, 780 - h - 200, x + 180, 780], fill=((150, 150, 160), (180, 170, 160), (130, 140, 150))[k % 3])
        for r in range(0, h, 60):
            for c in range(3):
                d.rectangle([x + 20 + c * 55, 780 - h - 170 + r, x + 50 + c * 55, 780 - h - 140 + r], fill=(220, 230, 240))
    d.rectangle([600, 420, 1320, 800], fill=(200, 60, 60))                  # おもちゃ屋の正面（文字なし）
    for k in range(3):
        d.rectangle([640 + k * 230, 480, 820 + k * 230, 760], fill=(250, 240, 220))
    for k, c in enumerate(((236, 120, 150), (120, 180, 230), (250, 214, 80), (140, 210, 140), (240, 240, 236), (190, 140, 220))):
        cx = 700 + (k % 3) * 230
        cy = 560 + (k // 3) * 110
        d.ellipse([cx - 22, cy - 28, cx + 22, cy + 28], fill=c, outline=(120, 120, 120), width=2)
        d.ellipse([cx + 48, cy - 28, cx + 92, cy + 28], fill=c, outline=(120, 120, 120), width=2)
    d.rectangle([0, 800, W, H], fill=(120, 120, 126))
    d.rectangle([0, 790, W, 810], fill=(170, 170, 170))
    d.rounded_rectangle([140, 820, 460, 920], radius=24, fill=(240, 200, 40))  # タクシー
    d.ellipse([170, 890, 230, 950], fill=(40, 40, 40))
    d.ellipse([370, 890, 430, 950], fill=(40, 40, 40))
    return img


def zaiko():
    """売れ残りの山。薄暗い倉庫に、天井まで積んだ段ボール。"""
    img = _rgb(base((110, 110, 118), (80, 80, 88)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(70, 70, 76))
    for x0 in (0, 1480):
        for r in range(6):
            for c in range(2):
                _box(d, x0 + 20 + c * 210, FLOOR - 140 - r * 140, 200, 135, erased=False)
    for r in range(5):
        for c in range(2):
            _box(d, 770 + c * 195, FLOOR - 140 - r * 140, 185, 135, erased=False)
    return img


def zukai():
    """図解: 横32×縦16の白黒の点と、上下4個ずつのアイコン。"""
    img = _rgb(base((246, 244, 238), (232, 230, 222)))
    d = _d(img)
    cell = 13
    gx, gy = 960 - 16 * cell, 430 - 8 * cell
    d.rounded_rectangle([gx - 40, gy - 130, gx + 32 * cell + 40, gy + 16 * cell + 130], radius=30,
                        fill=(236, 120, 150), outline=(170, 80, 100), width=6)
    d.rectangle([gx - 10, gy - 100, gx + 32 * cell + 10, gy + 16 * cell + 100], fill=(250, 248, 240))
    d.rectangle([gx, gy, gx + 32 * cell, gy + 16 * cell], fill=LCD)
    for c in range(33):
        d.line([(gx + c * cell, gy), (gx + c * cell, gy + 16 * cell)], fill=(170, 184, 156), width=1)
    for r in range(17):
        d.line([(gx, gy + r * cell), (gx + 32 * cell, gy + r * cell)], fill=(170, 184, 156), width=1)
    _pix(d, gx + 12 * cell, gy + 4 * cell, cell)
    for i in range(4):                                                     # 上下のアイコン（汎用の形）
        for j, yy in enumerate((gy - 70, gy + 16 * cell + 30)):
            x = gx + 14 + i * 110
            if (i + j) % 3 == 0:
                d.ellipse([x, yy, x + 40, yy + 40], outline=INK, width=4)
            elif (i + j) % 3 == 1:
                d.rectangle([x, yy, x + 40, yy + 40], outline=INK, width=4)
            else:
                d.polygon([(x + 20, yy), (x + 40, yy + 40), (x, yy + 40)], outline=INK, width=4)
    f = _font(48)
    d.text((gx + 16 * cell - 28, gy + 16 * cell + 146), "32", font=f, fill=(60, 60, 70))
    d.text((gx + 32 * cell + 50, gy + 8 * cell - 30), "16", font=f, fill=(60, 60, 70))
    return img


def zukai2():
    """図解: 卵から大人まで、育ち方で枝分かれする流れ（形は架空）。"""
    img = _rgb(base((246, 244, 238), (232, 230, 222)))
    d = _d(img)
    ar = (150, 150, 160)
    d.ellipse([915, 90, 1005, 200], fill=(250, 248, 240), outline=INK, width=6)        # 卵
    d.line([(960, 200), (960, 250)], fill=ar, width=8)
    small = ["..##..", ".####.", "#.##.#", "######", ".#..#.", "......"]
    _pix(d, 918, 262, 14, small)                                            # 赤ちゃん
    for x in (780, 1140):
        d.line([(960, 350), (x, 410)], fill=ar, width=8)
    mid = [".####.", "#.##.#", "######", "#....#", ".####.", ".#..#."]
    for x in (735, 1095):
        _pix(d, x, 420, 15, mid)                                            # 子ども
    adults = [
        ["..##..", ".####.", "#.##.#", "######", "######", ".####.", "##..##", "......"],
        ["#....#", "##..##", "######", "#.##.#", "######", ".####.", ".#..#.", "......"],
        [".####.", "######", "##.#.#", "######", "#....#", "######", "#.##.#", "......"],
        ["..##..", "######", "#.##.#", "######", ".####.", "..##..", ".#..#.", "......"],
    ]
    for k, x in enumerate((600, 800, 1000, 1200)):
        src = 780 if k < 2 else 1140
        d.line([(src, 520), (x + 60, 580)], fill=ar, width=8)
        _pix(d, x, 590, 16, adults[k])                                      # 大人
    return img


def gendai():
    """今のおもちゃ売り場。色とりどりの卵形、腕時計型、指輪型。"""
    img = _rgb(base((246, 246, 244), (230, 230, 226)))
    wood_floor(img, FLOOR, col=(200, 190, 176), line=(180, 170, 156))
    d = _d(img)
    for y in (230, 470):
        d.rectangle([600, y + 150, 1320, y + 166], fill=(170, 170, 176))
    cols = [(236, 120, 150), (120, 180, 230), (250, 214, 80), (140, 210, 140), (190, 140, 220), (240, 240, 236)]
    for k, c in enumerate(cols):
        _egg(d, 660 + k * 120, 310, 110, c, chain=False)
    d.rounded_rectangle([840, 560, 960, 620], radius=20, fill=(90, 90, 100))    # 腕時計型
    d.rounded_rectangle([870, 520, 930, 660], radius=10, fill=(236, 120, 150))
    d.rectangle([880, 540, 920, 600], fill=(150, 210, 230))
    d.ellipse([1000, 540, 1080, 620], outline=(210, 180, 90), width=12)         # 指輪型
    d.ellipse([1022, 520, 1058, 556], fill=(236, 236, 240), outline=(180, 180, 180), width=3)
    _egg(d, 740, 560, 130, (120, 180, 230), chain=False)                        # カラー画面の機種
    d.rectangle([716, 540, 764, 572], fill=(250, 190, 120))
    _egg(d, 1180, 560, 130, (250, 214, 80), chain=False)
    return img


# ---- 作り直し版（84_たまごっちの誕生 / slug=tamagotchi-yokoi-v2）で足した背景
# 場面の途中で差し替える「状況が変わった」背景は、元の背景を呼んで要素を足す（同じ構図で差が一目で分かる）。
RED = (210, 50, 50)


def _sheet(d, x, y, w, h, angle_dx=0, lines=4, col=(250, 248, 238)):
    """企画を書いた紙（字は描かず灰色の行だけ）。angle_dx で少し傾ける。"""
    d.polygon([(x, y), (x + w, y + angle_dx), (x + w - angle_dx, y + h + angle_dx), (x - angle_dx, y + h)],
              fill=col, outline=(170, 164, 150))
    for k in range(lines):
        yy = y + 14 + k * (h - 24) // max(1, lines)
        d.line([(x + 10, yy), (x + w - 16 - (k % 2) * 20, yy + angle_dx // 2)], fill=(150, 150, 160), width=3)


def _batsu(d, cx, cy, r, w=7):
    d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=RED, width=w)
    d.line([(cx + r, cy - r), (cx - r, cy + r)], fill=RED, width=w)


def bandai_botsu():
    """1977年の企画室。机の上と床に、赤い×の付いたボツの企画書が山になっている。"""
    img = bandai()
    d = _d(img)
    for k in range(16):                                                    # 机の上に積み上がった紙の山
        x = 790 + ((k * 37) % 5 - 2) * 8
        y = 620 - k * 14
        _sheet(d, x, y, 300, 26, angle_dx=((k * 5) % 3 - 1) * 4, lines=1)
        if k % 3 == 0:
            _batsu(d, x + 250, y + 13, 10, 4)
    for x, y, a in ((700, 840, 6), (860, 900, -4), (1010, 860, 5), (1150, 910, -6), (760, 960, 3),
                    (930, 990, -3), (1090, 975, 4), (640, 920, -5), (1230, 850, 2)):   # 床に散らばったボツ
        _sheet(d, x, y, 130, 90, angle_dx=a, lines=3)
        _batsu(d, x + 65, y + 45, 30)
    for x, y in ((820, 1020), (990, 1040), (1180, 1010), (700, 1030)):     # 丸めた紙
        d.ellipse([x, y, x + 54, y + 44], fill=(240, 236, 226), outline=(170, 160, 150), width=3)
        d.line([(x + 12, y + 18), (x + 40, y + 26)], fill=(190, 180, 170), width=3)
    return img


def _flyer(d, x, y, w, h, col):
    """スーパーのチラシ（文字は描かず、色の帯と商品の丸だけ）。"""
    d.rectangle([x, y, x + w, y + h], fill=(250, 248, 240), outline=(180, 176, 166), width=2)
    d.rectangle([x, y, x + w, y + h // 5], fill=col)
    for r in range(2):
        for c in range(3):
            cx = x + 14 + c * (w - 28) // 3
            cy = y + h // 5 + 12 + r * (h * 2 // 5)
            d.ellipse([cx, cy, cx + (w - 40) // 4, cy + (w - 40) // 4], fill=((240, 200, 90), (220, 120, 100), (140, 200, 140))[(r + c) % 3])
            d.rectangle([cx, cy + (w - 40) // 4 + 6, cx + (w - 40) // 4, cy + (w - 40) // 4 + 14], fill=RED)


def wiz_chirashi():
    """ウィズの事務所。水槽の前までチラシと箱のデザインと会議のパネルで埋まっている。"""
    img = wiz()
    d = _d(img)
    cols = [(220, 60, 60), (240, 160, 40), (60, 120, 200), (60, 160, 90)]
    for x in (60, 1460):                                                   # 両側の机の紙の山をチラシの塔に
        for k in range(10):
            _flyer(d, x + 30 + (k % 4) * 90, 560 - (k // 4) * 120, 84, 112, cols[k % 4])
    for k in range(7):                                                     # 水槽の前に立てかけたパネル
        x = 700 + k * 80
        d.rectangle([x, 560 + (k % 2) * 20, x + 150, 800], fill=(236, 234, 228), outline=(130, 126, 118), width=4)
        d.rectangle([x + 14, 580 + (k % 2) * 20, x + 136, 640 + (k % 2) * 20], fill=cols[(k + 1) % 4])
        for j in range(3):
            d.rectangle([x + 14, 660 + j * 36, x + 120 - j * 14, 676 + j * 36], fill=(150, 150, 160))
    for x, y in ((640, 840), (820, 880), (1000, 850), (1180, 890), (740, 960), (960, 980), (1150, 970)):   # 床のチラシ
        _flyer(d, x, y, 120, 150, cols[(x // 10) % 4])
    for k in range(3):                                                     # 箱のデザインの見本
        x = 600 + k * 260
        d.rectangle([x, 990, x + 120, 1070], fill=(196, 160, 110), outline=(140, 110, 70), width=3)
        d.rectangle([x + 20, 1004, x + 100, 1040], fill=cols[k])
    return img


def kaigi_kazu():
    """会議室。ホワイトボードに貼った紙に、6万個と30万個を消して100万個と書いてある。"""
    img = kaigi()
    d = _d(img)
    d.rectangle([770, 140, 1150, 470], fill=(252, 250, 240), outline=(170, 164, 150), width=4)
    for x in (790, 1130):                                                  # 留めたテープ
        d.rectangle([x - 20, 130, x + 20, 156], fill=(230, 220, 160))
    f_small, f_big = _font(48), _font(78)
    rows = (("6万個", 160, f_small), ("30万個", 248, f_small), ("100万個", 362, f_big))
    for t, y, f in rows:
        bb = d.textbbox((0, 0), t, font=f)
        x = 960 - (bb[2] - bb[0]) // 2 - bb[0]
        d.text((x, y - bb[1]), t, font=f, fill=(40, 60, 120))
        if f is f_small:                                                   # 消した数には線を2本
            midy = y + (bb[3] - bb[1]) // 2
            d.line([(x - 10, midy - 6), (x + bb[2] - bb[0] + 10, midy - 6)], fill=RED, width=6)
            d.line([(x - 10, midy + 6), (x + bb[2] - bb[0] + 10, midy + 6)], fill=RED, width=6)
        else:
            d.ellipse([x - 30, y - 22, x + bb[2] - bb[0] + 30, y + bb[3] - bb[1] + 22], outline=RED, width=8)
    for y in (218, 306):                                                   # 次の数への矢印（下向き）
        d.polygon([(944, y), (976, y), (960, y + 20)], fill=(40, 60, 120))
    return img


def _person(d, cx, foot, h, col):
    """行列の人（顔は描かないシルエット）。cx は中心、foot は足元の y、h は身長。"""
    hr = h * 0.12
    d.ellipse([cx - hr, foot - h, cx + hr, foot - h + hr * 2], fill=col)
    d.rounded_rectangle([cx - h * 0.16, foot - h + hr * 2 + 4, cx + h * 0.16, foot - h * 0.42], radius=int(h * 0.06), fill=col)
    d.rectangle([cx - h * 0.12, foot - h * 0.44, cx - h * 0.02, foot], fill=col)
    d.rectangle([cx + h * 0.02, foot - h * 0.44, cx + h * 0.12, foot], fill=col)


def mise_retsu():
    """おもちゃ屋の売り場。入荷した日。抽選の札の前から右の外まで、人の列が続いている。"""
    img = mise()
    d = _d(img)
    d.rectangle([810, 330, 1110, 520], fill=(250, 246, 236), outline=(200, 60, 60), width=10)   # 札を描き替える
    f = _font(58)
    for i, t in enumerate(("本日入荷", "抽選50個")):
        bb = d.textbbox((0, 0), t, font=f)
        d.text((960 - (bb[2] - bb[0]) // 2 - bb[0], 352 + i * 80), t, font=f, fill=(200, 50, 50))
    cols = [(92, 100, 126), (120, 96, 110), (84, 112, 104), (110, 104, 92), (96, 92, 120)]
    for k in range(14):                                                    # 奥の列（小さめ）
        cx = 700 + k * 62
        _person(d, cx, 760, 230 - (k % 3) * 14, tuple(int(c * 1.25) for c in cols[k % 5]))
    for k in range(12):                                                    # 手前の列（右の外へ続く）
        cx = 640 + k * 118
        _person(d, cx, 1000 + (k % 2) * 10, 330 - (k % 4) * 16, cols[(k + 2) % 5])
    return img


def soko_yama():
    """倉庫。名前を消した段ボールが、天井まで隙間なく積み上がっている。"""
    img = soko()
    d = _d(img)
    for r in range(8):
        for c in range(11):
            x = c * 196 - (r % 2) * 90
            y = FLOOR - 145 - r * 140
            if y < -150:
                continue
            _box(d, x, y, 190, 138)
    d.rectangle([0, 0, W, 26], fill=(150, 146, 138))                       # 天井の梁
    return img


def wiz2009():
    """2009年ごろのウィズの事務所。並んだ机と薄型の画面、棚に卵形の試作品。"""
    img = _rgb(base((236, 238, 240), (214, 218, 222)))
    wood_floor(img, FLOOR, col=(150, 150, 154), line=(132, 132, 136))
    d = _d(img)
    for k in range(3):                                                     # 窓
        _window(d, 640 + k * 220, 110, 840 + k * 220, 330, sky=(178, 206, 228), frame=(120, 124, 130))
    d.rectangle([660, 380, 1260, 600], fill=(180, 170, 156))               # 試作品の棚
    for r in range(2):
        _shelf(d, 660, 1260, 480 + r * 104, col=(130, 120, 108))
        for k in range(6):
            c = ((236, 120, 150), (120, 180, 230), (250, 214, 80), (140, 210, 140), (190, 140, 220), (240, 240, 236))[(k + r) % 6]
            _egg(d, 712 + k * 98, 440 + r * 104, 70, c, chain=False)
    for x in (60, 1480):                                                   # 両側の机と画面
        for k in range(2):
            y = 640 + k * 150
            d.rectangle([x, y, x + 380, y + 30], fill=(200, 200, 204))
            d.rectangle([x + 20, y + 30, x + 34, y + 140], fill=(150, 150, 156))
            d.rectangle([x + 346, y + 30, x + 360, y + 140], fill=(150, 150, 156))
            for j in range(2):
                mx = x + 40 + j * 180
                d.rectangle([mx, y - 110, mx + 140, y - 20], fill=(40, 44, 52))
                d.rectangle([mx + 8, y - 102, mx + 132, y - 28], fill=(90, 130, 170))
                d.rectangle([mx + 62, y - 20, mx + 78, y], fill=(60, 60, 66))
    d.rectangle([760, 680, 1160, 720], fill=(110, 100, 90))                # 社長の机
    d.rectangle([780, 720, 800, 860], fill=(90, 82, 74))
    d.rectangle([1120, 720, 1140, 860], fill=(90, 82, 74))
    for k in range(5):                                                     # 机の上の書類
        d.rectangle([800 + k * 6, 650 - k * 6, 920 + k * 6, 680 - k * 6], fill=(246, 244, 236), outline=(170, 166, 156))
    return img


LOCATIONS = {
    "tg_bandai_botsu": bandai_botsu, "tg_wiz_chirashi": wiz_chirashi, "tg_kaigi_kazu": kaigi_kazu,
    "tg_mise_retsu": mise_retsu, "tg_soko_yama": soko_yama, "tg_wiz2009": wiz2009,
    "tg_ima": ima, "tg_bandai": bandai, "tg_wiz": wiz, "tg_pc": pc, "tg_sketch": sketch,
    "tg_kaigi": kaigi, "tg_kaigi2": kaigi2, "tg_harajuku": harajuku, "tg_henshu": henshu,
    "tg_mise": mise, "tg_soko": soko, "tg_ny": ny, "tg_zaiko": zaiko, "tg_zukai": zukai,
    "tg_zukai2": zukai2, "tg_gendai": gendai,
}

CARDS = ["1977", "1995", "1996", "1998", "2003", "2004"]   # 2003 は作り直し版で追加


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
        if only and f"tg_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"tg_card_{y}.png")
        print(f"生成完了: tg_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
