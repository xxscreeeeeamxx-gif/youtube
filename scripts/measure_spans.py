#!/usr/bin/env python3
"""timing.json から各クリップのフェーズ境界と DUR を実測して表示する。

spans_from_timing はクリップ名の接頭辞をハードコードで絞っているので、
そこに載っていない名義（escalator の esc_loop / ronsou など）が測れない。
台本を直したあとに定数ベタ書きの生成スクリプトを合わせ直すためのツール。

実行: PYTHONPATH=. python3 scripts/measure_spans.py <slug>
"""

import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ytf.config import Config, find_project_dir  # noqa: E402


def main() -> None:
    slug = sys.argv[1]
    root = find_project_dir(Config.load().root, slug)
    if root is None:
        raise SystemExit(f"プロジェクトが見つかりません: {slug}")
    t = json.loads((root / "audio" / "timing.json").read_text())
    s = yaml.safe_load((root / "script.yaml").read_text())
    cuts = [c for sc in s["scenes"] for c in sc["cuts"]]
    for i, c in enumerate(cuts):
        v = c.get("video")
        if not v:
            continue
        span = c.get("video_span", 1)
        seg = t[i:i + span]
        bounds, acc = [], 0.0
        for x in seg:
            bounds.append(round(acc, 2))
            acc += x["total_dur"]
        name = Path(v).stem
        speed = c.get("video_speed", 1.0)
        print(f"{name:18} 境界={bounds}  DUR={round(acc + 1.0, 1)}"
              + (f"  speed={speed}" if speed != 1.0 else ""))


if __name__ == "__main__":
    main()
