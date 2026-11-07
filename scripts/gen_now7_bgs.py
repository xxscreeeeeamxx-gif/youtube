#!/usr/bin/env python3
"""第7弾4本（2026-11-21〜24。方向転換の実験の5〜8本目：会社の転落・破綻・裁判）の背景を生成する。

接頭辞: bm_（ビッグモーターの不正）/ ik_（いきなり!ステーキの失速）/ kn_（カネボウの粉飾と解体。kb_ はエアバッグの回が使用済み）/
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
from scripts.gen_now_bgs import FLOOR, _car, _d, _rgb, kaigi, kuko_yoru, yakuin  # noqa: E402
from scripts.gen_now2_bgs import heya2, kabunushi_kaijo, shoken  # noqa: E402
from scripts.gen_now3_bgs import jimusho90, kakunoko, kinai, kuko_lobby  # noqa: E402
from scripts.gen_now5_bgs import cg_saikosai  # noqa: E402
from scripts.gen_sega_bgs import _person_line, gendai as _sega_gendai, kaiken as _sega_kaiken  # noqa: E402
from scripts.gen_sogo_bgs import enkaijo as _sogo_enkaijo, kokkai as _sogo_kokkai, saibansho as _sogo_saibansho  # noqa: E402


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


def bm_tenpo(karegi=False, kara=False, atarashii=False):
    """幹線道路ぞいの中古車の展示場。奥に大きな看板（文字なし）と店舗、展示の車、三角の小旗、
    手前の歩道に街路樹。karegi は街路樹が枯れて葉が無い。kara は車も旗も無く、看板に白い布。
    atarashii は看板の帯の色が違う（事業を引き継いだ新しい会社の店。実在の看板には似せない）。"""
    img = vgrad((W, H), (150, 196, 240), (226, 234, 242))
    d = _d(img)
    d.rectangle([360, 250, 1560, 560], fill=(244, 244, 246), outline=(150, 150, 156), width=5)   # 店舗
    d.rectangle([420, 380, 1500, 560], fill=(170, 200, 224))
    for k in range(1, 6):
        d.line([(420 + k * 180, 380), (420 + k * 180, 560)], fill=(150, 150, 156), width=5)
    d.rectangle([300, 130, 1620, 250], fill=(250, 250, 250), outline=(120, 120, 126), width=6)  # 看板（実在の色にしない）
    if not kara:
        d.rectangle([340, 160, 1580, 220], fill=(40, 120, 90) if atarashii else (200, 60, 40))
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


def bm_kojo(fusen=False, teishi=False):
    """板金・塗装の工場。リフトに上げた車、工具の台、奥に塗装のブース（ビニールの幕）。
    fusen は車体に矢印の付箋がいくつも貼られる（写真で見積もるための撮影）。teishi は奥のシャッターが下り、
    柱に白い紙（事業停止の掲示。文字は線）。"""
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
    if fusen:
        for x, y in ((380, 520), (520, 470), (700, 540), (820, 500), (460, 560)):
            d.rectangle([x, y, x + 46, y + 40], fill=(250, 220, 40), outline=(160, 130, 20), width=2)
            d.polygon([(x + 8, y + 20), (x + 30, y + 8), (x + 30, y + 32)], fill=(220, 30, 30))
    if teishi:
        d.rectangle([1260, 180, 1840, 760], fill=(170, 172, 176), outline=(120, 122, 126), width=5)
        for k in range(18):
            d.line([(1260, 200 + k * 31), (1840, 200 + k * 31)], fill=(140, 142, 146), width=3)
        d.rectangle([980, 360, 1160, 600], fill=(252, 252, 250), outline=(120, 120, 120), width=3)
        d.line([(1000, 390), (1140, 390)], fill=(200, 30, 30), width=8)
        for k in range(7):
            d.line([(1000, 420 + k * 24), (1140, 420 + k * 24)], fill=(30, 30, 30), width=3)
    return img


def bm_heya():
    """今の部屋。机に修理の見積書（文字は線）と車の鍵。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([220, 520, 380, 640], fill=(252, 252, 250), outline=(150, 150, 150), width=2)
    d.line([(236, 540), (364, 540)], fill=(40, 60, 120), width=5)
    for k in range(5):
        d.line([(236, 562 + k * 14), (340, 562 + k * 14)], fill=(110, 110, 110), width=2)
    d.line([(300, 626), (364, 626)], fill=(200, 30, 30), width=4)
    d.ellipse([430, 600, 470, 640], outline=(120, 120, 126), width=6)
    d.rounded_rectangle([462, 610, 540, 632], radius=8, fill=(40, 40, 46))
    return img


def bm_seibi_old():
    """1970年代の町の小さな整備工場。トタンの屋根、開いたシャッター、中に古い乗用車、ドラム缶。"""
    img = vgrad((W, H), (160, 196, 226), (220, 226, 220))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(150, 140, 120))
    d.polygon([(300, 260), (1620, 260), (1700, 330), (220, 330)], fill=(140, 150, 156), outline=(90, 96, 100))
    d.rectangle([300, 330, 1620, 860], fill=(200, 190, 170), outline=(120, 110, 96), width=5)
    for k in range(10):
        d.line([(300, 340 + k * 50), (1620, 340 + k * 50)], fill=(184, 174, 154), width=3)
    d.rectangle([460, 420, 1460, 860], fill=(60, 56, 52))                                          # 開いた口
    d.rectangle([460, 400, 1460, 430], fill=(150, 150, 156))                                       # 巻いたシャッター
    _car(d, 640, 840, 2.0, col=(200, 70, 50))
    for x in (1540, 1600):
        d.rounded_rectangle([x - 26, 760, x + 26, 860], radius=6, fill=(60, 90, 140), outline=(40, 60, 100), width=3)
    d.rectangle([340, 300, 900, 330], fill=(250, 250, 246))                                        # 看板（文字は線）
    d.line([(360, 315), (880, 315)], fill=(200, 40, 40), width=6)
    return img


def bm_pt(kara=False):
    """写真で見積もる部屋（事務所）。並んだ机、画面に車の写真、山積みの書類。kara は夜で、電気が消えて誰もいない。"""
    img = _rgb(base((236, 236, 232), (222, 222, 218)))
    wood_floor(img, FLOOR, col=(190, 190, 186), line=(176, 176, 172))
    d = _d(img)
    for k in range(10):
        d.rectangle([60 + k * 190, 90, 120 + k * 190, 110], fill=(250, 250, 240))                  # 蛍光灯
    for r in range(2):
        for c in range(4):
            x, y = 140 + c * 440, 430 + r * 220
            d.rectangle([x, y + 90, x + 360, y + 110], fill=(170, 150, 120))                       # 机
            d.rectangle([x + 60, y, x + 220, y + 90], fill=(40, 40, 44))                           # 画面
            d.rectangle([x + 70, y + 8, x + 210, y + 82], fill=(140, 170, 200))
            _car(d, x + 84, y + 70, 0.44, col=(220, 222, 228))
            d.rectangle([x + 250, y + 40, x + 330, y + 90], fill=(250, 250, 246), outline=(170, 170, 170))
    if kara:
        d.rectangle([0, 0, W, H], fill=(10, 14, 30, 170))
    return img


def bm_sonpo():
    """大きな会社の応接室。窓いっぱいの高層ビル、低いテーブルと革のソファ（損保の本社・役員との面談）。"""
    img = _rgb(yakuin(view=(190, 210, 230), city=True))
    d = _d(img)
    d.rectangle([520, 820, 1400, 870], fill=(110, 80, 56))
    for x in (380, 1420):
        d.rounded_rectangle([x, 740, x + 220, 900], radius=26, fill=(90, 60, 44), outline=(60, 40, 28), width=4)
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


def ik_heya():
    """今の部屋。机に量り売りのナッツの袋と、長いレシート（文字は線）。"""
    img = heya2("none")
    d = _d(img)
    d.polygon([(220, 640), (330, 640), (316, 520), (234, 520)], fill=(236, 220, 180), outline=(150, 120, 80))
    for k in range(6):
        d.ellipse([244 + k * 12, 560 + (k % 2) * 16, 266 + k * 12, 578 + (k % 2) * 16], fill=(170, 120, 70))
    d.rectangle([400, 560, 470, 640], fill=(250, 250, 248), outline=(170, 170, 170))
    for k in range(6):
        d.line([(410, 574 + k * 11), (460, 574 + k * 11)], fill=(120, 120, 120), width=2)
    return img


def ik_chubo():
    """1960年代のホテルの厨房。白いタイルの壁、大きなかまど、吊るした鍋、ステンレスの台。"""
    img = vgrad((W, H), (236, 236, 230), (220, 220, 214))
    d = _d(img)
    for y in range(120, 620, 40):
        d.line([(0, y), (W, y)], fill=(210, 210, 204), width=2)
    for x in range(0, W, 40):
        d.line([(x, 120), (x, 620)], fill=(214, 214, 208), width=2)
    d.rectangle([0, 80, W, 110], fill=(150, 150, 150))
    for k in range(9):                                                                           # 吊るした鍋
        x = 160 + k * 190
        d.line([(x, 110), (x, 190)], fill=(90, 90, 96), width=4)
        d.ellipse([x - 50, 190, x + 50, 240], fill=(170, 120, 80), outline=(110, 80, 50), width=3)
    d.rectangle([200, 420, 1000, 640], fill=(60, 60, 64), outline=(30, 30, 34), width=5)          # かまど
    for k in range(4):
        d.ellipse([240 + k * 190, 400, 360 + k * 190, 440], fill=(40, 40, 44))
        d.polygon([(270 + k * 190, 410), (300 + k * 190, 370), (330 + k * 190, 410)], fill=(250, 150, 40))
    d.rectangle([1100, 460, 1800, 520], fill=(200, 204, 210), outline=(150, 154, 160), width=4)   # ステンレスの台
    d.rectangle([1120, 520, 1780, 640], fill=(180, 184, 190))
    d.rounded_rectangle([1250, 420, 1450, 460], radius=12, fill=(150, 50, 50))                    # 厚い肉
    d.rectangle([0, 640, W, H], fill=(170, 160, 150))
    return img


def _shopfront(d, x0, x1, y0=260, y1=860, awning=(110, 30, 30), door=(170, 200, 220)):
    """店の正面（文字なし）。日よけ、ガラスの戸、窓。戸の中心の x を返す。"""
    d.rectangle([x0, y0, x1, y1], fill=(70, 50, 40), outline=(40, 30, 24), width=4)
    d.polygon([(x0 - 20, y0), (x1 + 20, y0), (x1, y0 + 90), (x0, y0 + 90)], fill=awning)
    for k in range(int((x1 - x0) / 60)):
        d.line([(x0 + k * 60, y0), (x0 + k * 60 - 10, y0 + 90)], fill=(255, 255, 255, 60), width=6)
    cx = (x0 + x1) // 2
    d.rectangle([cx - 110, y0 + 150, cx + 110, y1], fill=door, outline=(40, 30, 24), width=4)
    d.line([(cx, y0 + 150), (cx, y1)], fill=(40, 30, 24), width=4)
    wb = max(y1 - 200, y0 + 260)                                                                 # 低い店でも窓が潰れない
    d.rectangle([x0 + 40, y0 + 150, cx - 150, wb], fill=(240, 210, 150), outline=(40, 30, 24), width=4)
    d.rectangle([cx + 150, y0 + 150, x1 - 40, wb], fill=(240, 210, 150), outline=(40, 30, 24), width=4)
    return cx


def ik_mise(gyoretsu=False, harigami=False, heiten=False):
    """街の通りの店の正面（文字なし）。gyoretsu は店の前に客の行列、harigami はガラス戸に白い紙（社長のお願い）、
    heiten は戸の前に柵と、閉店のお知らせの紙。"""
    img = vgrad((W, H), (170, 196, 226), (220, 228, 236))
    d = _d(img)
    for x, h in ((0, 520), (1500, 600)):                                                         # 両隣のビル
        d.rectangle([x, 760 - h, x + 420, 860], fill=(200, 196, 190), outline=(150, 146, 140), width=4)
        for r in range(int(h / 90)):
            for c in range(3):
                d.rectangle([x + 40 + c * 130, 800 - h + r * 90, x + 120 + c * 130, 850 - h + r * 90],
                            fill=(160, 186, 210))
    cx = _shopfront(d, 460, 1460)
    d.rectangle([0, 860, W, H], fill=(190, 186, 180))
    if harigami or heiten:
        d.rectangle([cx - 90, 520, cx - 10, 640], fill=(252, 252, 250), outline=(120, 120, 120), width=2)
        for k in range(7):
            d.line([(cx - 82, 534 + k * 14), (cx - 18, 534 + k * 14)], fill=(30, 30, 30), width=2)
    if heiten:
        d.rectangle([cx + 10, 520, cx + 90, 640], fill=(252, 252, 250), outline=(120, 120, 120), width=2)
        d.line([(cx + 20, 540), (cx + 80, 540)], fill=(200, 30, 30), width=5)
        for k in range(5):
            d.line([(cx + 20, 560 + k * 14), (cx + 80, 560 + k * 14)], fill=(30, 30, 30), width=2)
        for k in range(5):
            d.rectangle([cx - 260 + k * 120, 860, cx - 250 + k * 120, 960], fill=(230, 120, 30))
        d.rectangle([cx - 270, 880, cx + 230, 896], fill=(230, 120, 30))
    if gyoretsu:
        _person_line(d, 40, 1010, 9, 1.0)
        _person_line(d, 1160, 1010, 6, 1.0)
    return img


def ik_ekimae():
    """駅前の通り。同じ形の店（日よけが同じ色）が4つ並ぶ。奥に駅の屋根。"""
    img = vgrad((W, H), (170, 196, 226), (220, 228, 236))
    d = _d(img)
    d.rectangle([0, 160, W, 300], fill=(200, 200, 204), outline=(140, 140, 146), width=5)        # 駅の屋根
    d.rectangle([0, 300, W, 330], fill=(120, 120, 126))
    for k in range(4):
        x0 = 40 + k * 470
        _shopfront(d, x0, x0 + 420, y0=420, y1=860)
        d.ellipse([x0 + 170, 330, x0 + 250, 410], fill=(110, 30, 30), outline=(40, 30, 24), width=4)  # 同じ丸看板
    d.rectangle([0, 860, W, H], fill=(190, 186, 180))
    return img


def ik_ny():
    """ニューヨークの下町の通り。れんがの建物、非常階段、1階のステーキ店。窓に料理人の絵の看板（顔は描かない）。"""
    img = vgrad((W, H), (160, 190, 220), (214, 222, 230))
    d = _d(img)
    d.rectangle([200, 60, 1720, 860], fill=(150, 76, 56), outline=(100, 50, 36), width=5)         # れんが
    for y in range(80, 860, 26):
        d.line([(200, y), (1720, y)], fill=(130, 64, 48), width=2)
    for r in range(3):
        for c in range(5):
            x = 300 + c * 290
            y = 100 + r * 150
            d.rectangle([x, y, x + 140, y + 110], fill=(170, 196, 214), outline=(240, 236, 226), width=6)
        d.rectangle([260, 210 + r * 150, 1660, 220 + r * 150], fill=(40, 40, 44))                 # 非常階段
        for c in range(14):
            d.line([(270 + c * 100, 220 + r * 150), (270 + c * 100, 160 + r * 150)], fill=(40, 40, 44), width=3)
    cx = _shopfront(d, 360, 1560, y0=520, y1=860, awning=(30, 30, 34))
    d.rectangle([cx + 170, 600, cx + 360, 760], fill=(250, 246, 236), outline=(40, 30, 24), width=4)  # 看板の絵
    d.ellipse([cx + 230, 620, cx + 300, 690], fill=(240, 220, 200))
    d.rectangle([cx + 220, 600, cx + 310, 630], fill=(255, 255, 255), outline=(150, 150, 150))
    d.rectangle([cx + 215, 690, cx + 315, 750], fill=(255, 255, 255), outline=(150, 150, 150))
    d.rectangle([0, 860, W, H], fill=(150, 150, 154))
    d.rounded_rectangle([60, 900, 420, 1010], radius=20, fill=(240, 200, 30))                     # 黄色い車
    for wx in (130, 350):
        d.ellipse([wx - 34, 970, wx + 34, 1038], fill=(30, 30, 34))
    return img


def ik_shacho(pins=False, yoru=False):
    """社長室。壁に大きな地図（白地に細い線）、重い机。pins は地図が赤い印で埋まる。
    yoru は夜で、机に筆ペンと白い紙の束、卓上の灯り。"""
    img = _rgb(yakuin(view=(30, 40, 70) if yoru else (196, 214, 230), city=True))
    d = _d(img)
    d.rectangle([140, 160, 760, 560], fill=(244, 244, 238), outline=(120, 100, 80), width=8)       # 地図
    for k in range(9):
        d.line([(160 + k * 70, 180), (190 + k * 66, 540)], fill=(200, 210, 220), width=3)
    for k in range(6):
        d.line([(160, 200 + k * 60), (740, 190 + k * 66)], fill=(210, 220, 214), width=3)
    rnd = random.Random(3)
    for _ in range(140 if pins else 14):
        x, y = rnd.randint(180, 720), rnd.randint(190, 530)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(220, 30, 30))
    if yoru:
        d.rectangle([0, 0, W, H], fill=(0, 0, 30, 90))
        d.rectangle([900, 640, 1500, 700], fill=(250, 250, 246))
        for k in range(4):
            d.rectangle([920 + k * 140, 600 - k * 4, 1040 + k * 140, 640 - k * 4], fill=(252, 252, 250),
                        outline=(160, 160, 160))
        d.line([(1520, 650), (1620, 610)], fill=(20, 20, 20), width=10)
        d.ellipse([1640, 520, 1760, 600], fill=(255, 230, 160, 200))
    return _rgb(img)


def ik_studio():
    """テレビの報道番組のスタジオ。青い背景のパネル、半円の机、照明。"""
    img = vgrad((W, H), (30, 50, 100), (20, 30, 60))
    d = _d(img)
    for k in range(6):
        d.rectangle([120 + k * 290, 120, 380 + k * 290, 560], fill=(40, 80, 160), outline=(90, 140, 220), width=4)
    d.rectangle([0, 40, W, 70], fill=(70, 70, 80))
    for k in range(8):
        d.ellipse([140 + k * 230, 60, 200 + k * 230, 100], fill=(255, 244, 210))
    d.ellipse([360, 640, 1560, 900], fill=(230, 230, 236), outline=(160, 160, 170), width=6)        # 机
    d.rectangle([360, 770, 1560, 900], fill=(230, 230, 236))
    d.rectangle([0, 900, W, H], fill=(40, 44, 60))
    return img


def ik_ryogoku(heiten=False):
    """大きな屋根の建物（緑の屋根。文字なし）の向かいの、小さなステーキ店。のれん（文字なし）。
    heiten はのれんが無く、戸に白い紙。"""
    img = vgrad((W, H), (170, 200, 230), (226, 232, 238))
    d = _d(img)
    d.polygon([(1100, 300), (1500, 120), (1900, 300)], fill=(90, 140, 110), outline=(60, 100, 80))  # 奥の大屋根
    d.rectangle([1150, 300, 1880, 520], fill=(220, 214, 200))
    d.rectangle([200, 300, 1000, 860], fill=(230, 220, 200), outline=(120, 100, 80), width=5)       # 小さな店
    d.rectangle([200, 260, 1000, 320], fill=(60, 50, 44))
    d.rectangle([420, 460, 780, 860], fill=(150, 120, 90), outline=(80, 60, 40), width=5)
    for k in range(4):
        d.line([(420 + k * 90, 460), (420 + k * 90, 860)], fill=(110, 86, 60), width=4)
    if heiten:
        d.rectangle([540, 560, 660, 700], fill=(252, 252, 250), outline=(120, 120, 120), width=2)
        for k in range(6):
            d.line([(552, 580 + k * 18), (648, 580 + k * 18)], fill=(30, 30, 30), width=2)
    else:
        for k in range(3):
            d.rectangle([410 + k * 125, 430, 525 + k * 125, 580], fill=(40, 40, 60))
        d.rectangle([396, 418, 794, 432], fill=(90, 66, 40))
    d.rectangle([0, 860, W, H], fill=(190, 186, 180))
    return img


def ik_wakuni():
    """小さなステーキ店のカウンター。鉄板、木のカウンター、壁に品書きの札（文字は線）。"""
    img = _rgb(base((236, 224, 204), (220, 206, 184)))
    wood_floor(img, FLOOR, col=(150, 110, 76), line=(130, 92, 62))
    d = _d(img)
    for k in range(6):
        d.rectangle([200 + k * 260, 160, 320 + k * 260, 290], fill=(250, 246, 232), outline=(120, 90, 60), width=3)
        d.line([(220 + k * 260, 200), (300 + k * 260, 200)], fill=(80, 60, 40), width=4)
        d.line([(220 + k * 260, 240), (280 + k * 260, 240)], fill=(80, 60, 40), width=4)
    d.rectangle([300, 520, 1620, 600], fill=(70, 70, 74), outline=(30, 30, 34), width=4)            # 鉄板
    d.rounded_rectangle([700, 500, 880, 530], radius=10, fill=(150, 60, 50))
    d.rectangle([100, 680, 1820, 730], fill=(170, 130, 90), outline=(120, 90, 60), width=4)          # カウンター
    d.rectangle([120, 730, 1800, 900], fill=(140, 104, 70))
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


def kb_heya():
    """今の部屋。机にお菓子の箱の山と、貯金箱とノート（文字は線）。"""
    img = heya2("none")
    d = _d(img)
    for k in range(4):
        d.rectangle([200 + k * 8, 600 - k * 30, 330 + k * 8, 632 - k * 30],
                    fill=[(240, 120, 90), (250, 210, 80), (120, 180, 230), (240, 150, 190)][k], outline=(120, 90, 70))
    d.ellipse([400, 580, 470, 640], fill=(250, 170, 190), outline=(170, 100, 120), width=3)
    d.rectangle([500, 610, 600, 640], fill=(250, 250, 246), outline=(150, 150, 150))
    return img


def kb_kaigi_old():
    """1960年代の本社の会議室。黒板に五角形、長い机と灰皿、木の壁。"""
    img = _rgb(base((200, 180, 150), (180, 160, 130)))
    wood_floor(img, FLOOR, col=(140, 104, 70), line=(120, 88, 58))
    d = _d(img)
    d.rectangle([560, 140, 1360, 520], fill=(40, 70, 56), outline=(120, 90, 60), width=12)        # 黒板
    cx, cy, r = 960, 330, 140
    import math
    pts = [(cx + r * math.sin(2 * math.pi * k / 5), cy - r * math.cos(2 * math.pi * k / 5)) for k in range(5)]
    d.polygon(pts, outline=(240, 240, 230), width=6)
    for x, y in pts:
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(240, 240, 230))
    d.rectangle([300, 740, 1620, 800], fill=(110, 76, 48), outline=(80, 54, 34), width=4)         # 机
    for k in range(4):
        d.ellipse([440 + k * 340, 726, 500 + k * 340, 746], fill=(180, 180, 186))                  # 灰皿
    return img


def kb_soko(yama=False):
    """繊維の倉庫。毛布の箱（茶色の段ボール、文字なし）が並ぶ。yama は天井まで積み上がる。"""
    img = vgrad((W, H), (180, 176, 168), (160, 156, 148))
    d = _d(img)
    for k in range(8):
        d.line([(k * 260, 0), (k * 260 + 130, 110)], fill=(130, 126, 118), width=8)
    d.rectangle([0, FLOOR - 60, W, H], fill=(140, 134, 124))
    rows = 9 if yama else 2
    for r in range(rows):
        for c in range(12):
            if not yama and c % 3 == 2:
                continue
            x, y = 40 + c * 155, FLOOR - 60 - (r + 1) * 90
            d.rectangle([x, y, x + 145, y + 86], fill=(196, 160, 110), outline=(140, 110, 70), width=3)
            d.line([(x + 10, y + 43), (x + 135, y + 43)], fill=(170, 136, 90), width=3)
    return img


def kb_oroshi():
    """卸の倉庫。お菓子の箱が山積み、手前の棚に値札（赤い札と黄色い札。数字は描かない）。"""
    img = vgrad((W, H), (200, 200, 196), (180, 180, 176))
    d = _d(img)
    d.rectangle([0, FLOOR - 60, W, H], fill=(150, 150, 146))
    rnd = random.Random(9)
    for r in range(6):
        for c in range(14):
            x, y = 20 + c * 136, FLOOR - 60 - (r + 1) * 76
            col = rnd.choice([(240, 120, 90), (250, 210, 80), (120, 180, 230), (240, 150, 190), (160, 210, 140)])
            d.rectangle([x, y, x + 130, y + 72], fill=col, outline=(110, 90, 70), width=2)
    for k, col in enumerate(((230, 40, 40), (250, 220, 40))):
        d.rectangle([620 + k * 520, 520, 780 + k * 520, 600], fill=col, outline=(80, 60, 40), width=4)
    return img


def kb_torishimari():
    """取締役会の部屋。長い机に椅子が並び、いちばん奥の大きな椅子だけ空いている。"""
    img = _rgb(base((226, 222, 214), (210, 206, 198)))
    wood_floor(img, FLOOR, col=(150, 120, 90), line=(130, 102, 76))
    d = _d(img)
    d.polygon([(700, 560), (1220, 560), (1500, 900), (420, 900)], fill=(120, 84, 56), outline=(80, 54, 34))
    d.rounded_rectangle([880, 380, 1040, 560], radius=20, fill=(60, 40, 30), outline=(40, 26, 18), width=4)  # 空いた椅子
    for k in range(4):
        y = 600 + k * 80
        xl = 700 - (y - 560) * 0.8 - 90
        xr = 1220 + (y - 560) * 0.8 + 20
        d.rounded_rectangle([xl, y - 60, xl + 70, y + 30], radius=12, fill=(90, 90, 96))
        d.ellipse([xl + 10, y - 110, xl + 60, y - 60], fill=(60, 60, 66))
        d.rounded_rectangle([xr, y - 60, xr + 70, y + 30], radius=12, fill=(90, 90, 96))
        d.ellipse([xr + 10, y - 110, xr + 60, y - 60], fill=(60, 60, 66))
    return img


def kb_jitaku():
    """住宅街の家の門の前。黒い車、門の外に記者の人だかり（顔は描かない）。"""
    img = vgrad((W, H), (180, 200, 220), (220, 226, 230))
    d = _d(img)
    d.rectangle([0, 300, W, 760], fill=(200, 196, 186))
    d.polygon([(500, 300), (960, 140), (1420, 300)], fill=(90, 80, 76))
    d.rectangle([560, 300, 1360, 620], fill=(236, 230, 216), outline=(150, 140, 126), width=4)
    d.rectangle([0, 620, W, 700], fill=(170, 160, 146))                                            # 塀
    d.rectangle([820, 560, 1100, 760], fill=(80, 70, 60))                                         # 門
    d.rectangle([0, 760, W, H], fill=(140, 140, 144))
    _car(d, 760, 900, 1.6, col=(30, 30, 34))
    _person_line(d, 40, 1010, 5, 1.0)
    _person_line(d, 1380, 1010, 5, 1.0)
    return img


def kb_honsha(kanban=1):
    """本社のビルの正面。kanban=1 は看板が1枚、2 は2枚（会社が2つに分かれる）、3 は看板の色が替わる（新しい社名）。
    文字は描かない。"""
    img = vgrad((W, H), (170, 200, 230), (226, 232, 238))
    d = _d(img)
    d.rectangle([460, 100, 1460, 900], fill=(216, 214, 210), outline=(150, 148, 144), width=6)
    for r in range(7):
        for c in range(6):
            d.rectangle([520 + c * 156, 140 + r * 90, 620 + c * 156, 200 + r * 90], fill=(150, 180, 206))
    d.rectangle([840, 760, 1080, 900], fill=(120, 150, 176), outline=(90, 90, 96), width=4)
    cols = {1: [(200, 40, 50)], 2: [(200, 40, 50), (240, 160, 190)], 3: [(40, 110, 170)]}[kanban]
    for k, col in enumerate(cols):
        x0 = 560 + k * 420 if len(cols) == 2 else 700
        w = 380 if len(cols) == 2 else 520
        d.rectangle([x0, 690, x0 + w, 750], fill=col, outline=(80, 80, 86), width=4)
        d.line([(x0 + 30, 720), (x0 + w - 30, 720)], fill=(255, 255, 255), width=8)
    d.rectangle([0, 900, W, H], fill=(190, 186, 180))
    return img


# ---------------------------------------------------------------- スカイマーク
def sm_kuko(sukunai=False):
    """空港の出発ロビー。カウンターの帯を青にする（jl_kuko の赤い帯と分ける）。"""
    img = kuko_lobby(sukunai=sukunai)
    d = _d(img)
    d.rectangle([0, 520, W, 560], fill=(40, 90, 190))
    return img



def sm_heya():
    """今の部屋。机に大きなプラモデルの箱（飛行機の絵。文字なし）とスマホ。"""
    img = heya2("none")
    d = _d(img)
    d.rectangle([180, 560, 420, 640], fill=(70, 120, 200), outline=(40, 70, 130), width=3)
    d.polygon([(220, 600), (380, 590), (392, 600), (380, 610)], fill=(250, 250, 250))
    d.polygon([(290, 600), (320, 572), (334, 600)], fill=(250, 250, 250))
    d.rounded_rectangle([460, 600, 500, 640], radius=6, fill=(30, 30, 34))
    return img


def _clock(d, cx, cy, r, hour):
    """壁の時計（時の針だけ。分は12時）。"""
    import math
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 250, 248), outline=(60, 60, 66), width=6)
    for k in range(12):
        a = 2 * math.pi * k / 12
        d.line([(cx + r * 0.8 * math.sin(a), cy - r * 0.8 * math.cos(a)),
                (cx + r * 0.92 * math.sin(a), cy - r * 0.92 * math.cos(a))], fill=(60, 60, 66), width=4)
    a = 2 * math.pi * (hour % 12) / 12
    d.line([(cx, cy), (cx + r * 0.5 * math.sin(a), cy - r * 0.5 * math.cos(a))], fill=(30, 30, 34), width=8)
    d.line([(cx, cy), (cx, cy - r * 0.75)], fill=(30, 30, 34), width=5)


def sm_kaigi_clock(hour=2, full=False):
    """2000年代はじめの本社の会議室。壁に時計、長い机と椅子。full は椅子が人（顔は描かない）で埋まる。"""
    img = _rgb(base((226, 224, 218), (210, 208, 202)))
    wood_floor(img, FLOOR, col=(170, 150, 120), line=(150, 132, 104))
    d = _d(img)
    _clock(d, 960, 220, 100, hour)
    d.rectangle([260, 640, 1660, 700], fill=(150, 110, 76), outline=(110, 80, 52), width=4)
    for k in range(7):
        x = 300 + k * 200
        d.rounded_rectangle([x, 560, x + 110, 650], radius=12, fill=(70, 80, 110))
        if full or k in (0, 6):
            d.ellipse([x + 25, 470, x + 85, 530], fill=(60, 60, 66))
            d.rounded_rectangle([x + 10, 530, x + 100, 640], radius=20, fill=(80, 84, 96))
    return img


def sm_shacho(fax=False):
    """社長室。窓に空港の滑走路と飛行機、机に飛行機の模型。fax は机の上にファクスの紙が1枚。"""
    img = _rgb(yakuin(view=(180, 206, 232), city=False))
    d = _d(img)
    d.rectangle([0, 470, W, 520], fill=(120, 124, 130))
    d.polygon([(1300, 420), (1560, 410), (1580, 420), (1560, 430)], fill=(250, 250, 250))
    d.polygon([(1420, 420), (1460, 390), (1480, 420)], fill=(250, 250, 250))
    d.polygon([(560, 600), (700, 594), (712, 600), (700, 606)], fill=(240, 240, 244), outline=(150, 150, 156))
    if fax:
        d.rectangle([900, 590, 1020, 650], fill=(252, 252, 250), outline=(140, 140, 140), width=2)
        for k in range(4):
            d.line([(912, 604 + k * 11), (1008, 604 + k * 11)], fill=(40, 40, 40), width=2)
    return img


def sm_seisa():
    """夜の本社の会議室。机に段ボールと書類の山、窓の外は夜、ノートパソコンの明かり。"""
    img = _rgb(base((200, 200, 206), (186, 186, 192)))
    wood_floor(img, FLOOR, col=(150, 140, 126), line=(130, 122, 110))
    d = _d(img)
    d.rectangle([200, 120, 1720, 440], fill=(20, 26, 50), outline=(120, 120, 126), width=8)
    for k in range(1, 4):
        d.line([(200 + k * 380, 120), (200 + k * 380, 440)], fill=(120, 120, 126), width=6)
    for k in range(9):
        d.ellipse([260 + k * 170, 360, 270 + k * 170, 370], fill=(250, 220, 120))
    d.rectangle([220, 660, 1700, 720], fill=(140, 110, 80), outline=(100, 76, 54), width=4)
    for k in range(5):
        d.rectangle([280 + k * 290, 560, 420 + k * 290, 660], fill=(196, 160, 110), outline=(140, 110, 70), width=3)
        for r in range(3):
            d.rectangle([440 + k * 290, 640 - r * 14, 520 + k * 290, 652 - r * 14], fill=(250, 250, 246),
                        outline=(160, 160, 160))
    return img


def sm_shiten():
    """地方空港の小さな事務所。窓の外に小さな滑走路と機体、壁に時刻表の板（文字は線）、机が数台。"""
    img = _rgb(base((236, 236, 230), (222, 222, 216)))
    wood_floor(img, FLOOR, col=(190, 186, 176), line=(176, 172, 162))
    d = _d(img)
    d.rectangle([160, 140, 1100, 460], fill=(176, 206, 232), outline=(120, 120, 126), width=8)
    d.rectangle([168, 380, 1092, 452], fill=(120, 130, 120))
    d.polygon([(500, 380), (760, 372), (780, 380), (760, 388)], fill=(250, 250, 250))
    d.polygon([(620, 380), (660, 350), (680, 380)], fill=(250, 250, 250))
    d.rectangle([1260, 160, 1760, 460], fill=(40, 44, 56), outline=(120, 120, 126), width=6)
    for k in range(6):
        d.line([(1290, 200 + k * 42), (1730, 200 + k * 42)], fill=(250, 210, 80), width=5)
    for k in range(3):
        d.rectangle([260 + k * 520, 700, 640 + k * 520, 740], fill=(200, 196, 186), outline=(150, 146, 136), width=3)
    return img


def sm_gate(gyoretsu=True):
    """空港の搭乗口。大きな窓の外に機体、手前に搭乗口のカウンター、待つ客の列（顔は描かない）。"""
    img = vgrad((W, H), (220, 224, 230), (200, 204, 212))
    d = _d(img)
    d.rectangle([0, 100, W, 560], fill=(170, 200, 230))
    for k in range(9):
        d.line([(k * 240, 100), (k * 240, 560)], fill=(140, 146, 156), width=8)
    d.rectangle([0, 470, W, 560], fill=(130, 134, 140))
    d.polygon([(700, 470), (1500, 440), (1600, 470), (1500, 500)], fill=(250, 250, 252), outline=(160, 160, 170))
    d.polygon([(1080, 470), (1220, 380), (1300, 470)], fill=(250, 250, 252), outline=(160, 160, 170))
    d.rectangle([1380, 620, 1800, 720], fill=(240, 240, 244), outline=(160, 160, 166), width=4)
    d.rectangle([1380, 600, 1800, 620], fill=(40, 90, 190))
    d.rectangle([0, FLOOR - 120, W, H], fill=(196, 194, 190))
    if gyoretsu:
        _person_line(d, 80, 1010, 8, 1.0)
    return img


LOCATIONS = {
    # ビッグモーター
    "bm_heya": bm_heya, "bm_seibi_old": bm_seibi_old,
    "bm_tenpo": bm_tenpo, "bm_tenpo_karegi": lambda: bm_tenpo(karegi=True),
    "bm_tenpo_kara": lambda: bm_tenpo(kara=True, karegi=True), "bm_tenpo_new": lambda: bm_tenpo(atarashii=True),
    "bm_kojo": bm_kojo, "bm_kojo_fusen": lambda: bm_kojo(fusen=True), "bm_kojo_teishi": lambda: bm_kojo(teishi=True),
    "bm_pt": bm_pt, "bm_pt_kara": lambda: bm_pt(kara=True), "bm_sonpo": bm_sonpo,
    "bm_kaiken": _sega_kaiken, "bm_kaigi": kaigi, "bm_kaigi_akaji": lambda: kaigi(akaji=True),
    "bm_jimusho": jimusho90, "bm_yakuin": lambda: yakuin(), "bm_houtei": _sogo_saibansho,
    "bm_kokkai": _sogo_kokkai, "bm_gendai": _sega_gendai,
    # いきなり!ステーキ
    "ik_heya": ik_heya, "ik_chubo": ik_chubo, "ik_yoshoku": ik_yoshoku,
    "ik_tenpo": ik_tenpo, "ik_tenpo_isu": lambda: ik_tenpo(isu=True),
    "ik_mise": ik_mise, "ik_mise_gyoretsu": lambda: ik_mise(gyoretsu=True),
    "ik_mise_harigami": lambda: ik_mise(harigami=True), "ik_mise_heiten": lambda: ik_mise(heiten=True),
    "ik_ekimae": ik_ekimae, "ik_ny": ik_ny, "ik_party": _sogo_enkaijo,
    "ik_shacho": ik_shacho, "ik_shacho_pin": lambda: ik_shacho(pins=True), "ik_shacho_yoru": lambda: ik_shacho(yoru=True),
    "ik_studio": ik_studio, "ik_ryogoku": ik_ryogoku, "ik_ryogoku_heiten": lambda: ik_ryogoku(heiten=True),
    "ik_wakuni": ik_wakuni,
    "ik_kaiken": _sega_kaiken, "ik_kaigi": kaigi, "ik_kaigi_akaji": lambda: kaigi(akaji=True),
    "ik_shoken": shoken, "ik_jimusho": jimusho90, "ik_gendai": _sega_gendai,
    # カネボウ
    "kn_heya": kb_heya, "kn_boseki": kb_boseki, "kn_kaigi_old": kb_kaigi_old,
    "kn_soko": kb_soko, "kn_soko_yama": lambda: kb_soko(yama=True), "kn_oroshi": kb_oroshi,
    "kn_torishimari": kb_torishimari, "kn_jitaku": kb_jitaku, "kn_osetsu": bm_sonpo,
    "kn_honsha": kb_honsha, "kn_honsha_2": lambda: kb_honsha(2), "kn_honsha_new": lambda: kb_honsha(3),
    "kn_uriba": kb_uriba, "kn_uriba_kara": lambda: kb_uriba(kara=True),
    "kn_kaiken": _sega_kaiken, "kn_kaigi": kaigi, "kn_kaigi_akaji": lambda: kaigi(akaji=True),
    "kn_yakuin": lambda: yakuin(), "kn_houtei": _sogo_saibansho, "kn_saikosai": cg_saikosai,
    "kn_jimusho": jimusho90, "kn_shoken": shoken, "kn_kokkai": _sogo_kokkai, "kn_gendai": _sega_gendai,
    # スカイマーク
    "sm_heya": sm_heya, "sm_kaigi_2ji": lambda: sm_kaigi_clock(2), "sm_kaigi_4ji": lambda: sm_kaigi_clock(4, full=True),
    "sm_shacho": sm_shacho, "sm_shacho_fax": lambda: sm_shacho(fax=True), "sm_seisa": sm_seisa,
    "sm_shiten": sm_shiten, "sm_gate": sm_gate, "sm_kuko_yoru": kuko_yoru, "sm_kokkai": _sogo_kokkai,
    "sm_kuko": sm_kuko, "sm_kuko_sukunai": lambda: sm_kuko(sukunai=True), "sm_kinai": kinai,
    "sm_kakunoko": kakunoko, "sm_kaiken": _sega_kaiken, "sm_kaigi": kaigi, "sm_kaigi_akaji": lambda: kaigi(akaji=True),
    "sm_yakuin": lambda: yakuin(), "sm_houtei": _sogo_saibansho, "sm_saikensha": kabunushi_kaijo,
    "sm_shoken": shoken, "sm_jimusho": jimusho90, "sm_gendai": _sega_gendai,
}

# 年号カード。接頭辞ごとに "bm_card_2023" のように作る（台本が決まってから足す）
CARDS = {"bm": ["1976", "2005", "2014", "2020", "2021", "2022", "2023", "2024", "2026"], "ik": ["1961", "1970", "1994", "2013", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2025", "2026"],
         "kn": ["1887", "1961", "1968", "1998", "2002", "2003", "2004", "2005", "2006", "2007", "2026"], "sm": ["1996", "1998", "2003", "2004", "2006", "2010", "2012", "2014", "2015", "2017", "2018", "2022", "2024", "2026"]}


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
