"""プレースホルダー素材の生成。

実運用では assets/characters/<name>/<emotion>.png を
公認立ち絵（例: 坂本アヒル氏の立ち絵PSDから書き出したPNG）に
差し替えるだけで、パイプラインはそのまま動く。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from .config import Config

EMOTIONS = ["normal", "happy", "surprised", "thinking", "angry", "sad"]
SPRITE_W, SPRITE_H = 620, 840


def _blob_sprite(color: tuple[int, int, int], emotion: str) -> Image.Image:
    """キャラカラーのゆるいマスコット。表情差分つき。"""
    img = Image.new("RGBA", (SPRITE_W, SPRITE_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    dark = tuple(max(0, c - 60) for c in color)

    # 体
    d.ellipse([90, 300, 530, 830], fill=color + (255,), outline=dark + (255,), width=6)
    # 頭
    d.ellipse([110, 60, 510, 460], fill=color + (255,), outline=dark + (255,), width=6)
    # ほっぺ
    for cx in (185, 435):
        d.ellipse([cx - 28, 320, cx + 28, 360], fill=(255, 160, 160, 180))

    # 目・口（表情差分）
    eye = (40, 40, 40, 255)
    if emotion == "happy":
        d.arc([170, 200, 250, 280], 200, 340, fill=eye, width=12)
        d.arc([370, 200, 450, 280], 200, 340, fill=eye, width=12)
        d.arc([250, 290, 370, 380], 0, 180, fill=eye, width=12)
    elif emotion == "surprised":
        d.ellipse([180, 200, 244, 280], fill=eye)
        d.ellipse([376, 200, 440, 280], fill=eye)
        d.ellipse([280, 310, 340, 380], outline=eye, width=12)
    elif emotion == "thinking":
        d.line([175, 240, 250, 240], fill=eye, width=14)
        d.ellipse([376, 200, 440, 270], fill=eye)
        d.line([270, 350, 350, 340], fill=eye, width=12)
    elif emotion == "angry":
        d.line([170, 200, 250, 240], fill=eye, width=14)
        d.line([450, 200, 370, 240], fill=eye, width=14)
        d.arc([255, 330, 365, 400], 180, 360, fill=eye, width=12)
    elif emotion == "sad":
        d.line([170, 240, 250, 210], fill=eye, width=14)
        d.line([450, 240, 370, 210], fill=eye, width=14)
        d.arc([260, 340, 360, 400], 180, 360, fill=eye, width=12)
    else:  # normal
        d.ellipse([185, 205, 240, 275], fill=eye)
        d.ellipse([380, 205, 435, 275], fill=eye)
        d.arc([270, 300, 350, 370], 0, 180, fill=eye, width=12)
    return img


def _hex(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def gen_background(path: Path, w: int, h: int) -> None:
    """やわらかいグラデーション背景。"""
    img = Image.new("RGB", (w, h))
    top, bottom = (247, 244, 235), (214, 228, 240)
    for y in range(h):
        t = y / h
        img.paste(
            tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)),
            (0, y, w, y + 1),
        )
    d = ImageDraw.Draw(img, "RGBA")
    # 遠景のドット模様で少しリッチに
    for i in range(14):
        x = (i * 353) % w
        y = (i * 211) % (h // 2)
        r = 40 + (i * 37) % 90
        d.ellipse([x, y, x + r, y + r], fill=(255, 255, 255, 26))
    img = img.filter(ImageFilter.GaussianBlur(2))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def init_assets(cfg: Config, force: bool = False) -> None:
    assets = cfg.root / "assets"
    for key, ch in cfg.characters.items():
        sprite_dir = cfg.root / ch["sprite_dir"]
        sprite_dir.mkdir(parents=True, exist_ok=True)
        color = _hex(ch.get("color", "#AAAAAA"))
        for emo in EMOTIONS:
            p = sprite_dir / f"{emo}.png"
            if p.exists() and not force:
                continue
            _blob_sprite(color, emo).save(p)
        print(f"立ち絵(プレースホルダー): {sprite_dir}")

    bg = assets / "backgrounds" / "default.png"
    if force or not bg.exists():
        gen_background(
            bg,
            int(cfg.get("video", "width", default=1920)),
            int(cfg.get("video", "height", default=1080)),
        )
        print(f"背景: {bg}")
    (assets / "bgm").mkdir(parents=True, exist_ok=True)


def sprite_path(cfg: Config, speaker: str, emotion: str) -> Path:
    ch = cfg.character(speaker)
    d = cfg.root / ch["sprite_dir"]
    p = d / f"{emotion}.png"
    if not p.exists():
        p = d / "normal.png"
    if not p.exists():
        raise SystemExit(
            f"立ち絵がありません: {d}/normal.png — `ytf assets --init` を実行してください"
        )
    return p


def background_path(cfg: Config, name: str) -> Path:
    for ext in ("png", "jpg", "jpeg"):
        p = cfg.root / "assets" / "backgrounds" / f"{name}.{ext}"
        if p.exists():
            return p
    p = cfg.root / "assets" / "backgrounds" / "default.png"
    if not p.exists():
        raise SystemExit("背景がありません。`ytf assets --init` を実行してください")
    return p
