"""サムネイル生成（1280x720）。

背景 + メインキャラ + 大きな縁取りテキスト2段。
台本 meta.thumbnail の top / bottom を使う。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from .assets_gen import background_path, sprite_path
from .compose import _cover
from .config import Config, Project

W, H = 1280, 720


def _outlined_text(canvas: Image.Image, xy: tuple[int, int], text: str,
                   font, fill: tuple, stroke: int) -> None:
    d = ImageDraw.Draw(canvas)
    d.text(xy, text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(20, 20, 20))


def run_thumbnail(cfg: Config, proj: Project) -> Path:
    from PIL import ImageFont

    script = proj.load_script()
    th = script.meta.thumbnail
    top = th.top or script.meta.title[:12]
    bottom = th.bottom

    font_path = cfg.find_pillow_font()
    bg = Image.open(background_path(cfg, script.scenes[0].background)).convert("RGB")
    canvas = _cover(bg, W, H)
    canvas = ImageEnhance.Brightness(canvas).enhance(0.9)
    canvas = canvas.filter(ImageFilter.GaussianBlur(1)).convert("RGBA")

    # メインキャラ（最初の話者）を右側に大きく（立ち絵オフ時は出さない）
    show_chars = bool(cfg.get("video", "show_characters", default=True))
    speakers = script.speakers_used()
    if show_chars and speakers:
        sp = Image.open(sprite_path(cfg, speakers[0], "surprised")).convert("RGBA")
        scale = (H * 0.92) / sp.height
        sp = sp.resize((int(sp.width * scale), int(sp.height * scale)), Image.LANCZOS)
        canvas.paste(sp, (W - sp.width - 20, H - sp.height), sp)

    def fit_font(text: str, max_w: int, start: int) -> "ImageFont.FreeTypeFont":
        size = start
        while size > 30:
            f = ImageFont.truetype(font_path, size=size, index=0)
            if ImageDraw.Draw(canvas).textlength(text, font=f) <= max_w:
                return f
            size -= 6
        return ImageFont.truetype(font_path, size=30, index=0)

    text_w = int(W * 0.62) if show_chars else int(W * 0.88)
    if top:
        f = fit_font(top, text_w, 88)
        _outlined_text(canvas, (46, 60), top, f, (255, 255, 255), 10)
    if bottom:
        f = fit_font(bottom, text_w, 150)
        _outlined_text(canvas, (46, H - 220), bottom, f, (255, 232, 60), 12)

    out = proj.out_dir / "thumbnail.png"
    canvas.convert("RGB").save(out)
    print(f"サムネイル -> {out}")
    return out
