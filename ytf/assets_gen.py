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
    if not cfg.get("video", "show_characters", default=True):
        print("立ち絵はスキップ（show_characters: false）")
    else:
        for key, ch in cfg.characters.items():
            if "sprite_dir" not in ch:
                continue
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

    # 動画クリップ埋め込み（台本の video:）の動作確認用デモクリップ
    demo = assets / "clips" / "demo.mp4"
    (assets / "clips").mkdir(parents=True, exist_ok=True)
    if force or not demo.exists():
        _gen_demo_clip(demo)

    # BGM（アンビエント）と効果音ライブラリ
    _gen_bgm(assets / "bgm" / "ambient.mp3", force)
    _gen_se_library(assets / "se", force)


def _ff():
    import shutil

    from .config import ffmpeg_bin
    return ffmpeg_bin() if shutil.which(ffmpeg_bin()) else None


def _run_ff(args: list[str], label: str) -> None:
    import subprocess
    ff = _ff()
    if ff is None:
        print(f"{label}はスキップ（ffmpegが見つかりません）")
        return
    r = subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{label}生成に失敗: {r.stderr[-200:]}")


def _gen_bgm(path: Path, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fc = (
        "[0]tremolo=f=0.10:d=0.5[a];[1]tremolo=f=0.13:d=0.5[b];"
        "[2]tremolo=f=0.11:d=0.5[c];[3]volume=0.35,tremolo=f=0.16:d=0.6[d];"
        "[a][b][c][d]amix=inputs=4:normalize=0,lowpass=f=1100,"
        "aecho=0.8:0.88:800|1300:0.35|0.25,loudnorm=I=-16:TP=-1.5,"
        "afade=t=in:d=4,afade=t=out:st=44:d=4[out]"
    )
    args = []
    for f in (220, 261.63, 329.63, 659.26):
        args += ["-f", "lavfi", "-i", f"sine=frequency={f}:duration=48"]
    args += ["-filter_complex", fc, "-map", "[out]", "-ar", "44100",
             "-b:a", "160k", str(path)]
    _run_ff(args, "BGM")


def _gen_se_library(se_dir: Path, force: bool) -> None:
    se_dir.mkdir(parents=True, exist_ok=True)
    specs = {
        "pop": (["-f", "lavfi", "-i", "sine=frequency=920:duration=0.14"],
                "afade=t=out:st=0.03:d=0.11,volume=0.7,loudnorm=I=-15:TP=-1.5"),
        "tsuru": (["-f", "lavfi", "-i",
                   "aevalsrc='sin(2*PI*(500+1600*t)*t)':d=0.28:s=44100"],
                  "afade=t=in:d=0.02,afade=t=out:st=0.15:d=0.13,volume=0.6,"
                  "loudnorm=I=-15:TP=-1.5"),
    }
    for name, (inp, af) in specs.items():
        p = se_dir / f"{name}.mp3"
        if p.exists() and not force:
            continue
        _run_ff([*inp, "-af", af, "-ar", "44100", str(p)], f"SE({name})")
    # 複数音を合成するSE
    multi = {
        "don": ("[0][1]amix=inputs=2,afade=t=out:st=0.05:d=0.35,volume=1.4,"
                "loudnorm=I=-14:TP=-1.5[o]",
                ["sine=frequency=80:duration=0.4", "sine=frequency=160:duration=0.4"]),
        "jaan": ("[0][1][2]amix=inputs=3:normalize=0,afade=t=out:st=0.1:d=0.8,"
                 "aecho=0.8:0.85:60:0.4,loudnorm=I=-15:TP=-1.5[o]",
                 ["sine=frequency=523.25:duration=0.9", "sine=frequency=659.26:duration=0.9",
                  "sine=frequency=783.99:duration=0.9"]),
    }
    for name, (fc, srcs) in multi.items():
        p = se_dir / f"{name}.mp3"
        if p.exists() and not force:
            continue
        args = []
        for s in srcs:
            args += ["-f", "lavfi", "-i", s]
        args += ["-filter_complex", fc, "-map", "[o]", "-ar", "44100", str(p)]
        _run_ff(args, f"SE({name})")
    # クイズ用（正解ピンポン / 不正解ブブー）: 2音を連結
    quiz = {
        "pinpon": ("[0]adelay=0[a];[1]adelay=170[b];[a][b]concat=n=2:v=0:a=1,"
                   "afade=t=out:st=0.28:d=0.08,loudnorm=I=-15:TP=-1.5[o]",
                   ["sine=frequency=988:duration=0.16", "sine=frequency=1319:duration=0.16"]),
        "bubu": ("[0][1]concat=n=2:v=0:a=1,tremolo=f=30:d=0.5,volume=0.9,"
                 "loudnorm=I=-15:TP=-1.5[o]",
                 ["sine=frequency=165:duration=0.18", "sine=frequency=165:duration=0.18"]),
    }
    for name, (fc, srcs) in quiz.items():
        p = se_dir / f"{name}.mp3"
        if p.exists() and not force:
            continue
        args = []
        for s in srcs:
            args += ["-f", "lavfi", "-i", s]
        args += ["-filter_complex", fc, "-map", "[o]", "-ar", "44100", str(p)]
        _run_ff(args, f"SE({name})")


def _gen_demo_clip(path: Path) -> None:
    """ffmpegのテストソースで4秒のカラフルなクリップを作る（ffmpeg無しならスキップ）。"""
    import shutil
    import subprocess

    from .config import ffmpeg_bin

    if shutil.which(ffmpeg_bin()) is None:
        print("デモクリップはスキップ（ffmpegが見つかりません）")
        return
    r = subprocess.run(
        [ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30:duration=4",
         "-pix_fmt", "yuv420p", str(path)],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        print(f"デモクリップ: {path}")
    else:
        print(f"デモクリップ生成に失敗（動作には影響なし）: {r.stderr[-200:]}")


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
