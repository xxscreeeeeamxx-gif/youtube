"""FFmpegによる最終組み立て。

静止画の連番 + narration.wav + (任意)BGM + ASS字幕 を1パスで合成する。
静止画はconcat demuxerで時間指定するため、フレーム画像の複製は発生しない。
"""

from __future__ import annotations

import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

from .config import Config, Project, ffmpeg_bin, ffprobe_bin
from .subtitles import build_ass
from .voice import CutTiming


@lru_cache(maxsize=1)
def pick_encoder(cfg_encoder: str) -> list[str]:
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


def build_video(
    cfg: Config,
    proj: Project,
    frames: list[tuple[str, float]],
    audio_rel: str,
    ass_rel: str,
    out_rel: str,
    width: int,
    height: int,
) -> Path:
    fps = int(cfg.get("video", "fps", default=30))
    crf = str(cfg.get("video", "crf", default=20))
    enc = pick_encoder(cfg.get("video", "encoder", default="auto"))
    concat = write_concat_file(proj, frames, Path(out_rel).stem + "_list.txt")

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
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps},format=yuv420p,"
        f"subtitles={ass_rel}"
    )

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
        filters.append(f"{alabel}loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
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
    frames = render_frames(cfg, proj, timings, vertical=False)
    ass = proj.out_dir / "subs.ass"
    ass.write_text(build_ass(cfg, timings, w, h), encoding="utf-8")
    out = build_video(cfg, proj, frames, "audio/narration.wav", "out/subs.ass",
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

        frames = render_frames(cfg, proj, timings, vertical=True, only_scene=sid)
        ass_rel = f"out/short_{sid}.ass"
        (proj.root / ass_rel).write_text(
            build_ass(cfg, scene_ts, w, h, font_size=64, margin_v=800, offset=start),
            encoding="utf-8",
        )
        out = build_video(cfg, proj, frames, audio_rel, ass_rel,
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
