#!/usr/bin/env python3
"""胃カメラ再現ドラマ（gastro-camera）用のイラスト背景10種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_gc_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402


def clinic_now() -> Image.Image:
    """現代の内科診察室（フック/締め・胃カメラのモニタ）。"""
    img = vgrad((W, H), (236, 242, 246), (216, 224, 230)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (206, 210, 214), (178, 182, 188))
    # 診察台
    d.rounded_rectangle([120, 560, 720, int(H * 0.78)], radius=14, fill=(120, 170, 190))
    d.rectangle([120, 560, 720, 596], fill=(98, 148, 168))
    # モニタ台（内視鏡画像）
    d.rounded_rectangle([1180, 300, 1660, 620], radius=14, fill=(60, 66, 78))
    d.rectangle([1210, 330, 1630, 590], fill=(40, 44, 54))
    d.ellipse([1330, 380, 1510, 540], fill=(210, 140, 130))  # 胃壁っぽい円
    d.ellipse([1380, 430, 1460, 490], fill=(150, 80, 74))
    # ワゴン
    d.rounded_rectangle([1180, 640, 1660, int(H * 0.78)], radius=10, fill=(150, 156, 166))
    # 窓
    d.rounded_rectangle([820, 150, 1120, 470], radius=10, fill=(180, 210, 228))
    d.line([970, 150, 970, 470], fill=(150, 170, 186), width=8)
    d.line([820, 310, 1120, 310], fill=(150, 170, 186), width=8)
    return img


def hamamatsu() -> Image.Image:
    """浜松の町（誕生・少年期）。遠州灘と工場町。"""
    img = vgrad((W, H), (180, 210, 232), (220, 232, 240)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, int(H * 0.6), W, int(H * 0.74)], fill=(96, 150, 190))
    d.rectangle([0, int(H * 0.74), W, H], fill=(150, 140, 120))
    d.line([0, int(H * 0.74), W, int(H * 0.74)], fill=(120, 112, 96), width=6)
    # 松林
    for k in range(6):
        x = 120 + k * 320
        d.rectangle([x - 8, int(H * 0.55), x + 8, int(H * 0.62)], fill=(96, 72, 54))
        d.ellipse([x - 60, int(H * 0.45), x + 60, int(H * 0.58)], fill=(80, 130, 90))
    # 工場の煙突
    d.rectangle([1500, 260, 1560, int(H * 0.6)], fill=(150, 120, 110))
    for k in range(3):
        d.ellipse([1470 + k * 30, 180 - k * 50, 1560 + k * 40, 260 - k * 50],
                  fill=(210, 206, 200, 200))
    glow(img, 260, 150, 130, (255, 240, 200), 80)
    d.ellipse([210, 100, 310, 200], fill=(255, 244, 214))
    return img


def photo_school() -> Image.Image:
    """写真専門学校の暗室・実習（学生時代）。"""
    img = vgrad((W, H), (54, 48, 60), (36, 32, 42)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (60, 54, 50), (44, 40, 38))
    # 赤い安全灯
    glow(img, 460, 200, 160, (220, 60, 60), 80)
    d.ellipse([430, 170, 490, 230], fill=(230, 80, 80))
    # 現像バット
    for k in range(3):
        d.rounded_rectangle([300 + k * 320, 560, 560 + k * 320, 640], radius=10,
                            fill=(80, 90, 100))
        d.rectangle([320 + k * 320, 575, 540 + k * 320, 625], fill=(60, 90, 110))
    # 引き伸ばし機
    d.rectangle([1400, 300, 1440, 640], fill=(70, 74, 82))
    d.rounded_rectangle([1330, 300, 1510, 400], radius=10, fill=(90, 94, 102))
    d.rounded_rectangle([1360, 560, 1480, 640], radius=8, fill=(110, 114, 122))
    # 吊るした印画紙
    d.line([700, 240, 1200, 240], fill=(120, 120, 128), width=3)
    for k in range(4):
        d.rectangle([760 + k * 110, 240, 840 + k * 110, 340], fill=(200, 200, 196))
    return img


def olympus_lab() -> Image.Image:
    """オリンパスの光学開発室（カメラ設計）。"""
    img = vgrad((W, H), (66, 74, 88), (46, 52, 62)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (78, 80, 88), (58, 60, 68))
    _window(img, d, 200, 130, 640, 500, (176, 200, 220), (216, 228, 238), (90, 96, 108))
    # 作業台と光学部品
    d.rounded_rectangle([780, 560, 1500, int(H * 0.77)], radius=8, fill=(104, 96, 88))
    d.rectangle([780, 560, 1500, 592], fill=(84, 78, 72))
    # レンズ（同心円）
    for k in range(3):
        cx = 880 + k * 200
        for r in (54, 38, 22):
            d.ellipse([cx - r, 470 - r, cx + r, 470 + r], outline=(180, 200, 220), width=4)
    # 精密機械（ダイヤル）
    d.rounded_rectangle([1560, 300, 1840, int(H * 0.77)], radius=8, fill=(70, 74, 82))
    for r in range(3):
        for k in range(3):
            d.ellipse([1590 + k * 80, 340 + r * 130, 1650 + k * 80, 400 + r * 130],
                      fill=(150, 156, 166))
    return img


def train() -> Image.Image:
    """夜行列車の車内（宇治の口説き）。"""
    img = vgrad((W, H), (44, 46, 60), (30, 32, 44)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.8), (70, 60, 52), (52, 44, 38))
    # 窓（夜・流れる灯り）
    for k in range(3):
        wx = 180 + k * 560
        d.rounded_rectangle([wx, 200, wx + 420, 520], radius=12, fill=(24, 28, 44))
        d.rounded_rectangle([wx, 200, wx + 420, 520], outline=(90, 96, 110), width=8)
        for j in range(4):
            d.ellipse([wx + 40 + j * 100, 380 + (j % 2) * 40,
                       wx + 70 + j * 100, 410 + (j % 2) * 40], fill=(220, 200, 120, 180))
    # 網棚
    d.line([80, 150, W - 80, 150], fill=(120, 124, 134), width=6)
    # 座席背もたれ
    d.rounded_rectangle([120, 560, 760, int(H * 0.8)], radius=14, fill=(96, 70, 60))
    d.rounded_rectangle([1160, 560, 1800, int(H * 0.8)], radius=14, fill=(96, 70, 60))
    return img


def hospital_old() -> Image.Image:
    """昭和の大学病院（診察・手術）。"""
    img = vgrad((W, H), (200, 210, 214), (176, 186, 192)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (166, 172, 176), (140, 146, 150))
    # 診察ベッド
    d.rounded_rectangle([160, 580, 900, int(H * 0.78)], radius=10, fill=(214, 216, 220))
    d.rectangle([160, 580, 900, 612], fill=(190, 192, 198))
    d.rounded_rectangle([160, 520, 320, 580], radius=10, fill=(214, 216, 220))  # 枕
    # 点滴スタンド
    d.rectangle([1000, 300, 1012, int(H * 0.78)], fill=(150, 156, 166))
    d.rounded_rectangle([980, 300, 1032, 380], radius=8, fill=(210, 224, 220))
    # 薬品棚
    d.rounded_rectangle([1300, 260, 1660, int(H * 0.78)], radius=8, fill=(210, 214, 218))
    for r in range(4):
        d.rectangle([1320, 300 + r * 150, 1640, 320 + r * 150], fill=(170, 176, 182))
        for k in range(5):
            d.rectangle([1332 + k * 62, 256 + r * 150 + 14, 1372 + k * 62, 316 + r * 150],
                        fill=(230, 236, 240))
    # 窓の十字
    d.rounded_rectangle([1000, 130, 1240, 380], radius=6, fill=(200, 218, 228))
    d.line([1120, 130, 1120, 380], fill=(160, 170, 180), width=8)
    d.line([1000, 255, 1240, 255], fill=(160, 170, 180), width=8)
    return img


def workshop() -> Image.Image:
    """試作の作業場（電球・レンズの試行錯誤・夜）。"""
    img = vgrad((W, H), (56, 52, 58), (38, 36, 42)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (62, 56, 50), (46, 42, 38))
    # 作業台
    d.rounded_rectangle([200, 580, 1140, int(H * 0.77)], radius=8, fill=(110, 90, 66))
    d.rectangle([200, 580, 1140, 612], fill=(90, 74, 54))
    # 豆電球の試作が並ぶ
    for k in range(6):
        bx = 280 + k * 130
        d.ellipse([bx - 20, 500, bx + 20, 540], fill=(255, 236, 170) if k % 2 else (120, 120, 110))
        d.rectangle([bx - 8, 540, bx + 8, 560], fill=(150, 150, 140))
        if k % 2:
            glow(img, bx, 520, 60, (255, 220, 140), 70)
    # 工具棚
    d.rounded_rectangle([1260, 260, 1560, int(H * 0.77)], radius=8, fill=(74, 66, 58))
    for r in range(4):
        d.rectangle([1280, 300 + r * 150, 1540, 320 + r * 150], fill=(56, 50, 44))
        for k in range(3):
            d.rectangle([1300 + k * 90, 256 + r * 150 + 18, 1360 + k * 90, 306 + r * 150],
                        fill=(130, 122, 110))
    # 万力
    d.rounded_rectangle([1620, 520, 1780, 600], radius=6, fill=(96, 100, 108))
    d.line([660, 0, 660, 130], fill=(50, 46, 42), width=6)
    glow(img, 660, 170, 130, (255, 214, 140), 80)
    d.ellipse([632, 130, 688, 206], fill=(255, 226, 150))
    return img


def gakkai() -> Image.Image:
    """医学会の講演会場（発表・500人）。"""
    img = vgrad((W, H), (58, 54, 66), (40, 38, 48)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, int(H * 0.7), W, H], fill=(70, 60, 52))
    d.line([0, int(H * 0.7), W, int(H * 0.7)], fill=(54, 46, 40), width=6)
    # スクリーン（胃の写真）
    d.rounded_rectangle([620, 130, 1300, 560], radius=10, fill=(230, 232, 236))
    d.ellipse([760, 200, 1160, 500], fill=(206, 140, 130))
    d.ellipse([880, 280, 1040, 420], fill=(150, 84, 78))
    # 演台
    d.polygon([(300, 600), (520, 600), (500, int(H * 0.7)), (320, int(H * 0.7))],
              fill=(80, 60, 44))
    # 客席のシルエット（後頭部の列）
    for r in range(3):
        for k in range(9):
            d.ellipse([160 + k * 190, int(H * 0.72) + r * 60,
                       230 + k * 190, int(H * 0.72) + 60 + r * 60], fill=(40, 38, 44))
    return img


def home_night() -> Image.Image:
    """宇治の自宅（静かな夜・晩年の余韻）。"""
    img = vgrad((W, H), (46, 42, 52), (30, 28, 36)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.74), (58, 48, 42), (42, 36, 32))
    # 障子と月
    d.rounded_rectangle([1200, 130, 1720, 620], radius=8, fill=(60, 66, 84))
    d.rounded_rectangle([1230, 160, 1690, 590], radius=6, fill=(38, 44, 62))
    for i in range(3):
        d.line([1230 + (i + 1) * 115, 160, 1230 + (i + 1) * 115, 590],
               fill=(70, 76, 96), width=6)
    glow(img, 1460, 320, 120, (240, 240, 210), 60)
    d.ellipse([1410, 270, 1510, 370], fill=(240, 240, 214))
    # ちゃぶ台と湯呑み
    d.ellipse([260, 640, 720, 800], fill=(110, 84, 56))
    d.ellipse([430, 690, 490, 730], fill=(200, 196, 186))
    glow(img, 480, 200, 130, (255, 214, 150), 60)
    return img


def gendai_endo() -> Image.Image:
    """現代の内視鏡室（進化・ファイバー→電子）。"""
    img = vgrad((W, H), (40, 46, 58), (28, 32, 42)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (58, 62, 72), (44, 48, 56))
    # 大型モニタ2枚
    for k in range(2):
        mx = 700 + k * 500
        d.rounded_rectangle([mx, 220, mx + 420, 520], radius=12, fill=(20, 24, 32))
        d.rectangle([mx + 24, 244, mx + 396, 496], fill=(30, 34, 44))
        d.ellipse([mx + 120, 300, mx + 300, 460], fill=(210, 140, 130))
        d.ellipse([mx + 170, 350, mx + 250, 410], fill=(150, 82, 76))
    # 内視鏡システムのワゴン
    d.rounded_rectangle([700, 560, 1200, int(H * 0.78)], radius=10, fill=(60, 66, 78))
    for r in range(3):
        d.rectangle([720, 590 + r * 60, 1180, 620 + r * 60], fill=(80, 86, 98))
        for kk in range(4):
            col = (240, 120, 100) if (r + kk) % 3 == 0 else (120, 220, 160)
            d.ellipse([740 + kk * 60, 596 + r * 60, 762 + kk * 60, 618 + r * 60], fill=col)
    # スコープのケーブル
    d.arc([1180, 400, 1500, 720], -20, 180, fill=(40, 44, 54), width=16)
    return img


PAINTERS = {
    "il_gc_clinic": clinic_now,
    "il_gc_hamamatsu": hamamatsu,
    "il_gc_photoschool": photo_school,
    "il_gc_lab": olympus_lab,
    "il_gc_train": train,
    "il_gc_hospital": hospital_old,
    "il_gc_workshop": workshop,
    "il_gc_gakkai": gakkai,
    "il_gc_home": home_night,
    "il_gc_gendai": gendai_endo,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
