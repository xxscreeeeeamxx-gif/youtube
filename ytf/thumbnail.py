"""サムネイル生成（1280x720）。

YouTube映えする派手なデザイン:
- 背景写真を強く色調補正（暗く・彩度up・ビネット・テーマ色グラデ）
- キャラの背後に放射状の光線 + 巨大な半透明記号（？など）
- キャラは白フチ（ステッカー風）+ ドロップシャドウで背景から浮かせる
- 上段はマーカー風の斜めハイライトボックス、下段は極太多重フチの巨大文字

台本 meta.thumbnail の top / bottom / accent / symbol / emotion / bg を使う。
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from .assets_gen import background_path, sprite_path
from .compose import _cover
from .config import Config, Project

W, H = 1280, 720

# slug から自動で選ぶ派手なテーマ色パレット（濃いめ・文字が乗る前提）
_PALETTE = [
    (232, 53, 43),    # レッド
    (255, 122, 0),    # オレンジ
    (30, 123, 232),   # ブルー
    (138, 63, 252),   # パープル
    (18, 161, 80),    # グリーン
    (232, 54, 143),   # ピンク
    (15, 181, 174),   # ティール
    (255, 176, 0),    # アンバー
]


def _hex_rgb(s: str) -> tuple[int, int, int] | None:
    s = (s or "").lstrip("#")
    if len(s) == 6:
        try:
            return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore
        except ValueError:
            return None
    return None


def _darken(c: tuple[int, int, int], f: float) -> tuple[int, int, int]:
    return tuple(int(v * f) for v in c)  # type: ignore


def _lighten(c: tuple[int, int, int], f: float) -> tuple[int, int, int]:
    return tuple(int(v + (255 - v) * f) for v in c)  # type: ignore


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=max(size, 12), index=0)


def _fit_font(draw: ImageDraw.ImageDraw, path: str, text: str, max_w: int,
              start: int, floor: int = 30) -> ImageFont.FreeTypeFont:
    size = start
    while size > floor:
        f = _font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return _font(path, floor)


def _rays(size: tuple[int, int], center: tuple[int, int], color: tuple[int, int, int],
          n: int = 18, alpha: int = 60) -> Image.Image:
    """放射状の光線レイヤー。"""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = center
    R = int(math.hypot(size[0], size[1]))
    for i in range(n):
        a0 = (i / n) * 2 * math.pi
        a1 = a0 + (math.pi / n) * 0.9
        d.polygon([(cx, cy),
                   (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))],
                  fill=(*color, alpha))
    return layer.filter(ImageFilter.GaussianBlur(2))


def _sticker(sprite: Image.Image, pad: int = 14) -> Image.Image:
    """立ち絵に白フチ（ステッカー風）+ ドロップシャドウを付けた画像を返す。"""
    a = sprite.split()[-1]
    grown = a
    for _ in range(pad):
        grown = grown.filter(ImageFilter.MaxFilter(3))
    canvas = Image.new("RGBA", (sprite.width + pad * 4, sprite.height + pad * 4), (0, 0, 0, 0))
    off = (pad * 2, pad * 2)
    # 影
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    smask = Image.new("L", canvas.size, 0)
    smask.paste(grown, (off[0] + 10, off[1] + 14))
    shadow.putalpha(smask.point(lambda v: int(v * 0.55)))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)))
    # 白フチ
    white = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    wmask = Image.new("L", canvas.size, 0)
    wmask.paste(grown, off)
    white.paste((255, 255, 255, 255), (0, 0), wmask)
    canvas.alpha_composite(white)
    # 本体
    canvas.alpha_composite(sprite, off)
    return canvas


def _punch_text(path: str, text: str, size: int, fill: tuple[int, int, int],
                stroke_col: tuple[int, int, int], stroke: int) -> Image.Image:
    """白抜き文字にテーマ色フチ + 黒フチ + 影を重ねたRGBA画像を返す。"""
    f = _font(path, size)
    tmp = Image.new("RGBA", (10, 10))
    box = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=f, stroke_width=stroke + 6)
    tw, th = box[2] - box[0], box[3] - box[1]
    pad = stroke + 20
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = pad - box[0], pad - box[1]
    # 影
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((ox + 6, oy + 7), text, font=f, fill=(0, 0, 0, 210),
                            stroke_width=stroke + 6, stroke_fill=(0, 0, 0, 210))
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    # 黒フチ（外）→ テーマ色フチ（中）→ 白（芯）
    d.text((ox, oy), text, font=f, fill=stroke_col, stroke_width=stroke + 6,
           stroke_fill=(15, 15, 20))
    d.text((ox, oy), text, font=f, fill=fill, stroke_width=stroke,
           stroke_fill=stroke_col)
    return layer


def run_thumbnail(cfg: Config, proj: Project) -> Path:
    script = proj.load_script()
    th = script.meta.thumbnail
    top = th.top or script.meta.title[:12]
    bottom = th.bottom
    font_path = cfg.find_pillow_font()

    # テーマ色: 明示指定 > slugハッシュで自動選択
    accent = _hex_rgb(th.accent)
    if accent is None:
        idx = int(hashlib.sha1(script.meta.slug.encode()).hexdigest(), 16) % len(_PALETTE)
        accent = _PALETTE[idx]

    # ---- 背景: 強めに色調補正して「生の動画フレーム感」を消す ----
    bg_name = th.bg or script.scenes[0].background
    bg = Image.open(background_path(cfg, bg_name)).convert("RGB")
    canvas = _cover(bg, W, H)
    canvas = ImageEnhance.Color(canvas).enhance(1.35)
    canvas = ImageEnhance.Contrast(canvas).enhance(1.12)
    canvas = ImageEnhance.Brightness(canvas).enhance(0.44)
    canvas = canvas.filter(ImageFilter.GaussianBlur(2)).convert("RGBA")

    # テーマ色を左下から差し込むグラデ + 上下の締め
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        a = int(150 * (y / H) ** 1.5)
        gd.line([(0, y), (W, y)], fill=(*_darken(accent, 0.5), a))
    canvas.alpha_composite(grad)
    # ビネット
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse([-W * 0.3, -H * 0.3, W * 1.3, H * 1.3], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 235))
    dark.putalpha(Image.eval(vig, lambda v: 235 - v))
    canvas.alpha_composite(dark)

    show_chars = bool(cfg.get("video", "show_characters", default=True))
    speakers = script.speakers_used()
    char_cx = int(W * 0.74)

    # ---- 放射光線（キャラ背後）----
    canvas.alpha_composite(_rays((W, H), (char_cx, int(H * 0.42)),
                                 _lighten(accent, 0.25), alpha=60))

    # ---- 巨大記号（背景の抜け感）----
    if th.symbol:
        sym_f = _font(font_path, 620)
        sym = Image.new("RGBA", (720, 760), (0, 0, 0, 0))
        ImageDraw.Draw(sym).text((360, 380), th.symbol, font=sym_f, anchor="mm",
                                 fill=(255, 255, 255, 40), stroke_width=10,
                                 stroke_fill=(*accent, 120))
        sym = sym.rotate(-8, expand=True, resample=Image.BICUBIC)
        canvas.alpha_composite(sym, (int(W * 0.34), int(H * 0.05)))

    # ---- メインキャラ（白フチ+影で浮かせる）----
    if show_chars and speakers:
        raw = Image.open(sprite_path(cfg, speakers[0], th.emotion)).convert("RGBA")
        scale = (H * 1.02) / raw.height
        raw = raw.resize((int(raw.width * scale), int(raw.height * scale)), Image.LANCZOS)
        sticker = _sticker(raw)
        canvas.alpha_composite(sticker, (W - sticker.width + 30, H - sticker.height + 10))

    d = ImageDraw.Draw(canvas)
    text_w = int(W * 0.60) if (show_chars and speakers) else int(W * 0.9)

    # ---- 上段: マーカー風ハイライトボックス ----
    if top:
        f = _fit_font(d, font_path, top, text_w, 74, 34)
        tb = d.textbbox((0, 0), top, font=f)
        tw, tht = tb[2] - tb[0], tb[3] - tb[1]
        box = Image.new("RGBA", (tw + 60, tht + 44), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle([0, 0, tw + 59, tht + 43], radius=14,
                                              fill=(*accent, 255))
        ImageDraw.Draw(box).text((30 - tb[0], 20 - tb[1]), top, font=f,
                                 fill=(255, 255, 255), stroke_width=2,
                                 stroke_fill=_darken(accent, 0.55))
        box = box.rotate(-3, expand=True, resample=Image.BICUBIC)
        canvas.alpha_composite(box, (40, 44))

    # ---- 下段: 極太多重フチの巨大文字 ----
    if bottom:
        # ？を除いた実効幅で判定しつつ、はみ出しは自動縮小
        size = 160
        while size > 60:
            layer = _punch_text(font_path, bottom, size, (255, 255, 255),
                                _lighten(accent, 0.1), 8)
            if layer.width <= int(W * (0.66 if (show_chars and speakers) else 0.94)):
                break
            size -= 8
        layer = layer.rotate(2, expand=True, resample=Image.BICUBIC)
        canvas.alpha_composite(layer, (34, H - layer.height - 26))

    # ---- チャンネルバッジ（右上）----
    ch = str(cfg.get("channel", "name", default="") or "")
    if ch:
        bf = _font(font_path, 30)
        bb = d.textbbox((0, 0), ch, font=bf)
        bw = bb[2] - bb[0]
        d.rounded_rectangle([W - bw - 72, 26, W - 24, 78], radius=26,
                            fill=(15, 18, 26, 220), outline=(*accent, 255), width=3)
        d.text((W - bw - 48 - bb[0], 38 - bb[1]), ch, font=bf, fill=(240, 244, 252))

    out = proj.out_dir / "thumbnail.png"
    canvas.convert("RGB").save(out)
    print(f"サムネイル -> {out}")
    return out
