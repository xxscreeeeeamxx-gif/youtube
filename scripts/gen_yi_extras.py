#!/usr/bin/env python3
"""乾電池の誕生（yai-denchi）用の年号カード5枚を生成する。

クリップ名は yi_ 名義。実行: PYTHONPATH=. python3 scripts/gen_yi_extras.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.gen_momofuku_extras as m  # noqa: E402
from scripts.gen_momofuku_extras import render  # noqa: E402

m.ERAS = [("1864", "誕生"), ("1884", "受験"), ("1885", "電気時計"),
          ("1894", "満洲の冬"), ("1910", "会社設立")]

CARDS = [
    ("yi_era1864", 0, "1864", "越後長岡に生まれる", "1月・のちの屋井先蔵"),
    ("yi_era1884", 1, "1884", "東京職工学校を受験", "20歳・二度目の挑戦"),
    ("yi_era1885", 2, "1885", "連続電気時計", "21歳・ゼンマイのない時計"),
    ("yi_era1894", 3, "1894", "日清戦争", "厳寒の満洲で電信が止まる"),
    ("yi_era1910", 4, "1910", "合資会社屋井乾電池", "いまの筒型の形へ"),
]

if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 13.0, m.make_era(idx, year, title, sub))
