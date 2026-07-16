"""白モブキャラの立ち絵を自動生成する（再現ドラマモード用）。

お手本準拠のミニマル造形: 白い頭・白い胴体・黒細フチ・胴体に縦書きの名前。
hair / item / photo の差分で見分けを付ける。

生成先: projects/<slug>/mobs/<id>/<emotion>.png（6感情とも同じ絵。表情は付けない）
チャンネル設定への登録: register_mobs() が cfg.characters に動的追加する。
これにより voice.py（音声合成）と compose.py（立ち絵表示）が無改造で動く。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .config import Config, Project

EMOTIONS = ["normal", "happy", "surprised", "thinking", "angry", "sad"]
W, H = 760, 1240          # 生成キャンバス（頭でっかちの可愛い比率）
OUTLINE = (60, 62, 70)
BODY = (252, 252, 252)


def _draw_mob(mob, photo_path: Path | None, font_path: str) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = W // 2
    head_r = 250
    head_cy = 300

    # 胴体（肩の丸いずんぐりシルエット）
    d.rounded_rectangle([cx - 230, head_cy + head_r - 60, cx + 230, H - 24],
                        radius=190, fill=BODY, outline=OUTLINE, width=7)
    # 頭
    d.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
              fill=BODY, outline=OUTLINE, width=7)

    # 髪の差分
    if mob.hair == "twintail":
        for sgn in (-1, 1):
            d.ellipse([cx + sgn * (head_r + 10) - 55, head_cy - 40,
                       cx + sgn * (head_r + 10) + 55, head_cy + 260],
                      fill=(96, 62, 48), outline=OUTLINE, width=6)
        d.chord([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
                start=180, end=360, fill=(96, 62, 48), outline=OUTLINE, width=6)
    elif mob.hair == "short":
        d.chord([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
                start=190, end=350, fill=(70, 66, 64), outline=OUTLINE, width=6)
    elif mob.hair == "bun":
        d.ellipse([cx - 70, head_cy - head_r - 90, cx + 70, head_cy - head_r + 30],
                  fill=(110, 100, 92), outline=OUTLINE, width=6)

    # 実写顔（丸抜きで頭に貼る）
    if photo_path and photo_path.exists():
        ph = Image.open(photo_path).convert("RGBA")
        side = min(ph.size)
        ph = ph.crop(((ph.width - side) // 2, 0, (ph.width + side) // 2, side))
        ph = ph.resize((head_r * 2 - 24, head_r * 2 - 24), Image.LANCZOS)
        mask = Image.new("L", ph.size, 0)
        ImageDraw.Draw(mask).ellipse([0, 0, ph.size[0], ph.size[1]], fill=255)
        img.paste(ph, (cx - head_r + 12, head_cy - head_r + 12), mask)

    # 小物の差分
    if mob.item == "mustache":
        d.ellipse([cx - 80, head_cy + 60, cx - 6, head_cy + 100], fill=(50, 46, 44))
        d.ellipse([cx + 6, head_cy + 60, cx + 80, head_cy + 100], fill=(50, 46, 44))
    elif mob.item == "hat":
        d.ellipse([cx - head_r - 30, head_cy - head_r + 10, cx + head_r + 30,
                   head_cy - head_r + 90], fill=(180, 150, 90), outline=OUTLINE, width=6)
        d.rounded_rectangle([cx - 120, head_cy - head_r - 110, cx + 120,
                             head_cy - head_r + 50], radius=40,
                            fill=(180, 150, 90), outline=OUTLINE, width=6)
    elif mob.item == "bible":
        d.rounded_rectangle([cx + 120, H - 500, cx + 260, H - 300], radius=12,
                            fill=(40, 40, 46), outline=OUTLINE, width=5)
        f = ImageFont.truetype(font_path, 60, index=0)
        d.text((cx + 165, H - 470), "✝", font=f, fill=(240, 240, 240))
    elif mob.item == "book":
        d.rounded_rectangle([cx + 120, H - 500, cx + 270, H - 310], radius=10,
                            fill=(90, 120, 90), outline=OUTLINE, width=5)

    # 名前ラベル（胴体に縦書き）
    label = mob.label
    if label:
        size = 110 if len(label) <= 4 else (84 if len(label) <= 6 else 66)
        f = ImageFont.truetype(font_path, size, index=0)
        total_h = size * len(label) + 8 * (len(label) - 1)
        y = head_cy + head_r + 40
        max_h = H - 90 - y
        if total_h > max_h:
            size = max(int(size * max_h / total_h), 34)
            f = ImageFont.truetype(font_path, size, index=0)
            total_h = size * len(label) + 8 * (len(label) - 1)
        for i, ch in enumerate(label):
            wch = d.textlength(ch, font=f)
            d.text((cx - wch / 2, y + i * (size + 8)), ch, font=f, fill=(30, 32, 40))
    return img


def ensure_mob_sprites(cfg: Config, proj: Project, script) -> None:
    """台本の mobs 定義から立ち絵PNGを生成する（定義が変わったときだけ再生成）。"""
    font_path = cfg.find_pillow_font()
    for mob in script.meta.mobs:
        out_dir = proj.root / "mobs" / mob.id
        out_dir.mkdir(parents=True, exist_ok=True)
        sig = f"{mob.label}|{mob.hair}|{mob.item}|{mob.photo}|v2"
        sig_file = out_dir / ".sig"
        if sig_file.exists() and sig_file.read_text() == sig \
                and (out_dir / "normal.png").exists():
            continue
        photo = (proj.root / mob.photo) if mob.photo else None
        if mob.photo and photo is not None and not photo.exists():
            photo = cfg.root / mob.photo
        img = _draw_mob(mob, photo, font_path)
        for emo in EMOTIONS:
            img.save(out_dir / f"{emo}.png")
        sig_file.write_text(sig)
        print(f"モブ生成: {mob.id}（{mob.label}）")


def register_mobs(cfg: Config, proj: Project, script) -> None:
    """mobs を cfg.characters に動的登録する（音声・立ち絵の既存経路に乗せる）。"""
    ensure_mob_sprites(cfg, proj, script)
    for mob in script.meta.mobs:
        cfg.characters[mob.id] = {
            "display_name": mob.label,
            "credit": "",
            "voicevox_style": mob.voice,
            "speed_scale": mob.speed,
            "pitch_scale": mob.pitch,
            "color": "#9AA2B2",
            "sprite_dir": str((proj.root / "mobs" / mob.id).relative_to(cfg.root)),
            "sprite_scale": 0.95,
            "position": "left",
        }
