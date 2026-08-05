#!/usr/bin/env python3
"""AquesTalk（ゆっくり）ナレの読みを faster-whisper で全数照合する。

VOICEVOXと違い moras が取れないので、合成音を書き起こして台本と突き合わせる。
一致率が低い行だけを出すので、全件を目視判定すること。
実行: PYTHONPATH=. python3 scripts/check_aq_readings.py <slug>
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml  # noqa: E402

from ytf.config import Config, find_project_dir  # noqa: E402
from ytf.schema import split_reading  # noqa: E402

THRESHOLD = 0.72


def _norm(t: str) -> str:
    return re.sub(r"[、。！？…・「」『』\s　,.!?]", "", t)


def main(slug: str) -> int:
    d = find_project_dir(Config.load().root, slug)
    if d is None:
        print(f"プロジェクトが見つかりません: {slug}")
        return 1
    from faster_whisper import WhisperModel

    sc = yaml.safe_load((d / "script.yaml").read_text())
    cuts = [c for s in sc["scenes"] for c in s["cuts"]]
    narrator = sc["meta"].get("narrator", "reimu")
    model = WhisperModel("small", device="cpu", compute_type="int8")

    ng = []
    n = 0
    for i, c in enumerate(cuts):
        if c["speaker"] != narrator:
            continue
        wav = d / "audio" / f"{i:04d}_{narrator}.wav"
        if not wav.exists():
            continue
        n += 1
        segs, _ = model.transcribe(str(wav), language="ja", beam_size=1)
        heard = _norm("".join(s.text for s in segs))
        want = _norm(split_reading(c["text"])[0])
        ratio = sum(1 for ch in want if ch in heard) / max(1, len(want))
        if ratio < THRESHOLD:
            ng.append((i, want, heard, ratio))

    print(f"ナレ {n} 本を書き起こし照合")
    for i, want, heard, r in ng:
        print(f"‼ idx{i} 一致{r:.0%}\n   台本: {want[:48]}\n   聞取: {heard[:48]}")
    print(f"要確認 {len(ng)} 件（whisperの聞き違いも混じるので必ず目視判定）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
