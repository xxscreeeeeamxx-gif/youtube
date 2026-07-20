#!/usr/bin/env python3
"""電気炊飯器再現ドラマ（rice-cooker）用のイラスト背景9種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_rc_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402


def _pot(d, cx, cy, s=1.0, col=(120, 126, 138)):
    """羽釜（つば付きの丸い釜）。"""
    d.ellipse([cx - 120 * s, cy - 70 * s, cx + 120 * s, cy + 80 * s], fill=col)
    d.ellipse([cx - 150 * s, cy - 40 * s, cx + 150 * s, cy], fill=col)
    d.ellipse([cx - 96 * s, cy - 96 * s, cx + 96 * s, cy - 30 * s], fill=(70, 74, 84))


def kitchen_now() -> Image.Image:
    """現代のキッチン（フック/締め）。"""
    img = vgrad((W, H), (238, 240, 244), (220, 224, 230)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (198, 190, 178), (168, 160, 148))
    # カウンターと吊り戸棚
    d.rectangle([0, 520, W, 600], fill=(180, 170, 156))
    d.rectangle([0, 600, W, int(H * 0.78)], fill=(206, 198, 186))
    for i in range(5):
        d.rectangle([120 + i * 340, 120, 400 + i * 340, 300], fill=(214, 208, 198),
                    outline=(180, 172, 160), width=4)
    # 炊飯器（現代・ボタン付き）
    d.rounded_rectangle([840, 360, 1120, 520], radius=30, fill=(70, 74, 84))
    d.rounded_rectangle([870, 340, 1090, 380], radius=14, fill=(90, 94, 104))
    d.rectangle([900, 410, 1060, 470], fill=(150, 210, 220))
    for k in range(3):
        d.ellipse([910 + k * 60, 485, 940 + k * 60, 505], fill=(140, 150, 164))
    # 電子レンジ
    d.rounded_rectangle([1300, 380, 1600, 520], radius=12, fill=(80, 84, 94))
    d.rectangle([1324, 404, 1520, 496], fill=(120, 130, 146))
    return img


def kamado() -> Image.Image:
    """昭和の土間・かまど（当時の炊飯の重労働）。"""
    img = vgrad((W, H), (74, 62, 52), (50, 42, 36)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.74), (58, 48, 40), (40, 34, 28))
    # かまど（土の塊+焚き口）
    d.rounded_rectangle([620, 460, 1180, int(H * 0.74)], radius=20, fill=(96, 80, 66))
    d.rectangle([620, 460, 1180, 500], fill=(78, 64, 52))
    _pot(d, 900, 460, s=1.0, col=(60, 62, 70))
    # 焚き口の火
    d.rounded_rectangle([720, 640, 860, int(H * 0.74)], radius=10, fill=(30, 24, 20))
    glow(img, 790, 700, 90, (255, 150, 40), 130)
    for k in range(4):
        d.polygon([(760 + k * 24, 720), (772 + k * 24, 660), (784 + k * 24, 720)],
                  fill=(250, 170, 50))
    # 薪
    for k in range(3):
        d.rectangle([560, 700 + k * 22, 700, 716 + k * 22], fill=(110, 84, 56))
    # 湯気
    for k in range(3):
        pts = [(860 + k * 40, 380 - j * 20) for j in range(6)]
        d.line(pts, fill=(220, 216, 210, 140), width=8)
    # 小窓（夜明け前の藍色）
    _window(img, d, 1360, 150, 1720, 470, (30, 34, 58), (60, 66, 96), (70, 58, 48))
    return img


def koba() -> Image.Image:
    """光伸社の町工場（精密測定器の作業場）。"""
    img = vgrad((W, H), (66, 70, 80), (46, 50, 60)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (72, 68, 62), (52, 48, 44))
    _window(img, d, 200, 130, 620, 500, (176, 196, 214), (210, 224, 236), (86, 82, 74))
    # 作業台+工具+試作の釜
    d.rounded_rectangle([760, 560, 1500, int(H * 0.77)], radius=8, fill=(110, 90, 66))
    d.rectangle([760, 560, 1500, 596], fill=(90, 74, 54))
    _pot(d, 1000, 560, s=0.6, col=(120, 126, 138))
    for k in range(5):
        d.rectangle([1180 + k * 40, 500, 1200 + k * 40, 560], fill=(150, 150, 160))
    # 部品棚
    d.rounded_rectangle([1560, 240, 1860, int(H * 0.77)], radius=8, fill=(80, 70, 60))
    for r in range(5):
        for k in range(3):
            d.rectangle([1580 + k * 90, 280 + r * 140, 1640 + k * 90, 340 + r * 140],
                        fill=(140, 132, 120) if (r + k) % 2 else (120, 112, 100))
    # 裸電球
    d.line([680, 0, 680, 150], fill=(56, 52, 46), width=6)
    glow(img, 680, 190, 120, (255, 216, 140), 90)
    d.ellipse([652, 150, 708, 226], fill=(255, 226, 150))
    return img


def home() -> Image.Image:
    """三並家の台所（風美子の炊飯実験）。"""
    img = vgrad((W, H), (92, 82, 70), (66, 58, 50)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.75), (78, 66, 54), (56, 48, 40))
    # 障子
    for sx in (120, 1500):
        d.rounded_rectangle([sx, 120, sx + 320, 640], radius=6, fill=(224, 216, 196))
        for i in range(2):
            d.line([sx + 106 + i * 106, 120, sx + 106 + i * 106, 640],
                   fill=(150, 130, 104), width=8)
        for j in range(3):
            d.line([sx, 190 + j * 150, sx + 320, 190 + j * 150],
                   fill=(150, 130, 104), width=8)
    # 台所の棚に炊いたご飯の茶碗がずらり（実験の跡）
    d.rounded_rectangle([600, 540, 1360, int(H * 0.75)], radius=8, fill=(140, 110, 74))
    d.rectangle([600, 540, 1360, 574], fill=(116, 90, 60))
    for k in range(7):
        cx = 660 + k * 100
        d.ellipse([cx - 34, 500, cx + 34, 544], fill=(236, 232, 224))
        d.ellipse([cx - 28, 494, cx + 28, 520], fill=(250, 248, 244))
    # 試作の釜（電気コード付き）
    _pot(d, 1000, 500, s=0.5, col=(120, 126, 138))
    d.line([1000, 520, 1180, 560], fill=(40, 40, 44), width=6)
    glow(img, 960, 150, 130, (255, 224, 160), 70)
    return img


def lab() -> Image.Image:
    """試作の作業場（電気系・計器）。"""
    img = vgrad((W, H), (60, 66, 78), (42, 48, 60)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (70, 66, 60), (50, 46, 42))
    # 計器の壁
    d.rounded_rectangle([200, 150, 640, 520], radius=10, fill=(80, 78, 74))
    for r in range(3):
        for k in range(3):
            d.ellipse([240 + k * 130, 190 + r * 110, 320 + k * 130, 270 + r * 110],
                      fill=(200, 196, 186), outline=(120, 116, 108), width=4)
            d.line([280 + k * 130, 230 + r * 110, 300 + k * 130, 200 + r * 110],
                   fill=(60, 60, 66), width=4)
    # 作業台+試作の二重釜（断面が見える）
    d.rounded_rectangle([820, 560, 1500, int(H * 0.77)], radius=8, fill=(104, 96, 88))
    d.rectangle([820, 560, 1500, 592], fill=(84, 78, 72))
    _pot(d, 1060, 560, s=0.7, col=(120, 126, 138))
    # サーモスタットらしき箱
    d.rounded_rectangle([1300, 470, 1440, 560], radius=8, fill=(70, 76, 90))
    for k in range(3):
        d.ellipse([1320 + k * 34, 500, 1344 + k * 34, 524], fill=(140, 200, 160))
    glow(img, 420, 130, 120, (200, 220, 240), 50)
    return img


def toshiba() -> Image.Image:
    """東芝のオフィス（依頼・会議）。"""
    img = vgrad((W, H), (200, 204, 212), (172, 178, 188)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (140, 132, 122), (114, 108, 100))
    # 大きな窓（都市）
    d.rounded_rectangle([180, 120, 900, 520], radius=8, fill=(150, 176, 200))
    for k in range(5):
        d.rectangle([220 + k * 130, 200, 320 + k * 130, 500], fill=(120, 150, 180))
    d.line([180, 120, 900, 120], fill=(120, 126, 138), width=8)
    # 会議机+資料
    d.rounded_rectangle([980, 540, 1720, int(H * 0.78)], radius=12, fill=(150, 120, 88))
    d.rectangle([980, 540, 1720, 574], fill=(124, 96, 62))
    for k in range(3):
        d.rounded_rectangle([1040 + k * 220, 480, 1200 + k * 220, 544], radius=4,
                            fill=(238, 234, 226))
    # 壁の社名プレート（抽象）
    d.rounded_rectangle([1300, 160, 1720, 300], radius=10, fill=(90, 100, 130))
    d.rectangle([1340, 210, 1680, 250], fill=(214, 220, 232))
    return img


def shop() -> Image.Image:
    """1955年の電器店（発売）。"""
    img = vgrad((W, H), (226, 214, 190), (208, 194, 168)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (150, 132, 110), (124, 108, 88))
    # 陳列棚に炊飯器がずらり
    d.rounded_rectangle([120, 300, 1800, int(H * 0.78)], radius=10, fill=(160, 130, 96))
    for shelf in (360, 520):
        d.rectangle([120, shelf, 1800, shelf + 16], fill=(120, 96, 70))
        for k in range(9):
            cx = 220 + k * 180
            d.rounded_rectangle([cx - 60, shelf - 96, cx + 60, shelf], radius=18,
                                fill=(120, 126, 138))
            d.ellipse([cx - 42, shelf - 110, cx + 42, shelf - 70], fill=(90, 94, 104))
    # 値札
    d.rounded_rectangle([760, 150, 1160, 280], radius=10, fill=(230, 60, 54))
    d.rectangle([800, 190, 1120, 240], fill=(240, 232, 214))
    # 電飾
    for k in range(9):
        d.ellipse([180 + k * 190, 110, 210 + k * 190, 140],
                  fill=(250, 220, 120) if k % 2 else (240, 150, 120))
    return img


def denki_now() -> Image.Image:
    """現代の家電売り場（進化）。"""
    img = vgrad((W, H), (236, 240, 246), (216, 222, 232)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.8), (200, 204, 212), (172, 176, 186))
    for i in range(3):
        d.rounded_rectangle([200 + i * 560, 60, 640 + i * 560, 96], radius=14,
                            fill=(250, 250, 246))
    # ずらりと並ぶ高級炊飯器
    d.rounded_rectangle([100, 420, 1820, int(H * 0.8)], radius=10, fill=(200, 196, 190))
    for k in range(6):
        cx = 240 + k * 290
        col = [(70, 74, 84), (150, 60, 54), (90, 80, 70), (60, 66, 78),
               (110, 90, 70), (80, 84, 94)][k]
        d.rounded_rectangle([cx - 90, 360, cx + 90, 500], radius=26, fill=col)
        d.rectangle([cx - 54, 400, cx + 54, 450], fill=(150, 210, 220))
        d.rounded_rectangle([cx - 40, 500, cx + 40, 520], radius=8, fill=(180, 184, 194))
    # POP
    d.rounded_rectangle([760, 200, 1160, 320], radius=10, fill=(240, 90, 80))
    return img


def washitsu() -> Image.Image:
    """三並家の居間（晩年・静か）。"""
    img = vgrad((W, H), (86, 76, 64), (60, 54, 46)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, int(H * 0.72), W, H], fill=(150, 140, 100))
    d.line([0, int(H * 0.72), W, int(H * 0.72)], fill=(112, 104, 74), width=6)
    for i in range(4):
        d.line([i * 520, int(H * 0.72), i * 520 - 160, H], fill=(124, 116, 82), width=5)
    for sx in (140, 1440):
        d.rounded_rectangle([sx, 120, sx + 340, 680], radius=6, fill=(226, 218, 198))
        for i in range(2):
            d.line([sx + 113 + i * 113, 120, sx + 113 + i * 113, 680],
                   fill=(150, 130, 104), width=8)
    # 床の間に初代炊飯器を飾る
    d.rounded_rectangle([820, 560, 1100, 760], radius=8, fill=(70, 62, 54))
    d.rounded_rectangle([860, 470, 1060, 600], radius=22, fill=(120, 126, 138))
    d.ellipse([884, 452, 1036, 512], fill=(90, 94, 104))
    glow(img, 960, 150, 140, (255, 226, 176), 60)
    d.ellipse([926, 96, 994, 168], fill=(255, 232, 180))
    return img


PAINTERS = {
    "il_rc_kitchen": kitchen_now,
    "il_rc_kamado": kamado,
    "il_rc_koba": koba,
    "il_rc_home": home,
    "il_rc_lab": lab,
    "il_rc_toshiba": toshiba,
    "il_rc_shop": shop,
    "il_rc_denki": denki_now,
    "il_rc_washitsu": washitsu,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
