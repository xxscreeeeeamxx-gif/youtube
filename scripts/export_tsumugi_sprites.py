#!/usr/bin/env python3
"""春日部つむぎ立ち絵素材PSD（製作: 坂本アヒル）から感情別PNGを書き出す。

PSDToolフォーマット: グループ先頭 ! = 排他、レイヤー/グループ先頭 * = ラジオ選択候補。
!まゆ / !目 / !口 の候補を切り替え、表情記号(なみだめ/汗)を必要時だけ表示。

使い方:
  PYTHONPATH=. python3 scripts/export_tsumugi_sprites.py <PSDファイル>
出力: assets/characters/tsumugi/<emotion>.png（全感情を共通bboxで切り抜き）
素材の入手元・規約: assets/characters/SOURCES.md
"""

import sys
from pathlib import Path

from psd_tools import PSDImage

# 感情 → {ラジオグループ名: 選ぶ候補名}
EMOTION_LAYERS = {
    "normal":    {"!まゆ": "*普通眉",    "!目": "*基本目セット", "!口": "*ほほえみ"},
    "happy":     {"!まゆ": "*ごきげん眉", "!目": "*にっこり",     "!口": "*わあーい"},
    "surprised": {"!まゆ": "*普通眉",    "!目": "*〇〇",         "!口": "*おあー"},
    "thinking":  {"!まゆ": "*困り眉",    "!目": "*基本目セット", "!口": "*む"},
    "angry":     {"!まゆ": "*おこ眉",    "!目": "*基本目セット", "!口": "*むん"},
    "sad":       {"!まゆ": "*困り眉",    "!目": "*閉じ",         "!口": "*えあー"},
}
# 感情ごとの表情記号（なみだめ / 汗）。無ければ全部消す
EMOTION_MARKS = {
    "sad": ["なみだめ"],
    "thinking": ["汗"],
}
OUT_DIR = Path("assets/characters/tsumugi")
MARGIN = 20


def find_group(psd, name):
    for g in psd:
        if g.name == name and g.is_group():
            return g
    raise SystemExit(f"グループが見つかりません: {name}")


def set_choice(psd, group_name, choice):
    g = find_group(psd, group_name)
    hit = False
    for l in g:
        if l.name.startswith("*"):
            l.visible = l.name == choice
            hit = hit or l.visible
    if not hit:
        opts = [l.name for l in g if l.name.startswith("*")]
        raise SystemExit(f"候補が見つかりません: {group_name}/{choice} 候補={opts}")


def set_marks(psd, show_names):
    for g in psd:
        if g.name == "表情記号" and g.is_group():
            for l in g:
                l.visible = l.name in show_names
            return


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    psd = PSDImage.open(sys.argv[1])
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    images = {}
    for emo, choices in EMOTION_LAYERS.items():
        for group, choice in choices.items():
            set_choice(psd, group, choice)
        set_marks(psd, EMOTION_MARKS.get(emo, []))
        images[emo] = psd.composite(force=True)
        print(f"合成: {emo}")

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
