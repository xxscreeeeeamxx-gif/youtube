"""動き演出用の描き素材（集中線・リアクション記号）。

PILで決定的に描いて assets/fx/ にキャッシュする。乱数はシード固定で、
同じ入力からは常に同じPNGができる（ビルドキャッシュを壊さないため）。
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .config import Config

MARK_SIZE = 160  # リアクション記号のキャンバス一辺

# emotion → 記号の種類
EMOTION_MARK = {"surprised": "bikkuri", "angry": "ikari",
                "thinking": "hatena", "sad": "ase"}


def _fx_dir(cfg: Config) -> Path:
    d = cfg.root / "assets" / "fx"
    d.mkdir(parents=True, exist_ok=True)
    return d


def speedlines(cfg: Config, w: int, h: int) -> str:
    """漫画の集中線（白・中央抜き）の透過PNGを返す。"""
    path = _fx_dir(cfg) / f"speed_{w}x{h}.png"
    if path.exists():
        return str(path)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h / 2
    rng = random.Random(7)
    r_out = math.hypot(cx, cy) + 10
    n = 56
    for i in range(n):
        a = (i / n) * 2 * math.pi + rng.uniform(-0.02, 0.02)
        half = math.radians(rng.uniform(0.3, 0.85))   # 線の太さ（角度幅）
        r_in = min(w, h) * rng.uniform(0.44, 0.58)     # 中央の抜き半径
        alpha = rng.randint(90, 165)
        pts = [
            (cx + r_out * math.cos(a - half), cy + r_out * math.sin(a - half)),
            (cx + r_out * math.cos(a + half), cy + r_out * math.sin(a + half)),
            (cx + r_in * math.cos(a), cy + r_in * math.sin(a)),
        ]
        d.polygon(pts, fill=(255, 255, 255, alpha))
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img.save(path)
    return str(path)


def _outline_text(d: ImageDraw.ImageDraw, xy, text, font, fill, stroke):
    d.text(xy, text, font=font, fill=fill, anchor="mm",
           stroke_width=10, stroke_fill=stroke)


def reaction_mark(cfg: Config, kind: str) -> str:
    """リアクション記号（bikkuri/hatena/ikari/ase）の透過PNGを返す。"""
    path = _fx_dir(cfg) / f"mark_{kind}.png"
    if path.exists():
        return str(path)
    s = MARK_SIZE
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if kind == "bikkuri":
        font = ImageFont.truetype(cfg.find_pillow_font(), int(s * 0.94))
        _outline_text(d, (s / 2, s / 2 - 6), "！", font,
                      (255, 222, 40, 255), (110, 60, 0, 255))
    elif kind == "hatena":
        font = ImageFont.truetype(cfg.find_pillow_font(), int(s * 0.9))
        _outline_text(d, (s / 2, s / 2 - 4), "？", font,
                      (120, 190, 255, 255), (20, 60, 120, 255))
    elif kind == "ikari":
        # 怒りマーク: 4本の丸い弧を十字に配置（漫画の青筋）
        red = (235, 60, 60, 255)
        cx = cy = s / 2
        rr = s * 0.30          # 弧の円半径
        off = s * 0.30         # 中心からのずらし
        lw = int(s * 0.11)
        for dx, dy in [(-off, -off), (off, -off), (off, off), (-off, off)]:
            box = [cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr]
            # 中心側に向いた弧だけ描く
            start = (math.degrees(math.atan2(-dy, -dx)) - 42) % 360
            d.arc(box, start=start, end=start + 84, fill=red, width=lw)
    elif kind == "ase":
        # 汗のしずく（水色・白ハイライト）
        blue = (150, 205, 255, 255)
        edge = (40, 90, 160, 255)
        cx, top, bot = s * 0.5, s * 0.12, s * 0.88
        r = s * 0.30
        cyc = bot - r
        d.ellipse([cx - r, cyc - r, cx + r, cyc + r], fill=blue,
                  outline=edge, width=7)
        d.polygon([(cx, top), (cx + r * 0.72, cyc - r * 0.55),
                   (cx - r * 0.72, cyc - r * 0.55)], fill=blue)
        d.line([(cx, top), (cx + r * 0.7, cyc - r * 0.5)], fill=edge, width=7)
        d.line([(cx, top), (cx - r * 0.7, cyc - r * 0.5)], fill=edge, width=7)
        d.ellipse([cx - r * 0.55, cyc - r * 0.25, cx - r * 0.1, cyc + r * 0.25],
                  fill=(255, 255, 255, 190))
    else:
        raise ValueError(f"unknown mark: {kind}")
    img.save(path)
    return str(path)
