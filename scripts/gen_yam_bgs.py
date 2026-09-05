#!/usr/bin/env python3
"""山一證券・野澤正平の再現ドラマ（yamaichi-nozawa）用のイラスト背景15種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
トーンの設計:
  長野・畑・営業     … 明るい自然光。ここが「耕した分だけ返ってくる」世界
  明治の兜町          … セピア。百年前だと一目で分かるように彩度を落とす
  取り付け騒ぎ・飛ばし … 寒色＋低彩度。不穏
  バブル              … 唯一の高彩度。赤い数字で浮かれた感じ
  告白〜会見           … いちばん暗い。会見だけは青白い光にして異質にする
立ち絵は x=0.3 と x=0.74 に常駐し、モブが x=0.5〜0.62 に立つので、
**見せたいものは画面の上半分**に置く（下半分はキャラでほぼ隠れる）。

実行: PYTHONPATH=. python3 scripts/gen_yam_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402


# ---------------------------------------------------------------- 共通パーツ
def _building(d, x0, y0, x1, y1, body, win, cols=5, rows=6, lit=None):
    """ビル。lit を渡すとその割合の窓だけ明るくする（夜用）。"""
    d.rectangle([x0, y0, x1, y1], fill=body)
    ww = (x1 - x0) / (cols + 1)
    hh = (y1 - y0) / (rows + 1)
    for r in range(rows):
        for c in range(cols):
            wx = x0 + ww * (c + 0.6)
            wy = y0 + hh * (r + 0.6)
            col = win
            if lit is not None and ((r * 7 + c * 3) % 5) < lit:
                col = (250, 226, 150)
            d.rectangle([wx, wy, wx + ww * 0.66, wy + hh * 0.62], fill=col)


def _person(d, x, y, h, body=(58, 62, 78), head=(226, 198, 172)):
    """遠景のモブ（顔は描かない）。列や群衆に使う。"""
    hd = h * 0.22
    d.ellipse([x - hd / 2, y - h, x + hd / 2, y - h + hd], fill=head)
    d.polygon([(x - hd * 0.72, y), (x + hd * 0.72, y),
               (x + hd * 0.5, y - h + hd * 0.9), (x - hd * 0.5, y - h + hd * 0.9)],
              fill=body)


def _desk(d, x0, y0, x1, y1, top=(122, 84, 54), leg=(88, 58, 36)):
    d.rectangle([x0, y0, x1, y0 + 26], fill=top)
    d.rectangle([x0 + 24, y0 + 26, x0 + 46, y1], fill=leg)
    d.rectangle([x1 - 46, y0 + 26, x1 - 24, y1], fill=leg)


def _sepia(img, amount=0.55):
    """明治の場面用。彩度を落として黄ばませる。"""
    g = img.convert("L").convert("RGB")
    return Image.blend(img.convert("RGB"), Image.merge("RGB", (
        g.split()[0].point(lambda v: min(255, int(v * 1.10 + 18))),
        g.split()[1].point(lambda v: min(255, int(v * 1.00 + 8))),
        g.split()[2].point(lambda v: int(v * 0.80)))), amount).convert("RGBA")


# ---------------------------------------------------------------- 現代（茶番）
def ima() -> Image.Image:
    img = vgrad((W, H), (246, 240, 230), (222, 212, 198)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 760, (206, 178, 146), (170, 142, 112))
    _window(img, d, 720, 150, 1200, 520, (166, 208, 244), (222, 236, 248))
    d = ImageDraw.Draw(img)
    # 食器棚
    d.rounded_rectangle([1320, 300, 1700, 760], radius=10, fill=(196, 168, 140))
    for r in range(3):
        ty = 380 + r * 120
        d.rectangle([1336, ty, 1684, ty + 12], fill=(160, 132, 104))
        for c in range(4):
            cx = 1372 + c * 82
            d.ellipse([cx - 26, ty - 46, cx + 26, ty - 2], fill=(250, 248, 242),
                      outline=(198, 190, 178), width=3)
    # 割れたコップの破片（茶番の直後という設定）
    for k, (px, ang) in enumerate(((980, 20), (1040, -35), (1092, 8), (930, -14))):
        s = 20 + (k % 3) * 9
        d.polygon([(px, 800), (px + s, 796 - s * 0.5), (px + s * 1.5, 806)],
                  fill=(226, 238, 244), outline=(178, 196, 208))
    glow(img, 960, 320, 420, (255, 246, 220), 60)
    return img


# ---------------------------------------------------------------- 長野
def kawanakajima() -> Image.Image:
    img = vgrad((W, H), (176, 214, 244), (232, 240, 228)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # 遠山（北信の山並み）
    for base, col in ((640, (150, 168, 186)), (700, (128, 152, 164))):
        pts = [(0, base)]
        for i in range(11):
            pts.append((i * W / 10, base - 150 - 90 * math.sin(i * 1.1 + base)))
        pts += [(W, base), (W, H), (0, H)]
        d.polygon(pts, fill=col)
    # 田んぼ
    d.rectangle([0, 720, W, H], fill=(168, 190, 132))
    for r in range(6):
        y = 740 + r * 62
        d.line([0, y, W, y], fill=(140, 166, 108), width=5)
    # 農家（茅葺き）と物干し
    d.polygon([(1240, 560), (1560, 560), (1400, 430)], fill=(120, 98, 70))
    d.rectangle([1268, 560, 1532, 726], fill=(216, 202, 176))
    d.rectangle([1330, 620, 1400, 726], fill=(96, 74, 54))
    # 畳を干している（父の仕事。人は描かない）
    for k in range(3):
        x = 690 + k * 120
        d.polygon([(x, 700), (x + 96, 700), (x + 84, 560), (x - 12, 560)],
                  fill=(206, 196, 140), outline=(150, 140, 96), width=4)
        d.line([x - 6, 588, x + 90, 588], fill=(70, 92, 60), width=6)
    glow(img, 420, 200, 320, (255, 250, 214), 90)
    return img


def hatake() -> Image.Image:
    img = vgrad((W, H), (198, 220, 240), (246, 234, 206)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.polygon([(0, 640), (W, 590), (W, H), (0, H)], fill=(146, 122, 88))
    # 畝（遠近をつけて奥へ収束させる）
    for i in range(13):
        f = i / 12
        x_far = 300 + f * 1400
        x_near = -420 + f * 2700
        d.polygon([(x_far, 600), (x_far + 40, 600), (x_near + 150, H), (x_near, H)],
                  fill=(166, 140, 100) if i % 2 else (134, 110, 78))
    # 苗
    for i in range(70):
        px = (i * 149) % W
        py = 660 + ((i * 83) % 380)
        s = 8 + (py - 660) / 34
        d.polygon([(px, py), (px - s, py - s * 2.4), (px + s, py - s * 2.2)],
                  fill=(96, 138, 74))
    # 鍬（立てかけ）
    d.line([1520, 760, 1596, 470], fill=(126, 92, 58), width=16)
    d.polygon([(1500, 764), (1560, 748), (1566, 800), (1506, 812)], fill=(96, 100, 108))
    glow(img, 1500, 180, 380, (255, 236, 180), 96)
    return img


# ---------------------------------------------------------------- 明治の兜町
def meiji() -> Image.Image:
    img = vgrad((W, H), (206, 200, 176), (232, 224, 200)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (188, 176, 152), (154, 142, 120))
    # 木造の商店（切妻・格子）
    d.polygon([(600, 300), (1340, 300), (1240, 200), (700, 200)], fill=(112, 88, 60))
    d.rectangle([620, 300, 1320, 800], fill=(198, 176, 142))
    for c in range(9):
        cx = 660 + c * 74
        d.rectangle([cx, 360, cx + 10, 620], fill=(126, 100, 68))
    d.rectangle([620, 340, 1320, 356], fill=(140, 112, 76))
    # 看板（文字は描かず、山に一の印だけ）
    d.rounded_rectangle([840, 380, 1100, 520], radius=8, fill=(238, 230, 206),
                        outline=(120, 96, 62), width=7)
    d.polygon([(900, 480), (970, 400), (1040, 480)], fill=(60, 52, 42))
    d.rectangle([880, 494, 1060, 508], fill=(60, 52, 42))
    # 行灯と人力車の車輪
    d.rounded_rectangle([1370, 520, 1440, 660], radius=6, fill=(242, 226, 172),
                        outline=(120, 96, 62), width=5)
    d.ellipse([380, 640, 560, 820], outline=(112, 88, 60), width=14)
    for a in range(12):
        d.line([470, 730,
                470 + math.cos(a * math.pi / 6) * 84,
                730 + math.sin(a * math.pi / 6) * 84], fill=(112, 88, 60), width=5)
    return _sepia(img, 0.62)


# ---------------------------------------------------------------- 1964 兜町
def kabutocho() -> Image.Image:
    img = vgrad((W, H), (172, 202, 232), (226, 226, 218)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _building(d, 60, 180, 470, 800, (176, 172, 164), (120, 140, 158), 4, 8)
    _building(d, 500, 260, 900, 800, (196, 190, 178), (128, 148, 166), 4, 7)
    _building(d, 1020, 150, 1460, 800, (168, 164, 158), (118, 138, 156), 5, 9)
    _building(d, 1490, 300, 1880, 800, (200, 194, 182), (130, 150, 168), 4, 6)
    # 証券会社の袖看板（社名は描かない）
    for x, col in ((940, (186, 60, 54)), (1470, (44, 78, 140))):
        d.rectangle([x, 300, x + 62, 640], fill=col)
        for k in range(4):
            d.rectangle([x + 14, 330 + k * 78, x + 48, 380 + k * 78],
                        fill=(246, 242, 232))
    _floor(d, 800, (146, 146, 150), (112, 112, 118))
    # 通勤の列
    for i in range(9):
        _person(d, 240 + i * 190, 880 + (i % 3) * 16, 150 + (i % 4) * 10,
                (54 + (i % 3) * 12, 58, 74))
    glow(img, 1600, 200, 320, (255, 244, 210), 70)
    return img


def eigyo() -> Image.Image:
    """客先の座敷。営業の三十年。"""
    img = vgrad((W, H), (238, 228, 202), (216, 202, 172)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # 畳（主人公の生家と同じ素材、という含み）
    d.rectangle([0, 700, W, H], fill=(206, 198, 150))
    for c in range(6):
        d.rectangle([c * 330, 700, c * 330 + 10, H], fill=(176, 168, 122))
    d.line([0, 700, W, 700], fill=(176, 168, 122), width=8)
    # 障子
    d.rectangle([560, 160, 1400, 700], fill=(246, 242, 226))
    for c in range(7):
        d.rectangle([560 + c * 120, 160, 560 + c * 120 + 10, 700], fill=(178, 160, 128))
    for r in range(5):
        d.rectangle([560, 160 + r * 108, 1400, 170 + r * 108], fill=(178, 160, 128))
    d.rectangle([544, 148, 1416, 172], fill=(140, 112, 78))
    # 床の間と掛け軸
    d.rectangle([1460, 200, 1760, 700], fill=(198, 178, 146))
    d.rounded_rectangle([1540, 240, 1680, 600], radius=4, fill=(238, 232, 214),
                        outline=(150, 128, 98), width=5)
    # 座卓と湯呑み
    _desk(d, 760, 780, 1180, 900, (150, 106, 66), (112, 76, 44))
    for k in range(2):
        d.ellipse([850 + k * 190, 748, 900 + k * 190, 786], fill=(250, 248, 240),
                  outline=(190, 182, 168), width=4)
    return img


# ---------------------------------------------------------------- 1965 取り付け
def toritsuke() -> Image.Image:
    img = vgrad((W, H), (140, 152, 172), (188, 190, 190)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _building(d, 0, 120, 700, 820, (150, 148, 148), (96, 112, 130), 4, 8)
    _building(d, 1240, 90, 1920, 820, (140, 138, 140), (92, 108, 126), 5, 9)
    # 店頭（シャッター半分）
    d.rectangle([700, 300, 1240, 820], fill=(178, 174, 168))
    d.rectangle([720, 320, 1220, 560], fill=(96, 110, 126))
    for r in range(7):
        d.line([720, 330 + r * 34, 1220, 330 + r * 34], fill=(120, 132, 148), width=6)
    d.rectangle([700, 276, 1240, 306], fill=(120, 116, 112))
    _floor(d, 820, (128, 128, 132), (98, 98, 104))
    # 押し寄せる列（奥から手前へ、密度を上げる）
    for i in range(26):
        f = i / 25
        x = 120 + f * 1720 + ((i * 53) % 60)
        y = 850 + f * 180
        _person(d, x, y, 130 + f * 90, (46 + (i % 4) * 10, 50, 66))
    # 新聞（不穏の記号）
    d.polygon([(1520, 900), (1720, 872), (1740, 990), (1540, 1020)],
              fill=(240, 238, 230))
    for k in range(5):
        d.line([1546, 906 + k * 22, 1712, 894 + k * 22], fill=(150, 150, 148), width=6)
    img = Image.blend(img.convert("RGB"),
                      img.convert("L").convert("RGB"), 0.28).convert("RGBA")
    return img


# ---------------------------------------------------------------- バブル
def bubble() -> Image.Image:
    img = vgrad((W, H), (18, 20, 34), (40, 30, 46)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # 株価ボード
    d.rounded_rectangle([180, 120, 1740, 720], radius=14, fill=(12, 14, 22),
                        outline=(70, 74, 96), width=8)
    for r in range(7):
        y = 170 + r * 76
        d.line([200, y + 58, 1720, y + 58], fill=(38, 42, 58), width=3)
        for c in range(6):
            x = 220 + c * 252
            up = (r * 5 + c * 3) % 4 != 0
            col = (236, 78, 62) if up else (86, 190, 132)
            d.rectangle([x, y, x + 96, y + 40], fill=(70, 76, 96))
            for k in range(3):
                d.rectangle([x + 112 + k * 34, y + 6, x + 138 + k * 34, y + 40],
                            fill=col)
    # 上がり続ける折れ線
    pts, y = [], 660
    for i in range(15):
        y -= 18 + (i % 4) * 12
        pts.append((240 + i * 106, y))
    d.line(pts, fill=(255, 214, 60), width=12, joint="curve")
    d.polygon([(pts[-1][0] + 6, pts[-1][1]), (pts[-1][0] - 46, pts[-1][1] + 26),
               (pts[-1][0] - 34, pts[-1][1] - 40)], fill=(255, 214, 60))
    glow(img, 960, 400, 620, (255, 120, 90), 46)
    _floor(d, 820, (36, 34, 46), (66, 62, 82))
    return img


# ---------------------------------------------------------------- 飛ばし・役員室
def yakuinshitsu() -> Image.Image:
    img = vgrad((W, H), (34, 36, 48), (22, 24, 34)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (44, 40, 48), (30, 28, 36))
    # 長机（会議）
    d.polygon([(360, 900), (1560, 900), (1400, 790), (520, 790)],
              fill=(70, 52, 40))
    for k in range(6):
        x = 600 + k * 148
        d.rectangle([x, 762, x + 96, 792], fill=(228, 224, 212))
    # 背後の書棚（バインダーが並ぶ＝帳簿）
    d.rectangle([1280, 200, 1860, 800], fill=(52, 46, 44))
    for r in range(4):
        ty = 260 + r * 140
        d.rectangle([1296, ty + 110, 1844, ty + 124], fill=(38, 34, 32))
        for c in range(11):
            cx = 1306 + c * 48
            col = [(150, 62, 54), (58, 78, 118), (128, 116, 70)][(r + c) % 3]
            d.rectangle([cx, ty, cx + 38, ty + 110], fill=col)
    # 一冊だけ抜けている（隠された帳簿）
    d.rectangle([1306 + 5 * 48, 260 + 140, 1306 + 5 * 48 + 38, 260 + 140 + 110],
                fill=(18, 16, 20))
    glow(img, 760, 300, 300, (120, 140, 190), 46)
    return img


# ---------------------------------------------------------------- 社長室
def shachoshitsu() -> Image.Image:
    img = vgrad((W, H), (72, 70, 82), (44, 44, 56)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 790, (86, 66, 52), (62, 46, 36))
    _window(img, d, 700, 170, 1240, 560, (110, 130, 168), (176, 178, 176),
            frame=(56, 52, 60))
    d = ImageDraw.Draw(img)
    # 執務机
    _desk(d, 660, 800, 1300, 960, (96, 66, 44), (68, 46, 30))
    d.rectangle([760, 752, 900, 800], fill=(232, 228, 218))
    d.rounded_rectangle([1120, 742, 1240, 800], radius=6, fill=(40, 44, 56))
    # 社旗の代わりに、山に一の額（社名文字は描かない）
    d.rounded_rectangle([1420, 240, 1700, 470], radius=6, fill=(226, 218, 198),
                        outline=(120, 100, 70), width=8)
    d.polygon([(1490, 410), (1560, 320), (1630, 410)], fill=(60, 52, 42))
    d.rectangle([1470, 424, 1650, 438], fill=(60, 52, 42))
    glow(img, 970, 340, 340, (200, 216, 244), 52)
    return img


def ginkou() -> Image.Image:
    img = vgrad((W, H), (86, 84, 92), (56, 56, 64)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (96, 88, 80), (68, 62, 56))
    # 応接（重厚な壁パネル）
    d.rectangle([0, 0, W, 800], fill=(74, 66, 62))
    for c in range(8):
        d.rectangle([40 + c * 236, 120, 40 + c * 236 + 196, 700],
                    fill=(86, 76, 70), outline=(62, 54, 50), width=5)
    # 応接テーブルとソファ
    d.rounded_rectangle([700, 810, 1240, 900], radius=8, fill=(58, 46, 40))
    for x in (620, 1320):
        d.rounded_rectangle([x - 120, 760, x + 120, 900], radius=14,
                            fill=(74, 60, 56))
    # 書類の束
    d.polygon([(880, 800), (1080, 788), (1084, 812), (884, 824)],
              fill=(236, 232, 222))
    glow(img, 960, 260, 380, (150, 160, 190), 34)
    return img


def okurasho() -> Image.Image:
    img = vgrad((W, H), (60, 62, 72), (38, 40, 48)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 820, (78, 76, 74), (54, 52, 52))
    # 石造りの列柱（重さを出す）
    for c in range(5):
        x = 120 + c * 400
        d.rectangle([x, 90, x + 130, 820], fill=(104, 100, 96))
        d.rectangle([x - 22, 90, x + 152, 140], fill=(120, 116, 112))
        d.rectangle([x - 22, 770, x + 152, 820], fill=(120, 116, 112))
        for k in range(5):
            d.line([x + 22 + k * 22, 150, x + 22 + k * 22, 764],
                   fill=(88, 84, 82), width=5)
    # 奥の高窓
    for c in range(3):
        x = 420 + c * 420
        d.rounded_rectangle([x, 180, x + 200, 520], radius=6, fill=(130, 142, 160))
        d.line([x + 100, 180, x + 100, 520], fill=(70, 68, 68), width=8)
    glow(img, 960, 300, 420, (170, 184, 208), 38)
    return img


# ---------------------------------------------------------------- 夜・会見・街
def honsha_yoru() -> Image.Image:
    img = vgrad((W, H), (14, 18, 34), (30, 34, 52)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _building(d, 60, 240, 520, 860, (30, 34, 46), (24, 28, 38), 4, 9, lit=2)
    _building(d, 620, 110, 1300, 860, (34, 38, 52), (26, 30, 42), 6, 12, lit=3)
    _building(d, 1380, 300, 1860, 860, (28, 32, 44), (24, 28, 38), 4, 7, lit=1)
    _floor(d, 860, (24, 26, 36), (44, 48, 62))
    # 街灯
    for x in (300, 960, 1620):
        d.rectangle([x - 6, 700, x + 6, 880], fill=(52, 56, 70))
        d.ellipse([x - 26, 676, x + 26, 716], fill=(250, 236, 180))
        glow(img, x, 696, 130, (255, 234, 160), 70)
    glow(img, 960, 420, 460, (90, 120, 190), 40)
    return img


def kaiken() -> Image.Image:
    """記者会見場。青白い光と、カメラの砲列。ここだけ光の色を変える。"""
    img = vgrad((W, H), (26, 30, 44), (16, 18, 28)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # バックボード（社名は描かない）
    d.rectangle([420, 120, 1500, 620], fill=(34, 44, 70))
    for c in range(9):
        d.line([440 + c * 122, 120, 440 + c * 122, 620], fill=(42, 54, 84), width=4)
    d.rectangle([420, 120, 1500, 140], fill=(58, 74, 110))
    # 長机とマイクの束
    d.rectangle([300, 780, 1620, 900], fill=(46, 42, 46))
    d.rectangle([300, 760, 1620, 784], fill=(62, 58, 62))
    for k in range(9):
        mx = 720 + k * 54
        d.line([mx, 760, mx + (k - 4) * 6, 660], fill=(70, 74, 86), width=7)
        d.ellipse([mx + (k - 4) * 6 - 15, 634, mx + (k - 4) * 6 + 15, 668],
                  fill=(38, 40, 50))
    # カメラの砲列（手前・シルエット）
    for k in range(6):
        cx = 120 + k * 352
        d.rectangle([cx, 960, cx + 150, 1080], fill=(18, 20, 28))
        d.ellipse([cx + 92, 968, cx + 178, 1054], fill=(24, 26, 36),
                  outline=(52, 56, 70), width=6)
        d.rectangle([cx + 34, 916, cx + 92, 962], fill=(18, 20, 28))
    # フラッシュ
    for fx, fy, r in ((300, 430, 190), (1560, 380, 210), (900, 300, 150)):
        glow(img, fx, fy, r, (220, 234, 255), 84)
    return img


def machi() -> Image.Image:
    """履歴書を持って歩く街。朝。ここで初めて色が戻る。"""
    img = vgrad((W, H), (196, 220, 242), (244, 234, 214)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _building(d, 0, 260, 420, 800, (206, 200, 190), (150, 168, 186), 3, 6)
    _building(d, 1520, 220, 1920, 800, (198, 192, 184), (146, 164, 184), 3, 7)
    _building(d, 460, 340, 900, 800, (214, 206, 194), (152, 170, 190), 4, 5)
    _building(d, 960, 300, 1460, 800, (204, 198, 188), (148, 166, 186), 4, 6)
    _floor(d, 800, (170, 168, 168), (140, 138, 140))
    # 横断歩道
    for k in range(9):
        d.polygon([(60 + k * 210, 1080), (170 + k * 210, 1080),
                   (250 + k * 210, 880), (170 + k * 210, 880)],
                  fill=(238, 238, 236))
    # 街路樹
    for x in (330, 1180, 1700):
        d.rectangle([x - 12, 640, x + 12, 800], fill=(110, 88, 66))
        d.ellipse([x - 96, 500, x + 96, 690], fill=(122, 168, 108))
    glow(img, 1500, 180, 420, (255, 246, 208), 96)
    return img


PAINTERS = {
    "il_yam_ima": ima,
    "il_yam_kawanakajima": kawanakajima,
    "il_yam_hatake": hatake,
    "il_yam_meiji": meiji,
    "il_yam_kabutocho": kabutocho,
    "il_yam_eigyo": eigyo,
    "il_yam_toritsuke": toritsuke,
    "il_yam_bubble": bubble,
    "il_yam_yakuinshitsu": yakuinshitsu,
    "il_yam_shachoshitsu": shachoshitsu,
    "il_yam_ginko": ginkou,
    "il_yam_okurasho": okurasho,
    "il_yam_honsha_yoru": honsha_yoru,
    "il_yam_kaiken": kaiken,
    "il_yam_machi": machi,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
