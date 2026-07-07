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

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from .assets_gen import background_path, sprite_path
from .config import Config, Project
from .schema import Script, Slide, split_reading
from .voice import CutTiming


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


class Composer:
    def __init__(self, cfg: Config, proj: Project, vertical: bool = False):
        self.cfg = cfg
        self.proj = proj
        self.lay = layout_for(cfg, vertical)
        self.show_chars = bool(cfg.get("video", "show_characters", default=True))
        self.font_path = cfg.find_pillow_font()
        self._sprite_cache: dict[tuple[str, str, bool], Image.Image] = {}
        self._bg_cache: dict[str, Image.Image] = {}

    # ---------- 部品 ----------

    def font(self, size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(self.font_path, size=size, index=0)

    def _bg(self, name: str) -> Image.Image:
        if name not in self._bg_cache:
            img = Image.open(background_path(self.cfg, name)).convert("RGB")
            self._bg_cache[name] = _cover(img, self.lay.w, self.lay.h)
        return self._bg_cache[name]

    def _sprite(self, speaker: str, emotion: str, active: bool) -> Image.Image:
        key = (speaker, emotion, active)
        if key not in self._sprite_cache:
            img = Image.open(sprite_path(self.cfg, speaker, emotion)).convert("RGBA")
            scale = (self.lay.char_h if active else int(self.lay.char_h * 0.9)) / img.height
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
        while d.textlength(title, font=f) > self.lay.w - 140 and size > 28:
            size -= 4
            f = self.font(size)
        tw = d.textlength(title, font=f)
        pad, y0 = 36, 28
        x0 = (self.lay.w - tw) / 2 - pad
        x1 = (self.lay.w + tw) / 2 + pad
        y1 = y0 + size + 36
        d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=(30, 34, 46, 215))
        d.text(((self.lay.w - tw) / 2, y0 + 16), title, font=f, fill=(255, 255, 255))

    def _card_box(self) -> tuple[int, int, int, int]:
        if self.lay.vertical:
            return (60, 190, self.lay.w - 60, 980)
        if not self.show_chars:
            # 立ち絵なし: 左右の余白を詰めてカードを大きく使う
            return (150, 170, self.lay.w - 150, self.lay.h - 200)
        return (400, 170, self.lay.w - 400, self.lay.h - 330)

    def _draw_card(self, canvas: Image.Image) -> tuple[int, int, int, int]:
        d = ImageDraw.Draw(canvas, "RGBA")
        box = self._card_box()
        d.rounded_rectangle(box, radius=26, fill=(255, 255, 255, 235),
                            outline=(30, 34, 46, 255), width=4)
        return box

    def card_inner_box(self) -> tuple[int, int, int, int]:
        """カード内側（パディング込み）の領域。動画クリップの配置に使う。"""
        x0, y0, x1, y1 = self._card_box()
        return (x0 + 24, y0 + 24, x1 - 24, y1 - 24)

    def _draw_slide(self, canvas: Image.Image, slide: Slide) -> None:
        x0, y0, x1, y1 = self._draw_card(canvas)
        d = ImageDraw.Draw(canvas)
        cx = (x0 + x1) // 2
        y = y0 + 40
        if slide.title:
            title = split_reading(slide.title)[0]
            f = self.font(int(self.lay.slide_font * 1.25))
            tw = d.textlength(title, font=f)
            d.text((cx - tw / 2, y), title, font=f, fill=(200, 60, 40))
            y += int(self.lay.slide_font * 1.25) + 34
            d.line([x0 + 60, y - 12, x1 - 60, y - 12], fill=(220, 220, 220), width=3)
        if slide.big:
            f = self.font(int(self.lay.slide_font * 1.9))
            for line in _wrap(d, split_reading(slide.big)[0], f, (x1 - x0) - 120):
                tw = d.textlength(line, font=f)
                d.text((cx - tw / 2, y), line, font=f, fill=(30, 34, 46))
                y += int(self.lay.slide_font * 1.9) + 16
        else:
            f = self.font(self.lay.slide_font)
            for b in slide.bullets:
                b = split_reading(b)[0]
                for j, line in enumerate(_wrap(d, b, f, (x1 - x0) - 200)):
                    prefix = "・" if j == 0 else "　"
                    d.text((x0 + 70, y), prefix + line, font=f, fill=(30, 34, 46))
                    y += self.lay.slide_font + 22

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
    ) -> Image.Image:
        canvas = self._bg(background).copy().convert("RGBA")
        self._draw_header(canvas, header)
        if slide is not None:
            self._draw_slide(canvas, slide)
        elif video_card:
            self._draw_card(canvas)
        elif image:
            self._draw_image(canvas, image)

        if not self.show_chars:
            # 立ち絵を出さない構成（テロップ主体）
            return canvas.convert("RGB")

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
        return canvas.convert("RGB")


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
    png: str                                 # frames/ 相対のベース静止画
    dur: float                               # 表示秒（音声実測 + ポーズ）
    motion: str                              # zoom-in/zoom-out/pan-left/pan-right/none
    video: str | None                        # 埋め込みクリップの絶対パス（無ければNone）
    box: tuple[int, int, int, int] | None    # クリップを載せるカード内側領域


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
    proj.frames_dir  # frames/ を作成
    composer = Composer(cfg, proj, vertical=vertical)
    motion_on = bool(cfg.get("video", "motion", "enabled", default=True))
    cuts_meta = {}
    for scene in script.scenes:
        for i, cut in enumerate(scene.cuts):
            cuts_meta[(scene.id, i)] = (scene, cut)

    speakers = script.speakers_used()
    emotion_state = {s: "normal" for s in speakers}
    scene_counters: dict[str, int] = {}
    result: list[CutRender] = []
    sub = "v" if vertical else "h"
    manifest_used: set[str] = set()

    for ct in timings:
        i = scene_counters.get(ct.scene_id, 0)
        scene_counters[ct.scene_id] = i + 1
        scene, cut = cuts_meta[(ct.scene_id, i)]
        if only_scene and scene.id != only_scene:
            continue
        emotion_state[cut.speaker] = cut.emotion

        # 動画クリップ（slide があるカットでは使わない）
        video_path = None
        if cut.video and cut.slide is None:
            video_path = _resolve_clip(cfg, proj, cut.video)

        # 動きの決定: クリップ埋め込み時は静止、それ以外はズーム交互が既定
        if video_path or not motion_on:
            motion = "none"
        elif cut.motion:
            motion = cut.motion
        else:
            motion = "zoom-in" if ct.index % 2 == 0 else "zoom-out"

        chars = [(s, emotion_state[s], s == cut.speaker) for s in speakers]
        header = scene.title or (script.meta.title if vertical else "")
        key_src = json.dumps(
            [scene.background, header, chars,
             cut.slide.model_dump() if cut.slide else None, cut.image,
             bool(video_path), sub],
            ensure_ascii=False, sort_keys=True, default=str,
        )
        key = hashlib.sha1(key_src.encode()).hexdigest()[:16]
        rel = f"frames/{sub}_{key}.png"
        path = proj.root / rel
        if key not in manifest_used and not path.exists():
            composer.compose_cut(scene.background, header, chars, cut.slide,
                                 cut.image, video_card=bool(video_path)).save(path)
        manifest_used.add(key)
        result.append(CutRender(
            png=rel,
            dur=ct.total_dur,
            motion=motion,
            video=video_path,
            box=composer.card_inner_box() if video_path else None,
        ))
    return result
