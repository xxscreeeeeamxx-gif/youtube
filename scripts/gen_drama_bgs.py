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


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    kitchen_night().save(OUT / "il_kitchen_night.png")
    print("生成完了: assets/backgrounds/il_kitchen_night.png")
    washitsu_1957().save(OUT / "il_washitsu_1957.png")
    print("生成完了: assets/backgrounds/il_washitsu_1957.png")
