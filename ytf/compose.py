"""カット静止画の合成（紙芝居の1枚1枚を作る）。

レイヤー構成: 背景 → 見出しバー → スライド/画像カード → キャラ立ち絵。
字幕はここでは描かず、FFmpegのASS焼き込みで載せる。

同一見た目のカットはハッシュで同一PNGを共有するので、
セリフ数が多くても合成は速い。
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from .assets_gen import background_path, sprite_path
from .config import Config, Project
from .schema import Script, Slide, Telop, split_reading
from .voice import CutTiming

# テロップの文字サイズ（画面幅に対する比率）
TELOP_SIZE_RATIO = {"sm": 0.032, "md": 0.045, "lg": 0.060, "xl": 0.080}


@dataclass
class Layout:
    w: int
    h: int
    vertical: bool
    char_h: int          # 立ち絵の表示高さ
    header_font: int
    slide_font: int


def layout_for(cfg: Config, vertical: bool) -> Layout:
    if vertical:
        w = int(cfg.get("shorts", "width", default=1080))
        h = int(cfg.get("shorts", "height", default=1920))
        return Layout(w, h, True, char_h=760, header_font=64, slide_font=52)
    w = int(cfg.get("video", "width", default=1920))
    h = int(cfg.get("video", "height", default=1080))
    return Layout(w, h, False, char_h=640, header_font=54, slide_font=46)


# 再現ドラマの立ち絵倍率。お手本準拠で画面の主役になる大きさ（腰上構図ぎみ）
DRAMA_SCALE = 1.42


class Composer:
    def __init__(self, cfg: Config, proj: Project, vertical: bool = False):
        self.cfg = cfg
        self.proj = proj
        self.lay = layout_for(cfg, vertical)
        self.show_chars = bool(cfg.get("video", "show_characters", default=True))
        self.font_path = cfg.find_pillow_font()
        self._sprite_cache: dict[tuple[str, str, bool], Image.Image] = {}
        self._bg_cache: dict[str, Image.Image] = {}
        # アクセント色（見出し・カードの装飾に使う）。最初のキャラ色 or 既定の青
        cols = [c.get("color") for c in cfg.characters.values() if c.get("color")]
        self.accent = _hex_rgb(cols[0]) if cols else (58, 160, 255)
        self.ink = (28, 32, 44)  # 本文の濃色

    # ---------- 部品 ----------

    def font(self, size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(self.font_path, size=size, index=0)

    def _bg(self, name: str) -> Image.Image:
        if name not in self._bg_cache:
            img = Image.open(background_path(self.cfg, name)).convert("RGB")
            self._bg_cache[name] = _cover(img, self.lay.w, self.lay.h)
        return self._bg_cache[name]

    def _sprite(self, speaker: str, emotion: str, active: bool,
                flip_override: bool | None = None, scale_mult: float = 1.0) -> Image.Image:
        key = (speaker, emotion, active, flip_override, round(scale_mult, 3))
        if key not in self._sprite_cache:
            ch = self.cfg.character(speaker)
            img = Image.open(sprite_path(self.cfg, speaker, emotion)).convert("RGBA")
            flip = ch.get("sprite_flip") if flip_override is None else flip_override
            if flip:
                # 素材の向きが外向きのキャラは反転して内側（相手側）を向かせる
                img = ImageOps.mirror(img)
            # sprite_scale: キャラごとの体格差（ちびキャラは小さく描く）
            base = self.lay.char_h * float(ch.get("sprite_scale", 1.0)) * scale_mult
            scale = (base if active else base * 0.9) / img.height
            img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
            if not active:
                # 非話者は暗くして視線誘導
                rgb = ImageEnhance.Brightness(img.convert("RGB")).enhance(0.55)
                img = Image.merge("RGBA", (*rgb.split(), img.split()[3]))
            self._sprite_cache[key] = img
        return self._sprite_cache[key]

    def _draw_header(self, canvas: Image.Image, title: str) -> None:
        if not title:
            return
        title = split_reading(title)[0]
        d = ImageDraw.Draw(canvas, "RGBA")
        size = self.lay.header_font
        f = self.font(size)
        while d.textlength(title, font=f) > self.lay.w - 260 and size > 26:
            size -= 4
            f = self.font(size)
        tw = d.textlength(title, font=f)
        # 左上に配置。左端にアクセントバー付きのダークタブ
        m = 44
        bar_w, gap, pad = 12, 22, 30
        x0, y0 = m, 40
        h = size + 30
        x1 = x0 + bar_w + gap + tw + pad
        y1 = y0 + h
        d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=(22, 26, 38, 230))
        d.rounded_rectangle([x0 + 10, y0 + 12, x0 + 10 + bar_w, y1 - 12],
                            radius=6, fill=(*self.accent, 255))
        d.text((x0 + 10 + bar_w + gap, y0 + (h - size) / 2 - 2), title,
               font=f, fill=(245, 247, 252))

    def _card_box(self) -> tuple[int, int, int, int]:
        if self.lay.vertical:
            return (60, 210, self.lay.w - 60, 980)
        if not self.show_chars:
            # 立ち絵なし: 左右の余白を詰めてカードを大きく使う（見出しの下から）
            return (190, 200, self.lay.w - 190, self.lay.h - 210)
        return (400, 180, self.lay.w - 400, self.lay.h - 330)

    def _card_band(self) -> tuple[int, int]:
        """カードを縦方向に中央寄せする帯（上端, 下端）。"""
        if self.lay.vertical:
            return (210, 990)
        return (196, self.lay.h - 116)

    def _draw_card(self, canvas: Image.Image, box=None) -> tuple[int, int, int, int]:
        box = tuple(box or self._card_box())
        x0, y0, x1, y1 = box
        r = 30
        # 影（ぼかした暗い矩形をずらして敷く）
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle([x0 + 6, y0 + 16, x1 + 6, y1 + 20], radius=r,
                             fill=(10, 14, 24, 115))
        canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))
        d = ImageDraw.Draw(canvas, "RGBA")
        # カード本体（ごく淡いオフホワイト＋細い枠）
        d.rounded_rectangle(box, radius=r, fill=(252, 252, 254, 247),
                            outline=(*self.accent, 90), width=2)
        # 上辺のアクセントライン
        d.rounded_rectangle([x0 + r, y0, x1 - r, y0 + 7], radius=3,
                            fill=(*self.accent, 255))
        return box

    def card_inner_box(self) -> tuple[int, int, int, int]:
        """カード内側（パディング込み）の領域。動画クリップの配置に使う。"""
        x0, y0, x1, y1 = self._card_box()
        return (x0 + 26, y0 + 26, x1 - 26, y1 - 26)

    def _draw_slide(self, canvas: Image.Image, slide: Slide) -> None:
        d = ImageDraw.Draw(canvas, "RGBA")
        fx0, _, fx1, _ = self._card_box()
        inner_w = fx1 - fx0 - 130
        pad_top, pad_bot = 56, 56

        # --- 1) 内容の高さと行を先に計算する（カード高さを内容に合わせるため） ---
        title_f = self.font(int(self.lay.slide_font * 1.3))
        title_zone = 0
        if slide.title:
            title_zone = int(self.lay.slide_font * 1.3) + 20 + 6 + 68

        body: list[tuple] = []      # (line, font, line_height, is_bullet_head)
        if slide.big:
            bf = self.font(int(self.lay.slide_font * 1.9))
            blh = int(self.lay.slide_font * 1.9) + 28
            for ln in _wrap(d, split_reading(slide.big)[0], bf, inner_w):
                body.append((ln, bf, blh, False))
        else:
            bf = self.font(self.lay.slide_font)
            blh = self.lay.slide_font + 48
            for b in slide.bullets:
                wl = _wrap(d, split_reading(b)[0], bf, inner_w - 60)
                for j, ln in enumerate(wl):
                    body.append((ln, bf, blh, j == 0))
        body_h = sum(r[2] for r in body)
        content_h = title_zone + body_h

        # --- 2) カード高さ = 内容 + 余白。帯の中で縦中央寄せ ---
        band_t, band_b = self._card_band()
        card_h = min(content_h + pad_top + pad_bot, band_b - band_t)
        y0 = band_t + (band_b - band_t - card_h) // 2
        box = (fx0, y0, fx1, y0 + card_h)
        x0, _, x1, y1 = self._draw_card(canvas, box)
        d = ImageDraw.Draw(canvas, "RGBA")
        cx = (x0 + x1) // 2

        # --- 3) 内容を上から順に描く（全体は中央寄せ済み） ---
        y = y0 + pad_top
        if slide.title:
            title = split_reading(slide.title)[0]
            tw = d.textlength(title, font=title_f)
            d.text((cx - tw / 2, y), title, font=title_f, fill=self.accent)
            y += int(self.lay.slide_font * 1.3) + 20
            d.rounded_rectangle([cx - 65, y, cx + 65, y + 6], radius=3,
                                fill=(*self.accent, 255))
            y += 44

        if slide.big:
            for ln, f, lh, _ in body:
                tw = d.textlength(ln, font=f)
                d.text((cx - tw / 2, y), ln, font=f, fill=self.ink)
                y += lh
        else:
            # 箇条書きブロックを水平方向にも中央寄せ（最長行を基準に）
            dot = max(7, self.lay.slide_font // 5)
            indent = dot * 2 + 22
            block_w = indent + max((d.textlength(ln, font=f) for ln, f, _, _ in body),
                                   default=0)
            bx = int(cx - block_w / 2)
            for ln, f, lh, head in body:
                if head:
                    cyd = y + self.lay.slide_font // 2
                    d.ellipse([bx, cyd - dot, bx + dot * 2, cyd + dot],
                              fill=(*self.accent, 255))
                d.text((bx + indent, y), ln, font=f, fill=self.ink)
                y += lh

    def _draw_telop(self, canvas: Image.Image, t: Telop) -> None:
        """キーワードテロップ。縁取り＋（任意で）光彩付きの大文字を指定位置に描く。"""
        text = split_reading(t.text)[0]
        size = int(self.lay.w * TELOP_SIZE_RATIO.get(t.size, 0.060))
        d = ImageDraw.Draw(canvas)
        f = self.font(size)
        max_w = self.lay.w - 100
        while d.textlength(text, font=f) > max_w and size > 24:
            size -= 4
            f = self.font(size)
        tw = d.textlength(text, font=f)
        margin = int(self.lay.w * 0.045)
        vert, _, horiz = t.position.partition("-")
        x = {
            "left": margin,
            "center": (self.lay.w - tw) / 2,
            "right": self.lay.w - tw - margin,
        }[horiz]
        y = {
            "top": margin,
            "middle": (self.lay.h - size) / 2,
            "bottom": self.lay.h - size * 1.45 - margin,
        }[vert]
        stroke_w = max(3, size // 14)

        if t.glow:
            glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            gd.text((x, y), text, font=f, fill=t.glow,
                    stroke_width=stroke_w * 3, stroke_fill=t.glow)
            glow = glow.filter(ImageFilter.GaussianBlur(max(6, size // 7)))
            canvas.alpha_composite(glow)
            canvas.alpha_composite(glow)  # 2回重ねて光を強める

        d = ImageDraw.Draw(canvas)
        d.text((x, y), text, font=f, fill=t.color,
               stroke_width=stroke_w, stroke_fill=t.stroke)

    def _draw_image(self, canvas: Image.Image, image_rel: str) -> None:
        p = self.proj.root / image_rel
        if not p.exists():
            p = self.cfg.root / image_rel
        if not p.exists():
            raise SystemExit(f"画像がありません: {image_rel}")
        x0, y0, x1, y1 = self._draw_card(canvas)
        inner_w, inner_h = (x1 - x0) - 48, (y1 - y0) - 48
        img = Image.open(p).convert("RGBA")
        scale = min(inner_w / img.width, inner_h / img.height)
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
        canvas.paste(img, (x0 + 24 + (inner_w - img.width) // 2,
                           y0 + 24 + (inner_h - img.height) // 2), img)

    # ---------- 1カットの合成 ----------

    def compose_cut(
        self,
        background: str,
        header: str,
        chars: list[tuple[str, str, bool]],  # (speaker, emotion, active)
        slide: Slide | None,
        image: str | None,
        video_card: bool = False,  # True なら空カードを描く（動画は後段でoverlay）
        fg_only: bool = False,     # True なら背景を敷かず透過PNG（背景は後段でzoompan）
        telops: list[Telop] | None = None,
        with_telops: bool = True,  # False ならテロップは焼かない（別レイヤーで動かす用）
        stage: list[dict] | None = None,   # 再現ドラマ: 舞台配置 [{who,emotion,x,flip,scale,tag}]
        bubble: dict | None = None,        # 再現ドラマ: 話者の吹き出し {text, x, color}
        caption: str | None = None,        # 再現ドラマ: ナレーション字幕（下部）
        actor: str | None = None,          # 再現ドラマ: 基底に描かず後段で動かす話者
        bubble_layered: bool = False,      # True なら吹き出しは基底に描かない（最前面レイヤー）
    ) -> Image.Image:
        if not with_telops:
            telops = []
        if fg_only:
            canvas = Image.new("RGBA", (self.lay.w, self.lay.h), (0, 0, 0, 0))
        else:
            canvas = self._bg(background).copy().convert("RGBA")
        self._draw_header(canvas, header)
        if slide is not None:
            self._draw_slide(canvas, slide)
        elif video_card:
            self._draw_card(canvas)
        elif image:
            self._draw_image(canvas, image)

        if stage is not None:
            # ---- 再現ドラマ: 舞台配置（暗転なし・自由なx位置・名札） ----
            for m in stage:
                sp, x, y = self.drama_actor(m)
                if actor is not None and m["who"] == actor:
                    # 話者は build 側で動く別レイヤー。名札だけ基底に静止で描く
                    if m.get("tag"):
                        self._draw_tag(canvas, m["tag"], x + sp.width // 2, y)
                    continue
                canvas.paste(sp, (x, y), sp)
                if m.get("tag"):
                    self._draw_tag(canvas, m["tag"], x + sp.width // 2, y)
            if bubble and not bubble_layered:
                self._draw_bubble(canvas, bubble["text"], float(bubble["x"]),
                                  edge=bubble.get("color"))
            if caption:
                self._draw_caption(canvas, caption)
            for t in telops or []:
                self._draw_telop(canvas, t)
            return canvas if fg_only else canvas.convert("RGB")

        if not self.show_chars:
            # 立ち絵を出さない構成（テロップ主体）
            for t in telops or []:
                self._draw_telop(canvas, t)
            return canvas if fg_only else canvas.convert("RGB")

        if self.lay.vertical:
            # 縦動画は話者のみを画面下端に。字幕はこの上に載る
            for speaker, emotion, active in chars:
                if not active:
                    continue
                sp = self._sprite(speaker, emotion, True)
                canvas.paste(sp, ((self.lay.w - sp.width) // 2, self.lay.h - sp.height + 30), sp)
        else:
            for speaker, emotion, active in chars:
                sp = self._sprite(speaker, emotion, active)
                pos = self.cfg.character(speaker).get("position", "right")
                if pos == "left":
                    x = 40
                else:
                    x = self.lay.w - sp.width - 40
                canvas.paste(sp, (x, self.lay.h - sp.height), sp)
        for t in telops or []:
            self._draw_telop(canvas, t)
        return canvas if fg_only else canvas.convert("RGB")

    def bubble_layer(self, bubble: dict) -> Image.Image:
        """吹き出しだけの透過レイヤー（動く立ち絵より前面に重ねる用）。"""
        canvas = Image.new("RGBA", (self.lay.w, self.lay.h), (0, 0, 0, 0))
        self._draw_bubble(canvas, bubble["text"], float(bubble["x"]),
                          edge=bubble.get("color"))
        return canvas

    def drama_actor(self, m: dict) -> tuple[Image.Image, int, int]:
        """再現ドラマの立ち絵1体ぶんの (画像, x, y)。基底描画と動くレイヤーで共用。"""
        sp = self._sprite(m["who"], m.get("emotion", "normal"), True,
                          flip_override=m.get("flip"),
                          scale_mult=float(m.get("scale", 1.0)) * DRAMA_SCALE)
        x = int(self.lay.w * float(m["x"]) - sp.width / 2)
        x = max(-sp.width // 3, min(x, self.lay.w - sp.width * 2 // 3))
        # 少し沈めて腰上構図に寄せる（足元5%はフレーム外）
        y = self.lay.h - int(sp.height * 0.95)
        return sp, x, y

    def _draw_tag(self, canvas: Image.Image, text: str, cx: int, y_top: int) -> None:
        """キャラ頭上の名札（オレンジの小箱・白フチ）。"""
        d = ImageDraw.Draw(canvas, "RGBA")
        f = self.font(30)
        tw = d.textlength(text, font=f)
        x0 = int(cx - tw / 2 - 18)
        y0 = max(96, y_top - 48)
        d.rounded_rectangle([x0, y0, x0 + tw + 36, y0 + 46], radius=10,
                            fill=(238, 120, 34, 255), outline=(255, 255, 255), width=3)
        d.text((x0 + 18, y0 + 7), text, font=f, fill=(255, 255, 255),
               stroke_width=2, stroke_fill=(90, 40, 8))

    def _draw_bubble(self, canvas: Image.Image, text: str, x_frac: float,
                     edge: str | None = None) -> None:
        """話者の上に出す吹き出し（白地・話者色フチ・黒太字）。短文前提で最大3行。"""
        edge_rgb = _hex_rgb(edge) if edge else (46, 174, 92)
        text = split_reading(text)[0]
        d = ImageDraw.Draw(canvas, "RGBA")
        f = self.font(38)
        # 12〜14文字で折り返し（句読点優先ではなく単純分割で十分短い前提）
        limit = 14
        lines = [text[i:i + limit] for i in range(0, len(text), limit)][:3]
        if len(text) > limit * 3:
            lines[-1] = lines[-1][:limit - 1] + "…"
        lh = 52
        tw = max(d.textlength(ln, font=f) for ln in lines)
        pad_x, pad_y = 26, 18
        bw, bh = int(tw + pad_x * 2), lh * len(lines) + pad_y * 2
        cx = int(self.lay.w * x_frac)
        x0 = max(16, min(cx - bw // 2, self.lay.w - bw - 16))
        y0 = 120
        d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=18,
                            fill=(255, 255, 255, 245), outline=edge_rgb, width=5)
        # しっぽ（話者の方向へ）
        tip_x = max(x0 + 30, min(cx, x0 + bw - 30))
        d.polygon([(tip_x - 16, y0 + bh - 2), (tip_x + 16, y0 + bh - 2),
                   (tip_x, y0 + bh + 26)], fill=edge_rgb)
        d.polygon([(tip_x - 10, y0 + bh - 4), (tip_x + 10, y0 + bh - 4),
                   (tip_x, y0 + bh + 16)], fill=(255, 255, 255))
        for i, ln in enumerate(lines):
            d.text((x0 + pad_x, y0 + pad_y + i * lh), ln, font=f, fill=(24, 26, 34))

    def _draw_caption(self, canvas: Image.Image, text: str) -> None:
        """ナレーション字幕（下部・暗帯+白文字に琥珀フチ）。最大2行。"""
        text = split_reading(text)[0]
        d = ImageDraw.Draw(canvas, "RGBA")
        f = self.font(42)
        limit = 26
        lines = [text[i:i + limit] for i in range(0, len(text), limit)][:2]
        if len(text) > limit * 2:
            lines[-1] = lines[-1][:limit - 1] + "…"
        lh = 58
        tw = max(d.textlength(ln, font=f) for ln in lines)
        bh = lh * len(lines) + 28
        y1 = self.lay.h - 26
        y0 = y1 - bh
        x0 = int(self.lay.w / 2 - tw / 2 - 34)
        x1 = int(self.lay.w / 2 + tw / 2 + 34)
        d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=(12, 14, 22, 175))
        for i, ln in enumerate(lines):
            lw = d.textlength(ln, font=f)
            d.text((self.lay.w / 2 - lw / 2, y0 + 16 + i * lh), ln, font=f,
                   fill=(255, 252, 240), stroke_width=3, stroke_fill=(140, 96, 20))

    def telop_layer(self, telops: list[Telop]) -> Image.Image:
        """テロップだけを描いた透過フレーム（build でアニメ付き overlay に使う）。"""
        canvas = Image.new("RGBA", (self.lay.w, self.lay.h), (0, 0, 0, 0))
        for t in telops:
            self._draw_telop(canvas, t)
        return canvas

    def transition_layer(self, title: str) -> Image.Image:
        """章の切替: 全画面のダークパネル＋章タイトル（横スライドのワイプに使う）。"""
        w, h = self.lay.w, self.lay.h
        canvas = Image.new("RGBA", (w, h), (16, 20, 30, 255))
        d = ImageDraw.Draw(canvas, "RGBA")
        cy = h // 2
        title = split_reading(title)[0]
        size = 82
        f = self.font(size)
        while d.textlength(title, font=f) > w - 220 and size > 40:
            size -= 4
            f = self.font(size)
        tw = d.textlength(title, font=f)
        # タイトルの上下にアクセントライン
        half = tw / 2 + 30
        d.rounded_rectangle([w / 2 - half, cy - size / 2 - 34,
                             w / 2 + half, cy - size / 2 - 27], radius=3,
                            fill=(*self.accent, 255))
        d.rounded_rectangle([w / 2 - half, cy + size / 2 + 27,
                             w / 2 + half, cy + size / 2 + 34], radius=3,
                            fill=(*self.accent, 255))
        d.text(((w - tw) / 2, cy - size / 2 - 4), title, font=f,
               fill=(245, 247, 252))
        return canvas


def _hex_rgb(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _cover(img: Image.Image, w: int, h: int) -> Image.Image:
    scale = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1), Image.LANCZOS)
    x = (img.width - w) // 2
    y = (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def _wrap(d: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=font) > max_w and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


@dataclass
class CutRender:
    """1カット分の描画計画。build がこれをもとに動画セグメントを作る。"""
    png: str                                 # frames/ 相対の静止画（bgありなら透過前景）
    dur: float                               # 表示秒（音声実測 + ポーズ）
    motion: str                              # zoom-in/zoom-out/pan-left/pan-right/none
    video: str | None                        # 埋め込みクリップの絶対パス（無ければNone）
    box: tuple[int, int, int, int] | None    # クリップを載せるカード内側領域（Noneで全画面）
    bg: str | None = None                    # 背景画像の絶対パス。あれば背景だけを動かし
                                             # 前景（見出し・カード・文字）は静止させる
    # 複数カットにまたがる動画（span）用: 動画側の再生開始オフセットと速度
    v_offset: float = 0.0                    # このカットが再生する動画内の開始秒（速度適用後の時間軸）
    v_speed: float = 1.0                     # 再生速度（0.5でスロー）
    v_full: bool = False                     # 全画面表示か
    # テロップ（別レイヤーでアニメ付き overlay する）
    telop_png: str | None = None             # テロップだけを描いた透過PNGの相対パス
    telop_anim: str = "up"                   # 登場アニメ none/fade/up/down
    trans_png: str | None = None             # 章トランジションのバナー透過PNG（先頭カット）
    trans_lead: float = 0.0                  # カット冒頭のトランジション表示秒（この間ナレは無音）
    op_gap: float = 0.0                      # このカットの直前にOP映像を挿入（秒）
    stat: dict | None = None                 # 数字カウントアップ {value,unit,label,start}
    # シーン単位の連続モーション（1画像を1方向にゆっくり動かす）用のタイムライン
    m_start: float = 0.0                     # シーン先頭からこのカット開始までの秒数
    m_total: float = 0.0                     # シーン全体の秒数（0ならこのカット単独）
    # 再現ドラマ: 話者立ち絵の動くレイヤー（跳ね・ジャンプ・震え）
    actor_png: str | None = None             # 話者立ち絵の透過PNG（frames/相対）
    actor_x: int = 0                         # 静止時の貼り付け左上x
    actor_y: int = 0                         # 静止時の貼り付け左上y
    actor_anim: str = "talk"                 # talk / jump / shake
    bubble_png: str | None = None            # 吹き出しの透過PNG（立ち絵より前面）


def _resolve_clip(cfg: Config, proj: Project, rel: str) -> str:
    p = proj.root / rel
    if not p.exists():
        p = cfg.root / rel
    if not p.exists():
        raise SystemExit(
            f"動画クリップが見つかりません: {rel}\n"
            "（assets/clips/ 等に配置するか、台本の video: を修正してください）"
        )
    return str(p)


def render_frames(
    cfg: Config,
    proj: Project,
    timings: list[CutTiming],
    vertical: bool = False,
    only_scene: str | None = None,
) -> list[CutRender]:
    """全カットのベースPNGを frames/ に生成し、描画計画のリストを返す。

    キャラの表情はセリフをまたいで持続する（最後に指定された表情を維持）。
    motion 未指定のカットは zoom-in / zoom-out を交互に割り当てて常時微動させる。
    """
    script = proj.load_script()
    drama = getattr(script.meta, "mode", "talk") == "drama"
    narrator = script.meta.narrator if drama else ""
    if drama:
        from .mobgen import register_mobs
        register_mobs(cfg, proj, script)
    proj.frames_dir  # frames/ を作成
    composer = Composer(cfg, proj, vertical=vertical)
    motion_on = bool(cfg.get("video", "motion", "enabled", default=True))
    cuts_meta = {}
    for scene in script.scenes:
        for i, cut in enumerate(scene.cuts):
            cuts_meta[(scene.id, i)] = (scene, cut)

    # 出力対象のカットを平坦化（timings順＝台本の通し順）
    flat: list[tuple[CutTiming, "object", "object"]] = []
    scene_counters: dict[str, int] = {}
    for ct in timings:
        i = scene_counters.get(ct.scene_id, 0)
        scene_counters[ct.scene_id] = i + 1
        scene, cut = cuts_meta[(ct.scene_id, i)]
        if only_scene and scene.id != only_scene:
            continue
        flat.append((ct, scene, cut))

    # 動画スパンの割り当て: video を持つカットが video_span カット分を占有し、
    # 後続カットは同じ動画の続き（オフセット）を再生する
    span_of: dict[int, dict] = {}
    k = 0
    while k < len(flat):
        _, _, cut = flat[k]
        if cut.video and cut.slide is None:
            src = _resolve_clip(cfg, proj, cut.video)
            span_len = min(cut.video_span, len(flat) - k)
            members = flat[k:k + span_len]
            off = 0.0
            for (mct, _, _) in members:
                span_of[mct.index] = {
                    "src": src, "offset": round(off, 3),
                    "speed": float(cut.video_speed), "full": bool(cut.video_full),
                }
                off += mct.total_dur
            k += span_len
        else:
            k += 1

    # 背景ショット（＝1画像が映る連続カットのまとまり）ごとに1方向の動きを決める。
    # 数カットごとに背景を切り替えると各画像が短時間だけ動くので、動きが速く・
    # 滑らかになり、絵の切り替わりで飽きさせない（プロの解説動画の定石）。
    # 背景は cut.background で切替。無ければシーンの background を引き継ぐ。
    by_index = {ct.index: (scene, cut) for ct, scene, cut in flat}
    eff_bg: dict[int, str] = {}
    cur_bg = None
    cur_scene = None
    for ct, scene, cut in flat:
        if scene.id != cur_scene:
            cur_scene, cur_bg = scene.id, scene.background
        if cut.background:
            cur_bg = cut.background
        eff_bg[ct.index] = cur_bg

    auto_cycle = ["zoom-in", "pan-left", "zoom-out", "pan-right"]
    shot_id: dict[int, int] = {}
    shots: list[list[int]] = []
    prev_key = None
    for ct, scene, cut in flat:
        key = (scene.id, eff_bg[ct.index])  # シーン変化 or 背景変化で新ショット
        if key != prev_key:
            shots.append([])
            prev_key = key
        shots[-1].append(ct.index)
        shot_id[ct.index] = len(shots) - 1

    shot_motion: dict[int, str] = {}
    for si, idxs in enumerate(shots):
        scene0, cut0 = by_index[idxs[0]]
        shot_motion[si] = cut0.motion or scene0.motion or auto_cycle[si % len(auto_cycle)]
    # モーションのタイムライン（各カットのショット内開始秒とショート総尺）は
    # 実測長を持つ timings（total_dur）から作る
    shot_total: dict[int, float] = {si: 0.0 for si in range(len(shots))}
    shot_start: dict[int, float] = {}
    for ct, scene, cut in flat:
        si = shot_id[ct.index]
        shot_start[ct.index] = shot_total[si]
        shot_total[si] += ct.total_dur

    # 各シーンの先頭カット（章トランジションを出す位置）
    scene_first_idx: set[int] = set()
    seen_sc = None
    for ct, scene, cut in flat:
        if scene.id != seen_sc:
            scene_first_idx.add(ct.index)
            seen_sc = scene.id
    trans_on = bool(cfg.get("video", "transition", "enabled", default=True))

    speakers = script.speakers_used()
    emotion_state = {s: "normal" for s in speakers}

    # 立ち絵の対象: ナレーターは除外。dramaでは舞台に立つだけのキャラも含める
    sprite_speakers = [s for s in speakers if s != narrator]
    if drama:
        for sc in script.scenes:
            for m in sc.stage:
                if m.who not in sprite_speakers:
                    sprite_speakers.append(m.who)
                    emotion_state.setdefault(m.who, "normal")

    # 立ち絵は「出演キャラ全員が sprite_dir を持つ」プロジェクトだけ有効にする。
    # （aoyama単独回など素材のない構成では自動オフになり、レイアウトも従来どおり）
    composer.show_chars = composer.show_chars and bool(sprite_speakers) and all(
        "sprite_dir" in cfg.character(s) for s in sprite_speakers
    )
    # 立ち絵ファイルの差し替えで前景PNGを確実に作り直すための署名
    sprite_sig = ""
    if composer.show_chars:
        parts = []
        for s in sprite_speakers:
            ch = cfg.character(s)
            parts.append(f"{s}@{ch.get('sprite_scale', 1.0)}:{ch.get('sprite_flip', False)}")
            d = cfg.root / ch["sprite_dir"]
            for p in sorted(d.glob("*.png")) if d.is_dir() else []:
                st = p.stat()
                parts.append(f"{s}:{p.name}:{st.st_size}:{int(st.st_mtime)}")
        sprite_sig = "|".join(parts)

    result: list[CutRender] = []
    sub = "v" if vertical else "h"
    manifest_used: set[str] = set()

    for ct, scene, cut in flat:
        emotion_state[cut.speaker] = cut.emotion
        sp = span_of.get(ct.index)
        full = bool(sp and sp["full"])
        bg_name = eff_bg[ct.index]

        # 動きの決定: 動画カットは静止。それ以外は背景ショット単位の1方向モーション
        if sp or not motion_on:
            motion = "none"
        else:
            motion = shot_motion.get(shot_id[ct.index], "zoom-in")

        # 背景だけを動かすカットは前景（文字・カード）を透過PNGで分離して静止させる。
        # 全画面動画のカットも前景を透過にして動画の上に重ねる
        fg_only = motion != "none" or full
        bg_path = str(background_path(cfg, bg_name)) if (fg_only and not full) else None
        card = bool(sp) and not full

        if cut.duet_with:
            emotion_state[cut.duet_with] = cut.emotion
        chars = [(s, emotion_state[s],
                  s == cut.speaker or s == cut.duet_with) for s in speakers
                 if s != narrator]

        # 再現ドラマ: 舞台配置・吹き出し・ナレーション字幕
        stage_list = None
        bubble = None
        caption = None
        if drama:
            stage_list = [{"who": m.who,
                           "emotion": emotion_state.get(m.who, "normal"),
                           "x": m.x, "flip": m.flip, "scale": m.scale,
                           "tag": m.tag} for m in scene.stage]
            if cut.speaker == narrator:
                caption = cut.text
            else:
                mem = next((m for m in scene.stage if m.who == cut.speaker), None)
                bx = mem.x if mem else 0.5
                if cut.duet_with:
                    # デュエットは2人の中間に1つの吹き出し（両者のセリフとして見せる）
                    mem2 = next((m for m in scene.stage
                                 if m.who == cut.duet_with), None)
                    if mem2 is not None:
                        bx = (bx + mem2.x) / 2
                bubble = {"text": cut.text, "x": bx,
                          "color": cfg.character(cut.speaker).get("color")}

        # 再現ドラマ: 話者の立ち絵は基底から抜いて動くレイヤーにする（横動画のみ）
        actor = None
        actor_member = None
        if drama and not vertical and cut.speaker != narrator and stage_list:
            actor_member = next((m for m in stage_list if m["who"] == cut.speaker),
                                None)
            if actor_member:
                actor = cut.speaker

        header = scene.title or (script.meta.title if vertical else "")
        if drama and full:
            # 全画面動画（年号カード・図解アニメ）では章タブを消す（見出しと干渉するため）
            header = ""
        # ベースはテロップ抜きで合成（テロップは別レイヤーで動かす）
        key_src = json.dumps(
            [bg_name, header, chars,
             cut.slide.model_dump() if cut.slide else None, cut.image,
             bool(sp), card, full, fg_only, sub, sprite_sig,
             stage_list, bubble, caption, actor],
            ensure_ascii=False, sort_keys=True, default=str,
        )
        key = hashlib.sha1(key_src.encode()).hexdigest()[:16]
        rel = f"frames/{sub}_{key}.png"
        path = proj.root / rel
        if key not in manifest_used and not path.exists():
            composer.compose_cut(bg_name, header, chars, cut.slide,
                                 cut.image, video_card=card,
                                 fg_only=fg_only, with_telops=False,
                                 stage=stage_list, bubble=bubble,
                                 caption=caption, actor=actor,
                                 bubble_layered=bool(actor)).save(path)
        manifest_used.add(key)

        # 話者立ち絵レイヤー（透過PNG）と動き。吹き出しは立ち絵より前面のレイヤーに
        # 分離する（ジャンプ等で立ち絵が自分の吹き出しを隠さないように）
        actor_png = None
        actor_x = actor_y = 0
        actor_anim = "talk"
        bubble_png = None
        if actor_member:
            akey = hashlib.sha1(json.dumps(
                [actor_member, sprite_sig, "actor1"],
                ensure_ascii=False, sort_keys=True, default=str,
            ).encode()).hexdigest()[:16]
            actor_png = f"frames/actor_{akey}.png"
            ap = proj.root / actor_png
            spimg, actor_x, actor_y = composer.drama_actor(actor_member)
            if akey not in manifest_used and not ap.exists():
                spimg.save(ap)
            manifest_used.add(akey)
            actor_anim = {"surprised": "jump", "angry": "shake"}.get(
                cut.emotion, "talk")
            if bubble:
                bkey = hashlib.sha1(json.dumps(
                    [bubble, "bub1"], ensure_ascii=False, sort_keys=True,
                    default=str).encode()).hexdigest()[:16]
                bubble_png = f"frames/bub_{bkey}.png"
                bp = proj.root / bubble_png
                if bkey not in manifest_used and not bp.exists():
                    composer.bubble_layer(bubble).save(bp)
                manifest_used.add(bkey)

        # テロップレイヤー（あれば透過PNGを別に生成）
        telop_png = None
        telop_anim = "up"
        if cut.telops:
            tkey = hashlib.sha1(json.dumps(
                [[t.model_dump() for t in cut.telops], sub],
                ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]
            telop_png = f"frames/tel_{tkey}.png"
            tp = proj.root / telop_png
            if tkey not in manifest_used and not tp.exists():
                composer.telop_layer(cut.telops).save(tp)
            manifest_used.add(tkey)
            telop_anim = cut.telops[0].anim

        # 章トランジション: シーンの先頭カット（見出しあり）にバナーを出す
        trans_png = None
        if (trans_on and not vertical and ct.index in scene_first_idx
                and scene.title):
            xkey = hashlib.sha1(f"trans|{scene.title}|{sub}".encode()).hexdigest()[:16]
            trans_png = f"frames/trans_{xkey}.png"
            xp = proj.root / trans_png
            if xkey not in manifest_used and not xp.exists():
                composer.transition_layer(scene.title).save(xp)
            manifest_used.add(xkey)

        result.append(CutRender(
            png=rel,
            dur=round(ct.total_dur + getattr(ct, "lead", 0.0), 3),
            motion=motion,
            video=sp["src"] if sp else None,
            box=composer.card_inner_box() if card else None,
            bg=bg_path,
            v_offset=sp["offset"] if sp else 0.0,
            v_speed=sp["speed"] if sp else 1.0,
            v_full=full,
            telop_png=telop_png,
            telop_anim=telop_anim,
            trans_png=trans_png,
            trans_lead=round(getattr(ct, "lead", 0.0), 3) if trans_png else 0.0,
            op_gap=round(getattr(ct, "op_gap", 0.0), 3) if not vertical else 0.0,
            stat=cut.stat.model_dump() if cut.stat else None,
            m_start=round(shot_start.get(ct.index, 0.0), 3),
            m_total=round(shot_total.get(shot_id[ct.index], 0.0), 3),
            actor_png=actor_png,
            actor_x=actor_x,
            actor_y=actor_y,
            actor_anim=actor_anim,
            bubble_png=bubble_png,
        ))
    return result
