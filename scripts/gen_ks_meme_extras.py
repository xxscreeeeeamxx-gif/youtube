#!/usr/bin/env python3
"""kaiten-meme（ミーム版）用のフェーズ同期アニメを km_ 名義で生成する。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.gen_ks_extras as k  # noqa: E402
import scripts.gen_momofuku_v2_extras as v2  # noqa: E402
from scripts.gen_momofuku_extras import render  # noqa: E402

if __name__ == "__main__":
    spans = v2.spans_from_timing("kaiten-meme")

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

    sync("km_beerline", k.BL_P, k.draw_beerline)
    sync("km_curve", k.CV_P, k.draw_curve)
    sync("km_fan", k.FN_P, k.draw_fan)
    sync("km_speed", k.SP_P, k.draw_speed)
    sync("km_lane", k.LN_P, k.draw_lane)
    sync("km_expo", k.EX_P, k.draw_expo)
    sync("km_spread", k.SD_P, k.draw_spread)
    sync("km_now", k.NW_P, k.draw_now)
