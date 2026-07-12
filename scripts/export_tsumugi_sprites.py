#!/usr/bin/env python3
"""春日部つむぎ公式立ち絵素材PSDから感情別PNGを書き出す。

PSDTool形式（グループ先頭 ! = 必須、レイヤー先頭 * = ラジオ選択）のPSDを読み、
EMOTION_LAYERS の指定でレイヤー可視状態を切り替えて合成 → 共通bboxで切り抜き。

使い方:
  PYTHONPATH=. python3 scripts/export_tsumugi_sprites.py <PSDファイル>
出力: assets/characters/tsumugi/<emotion>.png
素材の入手元・規約: assets/characters/SOURCES.md
"""

import sys
from pathlib import Path

from psd_tools import PSDImage

# 感情 → {ラジオグループ名: 選ぶレイヤー名}。未指定のグループはデフォルトのまま
EMOTION_LAYERS = {
    "normal":    {"!眉": "*普通", "!目": "*普通", "!口": "*ω"},
    "happy":     {"!眉": "*普通", "!目": "*笑う", "!口": "*わ"},
    "surprised": {"!眉": "*ん？", "!目": "*見開く", "!口": "*お"},
    "thinking":  {"!眉": "*困る", "!目": "*普通（横目）", "!口": "*綴じ　－"},
    "angry":     {"!眉": "*怒る", "!目": "*ジト目", "!口": "*綴じ　むっ"},
    "sad":       {"!眉": "*悲しい", "!目": "*なごみ", "!口": "*綴じ　へ"},
}
OUT_DIR = Path("assets/characters/tsumugi")
MARGIN = 20  # bbox切り抜きの余白(px)


def set_choice(psd, group_name: str, choice: str) -> None:
    for g in psd:
        if g.name == group_name and g.is_group():
            found = False
            for l in g:
                if l.name.startswith("*"):
                    l.visible = l.name == choice
                    found = found or l.visible
            if not found:
                raise SystemExit(f"レイヤーが見つかりません: {group_name}/{choice}")
            return
    raise SystemExit(f"グループが見つかりません: {group_name}")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    psd = PSDImage.open(sys.argv[1])
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    images = {}
    for emo, choices in EMOTION_LAYERS.items():
        for group, choice in choices.items():
            set_choice(psd, group, choice)
        img = psd.composite(force=True)
        images[emo] = img
        print(f"合成: {emo}")

    # 全感情共通のbboxで切り抜く（サイズと立ち位置を揃える）
    bbox = None
    for img in images.values():
        b = img.getbbox()
        bbox = b if bbox is None else (
            min(bbox[0], b[0]), min(bbox[1], b[1]),
            max(bbox[2], b[2]), max(bbox[3], b[3]))
    x0, y0, x1, y1 = bbox
    x0, y0 = max(0, x0 - MARGIN), max(0, y0 - MARGIN)

    for emo, img in images.items():
        img.crop((x0, y0, min(img.width, x1 + MARGIN),
                  min(img.height, y1 + MARGIN))).save(OUT_DIR / f"{emo}.png")
        print(f"書き出し: {OUT_DIR}/{emo}.png")


if __name__ == "__main__":
    main()
