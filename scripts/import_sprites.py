#!/usr/bin/env python3
"""入手した立ち絵PNGをパイプライン用に整えるヘルパー。

やること:
  - 透明余白のトリミング
  - 高さの統一（既定1000px）
  - assets/characters/<キャラ>/<emotion>.png として配置

使い方:
  1. 公認立ち絵素材（PSD等）から、好きなツールで表情ごとにPNGを書き出す
  2. ファイル名を normal.png / happy.png / surprised.png / thinking.png /
     angry.png / sad.png にして1つのフォルダに入れる（normalだけでも可。
     足りない表情は normal で補完される）
  3. 実行:
       python3 scripts/import_sprites.py zunda ~/Downloads/zunda_pngs
       python3 scripts/import_sprites.py metan ~/Downloads/metan_pngs

※ 素材の利用規約（クレジット表記・改変可否）は必ず確認してください。
"""

import sys
from pathlib import Path

from PIL import Image

EMOTIONS = ["normal", "happy", "surprised", "thinking", "angry", "sad"]
TARGET_H = 1000


def normalize(src: Path) -> Image.Image:
    img = Image.open(src).convert("RGBA")
    bbox = img.split()[3].getbbox()  # アルファで余白判定
    if bbox:
        img = img.crop(bbox)
    w = max(1, round(img.width * TARGET_H / img.height))
    return img.resize((w, TARGET_H), Image.LANCZOS)


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    char, src_dir = sys.argv[1], Path(sys.argv[2]).expanduser()
    if not src_dir.is_dir():
        sys.exit(f"フォルダがありません: {src_dir}")
    dst = Path(__file__).resolve().parent.parent / "assets" / "characters" / char
    dst.mkdir(parents=True, exist_ok=True)

    found: dict[str, Path] = {}
    for p in src_dir.glob("*.png"):
        name = p.stem.lower()
        if name in EMOTIONS:
            found[name] = p
    if "normal" not in found:
        sys.exit(f"{src_dir} に normal.png がありません（最低1枚必要）")

    for emo in EMOTIONS:
        src = found.get(emo, found["normal"])
        normalize(src).save(dst / f"{emo}.png")
        mark = "" if emo in found else "（normalで補完）"
        print(f"  {emo}.png ← {src.name} {mark}")
    print(f"完了: {dst}")
    print("確認ビルド: ytf make sample")


if __name__ == "__main__":
    main()
