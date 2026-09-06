#!/usr/bin/env python3
"""東京ディズニーランド・高橋政知の再現ドラマ（takahashi-urayasu）用の背景7種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
★商標に触れないため、パークの意匠・キャラクター・城などは一切描かない。
  この回で描くのは「海」「埋め立て」「交渉の部屋」であって、園の中身ではない。
トーンの設計:
  海・浦安   … 朝の水色。いちばん気持ちのいい画。ここが失われる側
  料亭       … 行灯の橙。交渉の温度
  埋め立て   … 灰と土。工事の無機質さ
  会議室     … 寒色で重く
  建設現場   … 夕方の橙。ここで色が戻る
立ち絵は x=0.3 と x=0.74 に常駐し、モブが x=0.46〜0.66 に立つので、
**見せたいものは画面の上半分**に置く。

実行: PYTHONPATH=. python3 scripts/gen_tdl_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402
from scripts.gen_yam_bgs import _building, _person, _desk  # noqa: E402


def _boat(d, x, y, s=1.0, body=(158, 128, 88)):
    """漁船。舳先が上がった木の船を横から。"""
    d.polygon([(x, y), (x + 300 * s, y), (x + 330 * s, y - 54 * s),
               (x - 20 * s, y - 44 * s)], fill=body,
              outline=(104, 82, 52))
    d.rectangle([x + 90 * s, y - 116 * s, x + 190 * s, y - 44 * s],
                fill=(184, 156, 116), outline=(104, 82, 52), width=int(5 * s))
    d.line([x + 250 * s, y - 44 * s, x + 250 * s, y - 190 * s],
           fill=(120, 96, 62), width=int(9 * s))


def _crane(d, x, y, s=1.0):
    """工事のクレーン。埋め立ての章に置く。"""
    d.rectangle([x - 16 * s, y - 420 * s, x + 16 * s, y], fill=(150, 152, 158))
    for k in range(7):
        yy = y - 60 * s * (k + 1)
        d.line([x - 16 * s, yy, x + 16 * s, yy - 30 * s], fill=(122, 124, 130),
               width=int(5 * s))
    d.line([x - 200 * s, y - 420 * s, x + 320 * s, y - 420 * s],
           fill=(150, 152, 158), width=int(14 * s))
    d.line([x + 250 * s, y - 420 * s, x + 250 * s, y - 240 * s],
           fill=(90, 92, 98), width=int(5 * s))
    d.rounded_rectangle([x + 216 * s, y - 240 * s, x + 284 * s, y - 180 * s],
                        radius=8 * s, fill=(190, 150, 60))


# ---------------------------------------------------------------- 現代
def ima() -> Image.Image:
    img = vgrad((W, H), (238, 240, 244), (214, 218, 224)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 780, (196, 178, 152), (162, 146, 122))
    _window(img, d, 700, 160, 1230, 540, (168, 204, 240), (226, 238, 248))
    d = ImageDraw.Draw(img)
    # 地図（浦安のあたり。文字も記号も描かない）
    d.rounded_rectangle([1320, 300, 1760, 660], radius=8, fill=(246, 244, 238),
                        outline=(170, 168, 162), width=6)
    d.polygon([(1350, 620), (1450, 480), (1620, 440), (1730, 520), (1730, 640),
               (1350, 640)], fill=(198, 214, 190))
    d.polygon([(1350, 340), (1730, 330), (1730, 520), (1620, 440), (1450, 480),
               (1350, 620)], fill=(178, 208, 232))
    glow(img, 960, 300, 400, (255, 252, 244), 54)
    return img


# ---------------------------------------------------------------- 海
def umi() -> Image.Image:
    """浦安の浅い海。この回でいちばん気持ちのいい画にする（失われる側だから）。"""
    img = vgrad((W, H), (176, 214, 244), (226, 236, 240)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 560, W, H], fill=(150, 190, 208))
    for r in range(14):
        y = 590 + r * 34
        for k in range(9):
            x = (k * 230 + (r % 2) * 110) % (W + 200) - 100
            d.arc([x, y - 12, x + 150, y + 12], 200, 340,
                  fill=(184, 214, 228), width=6)
    # 海苔の棚（浅さの記号）
    for k in range(9):
        x = 140 + k * 200
        d.line([x, 620, x, 700], fill=(96, 84, 66), width=7)
        d.line([x, 640, x + 160, 640], fill=(120, 106, 84), width=5)
    # 遠景の陸と、船
    d.rectangle([0, 540, W, 566], fill=(150, 168, 150))
    _boat(d, 1240, 800, 0.9)
    _boat(d, 340, 900, 0.62)
    glow(img, 500, 180, 380, (255, 250, 226), 90)
    return img


def ryotei() -> Image.Image:
    """料亭。行灯の橙。交渉の温度を出す。"""
    img = vgrad((W, H), (206, 176, 132), (182, 152, 112)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # 畳
    d.rectangle([0, 720, W, H], fill=(202, 194, 146))
    for c in range(6):
        d.rectangle([c * 330, 720, c * 330 + 10, H], fill=(172, 164, 118))
    d.line([0, 720, W, 720], fill=(172, 164, 118), width=8)
    # 障子と欄間
    d.rectangle([460, 150, 1460, 720], fill=(244, 238, 220))
    for c in range(9):
        d.rectangle([460 + c * 112, 150, 470 + c * 112, 720], fill=(176, 156, 122))
    for r in range(5):
        d.rectangle([460, 150 + r * 114, 1460, 160 + r * 114], fill=(176, 156, 122))
    d.rectangle([440, 120, 1480, 152], fill=(132, 104, 70))
    # 行灯
    for x in (300, 1660):
        d.rounded_rectangle([x - 52, 470, x + 52, 660], radius=8,
                            fill=(246, 226, 168), outline=(126, 100, 62), width=6)
        glow(img, x, 566, 190, (255, 214, 130), 96)
    # 座卓と徳利
    _desk(d, 700, 800, 1220, 900, (128, 88, 52), (94, 62, 34))
    d.rounded_rectangle([900, 740, 950, 800], radius=14, fill=(246, 244, 238),
                        outline=(190, 186, 174), width=4)
    for k in range(2):
        d.ellipse([1000 + k * 70, 764, 1044 + k * 70, 800], fill=(250, 248, 242),
                  outline=(196, 190, 178), width=4)
    return img


def office() -> Image.Image:
    img = vgrad((W, H), (228, 226, 220), (202, 200, 196)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 790, (150, 132, 110), (118, 102, 84))
    _window(img, d, 660, 170, 1260, 550, (166, 196, 226), (222, 230, 238),
            frame=(118, 116, 114))
    d = ImageDraw.Draw(img)
    _desk(d, 620, 800, 1300, 950, (124, 88, 56), (92, 62, 38))
    d.rectangle([760, 754, 920, 800], fill=(234, 230, 220))
    # 書棚
    d.rectangle([1360, 300, 1820, 800], fill=(178, 160, 134))
    for r in range(3):
        ty = 400 + r * 130
        d.rectangle([1374, ty, 1806, ty + 12], fill=(146, 130, 106))
        for c in range(9):
            d.rectangle([1390 + c * 46, ty - 84, 1424 + c * 46, ty],
                        fill=[(146, 74, 62), (74, 92, 128), (128, 118, 74)][(r + c) % 3])
    glow(img, 960, 300, 360, (255, 253, 246), 48)
    return img


def umetate() -> Image.Image:
    """埋め立て工事。灰と土。無機質に。"""
    img = vgrad((W, H), (176, 182, 190), (204, 200, 192)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # 残った海（右奥）
    d.rectangle([1200, 480, W, 700], fill=(148, 176, 192))
    for r in range(4):
        d.line([1200, 520 + r * 44, W, 520 + r * 44], fill=(170, 194, 208), width=5)
    # 土
    d.polygon([(0, 520), (1240, 500), (1240, H), (0, H)], fill=(158, 138, 108))
    for i in range(60):
        px = (i * 149) % 1240
        py = 560 + ((i * 83) % 420)
        s = 14 + (i % 4) * 8
        d.ellipse([px, py, px + s, py + s * 0.6], fill=(140, 122, 94))
    # 護岸のブロック
    for k in range(11):
        x = 1160 + (k % 3) * 60
        y = 700 - (k // 3) * 60
        d.rectangle([x, y - 56, x + 56, y], fill=(178, 178, 180),
                    outline=(140, 140, 144), width=4)
    _crane(d, 420, 520, 0.9)
    _crane(d, 900, 540, 0.66)
    # ダンプ
    d.rectangle([1380, 800, 1700, 900], fill=(150, 128, 70))
    d.polygon([(1700, 900), (1700, 810), (1790, 830), (1830, 900)],
              fill=(90, 92, 100))
    for cx in (1450, 1640, 1780):
        d.ellipse([cx - 40, 870, cx + 40, 950], fill=(46, 46, 52))
    return img


def kaigi() -> Image.Image:
    img = vgrad((W, H), (88, 90, 100), (60, 62, 70)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (74, 66, 60), (52, 46, 42))
    d.rectangle([0, 0, W, 800], fill=(82, 86, 98))
    for c in range(6):
        d.rectangle([60 + c * 314, 130, 60 + c * 314 + 248, 630],
                    fill=(94, 98, 112), outline=(70, 74, 86), width=5)
    d.polygon([(280, 900), (1640, 900), (1470, 790), (450, 790)],
              fill=(60, 52, 46))
    for k in range(6):
        d.polygon([(540 + k * 140, 786), (640 + k * 140, 786),
                   (632 + k * 140, 758), (548 + k * 140, 758)],
                  fill=(234, 232, 224))
    glow(img, 960, 250, 340, (140, 154, 184), 32)
    return img


def kensetsu() -> Image.Image:
    """建設現場。夕方の橙。ここで色が戻る。意匠は一切描かない（足場だけ）。"""
    img = vgrad((W, H), (250, 196, 130), (246, 226, 190)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 820, (168, 140, 104), (134, 112, 82))
    # 足場だけを組む（建物の形は出さない）
    for gx, gy, cols, rows in ((260, 820, 5, 6), (900, 820, 7, 7), (1560, 820, 4, 5)):
        cw, ch = 66, 62
        for c in range(cols + 1):
            d.line([gx + c * cw, gy, gx + c * cw, gy - rows * ch],
                   fill=(150, 140, 128), width=7)
        for r in range(rows + 1):
            d.line([gx, gy - r * ch, gx + cols * cw, gy - r * ch],
                   fill=(150, 140, 128), width=6)
        for r in range(0, rows, 2):
            d.line([gx, gy - r * ch, gx + cols * cw, gy - (r + 1) * ch],
                   fill=(166, 156, 142), width=4)
    _crane(d, 1300, 820, 1.0)
    # 作業員のシルエット
    for i in range(6):
        _person(d, 380 + i * 230, 900 + (i % 3) * 16, 120, (86, 74, 62))
    glow(img, 1600, 220, 460, (255, 200, 120), 110)
    return img


PAINTERS = {
    "il_tdl_ima": ima,
    "il_tdl_umi": umi,
    "il_tdl_ryotei": ryotei,
    "il_tdl_office": office,
    "il_tdl_umetate": umetate,
    "il_tdl_kaigi": kaigi,
    "il_tdl_kensetsu": kensetsu,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
