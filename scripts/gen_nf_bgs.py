#!/usr/bin/env python3
"""光ファイバーの再現ドラマ（nishizawa-fiber）用のイラスト背景12種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
仙台の研究室（木と緑）と、役所・企業の冷たい灰色、の対比で場面を分けている。
実行: PYTHONPATH=. python3 scripts/gen_nf_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402


def _oscillo(d, x, y, w=260, h=200, trace=(120, 240, 160)):
    """オシロスコープを1台。y は上端。"""
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=(78, 80, 88))
    d.rounded_rectangle([x + 16, y + 16, x + w - 90, y + h - 20], radius=6,
                        fill=(18, 34, 26))
    pts = []
    for i in range(0, w - 106, 6):
        import math
        pts.append((x + 20 + i, y + (h - 36) // 2 + 6
                    + int(26 * math.sin(i / 16.0))))
    d.line(pts, fill=trace, width=4)
    for k in range(3):
        d.ellipse([x + w - 70, y + 24 + k * 46, x + w - 34, y + 60 + k * 46],
                  fill=(150, 156, 166))


def kenkyushitsu() -> Image.Image:
    """東北大の研究室。木の机、オシロ、黒板。"""
    img = vgrad((W, H), (170, 162, 144), (146, 138, 122)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 690, (128, 106, 78), (106, 88, 64))
    # 黒板
    d.rounded_rectangle([90, 130, 900, 520], radius=6, fill=(92, 76, 58))
    d.rectangle([108, 148, 882, 502], fill=(46, 62, 54))
    for j, y in enumerate((200, 260, 320)):
        d.line([150, y, 150 + 180 * (j + 2), y], fill=(210, 214, 206), width=5)
    d.ellipse([620, 350, 800, 460], outline=(210, 214, 206), width=6)
    # 実験台とオシロ
    d.rounded_rectangle([120, 560, 1180, 700], radius=6, fill=(140, 112, 78))
    d.rectangle([120, 560, 1180, 592], fill=(116, 92, 64))
    _oscillo(d, 700, 380)
    _window(img, d, 1400, 150, 1800, 470, (170, 198, 220), (220, 232, 240))
    return img


def jitsuken() -> Image.Image:
    """暗くした実験室。炉の赤い光と、ガラスを引く装置。"""
    img = vgrad((W, H), (44, 44, 54), (30, 30, 40)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 700, (58, 52, 48), (44, 40, 38))
    # 縦型の線引き炉
    d.rounded_rectangle([760, 90, 1060, 470], radius=10, fill=(74, 78, 88))
    d.rectangle([800, 300, 1020, 420], fill=(60, 30, 24))
    d.ellipse([840, 320, 980, 400], fill=(240, 140, 60))
    glow(img, 910, 360, 460, (255, 160, 70), 52)
    # 引かれるガラス（細い線）
    d.line([910, 470, 910, 700], fill=(200, 220, 236), width=6)
    d.ellipse([840, 660, 980, 720], fill=(90, 96, 106))
    # 巻き取りドラム
    d.ellipse([1180, 520, 1460, 720], fill=(96, 102, 112), outline=(70, 76, 86), width=8)
    d.ellipse([1270, 590, 1370, 650], fill=(66, 72, 82))
    # 計測ラック
    d.rounded_rectangle([80, 260, 520, 700], radius=8, fill=(64, 68, 78))
    for r in range(4):
        d.rectangle([100, 290 + r * 100, 500, 360 + r * 100], fill=(44, 60, 54))
        d.ellipse([440, 306 + r * 100, 480, 346 + r * 100], fill=(120, 220, 150))
    return img


def kokuban() -> Image.Image:
    """黒板の前。屈折率の説明をする場面。"""
    img = vgrad((W, H), (150, 146, 136), (128, 124, 116)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 720, (116, 98, 74), (94, 80, 62))
    d.rounded_rectangle([60, 90, 1860, 620], radius=6, fill=(84, 70, 54))
    d.rectangle([84, 114, 1836, 596], fill=(44, 60, 52))
    # 管の断面と、中を蛇行する光
    d.rectangle([300, 250, 1500, 460], outline=(212, 216, 208), width=6)
    d.line([300, 355, 1500, 355], fill=(150, 160, 152), width=3)
    import math
    pts = [(300 + i, 355 + int(70 * math.sin(i / 130.0))) for i in range(0, 1201, 8)]
    d.line(pts, fill=(250, 214, 90), width=6)
    # 屈折率の目盛り
    for k in range(5):
        d.line([220, 260 + k * 50, 280, 260 + k * 50], fill=(180, 200, 190), width=4)
    d.rectangle([84, 596, 1836, 620], fill=(70, 58, 46))
    return img


def denden() -> Image.Image:
    """電電公社の研究所。灰色の応接。断られる場所。"""
    img = vgrad((W, H), (196, 198, 200), (172, 174, 178)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 680, (150, 150, 154), (130, 130, 136))
    d.rectangle([0, 470, W, 680], fill=(160, 160, 164))
    d.line([0, 470, W, 470], fill=(140, 140, 146), width=6)
    _window(img, d, 1330, 140, 1810, 450, (176, 190, 204), (214, 224, 232))
    # 書類棚
    d.rectangle([80, 150, 620, 470], fill=(150, 148, 144))
    for r in range(3):
        d.rectangle([96, 176 + r * 100, 604, 188 + r * 100], fill=(128, 126, 122))
        for c in range(9):
            d.rectangle([112 + c * 54, 196 + r * 100, 148 + c * 54, 268 + r * 100],
                        fill=(196, 194, 188) if (r + c) % 2 else (176, 174, 170))
    # 応接テーブルとソファ
    d.rounded_rectangle([700, 700, 1300, 830], radius=8, fill=(120, 122, 128))
    d.rectangle([700, 700, 1300, 732], fill=(102, 104, 110))
    for x in (620, 1320):
        d.rounded_rectangle([x, 640, x + 180, 880], radius=14, fill=(96, 100, 110))
    # 壁の掲示
    d.rectangle([780, 200, 1180, 400], fill=(226, 226, 222), outline=(160, 160, 156), width=6)
    for j in range(4):
        d.line([812, 240 + j * 38, 1148, 240 + j * 38], fill=(170, 172, 176), width=5)
    return img


def gakkai() -> Image.Image:
    """学会の会場。演台と、並んだ椅子の背。"""
    img = vgrad((W, H), (58, 58, 74), (40, 40, 54)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # スクリーン
    d.rounded_rectangle([420, 110, 1500, 600], radius=6, fill=(30, 30, 44))
    d.rectangle([446, 136, 1474, 574], fill=(226, 228, 232))
    for j in range(5):
        d.line([500, 200 + j * 70, 500 + 180 * (j % 3 + 3), 200 + j * 70],
               fill=(150, 156, 168), width=6)
    glow(img, 960, 350, 700, (240, 240, 250), 22)
    _floor(d, 700, (48, 48, 62), (36, 36, 48))
    # 演台
    d.rounded_rectangle([120, 560, 400, 780], radius=8, fill=(76, 66, 62))
    d.rectangle([120, 560, 400, 592], fill=(60, 52, 50))
    # 客席の背
    for r in range(2):
        for x in range(560, W, 210):
            d.rounded_rectangle([x, 780 + r * 90, x + 160, 900 + r * 90],
                                radius=10, fill=(62, 60, 76))
    return img


def kigyou() -> Image.Image:
    """企業の会議室。特許の話をする場所。"""
    img = vgrad((W, H), (206, 202, 192), (182, 178, 168)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 700, (146, 132, 110), (124, 112, 94))
    _window(img, d, 1340, 130, 1810, 470, (180, 200, 218), (220, 230, 238))
    # 壁の社章枠と表彰状
    d.rectangle([120, 160, 520, 420], fill=(216, 212, 202), outline=(160, 154, 142), width=8)
    for j in range(5):
        d.line([160, 210 + j * 40, 480, 210 + j * 40], fill=(176, 170, 158), width=5)
    # 長机
    d.rounded_rectangle([260, 720, 1660, 880], radius=12, fill=(150, 128, 98))
    d.rectangle([260, 720, 1660, 756], fill=(128, 108, 82))
    for bx in (420, 900, 1360):
        d.rectangle([bx, 690, bx + 180, 726], fill=(244, 242, 234),
                    outline=(196, 192, 182), width=3)
    return img


def america() -> Image.Image:
    """アメリカの研究所。明るい実験室と星条旗の色みだけ示唆する。"""
    img = vgrad((W, H), (226, 232, 238), (200, 208, 218)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 660, (196, 202, 210), (176, 182, 192))
    _window(img, d, 1280, 120, 1810, 470, (156, 194, 226), (218, 232, 244))
    # 白い実験台とレーザー装置
    d.rounded_rectangle([120, 560, 1180, 700], radius=8, fill=(238, 240, 244))
    d.rectangle([120, 560, 1180, 594], fill=(212, 216, 224))
    d.rounded_rectangle([300, 430, 700, 566], radius=8, fill=(120, 128, 140))
    d.rectangle([700, 480, 1080, 492], fill=(230, 70, 70))
    glow(img, 900, 486, 300, (255, 90, 90), 40)
    d.ellipse([1060, 456, 1140, 516], fill=(90, 96, 108))
    # 掲示板
    d.rectangle([80, 150, 520, 460], fill=(232, 234, 238), outline=(190, 194, 202), width=6)
    for i, (x, y) in enumerate([(110, 180), (300, 200), (140, 320), (330, 340)]):
        d.rectangle([x, y, x + 150, y + 100],
                    fill=(206, 224, 240) if i % 2 else (240, 226, 226))
    return img


def jitaku() -> Image.Image:
    """西澤家の書斎。夜、机の灯りひとつ。"""
    img = vgrad((W, H), (74, 66, 58), (52, 46, 42)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 700, (96, 78, 58), (78, 64, 48))
    # 本棚
    d.rectangle([90, 130, 660, 660], fill=(80, 62, 46))
    for r in range(4):
        d.rectangle([104, 156 + r * 128, 646, 168 + r * 128], fill=(62, 48, 36))
        for c in range(10):
            d.rectangle([118 + c * 52, 176 + r * 128, 152 + c * 52, 272 + r * 128],
                        fill=[(140, 60, 54), (60, 84, 130), (200, 186, 140),
                              (86, 120, 86)][(r + c) % 4])
    # 机とスタンド
    d.rounded_rectangle([760, 580, 1440, 720], radius=6, fill=(112, 88, 62))
    d.rectangle([760, 580, 1440, 612], fill=(92, 72, 50))
    d.polygon([(1240, 300), (1400, 300), (1440, 400), (1200, 400)], fill=(70, 74, 84))
    d.rectangle([1310, 400, 1326, 586], fill=(70, 74, 84))
    glow(img, 1320, 470, 520, (255, 236, 170), 44)
    # 原稿の束
    for k in range(4):
        d.rectangle([860 + k * 6, 546 - k * 12, 1080 + k * 6, 586 - k * 12],
                    fill=(238, 234, 222), outline=(190, 184, 170), width=3)
    return img


def hikari_michi() -> Image.Image:
    """光が走る抽象背景。仕組みの説明や、現代のネットの場面に。"""
    img = vgrad((W, H), (14, 26, 44), (24, 42, 70)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    import math
    for k in range(7):
        y0 = 120 + k * 130
        pts = [(x, y0 + int(34 * math.sin((x + k * 90) / 150.0)))
               for x in range(-40, W + 40, 10)]
        col = (90, 200, 240) if k % 2 else (140, 160, 250)
        d.line(pts, fill=col, width=5)
    for k, x in enumerate(range(120, W, 260)):
        glow(img, x, 200 + (k % 4) * 190, 220, (120, 220, 255), 30)
    return img


def kyoshitsu() -> Image.Image:
    """仙台の中学校の教室。物理の授業の場面。"""
    img = vgrad((W, H), (198, 194, 178), (176, 172, 158)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, 700, (140, 116, 84), (118, 98, 70))
    # 黒板と教壇
    d.rounded_rectangle([200, 120, 1500, 540], radius=4, fill=(86, 72, 56))
    d.rectangle([220, 140, 1480, 520], fill=(48, 64, 56))
    for j in range(3):
        d.line([280, 200 + j * 70, 280 + 220 * (j + 2), 200 + j * 70],
               fill=(206, 210, 202), width=5)
    d.rectangle([160, 700, 1540, 760], fill=(150, 126, 92))
    # 窓
    _window(img, d, 1600, 160, 1860, 520, (180, 206, 226), (222, 234, 242))
    # 机の列
    for r in range(2):
        for x in range(120, W, 300):
            d.rounded_rectangle([x, 800 + r * 100, x + 220, 840 + r * 100],
                                radius=4, fill=(168, 140, 102))
    return img


def jushou() -> Image.Image:
    """授賞式。落ち着いた壇上。晩年の場面。"""
    img = vgrad((W, H), (40, 36, 48), (26, 24, 34)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W, 150], fill=(72, 58, 46))
    d.rounded_rectangle([300, 210, 1620, 640], radius=8, fill=(52, 46, 60))
    d.rounded_rectangle([420, 270, 1500, 390], radius=6, fill=(226, 222, 214))
    for k in range(2):
        d.rectangle([620 + k * 400, 450, 900 + k * 400, 540], fill=(74, 66, 84))
    _floor(d, 700, (48, 42, 54), (36, 32, 42))
    d.rounded_rectangle([740, 700, 1180, 940], radius=8, fill=(88, 70, 58))
    d.rectangle([740, 700, 1180, 740], fill=(70, 56, 46))
    for x in (280, 1640):
        glow(img, x, 320, 380, (255, 238, 190), 30)
    return img


def ima_heya() -> Image.Image:
    """現代の部屋（茶番用）。ルーターとスマホ。"""
    img = vgrad((W, H), (234, 236, 242), (212, 216, 226)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _window(img, d, 1380, 140, 1810, 470, (172, 202, 228), (224, 236, 244))
    _floor(d, 660, (198, 200, 208), (178, 180, 190))
    # 壁のポスター
    d.rounded_rectangle([180, 170, 560, 500], radius=8, fill=(246, 248, 250),
                        outline=(202, 206, 214), width=6)
    import math
    pts = [(210 + i, 340 + int(50 * math.sin(i / 40.0))) for i in range(0, 321, 6)]
    d.line(pts, fill=(90, 170, 230), width=6)
    # 机とルーター
    d.rounded_rectangle([640, 700, 1300, 870], radius=10, fill=(190, 178, 162))
    d.rectangle([640, 700, 1300, 736], fill=(166, 154, 138))
    d.rounded_rectangle([760, 620, 980, 706], radius=8, fill=(70, 74, 84))
    for k in range(3):
        d.ellipse([790 + k * 46, 650, 812 + k * 46, 672], fill=(120, 230, 160))
    d.line([980, 640, 1080, 560], fill=(70, 74, 84), width=8)
    d.line([970, 646, 1040, 548], fill=(70, 74, 84), width=8)
    # スマホ
    d.rounded_rectangle([1120, 636, 1220, 706], radius=8, fill=(48, 50, 60))
    d.rounded_rectangle([1130, 646, 1210, 696], radius=5, fill=(140, 200, 230))
    return img


PAINTERS = {
    "il_nf_kenkyu": kenkyushitsu,
    "il_nf_jitsuken": jitsuken,
    "il_nf_kokuban": kokuban,
    "il_nf_denden": denden,
    "il_nf_gakkai": gakkai,
    "il_nf_kigyou": kigyou,
    "il_nf_america": america,
    "il_nf_jitaku": jitaku,
    "il_nf_hikari": hikari_michi,
    "il_nf_kyoshitsu": kyoshitsu,
    "il_nf_jushou": jushou,
    "il_nf_ima": ima_heya,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
