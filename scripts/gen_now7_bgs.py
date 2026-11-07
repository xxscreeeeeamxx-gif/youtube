#!/usr/bin/env python3
"""第7弾4本（2026-11-21〜24。方向転換の実験の5〜8本目：会社の転落・破綻・裁判）の背景を生成する。

接頭辞: bm_（ビッグモーターの不正）/ ik_（いきなり!ステーキの失速）/ kb_（カネボウの粉飾と解体）/
        sm_（スカイマークの破綻と再生）
方針は gen_now6_bgs.py と同じ。実在の会社のロゴ・社名の文字・店の意匠・機体の塗り分けは描かない。
差し替え用（_kara・_karegi など）は元の絵に要素を足すか減らす。

実行: PYTHONPATH=. python scripts/gen_now7_bgs.py [名前...]
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gen_drama_bgs import H, OUT, W, base, vgrad, wood_floor  # noqa: E402
from scripts.gen_famicom_bgs import year_card  # noqa: E402
from scripts.gen_honda_bgs import _broadleaf  # noqa: E402
from scripts.gen_now_bgs import FLOOR, _car, _d, _rgb, kaigi, yakuin  # noqa: E402
from scripts.gen_now2_bgs import heya2, kabunushi_kaijo, shoken  # noqa: E402
from scripts.gen_now3_bgs import jimusho90, kakunoko, kinai, kuko_lobby  # noqa: E402
from scripts.gen_now5_bgs import cg_saikosai  # noqa: E402
from scripts.gen_sega_bgs import _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import kokkai as _sogo_kokkai, saibansho as _sogo_saibansho  # noqa: E402


# ---------------------------------------------------------------- ビッグモーター
def _flags(d, x0, x1, y, col_seq=((230, 40, 40), (250, 210, 40), (40, 110, 220), (250, 250, 250))):
    """展示場に張る三角の小旗の列（文字なし）。"""
    d.line([(x0, y), (x1, y)], fill=(80, 80, 86), width=3)
    k = 0
    for x in range(int(x0), int(x1) - 30, 46):
        d.polygon([(x, y), (x + 36, y), (x + 18, y + 40)], fill=col_seq[k % len(col_seq)])
        k += 1


def _dead_tree(d, x, base_y, h):
    """枯れた街路樹（葉が無く、幹と枝だけ）。"""
    d.rectangle([x - h * 0.035, base_y - h * 0.6, x + h * 0.035, base_y], fill=(110, 92, 72))
    for dx, dy, ex, ey in ((0, -0.6, -0.18, -0.85), (0, -0.6, 0.16, -0.88), (0, -0.45, -0.22, -0.62),
                           (0, -0.5, 0.2, -0.66)):
        d.line([(x + dx * h, base_y + dy * h), (x + ex * h, base_y + ey * h)], fill=(110, 92, 72), width=8)


def bm_tenpo(karegi=False, kara=False):
    """幹線道路ぞいの中古車の展示場。奥に大きな看板（文字なし）と店舗、展示の車、三角の小旗、
    手前の歩道に街路樹。karegi は街路樹が枯れて葉が無い。kara は車も旗も無く、看板に白い布。"""
    img = vgrad((W, H), (150, 196, 240), (226, 234, 242))
    d = _d(img)
    d.rectangle([360, 250, 1560, 560], fill=(244, 244, 246), outline=(150, 150, 156), width=5)   # 店舗
    d.rectangle([420, 380, 1500, 560], fill=(170, 200, 224))
    for k in range(1, 6):
        d.line([(420 + k * 180, 380), (420 + k * 180, 560)], fill=(150, 150, 156), width=5)
    d.rectangle([300, 130, 1620, 250], fill=(250, 250, 250), outline=(120, 120, 126), width=6)  # 看板（実在の色にしない）
    if not kara:
        d.rectangle([340, 160, 1580, 220], fill=(200, 60, 40))
        for k in range(4):
            d.line([(420 + k * 300, 190), (620 + k * 300, 190)], fill=(255, 240, 230), width=10)
    d.rectangle([0, 560, W, 860], fill=(150, 154, 160))                                          # 展示場
    for k in range(10):
        d.line([(k * 200, 600), (k * 200 + 40, 860)], fill=(236, 236, 230), width=5)
    if not kara:
        _flags(d, 0, W, 590)
        rnd = random.Random(7)
        for r in range(2):
            for k in range(7):
                _car(d, k * 280 - 40 + r * 90, 720 + r * 120, 0.95,
                     col=rnd.choice([(230, 230, 236), (40, 40, 46), (180, 30, 40), (90, 110, 140), (200, 200, 200)]))
                d.rectangle([k * 280 + 60 + r * 90, 640 + r * 120, k * 280 + 130 + r * 90, 660 + r * 120],
                            fill=(250, 230, 60))                                                 # 値札（数字なし）
    d.rectangle([0, 860, W, H], fill=(196, 190, 180))                                            # 歩道
    for k in range(6):
        x = 120 + k * 340
        d.rectangle([x - 70, 990, x + 70, 1010], fill=(150, 120, 90))                            # 植えます
        if karegi:
            _dead_tree(d, x, 1000, 240)
        else:
            _broadleaf(d, x, 1000, 240)
    return img


def bm_kojo():
    """板金・塗装の工場。リフトに上げた車、工具の台、奥に塗装のブース（ビニールの幕）。"""
    img = vgrad((W, H), (190, 194, 200), (170, 174, 180))
    d = _d(img)
    for k in range(9):
        d.line([(k * 240, 0), (k * 240 + 120, 120)], fill=(130, 134, 140), width=8)
    d.rectangle([1260, 180, 1840, 760], fill=(220, 226, 230), outline=(140, 146, 152), width=5)  # 塗装ブース
    for k in range(6):
        d.line([(1290 + k * 96, 190), (1290 + k * 96, 750)], fill=(200, 206, 212), width=4)
    d.rectangle([0, 760, W, H], fill=(140, 144, 148))                                            # 床
    d.rectangle([180, 600, 220, 900], fill=(230, 180, 30))                                       # リフトの柱
    d.rectangle([900, 600, 940, 900], fill=(230, 180, 30))
    d.rectangle([200, 600, 920, 620], fill=(200, 160, 30))
    _car(d, 300, 600, 1.9, col=(220, 222, 228))
    d.rectangle([1000, 780, 1200, 900], fill=(200, 40, 40), outline=(120, 20, 20), width=4)       # 工具の台
    for k in range(4):
        d.line([(1010, 800 + k * 24), (1190, 800 + k * 24)], fill=(120, 20, 20), width=3)
    for k in range(5):
        d.rectangle([1020 + k * 34, 740, 1040 + k * 34, 780], fill=(70, 70, 76))
    return img


# ---------------------------------------------------------------- いきなり!ステーキ
def _grill(d, x0, y0, x1, y1):
    """店の奥の焼き場（鉄板と炎）。"""
    d.rectangle([x0, y0, x1, y1], fill=(60, 60, 64), outline=(30, 30, 34), width=4)
    d.rectangle([x0 + 20, y0 - 20, x1 - 20, y0 + 6], fill=(110, 110, 116))
    for k in range(int((x1 - x0) / 60)):
        x = x0 + 40 + k * 60
        d.polygon([(x - 18, y0 + 2), (x, y0 - 40), (x + 18, y0 + 2)], fill=(250, 140, 30))
        d.polygon([(x - 9, y0 + 2), (x, y0 - 22), (x + 9, y0 + 2)], fill=(255, 230, 90))


def ik_tenpo(isu=False):
    """立ち食いのステーキ店。手前に背の高いカウンター（椅子なし）、奥に焼き場と肉を切る台。
    isu はカウンターに椅子が並ぶ。"""
    img = _rgb(base((236, 222, 200), (214, 196, 170)))
    wood_floor(img, FLOOR, col=(150, 110, 76), line=(130, 92, 62))
    d = _d(img)
    d.rectangle([0, 120, W, 180], fill=(90, 56, 34))                                             # 壁の帯
    _grill(d, 200, 360, 900, 520)
    d.rectangle([1020, 380, 1700, 520], fill=(240, 240, 236), outline=(160, 160, 156), width=4)   # 肉を切る台
    for k in range(3):
        d.rounded_rectangle([1080 + k * 200, 330, 1220 + k * 200, 380], radius=16, fill=(170, 50, 50))
    d.rectangle([1580, 330, 1680, 380], fill=(250, 250, 250), outline=(80, 80, 86), width=3)      # はかり
    d.rectangle([0, 680, W, 720], fill=(120, 80, 50), outline=(80, 50, 30), width=4)              # カウンター
    d.rectangle([60, 720, W - 60, 900], fill=(100, 66, 42))
    for k in range(6):
        x = 160 + k * 300
        d.rounded_rectangle([x, 646, x + 120, 680], radius=10, fill=(40, 40, 44))                 # 鉄皿
        d.ellipse([x + 20, 650, x + 100, 676], fill=(140, 70, 40))
        if isu:
            d.rectangle([x + 20, 900, x + 100, 930], fill=(60, 40, 30))
            d.line([(x + 60, 930), (x + 60, H)], fill=(60, 40, 30), width=10)
    return img


def ik_yoshoku():
    """1970年ごろの小さな洋食店。赤い格子のテーブルクロス、カウンターと棚、壁に品書きの札（文字は線）。"""
    img = _rgb(base((244, 232, 210), (226, 210, 186)))
    wood_floor(img, FLOOR, col=(160, 120, 84), line=(140, 102, 70))
    d = _d(img)
    d.rectangle([140, 300, 1780, 560], fill=(150, 110, 76), outline=(110, 80, 52), width=5)       # 棚
    for k in range(5):
        d.line([(160, 340 + k * 50), (1760, 340 + k * 50)], fill=(120, 86, 58), width=4)
    for k in range(8):
        d.rectangle([180 + k * 200, 180, 300 + k * 200, 270], fill=(250, 246, 232), outline=(120, 90, 60), width=3)
        d.line([(200 + k * 200, 210), (280 + k * 200, 210)], fill=(80, 60, 40), width=4)
        d.line([(200 + k * 200, 240), (260 + k * 200, 240)], fill=(80, 60, 40), width=4)
    for k in range(3):
        x0 = 220 + k * 560
        d.rectangle([x0, 760, x0 + 360, 800], fill=(250, 250, 250))
        for i in range(9):
            for j in range(1):
                if i % 2 == 0:
                    d.rectangle([x0 + i * 40, 760, x0 + i * 40 + 40, 800], fill=(200, 40, 40))
        d.rectangle([x0 + 20, 800, x0 + 340, 820], fill=(250, 250, 250))
        d.rectangle([x0 + 170, 820, x0 + 190, 960], fill=(90, 70, 50))
    return img


# ---------------------------------------------------------------- カネボウ
def kb_boseki():
    """明治・大正の紡績工場。のこぎり屋根の明かり取り、並んだ紡績機と糸巻き。"""
    img = vgrad((W, H), (210, 206, 196), (190, 184, 172))
    d = _d(img)
    for k in range(8):                                                                           # のこぎり屋根
        x = k * 260
        d.polygon([(x, 160), (x + 200, 40), (x + 200, 160)], fill=(236, 236, 226))
        d.polygon([(x + 200, 40), (x + 260, 160), (x + 200, 160)], fill=(150, 140, 126))
    d.rectangle([0, 160, W, 190], fill=(120, 110, 96))
    for r in range(3):                                                                           # 紡績機の列
        y = 420 + r * 190
        d.rectangle([60, y, 1860, y + 70], fill=(110, 100, 86), outline=(70, 62, 52), width=4)
        for k in range(36):
            x = 90 + k * 50
            d.rectangle([x, y - 50, x + 18, y], fill=(240, 236, 226), outline=(160, 150, 136), width=2)
            d.line([(x + 9, y - 50), (x + 9, y - 90)], fill=(200, 196, 186), width=2)
        d.rectangle([60, y + 70, 1860, y + 90], fill=(70, 62, 52))
    d.rectangle([0, FLOOR, W, H], fill=(150, 136, 116))
    return img


def kb_uriba(kara=False):
    """百貨店の化粧品の売り場。白いガラスのカウンター、並んだ瓶、鏡（ブランド名は描かない）。
    kara は棚に何も無く、白い布がかかる。"""
    img = vgrad((W, H), (250, 246, 244), (236, 230, 228))
    d = _d(img)
    d.rectangle([0, 120, W, 160], fill=(230, 200, 206))
    for k in range(3):                                                                           # 鏡と棚
        x0 = 140 + k * 580
        d.rectangle([x0, 200, x0 + 480, 600], fill=(244, 240, 240), outline=(200, 190, 190), width=5)
        if kara:
            d.rectangle([x0 + 20, 260, x0 + 460, 580], fill=(250, 250, 250))
            continue
        d.ellipse([x0 + 170, 220, x0 + 310, 340], fill=(210, 226, 236), outline=(190, 190, 196), width=4)
        for r in range(2):
            d.line([(x0 + 20, 420 + r * 90), (x0 + 460, 420 + r * 90)], fill=(200, 190, 190), width=4)
            for i in range(9):
                bx = x0 + 40 + i * 46
                c = [(220, 80, 110), (250, 250, 250), (240, 190, 200), (60, 60, 70)][(i + r) % 4]
                d.rounded_rectangle([bx, 360 + r * 90, bx + 26, 418 + r * 90], radius=6, fill=c,
                                    outline=(150, 140, 140))
    d.rectangle([80, 680, 1840, 740], fill=(250, 250, 250), outline=(200, 196, 196), width=4)     # カウンター
    d.rectangle([80, 740, 1840, 900], fill=(236, 220, 224))
    d.rectangle([0, 900, W, H], fill=(214, 206, 204))
    return img


# ---------------------------------------------------------------- スカイマーク
def sm_kuko(sukunai=False):
    """空港の出発ロビー。カウンターの帯を青にする（jl_kuko の赤い帯と分ける）。"""
    img = kuko_lobby(sukunai=sukunai)
    d = _d(img)
    d.rectangle([0, 520, W, 560], fill=(40, 90, 190))
    return img


LOCATIONS = {
    # ビッグモーター
    "bm_tenpo": bm_tenpo, "bm_tenpo_karegi": lambda: bm_tenpo(karegi=True),
    "bm_tenpo_kara": lambda: bm_tenpo(kara=True, karegi=True), "bm_kojo": bm_kojo,
    "bm_kaiken": _sega_kaiken, "bm_kaigi": kaigi, "bm_kaigi_akaji": lambda: kaigi(akaji=True),
    "bm_jimusho": jimusho90, "bm_yakuin": lambda: yakuin(), "bm_houtei": _sogo_saibansho,
    "bm_kokkai": _sogo_kokkai, "bm_gendai": _sega_gendai,
    # いきなり!ステーキ
    "ik_tenpo": ik_tenpo, "ik_tenpo_isu": lambda: ik_tenpo(isu=True), "ik_yoshoku": ik_yoshoku,
    "ik_kaiken": _sega_kaiken, "ik_kaigi": kaigi, "ik_kaigi_akaji": lambda: kaigi(akaji=True),
    "ik_shoken": shoken, "ik_yakuin": lambda: yakuin(), "ik_gendai": _sega_gendai,
    # カネボウ
    "kb_boseki": kb_boseki, "kb_uriba": kb_uriba, "kb_uriba_kara": lambda: kb_uriba(kara=True),
    "kb_kaiken": _sega_kaiken, "kb_kaigi": kaigi, "kb_kaigi_akaji": lambda: kaigi(akaji=True),
    "kb_yakuin": lambda: yakuin(), "kb_houtei": _sogo_saibansho, "kb_saikosai": cg_saikosai,
    "kb_jimusho": jimusho90, "kb_shoken": shoken, "kb_kokkai": _sogo_kokkai, "kb_gendai": _sega_gendai,
    # スカイマーク
    "sm_kuko": sm_kuko, "sm_kuko_sukunai": lambda: sm_kuko(sukunai=True), "sm_kinai": kinai,
    "sm_kakunoko": kakunoko, "sm_kaiken": _sega_kaiken, "sm_kaigi": kaigi, "sm_kaigi_akaji": lambda: kaigi(akaji=True),
    "sm_yakuin": lambda: yakuin(), "sm_houtei": _sogo_saibansho, "sm_saikensha": kabunushi_kaijo,
    "sm_shoken": shoken, "sm_jimusho": jimusho90, "sm_gendai": _sega_gendai,
}

# 年号カード。接頭辞ごとに "bm_card_2023" のように作る（台本が決まってから足す）
CARDS = {"bm": [], "ik": [], "kb": [], "sm": []}


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
