#!/usr/bin/env python3
"""ロータリーエンジン・山本健一の再現ドラマ（yamamoto-rotary）用の背景8種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
トーンの設計:
  工場・研究室 … 蛍光灯の白。ここが主戦場なので中間色でまとめる
  西ドイツ      … 寒色。よそ行きの緊張
  カーボン会社  … 黒と銀。素材の話だと分かる色
  ショールーム  … いちばん明るい。売れた瞬間
  ガソリン station … 曇天。逆風の章
  ル・マン      … 夜のサーキット。光の線で速さを出す
立ち絵は x=0.3 と x=0.74 に常駐し、モブが x=0.46〜0.66 に立つので、
**見せたいものは画面の上半分**に置く。

実行: PYTHONPATH=. python3 scripts/gen_rot_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402
from scripts.gen_yam_bgs import _building, _desk  # noqa: E402


def _rotor(d, cx, cy, r, body=(196, 202, 212), edge=(120, 126, 138)):
    """ロータリーの断面。おにぎり型のローターと、繭型のハウジング。

    この回の主役なので、研究室の背景に大きく描いて「何の話か」を一目で出す。
    """
    # ハウジング（繭型）を多角形で近似
    pts = []
    for i in range(120):
        t = i / 120 * 2 * math.pi
        rr = r * (1.0 + 0.30 * math.cos(2 * t))
        pts.append((cx + math.cos(t) * rr, cy + math.sin(t) * rr * 0.78))
    d.polygon(pts, fill=(70, 74, 86), outline=edge)
    for k in range(3):
        d.line(pts[k::3][:40], fill=edge, width=4)
    # ローター（おにぎり＝ルーローの三角形っぽく）
    tri = []
    for i in range(3):
        a = i * 2 * math.pi / 3 - math.pi / 2
        tri.append((cx + math.cos(a) * r * 0.72, cy + math.sin(a) * r * 0.56))
    d.polygon(tri, fill=body, outline=edge, width=6)
    for (px, py) in tri:                      # 角＝アペックスシール
        d.ellipse([px - r * 0.06, py - r * 0.06, px + r * 0.06, py + r * 0.06],
                  fill=(232, 96, 60), outline=(140, 40, 24), width=4)
    d.ellipse([cx - r * 0.14, cy - r * 0.14, cx + r * 0.14, cy + r * 0.14],
              fill=(96, 100, 112), outline=edge, width=4)


def _lathe(d, x, y, s=1.0):
    """工作機械。工場の場面に置く。"""
    d.rounded_rectangle([x, y - 150 * s, x + 340 * s, y], radius=8 * s,
                        fill=(96, 110, 122), outline=(64, 74, 84), width=int(6 * s))
    d.rounded_rectangle([x + 30 * s, y - 240 * s, x + 120 * s, y - 150 * s],
                        radius=6 * s, fill=(110, 124, 136))
    d.line([x + 120 * s, y - 196 * s, x + 300 * s, y - 196 * s],
           fill=(180, 186, 194), width=int(14 * s))
    d.ellipse([x + 250 * s, y - 224 * s, x + 320 * s, y - 168 * s],
              fill=(150, 156, 166), outline=(84, 92, 102), width=int(5 * s))


# ---------------------------------------------------------------- 現代
def ima() -> Image.Image:
    img = vgrad((W, H), (238, 240, 244), (212, 216, 222)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 780, (176, 178, 184), (146, 148, 154))
    _window(img, d, 700, 160, 1240, 540, (168, 202, 238), (222, 234, 246))
    d = ImageDraw.Draw(img)
    # 棚に模型のエンジン
    d.rounded_rectangle([1330, 380, 1740, 780], radius=10, fill=(190, 178, 162))
    d.rectangle([1346, 560, 1724, 574], fill=(156, 144, 128))
    _rotor(d, 1450, 490, 76)
    d.rounded_rectangle([1580, 600, 1700, 700], radius=8, fill=(140, 148, 160),
                        outline=(96, 104, 116), width=5)
    glow(img, 960, 320, 400, (255, 252, 240), 54)
    return img


# ---------------------------------------------------------------- 工場・研究室
def kojo() -> Image.Image:
    img = vgrad((W, H), (204, 208, 212), (176, 180, 186)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # 鋸屋根の工場
    for k in range(5):
        x = k * 400
        d.polygon([(x, 300), (x + 400, 300), (x + 400, 150), (x + 200, 150)],
                  fill=(150, 156, 164))
        d.polygon([(x + 200, 150), (x + 400, 150), (x + 400, 300)],
                  fill=(186, 206, 224))
    d.rectangle([0, 300, W, 320], fill=(120, 126, 134))
    _floor(d, 800, (150, 146, 142), (118, 114, 112))
    _lathe(d, 180, 800, 0.9)
    _lathe(d, 1380, 800, 0.9)
    # 変速機のギアが箱に
    for k in range(4):
        cx, cy = 900 + (k % 2) * 130, 720 + (k // 2) * 90
        d.ellipse([cx - 46, cy - 46, cx + 46, cy + 46], fill=(140, 146, 156),
                  outline=(92, 98, 108), width=5)
        for a in range(10):
            ang = a * math.pi / 5
            d.line([cx + math.cos(ang) * 40, cy + math.sin(ang) * 40,
                    cx + math.cos(ang) * 56, cy + math.sin(ang) * 56],
                   fill=(120, 126, 136), width=8)
    glow(img, 500, 200, 340, (250, 252, 255), 52)
    return img


def kenkyu() -> Image.Image:
    """研究室。壁に大きくロータリーの断面図を貼る（この回の主役）。"""
    img = vgrad((W, H), (222, 224, 228), (198, 200, 206)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 790, (160, 156, 152), (128, 124, 122))
    d.rectangle([0, 0, W, 790], fill=(214, 216, 220))
    # 黒板／図面ボード
    d.rounded_rectangle([560, 120, 1400, 620], radius=10, fill=(246, 246, 244),
                        outline=(150, 150, 148), width=8)
    _rotor(d, 830, 370, 180)
    # 右側に、波打った面の断面（悪魔の爪痕）
    base = 470
    pts = [(1080 + i * 14, base - 26 * math.sin(i * 0.9)) for i in range(22)]
    d.line(pts, fill=(206, 60, 52), width=9, joint="curve")
    d.line([1080, base + 40, 1374, base + 40], fill=(120, 120, 124), width=6)
    for i in range(0, 22, 3):
        d.line([1080 + i * 14, base - 26 * math.sin(i * 0.9),
                1080 + i * 14, base + 40], fill=(190, 190, 194), width=3)
    # 試験台
    _desk(d, 260, 800, 700, 940, (120, 124, 132), (88, 92, 100))
    d.rounded_rectangle([340, 730, 620, 800], radius=8, fill=(150, 156, 166),
                        outline=(100, 106, 116), width=5)
    glow(img, 960, 300, 380, (255, 255, 250), 44)
    return img


def nsu() -> Image.Image:
    """西ドイツの工場。寒色でよそ行きの緊張を出す。"""
    img = vgrad((W, H), (168, 184, 206), (196, 202, 210)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (140, 146, 156), (110, 116, 126))
    d.rectangle([0, 0, W, 800], fill=(182, 192, 206))
    # アーチ窓の並ぶ古い工場
    for k in range(5):
        x = 160 + k * 340
        d.rounded_rectangle([x, 200, x + 210, 600], radius=100, fill=(122, 146, 176))
        d.line([x + 105, 200, x + 105, 600], fill=(90, 100, 116), width=8)
        d.line([x, 400, x + 210, 400], fill=(90, 100, 116), width=8)
    # 台に載ったエンジン
    _desk(d, 700, 820, 1220, 960, (108, 100, 92), (78, 72, 66))
    _rotor(d, 960, 740, 110)
    glow(img, 960, 300, 380, (220, 232, 248), 44)
    return img


def carbon() -> Image.Image:
    """カーボン会社。黒と銀。素材の話だと色で分かるようにする。"""
    img = vgrad((W, H), (56, 58, 64), (38, 40, 46)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (52, 52, 58), (36, 36, 42))
    # 炉と配管
    d.rounded_rectangle([1240, 200, 1720, 800], radius=12, fill=(72, 74, 82),
                        outline=(46, 48, 54), width=8)
    d.ellipse([1360, 380, 1600, 620], fill=(28, 28, 34), outline=(96, 98, 106),
              width=8)
    glow(img, 1480, 500, 190, (255, 140, 60), 96)
    for k in range(3):
        d.line([1240, 300 + k * 160, 900, 300 + k * 160], fill=(88, 90, 98),
               width=22)
    # 作業台に、黒い粉と銀のインゴット
    _desk(d, 300, 810, 900, 950, (74, 68, 62), (52, 48, 44))
    d.ellipse([380, 742, 560, 812], fill=(26, 26, 30), outline=(70, 70, 78),
              width=5)
    for k in range(3):
        d.polygon([(640 + k * 70, 806), (700 + k * 70, 806),
                   (690 + k * 70, 762), (650 + k * 70, 762)],
                  fill=(196, 200, 210), outline=(140, 144, 154), width=4)
    return img


def showroom() -> Image.Image:
    """ショールーム。この回でいちばん明るい画。"""
    img = vgrad((W, H), (250, 248, 242), (226, 224, 218)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (206, 202, 196), (176, 172, 166))
    # 全面ガラス
    d.rectangle([0, 0, W, 800], fill=(238, 240, 242))
    for k in range(6):
        d.line([180 + k * 300, 0, 180 + k * 300, 800], fill=(198, 202, 206),
               width=10)
    d.line([0, 300, W, 300], fill=(198, 202, 206), width=10)
    # 展示台に、低いクーペのシルエット
    d.ellipse([420, 780, 1500, 900], fill=(226, 222, 214))
    d.polygon([(520, 800), (740, 700), (1180, 690), (1400, 800)],
              fill=(196, 44, 40))
    d.polygon([(760, 700), (1150, 694), (1080, 634), (830, 638)],
              fill=(180, 208, 232), outline=(140, 40, 36), width=5)
    for cx in (700, 1230):
        d.ellipse([cx - 62, 762, cx + 62, 862], fill=(48, 48, 54))
        d.ellipse([cx - 26, 798, cx + 26, 850], fill=(180, 184, 192))
    glow(img, 960, 260, 460, (255, 252, 236), 78)
    return img


def gas() -> Image.Image:
    """給油所。曇天。逆風の章。"""
    img = vgrad((W, H), (172, 176, 182), (198, 198, 196)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 810, (152, 152, 156), (122, 122, 128))
    # 屋根
    d.rectangle([120, 240, 1800, 320], fill=(200, 198, 192))
    for x in (240, 1660):
        d.rectangle([x, 320, x + 40, 810], fill=(184, 182, 176))
    # 計量機と、並ぶ車の影
    for k in range(2):
        x = 700 + k * 460
        d.rounded_rectangle([x, 560, x + 120, 810], radius=8, fill=(206, 88, 68),
                            outline=(140, 56, 42), width=6)
        d.rounded_rectangle([x + 22, 600, x + 98, 680], radius=4,
                            fill=(240, 238, 230))
    for k in range(3):
        x = 200 + k * 520
        d.polygon([(x, 900), (x + 90, 840), (x + 300, 836), (x + 380, 900)],
                  fill=(120, 120, 128))
    glow(img, 960, 200, 420, (226, 226, 224), 40)
    return img


def lemans() -> Image.Image:
    """夜のサーキット。光の線で速さを出す。"""
    img = vgrad((W, H), (16, 18, 30), (30, 32, 44)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # 観客席（点の集合）
    for i in range(420):
        px = (i * 137) % W
        py = 180 + ((i * 71) % 220)
        c = [(180, 170, 160), (140, 140, 150), (200, 190, 170)][i % 3]
        d.ellipse([px, py, px + 7, py + 7], fill=c)
    d.rectangle([0, 420, W, 470], fill=(48, 50, 60))
    # コースと白線
    d.rectangle([0, 470, W, H], fill=(38, 38, 44))
    for k in range(11):
        d.rectangle([k * 190 - 40, 700, k * 190 + 80, 716], fill=(210, 210, 206))
    # ヘッドライトの流れ
    for k, (y, ln) in enumerate(((560, 900), (640, 1300), (830, 1700))):
        glow(img, 300 + k * 200, y, 130, (255, 240, 190), 80)
        d.line([300 + k * 200, y, 300 + k * 200 + ln, y],
               fill=(255, 232, 170, 90), width=10 - k * 2)
    # ピットの明かり
    for k in range(4):
        glow(img, 260 + k * 480, 380, 150, (255, 226, 150), 46)
    return img


PAINTERS = {
    "il_rot_ima": ima,
    "il_rot_kojo": kojo,
    "il_rot_kenkyu": kenkyu,
    "il_rot_nsu": nsu,
    "il_rot_carbon": carbon,
    "il_rot_showroom": showroom,
    "il_rot_gas": gas,
    "il_rot_lemans": lemans,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
