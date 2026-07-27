#!/usr/bin/env python3
"""カッターナイフ再現ドラマ（cutter-knife）用のイラスト背景6種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
実行: PYTHONPATH=. python3 scripts/gen_ck_bgs.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402

YELLOW = (240, 200, 50)


def desk_now() -> Image.Image:
    """現代の工作机（フック/現代/締め）。カッターとカッターマット。"""
    img = vgrad((W, H), (232, 234, 238), (218, 222, 228)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.74), (196, 186, 172), (170, 160, 148))
    _window(img, d, 180, 110, 640, 500, (176, 200, 220), (216, 230, 240), (190, 184, 172))
    # 机とカッターマット（緑・方眼）
    d.rounded_rectangle([700, 560, 1560, int(H * 0.74)], radius=10, fill=(150, 122, 90))
    d.rectangle([700, 560, 1560, 596], fill=(126, 102, 76))
    d.rounded_rectangle([780, 470, 1300, 580], radius=10, fill=(70, 130, 90))
    for gx in range(820, 1300, 60):
        d.line([gx, 476, gx, 574], fill=(96, 156, 112), width=2)
    for gy in range(490, 580, 30):
        d.line([786, gy, 1294, gy], fill=(96, 156, 112), width=2)
    # 黄色いカッター
    d.rounded_rectangle([1340, 500, 1520, 544], radius=10, fill=YELLOW)
    d.polygon([(1520, 508), (1570, 522), (1520, 536)], fill=(190, 194, 204))
    d.line([1535, 512, 1541, 532], fill=(150, 154, 164), width=3)
    # 工作の紙と本棚
    d.polygon([(840, 440), (960, 410), (1000, 470), (880, 500)], fill=(240, 238, 230))
    d.rectangle([1660, 260, 1880, int(H * 0.74)], fill=(120, 108, 92))
    for r in range(4):
        d.rectangle([1676, 290 + r * 140, 1864, 380 + r * 140], fill=(160, 148, 130))
    return img


def insatsu() -> Image.Image:
    """昭和の印刷所（紙の山と裁断台）。"""
    img = vgrad((W, H), (86, 82, 76), (62, 60, 56)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (104, 96, 84), (82, 76, 68))
    _window(img, d, 180, 120, 560, 470, (176, 196, 214), (214, 226, 236), (90, 84, 74))
    # 印刷機（ローラー）
    d.rounded_rectangle([1480, 380, 1880, int(H * 0.77)], radius=12, fill=(90, 96, 110))
    d.ellipse([1520, 330, 1650, 460], fill=(70, 76, 90))
    d.ellipse([1700, 330, 1830, 460], fill=(70, 76, 90))
    # 裁断台と紙の山
    d.rounded_rectangle([700, 560, 1380, int(H * 0.77)], radius=8, fill=(112, 92, 66))
    d.rectangle([700, 560, 1380, 596], fill=(92, 76, 56))
    for k in range(4):
        d.rectangle([760 + k * 6, 470 - k * 26, 1060 + k * 6, 560 - k * 26],
                    fill=(238 - k * 4, 236 - k * 4, 228 - k * 4))
    d.rectangle([1120, 500, 1330, 560], fill=(200, 202, 208))
    d.polygon([(1120, 500), (1330, 500), (1330, 516)], fill=(150, 154, 164))
    # 裸電球
    d.line([1000, 0, 1000, 130], fill=(56, 52, 46), width=6)
    glow(img, 1000, 170, 110, (255, 216, 140), 90)
    d.ellipse([974, 130, 1026, 202], fill=(255, 226, 150))
    return img


def machi_sengo() -> Image.Image:
    """戦後の街角（靴修理の屋台）。"""
    img = vgrad((W, H), (196, 186, 168), (224, 214, 196)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # バラック街並み
    for k, bx in enumerate(range(60, W, 380)):
        hh = 260 + (k % 2) * 50
        d.rectangle([bx, 560 - hh, bx + 320, 560], fill=(150, 132, 108) if k % 2 else (166, 146, 118))
        d.polygon([(bx - 16, 560 - hh), (bx + 160, 560 - hh - 60), (bx + 336, 560 - hh)],
                  fill=(110, 96, 78))
        d.rectangle([bx + 40, 560 - hh + 60, bx + 130, 560 - hh + 150], fill=(110, 102, 90))
    _floor(d, 560, (176, 160, 136), (152, 138, 118))
    # 靴修理の屋台（台・道具箱・靴）
    d.rounded_rectangle([700, 620, 1240, 800], radius=12, fill=(126, 102, 74))
    d.rectangle([700, 620, 1240, 654], fill=(104, 84, 62))
    for k in range(3):
        d.rounded_rectangle([760 + k * 150, 560, 860 + k * 150, 616], radius=14,
                            fill=(70, 56, 46))
        d.rectangle([760 + k * 150, 596, 860 + k * 150, 616], fill=(50, 40, 34))
    d.rectangle([1300, 660, 1480, 780], fill=(96, 80, 62))
    d.line([1300, 700, 1480, 700], fill=(80, 66, 52), width=5)
    # のぼり
    d.line([620, 400, 620, 800], fill=(110, 96, 78), width=10)
    d.rectangle([624, 410, 700, 700], fill=(220, 210, 190))
    return img


def home_nagaya() -> Image.Image:
    """岡田家の長屋（ちゃぶ台と試作道具）。"""
    img = vgrad((W, H), (92, 82, 68), (68, 60, 50)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.72), (166, 144, 104), (144, 124, 90))
    # 障子と柱
    for sx in (120, 1540):
        d.rounded_rectangle([sx, 120, sx + 280, 620], radius=6, fill=(224, 216, 196))
        for i in range(2):
            d.line([sx + 93 + i * 93, 120, sx + 93 + i * 93, 620],
                   fill=(150, 130, 104), width=7)
        for j in range(3):
            d.line([sx, 190 + j * 145, sx + 280, 190 + j * 145],
                   fill=(150, 130, 104), width=7)
    d.rectangle([480, 80, 520, int(H * 0.72)], fill=(110, 88, 62))
    # ちゃぶ台と試作道具（金ヤスリ・刃・チョコ）
    d.ellipse([760, 640, 1320, 830], fill=(140, 110, 74))
    d.ellipse([780, 630, 1300, 790], fill=(160, 128, 88))
    d.rounded_rectangle([880, 660, 1000, 690], radius=6, fill=(150, 154, 164))
    d.rounded_rectangle([1040, 650, 1180, 700], radius=6, fill=(120, 84, 60))
    for gx in range(1052, 1180, 26):
        d.line([gx, 650, gx, 700], fill=(96, 66, 48), width=3)
    for gy in (666, 684):
        d.line([1040, gy, 1180, gy], fill=(96, 66, 48), width=3)
    # 行灯風の明かり
    glow(img, 960, 200, 130, (255, 220, 150), 70)
    d.rectangle([920, 150, 1000, 250], fill=(240, 226, 180))
    d.line([920, 150, 1000, 150], fill=(110, 88, 62), width=8)
    d.line([920, 250, 1000, 250], fill=(110, 88, 62), width=8)
    return img


def tonya() -> Image.Image:
    """メーカーの応接室（売り込みの場）。"""
    img = vgrad((W, H), (110, 104, 96), (86, 82, 76)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.78), (130, 112, 92), (108, 94, 78))
    _window(img, d, 1420, 140, 1840, 520, (170, 190, 210), (210, 222, 234), (100, 92, 82))
    # 応接テーブルとソファ
    d.rounded_rectangle([760, 600, 1360, int(H * 0.78)], radius=10, fill=(96, 74, 54))
    d.rectangle([760, 600, 1360, 636], fill=(80, 62, 46))
    d.rounded_rectangle([820, 540, 1010, 600], radius=8, fill=(238, 238, 232))
    # 会社の額と棚
    d.rectangle([200, 180, 640, 300], fill=(214, 206, 190))
    d.rectangle([220, 200, 620, 280], fill=(160, 150, 134))
    d.rectangle([200, 380, 560, int(H * 0.78)], fill=(104, 92, 78))
    for r in range(3):
        d.rectangle([220, 410 + r * 150, 540, 510 + r * 150], fill=(140, 126, 108))
        for c in range(4):
            d.rounded_rectangle([236 + c * 80, 424 + r * 150, 292 + c * 80, 496 + r * 150],
                                radius=6, fill=(180, 170, 152))
    return img


def kojo_olfa() -> Image.Image:
    """岡田工業の町工場（黄色いカッターの生産）。"""
    img = vgrad((W, H), (80, 84, 94), (58, 62, 72)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    _floor(d, int(H * 0.77), (96, 90, 82), (74, 70, 64))
    _window(img, d, 200, 120, 620, 470, (176, 196, 214), (214, 226, 236), (88, 90, 100))
    # ベルトコンベアに黄色いカッター
    d.rounded_rectangle([700, 560, 1560, 620], radius=10, fill=(110, 116, 130))
    for k in range(5):
        d.rounded_rectangle([740 + k * 170, 520, 860 + k * 170, 556], radius=8, fill=YELLOW)
        d.polygon([(860 + k * 170, 526), (890 + k * 170, 538), (860 + k * 170, 550)],
                  fill=(190, 194, 204))
    d.rectangle([760, 620, 800, int(H * 0.77)], fill=(90, 96, 110))
    d.rectangle([1460, 620, 1500, int(H * 0.77)], fill=(90, 96, 110))
    # プレス機と出荷箱
    d.rounded_rectangle([1640, 300, 1880, int(H * 0.77)], radius=10, fill=(84, 90, 104))
    d.rectangle([1690, 380, 1830, 430], fill=(70, 76, 90))
    for k in range(2):
        d.rounded_rectangle([120 + k * 180, 620, 270 + k * 180, 760], radius=8,
                            fill=(180, 150, 110))
        d.line([120 + k * 180, 690, 270 + k * 180, 690], fill=(150, 122, 88), width=6)
    return img


PAINTERS = {
    "il_ck_desk": desk_now,
    "il_ck_insatsu": insatsu,
    "il_ck_machi": machi_sengo,
    "il_ck_home": home_nagaya,
    "il_ck_tonya": tonya,
    "il_ck_kojo": kojo_olfa,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
