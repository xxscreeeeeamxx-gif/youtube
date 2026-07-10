"""品質チェック。

- 尺・ファイル整合の機械チェック
- Whisperによる誤読検出（任意。VOICEVOXの読み間違い候補を洗い出す）
"""

from __future__ import annotations

import difflib
import re

from .config import Config, Project
from .voice import CutTiming, load_timings


def _norm(s: str) -> str:
    return re.sub(r"[\s、。！？!?・「」()（）\[\]…〜ー]", "", s)


def _transcribe(path: str) -> list[dict]:
    """narration.wav を書き起こす。faster-whisper（数倍速）を優先し、
    無ければ openai-whisper にフォールバックする。"""
    try:
        from faster_whisper import WhisperModel
        print("faster-whisper で書き起こし中...")
        model = WhisperModel("small", device="auto", compute_type="int8")
        segs, _ = model.transcribe(path, language="ja")
        return [{"start": s.start, "end": s.end, "text": s.text} for s in segs]
    except ImportError:
        pass
    try:
        import whisper
    except ImportError:
        raise SystemExit(
            "whisperがありません: pip install faster-whisper（推奨・高速）"
            " または pip install openai-whisper"
        )
    print("openai-whisper で書き起こし中...")
    model = whisper.load_model("small")
    return model.transcribe(path, language="ja")["segments"]


def run_qc(cfg: Config, proj: Project, use_whisper: bool = False) -> None:
    timings = load_timings(proj)
    total = timings[-1].start + timings[-1].total_dur
    target = float(cfg.get("channel", "target_length_minutes", default=9))
    print(f"合計尺: {total/60:.1f} 分（目標 {target:.0f} 分）")
    if total / 60 < target * 0.6:
        print("⚠ 目標より大幅に短いです。台本の加筆を検討してください。")

    narration = proj.audio_dir / "narration.wav"
    if not narration.exists():
        print("⚠ narration.wav がありません")
        return

    if not use_whisper:
        print("（誤読チェックは `ytf qc --whisper` で実行）")
        return

    segments = _transcribe(str(narration))

    print("---- 読み上げの一致率が低いセリフ（誤読の可能性）----")
    flagged = 0
    for ct in timings:
        # カット時間帯に重なるセグメントを集める
        text = "".join(
            s["text"] for s in segments
            if s["start"] < ct.start + ct.voice_dur and s["end"] > ct.start
        )
        ratio = difflib.SequenceMatcher(None, _norm(ct.display_text), _norm(text)).ratio()
        if ratio < 0.55:
            flagged += 1
            print(f"  #{ct.index:03d} [{ratio:.2f}] 台本: {ct.display_text}")
            print(f"        {' ' * 6} 認識: {text.strip()}")
    if flagged == 0:
        print("  問題なし")
    else:
        print(f"⚠ {flagged} 件。読み修正は `[表示|よみ]` 記法か channel.yaml の辞書で。")
