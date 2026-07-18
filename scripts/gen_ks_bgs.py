#!/usr/bin/env python3
"""回転寿司再現ドラマ（kaiten-sushi）用のイラスト背景11種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_ks_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402


def _sushi_plate(d, cx, cy, s=1.0, col=(240, 244, 248)):
    """皿+にぎり2貫。"""
    d.ellipse([cx - 52 * s, cy - 14 * s, cx + 52 * s, cy + 16 * s], fill=col,
              outline=(170, 176, 186), width=2)
    for k in (-22, 12):
        d.rounded_rectangle([cx + (k - 14) * s, cy - 14 * s, cx + (k + 16) * s, cy - 2 * s],
                            radius=int(5 * s), fill=(244, 240, 230))
        d.rounded_rectangle([cx + (k - 16) * s, cy - 20 * s, cx + (k + 18) * s, cy - 10 * s],
                            radius=int(5 * s), fill=(236, 120, 100))


def _lane(d, y, h=70, col=(96, 104, 116)):
    """回転レーンの帯+ウロコ板。"""
    d.rectangle([0, y, W, y + h], fill=col)
    d.line([0, y, W, y], fill=(70, 76, 88), width=5)
    d.line([0, y + h, W, y + h], fill=(70, 76, 88), width=5)
    for i in range(24):
        x = i * 84
        d.arc([x - 42, y + 4, x + 42, y + h - 4], -80, 80, fill=(140, 148, 160), width=4)


def ehime() -> Image.Image:
    """愛媛の海辺の町（誕生・少年期）。"""
    img = vgrad((W, H), (168, 208, 232), (216, 232, 240)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, int(H * 0.55), W, int(H * 0.74)], fill=(96, 150, 190))
    for i in range(5):
        d.arc([i * 420 - 80, int(H * 0.55) + 26 + (i % 2) * 22 - 8,
               i * 420 + 240, int(H * 0.55) + 26 + (i % 2) * 22 + 12],
              200, 340, fill=(150, 190, 216), width=5)
    d.rectangle([0, int(H * 0.74), W, H], fill=(196, 178, 140))
    d.line([0, int(H * 0.74), W, int(H * 0.74)], fill=(160, 144, 110), width=6)
    # みかん山
    d.polygon([(60, int(H * 0.55)), (560, 190), (1060, int(H * 0.55))], fill=(120, 160, 110))
    for k in range(7):
        d.ellipse([300 + k * 70, 330 + (k % 3) * 60, 330 + k * 70, 360 + (k % 3) * 60],
                  fill=(235, 160, 60))
    # 漁船
    d.polygon([(1350, int(H * 0.62)), (1700, int(H * 0.62)), (1640, int(H * 0.7)),
               (1410, int(H * 0.7))], fill=(120, 96, 70))
    d.rectangle([1500, int(H * 0.5), 1516, int(H * 0.62)], fill=(90, 74, 56))
    glow(img, 1700, 150, 140, (255, 240, 200), 90)
    d.ellipse([1650, 100, 1760, 210], fill=(255, 244, 214))
    return img


def shugyo() -> Image.Image:
    """料理屋の厨房（板前修業）。"""
    img = vgrad((W, H), (84, 72, 60), (58, 50, 44)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.76), (68, 58, 48), (48, 42, 36))
    # まな板台と大鍋
    d.rounded_rectangle([200, 560, 900, int(H * 0.76)], radius=8, fill=(140, 110, 74))
    d.rectangle([200, 560, 900, 592], fill=(114, 90, 60))
    d.rounded_rectangle([300, 520, 560, 560], radius=6, fill=(210, 186, 140))
    d.ellipse([680, 470, 860, 566], fill=(90, 96, 104))
    # 棚に器
    d.rounded_rectangle([1060, 240, 1400, int(H * 0.76)], radius=8, fill=(96, 78, 56))
    for r in range(4):
        d.rectangle([1080, 280 + r * 160, 1380, 300 + r * 160], fill=(70, 58, 44))
        for k in range(4):
            d.ellipse([1090 + k * 74, 236 + r * 160 + 14, 1146 + k * 74, 276 + r * 160],
                      fill=(216, 210, 196))
    # のれん
    for k in range(3):
        d.rectangle([1520 + k * 110, 120, 1610 + k * 110, 440], fill=(70, 90, 140))
    glow(img, 640, 160, 130, (255, 220, 150), 80)
    d.ellipse([612, 120, 668, 196], fill=(255, 228, 160))
    return img


def eki() -> Image.Image:
    """戦後の大阪駅前（移住の決意）。"""
    img = vgrad((W, H), (232, 196, 150), (214, 172, 128)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (150, 138, 124), (122, 112, 100))
    # 駅舎
    d.rectangle([220, 240, 1240, int(H * 0.78)], fill=(180, 160, 136))
    d.rectangle([220, 240, 1240, 330], fill=(140, 122, 100))
    d.rectangle([560, 250, 900, 320], fill=(226, 220, 206))
    d.line([600, 285, 860, 285], fill=(90, 82, 70), width=8)
    for k in range(4):
        d.rectangle([300 + k * 240, 420, 440 + k * 240, int(H * 0.78)], fill=(120, 104, 86))
    # 時計
    d.ellipse([690, 350, 770, 430], fill=(240, 240, 236), outline=(100, 90, 76), width=6)
    d.line([730, 390, 730, 362], fill=(60, 56, 48), width=5)
    d.line([730, 390, 748, 400], fill=(60, 56, 48), width=4)
    # 汽車の煙
    d.rectangle([1420, 520, 1860, int(H * 0.78)], fill=(70, 66, 64))
    d.ellipse([1440, 540, 1560, 660], fill=(52, 50, 50))
    for k in range(3):
        d.ellipse([1500 + k * 90, 330 - k * 60, 1600 + k * 110, 430 - k * 60],
                  fill=(220, 214, 206, 200))
    return img


def koryori() -> Image.Image:
    """小料理屋「元禄」店内（開店〜経営難）。"""
    img = vgrad((W, H), (92, 76, 62), (64, 54, 46)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.76), (76, 62, 50), (54, 46, 38))
    # カウンター
    d.rounded_rectangle([160, 600, 1300, int(H * 0.76)], radius=10, fill=(146, 112, 72))
    d.rectangle([160, 600, 1300, 636], fill=(120, 92, 60))
    for k in range(3):
        d.ellipse([260 + k * 340, 550, 320 + k * 340, 586], fill=(206, 200, 188))
    # 品書き札
    for k in range(5):
        d.rectangle([300 + k * 150, 160, 400 + k * 150, 420], fill=(228, 218, 194))
        d.line([350 + k * 150, 190, 350 + k * 150, 390], fill=(90, 80, 66), width=6)
    # 提灯
    d.ellipse([1480, 200, 1640, 420], fill=(220, 90, 70))
    d.rectangle([1540, 170, 1580, 200], fill=(90, 70, 50))
    d.line([1520, 300, 1600, 300], fill=(180, 60, 46), width=5)
    glow(img, 1560, 300, 130, (255, 170, 120), 70)
    return img


def tachigui() -> Image.Image:
    """立ち食い寿司の店（4貫20円・満席）。"""
    img = vgrad((W, H), (98, 84, 66), (68, 58, 48)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (80, 66, 52), (58, 48, 40))
    # 長いカウンターとガラスケース
    d.rounded_rectangle([120, 560, 1800, int(H * 0.77)], radius=10, fill=(150, 116, 74))
    d.rectangle([120, 560, 1800, 598], fill=(124, 96, 62))
    d.rectangle([220, 470, 1700, 560], fill=(196, 216, 228, 160))
    d.line([220, 470, 1700, 470], fill=(150, 160, 170), width=5)
    for k in range(9):
        _sushi_plate(d, 330 + k * 160, 528, s=0.9)
    # 壁の品書き「にぎり 二十円」風の札
    for k in range(4):
        d.rectangle([420 + k * 260, 150, 560 + k * 260, 400], fill=(232, 222, 198))
        d.line([490 + k * 260, 180, 490 + k * 260, 370], fill=(96, 84, 68), width=7)
    glow(img, 960, 130, 150, (255, 226, 160), 70)
    d.ellipse([930, 90, 990, 160], fill=(255, 232, 170))
    return img


def beer_kojo() -> Image.Image:
    """ビール工場（見学・ひらめき）。"""
    img = vgrad((W, H), (76, 84, 96), (54, 60, 70)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (88, 92, 100), (66, 70, 78))
    for i in range(3):
        d.rectangle([220 + i * 560, 90, 620 + i * 560, 240], fill=(176, 196, 214))
        d.line([420 + i * 560, 90, 420 + i * 560, 240], fill=(96, 104, 118), width=8)
    # 大タンク
    for k in range(2):
        d.rounded_rectangle([170 + k * 240, 300, 350 + k * 240, int(H * 0.78)],
                            radius=30, fill=(150, 156, 166))
        d.ellipse([170 + k * 240, 270, 350 + k * 240, 340], fill=(170, 176, 186))
    # コンベアとビール瓶
    d.rectangle([700, 600, 1860, 680], fill=(64, 70, 82))
    for i in range(6):
        d.ellipse([740 + i * 190, 664, 790 + i * 190, 706], fill=(46, 50, 60))
    for i in range(7):
        bx = 760 + i * 160
        d.rounded_rectangle([bx, 500, bx + 44, 600], radius=8, fill=(150, 96, 40))
        d.rectangle([bx + 12, 470, bx + 32, 510], fill=(130, 82, 34))
    return img


def machikoba_ks() -> Image.Image:
    """町工場（コンベア開発・夜）。"""
    img = vgrad((W, H), (58, 54, 60), (40, 38, 44)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (62, 54, 48), (46, 40, 36))
    # 作業台+試作レーンの断片
    d.rounded_rectangle([220, 580, 1100, int(H * 0.77)], radius=8, fill=(110, 88, 62))
    d.rectangle([220, 580, 1100, 614], fill=(90, 72, 52))
    d.rectangle([300, 520, 1020, 580], fill=(96, 104, 116))
    for i in range(9):
        x = 320 + i * 78
        d.arc([x - 36, 524, x + 36, 576], -80, 80, fill=(150, 158, 170), width=4)
    # 工具棚
    d.rounded_rectangle([1240, 260, 1560, int(H * 0.77)], radius=8, fill=(76, 66, 58))
    for r in range(4):
        d.rectangle([1260, 300 + r * 160, 1540, 320 + r * 160], fill=(56, 48, 42))
        for k in range(3):
            d.rectangle([1280 + k * 90, 250 + r * 160 + 20, 1340 + k * 90, 300 + r * 160],
                        fill=(130, 120, 108))
    # 一升瓶と湯呑み
    d.rounded_rectangle([1660, 560, 1720, 740], radius=12, fill=(70, 96, 66))
    d.rectangle([1678, 520, 1702, 570], fill=(60, 82, 58))
    d.ellipse([1740, 690, 1800, 740], fill=(214, 208, 196))
    glow(img, 660, 170, 140, (255, 214, 140), 90)
    d.line([660, 0, 660, 130], fill=(52, 48, 44), width=6)
    d.ellipse([632, 130, 688, 206], fill=(255, 226, 150))
    return img


def kaiten1() -> Image.Image:
    """廻る元禄寿司1号店（レーン付きカウンター）。"""
    img = vgrad((W, H), (238, 226, 200), (222, 206, 176)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (170, 140, 100), (140, 116, 84))
    # 壁の垂れ幕
    d.rectangle([260, 120, 560, 420], fill=(196, 60, 54))
    d.rectangle([300, 160, 520, 380], fill=(226, 216, 196))
    d.line([410, 190, 410, 350], fill=(90, 30, 26), width=8)
    for k in range(3):
        d.rectangle([1300 + k * 180, 140, 1420 + k * 180, 400], fill=(232, 222, 198))
        d.line([1360 + k * 180, 170, 1360 + k * 180, 370], fill=(96, 84, 68), width=6)
    # カウンター+回転レーン
    d.rounded_rectangle([100, 640, 1820, int(H * 0.78)], radius=10, fill=(150, 116, 74))
    _lane(d, 560, 76)
    for k in range(7):
        _sushi_plate(d, 200 + k * 260, 596, s=1.0)
    glow(img, 960, 120, 150, (255, 230, 170), 70)
    d.ellipse([928, 84, 992, 152], fill=(255, 236, 180))
    return img


def dotonbori() -> Image.Image:
    """道頓堀の夜（2号店・繁盛）。"""
    img = vgrad((W, H), (30, 32, 52), (18, 20, 34)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.8), (44, 42, 52), (32, 30, 38))
    # ネオン看板群
    for k, col in enumerate(((236, 110, 90), (110, 170, 230), (240, 200, 90),
                             (140, 210, 140), (230, 140, 200))):
        sx = 130 + k * 350
        d.rounded_rectangle([sx, 160 + (k % 2) * 120, sx + 260, 360 + (k % 2) * 120],
                            radius=12, fill=(40, 42, 56), outline=col, width=8)
        d.line([sx + 40, 260 + (k % 2) * 120, sx + 220, 260 + (k % 2) * 120],
               fill=col, width=10)
        glow(img, sx + 130, 260 + (k % 2) * 120, 150, col, 60)
    # 川面の反射
    d.rectangle([0, int(H * 0.8), W, H], fill=(28, 32, 48))
    for k in range(5):
        d.line([160 + k * 380, int(H * 0.82), 240 + k * 380, H - 30],
               fill=(90, 110, 150), width=6)
    return img


def banpaku() -> Image.Image:
    """1970年大阪万博の会場（出店）。"""
    img = vgrad((W, H), (150, 200, 236), (210, 232, 244)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.8), (190, 186, 178), (160, 156, 148))
    # 塔（太陽の塔を模さない抽象タワー）とパビリオン群
    d.polygon([(430, int(H * 0.8)), (530, 180), (630, int(H * 0.8))], fill=(210, 206, 196))
    d.ellipse([490, 260, 570, 340], fill=(236, 190, 90))
    for k in range(3):
        d.ellipse([800 + k * 340, 380, 1080 + k * 340, 560], fill=(160, 190, 220))
        d.rectangle([860 + k * 340, 540, 1020 + k * 340, int(H * 0.8)], fill=(200, 210, 224))
    # 旗の列
    for k in range(8):
        x = 140 + k * 230
        d.line([x, 120, x, 300], fill=(120, 124, 134), width=6)
        d.polygon([(x, 130), (x + 70, 150), (x, 175)],
                  fill=[(226, 110, 90), (110, 170, 230), (240, 200, 90)][k % 3])
    return img


def gendai_sushi() -> Image.Image:
    """現代の回転寿司店（フック/締め・タッチパネル）。"""
    img = vgrad((W, H), (244, 240, 232), (228, 222, 210)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (196, 176, 150), (166, 148, 126))
    # ボックス席とレーン
    d.rounded_rectangle([80, 620, 1840, int(H * 0.78)], radius=10, fill=(170, 140, 100))
    _lane(d, 540, 76, col=(120, 128, 140))
    for k in range(6):
        _sushi_plate(d, 260 + k * 300, 576, s=1.0)
    # タッチパネル
    d.rounded_rectangle([840, 260, 1120, 460], radius=14, fill=(50, 56, 70))
    d.rectangle([864, 284, 1096, 420], fill=(120, 200, 220))
    for j in range(3):
        d.line([880, 310 + j * 40, 1080, 310 + j * 40], fill=(240, 248, 250), width=8)
    # 湯呑みと蛇口
    d.rectangle([1500, 470, 1560, 540], fill=(150, 156, 166))
    d.ellipse([1580, 560, 1650, 620], fill=(90, 130, 110))
    glow(img, 960, 110, 150, (255, 240, 200), 60)
    return img


PAINTERS = {
    "il_ks_ehime": ehime,
    "il_ks_shugyo": shugyo,
    "il_ks_eki": eki,
    "il_ks_koryori": koryori,
    "il_ks_tachigui": tachigui,
    "il_ks_beer": beer_kojo,
    "il_ks_machikoba": machikoba_ks,
    "il_ks_kaiten": kaiten1,
    "il_ks_dotonbori": dotonbori,
    "il_ks_banpaku": banpaku,
    "il_ks_gendai": gendai_sushi,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
