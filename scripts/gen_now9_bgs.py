#!/usr/bin/env python3
"""第9弾4本（2026-11-29〜12-02。方向転換の実験の13〜16本目：会社の転落・破綻・裁判）の背景を生成する。

接頭辞: gs_（ゴーン事件）/ ez_（リクルート事件）/ tm_（てるみくらぶの破綻）/ og_（コムスンの処分）
方針は gen_now8_bgs.py と同じ。実在の会社のロゴ・社名の文字・店の意匠・商品のパッケージは描かない。
実在の人の写真や肖像は描かない（壁の写真は人の形だけ）。差し替え用は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now9_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import year_card  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _car, _d, _rgb, kaigi, kojo_line, yakuin  # noqa: E402
from scripts.gen_now2_bgs import heya2, kabunushi_kaijo, shoken  # noqa: E402
from scripts.gen_now3_bgs import _plane_side, heya3, jimusho90, kuko_lobby  # noqa: E402
from scripts.gen_now5_bgs import cg_saikosai  # noqa: E402
from scripts.gen_now7_bgs import ik_ny, ik_studio  # noqa: E402
from scripts.gen_now8_bgs import dz_jigyobu, ld_hei, ld_kanmae, ld_tower, mx_genkan, tj_osetsu, tj_shinbun  # noqa: E402
from scripts.gen_sega_bgs import _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import kokkai as _sogo_kokkai, saibansho as _sogo_saibansho  # noqa: E402


def _light(img, polys, col, alpha=70, blur=0):
    """半透明の光（スポットライトの筋など）を重ねる。"""
    base_img = img.convert("RGBA")
    layer = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for p in polys:
        ld.polygon(p, fill=(*col, alpha))
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base_img, layer).convert("RGB")


def _press(d, x0, y, n, s=1.0):
    """報道陣（人の形とカメラ）。"""
    _person_line(d, x0, y, n, s)
    for k in range(0, n, 2):
        x = x0 + k * 70 * s
        d.rectangle([x - 4 * s, y - 176 * s, x + 46 * s, y - 140 * s], fill=(30, 30, 34))
        d.ellipse([x + 30 * s, y - 170 * s, x + 54 * s, y - 146 * s], fill=(80, 90, 110))


# ---------------------------------------------------------------- ゴーン事件
def gs_heya():
    """今の部屋。机に開いたままの宿題のノートと鉛筆、床に大きな段ボール箱（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([200, 596, 420, 640], fill=(250, 250, 240), outline=(120, 120, 120), width=3)
    d.line([(310, 596), (310, 640)], fill=(120, 120, 120), width=2)
    for k in range(3):
        d.line([(212, 606 + k * 10), (300, 606 + k * 10)], fill=(150, 150, 200), width=2)
    d.line([(440, 630), (560, 610)], fill=(230, 190, 60), width=8)
    d.polygon([(1180, 920), (1180, 700), (1560, 700), (1560, 920)], fill=(200, 160, 110), outline=(140, 110, 70))
    d.polygon([(1180, 700), (1240, 640), (1620, 640), (1560, 700)], fill=(214, 176, 126), outline=(140, 110, 70))
    d.polygon([(1560, 700), (1620, 640), (1620, 860), (1560, 920)], fill=(176, 140, 96), outline=(140, 110, 70))
    d.line([(1370, 700), (1430, 640)], fill=(150, 120, 80), width=4)
    return img


def gs_nimai():
    """秘書室の机の上に、2枚の紙。左は印刷の報告書（数字の帯）、右は手書きのメモ（線）。文字は描かない。"""
    img = vgrad((W, H), (150, 120, 90), (120, 92, 66))
    d = _d(img)
    d.polygon([(260, 180), (900, 160), (930, 920), (240, 940)], fill=(250, 250, 246), outline=(180, 170, 150))
    d.rectangle([320, 230, 760, 270], fill=(60, 60, 64))
    for k in range(9):
        y = 330 + k * 60
        d.line([(320, y), (600, y)], fill=(150, 150, 150), width=5)
        d.rectangle([660, y - 12, 840, y + 12], fill=(40, 40, 44))
    d.polygon([(1040, 220), (1640, 250), (1610, 900), (1010, 870)], fill=(252, 248, 220), outline=(190, 180, 140))
    rnd = random.Random(6)
    for k in range(9):
        y = 300 + k * 64
        pts = [(1080 + j * 60, y + rnd.randint(-6, 6)) for j in range(8)]
        d.line(pts, fill=(40, 60, 140), width=4)
    d.rectangle([1340, 760, 1560, 820], outline=(200, 40, 40), width=6)
    return img


def gs_door(n=1):
    """役員の部屋のドアの横の名札。n=1 は1枚、n=3 は色違いの3枚が縦に並ぶ（文字は線）。"""
    img = _rgb(base((214, 212, 206), (200, 198, 192)))
    wood_floor(img, FLOOR, col=(130, 100, 76), line=(110, 84, 62))
    d = _d(img)
    d.rectangle([700, 140, 1180, FLOOR], fill=(140, 104, 72), outline=(100, 74, 50), width=10)
    d.ellipse([1100, 560, 1140, 600], fill=(210, 190, 120))
    cols = [(60, 70, 90), (180, 150, 60), (150, 40, 40)]
    for k in range(n):
        y = 300 + k * 110
        d.rectangle([1240, y, 1560, y + 80], fill=cols[k], outline=(90, 90, 90), width=3)
        d.line([(1270, y + 40), (1530, y + 40)], fill=(240, 240, 236), width=8)
    return img


def gs_karenda():
    """灰色の壁に、日付の升目のカレンダー（12月）。いくつかの升に赤と青の札が貼られている（数字は描かない）。"""
    img = _rgb(base((176, 178, 176), (160, 162, 160)))
    d = _d(img)
    d.rectangle([0, FLOOR, W, H], fill=(130, 132, 130))
    d.rectangle([560, 120, 1360, 860], fill=(250, 250, 246), outline=(120, 120, 120), width=6)
    d.rectangle([560, 120, 1360, 220], fill=(200, 60, 50))
    for r in range(6):
        d.line([(560, 220 + r * 107), (1360, 220 + r * 107)], fill=(170, 170, 170), width=3)
    for c in range(1, 7):
        d.line([(560 + c * 114, 220), (560 + c * 114, 860)], fill=(170, 170, 170), width=3)
    for (r, c, col) in ((1, 1, (220, 60, 50)), (1, 2, (60, 110, 200)), (2, 4, (220, 60, 50)), (3, 3, (60, 110, 200)), (3, 4, (220, 60, 50))):
        x, y = 560 + c * 114 + 14, 220 + r * 107 + 30
        d.rectangle([x, y, x + 86, y + 50], fill=col)
    d.rectangle([1500, 160, 1620, 280], fill=(110, 116, 126), outline=(80, 80, 86), width=6)
    for k in range(3):
        d.line([(1520 + k * 40, 160), (1520 + k * 40, 280)], fill=(60, 60, 66), width=6)
    return img


def gs_menkai():
    """拘置所の面会室。中央に穴のあいた透明な仕切り、両側に机といす。"""
    img = _rgb(base((200, 204, 200), (186, 190, 186)))
    wood_floor(img, FLOOR, col=(150, 152, 150), line=(136, 138, 136))
    d = _d(img)
    img = _light(img, [[(860, 120), (1060, 120), (1060, 900), (860, 900)]], (210, 230, 240), alpha=90)
    d = _d(img)
    d.rectangle([856, 120, 1064, 900], outline=(120, 124, 130), width=8)
    for r in range(3):
        for c in range(3):
            d.ellipse([920 + c * 30, 460 + r * 30, 934 + c * 30, 474 + r * 30], fill=(150, 156, 166))
    d.rectangle([200, 640, 856, 700], fill=(170, 160, 140))
    d.rectangle([1064, 640, 1720, 700], fill=(170, 160, 140))
    for x in (460, 1400):
        d.rectangle([x, 720, x + 120, 760], fill=(90, 96, 110))
        d.rectangle([x + 10, 600, x + 110, 720], fill=(110, 116, 130))
    return img


def gs_kei(hodo=True):
    """夕方の拘置所の門の前を走り出す、屋根に脚立を積んだ白い小さな作業の車（後ろ姿）。hodo は周りに報道陣とカメラ。"""
    img = gs_kosoku(hodo=False)
    d = _d(img)
    x0, y0 = 780, 760
    d.rounded_rectangle([x0, y0, x0 + 360, y0 + 220], radius=20, fill=(244, 244, 246), outline=(150, 150, 156), width=4)
    d.rectangle([x0 + 30, y0 + 30, x0 + 330, y0 + 110], fill=(140, 170, 196))
    d.rectangle([x0 + 20, y0 + 150, x0 + 70, y0 + 176], fill=(220, 60, 50))
    d.rectangle([x0 + 290, y0 + 150, x0 + 340, y0 + 176], fill=(220, 60, 50))
    for wx in (x0 + 40, x0 + 280):
        d.rectangle([wx, y0 + 210, wx + 50, y0 + 250], fill=(24, 24, 26))
    d.rectangle([x0 - 20, y0 - 40, x0 + 380, y0 - 20], fill=(200, 200, 206))
    for k in range(9):
        d.line([(x0 - 10 + k * 46, y0 - 40), (x0 - 10 + k * 46, y0 - 20)], fill=(150, 150, 156), width=4)
    if hodo:
        _press(d, 60, 1060, 9, 1.1)
        _press(d, 1250, 1060, 9, 1.1)
    return img


def gs_doga():
    """パソコンの画面いっぱいに映る動画の画（机といす、無地の壁。人はいない）。"""
    img = vgrad((W, H), (30, 30, 34), (44, 44, 50))
    d = _d(img)
    d.rectangle([180, 80, 1740, 900], fill=(20, 20, 24), outline=(90, 90, 96), width=14)
    d.rectangle([200, 100, 1720, 880], fill=(206, 200, 190))
    d.rectangle([200, 700, 1720, 880], fill=(150, 120, 90))
    d.rectangle([760, 300, 1160, 520], fill=(120, 100, 80))
    d.rectangle([200, 820, 1720, 880], fill=(0, 0, 0))
    d.rectangle([230, 840, 800, 852], fill=(220, 50, 50))
    d.polygon([(860, 940), (1060, 940), (1100, 1000), (820, 1000)], fill=(70, 70, 76))
    return img


def gs_houtei_kara():
    """法廷。手前の被告人の長いすが空いていて、そこにだけ光が当たる。"""
    img = _sogo_saibansho()
    d = _d(img)
    d.rectangle([1260, 640, 1700, 700], fill=(100, 72, 50), outline=(80, 56, 40), width=4)
    d.rectangle([1260, 700, 1290, 760], fill=(90, 64, 44))
    d.rectangle([1670, 700, 1700, 760], fill=(90, 64, 44))
    img = _light(img, [[(1400, 0), (1560, 0), (1760, 760), (1200, 760)]], (255, 250, 220), alpha=70, blur=10)
    return img


def gs_mado():
    """海の見える部屋の大きな窓（部屋の中は描かない。窓枠と青い海と空だけ）。"""
    img = _rgb(base((226, 220, 210), (214, 208, 198)))
    d = _d(img)
    d.rectangle([260, 100, 1660, 800], fill=(150, 200, 236), outline=(240, 240, 236), width=20)
    d.rectangle([280, 480, 1640, 780], fill=(40, 110, 170))
    for k in range(6):
        d.line([(300, 520 + k * 44), (1620, 520 + k * 44)], fill=(80, 150, 200), width=4)
    d.line([(960, 100), (960, 800)], fill=(240, 240, 236), width=14)
    d.rectangle([0, 800, W, H], fill=(190, 180, 166))
    return img


def gs_haneda(kuruma=False):
    """夕方の空港の駐機場。小型のジェット機とタラップ。kuruma は機体の横に黒い車が2台と人の形。"""
    img = vgrad((W, H), (246, 160, 110), (250, 214, 180))
    d = _d(img)
    d.rectangle([0, 500, W, 600], fill=(116, 106, 118))
    for k in range(12):
        d.rectangle([40 + k * 160, 524, 120 + k * 160, 556], fill=(244, 214, 150))
    d.rectangle([0, 600, W, H], fill=(92, 94, 102))
    for k in range(5):
        d.line([(160 + k * 420, H), (520 + k * 300, 600)], fill=(226, 196, 60), width=6)
    _plane_side(d, 1560, 780, 0.72, body=(240, 240, 246))
    d.polygon([(1150, 770), (1206, 770), (1086, 920), (1030, 920)], fill=(206, 206, 212), outline=(120, 120, 126))
    if kuruma:
        _car(d, 600, 930, 1.3, col=(24, 24, 28))
        _car(d, 240, 960, 1.3, col=(30, 30, 34))
        _person_line(d, 980, 940, 4, 1.0, cols=[(40, 40, 46), (50, 50, 58)])
    return img


def gs_kanku(hako=False):
    """夜の空港の駐機場。照明のついた格納庫の口と、小型のジェット機とタラップ。
    hako は機体の手前に大きな黒い箱が2つ（台車の上）。"""
    img = vgrad((W, H), (10, 14, 30), (30, 34, 60))
    d = _d(img)
    d.rectangle([0, 620, W, H], fill=(40, 42, 50))
    d.rectangle([60, 260, 780, 620], fill=(66, 70, 82), outline=(110, 114, 126), width=4)
    d.rectangle([130, 360, 710, 620], fill=(226, 214, 176))
    img = _light(img, [[(130, 620), (710, 620), (900, H), (-60, H)]], (255, 236, 180), alpha=60, blur=20)
    d = _d(img)
    _plane_side(d, 1640, 800, 0.7, body=(236, 236, 242))
    d.polygon([(1250, 790), (1300, 790), (1190, 930), (1140, 930)], fill=(196, 196, 202), outline=(110, 110, 116))
    for x in (980, 1900):
        d.line([(x, 620), (x, 320)], fill=(90, 90, 96), width=10)
        d.ellipse([x - 30, 300, x + 30, 340], fill=(255, 236, 190))
    if hako:
        d.rectangle([860, 900, 1260, 930], fill=(120, 120, 126))
        for wx in (890, 1230):
            d.ellipse([wx - 18, 920, wx + 18, 956], fill=(20, 20, 22))
        for x0 in (880, 1070):
            d.rounded_rectangle([x0, 700, x0 + 170, 900], radius=8, fill=(22, 22, 26), outline=(96, 96, 104), width=4)
            for cx, cy in ((x0 + 10, 710), (x0 + 150, 710), (x0 + 10, 880), (x0 + 150, 880)):
                d.rectangle([cx, cy, cx + 12, cy + 12], fill=(170, 170, 176))
            d.rectangle([x0 + 60, 780, x0 + 110, 800], fill=(150, 150, 156))
    return img


def gs_hako():
    """大きな黒い箱（音響の機材を入れるようなハードケース）のアップ。金具と車輪、底の近くに小さな穴が並ぶ。"""
    img = _rgb(base((206, 204, 200), (190, 188, 184)))
    d = _d(img)
    d.rectangle([0, FLOOR - 80, W, H], fill=(150, 146, 140))
    x0, y0, x1, y1 = 640, 230, 1280, 900
    d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=(26, 26, 30), outline=(110, 110, 116), width=8)
    for cx, cy in ((x0, y0), (x1 - 60, y0), (x0, y1 - 60), (x1 - 60, y1 - 60)):
        d.rectangle([cx, cy, cx + 60, cy + 60], fill=(176, 176, 182), outline=(110, 110, 116), width=3)
    d.line([(x0, 420), (x1, 420)], fill=(90, 90, 96), width=6)
    for k in range(3):
        d.rectangle([x0 + 150 + k * 140, 400, x0 + 210 + k * 140, 440], fill=(170, 170, 176))
    d.rounded_rectangle([900, 330, 1020, 370], radius=12, fill=(120, 120, 126))
    for k in range(10):
        d.ellipse([x0 + 80 + k * 52, y1 - 110, x0 + 96 + k * 52, y1 - 94], fill=(70, 70, 76))
    for wx in (x0 + 80, x1 - 80):
        d.ellipse([wx - 34, y1 - 10, wx + 34, y1 + 50], fill=(16, 16, 18))
    return img


def gs_kosoku(hodo=False):
    """拘置所の外。高い灰色の建物と塀、門。hodo は門の前に報道陣とカメラ。"""
    img = vgrad((W, H), (176, 186, 198), (214, 218, 222))
    d = _d(img)
    d.rectangle([520, 120, 1400, 620], fill=(150, 152, 156), outline=(110, 112, 116), width=4)
    for r in range(8):
        for c in range(14):
            d.rectangle([560 + c * 60, 150 + r * 56, 590 + c * 60, 186 + r * 56], fill=(110, 116, 126))
    for x0, x1 in ((260, 520), (1400, 1660)):
        d.rectangle([x0, 330, x1, 620], fill=(160, 162, 166), outline=(116, 118, 122), width=3)
    d.rectangle([0, 520, W, 660], fill=(186, 184, 178), outline=(140, 138, 132), width=4)
    d.rectangle([820, 540, 1100, 660], fill=(70, 74, 80))
    for k in range(9):
        d.line([(836 + k * 30, 548), (836 + k * 30, 656)], fill=(150, 150, 156), width=4)
    d.rectangle([0, 660, W, H], fill=(170, 168, 162))
    for k in range(6):
        d.ellipse([40 + k * 330, 420, 220 + k * 330, 560], fill=(80, 120, 80))
    if hodo:
        _press(d, 120, 1000, 9, 1.1)
        _press(d, 1180, 1000, 9, 1.1)
    return img


def gs_beirut():
    """外国の会見場。木の壁と大きなシャンデリア、中央に演台とマイク、手前に記者の頭とカメラが並ぶ。旗は描かない。"""
    img = _rgb(base((150, 112, 80), (130, 96, 68)))
    d = _d(img)
    for k in range(9):
        d.line([(k * 240, 0), (k * 240, 760)], fill=(110, 80, 54), width=8)
    d.rectangle([0, 760, W, H], fill=(70, 50, 40))
    for x in (520, 1400):
        d.line([(x, 0), (x, 70)], fill=(200, 170, 90), width=4)
        d.ellipse([x - 120, 70, x + 120, 150], fill=(250, 224, 150), outline=(200, 170, 90), width=4)
        for j in range(7):
            d.ellipse([x - 110 + j * 34, 150, x - 96 + j * 34, 176], fill=(255, 244, 210))
    d.rectangle([600, 300, 1320, 640], fill=(120, 30, 36), outline=(90, 20, 26), width=6)
    d.polygon([(840, 560), (1080, 560), (1050, 820), (870, 820)], fill=(90, 66, 50), outline=(60, 44, 34))
    for k in range(4):
        d.line([(900 + k * 40, 560), (930 + k * 30, 500)], fill=(30, 30, 30), width=5)
        d.ellipse([922 + k * 30, 488, 940 + k * 30, 506], fill=(40, 40, 44))
    _press(d, 20, 1080, 27, 1.0)
    return img


# ---------------------------------------------------------------- コムスンの処分
def og_heya():
    """今の部屋。机にスマホと、白い封筒（お知らせ）。"""
    img = heya2("none")
    d = _d(img)
    d.rounded_rectangle([230, 560, 300, 640], radius=10, fill=(30, 30, 34))
    d.rectangle([238, 570, 292, 630], fill=(110, 170, 230))
    d.rectangle([360, 596, 540, 640], fill=(248, 248, 244), outline=(170, 170, 170), width=3)
    d.line([(360, 596), (450, 622), (540, 596)], fill=(170, 170, 170), width=3)
    return img


def og_disco(kara=False):
    """1990年代のディスコのフロア。天井のミラーボールと色の光の筋、右に高いお立ち台、踊る人の形と扇子。
    kara は照明が消え、人もいない（閉店のあと）。店名・ロゴは描かない。"""
    img = vgrad((W, H), (14, 8, 30), (34, 12, 54)) if not kara else vgrad((W, H), (18, 18, 22), (30, 30, 34))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(30, 20, 40) if not kara else (34, 34, 38))
    for k in range(1, 12):
        d.line([(k * 180 - 200, H), (k * 160 + 80, 700)], fill=(60, 40, 80) if not kara else (50, 50, 54), width=3)
    for k in range(4):
        d.line([(0, 720 + k * 90), (W, 720 + k * 90)], fill=(60, 40, 80) if not kara else (50, 50, 54), width=3)
    d.line([(960, 0), (960, 60)], fill=(120, 120, 130), width=4)
    d.ellipse([890, 60, 1030, 200], fill=(200, 200, 214) if not kara else (90, 90, 96))
    for k in range(5):
        d.line([(890, 74 + k * 26), (1030, 74 + k * 26)], fill=(150, 150, 170) if not kara else (70, 70, 76), width=2)
        d.line([(904 + k * 28, 60), (904 + k * 28, 200)], fill=(150, 150, 170) if not kara else (70, 70, 76), width=2)
    d.rectangle([1120, 540, 1820, 700], fill=(70, 50, 90) if not kara else (54, 54, 58), outline=(200, 180, 230) if not kara else (80, 80, 84), width=6)
    if not kara:
        img = _light(img, [[(960, 130), (1000, 130), (520, H), (300, H)],
                           [(960, 130), (1000, 130), (1500, 700), (1300, 700)],
                           [(960, 130), (1000, 130), (980, H), (760, H)]], (255, 70, 170), alpha=60, blur=6)
        img = _light(img, [[(960, 130), (1000, 130), (1900, 560), (1820, 700)],
                           [(960, 130), (1000, 130), (120, 700), (0, 820)]], (80, 180, 255), alpha=60, blur=6)
        d = _d(img)
        rnd = random.Random(7)
        for k in range(6):
            x = 1170 + k * 108
            d.ellipse([x, 380, x + 40, 420], fill=(30, 20, 34))
            d.rounded_rectangle([x - 6, 420, x + 46, 540], radius=14, fill=(20, 14, 26))
            fx, fy = x + 40, 340 - rnd.randint(0, 30)
            d.pieslice([fx - 40, fy - 10, fx + 40, fy + 60], 200, 340, fill=(250, 250, 250), outline=(200, 200, 210))
        for k in range(10):
            x = 120 + k * 92
            d.ellipse([x, 760, x + 40, 800], fill=(20, 14, 26))
            d.rounded_rectangle([x - 6, 800, x + 46, 930], radius=14, fill=(16, 10, 22))
    return img


def og_kaigo():
    """訪問介護の家の部屋。畳と障子の窓、手すりの付いた介護ベッド、たたんだ車いす、小さなたんす。"""
    img = _rgb(base((230, 222, 204), (216, 208, 190)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([700, 120, 1180, 460], fill=(246, 242, 226), outline=(150, 120, 80), width=10)
    for k in range(1, 4):
        d.line([(700 + k * 120, 120), (700 + k * 120, 460)], fill=(170, 140, 100), width=4)
    for k in range(1, 4):
        d.line([(700, 120 + k * 85), (1180, 120 + k * 85)], fill=(170, 140, 100), width=4)
    d.rectangle([1260, 560, 1840, 700], fill=(236, 236, 240), outline=(150, 150, 156), width=4)
    d.rectangle([1260, 500, 1840, 560], fill=(250, 250, 252), outline=(170, 170, 176), width=3)
    for x in (1260, 1840):
        d.rectangle([x - 14, 440, x + 14, 820], fill=(160, 160, 166))
    d.line([(1300, 500), (1500, 500)], fill=(120, 120, 126), width=10)
    d.rectangle([1250, 700, 1850, 740], fill=(140, 140, 146))
    for x in (1290, 1810):
        d.ellipse([x - 22, 800, x + 22, 844], fill=(60, 60, 64))
    d.ellipse([200, 640, 420, 860], outline=(80, 80, 86), width=12)
    d.line([(240, 560), (300, 760), (400, 760)], fill=(80, 80, 86), width=12)
    d.rectangle([260, 680, 380, 720], fill=(60, 90, 150))
    d.rectangle([440, 470, 620, 760], fill=(170, 130, 90), outline=(120, 90, 60), width=4)
    for k in range(3):
        d.line([(440, 560 + k * 70), (620, 560 + k * 70)], fill=(120, 90, 60), width=3)
    return img


def og_jigyosho(sukunai=False):
    """訪問介護の事業所。机とパソコン、壁のホワイトボードに勤務表（升目に色のマグネット）。
    sukunai はマグネットがまばらで、机も空いている（人が足りない）。"""
    img = jimusho90()
    d = _d(img)
    d.rectangle([1180, 120, 1860, 520], fill=(250, 250, 252), outline=(150, 150, 156), width=6)
    for r in range(7):
        d.line([(1180, 170 + r * 50), (1860, 170 + r * 50)], fill=(180, 180, 186), width=2)
    for c in range(8):
        d.line([(1260 + c * 75, 120), (1260 + c * 75, 520)], fill=(180, 180, 186), width=2)
    rnd = random.Random(5)
    cols = [(230, 80, 70), (60, 140, 220), (250, 200, 60), (90, 180, 100)]
    for r in range(7):
        for c in range(8):
            if sukunai and rnd.random() < 0.7:
                continue
            if not sukunai and rnd.random() < 0.15:
                continue
            x, y = 1278 + c * 75, 182 + r * 50
            d.ellipse([x, y, x + 26, y + 26], fill=cols[(r + c) % 4])
    return img


def og_soko():
    """夜の湾岸の倉庫街。並んだ倉庫の大きな扉、街灯、奥に運河と対岸の灯り。"""
    img = vgrad((W, H), (16, 20, 40), (40, 44, 70))
    d = _d(img)
    for k in range(10):
        d.ellipse([k * 200, 300, k * 200 + 6, 306], fill=(250, 230, 170))
    d.rectangle([0, 320, W, 400], fill=(30, 40, 70))
    for k in range(4):
        x0 = k * 500 - 40
        d.polygon([(x0, 760), (x0, 420), (x0 + 230, 360), (x0 + 460, 420), (x0 + 460, 760)], fill=(86, 88, 96), outline=(60, 62, 70))
        d.rectangle([x0 + 130, 520, x0 + 330, 760], fill=(66, 68, 76))
        for j in range(8):
            d.line([(x0 + 130, 530 + j * 28), (x0 + 330, 530 + j * 28)], fill=(80, 82, 90), width=3)
    d.rectangle([0, 760, W, H], fill=(56, 56, 60))
    for x in (440, 1440):
        d.line([(x, 760), (x, 470)], fill=(80, 80, 86), width=10)
        d.ellipse([x - 24, 450, x + 24, 490], fill=(255, 226, 160))
    return img


def og_care(oshirase=False):
    """開いたばかりの小さな介護の事業所（ケアセンター）。受付の机、電話、観葉植物、壁の地図と予定の白板。
    oshirase は同じ部屋の壁と扉に白い「お知らせ」の紙（文字は線）、机の上に段ボール。看板の文字は描かない。"""
    img = _rgb(base((236, 236, 228), (222, 222, 214)))
    wood_floor(img, FLOOR, col=(196, 180, 150), line=(176, 160, 130))
    d = _d(img)
    d.rectangle([140, 160, 620, 420], fill=(250, 250, 248), outline=(150, 150, 156), width=6)
    for k in range(4):
        d.line([(180, 200 + k * 50), (480, 200 + k * 50)], fill=(80, 140, 200), width=5)
    d.rectangle([760, 140, 1160, 420], fill=(210, 230, 210), outline=(140, 140, 146), width=6)
    d.polygon([(840, 200), (1000, 180), (1100, 300), (980, 380), (820, 330)], fill=(160, 200, 160))
    d.rectangle([600, 600, 1500, 660], fill=(214, 196, 166), outline=(160, 140, 110), width=4)
    d.rectangle([640, 660, 1460, 820], fill=(200, 182, 150))
    d.rounded_rectangle([1300, 560, 1400, 600], radius=8, fill=(240, 240, 236), outline=(120, 120, 120), width=3)
    d.rectangle([1640, 600, 1720, 760], fill=(170, 120, 80))
    for k in range(5):
        d.ellipse([1600 + k * 20, 470 - (k % 2) * 30, 1680 + k * 20, 600], fill=(70, 150, 80))
    if oshirase:
        for x0, y0 in ((200, 450), (1220, 180), (1500, 300)):
            d.rectangle([x0, y0, x0 + 200, y0 + 260], fill=(252, 252, 250), outline=(160, 160, 160), width=3)
            for j in range(6):
                d.line([(x0 + 24, y0 + 40 + j * 34), (x0 + 176, y0 + 40 + j * 34)], fill=(60, 60, 60), width=5)
        for k in range(3):
            d.rectangle([700 + k * 190, 470 + (k % 2) * 30, 860 + k * 190, 600], fill=(196, 160, 110), outline=(140, 110, 70), width=3)
    return img


def og_kencho():
    """県庁の監査の部屋。長机に申請書の束とファイル、壁に書類の棚、窓。"""
    img = _rgb(base((222, 224, 222), (208, 210, 208)))
    wood_floor(img, FLOOR, col=(150, 150, 146), line=(132, 132, 128))
    d = _d(img)
    d.rectangle([1300, 120, 1820, 440], fill=(196, 214, 230), outline=(120, 120, 126), width=10)
    for r in range(4):
        d.rectangle([120, 150 + r * 110, 1100, 160 + r * 110], fill=(150, 130, 100))
        for c in range(22):
            col = [(70, 110, 170), (190, 70, 60), (90, 140, 90), (220, 190, 80)][(r + c) % 4]
            d.rectangle([140 + c * 43, 70 + r * 110, 172 + c * 43, 150 + r * 110], fill=col)
    d.rectangle([300, 620, 1620, 680], fill=(190, 170, 140), outline=(140, 120, 90), width=4)
    for x in (340, 1580):
        d.rectangle([x, 680, x + 20, 840], fill=(140, 120, 90))
    for k in range(5):
        d.rectangle([420 + k * 220, 590 - (k % 2) * 20, 580 + k * 220, 620], fill=(250, 250, 246), outline=(160, 160, 160), width=2)
    return img


def og_kanban(new=False):
    """商店街の角の小さな事業所の外。入口の上に看板（帯の色だけ。文字は描かない）。new は看板の色が変わる。"""
    img = vgrad((W, H), (180, 206, 230), (222, 230, 236))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(170, 166, 160))
    for k in range(2):
        x0 = -200 + k * 1520
        d.rectangle([x0, 240, x0 + 600, 760], fill=(200, 190, 176), outline=(150, 140, 126), width=4)
    d.rectangle([460, 220, 1460, 760], fill=(236, 230, 220), outline=(160, 150, 136), width=6)
    band = (240, 150, 40) if not new else (60, 150, 120)
    d.rectangle([500, 260, 1420, 380], fill=band, outline=(120, 110, 100), width=4)
    d.rectangle([540, 290, 900, 350], fill=(255, 255, 255))
    d.rectangle([760, 450, 1160, 760], fill=(176, 200, 214), outline=(120, 124, 130), width=8)
    d.line([(960, 450), (960, 760)], fill=(120, 124, 130), width=6)
    d.rectangle([520, 450, 700, 640], fill=(196, 214, 228), outline=(120, 124, 130), width=6)
    d.rectangle([1220, 450, 1400, 640], fill=(196, 214, 228), outline=(120, 124, 130), width=6)
    return img


def og_haken():
    """早朝の駅前の歩道。まだ薄暗い空、閉まった店のシャッター、集合場所に並ぶ人の形。"""
    img = vgrad((W, H), (70, 90, 130), (180, 170, 170))
    d = _d(img)
    for k in range(5):
        d.rectangle([k * 400, 260, k * 400 + 360, 700], fill=(120, 116, 120), outline=(90, 86, 90), width=3)
        d.rectangle([k * 400 + 30, 480, k * 400 + 330, 700], fill=(170, 170, 176))
        for j in range(8):
            d.line([(k * 400 + 30, 490 + j * 26), (k * 400 + 330, 490 + j * 26)], fill=(140, 140, 146), width=3)
    d.rectangle([0, 700, W, H], fill=(150, 146, 140))
    for x in (300, 1500):
        d.line([(x, 700), (x, 380)], fill=(80, 80, 86), width=10)
        d.ellipse([x - 26, 360, x + 26, 400], fill=(250, 230, 180))
    _person_line(d, 520, 960, 12, 1.0, cols=[(70, 74, 90), (90, 80, 70), (60, 70, 80)])
    return img


# ---------------------------------------------------------------- リクルート事件
def ez_okujo():
    """1960年、ビルの屋上の小さな部屋（2坪半ほど）。机1つと黒電話、窓の外に給水塔と空。"""
    img = _rgb(base((214, 206, 188), (200, 192, 174)))
    wood_floor(img, FLOOR, col=(150, 120, 90), line=(130, 100, 72))
    d = _d(img)
    d.rectangle([1100, 140, 1700, 520], fill=(176, 206, 230), outline=(110, 90, 70), width=12)
    d.line([(1400, 140), (1400, 520)], fill=(110, 90, 70), width=8)
    d.rectangle([1180, 300, 1300, 470], fill=(140, 140, 136))
    d.polygon([(1170, 300), (1240, 250), (1310, 300)], fill=(120, 120, 116))
    for k in range(4):
        d.line([(1190 + k * 30, 470), (1190 + k * 30, 520)], fill=(110, 110, 106), width=6)
    d.rectangle([300, 560, 900, 620], fill=(150, 110, 70), outline=(110, 80, 50), width=4)
    for x in (320, 860):
        d.rectangle([x, 620, x + 24, 820], fill=(120, 86, 56))
    d.ellipse([700, 500, 800, 560], fill=(24, 24, 26))
    d.rectangle([720, 470, 780, 510], fill=(24, 24, 26))
    for k in range(3):
        d.rectangle([380 + k * 90, 520 + k * 6, 460 + k * 90, 560], fill=(246, 242, 226), outline=(150, 140, 120), width=2)
    d.rectangle([120, 200, 300, 700], fill=(180, 160, 130), outline=(130, 110, 80), width=4)
    return img


def ez_henshu(yama=False):
    """情報誌の会社の事務所。机と電話、壁の棚。yama は床から天井近くまで分厚い本（電話帳ほど）の山（タダで配る本）。"""
    img = _rgb(base((222, 220, 210), (208, 206, 196)))
    wood_floor(img, FLOOR, col=(150, 140, 120), line=(132, 122, 104))
    d = _d(img)
    d.rectangle([140, 140, 760, 420], fill=(248, 246, 236), outline=(140, 140, 136), width=6)
    for k in range(5):
        d.line([(180, 180 + k * 46), (560 + (k % 2) * 80, 180 + k * 46)], fill=(70, 70, 70), width=5)
    d.rectangle([300, 620, 1620, 680], fill=(170, 150, 120), outline=(130, 110, 80), width=4)
    for k in range(4):
        x = 420 + k * 300
        d.ellipse([x, 570, x + 70, 620], fill=(24, 24, 26))
    if yama:
        rnd = random.Random(4)
        cols = [(200, 60, 60), (60, 100, 170), (230, 180, 60), (90, 150, 100)]
        for c in range(9):
            x = 60 + c * 205
            h = rnd.randint(5, 9)
            for r in range(h):
                y = FLOOR - (r + 1) * 70
                d.rectangle([x, y, x + 180, y + 66], fill=cols[(c + r) % 4], outline=(60, 50, 40), width=3)
                d.rectangle([x + 10, y + 10, x + 170, y + 22], fill=(250, 250, 246))
    return img


def ez_party():
    """ホテルの宴会場の「励ます会」。金の屏風と壇、白いテーブルクロスの丸テーブル、手前の末席に名札の札（文字は線）。"""
    img = _rgb(base((200, 184, 160), (186, 170, 146)))
    d = _d(img)
    d.rectangle([0, 640, W, H], fill=(150, 60, 50))
    for k in range(6):
        d.rectangle([460 + k * 170, 140, 620 + k * 170, 520], fill=(230, 190, 80), outline=(170, 130, 50), width=4)
    d.rectangle([420, 520, 1500, 600], fill=(130, 90, 60))
    for k in range(5):
        d.ellipse([1180 + k * 10, 160 - k * 4, 1260 + k * 10, 240 - k * 4], fill=(220, 220, 230))
    for cx, cy in ((300, 760), (960, 760), (1620, 760), (620, 960), (1300, 960)):
        d.ellipse([cx - 220, cy - 60, cx + 220, cy + 60], fill=(250, 250, 248), outline=(200, 200, 196), width=4)
        for j in range(4):
            d.ellipse([cx - 120 + j * 70, cy - 30, cx - 90 + j * 70, cy], fill=(230, 236, 240))
    d.rectangle([560, 900, 680, 940], fill=(250, 250, 246), outline=(150, 150, 150), width=2)
    d.line([(576, 920), (664, 920)], fill=(60, 60, 60), width=4)
    return img


def ez_osetsu(kinko=False):
    """応接室の机に、鉛筆で囲いのある売買の書類と朱肉。kinko は奥の金庫の扉が開いて、株券の束が積まれている。"""
    img = tj_osetsu()
    d = _d(img)
    d.rectangle([840, 560, 1060, 610], fill=(250, 250, 246), outline=(150, 150, 150), width=2)
    d.rectangle([860, 572, 960, 598], outline=(90, 90, 90), width=3)
    d.ellipse([1080, 572, 1120, 604], fill=(200, 40, 40))
    if kinko:
        d.rectangle([1500, 380, 1800, 820], fill=(70, 74, 82), outline=(40, 40, 46), width=8)
        d.rectangle([1520, 400, 1780, 800], fill=(40, 42, 48))
        for r in range(5):
            for c in range(2):
                d.rectangle([1540 + c * 120, 420 + r * 74, 1640 + c * 120, 480 + r * 74], fill=(232, 220, 190), outline=(170, 150, 110), width=2)
                d.line([(1550 + c * 120, 450 + r * 74), (1630 + c * 120, 450 + r * 74)], fill=(170, 90, 60), width=3)
    return img


def ez_board(ue=False):
    """証券会社の店頭の株価のボード（数字は描かず、帯の長さで値を見せる）。ue は1行の帯だけがいっぱいまで伸びて赤く光る。"""
    img = shoken()
    d = _d(img)
    d.rectangle([120, 80, 1800, 600], fill=(20, 24, 30), outline=(90, 90, 96), width=10)
    for r in range(9):
        y = 120 + r * 52
        d.rectangle([180, y, 420, y + 30], fill=(200, 200, 210))
        ln = 640 if (r == 4 and ue) else 160 + (r * 97) % 300
        d.rectangle([500, y, 500 + ln * 2, y + 30], fill=(230, 60, 50) if (r == 4 and ue) else (240, 200, 80))
    return img


def ez_byoin():
    """病院の個室。白い壁、ベッド、点滴の台、窓のカーテン。"""
    img = _rgb(base((236, 238, 236), (224, 226, 224)))
    wood_floor(img, FLOOR, col=(200, 200, 196), line=(186, 186, 182))
    d = _d(img)
    d.rectangle([1100, 140, 1640, 480], fill=(200, 220, 236), outline=(160, 160, 166), width=8)
    d.rectangle([1060, 120, 1180, 520], fill=(230, 220, 200))
    d.rectangle([1560, 120, 1680, 520], fill=(230, 220, 200))
    d.rectangle([300, 600, 1000, 700], fill=(250, 250, 252), outline=(170, 170, 176), width=4)
    d.rectangle([300, 560, 420, 600], fill=(250, 250, 252), outline=(170, 170, 176), width=3)
    d.rectangle([280, 700, 1020, 730], fill=(150, 150, 156))
    for x in (300, 1000):
        d.rectangle([x - 10, 520, x + 10, 840], fill=(170, 170, 176))
    d.line([(1120, 300), (1120, 840)], fill=(150, 150, 156), width=8)
    d.rounded_rectangle([1090, 300, 1150, 380], radius=10, fill=(230, 240, 250), outline=(150, 150, 156), width=3)
    return img


def ez_shukusha(tv=False):
    """議員宿舎の和室。座卓、テレビの下のラック、食卓のガラスケース。tv は同じ部屋がテレビの画面になり、
    画面の中は和室に白いモザイクの四角（放送の画）。"""
    img = _rgb(base((226, 214, 190), (212, 200, 176)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([1200, 360, 1640, 640], fill=(30, 30, 34), outline=(80, 80, 86), width=8)
    d.rectangle([1180, 640, 1660, 760], fill=(130, 96, 66), outline=(100, 70, 46), width=4)
    d.rectangle([500, 700, 1000, 760], fill=(140, 100, 66))
    d.rectangle([180, 400, 420, 700], fill=(220, 230, 236), outline=(150, 130, 100), width=6)
    for k in range(3):
        d.line([(180, 480 + k * 80), (420, 480 + k * 80)], fill=(150, 130, 100), width=4)
    if tv:
        img2 = vgrad((W, H), (20, 20, 24), (30, 30, 36))
        d2 = _d(img2)
        d2.rectangle([160, 80, 1760, 940], fill=(60, 60, 64), outline=(120, 120, 126), width=20)
        small = img.resize((1560, 820))
        img2.paste(small, (180, 100))
        d2 = _d(img2)
        rnd = random.Random(8)
        for r in range(6):
            for c in range(6):
                g = rnd.randint(170, 240)
                d2.rectangle([700 + c * 50, 400 + r * 50, 748 + c * 50, 448 + r * 50], fill=(g, g, g))
        return img2
    return img


def ez_ginza(kenka=False):
    """銀座の大通りの角に立つ本社ビル（窓の帯。看板の文字は描かない）。kenka は入口に白い菊の献花台と遺影の額（人の形だけ）。"""
    img = vgrad((W, H), (176, 200, 226), (220, 228, 236))
    d = _d(img)
    d.rectangle([520, 60, 1400, 820], fill=(180, 180, 186), outline=(130, 130, 136), width=6)
    for r in range(11):
        d.rectangle([560, 90 + r * 58, 1360, 130 + r * 58], fill=(130, 160, 190))
    d.rectangle([800, 720, 1120, 820], fill=(90, 110, 130))
    for x0 in (0, 1460):
        d.rectangle([x0, 300, x0 + 460, 820], fill=(200, 196, 188), outline=(150, 146, 138), width=4)
    d.rectangle([0, 820, W, H], fill=(170, 168, 164))
    if kenka:
        d.rectangle([700, 760, 1220, 860], fill=(250, 250, 252), outline=(180, 180, 186), width=4)
        d.rectangle([900, 640, 1020, 760], fill=(40, 40, 44))
        d.rectangle([912, 652, 1008, 748], fill=(200, 200, 204))
        d.ellipse([940, 664, 980, 704], fill=(90, 90, 96))
        d.rounded_rectangle([930, 700, 990, 748], radius=12, fill=(90, 90, 96))
        rnd = random.Random(2)
        for _ in range(70):
            x, y = rnd.randint(710, 1200), rnd.randint(770, 840)
            d.ellipse([x, y, x + 26, y + 26], fill=(250, 250, 244), outline=(210, 210, 200))
    return img


# ---------------------------------------------------------------- てるみくらぶの破綻
def tm_shinbun():
    """机の上に広げた新聞の全面広告（南の島の海と飛行機の形、値段の代わりの赤い大きな帯。文字は描かない）。"""
    img = vgrad((W, H), (150, 120, 90), (120, 92, 66))
    d = _d(img)
    d.polygon([(260, 140), (1680, 110), (1720, 960), (220, 990)], fill=(240, 236, 224), outline=(180, 170, 150))
    d.rectangle([330, 200, 1610, 760], fill=(60, 170, 220))
    d.rectangle([330, 560, 1610, 760], fill=(240, 220, 160))
    d.ellipse([1330, 230, 1480, 380], fill=(255, 220, 90))
    for k in range(3):
        x = 420 + k * 120
        d.line([(x, 760), (x + 30, 560)], fill=(120, 90, 50), width=10)
        for a in range(4):
            d.line([(x + 30, 560), (x - 40 + a * 50, 520 + (a % 2) * 30)], fill=(40, 140, 70), width=12)
    d.polygon([(900, 330), (1180, 300), (1200, 316), (920, 350)], fill=(250, 250, 252))
    d.polygon([(1030, 318), (1080, 262), (1100, 262), (1070, 322)], fill=(250, 250, 252))
    for k in range(3):
        d.rectangle([380 + k * 410, 790, 740 + k * 410, 900], fill=(220, 40, 40))
        d.rectangle([400 + k * 410, 810, 720 + k * 410, 840], fill=(255, 240, 240))
    return img


def tm_jimusho(poster=False, yoru=False):
    """渋谷の旅行会社の事務所（ブラウン管でなく薄い画面）。poster は壁一面に旅のポスター（海・山・街の絵。文字なし）。"""
    img = jimusho90(yoru=yoru)
    d = _d(img)
    if poster:
        rnd = random.Random(11)
        scenes = [((60, 170, 220), (240, 220, 160)), ((120, 180, 230), (90, 150, 90)), ((250, 170, 120), (120, 110, 130)),
                  ((90, 160, 220), (250, 250, 250)), ((40, 140, 200), (230, 210, 150))]
        for r in range(2):
            for c in range(7):
                x0, y0 = 60 + c * 190 + (r % 2) * 40, 90 + r * 230
                if x0 > 1300:
                    continue
                sky, land = scenes[rnd.randint(0, 4)]
                d.rectangle([x0, y0, x0 + 160, y0 + 200], fill=sky, outline=(250, 250, 250), width=6)
                d.rectangle([x0 + 6, y0 + 120, x0 + 154, y0 + 194], fill=land)
                d.ellipse([x0 + 110, y0 + 20, x0 + 140, y0 + 50], fill=(255, 230, 120))
    return img


def tm_kessan(kuro=False):
    """机の上の決算書（大きな紙。数字の代わりに太い帯）。帯は赤。kuro は同じ帯が黒に塗り替わる。"""
    img = vgrad((W, H), (150, 120, 90), (120, 92, 66))
    d = _d(img)
    d.polygon([(420, 120), (1500, 100), (1540, 960), (380, 980)], fill=(250, 250, 246), outline=(180, 170, 150))
    d.rectangle([500, 180, 1100, 230], fill=(60, 60, 64))
    for k in range(7):
        y = 300 + k * 80
        d.line([(500, y), (900, y)], fill=(150, 150, 150), width=5)
        col = (40, 40, 44) if (kuro or k < 4) else (210, 40, 40)
        d.rectangle([1040, y - 14, 1400, y + 14], fill=col)
    d.rectangle([1040, 860, 1400, 900], fill=(40, 40, 44) if kuro else (210, 40, 40))
    d.line([(1000, 840), (1440, 840)], fill=(60, 60, 64), width=6)
    return img


def tm_seikyu():
    """机の上の新聞の広告と、その上に重なった支払いの請求書の束（赤い判）。文字は描かない。"""
    img = tm_shinbun()
    d = _d(img)
    for k in range(5):
        x0, y0 = 980 + k * 40, 420 + k * 50
        d.polygon([(x0, y0), (x0 + 520, y0 - 30), (x0 + 560, y0 + 380), (x0 + 30, y0 + 410)], fill=(248, 248, 244), outline=(150, 150, 150))
        for j in range(5):
            d.line([(x0 + 60, y0 + 70 + j * 50), (x0 + 400, y0 + 50 + j * 50)], fill=(140, 140, 140), width=4)
    d.ellipse([1340, 760, 1480, 860], outline=(210, 40, 40), width=10)
    return img


def tm_honsha(harigami=False):
    """ビルの中の旅行会社の入口（ガラスの扉、受付）。harigami は扉に白い張り紙と、前に報道のカメラ。"""
    img = _rgb(base((214, 214, 210), (200, 200, 196)))
    wood_floor(img, FLOOR, col=(170, 166, 160), line=(150, 146, 140))
    d = _d(img)
    d.rectangle([520, 140, 1400, FLOOR], fill=(180, 200, 214), outline=(120, 124, 130), width=10)
    d.line([(960, 140), (960, FLOOR)], fill=(120, 124, 130), width=8)
    for x in (930, 990):
        d.rectangle([x - 6, 520, x + 6, 640], fill=(200, 200, 206))
    d.rectangle([620, 520, 900, 680], fill=(236, 230, 220))
    d.rectangle([600, 200, 1320, 260], fill=(60, 140, 200))
    if harigami:
        for x0 in (700, 1030):
            d.rectangle([x0, 380, x0 + 190, 640], fill=(252, 252, 250), outline=(160, 160, 160), width=3)
            for j in range(6):
                d.line([(x0 + 24, 420 + j * 34), (x0 + 166, 420 + j * 34)], fill=(60, 60, 60), width=5)
        _press(d, 60, 1060, 7, 1.1)
        _press(d, 1380, 1060, 7, 1.1)
    return img


def tm_hotel():
    """南の島のホテルのフロント。木のカウンター、背中にヤシの見える窓、天井のファン。"""
    img = _rgb(base((236, 226, 204), (222, 212, 190)))
    wood_floor(img, FLOOR, col=(170, 130, 90), line=(150, 112, 76))
    d = _d(img)
    d.rectangle([160, 120, 1760, 470], fill=(120, 200, 230), outline=(150, 110, 70), width=10)
    d.rectangle([160, 400, 1760, 470], fill=(60, 150, 200))
    for k in range(4):
        x = 300 + k * 420
        d.line([(x, 470), (x + 40, 200)], fill=(120, 90, 50), width=14)
        for a in range(5):
            d.line([(x + 40, 200), (x - 60 + a * 50, 160 + (a % 2) * 50)], fill=(40, 140, 70), width=14)
    d.line([(960, 0), (960, 60)], fill=(110, 90, 70), width=6)
    d.ellipse([900, 50, 1020, 80], fill=(150, 120, 90))
    d.rectangle([380, 600, 1540, 820], fill=(150, 104, 66), outline=(110, 74, 46), width=6)
    d.rectangle([360, 580, 1560, 610], fill=(190, 150, 110))
    d.rectangle([1300, 540, 1360, 580], fill=(220, 190, 80))
    return img


def tm_kuko_yoru():
    """夜の空港のロビー。並んだ長いすと、窓の外の暗い駐機場。人はいない。"""
    img = vgrad((W, H), (30, 36, 56), (60, 64, 80))
    d = _d(img)
    d.rectangle([0, 120, W, 560], fill=(14, 18, 34), outline=(90, 94, 110), width=8)
    for k in range(1, 8):
        d.line([(k * 240, 120), (k * 240, 560)], fill=(90, 94, 110), width=6)
    d.rectangle([0, 560, W, H], fill=(110, 110, 118))
    for r in range(2):
        for k in range(5):
            x = 120 + k * 360 + r * 60
            y = 760 + r * 160
            d.rectangle([x, y - 60, x + 300, y], fill=(60, 90, 140))
            d.rectangle([x, y, x + 300, y + 20], fill=(140, 140, 150))
            for j in range(4):
                d.line([(x + 30 + j * 80, y + 20), (x + 30 + j * 80, y + 70)], fill=(140, 140, 150), width=6)
    for x in (400, 1500):
        d.ellipse([x - 20, 420, x + 20, 440], fill=(255, 220, 140))
    return img


def tm_kyokai(hako=False):
    """業界団体の事務の部屋。机と電卓、封筒の束。hako は部屋じゅうに封筒の詰まった段ボール箱が積み上がる。"""
    img = jimusho90()
    d = _d(img)
    for k in range(4):
        d.rectangle([520 + k * 260, 560, 700 + k * 260, 610], fill=(240, 236, 220), outline=(170, 160, 140), width=2)
    if hako:
        rnd = random.Random(9)
        for r in range(4):
            for c in range(11):
                if rnd.random() < 0.15:
                    continue
                x, y = 20 + c * 172, FLOOR - (r + 1) * 120
                d.rectangle([x, y, x + 160, y + 112], fill=(196, 160, 110), outline=(140, 110, 70), width=3)
                d.line([(x, y + 30), (x + 160, y + 30)], fill=(150, 120, 80), width=3)
                d.rectangle([x + 40, y - 14, x + 120, y + 6], fill=(246, 244, 236))
    return img


def tm_kuko(gyoretsu=False):
    """空港の出発ロビーのカウンター。gyoretsu はカウンターの前に困った客の長い列。"""
    img = kuko_lobby(sukunai=True)
    if gyoretsu:
        d = _d(img)
        _person_line(d, 60, 1010, 13, 1.0)
        _person_line(d, 1000, 1010, 13, 1.0)
    return img


LOCATIONS = {
    # ゴーン事件
    "gs_heya": gs_heya, "gs_haneda": gs_haneda, "gs_haneda_kuruma": lambda: gs_haneda(kuruma=True),
    "gs_kanku": gs_kanku, "gs_kanku_hako": lambda: gs_kanku(hako=True), "gs_hako": gs_hako,
    "gs_kosoku": gs_kosoku, "gs_kosoku_hodo": lambda: gs_kosoku(hodo=True), "gs_beirut": gs_beirut,
    "gs_kojo": kojo_line, "gs_kojo_teishi": lambda: kojo_line(teishi=True),
    "gs_honsha": ld_tower, "gs_honsha_yoru": lambda: ld_tower(sosaku=True),
    "gs_kaigi": kaigi, "gs_kaigi_up": lambda: kaigi(up=True), "gs_kaigi_akaji": lambda: kaigi(akaji=True),
    "gs_yakuin": lambda: yakuin(view=(170, 196, 230), city=True), "gs_kaiken": _sega_kaiken,
    "gs_houtei": _sogo_saibansho, "gs_saikosai": cg_saikosai, "gs_kanmae": ld_kanmae,
    "gs_shinbun": tj_shinbun, "gs_gendai": _sega_gendai,
    "gs_sokai": kabunushi_kaijo, "gs_nimai": gs_nimai, "gs_door": gs_door, "gs_door3": lambda: gs_door(3),
    "gs_karenda": gs_karenda, "gs_menkai": gs_menkai, "gs_kei": gs_kei, "gs_doga": gs_doga,
    "gs_houtei_kara": gs_houtei_kara, "gs_mado": gs_mado, "gs_genkan": mx_genkan, "gs_shoken": shoken,
    # コムスンの処分
    "og_heya": og_heya, "og_disco": og_disco, "og_disco_kara": lambda: og_disco(kara=True),
    "og_kaigo": og_kaigo, "og_jigyosho": og_jigyosho, "og_jigyosho_sukunai": lambda: og_jigyosho(sukunai=True),
    "og_haken": og_haken, "og_tower": ld_tower, "og_jimusho": jimusho90,
    "og_soko": og_soko, "og_care": og_care, "og_care_oshirase": lambda: og_care(oshirase=True),
    "og_kencho": og_kencho, "og_kanban": og_kanban, "og_kanban_new": lambda: og_kanban(new=True),
    "og_studio": ik_studio, "og_ny": ik_ny, "og_yakei": lambda: yakuin(view=(24, 30, 56), city=True),
    "og_kaigi": kaigi, "og_kaigi_akaji": lambda: kaigi(akaji=True), "og_yakuin": lambda: yakuin(),
    "og_kaiken": _sega_kaiken, "og_shinbun": tj_shinbun, "og_houtei": _sogo_saibansho,
    "og_kokkai": _sogo_kokkai, "og_shoken": shoken, "og_gendai": _sega_gendai,
    # てるみくらぶの破綻
    "tm_heya": lambda: heya3("ryoko"), "tm_shinbun": tm_shinbun, "tm_seikyu": tm_seikyu, "tm_kuko": tm_kuko,
    "tm_kuko_gyoretsu": lambda: tm_kuko(gyoretsu=True), "tm_kuko_yoru": tm_kuko_yoru,
    "tm_jimusho": tm_jimusho, "tm_jimusho_poster": lambda: tm_jimusho(poster=True),
    "tm_jimusho_yoru": lambda: tm_jimusho(yoru=True), "tm_kessan": tm_kessan, "tm_kessan_kuro": lambda: tm_kessan(kuro=True),
    "tm_honsha": tm_honsha, "tm_honsha_harigami": lambda: tm_honsha(harigami=True), "tm_hotel": tm_hotel,
    "tm_kyokai": tm_kyokai, "tm_kyokai_hako": lambda: tm_kyokai(hako=True), "tm_hall": kabunushi_kaijo,
    "tm_denwa": lambda: dz_jigyobu(denwa=True), "tm_osetsu": tj_osetsu, "tm_kaigi": kaigi,
    "tm_kaigi_akaji": lambda: kaigi(akaji=True), "tm_kaiken": _sega_kaiken, "tm_houtei": _sogo_saibansho,
    "tm_gendai": _sega_gendai,
    # リクルート事件
    "ez_heya": lambda: heya3("sumaho"), "ez_okujo": ez_okujo, "ez_henshu": ez_henshu,
    "ez_henshu_yama": lambda: ez_henshu(yama=True), "ez_party": ez_party,
    "ez_osetsu": ez_osetsu, "ez_osetsu_kinko": lambda: ez_osetsu(kinko=True),
    "ez_board": ez_board, "ez_board_ue": lambda: ez_board(ue=True), "ez_byoin": ez_byoin,
    "ez_shukusha": ez_shukusha, "ez_shukusha_tv": lambda: ez_shukusha(tv=True),
    "ez_ginza": ez_ginza, "ez_ginza_kenka": lambda: ez_ginza(kenka=True),
    "ez_kosoku": gs_kosoku, "ez_kosoku_hodo": lambda: gs_kosoku(hodo=True),
    "ez_hei": ld_hei, "ez_hei_yuki": lambda: ld_hei("yuki"), "ez_hei_sakura": lambda: ld_hei("sakura"),
    "ez_saikosai": cg_saikosai, "ez_shachoshitsu": lambda: yakuin(view=(170, 196, 230), city=True),
    "ez_shinbun": tj_shinbun, "ez_kokkai": _sogo_kokkai, "ez_houtei": _sogo_saibansho,
    "ez_kaigi": kaigi, "ez_yakuin": lambda: yakuin(view=(170, 196, 230), city=True),
    "ez_kaiken": _sega_kaiken, "ez_shoken": shoken, "ez_jimusho": jimusho90, "ez_gendai": _sega_gendai,
}

# 年号カード。接頭辞ごとに "gs_card_2018" のように作る（台帳を見て足す）
CARDS = {"gs": ["1999", "2001", "2010", "2015", "2018", "2019", "2020", "2021", "2022", "2024", "2026"], "ez": ["1960", "1984", "1986", "1988", "1989", "1999", "2003", "2006", "2013", "2026"], "tm": ["1998", "2013", "2015", "2016", "2017", "2018", "2019", "2026"],
         "og": ["1991", "1995", "2000", "2004", "2006", "2007", "2008", "2009", "2026"]}


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
