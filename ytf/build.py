"""FFmpegによる最終組み立て。

各カットを「動きのある短い動画セグメント」として生成し（Ken Burnsズーム/パン、
動画クリップのカード内再生に対応）、concat demuxer で連結してから
narration.wav + (任意)BGM + ASS字幕 を合成する。

セグメントはハッシュでキャッシュされるので、台本を一部直しての再ビルドは
変更カットぶんだけ再生成される。motion を無効にした場合は従来どおり
静止PNGを時間指定で並べる高速パスを使う。
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

from .compose import CutRender
from .config import Config, Project, ffmpeg_bin, ffprobe_bin
from .subtitles import build_ass
from .voice import CutTiming

# zoompan のガタつき対策で入力を拡大してから動かす倍率
_UPSCALE = 2


@lru_cache(maxsize=1)
def pick_encoder(cfg_encoder: str) -> list[str]:
    if shutil.which(ffmpeg_bin()) is None:
        raise SystemExit(
            "ffmpeg が見つかりません。`brew install ffmpeg` でインストールするか、"
            "環境変数 YTF_FFMPEG にバイナリのパスを指定してください。"
        )
    if cfg_encoder not in ("auto", "h264_videotoolbox", "libx264"):
        return [cfg_encoder]
    if cfg_encoder in ("auto", "h264_videotoolbox"):
        out = subprocess.run(
            [ffmpeg_bin(), "-hide_banner", "-encoders"],
            capture_output=True, text=True,
        ).stdout
        if "h264_videotoolbox" in out:
            return ["h264_videotoolbox", "-b:v", "8M"]
    return ["libx264", "-preset", "medium"]


def write_concat_file(proj: Project, frames: list[tuple[str, float]], name: str) -> Path:
    """concat demuxer 用リスト。最後にファイルを再掲して末尾durationを効かせる。"""
    lines = ["ffconcat version 1.0"]
    for rel, dur in frames:
        lines.append(f"file '{rel}'")
        lines.append(f"duration {dur:.3f}")
    lines.append(f"file '{frames[-1][0]}'")
    p = proj.root / name
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _run(cmd: list[str], cwd: Path) -> None:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"ffmpeg 失敗:\n{' '.join(cmd)}\n{r.stderr[-3000:]}")


# ---------- カットごとのセグメント生成（動きを付ける） ----------


def _cut_frame_counts(durs: list[float], fps: int) -> list[int]:
    """各カットのフレーム数。累積で丸めて音声との誤差を1フレーム未満に保つ。"""
    counts, acc, prev = [], 0.0, 0
    for d in durs:
        acc += d
        total = round(acc * fps)
        counts.append(max(1, total - prev))
        prev = max(total, prev + 1)
    return counts


def _zoompan_expr(motion: str, zoom: float, n: int) -> tuple[str, str, str]:
    """(z, x, y) の zoompan 式。on は 0..n-1 の出力フレーム番号。"""
    z_max = 1.0 + zoom
    cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if motion == "zoom-out":
        return f"{z_max}-{zoom}*on/{n}", cx, cy
    if motion == "pan-left":
        return f"{z_max}", f"(iw-iw/zoom)*(1-on/{n})", "(ih-ih/zoom)/2"
    if motion == "pan-right":
        return f"{z_max}", f"(iw-iw/zoom)*on/{n}", "(ih-ih/zoom)/2"
    return f"1+{zoom}*on/{n}", cx, cy  # zoom-in（既定）


def _render_one_segment(
    proj: Project, item: CutRender, out_rel: str, n: int,
    fps: int, w: int, h: int, zoom: float, enc: list[str], crf: str,
) -> None:
    base = [ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error"]
    if item.video:
        # ベースPNG（空カード）にクリップをカード内側へ overlay。クリップは無音・ループ
        x0, y0, x1, y1 = item.box
        bw, bh = x1 - x0, y1 - y0
        fc = (
            f"[1:v]scale={bw}:{bh}:force_original_aspect_ratio=decrease,setsar=1[clip];"
            f"[0:v][clip]overlay=x={x0}+({bw}-w)/2:y={y0}+({bh}-h)/2,"
            f"format=yuv420p,setsar=1[vout]"
        )
        cmd = base + [
            "-loop", "1", "-framerate", str(fps), "-i", item.png,
            "-stream_loop", "-1", "-i", item.video,
            "-filter_complex", fc, "-map", "[vout]",
        ]
    elif item.motion == "none":
        cmd = base + [
            "-loop", "1", "-framerate", str(fps), "-i", item.png,
            "-vf", "format=yuv420p,setsar=1",
        ]
    elif item.bg:
        # 背景だけを zoompan で動かし、前景（見出し・カード・文字）は静止 overlay
        z, x, y = _zoompan_expr(item.motion, zoom, n)
        fc = (
            f"[0:v]scale={w * _UPSCALE}:{h * _UPSCALE}:force_original_aspect_ratio=increase,"
            f"crop={w * _UPSCALE}:{h * _UPSCALE},"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={w}x{h}:fps={fps}[bg];"
            f"[bg][1:v]overlay=0:0,format=yuv420p,setsar=1[vout]"
        )
        cmd = base + [
            "-i", item.bg,
            "-loop", "1", "-framerate", str(fps), "-i", item.png,
            "-filter_complex", fc, "-map", "[vout]",
        ]
    else:
        z, x, y = _zoompan_expr(item.motion, zoom, n)
        vf = (
            f"scale={w * _UPSCALE}:-2,"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={w}x{h}:fps={fps},"
            f"format=yuv420p,setsar=1"
        )
        cmd = base + ["-i", item.png, "-vf", vf]

    cmd += ["-frames:v", str(n), "-an", "-c:v", *enc]
    if enc[0] == "libx264":
        cmd += ["-crf", crf]
    cmd += [out_rel]
    _run(cmd, cwd=proj.root)


def render_segments(
    cfg: Config, proj: Project, plan: list[CutRender], w: int, h: int,
) -> list[str]:
    """カットごとの動画セグメントを frames/ に生成（キャッシュあり）。"""
    fps = int(cfg.get("video", "fps", default=30))
    crf = str(cfg.get("video", "crf", default=20))
    zoom = float(cfg.get("video", "motion", "zoom", default=0.06))
    enc = pick_encoder(cfg.get("video", "encoder", default="auto"))
    counts = _cut_frame_counts([c.dur for c in plan], fps)

    rels, made = [], 0
    for item, n in zip(plan, counts):
        vsig = ""
        if item.video:
            st = Path(item.video).stat()
            vsig = f"{item.video}:{st.st_size}:{int(st.st_mtime)}:{item.box}"
        if item.bg:
            st = Path(item.bg).stat()
            vsig += f"|bg:{item.bg}:{st.st_size}:{int(st.st_mtime)}"
        key_src = f"{item.png}|{n}|{fps}|{item.motion}|{zoom}|{w}x{h}|{vsig}|{enc[0]}"
        key = hashlib.sha1(key_src.encode()).hexdigest()[:16]
        rel = f"frames/seg_{key}.mp4"
        if not (proj.root / rel).exists():
            _render_one_segment(proj, item, rel, n, fps, w, h, zoom, enc, crf)
            made += 1
        rels.append(rel)
    print(f"セグメント {len(plan)} カット（新規 {made} / キャッシュ {len(plan) - made}）")
    return rels


def _prepare_visual(cfg: Config, proj: Project, plan: list[CutRender],
                    w: int, h: int, stem: str) -> Path:
    """映像側のconcatリストを作る。動きあり=セグメント連結 / なし=静止画を時間指定。"""
    motion_on = bool(cfg.get("video", "motion", "enabled", default=True))
    if motion_on or any(c.video for c in plan):
        segs = render_segments(cfg, proj, plan, w, h)
        lines = ["ffconcat version 1.0"] + [f"file '{s}'" for s in segs]
        p = proj.root / f"{stem}_list.txt"
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return p
    return write_concat_file(proj, [(c.png, c.dur) for c in plan], f"{stem}_list.txt")


def build_video(
    cfg: Config,
    proj: Project,
    concat: Path,
    audio_rel: str,
    ass_rel: str,
    out_rel: str,
    width: int,
    height: int,
) -> Path:
    fps = int(cfg.get("video", "fps", default=30))
    crf = str(cfg.get("video", "crf", default=20))
    enc = pick_encoder(cfg.get("video", "encoder", default="auto"))

    bgm_file = cfg.get("video", "bgm", "file")
    bgm_path = (cfg.root / bgm_file) if bgm_file else None
    if bgm_path and not bgm_path.exists():
        print(f"警告: BGMが見つからないためスキップ: {bgm_path}")
        bgm_path = None

    cmd = [ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
           "-f", "concat", "-safe", "0", "-i", concat.name,
           "-i", audio_rel]
    if bgm_path:
        cmd += ["-stream_loop", "-1", "-i", str(bgm_path)]

    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps},format=yuv420p"
    )
    # subtitles.enabled: false でテロップ焼き込みをオフ（.assは生成されるので
    # YouTubeの字幕ファイルとして使うことも、フラグを戻して焼き込むことも可能）
    if cfg.get("subtitles", "enabled", default=True):
        vf += f",subtitles={ass_rel}"

    filters = [f"[0:v]{vf}[vout]"]
    if bgm_path:
        vol = float(cfg.get("video", "bgm", "volume_db", default=-24))
        chain = f"[2:a]volume={vol}dB[b]"
        if cfg.get("video", "bgm", "ducking", default=True):
            filters += [chain,
                        "[b][1:a]sidechaincompress=threshold=0.03:ratio=10:attack=30:release=400[bd]",
                        "[1:a][bd]amix=inputs=2:duration=first:normalize=0[amix]"]
        else:
            filters += [chain, "[1:a][b]amix=inputs=2:duration=first:normalize=0[amix]"]
        alabel = "[amix]"
    else:
        alabel = "[1:a]"

    if cfg.get("video", "loudnorm", default=True):
        # loudnorm は内部で 192kHz 等に上げるので 48kHz に戻す（YouTube推奨）
        filters.append(f"{alabel}loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
        alabel = "[aout]"

    cmd += ["-filter_complex", ";".join(filters),
            "-map", "[vout]", "-map", alabel,
            "-c:v", *enc]
    if enc[0] == "libx264":
        cmd += ["-crf", crf]
    cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest", out_rel]

    _run(cmd, cwd=proj.root)
    return proj.root / out_rel


def render_main(cfg: Config, proj: Project, timings: list[CutTiming]) -> Path:
    from .compose import render_frames

    w = int(cfg.get("video", "width", default=1920))
    h = int(cfg.get("video", "height", default=1080))
    plan = render_frames(cfg, proj, timings, vertical=False)
    ass = proj.out_dir / "subs.ass"
    ass.write_text(build_ass(cfg, timings, w, h), encoding="utf-8")
    concat = _prepare_visual(cfg, proj, plan, w, h, "video")
    out = build_video(cfg, proj, concat, "audio/narration.wav", "out/subs.ass",
                      "out/video.mp4", w, h)
    print(f"書き出し完了: {out}")
    return out


def render_shorts(cfg: Config, proj: Project, timings: list[CutTiming]) -> list[Path]:
    """short: true のシーンを縦動画として切り出す。"""
    from .compose import render_frames

    w = int(cfg.get("shorts", "width", default=1080))
    h = int(cfg.get("shorts", "height", default=1920))
    scene_ids: list[str] = []
    for ct in timings:
        if ct.short and ct.scene_id not in scene_ids:
            scene_ids.append(ct.scene_id)
    if not scene_ids:
        print("short: true のシーンがありません（台本の scenes[].short を設定）")
        return []

    outs = []
    for sid in scene_ids:
        scene_ts = [ct for ct in timings if ct.scene_id == sid]
        start = scene_ts[0].start
        dur = sum(ct.total_dur for ct in scene_ts)

        # 音声をシーン範囲で切り出し
        audio_rel = f"out/short_{sid}.wav"
        _run([ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
              "-ss", f"{start:.3f}", "-t", f"{dur:.3f}",
              "-i", "audio/narration.wav", audio_rel], cwd=proj.root)

        plan = render_frames(cfg, proj, timings, vertical=True, only_scene=sid)
        ass_rel = f"out/short_{sid}.ass"
        (proj.root / ass_rel).write_text(
            build_ass(cfg, scene_ts, w, h, font_size=64, margin_v=800, offset=start),
            encoding="utf-8",
        )
        concat = _prepare_visual(cfg, proj, plan, w, h, f"short_{sid}")
        out = build_video(cfg, proj, concat, audio_rel, ass_rel,
                          f"out/short_{sid}.mp4", w, h)
        print(f"ショート書き出し: {out}")
        outs.append(out)
    return outs


def probe_duration(path: Path) -> float:
    r = subprocess.run(
        [ffprobe_bin(), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())
