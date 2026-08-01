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
    cols = {"red": (255, 90, 70), "yellow": (255, 210, 70), "green": (60, 220, 140)}
    for i, name in enumerate(["green", "yellow", "red"]):
        cx = s*0.24 + i * s*0.26
        on = name == active
        c = cols[name] if on else tuple(int(v*0.25) for v in cols[name])
        d.ellipse([cx-s*0.09, s*0.39, cx+s*0.09, s*0.57], fill=c)
        if on:
            d.ellipse([cx-s*0.12, s*0.36, cx+s*0.12, s*0.60],
                      outline=(255, 255, 255), width=6)


# ---------------------------------------------------------------- レイアウト

def layout_hero(spec):
    c1, c2 = spec.get("bg", ((52, 20, 86), (78, 32, 120)))
    img = rays((W, H), c1, c2)
    pr = prop_layer(spec["prop"], tilt=spec.get("tilt", -12))
    scale = spec.get("prop_h", 500) / pr.height
    pr = pr.resize((int(pr.width*scale), int(pr.height*scale)), Image.LANCZOS)
    img.alpha_composite(pr, (int(W*0.30) - pr.width//2, int(H*0.46) - pr.height//2))
    b = bust("zundamon", spec.get("emotion", "surprised"), 470)
    img.alpha_composite(b, (W - b.width + 40, H - b.height + 70))
    big_text(img, (30, 30), spec["top"], spec.get("top_size", 76),
             (255, 255, 255, 255), (20, 20, 30, 255), (20, 20, 30, 255),
             rotate=1, kind=spec.get("top_font", "w9"))
    bf = spec.get("bottom_font", "genkai")
    if not has_glyphs(bf, spec["bottom"]):
        bf = "w9"
    big_text(img, (24, H - spec.get("bottom_size", 132) - 105), spec["bottom"],
             spec.get("bottom_size", 132), spec.get("bottom_fill", (255, 225, 40, 255)),
             spec.get("bottom_edge", (150, 30, 20, 255)), (25, 8, 8, 255),
             rotate=-2, kind=bf)
    return vignette(img, 100)


def layout_split(spec):
    """左右分割のビフォー/アフター。"""
    img = Image.new("RGBA", (W, H))
    lc = spec.get("left_bg", (34, 38, 56))
    rc1, rc2 = spec.get("right_bg", ((250, 205, 50), (255, 226, 110)))
    img.paste(Image.new("RGBA", (W, H), (*lc, 255)), (0, 0))
    right = rays((W, H), rc1, rc2, n=24, center=(0.75, 0.4))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([(W*0.54, 0), (W, 0), (W, H), (W*0.44, H)], fill=255)
    img.paste(right, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.line([(W*0.54, 0), (W*0.44, H)], fill=(255, 255, 255), width=12)
    # 左右の小物
    for side, key, cx in [("l", "prop_l", 0.24), ("r", "prop_r", 0.72)]:
        fn = spec.get(key)
        if not fn:
            continue
        pr = prop_layer(fn, tilt=-8 if side == "l" else 8)
        scale = spec.get("prop_h", 330) / pr.height
        pr = pr.resize((int(pr.width*scale), int(pr.height*scale)), Image.LANCZOS)
        img.alpha_composite(pr, (int(W*cx) - pr.width//2, int(H*0.44) - pr.height//2))
    b = bust("zundamon", spec.get("emotion", "surprised"), 400)
    img.alpha_composite(b, (W - b.width + 30, H - b.height + 60))
    # 文字: 左上(ビフォー)・左下 / 右下(アフター)
    big_text(img, (26, 26), spec["left_top"], 62, (230, 234, 244, 255),
             (16, 18, 26, 255), (16, 18, 26, 255))
    lf = spec.get("left_font", "genkai")
    if not has_glyphs(lf, spec["left_big"]):
        lf = "w9"
    big_text(img, (20, H - 210), spec["left_big"], 104,
             spec.get("left_fill", (255, 90, 80, 255)),
             spec.get("left_edge", (255, 255, 255, 255)),
             (20, 8, 8, 255), rotate=-2, kind=lf)
    rf = spec.get("right_font", "851")
    if not has_glyphs(rf, spec["right_big"]):
        rf = "w9"
    big_text(img, (int(W*0.52), 40), spec["right_big"], 88,
             spec.get("right_fill", (40, 44, 60, 255)),
             spec.get("right_edge", (18, 22, 32, 255)),
             (255, 255, 255, 255), rotate=2, kind=rf)
    return vignette(img, 80)


# ---------------------------------------------------------------- 動画ごとの仕様

SPECS = {
    # 開発秘話・挑戦もの → 851（熱血の殴り書き）
    "karaoke": dict(layout="hero", prop=p_mic, tilt=-16,
                    bg=((52, 20, 86), (78, 32, 120)),
                    top="手作り11台から世界へ", bottom="特許、取らず。",
                    bottom_font="851", emotion="surprised"),
    "cutter-knife": dict(layout="hero", prop=p_blade, tilt=0,
                         bg=((22, 58, 92), (28, 76, 118)),
                         top="ヒントは板チョコ", bottom="折る刃、世界へ。",
                         bottom_font="851", emotion="happy"),
    "washlet": dict(layout="hero", prop=p_toilet, tilt=-8,
                    bg=((16, 66, 72), (22, 88, 96)),
                    top="社員300人が体を張った", bottom="前代未聞の開発。",
                    bottom_font="851", emotion="surprised"),
    "tenji-block-meme": dict(layout="hero", prop=p_block, tilt=-10,
                             bg=((20, 44, 84), (28, 60, 110)),
                             top="友の失明から生まれた", bottom="全財産を、道路に。",
                             bottom_font="w9", emotion="normal"),
    # 不穏・偽造・未解明 → genkai（崩壊明朝）
    "banknote": dict(layout="hero", prop=p_bill, tilt=-10,
                     bg=((44, 20, 52), (62, 28, 72)),
                     top="偽札は2年で343枚だけ", bottom="コピー、不可能。",
                     bottom_font="genkai", emotion="thinking"),
    # 対比もの（左右分割）
    "battery-80-duo": dict(layout="split",
                           left_bg=(52, 26, 30), right_bg=((24, 72, 52), (30, 92, 66)),
                           prop_l=lambda d, s: p_battery(d, s, 100, (255, 90, 70)),
                           prop_r=lambda d, s: p_battery(d, s, 80, (80, 220, 130)),
                           left_top="充電100%は", left_big="実は損",
                           left_font="851", left_fill=(255, 96, 86, 255),
                           right_big="80%が正解", right_font="851",
                           right_fill=(255, 255, 255, 255),
                           emotion="surprised"),
    "shinkansen-bird": dict(layout="split",
                            left_bg=(30, 34, 52), right_bg=((28, 90, 120), (36, 112, 148)),
                            prop_l=p_shinkansen, prop_r=p_kingfisher,
                            left_top="時速300キロの騒音", left_big="どうする？",
                            left_font="851", left_fill=(255, 235, 90, 255),
                            right_big="鳥が解決", right_font="851",
                            right_fill=(255, 255, 255, 255),
                            emotion="surprised"),
    "traffic-light": dict(layout="split",
                          left_bg=(24, 52, 36), right_bg=((30, 60, 130), (40, 78, 160)),
                          prop_l=lambda d, s: p_signal(d, s, "green"),
                          prop_r=lambda d, s: p_signal(d, s, "green"),
                          left_top="どう見ても", left_big="緑なのに",
                          left_font="w9", left_fill=(90, 230, 150, 255),
                          right_big="呼び名は青", right_font="851",
                          right_fill=(150, 200, 255, 255),
                          emotion="thinking"),
}


def render(slug, out_path=None):
    spec = SPECS[slug]
    img = layout_split(spec) if spec["layout"] == "split" else layout_hero(spec)
    out = out_path or Path(f"projects/{slug}/out/thumbnail.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


if __name__ == "__main__":
    slugs = sys.argv[1:] or list(SPECS)
    outdir = None
    if slugs and slugs[0] == "--sample":
        outdir = Path(slugs[1])
        slugs = slugs[2:] or list(SPECS)
    for slug in slugs:
        if slug not in SPECS:
            print(f"スキップ（SPECS未登録）: {slug}")
            continue
        dst = (outdir / f"tn_{slug}.png") if outdir else None
        print("生成:", render(slug, dst))
