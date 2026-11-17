#!/usr/bin/env python3
"""第11弾4本（2026-12-06〜09。方向転換の実験の20〜23本目：会社の転落・破綻・裁判）の背景を生成する。

接頭辞: mt_（三越事件）/ mh_（ミートホープの偽装）/ ag_（安愚楽牧場の破綻）/ dw_（大和銀行ニューヨーク支店事件）
方針は gen_now10_bgs.py と同じ。実在の会社のロゴ・社名の文字・店の意匠・商品のパッケージは描かない。
実在の人の写真や肖像は描かない（壁の写真は人の形だけ）。差し替え用は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now11_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_aj_bgs import kitchen_now  # noqa: E402
from scripts.gen_ck_bgs import insatsu  # noqa: E402
from scripts.gen_dai_bgs import ima_super  # noqa: E402
from scripts.gen_drama_bgs import H, OUT, W, base, tatami_floor, vgrad, wood_floor  # noqa: E402
from scripts.gen_nd_bgs import hyoushou  # noqa: E402
from scripts.gen_famicom_bgs import shachoshitsu, year_card  # noqa: E402
from scripts.gen_led_bgs import bengoshi, saibansho_mae  # noqa: E402
from scripts.gen_now2_bgs import heya2  # noqa: E402
from scripts.gen_now3_bgs import jimusho90  # noqa: E402
from scripts.gen_gz_bgs import eigakan, juyakushitsu  # noqa: E402
from scripts.gen_ka_bgs import showa_office  # noqa: E402
from scripts.gen_now8_bgs import ld_kanmae, tj_kaiken, tj_osetsu, tj_shinbun  # noqa: E402
from scripts.gen_now9_bgs import _light, _press  # noqa: E402
from scripts.gen_sogo_bgs import uriba  # noqa: E402
from scripts.gen_shirota_bgs import genkan  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _d, _rgb, kaigi  # noqa: E402
from scripts.gen_pn_bgs import kokaido  # noqa: E402
from scripts.gen_sega_bgs import _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_shirota_bgs import michi  # noqa: E402
from scripts.gen_sogo_bgs import saibansho as _sogo_saibansho  # noqa: E402
from scripts.gen_fujifilm_bgs import kaigai_office  # noqa: E402
from scripts.gen_ms_bgs import court  # noqa: E402
from scripts.gen_now8_bgs import mx_kinko, mx_ryuchijo  # noqa: E402
from scripts.gen_now_bgs import yakuin  # noqa: E402

GRASS = (120, 170, 80)


def _mountains(d, y, col=(110, 140, 170)):
    """遠くの山並み。"""
    pts = [(0, y)]
    rnd = random.Random(7)
    x = 0
    while x < W:
        x += rnd.randint(140, 260)
        pts.append((x, y - rnd.randint(60, 200)))
    pts += [(W, y), (W, y + 40), (0, y + 40)]
    d.polygon(pts, fill=col)


def _fence(d, y, col=(200, 186, 160)):
    """牧場の木の柵。"""
    for x in range(0, W + 1, 160):
        d.rectangle([x, y - 90, x + 14, y + 10], fill=col)
    d.rectangle([0, y - 76, W, y - 64], fill=col)
    d.rectangle([0, y - 36, W, y - 24], fill=col)


def _ushi(d, x, y, s=1.0, left=False, tag=True):
    """黒毛の牛（横向き）。x, y は胴の左下。tag は耳の黄色い札。"""
    k = -1 if left else 1
    bx0, bx1 = (x, x + 260 * s)
    d.rounded_rectangle([bx0, y - 130 * s, bx1, y], radius=int(50 * s), fill=(36, 30, 30))
    for lx in (bx0 + 30 * s, bx0 + 70 * s, bx1 - 70 * s, bx1 - 30 * s):
        d.rectangle([lx - 10 * s, y - 10 * s, lx + 10 * s, y + 70 * s], fill=(30, 26, 26))
    hx = bx1 + 30 * s if not left else bx0 - 30 * s
    d.ellipse([hx - 50 * s, y - 160 * s, hx + 50 * s, y - 70 * s], fill=(40, 34, 34))
    d.ellipse([hx + k * 20 * s - 26 * s, y - 110 * s, hx + k * 20 * s + 26 * s, y - 70 * s], fill=(70, 56, 56))
    ex = hx - k * 40 * s
    d.polygon([(ex, y - 150 * s), (ex - k * 40 * s, y - 160 * s), (ex - k * 10 * s, y - 130 * s)], fill=(40, 34, 34))
    if tag:
        d.rectangle([ex - k * 34 * s - 9 * s, y - 150 * s, ex - k * 34 * s + 9 * s, y - 130 * s], fill=(240, 200, 40))
    tx = bx0 if not left else bx1
    d.line([(tx, y - 110 * s), (tx - k * 30 * s, y - 40 * s)], fill=(30, 26, 26), width=int(6 * s))


# ---------------------------------------------------------------- 安愚楽牧場の破綻
def ag_heya():
    """今の部屋。机にカードのケース（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.rounded_rectangle([250, 570, 430, 640], radius=8, fill=(60, 90, 160), outline=(30, 50, 100), width=3)
    for k in range(4):
        d.rectangle([266 + k * 40, 584, 296 + k * 40, 626], fill=(240, 220, 120), outline=(160, 130, 40), width=2)
    return img


def ag_bokujo(kara=False):
    """那須の牧草地。遠くの山、木の柵、黒毛の牛。看板は文字なし。kara は牛が1頭もいない。"""
    img = vgrad((W, H), (150, 196, 236), (220, 232, 240))
    d = _d(img)
    _mountains(d, 470)
    d.rectangle([0, 500, W, H], fill=GRASS)
    for k in range(5):
        d.ellipse([-200 + k * 460, 470, 400 + k * 460, 560], fill=(130, 180, 90))
    _fence(d, 640)
    d.rectangle([1500, 380, 1760, 520], fill=(250, 248, 240), outline=(150, 120, 80), width=6)
    d.rectangle([1530, 520, 1546, 640], fill=(150, 120, 80))
    d.rectangle([1714, 520, 1730, 640], fill=(150, 120, 80))
    if not kara:
        rnd = random.Random(3)
        for k in range(9):
            x = 60 + k * 205 + rnd.randint(-30, 30)
            y = 760 + (k % 3) * 90
            _ushi(d, x, y, 0.62 + (k % 3) * 0.08, left=bool(k % 2))
    return img


def ag_gyusha(kara=False):
    """牛舎の中。屋根のはりと鉄パイプの仕切り、並んだ牛の首に番号の札（文字は描かない）。kara は区画の半分が空。"""
    img = _rgb(base((200, 196, 186), (176, 170, 160)))
    d = _d(img)
    for k in range(7):
        x = k * 320
        d.polygon([(x, 0), (x + 320, 0), (x + 160, 120)], outline=(120, 100, 80), fill=None)
        d.line([(x, 0), (x + 160, 120), (x + 320, 0)], fill=(120, 100, 80), width=10)
    d.rectangle([0, 120, W, 140], fill=(120, 100, 80))
    d.rectangle([0, 760, W, H], fill=(150, 130, 100))
    rnd = random.Random(5)
    for k in range(8):
        x = 40 + k * 235
        d.rectangle([x, 300, x + 12, 820], fill=(160, 164, 170))
        if kara and k % 2 == 1:
            d.rectangle([x + 40, 700, x + 200, 760], fill=(220, 200, 120))  # 空の区画の敷きわら
            continue
        d.ellipse([x + 50, 420, x + 190, 560], fill=(38, 32, 32))
        d.ellipse([x + 80, 500, x + 160, 570], fill=(70, 56, 56))
        d.polygon([(x + 50, 440), (x + 10, 430), (x + 56, 470)], fill=(38, 32, 32))
        d.polygon([(x + 190, 440), (x + 230, 430), (x + 184, 470)], fill=(38, 32, 32))
        d.rectangle([x + 16, 440, x + 34, 462], fill=(240, 200, 40))
        d.rounded_rectangle([x + 70, 580, x + 170, 640], radius=8, fill=(250, 250, 246), outline=(120, 120, 120), width=3)
        for j in range(2):
            d.line([(x + 84, 598 + j * 22), (x + 156, 598 + j * 22)], fill=(80, 80, 80), width=5)
        if rnd.random() < 0.3:
            d.rectangle([x + 40, 700, x + 200, 760], fill=(220, 200, 120))
    d.rectangle([0, 560, W, 576], fill=(170, 174, 180))
    return img


def ag_pamph(chirashi=False):
    """机の上（上から見た）。開いたパンフレット：牛の絵と牧場の写真の枠、白い文字の枠（文字は描かない）。
    chirashi は新しい募集のチラシの束（牛の形と、値段の帯が赤い）。"""
    img = vgrad((W, H), (150, 120, 90), (120, 92, 66))
    d = _d(img)
    if chirashi:
        rnd = random.Random(9)
        for k in range(14):
            x, y = rnd.randint(140, 1380), rnd.randint(80, 640)
            d.rectangle([x, y, x + 420, y + 300], fill=(252, 250, 244), outline=(170, 160, 140), width=3)
            d.rectangle([x + 20, y + 20, x + 400, y + 70], fill=(60, 120, 60))
            d.ellipse([x + 40, y + 110, x + 180, y + 200], fill=(40, 34, 34))
            d.rectangle([x + 220, y + 120, x + 390, y + 170], fill=(220, 50, 50))
            for j in range(3):
                d.line([(x + 220, y + 200 + j * 26), (x + 380, y + 200 + j * 26)], fill=(120, 120, 120), width=5)
        return img
    d.rectangle([300, 140, 1620, 940], fill=(252, 250, 244), outline=(170, 160, 140), width=4)
    d.line([(960, 140), (960, 940)], fill=(200, 192, 180), width=4)
    d.rectangle([340, 180, 920, 520], fill=(150, 200, 120))
    d.ellipse([360, 380, 900, 560], fill=(130, 180, 90))
    _ushi(d, 470, 470, 0.9, tag=True)
    for j in range(6):
        d.line([(360, 600 + j * 50), (900 - (j % 2) * 120, 600 + j * 50)], fill=(120, 120, 120), width=6)
    for blk in range(3):
        y0 = 200 + blk * 240
        d.rounded_rectangle([1000, y0, 1580, y0 + 200], radius=14, fill=(240, 246, 236), outline=(90, 150, 90), width=4)
        d.ellipse([1020, y0 + 20, 1080, y0 + 80], fill=(60, 140, 70))
        for j in range(3):
            d.line([(1100, y0 + 50 + j * 44), (1550 - j * 60, y0 + 50 + j * 44)], fill=(110, 110, 110), width=6)
    return img


def ag_ishigaki():
    """石垣島の海辺の牧場。青い海と白い砂、低い木、牧草地に牛が数頭。"""
    img = vgrad((W, H), (90, 170, 236), (200, 230, 246))
    d = _d(img)
    d.rectangle([0, 420, W, 560], fill=(40, 150, 200))
    d.rectangle([0, 440, W, 470], fill=(80, 190, 220))
    d.rectangle([0, 560, W, 620], fill=(240, 232, 200))
    d.rectangle([0, 620, W, H], fill=(110, 170, 80))
    for x in (180, 520, 1500, 1800):
        d.rectangle([x - 10, 460, x + 10, 640], fill=(110, 80, 50))
        d.ellipse([x - 110, 380, x + 110, 500], fill=(50, 120, 60))
    _fence(d, 760)
    for k, x in enumerate((360, 900, 1300)):
        _ushi(d, x, 900 + (k % 2) * 60, 0.7, left=bool(k % 2))
    return img


def ag_miyazaki():
    """宮崎の農場（2010年）。牛舎の外、白い消毒の霧と、白い防護服の人の形。笑いにしない静かな画。"""
    img = vgrad((W, H), (190, 200, 210), (226, 228, 230))
    d = _d(img)
    d.rectangle([200, 260, 1720, 700], fill=(170, 160, 150), outline=(120, 110, 100), width=6)
    d.polygon([(160, 280), (960, 120), (1760, 280)], fill=(110, 110, 120))
    for k in range(6):
        d.rectangle([300 + k * 240, 420, 440 + k * 240, 700], fill=(90, 80, 74))
    d.rectangle([0, 700, W, H], fill=(196, 196, 190))
    for k in range(40):
        rnd = random.Random(k)
        x, y = rnd.randint(0, W), rnd.randint(600, 980)
        d.ellipse([x - 120, y - 40, x + 120, y + 40], fill=(255, 255, 255, 70))
    _person_line(d, 120, 1020, 5, 1.0, cols=[(240, 240, 242)])
    _person_line(d, 1400, 1020, 5, 1.0, cols=[(240, 240, 242)])
    return img


def ag_shiten(retsu=False):
    """都心の事務所のビルの前（東京支店）。ガラスの入口、名前の板は文字なし。retsu は前に集まった人の列（後ろ姿）。"""
    img = vgrad((W, H), (170, 196, 222), (220, 226, 232))
    d = _d(img)
    d.rectangle([360, 60, 1560, 820], fill=(200, 196, 188), outline=(150, 146, 138), width=6)
    for r in range(6):
        for c in range(9):
            d.rectangle([420 + c * 124, 100 + r * 100, 500 + c * 124, 170 + r * 100], fill=(140, 170, 196))
    d.rectangle([800, 680, 1120, 820], fill=(100, 130, 150), outline=(80, 90, 100), width=6)
    d.line([(960, 680), (960, 820)], fill=(80, 90, 100), width=6)
    d.rectangle([1160, 700, 1300, 760], fill=(230, 226, 214), outline=(150, 146, 138), width=3)
    d.rectangle([0, 820, W, H], fill=(186, 184, 178))
    if retsu:
        _person_line(d, 60, 1040, 25, 1.05)
    return img


def ag_kokugikan_soto():
    """雨の両国国技館の外。大きな屋根の建物（文字・のぼりの文字は描かない）、傘の列、雨の筋。"""
    img = vgrad((W, H), (120, 126, 136), (176, 180, 186))
    d = _d(img)
    d.rectangle([300, 360, 1620, 760], fill=(186, 180, 170), outline=(130, 126, 120), width=6)
    d.polygon([(220, 380), (960, 120), (1700, 380)], fill=(70, 120, 110))
    d.polygon([(420, 300), (960, 170), (1500, 300)], fill=(60, 104, 96))
    for k in range(5):
        d.rectangle([620 + k * 150, 600, 720 + k * 150, 760], fill=(90, 90, 96))
    d.rectangle([0, 760, W, H], fill=(120, 124, 128))
    rnd = random.Random(19)
    for k in range(26):
        x = 40 + k * 72
        y = 940 + rnd.randint(-20, 20)
        col = [(40, 60, 120), (30, 30, 34), (120, 40, 50), (60, 90, 60), (200, 200, 206)][k % 5]
        d.rectangle([x + 16, y - 40, x + 50, y + 100], fill=(60, 60, 66))
        d.pieslice([x - 20, y - 90, x + 86, y + 10], 180, 360, fill=col)
    for k in range(240):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        d.line([(x, y), (x - 8, y + 40)], fill=(220, 226, 236, 120), width=2)
    return img


def ag_kokugikan():
    """国技館の中。上に吊り屋根と四色の房、中央に土俵、その前に白い布の長机。まわりの客席は人の形でいっぱい。"""
    img = _rgb(base((70, 60, 56), (110, 96, 86)))
    d = _d(img)
    for r in range(6):
        y = 300 + r * 70
        d.rectangle([0, y, W, y + 60], fill=(120 - r * 6, 50, 50))
        for k in range(40):
            x = k * 50 + (r % 2) * 25
            d.ellipse([x, y - 10, x + 30, y + 20], fill=(40, 34, 30))
            d.rounded_rectangle([x - 6, y + 18, x + 36, y + 56], radius=8, fill=[(70, 74, 90), (90, 70, 66), (60, 84, 70), (100, 96, 86)][(k + r) % 4])
    d.polygon([(640, 120), (1280, 120), (1360, 200), (560, 200)], fill=(60, 50, 44))
    d.rectangle([600, 40, 1320, 120], fill=(90, 70, 50))
    for x, col in ((600, (40, 40, 140)), (1320, (200, 40, 40)), (640, (40, 120, 60)), (1280, (240, 240, 240))):
        d.ellipse([x - 26, 200, x + 26, 280], fill=col)
    d.polygon([(560, 820), (1360, 820), (1500, 1000), (420, 1000)], fill=(200, 176, 120))
    d.ellipse([700, 840, 1220, 980], outline=(240, 236, 220), width=10)
    d.rectangle([560, 740, 1360, 820], fill=(250, 250, 250), outline=(200, 200, 200), width=4)
    for k in range(5):
        d.rectangle([640 + k * 150, 700, 690 + k * 150, 740], fill=(40, 40, 44))
    return img


# ---------------------------------------------------------------- 三越事件
def _boxes(d, x0, x1, floor, rows, seed=1, gap=0.1, col=(196, 160, 110)):
    """段ボールの山。"""
    rnd = random.Random(seed)
    w = 180
    for r in range(rows):
        for c in range(int((x1 - x0) / (w + 10))):
            if rnd.random() < gap:
                continue
            x, y = x0 + c * (w + 10) + (r % 2) * 20, floor - (r + 1) * 126
            d.rectangle([x, y, x + w, y + 118], fill=col, outline=(140, 110, 70), width=3)
            d.line([(x, y + 30), (x + w, y + 30)], fill=(170, 136, 90), width=3)


def mt_heya():
    """今の教室の後ろ（茶番）。黒板に投票の正の字（線だけ）、ロッカー。"""
    img = _rgb(base((236, 232, 220), (222, 218, 206)))
    wood_floor(img, FLOOR, col=(190, 160, 120), line=(170, 140, 100))
    d = _d(img)
    d.rectangle([360, 120, 1560, 520], fill=(40, 80, 60), outline=(150, 120, 80), width=14)
    for g in range(3):
        x0 = 460 + g * 360
        d.line([(x0, 200), (x0 + 200, 200)], fill=(240, 240, 236), width=6)
        for k in range(5):
            d.line([(x0 + 20 + k * 40, 240), (x0 + 20 + k * 40, 330 + (k % 2) * 40)], fill=(240, 240, 236), width=6)
    for k in range(8):
        d.rectangle([40 + k * 230, 600, 250 + k * 230, 760], fill=(180, 186, 190), outline=(130, 136, 140), width=3)
    return img


def mt_honten():
    """石造りの大きな百貨店の外観（架空。像・のれん・文字は描かない）。柱の並ぶ正面と、旗の竿だけ。"""
    img = vgrad((W, H), (170, 200, 230), (226, 232, 238))
    d = _d(img)
    d.rectangle([180, 160, 1740, 820], fill=(214, 206, 188), outline=(160, 150, 130), width=6)
    d.rectangle([180, 120, 1740, 170], fill=(196, 188, 170))
    for r in range(3):
        for c in range(12):
            d.rectangle([240 + c * 124, 210 + r * 120, 320 + c * 124, 300 + r * 120], fill=(150, 170, 186))
    for c in range(9):
        x = 300 + c * 160
        d.rectangle([x, 580, x + 40, 820], fill=(226, 220, 204), outline=(170, 160, 140), width=3)
    d.rectangle([760, 640, 1160, 820], fill=(120, 110, 96))
    d.rectangle([0, 820, W, H], fill=(176, 172, 164))
    _person_line(d, 60, 1060, 10, 0.9)
    _person_line(d, 1200, 1060, 9, 0.9)
    return img


def mt_uriba_hako():
    """百貨店の売り場の通路まで、倉庫から出した箱があふれる（差し替え用）。"""
    img = uriba()
    d = _d(img)
    _boxes(d, 0, W, H - 40, 2, seed=11, gap=0.25)
    return img


def mt_soko():
    """倉庫の中。天井近くまで積まれた段ボールの山と、鉄の棚。"""
    img = _rgb(base((190, 188, 182), (170, 168, 162)))
    wood_floor(img, FLOOR, col=(150, 146, 140), line=(134, 130, 124))
    d = _d(img)
    for x in (40, 1000):
        for k in range(4):
            d.rectangle([x, 160 + k * 200, x + 880, 172 + k * 200], fill=(120, 130, 140))
        d.rectangle([x, 160, x + 14, FLOOR], fill=(120, 130, 140))
        d.rectangle([x + 866, 160, x + 880, FLOOR], fill=(120, 130, 140))
    for k in range(4):
        _boxes(d, 60, 900, 360 + k * 200, 1, seed=k, gap=0.15)
        _boxes(d, 1020, 1860, 360 + k * 200, 1, seed=k + 9, gap=0.15)
    return img


def mt_denpyo():
    """机の上（上から）。複写の伝票の束が何山も。数字の欄は線だけ。"""
    img = vgrad((W, H), (150, 120, 90), (120, 92, 66))
    d = _d(img)
    for k in range(6):
        x, y = 160 + (k % 3) * 560, 160 + (k // 3) * 420
        for j in range(8):
            d.rectangle([x + j * 3, y - j * 6, x + 440 + j * 3, y + 300 - j * 6], fill=(250, 248, 236) if j % 2 else (236, 236, 250),
                        outline=(170, 160, 140), width=2)
        d.rectangle([x + 21, y - 42, x + 461, y - 12], fill=(200, 60, 60))
        for r in range(6):
            d.line([(x + 40, y + 20 + r * 40), (x + 440, y + 20 + r * 40)], fill=(150, 150, 150), width=3)
        d.line([(x + 300, y - 12), (x + 300, y + 250)], fill=(150, 150, 150), width=3)
    return img


def mt_uchiawase():
    """打ち合わせの部屋（和室）。障子と襖、中央に長い座卓、座布団、卓の上に書類と湯のみ。花・掛け軸・仏具は描かない。"""
    img = _rgb(base((226, 214, 190), (212, 200, 176)))
    tatami_floor(img, FLOOR)
    d = _d(img)
    for k in range(6):
        x = 40 + k * 310
        d.rectangle([x, 80, x + 290, FLOOR - 10], fill=(244, 240, 228) if k % 3 else (200, 184, 150), outline=(140, 110, 80), width=8)
        if k % 3:
            for r in range(1, 5):
                d.line([(x, 80 + r * 120), (x + 290, 80 + r * 120)], fill=(170, 150, 120), width=3)
            d.line([(x + 145, 80), (x + 145, FLOOR - 10)], fill=(170, 150, 120), width=3)
    d.rectangle([0, 60, W, 84], fill=(130, 100, 70))
    d.rectangle([420, 800, 1500, 860], fill=(110, 66, 40), outline=(80, 46, 30), width=5)
    d.rectangle([460, 860, 500, 960], fill=(90, 54, 34))
    d.rectangle([1420, 860, 1460, 960], fill=(90, 54, 34))
    for x in (560, 820, 1080, 1340):
        d.rectangle([x - 80, 770, x + 20, 800], fill=(250, 248, 236), outline=(170, 160, 140), width=2)
        d.ellipse([x + 40, 760, x + 80, 800], fill=(110, 140, 110))
    for x in (330, 1590):
        d.rounded_rectangle([x - 90, 950, x + 90, 1000], radius=14, fill=(150, 50, 60))
    return img


def mt_osetsu_ken():
    """取引先の応接室の机に、映画の前売券の束が積み上がる（券は色の帯だけで文字なし）。"""
    img = tj_osetsu()
    d = _d(img)
    for k in range(7):
        x, y = 640 + (k % 4) * 150, 520 - (k // 4) * 70
        for j in range(5):
            d.rectangle([x, y - j * 12, x + 130, y + 56 - j * 12], fill=(240, 220, 120), outline=(160, 130, 40), width=2)
            d.rectangle([x, y - j * 12, x + 30, y + 56 - j * 12], fill=(200, 60, 60))
    return img


def mt_hihoten():
    """展覧会の展示室。暗い壁にスポットライト、ガラスケースに壺・水さし・器（文字のパネルは無地）。"""
    img = _rgb(base((50, 46, 52), (70, 64, 70)))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(90, 80, 76))
    for k in range(4):
        x = 160 + k * 430
        d.rectangle([x, 380, x + 300, 760], fill=(110, 100, 96))
        d.rectangle([x - 10, 200, x + 310, 380], fill=(200, 220, 230, 60), outline=(220, 230, 236), width=4)
        vcol = [(170, 130, 70), (110, 140, 120), (150, 110, 80), (190, 170, 110)][k]
        d.ellipse([x + 90, 240, x + 210, 370], fill=vcol)
        d.rectangle([x + 125, 210, x + 175, 250], fill=vcol)
        d.rectangle([x + 60, 300, x + 90, 316], fill=vcol)
        d.rectangle([x + 40, 680, x + 260, 720], fill=(230, 226, 214))
    img = _light(img, [[(x + 150, 0), (x - 20, 380), (x + 320, 380)] for x in (160, 590, 1020, 1450)], (255, 240, 200), 50, 12)
    return img


def mt_torishimari(state="futsu"):
    """取締役会の部屋。木の壁、長い机と役員の椅子、右の端に議長の大きな椅子。
    kiritsu は机の向こうに起立した役員の影が並ぶ。kara は誰もいず、議長の椅子が引かれたまま。"""
    img = _rgb(base((150, 112, 80), (126, 92, 64)))
    wood_floor(img, FLOOR, col=(90, 60, 50), line=(76, 50, 40))
    d = _d(img)
    for k in range(9):
        d.rectangle([k * 220, 60, k * 220 + 200, 480], outline=(110, 80, 56), width=6)
    d.rectangle([840, 110, 1080, 300], fill=(200, 190, 160), outline=(170, 140, 80), width=10)
    for k in range(8):
        x = 160 + k * 170
        d.rounded_rectangle([x, 420, x + 110, 600], radius=14, fill=(70, 40, 36))
    cx = 1660 if state == "kara" else 1560  # kara は議長の椅子が引かれたまま
    d.rounded_rectangle([cx, 360, cx + 170, 600], radius=18, fill=(90, 30, 30), outline=(200, 170, 90), width=6)
    if state == "kiritsu":
        cols = [(40, 40, 50), (50, 46, 52), (36, 40, 48)]
        for k in range(8):
            x = 170 + k * 170
            d.ellipse([x + 20, 250, x + 90, 320], fill=(30, 26, 26))
            d.rounded_rectangle([x, 320, x + 110, 520], radius=20, fill=cols[k % 3])
    d.rectangle([100, 560, 1780, 660], fill=(110, 66, 40), outline=(80, 46, 30), width=6)
    for k in range(9):
        d.rectangle([180 + k * 170, 576, 260 + k * 170, 600], fill=(246, 244, 236))
    return img


MEAT = [(196, 70, 80), (220, 110, 120), (180, 60, 70), (230, 150, 150)]


def _mincer(d, x, y, s=1.0, nuno=False):
    """挽肉機（ステンレスの箱、上にじょうご、前に出口）。x, y は台に置いた下の左。nuno は白い布がかかる。"""
    if nuno:
        d.polygon([(x - 20 * s, y), (x + 20 * s, y - 300 * s), (x + 260 * s, y - 320 * s), (x + 300 * s, y)], fill=(244, 244, 240))
        return
    d.rectangle([x, y - 200 * s, x + 260 * s, y], fill=(196, 200, 206), outline=(140, 144, 150), width=int(4 * s))
    d.polygon([(x + 60 * s, y - 200 * s), (x + 20 * s, y - 300 * s), (x + 240 * s, y - 300 * s), (x + 200 * s, y - 200 * s)],
              fill=(210, 214, 220), outline=(140, 144, 150))
    d.ellipse([x + 230 * s, y - 150 * s, x + 310 * s, y - 70 * s], fill=(170, 174, 180), outline=(120, 124, 130), width=int(4 * s))


def _crate(d, x, y, s=1.0, meat=True):
    """青いプラスチックのコンテナ。meat は肉の塊が入っている。"""
    d.rectangle([x, y - 90 * s, x + 200 * s, y], fill=(60, 110, 180), outline=(40, 80, 140), width=3)
    if meat:
        for k in range(5):
            d.ellipse([x + 10 * s + k * 36 * s, y - 120 * s, x + 60 * s + k * 36 * s, y - 80 * s], fill=MEAT[k % 4])


def mh_kojo(state="futsu"):
    """食肉の加工場。白いタイルの壁、ステンレスの台、挽肉機、肉の入った青いコンテナ。
    katazuke は台の上が片づいてコンテナが無い（検査の日）。nuno は機械と台に白い布がかかり、床に段ボール。"""
    img = _rgb(base((236, 240, 242), (220, 226, 230)))
    d = _d(img)
    for x in range(0, W, 80):
        d.line([(x, 0), (x, 620)], fill=(206, 212, 216), width=2)
    for y in range(0, 620, 80):
        d.line([(0, y), (W, y)], fill=(206, 212, 216), width=2)
    d.rectangle([0, 620, W, H], fill=(170, 180, 186))
    for x0 in (80, 1180):
        d.rectangle([x0, 600, x0 + 660, 640], fill=(200, 204, 210), outline=(150, 154, 160), width=4)
        for lx in (x0 + 20, x0 + 620):
            d.rectangle([lx, 640, lx + 20, 860], fill=(160, 164, 170))
    _mincer(d, 260, 600, 1.0, nuno=(state == "nuno"))
    _mincer(d, 1340, 600, 1.0, nuno=(state == "nuno"))
    if state == "futsu":
        for x in (100, 560, 1200, 1660):
            _crate(d, x, 600, 0.8)
        for k in range(4):
            _crate(d, 60 + k * 240, 1000, 1.0)
    elif state == "nuno":
        for x in (100, 560, 1200, 1660):
            d.polygon([(x - 10, 600), (x + 10, 520), (x + 170, 520), (x + 190, 600)], fill=(244, 244, 240))
        for k in range(5):
            d.rectangle([60 + k * 360, 880, 300 + k * 360, 1040], fill=(196, 160, 110), outline=(140, 110, 70), width=3)
    return img


def mh_hikiniku():
    """挽肉機のアップ。出口の穴の板から、細いひき肉が下のトレーに落ちる。"""
    img = _rgb(base((226, 230, 234), (200, 206, 210)))
    d = _d(img)
    d.rectangle([300, 120, 1300, 700], fill=(196, 200, 206), outline=(140, 144, 150), width=8)
    d.polygon([(500, 120), (380, -60), (1220, -60), (1100, 120)], fill=(210, 214, 220))
    d.ellipse([1180, 240, 1620, 680], fill=(176, 180, 186), outline=(120, 124, 130), width=10)
    for r in range(5):
        for c in range(5):
            d.ellipse([1240 + c * 70, 300 + r * 70, 1280 + c * 70, 340 + r * 70], fill=(90, 94, 100))
    rnd = random.Random(4)
    for k in range(60):
        x = 1240 + rnd.randint(0, 320)
        d.line([(x, 660), (x + rnd.randint(-20, 20), 900)], fill=MEAT[k % 4], width=12)
    d.rectangle([1100, 880, 1760, 980], fill=(250, 250, 250), outline=(180, 180, 180), width=4)
    d.ellipse([1160, 840, 1700, 940], fill=(210, 110, 120))
    d.rectangle([0, 980, W, H], fill=(170, 180, 186))
    return img


def mh_reito():
    """冷凍庫の中。霜の付いた壁と、白く凍った段ボールの山。"""
    img = _rgb(base((150, 170, 190), (120, 140, 160)))
    d = _d(img)
    rnd = random.Random(8)
    for c in range(9):
        for r in range(5):
            if rnd.random() < 0.15:
                continue
            x, y = 20 + c * 212, 960 - (r + 1) * 150
            d.rectangle([x, y, x + 200, y + 142], fill=(200, 180, 150), outline=(150, 130, 100), width=3)
            d.rectangle([x, y, x + 200, y + 20], fill=(236, 242, 248))
    for k in range(300):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        d.ellipse([x, y, x + 6, y + 6], fill=(240, 246, 252, 160))
    d.rectangle([0, 960, W, H], fill=(170, 186, 200))
    return img


def mh_pack():
    """事務所の机に並んだ牛ひき肉のトレー（ラップと白いシール、シールは赤い帯と線だけで文字なし）。"""
    img = vgrad((W, H), (150, 120, 90), (120, 92, 66))
    d = _d(img)
    for r in range(3):
        for c in range(4):
            x, y = 240 + c * 380, 140 + r * 300
            d.rounded_rectangle([x, y, x + 340, y + 240], radius=20, fill=(250, 250, 250), outline=(200, 200, 200), width=4)
            d.rounded_rectangle([x + 20, y + 20, x + 320, y + 220], radius=14, fill=(206, 100, 112))
            for k in range(30):
                rnd = random.Random(r * 10 + c * 100 + k)
                xx, yy = x + 30 + rnd.randint(0, 270), y + 30 + rnd.randint(0, 170)
                d.ellipse([xx, yy, xx + 14, yy + 10], fill=(236, 150, 160))
            d.rectangle([x + 180, y + 130, x + 320, y + 210], fill=(252, 252, 250), outline=(160, 160, 160), width=2)
            d.rectangle([x + 180, y + 130, x + 320, y + 152], fill=(210, 40, 40))
            for j in range(2):
                d.line([(x + 194, y + 172 + j * 20), (x + 304, y + 172 + j * 20)], fill=(90, 90, 90), width=4)
    return img


def mh_honsha(state="futsu"):
    """郊外の工場と事務所の建物（2階建て）。屋上に大きな牛の像（形だけ）。看板は文字なし。
    press は前に報道の車とカメラの列。nashi は屋上の像が無い。"""
    img = vgrad((W, H), (170, 200, 230), (226, 232, 238))
    d = _d(img)
    d.rectangle([200, 380, 1720, 780], fill=(230, 226, 216), outline=(160, 156, 146), width=6)
    for c in range(10):
        d.rectangle([260 + c * 144, 440, 360 + c * 144, 520], fill=(140, 170, 196))
    d.rectangle([260, 600, 1100, 780], fill=(196, 196, 190), outline=(150, 150, 146), width=4)
    for k in range(6):
        d.line([(260, 620 + k * 26), (1100, 620 + k * 26)], fill=(170, 170, 166), width=3)
    d.rectangle([1260, 640, 1460, 780], fill=(110, 130, 150), outline=(80, 90, 100), width=4)
    d.rectangle([1500, 560, 1700, 620], fill=(250, 250, 246), outline=(150, 146, 138), width=3)
    if state != "nashi":
        bx, by = 760, 380
        d.rounded_rectangle([bx, by - 150, bx + 340, by - 30], radius=50, fill=(150, 100, 70))
        for lx in (bx + 40, bx + 100, bx + 240, bx + 300):
            d.rectangle([lx - 14, by - 40, lx + 14, by], fill=(130, 86, 60))
        d.ellipse([bx + 300, by - 210, bx + 420, by - 110], fill=(160, 108, 76))
        d.polygon([(bx + 330, by - 200), (bx + 300, by - 240), (bx + 350, by - 206)], fill=(230, 220, 200))
        d.polygon([(bx + 390, by - 200), (bx + 420, by - 240), (bx + 370, by - 206)], fill=(230, 220, 200))
    d.rectangle([0, 780, W, H], fill=(176, 176, 170))
    if state == "press":
        for k in range(3):
            x = 120 + k * 560
            d.rounded_rectangle([x, 800, x + 360, 920], radius=24, fill=[(240, 240, 240), (60, 80, 120), (200, 40, 40)][k])
            d.rectangle([x + 60, 760, x + 300, 810], fill=(80, 90, 100))
            d.ellipse([x + 40, 890, x + 110, 960], fill=(30, 30, 34))
            d.ellipse([x + 250, 890, x + 320, 960], fill=(30, 30, 34))
        _press(d, 80, 1070, 10, 1.1)
        _press(d, 1100, 1070, 10, 1.1)
    return img


def mh_hiroma():
    """本社2階の広間での会見。白い壁と窓、白い布の長机とマイク、手前に記者とカメラ。"""
    img = _rgb(base((236, 232, 224), (220, 216, 208)))
    wood_floor(img, FLOOR, col=(170, 150, 120), line=(150, 130, 100))
    d = _d(img)
    for k in range(3):
        d.rectangle([260 + k * 520, 120, 560 + k * 520, 380], fill=(200, 220, 236), outline=(150, 140, 120), width=8)
    d.rectangle([420, 560, 1500, 660], fill=(250, 250, 250), outline=(200, 200, 200), width=4)
    for k in range(4):
        x = 560 + k * 260
        d.line([(x, 560), (x, 500)], fill=(40, 40, 44), width=6)
        d.ellipse([x - 14, 480, x + 14, 508], fill=(40, 40, 44))
    _press(d, 20, 1080, 8, 1.1)
    _press(d, 1340, 1080, 8, 1.1)
    return img


def mh_madoguchi():
    """役所の相談の窓口。長いカウンター、ガラスの仕切り、壁の張り紙（文字は描かない）、番号札の機械。"""
    img = _rgb(base((232, 234, 230), (214, 216, 210)))
    d = _d(img)
    for k in range(4):
        x = 200 + k * 380
        d.rectangle([x, 160, x + 260, 360], fill=(252, 252, 248), outline=(160, 160, 160), width=3)
        d.rectangle([x, 160, x + 260, 200], fill=[(60, 120, 180), (200, 60, 60), (60, 140, 90), (230, 160, 40)][k])
        for j in range(4):
            d.line([(x + 20, 230 + j * 30), (x + 240, 230 + j * 30)], fill=(120, 120, 120), width=4)
    d.rectangle([0, 600, W, 700], fill=(180, 160, 130), outline=(140, 120, 90), width=4)
    d.rectangle([0, 700, W, H], fill=(160, 164, 160))
    for k in range(5):
        d.rectangle([80 + k * 380, 440, 90 + k * 380, 600], fill=(170, 176, 180))
    d.rectangle([0, 440, W, 450], fill=(170, 176, 180))
    d.rectangle([1700, 560, 1800, 700], fill=(220, 220, 214), outline=(140, 140, 140), width=3)
    d.rectangle([1720, 580, 1780, 610], fill=(40, 60, 90))
    return img


def mh_heya():
    """今の台所。まな板とボウルに入ったひき肉（茶番）。"""
    img = kitchen_now()
    d = _d(img)
    d.rectangle([260, 640, 620, 700], fill=(230, 210, 170), outline=(170, 150, 110), width=3)
    d.ellipse([700, 600, 960, 700], fill=(240, 240, 240), outline=(180, 180, 180), width=4)
    d.ellipse([730, 610, 930, 660], fill=(210, 110, 120))
    d.ellipse([780, 620, 860, 650], fill=(240, 236, 220))
    return img


# ---------------------------------------------------------------- 大和銀行ニューヨーク支店事件
def dw_heya():
    """今の部屋。机に集金の封筒と小銭（茶番）。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([250, 580, 420, 640], fill=(250, 246, 236), outline=(170, 160, 140), width=3)
    d.line([(270, 600), (400, 600)], fill=(200, 60, 60), width=4)
    for k in range(5):
        d.ellipse([440 + k * 26, 616, 466 + k * 26, 640], fill=(200, 200, 206), outline=(140, 140, 146), width=2)
    return img


def dw_ny():
    """マンハッタンの通り。高いビルが並び、黄色いタクシーと街灯。看板の文字は描かない。"""
    img = vgrad((W, H), (150, 186, 226), (214, 224, 234))
    d = _d(img)
    rnd = random.Random(13)
    x = -40
    while x < W:
        w = rnd.randint(180, 300)
        top = rnd.randint(40, 320)
        col = rnd.choice([(150, 140, 130), (120, 120, 130), (170, 160, 146), (100, 110, 126)])
        d.rectangle([x, top, x + w, 820], fill=col)
        for r in range(top + 30, 800, 60):
            for c in range(x + 20, x + w - 30, 46):
                d.rectangle([c, r, c + 26, r + 34], fill=(200, 214, 230))
        x += w + 8
    d.rectangle([0, 820, W, H], fill=(110, 110, 116))
    d.rectangle([0, 900, W, 912], fill=(230, 230, 230))
    for k in range(2):
        x = 300 + k * 900
        d.rounded_rectangle([x, 880, x + 360, 990], radius=24, fill=(240, 200, 40))
        d.rectangle([x + 70, 840, x + 280, 890], fill=(220, 180, 30))
        d.ellipse([x + 40, 960, x + 110, 1030], fill=(30, 30, 34))
        d.ellipse([x + 250, 960, x + 320, 1030], fill=(30, 30, 34))
    return img


def dw_torihiki(soko=False):
    """取引室。机の列に画面と電話、壁に時計と相場の電光板（数字は線だけ）。
    soko は照明を消して段ボールを机の上まで積み、倉庫に見せかけた部屋（差し替え用）。"""
    if soko:
        img = _rgb(base((70, 70, 76), (54, 54, 60)))
    else:
        img = _rgb(base((220, 224, 228), (200, 206, 212)))
    wood_floor(img, FLOOR, col=(110, 110, 120) if not soko else (60, 60, 66), line=(96, 96, 104) if not soko else (50, 50, 56))
    d = _d(img)
    d.rectangle([200, 80, 1720, 260], fill=(30, 34, 40) if not soko else (24, 24, 28))
    if not soko:
        for r in range(3):
            for c in range(12):
                d.line([(240 + c * 122, 120 + r * 50), (320 + c * 122, 120 + r * 50)], fill=(80, 220, 120) if (r + c) % 3 else (230, 80, 60), width=6)
    for k in range(5):
        x = 80 + k * 370
        d.rectangle([x, 560, x + 320, 600], fill=(150, 120, 90) if not soko else (70, 60, 50))
        for j in range(2):
            d.rectangle([x + 20 + j * 150, 440, x + 150 + j * 150, 550], fill=(50, 54, 60), outline=(30, 30, 34), width=4)
            if not soko:
                d.rectangle([x + 30 + j * 150, 450, x + 140 + j * 150, 540], fill=(40, 90, 70))
    if soko:
        _boxes(d, 40, W - 40, FLOOR, 4, seed=21, gap=0.08, col=(150, 120, 80))
    return img


def dw_meisai():
    """机の上（上から）。保管の明細と売買の確認書（表の線だけ。数字・社名は描かない）、ハンコとペン。"""
    img = vgrad((W, H), (160, 130, 96), (128, 100, 72))
    d = _d(img)
    for k in range(4):
        x, y = 200 + k * 400, 160 + (k % 2) * 80
        d.rectangle([x, y, x + 360, y + 620], fill=(250, 250, 246), outline=(170, 160, 140), width=3)
        d.rectangle([x, y, x + 360, y + 60], fill=(60, 90, 140) if k % 2 else (150, 60, 60))
        for r in range(12):
            d.line([(x + 20, y + 100 + r * 42), (x + 340, y + 100 + r * 42)], fill=(170, 170, 170), width=2)
        d.line([(x + 230, y + 80), (x + 230, y + 600)], fill=(170, 170, 170), width=2)
    d.rectangle([1500, 860, 1560, 980], fill=(140, 40, 40))
    d.line([(1620, 900), (1820, 820)], fill=(30, 30, 34), width=12)
    return img


def dw_jitaku(denwa=False):
    """郊外の家の書斎（夜）。机にタイプライターと紙の束、窓の外は暗い庭。denwa は机の電話の受話器が上がり、光る。"""
    img = _rgb(base((120, 100, 86), (96, 80, 68)))
    wood_floor(img, FLOOR, col=(110, 80, 56), line=(96, 68, 46))
    d = _d(img)
    d.rectangle([1200, 120, 1680, 480], fill=(24, 30, 56), outline=(220, 210, 190), width=12)
    d.line([(1440, 120), (1440, 480)], fill=(220, 210, 190), width=8)
    for k in range(3):
        d.ellipse([1240 + k * 140, 380, 1360 + k * 140, 470], fill=(30, 50, 40))
    d.rectangle([300, 560, 1100, 620], fill=(130, 90, 60))
    d.rectangle([340, 620, 380, 860], fill=(110, 76, 50))
    d.rectangle([1020, 620, 1060, 860], fill=(110, 76, 50))
    d.rounded_rectangle([520, 470, 820, 560], radius=10, fill=(60, 64, 70))
    d.rectangle([560, 400, 780, 470], fill=(252, 252, 246), outline=(180, 180, 170), width=2)
    for j in range(3):
        d.line([(580, 420 + j * 16), (760, 420 + j * 16)], fill=(120, 120, 120), width=3)
    for j in range(6):
        d.rectangle([860 + j * 2, 540 - j * 6, 1040 + j * 2, 560 - j * 6], fill=(250, 248, 240), outline=(170, 160, 140), width=1)
    d.ellipse([320, 470, 420, 560], fill=(240, 220, 160, 120))
    d.rectangle([360, 400, 380, 480], fill=(60, 60, 60))
    d.rectangle([420, 520, 500, 560], fill=(30, 30, 34))
    if denwa:
        d.rounded_rectangle([400, 470, 520, 500], radius=12, fill=(30, 30, 34))
        img = _light(img, [[(380, 440), (540, 440), (560, 580), (360, 580)]], (255, 250, 220), 60, 16)
    return img


def dw_post():
    """郊外の通りの青い郵便ポスト（文字は描かない）と、木の並ぶ歩道。"""
    img = vgrad((W, H), (170, 200, 230), (226, 232, 238))
    d = _d(img)
    for k in range(5):
        x = 80 + k * 420
        d.rectangle([x + 60, 360, x + 90, 760], fill=(110, 80, 50))
        d.ellipse([x - 40, 200, x + 190, 420], fill=(70, 130, 70))
    d.rectangle([0, 760, W, H], fill=(186, 184, 178))
    d.rectangle([0, 740, W, 770], fill=(150, 170, 120))
    d.rounded_rectangle([860, 540, 1060, 860], radius=40, fill=(40, 70, 150))
    d.rectangle([860, 700, 1060, 860], fill=(40, 70, 150))
    d.rectangle([900, 600, 1020, 620], fill=(20, 30, 70))
    d.rectangle([880, 860, 900, 920], fill=(30, 40, 80))
    d.rectangle([1020, 860, 1040, 920], fill=(30, 40, 80))
    return img


def dw_ie(kaiten=False):
    """郊外の家の外観（2階建ての木の家、芝生と車寄せ）。kaiten は前に車が止まり、赤と青の回転灯が光る（差し替え用）。"""
    img = vgrad((W, H), (160, 190, 220), (222, 230, 236))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(110, 160, 90))
    d.rectangle([520, 320, 1400, 760], fill=(236, 230, 216), outline=(160, 150, 130), width=6)
    d.polygon([(460, 330), (960, 120), (1460, 330)], fill=(110, 80, 70))
    for r in range(2):
        for c in range(4):
            d.rectangle([600 + c * 200, 380 + r * 180, 700 + c * 200, 480 + r * 180], fill=(150, 180, 200), outline=(250, 250, 250), width=6)
    d.rectangle([900, 600, 1020, 760], fill=(120, 80, 60))
    d.polygon([(900, 760), (1020, 760), (1300, H), (700, H)], fill=(190, 186, 176))
    if kaiten:
        x = 1300
        d.rounded_rectangle([x, 820, x + 460, 960], radius=30, fill=(240, 240, 244))
        d.rectangle([x + 90, 770, x + 360, 830], fill=(200, 204, 210))
        d.rectangle([x + 170, 750, x + 230, 772], fill=(220, 40, 40))
        d.rectangle([x + 230, 750, x + 290, 772], fill=(40, 80, 220))
        d.ellipse([x + 50, 930, x + 130, 1010], fill=(30, 30, 34))
        d.ellipse([x + 330, 930, x + 410, 1010], fill=(30, 30, 34))
        img = _light(img, [[(x + 200, 760), (x - 200, 400), (x + 100, 380)], [(x + 260, 760), (x + 560, 380), (x + 760, 420)]],
                     (255, 80, 80), 40, 20)
    return img


def dw_hotel():
    """ホテルの会議室。厚いカーテン、小さなシャンデリア、長机に書類の束と水差し。"""
    img = _rgb(base((200, 186, 160), (176, 160, 136)))
    wood_floor(img, FLOOR, col=(120, 60, 60), line=(100, 48, 48))
    d = _d(img)
    for x in (100, 1560):
        d.rectangle([x, 60, x + 260, 760], fill=(130, 40, 50))
        for k in range(5):
            d.line([(x + 30 + k * 50, 60), (x + 30 + k * 50, 760)], fill=(110, 30, 40), width=4)
    d.ellipse([880, 40, 1040, 140], fill=(250, 230, 170, 200))
    d.line([(960, 0), (960, 50)], fill=(160, 140, 80), width=4)
    d.rectangle([440, 560, 1480, 640], fill=(250, 250, 246), outline=(200, 196, 186), width=4)
    for k in range(5):
        x = 500 + k * 200
        d.rectangle([x, 530, x + 120, 560], fill=(240, 238, 230), outline=(170, 160, 140), width=2)
    d.rectangle([1380, 480, 1420, 560], fill=(200, 220, 236), outline=(150, 170, 186), width=3)
    return img


LOCATIONS = {
    # 大和銀行ニューヨーク支店事件
    "dw_heya": dw_heya, "dw_ny": dw_ny, "dw_shiten": kaigai_office, "dw_torihiki": dw_torihiki,
    "dw_torihiki_soko": lambda: dw_torihiki(soko=True), "dw_kinko": mx_kinko, "dw_meisai": dw_meisai,
    "dw_jitaku": dw_jitaku, "dw_jitaku_denwa": lambda: dw_jitaku(denwa=True), "dw_post": dw_post,
    "dw_ie": dw_ie, "dw_ie_kaiten": lambda: dw_ie(kaiten=True), "dw_hotel": dw_hotel,
    "dw_honten": lambda: yakuin(), "dw_kaiken": tj_kaiken, "dw_us_houtei": court, "dw_kochisho": mx_ryuchijo,
    "dw_houtei": _sogo_saibansho, "dw_saibansho_mae": saibansho_mae, "dw_shinbun": tj_shinbun, "dw_gendai": _sega_gendai,
    # 三越事件
    "mt_heya": mt_heya, "mt_honten": mt_honten, "mt_uriba": uriba, "mt_uriba_hako": mt_uriba_hako, "mt_soko": mt_soko,
    "mt_shachoshitsu": juyakushitsu, "mt_shiire": showa_office, "mt_denpyo": mt_denpyo,
    "mt_osetsu": tj_osetsu, "mt_osetsu_ken": mt_osetsu_ken, "mt_eigakan": eigakan, "mt_uchiawase": mt_uchiawase,
    "mt_hihoten": mt_hihoten, "mt_kaiken": tj_kaiken, "mt_torishimari": mt_torishimari,
    "mt_torishimari_kiritsu": lambda: mt_torishimari("kiritsu"), "mt_torishimari_kara": lambda: mt_torishimari("kara"),
    "mt_genkan": genkan, "mt_kensatsu": ld_kanmae, "mt_houtei": _sogo_saibansho, "mt_shinbun": tj_shinbun,
    "mt_gendai": _sega_gendai,
    # ミートホープの偽装
    "mh_heya": mh_heya, "mh_kojo": mh_kojo, "mh_kojo_katazuke": lambda: mh_kojo("katazuke"),
    "mh_kojo_nuno": lambda: mh_kojo("nuno"), "mh_hikiniku": mh_hikiniku, "mh_reito": mh_reito, "mh_pack": mh_pack,
    "mh_honsha": mh_honsha, "mh_honsha_press": lambda: mh_honsha("press"), "mh_honsha_nashi": lambda: mh_honsha("nashi"),
    "mh_hiroma": mh_hiroma, "mh_shachoshitsu": shachoshitsu, "mh_hyosho": hyoushou, "mh_madoguchi": mh_madoguchi,
    "mh_shinbun": tj_shinbun, "mh_insatsu": insatsu, "mh_super": ima_super, "mh_houtei": _sogo_saibansho,
    "mh_saibansho_mae": saibansho_mae, "mh_gendai": _sega_gendai,
    # 安愚楽牧場の破綻
    "ag_heya": ag_heya, "ag_bokujo": ag_bokujo, "ag_bokujo_kara": lambda: ag_bokujo(kara=True),
    "ag_gyusha": ag_gyusha, "ag_gyusha_kara": lambda: ag_gyusha(kara=True),
    "ag_eigyo": jimusho90, "ag_pamph": ag_pamph, "ag_chirashi": lambda: ag_pamph(chirashi=True),
    "ag_shachoshitsu": shachoshitsu, "ag_kaigi": kaigi, "ag_ishigaki": ag_ishigaki, "ag_miyazaki": ag_miyazaki,
    "ag_michi": michi, "ag_shiten": ag_shiten, "ag_shiten_retsu": lambda: ag_shiten(retsu=True),
    "ag_kokugikan_soto": ag_kokugikan_soto, "ag_kokugikan": ag_kokugikan, "ag_kanzai": bengoshi,
    "ag_kokaido": kokaido, "ag_houtei": _sogo_saibansho, "ag_saibansho_mae": saibansho_mae,
    "ag_kaiken": _sega_kaiken, "ag_shinbun": tj_shinbun, "ag_gendai": _sega_gendai,
}

# 年号カード。接頭辞ごとに "ag_card_2011" のように作る（台帳を見て足す）
CARDS = {"dw": ["1976", "1983", "1984", "1992", "1995", "1996", "2000", "2001", "2003", "2014", "2019", "2026"],
         "mt": ["1938", "1962", "1966", "1972", "1973", "1976", "1978", "1979", "1981", "1982", "1987", "1993", "1995", "2008", "2026"],
         "mh": ["1976", "1995", "2006", "2007", "2008", "2017", "2023", "2026"],
         "ag": ["1981", "1990", "1996", "1997", "2007", "2009", "2010", "2011", "2013", "2014", "2022", "2026"]}


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
