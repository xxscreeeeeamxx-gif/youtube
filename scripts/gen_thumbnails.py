#!/usr/bin/env python3
"""凝ったサムネイル生成（絵入り・分割・飾りフォント対応）。

方針（2026-08 ユーザー決定）:
- 絵はタイトルに合ったもの（動画ごとの小物イラスト）を主役にする
- 左右2分割のビフォーアフター構図も使う
- フォントは 源界明朝（崩れ・衝撃）/ 851チカラヅヨク（殴り書き・ツッコミ）/
  ヒラギノW9（極太・基本）を使い分け。ラノベPOP v2 が assets/fonts/ にあれば
  ポップ枠として自動採用

実行: PYTHONPATH=. python3 scripts/gen_thumbnails.py <slug> [...]  # 省略で全部
出力: projects/<slug>/out/thumbnail.png
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps  # noqa: E402

from ytf.config import Config  # noqa: E402
from ytf.assets_gen import sprite_path  # noqa: E402

W, H = 1280, 720
cfg = Config.load()

FONT_DIR = Path("assets/fonts")
FONTS = {
    "w9": "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc",
    "genkai": str(FONT_DIR / "genkai-mincho.ttf"),
    "851": str(FONT_DIR / "851CHIKARA-DZUYOKU_kanaA_004.ttf"),
}
_lanobe = list(FONT_DIR.glob("*[Ll]anobe*")) + list(FONT_DIR.glob("*ラノベ*"))
if _lanobe:
    FONTS["pop"] = str(_lanobe[0])


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONTS.get(kind) or FONTS["w9"]
    if not Path(path).exists():
        path = FONTS["w9"]
    return ImageFont.truetype(path, size)


def _cmap(path: str) -> set:
    """フォントが収録する文字コード集合（欠字フォールバック判定用）。"""
    import struct
    data = Path(path).read_bytes()
    n_tab = struct.unpack(">H", data[4:6])[0]
    off = None
    for i in range(n_tab):
        rec = 12 + i * 16
        if data[rec:rec + 4] == b"cmap":
            off = struct.unpack(">I", data[rec + 8:rec + 12])[0]
            break
    if off is None:
        return set()
    chars: set = set()
    for i in range(struct.unpack(">H", data[off + 2:off + 4])[0]):
        rec = off + 4 + i * 8
        sub = off + struct.unpack(">I", data[rec + 4:rec + 8])[0]
        fmt = struct.unpack(">H", data[sub:sub + 2])[0]
        if fmt == 4:
            seg_x2 = struct.unpack(">H", data[sub + 6:sub + 8])[0]
            seg = seg_x2 // 2
            ends = struct.unpack(">" + "H" * seg, data[sub + 14:sub + 14 + seg_x2])
            sp = sub + 14 + seg_x2 + 2
            starts = struct.unpack(">" + "H" * seg, data[sp:sp + seg_x2])
            for a, b in zip(starts, ends):
                if b != 0xFFFF:
                    chars |= set(range(a, b + 1))
        elif fmt == 12:
            for g in range(struct.unpack(">I", data[sub + 12:sub + 16])[0]):
                pp = sub + 16 + g * 12
                a, b, _ = struct.unpack(">III", data[pp:pp + 12])
                if b - a < 0x10000:
                    chars |= set(range(a, b + 1))
    return chars


_CMAPS: dict = {}


def has_glyphs(kind: str, text: str) -> bool:
    """フォントが全文字を収録しているか（欠字ならW9へ落とす）。"""
    path = FONTS.get(kind)
    if not path or not Path(path).exists():
        return False
    if kind not in _CMAPS:
        try:
            _CMAPS[kind] = _cmap(path)
        except Exception:
            _CMAPS[kind] = set()
    cs = _CMAPS[kind]
    return bool(cs) and all(ord(c) in cs for c in text if not c.isspace())


# ---------------------------------------------------------------- 共通部品

def rays(size, c1, c2, n=28, center=(0.62, 0.42)):
    img = Image.new("RGBA", size, (*c1, 255))
    d = ImageDraw.Draw(img)
    cx, cy = size[0] * center[0], size[1] * center[1]
    R = max(size) * 1.7
    for i in range(n):
        a0 = (i / n) * 2 * math.pi
        a1 = ((i + 0.5) / n) * 2 * math.pi
        if i % 2 == 0:
            d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                       (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=(*c2, 255))
    return img


def vignette(img, strength=110):
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse([-img.width * 0.25, -img.height * 0.25,
               img.width * 1.25, img.height * 1.25], fill=255)
    m = ImageOps.invert(m.filter(ImageFilter.GaussianBlur(120)))
    black = Image.new("RGB", img.size, (0, 0, 0))
    return Image.composite(black, img.convert("RGB"), m.point(lambda v: min(v, strength)))


# フォントは動画のトーンで選ぶ（見た目の派手さで選ばない）:
#   genkai(源界明朝・崩壊) = 不穏・ミステリー・偽造・未解明。発明の成功譚には使わない
#     （「折る刃、世界へ」に使って血しぶき調になった失敗あり）
#   851(チカラヅヨク・殴り書き) = 熱血・挑戦・根性・ツッコミ。開発秘話の主力
#   w9(ヒラギノ極太) = 断定・数字・かっちり見せたい所
# 飾りフォントは字形が繊細なので縁取りを細くする（太いと塊に潰れる）
EDGE_SCALE = {"w9": 1.0, "genkai": 0.5, "851": 0.45, "pop": 0.8}


def big_text(canvas, xy, text, size, fill, edge1, edge2,
             rotate=0, ew1=10, ew2=22, kind="w9"):
    """二重縁取り+落ち影の見出し文字。"""
    k = EDGE_SCALE.get(kind, 1.0)
    ew1, ew2 = max(3, int(ew1 * k)), max(7, int(ew2 * k))
    f = font(kind, size)
    pad = ew2 + 28
    tw = int(f.getlength(text)) + pad * 2
    th = int(size * 1.35) + pad * 2
    layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((pad, pad), text, font=f, fill=edge2, stroke_width=ew2, stroke_fill=edge2)
    d.text((pad, pad), text, font=f, fill=fill, stroke_width=ew1, stroke_fill=edge1)
    if rotate:
        layer = layer.rotate(rotate, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", layer.size, (0, 0, 0, 165)), (0, 0), layer.split()[3])
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), (xy[0] + 8, xy[1] + 12))
    canvas.alpha_composite(layer, xy)


def outline_sprite(sp, width=12, color=(255, 255, 255, 255)):
    a = sp.split()[3]
    big = a.filter(ImageFilter.MaxFilter(width * 2 + 1))
    halo = Image.new("RGBA", sp.size, (0, 0, 0, 0))
    halo.paste(Image.new("RGBA", sp.size, color), (0, 0), big)
    halo.paste(sp, (0, 0), sp)
    return halo


def bust(who="zundamon", emotion="surprised", height=560, crop=0.52):
    sp = Image.open(sprite_path(cfg, who, emotion)).convert("RGBA")
    b = sp.crop((0, 0, sp.width, int(sp.height * crop)))
    scale = height / b.height
    b = b.resize((int(b.width * scale), height), Image.LANCZOS)
    return outline_sprite(b)


def prop_layer(draw_fn, size=620, tilt=-12):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(img), size)
    bb = img.getbbox()          # 描いた範囲だけに切り詰める（余白で小さく見えるのを防ぐ）
    if bb:
        img = img.crop(bb)
    if tilt:
        img = img.rotate(tilt, expand=True, resample=Image.BICUBIC)
    # 白フチ+影で切り抜き感
    img = outline_sprite(img, 8)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", img.size, (0, 0, 0, 140)), (0, 0), img.split()[3])
    base = Image.new("RGBA", (img.width + 30, img.height + 34), (0, 0, 0, 0))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (18, 26))
    base.alpha_composite(img, (0, 0))
    return base


# ---------------------------------------------------------------- 小物イラスト

def p_wristwatch(d, s):
    """腕時計。クオーツの回。文字盤とベルトで一目で時計と分かる形にする。"""
    # ベルト（上下）
    d.rounded_rectangle([s*0.34, s*0.02, s*0.66, s*0.34], radius=int(s*0.05),
                        fill=(72, 64, 58), outline=(40, 34, 30), width=7)
    d.rounded_rectangle([s*0.34, s*0.66, s*0.66, s*0.98], radius=int(s*0.05),
                        fill=(72, 64, 58), outline=(40, 34, 30), width=7)
    for y in (0.10, 0.20, 0.76, 0.86):
        d.line([(s*0.36, s*y), (s*0.64, s*y)], fill=(48, 42, 38), width=5)
    # ケース
    d.ellipse([s*0.16, s*0.20, s*0.84, s*0.80], fill=(226, 200, 118),
              outline=(140, 112, 40), width=9)
    d.ellipse([s*0.23, s*0.27, s*0.77, s*0.73], fill=(248, 248, 244),
              outline=(150, 152, 156), width=6)
    # 目盛り
    import math as _m
    for k in range(12):
        a = _m.radians(k * 30 - 90)
        x0 = s*0.50 + _m.cos(a) * s*0.21
        y0 = s*0.50 + _m.sin(a) * s*0.21
        x1 = s*0.50 + _m.cos(a) * s*0.245
        y1 = s*0.50 + _m.sin(a) * s*0.245
        d.line([(x0, y0), (x1, y1)], fill=(60, 64, 78), width=6 if k % 3 == 0 else 4)
    # 針（10時10分）
    d.line([(s*0.50, s*0.50), (s*0.50 - s*0.13, s*0.50 - s*0.10)],
           fill=(40, 44, 56), width=9)
    d.line([(s*0.50, s*0.50), (s*0.50 + s*0.15, s*0.50 - s*0.12)],
           fill=(40, 44, 56), width=7)
    d.line([(s*0.50, s*0.50), (s*0.50 + s*0.06, s*0.50 + s*0.18)],
           fill=(210, 70, 60), width=5)
    d.ellipse([s*0.47, s*0.47, s*0.53, s*0.53], fill=(40, 44, 56))
    # リューズ
    d.rounded_rectangle([s*0.84, s*0.45, s*0.92, s*0.55], radius=6,
                        fill=(200, 176, 100), outline=(130, 104, 36), width=5)


def p_mic(d, s):
    """マイク。"""
    d.ellipse([s*0.28, s*0.04, s*0.72, s*0.48], fill=(215, 219, 230), outline=(70, 74, 88), width=10)
    for k in range(5):
        y = s*0.09 + k * s*0.075
        d.line([(s*0.31, y), (s*0.69, y)], fill=(150, 155, 170), width=6)
        d.line([(s*0.40 + (k%2)*0.04*s, s*0.06), (s*0.40 + (k%2)*0.04*s, s*0.46)], fill=(150, 155, 170), width=4)
    d.polygon([(s*0.42, s*0.46), (s*0.58, s*0.46), (s*0.55, s*0.96), (s*0.45, s*0.96)],
              fill=(60, 64, 80), outline=(30, 32, 44))
    d.rectangle([s*0.44, s*0.60, s*0.56, s*0.66], fill=(230, 180, 60))


def p_jukebox(d, s):
    """手作りの8JUKE（箱型のカラオケ機）。"""
    d.rounded_rectangle([s*0.14, s*0.10, s*0.86, s*0.90], radius=18,
                        fill=(58, 62, 78), outline=(150, 156, 172), width=10)
    d.rounded_rectangle([s*0.22, s*0.18, s*0.78, s*0.40], radius=8, fill=(24, 26, 34))
    for k in range(3):
        d.line([(s*0.27, s*0.24 + k*s*0.06), (s*0.73, s*0.24 + k*s*0.06)],
               fill=(90, 200, 150), width=6)
    d.ellipse([s*0.22, s*0.50, s*0.38, s*0.66], fill=(230, 180, 60), outline=(150, 110, 20), width=5)
    d.ellipse([s*0.44, s*0.50, s*0.56, s*0.62], fill=(200, 80, 70), outline=(120, 40, 34), width=5)
    d.rounded_rectangle([s*0.62, s*0.48, s*0.80, s*0.68], radius=6, fill=(36, 38, 48),
                        outline=(150, 156, 172), width=5)
    d.rectangle([s*0.24, s*0.74, s*0.76, s*0.82], fill=(30, 32, 40))
    d.rectangle([s*0.40, s*0.72, s*0.60, s*0.76], fill=(230, 180, 60))


def p_block(d, s):
    """点字ブロック。"""
    d.rounded_rectangle([s*0.08, s*0.08, s*0.92, s*0.92], radius=24,
                        fill=(250, 205, 40), outline=(140, 100, 10), width=12)
    for gy in range(5):
        for gx in range(5):
            cx = s*0.18 + gx * s*0.16
            cy = s*0.18 + gy * s*0.16
            d.ellipse([cx-s*0.05, cy-s*0.05, cx+s*0.05, cy+s*0.05],
                      fill=(255, 228, 110), outline=(170, 125, 15), width=6)


def p_fiber(d, s):
    """光ファイバー。束ねた糸が扇状に広がり、先が光っている図。

    実寸168pxで読めることだけを狙う。断面図や外皮を描き込むと小さな暗い塊に
    潰れるので、暗い地の上に「光る線が広がる」形だけを残した。
    枠（0〜s）からはみ出した分は切り落とされるので、先端の光のにじみまで
    含めて全部を内側に収める（はみ出させて短い棒に化けた失敗あり）。
    """
    import math as _m
    ox, oy = s*0.92, s*0.92          # 束の根元（右下）
    r = s*0.78                        # 先端が光のにじみごと枠に収まる長さ
    tips = [(ox + _m.cos(_m.radians(a)) * r, oy + _m.sin(_m.radians(a)) * r)
            for a in (190, 205, 220, 235, 250)]
    for tx, ty in tips:               # ① にじみ
        d.line([ox, oy, tx, ty], fill=(90, 180, 240, 80), width=int(s*0.070))
    for tx, ty in tips:               # ② 糸
        d.line([ox, oy, tx, ty], fill=(120, 200, 245), width=int(s*0.038))
        d.line([ox, oy, tx, ty], fill=(245, 252, 255), width=int(s*0.016))
    # ③ 束ねている根元のスリーブ
    d.polygon([(s*0.74, s*0.99), (s*0.99, s*0.99), (s*0.99, s*0.74), (s*0.80, s*0.83)],
              fill=(24, 38, 68), outline=(165, 195, 230), width=int(s*0.020))
    for tx, ty in tips:               # ④ 先端の光
        for rr, col in ((s*0.100, (110, 195, 255, 90)), (s*0.065, (185, 230, 255, 165)),
                        (s*0.038, (255, 255, 255, 255))):
            d.ellipse([tx-rr, ty-rr, tx+rr, ty+rr], fill=col)


def p_exitsign(d, s):
    """非常口の標識。緑地に白の走る人と扉。

    実寸168pxで「あの緑のやつ」と分かることだけを狙う。JIS・ISOの規格図形なので
    誰でも使えるが、ここは正確な複製ではなく、印象を伝えるための簡略な描き起こし。
    """
    g, ink = (26, 152, 92), (250, 252, 250)
    d.rounded_rectangle([s*0.02, s*0.16, s*0.98, s*0.84], radius=s*0.05, fill=g,
                        outline=(14, 96, 58), width=int(s*0.028))
    cx, cy = s*0.36, s*0.50
    u = s * 0.011                              # 人型の基準寸法
    d.ellipse([cx - 9*u, cy - 30*u, cx + 9*u, cy - 12*u], fill=ink)          # 頭
    d.polygon([(cx - 15*u, cy - 11*u), (cx + 10*u, cy - 15*u),
               (cx + 5*u, cy + 10*u), (cx - 19*u, cy + 6*u)], fill=ink)      # 胴
    d.polygon([(cx + 3*u, cy + 5*u), (cx + 22*u, cy + 27*u),
               (cx + 11*u, cy + 32*u), (cx - 6*u, cy + 14*u)], fill=ink)     # 前脚
    d.polygon([(cx - 17*u, cy + 1*u), (cx - 6*u, cy + 27*u),
               (cx - 19*u, cy + 32*u), (cx - 28*u, cy + 7*u)], fill=ink)     # 後脚
    d.polygon([(cx - 13*u, cy - 12*u), (cx - 30*u, cy - 2*u),
               (cx - 34*u, cy - 12*u), (cx - 17*u, cy - 22*u)], fill=ink)    # 腕
    # 足先の影（これが無いと浮いて見える。本編で語る要点なので必ず描く）
    d.ellipse([cx + 6*u, cy + 31*u, cx + 26*u, cy + 37*u], fill=(150, 210, 175))
    d.ellipse([cx - 24*u, cy + 31*u, cx - 4*u, cy + 37*u], fill=(150, 210, 175))
    # 扉
    d.rectangle([s*0.60, s*0.26, s*0.86, s*0.76], fill=ink)
    d.rectangle([s*0.66, s*0.31, s*0.86, s*0.71], fill=g)
    d.ellipse([s*0.685, s*0.49, s*0.715, s*0.52], fill=ink)


def p_pricetag(d, s):
    """赤い値札と、下がる矢印。価格破壊を1枚で示す。

    数字を描くと実寸168pxで潰れるので、**札の形と矢印の向き**だけで意味を出す。
    札には値段ではなく打ち消し線を1本入れて「元の値段を消した」ことを示す。
    """
    # 値札本体（左に紐穴のある札の形）
    d.polygon([(s*0.10, s*0.30), (s*0.94, s*0.18), (s*0.94, s*0.70), (s*0.10, s*0.58)],
              fill=(214, 46, 40), outline=(120, 16, 14), width=int(s*0.026))
    d.ellipse([s*0.15, s*0.38, s*0.25, s*0.48], fill=(120, 16, 14))
    # 値段に見立てた白い帯を2本
    d.polygon([(s*0.33, s*0.34), (s*0.86, s*0.27), (s*0.86, s*0.37), (s*0.33, s*0.44)],
              fill=(252, 248, 244))
    d.polygon([(s*0.33, s*0.48), (s*0.70, s*0.43), (s*0.70, s*0.53), (s*0.33, s*0.58)],
              fill=(252, 248, 244))
    # 上の帯を打ち消す線（元の値段を消した、の意）
    d.line([s*0.30, s*0.42, s*0.90, s*0.27], fill=(255, 214, 40), width=int(s*0.032))
    # 下がる矢印
    ax = s * 0.60
    d.polygon([(ax - s*0.075, s*0.70), (ax + s*0.075, s*0.70),
               (ax + s*0.075, s*0.84), (ax + s*0.16, s*0.84),
               (ax, s*0.99), (ax - s*0.16, s*0.84), (ax - s*0.075, s*0.84)],
              fill=(255, 214, 40), outline=(150, 110, 10), width=int(s*0.016))


def p_hanafuda(d, s):
    """花札を扇状に広げた図。任天堂が何屋だったかを1枚で示す。

    絵柄を描き込むと実寸168pxで潰れるので、**黒地に赤と白の面**という
    花札の配色だけで見せる。扇に広げると「札」だと分かりやすい。
    """
    import math as _m
    ox, oy = s * 0.52, s * 1.02        # 扇の要（下側）
    for k, ang in enumerate((-58, -37, -16, 5, 26)):
        a = _m.radians(ang - 90)
        cx = ox + _m.cos(a) * s * 0.30
        cy = oy + _m.sin(a) * s * 0.30
        w, h = s * 0.235, s * 0.40
        # 札（回転は角で近似せず、少しずつずらした矩形で扇に見せる）
        sh = s * 0.055 * k - s * 0.11
        d.rounded_rectangle([cx - w / 2 + sh, cy - h / 2, cx + w / 2 + sh, cy + h / 2],
                            radius=s * 0.028, fill=(26, 24, 26),
                            outline=(232, 228, 220), width=int(s * 0.016))
        # 中の図柄は面だけ
        col = [(206, 46, 40), (232, 216, 96), (206, 46, 40),
               (86, 152, 96), (232, 216, 96)][k]
        d.rounded_rectangle([cx - w / 2 + sh + s * 0.045, cy - h / 2 + s * 0.055,
                             cx + w / 2 + sh - s * 0.045, cy - s * 0.02],
                            radius=s * 0.018, fill=col)
        d.ellipse([cx - s * 0.035 + sh, cy + s * 0.05,
                   cx + s * 0.035 + sh, cy + s * 0.12], fill=(232, 228, 220))


def p_beefpack(d, s):
    """牛肉のトレーパック。ダイエー回の「牛肉100円→39円」。

    最初は値札（p_pricetag）を置いたが、実寸だと赤い旗にしか見えなかった。
    小物は「形だけで何か分かる」ものにする。抽象的な記号は縮めると意味を失う。
    """
    cx, cy = s * 0.5, s * 0.5
    w, h = s * 0.78, s * 0.50
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    # 発泡トレー（下の厚みを先に描いて立体に見せる）
    d.rounded_rectangle([x0, y0 + h * 0.10, x1, y1 + h * 0.16], radius=s * 0.04,
                        fill=(206, 206, 210))
    d.rounded_rectangle([x0, y0, x1, y1], radius=s * 0.04,
                        fill=(244, 244, 246), outline=(120, 120, 126), width=int(s * 0.008))
    # 牛肉のスライス（縁を濃く・中を明るくして霜降りに見せる）
    import random as _r
    rnd = _r.Random(7)
    for i in range(6):
        px = x0 + w * (0.14 + 0.145 * i)
        py = cy + (h * 0.06 if i % 2 else -h * 0.05)
        rw, rh = w * 0.19, h * 0.52
        d.ellipse([px - rw / 2, py - rh / 2, px + rw / 2, py + rh / 2],
                  fill=(176, 34, 44), outline=(120, 18, 28), width=int(s * 0.008))
        for _ in range(5):                       # 霜降り
            mx = px + rnd.uniform(-rw * 0.28, rw * 0.28)
            my = py + rnd.uniform(-rh * 0.30, rh * 0.30)
            d.ellipse([mx - s * 0.012, my - s * 0.006,
                       mx + s * 0.012, my + s * 0.006], fill=(238, 214, 210))
    # ラップの光沢
    d.polygon([(x0 + w * 0.10, y1), (x0 + w * 0.30, y1),
               (x0 + w * 0.58, y0), (x0 + w * 0.38, y0)], fill=(255, 255, 255, 70))
    # 値札シール
    sw, sh = s * 0.26, s * 0.14
    sx, sy = x1 - sw * 0.82, y1 - sh * 0.30
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=s * 0.02,
                        fill=(255, 222, 40), outline=(60, 44, 8), width=int(s * 0.008))
    d.line([sx + sw * 0.14, sy + sh * 0.36, sx + sw * 0.86, sy + sh * 0.36],
           fill=(60, 44, 8), width=int(s * 0.014))
    d.line([sx + sw * 0.14, sy + sh * 0.66, sx + sw * 0.62, sy + sh * 0.66],
           fill=(60, 44, 8), width=int(s * 0.014))


def p_sukiyaki(d, s):
    """すき焼きの鉄鍋。戦場で願ったもの。"""
    d.ellipse([s*0.04, s*0.30, s*0.96, s*0.86], fill=(52, 48, 48),
              outline=(28, 26, 26), width=int(s*0.030))
    d.ellipse([s*0.12, s*0.36, s*0.88, s*0.78], fill=(150, 92, 56))
    for k, (cx, cy, r) in enumerate(((0.30, 0.50, 0.09), (0.52, 0.46, 0.10),
                                     (0.70, 0.54, 0.08), (0.42, 0.62, 0.09),
                                     (0.62, 0.66, 0.07))):
        col = [(206, 118, 96), (236, 200, 120), (206, 118, 96),
               (140, 176, 110), (236, 200, 120)][k]
        d.ellipse([s*(cx-r), s*(cy-r*0.7), s*(cx+r), s*(cy+r*0.7)], fill=col)
    # 湯気
    for k, x in enumerate((0.30, 0.50, 0.70)):
        d.line([s*x, s*0.28, s*(x+0.04), s*0.14, s*(x-0.02), s*0.04],
               fill=(240, 240, 236), width=int(s*0.022), joint="curve")
    # 取っ手
    for sgn in (-1, 1):
        d.ellipse([s*(0.5+sgn*0.52)-s*0.07, s*0.50, s*(0.5+sgn*0.52)+s*0.07, s*0.64],
                  outline=(28, 26, 26), width=int(s*0.030))


def p_downgraph(d, s):
    """右肩下がりのグラフ。転落の図。"""
    d.rounded_rectangle([s*0.04, s*0.06, s*0.96, s*0.94], radius=s*0.04,
                        fill=(248, 246, 242), outline=(60, 58, 62), width=int(s*0.026))
    for k in range(4):
        y = s*0.22 + k*s*0.18
        d.line([s*0.12, y, s*0.90, y], fill=(210, 208, 204), width=int(s*0.012))
    pts = [(s*0.14, s*0.20), (s*0.32, s*0.30), (s*0.50, s*0.28),
           (s*0.66, s*0.56), (s*0.88, s*0.84)]
    d.line(pts, fill=(214, 44, 38), width=int(s*0.055), joint="curve")
    for x, y in pts:
        d.ellipse([x-s*0.035, y-s*0.035, x+s*0.035, y+s*0.035], fill=(214, 44, 38))
    # 下向きの矢
    d.polygon([(s*0.88, s*0.92), (s*0.76, s*0.72), (s*1.00, s*0.72)], fill=(214, 44, 38))


def p_needle(d, s):
    """注射針。先が細く根元が太いメガホン型を、斜めに描く。

    ただの棒に見えないよう、根元のハブ（樹脂の台座）と、先端の斜めの刃口を付ける。
    """
    # ハブ（根元の台座）
    d.polygon([(s*0.70, s*0.22), (s*0.94, s*0.34), (s*0.86, s*0.52), (s*0.62, s*0.40)],
              fill=(120, 200, 236), outline=(40, 110, 150), width=8)
    for k in range(3):
        d.line([s*0.70 + k*s*0.06, s*0.26 + k*s*0.03,
                s*0.62 + k*s*0.06, s*0.42 + k*s*0.03], fill=(70, 160, 200), width=6)
    # 針（根元は太く、先端へ細くなる）
    d.polygon([(s*0.66, s*0.31), (s*0.72, s*0.44), (s*0.16, s*0.80), (s*0.14, s*0.74)],
              fill=(214, 220, 230), outline=(120, 130, 144), width=7)
    # 先端の斜めの刃口
    d.polygon([(s*0.16, s*0.80), (s*0.14, s*0.74), (s*0.05, s*0.86)],
              fill=(160, 170, 184), outline=(110, 120, 134), width=6)
    # 液のしずく
    d.ellipse([s*0.03, s*0.87, s*0.13, s*0.97], fill=(150, 210, 240),
              outline=(70, 150, 200), width=5)
    # 太さを示す補助線（根元と先端）
    d.line([s*0.60, s*0.20, s*0.78, s*0.50], fill=(255, 214, 40), width=6)
    d.line([s*0.10, s*0.66, s*0.22, s*0.84], fill=(255, 214, 40), width=6)


def p_sharppencil(d, s):
    """シャープペンシル。先の金属の筒と出ている芯が要なので、全部を枠の中に収める。

    枠（0〜s）からはみ出した分は切り落とされるため、芯と筆記線まで含めて
    y=0.96s までに納めている。
    """
    ax, ay = s*0.62, s*0.10          # 後端
    bx, by = s*0.34, s*0.74          # 先端（金属の筒の付け根）
    w = s*0.085
    # 軸
    d.polygon([(bx - w, by), (bx + w, by), (ax + w, ay), (ax - w, ay)],
              fill=(40, 96, 168), outline=(18, 52, 100), width=8)
    # グリップのローレット
    for k in range(5):
        t = 0.06 + k * 0.11
        cx, cy = bx + (ax - bx) * t, by + (ay - by) * t
        d.line([cx - w*0.8, cy, cx + w*0.8, cy], fill=(20, 60, 116), width=7)
    # 後端のノック部
    d.polygon([(ax - w, ay), (ax + w, ay), (ax + w*0.8, ay - s*0.07),
               (ax - w*0.8, ay - s*0.07)],
              fill=(212, 216, 224), outline=(120, 128, 142), width=7)
    # 先の金属の筒（この話の核。100年変わっていないところ）
    d.polygon([(bx - w, by), (bx + w, by), (bx + w*0.32, by + s*0.13),
               (bx - w*0.32, by + s*0.13)],
              fill=(214, 220, 230), outline=(110, 118, 132), width=7)
    # 出ている芯
    d.line([bx, by + s*0.13, bx - s*0.015, by + s*0.22], fill=(46, 46, 54), width=12)
    # 書いた線
    d.line([s*0.05, s*0.93, bx - s*0.02, by + s*0.21], fill=(80, 80, 92), width=10)


def p_purikura(d, s):
    """プリクラのシール。顔の代わりに、切り取り線で分かれた小さな枠を並べる。

    機械そのものより「小さいのが何枚も出て、分けて配れる」ほうが題材の核なので、
    シール紙を主役にした。ピンクの縁と切り取り線でプリクラだと分かる。
    """
    # シール台紙
    d.rounded_rectangle([s*0.06, s*0.10, s*0.94, s*0.90], radius=20,
                        fill=(255, 246, 250), outline=(216, 60, 130), width=12)
    # 2×3 の小コマ
    for gy in range(3):
        for gx in range(2):
            x0 = s*0.14 + gx * s*0.42
            y0 = s*0.17 + gy * s*0.245
            x1, y1 = x0 + s*0.30, y0 + s*0.175
            d.rounded_rectangle([x0, y0, x1, y1], radius=8,
                                fill=(250, 214, 232) if (gx + gy) % 2 else (206, 232, 250),
                                outline=(216, 60, 130), width=5)
            # 顔（丸と髪）
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + s*0.012
            r = s*0.048
            d.ellipse([cx-r*1.35, cy-r*1.5, cx+r*1.35, cy-r*0.1], fill=(90, 66, 74))
            d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 228, 206))
            d.ellipse([cx-r*0.42, cy-r*0.2, cx-r*0.16, cy+r*0.1], fill=(60, 46, 50))
            d.ellipse([cx+r*0.16, cy-r*0.2, cx+r*0.42, cy+r*0.1], fill=(60, 46, 50))
    # 切り取り線（縦・横の破線）
    for k in range(1, 3):
        yy = s*0.10 + k * s*0.267
        for xx in range(int(s*0.10), int(s*0.90), int(s*0.05)):
            d.line([xx, yy, xx + s*0.028, yy], fill=(230, 150, 185), width=4)
    for yy in range(int(s*0.13), int(s*0.88), int(s*0.05)):
        d.line([s*0.50, yy, s*0.50, yy + s*0.028], fill=(230, 150, 185), width=4)


def p_bill(d, s):
    """お札。"""
    d.rounded_rectangle([s*0.05, s*0.22, s*0.95, s*0.78], radius=16,
                        fill=(228, 232, 214), outline=(90, 100, 70), width=10)
    d.rounded_rectangle([s*0.10, s*0.27, s*0.90, s*0.73], radius=10,
                        outline=(140, 150, 110), width=4)
    d.ellipse([s*0.36, s*0.32, s*0.64, s*0.68], fill=(240, 243, 228),
              outline=(150, 160, 120), width=4)
    d.ellipse([s*0.43, s*0.40, s*0.57, s*0.60], fill=(200, 208, 170))
    d.text((s*0.13, s*0.30), "10000", font=font("w9", int(s*0.09)), fill=(90, 100, 70))


def p_blade(d, s):
    """カッターナイフ。刃だけだと何か分からないので、黄色い本体ごと描く。"""
    # 本体
    d.polygon([(s*0.06, s*0.78), (s*0.62, s*0.22), (s*0.78, s*0.38), (s*0.22, s*0.94)],
              fill=(240, 196, 40), outline=(140, 106, 10), width=7)
    # スライダー
    d.polygon([(s*0.24, s*0.66), (s*0.36, s*0.54), (s*0.44, s*0.62), (s*0.32, s*0.74)],
              fill=(70, 76, 92), outline=(30, 34, 46), width=5)
    # 刃（本体から突き出す）
    d.polygon([(s*0.62, s*0.22), (s*0.94, s*0.06), (s*0.99, s*0.20), (s*0.72, s*0.32)],
              fill=(216, 222, 234), outline=(90, 96, 110), width=6)
    # 折り線
    for k in range(1, 3):
        t = k / 3
        x0 = s*0.62 + (s*0.32) * t
        y0 = s*0.22 - (s*0.16) * t
        d.line([(x0, y0), (x0 + s*0.05, y0 + s*0.11)], fill=(120, 126, 140), width=6)
    d.line([(s*0.66, s*0.26), (s*0.92, s*0.13)], fill=(255, 255, 255), width=7)


def p_toilet(d, s):
    """ウォシュレット便座+水流。"""
    d.rounded_rectangle([s*0.16, s*0.10, s*0.60, s*0.52], radius=20,
                        fill=(235, 238, 242), outline=(120, 128, 140), width=10)
    d.rounded_rectangle([s*0.10, s*0.48, s*0.90, s*0.72], radius=30,
                        fill=(245, 247, 250), outline=(120, 128, 140), width=10)
    d.rounded_rectangle([s*0.18, s*0.54, s*0.80, s*0.66], radius=24,
                        fill=(222, 228, 236))
    d.rounded_rectangle([s*0.66, s*0.30, s*0.90, s*0.48], radius=10,
                        fill=(70, 140, 220), outline=(40, 80, 140), width=6)
    # 水流
    for k in range(3):
        x = s*0.42 + k * s*0.07
        d.arc([x, s*0.70, x + s*0.16, s*0.95], start=200, end=340,
              fill=(90, 170, 250), width=10)


def p_shinkansen(d, s):
    """新幹線の鼻先。"""
    d.polygon([(s*0.02, s*0.72), (s*0.30, s*0.40), (s*0.62, s*0.30),
               (s*0.98, s*0.30), (s*0.98, s*0.72)],
              fill=(240, 244, 250), outline=(110, 120, 135))
    d.polygon([(s*0.05, s*0.70), (s*0.32, s*0.46), (s*0.60, s*0.38),
               (s*0.98, s*0.38), (s*0.98, s*0.46), (s*0.34, s*0.52), (s*0.10, s*0.72)],
              fill=(60, 110, 200))
    d.ellipse([s*0.44, s*0.32, s*0.60, s*0.40], fill=(40, 46, 60))
    d.rectangle([s*0.02, s*0.72, s*0.98, s*0.80], fill=(90, 98, 112))


def p_kingfisher(d, s):
    """カワセミ。"""
    d.ellipse([s*0.30, s*0.28, s*0.78, s*0.72], fill=(70, 170, 220), outline=(30, 90, 130), width=8)
    d.ellipse([s*0.36, s*0.42, s*0.70, s*0.70], fill=(240, 150, 70))
    d.ellipse([s*0.56, s*0.20, s*0.86, s*0.50], fill=(70, 170, 220), outline=(30, 90, 130), width=8)
    d.polygon([(s*0.82, s*0.30), (s*1.02, s*0.36), (s*0.82, s*0.44)],
              fill=(40, 46, 60), outline=(20, 24, 32))
    d.ellipse([s*0.72, s*0.28, s*0.80, s*0.36], fill=(20, 24, 32))
    d.polygon([(s*0.34, s*0.66), (s*0.20, s*0.86), (s*0.30, s*0.88), (s*0.42, s*0.70)],
              fill=(70, 170, 220), outline=(30, 90, 130))


def p_battery(d, s, pct=80, col=(80, 200, 120)):
    """電池と残量。"""
    d.rounded_rectangle([s*0.16, s*0.14, s*0.84, s*0.90], radius=26,
                        fill=(36, 40, 52), outline=(150, 156, 170), width=12)
    d.rounded_rectangle([s*0.38, s*0.04, s*0.62, s*0.14], radius=8, fill=(150, 156, 170))
    top = s*0.88 - (s*0.68) * pct / 100
    d.rounded_rectangle([s*0.22, top, s*0.78, s*0.86], radius=14, fill=col)
    d.text((s*0.28, s*0.40), f"{pct}", font=font("w9", int(s*0.22)),
           fill=(255, 255, 255), stroke_width=8, stroke_fill=(20, 22, 30))


def p_signal(d, s, active="green"):
    """信号機。"""
    d.rounded_rectangle([s*0.10, s*0.30, s*0.90, s*0.66], radius=30,
                        fill=(50, 54, 66), outline=(24, 26, 34), width=10)
    cols = {"red": (255, 90, 70), "yellow": (255, 210, 70), "green": (60, 220, 140),
            "blue": (70, 150, 255)}
    for i, name in enumerate([("blue" if active == "blue" else "green"), "yellow", "red"]):
        cx = s*0.24 + i * s*0.26
        on = name == active
        c = cols[name] if on else tuple(int(v*0.25) for v in cols[name])
        d.ellipse([cx-s*0.09, s*0.39, cx+s*0.09, s*0.57], fill=c)
        if on:
            d.ellipse([cx-s*0.12, s*0.36, cx+s*0.12, s*0.60],
                      outline=(255, 255, 255), width=6)


def p_cupnoodle(d, s):
    """カップ麺（フタを開けた容器）。"""
    d.polygon([(s*0.24, s*0.30), (s*0.76, s*0.30), (s*0.68, s*0.92), (s*0.32, s*0.92)],
              fill=(245, 240, 232), outline=(120, 110, 100), width=8)
    d.ellipse([s*0.22, s*0.22, s*0.78, s*0.38], fill=(238, 232, 222), outline=(120, 110, 100), width=8)
    d.ellipse([s*0.28, s*0.25, s*0.72, s*0.36], fill=(230, 190, 120))
    d.rectangle([s*0.30, s*0.48, s*0.70, s*0.60], fill=(210, 60, 50))
    d.rectangle([s*0.30, s*0.66, s*0.70, s*0.72], fill=(180, 170, 160))
    # 湯気
    for k, x in enumerate([0.36, 0.50, 0.64]):
        d.arc([s*x-s*0.06, s*0.02, s*x+s*0.06, s*0.22], start=200+k*20, end=340+k*20,
              fill=(235, 238, 245), width=9)


def p_endoscope(d, s):
    """胃カメラ。楕円だと胃に見えないので、J字の胃袋を輪郭で描いて管を差し込む。"""
    import math
    # 胃袋（J字）。上が広く、右下がすぼまる
    body = [(0.20, 0.30), (0.40, 0.26), (0.58, 0.36), (0.66, 0.56), (0.62, 0.76),
            (0.48, 0.90), (0.30, 0.92), (0.14, 0.80), (0.10, 0.58), (0.13, 0.40)]
    d.polygon([(x*s, y*s) for x, y in body], fill=(246, 190, 176),
              outline=(190, 104, 92))
    d.line([(x*s, y*s) for x, y in body] + [(body[0][0]*s, body[0][1]*s)],
           fill=(190, 104, 92), width=9, joint="curve")
    # 幽門側の細い出口（胃らしさ）
    d.line([(s*0.60, s*0.78), (s*0.76, s*0.90)], fill=(190, 104, 92), width=16)
    d.line([(s*0.60, s*0.78), (s*0.76, s*0.90)], fill=(246, 190, 176), width=8)
    # 内側の陰影（ひだ）
    for k in range(3):
        y = s*(0.46 + k*0.13)
        d.arc([s*0.18, y - s*0.06, s*0.56, y + s*0.06], 20, 160,
              fill=(228, 152, 138), width=6)
    # 食道から差し込む管
    d.line([(s*0.96, s*0.02), (s*0.72, s*0.10), (s*0.46, s*0.16), (s*0.36, s*0.38)],
           fill=(56, 62, 78), width=int(s*0.10), joint="curve")
    d.line([(s*0.96, s*0.02), (s*0.72, s*0.10), (s*0.46, s*0.16), (s*0.36, s*0.38)],
           fill=(126, 134, 150), width=int(s*0.035), joint="curve")
    # 先端のレンズと光
    d.ellipse([s*0.26, s*0.34, s*0.46, s*0.54], fill=(226, 231, 242),
              outline=(46, 52, 68), width=7)
    d.ellipse([s*0.30, s*0.38, s*0.42, s*0.50], fill=(80, 200, 245),
              outline=(28, 106, 160), width=5)
    for a in (150, 195, 240):
        rad = math.radians(a)
        d.line([(s*0.36 + math.cos(rad)*s*0.12, s*0.44 + math.sin(rad)*s*0.12),
                (s*0.36 + math.cos(rad)*s*0.26, s*0.44 + math.sin(rad)*s*0.26)],
               fill=(255, 232, 120), width=8)


def p_sushi(d, s):
    """回転寿司（皿に乗ったにぎり）。"""
    d.ellipse([s*0.08, s*0.58, s*0.92, s*0.92], fill=(220, 90, 80), outline=(140, 40, 34), width=8)
    d.ellipse([s*0.18, s*0.62, s*0.82, s*0.86], fill=(240, 130, 118))
    d.rounded_rectangle([s*0.28, s*0.40, s*0.72, s*0.68], radius=18, fill=(250, 248, 244),
                        outline=(190, 184, 174), width=6)
    d.rounded_rectangle([s*0.24, s*0.30, s*0.76, s*0.50], radius=16, fill=(240, 110, 96),
                        outline=(180, 60, 50), width=6)
    for x in (0.34, 0.50, 0.66):
        d.line([(s*x, s*0.33), (s*x, s*0.47)], fill=(255, 180, 170), width=6)


def p_ricecooker(d, s):
    """電気炊飯器。"""
    d.rounded_rectangle([s*0.12, s*0.34, s*0.88, s*0.90], radius=26,
                        fill=(238, 240, 246), outline=(120, 128, 142), width=9)
    d.ellipse([s*0.10, s*0.22, s*0.90, s*0.46], fill=(248, 250, 254), outline=(120, 128, 142), width=9)
    d.rounded_rectangle([s*0.40, s*0.14, s*0.60, s*0.26], radius=8, fill=(150, 156, 172))
    d.rounded_rectangle([s*0.24, s*0.58, s*0.52, s*0.74], radius=8, fill=(40, 44, 56))
    d.ellipse([s*0.62, s*0.60, s*0.76, s*0.74], fill=(240, 90, 70), outline=(255, 255, 255), width=5)
    for k, x in enumerate([0.34, 0.50, 0.66]):
        d.arc([s*x-s*0.06, s*0.00, s*x+s*0.06, s*0.18], start=200+k*20, end=340+k*20,
              fill=(235, 238, 245), width=8)


def p_gameboy(d, s):
    """携帯ゲーム機。"""
    d.rounded_rectangle([s*0.22, s*0.06, s*0.78, s*0.96], radius=22,
                        fill=(198, 200, 190), outline=(110, 112, 106), width=8)
    d.rounded_rectangle([s*0.30, s*0.14, s*0.70, s*0.46], radius=10, fill=(60, 66, 60))
    d.rounded_rectangle([s*0.34, s*0.18, s*0.66, s*0.42], radius=6, fill=(150, 172, 110))
    # 十字キー
    d.rectangle([s*0.30, s*0.62, s*0.44, s*0.68], fill=(50, 52, 58))
    d.rectangle([s*0.34, s*0.58, s*0.40, s*0.72], fill=(50, 52, 58))
    d.ellipse([s*0.56, s*0.60, s*0.66, s*0.70], fill=(170, 60, 90))
    d.ellipse([s*0.66, s*0.55, s*0.76, s*0.65], fill=(170, 60, 90))
    d.rounded_rectangle([s*0.40, s*0.82, s*0.60, s*0.88], radius=4, fill=(90, 94, 102))


def p_umami(d, s):
    """うま味。昆布だけだと海藻に見えるので、卓上びんを主役にして昆布を添える。"""
    # 昆布（背後に2枚）
    d.polygon([(s*0.04, s*0.96), (s*0.14, s*0.30), (s*0.30, s*0.96)],
              fill=(38, 68, 44), outline=(18, 40, 24), width=5)
    d.polygon([(s*0.18, s*0.96), (s*0.30, s*0.40), (s*0.44, s*0.96)],
              fill=(52, 88, 56), outline=(18, 40, 24), width=5)
    # びん本体
    d.rounded_rectangle([s*0.44, s*0.34, s*0.88, s*0.96], radius=int(s*0.08),
                        fill=(250, 252, 255), outline=(120, 130, 150), width=7)
    # ラベル
    d.rounded_rectangle([s*0.48, s*0.52, s*0.84, s*0.80], radius=int(s*0.03),
                        fill=(228, 32, 48), outline=(150, 16, 28), width=5)
    d.line([(s*0.52, s*0.60), (s*0.80, s*0.60)], fill=(255, 255, 255), width=7)
    d.line([(s*0.52, s*0.70), (s*0.74, s*0.70)], fill=(255, 255, 255), width=7)
    # 赤いキャップ
    d.rounded_rectangle([s*0.50, s*0.16, s*0.82, s*0.38], radius=int(s*0.05),
                        fill=(228, 32, 48), outline=(150, 16, 28), width=6)
    for k in range(3):
        cx = s*0.58 + k * s*0.08
        d.ellipse([cx, s*0.24, cx + s*0.035, s*0.275], fill=(150, 16, 28))


def p_usb(d, s):
    """USBメモリ。"""
    d.rounded_rectangle([s*0.30, s*0.30, s*0.70, s*0.94], radius=12,
                        fill=(50, 56, 70), outline=(150, 156, 172), width=8)
    d.rounded_rectangle([s*0.36, s*0.06, s*0.64, s*0.34], radius=6,
                        fill=(200, 206, 220), outline=(110, 116, 132), width=6)
    d.rectangle([s*0.40, s*0.12, s*0.60, s*0.24], fill=(120, 126, 142))
    d.ellipse([s*0.44, s*0.72, s*0.56, s*0.84], fill=(90, 220, 150))
    d.rounded_rectangle([s*0.36, s*0.42, s*0.64, s*0.62], radius=4, fill=(30, 34, 44))


def p_autodoor(d, s):
    """自動ドアとセンサー。"""
    d.rectangle([s*0.06, s*0.10, s*0.94, s*0.20], fill=(90, 96, 110))
    d.rounded_rectangle([s*0.44, s*0.20, s*0.58, s*0.30], radius=4, fill=(40, 44, 56))
    for a in (-30, 0, 30):
        import math
        rad = math.radians(90 + a)
        d.line([(s*0.51, s*0.30), (s*0.51 + math.cos(rad)*s*0.34, s*0.30 + math.sin(rad)*s*0.34)],
               fill=(255, 220, 90), width=7)
    d.rectangle([s*0.08, s*0.22, s*0.44, s*0.96], fill=(190, 220, 235, 200),
                outline=(120, 128, 142), width=8)
    d.rectangle([s*0.58, s*0.22, s*0.94, s*0.96], fill=(190, 220, 235, 200),
                outline=(120, 128, 142), width=8)


def p_gate(d, s):
    """自動改札機。"""
    d.rounded_rectangle([s*0.06, s*0.34, s*0.40, s*0.94], radius=14,
                        fill=(210, 214, 224), outline=(110, 116, 132), width=8)
    d.rounded_rectangle([s*0.60, s*0.34, s*0.94, s*0.94], radius=14,
                        fill=(210, 214, 224), outline=(110, 116, 132), width=8)
    d.rounded_rectangle([s*0.10, s*0.38, s*0.36, s*0.50], radius=8, fill=(60, 160, 220))
    d.rounded_rectangle([s*0.64, s*0.38, s*0.90, s*0.50], radius=8, fill=(60, 160, 220))
    d.rectangle([s*0.40, s*0.62, s*0.60, s*0.70], fill=(90, 200, 140))
    d.rounded_rectangle([s*0.42, s*0.06, s*0.58, s*0.28], radius=4,
                        fill=(250, 248, 240), outline=(150, 150, 160), width=5)


def p_escalator(d, s):
    """エスカレーター。段だけだと階段と区別がつかないので、手すりと側板まで描く。"""
    # 側板（斜めのパネル）
    d.polygon([(s*0.04, s*0.98), (s*0.04, s*0.80), (s*0.96, s*0.24), (s*0.96, s*0.42)],
              fill=(96, 104, 122), outline=(48, 54, 68), width=6)
    # ステップ
    for k in range(5):
        x0 = s*0.10 + k * s*0.165
        y0 = s*0.80 - k * s*0.135
        d.polygon([(x0, y0), (x0 + s*0.20, y0), (x0 + s*0.20, y0 + s*0.13),
                   (x0, y0 + s*0.13)],
                  fill=(214, 220, 232), outline=(90, 96, 112), width=5)
        d.line([(x0 + s*0.02, y0 + s*0.11), (x0 + s*0.18, y0 + s*0.11)],
               fill=(240, 196, 40), width=6)
    # 手すり（太い黒ベルト）
    d.line([(s*0.02, s*0.66), (s*0.98, s*0.10)], fill=(38, 42, 54), width=int(s*0.10))
    d.line([(s*0.02, s*0.64), (s*0.98, s*0.08)], fill=(120, 128, 145), width=int(s*0.03))


def p_qr(d, s):
    """QRコード。"""
    d.rounded_rectangle([s*0.06, s*0.06, s*0.94, s*0.94], radius=10, fill=(255, 255, 255),
                        outline=(40, 44, 56), width=6)
    def finder(x, y):
        u = s*0.20
        d.rectangle([x, y, x+u, y+u], fill=(20, 22, 30))
        d.rectangle([x+u*0.18, y+u*0.18, x+u*0.82, y+u*0.82], fill=(255, 255, 255))
        d.rectangle([x+u*0.34, y+u*0.34, x+u*0.66, y+u*0.66], fill=(20, 22, 30))
    finder(s*0.12, s*0.12); finder(s*0.68, s*0.12); finder(s*0.12, s*0.68)
    import random
    rnd = random.Random(3)
    for gy in range(9):
        for gx in range(9):
            x = s*0.14 + gx*s*0.08
            y = s*0.14 + gy*s*0.08
            if (gx < 3 and gy < 3) or (gx > 5 and gy < 3) or (gx < 3 and gy > 5):
                continue
            if rnd.random() < 0.52:
                d.rectangle([x, y, x+s*0.062, y+s*0.062], fill=(20, 22, 30))


def p_barcode(d, s):
    """バーコード（QRの「ビフォー」。情報量の少なさを絵で見せる）。"""
    d.rounded_rectangle([s*0.06, s*0.22, s*0.94, s*0.80], radius=8, fill=(255, 255, 255),
                        outline=(40, 44, 56), width=6)
    import random
    rnd = random.Random(9)
    x = s*0.13
    while x < s*0.87:
        w = rnd.choice([s*0.012, s*0.02, s*0.032])
        d.rectangle([x, s*0.28, x + w, s*0.64], fill=(20, 22, 30))
        x += w + rnd.choice([s*0.014, s*0.022])
    for k, ch in enumerate("4901234"):
        d.text((s*0.16 + k*s*0.10, s*0.66), ch, font=font("w9", int(s*0.10)),
               fill=(30, 34, 44))


def p_kamado(d, s):
    """かまどと羽釜（炊飯器の「ビフォー」）。"""
    d.polygon([(s*0.12, s*0.94), (s*0.20, s*0.52), (s*0.80, s*0.52), (s*0.88, s*0.94)],
              fill=(96, 74, 60), outline=(56, 42, 34), width=8)
    d.ellipse([s*0.16, s*0.36, s*0.84, s*0.60], fill=(120, 124, 134), outline=(60, 64, 74), width=8)
    d.ellipse([s*0.26, s*0.30, s*0.74, s*0.48], fill=(78, 62, 50), outline=(48, 38, 30), width=7)
    d.rectangle([s*0.34, s*0.68, s*0.66, s*0.92], fill=(30, 24, 20))
    # 炎
    for k, x in enumerate([0.42, 0.50, 0.58]):
        d.polygon([(s*x, s*0.70), (s*(x+0.045), s*0.80), (s*x, s*0.90), (s*(x-0.045), s*0.80)],
                  fill=(250, 150 + k*20, 40))
    for k, x in enumerate([0.30, 0.50, 0.70]):
        d.arc([s*x-s*0.06, s*0.06, s*x+s*0.06, s*0.28], start=200+k*20, end=340+k*20,
              fill=(228, 232, 240), width=8)


def p_chickenramen(d, s):
    """どんぶりのラーメン（カップ麺の「ビフォー」=チキンラーメン）。"""
    d.ellipse([s*0.06, s*0.40, s*0.94, s*0.92], fill=(240, 236, 228),
              outline=(150, 60, 50), width=9)
    d.ellipse([s*0.14, s*0.44, s*0.86, s*0.74], fill=(212, 160, 70))
    for k, x in enumerate([0.28, 0.44, 0.60, 0.74]):
        d.arc([s*x-s*0.08, s*0.46, s*x+s*0.08, s*0.66], start=190, end=350,
              fill=(238, 200, 110), width=7)
    d.ellipse([s*0.30, s*0.50, s*0.44, s*0.60], fill=(250, 248, 240), outline=(200, 190, 170), width=4)
    d.rectangle([s*0.54, s*0.48, s*0.72, s*0.58], fill=(60, 130, 70))
    for k, x in enumerate([0.34, 0.50, 0.66]):
        d.arc([s*x-s*0.06, s*0.06, s*x+s*0.06, s*0.34], start=200+k*20, end=340+k*20,
              fill=(232, 236, 244), width=8)


def p_sushilane(d, s):
    """回転レーン（回転寿司の「アフター」）。"""
    d.polygon([(s*0.02, s*0.72), (s*0.98, s*0.46), (s*0.98, s*0.68), (s*0.02, s*0.94)],
              fill=(70, 76, 92), outline=(40, 44, 56), width=6)
    d.polygon([(s*0.02, s*0.70), (s*0.98, s*0.44), (s*0.98, s*0.50), (s*0.02, s*0.76)],
              fill=(150, 156, 172))
    for k, (x, y) in enumerate([(0.14, 0.66), (0.44, 0.58), (0.74, 0.50)]):
        d.ellipse([s*(x-0.11), s*(y-0.06), s*(x+0.11), s*(y+0.06)],
                  fill=(220, 90, 80), outline=(140, 40, 34), width=5)
        d.rounded_rectangle([s*(x-0.06), s*(y-0.12), s*(x+0.06), s*(y-0.02)], radius=6,
                            fill=(250, 248, 244), outline=(190, 184, 174), width=4)
        d.rounded_rectangle([s*(x-0.07), s*(y-0.16), s*(x+0.07), s*(y-0.08)], radius=5,
                            fill=(240, 110, 96), outline=(180, 60, 50), width=4)


def p_cane(d, s):
    """白杖（点字ブロックの「ビフォー」）。

    小物は prop_layer で傾けて配置するので、路面など水平が前提の要素は描かない。
    杖そのものだけで「白杖」と分かる形にする。
    """
    # 本体（上の握りから下の石突きへ）
    d.line([(s*0.74, s*0.10), (s*0.34, s*0.90)], fill=(250, 252, 255), width=int(s*0.11))
    d.line([(s*0.74, s*0.10), (s*0.34, s*0.90)], fill=(206, 212, 224), width=int(s*0.025))
    # 赤い帯（白杖の識別色）
    d.line([(s*0.60, s*0.38), (s*0.50, s*0.58)], fill=(224, 58, 48), width=int(s*0.115))
    # 握り（上端の曲がり）
    d.arc([s*0.62, s*0.02, s*0.94, s*0.22], start=190, end=350,
          fill=(236, 240, 250), width=int(s*0.075))
    # 石突き（先端の玉）
    d.ellipse([s*0.26, s*0.82, s*0.46, s*1.00], fill=(236, 240, 248),
              outline=(150, 156, 172), width=6)


def p_wetcell(d, s):
    """湿電池（ガラス瓶に液と電極。凍る・こぼれる側）。"""
    d.rounded_rectangle([s*0.18, s*0.24, s*0.82, s*0.92], radius=10,
                        fill=(198, 226, 236, 230), outline=(120, 150, 168), width=8)
    d.rectangle([s*0.20, s*0.52, s*0.80, s*0.90], fill=(150, 196, 214))
    for x in (0.34, 0.62):
        d.rectangle([s*x, s*0.10, s*(x+0.08), s*0.72], fill=(120, 126, 140),
                    outline=(70, 76, 92), width=5)
    d.ellipse([s*0.16, s*0.18, s*0.84, s*0.32], fill=(214, 236, 244),
              outline=(120, 150, 168), width=7)
    # 凍結のひび
    d.line([(s*0.30, s*0.62), (s*0.42, s*0.74), (s*0.36, s*0.86)],
           fill=(255, 255, 255), width=7)
    d.line([(s*0.58, s*0.60), (s*0.68, s*0.78)], fill=(255, 255, 255), width=6)


def p_drycell(d, s):
    """乾電池（筒型・現在の形）。"""
    d.rounded_rectangle([s*0.28, s*0.14, s*0.72, s*0.94], radius=14,
                        fill=(206, 172, 70), outline=(120, 96, 40), width=8)
    d.rounded_rectangle([s*0.42, s*0.04, s*0.58, s*0.16], radius=5,
                        fill=(180, 186, 200), outline=(110, 116, 132), width=5)
    d.rectangle([s*0.28, s*0.40, s*0.72, s*0.56], fill=(46, 42, 36))
    d.rectangle([s*0.28, s*0.82, s*0.72, s*0.94], fill=(160, 166, 180))
    d.text((s*0.38, s*0.60), "＋", font=font("w9", int(s*0.18)), fill=(40, 36, 30))


def p_kyakka(d, s):
    """却下印の押された申請書（フラッシュメモリ回のビフォー）。"""
    d.rounded_rectangle([s*0.14, s*0.06, s*0.86, s*0.94], radius=10,
                        fill=(248, 246, 238), outline=(150, 146, 134), width=7)
    for i, y in enumerate(range(int(s*0.20), int(s*0.80), int(s*0.09))):
        w = 0.60 if i % 3 else 0.44
        d.rectangle([s*0.22, y, s*(0.22+w), y + s*0.028], fill=(176, 178, 186))
    # 却下のスタンプ
    d.rounded_rectangle([s*0.30, s*0.40, s*0.82, s*0.66], radius=8,
                        outline=(206, 44, 52), width=9)
    d.text((s*0.36, s*0.435), "却下", font=font("w9", int(s*0.19)), fill=(206, 44, 52))


def p_phone_mem(d, s):
    """スマホとメモリチップ（アフター）。"""
    d.rounded_rectangle([s*0.24, s*0.04, s*0.76, s*0.80], radius=int(s*0.09),
                        fill=(38, 42, 56), outline=(178, 184, 200), width=8)
    d.rounded_rectangle([s*0.29, s*0.11, s*0.71, s*0.72], radius=int(s*0.04),
                        fill=(96, 170, 220))
    for gy in range(6):
        for gx in range(4):
            x = s*0.32 + gx*s*0.10
            y = s*0.15 + gy*s*0.095
            d.rounded_rectangle([x, y, x+s*0.075, y+s*0.072], radius=6, fill=(232, 240, 250))
    # チップ
    d.rounded_rectangle([s*0.10, s*0.72, s*0.56, s*0.98], radius=8,
                        fill=(28, 30, 40), outline=(150, 156, 172), width=6)
    for k in range(6):
        d.rectangle([s*(0.13+k*0.075), s*0.68, s*(0.155+k*0.075), s*0.74], fill=(200, 176, 90))
        d.rectangle([s*(0.13+k*0.075), s*0.96, s*(0.155+k*0.075), s*1.02], fill=(200, 176, 90))


def p_hasami(d, s):
    """改札鋏と切符（自動改札のビフォー）。"""
    # 切符
    d.rounded_rectangle([s*0.06, s*0.52, s*0.62, s*0.86], radius=6, fill=(244, 240, 226),
                        outline=(160, 152, 132), width=6)
    for y in (s*0.60, s*0.68):
        d.rectangle([s*0.12, y, s*0.46, y + s*0.03], fill=(150, 146, 136))
    # 鋏
    d.line([(s*0.52, s*0.44), (s*0.88, s*0.10)], fill=(150, 156, 170), width=int(s*0.09))
    d.line([(s*0.62, s*0.46), (s*0.96, s*0.20)], fill=(178, 184, 198), width=int(s*0.08))
    d.ellipse([s*0.80, s*0.02, s*0.98, s*0.20], outline=(120, 126, 140), width=int(s*0.05))
    d.ellipse([s*0.88, s*0.16, s*1.04, s*0.32], outline=(120, 126, 140), width=int(s*0.05))
    d.ellipse([s*0.50, s*0.40, s*0.66, s*0.54], fill=(90, 96, 110))


def p_gate_now(d, s):
    """現代の自動改札（タッチ面が光る）。"""
    d.rounded_rectangle([s*0.06, s*0.30, s*0.40, s*0.96], radius=12,
                        fill=(206, 210, 222), outline=(110, 116, 130), width=7)
    d.rounded_rectangle([s*0.60, s*0.30, s*0.94, s*0.96], radius=12,
                        fill=(206, 210, 222), outline=(110, 116, 130), width=7)
    for x in (0.10, 0.64):
        d.rounded_rectangle([s*x, s*0.20, s*(x+0.26), s*0.34], radius=8, fill=(64, 70, 86))
        d.ellipse([s*(x+0.05), s*0.40, s*(x+0.21), s*0.55], fill=(96, 200, 244))
        d.rectangle([s*(x+0.03), s*0.66, s*(x+0.23), s*0.72], fill=(110, 210, 150))
    # 開いた通路（緑の矢印）
    d.polygon([(s*0.44, s*0.62), (s*0.56, s*0.62), (s*0.56, s*0.56), (s*0.62, s*0.68),
               (s*0.56, s*0.80), (s*0.56, s*0.74), (s*0.44, s*0.74)], fill=(90, 220, 150))


# ---------------------------------------------------------------- レイアウト
#
# 調査した定石（stock-sun / LEL-japan 他）を反映:
#  - 文字は全体で20字以内。1行5〜7字、最大2行
#  - 色は3色以内。背景と文字のコントラストを強く取る
#  - ジャンプ率（小フックと大コピーの大小差）を3倍以上つける
#  - 右下25%は再生時間バッジが乗るので文字を置かない
#  - 装飾しすぎない（スマホで潰れる）。縁取りは太い一本+影
#  - タイトルと同じ文言を繰り返さない（一覧で情報が重複して弱くなる）

BADGE_W, BADGE_H = 330, 150   # 右下の再生時間バッジ回避域


def hook_label(canvas, xy, text, size=54, fill=(255, 255, 255, 255),
               bg=(16, 18, 26, 235), kind="w9"):
    """小フック: 帯の中に置いて背景から確実に浮かせる。"""
    f = font(kind, size)
    tw = int(f.getlength(text))
    pad_x, pad_y = 26, 16
    box = Image.new("RGBA", (tw + pad_x * 2, size + pad_y * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    d.rounded_rectangle([0, 0, box.width - 1, box.height - 1], radius=14, fill=bg)
    d.text((pad_x, pad_y - 4), text, font=f, fill=fill)
    sh = Image.new("RGBA", box.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", box.size, (0, 0, 0, 150)), (0, 0), box.split()[3])
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)), (xy[0] + 5, xy[1] + 9))
    canvas.alpha_composite(box, xy)
    return box.width, box.height


def punch_text(canvas, xy, text, size, fill, edge, kind="w9", rotate=-2):
    """大コピー: 太い一本縁+影のみ（二重縁はスマホで潰れる）。"""
    big_text(canvas, xy, text, size, fill, edge, edge,
             rotate=rotate, ew1=max(8, size // 12), ew2=max(8, size // 12), kind=kind)


def layout_hero(spec):
    c1, c2 = spec.get("bg", ((52, 20, 86), (78, 32, 120)))
    img = rays((W, H), c1, c2)
    pr = prop_layer(spec["prop"], tilt=spec.get("tilt", -12))
    scale = spec.get("prop_h", 520) / pr.height
    pr = pr.resize((int(pr.width * scale), int(pr.height * scale)), Image.LANCZOS)
    img.alpha_composite(pr, (int(W * 0.40) - pr.width // 2, int(H * 0.42) - pr.height // 2))
    b = bust("zundamon", spec.get("emotion", "surprised"), 470)
    img.alpha_composite(b, (W - b.width + 40, H - b.height + 70))
    hook_label(img, (34, 34), spec["hook"], spec.get("hook_size", 54))
    size = spec.get("punch_size", 176)
    punch_text(img, (24, H - size - 128), spec["punch"], size,
               spec.get("punch_fill", (255, 226, 40, 255)),
               spec.get("punch_edge", (22, 12, 6, 255)),
               kind=spec.get("punch_font", "w9"))
    return vignette(img, 100)


def layout_split(spec):
    """左右分割のビフォー/アフター。左=問題、右=答え。"""
    img = Image.new("RGBA", (W, H))
    lc = spec.get("left_bg", (34, 38, 56))
    rc1, rc2 = spec.get("right_bg", ((24, 72, 52), (30, 92, 66)))
    img.paste(Image.new("RGBA", (W, H), (*lc, 255)), (0, 0))
    right = rays((W, H), rc1, rc2, n=24, center=(0.75, 0.4))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(W * 0.54, 0), (W, 0), (W, H), (W * 0.44, H)], fill=255)
    img.paste(right, (0, 0), mask)
    ImageDraw.Draw(img).line([(W * 0.54, 0), (W * 0.44, H)], fill=(255, 255, 255), width=12)
    for key, cx in [("prop_l", 0.25), ("prop_r", 0.74)]:
        fn = spec.get(key)
        if not fn:
            continue
        pr = prop_layer(fn, tilt=-8 if key == "prop_l" else 8)
        scale = spec.get("prop_h", 300) / pr.height
        pr = pr.resize((int(pr.width * scale), int(pr.height * scale)), Image.LANCZOS)
        img.alpha_composite(pr, (int(W * cx) - pr.width // 2, int(H * 0.34) - pr.height // 2))
    b = bust("zundamon", spec.get("emotion", "surprised"), 320)
    img.alpha_composite(b, (W - b.width + 56, H - b.height + 26))
    hook_label(img, (30, 30), spec["hook"], spec.get("hook_size", 48))
    ls = spec.get("punch_size", 128)
    punch_text(img, (26, H - ls - 92), spec["left_big"], ls,
               spec.get("left_fill", (255, 96, 86, 255)), (255, 255, 255, 255),
               kind=spec.get("left_font", "w9"), rotate=-2)
    punch_text(img, (int(W * 0.55), H - ls - 150), spec["right_big"], ls,
               spec.get("right_fill", (255, 255, 255, 255)), (16, 30, 22, 255),
               kind=spec.get("right_font", "w9"), rotate=2)
    return vignette(img, 80)


def layout_band(spec):
    """黄色ベタ帯型。実際の人気ゆっくり解説サムネで最も多い構図:
    上=絵、下=黄色帯の中に「状況（黒）＋オチ（赤）」の2行。
    文字が背景から完全に分離するので一覧でも確実に読める。
    """
    c1, c2 = spec.get("bg", ((30, 34, 48), (44, 50, 70)))
    img = rays((W, H), c1, c2, n=22, center=(0.5, 0.34))
    pr = prop_layer(spec["prop"], tilt=spec.get("tilt", -10))
    scale = spec.get("prop_h", 380) / pr.height
    pr = pr.resize((int(pr.width * scale), int(pr.height * scale)), Image.LANCZOS)
    img.alpha_composite(pr, (int(W * 0.32) - pr.width // 2, int(H * 0.30) - pr.height // 2))
    b = bust("zundamon", spec.get("emotion", "surprised"), 400)
    img.alpha_composite(b, (W - b.width + 44, 20))
    # 下部の黄色帯（画面の約4割）
    band_y = int(H * 0.55)
    d = ImageDraw.Draw(img)
    d.rectangle([0, band_y, W, H], fill=(252, 216, 40, 255))
    d.rectangle([0, band_y, W, band_y + 10], fill=(196, 150, 12, 255))
    # 1行目（状況・黒）
    f1 = font(spec.get("line1_font", "w9"), spec.get("line1_size", 84))
    t1 = spec["line1"]
    x1 = max(24, (W - int(f1.getlength(t1))) // 2)
    d.text((x1, band_y + 26), t1, font=f1, fill=(26, 26, 30))
    # 2行目（オチ・赤。末尾の…で引きを作る）
    size2 = spec.get("line2_size", 112)
    kind2 = spec.get("line2_font", "851")
    if not has_glyphs(kind2, spec["line2"]):
        kind2 = "w9"
    f2 = font(kind2, size2)
    t2 = spec["line2"]
    x2 = max(20, (W - int(f2.getlength(t2))) // 2)
    y2 = band_y + 26 + spec.get("line1_size", 84) + 18
    layer = Image.new("RGBA", (W, size2 + 80), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((x2, 10), t2, font=f2, fill=(214, 32, 28),
            stroke_width=max(6, size2 // 16), stroke_fill=(255, 255, 255))
    img.alpha_composite(layer, (0, y2))
    return vignette(img, 60)


def _yellow_tag(canvas, xy, text, size=30, w=None):
    """小さな黄色ラベル（年号・状況の説明）。"""
    f = font("w9", size)
    tw = w or int(f.getlength(text)) + 24
    box = Image.new("RGBA", (tw, size + 18), (250, 214, 32, 255))
    d = ImageDraw.Draw(box)
    d.text((12, 6), text, font=f, fill=(24, 24, 28))
    canvas.alpha_composite(box, xy)
    return box.size


def _arrow(canvas, cx, cy, w=150, h=110, col=(255, 138, 24)):
    """中央のオレンジ矢印（左→右の流れ）。白フチ付き。"""
    lay = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0 = 20, 20
    pts = [(x0, y0 + h * 0.28), (x0 + w * 0.55, y0 + h * 0.28),
           (x0 + w * 0.55, y0), (x0 + w, y0 + h * 0.5),
           (x0 + w * 0.55, y0 + h), (x0 + w * 0.55, y0 + h * 0.72),
           (x0, y0 + h * 0.72)]
    d.polygon(pts, fill=col)
    lay = outline_sprite(lay, 7)
    canvas.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))


def _speech(canvas, xy, text, size=44):
    """白い吹き出し（下部のツッコミ）。"""
    f = font("w9", size)
    tw = int(f.getlength(text))
    bw, bh = tw + 64, size + 44
    lay = Image.new("RGBA", (bw, bh + 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=bh // 2,
                        fill=(255, 255, 255), outline=(20, 20, 26), width=6)
    d.polygon([(bw * 0.36, bh - 4), (bw * 0.5, bh + 20), (bw * 0.52, bh - 4)],
              fill=(255, 255, 255), outline=(20, 20, 26))
    d.text((32, 18), text, font=f, fill=(200, 26, 26))
    canvas.alpha_composite(lay, xy)


def layout_beforeafter(spec):
    """ビフォー→アフター型（実物のゆっくり解説サムネで最も情報量が多い構図）。

    上部に見出し2色、左右パネルに黄色ラベル+絵、中央にオレンジ矢印、
    下部に吹き出しのツッコミ。余白を作らず画面を埋める。
    """
    img = Image.new("RGBA", (W, H), (18, 18, 24, 255))
    lc = spec.get("left_bg", ((26, 30, 44), (38, 44, 62)))
    rc = spec.get("right_bg", ((58, 22, 92), (84, 34, 126)))
    top = 118                      # 見出し帯の高さ
    left = rays((W, H), *lc, n=20, center=(0.25, 0.5))
    right = rays((W, H), *rc, n=20, center=(0.75, 0.5))
    img.paste(left.crop((0, 0, W // 2, H)), (0, 0))
    img.paste(right.crop((W // 2, 0, W, H)), (W // 2, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, top], fill=(16, 16, 22, 255))
    d.line([(W // 2, top), (W // 2, H)], fill=(255, 255, 255), width=10)

    # 上部見出し（左=白 / 右=黄。合わせて一文になる）
    t1, t2 = spec["head_l"], spec["head_r"]
    gap = 22
    size = spec.get("head_size", 78)
    while size > 44:
        f = font("w9", size)
        if int(f.getlength(t1)) + int(f.getlength(t2)) + gap <= W - 40:
            break
        size -= 3
    f = font("w9", size)
    w1, w2 = int(f.getlength(t1)), int(f.getlength(t2))
    x = max(12, (W - (w1 + w2 + gap)) // 2)
    y = (top - size) // 2 - 6
    for t, col, xx in [(t1, (255, 255, 255), x), (t2, (255, 222, 40), x + w1 + gap)]:
        d.text((xx, y), t, font=f, fill=col, stroke_width=8, stroke_fill=(12, 12, 18))

    # 左右パネルの黄色ラベル
    _yellow_tag(img, (16, top + 14), spec["tag_l"], 30)
    _yellow_tag(img, (W // 2 + 16, top + 14), spec["tag_r"], 30)

    # 左右の絵
    for key, cx in [("prop_l", 0.26), ("prop_r", 0.76)]:
        fn = spec.get(key)
        if not fn:
            continue
        pr = prop_layer(fn, tilt=-8 if key == "prop_l" else 8)
        sc = spec.get("prop_h", 300) / pr.height
        pr = pr.resize((int(pr.width * sc), int(pr.height * sc)), Image.LANCZOS)
        img.alpha_composite(pr, (int(W * cx) - pr.width // 2, top + 96))

    # キャラ（各パネル手前・小さめ）
    bl = bust("zundamon", spec.get("emo_l", "sad"), 320)
    img.alpha_composite(bl, (-16, H - bl.height + 22))
    br = bust("tsumugi", spec.get("emo_r", "happy"), 320)
    img.alpha_composite(br, (W - br.width + 16, H - br.height + 22))

    _arrow(img, W // 2, top + 210)
    f2 = font("w9", spec.get("speech_size", 50))
    sw = int(f2.getlength(spec["speech"])) + 64
    _speech(img, ((W - sw) // 2, H - 128), spec["speech"], spec.get("speech_size", 50))
    return vignette(img, 60)


def _dots(size, base, dot, r=9, step=46):
    """ポップなドット背景。"""
    img = Image.new("RGBA", size, (*base, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, size[1] + step, step):
        off = (y // step % 2) * (step // 2)
        for x in range(-step, size[0] + step, step):
            d.ellipse([x + off - r, y - r, x + off + r, y + r], fill=(*dot, 255))
    return img


def text_block(canvas, xy, lines, align="left", max_w=None):
    """見出しを帯付きの塊として置く（プロのサムネの定番）。

    lines: [(文字列, サイズ, 文字色, 帯色 or None)]
    帯を敷くことで背景から完全に分離し、行間の余白も埋まる。
    フォントは原則 w9 一種に統一し、差は「大きさ・色・帯」でつける。
    """
    x, y = xy
    out_w = 0
    for text, size, fill, band in lines:
        f = font("w9", size)
        tw = int(f.getlength(text))
        if max_w:                       # 右のキャラに文字が被らないよう縮める
            while size > 40 and tw + int(size * 0.44) > max_w:
                size -= 3
                f = font("w9", size)
                tw = int(f.getlength(text))
        pad_x, pad_y = int(size * 0.22), int(size * 0.16)
        bw, bh = tw + pad_x * 2, size + pad_y * 2
        lay = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        if band:
            d.rounded_rectangle([0, 0, bw - 1, bh - 1], radius=int(size * 0.12), fill=band)
            d.text((pad_x, pad_y - int(size * 0.06)), text, font=f, fill=fill)
        else:
            d.text((pad_x, pad_y - int(size * 0.06)), text, font=f, fill=fill,
                   stroke_width=max(6, size // 11), stroke_fill=(16, 14, 22))
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", lay.size, (0, 0, 0, 170)), (0, 0), lay.split()[3])
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (x + 7, y + 11))
        canvas.alpha_composite(lay, (x, y))
        y += bh - int(size * 0.06)
        out_w = max(out_w, bw)
    return out_w, y - xy[1]


def stripes(size, base, line, w=26, gap=44):
    """斜めストライプの下地（無地の余白を消す）。"""
    img = Image.new("RGBA", size, (*base, 255))
    d = ImageDraw.Draw(img)
    for x in range(-size[1], size[0] + size[1], gap):
        d.polygon([(x, size[1]), (x + w, size[1]), (x + w + size[1], 0), (x + size[1], 0)],
                  fill=(*line, 255))
    return img


def layout_charbig(spec):
    """キャラ大型。右にキャラを大きく、左に帯付きの見出しの塊。

    ギャラリーで見た「キャラが画面の半分近くを占める」構図。
    表情で感情を伝えられるので、驚き・落胆が主題の回に向く。
    """
    base = spec.get("bg", ((52, 22, 84), (62, 28, 98)))
    prop_box = None
    img = stripes((W, H), base[0], base[1])
    img.alpha_composite(_dots((W, H), (0, 0, 0), base[1], r=5, step=54).point(
        lambda v: v) if False else Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    # キャラ（顔が大きく見えるようバストで切って画面いっぱい）
    sp = Image.open(sprite_path(cfg, spec.get("who", "zundamon"),
                                spec.get("emotion", "surprised"))).convert("RGBA")
    b = sp.crop((0, 0, sp.width, int(sp.height * 0.62)))
    sc = int(H * 1.02) / b.height
    b = outline_sprite(b.resize((int(b.width * sc), int(b.height * sc)), Image.LANCZOS), 14)
    img.alpha_composite(b, (W - b.width + 74, H - b.height + 20))
    # 左の見出し（帯付きの塊。余白を残さない）
    bw, bh = text_block(img, (26, spec.get("text_top", 26)), spec["lines"],
                        max_w=spec.get("text_max_w", int(W * 0.53)))
    # 小物は見出しのすぐ下に大きく置いて左側を埋める
    if spec.get("prop"):
        pr = prop_layer(spec["prop"], tilt=-12)
        avail_h = H - (spec.get("text_top", 26) + bh) - 10
        avail_w = int(W * 0.46)
        psc = min(avail_h / pr.height, avail_w / pr.width)
        pr = pr.resize((max(1, int(pr.width * psc)), max(1, int(pr.height * psc))),
                       Image.LANCZOS)
        px, py = 26, H - pr.height + 4
        img.alpha_composite(pr, (px, py))
        prop_box = (px, py, px + pr.width, py + pr.height)
    # 題材ラベル（何を説明する動画かを一目で示す）。
    # 空きスペースを埋めるよう、入る範囲で最大のサイズまで広げる
    if spec.get("subject"):
        sx, sy = spec.get("subject_at", (228, 556))
        if prop_box:                      # 小物の右端より内側に入らないようにする
            sx = max(sx, prop_box[2] + 18)
        avail_w = spec.get("subject_max_w", int(W * 0.52)) - sx
        avail_h = H - sy - 16
        size = min(spec.get("subject_size", 132), int(avail_h / 1.44))
        while size > 46:
            sf = font("w9", size)
            if int(sf.getlength(spec["subject"])) + int(size * 0.44) <= avail_w:
                break
            size -= 4
        sf = font("w9", size)
        tw = int(sf.getlength(spec["subject"]))
        pad = int(size * 0.22)
        lay = Image.new("RGBA", (tw + pad * 2, int(size * 1.44)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([0, 0, lay.width - 1, lay.height - 1], radius=14,
                             fill=(250, 250, 252, 250))
        ld.text((pad, int(size * 0.14)), spec["subject"], font=sf, fill=(20, 22, 32))
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", lay.size, (0, 0, 0, 150)), (0, 0), lay.split()[3])
        pos = (sx, sy)
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)), (pos[0] + 6, pos[1] + 9))
        img.alpha_composite(lay, pos)
    if spec.get("speech") and not spec.get("subject_big"):
        f2 = font("w9", 44)
        sw = int(f2.getlength(spec["speech"])) + 64
        _speech(img, (min(W - sw - 24, int(W * 0.47)), H - 130), spec["speech"], 44)
    return vignette(img, 70)


def _photo_bg(name, darken=0.42, blur=0):
    """実写を16:9に切り出して暗くする（文字を載せるため）。"""
    src = Path("assets/photos") / name
    im = Image.open(src).convert("RGB")
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x0 = (im.width - W) // 2
    y0 = (im.height - H) // 2
    im = im.crop((x0, y0, x0 + W, y0 + H))
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    im = Image.blend(im, dark, darken)
    return im.convert("RGBA")


def _bolt(canvas, cx, cy, s=90, col=(255, 214, 40, 255)):
    """稲妻マーク（充電の記号）。"""
    lay = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(s * 1.15, 6), (s * 0.55, s * 1.02), (s * 0.98, s * 1.02),
               (s * 0.80, s * 1.94), (s * 1.46, s * 0.86), (s * 1.02, s * 0.86),
               (s * 1.28, 6)], fill=col)
    lay = outline_sprite(lay, 8)
    canvas.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))


def layout_photo(spec):
    """実写背景型。視聴者自身の行動を写真で見せ、損失を文字で言い切る。

    「100%と80%」のような抽象的な数字だけでは何の話か伝わらないので、
    情景（夜の充電）＋損失（寿命が縮む）をセットで出す。
    """
    img = _photo_bg(spec["photo"], spec.get("darken", 0.45), spec.get("blur", 0))
    # 上部の小フック（黒帯）
    hook_label(img, (30, 28), spec["hook"], spec.get("hook_size", 52))
    # 中央〜下の大コピー（帯付きの塊）
    bw, bh = text_block(img, (28, spec.get("text_top", 150)), spec["lines"],
                        max_w=spec.get("text_max_w", int(W * 0.60)))
    # 右上のアクセント: バッジ（バッテリー残量など）か稲妻
    badge = spec.get("badge")
    if badge:
        pr = prop_layer(badge, tilt=spec.get("badge_tilt", 8))
        sc = spec.get("badge_h", 250) / pr.height
        pr = pr.resize((int(pr.width * sc), int(pr.height * sc)), Image.LANCZOS)
        img.alpha_composite(pr, (W - pr.width - 150, 26))
        _bolt(img, W - 152, 96, 58)
    elif spec.get("bolt", True):
        _bolt(img, W - 250, 130, 76)
    b = bust("zundamon", spec.get("emotion", "surprised"), 430)
    img.alpha_composite(b, (W - b.width + 46, H - b.height + 24))
    if spec.get("speech"):
        f2 = font("w9", 44)
        sw = int(f2.getlength(spec["speech"])) + 64
        _speech(img, (min(W - sw - 24, int(W * 0.44)), H - 126), spec["speech"], 44)
    return vignette(img, 90)


def layout_bold(spec):
    """極大文字型。スマホ幅168pxでも読めることだけを狙う。

    クリック率1.5%（2026-08のStudio実測）の原因は、実寸で文字が読めないこと。
    要素を「短い2行の文字」と「大きなキャラ」だけに絞り、小物・ラベル・
    吹き出しは置かない。1行は最大7文字を目安にする。
    """
    base = spec.get("bg", ((150, 26, 40), (96, 14, 26)))
    img = Image.new("RGBA", (W, H), (*base[0], 255))
    d = ImageDraw.Draw(img)
    # 斜めの色面で奥行きを作る（単色だと一覧で沈む）
    d.polygon([(0, H), (0, int(H * 0.42)), (W, int(H * 0.06)), (W, H)], fill=(*base[1], 255))
    # 斜めストライプを全面に薄く敷く（無地だと一覧で「空白」に見える）
    stripe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe)
    for x in range(-H, W + H, 58):
        sd.polygon([(x, H), (x + 22, H), (x + 22 + H, 0), (x + H, 0)],
                   fill=(255, 255, 255, 13))
    img.alpha_composite(stripe)
    d = ImageDraw.Draw(img)
    for i in range(-2, 22):                      # 集中線
        x = int(W * 0.62) + i * 96
        d.polygon([(int(W * 0.62), int(H * 0.5)), (x, -60), (x + 42, -60)],
                  fill=(255, 255, 255, 12))
    # キャラ（顔が大きく出るようバストで切る）
    sp = Image.open(sprite_path(cfg, spec.get("who", "zundamon"),
                                spec.get("emotion", "surprised"))).convert("RGBA")
    b = sp.crop((0, 0, sp.width, int(sp.height * 0.58)))
    sc = int(H * 0.99) / b.height
    b = outline_sprite(b.resize((int(b.width * sc), int(b.height * sc)), Image.LANCZOS), 16)
    char_x = W - b.width + 128
    img.alpha_composite(b, (char_x, H - b.height + 18))
    # 文字（2行・極大）。キャラの実際の左端（不透明部分）の手前までに収める
    bb = b.split()[3].getbbox()                  # 白フチ込みの実体範囲
    char_left = char_x + (bb[0] if bb else 0)
    lines = spec["lines"]
    max_w = min(int(W * 0.70), char_left - 28)

    def _fit(text, base):
        size = base
        while size > 56:
            f = font("w9", size)
            if int(f.getlength(text)) <= max_w:
                return size, f
            size -= 5
        return size, font("w9", size)

    # 行ごとの基準サイズ。4要素目に倍率を持てる（前振りは小さく）
    fits = [_fit(t, int(spec.get("size", 190) * (ln[3] if len(ln) > 3 else 1.0)))
            for t, ln in ((l[0], l) for l in lines)]
    # 3行で画面の縦を使い切るよう、行間を自動で広げる（無地を残さない）
    base_h = sum(fits[i][0] for i in range(len(fits)))
    gap = 1.30
    while gap < 2.2 and sum(int(sz * gap) for sz, _ in fits) < int(H * 0.86):
        gap += 0.04
    block_h = sum(int(sz * gap) for sz, _ in fits) + int(fits[-1][0] * 0.18)
    y = spec.get("text_top") or max(14, (H - block_h) // 2)
    for ln, (size, f) in zip(lines, fits):
        text, color, accent = ln[0], ln[1], ln[2]
        tw = int(f.getlength(text))
        lay = Image.new("RGBA", (tw + 80, int(size * 1.34)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        if accent:                               # 帯付き（強調行）
            ld.rounded_rectangle([0, 0, lay.width - 1, lay.height - 1],
                                 radius=int(size * 0.1), fill=accent)
            ld.text((40, int(size * 0.1)), text, font=f, fill=color)
        else:
            ld.text((40, int(size * 0.1)), text, font=f, fill=color,
                    stroke_width=max(10, size // 12), stroke_fill=(14, 12, 20))
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", lay.size, (0, 0, 0, 190)), (0, 0), lay.split()[3])
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(11)), (28, y + 14))
        img.alpha_composite(lay, (22, y))
        y += int(size * gap)
    return vignette(img, 78)


def layout_face(spec):
    """顔アップ型。クリック率の定石「顔を大きく」に振った版。

    従来の bold 型は顔の面積が画面の7.6%しかなく、定石の25〜40%に届いていない
    （2026-08の実測）。頭部を切り出して大きく置き、文字は左に2〜3行。
    """
    base = spec.get("bg", ((150, 26, 40), (96, 14, 26)))
    img = Image.new("RGBA", (W, H), (*base[0], 255))
    d = ImageDraw.Draw(img)
    d.polygon([(0, H), (0, int(H * 0.46)), (W, int(H * 0.04)), (W, H)], fill=(*base[1], 255))
    stripe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe)
    for x in range(-H, W + H, 58):
        sd.polygon([(x, H), (x + 22, H), (x + 22 + H, 0), (x + H, 0)],
                   fill=(255, 255, 255, 13))
    img.alpha_composite(stripe)
    d = ImageDraw.Draw(img)
    for i in range(-2, 22):
        x = int(W * 0.58) + i * 96
        d.polygon([(int(W * 0.58), int(H * 0.5)), (x, -60), (x + 42, -60)],
                  fill=(255, 255, 255, 14))
    # 頭部だけを切り出して大きく（顔の面積を稼ぐ）
    sp = Image.open(sprite_path(cfg, spec.get("who", "zundamon"),
                                spec.get("emotion", "surprised"))).convert("RGBA")
    head = sp.crop((0, 0, sp.width, int(sp.height * 0.34)))
    hb = head.split()[3].getbbox()
    if hb:
        head = head.crop(hb)
    sc = int(H * 1.02) / head.height
    head = outline_sprite(head.resize((int(head.width * sc), int(head.height * sc)),
                                      Image.LANCZOS), 18)
    char_x = W - head.width + int(head.width * 0.10)
    img.alpha_composite(head, (char_x, H - head.height + 10))
    char_left = char_x + (head.split()[3].getbbox() or (0,))[0]

    lines = spec["lines"]
    max_w = min(int(W * 0.60), char_left - 26)

    def _fit(text, base_size):
        size = base_size
        while size > 56:
            f = font("w9", size)
            if int(f.getlength(text)) <= max_w:
                return size, f
            size -= 5
        return size, font("w9", size)

    fits = [_fit(l[0], int(spec.get("size", 190) * (l[3] if len(l) > 3 else 1.0)))
            for l in lines]
    gap = 1.30
    while gap < 2.2 and sum(int(sz * gap) for sz, _ in fits) < int(H * 0.86):
        gap += 0.04
    block_h = sum(int(sz * gap) for sz, _ in fits) + int(fits[-1][0] * 0.18)
    y = max(14, (H - block_h) // 2)
    for ln, (size, f) in zip(lines, fits):
        text, color, accent = ln[0], ln[1], ln[2]
        tw = int(f.getlength(text))
        lay = Image.new("RGBA", (tw + 80, int(size * 1.34)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        if accent:
            ld.rounded_rectangle([0, 0, lay.width - 1, lay.height - 1],
                                 radius=int(size * 0.1), fill=accent)
            ld.text((40, int(size * 0.1)), text, font=f, fill=color)
        else:
            ld.text((40, int(size * 0.1)), text, font=f, fill=color,
                    stroke_width=max(10, size // 12), stroke_fill=(14, 12, 20))
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", lay.size, (0, 0, 0, 190)), (0, 0), lay.split()[3])
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(11)), (28, y + 14))
        img.alpha_composite(lay, (22, y))
        y += int(size * gap)
    return vignette(img, 78)


def layout_punch(spec):
    """パンチ型。文字は2行まで・顔は右端で見切れるほど大きく。

    bold 型は3行22文字あり、スマホ幅168pxで一瞬に読み切れない。文字を12〜14文字まで
    削ると1行あたりを1.5倍に拡大でき、空いた分だけ顔も大きくできる（顔の面積は
    定石の25〜40%に対し bold 型は7.6%しかなかった・2026-08の実測）。
    """
    base = spec.get("bg", ((150, 26, 40), (96, 14, 26)))
    img = Image.new("RGBA", (W, H), (*base[0], 255))
    d = ImageDraw.Draw(img)
    d.polygon([(0, H), (0, int(H * 0.44)), (W, int(H * 0.05)), (W, H)], fill=(*base[1], 255))
    stripe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe)
    for x in range(-H, W + H, 58):
        sd.polygon([(x, H), (x + 22, H), (x + 22 + H, 0), (x + H, 0)],
                   fill=(255, 255, 255, 13))
    img.alpha_composite(stripe)
    # 顔の後ろに集中線。視線を顔へ集める
    d = ImageDraw.Draw(img)
    cx, cy = int(W * 0.78), int(H * 0.42)
    for i in range(30):
        a = i * (360 / 30)
        import math
        x1 = cx + math.cos(math.radians(a)) * 300
        y1 = cy + math.sin(math.radians(a)) * 300
        x2 = cx + math.cos(math.radians(a + 1.6)) * 1400
        y2 = cy + math.sin(math.radians(a + 1.6)) * 1400
        d.polygon([(cx, cy), (x1, y1), (x2, y2)], fill=(255, 255, 255, 16))

    # 頭部を切り出して大きく。右端で少し見切れさせて迫力を出す
    sp = Image.open(sprite_path(cfg, spec.get("who", "zundamon"),
                                spec.get("emotion", "surprised"))).convert("RGBA")
    head = sp.crop((0, 0, sp.width, int(sp.height * 0.40)))
    hb = head.split()[3].getbbox()
    if hb:
        head = head.crop(hb)
    sc = int(H * 1.06) / head.height
    head = outline_sprite(head.resize((int(head.width * sc), int(head.height * sc)),
                                      Image.LANCZOS), 20)
    char_x = W - int(head.width * 0.80)
    img.alpha_composite(head, (char_x, H - head.height + 6))
    char_left = char_x + (head.split()[3].getbbox() or (0,))[0]

    lines = spec["lines"]
    max_w = min(int(W * 0.62), char_left - 24)

    def _fit(text, base_size):
        size = base_size
        while size > 70:
            f = font("w9", size)
            if int(f.getlength(text)) <= max_w:
                return size, f
            size -= 4
        return size, font("w9", size)

    fits = [_fit(l[0], int(spec.get("size", 240) * (l[3] if len(l) > 3 else 1.0)))
            for l in lines]
    gap = 1.32
    while gap < 2.4 and sum(int(sz * gap) for sz, _ in fits) < int(H * 0.80):
        gap += 0.04
    block_h = sum(int(sz * gap) for sz, _ in fits) + int(fits[-1][0] * 0.20)
    y = max(12, (H - block_h) // 2)
    for ln, (size, f) in zip(lines, fits):
        text, color, accent = ln[0], ln[1], ln[2]
        tw = int(f.getlength(text))
        lay = Image.new("RGBA", (tw + 84, int(size * 1.36)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        if accent:
            ld.rounded_rectangle([0, 0, lay.width - 1, lay.height - 1],
                                 radius=int(size * 0.1), fill=accent)
            ld.text((42, int(size * 0.11)), text, font=f, fill=color)
        else:
            ld.text((42, int(size * 0.11)), text, font=f, fill=color,
                    stroke_width=max(12, size // 11), stroke_fill=(14, 12, 20))
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", lay.size, (0, 0, 0, 200)), (0, 0), lay.split()[3])
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(13)), (26, y + 16))
        img.alpha_composite(lay, (18, y))
        y += int(size * gap)
    return vignette(img, 74)


def _tw(f, text):
    """句読点の後ろは詰めて測る。全角の読点は右に半角分の余白を持つので、
    そのままだと「金がない、却下」が「金がない、、却下」に見えるほど間延びする。"""
    w = 0.0
    for ch in text:
        a = f.getlength(ch)
        w += a * 0.52 if ch in "、。，．" else a
    return int(w)


def _ttext(d, xy, text, f, fill, **kw):
    """_tw と同じ送りで1文字ずつ描く。"""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill, **kw)
        a = f.getlength(ch)
        x += a * 0.52 if ch in "、。，．" else a


def _wrap_chars(f, text, max_w):
    lines, cur = [], ""
    for ch in text:
        if ch == "|":
            lines.append(cur); cur = ""; continue
        if _tw(f, cur + ch) <= max_w:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    return lines


def _fit_lines(text, fname, max_w, max_size, min_size, max_lines=2):
    size = max_size
    while size > min_size:
        f = font(fname, size)
        ls = _wrap_chars(f, text, max_w)
        if len(ls) <= max_lines:
            return f, ls
        size -= 2
    f = font(fname, min_size)
    return f, _wrap_chars(f, text, max_w)[:max_lines]


def _bubble(dr, box, text, tail_x=None):
    """白い吹き出し。**これが3コマ型の主役**（2026-09-02）。

    最初に作った版はコマに黄ラベル1個だけで、名詞が3つ並んでいるだけだった。
    伸びている局は例外なく「吹き出しのセリフ」＋「黄ラベルの意味づけ」の2層で、
    3コマ読むと話が分かる。ラベルだけでは物語にならない。
    """
    x0, y0, x1, y1 = box
    f, lines = _fit_lines(text, "w9", (x1 - x0) - 26, 44, 20, 2)
    dr.rounded_rectangle(box, radius=14, fill=(255, 255, 255),
                         outline=(18, 14, 12), width=5)
    if tail_x is not None:
        tip = (tail_x + 2, y0 - 26)
        dr.polygon([(tail_x - 20, y0), (tail_x + 20, y0), tip], fill=(255, 255, 255))
        dr.line([(tail_x - 20, y0), tip], fill=(18, 14, 12), width=5)
        dr.line([(tail_x + 20, y0), tip], fill=(18, 14, 12), width=5)
        dr.line([(tail_x - 15, y0), (tail_x + 15, y0)], fill=(255, 255, 255), width=6)
    lh = int(f.size * 1.10)
    ty = (y0 + y1) // 2 - lh * len(lines) // 2
    for k, ln in enumerate(lines):
        _ttext(dr, ((x0 + x1) // 2 - _tw(f, ln) // 2, ty + k * lh), ln, f, (20, 16, 12))


def layout_panels(spec):
    """3コマ構成。**伸びている局を実測して作った型**（2026-09-02）。

    それまでの1枚絵（layout_stack）は CTR 1.3%・0.8% で、目安2〜10%の下限を割っていた。
    ゲーム大好きずんだもん / 世界まる見えずんだもん / ずんだもん末路ストーリー /
    カカチャンネル の上位サムネを16枚並べて見たところ、全部が逆をやっていた:
      - 3〜4コマに割って、矢印で「変化」を見せる
      - 各コマに黄枠の小ラベル。1枚に3〜6個
      - 数字をほぼ必ず入れる（275万本・61%大暴落・3万人解雇）
      - ずんだもんは小さく、各コマに複数
    「情報を足すほど実寸で読めなくなる」という以前の見立ては誤りだった。
    168pxでも、コマ割りと色分けは「何かたくさん起きている」ことを伝える。

    **初版からの作り直し**（同日・実物を並べて比べた結果）:
      - 各コマに吹き出しを足した。ラベルだけだと名詞が3つ並ぶだけで物語にならない
      - コマ左上に小タグ（年・立場）。競合は全部これで「誰の話か」を出している
      - 矢印を太い赤＋白フチにして吹き出しの高さに置いた（小さい三角は実寸で消える）
      - 下の帯を廃止してコマを縦いっぱいに。題材名は見出しに入れて2色で出す
      - 立ち絵は左右交互＋反転。同じ絵を3回並べると手抜きに見える
    """
    headline = spec["headline"]
    panels = spec["panels"]
    n = len(panels)

    img = Image.new("RGBA", (W, H), (16, 14, 18, 255))

    HEAD_H = int(H * 0.21)
    body_top = HEAD_H
    ph = H - body_top
    gap = 8
    pw = (W - gap * (n - 1)) // n

    LAB_H, BUB_H, TAG_H = 84, 104, 50
    lab_y = ph - LAB_H - 8
    bub_y = lab_y - BUB_H - 10

    for i, pn in enumerate(panels):
        x0 = i * (pw + gap)
        cell = Image.new("RGBA", (pw, ph), (*pn.get("bg", (60, 60, 68)), 255))
        cd = ImageDraw.Draw(cell, "RGBA")
        for k in range(-ph, pw + ph, 64):
            cd.polygon([(k, ph), (k + 16, ph), (k + 16 + ph, 0), (k + ph, 0)],
                       fill=(255, 255, 255, 22))

        art_top, art_bot = TAG_H - 6, bub_y - 6
        art_h = art_bot - art_top
        right = i % 2 == 0
        # **立ち絵はコマの端で切る**。中に丸ごと収めると小物が隠れ、上半分が空く
        bu = bust(spec.get("who", "zundamon"), pn.get("emo", "surprised"),
                  height=int(art_h * 0.78), crop=0.42)
        if not right:                       # 内側を向かせる（3コマ同じ絵に見せない）
            bu = bu.transpose(Image.FLIP_LEFT_RIGHT)
        bx = pw - int(bu.width * 0.66) if right else -int(bu.width * 0.34)

        if pn.get("prop") and globals().get(pn["prop"]):
            pl = prop_layer(globals()[pn["prop"]], size=520, tilt=-8)
            sc = min(pw * 0.70 / pl.width, art_h * 1.0 / pl.height)
            pl = pl.resize((max(1, int(pl.width * sc)), max(1, int(pl.height * sc))),
                           Image.LANCZOS)
            px = int(pw * 0.03) if right else pw - pl.width - int(pw * 0.03)
            py = art_top + (art_h - pl.height) // 2
            glow = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            gcx, gcy = px + pl.width // 2, py + pl.height // 2
            for t in range(24):
                ang = t * 15.0
                gd.polygon([(gcx, gcy),
                            (gcx + math.cos(math.radians(ang)) * 900,
                             gcy + math.sin(math.radians(ang)) * 900),
                            (gcx + math.cos(math.radians(ang + 7)) * 900,
                             gcy + math.sin(math.radians(ang + 7)) * 900)],
                           fill=(255, 255, 255, 26))
            cell.alpha_composite(glow)
            cell.alpha_composite(pl, (px, py))

        cell.alpha_composite(bu, (bx, art_bot - bu.height))

        tag = pn.get("tag", "")
        if tag:
            f, _ = _fit_lines(tag, "w9", pw - 40, 34, 20, 1)
            tw = _tw(f, tag) + 24
            cd.rounded_rectangle([10, 8, 10 + tw, 8 + TAG_H - 18], radius=6,
                                 fill=(*pn.get("tag_bg", (255, 120, 30)), 255))
            _ttext(cd, (22, 8 + (TAG_H - 18 - int(f.size * 1.2)) // 2), tag, f,
                   (255, 255, 255))

        if pn.get("say"):
            # 矢印が来る側は空けておく（詰めると矢印が吹き出しの黒フチに埋もれる）
            bl = 44 if i > 0 else 10
            br = pw - (44 if i < n - 1 else 10)
            _bubble(cd, (bl, bub_y, br, bub_y + BUB_H), pn["say"],
                    tail_x=br - 80 if right else bl + 80)

        lab = pn.get("label", "")
        if lab:
            f, _ = _fit_lines(lab, "w9", pw - 40, 62, 24, 1)
            cd.rounded_rectangle([8, lab_y, pw - 8, lab_y + LAB_H], radius=8,
                                 fill=(255, 214, 40), outline=(30, 22, 6), width=5)
            _ttext(cd, ((pw - _tw(f, lab)) // 2,
                        lab_y + (LAB_H - int(f.size * 1.22)) // 2), lab, f, (26, 20, 12))

        img.paste(cell, (x0, body_top), cell)

        if i < n - 1:                       # 太い赤矢印。小さい三角は実寸で消える
            ax = x0 + pw + gap // 2
            ay = body_top + bub_y + BUB_H // 2
            d3 = ImageDraw.Draw(img)
            d3.polygon([(ax - 36, ay - 34), (ax + 34, ay), (ax - 36, ay + 34)],
                       fill=(228, 26, 32))

    # 見出し。題材名だけ色を変える（競合は例外なく2色）
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, HEAD_H], fill=(14, 12, 16))
    hi = spec.get("head_hi", "")
    base_c = spec.get("head_color", (255, 255, 255))
    hi_c = spec.get("head_hi_color", (255, 214, 40))
    if hi and hi in headline:
        a, b = headline.split(hi, 1)
        segs = [(t, c) for t, c in ((a, base_c), (hi, hi_c), (b, base_c)) if t]
    else:
        segs = [(headline, base_c)]
    size = 130
    while size > 56 and sum(_tw(font("851", size), t) for t, _ in segs) > W - 44:
        size -= 4
    f = font("851", size)
    x = (W - sum(_tw(f, t) for t, _ in segs)) // 2
    y = (HEAD_H - int(size * 1.18)) // 2
    for t, c in segs:
        _ttext(d, (x, y), t, f, c, stroke_width=max(10, size // 9),
               stroke_fill=(20, 8, 8))
        x += _tw(f, t)
    return img.convert("RGB")


def layout_stack(spec):
    """上下分割型。文字は横幅いっぱい・顔は右下に大きく。

    横並び（bold/punch）は顔を大きくすると文字の使える幅が減り、両方は立たない。
    上下に分ければ上段のフックは画面幅の94%を使えるので1文字あたり約155px
    （bold は約93px）まで太らせられ、空いた右下に顔を大きく置ける。
    3段（フック／サブ／題材）にして中央の空きも潰す。
    """
    base = spec.get("bg", ((150, 26, 40), (96, 14, 26)))
    img = Image.new("RGBA", (W, H), (*base[0], 255))
    d = ImageDraw.Draw(img)
    d.polygon([(0, H), (0, int(H * 0.40)), (W, int(H * 0.16)), (W, H)], fill=(*base[1], 255))
    stripe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe)
    for x in range(-H, W + H, 58):
        sd.polygon([(x, H), (x + 22, H), (x + 22 + H, 0), (x + H, 0)],
                   fill=(255, 255, 255, 13))
    img.alpha_composite(stripe)
    d = ImageDraw.Draw(img)
    cx, cy = int(W * 0.74), int(H * 0.74)
    for i in range(30):
        a = i * 12.0
        x1 = cx + math.cos(math.radians(a)) * 240
        y1 = cy + math.sin(math.radians(a)) * 240
        x2 = cx + math.cos(math.radians(a + 1.7)) * 1500
        y2 = cy + math.sin(math.radians(a + 1.7)) * 1500
        d.polygon([(cx, cy), (x1, y1), (x2, y2)], fill=(255, 255, 255, 17))

    lines = spec["lines"]
    hook, topic = lines[0], lines[-1]
    sub = lines[1] if len(lines) > 2 else None

    # ① 顔を先に置く。文字は必ずこの上に来る
    sp = Image.open(sprite_path(cfg, spec.get("who", "zundamon"),
                                spec.get("emotion", "surprised"))).convert("RGBA")
    head = sp.crop((0, 0, sp.width, int(sp.height * 0.44)))
    hb = head.split()[3].getbbox()
    if hb:
        head = head.crop(hb)
    sc = int(H * 0.84) / head.height
    head = outline_sprite(head.resize((int(head.width * sc), int(head.height * sc)),
                                      Image.LANCZOS), 20)
    head_x = W - int(head.width * 0.90)
    head_left = head_x + (head.split()[3].getbbox() or (0,))[0]

    # ② 上段フックの下地。キャラの白フチと文字がぶつかるのを防ぐ。
    #    帯 → 顔 の順に重ねる（逆にすると頭の豆が帯に埋まり、ずんだもんと分からなくなる）
    band_h = int(H * 0.34)
    top = Image.new("RGBA", (W, band_h), (0, 0, 0, 0))
    td = ImageDraw.Draw(top)
    td.rectangle([0, 0, W, band_h - 26], fill=(10, 9, 14, 205))
    td.polygon([(0, band_h - 26), (W, band_h - 26), (W, band_h - 60), (0, band_h)],
               fill=(10, 9, 14, 205))
    img.alpha_composite(top, (0, 0))
    img.alpha_composite(head, (head_x, H - head.height + 8))

    def _fit(text, base_size, limit, ratio=1.0):
        size = int(base_size * ratio)
        while size > 56:
            f = font("w9", size)
            if _tw(f, text) <= limit:
                break
            size -= 4
        f = font("w9", size)
        pad = 42
        return size, f, _tw(f, text) + pad * 2, int(size * 1.36), pad

    def _blit(text, color, accent, fit, x, y):
        size, f, w, h, pad = fit
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        if accent:
            ld.rounded_rectangle([0, 0, w - 1, h - 1], radius=int(size * 0.12), fill=accent)
            _ttext(ld, (pad, int(size * 0.11)), text, f, color)
        else:
            _ttext(ld, (pad, int(size * 0.11)), text, f, color,
                   stroke_width=max(12, size // 11), stroke_fill=(14, 12, 20))
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", lay.size, (0, 0, 0, 205)), (0, 0), lay.split()[3])
        px = x if x is not None else (W - w) // 2
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(15)), (px + 8, y + 16))
        img.alpha_composite(lay, (px, y))

    # 先に3段すべての寸法を確定させてから置く。順に描くと、フックが縮んだときに
    # サブ行が題材帯へめり込む（escalator で実際に重なった・2026-08）
    left_limit = min(int(W * 0.60), head_left - 20)
    hf = _fit(hook[0], 300, int(W * 0.94))
    tf = _fit(topic[0], hf[0], left_limit, 0.62)
    hook_y = int(H * 0.005)
    topic_y = H - tf[3] - int(H * 0.05)
    gap_top = hook_y + hf[3]
    # 絵を置くので中段の高さを確保する。フックが短い語だと文字が最大まで太り、
    # 中段が潰れて絵だけ極端に小さくなる（乾電池「5分の遅刻が」で170pxしか残らなかった）
    if spec.get("prop"):
        while topic_y - gap_top < int(H * 0.40) and hf[0] > 96:
            hf = _fit(hook[0], hf[0] - 10, int(W * 0.94))
            tf = _fit(topic[0], hf[0], left_limit, 0.62)
            topic_y = H - tf[3] - int(H * 0.05)
            gap_top = hook_y + hf[3]
    gap = topic_y - gap_top

    _blit(hook[0], hook[1], hook[2], hf, None, hook_y)
    _blit(topic[0], topic[1], topic[2] or (255, 214, 40, 255), tf, 22, topic_y)

    # 題材の絵。文字だけでは一覧で何の動画か伝わらない（ユーザー指摘 2026-08-17）。
    # 中段はまるごと絵に使う。サブ行と横に並べると両方小さくなるので、サブ行は捨てた
    # ——「一目でわかる」ほうが補助情報より効く。
    prop = spec.get("prop")
    if prop and globals().get(prop):
        pl = prop_layer(globals()[prop], size=620, tilt=-10)
        room_h = max(80, topic_y - gap_top - 20)
        room_w = max(120, head_left - 12 - 40)
        # 高さだけで合わせると、マイクやUSBのような細長い絵が痩せて見える。
        # 面積を基準に決めてから枠に収めると、絵ごとの見た目の大きさがそろう
        import math as _m
        area = _m.sqrt(room_w * room_h * 0.92 / (pl.width * pl.height))
        sc = min(area, room_w / pl.width, room_h / pl.height)
        pl = pl.resize((max(1, int(pl.width * sc)), max(1, int(pl.height * sc))),
                       Image.LANCZOS)
        # 顔の左の帯を絵で埋める。中央に置くと左が空くので、やや左寄せにする
        px = max(30, 30 + int((room_w - pl.width) * 0.42))
        img.alpha_composite(pl, (px, gap_top + (room_h - pl.height) // 2 + 8))
    return vignette(img, 74)


# ---------------------------------------------------------------- 動画ごとの仕様

# 全20本の仕様。型は題材で使い分ける:
#   ba      = 時代の変化がある（ビフォー→アフター）
#   charbig = 驚き・落胆が主題（キャラの表情で見せる）
#   split   = 数字や二択の対比
#   hero    = 発明品そのものを主役に
# 文言はタイトルと重複させない（一覧で情報が重複して弱くなる）
W1 = (255, 255, 255, 255)
B1 = (26, 20, 12, 255)
Y1 = (255, 214, 40, 255)

SPECS = {
    # 2026-08のStudio実測でクリック率1.5%だったため、スマホ幅168pxで読めることを
    # 最優先に全面刷新した。1行7文字以内・2行・要素は文字とキャラだけに絞る
    # ---- 人物物語 ----
    "momofuku-meme": dict(prop="p_cupnoodle", layout="stack", bg=((160, 44, 24), (98, 22, 12)), emotion="sad",
    lines=[("47歳で全財産ゼロ", W1, None), ("裏庭の小屋から", W1, None), ("カップ麺", B1, Y1)]),
    "qr-meme": dict(prop="p_qr", layout="stack", bg=((22, 52, 110), (12, 28, 66)), emotion="surprised",
    lines=[("疲れたの一言から", W1, None), ("愛知の部品工場で", W1, None), ("QRコード", B1, Y1)]),
    "kaiten-meme": dict(prop="p_sushilane", layout="stack", bg=((150, 34, 44), (88, 18, 26)), emotion="thinking",
    lines=[("ヒントはビール工場", W1, None), ("人手が足りない", W1, None), ("回転寿司", B1, Y1)]),
    "yai-denchi": dict(prop="p_drycell", layout="stack", bg=((60, 30, 96), (34, 16, 58)), emotion="sad",
    lines=[("5分の遅刻が", W1, None), ("明治の職工が挑む", W1, None), ("乾電池", B1, Y1)]),
    "tenji-block-meme": dict(prop="p_block", layout="stack", bg=((146, 108, 16), (92, 66, 8)), emotion="sad",
    lines=[("全財産を道路に", W1, None), ("友の失明がきっかけ", W1, None), ("点字ブロック", B1, Y1)]),
    "masuoka-flash": dict(prop="p_usb", layout="stack", bg=((26, 60, 104), (14, 32, 62)), emotion="sad",
    lines=[("金がない、却下", W1, None), ("土日に特許23件", W1, None), ("USBメモリ", B1, Y1)]),
    "kaisatsu-drama": dict(prop="p_gate", layout="stack", bg=((22, 66, 78), (12, 38, 46)), emotion="surprised",
    lines=[("1分間に80人", W1, None), ("駅員より速くしろ", W1, None), ("自動改札", B1, Y1)]),
    "gastro-meme": dict(prop="p_endoscope", layout="stack", bg=((26, 52, 92), (14, 28, 56)), emotion="surprised",
    lines=[("たった2人で作る", W1, None), ("夜行列車で口説いた", W1, None), ("胃カメラ", B1, Y1)]),
    "rice-cooker-meme": dict(prop="p_ricecooker", layout="stack", bg=((132, 62, 22), (80, 36, 12)), emotion="sad",
    lines=[("妻が千回炊いた", W1, None), ("町工場の夫婦が", W1, None), ("炊飯器", B1, Y1)]),
    "quartz-astron": dict(prop="p_wristwatch", layout="stack",
        bg=((28, 52, 92), (14, 28, 56)), emotion="surprised",
        lines=[("スイスを倒した", W1, None), ("1600社が600社に", W1, None),
               ("クオーツ時計", B1, Y1)]),
    "yamauchi-nintendo": dict(prop="p_hanafuda", layout="stack",
        bg=((18, 78, 58), (8, 38, 30)), emotion="surprised",
        lines=[("全部失敗した", W1, None), ("借金70億からの再起", W1, None),
               ("任天堂", B1, Y1)]),
    "nakauchi-daiei": dict(layout="panels",
        headline="ダイエーはなぜ消えた", head_hi="ダイエー",
        panels=[
            dict(prop="p_sukiyaki", tag="1943年 戦地", bg=(150, 74, 26),
                 tag_bg=(60, 44, 30), emo="sad",
                 say="すき焼きが|食いたいのだ…", label="生きて帰った"),
            dict(prop="p_beefpack", tag="1957年 大阪", bg=(224, 168, 26),
                 tag_bg=(150, 30, 20), emo="angry",
                 say="よそより|安く売るのだ！", label="牛肉 100円→39円"),
            dict(prop="p_downgraph", tag="2004年", bg=(30, 44, 96),
                 tag_bg=(18, 26, 60), emo="surprised",
                 say="借金、1兆円…", label="創業者、追放"),
        ]),    "exit-sign": dict(prop="p_exitsign", layout="stack",
        bg=((20, 88, 62), (8, 44, 32)), emotion="surprised",
        lines=[("描いたのは日本人", W1, None), ("毎日見てるのに知らない", W1, None),
               ("非常口マーク", B1, Y1)]),
    "nishizawa-fiber": dict(prop="p_fiber", layout="stack",
        bg=((18, 46, 92), (8, 22, 50)), emotion="sad",
        lines=[("金は出せない", W1, None), ("日本が捨てた発明", W1, None),
               ("光ファイバー", B1, Y1)]),
    "okano-needle": dict(prop="p_needle", layout="stack",
        bg=((16, 74, 84), (8, 40, 48)), emotion="surprised",
        lines=[("100社が断った", W1, None), ("6人の町工場がやった", W1, None),
               ("注射針", B1, Y1)]),
    "sharp-pencil": dict(prop="p_sharppencil", layout="stack",
        bg=((22, 54, 104), (10, 28, 60)), emotion="sad",
        lines=[("全部失って大阪へ", W1, None), ("シャープの名前の由来", W1, None),
               ("シャーペン", B1, Y1)]),
    "purikura-meme": dict(prop="p_purikura", layout="stack",
        bg=((150, 26, 88), (86, 12, 50)), emotion="sad",
        lines=[("持って帰ってどうすんの", W1, None), ("ゲーセンは男の場所", W1, None),
               ("プリクラ", B1, Y1)]),
    "karaoke": dict(prop="p_mic", layout="stack", bg=((88, 26, 108), (52, 14, 66)), emotion="sad",
    lines=[("特許を取らなかった", W1, None), ("手作り11台から", W1, None), ("カラオケ", B1, Y1)]),
    "yokoi-gunpei": dict(prop="p_gameboy", layout="stack", bg=((36, 44, 74), (20, 26, 46)), emotion="surprised",
    lines=[("あえて白黒で勝つ", W1, None), ("枯れた技術の水平思考", W1, None), ("ゲームボーイ", B1, Y1)]),
    "shinkansen-bird": dict(prop="p_shinkansen", layout="stack", bg=((22, 70, 110), (12, 40, 66)), emotion="surprised",
    lines=[("騒音を鳥が解決", W1, None), ("趣味の野鳥観察が", W1, None), ("新幹線", B1, Y1)]),
    "cutter-knife": dict(prop="p_blade", layout="stack", bg=((24, 62, 108), (12, 34, 64)), emotion="happy",
    lines=[("ヒントは板チョコ", W1, None), ("折れば切れる", W1, None), ("カッターナイフ", B1, Y1)]),
    "washlet": dict(prop="p_toilet", layout="stack", bg=((18, 78, 88), (10, 44, 52)), emotion="surprised",
    lines=[("社員300人が実験", W1, None), ("日本人の体を測れ", W1, None), ("ウォシュレット", B1, Y1)]),
    "ajinomoto": dict(prop="p_umami", layout="stack", bg=((110, 76, 20), (66, 44, 10)), emotion="thinking",
    # ---- 解説 ----
    lines=[("5つ目の味を発見", W1, None), ("昆布12キロから", W1, None), ("味の素", B1, Y1)]),
    "battery-80-duo": dict(prop="p_battery", layout="stack", bg=((150, 30, 34), (92, 16, 22)), emotion="surprised",
    lines=[("毎晩100%は損", W1, None), ("メーカーが止める機能", W1, None), ("スマホ充電", B1, Y1)]),
    "banknote": dict(prop="p_bill", layout="stack", bg=((72, 26, 96), (42, 14, 58)), emotion="surprised",
    lines=[("コピー機が拒否", W1, None), ("偽札は2年で343枚", W1, None), ("お札の秘密", B1, Y1)]),
    "escalator": dict(prop="p_escalator", layout="stack", bg=((34, 52, 82), (18, 30, 50)), emotion="surprised",
    lines=[("誰も得しない", W1, None), ("片側空けの謎", W1, None), ("エスカレーター", B1, Y1)]),
    "traffic-light": dict(prop="p_signal", layout="stack", bg=((20, 62, 60), (10, 36, 36)), emotion="thinking",
    lines=[("緑なのに青と呼ぶ", W1, None), ("世界で日本だけ", W1, None), ("信号機", B1, Y1)]),
    "auto-door": dict(prop="p_autodoor", layout="stack", bg=((28, 54, 78), (14, 30, 46)), emotion="angry",
    lines=[("黒い服だと開かない", W1, None), ("見てるのは人じゃない", W1, None), ("自動ドア", B1, Y1)]),
}


def render(slug, out_path=None):
    spec = SPECS[slug]
    kind = spec["layout"]
    img = {"split": layout_split, "band": layout_band, "ba": layout_beforeafter,
           "charbig": layout_charbig, "photo": layout_photo,
           "bold": layout_bold, "face": layout_face,
           "punch": layout_punch,
           "stack": layout_stack,
           "panels": layout_panels}.get(kind, layout_hero)(spec)
    if out_path is None:
        from ytf.config import find_project_dir
        d = find_project_dir(cfg.root, slug)
        out_path = (d / "out" / "thumbnail.png") if d else Path(f"projects/{slug}/out/thumbnail.png")
    out = out_path
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


if __name__ == "__main__":
    slugs = sys.argv[1:] or list(SPECS)
    outdir = None
    if slugs and slugs[0] == "--sample":
        outdir = Path(slugs[1])
        slugs = slugs[2:] or list(SPECS)
    from ytf.config import find_project_dir, is_uploaded
    explicit = bool(sys.argv[1:]) and sys.argv[1] != "--sample"
    for slug in slugs:
        if slug not in SPECS:
            print(f"スキップ（SPECS未登録）: {slug}")
            continue
        d = find_project_dir(cfg.root, slug)
        if d is not None and is_uploaded(d) and not explicit and not outdir:
            print(f"スキップ（公開済み・編集しない）: {slug}")
            continue
        dst = (outdir / f"tn_{slug}.png") if outdir else None
        print("生成:", render(slug, dst))
