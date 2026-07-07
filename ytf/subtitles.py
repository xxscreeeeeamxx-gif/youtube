"""ASS字幕の生成。タイミングは音声の実測長 (timing.json) から取る。"""

from __future__ import annotations

from pathlib import Path

from .config import Config, Project
from .voice import CutTiming


def hex_to_ass(color: str) -> str:
    """'#RRGGBB' -> '&H00BBGGRR' (ASSはBGR順)。"""
    c = color.lstrip("#")
    r, g, b = c[0:2], c[2:4], c[4:6]
    return f"&H00{b}{g}{r}".upper()


def _fmt(t: float) -> str:
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", "\\N")


_NO_LINE_HEAD = "、。！？!?）」』・ーぁぃぅぇぉっゃゅょ"


def _wrap_jp(text: str, chars_per_line: int) -> str:
    """CJK対応の自前折返し（libassのビルド差異に依存しない）。"""
    if len(text) <= chars_per_line:
        return text
    lines: list[str] = []
    cur = ""
    for ch in text:
        if len(cur) >= chars_per_line and ch not in _NO_LINE_HEAD:
            lines.append(cur)
            cur = ""
        cur += ch
    if cur:
        lines.append(cur)
    return "\\N".join(lines)


def build_ass(
    cfg: Config,
    timings: list[CutTiming],
    width: int,
    height: int,
    font_size: int | None = None,
    margin_v: int | None = None,
    offset: float = 0.0,
) -> str:
    sub = cfg.get("subtitles", default={}) or {}
    font = sub.get("font", "Noto Sans CJK JP")
    fallbacks = sub.get("font_fallbacks", [])
    fontname = font  # libassが見つからなければfontconfigのフォールバックに任せる
    size = font_size or int(sub.get("font_size", 60))
    outline = int(sub.get("outline", 3))
    mv = margin_v if margin_v is not None else int(sub.get("margin_v", 42))

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
    ]
    for key, ch in cfg.characters.items():
        color = hex_to_ass(ch.get("color", "#FFFFFF"))
        lines.append(
            f"Style: {key},{fontname},{size},{color},&H000000FF,"
            f"&H00101010,&H88000000,1,0,0,0,100,100,0,0,1,{outline},1,"
            f"2,60,60,{mv},1"
        )
    lines += [
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    chars_per_line = max(8, int((width - 150) / size))
    for ct in timings:
        start = ct.start - offset
        end = start + ct.voice_dur + min(0.25, ct.total_dur - ct.voice_dur)
        text = _wrap_jp(_esc(ct.display_text), chars_per_line)
        lines.append(
            f"Dialogue: 0,{_fmt(start)},{_fmt(end)},{ct.speaker},,0,0,0,,{text}"
        )
    return "\n".join(lines) + "\n"


def write_ass(cfg: Config, proj: Project, timings: list[CutTiming]) -> Path:
    w = int(cfg.get("video", "width", default=1920))
    h = int(cfg.get("video", "height", default=1080))
    path = proj.out_dir / "subs.ass"
    path.write_text(build_ass(cfg, timings, w, h), encoding="utf-8")
    return path
