#!/usr/bin/env python3
"""qr-meme（ミーム版）用のフェーズ同期アニメを生成する。

ミーム版はセリフが違い尺が変わるため、qr-drama の描画関数を qm_ 名義で
timing.json 実測に合わせて描き直す（年号カード era_d は尺非依存なので共用）。
実行: PYTHONPATH=. python3 scripts/gen_qr_meme_extras.py（voice 後）
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.gen_qr_drama_extras as q  # noqa: E402
import scripts.gen_momofuku_v2_extras as v2  # noqa: E402
from scripts.gen_momofuku_extras import render  # noqa: E402

if __name__ == "__main__":
    spans = v2.spans_from_timing("qr-meme")

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

    sync("qm_kanban", q.KB_P, q.draw_kanban)
    sync("qm_barcode", q.BC_P, q.draw_barcode)
    sync("qm_burden", q.BD_P, q.draw_burden)
    sync("qm_2d", q.D2_P, q.draw_2d)
    sync("qm_finder", q.FD_P, q.draw_finder)
    sync("qm_goban", q.GB_P, q.draw_goban)
    sync("qm_gosei", q.GS_P, q.draw_gosei)
    sync("qm_spec", q.SP_P, q.draw_spec)
    sync("qm_keitai", q.KT_P, q.draw_keitai)
    sync("qm_payment", q.PM_P, q.draw_payment)
