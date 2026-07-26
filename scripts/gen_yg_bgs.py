#!/usr/bin/env python3
"""横井軍平再現ドラマ（yokoi-gunpei）用のイラスト背景7種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_yg_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402


def living_now() -> Image.Image:
    """現代のリビング（フック/遺産/締め）。テレビとゲーム機。"""
    img = vgrad((W, H), (232, 228, 220), (244, 240, 232)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.75), (196, 176, 150), (170, 152, 130))
    _window(img, d, 160, 120, 640, 520, (170, 200, 224), (214, 230, 240), (196, 188, 172))
    # テレビとゲーム画面
    d.rounded_rectangle([820, 200, 1420, 560], radius=14, fill=(40, 44, 54))
    d.rectangle([850, 230, 1390, 520], fill=(90, 160, 130))
    d.rectangle([900, 280, 1000, 360], fill=(240, 220, 90))
    d.rectangle([1150, 320, 1330, 400], fill=(220, 120, 110))
    d.rectangle([1080, 560, 1160, 600], fill=(90, 94, 104))
    # ソファ
    d.rounded_rectangle([1540, 480, 1880, 700], radius=20, fill=(150, 120, 100))
    d.rounded_rectangle([1540, 420, 1880, 520], radius=20, fill=(170, 138, 114))
    # 棚のレトロゲーム機
    d.rounded_rectangle([60, 560, 360, 700], radius=10, fill=(120, 104, 88))
    d.rounded_rectangle([100, 590, 200, 660], radius=8, fill=(200, 200, 206))
    d.rectangle([118, 602, 182, 636], fill=(120, 150, 90))
    return img


def kojo_showa() -> Image.Image:
    """昭和の任天堂工場（花札の印刷機と配電盤・保全係の職場）。"""
    img = vgrad((W, H), (92, 84, 72), (66, 60, 52)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (104, 92, 78), (80, 72, 62))
    _window(img, d, 180, 120, 560, 460, (176, 196, 214), (214, 226, 236), (86, 78, 66))
    # 印刷機（ローラーと台）
    d.rounded_rectangle([700, 460, 1300, int(H * 0.77)], radius=10, fill=(90, 96, 110))
    d.ellipse([760, 400, 900, 540], fill=(70, 76, 90))
    d.ellipse([960, 400, 1100, 540], fill=(70, 76, 90))
    d.rectangle([700, 560, 1300, 590], fill=(70, 76, 90))
    # 刷り上がった花札（赤い札の列）
    for k in range(6):
        d.rounded_rectangle([740 + k * 90, 620, 800 + k * 90, 700], radius=6,
                            fill=(200, 70, 70))
        d.ellipse([756 + k * 90, 640, 784 + k * 90, 668], fill=(240, 220, 200))
    # 配電盤
    d.rounded_rectangle([1480, 240, 1860, int(H * 0.77)], radius=10, fill=(76, 82, 96))
    for r in range(3):
        for c in range(3):
            col = (120, 200, 140) if (r + c) % 2 else (220, 200, 90)
            d.ellipse([1520 + c * 110, 290 + r * 130, 1570 + c * 110, 340 + r * 130],
                      fill=col)
    d.rectangle([1500, 660, 1840, 700], fill=(60, 66, 78))
    # 裸電球
    d.line([1100, 0, 1100, 130], fill=(56, 52, 46), width=6)
    glow(img, 1100, 170, 110, (255, 216, 140), 90)
    d.ellipse([1074, 130, 1126, 202], fill=(255, 226, 150))
    return img


def shacho() -> Image.Image:
    """社長室（重厚な机と本棚）。"""
    img = vgrad((W, H), (70, 60, 54), (50, 44, 40)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (110, 84, 60), (88, 68, 50))
    # 大きな窓とカーテン
    _window(img, d, 760, 120, 1240, 520, (150, 170, 196), (200, 214, 228), (90, 74, 58))
    for sx in (700, 1240):
        d.rectangle([sx, 100, sx + 60, 560], fill=(120, 60, 56))
    # 社長机
    d.rounded_rectangle([760, 560, 1460, int(H * 0.78)], radius=10, fill=(88, 62, 44))
    d.rectangle([760, 560, 1460, 600], fill=(70, 50, 36))
    d.rectangle([840, 520, 1000, 560], fill=(220, 216, 206))
    d.ellipse([1280, 500, 1380, 560], fill=(60, 64, 74))
    # 本棚と花札の額
    d.rectangle([120, 200, 520, int(H * 0.78)], fill=(84, 62, 46))
    for r in range(4):
        d.rectangle([140, 230 + r * 160, 500, 340 + r * 160], fill=(120, 96, 70))
        for c in range(6):
            d.rectangle([150 + c * 56, 240 + r * 160, 196 + c * 56, 330 + r * 160],
                        fill=(150, 60, 56) if (r + c) % 3 else (70, 90, 130))
    d.rectangle([1600, 200, 1800, 460], fill=(120, 96, 70))
    d.rounded_rectangle([1630, 240, 1770, 420], radius=6, fill=(200, 70, 70))
    glow(img, 1700, 330, 60, (255, 220, 160), 40)
    return img


def kaihatsu() -> Image.Image:
    """開発室（試作机・玩具棚・図面）。"""
    img = vgrad((W, H), (78, 84, 96), (56, 62, 74)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (92, 86, 78), (70, 66, 60))
    _window(img, d, 1460, 130, 1860, 490, (150, 176, 200), (200, 216, 230), (84, 88, 100))
    # 作業机（試作品と工具）
    d.rounded_rectangle([680, 560, 1400, int(H * 0.77)], radius=8, fill=(112, 92, 66))
    d.rectangle([680, 560, 1400, 596], fill=(92, 76, 56))
    d.rounded_rectangle([740, 500, 900, 560], radius=8, fill=(200, 200, 206))
    d.rectangle([760, 512, 880, 548], fill=(120, 150, 90))
    for k in range(4):
        d.rectangle([960 + k * 50, 520, 984 + k * 50, 560], fill=(150, 150, 160))
    d.ellipse([1180, 500, 1300, 560], fill=(220, 200, 90))
    # 玩具棚（カラフルな箱）
    d.rectangle([80, 240, 560, int(H * 0.77)], fill=(96, 88, 78))
    for r in range(4):
        for c in range(4):
            cols = [(220, 120, 110), (110, 160, 210), (240, 200, 90), (130, 190, 140)]
            d.rounded_rectangle([100 + c * 115, 270 + r * 150, 195 + c * 115, 380 + r * 150],
                                radius=8, fill=cols[(r + c) % 4])
    # 壁の図面
    d.rectangle([700, 180, 1060, 420], fill=(238, 240, 244))
    d.ellipse([760, 240, 860, 340], outline=(120, 140, 180), width=5)
    d.line([900, 240, 1020, 240], fill=(120, 140, 180), width=5)
    d.line([900, 300, 1020, 300], fill=(120, 140, 180), width=5)
    d.line([900, 360, 980, 360], fill=(120, 140, 180), width=5)
    return img


def train() -> Image.Image:
    """新幹線の車内（電卓のサラリーマンの場）。"""
    img = vgrad((W, H), (214, 216, 222), (236, 238, 242)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # 天井と荷棚
    d.rectangle([0, 0, W, 90], fill=(190, 192, 198))
    d.rectangle([0, 90, W, 130], fill=(160, 164, 172))
    # 窓の外（流れる景色）
    for k in range(3):
        x0 = 140 + k * 640
        d.rounded_rectangle([x0, 180, x0 + 480, 480], radius=20, fill=(150, 190, 220))
        d.polygon([(x0, 420), (x0 + 160, 300), (x0 + 320, 420)], fill=(110, 150, 110))
        d.polygon([(x0 + 220, 440), (x0 + 400, 320), (x0 + 480, 440)], fill=(96, 134, 100))
        d.line([x0, 250, x0 + 480, 250], fill=(220, 230, 240), width=8)
        d.rectangle([x0 - 30, 160, x0 + 510, 182], fill=(180, 184, 192))
    _floor(d, 640, (120, 110, 116), (100, 92, 98))
    # 座席（青いシートの列）
    for k, bx in enumerate((120, 620, 1120, 1620)):
        d.rounded_rectangle([bx, 470, bx + 260, 660], radius=16, fill=(70, 90, 150))
        d.rounded_rectangle([bx, 430, bx + 260, 500], radius=16, fill=(90, 110, 170))
        d.rectangle([bx + 40, 660, bx + 220, 700], fill=(90, 94, 104))
    return img


def mise() -> Image.Image:
    """おもちゃ売り場（棚とレジ・にぎわい）。"""
    img = vgrad((W, H), (250, 236, 210), (255, 246, 228)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.76), (216, 196, 168), (192, 174, 150))
    # 吊り看板
    d.rounded_rectangle([760, 90, 1180, 190], radius=14, fill=(220, 90, 90))
    d.rectangle([790, 120, 1150, 164], fill=(240, 236, 226))
    # 商品棚（カラフルな箱がぎっしり）
    for sx in (100, 1460):
        d.rectangle([sx, 260, sx + 380, int(H * 0.76)], fill=(150, 130, 104))
        for r in range(4):
            for c in range(3):
                cols = [(220, 120, 110), (110, 160, 210), (240, 200, 90), (130, 190, 140)]
                d.rounded_rectangle([sx + 20 + c * 120, 290 + r * 140,
                                     sx + 120 + c * 120, 400 + r * 140],
                                    radius=8, fill=cols[(r * 3 + c) % 4])
    # 中央の平台（ゲーム機の山）
    d.rounded_rectangle([760, 520, 1180, int(H * 0.76)], radius=10, fill=(170, 148, 120))
    for k in range(4):
        d.rounded_rectangle([790 + k * 100, 470, 870 + k * 100, 540], radius=8,
                            fill=(200, 200, 206))
        d.rectangle([806 + k * 100, 482, 854 + k * 100, 516], fill=(120, 150, 90))
    glow(img, 970, 300, 160, (255, 240, 200), 50)
    return img


def yugure() -> Image.Image:
    """夕暮れの京都の道（静かな追悼の場）。"""
    img = vgrad((W, H), (244, 170, 110), (255, 214, 160)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    glow(img, 500, 300, 200, (255, 220, 140), 100)
    d.ellipse([420, 220, 580, 380], fill=(255, 236, 180))
    # 町屋のシルエット
    for k, bx in enumerate(range(700, W, 300)):
        hh = 300 + (k % 2) * 60
        d.rectangle([bx, 560 - hh + 160, bx + 260, 620], fill=(110, 80, 66))
        d.polygon([(bx - 20, 560 - hh + 160), (bx + 130, 560 - hh + 90),
                   (bx + 280, 560 - hh + 160)], fill=(90, 64, 54))
    # 五重塔のシルエット
    for r in range(5):
        w = 220 - r * 36
        y = 520 - r * 80
        d.polygon([(300 - w // 2, y), (300 + w // 2, y), (300, y - 46)], fill=(90, 64, 54))
        d.rectangle([300 - w // 2 + 14, y, 300 + w // 2 - 14, y + 36], fill=(110, 80, 66))
    d.rectangle([292, 120, 308, 200], fill=(90, 64, 54))
    _floor(d, 620, (200, 150, 110), (176, 132, 98))
    return img


PAINTERS = {
    "il_yg_living": living_now,
    "il_yg_kojo": kojo_showa,
    "il_yg_shacho": shacho,
    "il_yg_kaihatsu": kaihatsu,
    "il_yg_train": train,
    "il_yg_mise": mise,
    "il_yg_yugure": yugure,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
