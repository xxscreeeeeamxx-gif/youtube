#!/usr/bin/env python3
"""アップロード待ち（.release）のプロジェクトを1件、JSONで出力する。

n8n の Execute Command ノードから呼び、後段の YouTube ノードに
タイトル・概要欄・タグ・動画パスを渡すためのヘルパー。
対象が無ければ何も出力しない（n8n側のIFノードで分岐する）。
"""

import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent

for marker in sorted(root.glob("projects/*/.release")):
    proj = marker.parent
    video = proj / "out" / "video.mp4"
    meta_path = proj / "out" / "metadata.json"
    if not (video.exists() and meta_path.exists()):
        continue
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    print(json.dumps({
        "slug": proj.name,
        "video": str(video),
        "thumbnail": str(proj / "out" / "thumbnail.png"),
        "title": meta["title"],
        "description": meta["description"],
        "tags": meta["tags"],
    }, ensure_ascii=False))
    break
