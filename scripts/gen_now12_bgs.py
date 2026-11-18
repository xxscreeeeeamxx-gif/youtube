#!/usr/bin/env python3
"""第12弾4本（2026-12-10〜13。方向転換の実験の24〜26本目＋開発秘話の実験1本）の背景を生成する。

接頭辞: lt_（ロッテのお家騒動）/ nb_（日本振興銀行の破綻）/ pl_（プレイステーションの誕生）/ hy_（林原の破綻）
方針は gen_now11_bgs.py と同じ。実在の会社のロゴ・社名の文字・店の意匠・商品のパッケージは描かない。
実在のゲーム機・ゲームの画面・キャラクターは描かない（形を変えた架空の機械と、色の四角だけ）。
実在の人の写真や肖像は描かない（壁の写真は人の形だけ）。差し替え用は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now12_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import year_card  # noqa: E402
from scripts.gen_led_bgs import saibansho_mae  # noqa: E402
from scripts.gen_now2_bgs import heya2, kabunushi_kaijo, shingikai  # noqa: E402
from scripts.gen_now3_bgs import server_shitsu  # noqa: E402
from scripts.gen_famicom_bgs import shachoshitsu  # noqa: E402
from scripts.gen_fujifilm_bgs import kenkyujo  # noqa: E402
from scripts.gen_now8_bgs import ld_kanmae, ld_tower, tj_kaiken, tj_osetsu, tj_shinbun  # noqa: E402
from scripts.gen_now11_bgs import mt_torishimari  # noqa: E402
from scripts.gen_dai_bgs import yamiichi  # noqa: E402
from scripts.gen_sega_bgs import kaichoshitsu  # noqa: E402
from scripts.gen_sogo_bgs import kokkai  # noqa: E402
from scripts.gen_now3_bgs import jimusho90, kuko_lobby, tenjikai  # noqa: E402
from scripts.gen_sega_bgs import yakuinkai  # noqa: E402
from scripts.gen_now9_bgs import _light, _press  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _d, _rgb, kaigi  # noqa: E402
from scripts.gen_pn_bgs import kokaido  # noqa: E402
from scripts.gen_sega_bgs import _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import saibansho as _sogo_saibansho  # noqa: E402


def _lines(d, x0, y0, x1, n, gap=34, col=(110, 110, 110), w=5):
    """文字の代わりの線。"""
    for j in range(n):
        d.line([(x0, y0 + j * gap), (x1 - (j % 3) * 40, y0 + j * gap)], fill=col, width=w)


# ---------------------------------------------------------------- 日本振興銀行の破綻
def nb_heya():
    """今の部屋。机に通帳とお年玉の袋（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([250, 590, 380, 640], fill=(60, 110, 170), outline=(30, 60, 110), width=3)
    d.rectangle([262, 600, 368, 606], fill=(230, 230, 236))
    for k in range(3):
        x = 410 + k * 60
        d.rectangle([x, 570, x + 46, 640], fill=[(220, 60, 70), (240, 180, 60), (90, 160, 90)][k], outline=(120, 60, 40), width=2)
        d.rectangle([x + 10, 580, x + 36, 596], fill=(250, 248, 236))
    return img


def nb_madoguchi(retsu=False):
    """銀行の窓口。カウンターと仕切り、後ろの壁に金利の掲示板（数字は線だけ）。retsu は窓口の前に並ぶ人の列。"""
    img = _rgb(base((236, 236, 232), (220, 220, 214)))
    d = _d(img)
    d.rectangle([520, 120, 1400, 420], fill=(30, 50, 80), outline=(200, 190, 150), width=8)
    for r in range(5):
        d.line([(580, 170 + r * 50), (900, 170 + r * 50)], fill=(230, 230, 236), width=6)
        d.line([(1100, 170 + r * 50), (1320, 170 + r * 50)], fill=(250, 200, 80), width=8)
    d.rectangle([0, 620, W, 720], fill=(180, 160, 130), outline=(140, 120, 90), width=4)
    d.rectangle([0, 720, W, H], fill=(196, 196, 190))
    for k in range(6):
        d.rectangle([60 + k * 320, 470, 70 + k * 320, 620], fill=(180, 186, 190))
    d.rectangle([0, 470, W, 478], fill=(180, 186, 190))
    if retsu:
        _person_line(d, 40, 1060, 26, 1.0)
    return img


def nb_rouka(kara=False):
    """本店の廊下。会員企業の看板（白い板、社名は線だけ）が壁にずらりと並ぶ。kara は看板が外れ、跡の四角だけが残る。"""
    img = _rgb(base((226, 224, 218), (210, 208, 202)))
    wood_floor(img, FLOOR, col=(150, 140, 130), line=(134, 124, 114))
    d = _d(img)
    rnd = random.Random(41)
    for r in range(3):
        for c in range(8):
            x, y = 80 + c * 225, 120 + r * 170
            if kara and rnd.random() < 0.8:
                d.rectangle([x, y, x + 190, y + 120], outline=(196, 194, 188), width=3)
                continue
            d.rectangle([x, y, x + 190, y + 120], fill=(250, 250, 246), outline=(150, 146, 140), width=4)
            d.rectangle([x, y, x + 190, y + 24], fill=[(60, 100, 160), (40, 120, 90), (160, 70, 60)][(r + c) % 3])
            _lines(d, x + 20, y + 56, x + 170, 2, gap=32, w=6)
    return img


def nb_server(kara=False):
    """サーバー室の画面。大きな画面にメールの一覧（行は線だけ）。kara は一覧が空白になる。"""
    img = server_shitsu()
    d = _d(img)
    d.rectangle([560, 140, 1360, 620], fill=(20, 24, 30), outline=(120, 124, 130), width=10)
    d.rectangle([590, 170, 1330, 220], fill=(40, 80, 140))
    if not kara:
        for j in range(9):
            y = 250 + j * 40
            d.rectangle([600, y, 630, y + 24], fill=(230, 200, 80))
            d.line([(650, y + 12), (1000 - (j % 3) * 60, y + 12)], fill=(220, 224, 230), width=6)
            d.line([(1060, y + 12), (1300, y + 12)], fill=(150, 156, 166), width=6)
    return img


def nb_honten(yoake=False):
    """大手町の高いビルの入口（ガラスの壁）。yoake は夜明け前の暗い空。"""
    return ld_tower(yoake=yoake)


def nb_shutter():
    """銀行の支店の入口（石の壁のビルの1階）。下りた銀色のシャッターに白い張り紙が2枚（文字は線だけ）、前に報道のカメラ。"""
    img = vgrad((W, H), (180, 200, 222), (222, 228, 234))
    d = _d(img)
    d.rectangle([200, 80, 1720, 820], fill=(200, 194, 184), outline=(150, 146, 138), width=6)
    for c in range(8):
        d.rectangle([260 + c * 180, 140, 380 + c * 180, 300], fill=(140, 166, 190))
    d.rectangle([200, 340, 1720, 380], fill=(170, 164, 156))
    d.rectangle([520, 420, 1400, 820], fill=(190, 194, 200), outline=(130, 134, 140), width=6)
    for k in range(18):
        d.line([(520, 440 + k * 21), (1400, 440 + k * 21)], fill=(160, 164, 170), width=3)
    for x0 in (700, 1040):
        d.rectangle([x0, 520, x0 + 180, 740], fill=(252, 252, 250), outline=(160, 160, 160), width=3)
        _lines(d, x0 + 22, 560, x0 + 160, 5, gap=32, col=(60, 60, 60), w=5)
    d.rectangle([0, 820, W, H], fill=(186, 184, 178))
    _press(d, 30, 1070, 6, 1.1)
    _press(d, 1440, 1070, 6, 1.1)
    return img


def nb_kaigi_akaji():
    """本店の会議室。ホワイトボードに右下がりの赤い線（数字は描かない）。"""
    return kaigi(akaji=True)


# ---------------------------------------------------------------- 林原の破綻
def hy_heya():
    """今の部屋。机にテストの答案（赤い丸と点数の欄は線だけ）。"""
    img = heya2("none")
    d = _d(img)
    for k in range(2):
        x = 240 + k * 200
        d.rectangle([x, 560, x + 170, 640], fill=(252, 252, 248), outline=(170, 160, 140), width=2)
        d.ellipse([x + 120, 566, x + 160, 600], outline=(220, 40, 40), width=4)
        _lines(d, x + 14, 584, x + 110, 2, gap=24, w=4)
    return img


def hy_kojo():
    """古い水あめの工場。大きな鉄の釜が並び、湯気、木の床。"""
    img = _rgb(base((150, 136, 120), (124, 110, 96)))
    wood_floor(img, FLOOR, col=(110, 90, 70), line=(96, 76, 58))
    d = _d(img)
    for k in range(4):
        x = 140 + k * 440
        d.ellipse([x, 520, x + 320, 640], fill=(70, 70, 76))
        d.rectangle([x, 580, x + 320, 840], fill=(80, 80, 86))
        d.ellipse([x, 780, x + 320, 900], fill=(70, 70, 76))
        d.ellipse([x + 30, 530, x + 290, 620], fill=(210, 170, 90))
        for j in range(3):
            d.ellipse([x + 60 + j * 70, 360 - j * 40, x + 160 + j * 70, 460 - j * 40], fill=(240, 240, 240, 90))
    return img


def hy_ekimae(kouji=False):
    """駅前の広い空き地（フェンスと雑草、遠くに駅ビルと高架）。kouji は大きな建物の骨組みとクレーン（看板は文字なし）。"""
    img = vgrad((W, H), (160, 196, 232), (224, 230, 236))
    d = _d(img)
    d.rectangle([0, 360, W, 420], fill=(150, 150, 156))
    for k in range(6):
        d.rectangle([60 + k * 320, 300, 300 + k * 320, 360], fill=[(190, 186, 176), (170, 176, 186)][k % 2])
    d.rectangle([0, 420, W, H], fill=(176, 166, 140))
    if kouji:
        for r in range(5):
            d.line([(300, 860 - r * 110), (1620, 860 - r * 110)], fill=(130, 130, 136), width=10)
        for c in range(12):
            d.line([(300 + c * 120, 860), (300 + c * 120, 420)], fill=(130, 130, 136), width=10)
        for x in (420, 1500):
            d.line([(x, 860), (x, 140)], fill=(230, 180, 40), width=16)
            d.line([(x - 220, 160), (x + 180, 160)], fill=(230, 180, 40), width=12)
        d.rectangle([700, 900, 1220, 980], fill=(250, 250, 246), outline=(150, 146, 140), width=4)
    else:
        rnd = random.Random(5)
        for _ in range(160):
            x, y = rnd.randint(0, W), rnd.randint(480, 900)
            d.line([(x, y), (x + rnd.randint(-8, 8), y - 30)], fill=(110, 140, 80), width=4)
    for x in range(0, W, 120):
        d.line([(x, 900), (x, 1000)], fill=(120, 120, 120), width=6)
    d.line([(0, 920), (W, 920)], fill=(120, 120, 120), width=4)
    d.line([(0, 980), (W, 980)], fill=(120, 120, 120), width=4)
    return img


def hy_gobi():
    """砂漠の発掘現場。黄土色の大地、テントと道具、地面に見える大きな骨の形。"""
    img = vgrad((W, H), (150, 190, 230), (236, 220, 180))
    d = _d(img)
    d.polygon([(0, 480), (500, 420), (1100, 460), (1500, 410), (W, 450), (W, H), (0, H)], fill=(210, 170, 110))
    d.rectangle([0, 600, W, H], fill=(200, 160, 100))
    d.polygon([(200, 600), (340, 460), (480, 600)], fill=(240, 240, 230))
    d.polygon([(1500, 600), (1640, 470), (1780, 600)], fill=(240, 240, 230))
    bx, by = 620, 820
    for k in range(10):
        d.ellipse([bx + k * 60, by - 20, bx + k * 60 + 50, by + 20], fill=(240, 232, 210), outline=(170, 150, 120), width=3)
    for k in range(6):
        x = bx + 100 + k * 70
        d.arc([x, by - 110, x + 60, by + 30], 200, 340, fill=(240, 232, 210), width=10)
    d.ellipse([bx + 600, by - 70, bx + 760, by + 40], fill=(240, 232, 210), outline=(170, 150, 120), width=3)
    d.rectangle([560, 760, 1440, 900], outline=(150, 110, 70), width=4)
    return img


def hy_kessan(chigau=False):
    """机の上に、同じ表紙の決算書が2冊開いて並ぶ（数字の代わりに帯）。chigau は右の冊の帯の長さと色が違う。"""
    img = vgrad((W, H), (150, 120, 90), (120, 92, 66))
    d = _d(img)
    lens = [380, 120, 400, 300, 90, 360, 410, 150, 330]
    for k, x0 in enumerate((200, 1000)):
        d.rectangle([x0, 160, x0 + 720, 900], fill=(252, 252, 248), outline=(170, 160, 140), width=4)
        d.rectangle([x0, 160, x0 + 720, 240], fill=(40, 70, 120))
        for r in range(9):
            y = 300 + r * 64
            d.line([(x0 + 40, y), (x0 + 300, y)], fill=(140, 140, 140), width=5)
            alt = chigau and k == 1
            ln = lens[r] if alt else 260
            col = (200, 50, 50) if alt else (60, 60, 60)
            d.rectangle([x0 + 400, y - 14, x0 + 400 + int(ln * 0.75), y + 14], fill=col)
    return img


def hy_studio():
    """テレビのスタジオ。暗い背景に照明の吊り、向かい合う椅子と小さな机（番組の文字は描かない）。"""
    img = _rgb(base((40, 44, 60), (30, 32, 44)))
    d = _d(img)
    d.rectangle([0, 0, W, 60], fill=(20, 20, 26))
    for k in range(8):
        x = 140 + k * 230
        d.line([(x, 60), (x, 120)], fill=(80, 80, 90), width=6)
        d.rectangle([x - 30, 120, x + 30, 160], fill=(90, 90, 100))
    d.ellipse([460, 300, 1460, 620], fill=(70, 90, 140))
    d.rectangle([0, 760, W, H], fill=(50, 52, 64))
    d.rectangle([860, 620, 1060, 700], fill=(200, 196, 186))
    for x in (640, 1220):
        d.rounded_rectangle([x, 560, x + 120, 720], radius=20, fill=(220, 120, 60))
    img = _light(img, [[(300, 120), (100, 760), (600, 760)], [(1620, 120), (1300, 760), (1820, 760)]], (255, 240, 200), 40, 20)
    return img


def hy_kaigi_yasumi():
    """債権者会議の会議室が休憩で空き、長机に置かれたファクスの紙が1枚（文字は線だけ）。"""
    img = kaigi()
    d = _d(img)
    d.rectangle([880, 540, 1040, 600], fill=(252, 252, 250), outline=(150, 150, 150), width=2)
    _lines(d, 896, 556, 1024, 2, gap=18, col=(80, 80, 80), w=3)
    return img


def hy_honsha_yoru():
    """夜の本社のビル（地方都市の中くらいのビル）。窓の明かりがところどころ消えている。看板は文字なし。"""
    img = vgrad((W, H), (20, 26, 50), (50, 56, 80))
    d = _d(img)
    d.rectangle([460, 160, 1460, 880], fill=(70, 72, 84), outline=(50, 52, 60), width=6)
    rnd = random.Random(23)
    for r in range(8):
        for c in range(9):
            on = rnd.random() < 0.35
            d.rectangle([520 + c * 104, 210 + r * 80, 590 + c * 104, 260 + r * 80], fill=(250, 220, 140) if on else (40, 44, 56))
    d.rectangle([860, 120, 1060, 160], fill=(200, 200, 206))
    d.rectangle([0, 880, W, H], fill=(40, 42, 50))
    return img


# ---------------------------------------------------------------- ロッテのお家騒動
def lt_heya():
    """今の部屋（茶番）。机に部活の名簿の紙と、ガムの小さな箱（無地）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([240, 560, 420, 640], fill=(252, 252, 248), outline=(170, 160, 140), width=2)
    _lines(d, 256, 580, 400, 3, gap=18, w=4)
    d.rectangle([450, 600, 540, 640], fill=(60, 150, 110), outline=(30, 90, 70), width=2)
    return img


def lt_seoul():
    """韓国の大きな街。川と橋、高いビル群の奥に細長い高い塔（架空の形）。"""
    img = vgrad((W, H), (160, 196, 232), (224, 232, 240))
    d = _d(img)
    rnd = random.Random(17)
    x = 0
    while x < W:
        w = rnd.randint(120, 220)
        top = rnd.randint(300, 520)
        d.rectangle([x, top, x + w, 760], fill=rnd.choice([(150, 156, 170), (130, 136, 150), (170, 170, 176)]))
        x += w + 10
    d.polygon([(1180, 760), (1230, 60), (1280, 760)], fill=(120, 140, 170))
    d.polygon([(1200, 300), (1230, 60), (1260, 300)], fill=(150, 170, 200))
    d.rectangle([0, 760, W, 880], fill=(90, 140, 180))
    for k in range(9):
        d.rectangle([k * 220, 740, k * 220 + 30, 800], fill=(200, 200, 206))
    d.rectangle([0, 740, W, 756], fill=(200, 200, 206))
    d.rectangle([0, 880, W, H], fill=(150, 160, 150))
    return img


def lt_kaigi():
    """会議室のホワイトボードに、株の持ち分の円グラフ（3つに分かれた円。数字は描かない）。"""
    img = kaigi()
    d = _d(img)
    d.rectangle([620, 120, 1000, 380], fill=(250, 250, 250), outline=(150, 150, 150), width=4)
    d.pieslice([700, 140, 920, 360], 0, 120, fill=(60, 110, 180))
    d.pieslice([700, 140, 920, 360], 120, 240, fill=(80, 160, 110))
    d.pieslice([700, 140, 920, 360], 240, 360, fill=(220, 160, 60))
    return img


def lt_kojo():
    """ガムの工場。ベルトの上を銀紙に包んだ小さな板が流れる。"""
    img = _rgb(base((220, 224, 226), (200, 206, 210)))
    wood_floor(img, FLOOR, col=(160, 160, 166), line=(146, 146, 150))
    d = _d(img)
    d.rectangle([0, 560, W, 640], fill=(90, 94, 100))
    for k in range(40):
        x = 20 + k * 48
        d.rectangle([x, 540, x + 34, 560], fill=(200, 204, 214), outline=(150, 154, 160), width=2)
    for x in (300, 1300):
        d.rectangle([x, 300, x + 320, 560], fill=(170, 176, 186), outline=(120, 126, 136), width=6)
        d.rectangle([x + 40, 340, x + 140, 420], fill=(40, 60, 90))
    return img


def lt_jet():
    """空港の駐機場の小さなジェット機（白い機体、文字・ロゴは描かない）と、タラップ。"""
    img = vgrad((W, H), (150, 186, 226), (214, 224, 234))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(120, 124, 130))
    d.rounded_rectangle([360, 460, 1500, 620], radius=80, fill=(244, 244, 248))
    d.polygon([(1500, 470), (1700, 330), (1720, 380), (1560, 560)], fill=(236, 236, 240))
    d.polygon([(800, 560), (1100, 560), (900, 720), (760, 720)], fill=(230, 230, 236))
    for k in range(8):
        d.ellipse([560 + k * 100, 500, 600 + k * 100, 540], fill=(60, 80, 110))
    d.polygon([(560, 600), (520, 860), (620, 860), (640, 600)], fill=(200, 200, 206))
    return img


def lt_torishimari_kara():
    """取締役会の長い机。役員の影が並び、いちばん奥の大きな席だけが空いている。"""
    img = mt_torishimari("kiritsu")
    return img


def lt_byoin():
    """夜の大きな病院の外観。窓の明かり、玄関の前に報道の車。"""
    img = vgrad((W, H), (20, 26, 50), (50, 56, 80))
    d = _d(img)
    d.rectangle([360, 160, 1560, 860], fill=(200, 204, 210), outline=(150, 154, 160), width=6)
    rnd = random.Random(9)
    for r in range(8):
        for c in range(12):
            d.rectangle([410 + c * 96, 200 + r * 76, 470 + c * 96, 250 + r * 76],
                        fill=(250, 230, 160) if rnd.random() < 0.6 else (80, 90, 110))
    d.rectangle([860, 760, 1060, 860], fill=(120, 160, 190))
    d.rectangle([0, 860, W, H], fill=(60, 62, 70))
    _press(d, 40, 1070, 7, 1.1)
    return img


# ---------------------------------------------------------------- プレイステーションの誕生
def _crt(d, x, y, w=260, h=200, screen=(30, 40, 60)):
    """ブラウン管のモニター。x, y は左上。"""
    d.rounded_rectangle([x, y, x + w, y + h], radius=16, fill=(200, 196, 186), outline=(150, 146, 136), width=4)
    d.rounded_rectangle([x + 20, y + 18, x + w - 20, y + h - 40], radius=14, fill=screen)
    d.rectangle([x + w // 2 - 40, y + h, x + w // 2 + 40, y + h + 20], fill=(180, 176, 166))


def _tri3d(d, cx, cy, s=1.0):
    """画面の中の色の三角形でできた立体（ポリゴンの形。実在のゲームの絵ではない）。"""
    pts = [(cx, cy - 60 * s), (cx - 60 * s, cy + 30 * s), (cx + 60 * s, cy + 30 * s), (cx, cy + 70 * s)]
    d.polygon([pts[0], pts[1], pts[3]], fill=(80, 170, 230))
    d.polygon([pts[0], pts[2], pts[3]], fill=(40, 110, 190))
    d.polygon([pts[0], pts[1], pts[2]], fill=(140, 210, 250))


def pl_heya():
    """今の部屋（茶番）。机に文化祭の出し物の紙（色の四角と線）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([240, 560, 440, 640], fill=(252, 252, 248), outline=(170, 160, 140), width=2)
    d.rectangle([256, 572, 300, 610], fill=(240, 160, 60))
    _lines(d, 312, 580, 420, 3, gap=16, w=4)
    return img


def pl_keiyaku():
    """机の上（上から）。契約書の束と、銀色の円盤（CD の形。文字・ラベルは描かない）。"""
    img = vgrad((W, H), (150, 120, 90), (120, 92, 66))
    d = _d(img)
    for k in range(3):
        x = 200 + k * 30
        d.rectangle([x, 180 - k * 10, x + 640, 900 - k * 10], fill=(252, 252, 248), outline=(170, 160, 140), width=3)
    _lines(d, 280, 260, 760, 14, gap=44, w=6)
    for k, (cx, cy) in enumerate(((1250, 420), (1450, 640))):
        d.ellipse([cx - 220, cy - 220, cx + 220, cy + 220], fill=(210, 216, 226), outline=(160, 166, 176), width=4)
        d.ellipse([cx - 160, cy - 160, cx + 160, cy + 160], outline=(230, 200, 230), width=6)
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(120, 92, 66))
    return img


def pl_kaihatsu(sanji=False):
    """開発室。机の列にブラウン管とワークステーション、壁に配線の図。sanji は画面に色の三角形の立体。"""
    img = _rgb(base((214, 216, 214), (196, 198, 196)))
    wood_floor(img, FLOOR, col=(130, 130, 136), line=(116, 116, 122))
    d = _d(img)
    d.rectangle([100, 100, 700, 360], fill=(250, 250, 246), outline=(150, 150, 150), width=3)
    for k in range(6):
        d.line([(140, 140 + k * 36), (660 - (k % 3) * 80, 140 + k * 36)], fill=(80, 120, 170), width=4)
    for k in range(4):
        x = 160 + k * 430
        d.rectangle([x - 40, 640, x + 340, 680], fill=(150, 120, 90))
        _crt(d, x, 420, 280, 210, screen=(20, 30, 50))
        if sanji:
            _tri3d(d, x + 140, 510, 0.9)
        else:
            for j in range(4):
                d.line([(x + 40, 460 + j * 30), (x + 220, 460 + j * 30)], fill=(80, 220, 120), width=4)
        d.rectangle([x + 300, 520, x + 360, 640], fill=(70, 74, 84))
    return img


def pl_soft():
    """ゲーム会社の会議室。机の上の試作機（灰色の箱、ロゴなし）と、大きな画面に色の三角形の立体。"""
    img = kaigi()
    d = _d(img)
    d.rectangle([600, 110, 1320, 420], fill=(20, 26, 44), outline=(100, 104, 110), width=8)
    _tri3d(d, 960, 260, 1.4)
    d.rounded_rectangle([860, 520, 1060, 560], radius=8, fill=(170, 172, 178), outline=(120, 122, 128), width=3)
    return img


def pl_cd():
    """CD を作る工場。銀色の円盤が棒に積み重なり、プレスの機械が並ぶ。"""
    img = _rgb(base((226, 228, 232), (206, 208, 212)))
    wood_floor(img, FLOOR, col=(170, 172, 178), line=(156, 158, 164))
    d = _d(img)
    for k in range(3):
        x = 160 + k * 600
        d.rectangle([x, 300, x + 360, 700], fill=(190, 194, 202), outline=(140, 144, 152), width=6)
        d.rectangle([x + 40, 340, x + 160, 440], fill=(40, 60, 90))
    for k in range(9):
        x = 120 + k * 200
        for j in range(14):
            d.ellipse([x, 900 - j * 12, x + 140, 930 - j * 12], fill=(214, 220, 230), outline=(170, 176, 186), width=2)
        d.line([(x + 70, 900), (x + 70, 700)], fill=(120, 120, 126), width=6)
    return img


def pl_mise(yoru=False):
    """ゲームの店の前（看板は色の帯だけで文字なし）、店の前に長い人の列。yoru は夜（店の明かりと街灯）。"""
    if yoru:
        img = vgrad((W, H), (20, 26, 50), (50, 56, 80))
    else:
        img = vgrad((W, H), (170, 200, 230), (226, 232, 238))
    d = _d(img)
    d.rectangle([300, 200, 1620, 800], fill=(90, 90, 100) if yoru else (220, 216, 206), outline=(150, 146, 140), width=6)
    d.rectangle([300, 200, 1620, 300], fill=(40, 60, 140))
    for k in range(5):
        d.rectangle([340 + k * 250, 230, 520 + k * 250, 270], fill=[(220, 60, 60), (60, 160, 90), (240, 190, 50), (80, 130, 220), (220, 60, 60)][k])
    d.rectangle([380, 380, 1540, 720], fill=(250, 230, 160) if yoru else (180, 210, 230))
    d.rectangle([0, 800, W, H], fill=(60, 62, 70) if yoru else (186, 184, 178))
    _person_line(d, 20, 1060, 27, 1.0)
    return img


LOCATIONS = {
    # プレイステーションの誕生
    "pl_heya": pl_heya, "pl_kenkyujo": kenkyujo, "pl_osetsu": tj_osetsu, "pl_keiyaku": pl_keiyaku,
    "pl_tenjikai": tenjikai, "pl_kaigi": yakuinkai, "pl_music": jimusho90, "pl_kaihatsu": pl_kaihatsu,
    "pl_kaihatsu_3d": lambda: pl_kaihatsu(sanji=True), "pl_soft": pl_soft, "pl_cd": pl_cd,
    "pl_mise": pl_mise, "pl_mise_yoru": lambda: pl_mise(yoru=True), "pl_happyo": tj_kaiken,
    "pl_shinbun": tj_shinbun, "pl_gendai": _sega_gendai,
    # ロッテのお家騒動
    "lt_heya": lt_heya, "lt_yamiichi": yamiichi, "lt_kojo": lt_kojo, "lt_seoul": lt_seoul,
    "lt_kaichoshitsu": kaichoshitsu, "lt_kaigi": lt_kaigi, "lt_honsha": ld_tower,
    "lt_honsha_press": lambda: ld_tower(yoake=True), "lt_torishimari": mt_torishimari,
    "lt_torishimari_kara": lt_torishimari_kara, "lt_jet": lt_jet, "lt_kuko": kuko_lobby, "lt_kaiken": tj_kaiken,
    "lt_sokai": kabunushi_kaijo, "lt_kokkai": kokkai, "lt_houtei": _sogo_saibansho, "lt_byoin": lt_byoin,
    "lt_shinbun": tj_shinbun, "lt_gendai": _sega_gendai,
    # 林原の破綻
    "hy_heya": hy_heya, "hy_kojo": hy_kojo, "hy_kenkyujo": kenkyujo, "hy_shachoshitsu": shachoshitsu,
    "hy_ekimae": hy_ekimae, "hy_ekimae_kouji": lambda: hy_ekimae(kouji=True), "hy_gobi": hy_gobi,
    "hy_osetsu": tj_osetsu, "hy_kessan": hy_kessan, "hy_kessan_chigau": lambda: hy_kessan(chigau=True),
    "hy_studio": hy_studio, "hy_kaigi": kaigi, "hy_kaigi_yasumi": hy_kaigi_yasumi, "hy_honsha_yoru": hy_honsha_yoru,
    "hy_kaiken": _sega_kaiken, "hy_shinbun": tj_shinbun, "hy_gendai": _sega_gendai,
    # 日本振興銀行の破綻
    "nb_heya": nb_heya, "nb_kinyucho": shingikai, "nb_reikai": kokaido, "nb_kaiken": _sega_kaiken,
    "nb_madoguchi": nb_madoguchi, "nb_madoguchi_retsu": lambda: nb_madoguchi(retsu=True),
    "nb_kaigi": kaigi, "nb_kaigi_akaji": nb_kaigi_akaji, "nb_rouka": nb_rouka, "nb_rouka_kara": lambda: nb_rouka(kara=True),
    "nb_server": nb_server, "nb_server_kara": lambda: nb_server(kara=True), "nb_honten": nb_honten,
    "nb_honten_yoake": lambda: nb_honten(yoake=True), "nb_shutter": nb_shutter,
    "nb_soukai": kabunushi_kaijo, "nb_keisatsu": ld_kanmae, "nb_houtei": _sogo_saibansho,
    "nb_saibansho_mae": saibansho_mae, "nb_shinbun": tj_shinbun, "nb_gendai": _sega_gendai,
}

# 年号カード。接頭辞ごとに "nb_card_2010" のように作る（台帳を見て足す）
CARDS = {"pl": ["1975", "1987", "1988", "1991", "1992", "1993", "1994", "1995", "2026"],
         "lt": ["1941", "1948", "1967", "2009", "2014", "2015", "2017", "2018", "2020", "2026"],
         "hy": ["1961", "1970", "1984", "1993", "2002", "2009", "2010", "2011", "2012", "2020", "2026"],
         "nb": ["2002", "2003", "2004", "2005", "2008", "2009", "2010", "2012", "2016", "2026"]}


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
