#!/usr/bin/env python3
"""フラッシュメモリの誕生（masuoka-flash）用の年号カード3枚。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import scripts.gen_momofuku_extras as m  # noqa: E402
from scripts.gen_momofuku_extras import render  # noqa: E402

m.ERAS = [("1943", "誕生"), ("1980", "直感"), ("1986", "法廷")]
CARDS = [
    ("ms_era1943", 0, "1943", "群馬県高崎市に生まれる", "のちのフラッシュメモリの父"),
    ("ms_era1980", 1, "1980", "サンフランシスコの学会", "「これでは置き換えられない」"),
    ("ms_era1986", 2, "1986", "ワシントンの法廷へ", "空き時間に次の発明を書く"),
]
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))
