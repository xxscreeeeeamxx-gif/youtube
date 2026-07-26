#!/usr/bin/env python3
"""うま味発見再現ドラマ（ajinomoto）用のイラスト背景8種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_aj_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402


def kitchen_now() -> Image.Image:
    """現代のキッチン（フック/論争/締め）。鍋とスープ。"""
    img = vgrad((W, H), (236, 240, 242), (222, 228, 232)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.76), (200, 190, 176), (174, 164, 150))
    # 吊り戸棚とカウンター
    for i in range(4):
        d.rectangle([140 + i * 340, 110, 420 + i * 340, 280], fill=(214, 210, 200),
                    outline=(184, 178, 166), width=4)
    d.rectangle([0, 540, W, 610], fill=(178, 168, 154))
    d.rectangle([0, 610, W, int(H * 0.76)], fill=(204, 196, 184))
    # コンロと鍋（湯気）
    d.rectangle([820, 500, 1180, 545], fill=(90, 94, 104))
    d.rounded_rectangle([880, 400, 1120, 520], radius=14, fill=(200, 90, 70))
    d.rectangle([860, 390, 1140, 412], fill=(160, 70, 56))
    for k in range(3):
        pts = [(940 + k * 60 + 10 * ((j % 2) * 2 - 1), 360 - j * 22) for j in range(5)]
        d.line(pts, fill=(226, 230, 234, 150), width=8)
    # 調味料棚
    for k in range(4):
        d.rounded_rectangle([1360 + k * 90, 460, 1420 + k * 90, 545], radius=8,
                            fill=(150, 170, 130) if k % 2 else (220, 190, 110))
    return img


def germany() -> Image.Image:
    """ドイツ・ライプツィヒの研究室（洋風・重厚）。"""
    img = vgrad((W, H), (66, 60, 70), (48, 44, 54)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (98, 78, 60), (78, 62, 48))
    # 高いアーチ窓
    for wx in (240, 1520):
        d.rounded_rectangle([wx, 130, wx + 300, 560], radius=150, fill=(150, 170, 200))
        d.rounded_rectangle([wx + 24, 154, wx + 276, 560], radius=126, fill=(196, 212, 230))
        d.line([wx + 150, 154, wx + 150, 560], fill=(110, 100, 90), width=8)
        d.line([wx + 24, 340, wx + 276, 340], fill=(110, 100, 90), width=8)
    # 実験台（フラスコ・ビュレット）
    d.rounded_rectangle([680, 560, 1360, int(H * 0.78)], radius=8, fill=(96, 74, 54))
    d.rectangle([680, 560, 1360, 596], fill=(80, 62, 46))
    d.polygon([(760, 560), (800, 480), (840, 560)], fill=(170, 210, 230))
    d.ellipse([900, 490, 970, 560], fill=(150, 200, 170))
    d.line([1050, 440, 1050, 560], fill=(180, 186, 196), width=8)
    d.rectangle([1120, 500, 1200, 560], fill=(220, 200, 120))
    # 黒板（数式）
    d.rectangle([900, 180, 1300, 420], fill=(46, 66, 56))
    d.rectangle([890, 170, 1310, 184], fill=(110, 100, 90))
    for j in range(3):
        d.line([940, 230 + j * 60, 1240 - j * 40, 230 + j * 60], fill=(210, 214, 206), width=5)
    return img


def lab_teidai() -> Image.Image:
    """東京帝国大学の研究室（和洋折衷・実験器具）。"""
    img = vgrad((W, H), (84, 78, 68), (62, 58, 50)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (140, 116, 86), (114, 96, 72))
    _window(img, d, 200, 130, 620, 500, (176, 196, 214), (214, 226, 236), (96, 84, 66))
    # 実験台（蒸発皿・ビーカー・コンロ）
    d.rounded_rectangle([740, 550, 1460, int(H * 0.77)], radius=8, fill=(110, 88, 62))
    d.rectangle([740, 550, 1460, 586], fill=(92, 74, 54))
    d.ellipse([800, 500, 940, 560], fill=(210, 214, 222))
    d.polygon([(1020, 560), (1055, 470), (1090, 560)], fill=(170, 210, 230))
    d.ellipse([1160, 490, 1230, 560], fill=(230, 210, 150))
    d.rectangle([1300, 480, 1400, 560], fill=(120, 126, 138))
    glow(img, 870, 560, 40, (255, 170, 60), 90)
    # 薬品棚
    d.rectangle([1560, 240, 1860, int(H * 0.77)], fill=(96, 80, 62))
    for r in range(4):
        for c in range(3):
            d.rounded_rectangle([1580 + c * 92, 270 + r * 150, 1646 + c * 92, 380 + r * 150],
                                radius=6, fill=(150, 190, 170) if (r + c) % 2 else (190, 170, 140))
    # 昆布の束（研究材料）
    for k in range(3):
        d.line([300 + k * 60, 620, 340 + k * 60, 780], fill=(60, 80, 60), width=26)
    return img


def home_meiji() -> Image.Image:
    """池田家の和室（湯豆腐の食卓）。"""
    img = vgrad((W, H), (96, 84, 70), (70, 62, 52)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.72), (168, 146, 106), (146, 126, 92))
    # 障子
    for sx in (110, 1520):
        d.rounded_rectangle([sx, 110, sx + 300, 620], radius=6, fill=(226, 218, 198))
        for i in range(2):
            d.line([sx + 100 + i * 100, 110, sx + 100 + i * 100, 620],
                   fill=(150, 130, 104), width=8)
        for j in range(3):
            d.line([sx, 180 + j * 150, sx + 300, 180 + j * 150],
                   fill=(150, 130, 104), width=8)
    # ちゃぶ台と湯豆腐の鍋
    d.ellipse([740, 640, 1340, 840], fill=(140, 110, 74))
    d.ellipse([760, 630, 1320, 800], fill=(160, 128, 88))
    d.ellipse([960, 620, 1140, 700], fill=(210, 214, 222))
    d.rectangle([1000, 640, 1050, 670], fill=(240, 238, 230))
    d.rectangle([1060, 650, 1100, 676], fill=(240, 238, 230))
    for k in range(2):
        pts = [(1010 + k * 70 + 8 * ((j % 2) * 2 - 1), 590 - j * 18) for j in range(5)]
        d.line(pts, fill=(230, 232, 236, 150), width=7)
    # 掛け軸
    d.rectangle([880, 150, 1040, 460], fill=(214, 202, 176))
    d.line([930, 220, 990, 400], fill=(120, 100, 80), width=9)
    return img


def shoten() -> Image.Image:
    """鈴木商店（葉山・海辺の工場兼商家）。"""
    img = vgrad((W, H), (168, 198, 220), (216, 230, 238)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 海と水平線
    d.rectangle([0, 420, W, 560], fill=(110, 160, 200))
    d.line([0, 420, W, 420], fill=(150, 190, 220), width=4)
    for k in range(8):
        d.line([80 + k * 240, 460 + (k % 3) * 30, 180 + k * 240, 460 + (k % 3) * 30],
               fill=(160, 200, 226), width=5)
    # 商家（瓦屋根）
    d.rectangle([560, 300, 1440, 560], fill=(214, 202, 178))
    d.polygon([(520, 300), (1000, 170), (1480, 300)], fill=(90, 96, 110))
    d.rectangle([640, 380, 840, 560], fill=(140, 110, 80))
    d.rectangle([1100, 380, 1380, 540], fill=(170, 158, 136))
    _floor(d, 560, (196, 180, 152), (172, 158, 134))
    # 海藻を干す台
    d.line([120, 480, 480, 480], fill=(120, 96, 70), width=10)
    d.rectangle([120, 480, 132, 620], fill=(120, 96, 70))
    d.rectangle([468, 480, 480, 620], fill=(120, 96, 70))
    for k in range(5):
        d.line([160 + k * 70, 480, 150 + k * 70, 600], fill=(70, 90, 66), width=16)
    # 樽
    for k in range(3):
        d.rounded_rectangle([1560 + k * 110, 620, 1650 + k * 110, 760], radius=14,
                            fill=(140, 110, 74))
        d.line([1560 + k * 110, 680, 1650 + k * 110, 680], fill=(100, 78, 54), width=6)
    return img


def kojo() -> Image.Image:
    """量産工場（釜と配管・蒸気）。"""
    img = vgrad((W, H), (74, 72, 80), (54, 54, 62)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (92, 86, 80), (72, 68, 62))
    _window(img, d, 180, 120, 560, 440, (176, 196, 214), (214, 226, 236), (86, 82, 74))
    # 大釜2基
    for cx in (900, 1350):
        d.ellipse([cx - 160, 420, cx + 160, 700], fill=(110, 116, 130))
        d.ellipse([cx - 160, 390, cx + 160, 500], fill=(90, 96, 110))
        d.rectangle([cx - 180, 640, cx + 180, 700], fill=(84, 90, 104))
        for k in range(2):
            pts = [(cx - 40 + k * 80 + 10 * ((j % 2) * 2 - 1), 360 - j * 20) for j in range(5)]
            d.line(pts, fill=(220, 224, 230, 130), width=8)
    # 配管
    d.line([740, 300, 1510, 300], fill=(130, 136, 150), width=16)
    d.line([900, 300, 900, 400], fill=(130, 136, 150), width=16)
    d.line([1350, 300, 1350, 400], fill=(130, 136, 150), width=16)
    # 麻袋（小麦）
    for k in range(3):
        d.rounded_rectangle([1620 + (k % 2) * 70, 640 - (k // 2) * 90, 1720 + (k % 2) * 70,
                             760 - (k // 2) * 90], radius=18, fill=(190, 160, 110))
    return img


def mise_meiji() -> Image.Image:
    """明治の店頭（味の素売り出し・のれんと台）。"""
    img = vgrad((W, H), (240, 226, 200), (250, 240, 220)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.75), (206, 186, 156), (182, 164, 138))
    # 店構え（のれん）
    d.rectangle([0, 100, W, 200], fill=(150, 120, 90))
    for k in range(5):
        d.rectangle([200 + k * 340, 200, 480 + k * 340, 420], fill=(70, 90, 130))
    # 陳列台と小瓶
    d.rounded_rectangle([700, 520, 1240, int(H * 0.75)], radius=10, fill=(160, 134, 100))
    d.rectangle([700, 520, 1240, 556], fill=(136, 112, 84))
    for k in range(4):
        d.rounded_rectangle([760 + k * 120, 440, 820 + k * 120, 528], radius=8,
                            fill=(220, 60, 60))
        d.rectangle([772 + k * 120, 460, 808 + k * 120, 510], fill=(240, 236, 226))
    # 提灯
    for lx in (300, 1620):
        d.line([lx, 60, lx, 160], fill=(90, 74, 56), width=8)
        d.ellipse([lx - 60, 160, lx + 60, 300], fill=(240, 130, 90))
        glow(img, lx, 230, 80, (255, 190, 120), 60)
    return img


def sekai_now() -> Image.Image:
    """世界の食卓（UMAMI・夜のダイニング）。"""
    img = vgrad((W, H), (40, 46, 66), (58, 64, 86)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 摩天楼の夜景（窓明かり）
    for i, (bx, bw, bh) in enumerate([(80, 240, 420), (360, 200, 340), (600, 260, 480),
                                      (1420, 240, 400), (1700, 200, 460)]):
        d.rectangle([bx, 560 - bh, bx + bw, 560], fill=(30, 36, 52))
        for r in range(bh // 70):
            for c in range(bw // 70):
                if (r + c + i) % 3:
                    d.rectangle([bx + 14 + c * 70, 560 - bh + 14 + r * 70,
                                 bx + 48 + c * 70, 560 - bh + 48 + r * 70],
                                fill=(240, 210, 130))
    glow(img, 1120, 200, 120, (240, 220, 160), 60)
    d.ellipse([1070, 150, 1170, 250], fill=(240, 226, 180))
    _floor(d, 560, (72, 60, 56), (58, 48, 46))
    # ダイニングテーブルと世界の料理
    d.rounded_rectangle([560, 620, 1440, 800], radius=20, fill=(120, 90, 64))
    d.ellipse([640, 600, 800, 680], fill=(220, 222, 228))
    d.ellipse([680, 620, 760, 660], fill=(200, 90, 70))
    d.ellipse([920, 590, 1080, 670], fill=(220, 222, 228))
    d.ellipse([960, 610, 1040, 650], fill=(230, 190, 110))
    d.ellipse([1200, 600, 1360, 680], fill=(220, 222, 228))
    d.ellipse([1240, 620, 1320, 660], fill=(130, 170, 120))
    return img


def engawa_yu() -> Image.Image:
    """晩年の縁側（夕景・庭と湯豆腐の膳）。"""
    img = vgrad((W, H), (248, 178, 116), (255, 222, 172)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    glow(img, 420, 260, 190, (255, 216, 140), 90)
    d.ellipse([350, 190, 490, 330], fill=(255, 236, 186))
    # 庭（松と灯籠）
    d.rectangle([0, 520, W, 620], fill=(150, 130, 96))
    d.rectangle([160, 340, 200, 540], fill=(110, 84, 58))
    d.ellipse([60, 220, 320, 400], fill=(100, 130, 90))
    d.rectangle([540, 430, 590, 540], fill=(150, 152, 158))
    d.ellipse([520, 390, 610, 450], fill=(130, 132, 140))
    # 縁側（板の間）
    d.rectangle([0, 620, W, H], fill=(170, 136, 96))
    for k in range(0, W, 200):
        d.line([k, 620, k, H], fill=(146, 116, 82), width=6)
    d.rectangle([0, 620, W, 644], fill=(146, 116, 82))
    # 障子（右側・室内）
    d.rounded_rectangle([1420, 120, 1900, 640], radius=6, fill=(232, 224, 204))
    for i in range(3):
        d.line([1540 + i * 120, 120, 1540 + i * 120, 640], fill=(150, 130, 104), width=8)
    for j in range(3):
        d.line([1420, 200 + j * 150, 1900, 200 + j * 150], fill=(150, 130, 104), width=8)
    # 膳と湯豆腐
    d.rounded_rectangle([840, 700, 1180, 800], radius=10, fill=(120, 90, 60))
    d.ellipse([940, 660, 1080, 724], fill=(214, 218, 226))
    d.rectangle([980, 676, 1020, 700], fill=(242, 240, 232))
    return img


PAINTERS = {
    "il_aj_kitchen": kitchen_now,
    "il_aj_germany": germany,
    "il_aj_lab": lab_teidai,
    "il_aj_home": home_meiji,
    "il_aj_shoten": shoten,
    "il_aj_kojo": kojo,
    "il_aj_mise": mise_meiji,
    "il_aj_sekai": sekai_now,
    "il_aj_engawa": engawa_yu,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
