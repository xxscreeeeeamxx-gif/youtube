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
    """カッターの刃（先端が折れて飛ぶ）。"""
    seg = [(s*0.10, s*0.86), (s*0.62, s*0.34), (s*0.78, s*0.50), (s*0.26, s*1.02)]
    d.polygon(seg, fill=(200, 206, 218), outline=(90, 96, 110))
    for k in range(1, 4):
        x0 = s*0.10 + (s*0.52) * k / 4
        y0 = s*0.86 - (s*0.52) * k / 4
        d.line([(x0, y0), (x0 + s*0.16, y0 + s*0.16)], fill=(110, 116, 130), width=8)
    # 折れた先端
    tip = [(s*0.68, s*0.16), (s*0.84, s*0.32), (s*0.72, s*0.44), (s*0.58, s*0.28)]
    d.polygon(tip, fill=(225, 230, 240), outline=(90, 96, 110))
    d.line([(s*0.52, s*0.40), (s*0.60, s*0.32)], fill=(255, 255, 255), width=10)


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
    """胃カメラ（先端にレンズと光）。"""
    d.line([(s*0.12, s*0.10), (s*0.44, s*0.30), (s*0.62, s*0.58), (s*0.54, s*0.88)],
           fill=(70, 76, 92), width=int(s*0.16), joint="curve")
    d.ellipse([s*0.36, s*0.72, s*0.74, s*1.06], fill=(215, 220, 232), outline=(60, 66, 82), width=9)
    d.ellipse([s*0.44, s*0.80, s*0.66, s*0.99], fill=(90, 200, 240), outline=(40, 120, 170), width=6)
    d.ellipse([s*0.02, s*0.02, s*0.30, s*0.28], fill=(160, 166, 182), outline=(60, 66, 82), width=8)
    for a in (0, 45, 90, 135):
        import math
        rad = math.radians(a)
        d.line([(s*0.53 + math.cos(rad)*s*0.13, s*0.91 + math.sin(rad)*s*0.13),
                (s*0.53 + math.cos(rad)*s*0.22, s*0.91 + math.sin(rad)*s*0.22)],
               fill=(255, 230, 120), width=6)


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
    """味の素（結晶と昆布）。"""
    d.polygon([(s*0.16, s*0.94), (s*0.30, s*0.20), (s*0.44, s*0.94)],
              fill=(40, 70, 46), outline=(20, 44, 26))
    d.polygon([(s*0.30, s*0.94), (s*0.44, s*0.28), (s*0.58, s*0.94)],
              fill=(52, 88, 56), outline=(20, 44, 26))
    d.rounded_rectangle([s*0.58, s*0.44, s*0.94, s*0.94], radius=12,
                        fill=(250, 252, 255), outline=(150, 160, 180), width=7)
    import random
    rnd = random.Random(5)
    for _ in range(14):
        x = rnd.uniform(0.62, 0.90) * s
        y = rnd.uniform(0.52, 0.88) * s
        d.rectangle([x, y, x + s*0.045, y + s*0.045], fill=(235, 240, 250),
                    outline=(170, 180, 200), width=3)


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
    """エスカレーター（斜めの段）。"""
    for k in range(5):
        x0 = s*0.08 + k * s*0.16
        y0 = s*0.90 - k * s*0.16
        d.rectangle([x0, y0, x0 + s*0.22, y0 + s*0.10],
                    fill=(200, 206, 218), outline=(110, 116, 132), width=6)
    d.line([(s*0.06, s*0.74), (s*0.94, s*0.16)], fill=(60, 66, 80), width=14)
    d.line([(s*0.06, s*0.74), (s*0.94, s*0.16)], fill=(140, 146, 160), width=6)


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
    for i in range(-2, 22):                      # 集中線
        x = int(W * 0.62) + i * 96
        d.polygon([(int(W * 0.62), int(H * 0.5)), (x, -60), (x + 42, -60)],
                  fill=(255, 255, 255, 12))
    # キャラ（顔が大きく出るようバストで切る）
    sp = Image.open(sprite_path(cfg, spec.get("who", "zundamon"),
                                spec.get("emotion", "surprised"))).convert("RGBA")
    b = sp.crop((0, 0, sp.width, int(sp.height * 0.58)))
    sc = int(H * 1.06) / b.height
    b = outline_sprite(b.resize((int(b.width * sc), int(b.height * sc)), Image.LANCZOS), 16)
    img.alpha_composite(b, (W - b.width + 92, H - b.height + 18))
    # 文字（2行・極大）。幅に収まるまでサイズを落とす
    lines = spec["lines"]
    max_w = int(W * 0.62)
    y = spec.get("text_top", 96)
    for text, color, accent in lines:
        size = spec.get("size", 190)
        while size > 90:
            f = font("w9", size)
            if int(f.getlength(text)) <= max_w:
                break
            size -= 6
        f = font("w9", size)
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
        y += int(size * 1.18)
    return vignette(img, 78)


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
    "momofuku-meme": dict(layout="bold", bg=((160, 44, 24), (98, 22, 12)), emotion="sad",
        lines=[("47歳", W1, None), ("全財産ゼロ", B1, Y1)]),
    "qr-meme": dict(layout="bold", bg=((22, 52, 110), (12, 28, 66)), emotion="surprised",
        lines=[("疲れたの一言が", W1, None), ("世界標準に", B1, Y1)]),
    "kaiten-meme": dict(layout="bold", bg=((150, 34, 44), (88, 18, 26)), emotion="thinking",
        lines=[("寿司を回す", W1, None), ("ヒントは工場", B1, Y1)]),
    "yai-denchi": dict(layout="bold", bg=((60, 30, 96), (34, 16, 58)), emotion="sad",
        lines=[("5分の遅刻で", W1, None), ("人生が変わる", B1, Y1)]),
    "tenji-block-meme": dict(layout="bold", bg=((146, 108, 16), (92, 66, 8)), emotion="sad",
        lines=[("全財産を", W1, None), ("道路に敷いた", B1, Y1)]),
    "masuoka-flash": dict(layout="bold", bg=((26, 60, 104), (14, 32, 62)), emotion="sad",
        lines=[("金がない、却下", W1, None), ("それでも作った", B1, Y1)]),
    "kaisatsu-drama": dict(layout="bold", bg=((22, 66, 78), (12, 38, 46)), emotion="surprised",
        lines=[("1分間に80人", W1, None), ("機械で超えろ", B1, Y1)]),
    "gastro-meme": dict(layout="bold", bg=((26, 52, 92), (14, 28, 56)), emotion="surprised",
        lines=[("たった2人で", W1, None), ("胃の中を撮る", B1, Y1)]),
    "rice-cooker-meme": dict(layout="bold", bg=((132, 62, 22), (80, 36, 12)), emotion="sad",
        lines=[("妻が千回", W1, None), ("米を炊いた", B1, Y1)]),
    "karaoke": dict(layout="bold", bg=((88, 26, 108), (52, 14, 66)), emotion="sad",
        lines=[("手作り11台", W1, None), ("なのに収入0", B1, Y1)]),
    "yokoi-gunpei": dict(layout="bold", bg=((36, 44, 74), (20, 26, 46)), emotion="surprised",
        lines=[("カラー全盛に", W1, None), ("あえて白黒", B1, Y1)]),
    "shinkansen-bird": dict(layout="bold", bg=((22, 70, 110), (12, 40, 66)), emotion="surprised",
        lines=[("時速300キロ", W1, None), ("鳥が解決した", B1, Y1)]),
    "cutter-knife": dict(layout="bold", bg=((24, 62, 108), (12, 34, 64)), emotion="happy",
        lines=[("切れないなら", W1, None), ("折ればいい", B1, Y1)]),
    "washlet": dict(layout="bold", bg=((18, 78, 88), (10, 44, 52)), emotion="surprised",
        lines=[("社員300人が", W1, None), ("体を張った", B1, Y1)]),
    "ajinomoto": dict(layout="bold", bg=((110, 76, 20), (66, 44, 10)), emotion="thinking",
        lines=[("5つ目の味は", W1, None), ("昆布にあった", B1, Y1)]),
    # ---- 解説 ----
    "battery-80-duo": dict(layout="bold", bg=((150, 30, 34), (92, 16, 22)), emotion="surprised",
        lines=[("毎晩100%は", W1, None), ("損してる", B1, Y1)]),
    "banknote": dict(layout="bold", bg=((72, 26, 96), (42, 14, 58)), emotion="surprised",
        lines=[("コピー機は", W1, None), ("お札を拒否", B1, Y1)]),
    "escalator": dict(layout="bold", bg=((34, 52, 82), (18, 30, 50)), emotion="surprised",
        lines=[("片側空けの", W1, None), ("ルールは無い", B1, Y1)]),
    "traffic-light": dict(layout="bold", bg=((20, 62, 60), (10, 36, 36)), emotion="thinking",
        lines=[("どう見ても緑", W1, None), ("なのに青", B1, Y1)]),
    "auto-door": dict(layout="bold", bg=((28, 54, 78), (14, 30, 46)), emotion="angry",
        lines=[("黒い服だと", W1, None), ("開かない", B1, Y1)]),
}


def render(slug, out_path=None):
    spec = SPECS[slug]
    kind = spec["layout"]
    img = {"split": layout_split, "band": layout_band, "ba": layout_beforeafter,
           "charbig": layout_charbig, "photo": layout_photo,
           "bold": layout_bold}.get(kind, layout_hero)(spec)
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
