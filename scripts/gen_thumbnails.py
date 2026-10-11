#!/usr/bin/env python3
"""凝ったサムネイル生成（絵入り・分割・飾りフォント対応）。

方針（2026-08 ユーザー決定）:
- 絵はタイトルに合ったもの（動画ごとの小物イラスト）を主役にする
- 左右2分割のビフォーアフター構図も使う
- フォントは 源界明朝（崩れ・衝撃）/ 851チカラヅヨク（殴り書き・ツッコミ）/
  ヒラギノW9（極太・基本）を使い分け。ラノベPOP v2 が assets/fonts/ にあれば
  ポップ枠として自動採用
  ただし**現行の2コマ型（layout_panels）の見出しは w9 固定**。
  飾りフォントは実寸で字形が崩れ、成功譚がホラーに見える（2026-09-12）

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
from ytf.config import resolve_font  # noqa: E402

FONTS = {
    # **OS直書きにしない**（2026-09-18 Windows移行の準備）。
    # 同梱の Noto Sans JP Black があればそれを使い、無ければOS標準を探す
    "w9": resolve_font("w9", cfg.root),
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


def p_octopus(d, s):
    """タコの足と吸盤。アシックス回のヒントそのもの。"""
    import math as _m
    pts = [(s * 0.10 + i * s * 0.072, s * 0.46 - _m.sin(i * 0.6) * s * 0.13)
           for i in range(11)]
    d.line(pts, fill=(210, 96, 96), width=int(s * 0.115), joint="curve")
    for i, (px, py) in enumerate(pts):
        if i % 2:
            continue
        r = s * 0.042
        d.ellipse([px - r, py - r + s * 0.026, px + r, py + r + s * 0.026],
                  fill=(244, 182, 182), outline=(168, 66, 66), width=int(s * 0.012))


def p_tabi(d, s):
    """足袋。親指の割れとこはぜ。ブリヂストン回の「もとは足袋屋」。"""
    d.polygon([(s * 0.10, s * 0.68), (s * 0.72, s * 0.68), (s * 0.90, s * 0.50),
               (s * 0.84, s * 0.26), (s * 0.34, s * 0.18), (s * 0.10, s * 0.40)],
              fill=(242, 238, 230), outline=(140, 134, 122), width=int(s * 0.020))
    d.polygon([(s * 0.62, s * 0.66), (s * 0.90, s * 0.50), (s * 0.84, s * 0.36),
               (s * 0.62, s * 0.50)], fill=(212, 206, 194),
              outline=(140, 134, 122), width=int(s * 0.016))
    for k in range(3):                       # こはぜ
        d.rectangle([s * 0.13, s * 0.30 + k * s * 0.11, s * 0.21,
                     s * 0.37 + k * s * 0.11], fill=(198, 192, 178),
                    outline=(136, 130, 118), width=int(s * 0.012))
    d.polygon([(s * 0.10, s * 0.68), (s * 0.72, s * 0.68), (s * 0.90, s * 0.52),
               (s * 0.90, s * 0.62), (s * 0.70, s * 0.80), (s * 0.10, s * 0.80)],
              fill=(52, 52, 56), outline=(28, 28, 32), width=int(s * 0.016))


def p_tyrestack(d, s):
    """積み上がったタイヤ。ブリヂストン回の「全部返ってきた」。
    ★溝の模様は商標に触れうるので描かない。黒い輪だけで積む。"""
    for r, (cx, cy, rr) in enumerate([(0.50, 0.74, 0.26), (0.34, 0.44, 0.22),
                                      (0.68, 0.42, 0.22), (0.50, 0.18, 0.18)]):
        d.ellipse([s * (cx - rr), s * (cy - rr * 0.74), s * (cx + rr),
                   s * (cy + rr * 0.74)], fill=(46, 46, 50),
                  outline=(24, 24, 28), width=int(s * 0.020))
        ir = rr * 0.48
        d.ellipse([s * (cx - ir), s * (cy - ir * 0.74), s * (cx + ir),
                   s * (cy + ir * 0.74)], fill=(122, 124, 130),
                  outline=(80, 82, 88), width=int(s * 0.014))


def p_whiskybottle(d, s):
    """角瓶。銘柄の意匠は描かない。琥珀色の中身と無地のラベルだけ。"""
    d.rounded_rectangle([s * 0.26, s * 0.30, s * 0.74, s * 0.92], radius=s * 0.05,
                        fill=(216, 208, 192), outline=(140, 132, 116),
                        width=int(s * 0.020))
    d.rounded_rectangle([s * 0.31, s * 0.44, s * 0.69, s * 0.86], radius=s * 0.04,
                        fill=(190, 118, 40))
    d.rectangle([s * 0.42, s * 0.12, s * 0.58, s * 0.32], fill=(202, 194, 178),
                outline=(140, 132, 116), width=int(s * 0.016))
    d.rectangle([s * 0.39, s * 0.05, s * 0.61, s * 0.15], fill=(118, 94, 58))
    d.rectangle([s * 0.29, s * 0.56, s * 0.71, s * 0.74], fill=(242, 238, 228),
                outline=(150, 142, 126), width=int(s * 0.016))


def p_rtimer(d, s):
    """撮影用タイマー。丸い文字盤とつまみ。数字は描かない。"""
    d.rounded_rectangle([s * 0.10, s * 0.28, s * 0.90, s * 0.84], radius=s * 0.05,
                        fill=(118, 112, 104), outline=(66, 62, 56),
                        width=int(s * 0.022))
    cx, cy, r = s * 0.43, s * 0.56, s * 0.20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(242, 238, 228),
              outline=(66, 62, 56), width=int(s * 0.020))
    for k in range(12):                      # 目盛り
        import math as _m
        a = k * _m.pi / 6
        d.line([cx + _m.cos(a) * r * 0.72, cy + _m.sin(a) * r * 0.72,
                cx + _m.cos(a) * r * 0.90, cy + _m.sin(a) * r * 0.90],
               fill=(96, 92, 86), width=int(s * 0.012))
    d.line([cx, cy, cx + r * 0.62, cy - r * 0.54], fill=(206, 56, 46),
           width=int(s * 0.026))
    d.ellipse([s * 0.70, s * 0.44, s * 0.84, s * 0.58], fill=(80, 76, 72),
              outline=(50, 48, 44), width=int(s * 0.016))


def p_loom(d, s):
    """機織り機。縦糸が張られた木の枠。トヨタ回の「もとは織機屋」。"""
    fr, wd = (150, 116, 72), (108, 82, 48)
    d.rectangle([s * 0.10, s * 0.14, s * 0.19, s * 0.90], fill=fr, outline=wd,
                width=int(s * 0.016))
    d.rectangle([s * 0.81, s * 0.14, s * 0.90, s * 0.90], fill=fr, outline=wd,
                width=int(s * 0.016))
    d.rectangle([s * 0.06, s * 0.08, s * 0.94, s * 0.19], fill=(178, 140, 90),
                outline=wd, width=int(s * 0.016))
    for k in range(9):                       # 縦糸
        x = s * (0.23 + k * 0.066)
        d.line([x, s * 0.19, x, s * 0.66], fill=(240, 236, 224),
               width=int(s * 0.012))
    d.rectangle([s * 0.17, s * 0.44, s * 0.83, s * 0.53], fill=(96, 74, 44),
                outline=(62, 48, 28), width=int(s * 0.014))   # 筬
    d.rectangle([s * 0.17, s * 0.66, s * 0.83, s * 0.82], fill=(232, 226, 210),
                outline=(150, 142, 124), width=int(s * 0.014))  # 織り上がった布


def p_engineblock(d, s):
    """割れたエンジンの鋳物。トヨタ回の「9割が屑になる」。
    ★割れ目をはっきり描く。無傷の四角だと、ただの箱に見えて意味が出ない。"""
    d.rounded_rectangle([s * 0.14, s * 0.22, s * 0.86, s * 0.84], radius=s * 0.05,
                        fill=(132, 136, 146), outline=(62, 66, 76),
                        width=int(s * 0.022))
    for k in range(3):                       # シリンダーの穴
        cx = s * (0.30 + k * 0.20)
        d.ellipse([cx - s * 0.075, s * 0.30, cx + s * 0.075, s * 0.45],
                  fill=(70, 74, 84), outline=(46, 50, 58), width=int(s * 0.014))
    # 割れ目（これが主役）
    d.line([(s * 0.20, s * 0.84), (s * 0.38, s * 0.62), (s * 0.30, s * 0.50),
            (s * 0.46, s * 0.22)], fill=(30, 32, 38), width=int(s * 0.036),
           joint="curve")
    d.line([(s * 0.62, s * 0.22), (s * 0.70, s * 0.52), (s * 0.86, s * 0.60)],
           fill=(30, 32, 38), width=int(s * 0.030), joint="curve")


def p_sole(d, s):
    """靴底。吸盤型のへこみが並ぶ。意匠は付けない。"""
    d.rounded_rectangle([s * 0.24, s * 0.10, s * 0.76, s * 0.90], radius=s * 0.22,
                        fill=(78, 82, 94), outline=(40, 44, 54), width=int(s * 0.018))
    for r in range(5):
        for c in range(2 if r in (0, 4) else 3):
            n = 2 if r in (0, 4) else 3
            cx = s * (0.50 + (c - (n - 1) / 2) * 0.155)
            cy = s * (0.22 + r * 0.14)
            rr = s * 0.048
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(50, 54, 66),
                      outline=(126, 132, 146), width=int(s * 0.012))


def p_boat(d, s):
    """漁船。ディズニーランド回の「ここは海だった」。"""
    d.polygon([(s * 0.12, s * 0.62), (s * 0.80, s * 0.62), (s * 0.88, s * 0.48),
               (s * 0.06, s * 0.51)], fill=(166, 134, 92),
              outline=(100, 78, 48), width=int(s * 0.016))
    d.rectangle([s * 0.32, s * 0.30, s * 0.54, s * 0.51], fill=(196, 168, 126),
                outline=(100, 78, 48), width=int(s * 0.014))
    d.line([s * 0.68, s * 0.50, s * 0.68, s * 0.14], fill=(120, 96, 60),
           width=int(s * 0.022))
    # 水面
    for r in range(3):
        y = s * (0.70 + 0.08 * r)
        for k in range(4):
            d.arc([s * (0.06 + 0.22 * k), y - s * 0.03,
                   s * (0.22 + 0.22 * k), y + s * 0.03], 200, 340,
                  fill=(150, 190, 214), width=int(s * 0.018))


def p_stamp(d, s):
    """朱肉と判子。交渉がまとまる記号。"""
    d.ellipse([s * 0.10, s * 0.52, s * 0.48, s * 0.82], fill=(208, 200, 186),
              outline=(150, 142, 128), width=int(s * 0.014))
    d.ellipse([s * 0.15, s * 0.56, s * 0.43, s * 0.78], fill=(196, 40, 36))
    d.rounded_rectangle([s * 0.60, s * 0.20, s * 0.76, s * 0.66], radius=s * 0.02,
                        fill=(180, 146, 100), outline=(112, 86, 50),
                        width=int(s * 0.014))
    d.ellipse([s * 0.58, s * 0.62, s * 0.78, s * 0.74], fill=(196, 40, 36),
              outline=(120, 24, 22), width=int(s * 0.012))
    # 押された跡
    d.ellipse([s * 0.56, s * 0.84, s * 0.80, s * 0.96], outline=(206, 60, 52),
              width=int(s * 0.020))


def p_paper(d, s):
    """社内報の紙。ホンダ回の「優勝すると書いた宣言」。"""
    d.polygon([(s * 0.20, s * 0.14), (s * 0.80, s * 0.10),
               (s * 0.84, s * 0.86), (s * 0.24, s * 0.90)],
              fill=(250, 248, 240), outline=(150, 146, 138), width=int(s * 0.014))
    for r in range(7):
        w = 0.52 if r % 3 else 0.34
        d.line([s * 0.28, s * (0.24 + 0.09 * r),
                s * (0.28 + w), s * (0.235 + 0.09 * r)],
               fill=(186, 182, 174), width=int(s * 0.016))
    # 赤で囲った一行＝優勝
    d.rounded_rectangle([s * 0.26, s * 0.44, s * 0.78, s * 0.58], radius=s * 0.02,
                        outline=(216, 48, 40), width=int(s * 0.020))


def p_trophy(d, s):
    """優勝カップ。ホンダ回のマン島TT。"""
    cx = s * 0.5
    d.polygon([(cx - s * 0.20, s * 0.20), (cx + s * 0.20, s * 0.20),
               (cx + s * 0.13, s * 0.52), (cx - s * 0.13, s * 0.52)],
              fill=(238, 196, 72), outline=(150, 112, 26), width=int(s * 0.016))
    for sgn in (-1, 1):
        d.arc([cx + sgn * 0.20 * s - s * 0.11, s * 0.20,
               cx + sgn * 0.20 * s + s * 0.11, s * 0.40],
              0, 360, fill=(238, 196, 72), width=int(s * 0.026))
    d.rectangle([cx - s * 0.05, s * 0.52, cx + s * 0.05, s * 0.64],
                fill=(216, 172, 50))
    d.rounded_rectangle([cx - s * 0.22, s * 0.64, cx + s * 0.22, s * 0.80],
                        radius=s * 0.02, fill=(140, 96, 44),
                        outline=(92, 62, 26), width=int(s * 0.014))
    d.rectangle([cx - s * 0.14, s * 0.68, cx + s * 0.14, s * 0.76],
                fill=(232, 220, 196))


def p_keicar(d, s):
    """てんとう虫（スバル360）。角を落とした丸い軽自動車を横から。"""
    x0, y1 = s * 0.10, s * 0.66
    w, h = s * 0.80, s * 0.30
    d.ellipse([x0, y1 - h, x0 + w, y1 + h * 0.34], fill=(232, 198, 96),
              outline=(146, 116, 44), width=int(s * 0.018))
    d.ellipse([x0 + w * 0.18, y1 - h * 0.94, x0 + w * 0.82, y1 - h * 0.22],
              fill=(178, 210, 234), outline=(146, 116, 44), width=int(s * 0.014))
    d.line([x0 + w * 0.5, y1 - h * 0.94, x0 + w * 0.5, y1 - h * 0.22],
           fill=(146, 116, 44), width=int(s * 0.014))
    for cx in (x0 + w * 0.24, x0 + w * 0.78):
        d.ellipse([cx - s * 0.085, y1 + h * 0.02, cx + s * 0.085, y1 + h * 0.62],
                  fill=(46, 46, 52))
        d.ellipse([cx - s * 0.034, y1 + h * 0.20, cx + s * 0.034, y1 + h * 0.44],
                  fill=(188, 192, 200))
    d.ellipse([x0 + w * 0.93, y1 - h * 0.52, x0 + w * 1.02, y1 - h * 0.28],
              fill=(252, 242, 190), outline=(150, 130, 60), width=int(s * 0.01))


def p_propeller(d, s):
    """機首とプロペラ。中島飛行機の記号。"""
    import math as _m
    cx, cy = s * 0.44, s * 0.50
    d.polygon([(cx, cy), (cx + s * 0.40, cy - s * 0.13),
               (cx + s * 0.40, cy + s * 0.13)],
              fill=(158, 164, 174), outline=(92, 98, 110), width=int(s * 0.014))
    for a in (-72, 48, 168):
        d.polygon([(cx, cy),
                   (cx + _m.cos(_m.radians(a)) * s * 0.05,
                    cy + _m.sin(_m.radians(a)) * s * 0.40),
                   (cx + _m.cos(_m.radians(a + 14)) * s * 0.05,
                    cy + _m.sin(_m.radians(a + 14)) * s * 0.40)],
                  fill=(120, 126, 138), outline=(80, 86, 96), width=int(s * 0.01))
    d.ellipse([cx - s * 0.055, cy - s * 0.075, cx + s * 0.055, cy + s * 0.075],
              fill=(96, 100, 110), outline=(60, 64, 74), width=int(s * 0.012))


def p_rotor(d, s):
    """ロータリーの断面。おにぎり型のローターと繭型ハウジング。赤い点がアペックスシール。"""
    import math as _m
    cx, cy, r = s * 0.5, s * 0.5, s * 0.34
    pts = []
    for i in range(120):
        t = i / 120 * 2 * _m.pi
        rr = r * (1.0 + 0.30 * _m.cos(2 * t))
        pts.append((cx + _m.cos(t) * rr, cy + _m.sin(t) * rr * 0.78))
    d.polygon(pts, fill=(58, 62, 74), outline=(150, 156, 168))
    tri = []
    for i in range(3):
        a = i * 2 * _m.pi / 3 - _m.pi / 2
        tri.append((cx + _m.cos(a) * r * 0.72, cy + _m.sin(a) * r * 0.56))
    d.polygon(tri, fill=(206, 212, 222), outline=(110, 116, 128), width=int(s * 0.016))
    for (px, py) in tri:
        d.ellipse([px - r * 0.10, py - r * 0.10, px + r * 0.10, py + r * 0.10],
                  fill=(236, 88, 56), outline=(140, 36, 20), width=int(s * 0.012))
    d.ellipse([cx - r * 0.16, cy - r * 0.16, cx + r * 0.16, cy + r * 0.16],
              fill=(96, 100, 112), outline=(150, 156, 168), width=int(s * 0.012))


def p_scratch(d, s):
    """波打った摺動面（悪魔の爪痕）。等間隔の波と、その下の地の線。"""
    import math as _m
    base = s * 0.52
    pts = [(s * 0.12 + i * s * 0.036, base - s * 0.10 * _m.sin(i * 0.9))
           for i in range(21)]
    d.line([s * 0.10, base + s * 0.18, s * 0.90, base + s * 0.18],
           fill=(120, 120, 128), width=int(s * 0.022))
    d.line(pts, fill=(228, 60, 50), width=int(s * 0.034), joint="curve")
    for i in range(0, 21, 2):
        px, py = pts[i]
        d.line([px, py, px, base + s * 0.18], fill=(196, 196, 202),
               width=int(s * 0.008))
    for i in range(1, 20, 4):                 # 爪の記号
        px, py = pts[i]
        d.line([px - s * 0.02, py - s * 0.10, px + s * 0.02, py - s * 0.16],
               fill=(228, 60, 50), width=int(s * 0.014))


def p_parcel(d, s):
    """伝票を貼った段ボール箱。宅急便回。"""
    x0, y0, x1, y1 = s * 0.16, s * 0.28, s * 0.84, s * 0.80
    d.polygon([(x0, y0), (x1, y0), (x1 - s * 0.08, y0 - s * 0.13),
               (x0 + s * 0.08, y0 - s * 0.13)], fill=(214, 178, 128))
    d.rectangle([x0, y0, x1, y1], fill=(196, 158, 108),
                outline=(132, 100, 60), width=int(s * 0.014))
    d.line([x0, y0 + (y1 - y0) * 0.02, x1, y0 + (y1 - y0) * 0.02],
           fill=(132, 100, 60), width=int(s * 0.012))
    # ガムテープ
    d.rectangle([(x0 + x1) / 2 - s * 0.045, y0 - s * 0.13,
                 (x0 + x1) / 2 + s * 0.045, y1], fill=(224, 200, 156))
    # 伝票
    d.rectangle([x0 + s * 0.06, y0 + s * 0.14, x0 + s * 0.34, y0 + s * 0.40],
                fill=(250, 248, 240), outline=(150, 146, 138), width=int(s * 0.01))
    for k in range(3):
        d.line([x0 + s * 0.09, y0 + s * (0.19 + 0.06 * k),
                x0 + s * 0.31, y0 + s * (0.19 + 0.06 * k)],
               fill=(180, 176, 168), width=int(s * 0.012))


def p_gavel(d, s):
    """法廷の木槌。宅急便回。監督官庁を訴えた場面。"""
    import math as _m
    ang = _m.radians(-26)
    cx, cy = s * 0.52, s * 0.42
    hw, hh = s * 0.26, s * 0.13
    for dx, dy in ((0, 0),):
        pts = []
        for px, py in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)):
            pts.append((cx + px * _m.cos(ang) - py * _m.sin(ang) + dx,
                        cy + px * _m.sin(ang) + py * _m.cos(ang) + dy))
        d.polygon(pts, fill=(150, 106, 62), outline=(90, 62, 34),
                  width=int(s * 0.014))
    # 柄
    d.line([cx + s * 0.06, cy + s * 0.06, cx + s * 0.40, cy + s * 0.42],
           fill=(150, 106, 62), width=int(s * 0.07))
    d.line([cx + s * 0.06, cy + s * 0.06, cx + s * 0.40, cy + s * 0.42],
           fill=(186, 140, 88), width=int(s * 0.036))
    # 台
    d.rounded_rectangle([s * 0.16, s * 0.78, s * 0.72, s * 0.90], radius=s * 0.02,
                        fill=(126, 88, 50), outline=(80, 54, 28), width=int(s * 0.014))


def p_hoe(d, s):
    """鍬。山一回。高校を出たあと三年間、畑にいたことの記号。"""
    d.line([s * 0.30, s * 0.82, s * 0.66, s * 0.20], fill=(148, 106, 62),
           width=int(s * 0.075))
    d.line([s * 0.30, s * 0.82, s * 0.66, s * 0.20], fill=(186, 140, 84),
           width=int(s * 0.045))
    d.polygon([(s * 0.20, s * 0.76), (s * 0.40, s * 0.70),
               (s * 0.46, s * 0.90), (s * 0.26, s * 0.96)],
              fill=(150, 156, 166), outline=(78, 84, 94), width=int(s * 0.012))
    d.polygon([(s * 0.22, s * 0.80), (s * 0.38, s * 0.75),
               (s * 0.41, s * 0.85), (s * 0.25, s * 0.90)], fill=(184, 190, 200))
    for k in range(3):                       # 土
        d.ellipse([s * (0.16 + 0.10 * k), s * 0.95, s * (0.26 + 0.10 * k), s * 1.0],
                  fill=(122, 96, 66))


def p_ledger(d, s):
    """簿冊の山。山一回。帳簿に載っていない借金＝隠された一冊。"""
    for k in range(3):
        y = s * (0.66 - 0.16 * k)
        col = [(58, 74, 118), (128, 116, 70), (150, 62, 54)][k]
        d.rounded_rectangle([s * (0.18 + 0.02 * k), y, s * (0.82 - 0.02 * k),
                             y + s * 0.15], radius=s * 0.012, fill=col,
                            outline=(40, 34, 30), width=int(s * 0.01))
        d.rectangle([s * (0.22 + 0.02 * k), y + s * 0.03,
                     s * (0.78 - 0.02 * k), y + s * 0.05], fill=(240, 238, 230))
    # いちばん上に、赤い印を押した一枚
    d.polygon([(s * 0.30, s * 0.14), (s * 0.76, s * 0.10),
               (s * 0.80, s * 0.44), (s * 0.34, s * 0.48)],
              fill=(248, 246, 238), outline=(150, 146, 138), width=int(s * 0.01))
    for k in range(4):
        d.line([s * 0.36, s * (0.19 + 0.055 * k), s * 0.72, s * (0.175 + 0.055 * k)],
               fill=(176, 172, 164), width=int(s * 0.014))
    d.ellipse([s * 0.56, s * 0.24, s * 0.82, s * 0.44], outline=(206, 40, 38),
              width=int(s * 0.022))


def p_mics(d, s):
    """マイクの束。山一回。会見の記号（社名は描かない）。"""
    for k in range(5):
        f = (k - 2) / 2.0
        tx = s * (0.5 + f * 0.17)
        ty = s * (0.22 + abs(f) * 0.06)
        d.line([s * (0.5 + f * 0.05), s * 0.86, tx, ty + s * 0.06],
               fill=(78, 82, 96), width=int(s * 0.026))
        d.ellipse([tx - s * 0.055, ty - s * 0.055, tx + s * 0.055, ty + s * 0.055],
                  fill=(46, 48, 60), outline=(150, 154, 168), width=int(s * 0.012))
        d.rounded_rectangle([tx - s * 0.03, ty + s * 0.05, tx + s * 0.03,
                             ty + s * 0.13], radius=s * 0.012, fill=(64, 68, 82))
    d.rounded_rectangle([s * 0.24, s * 0.84, s * 0.76, s * 0.94], radius=s * 0.02,
                        fill=(58, 52, 56), outline=(30, 26, 30), width=int(s * 0.012))


def p_goban(d, s):
    """碁盤。QR回。昼休みの囲碁が「縦横で読む」発想の元になった。"""
    m = s * 0.13
    d.rounded_rectangle([m, m, s - m, s - m], radius=s * 0.02,
                        fill=(226, 186, 106), outline=(120, 84, 30), width=int(s * 0.012))
    n, sp = 8, (s - 2 * m) / 8
    for i in range(n + 1):
        v = m + sp * i
        d.line([m, v, s - m, v], fill=(70, 48, 18), width=int(s * 0.008))
        d.line([v, m, v, s - m], fill=(70, 48, 18), width=int(s * 0.008))
    r = sp * 0.42
    for gx, gy, col in ((2, 2, 0), (3, 3, 1), (4, 2, 0), (5, 4, 1), (3, 5, 0), (6, 5, 1)):
        cx, cy = m + sp * gx, m + sp * gy
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=(24, 24, 26) if col == 0 else (250, 250, 250),
                  outline=(60, 44, 20), width=int(s * 0.006))


def p_chocolate(d, s):
    """板チョコ。カッターナイフ回。刃を折るという発想の元そのもの。"""
    m, k = s * 0.16, s * 0.68
    d.rounded_rectangle([m + s * 0.03, m + s * 0.04, m + k + s * 0.03, m + k * 0.72 + s * 0.04],
                        radius=s * 0.02, fill=(74, 42, 22))
    d.rounded_rectangle([m, m, m + k, m + k * 0.72], radius=s * 0.02,
                        fill=(126, 74, 36), outline=(58, 32, 16), width=int(s * 0.01))
    cw, ch = k / 4, k * 0.72 / 3
    for r in range(3):
        for c in range(4):
            x, y = m + cw * c, m + ch * r
            d.rounded_rectangle([x + s * 0.014, y + s * 0.014,
                                 x + cw - s * 0.014, y + ch - s * 0.014],
                                radius=s * 0.012, fill=(150, 92, 44),
                                outline=(66, 36, 18), width=int(s * 0.008))
    # 折り取った1片
    d.rounded_rectangle([m + k * 0.86, m + k * 0.60, m + k * 1.16, m + k * 0.86],
                        radius=s * 0.012, fill=(150, 92, 44),
                        outline=(58, 32, 16), width=int(s * 0.01))


def p_gamewatch(d, s):
    """ゲーム＆ウオッチ。横井回。ゲームボーイの前段にある「薄い箱」。"""
    w, h = s * 0.74, s * 0.46
    x0, y0 = (s - w) / 2, (s - h) / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=s * 0.05,
                        fill=(196, 30, 34), outline=(90, 12, 14), width=int(s * 0.012))
    d.rounded_rectangle([x0 + w * 0.24, y0 + h * 0.16, x0 + w * 0.76, y0 + h * 0.70],
                        radius=s * 0.02, fill=(158, 174, 122), outline=(52, 60, 40),
                        width=int(s * 0.01))
    for i in range(3):                       # 液晶のドット絵
        d.rectangle([x0 + w * (0.30 + 0.14 * i), y0 + h * 0.30,
                     x0 + w * (0.36 + 0.14 * i), y0 + h * 0.56], fill=(46, 54, 36))
    ax, ay, a = x0 + w * 0.13, y0 + h * 0.46, s * 0.05   # 十字ボタン
    d.rectangle([ax - a * 0.34, ay - a, ax + a * 0.34, ay + a], fill=(40, 40, 44))
    d.rectangle([ax - a, ay - a * 0.34, ax + a, ay + a * 0.34], fill=(40, 40, 44))
    for k in range(2):
        bx = x0 + w * (0.85 + 0.07 * k)
        d.ellipse([bx - s * 0.028, ay - s * 0.028, bx + s * 0.028, ay + s * 0.028],
                  fill=(250, 210, 60), outline=(90, 70, 10), width=int(s * 0.008))


def p_ajibottle(d, s):
    """味の素の卓上瓶。うま味回。赤いキャップで一目で分かる（ロゴは描かない）。"""
    w, h = s * 0.36, s * 0.56
    x0, y0 = (s - w) / 2, (s - h) / 2 + s * 0.04
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=s * 0.04,
                        fill=(246, 246, 248), outline=(120, 120, 128), width=int(s * 0.012))
    d.rounded_rectangle([x0 + w * 0.14, y0 - h * 0.20, x0 + w * 0.86, y0 + h * 0.06],
                        radius=s * 0.02, fill=(210, 32, 34), outline=(110, 14, 16),
                        width=int(s * 0.012))
    for c in range(3):                       # 振り出し穴
        d.ellipse([x0 + w * (0.30 + 0.18 * c) - s * 0.012, y0 - h * 0.15,
                   x0 + w * (0.30 + 0.18 * c) + s * 0.012, y0 - h * 0.10],
                  fill=(120, 14, 16))
    d.rounded_rectangle([x0 + w * 0.10, y0 + h * 0.30, x0 + w * 0.90, y0 + h * 0.72],
                        radius=s * 0.015, fill=(214, 34, 36))
    for c in range(2):
        d.line([x0 + w * 0.20, y0 + h * (0.44 + 0.16 * c),
                x0 + w * 0.80, y0 + h * (0.44 + 0.16 * c)],
               fill=(255, 255, 255), width=int(s * 0.014))


def p_quartzfork(d, s):
    """音叉型の水晶振動子。クオーツ回。腕時計の中で震えている本体。"""
    cx = s * 0.5
    top, bot = s * 0.20, s * 0.80
    d.rounded_rectangle([cx - s * 0.10, bot - s * 0.16, cx + s * 0.10, bot],
                        radius=s * 0.02, fill=(190, 194, 202),
                        outline=(90, 94, 104), width=int(s * 0.01))
    for sgn in (-1, 1):                       # 2本の腕
        x = cx + sgn * s * 0.075
        d.rounded_rectangle([x - s * 0.035, top, x + s * 0.035, bot - s * 0.10],
                            radius=s * 0.03, fill=(232, 234, 240),
                            outline=(90, 94, 104), width=int(s * 0.01))
    for k in range(3):                        # 振動の波
        r = s * (0.20 + 0.07 * k)
        d.arc([cx - r, s * 0.42 - r, cx + r, s * 0.42 + r], 200, 340,
              fill=(255, 214, 40), width=int(s * 0.016))


def p_stomach(d, s):
    """胃のシルエット＋中を照らす光。胃カメラ回。"""
    cx, cy = s * 0.48, s * 0.52
    d.polygon([(cx - s * 0.06, cy - s * 0.34), (cx + s * 0.12, cy - s * 0.30),
               (cx + s * 0.26, cy - s * 0.02), (cx + s * 0.18, cy + s * 0.26),
               (cx - s * 0.08, cy + s * 0.32), (cx - s * 0.24, cy + s * 0.12),
               (cx - s * 0.20, cy - s * 0.14)],
              fill=(226, 130, 128), outline=(150, 50, 54), width=int(s * 0.016))
    d.rounded_rectangle([cx - s * 0.10, cy - s * 0.46, cx - s * 0.01, cy - s * 0.28],
                        radius=s * 0.02, fill=(214, 112, 110),
                        outline=(150, 50, 54), width=int(s * 0.014))
    d.ellipse([cx - s * 0.04, cy - s * 0.06, cx + s * 0.10, cy + s * 0.08],
              fill=(255, 244, 170), outline=(200, 160, 40), width=int(s * 0.012))
    for a in (215, 250, 285, 320):            # 光
        import math as _m
        d.line([cx + s * 0.03, cy + s * 0.01,
                cx + s * 0.03 + _m.cos(_m.radians(a)) * s * 0.24,
                cy + s * 0.01 + _m.sin(_m.radians(a)) * s * 0.24],
               fill=(255, 240, 150), width=int(s * 0.014))


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


def p_shutter(d, s):
    """閉まったシャッターと南京錠。ダイエー回の「消えた」の絵。

    転落を下降グラフで描くとカップ麺回の p_downgraph と同じ絵になり、
    一覧に並んだとき同じ回に見える（2026-09-14）。小物は回ごとに新造する。
    店が閉まった一枚絵のほうが「消えた」に直接効く。
    """
    d.rounded_rectangle([s*0.06, s*0.08, s*0.94, s*0.80], radius=s*0.02,
                        fill=(176, 180, 188), outline=(48, 48, 54), width=int(s*0.030))
    # 波板のスリット。実寸でシャッターと分かる唯一の手がかりなので太く
    y = s*0.15
    while y < s*0.76:
        d.line([s*0.09, y, s*0.91, y], fill=(126, 130, 140), width=int(s*0.020))
        y += s*0.075
    d.rounded_rectangle([s*0.03, s*0.78, s*0.97, s*0.88], radius=s*0.02,
                        fill=(62, 62, 70), outline=(30, 30, 36), width=int(s*0.020))
    # 南京錠（閉店の記号）
    d.arc([s*0.42, s*0.80, s*0.58, s*0.94], 180, 360,
          fill=(232, 232, 236), width=int(s*0.036))
    d.rounded_rectangle([s*0.38, s*0.88, s*0.62, s*1.00], radius=s*0.02,
                        fill=(236, 196, 40), outline=(70, 56, 8), width=int(s*0.022))


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


# 168px（スマホ一覧の実寸）で読める文字数の上限。**超えると _fit_lines が
# 黙って縮めて潰れる**ので、生成時に警告を出して台本側を直させる（2026-09-12）
# 吹き出しは**1行のみ**。2行にすると1行あたりの高さが半分になり、
# 168px では黄ラベルだけが読めて吹き出しが読めない状態になる（実測）
LEN_SAY, LEN_LABEL = 8, 8
_len_warn = []


def _budget(kind, text, limit, key=""):
    body = text.replace("|", "")
    if len(body) > limit:
        _len_warn.append(f"  {key:<20} {kind:<6} {len(body):>2}字 {text}")


def _bubble(dr, box, text, tail_x=None):
    """白い吹き出し。**これが3コマ型の主役**（2026-09-02）。

    最初に作った版はコマに黄ラベル1個だけで、名詞が3つ並んでいるだけだった。
    伸びている局は例外なく「吹き出しのセリフ」＋「黄ラベルの意味づけ」の2層で、
    3コマ読むと話が分かる。ラベルだけでは物語にならない。
    """
    x0, y0, x1, y1 = box
    # 1行化したので改行指定「|」は無視する。**残っていると _wrap_chars が
    # そこで切り、1行目しか描かれない**（ホンダ回が「車に」だけになった 2026-09-12）
    f, lines = _fit_lines(text.replace("|", ""), "w9", (x1 - x0) - 26, 78, 40, 1)
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
    """2コマ構成（ビフォー→アフター）。

    経緯（読み違えを2回やっているので全部残す）:
      1. 最初の1枚絵（layout_stack）は CTR 1.3%・0.8% で目安2〜10%の下限割れ。
      2. 伸びている局のサムネを16枚並べ「3〜4コマ＋各コマにラベル」を真似て3コマ型にした。
         このとき「情報を足すほど実寸で読めなくなる」という以前の見立てを誤りと判断した。
      3. **これも誤りだった**（2026-09-12・ユーザー指摘「3分割わかりづらい／真ん中いらない」）。
         実際に168pxへ縮めて数えたら、載っている9要素（吹き出し3・黄ラベル3・タグ3）が
         全部つぶれ、読めるのは見出しだけだった。コマ数を真似ても、
         **1コマの幅が421pxしかなければ中の文字は届かない**。
         競合が3〜4コマでも成立していたのは、1コマに文字を1個しか置いていないから。

    したがって今の型は「コマは2つ・1コマの中身も減らす」:
      - 左＝問題／右＝結果。真ん中の転機は見出し側で言う（コマにすると3つ目の情報になる）
      - 1コマ幅 421→636px。吹き出しもラベルも実寸で読める大きさまで上げた
      - 文字数の上限をコードで持つ（吹き出し1行8字・ラベル10字）。
        広げた分を長い文で埋め戻したら同じことになる
      - 見出しは w9（角ゴ極太）。851（殴り書き）は端が崩れてホラーの題字に見える
        （同ユーザー指摘）。成功譚に不穏な字面を当てない、は genkai について
        書いていたルールだが、851 も実寸では同じ失敗をしていた
    """
    headline = spec["headline"]
    panels = spec["panels"]
    if len(panels) > 2:
        # **落とすのは真ん中**。頭2つを取ると結末のコマが消えて見出しの答えが無くなる。
        # ただし題材そのもの（見出しに出てくる物）が真ん中にある回は keep で拾う。
        # 例: 「カッターナイフの答えは板チョコ」の板チョコ、「タコを見て靴を作った」のタコ
        a, b = spec.get("keep", (0, -1))
        panels = [panels[a], panels[b]]
    n = len(panels)

    img = Image.new("RGBA", (W, H), (16, 14, 18, 255))

    HEAD_H = int(H * 0.21)
    body_top = HEAD_H
    ph = H - body_top
    gap = 8
    pw = (W - gap * (n - 1)) // n

    # タグ（年・場所の小さい黒ラベル）は廃止した。168pxでは一度も読めた例がなく、
    # 読めない要素はコマを狭くするだけの純損失だった（2026-09-12）
    LAB_H, BUB_H, TAG_H = 112, 112, 0
    lab_y = ph - LAB_H - 12
    bub_y = lab_y - BUB_H - 14

    for i, pn in enumerate(panels):
        x0 = i * (pw + gap)
        cell = Image.new("RGBA", (pw, ph), (*pn.get("bg", (60, 60, 68)), 255))
        cd = ImageDraw.Draw(cell, "RGBA")
        for k in range(-ph, pw + ph, 64):
            cd.polygon([(k, ph), (k + 16, ph), (k + 16 + ph, 0), (k + ph, 0)],
                       fill=(255, 255, 255, 22))

        art_top, art_bot = TAG_H - 6, bub_y - 6
        art_h = art_bot - art_top
        # **立ち絵は外側・小物は内側**。3コマ時代は逆（小物が外）だったが、
        # 2コマだと立ち絵どうしが中央の継ぎ目でくっつき、同じ顔が2つ並んだ
        # 一つの塊に見えた（2026-09-12）。小物を内側に寄せると、
        # 矢印を挟んで「前の道具 → 後の道具」が一直線に読める
        right = i % 2 == 1
        has_prop = bool(pn.get("prop") and globals().get(pn["prop"]))
        # **立ち絵は小物があるならコマの端で切る**。中に丸ごと収めると小物が隠れ上が空く。
        # 小物が無いコマは逆に大きく中央へ（伸びている局も、山場のコマは顔だけで持たせる）
        bu = bust(spec.get("who", "zundamon"), pn.get("emo", "surprised"),
                  height=int(art_h * (0.78 if has_prop else 1.0)), crop=0.42)
        if not right:                       # 内側を向かせる（3コマ同じ絵に見せない）
            bu = bu.transpose(Image.FLIP_LEFT_RIGHT)
        bx = (pw - int(bu.width * 0.66) if right else -int(bu.width * 0.34)) \
            if has_prop else (pw - bu.width) // 2

        def _burst(gcx, gcy):
            glow = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            for t in range(24):
                ang = t * 15.0
                gd.polygon([(gcx, gcy),
                            (gcx + math.cos(math.radians(ang)) * 900,
                             gcy + math.sin(math.radians(ang)) * 900),
                            (gcx + math.cos(math.radians(ang + 7)) * 900,
                             gcy + math.sin(math.radians(ang + 7)) * 900)],
                           fill=(255, 255, 255, 26))
            cell.alpha_composite(glow)

        if has_prop:
            pl = prop_layer(globals()[pn["prop"]], size=520, tilt=-8)
            sc = min(pw * 0.70 / pl.width, art_h * 1.0 / pl.height)
            pl = pl.resize((max(1, int(pl.width * sc)), max(1, int(pl.height * sc))),
                           Image.LANCZOS)
            px = int(pw * 0.03) if right else pw - pl.width - int(pw * 0.03)
            py = art_top + (art_h - pl.height) // 2
            _burst(px + pl.width // 2, py + pl.height // 2)
            cell.alpha_composite(pl, (px, py))
        else:
            _burst(pw // 2, art_top + art_h // 2)

        cell.alpha_composite(bu, (bx, art_bot - bu.height))

        if pn.get("say"):
            _budget("say", pn["say"], LEN_SAY, spec.get("_key", ""))
            # 矢印が来る側は空けておく（詰めると矢印が吹き出しの黒フチに埋もれる）
            bl = 44 if i > 0 else 10
            br = pw - (44 if i < n - 1 else 10)
            _bubble(cd, (bl, bub_y, br, bub_y + BUB_H), pn["say"],
                    tail_x=br - 80 if right else bl + 80)

        lab = pn.get("label", "")
        if lab:
            _budget("label", lab, LEN_LABEL, spec.get("_key", ""))
            f, _ = _fit_lines(lab, "w9", pw - 40, 84, 38, 1)
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
    # **w9（角ゴ極太）で組む。851 は使わない**（2026-09-12・ユーザー指摘
    # 「上の文字がなんでホラーみたいな形なの」）。851チカラヅヨクは端が欠けた
    # 殴り書きなので、暗い地＋赤黒フチと合わさると恐怖映画の題字になる。
    # SKILL.md には「genkai は不穏なので成功譚に使わない」とだけ書いていたが、
    # 851 も同じ穴だった。見出しは字形で語らせず、大きさと2色だけで押す。
    size = 132
    while size > 60 and sum(_tw(font("w9", size), t) for t, _ in segs) > W - 44:
        size -= 4
    f = font("w9", size)
    x = (W - sum(_tw(f, t) for t, _ in segs)) // 2
    y = (HEAD_H - int(size * 1.16)) // 2
    for t, c in segs:
        _ttext(d, (x, y), t, f, c, stroke_width=max(6, size // 16),
               stroke_fill=(12, 10, 14))
        x += _tw(f, t)
    return img.convert("RGB")


# ---------------------------------------------------------------- 対立型（2026-10-11）
# 調査（docs/再生を伸ばす調査_2026-10-11.md）で、伸びている同ジャンル15枚のうち11枚が
# 「相手の台詞の吹き出し」、10枚が before→after、表情はコマで激変（ドヤ→青ざめ）、
# 色は赤・黒・黄だった。2コマ型（layout_panels）は吹き出しが本人の薄い独り言
# （「マークなのだ」）、表情の差が小さい、地が茶と灰、の3点で外れていた。
# 立ち絵は6表情しか無い（PSD 無し）ので、青ざめ・汗・キラキラ・怒りマークを上から描いて差を付ける。
PANEL_BG = {
    "dark": ((18, 20, 34), (52, 24, 40)),     # 窮地。黒〜暗い赤紫
    "red": ((196, 22, 28), (255, 120, 20)),   # 逆転・衝撃。赤〜橙の集中線
    "yellow": ((255, 196, 20), (255, 240, 120)),
    "blue": ((14, 40, 96), (40, 110, 190)),   # 冷たい結末（転落回の右コマ）
}


def _panel_bg(pw, ph, kind):
    c0, c1 = PANEL_BG.get(kind, PANEL_BG["dark"])
    img = Image.new("RGBA", (pw, ph), (*c0, 255))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = pw * 0.5, ph * 0.45
    for t in range(36):                       # 集中線
        a0 = math.radians(t * 10)
        a1 = math.radians(t * 10 + 4.5)
        d.polygon([(cx, cy), (cx + math.cos(a0) * 1400, cy + math.sin(a0) * 1400),
                   (cx + math.cos(a1) * 1400, cy + math.sin(a1) * 1400)],
                  fill=(*c1, 70))
    glow = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([pw * 0.15, ph * 0.1, pw * 0.85, ph * 0.8], fill=(*c1, 90))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    return img


def _fx(bu, kind, inner_left=False):
    """立ち絵に効果を重ねる。座標は bust(crop=0.40) の顔位置に合わせてある。
    汗・キラキラ・「!?」はコマの内側（画面中央寄り）に置く。外側はコマの端で切れる。"""
    if not kind:
        return bu
    w, h = bu.size

    def X(fx):                                 # 内側が左なら左右を反転
        return w * (1 - fx) if inner_left else w * fx
    out = bu.copy()
    d = ImageDraw.Draw(out, "RGBA")
    if kind == "gloom":                       # 青ざめ: 額から下へ青、頭の上に縦線
        tint = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        td = ImageDraw.Draw(tint)
        for y in range(int(h * 0.12), int(h * 0.56)):
            t = (y - h * 0.12) / (h * 0.44)
            al = int(175 * min(1.0, t / 0.25) * (1 - max(0.0, t - 0.25) / 0.75))
            td.line([(0, y), (w, y)], fill=(70, 60, 200, max(0, al)))
        mask = bu.split()[3]
        tint.putalpha(Image.composite(tint.split()[3], Image.new("L", (w, h), 0), mask))
        out.alpha_composite(tint)
        d = ImageDraw.Draw(out, "RGBA")
        for k in range(6):
            x = w * (0.34 + k * 0.064)
            d.line([(x, h * 0.24), (x, h * 0.40)], fill=(40, 30, 120, 235), width=max(5, w // 60))
        kind = "sweat"
    if kind == "sweat":
        for (fx, fy, s) in ((0.80, 0.30, 0.07), (0.86, 0.42, 0.05)):
            x, y, r = X(fx), h * fy, w * s
            d.polygon([(x, y - r * 1.6), (x - r * 0.7, y), (x + r * 0.7, y)], fill=(120, 200, 255, 255))
            d.ellipse([x - r * 0.7, y - r * 0.7, x + r * 0.7, y + r * 0.7], fill=(120, 200, 255, 255),
                      outline=(20, 60, 140, 255), width=3)
    elif kind == "sparkle":                   # ドヤ: 頭のまわりにキラキラ
        for (fx, fy, s) in ((0.12, 0.18, 0.10), (0.88, 0.14, 0.12), (0.92, 0.46, 0.07), (0.06, 0.48, 0.07)):
            x, y, r = X(fx), h * fy, w * s
            pts = []
            for i in range(8):
                a = math.radians(i * 45)
                rr = r if i % 2 == 0 else r * 0.28
                pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
            d.polygon(pts, fill=(255, 236, 60, 255), outline=(120, 70, 0, 255))
    elif kind == "anger":                     # 怒りマーク
        x, y, r = X(0.78), h * 0.16, w * 0.09
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            d.arc([x + sx * r * 0.2 - r * 0.6, y + sy * r * 0.2 - r * 0.6,
                   x + sx * r * 0.2 + r * 0.6, y + sy * r * 0.2 + r * 0.6],
                  start={(-1, -1): 0, (1, -1): 90, (-1, 1): 270, (1, 1): 180}[(sx, sy)],
                  end={(-1, -1): 90, (1, -1): 180, (-1, 1): 360, (1, 1): 270}[(sx, sy)],
                  fill=(230, 20, 30, 255), width=max(6, w // 40))
    elif kind == "shock":                     # 衝撃: 頭の横に「!?」と放射線
        f = font("w9", int(w * 0.22))
        tx = X(0.70) - (f.getlength("!?") if inner_left else 0)
        d.text((tx, h * 0.10), "!?", font=f, fill=(255, 230, 40, 255),
               stroke_width=8, stroke_fill=(20, 10, 10, 255))
    return out


def _shout(dr, box, text, by=""):
    """ギザギザの叫び吹き出し（相手の怒鳴り・宣告）。"""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    pts = []
    n = 22
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1.12 if i % 2 == 0 else 0.90
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    dr.polygon(pts, fill=(255, 255, 255), outline=(18, 14, 12), width=6)
    f, lines = _fit_lines(text, "w9", int(rx * 1.55), 86, 40, 1)
    _ttext(dr, (cx - _tw(f, lines[0]) / 2, cy - f.size * 0.62), lines[0], f, (210, 18, 24))
    if by:
        fb = font("w9", 30)
        bw = _tw(fb, by) + 24
        dr.rounded_rectangle([x0 + 6, y0 - 18, x0 + 6 + bw, y0 + 26], radius=8, fill=(18, 14, 12))
        _ttext(dr, (x0 + 18, y0 - 16), by, fb, (255, 255, 255))


def layout_conflict(spec):
    """対立型2コマ。見出し（問いか対立）＋各コマに吹き出し1つ・表情の差・ラベル1つ。"""
    panels = spec["panels"]
    img = Image.new("RGBA", (W, H), (10, 10, 12, 255))
    HEAD_H = int(H * 0.22)
    gap = 10
    pw = (W - gap) // 2
    ph = H - HEAD_H
    LAB_H = 104
    lab_y = ph - LAB_H - 10
    for i, pn in enumerate(panels[:2]):
        right = i == 1
        cell = _panel_bg(pw, ph, pn.get("bg", "dark" if i == 0 else "red"))
        has_prop = bool(pn.get("prop") and globals().get(pn["prop"]))
        art_bot = lab_y - 4
        # 立ち絵は大きく外側。顔が168pxでも見える大きさまで上げる
        bu = bust(spec.get("who", "zundamon"), pn.get("emo", "surprised"),
                  height=int(ph * 0.68), crop=0.40)
        if not right:
            bu = bu.transpose(Image.FLIP_LEFT_RIGHT)
        bu = _fx(bu, pn.get("fx"), inner_left=right)
        if has_prop:
            pl = prop_layer(globals()[pn["prop"]], size=520, tilt=-8 if right else 8)
            sc = min(pw * 0.58 / pl.width, ph * 0.50 / pl.height)
            pl = pl.resize((max(1, int(pl.width * sc)), max(1, int(pl.height * sc))), Image.LANCZOS)
            px = int(pw * 0.02) if right else pw - pl.width - int(pw * 0.02)
            py = art_bot - pl.height - 6
            cell.alpha_composite(pl, (px, py))
        bx = (pw - int(bu.width * 0.78)) if right else -int(bu.width * 0.22)
        if not has_prop:
            bx = (pw - bu.width) // 2
        cell.alpha_composite(bu, (bx, art_bot - bu.height))
        cd = ImageDraw.Draw(cell, "RGBA")
        say = pn.get("say", "")
        if say:
            _budget("say", say, LEN_SAY, spec.get("_key", ""))
            bw_ = int(pw * 0.74)
            bx0 = (pw - bw_ - 14) if not right else 14
            if not has_prop:
                bx0 = (pw - bw_) // 2
            box = (bx0, 18, bx0 + bw_, 18 + 124)
            if pn.get("shout"):
                _shout(cd, box, say, pn.get("by", ""))
            else:
                _bubble(cd, box, say, tail_x=(box[2] - 90) if right else (box[0] + 90))
                if pn.get("by"):
                    fb = font("w9", 30)
                    bw2 = _tw(fb, pn["by"]) + 24
                    cd.rounded_rectangle([box[0] + 6, box[1] - 16, box[0] + 6 + bw2, box[1] + 28],
                                         radius=8, fill=(18, 14, 12))
                    _ttext(cd, (box[0] + 18, box[1] - 14), pn["by"], fb, (255, 255, 255))
        lab = pn.get("label", "")
        if lab:
            _budget("label", lab, LEN_LABEL, spec.get("_key", ""))
            f, _ = _fit_lines(lab, "w9", pw - 40, 84, 38, 1)
            fill = (255, 214, 40) if not right else (255, 255, 255)
            cd.rounded_rectangle([8, lab_y, pw - 8, lab_y + LAB_H], radius=8,
                                 fill=fill, outline=(20, 14, 6), width=6)
            # 数字は赤で抜く（「1000万台」「0台」が一番先に目に入るように）
            x = (pw - _tw(f, lab)) // 2
            y = lab_y + (LAB_H - int(f.size * 1.22)) // 2
            for ch in lab:
                col = (214, 20, 26) if (ch.isdigit() or ch in "万億千百%") else (20, 14, 6)
                cd.text((x, y), ch, font=f, fill=col)
                x += f.getlength(ch) * (0.52 if ch in "、。" else 1)
        img.alpha_composite(cell, (i * (pw + gap), HEAD_H))
    # 中央の矢印（黄に黒フチ）
    d = ImageDraw.Draw(img)
    ax, ay = pw + gap // 2, HEAD_H + int(ph * 0.52)
    d.polygon([(ax - 46, ay - 60), (ax + 50, ay), (ax - 46, ay + 60)],
              fill=(255, 214, 40), outline=(14, 10, 6), width=6)
    # 見出し。1語だけ黄（head_hi_color で赤にもできる）
    d.rectangle([0, 0, W, HEAD_H], fill=(8, 8, 10))
    headline, hi = spec["headline"], spec.get("head_hi", "")
    base_c, hi_c = (255, 255, 255), spec.get("head_hi_color", (255, 214, 40))
    segs = [(headline, base_c)]
    if hi and hi in headline:
        a, b = headline.split(hi, 1)
        segs = [(t, c) for t, c in ((a, base_c), (hi, hi_c), (b, base_c)) if t]
    size = 136
    while size > 60 and sum(_tw(font("w9", size), t) for t, _ in segs) > W - 40:
        size -= 4
    f = font("w9", size)
    x = (W - sum(_tw(f, t) for t, _ in segs)) // 2
    y = (HEAD_H - int(size * 1.16)) // 2
    for t, c in segs:
        _ttext(d, (x, y), t, f, c, stroke_width=max(6, size // 14), stroke_fill=(0, 0, 0))
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

# コマの地色。**1枚のうち必ず1コマは明るい色にする**（3コマとも暗いと実寸で沈む）
def p_ykbox(d, s):
    """潰れた店に残っていた木箱。中身は半端なファスナー。
    実在の意匠は描かず、木箱と覗いた金具だけで「売れ残り」を出す。"""
    d.polygon([(s * 0.12, s * 0.40), (s * 0.88, s * 0.40),
               (s * 0.80, s * 0.90), (s * 0.20, s * 0.90)],
              fill=(150, 116, 80), outline=(104, 78, 52), width=int(s * 0.026))
    d.rectangle([s * 0.20, s * 0.56, s * 0.80, s * 0.64], fill=(120, 92, 62))
    # 開いた蓋
    d.polygon([(s * 0.10, s * 0.40), (s * 0.90, s * 0.40),
               (s * 0.84, s * 0.26), (s * 0.16, s * 0.26)],
              fill=(168, 134, 96), outline=(104, 78, 52), width=int(s * 0.022))
    # はみ出した半製品
    for i, x in enumerate((0.30, 0.48, 0.66)):
        d.rectangle([s * x, s * (0.30 + i * 0.01), s * (x + 0.06), s * 0.42],
                    fill=(216, 212, 200), outline=(158, 152, 140), width=int(s * 0.012))


def p_ykzip(d, s):
    """ファスナー。左右の務歯がかみ合い、下にスライダー。"""
    for side in (0, 1):
        x0 = s * (0.22 if side == 0 else 0.56)
        d.rectangle([x0, s * 0.10, x0 + s * 0.22, s * 0.66], fill=(206, 202, 192),
                    outline=(150, 146, 136), width=int(s * 0.016))
        for k in range(7):
            y = s * (0.14 + k * 0.072)
            d.rectangle([x0 + (s * 0.16 if side == 0 else 0), y,
                         x0 + (s * 0.24 if side == 0 else s * 0.08), y + s * 0.042],
                        fill=(178, 182, 188), outline=(132, 136, 142), width=int(s * 0.010))
    # スライダー
    d.rounded_rectangle([s * 0.34, s * 0.62, s * 0.66, s * 0.80], radius=s * 0.04,
                        fill=(170, 176, 182), outline=(120, 126, 132), width=int(s * 0.018))
    d.rounded_rectangle([s * 0.42, s * 0.78, s * 0.58, s * 0.94], radius=s * 0.03,
                        fill=(150, 156, 162), outline=(110, 116, 122), width=int(s * 0.016))


def p_cpbowl(d, s):
    """草原の器。内モンゴルでふるまわれた、乳を発酵させた白い食べもの。
    民族意匠は特定できないので、無地の木の器と白い中身だけで描く。"""
    # 168pxに縮めると中身が見えないと「ただの容器」になる。
    # 器を浅くして、白い液面を面積で見せる（実寸で確認して調整した）
    d.polygon([(s * 0.10, s * 0.46), (s * 0.90, s * 0.46),
               (s * 0.74, s * 0.88), (s * 0.26, s * 0.88)],
              fill=(150, 116, 80))
    d.ellipse([s * 0.08, s * 0.34, s * 0.92, s * 0.58], fill=(168, 132, 92),
              outline=(112, 86, 58), width=int(s * 0.026))
    d.ellipse([s * 0.14, s * 0.37, s * 0.86, s * 0.55], fill=(250, 250, 246))
    d.ellipse([s * 0.30, s * 0.41, s * 0.52, s * 0.47], fill=(232, 234, 230))
    d.polygon([(s * 0.26, s * 0.88), (s * 0.74, s * 0.88),
               (s * 0.69, s * 0.94), (s * 0.31, s * 0.94)], fill=(112, 86, 58))


def p_cpbottle(d, s):
    """乳酸菌飲料の瓶。**実在の青い水玉は商標の意匠なので描かない。**
    無地のラベルと白い中身だけで「白い飲み物の瓶」と分かるようにする。"""
    d.rounded_rectangle([s * 0.30, s * 0.26, s * 0.70, s * 0.92], radius=s * 0.06,
                        fill=(228, 230, 226), outline=(150, 154, 150),
                        width=int(s * 0.020))
    d.rounded_rectangle([s * 0.35, s * 0.40, s * 0.65, s * 0.87], radius=s * 0.04,
                        fill=(250, 250, 248))
    d.rectangle([s * 0.43, s * 0.10, s * 0.57, s * 0.28], fill=(216, 218, 214),
                outline=(150, 154, 150), width=int(s * 0.016))
    d.rectangle([s * 0.40, s * 0.04, s * 0.60, s * 0.13], fill=(70, 96, 150))
    d.rectangle([s * 0.32, s * 0.52, s * 0.68, s * 0.70], fill=(252, 252, 250),
                outline=(158, 162, 158), width=int(s * 0.016))


def p_nttrunk(d, s):
    """旅行用のトランク。蓋を開けて、中の仕切り板を見せる。
    縮めても「箱の中に壁がある」と分かるよう、仕切りを明るい色で太く描く。"""
    d.rectangle([s * 0.10, s * 0.46, s * 0.90, s * 0.88], fill=(132, 88, 56),
                outline=(88, 58, 36), width=int(s * 0.026))
    d.rectangle([s * 0.16, s * 0.50, s * 0.84, s * 0.84], fill=(96, 64, 42))
    d.rectangle([s * 0.46, s * 0.50, s * 0.54, s * 0.84], fill=(236, 212, 150),
                outline=(170, 140, 90), width=int(s * 0.012))       # 仕切り板
    d.polygon([(s * 0.10, s * 0.46), (s * 0.90, s * 0.46),
               (s * 0.84, s * 0.16), (s * 0.16, s * 0.16)],
              fill=(150, 104, 66), outline=(88, 58, 36), width=int(s * 0.024))  # 開いた蓋
    for y in (0.62, 0.78):                                           # 革のベルト
        d.rectangle([s * 0.10, s * y, s * 0.16, s * (y + 0.05)], fill=(70, 46, 30))
        d.rectangle([s * 0.84, s * y, s * 0.90, s * (y + 0.05)], fill=(70, 46, 30))
    d.rectangle([s * 0.44, s * 0.86, s * 0.56, s * 0.93], fill=(200, 170, 90),
                outline=(130, 104, 50), width=int(s * 0.010))       # 留め金


def p_nttower(d, s):
    """赤と白の電波塔。裾が広がり、上に行くほど細くなるトラス。"""
    # 先端がコマの上端で切れないよう、塔体は0.18から始めてアンテナを細く足す
    cx, yb, yt = s * 0.5, s * 0.94, s * 0.18
    d.line([(cx, s * 0.06), (cx, yt)], fill=(220, 70, 40), width=max(2, int(s * 0.014)))
    n = 10
    for i in range(n):
        ya = yb - (yb - yt) * i / n
        y2 = yb - (yb - yt) * (i + 1) / n
        ta, tb = i / n, (i + 1) / n
        wa = s * (0.02 + 0.28 * (1 - ta) ** 1.8)
        wb = s * (0.02 + 0.28 * (1 - tb) ** 1.8)
        col = (220, 70, 40) if i % 2 == 0 else (250, 246, 238)
        w = max(2, int(s * 0.03 * (1 - ta * 0.6)))
        d.polygon([(cx - wa, ya), (cx - wb, y2), (cx + wb, y2), (cx + wa, ya)],
                  outline=col, width=w)
        d.line([(cx - wa, ya), (cx + wb, y2)], fill=col, width=max(2, w - 2))
        d.line([(cx + wa, ya), (cx - wb, y2)], fill=col, width=max(2, w - 2))
    d.rectangle([cx - s * 0.08, s * 0.60, cx + s * 0.08, s * 0.66],
                fill=(250, 246, 238), outline=(200, 190, 176), width=int(s * 0.008))  # 展望台


def _gd_bowl(d, s, full):
    """丼。実在チェーンの器の柄や配色は描かず、黒い丼だけにする。"""
    d.pieslice([s * 0.12, s * 0.30, s * 0.88, s * 0.92], 0, 180, fill=(44, 42, 48),
               outline=(20, 20, 24), width=int(s * 0.02))
    d.ellipse([s * 0.10, s * 0.46, s * 0.90, s * 0.70], fill=(66, 62, 68),
              outline=(20, 20, 24), width=int(s * 0.02))
    if full:
        # 肉は縁の内側に収める（盛り上げると茶色の塊に見えた）。
        # 玉ねぎと紅しょうがで、縮めても牛丼と分かるようにする
        d.ellipse([s * 0.14, s * 0.44, s * 0.86, s * 0.68], fill=(150, 92, 54))
        for k in range(4):                                         # 肉のひだ
            x = s * (0.27 + k * 0.13)
            d.arc([x - s * 0.08, s * 0.47, x + s * 0.08, s * 0.61], 200, 340,
                  fill=(96, 56, 32), width=int(s * 0.022))
        for k in range(3):                                         # 玉ねぎ
            x = s * (0.30 + k * 0.15)
            d.arc([x - s * 0.06, s * 0.50, x + s * 0.06, s * 0.60], 190, 350,
                  fill=(240, 236, 210), width=int(s * 0.018))
        d.ellipse([s * 0.64, s * 0.48, s * 0.78, s * 0.56], fill=(220, 50, 60))   # 紅しょうが
    else:
        d.ellipse([s * 0.15, s * 0.50, s * 0.85, s * 0.66], fill=(236, 236, 230))


def p_gdempty(d, s):
    """牛丼が消えた日の、空の丼。"""
    _gd_bowl(d, s, False)


def p_gdbowl(d, s):
    """牛肉の乗った丼。縮めても「牛丼」と分かるよう肉を面で見せる。"""
    _gd_bowl(d, s, True)


def p_hsfield(d, s):
    """森になる前の代々木。奥へすぼまる畑の畝と、小さな芽。
    長方形で描くと看板の板に見えたので、台形の地面にして奥行きを出す。"""
    d.polygon([(s * 0.02, s * 0.94), (s * 0.98, s * 0.94), (s * 0.78, s * 0.40), (s * 0.22, s * 0.40)],
              fill=(176, 150, 96))
    for k in range(6):                                             # 奥へすぼまる畝
        xb = s * (0.08 + k * 0.17)
        xt = s * (0.26 + k * 0.10)
        d.line([(xb, s * 0.94), (xt, s * 0.40)], fill=(130, 104, 62), width=int(s * 0.022))
    for (x, y, r) in ((0.30, 0.78, 0.035), (0.52, 0.66, 0.03), (0.70, 0.80, 0.035), (0.44, 0.52, 0.025)):
        d.ellipse([s * (x - r), s * (y - r), s * (x + r), s * (y + r)], fill=(96, 160, 80))  # 芽
    d.rectangle([s * 0.08, s * 0.18, s * 0.92, s * 0.40], fill=(190, 214, 230))        # 空
def p_hsforest(d, s):
    """深い森。丸い樹冠を重ねた常緑広葉樹の森。"""
    for (cx, cy, r, col) in ((0.26, 0.40, 0.22, (60, 110, 64)), (0.74, 0.40, 0.22, (60, 110, 64)),
                             (0.50, 0.28, 0.26, (72, 128, 72)), (0.34, 0.56, 0.22, (48, 96, 54)),
                             (0.66, 0.56, 0.22, (48, 96, 54))):
        d.ellipse([s * (cx - r), s * (cy - r), s * (cx + r), s * (cy + r)], fill=col,
                  outline=(34, 70, 40), width=int(s * 0.012))
    for x in (0.34, 0.50, 0.66):                                   # 幹
        d.rectangle([s * (x - 0.03), s * 0.66, s * (x + 0.03), s * 0.92], fill=(100, 76, 52))


def p_ktstick(d, s):
    """最初の棒状の蚊取り線香。細い緑の棒を3本立て、先に火。"""
    d.rectangle([s * 0.20, s * 0.84, s * 0.80, s * 0.94], fill=(150, 150, 156),
                outline=(110, 110, 116), width=int(s * 0.014))             # 灰皿
    for k, x in enumerate((0.36, 0.50, 0.64)):
        top = s * (0.20 + k * 0.05)
        d.rectangle([s * (x - 0.025), top, s * (x + 0.025), s * 0.86], fill=(90, 130, 84),
                    outline=(60, 96, 58), width=int(s * 0.008))
        d.ellipse([s * (x - 0.035), top - s * 0.035, s * (x + 0.035), top + s * 0.02],
                  fill=(255, 130, 50))


def p_ktcoil(d, s):
    """渦巻きの蚊取り線香。外端に火。商標の意匠は描かない。"""
    import math as _m
    pts = []
    for i in range(301):
        t = i / 300
        ang = t * 4.2 * 2 * _m.pi
        rr = s * 0.40 * (1 - t * 0.84)
        pts.append((s * 0.5 + rr * _m.cos(ang), s * 0.52 + rr * _m.sin(ang) * 0.92))
    d.line(pts, fill=(80, 124, 78), width=int(s * 0.05), joint="curve")
    d.ellipse([s * 0.86, s * 0.47, s * 0.96, s * 0.57], fill=(255, 130, 50))


def p_srdish(d, s):
    """培養皿を重ねた絵。上の皿にだけ、生き残った菌の粒。"""
    for k, y in enumerate((0.78, 0.60, 0.42)):
        d.ellipse([s * 0.14, s * (y - 0.10), s * 0.86, s * (y + 0.10)], fill=(214, 224, 220),
                  outline=(130, 146, 142), width=int(s * 0.016))
        d.ellipse([s * 0.20, s * (y - 0.07), s * 0.80, s * (y + 0.07)], fill=(236, 226, 190))
    for x, y in ((0.40, 0.41), (0.56, 0.44), (0.48, 0.38)):
        d.ellipse([s * (x - 0.03), s * (y - 0.02), s * (x + 0.03), s * (y + 0.02)], fill=(230, 170, 60))


def p_csgear(d, s):
    """歯車で動く大きな計算機。"""
    import math as _m
    d.rectangle([s * 0.12, s * 0.30, s * 0.88, s * 0.92], fill=(120, 116, 110), outline=(70, 66, 62),
                width=int(s * 0.016))
    for cx, cy, r in ((0.36, 0.56, 0.16), (0.62, 0.66, 0.12), (0.62, 0.42, 0.09)):
        pts = []
        for i in range(32):
            a = i / 32 * 2 * _m.pi
            rr = r * (1.0 if i % 2 == 0 else 0.8)
            pts.append((s * (cx + rr * _m.cos(a)), s * (cy + rr * _m.sin(a))))
        d.polygon(pts, fill=(196, 170, 90), outline=(120, 100, 50))
        d.ellipse([s * (cx - r * 0.25), s * (cy - r * 0.25), s * (cx + r * 0.25), s * (cy + r * 0.25)],
                  fill=(120, 100, 50))


def p_csrelay(d, s):
    """リレーを並べた計算機の中身。細長い箱が整列し、上に数字の窓。"""
    d.rectangle([s * 0.10, s * 0.14, s * 0.90, s * 0.92], fill=(200, 204, 200), outline=(120, 124, 120),
                width=int(s * 0.016))
    d.rectangle([s * 0.16, s * 0.20, s * 0.84, s * 0.32], fill=(40, 44, 40))
    for r in range(4):
        for c in range(6):
            x, y = 0.18 + c * 0.11, 0.40 + r * 0.12
            d.rectangle([s * x, s * y, s * (x + 0.07), s * (y + 0.09)], fill=(180, 110, 60),
                        outline=(120, 70, 36), width=int(s * 0.008))


def p_csmini(d, s):
    """手のひらサイズの電卓。緑の数字窓と4列のキー。"""
    d.rounded_rectangle([s * 0.24, s * 0.10, s * 0.76, s * 0.92], radius=int(s * 0.04),
                        fill=(70, 74, 80), outline=(40, 42, 46), width=int(s * 0.014))
    d.rectangle([s * 0.30, s * 0.17, s * 0.70, s * 0.32], fill=(24, 40, 30))
    for i in range(6):
        x = 0.33 + i * 0.06
        d.rectangle([s * x, s * 0.21, s * (x + 0.035), s * 0.28], fill=(90, 230, 150))
    for r in range(5):
        for c in range(4):
            x, y = 0.30 + c * 0.10, 0.40 + r * 0.10
            col = (230, 120, 60) if c == 3 else (226, 226, 220)
            d.rounded_rectangle([s * x, s * y, s * (x + 0.08), s * (y + 0.075)],
                                radius=int(s * 0.012), fill=col)


def p_frnoise(d, s):
    """雑音だらけの記録紙。線がぐちゃぐちゃ。"""
    d.rectangle([s * 0.08, s * 0.16, s * 0.92, s * 0.88], fill=(236, 230, 210), outline=(150, 140, 120),
                width=int(s * 0.014))
    import random as _r
    rnd = _r.Random(1947)
    for k in range(7):
        y = 0.28 + k * 0.08
        pts = [(s * (0.12 + i * 0.042), s * (y + rnd.uniform(-0.06, 0.06))) for i in range(20)]
        d.line(pts, fill=(80, 70, 130), width=int(s * 0.01))


def p_frschool(d, s):
    """群れが映った記録紙。雲のような濃い影と海底の線。"""
    d.rectangle([s * 0.08, s * 0.16, s * 0.92, s * 0.88], fill=(236, 230, 210), outline=(150, 140, 120),
                width=int(s * 0.014))
    d.ellipse([s * 0.26, s * 0.34, s * 0.74, s * 0.58], fill=(70, 60, 120))
    d.ellipse([s * 0.32, s * 0.30, s * 0.60, s * 0.46], fill=(70, 60, 120))
    d.line([(s * 0.10, s * 0.76), (s * 0.40, s * 0.72), (s * 0.70, s * 0.78), (s * 0.90, s * 0.74)],
           fill=(90, 70, 110), width=int(s * 0.03))


def p_anhard(d, s):
    """硬くて売れない西洋パン（細長い塊）。"""
    d.rounded_rectangle([s * 0.10, s * 0.40, s * 0.90, s * 0.74], radius=int(s * 0.17), fill=(170, 116, 64),
                        outline=(110, 72, 36), width=int(s * 0.016))
    for k in range(3):
        x = 0.28 + k * 0.22
        d.line([(s * (x - 0.05), s * 0.47), (s * (x + 0.05), s * 0.66)], fill=(214, 164, 104), width=int(s * 0.03))


def p_anpan(d, s):
    """へそに桜の塩漬けをのせた、丸いあんぱん。"""
    d.ellipse([s * 0.10, s * 0.30, s * 0.90, s * 0.84], fill=(196, 124, 60), outline=(140, 84, 36),
              width=int(s * 0.016))
    d.ellipse([s * 0.20, s * 0.36, s * 0.56, s * 0.56], fill=(220, 156, 90))
    d.ellipse([s * 0.40, s * 0.48, s * 0.60, s * 0.64], fill=(240, 150, 172), outline=(200, 110, 130),
              width=int(s * 0.01))


def p_kkjelly(d, s):
    """溶けかけた透明の人工クラゲ（皿の上）。"""
    d.ellipse([s * 0.10, s * 0.62, s * 0.90, s * 0.86], fill=(236, 240, 244), outline=(170, 180, 190),
              width=int(s * 0.014))
    d.ellipse([s * 0.22, s * 0.56, s * 0.78, s * 0.76], fill=(200, 226, 240), outline=(150, 190, 214),
              width=int(s * 0.012))
    for k in range(4):
        x = 0.30 + k * 0.12
        d.line([(s * x, s * 0.60), (s * (x + 0.04), s * 0.72)], fill=(236, 246, 252), width=int(s * 0.02))
    d.ellipse([s * 0.62, s * 0.34, s * 0.74, s * 0.50], fill=(120, 80, 50))        # 醤油のしずく


def p_kkstick(d, s):
    """刻んだ身と、赤と白のカニカマ。"""
    for k in range(3):
        y = 0.30 + k * 0.14
        d.rounded_rectangle([s * 0.12, s * y, s * 0.88, s * (y + 0.10)], radius=int(s * 0.05),
                            fill=(248, 244, 236), outline=(190, 180, 170), width=int(s * 0.01))
        d.rounded_rectangle([s * 0.12, s * y, s * 0.88, s * (y + 0.05)], radius=int(s * 0.03), fill=(220, 70, 56))
    for k in range(8):
        x = 0.16 + k * 0.09
        d.line([(s * x, s * 0.80), (s * (x + 0.05), s * 0.86)], fill=(248, 244, 236), width=int(s * 0.025))


def p_oscap(d, s):
    """牛乳瓶の紙のフタ。3枚重ねて、片面に黒い紙。"""
    for k in range(3):
        x, y = 0.10 + k * 0.28, 0.50
        for j in range(3):
            yy = y - j * 0.03
            d.ellipse([s * x, s * yy, s * (x + 0.24), s * (yy + 0.16)], fill=(150, 146, 136))
            d.ellipse([s * x, s * (yy - 0.02), s * (x + 0.24), s * (yy + 0.14)],
                      fill=(24, 24, 26) if (k == 1 and j == 2) else (248, 246, 238))
        if k != 1:
            d.ellipse([s * (x + 0.03), s * (y - 0.07), s * (x + 0.21), s * (y + 0.05)],
                      outline=(90, 130, 200), width=int(s * 0.012))
    d.rectangle([s * 0.18, s * 0.74, s * 0.82, s * 0.84], fill=(24, 24, 26))      # 黒い紙


def p_osboard(d, s):
    """緑の盤に黒と白の石。"""
    x0, y0, w = s * 0.12, s * 0.22, s * 0.76
    d.rectangle([x0 - s * 0.03, y0 - s * 0.03, x0 + w + s * 0.03, y0 + w + s * 0.03], fill=(30, 30, 30))
    d.rectangle([x0, y0, x0 + w, y0 + w], fill=(38, 120, 70))
    c = w / 8
    for i in range(9):
        d.line([(x0 + i * c, y0), (x0 + i * c, y0 + w)], fill=(22, 80, 46), width=max(1, int(s * 0.006)))
        d.line([(x0, y0 + i * c), (x0 + w, y0 + i * c)], fill=(22, 80, 46), width=max(1, int(s * 0.006)))
    st = {(3, 3): 1, (4, 4): 1, (3, 4): 0, (4, 3): 0, (2, 3): 0, (2, 4): 1, (5, 2): 0, (4, 5): 1}
    for (r, cc), wht in st.items():
        x, y = x0 + (cc + 0.5) * c, y0 + (r + 0.5) * c
        rr = c * 0.4
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(244, 242, 236) if wht else (24, 24, 26))


def p_wmheavy(d, s):
    """重い録音機と、大きな黒いヘッドホン。"""
    d.rounded_rectangle([s * 0.08, s * 0.50, s * 0.56, s * 0.86], radius=int(s * 0.03),
                        fill=(176, 178, 184), outline=(90, 92, 98), width=int(s * 0.012))
    for k in range(3):
        d.ellipse([s * (0.14 + k * 0.13), s * 0.56, s * (0.22 + k * 0.13), s * 0.64], fill=(60, 60, 64))
    d.rectangle([s * 0.14, s * 0.70, s * 0.50, s * 0.78], fill=(40, 44, 50))
    d.arc([s * 0.46, s * 0.14, s * 0.94, s * 0.66], 190, 350, fill=(40, 40, 44), width=int(s * 0.05))
    for x in (0.46, 0.84):
        d.rounded_rectangle([s * (x - 0.04), s * 0.34, s * (x + 0.12), s * 0.58], radius=int(s * 0.04),
                            fill=(30, 30, 34))


def p_wmwalk(d, s):
    """青い再生機と、オレンジの軽いヘッドホン。"""
    d.rounded_rectangle([s * 0.10, s * 0.34, s * 0.46, s * 0.86], radius=int(s * 0.03),
                        fill=(70, 110, 170), outline=(40, 60, 90), width=int(s * 0.012))
    d.rounded_rectangle([s * 0.15, s * 0.42, s * 0.41, s * 0.62], radius=int(s * 0.02), fill=(30, 36, 44))
    for x in (0.22, 0.34):
        d.ellipse([s * (x - 0.03), s * 0.49, s * (x + 0.03), s * 0.55], outline=(200, 200, 200),
                  width=int(s * 0.008))
    d.ellipse([s * 0.30, s * 0.70, s * 0.38, s * 0.78], fill=(240, 140, 40))
    d.arc([s * 0.50, s * 0.22, s * 0.92, s * 0.70], 190, 350, fill=(150, 156, 166), width=int(s * 0.02))
    for x in (0.52, 0.90):
        d.ellipse([s * (x - 0.06), s * 0.44, s * (x + 0.06), s * 0.58], fill=(240, 140, 40))


def p_tgfish(d, s):
    """パソコンの画面の中で泳ぐ熱帯魚。"""
    d.rounded_rectangle([s * 0.10, s * 0.14, s * 0.90, s * 0.74], radius=int(s * 0.04), fill=(214, 208, 190),
                        outline=(150, 144, 130), width=int(s * 0.012))
    d.rectangle([s * 0.17, s * 0.20, s * 0.83, s * 0.66], fill=(30, 90, 150))
    for fx, fy, c in ((0.26, 0.30, (240, 140, 40)), (0.52, 0.46, (240, 220, 60)), (0.62, 0.28, (120, 220, 200))):
        d.ellipse([s * fx, s * fy, s * (fx + 0.14), s * (fy + 0.07)], fill=c)
        d.polygon([(s * fx, s * (fy + 0.035)), (s * (fx - 0.05), s * fy), (s * (fx - 0.05), s * (fy + 0.07))], fill=c)
    d.rectangle([s * 0.42, s * 0.74, s * 0.58, s * 0.82], fill=(190, 184, 168))
    d.rectangle([s * 0.26, s * 0.82, s * 0.74, s * 0.87], fill=(200, 196, 180))


def p_tgegg(d, s):
    """卵形の携帯ゲーム機。画面に小さなお墓（文字なし）。"""
    col = (236, 120, 150)
    d.ellipse([s * 0.16, s * 0.20, s * 0.84, s * 0.94], fill=col, outline=(170, 80, 100), width=int(s * 0.014))
    d.ellipse([s * 0.24, s * 0.10, s * 0.76, s * 0.60], fill=col)
    d.rounded_rectangle([s * 0.30, s * 0.32, s * 0.70, s * 0.62], radius=int(s * 0.02), fill=(250, 248, 240))
    d.rectangle([s * 0.34, s * 0.35, s * 0.66, s * 0.59], fill=(186, 200, 170))
    ink = (40, 46, 40)
    d.rounded_rectangle([s * 0.37, s * 0.42, s * 0.49, s * 0.57], radius=int(s * 0.05), fill=ink)   # 墓石
    d.rectangle([s * 0.35, s * 0.55, s * 0.51, s * 0.58], fill=ink)
    d.rectangle([s * 0.423, s * 0.45, s * 0.437, s * 0.53], fill=(186, 200, 170))      # 墓石の十字
    d.rectangle([s * 0.40, s * 0.475, s * 0.46, s * 0.489], fill=(186, 200, 170))
    d.ellipse([s * 0.53, s * 0.37, s * 0.63, s * 0.47], fill=(250, 250, 250), outline=ink, width=2)  # おばけ
    d.polygon([(s * 0.53, s * 0.42), (s * 0.63, s * 0.42), (s * 0.64, s * 0.53), (s * 0.60, s * 0.50),
               (s * 0.58, s * 0.54), (s * 0.55, s * 0.50), (s * 0.52, s * 0.53)], fill=(250, 250, 250), outline=ink)
    d.polygon([(s * 0.555, s * 0.375), (s * 0.605, s * 0.375), (s * 0.58, s * 0.405)], fill=ink)      # 三角の布
    d.ellipse([s * 0.555, s * 0.42, s * 0.565, s * 0.43], fill=ink)
    d.ellipse([s * 0.595, s * 0.42, s * 0.605, s * 0.43], fill=ink)
    for k in (-1, 0, 1):
        bx, by, r = s * (0.5 + k * 0.13), s * (0.76 + (0 if k else 0.03)), s * 0.035
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(250, 214, 80), outline=(160, 130, 40), width=2)


def p_mgroom(d, s):
    """7畳の部屋の作業台に置いた、レンズの付いた恒星球。"""
    d.rectangle([s * 0.10, s * 0.74, s * 0.90, s * 0.80], fill=(120, 100, 80))
    d.rectangle([s * 0.16, s * 0.80, s * 0.22, s * 0.96], fill=(100, 84, 66))
    d.rectangle([s * 0.78, s * 0.80, s * 0.84, s * 0.96], fill=(100, 84, 66))
    cx, cy, r = s * 0.5, s * 0.40, s * 0.24
    d.rectangle([cx - s * 0.03, cy + r, cx + s * 0.03, s * 0.74], fill=(80, 80, 90))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 64, 76), outline=(30, 30, 36), width=int(s * 0.01))
    for i in range(-2, 3):
        for j in range(-2, 3):
            if i * i + j * j <= 5:
                x, y, rr = cx + i * r * 0.36, cy + j * r * 0.36, r * 0.12
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(170, 200, 230))


def p_mgdome(d, s):
    """星でいっぱいのドーム。天の川も星の粒。"""
    import random
    d.chord([s * 0.04, s * 0.16, s * 0.96, s * 1.08], 180, 360, fill=(14, 18, 44))
    rnd = random.Random(7)
    for _ in range(900):
        x, y = rnd.uniform(s * 0.08, s * 0.92), rnd.uniform(s * 0.20, s * 0.60)
        if (x - s * 0.5) ** 2 / (s * 0.46) ** 2 + (y - s * 0.62) ** 2 / (s * 0.46) ** 2 > 1:
            continue
        r = rnd.random() ** 4 * s * 0.008 + 1
        d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 250, 255))
    for _ in range(700):
        t = rnd.uniform(-1, 1)
        x, y = s * 0.5 + t * s * 0.4, s * 0.40 - t * s * 0.12 + rnd.gauss(0, s * 0.03)
        if (x - s * 0.5) ** 2 / (s * 0.46) ** 2 + (y - s * 0.62) ** 2 / (s * 0.46) ** 2 > 1 or y > s * 0.60:
            continue
        d.ellipse([x - 1.2, y - 1.2, x + 1.2, y + 1.2], fill=(210, 214, 255))
    d.rectangle([s * 0.04, s * 0.60, s * 0.96, s * 0.66], fill=(30, 32, 50))


def p_sprou(d, s):
    """水たまりに落ちて、花のように開いた白いロウ。"""
    d.ellipse([s * 0.10, s * 0.50, s * 0.90, s * 0.90], fill=(80, 110, 160))
    import math
    for cx, cy, r in ((s * 0.38, s * 0.66, s * 0.10), (s * 0.62, s * 0.72, s * 0.08), (s * 0.50, s * 0.58, s * 0.07)):
        for k in range(5):
            a = k * 2 * math.pi / 5
            x, y = cx + r * math.cos(a), cy + r * 0.6 * math.sin(a)
            d.ellipse([x - r * 0.7, y - r * 0.45, x + r * 0.7, y + r * 0.45], fill=(250, 248, 240))
        d.ellipse([cx - r * 0.3, cy - r * 0.2, cx + r * 0.3, cy + r * 0.2], fill=(240, 230, 200))
    d.rectangle([s * 0.47, s * 0.12, s * 0.53, s * 0.40], fill=(250, 246, 236))   # ろうそく
    d.ellipse([s * 0.46, s * 0.02, s * 0.54, s * 0.13], fill=(255, 200, 80))


def p_spomu(d, s):
    """皿の上の、シワのあるオムレツ（ケチャップつき）。"""
    d.ellipse([s * 0.06, s * 0.58, s * 0.94, s * 0.86], fill=(250, 250, 246), outline=(190, 190, 186), width=int(s * 0.01))
    d.chord([s * 0.16, s * 0.26, s * 0.84, s * 0.86], 180, 360, fill=(246, 206, 80), outline=(210, 160, 50), width=int(s * 0.012))
    d.rectangle([s * 0.16, s * 0.54, s * 0.84, s * 0.58], fill=(246, 206, 80))
    for k in range(4):
        x = s * (0.30 + k * 0.13)
        d.arc([x - s * 0.05, s * 0.36, x + s * 0.05, s * 0.50], 200, 340, fill=(200, 150, 50), width=int(s * 0.012))
    d.line([(s * 0.30, s * 0.40), (s * 0.50, s * 0.34), (s * 0.70, s * 0.40)], fill=(200, 40, 30), width=int(s * 0.03))


def _yagi(d, x0, x1, y, h, col, w):
    """横から見た八木アンテナ。左端が反射器、右へ導波器が短くなっていく。"""
    d.line([(x0, y), (x1, y)], fill=col, width=w)
    n = 6
    for k in range(n):
        x = x0 + (x1 - x0) * k / (n - 1)
        hh = h * (1.0 if k == 0 else 0.86 if k == 1 else 0.74 - 0.05 * (k - 2))
        d.line([(x, y - hh / 2), (x, y + hh / 2)], fill=col, width=w)


def p_fxleaf(d, s):
    """緑の葉と赤い紅葉、その横に試験管。"""
    import math
    def leaf(cx, cy, r, col):
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=col)
        d.line([(cx, cy), (cx, cy + r * 1.1)], fill=(110, 70, 40), width=int(s * 0.012))
    leaf(s * 0.28, s * 0.36, s * 0.20, (90, 160, 70))
    leaf(s * 0.52, s * 0.50, s * 0.22, (220, 50, 40))
    d.rounded_rectangle([s * 0.74, s * 0.18, s * 0.86, s * 0.84], radius=int(s * 0.06), outline=(160, 170, 180), width=int(s * 0.015))
    d.rounded_rectangle([s * 0.755, s * 0.50, s * 0.845, s * 0.83], radius=int(s * 0.045), fill=(220, 60, 50))


def p_fxpen(d, s):
    """ボールペンと、途中から消えた線。"""
    d.line([(s * 0.08, s * 0.30), (s * 0.48, s * 0.30)], fill=(40, 50, 90), width=int(s * 0.03))
    for k in range(5):
        x = s * (0.52 + k * 0.08)
        d.line([(x, s * 0.30), (x + s * 0.04, s * 0.30)], fill=(200, 205, 220), width=int(s * 0.03))
    d.rounded_rectangle([s * 0.14, s * 0.56, s * 0.86, s * 0.68], radius=int(s * 0.06), fill=(40, 60, 120))
    d.polygon([(s * 0.86, s * 0.58), (s * 0.96, s * 0.62), (s * 0.86, s * 0.66)], fill=(200, 200, 206))
    d.rounded_rectangle([s * 0.04, s * 0.57, s * 0.16, s * 0.67], radius=int(s * 0.03), fill=(236, 236, 230))


def p_fcphone(d, s):
    """夜の窓と月、机の上の黒電話。"""
    d.rectangle([s * 0.08, s * 0.08, s * 0.52, s * 0.46], fill=(20, 24, 54), outline=(90, 76, 60), width=int(s * 0.02))
    d.ellipse([s * 0.34, s * 0.14, s * 0.46, s * 0.26], fill=(242, 236, 200))
    d.rectangle([s * 0.10, s * 0.80, s * 0.90, s * 0.86], fill=(110, 80, 56))
    d.rounded_rectangle([s * 0.36, s * 0.60, s * 0.84, s * 0.80], radius=int(s * 0.05), fill=(30, 30, 34))
    d.ellipse([s * 0.50, s * 0.62, s * 0.70, s * 0.79], fill=(200, 200, 200))
    d.ellipse([s * 0.57, s * 0.68, s * 0.63, s * 0.74], fill=(30, 30, 34))
    d.rounded_rectangle([s * 0.32, s * 0.50, s * 0.88, s * 0.59], radius=int(s * 0.04), fill=(30, 30, 34))


def p_fcbox(d, s):
    """回収された段ボールの山と、えんじと白のゲーム機。"""
    for r in range(3):
        for k in range(3 - r):
            x, y = s * (0.06 + k * 0.2 + r * 0.1), s * (0.62 - r * 0.17)
            d.rectangle([x, y, x + s * 0.19, y + s * 0.16], fill=(186, 150, 104), outline=(120, 90, 60), width=int(s * 0.008) + 1)
    x, y, w, h = s * 0.56, s * 0.52, s * 0.40, s * 0.16
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(s * 0.02), fill=(236, 228, 208))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(128, 30, 42))
    d.rectangle([x + w * 0.33, y - s * 0.08, x + w * 0.67, y + s * 0.01], fill=(210, 190, 60))



def p_gzsuit(d, s):
    """撮影所の床の角材と、形の分からない黒いゴムの着ぐるみ（背中のファスナーで着ぐるみと分かる）。
    怪獣のデザインは権利があるので、頭・背びれ・尻尾は描かない。"""
    body = (58, 62, 60)
    d.rounded_rectangle([s * 0.26, s * 0.16, s * 0.74, s * 0.80], radius=int(s * 0.16), fill=body)
    d.ellipse([s * 0.16, s * 0.34, s * 0.34, s * 0.52], fill=body)
    d.ellipse([s * 0.66, s * 0.34, s * 0.84, s * 0.52], fill=body)
    d.line([(s * 0.50, s * 0.22), (s * 0.50, s * 0.74)], fill=(170, 170, 170), width=int(s * 0.012) + 1)
    for k in range(9):
        y = s * (0.24 + k * 0.055)
        d.line([(s * 0.48, y), (s * 0.52, y)], fill=(170, 170, 170), width=int(s * 0.006) + 1)
    d.rectangle([s * 0.04, s * 0.82, s * 0.96, s * 0.90], fill=(176, 132, 84), outline=(110, 80, 50), width=int(s * 0.008) + 1)
    d.polygon([(s * 0.78, s * 0.06), (s * 0.96, s * 0.06), (s * 0.96, s * 0.22), (s * 0.78, s * 0.22)], fill=(236, 226, 196))
    d.rectangle([s * 0.81, s * 0.11, s * 0.93, s * 0.13], fill=(80, 70, 60))
    d.rectangle([s * 0.81, s * 0.16, s * 0.90, s * 0.18], fill=(80, 70, 60))


def p_gzqueue(d, s):
    """映画館の正面と、坂の上まで続く行列。"""
    d.polygon([(0, s * 0.92), (s, s * 0.92), (s, s * 0.80), (0, s * 0.40)], fill=(150, 140, 126))
    d.rectangle([s * 0.62, s * 0.20, s * 0.98, s * 0.86], fill=(196, 170, 130), outline=(110, 90, 66), width=int(s * 0.01) + 1)
    d.rectangle([s * 0.66, s * 0.26, s * 0.94, s * 0.40], fill=(236, 226, 196))
    d.rectangle([s * 0.72, s * 0.58, s * 0.88, s * 0.86], fill=(70, 56, 46))
    for k in range(11):
        t = k / 10
        x = s * (0.60 - t * 0.54)
        y = s * (0.80 - t * 0.36)
        r = s * (0.030 - t * 0.010)
        d.ellipse([x - r, y - r * 3.4, x + r, y - r * 1.4], fill=(40, 40, 46))
        d.rounded_rectangle([x - r * 1.3, y - r * 1.6, x + r * 1.3, y + r * 1.4], radius=int(r), fill=(60, 60, 72))


def p_yhorgan(d, s):
    """明治の足踏みオルガン（木の箱・鍵盤・ペダル）。"""
    wood, dark = (150, 96, 56), (96, 60, 34)
    d.rectangle([s * 0.16, s * 0.18, s * 0.84, s * 0.40], fill=wood, outline=dark, width=int(s * 0.012) + 1)
    d.rectangle([s * 0.10, s * 0.40, s * 0.90, s * 0.86], fill=wood, outline=dark, width=int(s * 0.012) + 1)
    d.rectangle([s * 0.14, s * 0.42, s * 0.86, s * 0.52], fill=(244, 240, 228))
    for k in range(14):
        x = s * (0.14 + 0.72 * k / 14)
        d.line([(x, s * 0.42), (x, s * 0.52)], fill=dark, width=1)
        if k % 7 not in (2, 6):
            d.rectangle([x + s * 0.03, s * 0.42, x + s * 0.055, s * 0.48], fill=(30, 30, 30))
    d.rectangle([s * 0.26, s * 0.66, s * 0.44, s * 0.80], fill=dark)
    d.rectangle([s * 0.56, s * 0.66, s * 0.74, s * 0.80], fill=dark)
    d.ellipse([s * 0.42, s * 0.24, s * 0.58, s * 0.34], fill=dark)


def p_yhpiano(d, s):
    """黒いグランドピアノを横から。"""
    blk = (24, 24, 28)
    d.polygon([(s * 0.10, s * 0.40), (s * 0.62, s * 0.40), (s * 0.90, s * 0.52), (s * 0.90, s * 0.62),
               (s * 0.10, s * 0.62)], fill=blk)
    d.line([(s * 0.12, s * 0.40), (s * 0.70, s * 0.12)], fill=blk, width=int(s * 0.03))
    d.rectangle([s * 0.10, s * 0.56, s * 0.30, s * 0.60], fill=(244, 240, 228))
    for x in (0.16, 0.48, 0.84):
        d.rectangle([s * (x - 0.02), s * 0.62, s * (x + 0.02), s * 0.88], fill=blk)


def p_pnsocket(d, s):
    """売れ残ったソケットの山と、裸電球。"""
    d.line([(s * 0.50, 0), (s * 0.50, s * 0.12)], fill=(60, 60, 60), width=int(s * 0.012) + 1)
    d.rectangle([s * 0.45, s * 0.12, s * 0.55, s * 0.20], fill=(60, 50, 40))
    d.ellipse([s * 0.40, s * 0.18, s * 0.60, s * 0.38], fill=(250, 236, 160), outline=(200, 170, 80), width=int(s * 0.008) + 1)
    for r in range(4):
        for k in range(5 - r):
            x = s * (0.10 + k * 0.17 + r * 0.085)
            y = s * (0.80 - r * 0.10)
            d.rounded_rectangle([x, y, x + s * 0.13, y + s * 0.10], radius=int(s * 0.02), fill=(70, 52, 40),
                                outline=(40, 30, 22), width=int(s * 0.006) + 1)
            d.ellipse([x + s * 0.04, y + s * 0.02, x + s * 0.09, y + s * 0.06], fill=(190, 170, 120))


def p_pnbuilding(d, s):
    """窓がたくさん並ぶ大きな会社のビル。"""
    d.rectangle([s * 0.12, s * 0.16, s * 0.88, s * 0.90], fill=(214, 220, 228), outline=(110, 120, 134), width=int(s * 0.012) + 1)
    for r in range(7):
        for k in range(6):
            x, y = s * (0.17 + k * 0.12), s * (0.21 + r * 0.095)
            d.rectangle([x, y, x + s * 0.08, y + s * 0.06], fill=(70, 110, 160))
    d.rectangle([s * 0.42, s * 0.78, s * 0.58, s * 0.90], fill=(90, 96, 106))


def p_sawasher(d, s):
    """昭和の丸い洗濯機（上から水が渦を巻く）。"""
    d.rounded_rectangle([s * 0.22, s * 0.30, s * 0.78, s * 0.86], radius=int(s * 0.10), fill=(236, 238, 240),
                        outline=(140, 146, 152), width=int(s * 0.012) + 1)
    d.ellipse([s * 0.26, s * 0.18, s * 0.74, s * 0.42], fill=(210, 214, 218), outline=(140, 146, 152), width=int(s * 0.012) + 1)
    d.ellipse([s * 0.32, s * 0.22, s * 0.68, s * 0.38], fill=(120, 170, 220))
    d.arc([s * 0.38, s * 0.25, s * 0.62, s * 0.35], 200, 520, fill=(240, 248, 255), width=int(s * 0.012) + 1)
    d.rectangle([s * 0.30, s * 0.52, s * 0.70, s * 0.58], fill=(100, 130, 170))
    for x in (0.30, 0.66):
        d.rectangle([s * x, s * 0.86, s * (x + 0.04), s * 0.92], fill=(90, 90, 96))


def p_sasign(d, s):
    """ビルの屋上の看板から、無地の文字の板をクレーンで1枚ずつ下ろす。"""
    d.rectangle([s * 0.04, s * 0.60, s * 0.70, s * 0.94], fill=(196, 200, 206), outline=(120, 124, 130), width=int(s * 0.01) + 1)
    for k in range(4):
        x = s * (0.08 + k * 0.15)
        d.rectangle([x, s * 0.70, x + s * 0.10, s * 0.80], fill=(110, 140, 180))
    d.rectangle([s * 0.06, s * 0.42, s * 0.66, s * 0.58], outline=(90, 90, 96), width=int(s * 0.01) + 1)
    for k in range(3):
        x = s * (0.10 + k * 0.17)
        d.rectangle([x, s * 0.44, x + s * 0.12, s * 0.56], fill=(30, 70, 150))
    d.line([(s * 0.86, s * 0.94), (s * 0.86, s * 0.08)], fill=(230, 170, 30), width=int(s * 0.03))
    d.line([(s * 0.86, s * 0.08), (s * 0.58, s * 0.08)], fill=(230, 170, 30), width=int(s * 0.025))
    d.line([(s * 0.62, s * 0.08), (s * 0.62, s * 0.24)], fill=(60, 60, 60), width=int(s * 0.006) + 1)
    d.rectangle([s * 0.56, s * 0.24, s * 0.68, s * 0.36], fill=(30, 70, 150))

def _tcub(d, s, body, shield, seat, demae=False):
    """サムネ用の横向きカブ（prop の座標系 0〜1）。"""
    k = s / 440
    x0, yg = 40 * k, 360 * k
    r = 62 * k
    rx, fx = x0 + 70 * k, x0 + 330 * k
    cy = yg - r
    P = lambda pts: [(x0 + a * k, cy + b * k) for a, b in pts]  # noqa: E731
    for cx in (rx, fx):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 40, 44))
        d.ellipse([cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72], outline=(170, 170, 176), width=3)
    d.polygon(P([(10, -40), (60, -112), (205, -118), (222, -48), (150, -18)]), fill=body)
    d.rounded_rectangle([x0 + 70 * k, cy - 138 * k, x0 + 205 * k, cy - 110 * k], radius=int(10 * k), fill=seat)
    d.ellipse([x0 + 165 * k, cy - 40 * k, x0 + 255 * k, cy + 8 * k], fill=(150, 150, 156))
    d.polygon(P([(205, -62), (262, -42), (302, -165), (286, -175)]), fill=body)
    d.polygon(P([(248, -14), (266, -150), (298, -182), (322, -150), (304, -18)]), fill=shield)
    d.line([(x0 + 306 * k, cy - 175 * k), (fx, cy)], fill=(90, 90, 96), width=int(8 * k) + 1)
    d.chord([fx - r * 1.08, cy - r * 1.08, fx + r * 1.08, cy + r * 1.08], 205, 335, fill=shield)
    d.polygon(P([(282, -205), (336, -210), (342, -186), (288, -182)]), fill=body)
    d.ellipse([x0 + 328 * k, cy - 210 * k, x0 + 354 * k, cy - 184 * k], fill=(250, 240, 180))
    if demae:
        d.rectangle([x0 + 30 * k, cy - 250 * k, x0 + 38 * k, cy - 120 * k], fill=(70, 70, 76))
        d.rounded_rectangle([x0 - 20 * k, cy - 320 * k, x0 + 90 * k, cy - 252 * k], radius=6, fill=(150, 90, 50),
                            outline=(100, 60, 30), width=3)


def p_scclay(d, s):
    """粘土の実物大模型（土色のカブ）。"""
    clay = (176, 146, 112)
    _tcub(d, s, clay, clay, (146, 116, 88))
    d.rectangle([s * 0.04, s * 0.84, s * 0.96, s * 0.90], fill=(110, 90, 70))


def p_sccub(d, s):
    """青いカブ。"""
    _tcub(d, s, (96, 150, 200), (238, 238, 230), (130, 40, 60))


def p_kbcar(d, s):
    """横から見た車と、車内の袋（運転席の前・天井・後ろ）。"""
    body = [(0.06, 0.74), (0.10, 0.60), (0.30, 0.57), (0.40, 0.38), (0.70, 0.38), (0.82, 0.57),
            (0.94, 0.60), (0.96, 0.74)]
    d.polygon([(s * x, s * y) for x, y in body], fill=(200, 206, 214), outline=(90, 96, 110))
    d.polygon([(s * 0.32, s * 0.57), (s * 0.41, s * 0.41), (s * 0.54, s * 0.41), (s * 0.54, s * 0.57)], fill=(236, 240, 244))
    d.polygon([(s * 0.56, s * 0.57), (s * 0.56, s * 0.41), (s * 0.69, s * 0.41), (s * 0.79, s * 0.57)], fill=(236, 240, 244))
    bag = (250, 206, 110)
    d.ellipse([s * 0.33, s * 0.44, s * 0.45, s * 0.58], fill=bag, outline=(200, 140, 40), width=3)
    d.ellipse([s * 0.40, s * 0.37, s * 0.72, s * 0.45], fill=bag, outline=(200, 140, 40), width=3)
    d.ellipse([s * 0.72, s * 0.44, s * 0.80, s * 0.58], fill=bag, outline=(200, 140, 40), width=3)
    for cx in (0.26, 0.78):
        r = 0.08
        d.ellipse([s * (cx - r), s * (0.74 - r), s * (cx + r), s * (0.74 + r)], fill=(40, 40, 44))
        d.ellipse([s * (cx - r / 2), s * (0.74 - r / 2), s * (cx + r / 2), s * (0.74 + r / 2)], fill=(170, 170, 176))


def p_kbwheel(d, s):
    """運転席から見たハンドルと、真ん中から大きくふくらんだ白い袋。"""
    cx, cy, r = s * 0.5, s * 0.70, s * 0.30
    ink = (40, 40, 46)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=int(s * 0.05))
    d.line([(cx - r, cy + s * 0.03), (cx + r, cy + s * 0.03)], fill=ink, width=int(s * 0.045))
    d.rectangle([cx - s * 0.025, cy, cx + s * 0.025, cy + r], fill=ink)
    d.ellipse([cx - s * 0.09, cy - s * 0.06, cx + s * 0.09, cy + s * 0.08], fill=(70, 70, 78))
    d.ellipse([s * 0.20, s * 0.08, s * 0.80, s * 0.66], fill=(248, 248, 244), outline=(180, 180, 176), width=int(s * 0.012))
    for k in range(3):
        d.arc([s * (0.30 + k * 0.1), s * 0.26, s * (0.40 + k * 0.1), s * 0.40], 200, 340, fill=(200, 200, 196), width=3)


def p_ygant(d, s):
    """屋上の柱に付けた八木アンテナと、右へ飛ぶ電波。"""
    d.rectangle([s * 0.26, s * 0.48, s * 0.30, s * 0.94], fill=(110, 110, 120))
    _yagi(d, s * 0.14, s * 0.62, s * 0.48, s * 0.36, (60, 64, 76), int(s * 0.018))
    for k in range(3):
        r = s * (0.10 + k * 0.08)
        d.arc([s * 0.66 - r, s * 0.48 - r, s * 0.66 + r, s * 0.48 + r], -40, 40, fill=(230, 120, 40),
              width=int(s * 0.02))


def p_ygradar(d, s):
    """八木アンテナを4段積み重ねた、戦時中のレーダー。"""
    frame = (70, 74, 64)
    d.rectangle([s * 0.46, s * 0.24, s * 0.50, s * 0.86], fill=frame)
    d.rectangle([s * 0.30, s * 0.84, s * 0.70, s * 0.92], fill=(90, 92, 80))
    for k in range(4):
        _yagi(d, s * 0.14, s * 0.86, s * (0.28 + k * 0.15), s * 0.11, (40, 44, 40), int(s * 0.012))


def p_pcparis(d, s):
    """ガラスケースに並んだ外国の鉛筆。"""
    d.rectangle([s * 0.08, s * 0.30, s * 0.92, s * 0.78], fill=(220, 236, 244), outline=(120, 110, 90),
                width=int(s * 0.014))
    cols = [(200, 170, 60), (40, 90, 60), (140, 40, 40), (40, 60, 120)]
    for k in range(4):
        y = s * (0.38 + k * 0.10)
        d.rectangle([s * 0.14, y - s * 0.025, s * 0.72, y + s * 0.025], fill=cols[k])
        d.polygon([(s * 0.72, y - s * 0.025), (s * 0.84, y), (s * 0.72, y + s * 0.025)], fill=(224, 190, 140))
        d.polygon([(s * 0.80, y - s * 0.008), (s * 0.86, y), (s * 0.80, y + s * 0.008)], fill=(50, 50, 56))


def p_pcmark(d, s):
    """家紋の三鱗と、3本の鉛筆。"""
    d.ellipse([s * 0.24, s * 0.12, s * 0.76, s * 0.64], fill=(250, 248, 240), outline=(170, 160, 150),
              width=int(s * 0.012))
    size = s * 0.18
    h = size * 0.866
    cx, cy = s * 0.5, s * 0.38
    tri = lambda x, y: [(x, y - h / 2), (x - size / 2, y + h / 2), (x + size / 2, y + h / 2)]
    for x, y in ((cx, cy - h / 2), (cx - size / 2, cy + h / 2), (cx + size / 2, cy + h / 2)):
        d.polygon(tri(x, y), fill=(40, 40, 44))
    for k in range(3):
        y = s * (0.72 + k * 0.07)
        d.rectangle([s * 0.16, y - s * 0.022, s * 0.72, y + s * 0.022], fill=(122, 30, 48))
        d.polygon([(s * 0.72, y - s * 0.022), (s * 0.84, y), (s * 0.72, y + s * 0.022)], fill=(224, 190, 140))


def p_mkshell(d, s):
    """開いたアコヤ貝。中は空っぽ。"""
    d.ellipse([s * 0.10, s * 0.44, s * 0.90, s * 0.92], fill=(120, 110, 104), outline=(70, 64, 60),
              width=int(s * 0.016))
    d.ellipse([s * 0.18, s * 0.50, s * 0.82, s * 0.86], fill=(214, 206, 214))
    d.chord([s * 0.10, s * 0.06, s * 0.90, s * 0.54], 180, 360, fill=(120, 110, 104), outline=(70, 64, 60),
            width=int(s * 0.016))


def p_mkpearl(d, s):
    """開いたアコヤ貝の中に、光る真珠1粒。"""
    p_mkshell(d, s)
    cx, cy, r = s * 0.5, s * 0.66, s * 0.14
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 236, 234), outline=(190, 184, 186),
              width=int(s * 0.01))
    d.ellipse([cx - r * 0.55, cy - r * 0.6, cx - r * 0.05, cy - r * 0.15], fill=(255, 255, 255))


def p_glkaki(d, s):
    """牡蠣の殻と、煮汁の入った大釜。"""
    d.ellipse([s * 0.10, s * 0.56, s * 0.90, s * 0.96], fill=(70, 66, 62), outline=(40, 38, 36),
              width=int(s * 0.016))                                           # 大釜
    d.ellipse([s * 0.16, s * 0.58, s * 0.84, s * 0.72], fill=(214, 196, 150))    # 煮汁
    for x, y, r in ((0.34, 0.34, 0.16), (0.62, 0.30, 0.14)):                   # 牡蠣の殻
        d.ellipse([s * (x - r), s * (y - r * 0.7), s * (x + r), s * (y + r * 0.7)], fill=(170, 166, 156),
                  outline=(110, 106, 98), width=int(s * 0.012))
        d.ellipse([s * (x - r * 0.55), s * (y - r * 0.35), s * (x + r * 0.55), s * (y + r * 0.35)],
                  fill=(236, 226, 206))


def p_glbox(d, s):
    """赤い小箱と、ハート形の粒（文字や絵柄は入れない）。"""
    d.rectangle([s * 0.10, s * 0.26, s * 0.56, s * 0.92], fill=(206, 40, 44), outline=(130, 20, 24),
                width=int(s * 0.014))
    d.rectangle([s * 0.10, s * 0.26, s * 0.56, s * 0.36], fill=(236, 200, 60))
    cx, cy, r = s * 0.74, s * 0.60, s * 0.10                                    # ハート
    d.ellipse([cx - r * 1.9, cy - r, cx, cy + r * 0.9], fill=(196, 134, 70))
    d.ellipse([cx, cy - r, cx + r * 1.9, cy + r * 0.9], fill=(196, 134, 70))
    d.polygon([(cx - r * 1.85, cy + r * 0.2), (cx + r * 1.85, cy + r * 0.2), (cx, cy + r * 2.2)],
              fill=(196, 134, 70))


def p_srbottle(d, s):
    """小瓶。胴はまっすぐの汎用の形にする（実在の容器の形は描かない）。"""
    for x, h, sc in ((0.30, 0.50, 0.8), (0.70, 0.50, 0.8), (0.50, 0.62, 1.0)):
        w = 0.16 * sc
        top = s * (0.92 - h)
        d.rounded_rectangle([s * (x - w / 2), top, s * (x + w / 2), s * 0.92], radius=int(s * 0.05 * sc),
                            fill=(240, 228, 196), outline=(150, 134, 108), width=int(s * 0.014))
        d.rectangle([s * (x - w / 2 + 0.02), top - s * 0.06 * sc, s * (x + w / 2 - 0.02), top + s * 0.02],
                    fill=(210, 50, 44))


NAVY, RED, GOLD = (26, 38, 84), (178, 30, 36), (224, 168, 26)
TEAL, PURPLE, BROWN = (16, 86, 92), (74, 32, 110), (140, 72, 26)
GREEN, MAGENTA, SLATE = (22, 96, 64), (150, 26, 88), (48, 54, 68)
INDIGO, ORANGE = (40, 32, 92), (206, 92, 20)


def _p(prop, tag, bg, emo, say, label):
    return dict(prop=prop, tag=tag, bg=bg, emo=emo, say=say, label=label)


# 3コマ構成。セリフは台本から裏を取った数字だけを入れている（未確認の数字は書かない）
SPECS = {
    # ---- 人物物語 ----
    "momofuku-meme": dict(layout="panels", headline="カップ麺はこうして生まれた",
        head_hi="カップ麺", panels=[
        _p("p_downgraph", "1957年 大阪", NAVY, "sad", "全財産が消えた", "47歳で無一文"),
        _p("p_chickenramen", "裏庭の小屋", BROWN, "thinking", "ここから|やり直すのだ", "たった1人でこもる"),
        _p("p_cupnoodle", "いま", RED, "surprised", "1000億食…！", "年1000億食"),
    ]),
    "qr-meme": dict(layout="panels", headline="QRコードはなぜ四角い",
        head_hi="QRコード", panels=[
        _p("p_barcode", "愛知の部品工場", SLATE, "sad", "もう|疲れたのだ…", "現場の一言から"),
        _p("p_goban", "昼休みの囲碁", GREEN, "thinking", "碁盤なら|一発で読めるのだ", "ヒントは碁盤の目"),
        _p("p_qr", "世界標準へ", NAVY, "surprised", "特許は取らない", "無料で開放した"),
    ]),
    "kaiten-meme": dict(layout="panels", headline="回転寿司はどこで生まれた",
        head_hi="回転寿司", panels=[
        _p("p_sushi", "1皿20円の立ち食い", RED, "sad", "板前が足りない", "深刻な人手不足"),
        _p(None, "ビール工場", GOLD, "surprised", "瓶が|流れてるのだ！", "答えはベルトコンベア"),
        _p("p_sushilane", "1958年 大阪", TEAL, "happy", "皿を|流すのだ！", "回転寿司、開店"),
    ]),
    "gastro-meme": dict(layout="panels", headline="胃カメラはたった2人で作られた",
        head_hi="胃カメラ", panels=[
        _p("p_stomach", "戦後の東大病院", INDIGO, "thinking", "中が見えないのだ", "誰も見ていない"),
        _p(None, "夜行列車", BROWN, "happy", "一緒に|作ってほしいのだ", "技師を口説き落とす"),
        _p("p_endoscope", "世界初", TEAL, "surprised", "胃の中が写った", "飲み込むカメラ"),
    ]),
    "rice-cooker-meme": dict(layout="panels", headline="炊飯器を作ったのは町工場の夫婦",
        head_hi="炊飯器", panels=[
        _p("p_kamado", "夜明け前", BROWN, "sad", "毎朝眠れないのだ", "毎朝の重労働"),
        _p(None, "大手が匙を投げた", SLATE, "thinking", "うちが|やるのだ", "町工場が引き受ける"),
        _p("p_ricecooker", "世界初", RED, "happy", "スイッチ一つ！", "妻が千回炊いた"),
    ]),
    "tenji-block-meme": dict(layout="panels", headline="点字ブロックは全財産で作られた",
        head_hi="点字ブロック", panels=[
        _p("p_cane", "岡山の交差点", SLATE, "surprised", "車道に入っていく", "白い杖の人を見た"),
        _p(None, "友の失明", INDIGO, "sad", "足の裏で|読むのだ…", "何気ない一言から"),
        _p("p_block", "1967年 原尾島", GOLD, "happy", "自腹で|敷くのだ", "230枚を私費で"),
    ]),
    "shinkansen-bird": dict(layout="panels", keep=(1, 2), headline="新幹線の鼻はなぜ長い",
        head_hi="新幹線", panels=[
        _p(None, "トンネル出口", SLATE, "angry", "爆音で苦情なのだ", "ドン！という爆音"),
        _p("p_kingfisher", "趣味は野鳥観察", TEAL, "thinking", "水しぶきが出ない", "答えはカワセミ"),
        _p("p_shinkansen", "500系", NAVY, "surprised", "時速300キロ", "世界最速へ"),
    ]),
    "yokoi-gunpei": dict(layout="panels", headline="ゲームボーイはなぜ白黒で勝った",
        head_hi="ゲームボーイ", panels=[
        _p(None, "任天堂 設備保守係", SLATE, "surprised", "社長に見つかった", "暇つぶしの玩具"),
        _p("p_gamewatch", "1980年", RED, "happy", "商品化しろ|と言われたのだ", "クビ覚悟が大ヒット"),
        _p("p_gameboy", "1989年", GREEN, "thinking", "あえて白黒なのだ", "白黒のまま1億台"),
    ]),
    "ajinomoto": dict(layout="panels", headline="うま味を見つけたのは日本人",
        head_hi="うま味", panels=[
        _p(None, "湯豆腐の夜", BROWN, "thinking", "4つの味に無い！", "5つ目の味"),
        _p(None, "東大の研究室", TEAL, "surprised", "半年かけて|取り出すのだ", "昆布12キロ→30グラム"),
        _p("p_ajibottle", "1909年 発売", RED, "happy", "世界の言葉に", "umami"),
    ]),
    "cutter-knife": dict(layout="panels", keep=(1, 2), headline="カッターナイフの答えは板チョコ",
        head_hi="カッターナイフ", panels=[
        _p(None, "大阪の印刷工", SLATE, "angry", "刃がすぐ駄目だ", "毎日捨てていた"),
        _p("p_chocolate", "街で見た光景", BROWN, "surprised", "割って使うのだ！", "ヒントは板チョコ"),
        _p("p_blade", "1956年", NAVY, "happy", "折れば戻るのだ", "世界中の定番に"),
    ]),
    "washlet": dict(layout="panels", headline="ウォシュレットを作った300人",
        head_hi="ウォシュレット", panels=[
        _p("p_toilet", "1964年 輸入品", TEAL, "angry", "熱すぎるのだ！", "温度が不安定"),
        _p(None, "社員 約300人", GOLD, "surprised", "頼むから|測らせてほしいのだ", "前代未聞の測定"),
        _p(None, "答え", NAVY, "happy", "角度は43度", "お湯38度"),
    ]),
    "karaoke": dict(layout="panels", headline="カラオケは特許を取らなかった",
        head_hi="カラオケ", panels=[
        _p("p_mic", "神戸のクラブ", PURPLE, "thinking", "楽譜が読めない", "バンドのドラマー"),
        _p("p_jukebox", "常連の頼み", MAGENTA, "surprised", "出張先でも|歌いたいのだ？", "手作りで11台"),
        _p("p_jukebox", "その後", NAVY, "sad", "特許を取らない", "年1億ドル超とも"),
    ]),
    "yai-denchi": dict(layout="panels", headline="乾電池を作ったのは日本人",
        head_hi="乾電池", panels=[
        _p("p_wetcell", "明治の東京", INDIGO, "angry", "冬は凍るのだ！", "冬は使えない"),
        _p(None, "5分の遅刻", SLATE, "sad", "時計が|止まっていたのだ…", "試験に間に合わなかった"),
        _p("p_drycell", "1887年", RED, "surprised", "凍らない電池！", "特許は5年出せず"),
    ]),
    "masuoka-flash": dict(layout="panels", headline="フラッシュメモリは却下された",
        head_hi="フラッシュメモリ", panels=[
        _p("p_kyakka", "東芝", SLATE, "angry", "金がない、却下", "予算はゼロ"),
        _p(None, "土日だけ", NAVY, "thinking", "特許を|23件書いたのだ", "仲間は同僚4人"),
        _p("p_usb", "いま", GOLD, "surprised", "洗っても消えない", "電気なしで残る"),
    ]),
    "kaisatsu-drama": dict(layout="panels", headline="自動改札は世界が真似しなかった",
        head_hi="自動改札", panels=[
        _p("p_hasami", "1960年代", BROWN, "thinking", "1枚ずつ手で切る", "1分間に80人"),
        _p(None, "無茶な注文", RED, "surprised", "それを|超えろ…！", "機械にできるのか"),
        _p("p_gate", "1967年 大阪", TEAL, "happy", "切符が消えた！", "世界初の自動改札"),
    ]),
    "quartz-astron": dict(layout="panels", headline="クオーツ時計はスイスを倒した",
        head_hi="クオーツ時計", panels=[
        _p(None, "天文台コンクール", SLATE, "sad", "最下位だったのだ", "機械式に勝てない"),
        _p("p_quartzfork", "長野県 諏訪", TEAL, "thinking", "体積を|30万分の1にするのだ", "無茶な目標"),
        _p("p_wristwatch", "1969年", NAVY, "surprised", "ずれは月5秒！", "スイスを抜いた"),
    ]),
    "purikura-meme": dict(layout="panels", headline="プリクラは会議で一蹴された",
        head_hi="プリクラ", panels=[
        _p(None, "1990年代 会議室", SLATE, "sad", "どうすんのだ…", "男性社員は一蹴"),
        _p("p_purikura", "小さなゲーム会社", MAGENTA, "thinking", "シールなら|配れるのだ", "営業がひとりで押した"),
        _p("p_purikura", "1995年", GOLD, "surprised", "行列が止まらない", "日本中で行列"),
    ]),
    "sharp-pencil": dict(layout="panels", headline="シャープの名前は商品が先だった",
        head_hi="シャープ", panels=[
        _p("p_sharppencil", "1915年 東京", NAVY, "happy", "折れない芯だ！", "21歳で発明"),
        _p(None, "関東大震災", SLATE, "sad", "全部|失ったのだ…", "家族も工場も"),
        _p(None, "大阪へ", RED, "thinking", "名前だけ残った", "商品名が社名に"),
    ]),
    "okano-needle": dict(layout="panels", headline="痛くない注射針は町工場が作った",
        head_hi="注射針", panels=[
        _p(None, "100社以上が断った", SLATE, "angry", "無理だと言われた", "100社が断った"),
        _p(None, "墨田区の町工場", TEAL, "happy", "よし、|やるのだ", "従業員6人"),
        _p("p_needle", "先端0.2ミリ", RED, "surprised", "蚊の口と同じ！", "刺しても痛くない"),
    ]),
    "nishizawa-fiber": dict(layout="panels", headline="光ファイバーを日本は捨てた",
        head_hi="光ファイバー", panels=[
        _p(None, "1950年代 仙台", INDIGO, "thinking", "光で|通信するのだ", "20年早すぎた"),
        _p("p_kyakka", "資金の相談", SLATE, "sad", "金は|出せないのだ…", "国内で相手にされず"),
        _p("p_fiber", "いま", TEAL, "surprised", "髪より細いのだ", "今の通信の土台"),
    ]),
    "exit-sign": dict(layout="panels", headline="非常口マークを描いたのは日本人",
        head_hi="非常口マーク", panels=[
        _p(None, "1970年代", SLATE, "surprised", "文字では読めない", "逃げ遅れが出た"),
        _p("p_exitsign", "公募", GREEN, "thinking", "走る人を|描くのだ", "緑の人が生まれる"),
        _p("p_exitsign", "世界標準へ", NAVY, "happy", "日本案が勝った", "ソ連案に勝った"),
    ]),
    "nakauchi-daiei": dict(layout="panels", headline="ダイエーはなぜ消えた",
        head_hi="ダイエー", panels=[
        _p("p_sukiyaki", "1943年 戦地", BROWN, "sad", "すき焼きが…", "生きて帰った"),
        _p("p_beefpack", "1957年 大阪", GOLD, "angry", "よそより|安く売るのだ！", "牛肉 100円→39円"),
        _p("p_shutter", "2004年", NAVY, "surprised", "借金、1兆円…", "創業者、追放"),
    ]),
    "yamauchi-nintendo": dict(layout="panels", headline="任天堂は花札の会社だった",
        head_hi="任天堂", panels=[
        _p("p_hanafuda", "22歳で社長", GREEN, "thinking", "うちは花札屋だ", "創業70年の老舗"),
        _p("p_downgraph", "多角化", SLATE, "sad", "タクシーも|食品も駄目なのだ…", "借金70億円"),
        _p("p_gameboy", "1980年代", RED, "surprised", "おもちゃ屋なのだ", "世界を取った"),
    ]),
    "yamaichi-nozawa": dict(layout="panels", headline="山一証券、最後の社長",   # 851フォントに「證」が無いので報道表記の「証」
        head_hi="山一証券", panels=[
        _p("p_hoe", "1938年 長野", BROWN, "normal", "畑を三年やった", "畳職人の家の子"),
        _p("p_ledger", "1997年8月", NAVY, "surprised", "2600億の|借金…！？", "自分は一円も使っていない"),
        _p("p_mics", "11月24日", SLATE, "sad", "社員は悪くない", "7500人が失職"),
    ]),
    "ogura-takkyubin": dict(layout="panels", keep=(1, 2), headline="宅急便は役所を訴えて作られた",
        head_hi="宅急便", panels=[
        _p(None, "1949年", TEAL, "thinking", "四年、病室で…", "動けない4年間"),
        _p("p_parcel", "1976年", BROWN, "sad", "初日は十一個…", "初日 11個"),
        _p("p_gavel", "1986年", RED, "angry", "役所を訴えるのだ", "監督官庁を訴えた"),
    ]),
    "yamamoto-rotary": dict(layout="panels", headline="世界が捨てたロータリー",
        head_hi="ロータリー", panels=[
        _p("p_rotor", "1963年 広島", NAVY, "thinking", "回るだけで動く", "47人が挑んだ"),
        _p("p_scratch", "悪魔の爪痕", SLATE, "surprised", "数十時間で|波打つ…！？", "原因が誰にも分からない"),
        _p(None, "1991年 ル・マン", RED, "happy", "24時間走った！", "日本車初の優勝"),
    ]),
    "momose-subaru360": dict(layout="panels", headline="スバル360は作れないはずだった",
        head_hi="スバル360", panels=[
        _p("p_propeller", "1942年", SLATE, "normal", "戦闘機の技術者だ", "飛行機を作れない"),
        _p(None, "枠は動かせない", NAVY, "angry", "この寸法に|大人4人…！？", "常識では2人乗りが限界"),
        _p("p_keicar", "1958年", GOLD, "happy", "自分で何十回も", "てんとう虫"),
    ]),
    "honda-soichiro": dict(layout="panels", headline="ホンダは宣言から始まった",
        head_hi="ホンダ", panels=[
        _p(None, "1922年 東京", BROWN, "sad", "車に|触れないのだ", "丁稚奉公から"),
        _p("p_paper", "1954年", SLATE, "angry", "出場ではなく|優勝と書く", "日本勢はまだ誰も出ていない"),
        _p("p_trophy", "1961年 マン島", RED, "surprised", "全部うち…！？", "1〜5位を独占"),
    ]),
    "takahashi-urayasu": dict(layout="panels", headline="あの場所は海だった",
        head_hi="海", panels=[
        _p("p_boat", "1961年 浦安", TEAL, "normal", "海は売らないのだ", "漁協が割れた"),
        _p("p_stamp", "一軒ずつ", BROWN, "thinking", "また来ます、を|何年もやる", "近道が無かった"),
        _p(None, "1983年 開園", GOLD, "surprised", "数えきれないのだ", "交渉から22年"),
    ]),
    "ibuka-sony": dict(layout="panels", headline="ソニーは役所に止められた",
        head_hi="ソニー", panels=[
        _p(None, "1945年 日本橋", SLATE, "normal", "まだ何も無いのだ", "デパートの一室"),
        _p(None, "1952年 アメリカ", TEAL, "surprised", "こんなに|小さいのか…！", "真空管に代わる部品"),
        _p("p_stamp", "役所の返事", RED, "angry", "できるわけない", "役所が拒否した"),
    ]),
    "onitsuka-asics": dict(layout="panels", keep=(1, 2), headline="タコを見て靴を作った",
        head_hi="タコ", panels=[
        _p(None, "1951年 体育館", BROWN, "angry", "選手が止まれない", "靴の裏は平ら"),
        _p("p_octopus", "夕飯の皿", RED, "surprised", "吸盤がへこんでる", "酢の物のタコ"),
        _p("p_sole", "いまの靴", NAVY, "happy", "形で解いたのだ", "靴底のへこみ"),
    ]),
    # ---- 解説 ----
    "ishibashi-bridgestone": dict(layout="panels", headline="ブリヂストンは足袋屋だった",
        head_hi="ブリヂストン", panels=[
        _p("p_tabi", "久留米の小さな店", BROWN, "normal", "底にゴムを貼る", "もとは足袋屋"),
        _p("p_tyrestack", "売った先から", SLATE, "sad", "全部返ってきた", "倉庫が埋まる"),
    ]),
    "torii-whisky": dict(layout="panels", headline="国産ウイスキーは売れなかった",
        head_hi="国産ウイスキー", panels=[
        _p("p_whiskybottle", "六年待った一本", GOLD, "happy", "日本初の一本", "1929年に出す"),
        _p(None, "客の反応", NAVY, "sad", "焦げくさい", "誰も買わない"),
    ]),
    "tateishi-omron": dict(layout="panels", headline="オムロンは新聞配達から始まった",
        head_hi="オムロン", panels=[
        _p(None, "小学一年で父を亡くす", INDIGO, "sad", "毎朝、数えてた", "新聞配達の少年"),
        _p("p_rtimer", "最初の商品", TEAL, "happy", "機械に数えさせる", "撮影用タイマー"),
    ]),
    "toyoda-kiichiro": dict(layout="panels", headline="トヨタは織機の会社だった",
        head_hi="トヨタ", panels=[
        _p("p_loom", "1933年 倉庫", BROWN, "normal", "布を織ってた", "もとは織機屋"),
        _p("p_engineblock", "作っても割れる", SLATE, "sad", "9割が屑なのだ", "エンジンの鋳物"),
    ]),
    "ykk": dict(layout="panels", headline="YKKは潰れた店から始まった",
        head_hi="潰れた店", panels=[
        _p("p_ykbox", "1933年 日本橋", BROWN, "sad", "店をたたむのだ", "未払いの売れ残り"),
        _p("p_ykzip", "世界のズボンへ", TEAL, "happy", "全部同じ三文字", "真似できない技術"),
    ]),
    "naito-tower": dict(layout="panels", headline="東京タワーは70歳が計算した",
        head_hi="東京タワー", panels=[
        _p("p_nttrunk", "1917年 アメリカ", BROWN, "surprised", "仕切りなのだ！", "トランクの仕切り"),
        _p("p_nttower", "1958年 東京", TEAL, "happy", "計算尺で333m", "70歳の構造計算"),
    ]),
    "yoshinoya-abe": dict(layout="panels", headline="吉野家から牛丼が消えた",
        head_hi="牛丼", panels=[
        _p("p_gdempty", "2004年2月", BROWN, "sad", "牛丼がないのだ", "全国で販売休止"),
        _p("p_gdbowl", "2006年9月", TEAL, "happy", "同じ味なのだ", "代わりは使わない"),
    ]),
    "honda-seiroku": dict(layout="panels", headline="明治神宮の森は人が植えた",
        head_hi="人が植えた", panels=[
        _p("p_hsfield", "1915年 代々木", BROWN, "surprised", "ここに森を？", "畑と野原だった"),
        _p("p_hsforest", "いま", GREEN, "happy", "深い森なのだ", "150年後を設計"),
    ]),
    "mosquito-coil": dict(layout="panels", headline="蚊取り線香はなぜ渦巻き",
        head_hi="渦巻き", panels=[
        _p("p_ktstick", "1890年 最初の線香", BROWN, "sad", "40分で消えた", "まっすぐな棒"),
        _p("p_ktcoil", "1902年", GREEN, "happy", "朝までもつのだ", "巻けば長いまま"),
    ]),
    "mosquito-coil-v2": dict(layout="panels", headline="蚊取り線香はなぜ渦巻き",
        head_hi="渦巻き", panels=[
        _p("p_ktstick", "1890年 最初の線香", BROWN, "sad", "40分で消えた", "まっすぐな棒"),
        _p("p_ktcoil", "1902年", GREEN, "happy", "朝までもつのだ", "巻けば長いまま"),
    ]),
    "iwasaki-sample": dict(layout="panels", headline="食品サンプルの元は妻のオムレツ",
        head_hi="妻のオムレツ", panels=[
        _p("p_sprou", "少年時代 郡上八幡", SLATE, "surprised", "花になったのだ！", "水に落ちたロウ"),
        _p("p_spomu", "1932年 第1号", RED, "happy", "シワまで写すのだ", "本物と見分けがつかない"),
    ]),
    "iwasaki-sample-v2": dict(layout="panels", headline="食品サンプルの元は妻のオムレツ",
        head_hi="妻のオムレツ", panels=[
        _p("p_sprou", "少年時代 郡上八幡", SLATE, "surprised", "花になったのだ！", "水に落ちたロウ"),
        _p("p_spomu", "1932年 第1号", RED, "happy", "シワまで写すのだ", "本物と見分けがつかない"),
    ]),
    "famicom-uemura": dict(layout="panels", headline="発売の年末、ファミコン全品回収",
        head_hi="全品回収", panels=[
        _p("p_fcphone", "1981年 夜の電話", SLATE, "thinking", "3年なんて無理なのだ", "社長から家に電話"),
        _p("p_fcbox", "1983年 年末", RED, "surprised", "全部引き取るのだ！？", "クリスマス直前に回収"),
    ]),
    "famicom-uemura-v2": dict(layout="panels", headline="発売の年末、ファミコン全品回収",
        head_hi="全品回収", panels=[
        _p("p_fcphone", "1981年 夜の電話", SLATE, "thinking", "3年なんて無理なのだ", "社長から家に電話"),
        _p("p_fcbox", "1983年 年末", RED, "surprised", "全部引き取るのだ！？", "クリスマス直前に回収"),
    ]),
    "matsushita-socket": dict(layout="panels", headline="ソケット100個から18万人の会社へ",
        head_hi="18万人", panels=[
        _p("p_pnsocket", "1917年 冬", SLATE, "sad", "100個だけ…", "売れないソケット"),
        _p("p_pnbuilding", "いま", RED, "surprised", "18万人！？", "パナソニックに"),
    ]),
    "yamaha-torakusu": dict(layout="panels", headline="酷評のオルガンが年4653億円に",
        head_hi="4653億円", panels=[
        _p("p_yhorgan", "1887年 東京", SLATE, "sad", "使用にはたえない", "手作りのオルガン"),
        _p("p_yhpiano", "いま", RED, "surprised", "世界のヤマハ！？", "年4653億円"),
    ]),
    "sanyo-end": dict(layout="panels", headline="10万人の会社が消えた日",
        head_hi="消えた", panels=[
        _p("p_sawasher", "1953年", SLATE, "happy", "売れたのだ！", "噴流式の洗濯機"),
        _p("p_sasign", "2011年", RED, "sad", "看板が降りる…", "最盛期10万人"),
    ]),
    "godzilla-tsuburaya": dict(layout="panels", headline="動けない怪獣が961万人を呼んだ",
        head_hi="961万人", panels=[
        _p("p_gzsuit", "1954年 撮影所", SLATE, "sad", "またげない…", "重さ150キロ"),
        _p("p_gzqueue", "1954年 公開初日", RED, "surprised", "道玄坂まで列！？", "観客961万人"),
    ]),
    "frixion-metamo": dict(layout="panels", headline="紅葉から生まれた消えるペン",
        head_hi="紅葉", panels=[
        _p("p_fxleaf", "1970年 渓谷の紅葉", SLATE, "surprised", "色が変わるのだ！", "試験管で作りたい"),
        _p("p_fxpen", "2006年 ヨーロッパ", RED, "happy", "消えるのだ！", "30年後にボールペンへ"),
    ]),
    "frixion-metamo-v2": dict(layout="panels", headline="紅葉から生まれた消えるペン",
        head_hi="紅葉", panels=[
        _p("p_fxleaf", "1970年 渓谷の紅葉", SLATE, "surprised", "色が変わるのだ！", "試験管で作りたい"),
        _p("p_fxpen", "2006年 ヨーロッパ", RED, "happy", "消えるのだ！", "30年後にボールペンへ"),
    ]),
    "fujisawa-supercub": dict(layout="panels", headline="「月に3万台売れる」と言った男",
        head_hi="月に3万台", panels=[
        _p("p_scclay", "1957年 粘土の模型", SLATE, "happy", "月間で、なのだ", "業界全体で月4万台の時代"),
        _p("p_sccub", "2017年", RED, "surprised", "1億台なのだ！", "世界の働くバイクに"),
    ]),
    "fujisawa-supercub-v2": dict(layout="panels", headline="「月に3万台売れる」と言った男",
        head_hi="月に3万台", panels=[
        _p("p_scclay", "1957年 粘土の模型", SLATE, "happy", "月間で、なのだ", "業界全体で月4万台の時代"),
        _p("p_sccub", "2017年", RED, "surprised", "1億台なのだ！", "世界の働くバイクに"),
    ]),
    "kobori-airbag": dict(layout="panels", headline="エアバッグを考えた日本人がいた",
        head_hi="日本人", panels=[
        _p("p_kbcar", "1964年 東京", SLATE, "thinking", "袋で守るのだ", "14か国で特許"),
        _p("p_kbwheel", "1980年 西ドイツ", RED, "surprised", "積まれたのだ！", "特許は使われず"),
    ]),
    "kobori-airbag-v2": dict(layout="panels", headline="エアバッグを考えた日本人がいた",
        head_hi="日本人", panels=[
        _p("p_kbcar", "1964年 東京", SLATE, "thinking", "袋で守るのだ", "14か国で特許"),
        _p("p_kbwheel", "1980年 西ドイツ", RED, "surprised", "積まれたのだ！", "特許は使われず"),
    ]),
    "yagi-uda-antenna": dict(layout="panels", headline="八木アンテナを敵から教わった",
        head_hi="敵から教わった", panels=[
        _p("p_ygant", "1926年 仙台", SLATE, "happy", "遠くまで届くのだ", "棒を並べただけ"),
        _p("p_ygradar", "1942年 シンガポール", RED, "surprised", "日本の発明なのだ！", "敵のレーダーの部品"),
    ]),
    "yagi-uda-antenna-v2": dict(layout="panels", headline="八木アンテナを敵から教わった",
        head_hi="敵から教わった", panels=[
        _p("p_ygant", "1926年 仙台", SLATE, "happy", "遠くまで届くのだ", "棒を並べただけ"),
        _p("p_ygradar", "1942年 シンガポール", RED, "surprised", "日本の発明なのだ！", "敵のレーダーの部品"),
    ]),
    "ohira-megastar": dict(layout="panels", headline="プラネタリウムを7畳間で作った",
        head_hi="7畳間", panels=[
        _p("p_mgroom", "1996年 実家の自室", SLATE, "thinking", "自分で作るのだ", "会社員の趣味"),
        _p("p_mgdome", "1998年 ロンドン", NAVY, "surprised", "100万個なのだ！", "パードン？と聞き返された"),
    ]),
    "ohira-megastar-v2": dict(layout="panels", headline="プラネタリウムを7畳間で作った",
        head_hi="7畳間", panels=[
        _p("p_mgroom", "1996年 実家の自室", SLATE, "thinking", "自分で作るのだ", "会社員の趣味"),
        _p("p_mgdome", "1998年 ロンドン", NAVY, "surprised", "100万個なのだ！", "パードン？と聞き返された"),
    ]),
    "tamagotchi-yokoi": dict(layout="panels", headline="たまごっちはわざと死ぬ",
        head_hi="わざと死ぬ", panels=[
        _p("p_tgfish", "1995年 パソコンの魚", SLATE, "thinking", "生きてるのだ", "人間と同じ時間"),
        _p("p_tgegg", "1996年 発売", RED, "surprised", "死んだのだ！？", "世話しないと死ぬ"),
    ]),
    "tamagotchi-yokoi-v2": dict(layout="panels", headline="たまごっちはわざと死ぬ",
        head_hi="わざと死ぬ", panels=[
        _p("p_tgfish", "1995年 パソコンの魚", SLATE, "thinking", "生きてるのだ", "人間と同じ時間"),
        _p("p_tgegg", "1996年 発売", RED, "surprised", "死んだのだ！？", "世話しないと死ぬ"),
    ]),
    "masaki-pencil": dict(layout="panels", headline="三菱鉛筆は三菱じゃない",
        head_hi="三菱じゃない", panels=[
        _p("p_pcparis", "1878年 パリ", SLATE, "surprised", "なんなのだ？", "初めて見た鉛筆"),
        _p("p_pcmark", "1903年", BROWN, "happy", "マークなのだ", "家紋と3本の鉛筆"),
    ]),
    "masaki-pencil-v2": dict(layout="panels", headline="三菱鉛筆は三菱じゃない",
        head_hi="三菱じゃない", panels=[
        _p("p_pcparis", "1878年 パリ", SLATE, "surprised", "なんなのだ？", "初めて見た鉛筆"),
        _p("p_pcmark", "1903年", BROWN, "happy", "マークなのだ", "家紋と3本の鉛筆"),
    ]),
    "sony-walkman": dict(layout="panels", headline="初代ウォークマンは録音できない",
        head_hi="録音できない", panels=[
        _p("p_wmheavy", "1978年", SLATE, "sad", "重すぎるのだ", "10万円の録音機"),
        _p("p_wmwalk", "1979年", TEAL, "happy", "歩いて聴けるのだ", "3万3000円"),
    ]),
    "sony-walkman-v2": dict(layout="panels", headline="初代ウォークマンは録音できない",
        head_hi="録音できない", panels=[
        _p("p_wmheavy", "1978年", SLATE, "sad", "重すぎるのだ", "10万円の録音機"),
        _p("p_wmwalk", "1979年", TEAL, "happy", "歩いて聴けるのだ", "3万3000円"),
    ]),
    "othello-hasegawa": dict(layout="panels", headline="オセロの石は牛乳瓶のフタ",
        head_hi="牛乳瓶のフタ", panels=[
        _p("p_oscap", "1964年 試作品", BROWN, "thinking", "3枚重ねるのだ", "牛乳瓶の紙のフタ"),
        _p("p_osboard", "1973年 発売", GREEN, "happy", "オセロなのだ", "フタと同じ大きさ"),
    ]),
    "othello-hasegawa-v2": dict(layout="panels", headline="オセロの石は牛乳瓶のフタ",
        head_hi="牛乳瓶のフタ", panels=[
        _p("p_oscap", "1964年 試作品", BROWN, "thinking", "3枚重ねるのだ", "牛乳瓶の紙のフタ"),
        _p("p_osboard", "1973年 発売", GREEN, "happy", "オセロなのだ", "フタと同じ大きさ"),
    ]),
    "sugiyo-kanikama": dict(layout="panels", headline="カニカマはクラゲの失敗作",
        head_hi="クラゲ", panels=[
        _p("p_kkjelly", "1970年 人工クラゲ", SLATE, "sad", "溶けたのだ", "味を付けると溶ける"),
        _p("p_kkstick", "1972年", RED, "happy", "カニなのだ", "刻んだらカニの身"),
    ]),
    "sugiyo-kanikama-v2": dict(layout="panels", headline="カニカマはクラゲの失敗作",
        head_hi="クラゲ", panels=[
        _p("p_kkjelly", "1970年 人工クラゲ", SLATE, "sad", "溶けたのだ", "味を付けると溶ける"),
        _p("p_kkstick", "1972年", RED, "happy", "カニなのだ", "刻んだらカニの身"),
    ]),
    "kimuraya-anpan": dict(layout="panels", headline="あんぱんは酒の種で焼いた",
        head_hi="酒の種", panels=[
        _p("p_anhard", "1869年 最初のパン", SLATE, "sad", "かたいのだ", "売れないパン"),
        _p("p_anpan", "1874年", RED, "happy", "ふんわりなのだ", "酒まんじゅうの種"),
    ]),
    "kimuraya-anpan-v2": dict(layout="panels", headline="売れないパンが天皇の茶菓子に",
        head_hi="天皇の茶菓子", panels=[
        _p("p_anhard", "1869年 最初のパン", SLATE, "sad", "かたいのだ", "売れないパン"),
        _p("p_anpan", "1874年", RED, "happy", "ふんわりなのだ", "酒まんじゅうの種"),
    ]),
    "furuno-fishfinder": dict(layout="panels", headline="魚の群れを音で見た",
        head_hi="音で", panels=[
        _p("p_frnoise", "1947年 五島灘", SLATE, "sad", "ぐちゃぐちゃだ", "雑音で見えない"),
        _p("p_frschool", "1949年 岩瀬浦", TEAL, "happy", "港で一番なのだ", "最下位の船が1位"),
    ]),
    "furuno-fishfinder-v2": dict(layout="panels", headline="「インチキ」と海に落とされた",
        head_hi="インチキ", panels=[
        _p("p_frnoise", "1948年 長崎", SLATE, "sad", "クラゲだったのだ…", "海へ放り込まれる"),
        _p("p_frschool", "1949年 岩瀬浦", TEAL, "happy", "港で一番なのだ", "最下位の船が1位"),
    ]),
    "casio-kashio": dict(layout="panels", headline="計算機は電話部品で作った",
        head_hi="電話部品", panels=[
        _p("p_csgear", "1949年 歯車の計算機", SLATE, "sad", "うるさいのだ", "車と同じ値段"),
        _p("p_csrelay", "1957年 14-A", TEAL, "happy", "静かなのだ", "リレー約340個"),
    ]),
    "casio-kashio-v2": dict(layout="panels", headline="動かない計算機が1000万台に",
        head_hi="1000万台", panels=[
        _p("p_csrelay", "1956年 札幌", SLATE, "sad", "動かないのだ…", "発表会の前の晩"),
        _p("p_csmini", "1972年 カシオミニ", TEAL, "happy", "手のひらなのだ！", "シリーズ1000万台"),
    ]),
    "mikimoto-pearl": dict(layout="panels", headline="真珠は貝に作らせた",
        head_hi="作らせた", panels=[
        _p("p_mkshell", "1892年 赤潮", NAVY, "sad", "貝が全滅なのだ", "何年も空っぽ"),
        _p("p_mkpearl", "1893年", TEAL, "happy", "光ってるのだ", "貝が巻いた真珠"),
    ]),
    "glico-ezaki": dict(layout="panels", headline="グリコは牡蠣から生まれた",
        head_hi="牡蠣", panels=[
        _p("p_glkaki", "1919年 佐賀", BROWN, "surprised", "煮汁を捨ててる", "牡蠣の煮汁"),
        _p("p_glbox", "1922年 大阪", RED, "happy", "お菓子にしたのだ", "一粒300m"),
    ]),
    "yakult-shirota": dict(layout="panels", headline="ヤクルトの菌は胃液に勝つ",
        head_hi="胃液に勝つ", panels=[
        _p("p_srdish", "1930年 京都", NAVY, "sad", "また全滅なのだ", "酸で菌が死ぬ"),
        _p("p_srbottle", "いま", RED, "happy", "毎日1本なのだ", "腸まで生きて届く"),
    ]),
    "calpis": dict(layout="panels", headline="カルピスは偶然に生まれた",
        head_hi="偶然", panels=[
        _p("p_cpbowl", "1900年代 草原", BROWN, "surprised", "これは何なのだ", "草原の白い飲み物"),
        _p("p_cpbottle", "1919年 東京", TEAL, "thinking", "置き忘れた瓶", "偶然できた一本"),
    ]),
    "battery-80-duo": dict(layout="panels", headline="スマホ充電100%は損",
        head_hi="100%", panels=[
        _p(None, "毎晩やってる", RED, "happy", "満タンで寝るのだ", "いちばん減る"),
        _p(None, "なぜ", SLATE, "surprised", "満タンが|電池を削るのだ？", "膨らんで戻らなくなる"),
        _p("p_battery", "メーカー自身が", TEAL, "thinking", "80%で止める", "最初から付属"),
    ]),
    "auto-door": dict(layout="panels", headline="自動ドアがあなたを無視する理由",
        head_hi="自動ドア", panels=[
        _p("p_autodoor", "黒い服の日", SLATE, "angry", "開かないのだ！", "反応しない人"),
        _p(None, "見ているもの", NAVY, "surprised", "人を|見てないのだ？", "床の見え方が変わったか"),
        _p(None, "真横から行くと", TEAL, "thinking", "近づき方なのだ", "歩き方で決まる"),
    ]),
    "banknote": dict(layout="panels", headline="お札はなぜコピーできない",
        head_hi="お札", panels=[
        _p("p_bill", "コピー機", PURPLE, "surprised", "印刷を拒否される", "機械が止まる"),
        _p(None, "見えない印", NAVY, "thinking", "人には|見えないのだ", "機械にだけ分かる仕掛け"),
        _p(None, "指で分かる", TEAL, "happy", "触るとザラザラ", "世界初の技術"),
    ]),
    "escalator": dict(layout="panels", headline="片側空けは公式ルールじゃない",
        head_hi="片側空け", panels=[
        _p("p_escalator", "東京は左・大阪は右", SLATE, "thinking", "どっちが正しい？", "実は決まりが無い"),
        _p(None, "作った側は", RED, "surprised", "ずっと|やめてと言ってるのだ", "歩かないでください"),
        _p(None, "隠れた機能", TEAL, "happy", "ステップが変形！", "知られてない"),
    ]),
    "traffic-light": dict(layout="panels", headline="信号の青はどう見ても緑",
        head_hi="信号の青", panels=[
        _p("p_signal", "日本だけ", GREEN, "thinking", "緑なのに青と呼ぶ", "法律も緑だった"),
        _p(None, "LEDの弱点", SLATE, "surprised", "雪が|溶けないのだ！", "熱を出さないから"),
        _p(None, "雪国は縦型", NAVY, "happy", "雪が積もらない", "理由がある"),
    ]),
}


def render(slug, out_path=None):
    spec = SPECS[slug]
    kind = spec["layout"]
    img = {"split": layout_split, "band": layout_band, "ba": layout_beforeafter,
           "charbig": layout_charbig, "photo": layout_photo,
           "bold": layout_bold, "face": layout_face,
           "punch": layout_punch,
           "stack": layout_stack,
           "conflict": layout_conflict,
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
