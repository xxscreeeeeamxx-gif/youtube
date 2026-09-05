#!/usr/bin/env python3
"""宅急便・小倉昌男の再現ドラマ（ogura-takkyubin）用のイラスト背景14種を生成する。

gen_drama_bgs.py と同じフラットイラスト調。場面ごとに新造（使い回し禁止）。
トーンの設計:
  現代・大正の運送店     … 温かい自然光
  病室                   … 白と青。彩度をいちばん落とす（4年の停滞）
  牛丼屋・郵便局・会議    … 生活の色。ヒントは日常の中にある
  運輸省・法廷            … 灰と石。人の気配を消す
  トラック・パン屋        … 明るく戻す。ここで話が開く
立ち絵は x=0.3 と x=0.74 に常駐し、モブが x=0.5〜0.62 に立つので、
**見せたいものは画面の上半分**に置く（下半分はキャラでほぼ隠れる）。

実行: PYTHONPATH=. python3 scripts/gen_ogu_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from scripts.gen_drama_bgs import W, H, OUT, vgrad, glow  # noqa: E402
from scripts.gen_qr_bgs import _floor, _window  # noqa: E402
from scripts.gen_yam_bgs import _building, _person, _desk  # noqa: E402


def _truck(d, x, y, s=1.0, body=(228, 226, 220), cab=(70, 78, 96)):
    """トラック（横向き・右へ）。荷台と運転席と車輪だけで形を作る。"""
    bw, bh = 420 * s, 190 * s
    d.rounded_rectangle([x, y - bh, x + bw, y], radius=10 * s, fill=body,
                        outline=(150, 148, 142), width=int(6 * s))
    d.polygon([(x + bw, y), (x + bw, y - bh * 0.78),
               (x + bw + 90 * s, y - bh * 0.62), (x + bw + 130 * s, y)], fill=cab)
    d.rounded_rectangle([x + bw + 14 * s, y - bh * 0.68, x + bw + 86 * s,
                         y - bh * 0.28], radius=6 * s, fill=(176, 202, 226))
    for cx in (x + bw * 0.24, x + bw * 0.74, x + bw + 86 * s):
        d.ellipse([cx - 34 * s, y - 34 * s, cx + 34 * s, y + 34 * s],
                  fill=(44, 44, 50))
        d.ellipse([cx - 14 * s, y - 14 * s, cx + 14 * s, y + 14 * s],
                  fill=(140, 140, 148))


def _box(d, x, y, w, h, col=(196, 162, 116)):
    """段ボール箱。荷物の数を見せるのに使う。"""
    d.rectangle([x, y - h, x + w, y], fill=col, outline=(140, 110, 74), width=4)
    d.line([x, y - h * 0.42, x + w, y - h * 0.42], fill=(140, 110, 74), width=4)
    d.line([x + w / 2, y - h, x + w / 2, y - h * 0.42], fill=(140, 110, 74), width=4)


# ---------------------------------------------------------------- 現代（茶番）
def ima() -> Image.Image:
    img = vgrad((W, H), (244, 238, 228), (218, 208, 194)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 780, (198, 172, 142), (162, 136, 106))
    # 玄関ドアと三和土
    d.rounded_rectangle([700, 150, 1230, 800], radius=8, fill=(178, 150, 118),
                        outline=(130, 104, 76), width=10)
    d.rounded_rectangle([760, 220, 1170, 520], radius=6, fill=(206, 184, 154))
    d.ellipse([1160, 470, 1200, 510], fill=(198, 176, 96), outline=(140, 120, 60),
              width=5)
    # 不在票が3枚、ドアに挟まっている
    for k in range(3):
        x = 800 + k * 34
        d.polygon([(x, 560 + k * 8), (x + 108, 552 + k * 8),
                   (x + 114, 636 + k * 8), (x + 6, 644 + k * 8)],
                  fill=(250, 248, 240), outline=(190, 186, 176), width=4)
        for r in range(3):
            d.line([x + 14, 578 + r * 18 + k * 8, x + 96, 572 + r * 18 + k * 8],
                   fill=(196, 192, 184), width=5)
    glow(img, 960, 300, 400, (255, 248, 224), 60)
    return img


# ---------------------------------------------------------------- 大正の運送店
def taisho() -> Image.Image:
    img = vgrad((W, H), (222, 210, 184), (238, 228, 204)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (192, 176, 148), (156, 142, 118))
    # 木造の営業所
    d.polygon([(560, 300), (1380, 300), (1280, 190), (660, 190)], fill=(116, 92, 62))
    d.rectangle([580, 300, 1360, 800], fill=(206, 186, 152))
    d.rectangle([580, 340, 1360, 358], fill=(146, 116, 78))
    for c in range(8):
        d.rectangle([620 + c * 92, 380, 630 + c * 92, 640], fill=(132, 104, 70))
    # 積まれた荷物
    for k in range(5):
        _box(d, 240 + (k % 3) * 130, 800 - (k // 3) * 120, 118, 108)
    _truck(d, 1420, 800, 0.72, (206, 198, 182), (96, 82, 62))
    glow(img, 500, 200, 320, (255, 244, 208), 84)
    return img


# ---------------------------------------------------------------- 病室
def byoshitsu() -> Image.Image:
    img = vgrad((W, H), (232, 238, 244), (210, 220, 230)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 790, (206, 210, 214), (176, 182, 188))
    _window(img, d, 660, 150, 1260, 560, (172, 200, 230), (222, 232, 242),
            frame=(190, 194, 200))
    d = ImageDraw.Draw(img)
    # ベッド
    d.rounded_rectangle([300, 700, 900, 810], radius=10, fill=(246, 246, 248),
                        outline=(200, 202, 208), width=6)
    d.rounded_rectangle([300, 620, 340, 810], radius=8, fill=(196, 200, 208))
    d.rounded_rectangle([330, 664, 470, 706], radius=12, fill=(238, 240, 246))
    # 点滴台
    d.line([1330, 380, 1330, 810], fill=(186, 190, 198), width=12)
    d.rounded_rectangle([1300, 330, 1360, 430], radius=10, fill=(226, 236, 244),
                        outline=(180, 190, 200), width=5)
    # 積まれた本（4年ぶんの時間）
    for k in range(6):
        d.rectangle([1440 + (k % 2) * 6, 780 - k * 26, 1660 + (k % 2) * 6,
                     800 - k * 26],
                    fill=[(150, 120, 96), (110, 130, 150), (140, 140, 120)][k % 3],
                    outline=(90, 90, 96), width=3)
    img = Image.blend(img.convert("RGB"), img.convert("L").convert("RGB"),
                      0.34).convert("RGBA")
    glow(img, 960, 300, 380, (240, 248, 255), 60)
    return img


# ---------------------------------------------------------------- 本社・会議
def honsha() -> Image.Image:
    img = vgrad((W, H), (232, 228, 220), (206, 202, 196)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (150, 130, 110), (118, 100, 84))
    _window(img, d, 640, 170, 1280, 560, (168, 196, 224), (222, 230, 238),
            frame=(120, 118, 116))
    d = ImageDraw.Draw(img)
    _desk(d, 620, 800, 1300, 950, (128, 90, 58), (94, 64, 40))
    # ホワイトボードに折れ線（値下げ合戦で下がる）
    d.rounded_rectangle([1360, 220, 1840, 600], radius=8, fill=(250, 250, 248),
                        outline=(150, 150, 148), width=7)
    pts = [(1400 + i * 78, 300 + i * 42 + (i % 2) * 18) for i in range(6)]
    d.line(pts, fill=(206, 60, 52), width=10, joint="curve")
    glow(img, 960, 300, 340, (255, 250, 230), 54)
    return img


def kaigi() -> Image.Image:
    img = vgrad((W, H), (86, 84, 88), (58, 56, 62)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (74, 64, 58), (52, 44, 40))
    d.rectangle([0, 0, W, 800], fill=(78, 76, 82))
    for c in range(7):
        d.rectangle([50 + c * 272, 120, 50 + c * 272 + 226, 660],
                    fill=(90, 88, 94), outline=(66, 64, 70), width=5)
    d.polygon([(300, 900), (1620, 900), (1450, 800), (470, 800)], fill=(64, 48, 38))
    for k in range(7):
        d.rectangle([560 + k * 120, 772, 650 + k * 120, 802], fill=(232, 230, 222))
    glow(img, 960, 260, 340, (150, 158, 180), 34)
    return img


# ---------------------------------------------------------------- ヒントの場所
def gyudon() -> Image.Image:
    """牛丼屋のカウンター。絞り込みのヒント。"""
    img = vgrad((W, H), (236, 216, 176), (216, 190, 150)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 810, (156, 118, 78), (122, 90, 58))
    # カウンター
    d.rectangle([0, 810, W, 900], fill=(178, 128, 76))
    d.rectangle([0, 890, W, 920], fill=(140, 98, 56))
    # 暖簾
    for k in range(5):
        d.rectangle([420 + k * 220, 120, 610 + k * 220, 380], fill=(196, 62, 48))
    d.rectangle([400, 100, 1620, 132], fill=(120, 86, 48))
    # 品書きは一種類だけ（絞り込みの記号。文字は描かない）
    d.rounded_rectangle([840, 430, 1090, 620], radius=6, fill=(246, 238, 214),
                        outline=(140, 106, 62), width=7)
    d.rectangle([880, 480, 1050, 502], fill=(70, 56, 36))
    d.rectangle([900, 540, 1030, 560], fill=(180, 60, 48))
    # 丼
    for k in range(2):
        cx = 620 + k * 700
        d.ellipse([cx - 90, 760, cx + 90, 860], fill=(240, 236, 226),
                  outline=(180, 172, 158), width=6)
        d.ellipse([cx - 70, 772, cx + 70, 828], fill=(150, 96, 52))
    glow(img, 960, 240, 340, (255, 226, 170), 70)
    return img


def yubinkyoku() -> Image.Image:
    """窓口。ここで「送る手段が無い」と言われる。"""
    img = vgrad((W, H), (228, 230, 226), (204, 208, 206)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (188, 184, 176), (156, 152, 146))
    d.rectangle([0, 0, W, 800], fill=(214, 216, 210))
    # 窓口カウンターと仕切り
    d.rectangle([0, 800, W, 900], fill=(178, 150, 112))
    for k in range(4):
        x = 300 + k * 380
        d.rectangle([x, 380, x + 14, 800], fill=(150, 148, 142))
    d.rectangle([260, 350, 1660, 386], fill=(150, 148, 142))
    # 掲示（内容は描かない）
    for k in range(3):
        d.rounded_rectangle([420 + k * 400, 180, 640 + k * 400, 320], radius=6,
                            fill=(250, 250, 246), outline=(178, 176, 170), width=5)
        for r in range(3):
            d.line([444 + k * 400, 218 + r * 32, 614 + k * 400, 214 + r * 32],
                   fill=(196, 194, 188), width=6)
    _box(d, 880, 800, 140, 120)
    glow(img, 960, 260, 360, (250, 252, 250), 46)
    return img


# ---------------------------------------------------------------- 初日・大口
def gaito() -> Image.Image:
    """1976年の冬の街。初日11個。荷物が少ないことを箱の数で見せる。"""
    img = vgrad((W, H), (176, 190, 210), (222, 218, 210)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _building(d, 0, 260, 380, 800, (188, 184, 178), (140, 156, 174), 3, 6)
    _building(d, 1560, 240, 1920, 800, (180, 176, 170), (136, 152, 172), 3, 7)
    _building(d, 420, 340, 820, 800, (196, 192, 184), (142, 158, 176), 3, 5)
    _floor(d, 800, (158, 158, 160), (128, 128, 132))
    _truck(d, 900, 830, 0.86)
    # 積んだ箱は11個ぶんだけ（数えられる数にする）
    for k in range(11):
        _box(d, 200 + (k % 4) * 96, 900 - (k // 4) * 92, 84, 80)
    glow(img, 400, 180, 340, (255, 246, 224), 70)
    return img


def hyakkaten() -> Image.Image:
    """百貨店の搬入口。大口を切る場面。"""
    img = vgrad((W, H), (206, 200, 196), (176, 170, 168)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 810, (140, 136, 134), (110, 106, 106))
    d.rectangle([0, 0, W, 810], fill=(160, 152, 148))
    # シャッターと庇
    d.rectangle([520, 240, 1420, 810], fill=(120, 122, 128))
    for r in range(14):
        d.line([520, 264 + r * 40, 1420, 264 + r * 40], fill=(142, 144, 150), width=8)
    d.rectangle([470, 200, 1470, 250], fill=(88, 72, 62))
    # 台車と箱の山
    for k in range(8):
        _box(d, 180 + (k % 2) * 104, 810 - (k // 2) * 96, 96, 88, (182, 148, 106))
    _truck(d, 1500, 840, 0.72, (214, 208, 196), (78, 74, 84))
    glow(img, 960, 240, 300, (230, 228, 224), 34)
    return img


# ---------------------------------------------------------------- 役所・法廷
def unyusho() -> Image.Image:
    img = vgrad((W, H), (72, 74, 80), (48, 50, 56)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 820, (92, 90, 88), (66, 64, 64))
    for c in range(4):
        x = 180 + c * 480
        d.rectangle([x, 100, x + 120, 820], fill=(112, 110, 106))
        d.rectangle([x - 20, 100, x + 140, 148], fill=(128, 126, 122))
    # 受付カウンターと、積み上がった書類
    d.rectangle([0, 820, W, 920], fill=(96, 82, 66))
    for k in range(9):
        d.polygon([(360 + k * 8, 820 - k * 12), (620 + k * 8, 812 - k * 12),
                   (624 + k * 8, 826 - k * 12), (364 + k * 8, 834 - k * 12)],
                  fill=(232, 230, 220) if k % 2 else (216, 214, 206))
    glow(img, 960, 300, 400, (150, 162, 186), 32)
    return img


def hotei() -> Image.Image:
    img = vgrad((W, H), (78, 68, 58), (52, 44, 38)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 820, (100, 76, 54), (72, 54, 38))
    d.rectangle([0, 0, W, 820], fill=(96, 76, 58))
    for c in range(9):
        d.rectangle([40 + c * 212, 140, 40 + c * 212 + 168, 700],
                    fill=(110, 88, 66), outline=(78, 60, 44), width=5)
    # 法壇
    d.rectangle([620, 560, 1300, 830], fill=(74, 56, 40))
    d.rectangle([600, 540, 1320, 580], fill=(96, 74, 54))
    # 木槌
    d.rounded_rectangle([1360, 762, 1470, 806], radius=10, fill=(126, 92, 58))
    d.line([1400, 806, 1520, 850], fill=(126, 92, 58), width=18)
    glow(img, 960, 320, 380, (200, 176, 130), 34)
    return img


# ---------------------------------------------------------------- 開けていく
def track() -> Image.Image:
    """全国へ。ここで色が戻る。"""
    img = vgrad((W, H), (168, 208, 240), (238, 232, 212)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for base, col in ((600, (156, 176, 194)), (660, (132, 158, 172))):
        pts = [(0, base)]
        for i in range(9):
            pts.append((i * W / 8, base - 120 - 80 * math.sin(i * 1.3 + base)))
        pts += [(W, base), (W, H), (0, H)]
        d.polygon(pts, fill=col)
    d.rectangle([0, 700, W, H], fill=(128, 164, 108))
    # 道路
    d.polygon([(0, H), (W, H), (W, 780), (0, 840)], fill=(120, 120, 124))
    for k in range(9):
        d.polygon([(60 + k * 220, 1000), (180 + k * 220, 996),
                   (176 + k * 220, 1016), (56 + k * 220, 1020)],
                  fill=(238, 238, 234))
    _truck(d, 260, 960, 0.8)
    _truck(d, 1180, 900, 0.6)
    glow(img, 1500, 180, 400, (255, 246, 210), 90)
    return img


def sagyosho() -> Image.Image:
    """作業所。ここは静かに、彩度を落とす。"""
    img = vgrad((W, H), (226, 224, 216), (202, 200, 192)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (176, 168, 154), (146, 138, 126))
    _window(img, d, 680, 180, 1240, 540, (192, 206, 216), (226, 230, 232),
            frame=(160, 156, 150))
    d = ImageDraw.Draw(img)
    # 作業台
    _desk(d, 340, 800, 1000, 930, (150, 122, 88), (112, 90, 64))
    for k in range(4):
        d.rounded_rectangle([400 + k * 140, 748, 490 + k * 140, 800], radius=6,
                            fill=(214, 206, 190), outline=(170, 162, 148), width=4)
    # 棚に、売れ残った品
    d.rectangle([1320, 320, 1780, 800], fill=(190, 180, 164))
    for r in range(3):
        ty = 420 + r * 130
        d.rectangle([1332, ty, 1768, ty + 12], fill=(158, 148, 132))
        for c in range(4):
            d.rounded_rectangle([1352 + c * 106, ty - 66, 1428 + c * 106, ty],
                                radius=6, fill=(206, 198, 184),
                                outline=(170, 162, 148), width=4)
    img = Image.blend(img.convert("RGB"), img.convert("L").convert("RGB"),
                      0.26).convert("RGBA")
    return img


def pan() -> Image.Image:
    """パン屋。焼きたての色。この回でいちばん温かい画にする。"""
    img = vgrad((W, H), (250, 232, 196), (232, 206, 166)).convert("RGBA")
    d = ImageDraw.Draw(img)
    _floor(d, 800, (176, 132, 84), (140, 102, 62))
    # 什器
    d.rounded_rectangle([300, 300, 1620, 800], radius=12, fill=(200, 156, 106),
                        outline=(150, 112, 70), width=8)
    for r in range(3):
        ty = 400 + r * 130
        d.rectangle([316, ty, 1604, ty + 14], fill=(160, 118, 74))
        for c in range(9):
            cx = 380 + c * 140
            # 丸パンとコッペパン
            if (r + c) % 2:
                d.ellipse([cx - 46, ty - 78, cx + 46, ty - 6], fill=(214, 158, 88),
                          outline=(168, 116, 58), width=5)
                d.arc([cx - 30, ty - 62, cx + 30, ty - 26], 200, 340,
                      fill=(238, 202, 148), width=6)
            else:
                d.rounded_rectangle([cx - 56, ty - 66, cx + 56, ty - 10], radius=26,
                                    fill=(222, 172, 102), outline=(170, 120, 62),
                                    width=5)
    # 窓の光
    glow(img, 960, 240, 460, (255, 230, 176), 96)
    glow(img, 320, 420, 260, (255, 240, 200), 60)
    return img


PAINTERS = {
    "il_ogu_ima": ima,
    "il_ogu_taisho": taisho,
    "il_ogu_byoshitsu": byoshitsu,
    "il_ogu_honsha": honsha,
    "il_ogu_kaigi": kaigi,
    "il_ogu_gyudon": gyudon,
    "il_ogu_yubinkyoku": yubinkyoku,
    "il_ogu_gaito": gaito,
    "il_ogu_hyakkaten": hyakkaten,
    "il_ogu_unyusho": unyusho,
    "il_ogu_hotei": hotei,
    "il_ogu_track": track,
    "il_ogu_sagyosho": sagyosho,
    "il_ogu_pan": pan,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in PAINTERS.items():
        fn().convert("RGB").save(OUT / f"{name}.png")
        print("背景生成:", name)
