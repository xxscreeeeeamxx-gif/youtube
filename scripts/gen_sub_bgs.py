#!/usr/bin/env python3
"""スバル360・百瀬晋六の再現ドラマ（momose-subaru360）用の背景8種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
トーンの設計:
  中島飛行機   … 冷たい格納庫の灰。まだ戦時
  廃墟         … いちばん彩度を落とす（飛行機を取り上げられた章）
  バス工場・設計室 … 作業灯の白。ここが主戦場
  会議室       … 銀行に断られる章なので寒色で重く
  町・工場      … 明るく戻す。売れた先の景色
立ち絵は x=0.3 と x=0.74 に常駐し、モブが x=0.5〜0.62 に立つので、
**見せたいものは画面の上半分**に置く。

実行: PYTHONPATH=. python3 scripts/gen_sub_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402
from scripts.gen_yam_bgs import _building, _desk  # noqa: E402


def _kei_car(d, x, y, s=1.0, body=(226, 196, 108)):
    """てんとう虫。丸い軽自動車を横から。角を落として中を広く見せる形。"""
    w, h = 520 * s, 200 * s
    d.ellipse([x, y - h, x + w, y + h * 0.3], fill=body,
              outline=(150, 122, 52), width=int(7 * s))
    d.ellipse([x + w * 0.18, y - h * 0.92, x + w * 0.82, y - h * 0.24],
              fill=(178, 208, 232), outline=(150, 122, 52), width=int(6 * s))
    d.line([x + w * 0.5, y - h * 0.92, x + w * 0.5, y - h * 0.24],
           fill=(150, 122, 52), width=int(6 * s))
    for cx in (x + w * 0.24, x + w * 0.78):
        d.ellipse([cx - 46 * s, y + h * 0.02, cx + 46 * s, y + h * 0.6],
                  fill=(48, 48, 54))
        d.ellipse([cx - 18 * s, y + h * 0.18, cx + 18 * s, y + h * 0.44],
                  fill=(186, 190, 198))
    d.ellipse([x + w * 0.94, y - h * 0.5, x + w * 1.02, y - h * 0.3],
              fill=(250, 240, 190))


def _plane_nose(d, x, y, s=1.0):
    """機首とプロペラ。中島飛行機の場面に置く。"""
    d.polygon([(x, y), (x + 420 * s, y - 90 * s), (x + 420 * s, y + 90 * s)],
              fill=(150, 156, 164), outline=(96, 102, 112))
    d.ellipse([x - 30 * s, y - 40 * s, x + 30 * s, y + 40 * s], fill=(96, 100, 108))
    for a in (-70, 50, 170):
        d.polygon([(x, y),
                   (x + math.cos(math.radians(a)) * 40 * s,
                    y + math.sin(math.radians(a)) * 300 * s),
                   (x + math.cos(math.radians(a + 12)) * 40 * s,
                    y + math.sin(math.radians(a + 12)) * 300 * s)],
                  fill=(120, 126, 136))


# ---------------------------------------------------------------- 現代
def ima() -> Image.Image:
    img = vgrad((W, H), (244, 242, 236), (218, 214, 206)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 790, (196, 176, 150), (162, 142, 118))
    _window(img, d, 700, 160, 1230, 540, (172, 206, 240), (226, 236, 246))
    d = ImageDraw.Draw(img)
    # 積んだ段ボール（茶番の小道具）
    for k in range(4):
        x = 300 + (k % 2) * 190
        y = 800 - (k // 2) * 170
        d.rectangle([x, y - 160, x + 176, y], fill=(202, 168, 118),
                    outline=(140, 110, 70), width=5)
        d.line([x, y - 68, x + 176, y - 68], fill=(140, 110, 70), width=5)
        d.line([x + 88, y - 160, x + 88, y - 68], fill=(140, 110, 70), width=5)
    glow(img, 960, 300, 400, (255, 250, 236), 56)
    return img


# ---------------------------------------------------------------- 中島飛行機
def hikoki() -> Image.Image:
    img = vgrad((W, H), (150, 156, 168), (188, 190, 194)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # 格納庫のトラス
    d.rectangle([0, 0, W, 820], fill=(168, 172, 180))
    for k in range(6):
        x = k * 340
        d.line([x, 120, x + 170, 40], fill=(126, 130, 140), width=12)
        d.line([x + 170, 40, x + 340, 120], fill=(126, 130, 140), width=12)
        d.line([x, 120, x + 340, 120], fill=(126, 130, 140), width=10)
        d.line([x + 170, 40, x + 170, 120], fill=(126, 130, 140), width=8)
    _floor(d, 820, (128, 128, 134), (100, 100, 106))
    _plane_nose(d, 1180, 520, 0.9)
    # 工具台
    _desk(d, 240, 820, 760, 960, (104, 96, 88), (76, 70, 64))
    for k in range(5):
        d.rectangle([300 + k * 84, 776, 340 + k * 84, 820], fill=(150, 154, 162))
    glow(img, 600, 200, 340, (230, 234, 242), 40)
    return img


def haikyo() -> Image.Image:
    """飛行機を作れなくなった章。いちばん彩度を落とす。"""
    img = vgrad((W, H), (168, 168, 164), (196, 192, 186)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 830, (146, 142, 136), (116, 112, 108))
    # 壊れたトラスと、抜けた屋根
    for k in range(5):
        x = k * 380
        if k in (1, 3):
            continue
        d.line([x, 160, x + 190, 70], fill=(120, 118, 116), width=12)
        d.line([x + 190, 70, x + 380, 160], fill=(120, 118, 116), width=12)
    d.rectangle([0, 160, W, 176], fill=(120, 118, 116))
    # 覆いを掛けられた機体
    d.polygon([(560, 830), (760, 660), (1300, 650), (1460, 830)],
              fill=(178, 174, 168), outline=(140, 136, 130), width=6)
    for k in range(6):
        d.line([620 + k * 140, 830, 660 + k * 140, 660], fill=(160, 156, 150),
               width=5)
    # 鍋と自転車の車輪（作れるものを作る）
    d.ellipse([260, 760, 460, 850], fill=(150, 152, 158),
              outline=(112, 114, 120), width=6)
    d.ellipse([1600, 700, 1820, 920], outline=(120, 118, 116), width=12)
    for a in range(12):
        d.line([1710, 810,
                1710 + math.cos(math.radians(a * 30)) * 104,
                810 + math.sin(math.radians(a * 30)) * 104],
               fill=(120, 118, 116), width=4)
    img = Image.blend(img.convert("RGB"), img.convert("L").convert("RGB"),
                      0.52).convert("RGBA")
    return img


# ---------------------------------------------------------------- バス・設計室
def bus() -> Image.Image:
    img = vgrad((W, H), (218, 220, 224), (194, 196, 200)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 800], fill=(206, 208, 212))
    for k in range(8):
        d.rectangle([60 + k * 240, 120, 220 + k * 240, 560], fill=(176, 196, 214),
                    outline=(140, 144, 152), width=6)
    _floor(d, 800, (148, 148, 152), (118, 118, 124))
    # バスの車体（角を丸くしてモノコックらしく）
    d.rounded_rectangle([420, 560, 1560, 860], radius=54, fill=(226, 214, 190),
                        outline=(150, 142, 124), width=8)
    for k in range(6):
        d.rounded_rectangle([500 + k * 170, 610, 630 + k * 170, 720], radius=10,
                            fill=(178, 204, 226), outline=(150, 142, 124), width=5)
    for cx in (620, 1360):
        d.ellipse([cx - 62, 800, cx + 62, 920], fill=(48, 48, 54))
        d.ellipse([cx - 24, 836, cx + 24, 884], fill=(184, 188, 196))
    glow(img, 960, 260, 380, (250, 252, 255), 46)
    return img


def sekkei() -> Image.Image:
    """設計室。壁に側面図、床に木製モックアップの骨。"""
    img = vgrad((W, H), (232, 230, 224), (206, 204, 198)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 790, (176, 156, 128), (144, 126, 102))
    d.rectangle([0, 0, W, 790], fill=(224, 222, 216))
    # 図面ボード（軽自動車の側面図）
    d.rounded_rectangle([540, 120, 1420, 600], radius=8, fill=(250, 250, 246),
                        outline=(150, 150, 148), width=8)
    _kei_car(d, 640, 460, 0.62, (238, 236, 232))
    # 寸法線
    d.line([620, 540, 1380, 540], fill=(206, 60, 52), width=6)
    for x in (620, 1380):
        d.line([x, 518, x, 562], fill=(206, 60, 52), width=6)
    d.line([1400, 200, 1400, 520], fill=(206, 60, 52), width=6)
    # 製図台
    d.polygon([(180, 940), (700, 940), (640, 760), (240, 760)],
              fill=(206, 196, 176), outline=(150, 140, 122), width=6)
    # 木のモックアップの骨組み
    d.rectangle([1500, 620, 1860, 800], fill=(198, 168, 122),
                outline=(146, 118, 78), width=6)
    for k in range(4):
        d.line([1520 + k * 100, 620, 1520 + k * 100, 800], fill=(146, 118, 78),
               width=6)
    glow(img, 960, 260, 380, (255, 255, 250), 44)
    return img


def kaigi() -> Image.Image:
    """銀行に断られる章。寒色で重く。"""
    img = vgrad((W, H), (84, 88, 100), (58, 60, 70)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (72, 66, 62), (50, 46, 44))
    d.rectangle([0, 0, W, 800], fill=(78, 82, 94))
    for c in range(6):
        d.rectangle([60 + c * 316, 130, 60 + c * 316 + 250, 640],
                    fill=(90, 94, 108), outline=(66, 70, 82), width=5)
    d.polygon([(280, 900), (1640, 900), (1470, 790), (450, 790)],
              fill=(62, 54, 48))
    for k in range(6):
        d.polygon([(540 + k * 140, 786), (640 + k * 140, 786),
                   (632 + k * 140, 758), (548 + k * 140, 758)],
                  fill=(232, 230, 222))
    glow(img, 960, 250, 340, (140, 152, 180), 32)
    return img


# ---------------------------------------------------------------- 町・工場
def machi() -> Image.Image:
    img = vgrad((W, H), (176, 210, 240), (240, 232, 212)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for base, col in ((620, (156, 176, 196)), (680, (132, 158, 174))):
        pts = [(0, base)]
        for i in range(9):
            pts.append((i * W / 8, base - 130 - 80 * math.sin(i * 1.4 + base)))
        pts += [(W, base), (W, H), (0, H)]
        d.polygon(pts, fill=col)
    _building(d, 40, 380, 380, 800, (216, 206, 190), (150, 168, 190), 3, 4)
    _building(d, 1560, 400, 1900, 800, (208, 200, 186), (146, 164, 188), 3, 4)
    _floor(d, 800, (162, 162, 164), (132, 132, 136))
    _kei_car(d, 640, 880, 0.78)
    glow(img, 1500, 180, 400, (255, 248, 216), 88)
    return img


def kojo() -> Image.Image:
    """組立工場。増産の章。"""
    img = vgrad((W, H), (212, 214, 218), (188, 190, 194)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 800], fill=(202, 204, 208))
    for k in range(5):
        x = k * 400
        d.polygon([(x, 260), (x + 400, 260), (x + 400, 120), (x + 200, 120)],
                  fill=(160, 164, 172))
        d.polygon([(x + 200, 120), (x + 400, 120), (x + 400, 260)],
                  fill=(190, 210, 228))
    _floor(d, 800, (154, 152, 150), (122, 120, 120))
    # ライン上に並ぶ車体
    for k, s in enumerate((0.42, 0.52, 0.64)):
        _kei_car(d, 180 + k * 520, 780 + k * 30, s, (226, 200, 130))
    # コンベアの支柱
    d.rectangle([0, 900, W, 924], fill=(120, 122, 128))
    for k in range(10):
        d.rectangle([80 + k * 200, 924, 108 + k * 200, 1000], fill=(140, 142, 148))
    glow(img, 700, 200, 340, (250, 252, 255), 48)
    return img


PAINTERS = {
    "il_sub_ima": ima,
    "il_sub_hikoki": hikoki,
    "il_sub_haikyo": haikyo,
    "il_sub_bus": bus,
    "il_sub_sekkei": sekkei,
    "il_sub_kaigi": kaigi,
    "il_sub_machi": machi,
    "il_sub_kojo": kojo,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
