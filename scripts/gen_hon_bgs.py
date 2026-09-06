#!/usr/bin/env python3
"""ホンダ・本田宗一郎の再現ドラマ（honda-soichiro）用の背景8種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
トーンの設計:
  鍛冶屋・小屋 … 炉の橙。手を動かす場所は暖色でまとめる
  アート商会    … 大正の土間。彩度低めの茶
  焼け跡        … いちばん彩度を落とす（全部を手放す章）
  工場・社長室  … 蛍光灯の白と、木の茶
  サーキット    … 芝の緑と空。ここだけ屋外で開ける
立ち絵は x=0.3 と x=0.74 に常駐し、モブが x=0.5〜0.62 に立つので、
**見せたいものは画面の上半分**に置く。

実行: PYTHONPATH=. python3 scripts/gen_hon_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402
from scripts.gen_yam_bgs import _building, _desk  # noqa: E402


def _bike(d, x, y, s=1.0, body=(196, 40, 36)):
    """バイクを横から。車輪2つとタンクとハンドルで形を作る。"""
    for cx in (x, x + 300 * s):
        d.ellipse([cx - 78 * s, y - 78 * s, cx + 78 * s, y + 78 * s],
                  outline=(40, 40, 46), width=int(18 * s))
        d.ellipse([cx - 12 * s, y - 12 * s, cx + 12 * s, y + 12 * s],
                  fill=(150, 154, 162))
    d.polygon([(x + 20 * s, y - 20 * s), (x + 160 * s, y - 96 * s),
               (x + 280 * s, y - 30 * s), (x + 150 * s, y - 10 * s)], fill=body)
    d.rounded_rectangle([x + 120 * s, y - 128 * s, x + 240 * s, y - 88 * s],
                        radius=18 * s, fill=body, outline=(110, 20, 18),
                        width=int(5 * s))
    d.line([x + 300 * s, y, x + 330 * s, y - 130 * s], fill=(90, 94, 102),
           width=int(12 * s))
    d.line([x + 300 * s, y - 130 * s, x + 370 * s, y - 140 * s],
           fill=(90, 94, 102), width=int(10 * s))
    d.line([x + 20 * s, y, x + 90 * s, y - 40 * s], fill=(90, 94, 102),
           width=int(10 * s))


def _anvil(d, x, y, s=1.0):
    """金床。鍛冶屋の記号。"""
    d.polygon([(x, y), (x + 220 * s, y), (x + 200 * s, y - 46 * s),
               (x + 20 * s, y - 46 * s)], fill=(96, 98, 106))
    d.polygon([(x + 60 * s, y - 46 * s), (x + 160 * s, y - 46 * s),
               (x + 150 * s, y - 110 * s), (x + 70 * s, y - 110 * s)],
              fill=(112, 114, 122))
    d.polygon([(x + 10 * s, y - 110 * s), (x + 240 * s, y - 110 * s),
               (x + 250 * s, y - 150 * s), (x - 10 * s, y - 150 * s)],
              fill=(132, 134, 142))
    d.polygon([(x + 250 * s, y - 150 * s), (x + 330 * s, y - 136 * s),
               (x + 250 * s, y - 112 * s)], fill=(132, 134, 142))


# ---------------------------------------------------------------- 現代
def ima() -> Image.Image:
    img = vgrad((W, H), (242, 240, 236), (216, 212, 206)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 780, (192, 172, 148), (158, 140, 118))
    _window(img, d, 700, 160, 1230, 540, (170, 204, 240), (226, 236, 246))
    d = ImageDraw.Draw(img)
    # 壁に貼った紙（宣言の記号）
    d.rounded_rectangle([1330, 300, 1740, 620], radius=6, fill=(250, 250, 244),
                        outline=(180, 176, 168), width=6)
    for r in range(6):
        d.line([1370, 360 + r * 42, 1700 - (r % 2) * 90, 360 + r * 42],
               fill=(198, 196, 190), width=8)
    glow(img, 960, 300, 400, (255, 252, 242), 54)
    return img


# ---------------------------------------------------------------- 鍛冶屋
def kajiya() -> Image.Image:
    img = vgrad((W, H), (96, 72, 54), (140, 106, 74)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (110, 84, 60), (82, 62, 44))
    d.rectangle([0, 0, W, 800], fill=(112, 84, 60))
    # 板壁
    for c in range(14):
        d.line([c * 140, 0, c * 140, 800], fill=(96, 72, 52), width=8)
    # 炉
    d.rounded_rectangle([1280, 460, 1720, 800], radius=10, fill=(88, 66, 48),
                        outline=(64, 48, 34), width=8)
    d.ellipse([1400, 560, 1620, 720], fill=(40, 26, 18))
    glow(img, 1510, 640, 210, (255, 150, 50), 120)
    # ふいご
    d.polygon([(1160, 800), (1280, 760), (1280, 660), (1160, 700)],
              fill=(126, 96, 66), outline=(88, 66, 44), width=6)
    _anvil(d, 300, 800, 1.0)
    # 吊るした道具
    for k in range(5):
        x = 640 + k * 90
        d.line([x, 120, x, 240 + (k % 3) * 40], fill=(70, 72, 80), width=7)
        d.rounded_rectangle([x - 22, 240 + (k % 3) * 40, x + 22,
                             300 + (k % 3) * 40], radius=6, fill=(120, 122, 130))
    return img


def artshokai() -> Image.Image:
    """大正の自動車修理工場。土間と、ばらした部品。"""
    img = vgrad((W, H), (188, 174, 152), (208, 196, 172)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 810, (150, 132, 108), (118, 102, 82))
    d.rectangle([0, 0, W, 810], fill=(196, 182, 158))
    for c in range(9):
        d.rectangle([40 + c * 214, 120, 40 + c * 214 + 170, 520],
                    fill=(176, 162, 140), outline=(146, 132, 112), width=5)
    # 木箱と部品
    for k in range(4):
        x = 220 + (k % 2) * 190
        y = 810 - (k // 2) * 150
        d.rectangle([x, y - 140, x + 170, y], fill=(170, 138, 96),
                    outline=(126, 100, 66), width=6)
    for k in range(5):
        cx, cy = 900 + k * 96, 740 + (k % 2) * 60
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(128, 132, 140),
                  outline=(88, 92, 100), width=5)
        for a in range(8):
            ang = a * math.pi / 4
            d.line([cx + math.cos(ang) * 34, cy + math.sin(ang) * 34,
                    cx + math.cos(ang) * 48, cy + math.sin(ang) * 48],
                   fill=(108, 112, 120), width=7)
    _bike(d, 1440, 800, 0.6, (150, 128, 96))
    glow(img, 500, 200, 300, (255, 244, 214), 60)
    return img


def yakeato() -> Image.Image:
    """三河地震と敗戦。全部を手放す章。彩度をいちばん落とす。"""
    img = vgrad((W, H), (166, 164, 158), (196, 192, 184)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 830, (150, 146, 140), (120, 116, 112))
    # 倒れた柱と、抜けた屋根
    for k, (x, ang) in enumerate(((260, -24), (760, 16), (1320, -12), (1700, 22))):
        L = 320
        d.line([x, 830, x + math.cos(math.radians(ang - 90)) * L,
                830 + math.sin(math.radians(ang - 90)) * L],
               fill=(128, 122, 116), width=30)
    # 瓦礫
    for i in range(26):
        px = (i * 173) % W
        py = 840 + ((i * 61) % 140)
        s = 26 + (i % 4) * 12
        d.polygon([(px, py), (px + s, py - s * 0.5), (px + s * 1.6, py + s * 0.3)],
                  fill=(142, 138, 132) if i % 2 else (160, 156, 150))
    img = Image.blend(img.convert("RGB"), img.convert("L").convert("RGB"),
                      0.58).convert("RGBA")
    return img


def koya() -> Image.Image:
    """終戦直後の小屋。自転車と、拾ってきた発動機。"""
    img = vgrad((W, H), (206, 190, 160), (226, 212, 182)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (162, 138, 104), (128, 108, 80))
    d.rectangle([0, 0, W, 800], fill=(196, 180, 152))
    for c in range(12):
        d.line([c * 164, 0, c * 164, 800], fill=(172, 156, 128), width=7)
    # 自転車
    for cx in (620, 900):
        d.ellipse([cx - 92, 660, cx + 92, 844], outline=(80, 74, 68), width=13)
        for a in range(12):
            d.line([cx, 752, cx + math.cos(math.radians(a * 30)) * 84,
                    752 + math.sin(math.radians(a * 30)) * 84],
                   fill=(120, 114, 106), width=4)
    d.line([620, 752, 780, 640], fill=(96, 90, 82), width=13)
    d.line([780, 640, 900, 752], fill=(96, 90, 82), width=13)
    d.line([700, 700, 860, 700], fill=(96, 90, 82), width=11)
    d.rounded_rectangle([740, 690, 830, 750], radius=8, fill=(120, 118, 124),
                        outline=(80, 78, 84), width=6)
    # 木箱と工具
    d.rectangle([1300, 660, 1560, 800], fill=(172, 140, 98),
                outline=(126, 100, 66), width=6)
    for k in range(4):
        d.rectangle([1340 + k * 56, 606, 1372 + k * 56, 660], fill=(130, 134, 142))
    glow(img, 400, 200, 320, (255, 246, 214), 76)
    return img


def kojo() -> Image.Image:
    """工場。作業台と、並ぶバイク。"""
    img = vgrad((W, H), (216, 218, 220), (192, 194, 198)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 800], fill=(206, 208, 212))
    for k in range(5):
        x = k * 400
        d.polygon([(x, 250), (x + 400, 250), (x + 400, 110), (x + 200, 110)],
                  fill=(162, 166, 174))
        d.polygon([(x + 200, 110), (x + 400, 110), (x + 400, 250)],
                  fill=(192, 212, 230))
    _floor(d, 800, (152, 150, 148), (120, 118, 118))
    _desk(d, 240, 800, 760, 940, (120, 100, 76), (88, 72, 54))
    for k in range(5):
        d.rectangle([300 + k * 86, 756, 340 + k * 86, 800], fill=(140, 144, 152))
    _bike(d, 1180, 830, 0.72)
    glow(img, 700, 200, 340, (250, 252, 255), 46)
    return img


def shachoshitsu() -> Image.Image:
    img = vgrad((W, H), (94, 84, 76), (66, 60, 56)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 790, (104, 80, 58), (76, 58, 42))
    _window(img, d, 690, 170, 1250, 550, (128, 146, 176), (188, 190, 188),
            frame=(64, 58, 54))
    d = ImageDraw.Draw(img)
    _desk(d, 640, 800, 1300, 960, (104, 74, 50), (74, 52, 34))
    d.rectangle([740, 754, 900, 800], fill=(234, 230, 220))
    # 壁に、レースの写真らしき額（中身は描かない）
    for k in range(2):
        d.rounded_rectangle([1400 + k * 220, 260, 1580 + k * 220, 420], radius=6,
                            fill=(216, 210, 196), outline=(120, 100, 74), width=7)
        d.polygon([(1420 + k * 220, 400), (1500 + k * 220, 320),
                   (1560 + k * 220, 400)], fill=(150, 146, 138))
    glow(img, 960, 320, 340, (200, 212, 236), 46)
    return img


def circuit() -> Image.Image:
    """サーキット。屋外で開ける画にする。"""
    img = vgrad((W, H), (152, 196, 236), (222, 232, 226)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for base, col in ((520, (150, 176, 158)), (580, (124, 156, 136))):
        pts = [(0, base)]
        for i in range(9):
            pts.append((i * W / 8, base - 110 - 70 * math.sin(i * 1.5 + base)))
        pts += [(W, base), (W, H), (0, H)]
        d.polygon(pts, fill=col)
    d.rectangle([0, 600, W, 720], fill=(140, 176, 120))
    # コースと縁石
    d.polygon([(0, H), (W, H), (W, 700), (0, 760)], fill=(70, 70, 76))
    for k in range(16):
        d.polygon([(k * 130 - 30, 770), (k * 130 + 40, 766),
                   (k * 130 + 44, 792), (k * 130 - 26, 796)],
                  fill=(214, 76, 66) if k % 2 else (238, 238, 234))
    # 観客のシルエット
    for i in range(40):
        px = (i * 97) % W
        d.ellipse([px, 600 - (i % 3) * 12, px + 20, 626 - (i % 3) * 12],
                  fill=(96, 100, 110))
    _bike(d, 620, 940, 0.9)
    _bike(d, 1320, 900, 0.7, (60, 66, 120))
    glow(img, 1520, 160, 400, (255, 250, 220), 84)
    return img


PAINTERS = {
    "il_hon_ima": ima,
    "il_hon_kajiya": kajiya,
    "il_hon_artshokai": artshokai,
    "il_hon_yakeato": yakeato,
    "il_hon_koya": koya,
    "il_hon_kojo": kojo,
    "il_hon_shachoshitsu": shachoshitsu,
    "il_hon_circuit": circuit,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
