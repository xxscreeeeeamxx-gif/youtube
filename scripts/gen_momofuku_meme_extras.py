#!/usr/bin/env python3
"""momofuku-meme（ミーム版）用のフェーズ同期アニメを生成する。

ミーム版はセリフが違うため各カットの尺が momofuku-v2 と異なる。
v2 と同じ描画関数を、ミーム版の timing.json 実測で mm2_/mm3_ 名義に描き直す
（クリップ名を分けることで本編版の同期を壊さない）。
年号カード・実写クリップは尺非依存なので共用する。

実行: PYTHONPATH=. python3 scripts/gen_momofuku_meme_extras.py（voice 後）
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.gen_momofuku_extras as m  # noqa: E402
import scripts.gen_momofuku_v2_extras as v2  # noqa: E402

if __name__ == "__main__":
    spans = v2.spans_from_timing("momofuku-meme")

    def sync(name, setter, draw):
        if name not in spans:
            print(f"スキップ（台本に無い）: {name}")
            return
        b, dur = spans[name]
        setter(b)
        v2.render(name, dur, draw)

    sync("mm2_gyoretsu", lambda b: setattr(v2, "Q_P", b), v2.draw_gyoretsu)
    sync("mm2_ana", lambda b: setattr(m, "A_P", b), m.draw_ana)
    sync("mm2_gyakusama", lambda b: setattr(m, "G_P", b), m.draw_gyakusama)
    sync("mm2_asama", lambda b: setattr(m, "S_P", b), m.draw_asama)
    sync("mm2_graph", lambda b: setattr(v2, "G2_P", b), v2.draw_graph)
    sync("mm2_gohan", lambda b: setattr(v2, "GH_P", b), v2.draw_gohan)
    sync("mm2_kenko", lambda b: setattr(v2, "K_P", b), v2.draw_kenko)
    sync("mm3_joken", lambda b: setattr(v2, "J_P", b), v2.draw_joken)
    sync("mm3_fail1", lambda b: setattr(v2, "F1_P", b), v2.draw_fail1)
    sync("mm3_fail2", lambda b: setattr(v2, "F2_P", b), v2.draw_fail2)
    sync("mm3_fail3", lambda b: setattr(v2, "F3_P", b), v2.draw_fail3)

    def set_timer(b):
        v2.T2_P = b
        v2.T2_END = spans["mm2_timer3"][1] - 1.4
    sync("mm2_timer3", set_timer, v2.draw_timer3_v2)
