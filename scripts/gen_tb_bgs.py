#!/usr/bin/env python3
"""点字ブロック再現ドラマ（tenji-block）用のイラスト背景10種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_tb_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402

YELLOW = (240, 200, 60)
YELLOW_DK = (200, 160, 40)


def _tenji_row(d, y0, y1, x0=0, x1=W, dot=True, step=140):
    """点字ブロックの帯を描く。dot=True で点状、False で線状。"""
    d.rectangle([x0, y0, x1, y1], fill=YELLOW)
    h = y1 - y0
    if dot:
        for cx in range(x0 + step // 2, x1, step):
            for r in range(2):
                for c in range(3):
                    px = cx - 40 + c * 40
                    py = y0 + h // 3 + r * (h // 3)
                    d.ellipse([px - 12, py - 8, px + 12, py + 8], fill=YELLOW_DK)
    else:
        for cx in range(x0 + step // 2, x1, step):
            for c in range(3):
                px = cx - 40 + c * 40
                d.rectangle([px - 8, y0 + 14, px + 8, y1 - 14], fill=YELLOW_DK)


def st_now() -> Image.Image:
    """現代の駅前歩道（フック/実用/締め）。黄色い点字ブロックが伸びる。"""
    img = vgrad((W, H), (196, 214, 230), (226, 234, 242)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # ビル群
    for i, (bx, bw, bh) in enumerate([(60, 300, 420), (420, 260, 340), (1240, 300, 400),
                                      (1600, 260, 460)]):
        col = (168, 180, 196) if i % 2 else (150, 162, 180)
        d.rectangle([bx, 560 - bh, bx + bw, 560], fill=col)
        for r in range(bh // 90):
            for c in range(bw // 90):
                d.rectangle([bx + 24 + c * 90, 560 - bh + 24 + r * 90,
                             bx + 74 + c * 90, 560 - bh + 74 + r * 90],
                            fill=(214, 226, 238))
    # 駅舎
    d.rounded_rectangle([760, 300, 1200, 560], radius=10, fill=(120, 132, 150))
    d.rectangle([800, 380, 1160, 560], fill=(90, 100, 116))
    d.rounded_rectangle([840, 330, 1120, 372], radius=8, fill=(230, 236, 242))
    _floor(d, 560, (200, 202, 206), (176, 178, 184))
    # 歩道と点字ブロック（線状が奥へ）
    _tenji_row(d, 700, 800, dot=False)
    d.rectangle([0, 800, W, H], fill=(186, 188, 194))
    for k in range(6):
        d.line([200 + k * 300, 800, 200 + k * 300, H], fill=(166, 168, 176), width=6)
    return img


def home_okayama() -> Image.Image:
    """三宅家の居間（旅館の一室・図面と発明品）。"""
    img = vgrad((W, H), (96, 84, 70), (70, 60, 50)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.75), (150, 122, 88), (124, 100, 72))
    # 障子
    for sx in (110, 1520):
        d.rounded_rectangle([sx, 110, sx + 300, 640], radius=6, fill=(226, 218, 198))
        for i in range(2):
            d.line([sx + 100 + i * 100, 110, sx + 100 + i * 100, 640],
                   fill=(150, 130, 104), width=8)
        for j in range(3):
            d.line([sx, 180 + j * 150, sx + 300, 180 + j * 150],
                   fill=(150, 130, 104), width=8)
    # 文机と図面
    d.rounded_rectangle([700, 600, 1300, int(H * 0.75)], radius=8, fill=(120, 94, 64))
    d.rectangle([700, 600, 1300, 634], fill=(100, 78, 54))
    d.rectangle([780, 540, 1040, 610], fill=(240, 236, 224))
    for j in range(3):
        d.line([800, 560 + j * 16, 1020, 560 + j * 16], fill=(140, 150, 170), width=4)
    d.ellipse([1100, 550, 1200, 606], fill=(190, 186, 176))
    # 掛け軸
    d.rectangle([880, 150, 1040, 460], fill=(214, 202, 176))
    d.line([920, 220, 1000, 380], fill=(120, 100, 80), width=10)
    return img


def kosaten_showa() -> Image.Image:
    """昭和の交差点（白い杖の人を目撃した場所）。"""
    img = vgrad((W, H), (176, 186, 198), (208, 214, 222)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 低い商店の並び
    for i, bx in enumerate(range(40, W, 420)):
        col = (170, 156, 136) if i % 2 else (150, 140, 124)
        d.rectangle([bx, 300, bx + 360, 560], fill=col)
        d.rectangle([bx + 30, 380, bx + 330, 560], fill=(110, 102, 90))
        d.rectangle([bx + 20, 310, bx + 340, 360], fill=(210, 200, 180))
    _floor(d, 560, (170, 172, 178), (150, 152, 158))
    # 車道と横断歩道（縞）
    d.rectangle([0, 720, W, H], fill=(96, 100, 108))
    for k in range(8):
        d.rectangle([120 + k * 240, 740, 240 + k * 240, H - 20], fill=(220, 222, 226))
    # 電柱
    d.rectangle([1700, 120, 1740, 560], fill=(110, 104, 96))
    d.rectangle([1650, 170, 1790, 200], fill=(110, 104, 96))
    return img


def niwa() -> Image.Image:
    """三宅家の庭（犬小屋とコケ・岩橋との対話の場）。"""
    img = vgrad((W, H), (150, 190, 220), (200, 220, 234)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 板塀
    d.rectangle([0, 260, W, 620], fill=(150, 124, 92))
    for k in range(0, W, 130):
        d.line([k, 260, k, 620], fill=(126, 104, 76), width=8)
    d.rectangle([0, 260, W, 290], fill=(126, 104, 76))
    _floor(d, 620, (128, 148, 96), (108, 128, 82))
    # コケの緑地帯と土の境目
    d.rounded_rectangle([160, 760, 900, H - 60], radius=30, fill=(96, 138, 76))
    for k in range(12):
        d.ellipse([200 + (k % 6) * 110, 780 + (k // 6) * 90,
                   260 + (k % 6) * 110, 820 + (k // 6) * 90], fill=(112, 156, 88))
    d.rectangle([960, 740, 1760, H - 40], fill=(146, 118, 84))
    # 犬小屋
    d.rounded_rectangle([1460, 400, 1820, 620], radius=10, fill=(140, 104, 66))
    d.polygon([(1430, 410), (1640, 290), (1850, 410)], fill=(110, 80, 50))
    d.ellipse([1560, 470, 1720, 620], fill=(70, 56, 44))
    # 庭石
    d.ellipse([1000, 640, 1140, 720], fill=(150, 152, 158))
    glow(img, 300, 200, 160, (255, 240, 200), 60)
    d.ellipse([250, 130, 350, 230], fill=(255, 244, 208))
    return img


def koujou() -> Image.Image:
    """試作の作業場（セメント型と試作ブロックの山）。"""
    img = vgrad((W, H), (70, 74, 84), (50, 54, 62)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.76), (86, 82, 76), (66, 62, 58))
    _window(img, d, 180, 120, 600, 480, (176, 196, 214), (214, 226, 238), (86, 82, 74))
    # 作業台と試作ブロック
    d.rounded_rectangle([720, 560, 1480, int(H * 0.76)], radius=8, fill=(112, 92, 66))
    d.rectangle([720, 560, 1480, 596], fill=(92, 76, 56))
    for k in range(3):
        bx = 780 + k * 230
        d.rectangle([bx, 470, bx + 180, 560], fill=YELLOW)
        for r in range(2):
            for c in range(4):
                d.ellipse([bx + 18 + c * 42, 486 + r * 38,
                           bx + 42 + c * 42, 504 + r * 38], fill=YELLOW_DK)
    # ブロックの山（在庫）
    for r in range(4):
        for c in range(3 - (r % 2)):
            bx = 1560 + c * 110 + (r % 2) * 55
            by = int(H * 0.76) - 70 - r * 64
            d.rectangle([bx, by, bx + 100, by + 60], fill=(206, 176, 84))
            d.rectangle([bx, by, bx + 100, by + 12], fill=(178, 148, 64))
    # 裸電球
    d.line([1060, 0, 1060, 140], fill=(56, 52, 46), width=6)
    glow(img, 1060, 180, 110, (255, 216, 140), 90)
    d.ellipse([1034, 140, 1086, 212], fill=(255, 226, 150))
    return img


def gakko() -> Image.Image:
    """盲学校近くの交差点（1967敷設の場）。黄色い点状ブロックが敷かれた歩道。"""
    img = vgrad((W, H), (255, 226, 170), (255, 240, 210)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 学校の建物と塀
    d.rectangle([120, 220, 900, 560], fill=(198, 188, 168))
    for c in range(5):
        d.rectangle([170 + c * 150, 280, 280 + c * 150, 400], fill=(230, 236, 242))
    d.rectangle([120, 430, 900, 470], fill=(170, 160, 140))
    d.rectangle([0, 500, W, 560], fill=(180, 168, 146))
    _floor(d, 560, (206, 200, 190), (184, 178, 168))
    # 点状ブロックの帯（横断歩道手前）
    _tenji_row(d, 690, 800, dot=True)
    # 車道と横断歩道
    d.rectangle([0, 800, W, H], fill=(100, 104, 112))
    for k in range(8):
        d.rectangle([100 + k * 240, 820, 220 + k * 240, H - 24], fill=(222, 224, 228))
    # 木
    d.rectangle([1560, 330, 1610, 560], fill=(120, 94, 66))
    d.ellipse([1430, 160, 1740, 400], fill=(120, 160, 96))
    glow(img, 1680, 130, 150, (255, 236, 180), 70)
    return img


def yakusho() -> Image.Image:
    """役所の窓口（門前払いの場）。"""
    img = vgrad((W, H), (188, 190, 196), (168, 172, 180)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (150, 148, 144), (128, 126, 122))
    # カウンター
    d.rectangle([200, 560, 1720, int(H * 0.77)], fill=(140, 118, 88))
    d.rectangle([200, 560, 1720, 600], fill=(118, 98, 72))
    # 窓口の仕切り
    for k in range(3):
        d.rectangle([300 + k * 460, 300, 640 + k * 460, 560], fill=(210, 214, 220))
        d.rectangle([300 + k * 460, 300, 640 + k * 460, 340], fill=(150, 154, 162))
        d.rectangle([340 + k * 460, 360, 600 + k * 460, 520], fill=(178, 186, 196))
    # 書類棚
    d.rectangle([40, 260, 240, int(H * 0.77)], fill=(120, 112, 100))
    for r in range(5):
        d.rectangle([56, 290 + r * 130, 224, 380 + r * 130], fill=(160, 152, 138))
    # 蛍光灯
    for k in range(3):
        d.rectangle([360 + k * 500, 80, 760 + k * 500, 104], fill=(235, 240, 244))
    return img


def tokyo() -> Image.Image:
    """東京・高田馬場の街並み（1万枚の敷設）。"""
    img = vgrad((W, H), (150, 170, 196), (200, 212, 226)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 高めのビル群
    for i, (bx, bw, bh) in enumerate([(0, 260, 460), (300, 220, 380), (560, 280, 500),
                                      (880, 240, 420), (1160, 280, 520), (1480, 240, 400),
                                      (1760, 200, 460)]):
        col = (150, 160, 178) if i % 2 else (132, 142, 160)
        d.rectangle([bx, 560 - bh, bx + bw, 560], fill=col)
        for r in range(bh // 80):
            for c in range(bw // 80):
                d.rectangle([bx + 18 + c * 80, 560 - bh + 18 + r * 80,
                             bx + 58 + c * 80, 560 - bh + 58 + r * 80],
                            fill=(226, 232, 240))
    # 電車の高架
    d.rectangle([0, 480, W, 540], fill=(110, 120, 136))
    d.rounded_rectangle([300, 420, 900, 500], radius=14, fill=(210, 190, 70))
    d.rectangle([340, 440, 860, 480], fill=(150, 160, 178))
    _floor(d, 560, (196, 198, 202), (174, 176, 182))
    # 点字ブロックの道（線状が長く伸びる）
    _tenji_row(d, 700, 800, dot=False)
    d.rectangle([0, 800, W, H], fill=(184, 186, 192))
    return img


def homu() -> Image.Image:
    """駅のホーム（端の警告ブロック）。"""
    img = vgrad((W, H), (60, 66, 80), (44, 50, 62)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 屋根と柱
    d.rectangle([0, 0, W, 90], fill=(80, 86, 98))
    for k in range(4):
        d.rectangle([220 + k * 480, 90, 260 + k * 480, 620], fill=(120, 126, 138))
    # 駅名標
    d.rounded_rectangle([760, 200, 1160, 320], radius=14, fill=(230, 236, 242))
    d.rectangle([760, 290, 1160, 320], fill=(90, 160, 90))
    _floor(d, 620, (150, 148, 152), (128, 126, 130))
    # ホーム端の点状ブロック
    _tenji_row(d, 700, 810, dot=True)
    # 線路（下）
    d.rectangle([0, 810, W, H], fill=(36, 38, 46))
    d.rectangle([0, 880, W, 900], fill=(90, 92, 100))
    d.rectangle([0, 980, W, 1000], fill=(90, 92, 100))
    for k in range(0, W, 160):
        d.rectangle([k, 860, k + 100, 1020], fill=(60, 54, 48))
    return img


def sekai_now() -> Image.Image:
    """現代の世界の街（75カ国への広がり・夕景）。"""
    img = vgrad((W, H), (250, 190, 120), (255, 226, 180)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    glow(img, 960, 240, 220, (255, 220, 150), 90)
    d.ellipse([880, 160, 1040, 320], fill=(255, 236, 190))
    # 世界の街並み（時計塔・ビル・タワー）
    d.rectangle([140, 300, 320, 560], fill=(140, 120, 110))
    d.polygon([(140, 300), (230, 220), (320, 300)], fill=(110, 94, 88))
    d.ellipse([200, 340, 260, 400], fill=(240, 236, 224))
    for bx, bw, bh in [(420, 220, 320), (700, 260, 400), (1320, 240, 360), (1640, 220, 300)]:
        d.rectangle([bx, 560 - bh, bx + bw, 560], fill=(160, 140, 130))
        for r in range(bh // 90):
            for c in range(bw // 90):
                d.rectangle([bx + 20 + c * 90, 560 - bh + 20 + r * 90,
                             bx + 60 + c * 90, 560 - bh + 60 + r * 90],
                            fill=(255, 220, 170))
    # タワー
    d.polygon([(1080, 560), (1140, 220), (1200, 560)], fill=(150, 120, 104))
    d.line([1140, 220, 1140, 160], fill=(150, 120, 104), width=10)
    _floor(d, 560, (216, 196, 172), (192, 172, 150))
    # 点字ブロック（線状）
    _tenji_row(d, 700, 800, dot=False)
    d.rectangle([0, 800, W, H], fill=(206, 186, 164))
    return img


PAINTERS = {
    "il_tb_st": st_now,
    "il_tb_home": home_okayama,
    "il_tb_kosaten": kosaten_showa,
    "il_tb_niwa": niwa,
    "il_tb_koujou": koujou,
    "il_tb_gakko": gakko,
    "il_tb_yakusho": yakusho,
    "il_tb_tokyo": tokyo,
    "il_tb_homu": homu,
    "il_tb_sekai": sekai_now,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
