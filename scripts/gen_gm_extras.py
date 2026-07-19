#!/usr/bin/env python3
"""gastro-meme（ミーム版）用のフェーズ同期アニメを gm_ 名義で生成する。

図解の描画はgen_gc_extras.pyと同一。gm_名義で本編との同期を分離。
実行: PYTHONPATH=. python3 scripts/gen_gm_extras.py（voice 後）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.gen_gc_extras as g  # noqa: E402
import scripts.gen_momofuku_v2_extras as v2  # noqa: E402
from scripts.gen_momofuku_extras import render  # noqa: E402

if __name__ == "__main__":
    spans = v2.spans_from_timing("gastro-meme")

    def sync(name, bounds, draw):
        if name not in spans:
            print(f"スキップ（台本に無い）: {name}")
            return
        b, dur = spans[name]
        vals = list(b)
        while len(vals) < 6:
            vals.append(vals[-1] + max(1.5, (dur - vals[-1]) * 0.5))
        bounds[:] = vals
        render(name, dur, draw)

    sync("gm_mokuhyou", g.MK_P, g.draw_mokuhyou)
    sync("gm_shashin", g.SH_P, g.draw_shashin)
    sync("gm_shinka", g.SK_P, g.draw_shinka)
