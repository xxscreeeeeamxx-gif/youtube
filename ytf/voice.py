"""音声合成ステージ。

VOICEVOX Engine (HTTP API) で台本の各セリフをWAV化し、
実測の音声長からカットごとの開始/終了時刻 (timing.json) を確定する。
以降のステージ（字幕・映像・章立て）はすべてこのタイミングを使う。

VOICEVOXが無い環境（CI等）では `--tts dummy` で無音WAVを生成して
パイプライン全体を検証できる。
"""

from __future__ import annotations

import json
import math
import wave
from dataclasses import asdict, dataclass
from pathlib import Path

import requests

from .config import Config, Project
from .schema import Script, split_reading

SAMPLE_RATE = 24000  # VOICEVOX既定の出力レート


@dataclass
class CutTiming:
    scene_id: str
    scene_title: str
    index: int          # 全カット通し番号
    speaker: str
    emotion: str
    display_text: str
    wav: str            # audio/ 相対ファイル名
    start: float        # 動画内の開始秒
    voice_dur: float    # 音声の実長
    total_dur: float    # 音声 + 後続ポーズ
    scene_start: bool   # シーン先頭カットか（章立てに使う）
    short: bool         # ショート切出対象シーンか


class VoicevoxClient:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")

    def ping(self) -> bool:
        try:
            requests.get(f"{self.base}/version", timeout=3)
            return True
        except requests.RequestException:
            return False

    def speakers(self) -> list[dict]:
        r = requests.get(f"{self.base}/speakers", timeout=10)
        r.raise_for_status()
        return r.json()

    def sync_dictionary(self, entries: list[dict]) -> None:
        """辞書をVOICEVOXのユーザー辞書に同期する（新規登録＋読みが変わったら更新）。"""
        import unicodedata

        if not entries:
            return

        def norm(s: str) -> str:
            # VOICEVOXはsurfaceを全角に正規化して保存するため、比較はNFKCで揃える
            return unicodedata.normalize("NFKC", s)

        r = requests.get(f"{self.base}/user_dict", timeout=10)
        r.raise_for_status()
        existing = {norm(w["surface"]): (uuid, w) for uuid, w in r.json().items()}
        for e in entries:
            params = {
                "surface": e["surface"],
                "pronunciation": e["pronunciation"],
                "accent_type": e.get("accent_type", 0),
            }
            hit = existing.get(norm(e["surface"]))
            if hit is None:
                requests.post(f"{self.base}/user_dict_word",
                              params=params, timeout=10).raise_for_status()
            else:
                uuid, word = hit
                same = (norm(word.get("pronunciation", "")) == norm(e["pronunciation"])
                        and int(word.get("accent_type", 0)) == int(params["accent_type"]))
                if not same:
                    requests.put(f"{self.base}/user_dict_word/{uuid}",
                                 params=params, timeout=10).raise_for_status()

    def synthesize(self, text: str, style_id: int, speed: float,
                   pitch: float = 0.0, intonation: float = 1.0) -> bytes:
        q = requests.post(
            f"{self.base}/audio_query",
            params={"text": text, "speaker": style_id},
            timeout=30,
        )
        q.raise_for_status()
        query = q.json()
        query["speedScale"] = speed
        query["pitchScale"] = pitch          # 声の高さ（±。低音にしたいなら負の値）
        query["intonationScale"] = intonation  # 抑揚（1.0が標準。下げると平坦・落ち着く）
        query["outputSamplingRate"] = SAMPLE_RATE
        query["outputStereo"] = False
        r = requests.post(
            f"{self.base}/synthesis",
            params={"speaker": style_id},
            json=query,
            timeout=120,
        )
        r.raise_for_status()
        return r.content


def dummy_wav(text: str, speed: float) -> bytes:
    """VOICEVOXなしでパイプラインを通すための無音WAV。

    日本語はおよそ 8モーラ/秒 で読まれる想定で長さを見積もる。
    """
    import io

    dur = max(0.6, len(text) / (8.0 * speed) * 1.35)
    n = int(dur * SAMPLE_RATE)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(b"\x00\x00" * n)
    return buf.getvalue()


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def style_for(cfg: Config, speaker: str, emotion: str) -> tuple[int, float, float, float]:
    """(スタイルID, 話速, ピッチ, 抑揚) を返す。ピッチ・抑揚は声トーンの調整用。"""
    ch = cfg.character(speaker)
    style = ch.get("style_overrides", {}).get(emotion, ch["voicevox_style"])
    return (
        int(style),
        float(ch.get("speed_scale", 1.0)),
        float(ch.get("pitch_scale", 0.0)),
        float(ch.get("intonation_scale", 1.0)),
    )


def load_dictionary(cfg: Config) -> list[dict]:
    """読み修正辞書。channel.yaml の voicevox.dictionary と
    dictionary.yaml（`ytf dict add` で管理）をマージして返す。"""
    import yaml

    entries = list(cfg.get("voicevox", "dictionary", default=[]) or [])
    extra = cfg.root / "dictionary.yaml"
    if extra.exists():
        data = yaml.safe_load(extra.read_text(encoding="utf-8")) or []
        entries += [e for e in data if isinstance(e, dict) and e.get("surface")]
    return entries


def run_voice(cfg: Config, proj: Project, tts: str = "voicevox") -> list[CutTiming]:
    script = proj.load_script()
    client = None
    if tts == "voicevox":
        client = VoicevoxClient(cfg.get("voicevox", "url", default="http://127.0.0.1:50021"))
        if not client.ping():
            raise SystemExit(
                "VOICEVOX Engine に接続できません。VOICEVOXを起動するか "
                "`--tts dummy` を指定してください。"
            )
        client.sync_dictionary(load_dictionary(cfg))

    default_pause = float(cfg.get("voicevox", "default_pause", default=0.3))
    # 同一セリフ・同一声設定のWAVはキャッシュ再利用（台本の一部修正後の再合成を高速化）
    cache_dir = proj.audio_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    dict_sig = json.dumps(load_dictionary(cfg), ensure_ascii=False, sort_keys=True)

    timings: list[CutTiming] = []
    t = 0.0
    idx = 0
    hits = 0
    for scene in script.scenes:
        for ci, cut in enumerate(scene.cuts):
            display, spoken = split_reading(cut.text)
            if cut.reading:
                # 誤読の手動修正: 読み上げだけを差し替える（表示は text のまま）
                spoken = cut.reading
            style_id, speed, pitch, intonation = style_for(cfg, cut.speaker, cut.emotion)
            wav_name = f"{idx:04d}_{cut.speaker}.wav"
            wav_path = proj.audio_dir / wav_name

            import hashlib
            key = hashlib.sha1(
                f"{spoken}|{style_id}|{speed}|{pitch}|{intonation}|{tts}|{dict_sig}".encode()
            ).hexdigest()[:16]
            cached = cache_dir / f"{key}.wav"
            if cached.exists():
                data = cached.read_bytes()
                hits += 1
            else:
                if client is not None:
                    data = client.synthesize(spoken, style_id, speed, pitch, intonation)
                else:
                    data = dummy_wav(spoken, speed)
                cached.write_bytes(data)
            wav_path.write_bytes(data)

            dur = wav_duration(wav_path)
            pause = cut.pause_after if cut.pause_after is not None else default_pause
            timings.append(
                CutTiming(
                    scene_id=scene.id,
                    scene_title=scene.title,
                    index=idx,
                    speaker=cut.speaker,
                    emotion=cut.emotion,
                    display_text=display,
                    wav=wav_name,
                    start=round(t, 3),
                    voice_dur=round(dur, 3),
                    total_dur=round(dur + pause, 3),
                    scene_start=(ci == 0),
                    short=scene.short,
                )
            )
            t += dur + pause
            idx += 1

    proj.timing_path.write_text(
        json.dumps([asdict(x) for x in timings], ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    concat_narration(proj, timings)
    print(f"音声 {len(timings)} 本（キャッシュ {hits}）/ 合計 {t/60:.1f} 分 -> {proj.audio_dir}")
    return timings


def concat_narration(proj: Project, timings: list[CutTiming]) -> Path:
    """個別WAVをポーズ込みで1本の narration.wav に連結する。"""
    out = proj.audio_dir / "narration.wav"
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        for ct in timings:
            with wave.open(str(proj.audio_dir / ct.wav), "rb") as src:
                if (src.getframerate(), src.getnchannels(), src.getsampwidth()) != (
                    SAMPLE_RATE, 1, 2,
                ):
                    raise SystemExit(f"想定外のWAVフォーマット: {ct.wav}")
                w.writeframes(src.readframes(src.getnframes()))
            pause_frames = int(round((ct.total_dur - ct.voice_dur) * SAMPLE_RATE))
            if pause_frames > 0:
                w.writeframes(b"\x00\x00" * pause_frames)
    return out


def load_timings(proj: Project) -> list[CutTiming]:
    if not proj.timing_path.exists():
        raise SystemExit("timing.json がありません。先に `ytf voice` を実行してください。")
    data = json.loads(proj.timing_path.read_text(encoding="utf-8"))
    return [CutTiming(**d) for d in data]
