#!/usr/bin/env python3
"""再現ドラマ用のイラスト背景を生成する（実写写真の代わりのフラットイラスト調）。

  il_kitchen_night.png   現代・夜のキッチン（フック/現代パート用）
  il_washitsu_1957.png   昭和の和室・夜（1957パート用）

お手本動画の「シンプルなイラスト背景に大きな立ち絵」の画面づくりに合わせる。
実行: PYTHONPATH=. python3 scripts/gen_drama_bgs.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

W, H = 1920, 1080
OUT = Path("assets/backgrounds")


def vgrad(size, top, bottom):
    """縦グラデーション画像。"""
    w, h = size
    img = Image.new("RGB", (1, h))
    for y in range(h):
        f = y / max(h - 1, 1)
        img.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * f)
                                   for i in range(3)))
    return img.resize((w, h))


def glow(canvas, cx, cy, r, color, alpha=110):
    """柔らかい光のにじみ。"""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r * 0.72, cx + r, cy + r * 0.72],
              fill=(*color, alpha))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(r // 3)))


# ---------------------------------------------------------------- 夜のキッチン
def kitchen_night() -> Image.Image:
    img = vgrad((W, H), (26, 32, 52), (16, 20, 34)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")

    # 床（濃い木目）
    floor_y = int(H * 0.74)
    d.rectangle([0, floor_y, W, H], fill=(38, 30, 34))
    for i in range(6):
        x = 160 + i * 320
        d.line([x, floor_y, x - 120, H], fill=(30, 24, 27), width=5)
    d.line([0, floor_y, W, floor_y], fill=(20, 16, 20), width=6)

    # 窓（夜空と月）
    wx0, wy0, wx1, wy1 = 1280, 120, 1760, 560
    d.rounded_rectangle([wx0 - 18, wy0 - 18, wx1 + 18, wy1 + 18], radius=18,
                        fill=(50, 56, 78))
    night = vgrad((wx1 - wx0, wy1 - wy0), (24, 34, 66), (40, 52, 92))
    img.paste(night, (wx0, wy0))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([wx1 - 150, wy0 + 40, wx1 - 60, wy0 + 130], fill=(246, 238, 190))
    for sx, sy in [(wx0 + 60, wy0 + 70), (wx0 + 170, wy0 + 180),
                   (wx0 + 300, wy0 + 90), (wx0 + 110, wy0 + 300),
                   (wx0 + 340, wy0 + 260)]:
        d.ellipse([sx, sy, sx + 7, sy + 7], fill=(220, 226, 244))
    # 窓の桟
    mx, my = (wx0 + wx1) // 2, (wy0 + wy1) // 2
    d.line([mx, wy0, mx, wy1], fill=(50, 56, 78), width=12)
    d.line([wx0, my, wx1, my], fill=(50, 56, 78), width=12)

    # 吊りランプ + 光
    lx = 620
    d.line([lx, 0, lx, 150], fill=(60, 62, 74), width=8)
    d.polygon([(lx - 90, 240), (lx + 90, 240), (lx + 52, 150), (lx - 52, 150)],
              fill=(224, 160, 74))
    glow(img, lx, 300, 320, (255, 196, 110), 70)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([lx - 26, 224, lx + 26, 262], fill=(255, 236, 180))

    # カウンター（奥）
    cy0 = int(H * 0.56)
    d.rounded_rectangle([120, cy0, 1140, floor_y + 10], radius=16,
                        fill=(58, 50, 62))
    d.rectangle([120, cy0, 1140, cy0 + 26], fill=(84, 74, 88))
    # やかん
    kx, ky = 300, cy0 - 90
    d.ellipse([kx, ky, kx + 170, ky + 96], fill=(150, 156, 172))
    d.rounded_rectangle([kx + 30, ky - 18, kx + 140, ky + 20], radius=14,
                        fill=(150, 156, 172))
    d.arc([kx + 30, ky - 60, kx + 140, ky + 10], 200, 340,
          fill=(120, 126, 142), width=10)
    d.polygon([(kx + 165, ky + 26), (kx + 215, ky - 2), (kx + 205, ky + 40)],
              fill=(150, 156, 172))
    # カップ麺（白カップ・赤帯）
    ux, uy = 700, cy0 - 110
    d.polygon([(ux, uy), (ux + 130, uy), (ux + 112, uy + 120), (ux + 18, uy + 120)],
              fill=(240, 238, 232))
    d.rectangle([ux + 4, uy + 34, ux + 126, uy + 62], fill=(196, 60, 54))
    d.ellipse([ux - 2, uy - 12, ux + 132, uy + 14], fill=(250, 248, 244))
    # 湯気
    for i in range(2):
        pts = []
        for j in range(8):
            yy = uy - 16 - j * 16
            pts.append((ux + 40 + i * 50 + 12 * math.sin(j * 0.9 + i * 2), yy))
        d.line(pts, fill=(235, 240, 248, 120), width=7)

    # 全体をわずかに暗くまとめるビネット
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    vd.rectangle([0, 0, W, H], fill=(6, 8, 14, 40))
    vd.ellipse([-300, -260, W + 300, H + 380], fill=(0, 0, 0, 0))
    img.alpha_composite(vig.filter(ImageFilter.GaussianBlur(120)))
    return img.convert("RGB")


# ---------------------------------------------------------------- 1957の和室
def washitsu_1957() -> Image.Image:
    img = vgrad((W, H), (54, 44, 38), (40, 32, 28)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")

    # 障子（奥の壁に2枚）。片方はほんのり明かり
    for i, (sx, lit) in enumerate([(420, False), (980, True)]):
        sw, sy0, sy1 = 460, 110, 640
        base = (232, 222, 198) if lit else (204, 194, 174)
        d.rectangle([sx, sy0, sx + sw, sy1], fill=base)
        if lit:
            glow(img, sx + sw // 2, (sy0 + sy1) // 2, 300, (255, 214, 140), 40)
            d = ImageDraw.Draw(img, "RGBA")
        # 格子
        for gx in range(sx, sx + sw + 1, sw // 4):
            d.line([gx, sy0, gx, sy1], fill=(96, 76, 58), width=7)
        for gy in range(sy0, sy1 + 1, (sy1 - sy0) // 4):
            d.line([sx, gy, sx + sw, gy], fill=(96, 76, 58), width=7)
        d.rectangle([sx - 10, sy0 - 10, sx + sw + 10, sy1 + 10],
                    outline=(70, 54, 42), width=12)

    # 柱（左右）
    d.rectangle([120, 0, 210, H], fill=(74, 56, 42))
    d.line([210, 0, 210, H], fill=(52, 40, 30), width=6)
    d.rectangle([1700, 0, 1790, H], fill=(74, 56, 42))
    d.line([1700, 0, 1700, H], fill=(52, 40, 30), width=6)
    # 鴨居（障子の上の横木）
    d.rectangle([210, 70, 1700, 112], fill=(70, 54, 42))

    # 畳（下1/3・2トーン＋縁）
    ty = int(H * 0.66)
    d.rectangle([0, ty, W, H], fill=(112, 108, 74))
    d.polygon([(0, H), (560, ty), (1360, ty), (W, H)], fill=(126, 120, 84))
    for x0, x1 in [(560, 0), (1360, W)]:
        d.line([x0, ty, x1, H], fill=(64, 60, 42), width=8)
    d.line([0, ty, W, ty], fill=(58, 52, 38), width=8)
    # 畳の目（うっすら横線）
    for yy in range(ty + 26, H, 34):
        d.line([0, yy, W, yy], fill=(104, 100, 68, 90), width=2)

    # ちゃぶ台
    tx, tyy = 960, int(H * 0.80)
    d.ellipse([tx - 300, tyy - 60, tx + 300, tyy + 60], fill=(96, 64, 44))
    d.ellipse([tx - 300, tyy - 68, tx + 300, tyy + 44], fill=(122, 82, 56))
    d.rectangle([tx - 220, tyy + 30, tx - 190, tyy + 130], fill=(76, 52, 38))
    d.rectangle([tx + 190, tyy + 30, tx + 220, tyy + 130], fill=(76, 52, 38))
    # 湯呑み
    d.ellipse([tx - 60, tyy - 58, tx + 4, tyy - 12], fill=(206, 200, 188))

    # 裸電球 + 暖色の光だまり
    lx = 960
    d.line([lx, 0, lx, 120], fill=(40, 34, 28), width=6)
    glow(img, lx, 200, 360, (255, 200, 120), 60)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([lx - 34, 120, lx + 34, 200], fill=(255, 226, 150))
    d.rectangle([lx - 16, 104, lx + 16, 132], fill=(120, 110, 96))

    # ビネット
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    vd.rectangle([0, 0, W, H], fill=(10, 8, 6, 52))
    img.alpha_composite(vig.filter(ImageFilter.GaussianBlur(140)))
    return img.convert("RGB")




# ================================================================ 共通キット
def base(top, bottom):
    return vgrad((W, H), top, bottom).convert("RGBA")


def wood_floor(img, y0, col=(38, 30, 34), line=(30, 24, 27)):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, y0, W, H], fill=col)
    for i in range(7):
        x = 100 + i * 300
        d.line([x, y0, x - 130, H], fill=line, width=5)
    d.line([0, y0, W, y0], fill=tuple(int(c * 0.7) for c in line), width=6)


def tatami_floor(img, y0):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, y0, W, H], fill=(112, 108, 74))
    d.polygon([(0, H), (560, y0), (1360, y0), (W, H)], fill=(126, 120, 84))
    for x0, x1 in [(560, 0), (1360, W)]:
        d.line([x0, y0, x1, H], fill=(64, 60, 42), width=8)
    d.line([0, y0, W, y0], fill=(58, 52, 38), width=8)
    for yy in range(y0 + 26, H, 34):
        d.line([0, yy, W, yy], fill=(104, 100, 68, 90), width=2)


def hanging_bulb(img, lx, warm=True, ly=120):
    d = ImageDraw.Draw(img, "RGBA")
    d.line([lx, 0, lx, ly], fill=(40, 34, 28), width=6)
    col = (255, 200, 120) if warm else (220, 230, 245)
    glow(img, lx, ly + 80, 340, col, 55)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([lx - 32, ly, lx + 32, ly + 76], fill=(255, 226, 150) if warm else (235, 240, 250))
    d.rectangle([lx - 15, ly - 16, lx + 15, ly + 12], fill=(120, 110, 96))


def fabric_shelf(d, x0, y0, x1, y1):
    """布問屋の棚（反物がぎっしり）。"""
    d.rectangle([x0, y0, x1, y1], fill=(70, 54, 42))
    rows = 3
    cols = 6
    pal = [(178, 96, 88), (98, 128, 158), (152, 138, 84), (120, 148, 108),
           (166, 118, 146), (108, 108, 140), (190, 150, 100), (86, 122, 122)]
    rh = (y1 - y0) / rows
    cw = (x1 - x0) / cols
    k = 0
    for r in range(rows):
        for c in range(cols):
            px0 = x0 + c * cw + 8
            py0 = y0 + r * rh + 8
            d.rounded_rectangle([px0, py0, px0 + cw - 16, py0 + rh - 16],
                                radius=10, fill=pal[k % len(pal)])
            d.ellipse([px0 + 6, py0 + 6, px0 + 34, py0 + rh - 22],
                      fill=tuple(min(255, int(v * 1.25)) for v in pal[k % len(pal)]))
            k += 1
        d.rectangle([x0, y0 + (r + 1) * rh - 4, x1, y0 + (r + 1) * rh + 4],
                    fill=(52, 40, 30))


def make_nunoya():
    """台湾・祖父の布問屋（幼少期）。"""
    img = base((66, 52, 40), (48, 38, 30))
    d = ImageDraw.Draw(img, "RGBA")
    fabric_shelf(d, 160, 120, 900, 640)
    fabric_shelf(d, 1020, 120, 1760, 640)
    wood_floor(img, int(H * 0.68), col=(60, 46, 36), line=(48, 36, 28))
    d = ImageDraw.Draw(img, "RGBA")
    # 帳場机
    d.rounded_rectangle([820, 760, 1120, 980], radius=14, fill=(84, 62, 44))
    d.rectangle([820, 760, 1120, 786], fill=(104, 78, 54))
    hanging_bulb(img, 960, ly=60)
    return img.convert("RGB")


def make_library():
    """図書館（司書時代）。"""
    img = base((52, 56, 66), (40, 44, 52))
    d = ImageDraw.Draw(img, "RGBA")
    pal = [(150, 60, 54), (60, 90, 130), (170, 140, 70), (70, 110, 80),
           (120, 80, 120), (90, 90, 100)]
    for bx in (140, 700, 1260):
        d.rectangle([bx, 90, bx + 520, 700], fill=(66, 50, 38))
        for r in range(4):
            sy = 110 + r * 150
            d.rectangle([bx + 14, sy + 118, bx + 506, sy + 132], fill=(48, 36, 28))
            x = bx + 22
            k = r
            while x < bx + 480:
                bw = 26 + (k * 37) % 30
                d.rectangle([x, sy, x + bw, sy + 118], fill=pal[k % len(pal)])
                x += bw + 6
                k += 1
    wood_floor(img, int(H * 0.70), col=(52, 44, 40), line=(42, 34, 30))
    hanging_bulb(img, 500, warm=False, ly=40)
    hanging_bulb(img, 1420, warm=False, ly=40)
    return img.convert("RGB")


def make_shokai():
    """大阪・日東商会（昼の事務所）。"""
    img = base((208, 196, 174), (176, 164, 142))
    d = ImageDraw.Draw(img, "RGBA")
    # 窓（昼の光）
    for wx in (240, 1420):
        d.rectangle([wx - 14, 110, wx + 274, 560], fill=(120, 104, 84))
        d.rectangle([wx, 124, wx + 260, 546], fill=(226, 234, 240))
        d.line([wx + 130, 124, wx + 130, 546], fill=(120, 104, 84), width=10)
        d.line([wx, 335, wx + 260, 335], fill=(120, 104, 84), width=10)
        glow(img, wx + 130, 620, 260, (255, 248, 220), 40)
        d = ImageDraw.Draw(img, "RGBA")
    fabric_shelf(d, 700, 150, 1240, 560)
    wood_floor(img, int(H * 0.70), col=(140, 116, 92), line=(118, 96, 76))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([760, 800, 1160, 1010], radius=12, fill=(110, 86, 62))
    d.rectangle([760, 800, 1160, 824], fill=(134, 106, 76))
    return img.convert("RGB")


def make_yagaku():
    """夜学の教室（立命館）。"""
    img = base((40, 42, 54), (30, 32, 42))
    d = ImageDraw.Draw(img, "RGBA")
    # 黒板
    d.rectangle([420, 140, 1500, 560], fill=(58, 66, 52))
    d.rectangle([404, 124, 1516, 576], outline=(96, 78, 58), width=16)
    d.rectangle([404, 560, 1516, 596], fill=(96, 78, 58))
    # 黒板の文字（走り書きの線）
    for i, (lx0, ly, lx1) in enumerate([(480, 220, 900), (480, 300, 1050),
                                        (480, 380, 820), (980, 220, 1420)]):
        d.line([lx0, ly, lx1, ly], fill=(206, 214, 202, 150), width=6)
    wood_floor(img, int(H * 0.70), col=(46, 40, 40), line=(36, 30, 30))
    d = ImageDraw.Draw(img, "RGBA")
    # 机
    for mx in (300, 1320):
        d.rectangle([mx, 830, mx + 320, 856], fill=(96, 78, 58))
        d.rectangle([mx + 20, 856, mx + 44, 1000], fill=(76, 60, 46))
        d.rectangle([mx + 276, 856, mx + 300, 1000], fill=(76, 60, 46))
    hanging_bulb(img, 960, warm=True, ly=50)
    return img.convert("RGB")


def make_kojo():
    """戦中の暗い工場。"""
    img = base((44, 46, 50), (30, 32, 36))
    d = ImageDraw.Draw(img, "RGBA")
    # 高い小窓
    for wx in (300, 760, 1220, 1680):
        d.rectangle([wx - 90, 90, wx + 90, 210], fill=(90, 100, 112))
        d.line([wx, 90, wx, 210], fill=(50, 54, 60), width=8)
    # 機械のシルエット
    for mx, mw, mh in [(240, 340, 300), (760, 280, 360), (1420, 360, 320)]:
        d.rounded_rectangle([mx, 720 - mh, mx + mw, 760], radius=16, fill=(58, 60, 66))
        d.ellipse([mx + 30, 700 - mh, mx + 110, 780 - mh], fill=(70, 72, 80))
        d.rectangle([mx + mw - 70, 640 - mh, mx + mw - 30, 720 - mh], fill=(70, 72, 80))
    d.rectangle([0, int(H * 0.72), W, H], fill=(40, 42, 46))
    d.line([0, int(H * 0.72), W, int(H * 0.72)], fill=(28, 30, 34), width=6)
    return img.convert("RGB")


def make_yamiichi():
    """戦後の闇市・夜。"""
    img = base((24, 26, 40), (36, 32, 38))
    d = ImageDraw.Draw(img, "RGBA")
    # 屋台の連なり
    for sx, name_col in [(120, (196, 90, 80)), (700, (90, 120, 170)), (1280, (170, 140, 80))]:
        d.rectangle([sx, 360, sx + 480, 700], fill=(56, 46, 40))
        d.polygon([(sx - 30, 360), (sx + 510, 360), (sx + 470, 260), (sx + 10, 260)],
                  fill=(78, 62, 48))
        # のれん
        for i in range(4):
            nx = sx + 40 + i * 110
            d.rectangle([nx, 370, nx + 90, 520], fill=name_col)
        # 提灯
        for lx in (sx + 60, sx + 420):
            glow(img, lx, 320, 120, (255, 190, 100), 70)
            d = ImageDraw.Draw(img, "RGBA")
            d.ellipse([lx - 36, 282, lx + 36, 366], fill=(240, 150, 70))
            d.line([lx - 20, 300, lx - 20, 350], fill=(190, 100, 40), width=4)
            d.line([lx + 20, 300, lx + 20, 350], fill=(190, 100, 40), width=4)
    d.rectangle([0, int(H * 0.72), W, H], fill=(34, 30, 32))
    return img.convert("RGB")


def make_hama():
    """製塩の浜（昼）。"""
    img = base((150, 190, 216), (208, 224, 232))
    d = ImageDraw.Draw(img, "RGBA")
    # 海
    d.rectangle([0, 470, W, 640], fill=(70, 120, 160))
    for i in range(5):
        yy = 500 + i * 26
        d.line([0 + i * 60, yy, W, yy], fill=(96, 148, 184), width=4)
    # 砂浜
    d.polygon([(0, 640), (W, 620), (W, H), (0, H)], fill=(196, 176, 138))
    # 塩焚きの鉄板と火
    d.rectangle([1180, 700, 1660, 740], fill=(80, 82, 90))
    d.rectangle([1220, 740, 1620, 800], fill=(60, 56, 60))
    d.polygon([(1300, 740), (1340, 690), (1380, 740)], fill=(240, 150, 70))
    d.polygon([(1420, 740), (1470, 680), (1520, 740)], fill=(250, 180, 80))
    # 白い塩の山
    d.polygon([(300, 780), (420, 660), (540, 780)], fill=(238, 240, 242))
    d.polygon([(560, 800), (660, 700), (760, 800)], fill=(230, 232, 236))
    # 太陽
    glow(img, 1620, 160, 180, (255, 240, 200), 90)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([1570, 110, 1670, 210], fill=(252, 244, 214))
    return img.convert("RGB")


def make_goku():
    """収監（灰色の壁と鉄格子窓）。"""
    img = base((70, 72, 78), (48, 50, 56))
    d = ImageDraw.Draw(img, "RGBA")
    # 石壁の目地
    for r in range(6):
        yy = 90 + r * 150
        d.line([0, yy, W, yy], fill=(58, 60, 66), width=5)
        off = 0 if r % 2 == 0 else 150
        for x in range(off, W, 300):
            d.line([x, yy, x, yy + 150], fill=(58, 60, 66), width=5)
    # 鉄格子窓（高い位置・冷たい光）
    wx0, wy0, wx1, wy1 = 820, 110, 1100, 330
    d.rectangle([wx0, wy0, wx1, wy1], fill=(150, 162, 176))
    glow(img, (wx0 + wx1) // 2, wy1 + 60, 240, (180, 196, 214), 40)
    d = ImageDraw.Draw(img, "RGBA")
    for bx in range(wx0 + 40, wx1, 60):
        d.line([bx, wy0, bx, wy1], fill=(44, 46, 52), width=12)
    d.rectangle([0, int(H * 0.74), W, H], fill=(56, 58, 62))
    return img.convert("RGB")


def make_koya():
    """研究小屋の中（板壁・棚・製麺機・中華鍋）。"""
    img = base((70, 56, 42), (52, 42, 34))
    d = ImageDraw.Draw(img, "RGBA")
    # 板壁
    for x in range(0, W, 160):
        d.line([x, 0, x, int(H * 0.7)], fill=(58, 46, 36), width=6)
    # 棚と瓶
    d.rectangle([140, 180, 820, 200], fill=(96, 74, 52))
    for i, bx in enumerate(range(180, 780, 90)):
        col = [(150, 130, 90), (120, 140, 120), (160, 110, 90)][i % 3]
        d.rounded_rectangle([bx, 110, bx + 56, 180], radius=8, fill=col)
    # 製麺機（ローラーとハンドル）
    d.rounded_rectangle([1280, 520, 1660, 780], radius=14, fill=(88, 92, 102))
    d.ellipse([1330, 560, 1430, 660], fill=(120, 124, 136))
    d.ellipse([1500, 560, 1600, 660], fill=(120, 124, 136))
    d.line([1660, 560, 1760, 480], fill=(120, 124, 136), width=14)
    d.ellipse([1740, 460, 1790, 510], fill=(140, 144, 156))
    # 中華鍋（かまど上）
    d.rectangle([300, 640, 700, 800], fill=(84, 66, 50))
    d.chord([340, 560, 660, 720], start=0, end=180, fill=(70, 72, 82))
    wood_floor(img, int(H * 0.76), col=(56, 44, 36), line=(46, 36, 30))
    hanging_bulb(img, 960, ly=90)
    return img.convert("RGB")


def make_daidokoro():
    """昭和の台所（かまど・鍋・湯気）。"""
    img = base((88, 78, 62), (66, 58, 48))
    d = ImageDraw.Draw(img, "RGBA")
    # 壁のタイル帯
    d.rectangle([0, 420, W, 700], fill=(168, 168, 152))
    for x in range(0, W, 90):
        d.line([x, 420, x, 700], fill=(146, 146, 132), width=4)
    d.line([0, 560, W, 560], fill=(146, 146, 132), width=4)
    # かまど+鍋
    d.rounded_rectangle([560, 620, 1000, 860], radius=14, fill=(120, 92, 66))
    d.chord([620, 540, 940, 700], start=0, end=180, fill=(66, 68, 78))
    d.ellipse([640, 540, 920, 600], fill=(84, 86, 96))
    # 油の鍋から湯気
    for i in range(3):
        pts = []
        for j in range(8):
            yy = 520 - j * 22
            pts.append((720 + i * 60 + 14 * math.sin(j * 0.8 + i * 2), yy))
        d.line(pts, fill=(235, 240, 248, 110), width=8)
    # 流し台
    d.rounded_rectangle([1220, 700, 1740, 880], radius=12, fill=(150, 156, 166))
    d.rectangle([1260, 730, 1700, 850], fill=(120, 126, 138))
    wood_floor(img, int(H * 0.82), col=(58, 48, 40), line=(48, 40, 34))
    hanging_bulb(img, 400, ly=70)
    return img.convert("RGB")


def make_shotengai():
    """昭和の商店街（昼・ひさしと看板）。"""
    img = base((196, 206, 214), (170, 182, 192))
    d = ImageDraw.Draw(img, "RGBA")
    # 店の並び
    cols = [(188, 108, 92), (108, 138, 168), (172, 148, 92)]
    for i, sx in enumerate((80, 700, 1320)):
        d.rectangle([sx, 260, sx + 540, 760], fill=(216, 208, 192))
        # ひさし（ストライプ）
        for k in range(9):
            c = cols[i] if k % 2 == 0 else (238, 236, 228)
            d.polygon([(sx + k * 60, 260), (sx + k * 60 + 60, 260),
                       (sx + k * 60 + 44, 360), (sx + k * 60 - 16, 360)], fill=c)
        # 看板（文字は描かない・板だけ）
        d.rounded_rectangle([sx + 120, 160, sx + 420, 236], radius=10,
                            fill=(90, 76, 60))
        # 店先の台
        d.rectangle([sx + 60, 640, sx + 480, 760], fill=(150, 128, 100))
    d.rectangle([0, int(H * 0.72), W, H], fill=(150, 146, 138))
    d.line([0, int(H * 0.72), W, int(H * 0.72)], fill=(120, 118, 112), width=6)
    return img.convert("RGB")


def make_america():
    """1966・ニューヨークのビル街（昼）。"""
    img = base((168, 196, 220), (200, 214, 224))
    d = ImageDraw.Draw(img, "RGBA")
    bl = [(96, 104, 118), (120, 126, 138), (82, 90, 104), (108, 112, 126)]
    heights = [(60, 260, 700), (300, 120, 820), (470, 300, 560), (820, 200, 760),
               (1060, 260, 640), (1360, 180, 860), (1580, 300, 700)]
    for i, (bx, bw, bh) in enumerate(heights):
        col = bl[i % len(bl)]
        d.rectangle([bx, 760 - bh, bx + bw, 760], fill=col)
        # 窓
        for wy in range(770 - bh + 20, 740, 44):
            for wx in range(bx + 14, bx + bw - 20, 40):
                d.rectangle([wx, wy, wx + 22, wy + 26], fill=(214, 226, 238))
    # 道路
    d.rectangle([0, 760, W, H], fill=(96, 98, 104))
    d.rectangle([0, 760, W, 790], fill=(140, 142, 148))
    for x in range(60, W, 240):
        d.rectangle([x, 900, x + 120, 924], fill=(210, 200, 90))
    return img.convert("RGB")


def make_kinai():
    """飛行機の機内。"""
    img = base((196, 200, 208), (170, 174, 184))
    d = ImageDraw.Draw(img, "RGBA")
    # 荷物棚のライン
    d.rectangle([0, 90, W, 200], fill=(150, 154, 164))
    d.line([0, 200, W, 200], fill=(120, 124, 134), width=6)
    # 丸窓と空
    for wx in range(180, W, 340):
        d.rounded_rectangle([wx, 300, wx + 170, 520], radius=70, fill=(120, 124, 134))
        d.rounded_rectangle([wx + 14, 314, wx + 156, 506], radius=58,
                            fill=(150, 196, 232))
        d.ellipse([wx + 30, 340, wx + 80, 380], fill=(240, 246, 250))
        d.ellipse([wx + 70, 420, wx + 130, 460], fill=(236, 242, 248))
    # 座席の背もたれ（下端）
    for sx in range(-60, W, 300):
        d.rounded_rectangle([sx, 800, sx + 240, 1080], radius=30, fill=(70, 92, 132))
        d.rounded_rectangle([sx + 30, 820, sx + 210, 900], radius=16, fill=(96, 118, 156))
    return img.convert("RGB")


def make_ginza():
    """1971・銀座の歩行者天国（昼・道路開放）。"""
    img = base((176, 204, 226), (210, 222, 230))
    d = ImageDraw.Draw(img, "RGBA")
    bl = [(140, 132, 124), (162, 154, 146), (120, 116, 112)]
    for i, (bx, bw, bh) in enumerate([(40, 340, 520), (420, 260, 620), (720, 380, 480),
                                      (1140, 280, 600), (1460, 400, 520)]):
        col = bl[i % 3]
        d.rectangle([bx, 700 - bh, bx + bw, 700], fill=col)
        for wy in range(710 - bh + 16, 680, 52):
            for wx in range(bx + 16, bx + bw - 24, 56):
                d.rectangle([wx, wy, wx + 30, wy + 34], fill=(226, 232, 238))
        # 看板の色板
        d.rectangle([bx + 20, 700 - bh + 8, bx + bw - 20, 700 - bh + 48],
                    fill=[(200, 90, 80), (90, 130, 180), (210, 170, 80)][i % 3])
    # 開放された車道（広い・明るい）
    d.rectangle([0, 700, W, H], fill=(174, 176, 180))
    d.line([0, 700, W, 700], fill=(140, 142, 148), width=6)
    for x in range(100, W, 320):
        d.rectangle([x, 860, x + 150, 884], fill=(230, 232, 236))
    # パラソル（歩行者天国名物）
    for px, pc in [(300, (220, 120, 100)), (1500, (110, 150, 200))]:
        d.line([px, 620, px, 830], fill=(110, 104, 98), width=10)
        d.pieslice([px - 170, 520, px + 170, 720], start=180, end=360, fill=pc)
    return img.convert("RGB")


def make_uchu():
    """星空と地球の縁（晩年・宇宙）。"""
    img = base((10, 14, 30), (22, 28, 52))
    d = ImageDraw.Draw(img, "RGBA")
    import random as _rr
    r = _rr.Random(5)
    for _ in range(180):
        x, y = r.random() * W, r.random() * H * 0.8
        s = 1 + r.random() * 3
        a = 120 + int(r.random() * 135)
        d.ellipse([x, y, x + s, y + s], fill=(230, 236, 250, a))
    # 地球の縁（下部の弧）
    d.ellipse([-500, 820, W + 500, 2400], fill=(40, 80, 140))
    d.ellipse([-500, 850, W + 500, 2430], fill=(52, 100, 160))
    d.arc([-500, 820, W + 500, 2400], start=180, end=360, fill=(140, 200, 255), width=10)
    glow(img, 960, 900, 700, (90, 150, 230), 40)
    return img.convert("RGB")


def make_conbini():
    """現代のコンビニ棚（カップ麺コーナー）。"""
    img = base((214, 220, 226), (192, 198, 206))
    d = ImageDraw.Draw(img, "RGBA")
    pal = [(196, 74, 64), (230, 168, 60), (86, 130, 180), (110, 160, 110),
           (170, 110, 160), (230, 120, 90)]
    for r in range(3):
        sy = 130 + r * 240
        d.rectangle([120, sy + 170, 1800, sy + 196], fill=(160, 166, 176))
        k = r * 2
        x = 160
        while x < 1740:
            col = pal[k % len(pal)]
            # カップ（台形）+ 蓋
            d.polygon([(x, sy + 40), (x + 96, sy + 40), (x + 84, sy + 168),
                       (x + 12, sy + 168)], fill=(242, 240, 234))
            d.rectangle([x + 6, sy + 66, x + 90, sy + 96], fill=col)
            d.ellipse([x - 2, sy + 28, x + 98, sy + 52], fill=(248, 246, 242))
            x += 128
            k += 1
    d.rectangle([0, int(H * 0.80), W, H], fill=(178, 182, 190))
    return img.convert("RGB")


def make_hotel():
    """京都のホテル・電話交換台（出会いの場）。"""
    img = base((92, 72, 66), (66, 52, 50))
    d = ImageDraw.Draw(img, "RGBA")
    # 壁のパネルと飾り
    for x in range(120, W, 440):
        d.rectangle([x, 120, x + 320, 620], outline=(120, 96, 84), width=8)
        d.rectangle([x + 24, 150, x + 296, 590], outline=(110, 88, 78), width=4)
    # シャンデリア風の照明
    for lx in (520, 1400):
        d.line([lx, 0, lx, 110], fill=(70, 58, 52), width=6)
        glow(img, lx, 190, 240, (255, 214, 150), 60)
        d = ImageDraw.Draw(img, "RGBA")
        for k in range(3):
            d.ellipse([lx - 70 + k * 50, 130, lx - 30 + k * 50, 190],
                      fill=(255, 228, 170))
    # 交換台（プラグボード）
    bx0, by0, bx1, by1 = 700, 300, 1240, 700
    d.rectangle([bx0, by0, bx1, by1], fill=(58, 46, 42))
    d.rectangle([bx0 + 16, by0 + 16, bx1 - 16, by1 - 120], fill=(40, 34, 32))
    for r in range(4):
        for c in range(10):
            px = bx0 + 50 + c * 46
            py = by0 + 50 + r * 60
            d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=(190, 170, 120))
    # コード
    for c in range(3):
        x0 = bx0 + 90 + c * 140
        d.arc([x0, by1 - 170, x0 + 180, by1 + 40], start=180, end=330,
              fill=(150, 120, 90), width=8)
    # 机
    d.rectangle([bx0 - 60, by1, bx1 + 60, by1 + 40], fill=(84, 62, 50))
    # 絨毯
    d.rectangle([0, int(H * 0.74), W, H], fill=(110, 60, 58))
    for yy in range(int(H * 0.74) + 20, H, 44):
        d.line([0, yy, W, yy], fill=(96, 52, 50), width=3)
    return img.convert("RGB")


def make_kenkyujo():
    """国民栄養化学研究所（フラスコと大鍋）。"""
    img = base((70, 78, 82), (54, 60, 64))
    d = ImageDraw.Draw(img, "RGBA")
    # 棚とフラスコ・瓶
    d.rectangle([130, 150, 900, 172], fill=(96, 88, 76))
    d.rectangle([130, 330, 900, 352], fill=(96, 88, 76))
    pal = [(150, 190, 170), (210, 180, 120), (170, 160, 200), (190, 140, 130)]
    for row, sy in ((0, 172), (1, 352)):
        for i, bx in enumerate(range(170, 860, 96)):
            col = pal[(i + row) % len(pal)]
            if (i + row) % 3 == 0:
                d.polygon([(bx + 18, sy - 90), (bx + 42, sy - 90), (bx + 58, sy - 8),
                           (bx + 2, sy - 8)], fill=col)
                d.rectangle([bx + 24, sy - 118, bx + 36, sy - 88], fill=(200, 208, 214))
            else:
                d.rounded_rectangle([bx + 8, sy - 100, bx + 52, sy - 6], radius=10,
                                    fill=col)
    # 大鍋（骨を煮る）と火
    d.rounded_rectangle([1200, 560, 1700, 820], radius=30, fill=(88, 92, 100))
    d.ellipse([1220, 530, 1680, 610], fill=(110, 114, 124))
    d.rectangle([1260, 820, 1640, 880], fill=(70, 62, 58))
    for fx in range(1300, 1620, 80):
        d.polygon([(fx, 880), (fx + 26, 830), (fx + 52, 880)], fill=(240, 160, 76))
    # 湯気
    for k in range(3):
        pts = []
        for j in range(9):
            yy = 520 - j * 26
            pts.append((1330 + k * 110 + 18 * (1 if (j + k) % 2 else -1), yy))
        d.line(pts, fill=(230, 236, 244, 130), width=10)
    # 作業台
    d.rectangle([150, 700, 900, 740], fill=(96, 88, 76))
    d.rectangle([180, 740, 220, 1000], fill=(80, 72, 62))
    d.rectangle([830, 740, 870, 1000], fill=(80, 72, 62))
    d.rectangle([0, int(H * 0.86), W, H], fill=(62, 66, 70))
    hanging_bulb(img, 960, warm=False, ly=60)
    return img.convert("RGB")


DRAMA_BGS = {
    "il_nunoya": make_nunoya, "il_library": make_library, "il_shokai": make_shokai,
    "il_yagaku": make_yagaku, "il_kojo": make_kojo, "il_yamiichi": make_yamiichi,
    "il_hama": make_hama, "il_goku": make_goku, "il_koya": make_koya,
    "il_daidokoro": make_daidokoro, "il_shotengai": make_shotengai,
    "il_america": make_america, "il_kinai": make_kinai, "il_ginza": make_ginza,
    "il_uchu": make_uchu, "il_conbini": make_conbini,
    "il_hotel": make_hotel, "il_kenkyujo": make_kenkyujo,
}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    kitchen_night().save(OUT / "il_kitchen_night.png")
    print("生成完了: assets/backgrounds/il_kitchen_night.png")
    washitsu_1957().save(OUT / "il_washitsu_1957.png")
    print("生成完了: assets/backgrounds/il_washitsu_1957.png")
    for name, fn in DRAMA_BGS.items():
        fn().save(OUT / f"{name}.png")
        print(f"生成完了: assets/backgrounds/{name}.png")
