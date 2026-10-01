#!/usr/bin/env python3
"""ヤマハの誕生・山葉寅楠回（76_ヤマハの誕生 / slug=yamaha-torakusu）の背景を生成する。

gen_drama_bgs.py の共通部品を使い、この回の場所背景と
章替わりの年号カードを書き出す。方針はファミコン回（gen_famicom_bgs.py）・
蚊取り線香回（gen_katori_bgs.py）と同じ。
実在の会社の商標（音叉3本のマーク・社名の文字）は描かない。音叉は道具としての1本だけを描く。
明治の場面は電灯ではなく石油ランプにする。
人物が立つ左右（ずんだもん x0.2〜0.28 / 相手 x0.56〜0.8）の下3分の1は床だけにし、
小道具はキャラの間（x 680〜1240 付近）か、頭より上（y 200 より上）に置く。

実行: PYTHONPATH=. python scripts/gen_yh_bgs.py [名前...]
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

from scripts.gen_drama_bgs import (  # noqa: E402
    H, OUT, W, base, glow, tatami_floor, vgrad, wood_floor,
)

FLOOR = int(H * 0.86)
INK = (60, 56, 52)
BRASS = (200, 170, 80)
PAPER = (244, 240, 226)


def _d(img):
    return ImageDraw.Draw(img, "RGBA")


def _dk(col, f=0.72):
    return tuple(int(c * f) for c in col[:3])


def _lt(col, f=1.25):
    return tuple(min(255, int(c * f)) for c in col[:3])


def _font(size):
    from ytf.config import Config, resolve_font
    Config.load()
    return ImageFont.truetype(resolve_font("w9"), size)


def _text_c(d, cx, y, t, size, fill):
    f = _font(size)
    bb = d.textbbox((0, 0), t, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y), t, font=f, fill=fill)


def _rgba(img):
    return img.convert("RGBA") if img.mode != "RGBA" else img


def _tint(img, col, alpha):
    """画面全体に色をかぶせる（夜・火事の照り返し）。"""
    return Image.alpha_composite(_rgba(img), Image.new("RGBA", img.size, (*col, alpha)))


# ---------------------------------------------------------------- 小物
def _window(d, x0, y0, x1, y1, sky=(176, 206, 228), frame=(84, 64, 48), bars=True):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)
    if bars:
        d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=8)
        d.line([(x0, (y0 + y1) // 2), (x1, (y0 + y1) // 2)], fill=frame, width=6)


def _arch_window(d, x0, y0, x1, y1, sky=(190, 212, 230), frame=(96, 76, 58)):
    """洋館の縦長の窓（上が半円）。"""
    r = (x1 - x0) // 2
    d.pieslice([x0, y0, x1, y0 + 2 * r], 180, 360, fill=sky)
    d.rectangle([x0, y0 + r, x1, y1], fill=sky)
    d.arc([x0, y0, x1, y0 + 2 * r], 180, 360, fill=frame, width=10)
    for x in (x0, x1):
        d.line([(x, y0 + r), (x, y1)], fill=frame, width=10)
    d.line([(x0, y1), (x1, y1)], fill=frame, width=10)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame, width=6)
    for k in (1, 2):
        yy = y0 + r + (y1 - y0 - r) * k // 3
        d.line([(x0, yy), (x1, yy)], fill=frame, width=5)


def _shoji(d, x0, y0, x1, y1, paper=(232, 224, 204), frame=(110, 84, 60), cols=4, rows=5):
    d.rectangle([x0, y0, x1, y1], fill=paper)
    for k in range(cols + 1):
        x = x0 + (x1 - x0) * k // cols
        d.line([(x, y0), (x, y1)], fill=frame, width=6)
    for k in range(rows + 1):
        y = y0 + (y1 - y0) * k // rows
        d.line([(x0, y), (x1, y)], fill=frame, width=5)
    d.rectangle([x0, y0, x1, y1], outline=frame, width=10)


def _wainscot(d, y0, y1, col=(120, 90, 62)):
    """洋室の腰板。"""
    d.rectangle([0, y0, W, y1], fill=col)
    d.line([(0, y0), (W, y0)], fill=_dk(col), width=8)
    for x in range(60, W, 240):
        d.rectangle([x, y0 + 20, x + 200, y1 - 16], outline=_dk(col, 0.85), width=4)


def _organ(d, x, y, s=1.0, wood=(112, 68, 42), open_front=False, simple=False):
    """足踏みのリードオルガン（左上が x, y。幅 360*s・高さ 480*s）。"""
    w = 360 * s
    dk, lt = _dk(wood), _lt(wood)
    if not simple:                                                           # 上の飾り棚
        d.polygon([(x + 10 * s, y), (x + w / 2, y - 44 * s), (x + w - 10 * s, y)], fill=dk)
        d.rectangle([x + 20 * s, y, x + w - 20 * s, y + 150 * s], fill=wood, outline=dk, width=3)
        d.rectangle([x + 60 * s, y + 26 * s, x + w - 60 * s, y + 120 * s], fill=lt)
        d.rectangle([x + w / 2 - 54 * s, y + 52 * s, x + w / 2 + 54 * s, y + 104 * s], fill=dk)  # 譜面台
    d.rectangle([x, y + 150 * s, x + w, y + 480 * s], fill=wood, outline=dk, width=3)
    ky = y + 192 * s                                                         # 鍵盤
    d.rectangle([x + 6 * s, ky - 16 * s, x + w - 6 * s, ky], fill=dk)
    d.rectangle([x + 20 * s, ky, x + w - 20 * s, ky + 40 * s], fill=(240, 234, 220), outline=dk, width=2)
    n = 20
    kw = (w - 40 * s) / n
    for k in range(1, n):
        kx = x + 20 * s + kw * k
        d.line([(kx, ky), (kx, ky + 40 * s)], fill=(176, 166, 146), width=1)
    for k in range(n - 1):
        if k % 7 in (2, 6):
            continue
        kx = x + 20 * s + kw * (k + 0.65)
        d.rectangle([kx, ky, kx + kw * 0.7, ky + 24 * s], fill=(40, 32, 28))
    if open_front:                                                           # 前板を外した中身
        d.rectangle([x + 26 * s, y + 252 * s, x + w - 26 * s, y + 424 * s], fill=(42, 30, 24))
        for k in range(12):                                                  # 並んだリード
            rx = x + 44 * s + k * (w - 88 * s) / 12
            d.rectangle([rx, y + 290 * s, rx + 12 * s, y + 380 * s], fill=BRASS)
        d.rectangle([x + 40 * s, y + 270 * s, x + w - 40 * s, y + 282 * s], fill=(90, 70, 50))
    else:
        d.rectangle([x + 40 * s, y + 262 * s, x + w - 40 * s, y + 412 * s], fill=lt, outline=dk, width=3)
        d.ellipse([x + w / 2 - 30 * s, y + 310 * s, x + w / 2 + 30 * s, y + 364 * s], outline=dk, width=3)
    for k in (0, 1):                                                         # ペダル
        px = x + w * (0.26 + 0.32 * k)
        d.polygon([(px, y + 432 * s), (px + 64 * s, y + 432 * s), (px + 74 * s, y + 470 * s),
                   (px - 10 * s, y + 470 * s)], fill=(70, 60, 50))


def _upright(d, x, y, s=1.0, col=(30, 28, 30), doors=False):
    """アップライトピアノ（左上が x, y。幅 400*s・高さ 380*s）。doors=True は戸棚のような扉の線。"""
    w, h = 400 * s, 380 * s
    hi = _lt(col, 1.0) if sum(col) > 300 else tuple(min(255, c + 40) for c in col)
    d.rectangle([x, y, x + w, y + h], fill=col)
    d.rectangle([x - 10 * s, y - 12 * s, x + w + 10 * s, y + 6 * s], fill=hi)
    if doors:                                                                # 観音開きの戸棚の扉
        for k in (0, 1):
            d.rectangle([x + 30 * s + k * (w / 2 - 20 * s), y + 30 * s,
                         x + w / 2 - 10 * s + k * (w / 2 - 20 * s), y + 150 * s], outline=_dk(col), width=5)
            d.ellipse([x + w / 2 - 22 * s + k * 34 * s, y + 84 * s, x + w / 2 - 12 * s + k * 34 * s, y + 96 * s],
                      fill=BRASS)
    else:
        d.rectangle([x + 30 * s, y + 40 * s, x + w - 30 * s, y + 140 * s], fill=hi)
    ky = y + 170 * s
    d.rectangle([x - 14 * s, ky - 16 * s, x + w + 14 * s, ky], fill=col)
    d.rectangle([x, ky, x + w, ky + 34 * s], fill=(244, 240, 232))
    n = 28
    for k in range(1, n):
        kx = x + w * k / n
        d.line([(kx, ky), (kx, ky + 34 * s)], fill=(180, 176, 168), width=1)
    for k in range(n - 1):
        if k % 7 in (2, 6):
            continue
        kx = x + w * (k + 0.65) / n
        d.rectangle([kx, ky, kx + w / n * 0.7, ky + 20 * s], fill=(20, 20, 22))
    d.rectangle([x - 14 * s, ky + 34 * s, x + w + 14 * s, ky + 50 * s], fill=hi)
    d.rectangle([x + 30 * s, ky + 74 * s, x + w - 30 * s, y + h - 24 * s], fill=hi)
    for lx in (x + 10 * s, x + w - 40 * s):
        d.rectangle([lx, y + h, lx + 30 * s, y + h + 20 * s], fill=col)
    for k in range(3):
        px = x + w / 2 - 50 * s + k * 40 * s
        d.rectangle([px, y + h - 10 * s, px + 20 * s, y + h + 2 * s], fill=BRASS)


def _grand(d, x, y, s=1.0, col=(26, 24, 26)):
    """グランドピアノを横から（左上が x, y。幅 ~540*s。屋根を開けている）。"""
    hi = tuple(min(255, c + 46) for c in col)
    d.polygon([(x + 70 * s, y + 70 * s), (x + 480 * s, y + 70 * s), (x + 330 * s, y - 150 * s)], fill=hi)
    d.line([(x + 260 * s, y + 70 * s), (x + 318 * s, y - 116 * s)], fill=(150, 150, 154), width=int(5 * s))
    d.rounded_rectangle([x + 40 * s, y + 66 * s, x + 540 * s, y + 170 * s], radius=int(50 * s), fill=col)
    d.rectangle([x, y + 92 * s, x + 64 * s, y + 132 * s], fill=col)
    d.rectangle([x + 4 * s, y + 94 * s, x + 60 * s, y + 106 * s], fill=(244, 240, 232))
    for lx in (x + 54 * s, x + 300 * s, x + 500 * s):
        d.rectangle([lx - 12 * s, y + 170 * s, lx + 12 * s, y + 330 * s], fill=col)
        d.ellipse([lx - 16 * s, y + 322 * s, lx + 16 * s, y + 338 * s], fill=BRASS)
    d.rectangle([x + 150 * s, y + 170 * s, x + 176 * s, y + 296 * s], fill=col)
    d.rectangle([x + 136 * s, y + 292 * s, x + 190 * s, y + 302 * s], fill=BRASS)


def _onsa(d, cx, by, s=1.0, col=(188, 192, 200)):
    """道具としての音叉1本（木の台に立てた形）。by は台の底。"""
    d.rectangle([cx - 30 * s, by - 18 * s, cx + 30 * s, by], fill=(120, 86, 58))
    d.rectangle([cx - 5 * s, by - 72 * s, cx + 5 * s, by - 18 * s], fill=col)
    wd = max(3, int(8 * s))
    d.arc([cx - 22 * s, by - 104 * s, cx + 22 * s, by - 60 * s], 0, 180, fill=col, width=wd)
    for k in (-1, 1):
        d.line([(cx + k * 18 * s, by - 82 * s), (cx + k * 18 * s, by - 196 * s)], fill=col, width=wd)


def _wall_clock(d, cx, cy, s=1.0):
    d.rounded_rectangle([cx - 60 * s, cy - 80 * s, cx + 60 * s, cy + 170 * s], radius=int(14 * s),
                        fill=(110, 70, 40), outline=(70, 44, 26), width=3)
    d.ellipse([cx - 46 * s, cy - 66 * s, cx + 46 * s, cy + 26 * s], fill=(244, 238, 220), outline=(70, 44, 26), width=3)
    d.line([(cx, cy - 20 * s), (cx, cy - 56 * s)], fill=INK, width=3)
    d.line([(cx, cy - 20 * s), (cx + 26 * s, cy - 10 * s)], fill=INK, width=3)
    d.rectangle([cx - 30 * s, cy + 44 * s, cx + 30 * s, cy + 156 * s], fill=(80, 52, 30))
    d.line([(cx, cy + 48 * s), (cx + 8 * s, cy + 128 * s)], fill=BRASS, width=3)
    d.ellipse([cx - 2 * s, cy + 124 * s, cx + 18 * s, cy + 144 * s], fill=(220, 190, 90))


def _gear(d, cx, cy, r, teeth=10, col=BRASS):
    pts = []
    for k in range(teeth * 2):
        a = math.pi * k / teeth
        rr = r if k % 2 == 0 else r * 0.78
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col)
    d.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3], fill=(90, 70, 40))


def _lamp(img, cx, by, s=1.0, lit=True):
    """石油ランプ。by は台の底。"""
    d = _d(img)
    if lit:
        glow(img, int(cx), int(by - 100 * s), int(230 * s), (255, 200, 120), 80)
        d = _d(img)
    d.rectangle([cx - 26 * s, by - 20 * s, cx + 26 * s, by], fill=(150, 120, 60))
    d.ellipse([cx - 30 * s, by - 72 * s, cx + 30 * s, by - 14 * s], fill=(180, 150, 70))
    d.rectangle([cx - 12 * s, by - 120 * s, cx + 12 * s, by - 66 * s], fill=(252, 238, 190) if lit else (200, 200, 190))
    d.ellipse([cx - 22 * s, by - 152 * s, cx + 22 * s, by - 90 * s], outline=(225, 225, 215), width=3)


def _hang_lamp(img, cx, ly=60, s=1.0, lit=True):
    """天井から吊るした石油ランプ。"""
    d = _d(img)
    d.line([(cx, 0), (cx, ly)], fill=(50, 40, 32), width=5)
    if lit:
        glow(img, int(cx), int(ly + 70 * s), int(300 * s), (255, 200, 120), 60)
        d = _d(img)
    d.polygon([(cx - 70 * s, ly + 40 * s), (cx + 70 * s, ly + 40 * s), (cx + 30 * s, ly), (cx - 30 * s, ly)], fill=(70, 60, 50))
    d.rectangle([cx - 14 * s, ly + 40 * s, cx + 14 * s, ly + 90 * s], fill=(252, 238, 190) if lit else (200, 200, 190))
    d.ellipse([cx - 22 * s, ly + 84 * s, cx + 22 * s, ly + 110 * s], fill=(180, 150, 70))


def _bench(d, x0, x1, y, col=(130, 96, 64), legs=150):
    d.rectangle([x0, y, x1, y + 30], fill=col)
    for lx in (x0 + 20, x1 - 44):
        d.rectangle([lx, y + 30, lx + 24, y + 30 + legs], fill=_dk(col, 0.78))


def _zumen(d, x, y, n=6, w=130):
    """図面の紙の束（左下が x, y）。"""
    for k in range(n):
        d.rectangle([x + k * 3, y - k * 7 - 60, x + w + k * 3, y - k * 7], fill=PAPER, outline=(170, 160, 140), width=2)
    tx, ty = x + (n - 1) * 3, y - (n - 1) * 7 - 60
    d.rectangle([tx + 18, ty + 12, tx + w - 18, ty + 46], outline=(60, 90, 150), width=2)
    for k in range(4):
        d.line([(tx + 18 + k * 24, ty + 12), (tx + 18 + k * 24, ty + 46)], fill=(60, 90, 150), width=1)


def _tool_rack(d, x0, y0, x1, y1, full=True):
    d.rectangle([x0, y0, x1, y1], fill=(120, 90, 60))
    d.rectangle([x0 + 10, y0 + 10, x1 - 10, y1 - 10], fill=(146, 112, 78))
    n = 6
    for k in range(n):
        if not full and k % 2:
            continue
        tx = x0 + 34 + k * (x1 - x0 - 68) / (n - 1)
        if k % 3 == 0:                                                       # 金槌
            d.line([(tx, y0 + 44), (tx, y1 - 30)], fill=(110, 80, 50), width=8)
            d.rectangle([tx - 22, y0 + 30, tx + 22, y0 + 52], fill=(120, 120, 128))
        elif k % 3 == 1:                                                     # 鏨
            d.line([(tx, y0 + 30), (tx, y1 - 40)], fill=(160, 160, 168), width=7)
        else:                                                                # 鑢
            d.rectangle([tx - 6, y0 + 30, tx + 6, y1 - 54], fill=(110, 110, 118))
            d.rectangle([tx - 8, y1 - 54, tx + 8, y1 - 28], fill=(110, 80, 50))


def _tansu(d, x0, y0, x1, y1, col=(156, 108, 62)):
    d.rectangle([x0, y0, x1, y1], fill=col, outline=(90, 60, 34), width=4)
    rh = (y1 - y0) / 4
    for r in range(4):
        yy = y0 + r * rh
        d.rectangle([x0 + 12, yy + 10, x1 - 12, yy + rh - 8], outline=(90, 60, 34), width=3)
        d.rectangle([(x0 + x1) / 2 - 22, yy + rh / 2 - 6, (x0 + x1) / 2 + 22, yy + rh / 2 + 6], fill=(60, 50, 40))


def _sugi(d, x, base_y, h, col=(50, 84, 58)):
    """杉の木。"""
    d.rectangle([x - 9, base_y - h * 0.3, x + 9, base_y], fill=(92, 64, 42))
    for k in range(4):
        ty = base_y - h * 0.22 - k * h * 0.19
        w = h * 0.2 * (1 - k * 0.17)
        d.polygon([(x - w, ty), (x + w, ty), (x, ty - h * 0.33)], fill=col if k % 2 == 0 else _lt(col, 1.12))


def _smoke(img, seed, n, ymin, ymax, col=(120, 116, 112), alpha=150, rmin=60, rmax=120, blur=14):
    rnd = random.Random(seed)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        cx, cy = rnd.randint(-80, W + 80), rnd.randint(ymin, ymax)
        for _ in range(5):
            r = rnd.randint(rmin, rmax)
            ox, oy = rnd.randint(-r, r), rnd.randint(-r // 2, r // 2)
            d.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r], fill=(*col, alpha))
    return Image.alpha_composite(_rgba(img), lay.filter(ImageFilter.GaussianBlur(blur)))


def _flames(img, x0, x1, base_y, h, seed=3):
    rnd = random.Random(seed)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(int((x1 - x0) / 46)):
        cx = x0 + k * 46 + rnd.randint(-12, 12)
        hh = h * rnd.uniform(0.45, 1.0)
        d.polygon([(cx - 56, base_y), (cx + 56, base_y), (cx + rnd.randint(-24, 24), base_y - hh)], fill=(236, 96, 36, 225))
        d.polygon([(cx - 30, base_y), (cx + 30, base_y), (cx + rnd.randint(-12, 12), base_y - hh * 0.6)], fill=(255, 196, 70, 235))
    return Image.alpha_composite(_rgba(img), lay.filter(ImageFilter.GaussianBlur(3)))


def _safe(d, x, y, s=1.0):
    """金庫（左上が x, y）。"""
    d.rectangle([x, y, x + 200 * s, y + 220 * s], fill=(46, 58, 50), outline=(20, 26, 22), width=5)
    d.rectangle([x + 16 * s, y + 16 * s, x + 184 * s, y + 204 * s], outline=(96, 110, 98), width=4)
    d.ellipse([x + 66 * s, y + 70 * s, x + 130 * s, y + 134 * s], fill=(184, 172, 130), outline=(60, 56, 40), width=3)
    d.line([(x + 98 * s, y + 102 * s), (x + 118 * s, y + 84 * s)], fill=(60, 56, 40), width=4)
    d.rectangle([x + 150 * s, y + 88 * s, x + 164 * s, y + 152 * s], fill=(184, 172, 130))


def _drill(d, x, y, s=1.0, col=(58, 78, 88)):
    """アメリカ製の穴あけ機械（ボール盤。左上が x, y、高さ 440*s）。"""
    d.rectangle([x, y + 400 * s, x + 230 * s, y + 440 * s], fill=col)
    d.rectangle([x + 30 * s, y, x + 72 * s, y + 400 * s], fill=col)
    d.rectangle([x + 30 * s, y + 20 * s, x + 206 * s, y + 104 * s], fill=col)
    d.ellipse([x + 150 * s, y + 26 * s, x + 236 * s, y + 96 * s], fill=(92, 112, 122))
    d.rectangle([x + 120 * s, y + 104 * s, x + 136 * s, y + 194 * s], fill=(172, 172, 178))
    d.polygon([(x + 120 * s, y + 194 * s), (x + 136 * s, y + 194 * s), (x + 128 * s, y + 220 * s)], fill=(206, 206, 212))
    d.rectangle([x + 72 * s, y + 252 * s, x + 206 * s, y + 272 * s], fill=col)
    d.line([(x + 72 * s, y + 132 * s), (x - 4 * s, y + 174 * s)], fill=(162, 162, 168), width=max(3, int(7 * s)))
    d.ellipse([x - 16 * s, y + 162 * s, x + 8 * s, y + 186 * s], fill=(150, 40, 40))
    d.rectangle([x + 84 * s, y + 300 * s, x + 176 * s, y + 380 * s], fill=PAPER, outline=(150, 140, 120), width=2)  # 英語の説明書
    for k in range(5):
        d.line([(x + 94 * s, y + (316 + k * 12) * s), (x + 166 * s, y + (316 + k * 12) * s)], fill=(120, 120, 130), width=2)


def _action(d, x, y, n=10, s=1.0):
    """ピアノのアクション（ハンマーが並ぶ部品。左上が x, y）。"""
    d.rectangle([x, y + 80 * s, x + n * 28 * s + 20 * s, y + 98 * s], fill=(150, 120, 80))
    for k in range(n):
        hx = x + 14 * s + k * 28 * s
        d.line([(hx, y + 80 * s), (hx, y + 24 * s)], fill=(206, 186, 146), width=max(2, int(5 * s)))
        d.rounded_rectangle([hx - 9 * s, y, hx + 9 * s, y + 28 * s], radius=int(5 * s), fill=(236, 232, 220), outline=(150, 140, 120))


def _kohaku(d, x0, x1, y, h=90):
    """紅白幕。"""
    d.rectangle([x0, y - 10, x1, y], fill=(60, 40, 30))
    for k, x in enumerate(range(x0, x1, 60)):
        d.rectangle([x, y, x + 60, y + h], fill=(206, 44, 54) if k % 2 == 0 else (250, 248, 244))


def _banners(d, xs, y0, y1, cols):
    for k, x in enumerate(xs):
        c = cols[k % len(cols)]
        d.polygon([(x, y0), (x + 70, y0), (x + 70, y1), (x + 35, y1 - 30), (x, y1)], fill=c)


def _trusses(d, col=(110, 96, 86)):
    """博覧会場の天井の梁。"""
    d.rectangle([0, 0, W, 40], fill=col)
    for x in range(0, W, 320):
        d.line([(x, 40), (x + 160, 150), (x + 320, 40)], fill=col, width=10)
        d.line([(x + 160, 40), (x + 160, 150)], fill=col, width=6)


def _dais(d, x0, x1, y, col=(150, 50, 50)):
    """展示の台（赤い布をかけた低い台）。"""
    d.rectangle([x0, y, x1, y + 70], fill=col)
    d.rectangle([x0, y, x1, y + 14], fill=_lt(col, 1.15))


# ---------------------------------------------------------------- 現代
def ongakushitsu():
    """今の学校の音楽室。真ん中にアップライトピアノ、その上に音叉、壁に五線の掲示。"""
    img = base((236, 234, 226), (222, 220, 212))
    wood_floor(img, FLOOR, col=(196, 168, 128), line=(176, 150, 112))
    d = _d(img)
    for x in (300, 900, 1500):                                              # 天井の照明
        d.rectangle([x, 0, x + 300, 26], fill=(250, 250, 246), outline=(200, 200, 196))
    d.rectangle([640, 90, 1280, 240], fill=(250, 250, 246), outline=(150, 150, 160), width=6)  # 五線の掲示
    for k in range(5):
        d.line([(670, 120 + k * 22), (1250, 120 + k * 22)], fill=(80, 80, 90), width=3)
    for k, (nx, ny) in enumerate(((740, 186), (840, 164), (940, 142), (1040, 164), (1140, 120))):
        d.ellipse([nx - 14, ny - 10, nx + 14, ny + 10], fill=(40, 40, 50))
        d.line([(nx + 13, ny), (nx + 13, ny - 60)], fill=(40, 40, 50), width=4)
    _window(d, 1400, 120, 1860, 520, sky=(186, 214, 236), frame=(200, 200, 204))
    d.ellipse([100, 120, 220, 240], fill=(250, 250, 248), outline=(90, 90, 100), width=6)   # 時計
    d.line([(160, 180), (160, 140)], fill=INK, width=4)
    d.line([(160, 180), (190, 196)], fill=INK, width=4)
    _upright(d, 760, 430, 1.0, col=(24, 22, 26))
    _onsa(d, 1090, 418, 0.75)
    return img


def gendai():
    """今の楽器の売り場。グランドピアノと電子ピアノ、ギター（社名やマークは描かない）。"""
    img = base((240, 240, 238), (226, 226, 224))
    wood_floor(img, FLOOR, col=(204, 186, 160), line=(186, 168, 142))
    d = _d(img)
    for x in (200, 760, 1320):                                              # 天井のライン照明
        d.rectangle([x, 0, x + 400, 22], fill=(255, 255, 250))
    d.rectangle([600, 110, 1320, 300], fill=(214, 220, 232))                 # 壁の色面
    _grand(d, 610, 520, 0.72)
    d.rectangle([1010, 600, 1250, 630], fill=(40, 40, 44))                  # 電子ピアノ
    d.rectangle([1016, 604, 1244, 618], fill=(244, 244, 240))
    for k in range(16):
        d.rectangle([1022 + k * 14, 604, 1030 + k * 14, 612], fill=(30, 30, 32))
    d.line([(1040, 630), (1080, 760)], fill=(60, 60, 64), width=8)
    d.line([(1220, 630), (1180, 760)], fill=(60, 60, 64), width=8)
    gy = 230                                                                # ギター（スタンドに立てる）
    d.ellipse([1236, 360 + gy, 1316, 450 + gy], fill=(196, 130, 60))
    d.ellipse([1228, 420 + gy, 1324, 530 + gy], fill=(196, 130, 60))
    d.ellipse([1262, 430 + gy, 1290, 458 + gy], fill=(60, 40, 26))
    d.rectangle([1270, 240 + gy, 1282, 380 + gy], fill=(80, 54, 34))
    d.rectangle([1264, 222 + gy, 1288, 246 + gy], fill=(60, 40, 26))
    d.line([(1276, 530 + gy), (1250, 600 + gy)], fill=(80, 80, 84), width=6)
    d.line([(1276, 530 + gy), (1300, 600 + gy)], fill=(80, 80, 84), width=6)
    return img


# ---------------------------------------------------------------- 紀州・長崎・大阪
def kishu():
    """幕末の紀州藩の天文係の家。障子、和本の棚、望遠鏡、天球儀、からくり人形。"""
    img = base((206, 192, 166), (180, 164, 138))
    tatami_floor(img, FLOOR)
    d = _d(img)
    _shoji(d, 1260, 130, 1880, 700)
    d.rectangle([60, 110, 600, 150], fill=(96, 70, 48))                      # 和本の棚
    for k in range(3):
        y = 200 + k * 110
        d.rectangle([60, y, 600, y + 14], fill=(96, 70, 48))
        for j in range(5):
            x = 80 + j * 104
            for i in range(3):
                d.rectangle([x, y - 16 * (i + 1), x + 86 - (i % 2) * 8, y - 16 * i - 2],
                            fill=((70, 80, 110), (120, 60, 50), (150, 130, 90))[(i + j + k) % 3])
    d.rectangle([700, 180, 1220, 430], fill=(236, 228, 206), outline=(110, 84, 60), width=8)   # 掛けた測量図
    d.line([(740, 380), (820, 300), (900, 330), (980, 250), (1060, 290), (1180, 220)], fill=(60, 90, 150), width=4)
    for k in range(5):
        d.line([(720 + k * 100, 190), (720 + k * 100, 420)], fill=(200, 190, 170), width=2)
    dy = 140
    d.rectangle([740, 640 + dy, 1180, 664 + dy], fill=(110, 80, 52))         # 文机
    for lx in (756, 1146):
        d.rectangle([lx, 664 + dy, lx + 20, 720 + dy], fill=(88, 64, 42))
    _armillary(d, 830, 560 + dy, 56)
    _karakuri(d, 1000, 640 + dy, 1.0)
    d.rectangle([1080, 616 + dy, 1160, 640 + dy], fill=(196, 176, 120))      # 測量の道具（目盛り板）
    for k in range(9):
        d.line([(1086 + k * 9, 616 + dy), (1086 + k * 9, 626 + (k % 2) * 6 + dy)], fill=INK, width=2)
    _telescope(d, 1700, 690, 0.95)
    return img


def _armillary(d, cx, cy, r, col=(190, 150, 70)):
    """天球儀（輪を組んだ形）。"""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=5)
    d.ellipse([cx - r, cy - r * 0.35, cx + r, cy + r * 0.35], outline=col, width=4)
    d.ellipse([cx - r * 0.35, cy - r, cx + r * 0.35, cy + r], outline=col, width=4)
    d.line([(cx - r * 0.8, cy + r * 0.6), (cx + r * 0.8, cy - r * 0.6)], fill=col, width=3)
    d.rectangle([cx - 6, cy + r, cx + 6, cy + r + 24], fill=(110, 80, 50))
    d.rectangle([cx - 36, cy + r + 20, cx + 36, cy + r + 28], fill=(110, 80, 50))


def _karakuri(d, cx, by, s=1.0):
    """からくり人形（茶運び人形ふう）。by は台の底。"""
    d.rectangle([cx - 40 * s, by - 18 * s, cx + 40 * s, by], fill=(140, 40, 40))
    d.polygon([(cx - 26 * s, by - 18 * s), (cx + 26 * s, by - 18 * s), (cx + 18 * s, by - 88 * s),
               (cx - 18 * s, by - 88 * s)], fill=(200, 64, 60))
    d.ellipse([cx - 20 * s, by - 136 * s, cx + 20 * s, by - 104 * s], fill=(30, 26, 24))
    d.ellipse([cx - 17 * s, by - 124 * s, cx + 17 * s, by - 88 * s], fill=(246, 236, 220))
    d.rectangle([cx - 4 * s, by - 72 * s, cx + 30 * s, by - 62 * s], fill=(200, 64, 60))
    d.ellipse([cx + 20 * s, by - 80 * s, cx + 44 * s, by - 62 * s], fill=(240, 240, 232))


def _telescope(d, x, y, s=1.0):
    """三脚の望遠鏡（x, y は三脚の頂点）。"""
    for dx in (-60, 0, 60):
        d.line([(x, y), (x + dx * s, y + 250 * s)], fill=(90, 64, 40), width=max(3, int(8 * s)))
    d.line([(x - 90 * s, y + 40 * s), (x + 110 * s, y - 70 * s)], fill=(184, 152, 82), width=max(6, int(30 * s)))
    d.line([(x + 110 * s, y - 70 * s), (x + 140 * s, y - 86 * s)], fill=(140, 110, 60), width=max(8, int(38 * s)))


def nagasaki():
    """明治初めの長崎の時計工房。窓の外に港と帆船、壁に柱時計、作業台に歯車。"""
    img = base((196, 176, 150), (170, 150, 126))
    wood_floor(img, FLOOR, col=(120, 90, 64), line=(100, 74, 52))
    d = _d(img)
    for x in range(0, W, 120):                                              # 板壁
        d.line([(x, 0), (x, FLOOR)], fill=(180, 160, 134), width=3)
    sx0, sy0, sx1, sy1 = 720, 110, 1200, 420                                 # 窓の外の港
    d.rectangle([sx0, sy0, sx1, sy1], fill=(176, 206, 230))
    d.rectangle([sx0, 300, sx1, sy1], fill=(70, 120, 160))
    d.polygon([(sx0, 300), (820, 250), (940, 280), (sx0 + 300, 300)], fill=(96, 130, 96))
    d.polygon([(980, 330), (1120, 330), (1100, 352), (1000, 352)], fill=(90, 64, 44))   # 帆船
    d.line([(1050, 330), (1050, 230)], fill=(90, 64, 44), width=4)
    d.polygon([(1052, 236), (1052, 320), (1110, 320)], fill=(246, 244, 236))
    d.polygon([(1048, 246), (1048, 320), (1000, 320)], fill=(236, 234, 226))
    d.rectangle([sx0, sy0, sx1, sy1], outline=(90, 66, 46), width=10)
    d.line([((sx0 + sx1) // 2, sy0), ((sx0 + sx1) // 2, sy1)], fill=(90, 66, 46), width=8)
    _wall_clock(d, 200, 200, 0.8)
    _wall_clock(d, 1700, 200, 0.8)
    _bench(d, 700, 1220, 640, col=(140, 104, 70))
    for k, (gx, r) in enumerate(((780, 26), (840, 18), (900, 34), (1110, 22))):
        _gear(d, gx, 618 + (k % 2) * 4, r)
    d.ellipse([960, 560, 1060, 640], fill=(240, 232, 210), outline=(110, 70, 40), width=5)   # 中を開けた時計
    _gear(d, 1010, 600, 20, col=(220, 190, 100))
    d.rectangle([1150, 520, 1162, 640], fill=(110, 110, 118))                # 拡大鏡のスタンド
    d.ellipse([1120, 490, 1192, 540], outline=(140, 140, 150), width=6)
    return img


def osaka():
    """大阪の医療器械の店。のれん、器械を並べたガラスの棚、帳場の台。"""
    img = base((222, 208, 182), (196, 180, 154))
    wood_floor(img, FLOOR, col=(126, 94, 64), line=(104, 78, 52))
    d = _d(img)
    d.rectangle([0, 90, W, 230], fill=(46, 62, 92))                           # のれん（文字なし）
    for x in range(160, W, 240):
        d.line([(x, 90), (x, 230)], fill=(34, 46, 70), width=6)
    d.rectangle([660, 270, 1260, 590], fill=(120, 88, 58))                   # ガラスの棚
    d.rectangle([680, 290, 1240, 570], fill=(206, 222, 226))
    for k in range(2):
        y = 420 + k * 150
        d.rectangle([680, y - 4, 1240, y + 4], fill=(120, 88, 58))
    for k in range(5):                                                       # 器械（はさみ・注射器・鉗子）
        x = 720 + k * 104
        d.line([(x, 330), (x + 40, 400)], fill=(150, 150, 160), width=6)
        d.line([(x + 40, 330), (x, 400)], fill=(150, 150, 160), width=6)
        d.ellipse([x - 12, 392, x + 8, 412], outline=(150, 150, 160), width=4)
        d.rectangle([x + 4, 470, x + 70, 486], fill=(214, 220, 226), outline=(140, 140, 150), width=2)
        d.rectangle([x + 70, 474, x + 90, 482], fill=(150, 150, 160))
        d.line([(x - 6, 478), (x + 4, 478)], fill=(150, 150, 160), width=3)
    d.rectangle([640, 640, 1280, 680], fill=(140, 104, 68))                  # 帳場の台
    d.rectangle([660, 680, 1260, 780], fill=(120, 88, 58))
    d.rectangle([900, 600, 1040, 640], fill=(80, 60, 44))                    # 器械の箱
    d.rectangle([910, 606, 1030, 620], fill=(150, 120, 80))
    return img


# ---------------------------------------------------------------- 浜松
def byoin():
    """明治の浜松病院の院長室。薬の棚、器械を置いた机、窓。"""
    img = base((232, 230, 218), (214, 212, 200))
    _wainscot(d=_d(img), y0=560, y1=FLOOR, col=(150, 162, 150))
    wood_floor(img, FLOOR, col=(126, 96, 68), line=(106, 80, 56))
    d = _d(img)
    _arch_window(d, 340, 120, 560, 520)
    d.rectangle([760, 170, 1160, 540], fill=(120, 88, 58))                   # 薬の棚
    d.rectangle([780, 190, 1140, 520], fill=(206, 222, 226))
    for k in range(3):
        y = 290 + k * 112
        d.rectangle([780, y, 1140, y + 8], fill=(120, 88, 58))
        for j in range(7):
            x = 800 + j * 48
            col = ((120, 70, 50), (60, 110, 80), (230, 230, 220), (70, 90, 140))[(j + k) % 4]
            d.rectangle([x, y - 64, x + 30, y], fill=col)
            d.rectangle([x + 8, y - 76, x + 22, y - 64], fill=(60, 60, 64))
    d.line([(960, 190), (960, 520)], fill=(120, 88, 58), width=8)
    _bench(d, 720, 1200, 620, col=(120, 84, 52), legs=140)
    d.rectangle([800, 560, 840, 620], fill=(60, 60, 66))                     # 顕微鏡
    d.line([(820, 560), (850, 500)], fill=(60, 60, 66), width=14)
    d.rectangle([790, 610, 870, 620], fill=(60, 60, 66))
    d.rectangle([960, 574, 1110, 620], fill=(150, 120, 70), outline=(100, 76, 44), width=3)   # 器械の箱
    d.ellipse([1000, 584, 1030, 610], fill=BRASS)
    d.ellipse([1050, 584, 1080, 610], fill=BRASS)
    return img


def gakko(open_front=False):
    """明治の浜松の小学校の教室。黒板の前にアメリカ製のオルガン。左の戸に錠前。"""
    img = base((206, 184, 150), (186, 164, 130))
    wood_floor(img, FLOOR, col=(132, 100, 70), line=(110, 82, 58))
    d = _d(img)
    for x in range(0, W, 110):                                              # 板壁
        d.line([(x, 0), (x, FLOOR)], fill=(190, 168, 134), width=3)
    d.rectangle([620, 120, 1300, 400], fill=(48, 66, 54), outline=(110, 80, 52), width=14)   # 黒板
    for k in range(5):
        d.line([(660, 170 + k * 16), (1260, 170 + k * 16)], fill=(200, 210, 200), width=2)
    _window(d, 1420, 110, 1860, 470, sky=(190, 212, 230))
    d.rectangle([40, 160, 250, 800], fill=(150, 112, 74), outline=(100, 72, 46), width=8)   # 戸と錠前
    d.rectangle([60, 190, 230, 470], outline=(110, 82, 54), width=4)
    d.rectangle([196, 450, 236, 500], fill=(180, 150, 70))
    d.arc([200, 420, 232, 470], 180, 360, fill=(150, 150, 156), width=6)
    _organ(d, 780, 420, 1.0, open_front=open_front)
    return img


def gakko_bunkai():
    """同じ教室。オルガンの前板を外し、手前の机いっぱいに部品と図面を広げている。"""
    img = gakko(open_front=True)
    d = _d(img)
    d.rectangle([1150, 520, 1190, 800], fill=(150, 98, 60))                  # 外した前板を立てかける
    d.rectangle([700, 700, 1220, 728], fill=(140, 104, 70))                  # 部品を広げた机
    for lx in (716, 1180):
        d.rectangle([lx, 728, lx + 24, 860], fill=(110, 82, 54))
    rnd = random.Random(11)
    for k in range(14):                                                      # リードとネジ
        x = 720 + k * 34 + rnd.randint(-4, 4)
        d.rectangle([x, 676 + rnd.randint(-6, 6), x + 10, 700], fill=BRASS)
    for k in range(10):
        x, y = 740 + rnd.randint(0, 440), 690 + rnd.randint(-4, 4)
        d.ellipse([x, y, x + 8, y + 8], fill=(120, 120, 126))
    for k, x in enumerate((900, 1000)):                                      # 折れたバネ2本
        pts = [(x + j * 10, 690 if j % 2 == 0 else 674) for j in range(7)]
        d.line(pts, fill=(200, 60, 50), width=4)
    _zumen(d, 1060, 700, n=4, w=120)
    for k in range(3):                                                       # 床に落ちた図面
        d.polygon([(760 + k * 140, 800), (880 + k * 140, 790), (890 + k * 140, 860), (770 + k * 140, 870)], fill=PAPER)
        d.line([(780 + k * 140, 820), (860 + k * 140, 812)], fill=(60, 90, 150), width=2)
    return img


def _kawai_room(img, night=False, full=True):
    d = _d(img)
    for x in (560, 1360):                                                   # 柱
        d.rectangle([x, 0, x + 40, FLOOR], fill=(110, 80, 52))
    d.rectangle([0, 96, W, 112], fill=(110, 80, 52))                        # 長押
    d.rectangle([600, 150, 1360, 166], fill=(110, 80, 52))                  # 上の棚
    if full:
        for k, x in enumerate(range(640, 1320, 110)):                        # 鍋や器
            if k % 2:
                d.chord([x, 104, x + 80, 156], 0, 180, fill=(60, 60, 66))
                d.rectangle([x - 6, 126, x + 86, 132], fill=(60, 60, 66))
            else:
                d.rectangle([x + 10, 112, x + 70, 150], fill=(200, 180, 140), outline=(140, 120, 90), width=3)
    _tool_rack(d, 30, 150, 300, 420, full=True)
    if full:
        _tansu(d, 1690, 330, 1900, FLOOR - 6)
        d.line([(1700, 150), (1900, 150)], fill=(90, 64, 42), width=8)       # 衣紋掛けの着物
        d.polygon([(1712, 156), (1888, 156), (1888, 200), (1850, 200), (1846, 320), (1754, 320), (1750, 200),
                   (1712, 200)], fill=(90, 110, 140))
        d.line([(1800, 156), (1780, 240)], fill=(240, 236, 226), width=6)
    _bench(d, 720, 1240, 660, col=(136, 100, 66), legs=130)
    d.rectangle([1100, 616, 1160, 660], fill=(70, 70, 76))                   # 小さな金床
    d.rectangle([1090, 606, 1170, 620], fill=(90, 90, 96))
    _zumen(d, 960, 660, n=5, w=120)
    _organ(d, 760, 420 if not night else 430, 0.62, wood=(150, 104, 62) if not night else (140, 96, 58))


def kawai():
    """池町の河合喜三郎の家兼仕事場。錺職の道具、上の棚に鍋、右にタンス、作業台と組みかけのオルガン。"""
    img = base((214, 200, 172), (190, 174, 146))
    tatami_floor(img, FLOOR)
    _kawai_room(img)
    return img


def kawai_garan():
    """同じ仕事場から、タンスも鍋も着物も消えた。壁に借用書が並ぶ。"""
    img = base((214, 200, 172), (190, 174, 146))
    tatami_floor(img, FLOOR)
    _kawai_room(img, full=False)
    _garan(_d(img))
    return img


def _garan(d):
    """家財を売った跡（タンスの跡・空の衣紋掛け）と、壁の借用書。"""
    d.rectangle([1690, 330, 1900, FLOOR - 6], outline=(176, 160, 132), width=4)   # タンスの跡
    d.rectangle([1696, 336, 1894, FLOOR - 12], fill=(222, 210, 184))
    d.line([(1700, 150), (1900, 150)], fill=(90, 64, 42), width=8)
    for k, (x, y) in enumerate(((640, 190), (790, 184), (940, 192), (1090, 186), (1240, 190),
                                (1700, 190), (1460, 196))):                  # 借用書
        d.rectangle([x, y, x + 110, y + 80], fill=PAPER, outline=(170, 160, 140), width=2)
        _text_c(d, x + 55, y + 8, "借用書", 26, (60, 50, 44))
        for j in range(3):
            d.line([(x + 14, y + 46 + j * 10), (x + 96, y + 46 + j * 10)], fill=(150, 140, 130), width=2)
        d.ellipse([x + 80, y + 54, x + 100, y + 74], outline=(200, 60, 50), width=3)


def kawai_yoru():
    """家財を売った後の仕事場の夜。ランプの明かりで、2台目を組み上げている。"""
    img = base((150, 138, 120), (120, 110, 96))
    tatami_floor(img, FLOOR)
    _kawai_room(img, night=True, full=False)
    _garan(_d(img))
    img = _tint(img, (20, 26, 60), 110)
    d = _d(img)
    d.rectangle([1440, 180, 1640, 330], fill=(24, 30, 60), outline=(90, 64, 42), width=8)   # 夜の小窓
    d.ellipse([1570, 200, 1620, 250], fill=(240, 236, 200))
    _onsa(d, 1180, 660, 0.6)
    _lamp(img, 1010, 660, 0.9)
    return img


def shihan():
    """静岡の師範学校の講堂。縦長の窓、壇、真ん中に1台目のオルガン。"""
    img = base((228, 224, 212), (210, 206, 194))
    _wainscot(_d(img), 600, FLOOR, col=(128, 98, 70))
    wood_floor(img, FLOOR, col=(140, 108, 76), line=(118, 90, 62))
    d = _d(img)
    for x in (120, 380, 1420, 1680):
        _arch_window(d, x, 110, x + 160, 520)
    d.rectangle([660, 120, 1260, 240], fill=(120, 90, 62))                   # 講堂の額（文字なし）
    d.rectangle([680, 136, 1240, 224], fill=(236, 228, 206))
    _organ(d, 790, 440, 0.95, wood=(150, 104, 62), simple=False)
    return img


def hakone():
    """箱根の旧街道。杉並木と石畳の上り坂、遠くの山と霧。"""
    img = Image.new("RGBA", (W, H))
    img.paste(vgrad((W, H), (190, 206, 214), (214, 216, 206)), (0, 0))
    d = _d(img)
    d.polygon([(0, 470), (360, 250), (700, 400), (1060, 220), (1460, 380), (1920, 240), (1920, 600), (0, 600)], fill=(140, 160, 150))
    d.polygon([(0, 560), (500, 400), (980, 520), (1400, 420), (1920, 520), (1920, 700), (0, 700)], fill=(104, 128, 104))
    d.rectangle([0, 640, W, H], fill=(112, 120, 92))
    d.polygon([(700, H), (1220, H), (1060, 640), (900, 640)], fill=(150, 146, 132))   # 石畳の道
    rnd = random.Random(5)
    for row in range(8):                                                     # 石畳（大きく淡く）
        y = 650 + row * 54
        t = (y - 640) / (H - 640)
        xl, xr = 900 - 200 * t, 1060 + 160 * t
        x = xl
        while x < xr - 20:
            w = 60 + 50 * t + rnd.randint(-10, 10)
            d.rounded_rectangle([x + 4, y + 4, min(x + w, xr) - 4, y + 46], radius=10, fill=(162, 158, 144))
            x += w
    for x, h in ((140, 520), (330, 600), (520, 560), (1400, 560), (1590, 620), (1790, 540)):
        _sugi(d, x, 700, h)
    img = _smoke(img, 9, 6, 420, 560, col=(244, 246, 244), alpha=70, rmin=120, rmax=200, blur=60)
    return img


def hakone_katsugi():
    """箱根の旧街道で、二人の肩に渡した天秤棒にオルガンを吊るしている（棒の両端はキャラの後ろに隠れる）。"""
    img = hakone()
    d = _d(img)
    x0, y0, x1, y1 = 600, 548, 1320, 604                                    # 天秤棒
    d.line([(x0, y0), (x1, y1)], fill=(96, 66, 40), width=26)
    d.line([(x0, y0 - 6), (x1, y1 - 6)], fill=(170, 126, 80), width=12)

    def pole_y(x):
        return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    ox, oy, sc = 856, 650, 0.58                                              # 吊ったオルガン
    ow = 360 * sc
    for rx, tx in ((ox + 20, ox + 30), (ox + ow - 20, ox + ow - 30)):       # 吊り縄
        d.line([(rx, pole_y(rx) + 8), (tx, oy - 10)], fill=(200, 176, 120), width=7)
    _organ(d, ox, oy, sc)
    for k in range(2):                                                       # 荷を縛った縄
        yy = oy + 120 + k * 120
        d.line([(ox - 6, yy), (ox + ow + 6, yy + 4)], fill=(206, 182, 126), width=8)
    return img


def torishirabe(benkyo=False):
    """東京・上野の音楽取調所の一室。黒板に五線、縦長の窓、真ん中にオルガン、上に音叉。"""
    img = base((226, 222, 208), (208, 204, 190))
    _wainscot(_d(img), 620, FLOOR, col=(116, 86, 60))
    wood_floor(img, FLOOR, col=(130, 98, 68), line=(108, 80, 56))
    d = _d(img)
    for x in (110, 1640):
        _arch_window(d, x, 110, x + 190, 540)
    d.rectangle([640, 90, 1280, 296], fill=(46, 62, 52), outline=(108, 80, 54), width=14)     # 黒板
    for g in (0, 1):
        for k in range(5):
            d.line([(680, 124 + g * 90 + k * 14), (1240, 124 + g * 90 + k * 14)], fill=(214, 220, 210), width=2)
    for k, (nx, g, step) in enumerate(((740, 0, 4), (820, 0, 3), (900, 0, 2), (980, 0, 3), (760, 1, 1), (860, 1, 2), (960, 1, 4))):
        ny = 124 + g * 90 + step * 7
        d.ellipse([nx - 10, ny - 7, nx + 10, ny + 7], fill=(230, 234, 226))
    _organ(d, 700, 430, 0.95)
    _onsa(d, 1010, 432, 0.6)
    return img


# ---------------------------------------------------------------- 工場
def fudaiji(full=False):
    """坂の上の廃寺の庫裏。太い梁、土間、古いかまど、坂を見下ろす窓。full=True は職人と作りかけのオルガンでぎっしり。"""
    img = base((170, 156, 136), (150, 136, 118))
    d = _d(img)
    d.rectangle([0, FLOOR - 40, W, H], fill=(128, 110, 92))                  # 土間
    d.line([(0, FLOOR - 40), (W, FLOOR - 40)], fill=(100, 84, 70), width=6)
    for y in (90, 150):                                                      # 梁
        d.rectangle([0, y, W, y + 34], fill=(78, 56, 38))
    for x in range(-100, W, 380):
        d.line([(x, 0), (x + 220, 124)], fill=(78, 56, 38), width=16)
    for x in (520, 1380):                                                   # 柱
        d.rectangle([x, 124, x + 46, FLOOR - 40], fill=(86, 62, 42))
    for (cx, cy) in ((40, 200), (1880, 200)):                               # 蜘蛛の巣
        for r in (40, 70, 100):
            d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=(220, 216, 206, 120), width=2)
        for a in range(0, 360, 45):
            d.line([(cx, cy), (cx + 100 * math.cos(math.radians(a)), cy + 100 * math.sin(math.radians(a)))],
                   fill=(220, 216, 206, 120), width=2)
    _window(d, 760, 220, 1160, 450, sky=(186, 206, 222), frame=(86, 62, 42))  # 坂の下の町
    d.polygon([(770, 450), (770, 380), (900, 410), (1150, 340), (1150, 450)], fill=(120, 140, 110))
    for k in range(6):
        d.rectangle([800 + k * 56, 400 - (k % 3) * 10, 840 + k * 56, 440], fill=(110, 100, 96))
    _kamado(d, 1790, FLOOR - 40)
    if not full:
        for (x, y) in ((700, 760), (1180, 800), (900, 820)):                # 床の汚れ
            d.ellipse([x, y, x + 120, y + 26], fill=(116, 100, 84))
        return img
    rnd = random.Random(4)
    for k in range(7):                                                       # 並んだオルガンの箱
        x = 600 + k * 108
        d.rectangle([x, 500 - (k % 2) * 20, x + 96, 760], fill=(150, 104, 62), outline=(96, 66, 40), width=3)
        d.rectangle([x + 8, 560 - (k % 2) * 20, x + 88, 584 - (k % 2) * 20], fill=(240, 234, 220))
    for k in range(9):                                                       # 立てかけた板
        d.polygon([(20 + k * 24, FLOOR - 40), (44 + k * 24, FLOOR - 40), (110 + k * 24, 300), (90 + k * 24, 300)],
                  fill=(186, 150, 104) if k % 2 else (170, 134, 92))
    _bench(d, 760, 1160, 780, col=(136, 100, 66), legs=60)
    for k in range(4):
        d.rectangle([790 + k * 90, 750 + rnd.randint(-4, 4), 850 + k * 90, 780], fill=(196, 160, 112))
    _hang_lamp(img, 700, 190, 0.8)
    _hang_lamp(img, 1220, 190, 0.8)
    return img


def _kamado(d, cx, by, col=(156, 126, 104)):
    d.rounded_rectangle([cx - 130, by - 150, cx + 130, by], radius=20, fill=col, outline=(116, 92, 74), width=4)
    for k in (-1, 1):
        d.ellipse([cx + k * 62 - 40, by - 90, cx + k * 62 + 40, by - 24], fill=(40, 32, 28))
        d.ellipse([cx + k * 62 - 50, by - 170, cx + k * 62 + 50, by - 140], fill=(60, 56, 60))


def fudaiji_full():
    return fudaiji(full=True)


def hakurankai():
    """1890年の上野の博覧会場。天井の梁、旗、赤い台にオルガンと、戸棚のようなピアノ。"""
    img = base((232, 226, 212), (214, 206, 190))
    wood_floor(img, FLOOR, col=(150, 120, 88), line=(130, 102, 74))
    d = _d(img)
    _trusses(d)
    _banners(d, range(80, W, 230), 150, 360, ((196, 60, 60), (60, 90, 150), (210, 170, 70), (70, 130, 90)))
    _dais(d, 610, 1300, 748)
    _upright(d, 640, 470, 0.68, col=(132, 92, 56), doors=True)
    _organ(d, 980, 370, 0.8)
    d.ellipse([1094, 250, 1154, 310], fill=(214, 60, 60))                    # オルガンの賞の花飾り
    d.polygon([(1110, 300), (1124, 360), (1138, 300)], fill=(214, 60, 60))
    return img


def hakurankai03():
    """1903年の大阪の博覧会場。金の縁の幕、赤い台に花飾りをつけたグランドピアノ。"""
    img = base((226, 230, 220), (206, 212, 200))
    wood_floor(img, FLOOR, col=(140, 116, 86), line=(120, 98, 70))
    d = _d(img)
    _trusses(d, col=(96, 104, 96))
    for x in range(0, W, 120):                                              # 幕
        d.chord([x, 20, x + 120, 200], 0, 180, fill=(120, 40, 60))
    d.rectangle([0, 20, W, 50], fill=(196, 160, 80))
    _banners(d, (100, 330, 1500, 1730), 210, 420, ((196, 160, 80), (120, 40, 60)))
    _dais(d, 620, 1300, 778, col=(130, 40, 50))
    _grand(d, 700, 460, 0.95)
    d.ellipse([1040, 520, 1100, 580], fill=(214, 60, 60))                    # 花飾り
    d.polygon([(1056, 570), (1070, 630), (1084, 570)], fill=(214, 60, 60))
    for x in (640, 1250):                                                    # 鉢植え
        d.rectangle([x, 690, x + 50, 778], fill=(150, 90, 60))
        d.ellipse([x - 40, 590, x + 90, 710], fill=(80, 130, 80))
    return img


def jimusho():
    """明治の会社の社長室。窓の外に工場の煙突、本棚、柱時計、机の上に音叉。"""
    img = base((214, 196, 166), (194, 176, 146))
    _wainscot(_d(img), 600, FLOOR, col=(110, 80, 54))
    wood_floor(img, FLOOR, col=(120, 88, 60), line=(100, 72, 48))
    d = _d(img)
    _shelf(d, 40, 140, 300, 560)
    _window(d, 1340, 130, 1840, 470, sky=(196, 214, 228))
    d.rectangle([1540, 260, 1580, 470], fill=(120, 96, 80))                  # 工場の煙突と煙
    for k in range(4):
        d.ellipse([1520 + k * 40, 200 - k * 30, 1600 + k * 50, 260 - k * 30], fill=(220, 220, 220))
    d.rectangle([1360, 400, 1820, 470], fill=(150, 120, 96))
    _wall_clock(d, 760, 230, 0.8)
    _bench(d, 700, 1240, 640, col=(110, 74, 46), legs=140)
    _onsa(d, 960, 640, 1.1)
    d.rectangle([1060, 600, 1180, 640], fill=PAPER, outline=(170, 160, 140), width=2)
    d.ellipse([800, 610, 840, 640], fill=(30, 30, 34))                       # 墨壺
    d.line([(830, 610), (860, 560)], fill=(200, 190, 160), width=4)
    return img


def _shelf(d, x0, y0, x1, y1, rows=3, col=(96, 68, 44)):
    d.rectangle([x0, y0, x1, y1], fill=col)
    rh = (y1 - y0) / rows
    pal = ((150, 60, 54), (60, 90, 130), (170, 140, 70), (70, 110, 80), (120, 80, 120))
    for r in range(rows):
        sy = y0 + r * rh
        d.rectangle([x0 + 8, sy + 8, x1 - 8, sy + rh - 4], fill=_dk(col, 0.7))
        x, k = x0 + 14, r
        while x < x1 - 30:
            bw = 18 + (k * 13) % 14
            d.rectangle([x, sy + 20 + (k % 3) * 6, x + bw, sy + rh - 6], fill=pal[k % 5])
            x += bw + 4
            k += 1


def america():
    """1899年のアメリカのピアノ工場。れんがの壁、大きな窓、天井のベルト、並んだピアノの箱。"""
    img = base((170, 104, 84), (150, 92, 74))
    wood_floor(img, FLOOR, col=(120, 100, 84), line=(100, 84, 70))
    d = _d(img)
    for y in range(0, FLOOR, 36):                                            # れんがの目地（淡く）
        d.line([(0, y), (W, y)], fill=(156, 96, 78), width=2)
        off = 0 if (y // 36) % 2 == 0 else 50
        for x in range(off, W, 100):
            d.line([(x, y), (x, y + 36)], fill=(156, 96, 78), width=2)
    for x in (80, 560, 1040, 1520):
        _window(d, x, 110, x + 320, 380, sky=(206, 220, 230), frame=(70, 60, 56))
    d.line([(0, 70), (W, 70)], fill=(60, 60, 66), width=12)                  # 天井の軸とベルト
    for x in (300, 780, 1260, 1740):
        d.ellipse([x - 30, 40, x + 30, 100], fill=(80, 80, 86))
        d.line([(x - 26, 76), (x - 60, 400)], fill=(70, 50, 40), width=6)
        d.line([(x + 26, 76), (x - 20, 400)], fill=(70, 50, 40), width=6)
    for k in range(10):                                                      # 作りかけのピアノの箱
        x = 40 + k * 190
        d.rectangle([x, 470, x + 160, 760], fill=(110, 76, 50), outline=(70, 48, 30), width=4)
        d.rectangle([x + 16, 600, x + 144, 620], fill=(236, 230, 214) if k % 3 else (90, 64, 42))
    _bench(d, 700, 1220, 700, col=(140, 110, 80), legs=120)
    _action(d, 760, 640, n=12, s=0.9)
    return img


def kangeikai():
    """1899年10月、浜松の帰国の歓迎会。金屏風、楽隊のラッパ、提灯、手前の膳。"""
    img = base((206, 188, 160), (186, 168, 140))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([0, 96, W, 112], fill=(110, 80, 52))
    for k in range(6):                                                       # 金屏風（床に立てる）
        x = 660 + k * 100
        d.polygon([(x, 300 + (k % 2) * 10), (x + 100, 300 + ((k + 1) % 2) * 10),
                   (x + 100, 900 + ((k + 1) % 2) * 10), (x, 900 + (k % 2) * 10)],
                  fill=(222, 186, 92) if k % 2 else (208, 172, 80))
    for x in (380, 1540):                                                    # 提灯
        d.line([(x, 112), (x, 160)], fill=(60, 50, 40), width=4)
        d.ellipse([x - 50, 160, x + 50, 290], fill=(236, 120, 70))
        for j in range(4):
            d.line([(x - 46, 190 + j * 26), (x + 46, 190 + j * 26)], fill=(200, 90, 50), width=3)
    d.rectangle([700, 640, 1220, 660], fill=(110, 80, 52))                   # 楽器を置いた台
    for lx in (716, 1190):
        d.rectangle([lx, 660, lx + 14, 760], fill=(90, 64, 42))
    for k, x in enumerate((740, 880)):                                       # 楽隊のラッパ
        d.line([(x, 636), (x + 70, 516)], fill=(150, 110, 30), width=18)
        d.line([(x, 636), (x + 70, 516)], fill=(236, 196, 80), width=10)
        d.polygon([(x + 56, 516), (x + 110, 482), (x + 96, 546)], fill=(236, 196, 80), outline=(150, 110, 30))
    d.ellipse([1020, 470, 1180, 630], outline=(150, 110, 30), width=24)      # 大きなラッパ
    d.ellipse([1020, 470, 1180, 630], outline=(236, 196, 80), width=14)
    d.rectangle([1088, 620, 1112, 640], fill=(236, 196, 80))
    d.ellipse([1120, 530, 1170, 590], fill=(236, 196, 80))
    for k, x in enumerate((740, 980)):                                       # 冷めた料理の膳
        d.rectangle([x, 820, x + 200, 856], fill=(130, 40, 40))
        d.rectangle([x + 12, 856, x + 36, 900], fill=(96, 30, 30))
        d.rectangle([x + 164, 856, x + 188, 900], fill=(96, 30, 30))
        d.ellipse([x + 14, 786, x + 94, 828], fill=(244, 240, 230), outline=(180, 170, 150), width=2)
        d.ellipse([x + 104, 786, x + 186, 828], fill=(244, 240, 230), outline=(180, 170, 150), width=2)
        d.ellipse([x + 28, 794, x + 80, 818], fill=(206, 146, 80))
        d.ellipse([x + 118, 794, x + 172, 818], fill=(120, 150, 90))
    return img


def _kojo_base(img, night=False):
    d = _d(img)
    for k in range(6):                                                       # 天窓
        x = 60 + k * 320
        d.rectangle([x, 20, x + 220, 90], fill=(206, 216, 224) if not night else (30, 36, 64))
        d.rectangle([x, 20, x + 220, 90], outline=(90, 70, 50), width=6)
    d.line([(0, 140), (W, 140)], fill=(70, 66, 66), width=12)                # 天井の軸とベルト
    for x in (420, 980, 1540):
        d.ellipse([x - 30, 110, x + 30, 170], fill=(84, 82, 86))
        d.line([(x - 24, 150), (x - 60, 380)], fill=(80, 60, 44), width=6)
        d.line([(x + 24, 150), (x - 20, 380)], fill=(80, 60, 44), width=6)
    for x in (20, 790, 970, 1730):                                           # 並んだオルガンの箱（キャラの後ろは空ける）
        d.rectangle([x, 430, x + 170, 720], fill=(150, 104, 62), outline=(96, 66, 40), width=4)
        d.rectangle([x + 14, 500, x + 156, 524], fill=(240, 234, 220))
        d.rectangle([x + 30, 580, x + 140, 690], fill=(170, 124, 80))


def kojo():
    """1890年代から1900年代の浜松の工場。天窓、天井のベルト、並んだオルガン、作業台。"""
    img = base((196, 176, 146), (176, 156, 128))
    wood_floor(img, FLOOR, col=(130, 104, 76), line=(110, 88, 64))
    _kojo_base(img)
    d = _d(img)
    _bench(d, 740, 1180, 650, col=(140, 106, 72), legs=130)
    for k in range(3):
        d.rectangle([780 + k * 120, 610, 870 + k * 120, 650], fill=(196, 160, 112))
    return img


def kojo_kikai():
    """同じ工場の真ん中に、アメリカから届いた穴あけ機械。英語の説明書が貼ってある。"""
    img = base((196, 176, 146), (176, 156, 128))
    wood_floor(img, FLOOR, col=(130, 104, 76), line=(110, 88, 64))
    _kojo_base(img)
    _drill(_d(img), 860, 430, 1.0)
    return img


def kojo_futon():
    """穴あけ機械の横に、布団と枕を持ち込んである。"""
    img = kojo_kikai()
    d = _d(img)
    d.polygon([(690, 850), (1080, 850), (1120, 950), (650, 950)], fill=(222, 228, 238), outline=(150, 160, 184))  # 敷布団
    d.polygon([(800, 836), (1080, 836), (1110, 930), (780, 930)], fill=(186, 70, 70), outline=(130, 44, 44))   # 掛け布団
    for k in range(5):
        d.ellipse([820 + k * 54, 862 + (k % 2) * 26, 846 + k * 54, 886 + (k % 2) * 26], fill=(236, 200, 120))
    d.rounded_rectangle([680, 828, 790, 880], radius=20, fill=(246, 242, 232), outline=(170, 164, 150), width=3)   # 枕
    return img


def kojo_yoru():
    """夜の工場。作業台にランプと、ハンマーが並ぶアクションの部品。"""
    img = base((196, 176, 146), (176, 156, 128))
    wood_floor(img, FLOOR, col=(130, 104, 76), line=(110, 88, 64))
    _kojo_base(img, night=True)
    img = _tint(img, (18, 22, 52), 120)
    d = _d(img)
    _bench(d, 720, 1200, 650, col=(130, 98, 66), legs=130)
    _action(d, 780, 560, n=10, s=1.0)
    _lamp(img, 1120, 650, 0.9)
    return img


def kojo_iwai():
    """褒章の祝い。工場に紅白幕と、祝の札、酒樽。"""
    img = kojo()
    d = _d(img)
    _kohaku(d, 0, W, 240, h=90)
    d.rectangle([690, 350, 850, 430], fill=PAPER, outline=(200, 60, 50), width=5)
    _text_c(d, 770, 358, "祝", 56, (200, 50, 40))
    for x in (1700, 1800):                                                   # 酒樽
        d.rounded_rectangle([x, 760, x + 90, 900], radius=16, fill=(186, 150, 100), outline=(110, 80, 50), width=4)
        d.rectangle([x, 800, x + 90, 812], fill=(60, 50, 40))
        d.rectangle([x, 850, x + 90, 862], fill=(60, 50, 40))
    return img


def kojo_kaji():
    """同じ工場が燃える。奥から炎、天井に黒い煙、全体が赤く照らされる。"""
    img = kojo_iwai()
    img = _tint(img, (200, 60, 20), 70)
    img = _flames(img, 0, W, 760, 420, seed=7)
    img = _smoke(img, 3, 22, -40, 300, col=(50, 44, 42), alpha=200, rmin=70, rmax=130, blur=12)
    glow(img, 960, 600, 900, (255, 120, 40), 60)
    return img


def yakeato():
    """焼け跡。黒く焦げた柱、崩れた梁、灰の地面、真ん中に金庫。"""
    img = Image.new("RGBA", (W, H))
    img.paste(vgrad((W, H), (150, 150, 152), (170, 166, 160)), (0, 0))
    d = _d(img)
    d.rectangle([0, 700, W, H], fill=(70, 66, 64))
    rnd = random.Random(2)
    for k in range(30):                                                      # 灰と炭
        x, y = rnd.randint(0, W), rnd.randint(720, H - 20)
        d.ellipse([x, y, x + rnd.randint(30, 90), y + rnd.randint(8, 18)], fill=(40, 38, 38))
    for x, h in ((440, 300), (560, 420), (1220, 360), (1370, 460), (1520, 260)):
        d.rectangle([x, 700 - h, x + 34, 700], fill=(30, 28, 28))
    d.line([(560, 300), (1000, 640)], fill=(34, 30, 30), width=26)          # 崩れた梁
    d.line([(1380, 260), (1100, 660)], fill=(34, 30, 30), width=22)
    _safe(d, 668, 560, 1.0)
    img = _smoke(img, 6, 6, 60, 360, col=(180, 178, 176), alpha=80, rmin=100, rmax=180, blur=50)
    return img


def kabunushi():
    """1912年の株主総会の会場。幕、白い布の長机、吊りランプ。"""
    img = base((214, 206, 190), (196, 188, 172))
    _wainscot(_d(img), 620, FLOOR, col=(110, 80, 56))
    wood_floor(img, FLOOR, col=(120, 90, 62), line=(100, 74, 50))
    d = _d(img)
    for x in range(0, W, 140):                                              # 幕
        d.chord([x, 60, x + 140, 260], 0, 180, fill=(110, 40, 50))
    d.rectangle([0, 50, W, 80], fill=(196, 160, 80))
    d.rectangle([680, 560, 1240, 600], fill=(246, 244, 238))                 # 長机
    d.rectangle([680, 600, 1240, 720], fill=(236, 232, 224))
    for x in (760, 1110):
        d.rectangle([x, 520, x + 40, 560], fill=(230, 236, 240), outline=(150, 150, 160), width=2)   # 水差し
    for k in range(4):
        d.rectangle([860 + k * 60, 540, 910 + k * 60, 560], fill=PAPER, outline=(170, 160, 140))
    _hang_lamp(img, 700, 280, 0.9)
    _hang_lamp(img, 1220, 280, 0.9)
    return img


def zashiki():
    """晩年の座敷。床の間に掛け軸、開けた障子の先に縁側と庭。"""
    img = base((214, 200, 172), (190, 174, 146))
    tatami_floor(img, FLOOR)
    d = _d(img)
    d.rectangle([0, 96, W, 112], fill=(110, 80, 52))
    d.rectangle([680, 150, 1000, 660], fill=(200, 186, 156), outline=(110, 80, 52), width=10)   # 床の間
    d.rectangle([780, 190, 900, 520], fill=(240, 234, 216), outline=(150, 120, 80), width=4)    # 掛け軸
    d.line([(820, 260), (860, 420)], fill=(70, 66, 60), width=6)
    d.line([(840, 300), (812, 360)], fill=(70, 66, 60), width=4)
    d.rectangle([680, 640, 1000, 660], fill=(96, 70, 46))
    d.ellipse([920, 570, 970, 640], fill=(120, 140, 170))                    # 花瓶
    d.line([(945, 570), (930, 500)], fill=(80, 120, 70), width=4)
    d.ellipse([916, 486, 944, 512], fill=(220, 90, 100))
    d.rectangle([1040, 150, 1880, 700], fill=(150, 190, 140))                # 縁側の先の庭
    d.rectangle([1040, 520, 1880, 700], fill=(126, 160, 110))
    d.ellipse([1300, 330, 1520, 520], fill=(96, 136, 90))
    d.rectangle([1400, 480, 1420, 560], fill=(100, 76, 54))
    d.rectangle([1040, 660, 1880, 700], fill=(150, 116, 80))                 # 縁側の板
    _shoji(d, 1040, 150, 1240, 660)
    _shoji(d, 1700, 150, 1900, 660)
    return img


def zashiki_natsu():
    """同じ座敷の夏の夕方。庭の空が夕焼け、軒に風鈴。"""
    img = zashiki()
    d = _d(img)
    sky = vgrad((660, 300), (236, 170, 110), (240, 210, 160))
    img.paste(sky, (1240, 150))
    d = _d(img)
    d.rectangle([1240, 450, 1700, 700], fill=(110, 136, 96))
    d.ellipse([1300, 330, 1520, 520], fill=(86, 116, 80))
    d.rectangle([1400, 480, 1420, 560], fill=(90, 68, 48))
    d.rectangle([1240, 660, 1700, 700], fill=(150, 116, 80))
    _shoji(d, 1040, 150, 1240, 660)
    _shoji(d, 1700, 150, 1900, 660)
    d.line([(1620, 150), (1620, 196)], fill=(80, 70, 60), width=3)           # 風鈴
    d.chord([1596, 190, 1644, 238], 180, 360, fill=(170, 210, 236), outline=(120, 160, 190))
    d.line([(1620, 214), (1620, 260)], fill=(80, 70, 60), width=2)
    d.rectangle([1610, 260, 1630, 310], fill=(240, 236, 220), outline=(200, 190, 170))
    return _tint(img, (255, 170, 90), 26)


def nakazawa():
    """1916年の中沢町の空き地。広い原っぱ、縄張りの杭、遠くの山。"""
    img = Image.new("RGBA", (W, H))
    img.paste(vgrad((W, H), (170, 200, 228), (220, 226, 220)), (0, 0))
    d = _d(img)
    for cx, cy in ((400, 180), (1300, 140), (1650, 230)):                    # 雲
        for k in range(3):
            d.ellipse([cx - 90 + k * 60, cy - 30, cx + k * 60, cy + 30], fill=(246, 248, 250))
    d.polygon([(0, 520), (400, 420), (800, 500), (1200, 400), (1600, 480), (1920, 430), (1920, 600), (0, 600)], fill=(130, 156, 140))
    d.rectangle([0, 580, W, H], fill=(150, 180, 110))
    rnd = random.Random(8)
    for _ in range(140):                                                     # 草（淡く）
        x, y = rnd.randint(0, W), rnd.randint(600, H)
        d.line([(x, y), (x + rnd.randint(-6, 6), y - rnd.randint(10, 22))], fill=(126, 160, 92), width=3)
    pts = [(640, 640), (1280, 640), (1360, 700), (560, 700)]                 # 縄張り
    for x, y in pts:
        d.rectangle([x - 6, y - 50, x + 6, y], fill=(150, 120, 80))
    for a, b in zip(pts, pts[1:] + pts[:1]):
        d.line([(a[0], a[1] - 40), (b[0], b[1] - 40)], fill=(236, 230, 210), width=3)
    for x in (180, 1760):
        d.rectangle([x - 8, 470, x + 8, 590], fill=(100, 76, 54))
        d.ellipse([x - 70, 380, x + 70, 510], fill=(90, 130, 80))
    return img


# ---------------------------------------------------------------- 解説の章
def ronsou():
    """論争の章の地図。浜松から箱根を越えて東京へ。国府津〜新橋だけ汽車が通っている。キャラの間に収める。"""
    img = Image.new("RGBA", (W, H))
    img.paste(vgrad((W, H), (240, 236, 224), (226, 222, 210)), (0, 0))
    d = _d(img)
    d.rounded_rectangle([540, 100, 1380, 860], radius=20, fill=(250, 248, 240), outline=(170, 160, 140), width=6)
    d.polygon([(540, 700), (700, 680), (900, 700), (1060, 650), (1200, 640), (1380, 560), (1380, 860), (540, 860)], fill=(176, 206, 226))  # 海
    _text_c(d, 960, 130, "浜松から東京へ", 48, INK)
    pts = {"浜松": (690, 640), "箱根": (1030, 520), "国府津": (1150, 590), "新橋": (1260, 330)}
    d.line([pts["浜松"], (800, 600), (920, 566), pts["箱根"], pts["国府津"]], fill=(190, 150, 90), width=10)  # 東海道
    d.polygon([(960, 540), (1030, 420), (1100, 540)], fill=(120, 150, 110))    # 箱根の山
    a, b = pts["国府津"], pts["新橋"]                                          # 汽車の線（白黒）
    d.line([a, b], fill=(40, 40, 44), width=14)
    n = 8
    for k in range(0, n, 2):
        p = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
        q = (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)
        d.line([p, q], fill=(246, 246, 246), width=8)
    for name, (x, y) in pts.items():
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(200, 60, 50), outline=(250, 250, 250), width=3)
    _text_c(d, 690, 668, "浜松", 44, INK)
    _text_c(d, 1030, 352, "箱根", 44, INK)
    _text_c(d, 1150, 618, "国府津", 38, INK)
    _text_c(d, 1260, 262, "新橋", 44, INK)
    _text_c(d, 1145, 410, "汽車", 34, (40, 40, 44))
    _text_c(d, 870, 300, "？", 120, (200, 70, 60))
    return img


def sonogo():
    """その後の章。寺島町の小さな工場、木のプロペラ、赤いオートバイ（実在車種の形は写さない）。"""
    img = Image.new("RGBA", (W, H))
    img.paste(vgrad((W, H), (240, 238, 230), (224, 224, 216)), (0, 0))
    d = _d(img)
    d.rectangle([0, 760, W, H], fill=(206, 200, 188))
    d.rectangle([640, 420, 860, 700], fill=(170, 130, 90), outline=(110, 80, 52), width=5)    # 小さな工場
    d.polygon([(620, 430), (750, 330), (880, 430)], fill=(100, 80, 70))
    d.rectangle([720, 560, 780, 700], fill=(90, 66, 44))
    d.rectangle([660, 470, 720, 520], fill=(206, 220, 230))
    d.rectangle([790, 470, 850, 520], fill=(206, 220, 230))
    _text_c(d, 750, 720, "1927", 44, INK)
    cx, cy = 960, 470                                                        # 木のプロペラ
    d.polygon([(cx - 14, cy), (cx - 26, cy - 190), (cx, cy - 210), (cx + 26, cy - 190), (cx + 14, cy)], fill=(176, 126, 70))
    d.polygon([(cx - 14, cy), (cx - 26, cy + 190), (cx, cy + 210), (cx + 26, cy + 190), (cx + 14, cy)], fill=(176, 126, 70))
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(110, 80, 52))
    _text_c(d, 960, 720, "1921", 44, INK)
    mx, my = 1030, 560                                                       # オートバイ
    for wx in (mx + 30, mx + 230):
        d.ellipse([wx - 50, my + 30, wx + 50, my + 130], outline=(40, 40, 44), width=14)
    d.polygon([(mx + 30, my + 80), (mx + 110, my + 20), (mx + 200, my + 20), (mx + 230, my + 80), (mx + 150, my + 80)], fill=(200, 50, 50))
    d.rectangle([mx + 90, my - 6, mx + 170, my + 20], fill=(30, 30, 34))
    d.line([(mx + 200, my + 20), (mx + 220, my - 30)], fill=(60, 60, 66), width=8)
    d.line([(mx + 200, my - 30), (mx + 250, my - 34)], fill=(60, 60, 66), width=8)
    _text_c(d, 1160, 720, "1955", 44, INK)
    return img


LOCATIONS = {
    "yh_ongakushitsu": ongakushitsu, "yh_gendai": gendai,
    "yh_kishu": kishu, "yh_nagasaki": nagasaki, "yh_osaka": osaka,
    "yh_byoin": byoin, "yh_gakko": gakko, "yh_gakko_bunkai": gakko_bunkai,
    "yh_kawai": kawai, "yh_kawai_garan": kawai_garan, "yh_kawai_yoru": kawai_yoru,
    "yh_shihan": shihan, "yh_hakone_katsugi": hakone_katsugi, "yh_torishirabe": torishirabe,
    "yh_fudaiji": fudaiji, "yh_fudaiji_full": fudaiji_full,
    "yh_hakurankai": hakurankai, "yh_hakurankai03": hakurankai03,
    "yh_jimusho": jimusho, "yh_america": america, "yh_kangeikai": kangeikai,
    "yh_kojo": kojo, "yh_kojo_kikai": kojo_kikai, "yh_kojo_futon": kojo_futon,
    "yh_kojo_yoru": kojo_yoru, "yh_kojo_iwai": kojo_iwai, "yh_kojo_kaji": kojo_kaji,
    "yh_yakeato": yakeato, "yh_kabunushi": kabunushi, "yh_zashiki": zashiki, "yh_zashiki_natsu": zashiki_natsu,
    "yh_nakazawa": nakazawa, "yh_ronsou": ronsou, "yh_sonogo": sonogo,
}

CARDS = ["1851", "1887", "1890", "1897", "1899", "1902", "1903", "1912", "1916"]


def year_card(text: str) -> Image.Image:
    """黒地に年号だけのカード。キャラと同居させない単独シーンで使う。"""
    img = Image.new("RGB", (W, H), (18, 18, 20))
    d = ImageDraw.Draw(img)
    font = _font(150)
    bb = d.textbbox((0, 0), text, font=font)
    d.text(((W - (bb[2] - bb[0])) // 2, (H - (bb[3] - bb[1])) // 2 - 40),
           text, font=font, fill=(238, 234, 226))
    d.line([(W // 2 - 220, H // 2 + 130), (W // 2 + 220, H // 2 + 130)],
           fill=(150, 146, 138), width=4)
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, fn in LOCATIONS.items():
        if only and name not in only:
            continue
        fn().convert("RGB").save(OUT / f"{name}.png")
        print(f"生成完了: {name}.png")
    for y in CARDS:
        if only and f"yh_card_{y}" not in only:
            continue
        year_card(f"{y}年").save(OUT / f"yh_card_{y}.png")
        print(f"生成完了: yh_card_{y}.png")
    print(f"合計 {len(LOCATIONS) + len(CARDS)} 枚")
