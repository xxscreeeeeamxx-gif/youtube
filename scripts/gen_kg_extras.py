#!/usr/bin/env python3
"""自動改札機の誕生（kaisatsu-drama）用の年号カード2枚。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import scripts.gen_momofuku_extras as m  # noqa: E402
from scripts.gen_momofuku_extras import render  # noqa: E402

m.ERAS = [("1960s", "通勤地獄"), ("1967", "北千里")]
CARDS = [
    ("kg_era1960", 0, "1960年代", "駅にあふれた通勤客", "係員は1分間に80人をさばいた"),
    ("kg_era1967", 1, "1967", "阪急・北千里駅", "3月1日、10台の機械が動きはじめる"),
]
if __name__ == "__main__":
    for name, idx, year, title, sub in CARDS:
        render(name, 6.5, m.make_era(idx, year, title, sub))
