#!/usr/bin/env python3
"""ウォシュレット再現ドラマ（washlet）用のイラスト背景6種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_wl_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402


def _toilet(d, cx, cy, s=1.0, lid_open=False):
    """ウォシュレット付き便器（横向きのフラット絵）。"""
    # タンク
    d.rounded_rectangle([cx - 150 * s, cy - 240 * s, cx + 10 * s, cy - 60 * s],
                        radius=16, fill=(235, 238, 242))
    # 便座+本体
    d.rounded_rectangle([cx - 160 * s, cy - 70 * s, cx + 170 * s, cy + 10 * s],
                        radius=30, fill=(242, 245, 248))
    d.rounded_rectangle([cx - 120 * s, cy - 60 * s, cx + 150 * s, cy], radius=24,
                        fill=(228, 232, 238))
    # 操作パネル
    d.rounded_rectangle([cx + 150 * s, cy - 110 * s, cx + 250 * s, cy - 40 * s],
                        radius=10, fill=(214, 220, 228))
    for k in range(3):
        d.ellipse([cx + 165 * s + k * 26 * s, cy - 96 * s,
                   cx + 183 * s + k * 26 * s, cy - 78 * s],
                  fill=[(110, 170, 220), (240, 150, 120), (130, 190, 140)][k])
    # 台座
    d.polygon([(cx - 60 * s, cy + 10 * s), (cx + 90 * s, cy + 10 * s),
               (cx + 60 * s, cy + 120 * s), (cx - 30 * s, cy + 120 * s)],
              fill=(235, 238, 242))
    d.ellipse([cx - 70 * s, cy + 100 * s, cx + 100 * s, cy + 140 * s],
              fill=(228, 232, 238))


def toilet_now() -> Image.Image:
    """現代の明るいトイレ（フック/現代/締め）。"""
    img = vgrad((W, H), (228, 238, 242), (214, 226, 234)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # タイル壁
    for gx in range(0, W, 240):
        d.line([gx, 0, gx, 620], fill=(214, 224, 230), width=4)
    d.line([0, 320, W, 320], fill=(214, 224, 230), width=4)
    _floor(d, 620, (222, 218, 210), (200, 196, 188))
    # 小窓と観葉植物
    _window(img, d, 220, 120, 520, 380, (176, 210, 226), (214, 234, 242), (190, 196, 200))
    d.rounded_rectangle([1700, 420, 1820, 560], radius=10, fill=(180, 150, 120))
    d.ellipse([1660, 300, 1860, 460], fill=(120, 170, 110))
    # 便器（右寄り）
    _toilet(d, 1280, 780, s=1.1)
    # 棚とタオル
    d.rectangle([560, 200, 900, 240], fill=(200, 190, 176))
    d.rounded_rectangle([600, 250, 700, 340], radius=10, fill=(240, 244, 248))
    d.rounded_rectangle([730, 250, 830, 340], radius=10, fill=(190, 214, 230))
    return img


def office_showa() -> Image.Image:
    """昭和のオフィス（輸入品の検品場）。"""
    img = vgrad((W, H), (96, 92, 84), (70, 68, 62)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (110, 100, 88), (88, 80, 70))
    _window(img, d, 180, 120, 600, 480, (176, 196, 214), (214, 226, 236), (100, 92, 80))
    # スチール机と書類
    d.rounded_rectangle([720, 560, 1360, int(H * 0.77)], radius=8, fill=(120, 126, 138))
    d.rectangle([720, 560, 1360, 596], fill=(100, 106, 118))
    d.rectangle([780, 520, 940, 560], fill=(238, 236, 228))
    d.rectangle([960, 530, 1100, 560], fill=(226, 224, 216))
    # 輸入品の木箱（英字風ラベル）
    for k in range(2):
        bx = 1480 + k * 210
        d.rectangle([bx, 560 - k * 40, bx + 180, int(H * 0.77) - k * 40], fill=(170, 140, 100))
        d.line([bx, 610 - k * 40, bx + 180, 610 - k * 40], fill=(140, 112, 80), width=6)
        d.rectangle([bx + 30, 630 - k * 40, bx + 150, 670 - k * 40], fill=(226, 220, 200))
    # 検品中の便座（机の上）
    d.rounded_rectangle([1130, 500, 1330, 560], radius=20, fill=(235, 238, 242))
    # 蛍光灯
    for k in range(2):
        d.rectangle([500 + k * 700, 70, 900 + k * 700, 94], fill=(235, 240, 244))
    return img


def kaigi() -> Image.Image:
    """会議室（決断と命名の場）。"""
    img = vgrad((W, H), (86, 90, 100), (62, 66, 76)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (100, 92, 82), (80, 74, 66))
    _window(img, d, 1440, 130, 1850, 500, (150, 176, 200), (196, 214, 228), (86, 88, 98))
    # ホワイトボード（グラフと文字風の線）
    d.rounded_rectangle([220, 150, 900, 560], radius=10, fill=(238, 240, 244))
    d.rectangle([220, 150, 900, 190], fill=(190, 194, 202))
    for j in range(3):
        d.line([260, 250 + j * 70, 620, 250 + j * 70], fill=(120, 130, 150), width=6)
    d.line([680, 480, 680, 260], fill=(220, 100, 90), width=6)
    d.line([620, 480, 860, 480], fill=(120, 130, 150), width=6)
    # 長机
    d.rounded_rectangle([460, 620, 1480, int(H * 0.78)], radius=10, fill=(116, 92, 66))
    d.rectangle([460, 620, 1480, 656], fill=(96, 76, 54))
    for k in range(3):
        d.rectangle([560 + k * 300, 566, 740 + k * 300, 604], fill=(228, 230, 234))
    return img


def lab() -> Image.Image:
    """開発試験室（試験用便座・計器・ハリガネ）。"""
    img = vgrad((W, H), (80, 86, 96), (58, 64, 74)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (96, 90, 82), (76, 72, 64))
    _window(img, d, 180, 120, 560, 460, (176, 196, 214), (214, 226, 236), (88, 90, 100))
    # 試験台の上の便座（ハリガネ格子付き）
    d.rounded_rectangle([700, 560, 1360, int(H * 0.77)], radius=8, fill=(112, 92, 66))
    d.rectangle([700, 560, 1360, 596], fill=(92, 76, 56))
    d.rounded_rectangle([780, 470, 1090, 560], radius=32, fill=(238, 241, 245))
    d.rounded_rectangle([820, 486, 1050, 548], radius=24, fill=(214, 220, 228))
    for k in range(4):
        d.line([840 + k * 52, 486, 840 + k * 52, 548], fill=(160, 168, 180), width=4)
    d.line([820, 517, 1050, 517], fill=(160, 168, 180), width=4)
    # 計器ラック
    d.rounded_rectangle([1480, 300, 1860, int(H * 0.77)], radius=10, fill=(84, 90, 104))
    d.rectangle([1520, 340, 1680, 420], fill=(120, 200, 160))
    d.ellipse([1720, 340, 1800, 420], fill=(220, 200, 90))
    for r in range(2):
        for c in range(4):
            d.ellipse([1520 + c * 84, 460 + r * 90, 1560 + c * 84, 500 + r * 90],
                      fill=(200, 120, 110) if (r + c) % 2 else (110, 170, 220))
    # 温度計ポール
    d.line([620, 300, 620, 760], fill=(150, 156, 170), width=10)
    d.ellipse([596, 260, 644, 308], fill=(220, 100, 90))
    return img


def mise() -> Image.Image:
    """住宅設備の売り場（ショールーム）。"""
    img = vgrad((W, H), (238, 234, 224), (248, 244, 236)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.76), (216, 208, 194), (194, 186, 172))
    # 展示台の便器3台
    for k, bx in enumerate((420, 1010, 1600)):
        d.rounded_rectangle([bx - 200, 640, bx + 200, 700], radius=10, fill=(206, 198, 184))
        _toilet(d, bx, 560, s=0.72)
    # 吊り看板
    d.rounded_rectangle([760, 100, 1180, 200], radius=14, fill=(110, 160, 210))
    d.rectangle([790, 130, 1150, 174], fill=(240, 244, 248))
    # ポスター
    for px in (140, 1760):
        d.rectangle([px, 240, px + 220, 520], fill=(226, 230, 236))
        d.rectangle([px + 20, 260, px + 200, 400], fill=(180, 210, 230))
    glow(img, 970, 260, 160, (255, 244, 210), 50)
    return img


def cha_no_ma() -> Image.Image:
    """1982年の茶の間（ブラウン管テレビのCM）。"""
    img = vgrad((W, H), (96, 84, 68), (72, 64, 54)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.72), (168, 146, 106), (146, 126, 92))
    # 障子
    for sx in (110, 1560):
        d.rounded_rectangle([sx, 120, sx + 280, 620], radius=6, fill=(226, 218, 198))
        for i in range(2):
            d.line([sx + 93 + i * 93, 120, sx + 93 + i * 93, 620],
                   fill=(150, 130, 104), width=7)
        for j in range(3):
            d.line([sx, 190 + j * 145, sx + 280, 190 + j * 145],
                   fill=(150, 130, 104), width=7)
    # ブラウン管テレビ（木枠・脚付き）
    d.rounded_rectangle([760, 300, 1300, 700], radius=16, fill=(120, 90, 60))
    d.rounded_rectangle([800, 340, 1180, 640], radius=20, fill=(60, 70, 90))
    d.rounded_rectangle([820, 360, 1160, 620], radius=16, fill=(120, 160, 200))
    d.ellipse([900, 420, 1000, 520], fill=(240, 230, 210))
    d.rectangle([1040, 440, 1130, 500], fill=(240, 244, 248))
    for k in range(2):
        d.ellipse([1210 + k % 1, 380 + k * 90, 1270, 440 + k * 90], fill=(90, 68, 46))
    d.rectangle([820, 700, 860, 780], fill=(90, 68, 46))
    d.rectangle([1200, 700, 1240, 780], fill=(90, 68, 46))
    # ちゃぶ台とみかん
    d.ellipse([420, 760, 900, 920], fill=(150, 118, 80))
    for k in range(3):
        d.ellipse([560 + k * 70, 790, 610 + k * 70, 840], fill=(240, 160, 60))
    glow(img, 990, 480, 200, (170, 200, 240), 40)
    return img


PAINTERS = {
    "il_wl_toilet": toilet_now,
    "il_wl_office": office_showa,
    "il_wl_kaigi": kaigi,
    "il_wl_lab": lab,
    "il_wl_mise": mise,
    "il_wl_cm": cha_no_ma,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
