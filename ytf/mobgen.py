"""白モブキャラの立ち絵を自動生成する（再現ドラマモード用）。

お手本準拠のミニマル造形: 白い頭・白い胴体・黒細フチ・胴体に縦書きの名前。
outfit で服（背広・作業着・白衣・着物・羽織・前掛け・学生服）を着せられる。
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
# 胴の名前ラベルの長さの上限（キャンバス座標）。ドラマの立ち絵は 1080p で高さ約909px・
# 上端 y≈217 に置かれ、ラベルは画面 y≈649 から始まる。2行ナレの帯は y≈910 から下なので、
# 帯に食われないのは画面で約250px。実測で330だと最後の字の下端が帯に10px前後かかったので300にした。5字以上のラベルが
# 「教室の先」「販売の」で切れていた（2026-09-23 ヤクルト回の検証で発覚）
LABEL_MAX_H = 300
OUTLINE = (60, 62, 70)
BODY = (252, 252, 252)

# 服の既定の地色（mob.color で上書きできる）
OUTFIT_COLORS = {
    "suit": (52, 62, 96),        # 紺の背広
    "work": (104, 128, 150),     # 灰青の作業着
    "labcoat": (250, 250, 250),  # 白衣
    "kimono": (74, 70, 96),      # 藍鼠の着物
    "haori": (60, 56, 60),       # 黒っぽい羽織
    "apron": (44, 62, 110),      # 紺の前掛け
    "gakuran": (34, 36, 46),     # 学生服
}


def _hex(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _shade(rgb, k: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(v * k))) for v in rgb)  # type: ignore[return-value]


def _draw_outfit(img: Image.Image, outfit: str, color, box: list[int], cx: int) -> str:
    """胴の上に服を描く（胴のシルエットでマスクして、はみ出さない）。
    名前ラベルは胴の真ん中に縦書きで乗るので、真ん中の縦帯（cx±110・y590〜890）には
    ボタンや紐を置かない。返り値はラベルの下地の明るさ 'light' / 'dark'。"""
    if outfit not in OUTFIT_COLORS:
        raise SystemExit(f"モブの outfit が不明です: {outfit}（{' / '.join(OUTFIT_COLORS)}）")
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=190, fill=255)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    top = box[1]
    base = color or OUTFIT_COLORS[outfit]
    under = base  # ラベルの真下に来る地の色

    if outfit in ("suit", "labcoat"):
        d.rectangle(box, fill=base)
        # 胸元のシャツ（ラベルはここに乗る）。白衣の下は水色のシャツ
        shirt = (250, 250, 250) if outfit == "suit" else (196, 214, 234)
        d.polygon([(cx - 112, top), (cx + 112, top), (cx + 70, 980), (cx - 70, 980)], fill=shirt)
        lap = _shade(base, 0.86) if outfit == "suit" else (238, 240, 244)
        for s in (-1, 1):
            d.polygon([(cx + s * 112, top), (cx + s * 200, top + 40),
                       (cx + s * 150, top + 210), (cx + s * 96, top + 250)],
                      fill=lap, outline=OUTLINE)
            d.line([(cx + s * 112, top), (cx + s * 70, 980)], fill=OUTLINE, width=6)
        for by in (1030, 1110):
            d.ellipse([cx - 16, by - 16, cx + 16, by + 16],
                      fill=_shade(base, 0.6) if outfit == "suit" else (200, 204, 210),
                      outline=OUTLINE, width=3)
        if outfit == "labcoat":
            for s in (-1, 1):
                x0, x1 = sorted((cx + s * 100, cx + s * 200))
                d.rectangle([x0, 900, x1, 990], outline=OUTLINE, width=5)
            d.rectangle([cx + 110, 700, cx + 200, 780], outline=OUTLINE, width=5)
            d.rectangle([cx + 130, 670, cx + 144, 720], fill=(60, 90, 170))
        under = shirt

    elif outfit == "work":
        d.rectangle(box, fill=base)
        d.line([(cx, top), (cx, H)], fill=_shade(base, 0.72), width=8)  # 前立て
        for s in (-1, 1):
            d.polygon([(cx, top + 70), (cx + s * 150, top + 10), (cx + s * 170, top + 90),
                       (cx + s * 40, top + 130)], fill=_shade(base, 1.15), outline=OUTLINE)
            x0, x1 = sorted((cx + s * 100, cx + s * 196))
            d.rectangle([x0, 700, x1, 800], fill=_shade(base, 0.92), outline=OUTLINE, width=5)
            d.line([(x0, 724), (x1, 724)], fill=OUTLINE, width=4)

    elif outfit in ("kimono", "haori"):
        kim = base if outfit == "kimono" else (96, 92, 100)
        d.rectangle(box, fill=kim)
        under = kim
        # 半衿と衿。右前なので、見て右側の衿が上に重なる
        vy = top + 170
        eri = (245, 242, 232)
        d.polygon([(cx - 150, top), (cx - 90, top), (cx + 30, vy + 40), (cx - 30, vy + 90)],
                  fill=eri, outline=OUTLINE)
        d.polygon([(cx + 150, top), (cx + 90, top), (cx - 30, vy + 40), (cx + 30, vy + 90)],
                  fill=eri, outline=OUTLINE)
        d.polygon([(cx + 190, top + 20), (cx + 120, top), (cx - 20, vy + 110),
                   (cx + 40, vy + 150)], fill=_shade(kim, 0.8), outline=OUTLINE)
        d.rectangle([box[0], 930, box[2], 1010], fill=(176, 146, 86), outline=OUTLINE, width=5)
        if outfit == "haori":
            for s in (-1, 1):
                d.polygon([(cx + s * 120, top), (cx + s * 240, top), (cx + s * 240, H),
                           (cx + s * 110, H), (cx + s * 110, 800)], fill=base, outline=OUTLINE)
            # 羽織紐はラベルの下（帯の上）に結ぶ
            d.line([(cx - 110, 916), (cx + 110, 916)], fill=eri, width=10)
            d.ellipse([cx - 18, 898, cx + 18, 934], fill=eri, outline=OUTLINE, width=3)

    elif outfit == "apron":
        d.rectangle(box, fill=BODY)
        d.rectangle([cx - 200, 860, cx + 200, H], fill=base, outline=OUTLINE, width=6)
        d.rectangle([box[0], 846, box[2], 876], fill=_shade(base, 0.8))  # 腰ひも
        under = BODY

    elif outfit == "gakuran":
        d.rectangle(box, fill=base)
        d.rectangle([cx - 120, top, cx + 120, top + 120], fill=_shade(base, 1.3),
                    outline=OUTLINE, width=5)  # 詰襟
        for by in (950, 1030, 1110):
            d.ellipse([cx - 18, by - 18, cx + 18, by + 18], fill=(214, 178, 70),
                      outline=OUTLINE, width=3)

    clip = Image.new("L", (W, H), 0)
    clip.paste(layer.split()[3], (0, 0), mask)
    img.paste(layer, (0, 0), clip)
    # 白い作業着（本田技研など）もあるので、字の色は地の明るさで決める
    lum = 0.299 * under[0] + 0.587 * under[1] + 0.114 * under[2]
    return "light" if lum > 165 else "dark"


def _draw_mob(mob, photo_path: Path | None, font_path: str) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = W // 2
    head_r = 250
    head_cy = 300

    # 胴体（肩の丸いずんぐりシルエット）
    body_box = [cx - 230, head_cy + head_r - 60, cx + 230, H - 24]
    d.rounded_rectangle(body_box, radius=190, fill=BODY, outline=OUTLINE, width=7)
    outfit = getattr(mob, "outfit", "none") or "none"
    label_bg = None
    if outfit != "none":
        color = _hex(mob.color) if getattr(mob, "color", "") else None
        label_bg = _draw_outfit(img, outfit, color, body_box, cx)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(body_box, radius=190, outline=OUTLINE, width=7)
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
        max_h = min(H - 90 - y, LABEL_MAX_H)
        while total_h > max_h and size > 34:
            size -= 2
            total_h = size * len(label) + 8 * (len(label) - 1)
        f = ImageFont.truetype(font_path, size, index=0)
        # 服の上では縁取りを付ける（濃い地は白字、明るい地は黒字に白フチ）
        if label_bg == "dark":
            kw = dict(fill=(255, 255, 255), stroke_width=6, stroke_fill=(30, 32, 40))
        elif label_bg == "light":
            kw = dict(fill=(30, 32, 40), stroke_width=4, stroke_fill=(255, 255, 255))
        else:
            kw = dict(fill=(30, 32, 40))
        for i, ch in enumerate(label):
            wch = d.textlength(ch, font=f)
            d.text((cx - wch / 2, y + i * (size + 8)), ch, font=f, **kw)
    return img


def ensure_mob_sprites(cfg: Config, proj: Project, script) -> None:
    """台本の mobs 定義から立ち絵PNGを生成する（定義が変わったときだけ再生成）。"""
    font_path = cfg.find_pillow_font()
    for mob in script.meta.mobs:
        out_dir = proj.root / "mobs" / mob.id
        out_dir.mkdir(parents=True, exist_ok=True)
        sig = f"{mob.label}|{mob.hair}|{mob.item}|{mob.photo}|v4"
        if mob.outfit != "none":
            sig += f"|{mob.outfit}|{mob.color}|o1"
        sig_file = out_dir / ".sig"
        if sig_file.exists() and sig_file.read_text(encoding="utf-8") == sig \
                and (out_dir / "normal.png").exists():
            continue
        photo = (proj.root / mob.photo) if mob.photo else None
        if mob.photo and photo is not None and not photo.exists():
            photo = cfg.root / mob.photo
        img = _draw_mob(mob, photo, font_path)
        for emo in EMOTIONS:
            img.save(out_dir / f"{emo}.png")
        sig_file.write_text(sig, encoding="utf-8")
        print(f"モブ生成: {mob.id}（{mob.label}）")


# モブの声のクレジット（VOICEVOX の規約で、使った話者は全員表記が要る）。
# 空欄にしていたため、50〜53本目の概要欄でモブの声が抜けていた（2026-09-23）。
VOICE_CREDITS = {
    3: "VOICEVOX:ずんだもん",
    8: "VOICEVOX:春日部つむぎ",
    11: "VOICEVOX:玄野武宏",
    12: "VOICEVOX:白上虎太郎",
    13: "VOICEVOX:青山龍星",
    42: "VOICEVOX:ちび式じい",
    67: "VOICEVOX:栗田まろん",
    73: "VOICEVOX:満別花丸",
    100: "VOICEVOX:黒沢冴白",
}


def _voice_credit(cfg: Config, style_id: int) -> str:
    """スタイルIDから話者名のクレジットを引く。表に無いIDは VOICEVOX に問い合わせる。"""
    if style_id in VOICE_CREDITS:
        return VOICE_CREDITS[style_id]
    from .voice import VoicevoxClient
    url = cfg.get("voicevox", "url", default="http://127.0.0.1:50021")
    for sp in VoicevoxClient(url).speakers():
        if any(st["id"] == style_id for st in sp["styles"]):
            return f"VOICEVOX:{sp['name']}"
    raise SystemExit(f"モブの声 {style_id} の話者名が分かりません（クレジットに必要）")


def register_mobs(cfg: Config, proj: Project, script) -> None:
    """mobs を cfg.characters に動的登録する（音声・立ち絵の既存経路に乗せる）。"""
    ensure_mob_sprites(cfg, proj, script)
    for mob in script.meta.mobs:
        cfg.characters[mob.id] = {
            "display_name": mob.label,
            "credit": _voice_credit(cfg, mob.voice),
            # モブは名前を胴体に焼き込んでいるので左右反転してはいけない。
            # のっぺら白キャラには向きが無く、反転しても得るものが無いのに
            # 名前だけが鏡文字になる（stage の flip: true で「原野」が鏡像化した。2026-08）
            "no_mirror": True,
            "voicevox_style": mob.voice,
            "speed_scale": mob.speed,
            "pitch_scale": mob.pitch,
            "color": "#9AA2B2",
            "sprite_dir": str((proj.root / "mobs" / mob.id).relative_to(cfg.root)),
            "sprite_scale": 0.95,
            "position": "left",
        }
