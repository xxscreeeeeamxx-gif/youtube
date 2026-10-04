#!/usr/bin/env python3
"""オセロの誕生・長谷川五郎回（57_オセロの誕生 / slug=othello-hasegawa）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はカニカマ回（gen_kanikama_bgs.py）と同じ。
実在メーカーの商標（ロゴ・商品名の文字）は描かない。

81_オセロの誕生（slug=othello-hasegawa-v2・作り直し）では、既存の絵は変えずに
場面の途中で差し替える絵（os_mito_yake / os_bushitsu_ban / os_yoru_futa / os_denwa_yuu / os_depart_kara）と
新しい場面の絵（os_kaisha_shogi / os_benkyou / os_densha / os_shosai / os_shosai_kara）、
年号カード 1932・2006・2016 を足した。足した絵だけを書き出すときは名前を指定して実行する。

実行: PYTHONPATH=. python scripts/gen_othello_bgs.py [名前...]
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
GREEN = (38, 120, 70)
GREEN_D = (22, 80, 46)
BLACK = (24, 24, 26)
WHITE = (244, 242, 236)


def _d(img):
    return ImageDraw.Draw(img)


def _glow(img, cx, cy, r, color, alpha=110):
    """glow() は RGBA に合成するので、変換した結果を貼り戻す必要がある。"""
    rgba = img.convert("RGBA")
    glow(rgba, cx, cy, r, color, alpha)
    img.paste(rgba.convert("RGB"), (0, 0))


def _rgb(img):
    return img.convert("RGB") if img.mode != "RGB" else img


def _window(d, x0, y0, x1, y1, sky=(150, 186, 214), frame=(70, 62, 56)):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)


def _board(d, cx, ytop, ybot, wtop, wbot, stones=None, col=GREEN, line=GREEN_D,
           frame=(30, 30, 30), black=BLACK, white=WHITE):
    """斜めから見た8マスの盤。stones は {(行, 列): 'b' か 'w'}。"""
    stones = stones or {}

    def pt(r, c):
        f = r / 8
        w = wtop + (wbot - wtop) * f
        return cx - w / 2 + w * c / 8, ytop + (ybot - ytop) * f

    fr = 10
    d.polygon([(cx - wtop / 2 - fr, ytop - fr), (cx + wtop / 2 + fr, ytop - fr),
               (cx + wbot / 2 + fr, ybot + fr), (cx - wbot / 2 - fr, ybot + fr)], fill=frame)
    d.polygon([pt(0, 0), pt(0, 8), pt(8, 8), pt(8, 0)], fill=col)
    for i in range(9):
        d.line([pt(i, 0), pt(i, 8)], fill=line, width=3)
        d.line([pt(0, i), pt(8, i)], fill=line, width=3)
    for (r, c), s in stones.items():
        x, y = pt(r + 0.5, c + 0.5)
        f = (r + 0.5) / 8
        cw = (wtop + (wbot - wtop) * f) / 8
        ch = (ybot - ytop) / 8
        rx, ry = cw * 0.4, ch * 0.4
        d.ellipse([x - rx, y - ry + 3, x + rx, y + ry + 3], fill=(10, 10, 10))
        d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=black if s == 'b' else white)


def _flat_board(d, x0, y0, size, stones=None, col=GREEN, line=GREEN_D, frame=(30, 30, 30),
                black=BLACK, white=WHITE):
    """真上から見た盤（図解用）。"""
    stones = stones or {}
    c = size / 8
    d.rectangle([x0 - 16, y0 - 16, x0 + size + 16, y0 + size + 16], fill=frame)
    d.rectangle([x0, y0, x0 + size, y0 + size], fill=col)
    for i in range(9):
        d.line([(x0 + i * c, y0), (x0 + i * c, y0 + size)], fill=line, width=4)
        d.line([(x0, y0 + i * c), (x0 + size, y0 + i * c)], fill=line, width=4)
    for (r, cc), s in stones.items():
        x, y = x0 + (cc + 0.5) * c, y0 + (r + 0.5) * c
        rr = c * 0.4
        d.ellipse([x - rr, y - rr + 4, x + rr, y + rr + 4], fill=(10, 10, 10))
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=black if s == 'b' else white)


def _cap(d, x, y, r=20, black=False):
    """牛乳瓶の紙のフタ（上から少し斜めに見た形）。black=True なら黒い紙を貼った面。"""
    ry = int(r * 0.6)
    d.ellipse([x - r, y - ry + 4, x + r, y + ry + 4], fill=(150, 146, 136))
    if black:
        d.ellipse([x - r, y - ry, x + r, y + ry], fill=BLACK)
        return
    d.ellipse([x - r, y - ry, x + r, y + ry], fill=(248, 246, 238))
    d.ellipse([x - r + 5, y - ry + 3, x + r - 5, y + ry - 3], outline=(90, 130, 200), width=3)


def _bottle(d, x, y, h=120):
    """牛乳瓶（紙のフタ付き）。x は中心、y は底。"""
    w = h * 0.42
    d.rounded_rectangle([x - w / 2, y - h * 0.72, x + w / 2, y], radius=10, fill=(236, 238, 240),
                        outline=(170, 180, 190), width=3)
    d.rectangle([x - w * 0.3, y - h, x + w * 0.3, y - h * 0.7], fill=(236, 238, 240),
                outline=(170, 180, 190), width=3)
    d.ellipse([x - w * 0.34, y - h - 8, x + w * 0.34, y - h + 8], fill=(248, 246, 238),
              outline=(90, 130, 200), width=3)


def _goishi(d, x, y, r=12, black=True):
    d.ellipse([x - r, y - r * 0.6 + 3, x + r, y + r * 0.6 + 3], fill=(60, 56, 50))
    d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=BLACK if black else WHITE)


def _toybox(d, x, y, w, h, col):
    """文字のないおもちゃの箱。"""
    d.rectangle([x, y, x + w, y + h], fill=col, outline=tuple(int(c * 0.6) for c in col), width=3)
    d.rectangle([x + 8, y + 8, x + w - 8, y + h * 0.45], fill=tuple(min(255, int(c * 1.25)) for c in col))


def _othello_box(d, x, y, w=150, h=110):
    """黒い箱に緑の盤の絵（文字なし）。"""
    d.rectangle([x, y, x + w, y + h], fill=(20, 20, 24), outline=(80, 80, 86), width=3)
    s = min(w, h) - 30
    bx, by = x + (w - s) / 2, y + 15
    d.rectangle([bx, by, bx + s, by + s], fill=GREEN)
    for i in range(1, 4):
        d.line([(bx + s * i / 4, by), (bx + s * i / 4, by + s)], fill=GREEN_D, width=2)
        d.line([(bx, by + s * i / 4), (bx + s, by + s * i / 4)], fill=GREEN_D, width=2)
    rr = s / 10
    for k, (dx, dy) in enumerate(((0.5, 0.5), (0.5, 0.75), (0.25, 0.5))):
        cx, cy = bx + s * dx - s / 8 + s / 8, by + s * dy - s / 8
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=WHITE if k % 2 else BLACK)


START = {(3, 3): 'w', (4, 4): 'w', (3, 4): 'b', (4, 3): 'b'}


# ------------------------------------------------------------ 現代
def ima():
    """今の居間。机の上にオセロ盤（黒が多い）。"""
    img = _rgb(base((236, 232, 222), (214, 208, 196)))
    wood_floor(img, FLOOR, col=(170, 140, 104), line=(150, 122, 90))
    d = _d(img)
    _window(d, 740, 110, 1180, 380, sky=(176, 210, 232))
    d.rectangle([760, 640, 1160, 690], fill=(160, 124, 88))                # 机
    d.rectangle([780, 690, 800, 820], fill=(130, 100, 70))
    d.rectangle([1120, 690, 1140, 820], fill=(130, 100, 70))
    st = {}
    for r in range(8):
        for c in range(8):
            if (r * 3 + c * 5) % 7 in (0, 1, 2, 4) and 1 <= r <= 6:
                st[(r, c)] = 'b'
    st.update({(3, 3): 'w', (5, 5): 'w'})
    _board(d, 960, 520, 632, 230, 330, st)
    return img


def ima2():
    """今の居間。締め用。盤は黒と白が半分ずつ。"""
    img = ima()
    d = _d(img)
    st = {(r, c): ('b' if (r * 5 + c * 3) % 2 == 0 else 'w') for r in range(8) for c in range(8)}
    _board(d, 960, 520, 632, 230, 330, st)
    return img


def senshu():
    """今の世界選手権の会場。対局机が並び、時計が置いてある。"""
    img = _rgb(base((226, 230, 236), (200, 206, 214)))
    wood_floor(img, FLOOR, col=(90, 100, 120), line=(76, 86, 104))
    d = _d(img)
    for k in range(6):                                                      # 旗（文字なし）
        x = 300 + k * 240
        d.rectangle([x, 80, x + 150, 180], fill=((220, 60, 60), (60, 110, 200), (240, 200, 70),
                                                   (70, 160, 110), (240, 240, 240), (150, 80, 170))[k])
        d.rectangle([x, 80, x + 150, 180], outline=(120, 120, 130), width=3)
    d.line([(200, 80), (1720, 80)], fill=(120, 120, 130), width=4)
    for cx in (620, 960, 1300):
        d.rectangle([cx - 150, 640, cx + 150, 680], fill=(236, 236, 240))
        d.rectangle([cx - 150, 680, cx + 150, 800], fill=(40, 60, 110))
        _board(d, cx, 560, 636, 170, 220, START | {(2, (cx // 9) % 8): 'b', (5, (cx // 13) % 8): 'w'})
        d.rectangle([cx + 100, 600, cx + 150, 636], fill=(30, 30, 34))       # 対局時計
        d.rectangle([cx + 106, 606, cx + 144, 622], fill=(150, 220, 170))
    return img


def mito():
    """戦前の水戸。低い家並みと、遠くの丘。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, 620), (170, 200, 222), (222, 224, 210)), (0, 0))
    img.paste(vgrad((W, H - 620), (150, 140, 110), (120, 110, 86)), (0, 620))
    d = _d(img)
    d.ellipse([-300, 420, 900, 760], fill=(110, 136, 100))
    d.ellipse([1000, 440, 2300, 780], fill=(104, 130, 96))
    for k in range(9):
        x0 = 60 + k * 210
        h = 130 + (k * 37) % 60
        d.rectangle([x0, 640 - h, x0 + 170, 640], fill=(126, 102, 78))
        d.polygon([(x0 - 20, 652 - h), (x0 + 85, 580 - h), (x0 + 190, 652 - h)], fill=(70, 66, 70))
        d.rectangle([x0 + 30, 580 - h + 110, x0 + 70, 620], fill=(96, 78, 60))
    d.rectangle([0, 640, W, 690], fill=(160, 146, 116))
    for x in range(40, W, 180):                                              # 電柱
        d.line([(x, 470), (x, 700)], fill=(90, 76, 60), width=8)
    return img


def aozora():
    """焼け跡の土手の青空授業。黒板と、地面に並べた碁石。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, 640), (120, 176, 230), (200, 222, 236)), (0, 0))
    img.paste(vgrad((W, H - 640), (150, 128, 96), (116, 96, 70)), (0, 640))
    d = _d(img)
    d.polygon([(0, 640), (W, 640), (W, 600), (0, 610)], fill=(130, 140, 90))    # 土手の草
    for x, h in ((120, 260), (300, 190), (1560, 240), (1760, 300)):           # 焼けた柱
        d.rectangle([x, 640 - h, x + 26, 640], fill=(46, 40, 36))
        d.line([(x - 30, 640 - h + 40), (x + 60, 640 - h + 10)], fill=(46, 40, 36), width=12)
    d.rectangle([840, 170, 1080, 360], fill=(40, 70, 56), outline=(120, 90, 60), width=10)   # 黒板
    d.line([(870, 380), (860, 560)], fill=(120, 90, 60), width=10)
    d.line([(1050, 380), (1060, 560)], fill=(120, 90, 60), width=10)
    for k, (x, y) in enumerate(((880, 220), (930, 260), (990, 230), (900, 310))):
        d.line([(x, y), (x + 50, y + 4)], fill=(230, 230, 220), width=4)
    # 地面の板と碁石（2人の場面の真ん中）
    d.rectangle([850, 810, 1070, 880], fill=(170, 140, 100), outline=(120, 96, 66), width=4)
    for k in range(10):
        _goishi(d, 870 + (k % 5) * 44, 830 + (k // 5) * 30, r=13, black=k % 3 != 0)
    # もう1組（3人の場面の右のすき間）
    d.rectangle([1195, 830, 1350, 890], fill=(170, 140, 100), outline=(120, 96, 66), width=4)
    for k in range(8):
        _goishi(d, 1212 + (k % 4) * 40, 848 + (k // 4) * 28, r=12, black=k % 2 == 0)
    # 表と裏を塗り分けた紙の駒（左のすき間）
    for k in range(5):
        x = 650 + k * 32
        d.rectangle([x, 850, x + 24, 872], fill=BLACK if k % 2 else WHITE, outline=(80, 70, 60), width=2)
    return img


def kyoushitsu():
    """戦後すぐの木造の教室。机の上に大きな駒。"""
    img = _rgb(base((206, 190, 160), (184, 166, 136)))
    wood_floor(img, FLOOR, col=(150, 120, 84), line=(128, 100, 70))
    d = _d(img)
    d.rectangle([600, 120, 1320, 400], fill=(40, 70, 56), outline=(110, 84, 56), width=12)   # 黒板
    for x in (140, 1560):
        _window(d, x, 150, x + 240, 520, sky=(180, 210, 230), frame=(110, 84, 56))
    d.rectangle([780, 640, 1140, 680], fill=(150, 116, 80))                 # 机
    d.rectangle([800, 680, 820, 830], fill=(120, 92, 64))
    d.rectangle([1100, 680, 1120, 830], fill=(120, 92, 64))
    for k in range(6):
        x = 820 + k * 52
        d.ellipse([x, 600 + (k % 2) * 14, x + 44, 626 + (k % 2) * 14], fill=(90, 80, 70))
        d.ellipse([x, 596 + (k % 2) * 14, x + 44, 622 + (k % 2) * 14], fill=BLACK if k % 2 else WHITE)
    return img


def byouin():
    """1950年代の病室。鉄のベッドと窓。"""
    img = _rgb(base((226, 228, 222), (204, 206, 198)))
    wood_floor(img, FLOOR, col=(170, 164, 150), line=(150, 144, 130))
    d = _d(img)
    _window(d, 780, 140, 1140, 460, sky=(186, 214, 230), frame=(150, 150, 146))
    d.rectangle([60, 600, 720, 700], fill=(240, 240, 236), outline=(160, 160, 156), width=4)   # ベッド
    d.rectangle([60, 520, 80, 820], fill=(110, 110, 116))
    d.rectangle([700, 560, 720, 820], fill=(110, 110, 116))
    d.rectangle([860, 640, 1060, 820], fill=(200, 196, 184), outline=(150, 146, 136), width=4)  # 棚
    d.rectangle([900, 590, 930, 640], fill=(140, 110, 70))                   # 薬びん
    d.rectangle([950, 600, 990, 640], fill=(230, 230, 236), outline=(160, 160, 170), width=2)
    return img


def bushitsu():
    """大学の部室。碁盤と将棋盤、真ん中の机に紙の盤。"""
    img = _rgb(base((214, 204, 180), (192, 180, 156)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    for k in range(4):                                                      # 壁の掛け軸（文字なし）
        x = 180 + k * 460
        d.rectangle([x, 110, x + 90, 360], fill=(236, 226, 200), outline=(120, 96, 70), width=5)
    d.rectangle([80, 700, 380, 780], fill=(200, 160, 100))                   # 碁盤
    for k in range(5):
        d.line([(100 + k * 65, 710), (100 + k * 65, 770)], fill=(80, 60, 40), width=2)
    d.rectangle([1560, 700, 1840, 780], fill=(210, 176, 110))                # 将棋盤
    d.rectangle([800, 650, 1120, 690], fill=(150, 116, 80))                  # 机
    d.rectangle([820, 690, 840, 840], fill=(120, 92, 64))
    d.rectangle([1080, 690, 1100, 840], fill=(120, 92, 64))
    _board(d, 960, 560, 640, 200, 280, START | {(2, 3): 'b', (2, 4): 'w', (5, 2): 'b'},
           col=(230, 222, 200), line=(90, 80, 70), frame=(120, 110, 96))
    return img


def yoru():
    """1964年の夜の机。牛乳瓶、フタ、黒い紙、手描きの盤。"""
    img = _rgb(base((70, 62, 70), (46, 40, 48)))
    wood_floor(img, FLOOR, col=(90, 72, 60), line=(72, 58, 48))
    d = _d(img)
    d.rectangle([800, 640, 1760, 690], fill=(130, 98, 70))                  # 机
    d.rectangle([830, 690, 856, 900], fill=(100, 76, 56))
    d.rectangle([1700, 690, 1726, 900], fill=(100, 76, 56))
    _glow(img, 1500, 420, 260, (255, 210, 140), 90)                          # 電気スタンド
    d = _d(img)
    d.line([(1560, 640), (1560, 440)], fill=(60, 60, 64), width=8)
    d.polygon([(1480, 440), (1640, 440), (1600, 380), (1520, 380)], fill=(60, 110, 90))
    for k, x in enumerate((880, 960, 1040)):
        _bottle(d, x, 636, h=130)
    for k in range(3):                                                      # 3枚重ねのフタ
        for j in range(3):
            _cap(d, 1130 + k * 56, 612 - j * 7, r=22, black=(j == 2 and k != 1))
    d.rectangle([1320, 590, 1440, 630], fill=(20, 20, 22))                  # 黒い紙
    d.rectangle([1340, 580, 1460, 620], fill=(34, 34, 38))
    _board(d, 1260, 470, 560, 180, 230, {(3, 3): 'w', (4, 4): 'w', (3, 4): 'b', (4, 3): 'b'},
           col=(236, 230, 214), line=(90, 84, 76), frame=(150, 140, 120))
    return img


def kaisha():
    """1960年代の会社の事務所。机の上に盤とフタの駒。"""
    img = _rgb(base((218, 216, 206), (196, 194, 184)))
    wood_floor(img, FLOOR, col=(150, 150, 140), line=(130, 130, 122))
    d = _d(img)
    for x in (120, 1500):
        _window(d, x, 130, x + 300, 440, sky=(176, 206, 226), frame=(120, 120, 116))
    d.ellipse([900, 110, 1020, 230], fill=(240, 240, 236), outline=(90, 90, 90), width=6)   # 時計
    d.line([(960, 170), (960, 130)], fill=(40, 40, 40), width=5)
    d.line([(960, 170), (990, 170)], fill=(40, 40, 40), width=5)
    d.rectangle([770, 650, 1150, 700], fill=(120, 130, 136))                # 事務机
    d.rectangle([790, 700, 1130, 860], fill=(110, 120, 126))
    _board(d, 960, 560, 646, 200, 270, {(3, 3): 'w', (4, 4): 'w', (3, 4): 'b', (4, 3): 'b',
                                        (2, 4): 'b', (5, 3): 'w'},
           col=(236, 230, 214), line=(90, 84, 76), frame=(150, 140, 120))
    for k in range(4):
        _cap(d, 1080 + (k % 2) * 40, 630 - (k // 2) * 16, r=16, black=k % 2 == 0)
    return img


def byouin2():
    """病院の談話室。窓辺の机で盤を囲む。"""
    img = _rgb(base((232, 234, 228), (210, 214, 206)))
    wood_floor(img, FLOOR, col=(180, 176, 160), line=(160, 156, 140))
    d = _d(img)
    for x in (620, 1060):
        _window(d, x, 130, x + 240, 420, sky=(190, 218, 232), frame=(160, 160, 156))
    d.rectangle([40, 120, 200, 800], fill=(200, 222, 214))                  # カーテン
    d.rectangle([1720, 120, 1880, 800], fill=(200, 222, 214))
    d.rectangle([790, 650, 1130, 690], fill=(200, 190, 170))                # 机
    d.rectangle([810, 690, 830, 830], fill=(160, 150, 130))
    d.rectangle([1090, 690, 1110, 830], fill=(160, 150, 130))
    _board(d, 960, 560, 646, 200, 270, START | {(2, 2): 'b', (5, 5): 'w', (2, 3): 'b'},
           col=(236, 230, 214), line=(90, 84, 76), frame=(150, 140, 120))
    return img


def goraku():
    """会社の娯楽室。手作りの盤がいくつも並ぶ。"""
    img = _rgb(base((226, 216, 196), (204, 192, 170)))
    wood_floor(img, FLOOR, col=(160, 130, 96), line=(140, 112, 80))
    d = _d(img)
    for k in range(18):                                                     # 紙の飾り
        x = 40 + k * 110
        d.polygon([(x, 90), (x + 90, 90), (x + 45, 150)],
                  fill=((230, 90, 80), (240, 200, 80), (90, 150, 220))[k % 3])
    d.line([(0, 90), (W, 90)], fill=(120, 100, 80), width=4)
    for cx in (1000, 1360, 1720):
        d.rectangle([cx - 150, 650, cx + 150, 690], fill=(150, 116, 80))
        d.rectangle([cx - 130, 690, cx - 112, 840], fill=(120, 92, 64))
        d.rectangle([cx + 112, 690, cx + 130, 840], fill=(120, 92, 64))
        _board(d, cx, 566, 646, 170, 230, START | {((cx // 7) % 8, 2): 'b', (5, (cx // 11) % 8): 'w'},
               col=(236, 230, 214), line=(90, 84, 76), frame=(150, 140, 120))
    return img


def jikka():
    """1968年の水戸の実家。英語の本の棚と、ちゃぶ台の上の盤。"""
    img = _rgb(base((214, 200, 172), (190, 176, 148)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([60, 110, 1860, 470], fill=(150, 116, 80))                  # 本棚
    for row, y in enumerate((130, 300)):
        d.rectangle([80, y + 150, 1840, y + 164], fill=(110, 84, 58))
        for k in range(88):
            x = 90 + k * 20
            h = 110 + (k * 13) % 30
            col = ((140, 50, 50), (50, 70, 120), (60, 100, 70), (170, 140, 90), (90, 60, 50))[(k + row) % 5]
            d.rectangle([x, y + 150 - h, x + 16, y + 150], fill=col)
    d.ellipse([650, 690, 890, 740], fill=(120, 84, 56))                     # ちゃぶ台
    d.rectangle([690, 715, 706, 830], fill=(100, 70, 46))
    d.rectangle([834, 715, 850, 830], fill=(100, 70, 46))
    _board(d, 770, 616, 700, 150, 200, START | {(2, 3): 'b', (5, 4): 'w', (2, 2): 'w'},
           col=(236, 230, 214), line=(90, 84, 76), frame=(150, 140, 120))   # 試作品（まだ緑ではない）
    return img


def butai():
    """劇場の舞台。スポットライトの中に、黒と白の半分ずつの石。"""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, H), (40, 28, 34), (20, 14, 18)), (0, 0))
    d = _d(img)
    d.rectangle([0, 780, W, H], fill=(110, 76, 50))
    for x in range(0, W, 120):
        d.line([(x, 780), (x - 60, H)], fill=(90, 62, 42), width=4)
    _glow(img, 960, 520, 360, (255, 236, 190), 90)
    d = _d(img)
    for side in (0, 1):                                                    # 幕
        for k in range(6):
            x = (k * 70) if side == 0 else (W - 420 + k * 70)
            d.rectangle([x, 0, x + 70, 900], fill=(150 - k * 6, 30, 40) if k % 2 else (130 - k * 6, 24, 34))
    d.rectangle([0, 0, W, 80], fill=(120, 24, 34))
    d.pieslice([780, 250, 1140, 610], 90, 270, fill=BLACK)                  # 半分黒・半分白
    d.pieslice([780, 250, 1140, 610], 270, 90, fill=WHITE)
    d.ellipse([780, 250, 1140, 610], outline=(200, 190, 170), width=6)
    return img


def tsukuda():
    """1972年のおもちゃ会社。箱の並ぶ棚と、机の上の厚紙の盤。"""
    img = _rgb(base((226, 222, 212), (204, 200, 190)))
    wood_floor(img, FLOOR, col=(150, 140, 126), line=(130, 120, 108))
    d = _d(img)
    d.rectangle([60, 110, 1860, 460], fill=(170, 150, 120))                 # 棚
    cols = [(220, 80, 70), (70, 130, 200), (240, 190, 70), (90, 170, 110), (180, 110, 180)]
    for row, y in enumerate((130, 300)):
        d.rectangle([80, y + 140, 1840, y + 154], fill=(130, 110, 86))
        for k in range(14):
            x = 100 + k * 124
            _toybox(d, x, y + 20 + (k % 3) * 10, 110, 120 - (k % 3) * 10, cols[(k + row * 2) % 5])
    d.rectangle([700, 650, 1160, 700], fill=(150, 116, 80))                 # 机
    d.rectangle([720, 700, 740, 860], fill=(120, 92, 64))
    d.rectangle([1120, 700, 1140, 860], fill=(120, 92, 64))
    _board(d, 820, 570, 640, 120, 160, START | {(2, 4): 'b', (5, 3): 'w'},
           col=(214, 196, 160), line=(110, 96, 76), frame=(170, 150, 120))
    d.rectangle([960, 600, 1110, 640], fill=GREEN, outline=GREEN_D, width=3)   # フェルトの見本
    for k in range(3):
        _cap(d, 1000 + k * 40, 590, r=16, black=k == 1)
    return img


def hako():
    """発売当時の箱の写真のイメージ。盤と、たばことライター。"""
    img = _rgb(base((200, 190, 176), (176, 166, 150)))
    d = _d(img)
    d.rectangle([600, 160, 1320, 820], fill=(28, 26, 30), outline=(170, 150, 110), width=10)
    d.rectangle([640, 200, 1280, 780], fill=(70, 50, 40))                   # 写真の中の机
    _board(d, 900, 300, 690, 300, 400, START | {(2, 3): 'b', (5, 4): 'w', (2, 4): 'w', (1, 2): 'b'})
    d.rectangle([1130, 560, 1250, 600], fill=(236, 236, 230))               # たばこの箱
    d.rectangle([1130, 540, 1250, 560], fill=(180, 60, 50))
    for k in range(2):
        d.rectangle([1150 + k * 30, 520, 1164 + k * 30, 540], fill=(240, 236, 220))
    d.rounded_rectangle([1150, 640, 1220, 740], radius=8, fill=(190, 180, 150))   # ライター
    d.rectangle([1150, 640, 1220, 668], fill=(150, 140, 110))
    return img


def zukai():
    """図解。真上から見た盤に、最初の4つの石。"""
    img = _rgb(base((236, 232, 222), (214, 208, 196)))
    d = _d(img)
    _flat_board(d, 700, 160, 520, START)
    return img


def computer():
    """図解。昔のパソコンの画面に盤。"""
    img = _rgb(base((40, 46, 60), (24, 28, 38)))
    d = _d(img)
    d.rectangle([640, 160, 1280, 700], fill=(200, 196, 184), outline=(150, 146, 136), width=8)   # 本体
    d.rectangle([690, 200, 1230, 620], fill=(10, 20, 16))
    st = dict(START)
    st.update({(2, 3): 'b', (2, 4): 'w', (5, 2): 'b', (1, 1): 'w', (6, 5): 'b', (3, 2): 'w'})
    _flat_board(d, 800, 230, 320, st, col=(30, 110, 60), line=(20, 70, 40), frame=(10, 20, 16))
    d.rectangle([880, 700, 1040, 760], fill=(170, 166, 156))
    d.rectangle([700, 780, 1220, 830], fill=(210, 206, 196), outline=(150, 146, 136), width=4)   # キーボード
    for k in range(12):
        d.rectangle([720 + k * 42, 792, 752 + k * 42, 818], fill=(236, 234, 226))
    return img


def hotel():
    """ホテルの大広間。シャンデリアと、盤の並ぶ机。"""
    img = base((96, 76, 70), (70, 56, 54))
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(120, W, 440):
        d.rectangle([x, 120, x + 320, 560], outline=(126, 100, 86), width=8)
    for lx in (520, 1400):
        d.line([lx, 0, lx, 110], fill=(70, 58, 52), width=6)
        glow(img, lx, 190, 240, (255, 214, 150), 60)
        d = ImageDraw.Draw(img, "RGBA")
        for k in range(3):
            d.ellipse([lx - 70 + k * 50, 130, lx - 30 + k * 50, 190], fill=(255, 228, 170))
    d.rectangle([0, int(H * 0.74), W, H], fill=(120, 50, 50))
    img = img.convert("RGB")
    d = _d(img)
    for cx, y in ((960, 640), (620, 580), (1300, 580)):
        d.rectangle([cx - 170, y, cx + 170, y + 40], fill=(240, 236, 226))  # 白い布の机
        d.rectangle([cx - 170, y + 40, cx + 170, y + 150], fill=(226, 222, 212))
        _board(d, cx, y - 70, y + 4, 170, 220, START | {(2, (cx // 9) % 8): 'b', (5, (cx // 13) % 8): 'w'})
    return img


def kiji():
    """1973年の新聞社。机の上の盤と、原稿の束。"""
    img = _rgb(base((206, 204, 196), (184, 182, 174)))
    wood_floor(img, FLOOR, col=(140, 136, 126), line=(120, 116, 108))
    d = _d(img)
    for x in (820, 1400):
        _window(d, x, 130, x + 340, 420, sky=(170, 196, 216), frame=(110, 110, 106))
    d.rectangle([900, 650, 1700, 700], fill=(120, 110, 96))                 # 机
    d.rectangle([920, 700, 1680, 860], fill=(108, 98, 86))
    for k in range(4):                                                      # 原稿の束
        d.rectangle([1480 + k * 6, 600 - k * 10, 1640 + k * 6, 620 - k * 10], fill=(246, 244, 236),
                    outline=(170, 166, 156), width=2)
    _board(d, 1180, 560, 646, 200, 270, {(r, c): ('w' if (r + c) % 3 else 'b') for r in range(8) for c in range(8)
                                         if (r * 5 + c) % 4})
    return img


def denwa():
    """1973年の自宅。鳴り続ける黒電話と、届いた箱。"""
    img = _rgb(base((222, 210, 186), (200, 186, 160)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([840, 600, 1140, 640], fill=(140, 104, 70))                 # 電話台
    d.rectangle([860, 640, 1120, 820], fill=(120, 88, 60))
    d.rounded_rectangle([900, 520, 1080, 600], radius=24, fill=(20, 20, 22))   # 黒電話
    d.rounded_rectangle([890, 490, 1090, 530], radius=20, fill=(30, 30, 34))
    d.ellipse([950, 530, 1030, 596], fill=(60, 60, 64))
    d.ellipse([975, 550, 1005, 578], fill=(200, 200, 196))
    for k in range(3):                                                      # 鳴っている線
        d.arc([820 - k * 30, 440 - k * 30, 1160 + k * 30, 660 + k * 30], 200, 250, fill=(200, 60, 50), width=6)
        d.arc([820 - k * 30, 440 - k * 30, 1160 + k * 30, 660 + k * 30], 290, 340, fill=(200, 60, 50), width=6)
    for k in range(4):
        _othello_box(d, 1320 + (k % 2) * 170, 700 - (k // 2) * 120, 160, 116)
    return img


def depart():
    """1973年のデパートのおもちゃ売り場。実演の台に盤。"""
    img = _rgb(base((240, 232, 216), (220, 210, 192)))
    wood_floor(img, FLOOR, col=(190, 170, 140), line=(170, 150, 120))
    d = _d(img)
    cols = [(220, 80, 70), (70, 130, 200), (240, 190, 70), (90, 170, 110)]
    for side, x0 in enumerate((40, 1480)):                                  # 両側の棚
        d.rectangle([x0, 150, x0 + 400, 620], fill=(200, 180, 150))
        for row in range(3):
            y = 170 + row * 150
            for k in range(3):
                if side == 1 and row == 1:
                    _othello_box(d, x0 + 20 + k * 126, y, 110, 100)
                else:
                    _toybox(d, x0 + 20 + k * 126, y, 110, 110, cols[(k + row + side) % 4])
    d.rectangle([760, 640, 1160, 690], fill=(236, 230, 214))                # 実演台
    d.rectangle([780, 690, 1140, 860], fill=(200, 60, 60))
    _board(d, 960, 556, 636, 210, 280, START | {(2, 3): 'b', (5, 4): 'w', (2, 2): 'w', (3, 2): 'b'})
    d.rectangle([1030, 600, 1150, 640], fill=(200, 190, 170))               # 台の上の見本の箱
    _othello_box(d, 1040, 560, 100, 60)
    return img


def sekai():
    """暗い地に世界地図の点。東京・ロンドン・ニューヨーク・ローマが光る。"""
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
                    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(90, 170, 120))
                    break
    for cx, cy in ((1590, 420), (910, 290), (440, 330), (990, 370)):
        _glow(img, cx, cy, 60, (255, 255, 255), 170)
    return img


def yuugure():
    """夕暮れの水戸。湖と町の影。"""
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
    for k in range(8):
        y = 630 + k * 34
        half = 110 - k * 10
        d.line([(1390 - half, y), (1390 + half, y)], fill=(240, 186, 130), width=5)
    return img


def shiryo():
    """古い資料。19世紀の遊び方の紙と、紅白の石の盤（源平碁）。"""
    img = _rgb(base((226, 216, 196), (204, 192, 170)))
    d = _d(img)
    d.rectangle([560, 120, 1360, 420], fill=(240, 228, 200), outline=(170, 150, 120), width=6)   # 古い紙
    for y in range(160, 400, 34):
        d.rectangle([600, y, 600 + (680 if (y // 34) % 4 else 420), y + 12], fill=(170, 150, 120))
    st = {(3, 3): 'w', (4, 4): 'w', (3, 4): 'b', (4, 3): 'b', (2, 2): 'b', (5, 5): 'w', (2, 5): 'b'}
    _board(d, 960, 500, 740, 440, 560, st, col=(214, 180, 120), line=(140, 110, 70),
           frame=(120, 90, 60), black=(200, 50, 50), white=(248, 244, 236))
    return img


def gendai():
    """今の売り場。箱の並ぶ棚と、盤の映ったスマホ。"""
    img = _rgb(base((244, 244, 240), (226, 226, 220)))
    wood_floor(img, FLOOR, col=(190, 180, 160), line=(170, 160, 140))
    d = _d(img)
    for row, y in enumerate((170, 400)):
        d.rectangle([600, y + 130, 1320, y + 146], fill=(160, 160, 166))
        for k in range(4):
            _othello_box(d, 620 + k * 175, y, 160, 124)
    d.rounded_rectangle([870, 640, 1050, 940], radius=24, fill=(30, 30, 34))   # スマホ
    _flat_board(d, 895, 700, 130, START | {(2, 3): 'b'}, frame=(30, 30, 34))
    return img


# ------------------------------------------------------------ 81_オセロの誕生（othello-hasegawa-v2）で足した絵
# 既存の絵はそのまま。場面の途中で差し替える絵は「元の背景を呼んで要素を足す」形で作る
# （同じ構図なので切り替わりの差が一目で分かる）。
def _wall_patch(img, box, top, bottom):
    """壁のグラデーションで矩形を塗り直す（元の絵に置いてあった物を消す）。"""
    x0, y0, x1, y1 = box
    img.paste(vgrad((W, H), top, bottom).crop((x0, y0, x1, y1)), (x0, y0))


def _flat_grid(d, x0, y0, cw, rows, cols, col=GREEN, line=GREEN_D, frame=(30, 30, 30)):
    """真正面から見た rows×cols の盤（壁に掛けた試作の盤）。"""
    w, h = cw * cols, cw * rows
    d.rectangle([x0 - 10, y0 - 10, x0 + w + 10, y0 + h + 10], fill=frame)
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=col)
    for i in range(cols + 1):
        d.line([(x0 + i * cw, y0), (x0 + i * cw, y0 + h)], fill=line, width=3)
    for i in range(rows + 1):
        d.line([(x0, y0 + i * cw), (x0 + w, y0 + i * cw)], fill=line, width=3)


def _octagon_board(img, cx, cy, size, col=(236, 230, 214), line=(90, 84, 76), frame=(150, 140, 120)):
    """角が8つある八角形の盤（大学時代に試した 88 の盤）。"""
    s = size + 20
    layer = Image.new("RGB", (s, s), frame)
    ld = ImageDraw.Draw(layer)
    c = size / 8
    ld.rectangle([10, 10, 10 + size, 10 + size], fill=col)
    for i in range(9):
        ld.line([(10 + i * c, 10), (10 + i * c, 10 + size)], fill=line, width=3)
        ld.line([(10, 10 + i * c), (10 + size, 10 + i * c)], fill=line, width=3)
    k = s * 0.29
    pts = [(k, 0), (s - k, 0), (s, k), (s, s - k), (s - k, s), (k, s), (0, s - k), (0, k)]
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    ox, oy = int(cx - s / 2), int(cy - s / 2)
    img.paste(layer, (ox, oy), mask)
    _d(img).polygon([(ox + x, oy + y) for x, y in pts], outline=frame, width=8)


def _memo(d, x, y, w=90, h=60, tilt=0):
    """走り書きのメモ用紙（字は描かず線だけ）。"""
    d.polygon([(x, y + tilt), (x + w, y), (x + w, y + h), (x, y + h + tilt)], fill=(248, 246, 236),
              outline=(170, 166, 156))
    for k in range(3):
        yy = y + 14 + k * 15
        d.line([(x + 10, yy + tilt * 0.6), (x + w - 14 - (k % 2) * 20, yy)], fill=(70, 70, 90), width=3)


def bushitsu_ban():
    """大学の部室。盤の形もルールも日替わりで、8×9・9×10・八角形の盤と、×だらけのルールの紙。"""
    img = bushitsu()
    d = _d(img)
    paper = dict(col=(236, 230, 214), line=(90, 84, 76), frame=(150, 140, 120))
    _flat_grid(d, 800, 150, 26, 8, 9, **paper)                              # 壁の中央: 8×9
    _flat_grid(d, 1275, 140, 20, 9, 10, **paper)                            # 壁の右: 9×10
    _octagon_board(img, 455, 230, 150)                                      # 壁の左: 八角形
    d = _d(img)
    for k, (x0, y0) in enumerate(((700, 950), (860, 985), (1010, 945), (1150, 990))):   # 床に散らばるルールの紙
        d.polygon([(x0, y0 + 8 * (k % 2)), (x0 + 130, y0), (x0 + 136, y0 + 70), (x0 + 6, y0 + 78)],
                  fill=(246, 242, 228), outline=(170, 160, 140))
        for j in range(3):
            d.line([(x0 + 16, y0 + 18 + j * 18), (x0 + 110 - (j % 2) * 26, y0 + 16 + j * 18)],
                   fill=(80, 70, 60), width=3)
        d.line([(x0 + 24, y0 + 64), (x0 + 112, y0 + 12)], fill=(190, 50, 50), width=5)   # 赤のバツ
        d.line([(x0 + 24, y0 + 12), (x0 + 112, y0 + 64)], fill=(190, 50, 50), width=5)
    for k in range(14):                                                     # 散らばった紙の駒
        x, y = 680 + (k * 97) % 560, 1035 + (k * 37) % 36
        d.ellipse([x, y, x + 34, y + 18], fill=BLACK if k % 2 else WHITE, outline=(80, 70, 60))
    return img


def yoru_futa():
    """1964年の夜の机。石64個ぶんで、フタ192枚。机も床も牛乳瓶とフタだらけ。"""
    img = yoru()
    d = _d(img)
    import random
    rnd = random.Random(81)
    for k in range(6):                                                      # 床の空き瓶（左）
        _bottle(d, 700 + k * 64, 960, h=100)
    for k in range(9):                                                      # 床の空き瓶（右）
        _bottle(d, 1270 + k * 70, 960, h=110)
    for _ in range(90):                                                     # 床のフタ
        _cap(d, rnd.randint(640, 1880), rnd.randint(975, 1060), r=20, black=rnd.random() < 0.3)
    for _ in range(40):                                                     # 机の手前のフタ
        _cap(d, rnd.randint(860, 1720), rnd.randint(626, 640), r=17, black=rnd.random() < 0.4)
    for i in range(4):                                                      # 積み上げたフタの塔
        for j in range(9):
            _cap(d, 1135 + i * 52, 612 - j * 7, r=21, black=(j % 3 == 2))
    return img


def denwa_yuu():
    """同じ部屋の午後4時。ベルは止み（赤い呼び出しの線を消す）、西日、時計は4時、問い合わせのメモの山。"""
    img = denwa()
    wall = ((222, 210, 186), (200, 186, 160))                               # denwa() の壁と同じグラデーション
    _wall_patch(img, (750, 370, 1230, 489), *wall)                          # 電話の上の呼び出しの線
    _wall_patch(img, (750, 489, 889, 600), *wall)                           # 電話の左
    _wall_patch(img, (1091, 489, 1230, 600), *wall)                         # 電話の右
    img = Image.blend(img, Image.new("RGB", (W, H), (255, 150, 70)), 0.22)
    _glow(img, 1650, 260, 420, (255, 190, 120), 90)
    d = _d(img)
    cx, cy, r = 1300, 210, 62                                               # 壁の時計（4時）
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 236, 226), outline=(90, 80, 70), width=6)
    d.line([(cx, cy), (cx, cy - 48)], fill=(40, 40, 40), width=5)
    a = math.radians(30)
    d.line([(cx, cy), (cx + 34 * math.cos(a), cy + 34 * math.sin(a))], fill=(40, 40, 40), width=8)
    for j in range(6):                                                      # 電話台の上のメモの山
        _memo(d, 850 + (j % 2) * 6, 586 - j * 9, w=80, h=50, tilt=(j % 3) - 1)
        _memo(d, 1046 - (j % 2) * 6, 586 - j * 9, w=80, h=50, tilt=1 - (j % 3))
    for k in range(12):                                                     # 畳に散らばるメモ
        _memo(d, 640 + (k * 113) % 640, 950 + (k * 41) % 80, tilt=(k % 5) - 2)
    return img


def mito_yake():
    """1945年8月2日の朝の水戸。os_mito と同じ構図の町並みが焼け野原になり、煙と残り火が残っている。"""
    from PIL import ImageFilter
    img = Image.new("RGB", (W, H))
    img.paste(vgrad((W, 620), (118, 108, 106), (196, 168, 138)), (0, 0))      # 煙でくすんだ空
    img.paste(vgrad((W, H - 620), (110, 98, 84), (84, 74, 62)), (0, 620))     # 焼けた地面
    d = _d(img)
    d.ellipse([-300, 420, 900, 760], fill=(92, 92, 72))                       # 焦げた丘（os_mito と同じ位置）
    d.ellipse([1000, 440, 2300, 780], fill=(88, 86, 68))
    for k in range(9):                                                        # 家の跡（os_mito の家と同じ位置）
        x0 = 60 + k * 210
        h = 130 + (k * 37) % 60
        d.polygon([(x0 - 14, 640), (x0 + 30, 598), (x0 + 82, 614), (x0 + 128, 586), (x0 + 184, 640)],
                  fill=(54, 48, 46))                                          # がれきの山
        for j, dx in enumerate((8, 78, 150)):                                 # 焼け残った柱
            top = 640 - h + (j * 37 + k * 23) % 70
            d.polygon([(x0 + dx, 640), (x0 + dx, top + 10), (x0 + dx + 7, top), (x0 + dx + 16, top + 14),
                       (x0 + dx + 16, 640)], fill=(30, 26, 26))
        d.line([(x0 + 18, 640 - h * 0.4), (x0 + 162, 632)], fill=(38, 32, 30), width=12)   # 倒れた梁
        for e in range(3):                                                    # 残り火
            ex, ey = x0 + 44 + e * 46, 626 - (e * 7) % 15
            d.ellipse([ex - 6, ey - 4, ex + 6, ey + 4], fill=(232, 120, 50))
    d.rectangle([0, 640, W, 690], fill=(122, 110, 94))                        # 道
    for x in range(40, W, 180):                                               # 焦げた電柱（傾いたものもある）
        tilt = 34 if (x // 180) % 3 == 1 else 0
        d.line([(x, 700), (x + tilt, 470)], fill=(34, 30, 28), width=8)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))                           # 立ちのぼる煙
    ld = ImageDraw.Draw(layer)
    for x in (180, 620, 1010, 1430, 1780):
        for j in range(5):
            r, cy = 50 + j * 26, 540 - j * 92
            ld.ellipse([x + j * 18 - r, cy - r * 0.7, x + j * 18 + r, cy + r * 0.7], fill=(70, 66, 64, 92 - j * 14))
    layer = layer.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def depart_kara():
    """売り場の棚から、オセロの箱だけが消えた。台の上の見本が1台だけ残っている。"""
    img = depart()
    d = _d(img)
    x0, y = 1480, 170 + 150                                                 # 右の棚の2段目（オセロの箱の段）
    for k in range(3):
        bx = x0 + 20 + k * 126
        d.rectangle([bx - 3, y - 3, bx + 113, y + 103], fill=(200, 180, 150))
    from ytf.config import Config, resolve_font
    Config.load()
    font = ImageFont.truetype(resolve_font("w9"), 40)
    label = "売り切れ"
    bb = d.textbbox((0, 0), label, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    tx, ty = 1680 - (tw + 40) // 2, 344
    d.rectangle([tx, ty, tx + tw + 40, ty + th + 26], fill=(200, 40, 40))
    d.text((tx + 20 - bb[0], ty + 13 - bb[1]), label, font=font, fill=(255, 255, 255))
    return img


def kaisha_shogi():
    """1964年の会社の事務所。机の上は将棋盤（手作りのオセロの盤はまだ無い）。"""
    img = kaisha()
    _wall_patch(img, (760, 520, 1170, 650), (218, 216, 206), (196, 194, 184))
    d = _d(img)
    d.rectangle([770, 650, 1150, 700], fill=(120, 130, 136))                # 机の天板を描き直す
    top, bot, xl0, xr0, xl1, xr1 = 566, 638, 870, 1050, 846, 1074
    d.polygon([(xl0, top), (xr0, top), (xr1, bot), (xl1, bot)], fill=(214, 176, 110))
    d.rectangle([xl1, bot, xr1, bot + 12], fill=(170, 130, 76))             # 盤の厚み
    for i in range(10):
        f = i / 9
        d.line([(xl0 + (xr0 - xl0) * f, top), (xl1 + (xr1 - xl1) * f, bot)], fill=(110, 80, 40), width=2)
        y = top + (bot - top) * f
        d.line([(xl0 + (xl1 - xl0) * f, y), (xr0 + (xr1 - xr0) * f, y)], fill=(110, 80, 40), width=2)
    for k, (fx, fy) in enumerate(((0.15, 0.15), (0.45, 0.2), (0.7, 0.3), (0.3, 0.75), (0.6, 0.8), (0.85, 0.7))):
        y = top + (bot - top) * fy
        xa = xl0 + (xl1 - xl0) * fy
        xb = xr0 + (xr1 - xr0) * fy
        x = xa + (xb - xa) * fx
        d.polygon([(x, y - 9), (x + 8, y - 4), (x + 7, y + 6), (x - 7, y + 6), (x - 8, y - 4)],
                  fill=(236, 214, 160), outline=(120, 90, 50))
    return img


def benkyou():
    """1968年の夜の机。閉じた分厚い法律の本の山と、手作りのオセロ盤。"""
    img = _rgb(base((62, 58, 70), (40, 38, 46)))
    wood_floor(img, FLOOR, col=(84, 68, 58), line=(68, 56, 48))
    _glow(img, 1500, 430, 260, (255, 210, 140), 80)
    d = _d(img)
    d.rectangle([760, 640, 1720, 690], fill=(120, 90, 66))                  # 机
    d.rectangle([790, 690, 814, 900], fill=(96, 72, 54))
    d.rectangle([1666, 690, 1690, 900], fill=(96, 72, 54))
    d.line([(1580, 640), (1580, 450)], fill=(60, 60, 64), width=8)          # 電気スタンド
    d.polygon([(1500, 450), (1660, 450), (1620, 390), (1540, 390)], fill=(60, 110, 90))
    y1 = 640
    for w, h, col in ((320, 72, (110, 40, 40)), (300, 64, (60, 50, 44)), (320, 76, (120, 56, 40)),
                      (290, 62, (40, 50, 70))):                             # 法律の本（字は描かない）
        x0 = 1130 + (320 - w) // 2
        d.rectangle([x0, y1 - h, x0 + w, y1], fill=col, outline=(30, 26, 24), width=3)
        d.line([(x0 + 14, y1 - h // 2), (x0 + w - 14, y1 - h // 2)], fill=(200, 170, 90), width=3)
        y1 -= h
    _board(d, 930, 566, 632, 150, 190, START | {(2, 3): 'b', (5, 4): 'w'},
           col=(236, 230, 214), line=(90, 84, 76), frame=(150, 140, 120))   # 手作りの盤
    for k in range(4):
        _cap(d, 1030 + k * 26, 628, r=13, black=k % 2 == 0)
    return img


def densha():
    """1972年の中央線の車内。ロングシートと吊り革、窓の外は夕方の街。"""
    img = _rgb(base((206, 220, 204), (186, 200, 184)))
    d = _d(img)
    d.rectangle([0, 0, W, 110], fill=(232, 236, 228))                       # 天井
    for x in (360, 960, 1560):                                              # 扇風機
        d.ellipse([x - 60, 20, x + 60, 90], fill=(210, 214, 206), outline=(150, 156, 150), width=4)
    for x0 in (60, 540, 1020, 1500):                                        # 窓と夕方の街
        x1 = x0 + 380
        img.paste(vgrad((x1 - x0, 300), (236, 160, 104), (250, 214, 160)), (x0, 210))
        d = _d(img)
        for k in range(7):
            bx = x0 + 10 + k * 54
            bh = 60 + (k * 37 + x0) % 110
            d.rectangle([bx, 510 - bh, bx + 44, 510], fill=(120, 96, 110))
        d.rectangle([x0, 210, x1, 510], outline=(150, 160, 150), width=12)
    d.line([(0, 140), (W, 140)], fill=(160, 160, 160), width=8)             # 吊り革
    for x in range(70, W, 120):
        d.line([(x, 140), (x, 196)], fill=(220, 220, 220), width=6)
        d.ellipse([x - 18, 194, x + 18, 230], outline=(244, 244, 244), width=6)
    d.rectangle([0, 600, W, 660], fill=(70, 92, 130))                       # ロングシート
    d.rectangle([0, 660, W, 740], fill=(56, 76, 112))
    d.rectangle([0, 740, W, 790], fill=(120, 124, 120))
    d.rectangle([0, 790, W, H], fill=(150, 140, 122))                       # 床
    for x in range(0, W, 160):
        d.line([(x, 790), (x - 80, H)], fill=(136, 126, 110), width=4)
    return img


def shosai():
    """晩年の書斎。本棚と窓、机の上に原稿用紙・万年筆・オセロ盤。"""
    img = _rgb(base((222, 212, 194), (198, 186, 166)))
    wood_floor(img, FLOOR, col=(140, 108, 80), line=(118, 90, 66))
    d = _d(img)
    for x0 in (40, 1500):                                                   # 本棚
        d.rectangle([x0, 100, x0 + 380, 880], fill=(120, 88, 60))
        for row in range(5):
            y = 120 + row * 150
            d.rectangle([x0 + 14, y + 128, x0 + 366, y + 140], fill=(90, 66, 46))
            for k in range(17):
                bx = x0 + 18 + k * 20
                h = 96 + (k * 17 + row * 7) % 30
                colr = ((130, 50, 46), (46, 66, 110), (60, 96, 70), (170, 140, 90), (96, 70, 56))[(k + row) % 5]
                d.rectangle([bx, y + 128 - h, bx + 16, y + 128], fill=colr)
    _window(d, 780, 130, 1140, 420, sky=(170, 200, 224), frame=(110, 84, 60))
    d.rectangle([700, 640, 1220, 690], fill=(110, 76, 50))                  # 机
    d.rectangle([720, 690, 744, 900], fill=(90, 62, 40))
    d.rectangle([1176, 690, 1200, 900], fill=(90, 62, 40))
    d.polygon([(905, 598), (1075, 598), (1092, 636), (888, 636)], fill=(248, 246, 238))   # 原稿用紙
    for k in range(1, 10):
        f = k / 10
        d.line([(905 + 170 * f, 598), (888 + 204 * f, 636)], fill=(210, 120, 110), width=2)
    for k in range(1, 4):
        y = 598 + 38 * k / 4
        d.line([(905 - 17 * k / 4, y), (1075 + 17 * k / 4, y)], fill=(210, 120, 110), width=2)
    d.line([(1046, 592), (1104, 566)], fill=(30, 30, 34), width=7)          # 万年筆
    d.line([(1180, 640), (1180, 470)], fill=(60, 60, 64), width=8)          # 電気スタンド
    d.polygon([(1110, 470), (1250, 470), (1215, 412), (1145, 412)], fill=(60, 110, 90))
    _board(d, 800, 592, 636, 110, 140, START | {(2, 3): 'b', (5, 4): 'w', (2, 4): 'w'})   # オセロ盤
    for k, col in enumerate(((60, 50, 44), (110, 40, 40), (46, 66, 110))):  # 積んだ本
        d.rectangle([1110, 624 - k * 16, 1170, 640 - k * 16], fill=col, outline=(30, 26, 24))
    return img


def shosai_kara():
    """主のいない書斎の夜。スタンドの灯りの下に書きかけの原稿と万年筆、引かれたままの椅子。"""
    from PIL import ImageEnhance
    img = shosai()
    d = _d(img)
    _window(d, 780, 130, 1140, 420, sky=(28, 36, 64), frame=(110, 84, 60))
    img = ImageEnhance.Brightness(img).enhance(0.6)
    _glow(img, 1180, 520, 300, (255, 214, 150), 120)
    d = _d(img)
    cx = 1000                                                               # 机から引かれたままの椅子（後ろから見た形）
    for x in (cx - 70, cx + 62):
        d.rectangle([x, 820, x + 10, 960], fill=(64, 44, 30))               # 脚
    d.rectangle([cx - 80, 800, cx + 80, 826], fill=(92, 64, 42))            # 座面
    d.rectangle([cx - 74, 690, cx - 60, 806], fill=(80, 54, 36))            # 背もたれの柱
    d.rectangle([cx + 60, 690, cx + 74, 806], fill=(80, 54, 36))
    d.rectangle([cx - 74, 690, cx + 74, 730], fill=(96, 66, 44))            # 背もたれの板
    d.rectangle([cx - 60, 752, cx + 60, 766], fill=(96, 66, 44))
    return img


LOCATIONS = {
    "os_ima": ima, "os_ima2": ima2, "os_senshu": senshu, "os_mito": mito, "os_aozora": aozora, "os_kyoushitsu": kyoushitsu,
    "os_byouin": byouin, "os_bushitsu": bushitsu, "os_yoru": yoru, "os_kaisha": kaisha,
    "os_byouin2": byouin2, "os_goraku": goraku, "os_jikka": jikka, "os_butai": butai,
    "os_tsukuda": tsukuda, "os_hako": hako, "os_zukai": zukai, "os_computer": computer,
    "os_hotel": hotel, "os_kiji": kiji, "os_denwa": denwa, "os_depart": depart,
    "os_sekai": sekai, "os_yuugure": yuugure, "os_shiryo": shiryo, "os_gendai": gendai,
    # 81_オセロの誕生（othello-hasegawa-v2）
    "os_bushitsu_ban": bushitsu_ban, "os_yoru_futa": yoru_futa, "os_denwa_yuu": denwa_yuu,
    "os_depart_kara": depart_kara, "os_kaisha_shogi": kaisha_shogi, "os_benkyou": benkyou,
    "os_densha": densha, "os_shosai": shosai, "os_shosai_kara": shosai_kara,
    "os_mito_yake": mito_yake,
}

CARDS = ["1945", "1964", "1968", "1972", "1973", "1977",
         "1932", "2006", "2016"]                                            # 下の3枚は 81 で追加


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
        if only and f"os_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"os_card_{y}.png")
        print(f"生成完了: os_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
