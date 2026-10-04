#!/usr/bin/env python3
"""鉛筆の誕生・眞崎仁六回（59_鉛筆の誕生 / slug=masaki-pencil）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はウォークマン回（gen_walkman_bgs.py）と同じ。
実在メーカーの商標（ロゴ・マーク・商品名の文字）は描かない。
マークの話は、元になった家紋「三鱗」と3本の鉛筆で表す。

83_鉛筆の誕生（slug=masaki-pencil-v2・作り直し）では、既存の絵は変えずに
場面の途中で差し替える絵（pc_yoru_shippai / pc_yoru_mark / pc_suisha_ame / pc_mise_kinpai /
pc_kojo_bunkatsu）と、新しい場面の絵（pc_zashiki / pc_kiritsu / pc_phila / pc_kojo_yuu）、
年号カード 1848・1925 を足した。足した絵だけを書き出すときは名前を指定して実行する。

実行: PYTHONPATH=. python scripts/gen_pencil_bgs.py [名前...]
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, glow, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)
WINE = (122, 30, 48)          # 高級鉛筆の軸の色（えんじ）
WOOD = (224, 190, 140)        # 削った木
GRAPHITE = (50, 50, 56)


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


def _pencil(d, x, y, length=200, thick=18, col=WINE):
    """横向きの削った鉛筆。x, y は左端（おしり）の中央。"""
    body = length * 0.82
    d.rectangle([x, y - thick / 2, x + body, y + thick / 2], fill=col)
    d.line([(x, y), (x + body, y)], fill=tuple(min(255, c + 40) for c in col), width=2)
    d.polygon([(x + body, y - thick / 2), (x + length - 10, y - 3), (x + length - 10, y + 3),
               (x + body, y + thick / 2)], fill=WOOD)
    d.polygon([(x + length - 22, y - 5), (x + length, y), (x + length - 22, y + 5)], fill=GRAPHITE)


def _table(d, x0, x1, y, col=(150, 116, 80)):
    d.rectangle([x0, y, x1, y + 40], fill=col)
    d.rectangle([x0 + 20, y + 40, x0 + 40, y + 190], fill=tuple(int(c * 0.8) for c in col))
    d.rectangle([x1 - 40, y + 40, x1 - 20, y + 190], fill=tuple(int(c * 0.8) for c in col))


def _uroko(d, cx, cy, size, col=(40, 40, 44)):
    """家紋の三鱗（三つの三角形）。"""
    h = size * 0.866
    tri = lambda x, y: [(x, y - h / 2), (x - size / 2, y + h / 2), (x + size / 2, y + h / 2)]
    d.polygon(tri(cx, cy - h / 2), fill=col)
    d.polygon(tri(cx - size / 2, cy + h / 2), fill=col)
    d.polygon(tri(cx + size / 2, cy + h / 2), fill=col)


def _box(d, x, y, w=120, h=60, col=(60, 80, 120)):
    """文字のない鉛筆の箱。"""
    d.rectangle([x, y, x + w, y + h], fill=col, outline=tuple(int(c * 0.6) for c in col), width=3)
    for k in range(5):
        d.ellipse([x + 12 + k * (w - 24) / 5, y + h * 0.35, x + 12 + k * (w - 24) / 5 + 12, y + h * 0.35 + 12],
                  fill=WOOD)


# ------------------------------------------------------------ 場所
def ima_base():
    img = _rgb(base((236, 232, 222), (214, 208, 196)))
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    d = _d(img)
    _window(d, 740, 110, 1180, 400, sky=(176, 210, 232))
    _table(d, 780, 1140, 640)
    return img


def ima():
    """今の居間。机の上に鉛筆と削りかす。"""
    img = ima_base()
    d = _d(img)
    for k in range(3):
        _pencil(d, 820, 600 + k * 12, 200, 14, (WINE, (40, 110, 70), (230, 190, 60))[k])
    for k in range(5):
        d.ellipse([1060 + k * 12, 612 + (k % 2) * 8, 1084 + k * 12, 628 + (k % 2) * 8], fill=WOOD)
    return img


def ima2():
    """締めの居間。紙に描いた三鱗と、3本の鉛筆。"""
    img = ima_base()
    d = _d(img)
    d.rectangle([800, 560, 940, 636], fill=(250, 248, 240), outline=(170, 160, 150), width=2)
    _uroko(d, 870, 598, 34)
    for k in range(3):
        _pencil(d, 960, 588 + k * 16, 160, 12)
    return img


def kunozan():
    """博物館の展示ケース。小さな古い鉛筆と、筆の形の鉛筆。"""
    img = _rgb(base((70, 60, 54), (40, 34, 30)))
    d = _d(img)
    _glow(img, 960, 380, 380, (255, 230, 190), 70)
    d = _d(img)
    d.rectangle([620, 240, 1300, 620], fill=(120, 100, 80), outline=(200, 180, 140), width=8)   # ケース
    d.rectangle([640, 260, 1280, 600], fill=(190, 170, 140))
    d.rounded_rectangle([700, 330, 900, 360], radius=10, fill=(140, 90, 60))       # 古い鉛筆（家康）
    d.polygon([(900, 332), (940, 345), (900, 358)], fill=GRAPHITE)
    d.rectangle([700, 380, 920, 420], fill=(120, 70, 40), outline=(80, 50, 30), width=3)   # 筆箱
    d.rounded_rectangle([1000, 330, 1180, 350], radius=8, fill=(160, 140, 90))     # 筆の形（政宗）
    d.polygon([(1180, 334), (1230, 340), (1180, 346)], fill=GRAPHITE)
    d.rounded_rectangle([1000, 370, 1080, 392], radius=8, fill=(170, 160, 110))    # 竹のキャップ
    d.rectangle([600, 620, 1320, 700], fill=(60, 50, 44))
    return img


def saga():
    """明治のはじめの町並み。港に船。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, 600), (170, 200, 222), (222, 224, 210)), (0, 0))
    img.paste(vgrad((W, H - 600), (90, 130, 160), (60, 100, 130)), (0, 600))
    d = _d(img)
    for k in range(8):
        x0 = 60 + k * 230
        h = 140 + (k * 37) % 60
        d.rectangle([x0, 600 - h, x0 + 190, 600], fill=(120, 96, 74))
        d.polygon([(x0 - 20, 612 - h), (x0 + 95, 540 - h), (x0 + 210, 612 - h)], fill=(60, 60, 66))
    d.rectangle([0, 600, W, 640], fill=(150, 136, 110))
    d.polygon([(1300, 760), (1700, 760), (1650, 820), (1350, 820)], fill=(60, 50, 44))   # 汽船
    d.rectangle([1440, 690, 1480, 760], fill=(40, 40, 44))
    d.ellipse([1420, 640, 1500, 690], fill=(200, 200, 200))
    return img


def paris():
    """パリ万博の会場。ガラスの屋根と、片すみの鉛筆の陳列台。"""
    img = _rgb(base((226, 222, 210), (200, 196, 184)))
    wood_floor(img, FLOOR, col=(160, 140, 110), line=(140, 120, 90))
    d = _d(img)
    for k in range(9):                                                            # 鉄骨とガラス
        x = k * 240
        d.line([(x, 0), (x + 120, 300)], fill=(110, 110, 116), width=8)
        d.line([(x + 240, 0), (x + 120, 300)], fill=(110, 110, 116), width=8)
    d.rectangle([0, 300, W, 316], fill=(110, 110, 116))
    for x in (60, 1540):                                                          # 三色旗（縦縞）
        d.rectangle([x, 330, x + 100, 480], fill=(40, 60, 150))
        d.rectangle([x + 100, 330, x + 200, 480], fill=(240, 240, 240))
        d.rectangle([x + 200, 330, x + 300, 480], fill=(210, 40, 50))
    d.rectangle([760, 600, 1160, 660], fill=(90, 70, 50))                          # 陳列台
    d.rectangle([780, 660, 1140, 860], fill=(70, 54, 40))
    d.rectangle([780, 520, 1140, 600], fill=(220, 236, 244), outline=(120, 110, 90), width=4)   # ガラスケース
    for k in range(6):
        _pencil(d, 800 + (k % 2) * 170, 540 + (k // 2) * 20, 150, 12,
                ((200, 170, 60), (40, 90, 60), (140, 40, 40), (40, 60, 120), (200, 170, 60), (90, 60, 40))[k])
    return img


def sekai():
    """暗い地に世界地図の点。イギリス・フランス・ドイツ・日本が光る。"""
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
                    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(150, 130, 90))
                    break
    for cx, cy in ((900, 280), (930, 330), (990, 300), (1590, 420)):
        _glow(img, cx, cy, 60, (255, 230, 150), 170)
    return img


def yoru():
    """明治の家の夜。机に黒鉛と粘土、乳鉢、小さな炉、折れた芯、木の板。"""
    img = _rgb(base((70, 62, 58), (46, 40, 38)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    _glow(img, 1500, 420, 260, (255, 200, 120), 90)                                # ランプ
    d = _d(img)
    d.rectangle([800, 640, 1760, 690], fill=(120, 90, 64))                         # 机
    d.rectangle([830, 690, 856, 880], fill=(96, 72, 52))
    d.rectangle([1700, 690, 1726, 880], fill=(96, 72, 52))
    d.ellipse([1470, 520, 1530, 600], fill=(255, 220, 150))
    d.rectangle([1490, 600, 1510, 640], fill=(120, 100, 70))
    d.rectangle([840, 610, 1050, 640], fill=(240, 234, 220))                        # 下に敷いた紙
    d.polygon([(860, 636), (900, 586), (940, 636)], fill=(20, 20, 24), outline=(150, 150, 160))   # 黒鉛のかたまり
    d.ellipse([960, 600, 1040, 640], fill=(170, 160, 150))                          # 粘土
    d.pieslice([1060, 560, 1180, 680], 0, 180, fill=(200, 196, 188))               # 乳鉢
    d.rounded_rectangle([1200, 560, 1300, 640], radius=10, fill=(90, 60, 50))      # 小さな炉
    d.ellipse([1225, 575, 1275, 605], fill=(240, 120, 60))
    for k in range(4):                                                             # 折れた芯
        d.line([(1320 + k * 24, 626), (1340 + k * 24, 618)], fill=GRAPHITE, width=6)
    for k in range(3):                                                             # 木の板（アララギ）
        d.rectangle([1560 + k * 10, 600 - k * 12, 1740 + k * 10, 614 - k * 12], fill=(210, 160, 110),
                    outline=(150, 110, 70), width=2)
    return img


def zukai():
    """図解。溝を9本彫った板、芯、挟んで削った六角の断面。"""
    img = _rgb(base((236, 232, 222), (214, 208, 196)))
    d = _d(img)
    d.rectangle([640, 180, 1280, 330], fill=(224, 190, 140), outline=(160, 120, 80), width=4)   # 板
    for k in range(9):
        x = 680 + k * 66
        d.rectangle([x, 180, x + 20, 330], fill=(190, 150, 100))
        d.rectangle([x + 4, 190, x + 16, 320], fill=GRAPHITE)
    for k in range(3):                                                            # 六角の断面
        cx, cy = 760 + k * 200, 470
        r = 60
        pts = [(cx + r * c, cy + r * s) for c, s in ((1, 0), (0.5, 0.866), (-0.5, 0.866), (-1, 0), (-0.5, -0.866), (0.5, -0.866))]
        d.polygon(pts, fill=(WINE, (40, 110, 70), (230, 190, 60))[k])
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=WOOD)
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=GRAPHITE)
    for k in range(9):                                                            # 濃さの段階（文字なし）
        g = 230 - k * 22
        d.rectangle([650 + k * 70, 580, 710 + k * 70, 640], fill=(g, g, g + 4))
    return img


def zukai2():
    """図解。家紋の三鱗と、3本の局用鉛筆。"""
    img = _rgb(base((236, 232, 222), (214, 208, 196)))
    d = _d(img)
    d.ellipse([740, 160, 1180, 600], fill=(250, 248, 240), outline=(170, 160, 150), width=6)
    _uroko(d, 960, 380, 150)
    for k in range(3):
        _pencil(d, 700, 680 + k * 40, 520, 26, ((40, 40, 44), (60, 60, 64), (80, 80, 86))[k])
    return img


def suisha():
    """竹やぶの中の、傾いた水車小屋の工場。草むらに狸。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, 640), (160, 196, 170), (200, 216, 190)), (0, 0))
    img.paste(vgrad((W, H - 640), (110, 140, 80), (80, 110, 60)), (0, 640))
    d = _d(img)
    for k in range(40):                                                           # 竹
        x = 20 + k * 48
        d.rectangle([x, 0, x + 14, 660], fill=(90, 150, 90))
        for y in range(40, 660, 110):
            d.line([(x, y), (x + 14, y)], fill=(60, 110, 60), width=3)
    d.polygon([(740, 360), (1180, 330), (1170, 660), (750, 660)], fill=(140, 110, 80))   # 傾いた小屋
    d.polygon([(700, 380), (960, 250), (1220, 340)], fill=(90, 80, 70))
    d.rectangle([840, 460, 920, 540], fill=(60, 50, 44))                            # 破れた窓
    d.line([(840, 460), (920, 540)], fill=(140, 110, 80), width=4)
    d.rectangle([980, 520, 1140, 660], fill=(100, 80, 60))                          # 手作りの機械
    d.ellipse([1000, 540, 1060, 600], outline=(60, 60, 64), width=8)
    d.ellipse([1070, 560, 1120, 610], outline=(60, 60, 64), width=6)
    d.rectangle([760, 660, 1160, 700], fill=(80, 110, 150))                         # 流れ
    d.ellipse([640, 520, 780, 660], outline=(110, 80, 50), width=14)                # 水車
    for k in range(8):
        a = k * math.pi / 4
        d.line([(710, 590), (710 + 64 * math.cos(a), 590 + 64 * math.sin(a))], fill=(110, 80, 50), width=8)
    _tanuki(d, 900, 800)                                                            # 狸（草むら）
    return img


def _tanuki(d, cx, cy):
    """草むらに座る狸。目のまわりの黒い模様と、先の黒い太い尻尾（しまは無い）。"""
    body, dark, light = (128, 96, 62), (52, 40, 32), (214, 196, 168)
    d.ellipse([cx + 30, cy + 10, cx + 120, cy + 70], fill=body)                     # 尻尾
    d.ellipse([cx + 84, cy + 16, cx + 122, cy + 64], fill=dark)
    d.ellipse([cx - 70, cy - 30, cx + 70, cy + 90], fill=body)                      # 胴
    d.ellipse([cx - 40, cy + 10, cx + 40, cy + 80], fill=light)                     # おなか
    d.ellipse([cx - 58, cy - 112, cx + 58, cy - 10], fill=body)                     # 頭
    for s in (-1, 1):
        d.polygon([(cx + s * 50, cy - 90), (cx + s * 30, cy - 132), (cx + s * 16, cy - 100)], fill=body)   # 耳
        d.polygon([(cx + s * 42, cy - 96), (cx + s * 30, cy - 122), (cx + s * 22, cy - 102)], fill=dark)
        d.ellipse([cx + s * 30 - 22, cy - 80, cx + s * 30 + 22, cy - 50], fill=dark)   # 目のまわり
        d.ellipse([cx + s * 30 - 7, cy - 72, cx + s * 30 + 7, cy - 58], fill=(250, 250, 244))
        d.ellipse([cx + s * 30 - 3, cy - 68, cx + s * 30 + 3, cy - 62], fill=(20, 20, 20))
    d.ellipse([cx - 26, cy - 58, cx + 26, cy - 22], fill=light)                     # 鼻先
    d.ellipse([cx - 9, cy - 54, cx + 9, cy - 42], fill=dark)
    for s in (-1, 1):
        d.ellipse([cx + s * 44 - 18, cy + 72, cx + s * 44 + 18, cy + 96], fill=dark)   # 足
    for k in range(9):                                                              # 手前の草
        x = cx - 110 + k * 26
        d.polygon([(x, cy + 100), (x + 10, cy + 50 + (k % 3) * 12), (x + 20, cy + 100)], fill=(70, 120, 56))


def nihonbashi():
    """明治の日本橋の問屋。外国製の鉛筆の箱が並ぶ棚。"""
    img = _rgb(base((214, 196, 166), (190, 170, 140)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([0, 80, W, 140], fill=(60, 50, 44))                                 # のれんの上
    for k in range(6):
        d.rectangle([80 + k * 300, 140, 340 + k * 300, 260], fill=(50, 70, 110))
    for x in (60, 1460):
        d.rectangle([x, 300, x + 400, 700], fill=(130, 100, 70))
        for r in range(4):
            for c in range(3):
                _box(d, x + 20 + c * 126, 320 + r * 92, 110, 60, ((200, 170, 60), (40, 90, 60), (140, 40, 40))[(r + c) % 3])
    d.rectangle([760, 640, 1160, 690], fill=(120, 90, 60))                          # 帳場
    for k in range(3):
        _pencil(d, 800, 610 + k * 10, 140, 10, (230, 190, 60))
    return img


def teishin():
    """明治の役所。机の上に3本の鉛筆と、郵便の赤いポスト。"""
    img = _rgb(base((220, 214, 200), (196, 190, 176)))
    wood_floor(img, FLOOR, col=(130, 110, 86), line=(110, 92, 70))
    d = _d(img)
    for x in (120, 1500):
        _window(d, x, 130, x + 300, 440, sky=(180, 204, 222), frame=(110, 90, 70))
    d.rectangle([760, 640, 1160, 690], fill=(110, 80, 56))
    d.rectangle([780, 690, 1140, 860], fill=(90, 66, 46))
    for k in range(3):
        _pencil(d, 820, 590 + k * 16, 220, 14, ((40, 40, 44), (70, 70, 74), (100, 100, 106))[k])
    d.rectangle([1090, 540, 1130, 640], fill=(200, 40, 40))                         # 郵便ポスト（小さな模型）
    d.rectangle([1086, 530, 1134, 544], fill=(160, 30, 30))
    return img


def kojo():
    """大正の鉛筆工場。機械と、束ねた鉛筆。"""
    img = _rgb(base((200, 196, 186), (176, 172, 162)))
    wood_floor(img, FLOOR, col=(130, 126, 116), line=(110, 106, 98))
    d = _d(img)
    for x in (120, 1500):
        _window(d, x, 120, x + 300, 400, sky=(180, 200, 214), frame=(110, 110, 106))
    for k, x in enumerate((780, 1180)):
        d.rectangle([x, 500, x + 300, 720], fill=(70, 74, 80))
        d.ellipse([x + 30, 530, x + 130, 630], outline=(40, 40, 44), width=10)
        d.rectangle([x + 160, 540, x + 280, 600], fill=(120, 120, 126))
    d.rectangle([1520, 640, 1800, 680], fill=(150, 116, 80))
    for k in range(4):
        for j in range(5):
            d.ellipse([1540 + j * 50, 600 - k * 16, 1580 + j * 50, 640 - k * 16], fill=WINE)
    return img


def mise():
    """大正の問屋の帳場。帳面と、鉛筆の箱。"""
    img = _rgb(base((220, 204, 176), (196, 180, 150)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([60, 120, 1860, 460], fill=(130, 100, 70))
    for r in range(2):
        for c in range(12):
            _box(d, 90 + c * 146, 150 + r * 150, 120, 90, ((60, 80, 120), (120, 60, 50), (60, 110, 80))[(r + c) % 3])
    d.rectangle([760, 640, 1160, 690], fill=(110, 80, 56))
    d.rectangle([800, 590, 900, 640], fill=(240, 236, 220), outline=(150, 140, 120), width=2)   # 帳面
    d.rectangle([940, 600, 1100, 640], fill=(60, 60, 64))                                        # そろばん
    for k in range(8):
        d.ellipse([950 + k * 18, 612, 962 + k * 18, 628], fill=(180, 140, 90))
    return img


def yuugure():
    """夕暮れの空と町並み。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, 600), (70, 60, 100), (236, 160, 110)), (0, 0))
    img.paste(vgrad((W, H - 600), (120, 90, 96), (44, 38, 58)), (0, 600))
    d = _d(img)
    d.ellipse([1300, 380, 1480, 560], fill=(250, 206, 150))
    img.paste(vgrad((W, H - 600), (120, 90, 96), (44, 38, 58)), (0, 600))
    d = _d(img)
    for k in range(12):
        x0 = k * 170
        h = 60 + (k * 41) % 90
        d.rectangle([x0, 600 - h, x0 + 150, 600], fill=(56, 46, 64))
    return img


def uni():
    """1958年の文房具店。えんじ色の鉛筆の陳列と、窓の外の電波塔。"""
    img = _rgb(base((232, 226, 212), (210, 202, 186)))
    wood_floor(img, FLOOR, col=(170, 150, 120), line=(150, 130, 100))
    d = _d(img)
    _window(d, 760, 100, 1160, 380, sky=(170, 200, 226), frame=(110, 90, 70))
    d.polygon([(960, 130), (930, 360), (990, 360)], fill=(220, 90, 60))           # 電波塔
    d.line([(945, 250), (975, 250)], fill=(240, 240, 240), width=6)
    d.rectangle([760, 640, 1160, 690], fill=(236, 230, 214))
    d.rectangle([780, 690, 1140, 860], fill=(120, 96, 70))
    d.rectangle([800, 540, 1120, 640], fill=(40, 30, 34), outline=(180, 150, 90), width=4)   # 高級な箱
    for k in range(10):
        _pencil(d, 820, 556 + k * 8, 280, 7)
    return img


def gendai():
    """今の文房具売り場。鉛筆とシャーペンの棚。"""
    img = _rgb(base((244, 244, 240), (226, 226, 220)))
    wood_floor(img, FLOOR, col=(190, 180, 160), line=(170, 160, 140))
    d = _d(img)
    for row, y in enumerate((170, 400)):
        d.rectangle([600, y + 150, 1320, y + 166], fill=(160, 160, 166))
        for k in range(6):
            x = 630 + k * 114
            if row == 0:
                for j in range(4):
                    _pencil(d, x, y + 40 + j * 22, 100, 12, (WINE, (40, 110, 70), (230, 190, 60), (60, 90, 160))[(j + k) % 4])
            else:
                d.rounded_rectangle([x, y + 30, x + 90, y + 146], radius=10, fill=(236, 240, 244), outline=(150, 160, 170), width=3)
                d.rectangle([x + 40, y + 44, x + 50, y + 130], fill=((60, 60, 64), (200, 60, 80), (60, 120, 200))[k % 3])
    return img


# ------------------------------------------------------------ 83_鉛筆の誕生（masaki-pencil-v2）で足した絵
# 既存の絵はそのまま。場面の途中で差し替える絵は「元の背景を呼んで要素を足す」形で作る
# （同じ構図なので切り替わりの差が一目で分かる）。
def _shoji(d, x0, y0, x1, y1, frame=(150, 120, 84), paper=(240, 234, 216)):
    """障子。枠と格子だけ。"""
    d.rectangle([x0, y0, x1, y1], fill=paper, outline=frame, width=10)
    for k in range(1, 4):
        x = x0 + (x1 - x0) * k / 4
        d.line([(x, y0), (x, y1)], fill=frame, width=4)
    for k in range(1, 6):
        y = y0 + (y1 - y0) * k / 6
        d.line([(x0, y), (x1, y)], fill=frame, width=4)


def _vase(d, cx, base_y, h=110, col=(236, 238, 244), pat=(50, 80, 150)):
    """染付の花びん（胴のふくらんだ形）。"""
    w = h * 0.55
    d.ellipse([cx - w / 2, base_y - h * 0.75, cx + w / 2, base_y], fill=col, outline=(150, 150, 160), width=2)
    d.rectangle([cx - w * 0.16, base_y - h, cx + w * 0.16, base_y - h * 0.6], fill=col, outline=(150, 150, 160), width=2)
    d.ellipse([cx - w * 0.24, base_y - h - 6, cx + w * 0.24, base_y - h + 8], fill=col, outline=(150, 150, 160), width=2)
    d.arc([cx - w * 0.36, base_y - h * 0.6, cx + w * 0.36, base_y - h * 0.2], 0, 180, fill=pat, width=5)
    d.arc([cx - w * 0.3, base_y - h * 0.5, cx + w * 0.3, base_y - h * 0.08], 180, 360, fill=pat, width=4)


def _lacquer(d, x, y, w=90, h=46):
    """蒔絵の漆の箱（黒地に金の線）。"""
    d.rounded_rectangle([x, y - h, x + w, y], radius=6, fill=(30, 22, 22))
    d.line([(x + 8, y - h * 0.55), (x + w - 8, y - h * 0.55)], fill=(214, 176, 80), width=3)
    d.arc([x + w * 0.3, y - h * 0.95, x + w * 0.7, y - h * 0.3], 200, 340, fill=(214, 176, 80), width=3)


def _bronze(d, cx, base_y, h=80):
    """銅器（香炉の形）。"""
    col, dark = (128, 104, 64), (90, 72, 44)
    d.ellipse([cx - h * 0.5, base_y - h * 0.7, cx + h * 0.5, base_y - h * 0.1], fill=col, outline=dark, width=3)
    d.rectangle([cx - h * 0.4, base_y - h * 0.82, cx + h * 0.4, base_y - h * 0.66], fill=dark)
    for s in (-1, 0, 1):
        d.rectangle([cx + s * h * 0.3 - 5, base_y - h * 0.18, cx + s * h * 0.3 + 5, base_y], fill=dark)


def _us_flag(d, x, y, w=300, h=160):
    """アメリカの旗（赤白の縞と、白い点を散らした青い角）。"""
    for k in range(13):
        d.rectangle([x, y + k * h / 13, x + w, y + (k + 1) * h / 13], fill=(200, 40, 50) if k % 2 == 0 else (244, 244, 244))
    d.rectangle([x, y, x + w * 0.42, y + h * 7 / 13], fill=(40, 60, 130))
    for r in range(4):
        for c in range(6):
            cx, cy = x + 12 + c * w * 0.42 / 6.2, y + 12 + r * h * 7 / 13 / 4.4
            d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(244, 244, 244))


def zashiki():
    """幕末の佐賀の武家の座敷。床の間に掛け軸（字は無い）と刀掛け、左右に障子。"""
    img = _rgb(base((216, 202, 172), (192, 176, 146)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([0, 150, W, 178], fill=(120, 92, 60))                               # 長押
    _shoji(d, 50, 210, 590, FLOOR - 4)
    _shoji(d, 1330, 210, 1870, FLOOR - 4)
    d.rectangle([700, 200, 1220, 820], fill=(170, 150, 118))                         # 床の間
    d.rectangle([700, 200, 1220, 220], fill=(110, 84, 56))
    d.rectangle([690, 200, 712, FLOOR], fill=(110, 84, 56))                          # 床柱
    d.rectangle([680, 800, 1230, 840], fill=(96, 70, 46))                            # 床板
    d.rectangle([900, 240, 1020, 600], fill=(246, 242, 230), outline=(120, 96, 64), width=6)   # 掛け軸
    d.polygon([(915, 560), (950, 470), (975, 520), (1000, 450), (1008, 560)], fill=(110, 110, 112))  # 山の墨絵
    d.ellipse([965, 300, 995, 330], fill=(190, 60, 50))                              # 朝日
    d.rectangle([892, 600, 1028, 616], fill=(120, 96, 64))
    d.rectangle([830, 760, 850, 800], fill=(60, 40, 30))                             # 刀掛け
    d.rectangle([1070, 760, 1090, 800], fill=(60, 40, 30))
    d.rectangle([820, 752, 1100, 762], fill=(60, 40, 30))
    for k, y in enumerate((732, 708)):                                               # 刀（大小）
        x0, x1 = 800 - k * 10, 1120 + k * 10
        d.line([(x0, y + 6), ((x0 + x1) / 2, y - 6), (x1, y + 6)], fill=(30, 30, 34), width=12, joint="curve")
        d.rectangle([x1 - 70, y - 2, x1 - 60, y + 14], fill=(170, 140, 60))          # 鍔
    return img


def kiritsu():
    """明治のはじめの商社の事務所。工芸品を並べたガラス戸棚と、帳場の机。"""
    img = _rgb(base((228, 216, 192), (202, 188, 160)))
    wood_floor(img, FLOOR, col=(130, 100, 70), line=(108, 82, 58))
    d = _d(img)
    for x in (110, 1510):                                                            # 縦長の洋窓
        d.rectangle([x, 200, x + 300, 620], fill=(176, 204, 222))
        d.pieslice([x, 120, x + 300, 280], 180, 360, fill=(176, 204, 222))
        d.rectangle([x, 200, x + 300, 620], outline=(110, 80, 56), width=12)
        d.arc([x, 120, x + 300, 280], 180, 360, fill=(110, 80, 56), width=12)
        d.line([(x + 150, 130), (x + 150, 620)], fill=(110, 80, 56), width=8)
        d.line([(x, 410), (x + 300, 410)], fill=(110, 80, 56), width=8)
    d.rectangle([680, 170, 1240, 760], fill=(120, 86, 56))                           # ガラス戸棚
    d.rectangle([700, 190, 1220, 740], fill=(214, 226, 230))
    for y in (370, 560, 740):
        d.rectangle([700, y - 10, 1220, y], fill=(120, 86, 56))
    _vase(d, 760, 360, 120)
    _vase(d, 1150, 360, 100, pat=(150, 60, 50))
    _lacquer(d, 830, 360, 120, 50)
    _lacquer(d, 980, 360, 120, 64)
    _bronze(d, 790, 550, 100)
    _bronze(d, 1150, 550, 80)
    _vase(d, 975, 550, 150, col=(240, 236, 226), pat=(60, 110, 90))
    for k in range(3):                                                               # 下の段の反物
        d.rounded_rectangle([730 + k * 160, 640, 860 + k * 160, 730], radius=20,
                            fill=((150, 60, 70), (60, 80, 120), (170, 140, 70))[k])
    d.line([(960, 190), (960, 740)], fill=(120, 86, 56), width=8)                    # 戸のさん
    d.rectangle([740, 800, 1180, 840], fill=(110, 78, 50))                           # 帳場の机
    d.rectangle([760, 840, 784, 990], fill=(90, 62, 40))
    d.rectangle([1136, 840, 1160, 990], fill=(90, 62, 40))
    d.rectangle([800, 770, 900, 800], fill=(240, 236, 220), outline=(150, 140, 120), width=2)   # 帳面
    d.rectangle([960, 776, 1120, 800], fill=(60, 60, 64))                            # そろばん
    for k in range(8):
        d.ellipse([970 + k * 18, 782, 982 + k * 18, 796], fill=(180, 140, 90))
    return img


def phila():
    """1876年の万博の大きな展示館。星条旗と、日本の工芸品の陳列台。"""
    img = _rgb(base((230, 226, 214), (206, 200, 186)))
    wood_floor(img, FLOOR, col=(150, 130, 100), line=(130, 110, 82))
    d = _d(img)
    for k in range(7):                                                               # 木の大屋根のトラス
        x = k * 320
        d.line([(x, 0), (x + 160, 260)], fill=(130, 100, 70), width=10)
        d.line([(x + 320, 0), (x + 160, 260)], fill=(130, 100, 70), width=10)
    d.rectangle([0, 260, W, 280], fill=(130, 100, 70))
    for k in range(6):                                                               # 高窓
        d.rectangle([60 + k * 320, 300, 220 + k * 320, 380], fill=(200, 220, 234), outline=(130, 100, 70), width=6)
    _us_flag(d, 60, 420)
    _us_flag(d, 1560, 420)
    d.rectangle([700, 380, 1220, 420], fill=(60, 50, 44))                            # 日本の出品の看板（字は無い）
    d.rectangle([720, 420, 736, 640], fill=(60, 50, 44))
    d.rectangle([1184, 420, 1200, 640], fill=(60, 50, 44))
    d.rectangle([700, 640, 1220, 690], fill=(120, 86, 56))                           # 陳列台
    d.rectangle([720, 690, 1200, 900], fill=(96, 70, 46))
    _vase(d, 960, 640, 170)                                                          # まん中の花びん
    _vase(d, 790, 640, 110, pat=(150, 60, 50))
    _lacquer(d, 1040, 640, 120, 54)
    _bronze(d, 1160, 640, 70)
    return img


def yoru_shippai():
    """同じ夜の机。炉の煙が部屋に広がり、壁はすすで黒く、机と畳は折れた芯と黒い粉だらけ。"""
    img = yoru()
    import random
    rnd = random.Random(83)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for k in range(9):                                                               # 炉から壁へ上がるすす
        x = 1180 + k * 18
        ld.polygon([(x, 590), (x + 14, 590), (x - 120 + k * 40, 120), (x - 150 + k * 40, 120)],
                   fill=(14, 12, 12, 120))
    for _ in range(26):                                                              # 煙のかたまり
        cx, cy, r = rnd.randint(620, 1880), rnd.randint(140, 620), rnd.randint(60, 150)
        ld.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], fill=(150, 146, 140, 90))
    for _ in range(14):                                                              # 壁の黒いしみ
        cx, cy, r = rnd.randint(640, 1880), rnd.randint(150, 600), rnd.randint(20, 60)
        ld.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], fill=(10, 10, 10, 150))
    from PIL import ImageFilter
    rgba = img.convert("RGBA")
    rgba.alpha_composite(layer.filter(ImageFilter.GaussianBlur(14)))
    img = rgba.convert("RGB")
    d = _d(img)
    for _ in range(40):                                                              # 机の上の折れた芯
        x, y = rnd.randint(840, 1740), rnd.randint(606, 636)
        d.line([(x, y), (x + rnd.randint(14, 30), y - rnd.randint(-8, 8))], fill=GRAPHITE, width=6)
    for _ in range(9):                                                               # 崩れた芯のかたまり
        x, y = rnd.randint(860, 1700), rnd.randint(612, 636)
        d.ellipse([x, y, x + 26, y + 12], fill=(70, 70, 76))
    for _ in range(16):                                                              # 畳の黒い粉の山
        x, y = rnd.randint(640, 1880), rnd.randint(960, 1060)
        w = rnd.randint(40, 110)
        d.ellipse([x, y, x + w, y + w * 0.3], fill=(26, 26, 30))
    for _ in range(30):                                                              # 畳に散った芯
        x, y = rnd.randint(640, 1880), rnd.randint(950, 1070)
        d.line([(x, y), (x + rnd.randint(16, 34), y + rnd.randint(-6, 6))], fill=(20, 20, 24), width=7)
    return img


def yoru_mark():
    """同じ夜の机。壁に眞崎家の家紋の三鱗を描いた紙を貼り、下に局用鉛筆の3種類（濃さ違い）を並べた図。"""
    img = yoru()
    d = _d(img)
    d.rectangle([860, 170, 1180, 540], fill=(246, 242, 228), outline=(170, 160, 140), width=4)   # 貼り紙
    for x in (872, 1168):
        d.ellipse([x - 7, 178, x + 7, 192], fill=(170, 60, 50))                     # 留め鋲
    d.ellipse([920, 200, 1120, 400], outline=(40, 40, 44), width=5)
    _uroko(d, 1020, 300, 70)
    for k in range(3):                                                               # 1号・2号・3号の3種類（濃さ違い）
        _pencil(d, 900, 440 + k * 30, 240, 18, ((40, 40, 44), (80, 80, 86), (130, 130, 136))[k])
    for k, (x, y) in enumerate(((1420, 612), (1330, 618), (1620, 610))):             # 机の上の丸めた下書き
        d.ellipse([x, y, x + 34, y + 26], fill=(236, 232, 220), outline=(170, 160, 140))
    return img


def suisha_ame():
    """同じ水車小屋の雨の日。空が暗く、雨が降り、軒から雨がしたたり、桶がいくつも並ぶ。"""
    img = Image.blend(suisha(), Image.new("RGB", (W, H), (70, 84, 104)), 0.38)
    import random
    rnd = random.Random(1887)
    d = _d(img)
    for _ in range(420):                                                             # 雨すじ
        x, y = rnd.randint(-100, W), rnd.randint(-40, H)
        L = rnd.randint(30, 60)
        d.line([(x, y), (x + L * 0.35, y + L)], fill=(206, 216, 232), width=2)
    for x in range(760, 1180, 34):                                                   # 軒からのしずく
        for j in range(3):
            y = 380 + j * 60 + (x % 3) * 10
            d.ellipse([x - 4, y, x + 4, y + 14], fill=(200, 220, 240))
    for cx, cy, w in ((560, 960, 240), (1250, 1000, 320), (1600, 940, 200), (300, 1030, 260)):   # 水たまり
        d.ellipse([cx - w / 2, cy - w * 0.12, cx + w / 2, cy + w * 0.12], fill=(120, 140, 170))
    for k, x in enumerate((790, 880, 1040, 1150)):                                   # 雨漏りを受ける桶
        y = 690 + (k % 2) * 10
        d.polygon([(x - 34, y - 50), (x + 34, y - 50), (x + 26, y), (x - 26, y)], fill=(150, 112, 70), outline=(90, 66, 40))
        d.line([(x - 31, y - 30), (x + 31, y - 30)], fill=(70, 70, 76), width=4)
        d.ellipse([x - 30, y - 56, x + 30, y - 44], fill=(120, 150, 190))
    return img


def mise_kinpai():
    """同じ問屋の帳場。棚の中央に賞状の額（字は無い）と金牌・銀牌が飾られている。"""
    img = mise()
    d = _d(img)
    d.rectangle([660, 130, 1260, 450], fill=(150, 116, 80))                          # 飾り板
    for k, x in enumerate((690, 890, 1090)):                                         # 賞状の額
        d.rectangle([x, 160, x + 140, 330], fill=(190, 150, 60))
        d.rectangle([x + 12, 172, x + 128, 318], fill=(248, 244, 232))
        d.rectangle([x + 30, 190, x + 110, 210], fill=(200, 60, 50) if k == 1 else (90, 90, 100))
        for j in range(4):
            d.line([(x + 30, 236 + j * 18), (x + 110, 236 + j * 18)], fill=(170, 166, 156), width=3)
    for k, (x, col) in enumerate(((760, (226, 186, 70)), (960, (226, 186, 70)), (1160, (196, 198, 206)))):   # 金牌・金牌・銀牌
        d.polygon([(x - 18, 340), (x + 18, 340), (x + 10, 380), (x - 10, 380)], fill=(190, 40, 50))
        d.ellipse([x - 34, 372, x + 34, 440], fill=col, outline=tuple(int(c * 0.7) for c in col), width=4)
        d.ellipse([x - 20, 386, x + 20, 426], outline=tuple(int(c * 0.8) for c in col), width=3)
    return img


def kojo_bunkatsu():
    """同じ大井の工場。2台の機械のあいだに仕切りの板塀が立ち、床にも杭と縄で境目が引かれている。"""
    img = kojo()
    d = _d(img)
    x0, x1 = 1088, 1172
    d.rectangle([x0, 150, x1, FLOOR + 6], fill=(150, 116, 80), outline=(100, 76, 52), width=4)   # 仕切りの板塀
    for x in range(x0 + 21, x1, 21):
        d.line([(x, 154), (x, FLOOR + 2)], fill=(116, 88, 60), width=3)
    for y in (260, 560, 840):
        d.rectangle([x0 - 6, y, x1 + 6, y + 16], fill=(100, 76, 52))
    d.polygon([(1112, FLOOR + 6), (1148, FLOOR + 6), (1200, H), (1140, H)], fill=(236, 232, 220))   # 床の境目の白線
    return img


def kojo_yuu():
    """同じ大井の工場の夕方（1921年に敷地を分けた後なので仕切りの塀がある）。西日で部屋全体が赤く染まる。"""
    img = Image.blend(kojo_bunkatsu(), Image.new("RGB", (W, H), (230, 130, 70)), 0.26)
    d = _d(img)
    for x in (120, 1500):                                                            # 窓の夕焼け
        sky = vgrad((280, 260), (236, 150, 100), (250, 206, 150))
        img.paste(sky, (x + 10, 130))
        d = _d(img)
        d.rectangle([x, 120, x + 300, 400], outline=(110, 90, 80), width=10)
        d.line([(x + 150, 120), (x + 150, 400)], fill=(110, 90, 80), width=8)
    _glow(img, 1650, 300, 420, (255, 180, 110), 80)
    _glow(img, 270, 300, 300, (255, 180, 110), 60)
    return img


LOCATIONS = {
    "pc_ima": ima, "pc_ima2": ima2, "pc_kunozan": kunozan, "pc_saga": saga, "pc_paris": paris,
    "pc_sekai": sekai, "pc_yoru": yoru, "pc_zukai": zukai, "pc_zukai2": zukai2, "pc_suisha": suisha,
    "pc_nihonbashi": nihonbashi, "pc_teishin": teishin, "pc_kojo": kojo, "pc_mise": mise,
    "pc_yuugure": yuugure, "pc_uni": uni, "pc_gendai": gendai,
    # 83_鉛筆の誕生（masaki-pencil-v2）で足した絵
    "pc_zashiki": zashiki, "pc_kiritsu": kiritsu, "pc_phila": phila,
    "pc_yoru_shippai": yoru_shippai, "pc_yoru_mark": yoru_mark, "pc_suisha_ame": suisha_ame,
    "pc_mise_kinpai": mise_kinpai, "pc_kojo_bunkatsu": kojo_bunkatsu, "pc_kojo_yuu": kojo_yuu,
}

CARDS = ["1878", "1887", "1901", "1848", "1925"]


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
        if only and f"pc_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"pc_card_{y}.png")
        print(f"生成完了: pc_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
